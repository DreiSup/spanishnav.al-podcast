#!/usr/bin/env python3
"""Etapa 8: clips de fine-tuning de un hablante en una fuente (Parte 2, sin exportar audio).

Corta los tramos del hablante (hablantes.json) en clips de 3 a 15 s por pausas >= 0,25 s y
mide cada clip. No escribe WAV: eso lo hace 09_montar.py, que aplica los umbrales, así se
pueden ajustar sin recalcular nada.

Segmentación, por tramo no descartado (los `sin_cobertura` solo con sim >= 0,65):
  - Punto de corte entre dos palabras con tiempo propio (ts_ok) separadas >= 0,25 s; también
    antes de la primera y después de la última palabra del tramo si el hueco con la vecina
    (de quien sea) es >= 0,25 s.
  - Un clip no puede cruzar una pausa > 1,0 s, una palabra sin tiempo ni una racha de palabras
    sin tiempo propio demasiado larga (03 reparte ahí pausas enteras).
  - Margen a cada lado: la mitad del hueco, entre 0,1 y 0,2 s. Duración 3-15 s con margen.
  - Programación dinámica: máxima duración cubierta, con un pequeño premio a empezar y
    acabar en frase y un coste por clip (prefiere clips largos a trocear en cada pausa). Clips sin turno de otra etiqueta a +-0,25 s ni solape a +-margen.
Métricas por clip (cortando de orig.wav, nunca el episodio entero):
  sim ECAPA contra emb/<hablante>.npy, asr_conf (media y mínimo de la prob. de palabra de
  02), DNSMOS (ovrl, sig, bak), LUFS integrado, pico, caracteres/s y re-transcripción del
  clip solo con faster-whisper large-v3 (beam 5, sin prompt): ese es el texto literal;
  wer_largo lo compara con el texto del ASR largo (un corte que se come una palabra sube).

`naval_kapil` = tramos de naval medidos contra emb/naval_kapil.npy (Naval con Kapil).

Salida: trabajo/<id>/clips_<hablante>.json. Se salta si existe (--forzar para rehacer).

Uso: 08_clips.py <hablante> <id> [<id> ...] [--forzar] [--cpu] [--modelo-asr tiny]
     [--limite N]  (solo los N primeros clips; pruebas)
     [--muestra-min N]  (solo ~N min repartidos por el episodio; para fuentes de eval)
"""
import argparse
import contextlib
import gc
import importlib
import math
import os
import re
import time
from pathlib import Path

import numpy as np

from common import (DATOS, TRABAJO, asegurar_entorno_cuda, candado_gpu, comprobar_recursos,
                    escribir_json, leer_json, log)

r07 = importlib.import_module("07_candidatos_ref")

PAUSA_CORTE = 0.25      # hueco mínimo entre palabras para cortar
PAUSA_INTERNA = 1.0     # pausa máxima dentro de un clip
MARGEN_MIN, MARGEN_MAX = 0.1, 0.2
DUR_MIN, DUR_MAX = 3.0, 15.0
OTRA_VOZ_S = 0.25       # sin turno ajeno a esta distancia del clip
SIM_ALTA = 0.65
EXTREMOS_S = 30.0       # sintonía inicial y final
RE_FIN_FRASE = r07.RE_FIN_FRASE
# cada clip resta COSTE_CLIP: partir un clip solo compensa si los dos cortes nuevos caen en
# fin de frase; así la DP prefiere clips largos en vez de trocear en cada pausa
PREMIO_FRASE, COSTE_CLIP = 0.25, 0.5


def margen(hueco: float) -> float:
    return min(MARGEN_MAX, max(MARGEN_MIN, hueco / 2))


