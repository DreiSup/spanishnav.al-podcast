#!/usr/bin/env python3
"""Etapa 3: alineado forzado WhisperX (wav2vec2 inglés) para tiempos finos de palabra.

Entrada: trabajo/<id>/asr.json (etapa 2) y trabajo/<id>/audio16k.wav (etapa 1).
Salida:  trabajo/<id>/palabras.json (formato en CONTRATO.md):
  {"modelo_alineado", "stats": {"n", "sin_tiempo", "sin_prob", "desajuste_pct", ...},
   "words": [{"i", "w", "start", "end", "prob", "align_score", "seg", "ts_ok"}]}

Cómo trabaja
- `whisperx.load_align_model("en")` + `align()` se llaman segmento a segmento sobre el
  texto de asr.json. WhisperX solo aporta los TIEMPOS (start/end/align_score); la
  probabilidad `prob` sale de faster-whisper (asr.json) y es la futura `asr_conf`.
- La lista de salida se construye sobre las palabras de faster-whisper (no se pierde
  ninguna aunque WhisperX descarte alguna). El emparejado WhisperX <-> faster-whisper se
  hace por segmento y por texto normalizado (difflib sobre tokens en minúsculas sin
  puntuación ni acentos), nunca por índice global. `desajuste_pct` = % de palabras que
  no quedaron en bloques idénticos.
- `ts_ok: false` (nunca punto de corte ni de pausa) cuando: WhisperX no dio tiempo y se usa
  el de faster-whisper o el interpolado; la palabra lleva dígitos/símbolos (el alineador
  los trata como comodín, así que su tiempo no es fiable); WhisperX dio un tiempo
  incoherente; o el segmento entero falló al alinear.
- Ventana de audio con holgura: a cada segmento se le pasa al alineador el audio de
  [start - pad_izq, end + pad_der] (pad_izq <= 0,3 s, pad_der <= 0,6 s, siempre dejando
  >= 0,1 s hasta el segmento vecino). faster-whisper recorta el end del segmento sobre la
  última palabra y CTC fuerza el último token contra el borde: sin holgura la última
  palabra sale truncada. El texto y las palabras no cambian.
- Bordes: la primera y la última palabra de cada segmento pasan a ts_ok false si su
  align_score < 0,3 (o < 0,5 con el end pegado al end del segmento). SCORE_MIN = 0,3.
- Al final se fuerza el orden monótono entre segmentos (start >= end anterior).
- Si falla el alineado de forma sistemática (> 5 % de segmentos fallidos o > 10 % sin
  palabras de WhisperX, o falta nltk punkt_tab) el script sale con error y NO escribe
  palabras.json, para que etapa.sh reintente.
- El texto que se le pasa al alineador lleva cada palabra sin puntuación (la puntuación
  se alinearía como comodín y alargaría el final de la palabra). `w` en la salida
  conserva mayúsculas y puntuación de faster-whisper. `--texto-literal` desactiva la
  limpieza (solo para diagnóstico).
- Memoria: el audio NO se carga entero. Se lee con soundfile en ventanas de ≤ ~10 min
  (solo los rangos de los segmentos) y se desplazan los tiempos a la ventana; un episodio
  de 3,6 h usa lo mismo que uno de 10 min. Coste lineal en nº de segmentos.
- Sin GPU en pruebas: `--cpu` o la variable NAVAL_PRUEBA=1 fuerzan CPU (y no toman el
  candado de la GPU).

Uso: 03_alinear.py <id> [--forzar] [--cpu]
     03_alinear.py --asr x.json --audio x.wav --out y.json [--cpu]
"""
import argparse
import difflib
import gc
import math
import os
import re
import resource
import time
import unicodedata

from common import (asegurar_entorno_cuda, candado_gpu, comprobar_recursos, escribir_json,
                    leer_json, log, trabajo_dir)

