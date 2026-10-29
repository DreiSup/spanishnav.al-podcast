#!/usr/bin/env python3
"""Etapa 9: monta el dataset de un hablante a partir de trabajo/<id>/clips_<h>.json (de 08).

Lee scripts/dataset/dataset_<h>.json (fuentes con split y registro, objetivos de minutos y
umbrales), aplica el control de calidad a cada clip y escribe:

  datasets/<h>/wavs/<h>_<fuente>_<00001>.wav   PCM16 mono a la sr de la fuente (sin
                                                remuestrear), ganancia fija hacia -20 LUFS
  datasets/<h>/metadata.jsonl                   una línea por clip, con su split
  datasets/<h>/metadata.csv                     LJSpeech: id|texto|texto (sin cabecera)
  datasets/<h>/fuentes.json                     fuente, URLs, registro, split, minutos
  datasets/<h>/informe.md                       minutos por fuente y split, descartes, métricas
  revision/<h>/escuchar.html                    N clips al azar (y algunos rechazados) para
                                                escuchar; fuera del dataset, no se sube

Control de calidad (umbrales en dataset_<h>.json, --umbral clave=valor para probar):
sim, asr_conf media y mínimo, DNSMOS ovrl, WER entre el clip re-transcrito y el ASR largo,
caracteres/s, pico (clipping) y texto vacío o con marcas de no-habla ([..], (..), ♪).
Split: train = todos los aprobados de las fuentes train; si pasan del tope de train_min, se
recorta por la fuente con más minutos quitando sus clips peores. eval = ~media de eval_min,
repartido por turnos entre las fuentes eval, los mejores primero, y nunca un clip que
solape una referencia elegida (speaker_refs/elegidas.json).
Ganancia: g = -20 - LUFS del clip, limitada para que el pico no pase de -1 dBFS y a +-12 dB.

Se reescribe entero cada vez (wavs/ se monta aparte y se cambia al final).

Uso: 09_montar.py <hablante> [--fuentes nav056,...] [--umbral sim_min=0.65 ...]
     [--escuchar 20] [--semilla 0]
"""
import argparse
import importlib
import json
import math
import random
import re
import shutil
import time
from pathlib import Path

import numpy as np

from common import (DATASETS, DATOS, REPO_DATASET, SPEAKER_REFS, TRABAJO, cargar_fuentes,
                    escribir_json, leer_json, log)

r07 = importlib.import_module("07_candidatos_ref")

LUFS_OBJ = -20.0
PICO_TECHO_DBFS = -1.0
GANANCIA_MAX_DB = 12.0
RE_NO_HABLA = re.compile(r"[\[\]()♪*]")


def puntuacion(c: dict) -> float:
    return round(0.4 * r07.clip01((c["sim"] - 0.5) / 0.4)
                 + 0.3 * r07.clip01((c["dnsmos"]["ovrl"] - 2.5) / 1.5)
                 + 0.2 * r07.clip01((c["asr_conf"]["media"] - 0.8) / 0.2)
                 + 0.1 * r07.clip01(1 - c["wer_largo"] / 0.3), 4)


def motivos(c: dict, u: dict) -> list:
    m = []
    if c["sim"] < u["sim_min"]:
        m.append("sim")
    if c["asr_conf"]["media"] < u["asr_media_min"]:
        m.append("asr_media")
    if c["asr_conf"]["min"] < u["asr_min_min"]:
        m.append("asr_min")
    if c["dnsmos"]["ovrl"] < u["dnsmos_ovrl_min"]:
        m.append("dnsmos")
    if c["wer_largo"] > u["wer_largo_max"]:
        m.append("wer_largo")
    if not u["cps"][0] <= c["cps"] <= u["cps"][1]:
        m.append("cps")
    if c["pico_dbfs"] >= u["pico_max_dbfs"]:
        m.append("clipping")
    if not c["texto"].strip() or RE_NO_HABLA.search(c["texto"]):
        m.append("texto")
    return m


def ganancia_db(c: dict) -> float:
    if c.get("lufs") is None:
        return 0.0
    g = LUFS_OBJ - c["lufs"]
    g = min(g, PICO_TECHO_DBFS - c["pico_dbfs"])
    return round(max(-GANANCIA_MAX_DB, min(GANANCIA_MAX_DB, g)), 2)


def aplicar_ganancia(x: np.ndarray, g_db: float) -> np.ndarray:
    if g_db == 0:
        return x
    y = x.astype(np.float64) * 10 ** (g_db / 20)
    return np.clip(np.round(y), -32768, 32767).astype(np.int16)


def choca_ref(c: dict, refs: list) -> bool:
    return any(r["fuente"] == c["fuente"] and c["start"] < r["end"] and c["end"] > r["start"]
               for r in refs)


