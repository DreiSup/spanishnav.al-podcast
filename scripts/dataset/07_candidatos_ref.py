#!/usr/bin/env python3
"""Etapa 7: candidatos de referencia por hablante (Fase 1a, speaker_refs/).

Busca, en los tramos de cada hablante (hablantes.json), ventanas de habla continua
limpia para los huecos ref01 (~6 s), ref02 (~12 s) y ref03 (~25 s), con +-20 % de
duracion contando el margen de 0,2 s a cada lado. `naval_kapil` es Naval en nav072
(un unico hueco "ref01" de 6 a 25 s, 3 clips en total); `naval` sale de todas las
fuentes MENOS nav072.

Flujo (el episodio nunca se carga entero; solo trozos de orig.wav):
  1. Enumeracion barata de ventanas valides sobre palabras.json + diar.json
     (solo texto/tiempos; O(palabras x palabras-por-ventana), sin O(n^2)).
     Se queda un pool diverso por fuente y hueco (no solapado, max. 4 por tramo).
  2. Metricas de audio del pool, cortando de orig.wav: pico (rechaza clipping >= -0,1 dBFS),
     ECAPA (sim contra emb/<hablante>.npy; si no existe se usa el centroide local del pool
     y `sim_ref` lo marca), DNSMOS (speechmos, copia a 16 kHz), LUFS (pyloudnorm).
  3. Seleccion de 3 candidatos por hueco con diversidad (penaliza mismo tramo y misma
     fuente) y sin solapes entre huecos del mismo hablante.
  4. Export del corte EXACTO de orig.wav (PCM16 mono a la sr original, sin normalizar) y
     re-transcripcion de cada clip con faster-whisper (large-v3, beam 5, sin prompt;
     GPU con candado, o --cpu con --modelo-asr tiny en pruebas). Ese es el .txt.
     Si difiere del texto largo (WER > 10 %) se marca `wer_alto`.
  5. candidatos.json, refs.json y escuchar.html (local, no publicar). Se fusionan con lo
     que ya hubiera de otros hablantes.

Salida (bajo --salida, por defecto ~/naval-datos/speaker_refs):
  <h>/candidatos/<h>_ref01_c1.wav + .txt  (c1 = mejor)
  candidatos.json, refs.json, escuchar.html

Los hablantes ya presentes en candidatos.json se saltan (salvo --forzar). Los clips se
exportan a <h>/.candidatos_nuevo/ y solo se mueven a candidatos/ (junto con candidatos.json)
cuando el ASR ha terminado bien. Candidatos con sim < 0,55 (--sim-min) se descartan. Con
--fuente (ids separados por comas) el hablante se rehace solo con esas fuentes. refs.json
(y escuchar.html) se regeneran siempre.

Uso: 07_candidatos_ref.py [hablante ...] [--fuente nav109,nav072] [--cpu] [--modelo-asr tiny]
     [--forzar]
     (sin hablantes: naval nivi brett naval_kapil y despues el resto con datos)
Pruebas: prueba.sh 07_candidatos_ref.py naval brett --trabajo X/trabajo --emb X/emb \
         --salida X/speaker_refs --excluir-extremos 5 --modelo-asr tiny
"""
import argparse
import bisect
import gc
import html
import math
import os
import re
import shutil
import time
from math import gcd
from pathlib import Path

import numpy as np

from common import (DATOS, HABLANTES, SOLO_KAPIL, SPEAKER_REFS, TRABAJO, asegurar_entorno_cuda,
                    candado_gpu, comprobar_recursos, escribir_json, leer_json, log)

# ---------------------------------------------------------------- constantes del contrato
HUECOS = {"ref01": (6.0, 4.8, 7.2), "ref02": (12.0, 9.6, 14.4), "ref03": (25.0, 20.0, 30.0)}
HUECOS_KAPIL = {"ref01": (15.0, 6.0, 25.0)}   # 2-3 clips en total, 6-25 s
N_POR_HUECO = 3
MARGEN = 0.2            # margen de corte a cada lado
HUECO_BORDE = 0.4       # silencio exigido antes de la 1a palabra y despues de la ultima
HUECO_INTERNO = 0.8     # pausa interna maxima
PROB_MIN = 0.4
PROB_MEDIA = 0.85
SIM_ALTA = 0.65         # tramo sin cobertura oficial: solo vale con sim >= esto
SIM_MIN = 0.55          # sim minima del clip con la voz del hablante (umbral por defecto de 06)
PAUSA_PALABRA_S = 0.35  # duracion razonable por palabra sin tiempo propio (ts_ok false)
PAUSA_CARACTER_S = 0.08 # idem por caracter; se toma la mayor de las dos
COMPILADOS = {"nav056", "nav167"}   # recopilatorios: su audio puede estar en otra fuente
EXTREMOS_S = 45.0       # sintonia inicial y final
PICO_MAX = 10 ** (-0.1 / 20)   # -0,1 dBFS
WER_ALTO = 0.10
POOL_POR_FUENTE = 12
MAX_POR_TRAMO_POOL = 4
ORDEN_DEFECTO = ["naval", "nivi", "brett", "naval_kapil", "deutsch", "kapil", "vitalik",
                 "ridley", "hodak", "rauch", "scholl", "qureshi"]