SR = 16000
SCORE_MIN = 0.3              # align_score por debajo: tiempo dudoso -> ts_ok false
BORDE_SCORE_MIN = 0.3        # 1a/última palabra del segmento: por debajo, ts_ok false
BORDE_PEGADO_MIN = 0.5       # ... y si su end roza el end del segmento, se exige más
PAD_IZQ_MAX = 0.3            # holgura de audio antes del inicio del segmento (s)
PAD_DER_MAX = 0.6            # holgura de audio tras el final del segmento (s)
PAD_GAP_MIN = 0.1            # hueco que se deja siempre hasta el segmento vecino (s)
MAX_FALLIDOS = 0.05          # fracción de segmentos que puede fallar al alinear
MAX_SIN_WX = 0.10            # fracción de segmentos sin ninguna palabra de WhisperX
VENTANA_S = 600.0            # audio en memoria a la vez (segundos)
_RE_NO_ALNUM = re.compile(r"[^0-9a-z']+")
_RE_DIGITO = re.compile(r"[0-9]")
_RE_LETRA_O_NUM = re.compile(r"[0-9a-z]")


# ---------------------------------------------------------------- texto

def _base(s: str) -> str:
    """Minúsculas, sin acentos, apóstrofos rectos."""
    s = s.replace("’", "'").replace("‘", "'").replace("`", "'")
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def normalizar(w: str) -> str:
    """Token para comparar: minúsculas, sin puntuación ni acentos (conserva ' y dígitos)."""
    return _RE_NO_ALNUM.sub("", _base(w)).strip("'")


def limpiar_alineador(w: str) -> str:
    """Palabra tal como se la damos al alineador (sin puntuación)."""
    return normalizar(w)


def tiene_simbolos(w: str) -> bool:
    """Dígitos o letras fuera del alfabeto del alineador: su tiempo no es fiable."""
    return bool(_RE_DIGITO.search(_base(w)))


# ---------------------------------------------------------------- audio

class AudioPorVentanas:
    """Lee rangos de un WAV 16 kHz mono sin cargarlo entero."""

    def __init__(self, ruta: str):
        import soundfile as sf
        self.sf = sf
        info = sf.info(ruta)
        if info.samplerate != SR:
            raise SystemExit(f"{ruta}: se esperaba 16 kHz y es {info.samplerate} Hz")
        self.ruta = ruta
        self.n = info.frames
        self.dur = info.frames / SR
        self.canales = info.channels

    def leer(self, t0: float, t1: float):
        import numpy as np
        a = max(0, int(round(t0 * SR)))
        b = min(self.n, int(round(t1 * SR)))
        if b <= a:
            return np.zeros(0, dtype="float32")
        x, _ = self.sf.read(self.ruta, start=a, stop=b, dtype="float32", always_2d=True)
        return x.mean(axis=1) if x.shape[1] > 1 else x[:, 0]


# ---------------------------------------------------------------- alineado

def alinear_segmento(modelo, meta, device, audio_t, seg_texto: str, t0: float, t1: float):
    """Devuelve la lista de palabras de WhisperX [{word,start,end,score}] (tiempos relativos
    a la ventana) o None si falla. `audio_t` es un tensor (1, N)."""
    import torch
    from whisperx import align
    for intento in (0, 1):
        try:
            r = align([{"start": t0, "end": t1, "text": seg_texto}], modelo, meta, audio_t,
                      device, return_char_alignments=False)
            return r["word_segments"]
        except RuntimeError as e:
            if "out of memory" in str(e).lower() and intento == 0:
                gc.collect()
                if device != "cpu":
                    torch.cuda.empty_cache()
                continue
            log(f"  aviso: align falló en [{t0:.1f},{t1:.1f}]: {str(e)[:120]}")
            return None
        except Exception as e:  # texto raro, backtrack imposible, etc.
            log(f"  aviso: align falló en [{t0:.1f},{t1:.1f}]: {type(e).__name__}: {str(e)[:120]}")
            return None
    return None