def segmentar(F, h: str, extremos: float, rech: dict) -> list:
    """Clips (s, e, c0, c1, ti) por programación dinámica sobre los puntos de corte.
    naval_kapil usa los tramos de naval (la fuente decide el registro, no la etiqueta)."""
    h = r07.real(h)
    otros = F.otros(h)
    sl, el, ts = F.sl, F.el, F.ts_l
    out = []
    for ti, t in enumerate(F.hab.get("tramos", [])):
        if t.get("hablante") != h:
            continue
        if t.get("descartado"):
            rech["tramo_descartado"] = rech.get("tramo_descartado", 0) + 1
            continue
        if t.get("sin_cobertura") and (t.get("sim") is None or t["sim"] < SIM_ALTA):
            rech["tramo_sin_cobertura_sim_baja"] = rech.get("tramo_sin_cobertura_sim_baja", 0) + 1
            continue
        ia, ib = F.indices_tramo(t)
        ia, ib = max(ia, 0), min(ib, F.n - 1)
        if ib < ia:
            continue
        # duro[k]: no se puede cruzar el paso de la palabra k-1 a la k
        # (pausa larga, palabra sin tiempo o racha sin tiempo propio sospechosa)
        malas = [not (math.isfinite(sl[k]) and math.isfinite(el[k]) and F.pl[k] == F.pl[k])
                 for k in range(ia, ib + 1)]
        duro = {}
        r0, r_ch = -1, 0
        for k in range(ia, ib + 1):
            if malas[k - ia]:
                duro[k] = duro[k + 1] = True
                r0 = -1
                continue
            if k > ia and not malas[k - ia - 1] and sl[k] - el[k - 1] > PAUSA_INTERNA:
                duro[k] = True
            if ts[k]:
                r0 = -1
            else:
                if r0 < 0:
                    r0, r_ch = k, 0
                r_ch += F.nch[k]
                nw = k - r0 + 1
                if el[k] - sl[r0] > r07.HUECO_INTERNO + max(r07.PAUSA_PALABRA_S * nw,
                                                           r07.PAUSA_CARACTER_S * r_ch):
                    duro[k] = duro[k + 1] = True
                    r0 = -1
        # puntos de corte: k = "antes de la palabra k" (ia..ib+1), con el hueco a cada lado
        cortes = []
        for k in range(ia, ib + 2):
            # en los bordes del tramo la vecina de fuera también debe tener tiempo propio:
            # con ts_ok false su tiempo es interpolado y el hueco medido no es real
            izq_ok = (k == 0 or ts[k - 1]) if k == ia else (not malas[k - 1 - ia] and ts[k - 1])
            der_ok = (k == F.n or ts[k]) if k == ib + 1 else (not malas[k - ia] and ts[k])
            if not (izq_ok and der_ok):
                continue
            if k == ia:
                hueco = sl[k] - el[k - 1] if k > 0 else math.inf
            elif k == ib + 1:
                hueco = sl[k] - el[k - 1] if k < F.n else math.inf
            else:
                hueco = sl[k] - el[k - 1]
            if hueco == hueco and hueco >= PAUSA_CORTE:
                cortes.append((k, hueco))
        if len(cortes) < 2:
            continue
        # programación dinámica: best[j] = mejor cobertura usando cortes[0..j]
        n = len(cortes)
        best = [0.0] * n
        prev = [None] * n
        for j in range(1, n):
            best[j], prev[j] = best[j - 1], None
            kj, hj = cortes[j]
            e = kj - 1
            c1 = el[e] + margen(hj)
            for i in range(j - 1, -1, -1):
                ki, hi_ = cortes[i]
                s = ki
                c0 = sl[s] - margen(hi_)
                dur = c1 - c0
                if dur > DUR_MAX:
                    break
                if any(duro.get(k) for k in range(ki + 1, kj)):
                    break
                if dur < DUR_MIN:
                    continue
                if c0 < extremos or c1 > F.dur - extremos:
                    continue
                if r07.choca(otros, sl[s] - OTRA_VOZ_S, el[e] + OTRA_VOZ_S) or \
                        r07.choca(F.solapes, c0, c1):
                    continue
                ini = s == 0 or bool(RE_FIN_FRASE.search(F.w[s - 1]))
                fin = bool(RE_FIN_FRASE.search(F.w[e]))
                v = best[i] + dur + PREMIO_FRASE * (ini + fin) - COSTE_CLIP
                if v > best[j]:
                    best[j], prev[j] = v, i
        j, sel = n - 1, []
        while j > 0:
            if prev[j] is None:
                j -= 1
                continue
            i = prev[j]
            s, e = cortes[i][0], cortes[j][0] - 1
            sel.append((s, e, sl[s] - margen(cortes[i][1]), el[e] + margen(cortes[j][1]), ti))
            j = i
        out += sel[::-1]
    return out