RE_FIN_FRASE = re.compile(r"[.?!][\"'”’)\]]*$")


# ---------------------------------------------------------------- reglas de hablante/fuente
def real(h: str) -> str:
    """Hablante cuyas etiquetas se buscan en hablantes.json."""
    return "naval" if h == "naval_kapil" else h


def fuente_vale(h: str, fid: str) -> bool:
    if h == "naval":
        return fid not in SOLO_KAPIL
    if h == "naval_kapil":
        return fid in SOLO_KAPIL
    return True


def huecos_de(h: str) -> dict:
    return HUECOS_KAPIL if h == "naval_kapil" else HUECOS


def clip01(x: float) -> float:
    return float(min(1.0, max(0.0, x)))


# ---------------------------------------------------------------- carga de una fuente
class Fuente:
    """Palabras y diarizacion de una fuente, en arrays numpy (sin audio)."""

    def __init__(self, fid: str, td: Path):
        self.id, self.td = fid, td
        pal = leer_json(td / "palabras.json")["words"]
        n = len(pal)
        self.n = n
        nan = float("nan")
        self.start = np.fromiter((nan if w.get("start") is None else w["start"] for w in pal),
                                 float, n)
        self.end = np.fromiter((nan if w.get("end") is None else w["end"] for w in pal),
                               float, n)
        self.prob = np.fromiter((nan if w.get("prob") is None else w["prob"] for w in pal),
                                float, n)
        self.ts = np.fromiter((bool(w.get("ts_ok", True)) for w in pal), bool, n)
        # palabra sin tiempo (palabras.json antiguos o editados a mano): no vale, rompe la racha
        sin_t = np.isnan(self.start) | np.isnan(self.end)
        self.prob[sin_t] = np.nan
        self.ts &= ~sin_t
        self.w = [w["w"].strip() for w in pal]
        del pal
        self.hab = leer_json(td / "hablantes.json")
        diar = leer_json(td / "diar.json")
        self.turnos = [(t["start"], t["end"], t["label"]) for t in diar["turnos"]]
        self.solapes = merge([(s["start"], s["end"]) for s in diar.get("solapes", [])])
        del diar
        sf = _sf()
        self.audio = td / "orig.wav"
        info = sf.info(str(self.audio))
        self.sr, self.dur = info.samplerate, info.frames / info.samplerate
        # huecos entre palabras vecinas y "esta bien como borde" (ts_ok propio y del vecino)
        gap_prev = np.full(n, np.inf)
        gap_prev[1:] = self.start[1:] - self.end[:-1]
        gap_next = np.full(n, np.inf)
        gap_next[:-1] = self.start[1:] - self.end[:-1]
        ts_prev = np.ones(n, bool)
        ts_prev[1:] = self.ts[:-1]
        ts_next = np.ones(n, bool)
        ts_next[:-1] = self.ts[1:]
        self.ok_ini = self.ts & ts_prev & (gap_prev >= HUECO_BORDE)
        self.ok_fin = self.ts & ts_next & (gap_next >= HUECO_BORDE)
        self.sl, self.el, self.pl = self.start.tolist(), self.end.tolist(), self.prob.tolist()
        self.okini_l, self.okfin_l = self.ok_ini.tolist(), self.ok_fin.tolist()
        self.ts_l = self.ts.tolist()
        self.nch = [len(x) for x in self.w]
        self._otros = {}

    def etiquetas_de(self, h: str) -> set:
        return {l for l, e in self.hab.get("etiquetas", {}).items()
                if e.get("hablante") == h and e.get("estado") == "ok"}

    def otros(self, h: str):
        """Turnos de diarizacion de etiquetas que NO son del hablante, fusionados."""
        if h not in self._otros:
            propias = self.etiquetas_de(h) | {t["label"] for t in self.hab.get("tramos", [])
                                              if t.get("hablante") == h}
            self._otros[h] = merge([(a, b) for a, b, l in self.turnos if l not in propias])
        return self._otros[h]

    def indices_tramo(self, t: dict):
        """(ia, ib) inclusivos de las palabras del tramo; w0/w1 si cuadran, si no, tiempos."""
        w0, w1 = t.get("w0"), t.get("w1")
        if w0 is not None and w1 is not None and 0 <= w0 < self.n:
            best, err = None, 1e9
            for e in (w1, w1 - 1):          # w1 inclusivo o exclusivo
                if w0 <= e < self.n:
                    d = abs(self.end[e] - t["end"]) + abs(self.start[w0] - t["start"])
                    if d < err:
                        best, err = e, d
            if best is not None and err < 1.0:
                return w0, best
        ia = int(np.searchsorted(self.start, t["start"] - 0.05, side="left"))
        ib = int(np.searchsorted(self.end, t["end"] + 0.05, side="right")) - 1
        return ia, ib


def merge(iv: list) -> tuple:
    """Intervalos fusionados -> (starts, ends) ordenados."""
    iv = sorted(iv)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [x[0] for x in out], [x[1] for x in out]