def asegurar_punkt():
    """whisperx.align necesita el tokenizador punkt_tab de nltk. Si falta y no hay red,
    cada segmento fallaría en silencio: mejor abortar antes de empezar."""
    import nltk
    from nltk.data import load as nltk_load
    ruta = "tokenizers/punkt_tab/english.pickle"
    try:
        nltk_load(ruta)
        return
    except LookupError:
        pass
    nltk.download("punkt_tab", quiet=True)
    try:
        nltk_load(ruta)
    except LookupError:
        raise SystemExit("falta nltk punkt_tab y no se pudo descargar (sin red?): "
                         "ejecuta nltk.download('punkt_tab') con red")


def forzar_orden_global(palabras: list) -> int:
    """Pasada final entre segmentos: start >= end de la palabra anterior y end >= start.
    Una palabra que hay que mover más de 20 ms pierde ts_ok. Devuelve cuántas se movieron."""
    movidas, prev_end = 0, None
    for p in palabras:
        s, e = p["start"], p["end"]
        if prev_end is not None and s < prev_end:
            if prev_end - s > 0.02:
                p["ts_ok"] = False
            movidas += 1
            s = prev_end
        if e < s:
            if s - e > 0.02:
                p["ts_ok"] = False
            e = s
        p["start"], p["end"] = s, e
        prev_end = e
    return movidas


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def fusionar_segmento(sidx: int, seg: dict, wx: list | None, off: float, score_min: float = SCORE_MIN):
    """Fusiona palabras faster-whisper y WhisperX de UN segmento por texto normalizado.

    Devuelve (palabras, n_desajuste, n_comparables, fallo_total). Las palabras llevan
    start/end ya en tiempo absoluto o None (se interpolan después).

    Bordes: la primera y la última palabra con tiempo de WhisperX pasan a ts_ok false si
    su align_score < BORDE_SCORE_MIN, o si su end roza el end del segmento (>= end - 0,02 s)
    con align_score < BORDE_PEGADO_MIN: CTC las fuerza contra el borde de la ventana y
    su tiempo no es fiable como punto de corte."""
    fw = seg.get("words") or []
    texto = (seg.get("text") or "").strip()
    if not fw:                                    # segmento sin palabras en asr.json
        fw = [{"word": t, "start": None, "end": None, "prob": None} for t in texto.split()]
        sin_fw = True
    else:
        sin_fw = False

    # tokens normalizables de cada lado
    a_idx = [k for k, w in enumerate(fw) if normalizar(w["word"])]
    wx = wx or []
    b_idx = [k for k, w in enumerate(wx) if normalizar(w.get("word", ""))]
    a_tok = [normalizar(fw[k]["word"]) for k in a_idx]
    b_tok = [normalizar(wx[k]["word"]) for k in b_idx]

    pareja = {}                                   # índice fw -> índice wx
    desajuste = 0
    sm = difflib.SequenceMatcher(None, a_tok, b_tok, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for d in range(i2 - i1):
                pareja[a_idx[i1 + d]] = b_idx[j1 + d]
        else:
            desajuste += max(i2 - i1, j2 - j1)
            if op == "replace" and (i2 - i1) == (j2 - j1):
                for d in range(i2 - i1):          # misma longitud: se emparejan igual
                    pareja[a_idx[i1 + d]] = b_idx[j1 + d]

    out = []
    for k, w in enumerate(fw):
        txt = w["word"].strip()
        prob = _num(w.get("prob"))
        fs, fe = _num(w.get("start")), _num(w.get("end"))
        ws, we, sc, ts_ok, de_wx = None, None, None, False, False
        j = pareja.get(k)
        if j is not None:
            x = wx[j]
            xs, xe, sc = _num(x.get("start")), _num(x.get("end")), _num(x.get("score"))
            if xs is not None and xe is not None and xe >= xs:
                ws, we, de_wx = xs + off, xe + off, True
                ts_ok = not tiene_simbolos(txt) and (sc is None or sc >= score_min)
        if ws is None and fs is not None and fe is not None and fe >= fs:
            ws, we, ts_ok = fs, fe, False         # tiempo de faster-whisper
        if not _RE_LETRA_O_NUM.search(_base(txt)):
            ts_ok = False                         # solo puntuación/símbolos
        out.append({"w": txt, "start": ws, "end": we, "prob": prob,
                    "align_score": sc, "seg": sidx, "ts_ok": ts_ok, "_wx": de_wx})
    con_wx = [p for p in out if p["_wx"]]
    if con_wx:
        s1 = _num(seg.get("end"))
        for p in {id(con_wx[0]): con_wx[0], id(con_wx[-1]): con_wx[-1]}.values():
            sc = p["align_score"]
            if sc is None:
                continue
            pegada = s1 is not None and p["end"] >= s1 - 0.02
            if sc < BORDE_SCORE_MIN or (pegada and sc < BORDE_PEGADO_MIN):
                p["ts_ok"] = False
    comparables = len(a_tok)
    return out, (0 if sin_fw else desajuste), comparables, len(b_tok) == 0


def interpolar(palabras: list, s0: float, s1: float) -> int:
    """Rellena los None entre vecinas con ts_ok True/False conocidas; devuelve cuántas."""
    n, cuenta = len(palabras), 0
    k = 0
    while k < n:
        if palabras[k]["start"] is not None:
            k += 1
            continue
        j = k
        while j < n and palabras[j]["start"] is None:
            j += 1
        a = palabras[k - 1]["end"] if k > 0 else s0
        b = palabras[j]["start"] if j < n else s1
        if b < a:
            b = a
        pesos = [max(1, len(p["w"])) for p in palabras[k:j]]
        tot, acum = float(sum(pesos)), 0.0
        for p, pe in zip(palabras[k:j], pesos):
            p["start"] = a + (b - a) * acum / tot
            acum += pe
            p["end"] = a + (b - a) * acum / tot
            p["ts_ok"] = False
            cuenta += 1
        k = j
    return cuenta


def validar_orden(palabras: list) -> int:
    """Las palabras con tiempo de WhisperX son anclas (monótonas entre sí). Una palabra con
    tiempo de faster-whisper solo se conserva si cabe entre la palabra anterior y la
    siguiente ancla; si no, se anula para interpolarla. Devuelve cuántas se anularon."""
    n, anuladas = len(palabras), 0
    sig = [None] * n                       # inicio de la siguiente ancla
    nxt = None
    for k in range(n - 1, -1, -1):
        sig[k] = nxt
        if palabras[k]["_wx"] and palabras[k]["start"] is not None:
            nxt = palabras[k]["start"]
    prev_end = None
    for k, p in enumerate(palabras):
        if p["start"] is not None and not p["_wx"]:
            ok = (prev_end is None or p["start"] >= prev_end - 1e-6) and \
                 (sig[k] is None or p["end"] <= sig[k] + 1e-6)
            if not ok:
                p["start"] = p["end"] = None
                anuladas += 1
        if p["end"] is not None:
            prev_end = p["end"]
    return anuladas


def agrupar_ventanas(segs: list[dict], dur: float):
    """Grupos consecutivos de segmentos cuyo rango total cabe en VENTANA_S."""
    grupos, actual = [], []
    for sidx, s in enumerate(segs):
        if actual and s["end"] - segs[actual[0]]["start"] > VENTANA_S:
            grupos.append(actual)
            actual = []
        actual.append(sidx)
    if actual:
        grupos.append(actual)
    return grupos


def alinear_episodio(asr: dict, ruta_audio: str, device: str, texto_literal: bool) -> dict:
    import numpy as np
    import torch
    from whisperx import load_align_model
    from whisperx.alignment import DEFAULT_ALIGN_MODELS_TORCH

    segs = asr["segments"]
    audio = AudioPorVentanas(ruta_audio)
    log(f"audio {ruta_audio}: {audio.dur:.1f}s, {len(segs)} segmentos")

    asegurar_punkt()
    nombre_modelo = DEFAULT_ALIGN_MODELS_TORCH["en"]
    modelo, meta = load_align_model("en", device)
    log(f"modelo de alineado {nombre_modelo} en {device}")

    palabras, stats = [], {"desajuste": 0, "comparables": 0, "seg_fallidos": 0,
                           "seg_sin_wx": 0, "interpoladas": 0}
    t0, ultimo = time.time(), time.time()
    for grupo in agrupar_ventanas(segs, audio.dur):
        # holgura a ambos lados: el último token de CTC se pega al borde de la ventana,
        # y faster-whisper recorta el end del segmento sobre la última palabra
        ini = max(0.0, float(segs[grupo[0]]["start"]) - PAD_IZQ_MAX)
        fin = min(audio.dur, float(segs[grupo[-1]]["end"]) + PAD_DER_MAX + PAD_GAP_MIN)
        x = audio.leer(ini, fin)
        audio_t = torch.from_numpy(np.ascontiguousarray(x)).unsqueeze(0)
        dur_ventana = len(x) / SR
        for sidx in grupo:
            seg = segs[sidx]
            s0, s1 = float(seg["start"]), float(seg["end"])
            fw = seg.get("words") or []
            if fw and not texto_literal:
                partes = [limpiar_alineador(w["word"]) for w in fw]
                texto = " ".join(p for p in partes if p)
            elif fw:
                texto = " ".join(w["word"].strip() for w in fw)
            else:
                texto = (seg.get("text") or "").strip()
                if not texto_literal:
                    texto = " ".join(p for p in (limpiar_alineador(t) for t in texto.split()) if p)
            prev_end = float(segs[sidx - 1]["end"]) if sidx > 0 else None
            sig_start = float(segs[sidx + 1]["start"]) if sidx + 1 < len(segs) else None
            hueco_izq = (s0 - prev_end) if prev_end is not None else PAD_IZQ_MAX * 2
            hueco_der = (sig_start - s1) if sig_start is not None else PAD_DER_MAX + PAD_GAP_MIN
            pad_izq = max(0.0, min(PAD_IZQ_MAX, hueco_izq / 2))
            pad_der = max(0.0, min(PAD_DER_MAX, hueco_der - PAD_GAP_MIN))
            a0 = max(ini, s0 - pad_izq)
            a1 = s1 + pad_der
            r0 = a0 - ini
            r1 = min(a1 - ini, dur_ventana)
            wx = None
            if texto and s1 > s0 and r1 > r0 and r0 < dur_ventana:
                wx = alinear_segmento(modelo, meta, device, audio_t, texto, r0, r1)
                if wx is None:
                    stats["seg_fallidos"] += 1
            ps, desaj, comp, sin_wx = fusionar_segmento(sidx, seg, wx, ini)
            if sin_wx and ps:
                stats["seg_sin_wx"] += 1
            stats["desajuste"] += desaj
            stats["comparables"] += comp
            validar_orden(ps)
            stats["interpoladas"] += interpolar(ps, s0, max(s1, s0))
            palabras.extend(ps)
            if time.time() - ultimo > 60:
                el = time.time() - t0
                log(f"  seg {sidx + 1}/{len(segs)}  {s1:7.0f}/{audio.dur:.0f}s "
                    f"x{s1 / max(el, 1e-6):.1f} tiempo real")
                ultimo = time.time()
        del x, audio_t
        gc.collect()
        if device != "cpu":
            torch.cuda.empty_cache()

    # un fallo sistemático no debe dejar un palabras.json inútil que "se salta si existe"
    nseg = len(segs)
    if stats["seg_fallidos"] > MAX_FALLIDOS * nseg or stats["seg_sin_wx"] > MAX_SIN_WX * nseg:
        raise SystemExit(f"alineado degradado: {stats['seg_fallidos']} segmentos fallidos y "
                         f"{stats['seg_sin_wx']} sin palabras de WhisperX de {nseg}; "
                         "no se escribe palabras.json")
    movidas = forzar_orden_global(palabras)
    if movidas:
        log(f"  orden global: {movidas} palabras desplazadas para mantener la monotonía")

    # índice global y estadísticas
    for i, p in enumerate(palabras):
        p["i"] = i
        for k in ("start", "end"):
            p[k] = round(p[k], 3)
        if p["align_score"] is not None:
            p["align_score"] = round(p["align_score"], 3)
        p = {k: p[k] for k in ("i", "w", "start", "end", "prob", "align_score", "seg", "ts_ok")}
        palabras[i] = p
    n = len(palabras)
    stats_out = {
        "n": n,
        "sin_tiempo": sum(1 for p in palabras if not p["ts_ok"]),
        "sin_prob": sum(1 for p in palabras if p["prob"] is None),
        "desajuste_pct": round(100.0 * stats["desajuste"] / max(1, stats["comparables"]), 2),
        "n_segmentos": len(segs),
        "seg_fallidos": stats["seg_fallidos"],
        "seg_sin_alinear": stats["seg_sin_wx"],
        "tiempo_interpolado": stats["interpoladas"],
        "orden_corregido": movidas,
    }
    el = time.time() - t0
    log(f"alineado: {n} palabras, ts_ok=false {stats_out['sin_tiempo']}, "
        f"desajuste {stats_out['desajuste_pct']}%, {el:.0f}s de pared, "
        f"RAM pico {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024} MB")
    del modelo
    gc.collect()
    return {"modelo_alineado": f"whisperx {_version_whisperx()} load_align_model('en') -> "
                               f"torchaudio {nombre_modelo}",
            "stats": stats_out, "words": palabras}


def _version_whisperx() -> str:
    try:
        from importlib.metadata import version
        return version("whisperx")
    except Exception:
        return "?"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("id", nargs="?")
    ap.add_argument("--asr")
    ap.add_argument("--audio")
    ap.add_argument("--out")
    ap.add_argument("--cpu", action="store_true", help="fuerza CPU (también NAVAL_PRUEBA=1)")
    ap.add_argument("--forzar", action="store_true", help="rehacer aunque la salida exista")
    ap.add_argument("--texto-literal", action="store_true",
                    help="diagnóstico: pasa al alineador el texto con puntuación")
    a = ap.parse_args()

    if a.id:
        td = trabajo_dir(a.id)
        asr_p, audio_p, salida = td / "asr.json", td / "audio16k.wav", td / "palabras.json"
    elif a.asr and a.audio and a.out:
        from pathlib import Path
        asr_p, audio_p, salida = Path(a.asr), Path(a.audio), Path(a.out)
    else:
        ap.error("indica <id> o bien --asr, --audio y --out")
    if salida.exists() and not a.forzar:
        log(f"{salida} ya existe, se salta (usa --forzar para rehacer)")
        return
    for f in (asr_p, audio_p):
        if not f.exists():
            raise SystemExit(f"falta {f}")

    cpu = a.cpu or os.environ.get("NAVAL_PRUEBA") == "1"
    if not cpu:
        asegurar_entorno_cuda()
    comprobar_recursos(min_ram_mb=1500 if cpu else 2500)

    asr = leer_json(asr_p)
    if not asr.get("segments"):
        raise SystemExit(f"{asr_p}: sin segmentos")

    if cpu:
        res = alinear_episodio(asr, str(audio_p), "cpu", a.texto_literal)
    else:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            log("CUDA no disponible; se usa CPU")
        with candado_gpu():
            res = alinear_episodio(asr, str(audio_p), device, a.texto_literal)
    escribir_json(salida, res)
    log(f"escrito {salida}")


if __name__ == "__main__":
    main()