def recortar_train(train: list, tope_s: float) -> list:
    """Quita clips peores de la fuente con más minutos hasta quedar bajo el tope."""
    train = list(train)
    while sum(c["dur"] for c in train) > tope_s:
        por_f = {}
        for c in train:
            por_f[c["fuente"]] = por_f.get(c["fuente"], 0) + c["dur"]
        f = max(por_f, key=por_f.get)
        peor = min((c for c in train if c["fuente"] == f), key=lambda c: c["punt"])
        peor["recortado"] = True
        train.remove(peor)
    return train


def elegir_eval(cands: list, objetivo_s: float, refs: list) -> list:
    por_f = {}
    for c in sorted(cands, key=lambda c: -c["punt"]):
        if not choca_ref(c, refs):
            por_f.setdefault(c["fuente"], []).append(c)
    out, tot = [], 0.0
    while tot < objetivo_s and any(por_f.values()):
        for f in sorted(por_f):
            if por_f[f] and tot < objetivo_s:
                c = por_f[f].pop(0)
                out.append(c)
                tot += c["dur"]
    return out


def pct(v: list) -> str:
    if not v:
        return "-"
    q = np.percentile(v, [5, 25, 50, 75, 95])
    return " / ".join(f"{x:.3g}" for x in q)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hablante")
    ap.add_argument("--fuentes", default=None, help="solo estas (ids separados por comas)")
    ap.add_argument("--umbral", action="append", default=[], metavar="CLAVE=VALOR")
    ap.add_argument("--escuchar", type=int, default=20)
    ap.add_argument("--semilla", type=int, default=0)
    ap.add_argument("--trabajo", type=Path, default=TRABAJO)
    ap.add_argument("--salida", type=Path, default=None)
    a = ap.parse_args()
    h = a.hablante
    cfg = leer_json(REPO_DATASET / f"dataset_{h}.json")
    u = dict(cfg["umbrales"])
    for x in a.umbral:
        k, _, v = x.partition("=")
        if k not in u:
            ap.error(f"umbral desconocido {k}; válidos: {sorted(u)}")
        u[k] = json.loads(v)
    salida = a.salida or DATASETS / h
    revision = DATOS / "revision" / h
    cat = {f["id"]: f for f in cargar_fuentes()}
    pedidas = set(a.fuentes.split(",")) if a.fuentes else None
    refs = [r for r in leer_json(SPEAKER_REFS / "elegidas.json")["elegidas"]
            if r["ref"].split("_ref")[0] in (h, f"{h}_kapil")]

    todos, fuentes_ok = [], []
    for fu in cfg["fuentes"]:
        if pedidas and fu["id"] not in pedidas:
            continue
        p = a.trabajo / fu["id"] / f"clips_{h}.json"
        if not p.exists():
            log(f"{fu['id']}: falta {p.name}, se omite")
            continue
        d = leer_json(p)
        fuentes_ok.append({**fu, "sr": d["sr"], "n_medidos": len(d["clips"])})
        for c in d["clips"]:
            c["split_fuente"], c["registro"] = fu["split"], fu["registro"]
            c["motivos"] = motivos(c, u)
            c["punt"] = puntuacion(c)
            todos.append(c)
    if not todos:
        raise SystemExit("no hay clips")
    aprob = [c for c in todos if not c["motivos"]]
    train = recortar_train([c for c in aprob if c["split_fuente"] == "train"],
                           cfg["train_min"][1] * 60)
    ev_obj = sum(cfg["eval_min"]) / 2 * 60
    ev = elegir_eval([c for c in aprob if c["split_fuente"] == "eval"], ev_obj, refs)
    for c in train:
        c["split"] = "train"
    for c in ev:
        c["split"] = "eval"
    final = sorted(train + ev, key=lambda c: (c["fuente"], c["start"]))

    # --- WAVs (a un directorio nuevo; se cambia al final)
    sf = r07._sf()
    nuevo = salida / "wavs_nuevo"
    shutil.rmtree(nuevo, ignore_errors=True)
    nuevo.mkdir(parents=True)
    fuentes_cache, num = {}, {}
    filas = []
    for c in final:
        f = c["fuente"]
        if f not in fuentes_cache:
            fuentes_cache.clear()
            fuentes_cache[f] = r07.Fuente(f, a.trabajo / f)
        F = fuentes_cache[f]
        num[f] = num.get(f, 0) + 1
        cid = f"{h}_{f}_{num[f]:05d}"
        g = ganancia_db(c)
        x = aplicar_ganancia(r07.cortar(F, c["start"], c["end"]), g)
        sf.write(str(nuevo / f"{cid}.wav"), x, F.sr, subtype="PCM_16")
        fu = cat.get(f, {})
        filas.append({
            "id": cid, "file": f"wavs/{cid}.wav", "text": c["texto"].strip(), "speaker": h,
            "source_id": f, "source_url": fu.get("url_episodio"),
            "source_audio": fu.get("url_audio"),
            "start": c["start"], "end": c["end"], "dur": c["dur"], "sr": F.sr,
            "sim": c["sim"], "asr_conf": c["asr_conf"]["media"],
            "asr_conf_min": c["asr_conf"]["min"], "mos": c["dnsmos"]["ovrl"],
            "dnsmos": c["dnsmos"], "wer_largo": c["wer_largo"], "lufs_orig": c["lufs"],
            "gain_db": g, "demucs": False, "tono": c["registro"], "split": c["split"]})
        c["id"] = cid
    fuentes_cache.clear()
    if (salida / "wavs").exists():
        shutil.rmtree(salida / "wavs")
    nuevo.rename(salida / "wavs")
    with open(salida / "metadata.jsonl", "w", encoding="utf-8") as fh:
        for r in filas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(salida / "metadata.csv", "w", encoding="utf-8") as fh:
        for r in filas:
            t = r["text"].replace("|", " ")
            fh.write(f"{r['id']}|{t}|{t}\n")

    # --- fuentes.json
    def mins(cs, **kw):
        return round(sum(c["dur"] for c in cs
                         if all(c.get(k) == v for k, v in kw.items())) / 60, 2)
    fj = []
    for fu in fuentes_ok:
        meta = cat.get(fu["id"], {})
        fj.append({"id": fu["id"], "titulo": meta.get("titulo"),
                   "url_episodio": meta.get("url_episodio"), "url_audio": meta.get("url_audio"),
                   "fecha": meta.get("fecha"), "registro": fu["registro"],
                   "split": fu["split"], "sr": fu["sr"], "demucs": False,
                   "clips_medidos": fu["n_medidos"],
                   "min_medidos": mins(todos, fuente=fu["id"]),
                   "min_aprobados": round(sum(c["dur"] for c in aprob
                                              if c["fuente"] == fu["id"]) / 60, 2),
                   "min_en_dataset": mins(final, fuente=fu["id"])})
    escribir_json(salida / "fuentes.json", {"hablante": h, "umbrales": u, "fuentes": fj})

    # --- informe.md
    rech = {}
    for c in todos:
        for m in c["motivos"]:
            rech[m] = rech.get(m, 0) + 1
    L = [f"# Dataset {h}", "",
         f"Generado {time.strftime('%Y-%m-%d %H:%M')}. Clips de 3-15 s, texto = re-transcripción "
         "literal del clip (faster-whisper large-v3), PCM16 mono a la sr de la fuente, ganancia "
         f"fija hacia {LUFS_OBJ:.0f} LUFS (pico <= {PICO_TECHO_DBFS:.0f} dBFS). Sin Demucs.", "",
         f"**train: {mins(final, split='train')} min ({sum(c['split'] == 'train' for c in final)} "
         f"clips) · eval: {mins(final, split='eval')} min "
         f"({sum(c['split'] == 'eval' for c in final)} clips)**", "",
         "| Fuente | Registro | Split | Medidos (min) | Aprobados (min) | En el dataset (min) |",
         "|---|---|---|---|---|---|"]
    for f in fj:
        L.append(f"| {f['id']} {f['titulo'] or ''} | {f['registro']} | {f['split']} | "
                 f"{f['min_medidos']} | {f['min_aprobados']} | {f['min_en_dataset']} |")
    L += ["", f"Aprobados: {len(aprob)} de {len(todos)} clips "
          f"({sum(c['dur'] for c in aprob) / 60:.1f} de {sum(c['dur'] for c in todos) / 60:.1f} min). "
          f"Recortados de train por tope: {sum(bool(c.get('recortado')) for c in todos)}.", "",
          "## Umbrales", "", "```json", json.dumps(u, ensure_ascii=False), "```", "",
          "## Descartes por motivo (un clip puede tener varios)", ""]
    L += [f"- {k}: {v}" for k, v in sorted(rech.items(), key=lambda kv: -kv[1])] or ["- ninguno"]
    L += ["", "## Métricas de todos los clips medidos (p5 / p25 / p50 / p75 / p95)", "",
          "| Métrica | Todos | Aprobados |", "|---|---|---|"]
    met = {"dur (s)": lambda c: c["dur"], "sim": lambda c: c["sim"],
           "asr_conf media": lambda c: c["asr_conf"]["media"],
           "asr_conf min": lambda c: c["asr_conf"]["min"],
           "DNSMOS ovrl": lambda c: c["dnsmos"]["ovrl"], "DNSMOS sig": lambda c: c["dnsmos"]["sig"],
           "DNSMOS bak": lambda c: c["dnsmos"]["bak"], "WER vs ASR largo": lambda c: c["wer_largo"],
           "caracteres/s": lambda c: c["cps"], "LUFS original": lambda c: c["lufs"] or float("nan")}
    for k, fn in met.items():
        L.append(f"| {k} | {pct([fn(c) for c in todos])} | {pct([fn(c) for c in aprob])} |")
    (salida / "informe.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # --- página de escucha (fuera del dataset)
    rnd = random.Random(a.semilla)
    muestra = rnd.sample(filas, min(a.escuchar, len(filas)))
    rech_c = [c for c in todos if c["motivos"]]
    muestra_r = rnd.sample(rech_c, min(10, len(rech_c)))
    shutil.rmtree(revision, ignore_errors=True)
    (revision / "rechazados").mkdir(parents=True)
    for c in muestra_r:
        F = r07.Fuente(c["fuente"], a.trabajo / c["fuente"])
        nom = f"rech_{c['fuente']}_{int(c['start'] * 1000)}.wav"
        sf.write(str(revision / "rechazados" / nom),
                 aplicar_ganancia(r07.cortar(F, c["start"], c["end"]), ganancia_db(c)),
                 F.sr, subtype="PCM_16")
        c["_wav"] = f"rechazados/{nom}"
    (revision / "escuchar.html").write_text(html_escuchar(h, muestra, muestra_r, salida),
                                             encoding="utf-8")
    log(f"listo: {salida} train {mins(final, split='train')} min, eval "
        f"{mins(final, split='eval')} min; escucha: {revision / 'escuchar.html'}")


def html_escuchar(h: str, muestra: list, rech: list, salida: Path) -> str:
    import html
    e = html.escape
    p = ["<!doctype html><html lang='es'><head><meta charset='utf-8'>",
         "<meta name='viewport' content='width=device-width,initial-scale=1'>",
         f"<title>Revisión {e(h)}</title><style>",
         ":root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--card:#f4f4f6;--bad:#b3261e}",
         "@media(prefers-color-scheme:dark){:root{--bg:#16161a;--fg:#e8e8ea;--mut:#9a9aa2;"
         "--card:#23232a;--bad:#ff8a80}}",
         "body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;"
         "max-width:880px;margin:0 auto;padding:16px}.c{background:var(--card);"
         "border-radius:8px;padding:10px 12px;margin:8px 0}audio{width:100%}"
         ".m{color:var(--mut);font-size:.85rem}.bad{color:var(--bad);font-weight:600}"
         "</style></head><body>", f"<h1>Revisión del dataset {e(h)}</h1>",
         f"<h2>{len(muestra)} clips aprobados al azar</h2>"]
    for i, r in enumerate(muestra, 1):
        p.append(f"<div class='c'><b>{i}. {e(r['id'])}</b> <span class='m'>{e(r['split'])}</span>"
                 f"<audio controls preload='none' src='{e(str(salida / r['file']))}'></audio>"
                 f"<div>{e(r['text'])}</div><div class='m'>{e(r['source_id'])} "
                 f"{r['start']:.1f}-{r['end']:.1f}s ({r['dur']:.1f}s) | sim {r['sim']:.3f} | "
                 f"asr {r['asr_conf']:.3f} (min {r['asr_conf_min']:.2f}) | DNSMOS {r['mos']:.2f} "
                 f"(sig {r['dnsmos']['sig']:.2f}, bak {r['dnsmos']['bak']:.2f}) | "
                 f"WER {r['wer_largo']:.2f} | ganancia {r['gain_db']:+.1f} dB</div></div>")
    p.append(f"<h2>{len(rech)} rechazados al azar (para calibrar umbrales)</h2>")
    for c in rech:
        p.append(f"<div class='c'><span class='bad'>{e(', '.join(c['motivos']))}</span>"
                 f"<audio controls preload='none' src='{e(c['_wav'])}'></audio>"
                 f"<div>{e(c['texto'])}</div><div class='m'>{e(c['fuente'])} "
                 f"{c['start']:.1f}-{c['end']:.1f}s ({c['dur']:.1f}s) | sim {c['sim']:.3f} | "
                 f"asr {c['asr_conf']['media']:.3f} (min {c['asr_conf']['min']:.2f}) | "
                 f"DNSMOS {c['dnsmos']['ovrl']:.2f} | WER {c['wer_largo']:.2f} | "
                 f"cps {c['cps']}</div></div>")
    p.append("</body></html>")
    return "\n".join(p)


if __name__ == "__main__":
    main()