def choca(m: tuple, a: float, b: float) -> bool:
    """Hay algun intervalo fusionado que cruce [a, b]?"""
    starts, ends = m
    i = bisect.bisect_right(starts, b) - 1
    return i >= 0 and ends[i] >= a


def _sf():
    import soundfile
    return soundfile


# ---------------------------------------------------------------- 1. enumeracion de ventanas
def enumerar(F: Fuente, h: str, huecos: dict, extremos: float, rech: dict) -> dict:
    """Devuelve {hueco: [ventana,...]} con todas las ventanas validas por texto/tiempos."""
    real_h = real(h)
    otros = F.otros(real_h)
    hi_max = max(v[2] for v in huecos.values())
    res = {k: [] for k in huecos}
    for ti, t in enumerate(F.hab.get("tramos", [])):
        if t.get("hablante") != real_h:
            continue
        if t.get("descartado"):
            rech["tramo_descartado"] = rech.get("tramo_descartado", 0) + 1
            continue
        if t.get("sin_cobertura") and (t.get("sim") is None or t["sim"] < SIM_ALTA):
            rech["tramo_sin_cobertura_sim_baja"] = rech.get("tramo_sin_cobertura_sim_baja", 0) + 1
            continue
        ia, ib = F.indices_tramo(t)
        ia, ib = max(ia, 0), min(ib, F.n - 1)
        sl, el, pl = F.sl, F.el, F.pl
        for s in range(ia, ib + 1):
            if not F.okini_l[s]:
                continue
            cs = sl[s] - MARGEN
            if cs < max(extremos, 0.0):
                rech["extremo_inicial"] = rech.get("extremo_inicial", 0) + 1
                continue
            inicio_frase = s == 0 or bool(RE_FIN_FRASE.search(F.w[s - 1]))
            psum, pmin = 0.0, 1.0
            r0 = -1                                         # inicio del tramo ts_ok=false actual
            r_ch = 0
            for e in range(s, ib + 1):
                if e > s and sl[e] - el[e - 1] > HUECO_INTERNO:
                    break                                   # pausa interna: fin de racha
                if F.ts_l[e]:
                    r0 = -1
                else:
                    # 03 reparte una pausa entera entre las palabras sin tiempo propio y el
                    # hueco entre vecinas sale 0: se limita la duracion del tramo entero
                    if r0 < 0:
                        r0, r_ch = e, 0
                    r_ch += F.nch[e]
                    nw = e - r0 + 1
                    if el[e] - sl[r0] > HUECO_INTERNO + max(PAUSA_PALABRA_S * nw,
                                                           PAUSA_CARACTER_S * r_ch):
                        rech["pausa_en_palabras_sin_tiempo"] = \
                            rech.get("pausa_en_palabras_sin_tiempo", 0) + 1
                        break
                p = pl[e]
                if not p >= PROB_MIN:                       # tambien NaN
                    break
                psum += p
                if p < pmin:
                    pmin = p
                ce = el[e] + MARGEN
                dur = ce - cs
                if dur > hi_max or ce > F.dur - extremos:
                    break
                if not F.okfin_l[e]:
                    continue
                pm = psum / (e - s + 1)
                if pm < PROB_MEDIA:
                    continue
                a, b = sl[s], el[e]
                for k, (obj, lo, hi) in huecos.items():
                    if not lo <= dur <= hi:
                        continue
                    if choca(otros, a - HUECO_BORDE, b + HUECO_BORDE) or \
                            choca(F.solapes, a - MARGEN, b + MARGEN):
                        rech["otra_voz_o_solape"] = rech.get("otra_voz_o_solape", 0) + 1
                        continue
                    fin_frase = bool(RE_FIN_FRASE.search(F.w[e]))
                    cerca = 1.0 - abs(dur - obj) / max(obj - lo, hi - obj)
                    pre = (0.45 * clip01((pm - PROB_MEDIA) / (1 - PROB_MEDIA))
                           + 0.15 * clip01((pmin - PROB_MIN) / (1 - PROB_MIN))
                           + 0.15 * inicio_frase + 0.15 * fin_frase + 0.10 * clip01(cerca))
                    res[k].append((pre, s, e, ti, pm, pmin, inicio_frase, fin_frase, cerca))
    return res


def pool_diverso(vent: list, F: Fuente, n: int) -> list:
    """Voraz por puntuacion previa: sin solapes (margen 1 s) y max. 4 por tramo."""
    vent = sorted(vent, key=lambda v: -v[0])
    elegidas, por_tramo = [], {}
    for v in vent:
        pre, s, e, ti = v[:4]
        a, b = F.start[s] - MARGEN, F.end[e] + MARGEN
        if por_tramo.get(ti, 0) >= MAX_POR_TRAMO_POOL:
            continue
        if any(a < ob + 1.0 and b > oa - 1.0 for oa, ob in ((F.start[x[1]] - MARGEN,
                                                             F.end[x[2]] + MARGEN)
                                                            for x in elegidas)):
            continue
        elegidas.append(v)
        por_tramo[ti] = por_tramo.get(ti, 0) + 1
        if len(elegidas) >= n:
            break
    return elegidas