def medir(F, clips: list, h: str, mod, cen: np.ndarray, rech: dict) -> list:
    res = []
    t0 = time.time()
    for n, (s, e, c0, c1, ti) in enumerate(clips, 1):
        x = r07.cortar(F, c0, c1)
        if x.size == 0:
            rech["corte_vacio"] = rech.get("corte_vacio", 0) + 1
            continue
        pico = float(np.abs(x.astype(np.int32)).max()) / 32768.0
        x16 = r07.a16k(x, F.sr)
        probs = [p for p in F.pl[s:e + 1] if p == p]
        texto_largo = " ".join(F.w[s:e + 1])
        texto = mod.transcribir(x16)
        emb = mod.embedding(x16)
        res.append({
            "fuente": F.id, "tramo": ti, "w0": s, "w1": e,
            "start": round(float(c0), 3), "end": round(float(c1), 3),
            "dur": round(float(c1 - c0), 3), "sr": F.sr,
            "texto": texto, "texto_largo": texto_largo,
            "wer_largo": r07.wer(texto_largo, texto),
            "chars": len(texto), "cps": round(len(texto) / (c1 - c0), 2),
            "asr_conf": {"media": round(float(np.mean(probs)), 4),
                         "min": round(float(np.min(probs)), 4)},
            "sim": round(float(np.dot(emb, cen)), 4),
            "dnsmos": mod.dnsmos(x16), "lufs": r07.lufs(x, F.sr),
            "pico_dbfs": round(20 * math.log10(max(pico, 1e-9)), 2),
            "inicio_frase": s == 0 or bool(RE_FIN_FRASE.search(F.w[s - 1])),
            "fin_frase": bool(RE_FIN_FRASE.search(F.w[e])),
        })
        if n % 50 == 0:
            log(f"  {F.id}: {n}/{len(clips)} clips medidos ({time.time() - t0:.0f}s)")
            if os.environ.get("NAVAL_PRUEBA") != "1":
                comprobar_recursos(esperar_s=120)
            gc.collect()
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hablante")
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--forzar", action="store_true")
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--modelo-asr", default=None)
    ap.add_argument("--trabajo", type=Path, default=TRABAJO)
    ap.add_argument("--emb", type=Path, default=DATOS / "emb")
    ap.add_argument("--excluir-extremos", type=float, default=EXTREMOS_S)
    ap.add_argument("--limite", type=int, default=None)
    ap.add_argument("--muestra-min", type=float, default=None,
                    help="medir solo ~N min repartidos por todo el episodio (fuentes de eval)")
    a = ap.parse_args()
    prueba = os.environ.get("NAVAL_PRUEBA") == "1"
    a.cpu = a.cpu or prueba
    a.modelo_asr = a.modelo_asr or ("tiny" if prueba else "large-v3")
    h = a.hablante
    emb_f = a.emb / f"{h}.npy"
    if not emb_f.exists():
        raise SystemExit(f"falta {emb_f} (06_hablantes.py --global)")
    cen = np.load(emb_f).astype(np.float64).ravel()
    cen /= np.linalg.norm(cen) + 1e-12
    pend = []
    for fid in a.ids:
        sal = a.trabajo / fid / f"clips_{h}.json"
        if sal.exists() and not a.forzar:
            log(f"{fid}: {sal.name} ya existe, se salta")
        else:
            pend.append(fid)
    if not pend:
        return
    if not a.cpu:
        asegurar_entorno_cuda()
    if not prueba:
        comprobar_recursos()
    mod = r07.Modelos(a.cpu, a.modelo_asr)
    cm = contextlib.nullcontext() if a.cpu else candado_gpu()
    with cm:
        try:
            for fid in pend:
                F = r07.Fuente(fid, a.trabajo / fid)
                rech = {}
                clips = segmentar(F, h, a.excluir_extremos, rech)
                if a.limite:
                    clips = clips[:a.limite]
                tot = sum(c[3] - c[2] for c in clips)
                if a.muestra_min and tot > a.muestra_min * 60:
                    paso = math.ceil(tot / (a.muestra_min * 60))
                    clips = clips[::paso]   # uno de cada `paso`: repartido por todo el episodio
                tot = sum(c[3] - c[2] for c in clips)
                log(f"{fid}: {len(clips)} clips, {tot / 60:.1f} min (descartes: {rech})")
                res = medir(F, clips, h, mod, cen, rech)
                escribir_json(a.trabajo / fid / f"clips_{h}.json", {
                    "fuente": fid, "hablante": h, "sr": F.sr, "modelo_asr": a.modelo_asr,
                    "generado": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "params": {"pausa_corte": PAUSA_CORTE, "pausa_interna": PAUSA_INTERNA,
                               "margen": [MARGEN_MIN, MARGEN_MAX], "dur": [DUR_MIN, DUR_MAX],
                               "otra_voz_s": OTRA_VOZ_S, "extremos_s": a.excluir_extremos},
                    "descartes": rech, "clips": res})
                log(f"{fid}: escrito clips_{h}.json ({len(res)} clips)")
                del F
                gc.collect()
        finally:
            mod.liberar_asr()


if __name__ == "__main__":
    main()