# ---------------------------------------------------------------- 2. audio y metricas
def cortar(F: Fuente, a: float, b: float) -> np.ndarray:
    """Trozo [a, b] de orig.wav como int16 mono, leyendo solo ese trozo."""
    sf = _sf()
    i0 = max(0, int(round(a * F.sr)))
    i1 = min(int(round(F.dur * F.sr)), int(round(b * F.sr)))
    with sf.SoundFile(str(F.audio)) as f:
        f.seek(i0)
        x = f.read(i1 - i0, dtype="int16", always_2d=True)
    if x.shape[1] > 1:
        x = x.astype(np.float32).mean(axis=1).round().astype(np.int16)
    else:
        x = x[:, 0]
    return np.ascontiguousarray(x)


def a16k(x16: np.ndarray, sr: int) -> np.ndarray:
    """int16 a float32 en [-1, 1) a 16 kHz."""
    x = x16.astype(np.float32) / 32768.0
    if sr == 16000:
        return x
    from scipy.signal import resample_poly
    g = gcd(16000, sr)
    y = resample_poly(x, 16000 // g, sr // g).astype(np.float32)
    return np.clip(y, -1.0, 1.0)


class Modelos:
    """ECAPA (CPU), DNSMOS (CPU) y ASR (GPU/CPU): se cargan al primer uso."""

    def __init__(self, cpu: bool, modelo_asr: str):
        self.cpu, self.modelo_asr = cpu, modelo_asr
        self._ecapa = self._asr = None

    def ecapa(self):
        if self._ecapa is None:
            import torch
            from speechbrain.inference.speaker import EncoderClassifier
            torch.set_num_threads(2)
            log("cargando ECAPA (CPU)")
            savedir = DATOS / "modelos" / "spkrec-ecapa-voxceleb"
            savedir.mkdir(parents=True, exist_ok=True)
            # como 06: si el modelo ya esta descargado no se consulta el hub
            src = str(savedir) if (savedir / "hyperparams.yaml").exists() \
                else "speechbrain/spkrec-ecapa-voxceleb"
            self._ecapa = EncoderClassifier.from_hparams(
                source=src, savedir=str(savedir), run_opts={"device": "cpu"})
            self._ecapa.eval()
        return self._ecapa

    def embedding(self, x16k: np.ndarray) -> np.ndarray:
        import torch
        with torch.no_grad():
            e = self.ecapa().encode_batch(torch.from_numpy(x16k)[None, :]).squeeze().cpu().numpy()
        e = e.astype(np.float64)
        return e / (np.linalg.norm(e) + 1e-12)

    def dnsmos(self, x16k: np.ndarray) -> dict:
        from speechmos import dnsmos
        r = dnsmos.run(x16k, 16000)
        return {"ovrl": round(float(r["ovrl_mos"]), 3), "sig": round(float(r["sig_mos"]), 3),
                "bak": round(float(r["bak_mos"]), 3), "p808": round(float(r["p808_mos"]), 3)}

    def asr(self):
        if self._asr is None:
            from faster_whisper import WhisperModel
            dev = "cpu" if self.cpu else "cuda"
            log(f"cargando faster-whisper {self.modelo_asr} ({dev}, int8)")
            self._asr = WhisperModel(self.modelo_asr, device=dev, compute_type="int8")
        return self._asr

    def transcribir(self, x16k: np.ndarray) -> str:
        segs, _ = self.asr().transcribe(x16k, language="en", beam_size=5, temperature=0.0,
                                        condition_on_previous_text=False,
                                        initial_prompt=None, vad_filter=False,
                                        no_speech_threshold=None, log_prob_threshold=None,
                                        without_timestamps=True)
        return " ".join(s.text.strip() for s in segs).strip()

    def liberar_asr(self):
        self._asr = None
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass


def lufs(x16: np.ndarray, sr: int):
    import pyloudnorm as pyln
    x = x16.astype(np.float64) / 32768.0
    try:
        v = float(pyln.Meter(sr).integrated_loudness(x))
    except Exception:
        return None
    return round(v, 2) if math.isfinite(v) else None


# ---------------------------------------------------------------- texto y WER
def normaliza(t: str) -> list:
    return re.sub(r"[^a-z0-9' ]+", " ", t.lower().replace("’", "'")).split()


def wer(ref: str, hip: str) -> float:
    r, h = normaliza(ref), normaliza(hip)
    if not r:
        return 0.0 if not h else 1.0
    prev = list(range(len(h) + 1))
    for i, rw in enumerate(r, 1):
        cur = [i]
        for j, hw in enumerate(h, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rw != hw)))
        prev = cur
    return round(prev[-1] / len(r), 4)


# ---------------------------------------------------------------- 3. un hablante entero
def cargar_fuente(fid: str, trabajo: str) -> Fuente:
    return Fuente(fid, Path(trabajo) / fid)


def fuentes_de(h: str, a) -> list:
    ids = a.fuente or sorted(p.name for p in Path(a.trabajo).iterdir() if p.is_dir())
    out = []
    for fid in ids:
        td = Path(a.trabajo) / fid
        if not fuente_vale(h, fid):
            continue
        faltan = [f for f in ("palabras.json", "diar.json", "hablantes.json", "orig.wav")
                  if not (td / f).exists()]
        if faltan:
            log(f"  {fid}: se omite (faltan {', '.join(faltan)})")
            continue
        hab = leer_json(td / "hablantes.json")
        if any(t.get("hablante") == real(h) and not t.get("descartado")
               for t in hab.get("tramos", [])):
            out.append(fid)
    return out


def procesar(h: str, mod: Modelos, a, salida: Path) -> tuple:
    """Devuelve (candidatos, fuentes usadas). Los clips quedan en <h>/.candidatos_nuevo/;
    `confirmar` los pone en su sitio solo cuando todo (ASR incluido) ha ido bien."""
    huecos = huecos_de(h)
    log(f"== {h}: huecos {', '.join(huecos)}")
    fids = fuentes_de(h, a)
    if not fids:
        log(f"{h}: ninguna fuente con tramos utilizables")
        return [], []
    # --- pool por fuente + metricas
    cands, rech = [], {}
    for fid in fids:
        comprobar_recursos_ligero()
        F = cargar_fuente(fid, str(a.trabajo))
        r_f = {}
        t0 = time.time()
        vent = enumerar(F, h, huecos, a.excluir_extremos, r_f)
        for k, v in r_f.items():
            rech[k] = rech.get(k, 0) + v
        log(f"  {fid}: " + ", ".join(f"{k}={len(v)}" for k, v in vent.items())
            + f" ventanas validas ({time.time()-t0:.1f}s)")
        if a.solo_enumerar:
            continue
        for k, v in vent.items():
            for pre, s, e, ti, pm, pmin, ini, fin, cerca in pool_diverso(v, F, a.pool):
                c0, c1 = F.start[s] - MARGEN, F.end[e] + MARGEN
                x = cortar(F, c0, c1)
                if x.size == 0:
                    rech["corte_vacio"] = rech.get("corte_vacio", 0) + 1
                    continue
                pico = float(np.abs(x.astype(np.int32)).max()) / 32768.0
                if pico >= PICO_MAX:
                    rech["clipping"] = rech.get("clipping", 0) + 1
                    continue
                x16 = a16k(x, F.sr)
                cands.append({
                    "hablante": h, "hueco": k, "fuente": fid, "tramo": ti, "s": s, "e": e,
                    "start": round(float(c0), 3), "end": round(float(c1), 3),
                    "w_start": round(float(F.start[s]), 3), "w_end": round(float(F.end[e]), 3),
                    "dur": round(float(c1 - c0), 3),
                    "texto_largo": " ".join(F.w[s:e + 1]),
                    "chars": len(" ".join(F.w[s:e + 1])),
                    "asr_conf": {"media": round(float(pm), 4), "min": round(float(pmin), 4)},
                    "pico_dbfs": round(20 * math.log10(max(pico, 1e-9)), 2),
                    "inicio_frase": bool(ini), "fin_frase": bool(fin), "cerca": clip01(cerca),
                    "sin_cobertura": bool(F.hab["tramos"][ti].get("sin_cobertura")),
                    "tramo_inicio": F.hab["tramos"][ti]["start"],
                    "dnsmos": mod.dnsmos(x16), "lufs": lufs(x, F.sr),
                    "_emb": mod.embedding(x16),
                })
        log(f"  {fid}: pool evaluado, acumulados {len(cands)} (descartes: {rech})")
        gc.collect()
    if a.solo_enumerar:
        log(f"{h}: rechazos {rech}")
        return [], fids
    if not cands:
        log(f"{h}: sin candidatos")
        return [], fids
    # --- sim contra el centroide
    emb_f = Path(a.emb) / f"{h}.npy"
    if not emb_f.exists() and h == "naval_kapil":
        emb_f = Path(a.emb) / "naval.npy"
    if emb_f.exists():
        cen, sim_ref = np.load(emb_f).astype(np.float64).ravel(), "global"
    else:
        log(f"  AVISO: no existe {emb_f}; sim contra el centroide local del pool")
        cen, sim_ref = centroide_robusto([c["_emb"] for c in cands]), "local"
    cen = cen / (np.linalg.norm(cen) + 1e-12)
    for c in cands:
        c["sim"] = round(float(np.dot(c["_emb"], cen)), 4)
        c["sim_ref"] = sim_ref
        c["puntuacion"] = puntuar(c)
    # --- umbral de similitud: la unica defensa contra una interjeccion sin turno propio
    n0 = len(cands)
    cands = [c for c in cands if c["sim"] >= a.sim_min]
    if len(cands) < n0:
        log(f"  {h}: {n0 - len(cands)} candidatos descartados por sim < {a.sim_min}")
    n0 = len(cands)
    cands = quitar_duplicados(cands)
    if len(cands) < n0:
        log(f"  {h}: {n0 - len(cands)} candidatos de recopilatorio duplicados en otra fuente")
    if not cands:
        log(f"{h}: sin candidatos tras filtrar por sim/duplicados")
        return [], fids
    # --- seleccion
    elegidos = seleccionar(cands, huecos, N_POR_HUECO)
    # --- exportar (a un directorio temporal) + ASR
    nuevo = salida / h / ".candidatos_nuevo"
    shutil.rmtree(nuevo, ignore_errors=True)
    nuevo.mkdir(parents=True, exist_ok=True)
    sf = _sf()
    out = []
    fuentes_ex = {}                       # cada fuente se carga una vez para exportar
    for k in huecos:
        grupo = sorted([c for c in elegidos if c["hueco"] == k], key=lambda c: -c["puntuacion"])
        if len(grupo) < 2:
            log(f"  AVISO: {h} {k}: solo {len(grupo)} candidato(s)")
        for n, c in enumerate(grupo, 1):
            if c["fuente"] not in fuentes_ex:
                fuentes_ex[c["fuente"]] = cargar_fuente(c["fuente"], str(a.trabajo))
            F = fuentes_ex[c["fuente"]]
            x = cortar(F, c["start"], c["end"])
            base = f"{h}_{k}_c{n}"
            sf.write(str(nuevo / f"{base}.wav"), x, F.sr, subtype="PCM_16")
            c["fichero"] = f"{h}/candidatos/{base}.wav"
            c["_x16"] = a16k(x, F.sr)
            c["n"] = n
        out += grupo
    del fuentes_ex
    gc.collect()
    for c in out:
        t0 = time.time()
        c["texto"] = mod.transcribir(c.pop("_x16"))
        c["wer_largo"] = wer(c["texto_largo"], c["texto"])
        c["wer_alto"] = c["wer_largo"] > WER_ALTO
        (nuevo / f"{Path(c['fichero']).stem}.txt").write_text(c["texto"] + "\n", encoding="utf-8")
        log(f"  {c['fichero']}: dur {c['dur']:.1f}s sim {c['sim']:.3f} "
            f"ovrl {c['dnsmos']['ovrl']:.2f} punt {c['puntuacion']:.3f} "
            f"wer {c['wer_largo']:.2f} ({time.time()-t0:.1f}s)")
    for c in out:
        for k in ("_emb", "s", "e", "tramo", "tramo_inicio", "cerca", "inicio_frase", "fin_frase"):
            c.pop(k, None)
    return out, fids


def confirmar(h: str, nuevos: list, salida: Path) -> None:
    """Coloca los clips nuevos (wav + txt) en <h>/candidatos/ con os.replace. Se llama justo
    antes de escribir candidatos.json, cuando el ASR ya ha terminado bien."""
    nuevo = salida / h / ".candidatos_nuevo"
    cdir = salida / h / "candidatos"
    cdir.mkdir(parents=True, exist_ok=True)
    for c in nuevos:
        base = Path(c["fichero"]).stem
        for ext in (".wav", ".txt"):
            os.replace(nuevo / f"{base}{ext}", cdir / f"{base}{ext}")
    shutil.rmtree(nuevo, ignore_errors=True)


def limpiar_antiguos(h: str, nuevos: list, salida: Path) -> None:
    """Borra solo los clips propios de una ejecucion anterior que ya no son candidatos."""
    vivos = {Path(c["fichero"]).stem for c in nuevos}
    for f in (salida / h / "candidatos").glob(f"{h}_ref*_c*.*"):
        if f.stem not in vivos:
            f.unlink()


def centroide_robusto(embs: list) -> np.ndarray:
    """Media de los embeddings sin los claramente ajenos (coseno bajo la mediana)."""
    E = np.array(embs, dtype=np.float64)
    cen = E.mean(axis=0)
    cen /= np.linalg.norm(cen) + 1e-12
    for _ in range(2):
        cos = E @ cen
        keep = cos >= np.median(cos) - 0.15
        if keep.sum() < max(3, len(E) // 2) or keep.all():
            break
        cen = E[keep].mean(axis=0)
        cen /= np.linalg.norm(cen) + 1e-12
    return cen


def ngramas(t: str, n: int = 5) -> set:
    tok = normaliza(t)
    return {tuple(tok[i:i + n]) for i in range(len(tok) - n + 1)}


def quitar_duplicados(cands: list) -> list:
    """Un candidato de nav056/nav167 se descarta si >=50 % de sus 5-gramas aparecen en un
    candidato de otra fuente (el mismo audio puede estar en el original y en el recopilatorio)."""
    ng = [ngramas(c["texto_largo"]) for c in cands]
    out = []
    for i, c in enumerate(cands):
        dup = False
        if c["fuente"] in COMPILADOS and ng[i]:
            for j, d in enumerate(cands):
                if d["fuente"] == c["fuente"] or not ng[j]:
                    continue
                if (d["fuente"] not in COMPILADOS or j < i) and \
                        len(ng[i] & ng[j]) / len(ng[i]) >= 0.5:
                    dup = True
                    break
        if not dup:
            out.append(c)
    return out


def comprobar_recursos_ligero():
    if os.environ.get("NAVAL_PRUEBA") != "1":
        comprobar_recursos(esperar_s=120)


def puntuar(c: dict) -> float:
    return round(0.35 * clip01((c["sim"] - 0.40) / 0.45)
                 + 0.25 * clip01((c["dnsmos"]["ovrl"] - 2.0) / 2.5)
                 + 0.15 * clip01((c["asr_conf"]["media"] - PROB_MEDIA) / (1 - PROB_MEDIA))
                 + 0.05 * clip01((c["asr_conf"]["min"] - PROB_MIN) / (1 - PROB_MIN))
                 + 0.08 * c["inicio_frase"] + 0.08 * c["fin_frase"] + 0.04 * c["cerca"], 4)


def solapa(c: dict, d: dict) -> bool:
    return c["fuente"] == d["fuente"] and c["start"] < d["end"] + 1.0 and c["end"] > d["start"] - 1.0


def seleccionar(cands: list, huecos: dict, n: int) -> list:
    """n por hueco, voraz: puntuacion - penalizacion por repetir tramo/fuente; nunca solapan
    con lo ya elegido (de cualquier hueco del hablante)."""
    elegidos = []
    for k in sorted(huecos, key=lambda k: -huecos[k][0]):   # el hueco largo, el mas dificil, primero
        del_hueco = []
        for _ in range(n):
            mejor, mejor_p = None, -1e9
            for c in cands:
                if c["hueco"] != k or any(solapa(c, d) for d in elegidos):
                    continue
                p = c["puntuacion"]
                p -= 0.08 * sum(d["fuente"] == c["fuente"] and d["tramo"] == c["tramo"]
                                for d in del_hueco)
                p -= 0.04 * sum(d["fuente"] == c["fuente"] for d in del_hueco)
                if p > mejor_p:
                    mejor, mejor_p = c, p
            if mejor is None:
                break
            del_hueco.append(mejor)
            elegidos.append(mejor)
    return elegidos


# ---------------------------------------------------------------- 4. salidas
def escribir_salidas(salida: Path) -> None:
    datos = leer_json(salida / "candidatos.json")
    cs = datos["candidatos"]
    escribir_json(salida / "refs.json", {
        "nota": "Fuente y tiempos (corte con margen) de TODOS los candidatos: la parte 2 "
                "nunca debe meterlos en eval (por tiempos y, para recopilatorios "
                "como nav056/nav167, tambien por texto_norm).",
        "refs": [{**{k: c[k] for k in ("hablante", "hueco", "fichero", "fuente", "start", "end")},
                  "texto_norm": " ".join(normaliza(c.get("texto_largo", "")))}
                 for c in cs]})
    (salida / "escuchar.html").write_text(html_escuchar(cs), encoding="utf-8")


def html_escuchar(cs: list) -> str:
    e = html.escape
    por_h = {}
    for c in cs:
        por_h.setdefault(c["hablante"], {}).setdefault(c["hueco"], []).append(c)
    p = ["<!doctype html><html lang='es'><head><meta charset='utf-8'>",
         "<meta name='viewport' content='width=device-width,initial-scale=1'>",
         "<title>Candidatos de referencia</title><style>",
         ":root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--card:#f4f4f6;--bad:#b3261e}",
         "@media(prefers-color-scheme:dark){:root{--bg:#16161a;--fg:#e8e8ea;--mut:#9a9aa2;"
         "--card:#23232a;--bad:#ff8a80}}",
         "body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;"
         "max-width:880px;margin:0 auto;padding:16px}",
         "h1{font-size:1.4rem}h2{margin-top:2rem;border-bottom:1px solid var(--mut)}",
         "h3{margin:1.2rem 0 .4rem}.c{background:var(--card);border-radius:8px;padding:10px 12px;"
         "margin:8px 0}audio{width:100%}.m{color:var(--mut);font-size:.85rem}"
         ".bad{color:var(--bad);font-weight:600}</style></head><body>",
         "<h1>Candidatos de referencia</h1>",
         "<p class='m'>Pagina local, no publicar. c1 = mejor puntuacion. El texto es la "
         "re-transcripcion del clip solo.</p>"]
    for h in sorted(por_h):
        p.append(f"<h2>{e(h)}</h2>")
        for k in sorted(por_h[h]):
            p.append(f"<h3>{e(k)}</h3>")
            for c in sorted(por_h[h][k], key=lambda c: c["n"]):
                d, a = c["dnsmos"], c["asr_conf"]
                marcas = ""
                if c.get("wer_alto"):
                    marcas += f" <span class='bad'>WER largo {c['wer_largo']:.0%}</span>"
                if c.get("sin_cobertura"):
                    marcas += " <span class='bad'>sin cobertura oficial</span>"
                if c.get("sim_ref") == "local":
                    marcas += " <span class='bad'>sim contra centroide local</span>"
                p.append(
                    f"<div class='c'><b>{e(Path(c['fichero']).stem)}</b>{marcas}"
                    f"<audio controls preload='none' src='{e(c['fichero'])}'></audio>"
                    f"<div>{e(c['texto'])}</div>"
                    f"<div class='m'>{e(c['fuente'])} {c['start']:.1f}-{c['end']:.1f}s "
                    f"({c['dur']:.1f}s, {c['chars']} car.) | punt {c['puntuacion']:.3f} | "
                    f"sim {c['sim']:.3f} | DNSMOS ovrl {d['ovrl']:.2f} sig {d['sig']:.2f} "
                    f"bak {d['bak']:.2f} | asr_conf {a['media']:.3f} (min {a['min']:.2f}) | "
                    f"LUFS {c['lufs']} | pico {c['pico_dbfs']} dBFS</div></div>")
    p.append("</body></html>")
    return "\n".join(p)


# ---------------------------------------------------------------- main
def lista_csv(txt: str) -> list:
    return [x.strip() for x in txt.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hablantes", nargs="*", help="sin indicar: todos los que tengan datos")
    ap.add_argument("--cpu", action="store_true", help="ASR en CPU (tambien con NAVAL_PRUEBA=1)")
    ap.add_argument("--modelo-asr", default=None,
                    help="large-v3 (por defecto; tiny si NAVAL_PRUEBA=1)")
    ap.add_argument("--forzar", action="store_true", help="rehacer hablantes ya presentes")
    ap.add_argument("--salida", type=Path, default=SPEAKER_REFS)
    ap.add_argument("--trabajo", type=Path, default=TRABAJO)
    ap.add_argument("--emb", type=Path, default=DATOS / "emb")
    ap.add_argument("--fuente", type=lista_csv, default=None, metavar="ID[,ID...]",
                    help="limitar a estas fuentes, separadas por comas (nav109,nav072)")
    ap.add_argument("--excluir-extremos", type=float, default=EXTREMOS_S,
                    help="segundos de sintonia a evitar al inicio y al final (45)")
    ap.add_argument("--pool", type=int, default=POOL_POR_FUENTE)
    ap.add_argument("--sim-min", type=float, default=SIM_MIN,
                    help=f"descarta candidatos con sim menor ({SIM_MIN})")
    ap.add_argument("--solo-enumerar", action="store_true",
                    help="solo cuenta ventanas validas (sin audio ni modelos)")
    a = ap.parse_args()
    prueba = os.environ.get("NAVAL_PRUEBA") == "1"
    a.cpu = a.cpu or prueba
    a.modelo_asr = a.modelo_asr or ("tiny" if prueba else "large-v3")
    validos = set(HABLANTES) | {"naval_kapil"}
    malos = [h for h in a.hablantes if h not in validos]
    if malos:
        ap.error(f"hablante desconocido: {malos}; validos: {sorted(validos)}")
    hablantes = a.hablantes or ORDEN_DEFECTO
    if not a.cpu and not a.solo_enumerar:
        asegurar_entorno_cuda()

    cand_f = a.salida / "candidatos.json"
    datos_prev = leer_json(cand_f) if cand_f.exists() else {}
    previos = datos_prev.get("candidatos", [])
    pedidas = dict(datos_prev.get("fuentes_pedidas", {}))   # {h: None (todas) | [ids]}
    hechos = {c["hablante"] for c in previos}

    def ya_hecho(h: str) -> bool:
        if a.forzar or h not in hechos:
            return False
        antes = pedidas.get(h)                  # ausente (formato antiguo) o None: todas
        if antes is None:
            return True
        return bool(a.fuente) and set(a.fuente) <= set(antes)

    # refs.json y escuchar.html son baratos: se regeneran siempre (un corte entre
    # candidatos.json y las salidas no deja nada obsoleto)
    if cand_f.exists() and not a.solo_enumerar:
        escribir_salidas(a.salida)
    pendientes = [h for h in hablantes if not ya_hecho(h)]
    for h in hablantes:
        if h not in pendientes:
            log(f"{h}: ya esta en candidatos.json, se salta (--forzar para rehacer)")
    if not pendientes:
        return
    if not prueba:
        comprobar_recursos()

    mod = Modelos(a.cpu, a.modelo_asr)
    import contextlib
    # el candado se omite en pruebas (la GPU la ocupa el ASR largo; prueba.sh tiene el suyo)
    # y con --solo-enumerar (no carga modelos); --cpu fuera de prueba SI lo toma
    cm = contextlib.nullcontext() if (prueba or a.solo_enumerar) else candado_gpu()
    with cm:
        try:
            for h in pendientes:
                try:
                    nuevos, _ = procesar(h, mod, a, a.salida)
                finally:
                    mod.liberar_asr()           # VRAM libre antes de soltar el candado
                if a.solo_enumerar or not nuevos:
                    continue
                # todo ha ido bien: clips y candidatos.json se actualizan juntos
                confirmar(h, nuevos, a.salida)
                previos = [c for c in previos if c["hablante"] != h] + nuevos
                pedidas[h] = a.fuente
                escribir_json(cand_f, {
                    "generado": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "modelo_asr": a.modelo_asr, "fuentes_pedidas": pedidas,
                    "candidatos": previos})
                limpiar_antiguos(h, nuevos, a.salida)
                escribir_salidas(a.salida)
                hechos.add(h)
        finally:
            mod.liberar_asr()
            gc.collect()
    log(f"listo: {len(previos)} candidatos en {cand_f}")


if __name__ == "__main__":
    main()
