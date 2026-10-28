#!/usr/bin/env python3
"""Etapa 4: diarización con pyannote community-1 (VBx), según CONTRATO.md.

- Modelo `pyannote/speaker-diarization-community-1`; token con `common.token_hf()`.
- `min_speakers = len(hablantes)`, `max_speakers = len(hablantes) + 1` (no `num_speakers`
  exacto), con los hablantes de `fuentes_podcast.json`.
- Salida trabajo/<id>/diar.json:
    {"modelo", "trozos": null | [...], "turnos": [{start, end, label}],
     "exclusivo": [{start, end, label}], "solapes": [{start, end}],
     "embeddings": {label: [...]}}
  `turnos` lleva los solapes; `exclusivo` es `exclusive_speaker_diarization` de pyannote 4;
  `solapes` son los intervalos donde coinciden >=2 etiquetas de `turnos`.
- Episodio entero por defecto SOLO si dura <= 5400 s (`--max-entero`). Por encima, pasa solo
  a `--trozos 3600`: el clustering VBx de pyannote hace un `linkage` O(n^2) sobre todos los
  embeddings activos (n ~ 13k-26k en 3,6 h = 1,4-5,4 GB de matriz condensada) y con el tope
  de cgroup de 5,5 GB el kernel mata el proceso (rc 137) sin dejar que salte el fallback.
  Si falla por falta de memoria de GPU y el audio es más largo que un trozo, reintenta con
  `--trozos 3600`.
- Checkpoint por trozo: cada trozo terminado se guarda en `trabajo/<id>/diar_trozos/t<k>.json`
  (en modo --audio, `<out>.parciales/`) con su firma de parámetros; al reanudar se cargan los
  que coinciden y se borra el directorio al escribir diar.json.
- `--trozos N`: trozos de N s con 30 s de solape; etiquetas `T<k>_SPEAKER_00`. Cada trozo
  solo aporta su tramo "propio" (el solape entre trozos se reparte por la mitad), para que
  los turnos de trozos distintos no coincidan y no fabriquen falsos solapes. En `trozos`
  van los límites: {k, start, end (lo diarizado), propio_start, propio_end}. Los
  embeddings de cada etiqueta salen de todo el trozo (incluido el solape). La etapa 06
  une las etiquetas de trozos distintos por coseno de sus embeddings.
- RAM: el audio se lee con soundfile por trozos (un solo trozo en memoria); en modo entero
  se carga una vez como float32 (0,83 GB por 3,6 h; solo si dura <= 5400 s). El clustering
  de pyannote es O(n^2) en los embeddings: por eso el límite de arriba.
- GPU: `asegurar_entorno_cuda()` + `candado_gpu()`. Con `--cpu` o NAVAL_PRUEBA=1 usa CPU, sin
  candado ni re-exec (prueba.sh ya serializa).

Uso: 04_diarizar.py <id> [--trozos 3600] [--forzar]
     04_diarizar.py --audio x.wav --out y.json --min 2 --max 3 [--cpu] [--trozos 60]
"""
import argparse
import contextlib
import gc
import os
import shutil
import time
from pathlib import Path

from common import (asegurar_entorno_cuda, candado_gpu, comprobar_recursos, escribir_json,
                    fuente, leer_json, log, token_hf, trabajo_dir)

MODELO = "pyannote/speaker-diarization-community-1"
SOLAPE_TROZOS_S = 30.0
SR = 16000
LIMITE_ENTERO_S = 5400.0  # por encima, nunca se intenta entero (linkage O(n^2) mata por RAM)
TROZOS_AUTO_S = 3600.0


# ---------------------------------------------------------------- audio

def duracion_audio(audio: str) -> tuple[float, int]:
    import soundfile as sf
    info = sf.info(audio)
    return info.frames / info.samplerate, info.samplerate


def leer_tramo(audio: str, t0: float, t1: float | None):
    """Lee [t0, t1) de un wav como tensor (1, T) float32 mono. Devuelve (tensor, sr)."""
    import numpy as np
    import soundfile as sf
    import torch
    with sf.SoundFile(audio) as f:
        sr = f.samplerate
        f.seek(int(round(t0 * sr)))
        frames = -1 if t1 is None else max(0, int(round((t1 - t0) * sr)))
        x = f.read(frames, dtype="float32", always_2d=True)
    if x.shape[1] > 1:
        x = x.mean(axis=1, keepdims=True)
    return torch.from_numpy(np.ascontiguousarray(x.T)), sr


# ---------------------------------------------------------------- utilidades de intervalos

def calcular_solapes(turnos: list[dict]) -> list[dict]:
    """Intervalos donde coinciden >=2 etiquetas distintas. O(n log n) por barrido."""
    eventos = []
    for t in turnos:
        if t["end"] > t["start"]:
            eventos.append((t["start"], 1, t["label"]))
            eventos.append((t["end"], -1, t["label"]))
    eventos.sort(key=lambda e: (e[0], e[1]))  # a igual tiempo, cierres antes que aperturas
    activos: dict[str, int] = {}
    solapes, ini = [], None
    for tiempo, delta, lab in eventos:
        activos[lab] = activos.get(lab, 0) + delta
        if activos[lab] <= 0:
            del activos[lab]
        if len(activos) >= 2:
            if ini is None:
                ini = tiempo
        elif ini is not None:
            if tiempo > ini:
                if solapes and ini - solapes[-1]["end"] < 1e-6:
                    solapes[-1]["end"] = round(tiempo, 3)
                else:
                    solapes.append({"start": round(ini, 3), "end": round(tiempo, 3)})
            ini = None
    return solapes


def recortar(turnos: list[dict], a: float, b: float) -> list[dict]:
    """Recorta los turnos a la ventana [a, b]; descarta los que quedan vacíos."""
    out = []
    for t in turnos:
        s, e = max(t["start"], a), min(t["end"], b)
        if e - s > 1e-3:
            out.append({"start": round(s, 3), "end": round(e, 3), "label": t["label"]})
    return out


# ---------------------------------------------------------------- pyannote

def cargar_pipeline(device: str, lote: int):
    import torch
    from pyannote.audio import Pipeline
    pipe = Pipeline.from_pretrained(MODELO, token=token_hf())
    if pipe is None:
        raise RuntimeError(f"no se pudo cargar {MODELO} (¿token HF o licencia sin aceptar?)")
    pipe.to(torch.device(device))
    # El config trae 32; en la GTX 1650 (4 GB compartida) es demasiado.
    pipe.segmentation_batch_size = lote
    pipe.embedding_batch_size = lote
    return pipe


def anotacion_a_turnos(ann, prefijo: str = "", offset: float = 0.0) -> list[dict]:
    out = [{"start": round(seg.start + offset, 3), "end": round(seg.end + offset, 3),
            "label": prefijo + str(lab)}
           for seg, _, lab in ann.itertracks(yield_label=True)]
    out.sort(key=lambda t: (t["start"], t["end"], t["label"]))
    return out


def embeddings_de(salida, prefijo: str = "") -> dict:
    """Embeddings por etiqueta, en el orden de speaker_diarization.labels()."""
    import numpy as np
    emb = salida.speaker_embeddings
    if emb is None:
        return {}
    labels = list(salida.speaker_diarization.labels())
    out = {}
    for i, lab in enumerate(labels):
        if i >= len(emb):
            break
        v = np.asarray(emb[i], dtype="float64")
        if not np.isfinite(v).all() or not np.any(v):
            continue  # relleno de ceros que mete pyannote para etiquetas sin centroide
        out[prefijo + str(lab)] = [round(float(x), 6) for x in v]
    return out


def diarizar_waveform(pipe, wav, sr, uri: str, mn: int, mx: int):
    t0 = time.time()
    ultimo = [t0]

    def hook(paso, artefacto=None, file=None, completed=None, total=None):
        if completed is not None and total and time.time() - ultimo[0] > 60:
            log(f"    {paso}: {completed}/{total}")
            ultimo[0] = time.time()

    salida = pipe({"waveform": wav, "sample_rate": sr, "uri": uri},
                  min_speakers=mn, max_speakers=mx, hook=hook)
    log(f"    diarizado {wav.shape[1] / sr:.0f}s de audio en {time.time() - t0:.0f}s")
    return salida


def liberar():
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass


def diarizar_entero(pipe, audio: str, mn: int, mx: int) -> dict:
    wav, sr = leer_tramo(audio, 0.0, None)
    salida = diarizar_waveform(pipe, wav, sr, "ep", mn, mx)
    del wav
    turnos = anotacion_a_turnos(salida.speaker_diarization)
    excl = anotacion_a_turnos(salida.exclusive_speaker_diarization)
    emb = embeddings_de(salida)
    del salida
    return {"trozos": None, "turnos": turnos, "exclusivo": excl, "embeddings": emb}


def limites_trozos(dur: float, n: float) -> list[dict]:
    """Trozos de n s con 30 s de solape; cada uno es "dueño" hasta la mitad del solape."""
    lim, k, ini = [], 0, 0.0
    while ini < dur - 1e-6:
        fin = min(ini + n + SOLAPE_TROZOS_S, dur)
        lim.append({"k": k, "start": round(ini, 3), "end": round(fin, 3)})
        if fin >= dur - 1e-6:
            break
        k += 1
        ini += n
    for i, z in enumerate(lim):
        z["propio_start"] = z["start"] if i == 0 else round(z["start"] + SOLAPE_TROZOS_S / 2, 3)
        z["propio_end"] = z["end"] if i == len(lim) - 1 else round(lim[i + 1]["start"] + SOLAPE_TROZOS_S / 2, 3)
    # Un último trozo diminuto (<= solape) no aporta nada propio: se funde con el anterior.
    if len(lim) > 1 and lim[-1]["end"] - lim[-1]["propio_start"] < 1.0:
        lim.pop()
        lim[-1]["end"] = round(dur, 3)
        lim[-1]["propio_end"] = round(dur, 3)
    return lim


def firma_trozo(z: dict, n: float, mn: int, mx: int) -> dict:
    """Parámetros que invalidan un checkpoint de trozo si cambian."""
    return {"modelo": MODELO, "min": mn, "max": mx, "n": n, "solape": SOLAPE_TROZOS_S,
            "k": z["k"], "start": z["start"], "end": z["end"],
            "propio_start": z["propio_start"], "propio_end": z["propio_end"]}


def cargar_checkpoint(cache: Path | None, z: dict, firma: dict):
    if cache is None:
        return None
    f = cache / f"t{z['k']}.json"
    if not f.exists():
        return None
    try:
        d = leer_json(f)
        if d.get("firma") == firma and all(k in d for k in ("turnos", "exclusivo", "embeddings")):
            return d
    except (OSError, ValueError):
        pass
    log(f"  checkpoint {f.name} inválido o de otros parámetros, se rehace")
    return None


def diarizar_trozos(pipe, audio: str, dur: float, n: float, mn: int, mx: int,
                    cache: Path | None = None) -> dict:
    lim = limites_trozos(dur, n)
    log(f"{len(lim)} trozos de {n:.0f}s (+{SOLAPE_TROZOS_S:.0f}s de solape)")
    turnos, excl, emb = [], [], {}
    for z in lim:
        pref = f"T{z['k']}_"
        firma = firma_trozo(z, n, mn, mx)
        previo = cargar_checkpoint(cache, z, firma)
        if previo is not None:
            log(f"  trozo {z['k'] + 1}/{len(lim)}: checkpoint, se reutiliza")
            turnos += previo["turnos"]
            excl += previo["exclusivo"]
            emb.update(previo["embeddings"])
            continue
        log(f"  trozo {z['k'] + 1}/{len(lim)}: {z['start']:.0f}-{z['end']:.0f}s")
        wav, sr = leer_tramo(audio, z["start"], z["end"])
        salida = diarizar_waveform(pipe, wav, sr, f"trozo{z['k']}", mn, mx)
        del wav
        a, b = z["propio_start"], z["propio_end"]
        t_k = recortar(anotacion_a_turnos(salida.speaker_diarization, pref, z["start"]), a, b)
        e_k = recortar(anotacion_a_turnos(salida.exclusive_speaker_diarization, pref, z["start"]), a, b)
        m_k = embeddings_de(salida, pref)
        del salida
        liberar()
        turnos += t_k
        excl += e_k
        emb.update(m_k)
        if cache is not None:
            escribir_json(cache / f"t{z['k']}.json",
                          {"firma": firma, "turnos": t_k, "exclusivo": e_k, "embeddings": m_k})
    turnos.sort(key=lambda t: (t["start"], t["end"], t["label"]))
    excl.sort(key=lambda t: (t["start"], t["end"], t["label"]))
    # Una etiqueta sin turnos propios tras el recorte no sirve para 06.
    vivas = {t["label"] for t in turnos} | {t["label"] for t in excl}
    emb = {k: v for k, v in emb.items() if k in vivas}
    return {"trozos": lim, "turnos": turnos, "exclusivo": excl, "embeddings": emb}


def es_oom(e: Exception) -> bool:
    return "out of memory" in str(e).lower()


def diarizar(audio: str, mn: int, mx: int, trozos: float | None, device: str, lote: int,
             cache: Path | None = None, limite_entero: float = LIMITE_ENTERO_S) -> dict:
    dur, sr = duracion_audio(audio)
    if sr != SR:
        log(f"AVISO: {audio} está a {sr} Hz, no a {SR}; pyannote lo remuestreará")
    log(f"diarización {audio}: {dur:.0f}s ({dur / 3600:.2f} h), min={mn} max={mx}, "
        f"device={device}, lote={lote}, trozos={trozos}")
    if trozos is None and dur > limite_entero:
        trozos = TROZOS_AUTO_S
        log(f"{dur:.0f}s > {limite_entero:.0f}s: el clustering entero es O(n^2) en RAM; "
            f"se usan trozos de {trozos:.0f}s")
    pipe = cargar_pipeline(device, lote)
    t0 = time.time()
    try:
        if trozos:
            res = diarizar_trozos(pipe, audio, dur, trozos, mn, mx, cache)
        else:
            oom = False
            try:
                res = diarizar_entero(pipe, audio, mn, mx)
            except (RuntimeError, MemoryError) as e:
                if not (es_oom(e) or isinstance(e, MemoryError)) or dur <= 3600 + SOLAPE_TROZOS_S:
                    raise
                oom = True
                log(f"sin memoria entero ({e}); reintento con --trozos 3600")
            if oom:
                # Fuera del except: así el traceback ya no retiene los tensores CUDA ni el wav.
                liberar()
                res = diarizar_trozos(pipe, audio, dur, TROZOS_AUTO_S, mn, mx, cache)
    finally:
        del pipe
        liberar()
    res["solapes"] = calcular_solapes(res["turnos"])
    res["modelo"] = MODELO
    res["params"] = {"min_speakers": mn, "max_speakers": mx, "device": device,
                     "lote": lote, "solape_trozos_s": SOLAPE_TROZOS_S if res["trozos"] else None}
    res["duracion_s"] = round(dur, 3)
    res["pared_s"] = round(time.time() - t0, 1)
    etiquetas = sorted({t["label"] for t in res["turnos"]})
    log(f"diarización fin: {len(res['turnos'])} turnos, {len(res['exclusivo'])} exclusivos, "
        f"{len(res['solapes'])} solapes, {len(etiquetas)} etiquetas, "
        f"{len(res['embeddings'])} embeddings, {res['pared_s']:.0f}s")
    orden = ["modelo", "params", "duracion_s", "pared_s", "trozos", "turnos", "exclusivo",
             "solapes", "embeddings"]
    return {k: res[k] for k in orden}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("id", nargs="?")
    ap.add_argument("--audio")
    ap.add_argument("--out")
    ap.add_argument("--min", type=int, help="min_speakers (por defecto len(hablantes))")
    ap.add_argument("--max", type=int, help="max_speakers (por defecto len(hablantes)+1)")
    ap.add_argument("--trozos", type=float, default=None,
                    help="diariza por trozos de N segundos con 30 s de solape (ej. 3600)")
    ap.add_argument("--lote", type=int, default=None,
                    help="batch de segmentación y embeddings (GPU 16, CPU 8)")
    ap.add_argument("--max-entero", type=float, default=LIMITE_ENTERO_S, dest="max_entero",
                    help="duración (s) por encima de la cual no se intenta entero (5400)")
    ap.add_argument("--cpu", action="store_true", help="CPU (también con NAVAL_PRUEBA=1)")
    ap.add_argument("--forzar", action="store_true", help="rehace aunque la salida exista")
    a = ap.parse_args()

    if a.id:
        if a.audio or a.out:
            ap.error("<id> no se combina con --audio/--out")
        try:
            n_h = len(fuente(a.id)["hablantes"])
        except KeyError as e:
            ap.error(str(e.args[0]))
        td = trabajo_dir(a.id)  # después de validar el id: no deja directorios basura
        audio, salida = str(td / "audio16k.wav"), td / "diar.json"
        cache = td / "diar_trozos"
        mn = a.min if a.min is not None else n_h
        mx = a.max if a.max is not None else n_h + 1
    elif a.audio and a.out:
        if a.min is None or a.max is None:
            ap.error("con --audio hacen falta --min y --max")
        audio, salida, cache = a.audio, a.out, Path(a.out + ".parciales")
        mn, mx = a.min, a.max
    else:
        ap.error("hace falta <id> o bien --audio y --out")
    if mn > mx:
        ap.error(f"--min {mn} > --max {mx}")

    if Path(salida).exists() and not a.forzar:
        log(f"{salida} ya existe, se salta (--forzar para rehacer)")
        return
    if not Path(audio).exists():
        raise SystemExit(f"no existe el audio {audio}")
    if a.trozos is not None and a.trozos <= 0:
        ap.error("--trozos debe ser > 0")
    if a.forzar and cache.exists():
        shutil.rmtree(cache, ignore_errors=True)  # --forzar rehace también los trozos

    cpu = a.cpu or os.environ.get("NAVAL_PRUEBA") == "1"
    if cpu:
        device, lote = "cpu", a.lote or 8
        ctx = contextlib.nullcontext()
    else:
        asegurar_entorno_cuda()
        device, lote = "cuda", a.lote or 16
        ctx = candado_gpu()
    with ctx:
        # Con el candado ya tomado: la RAM comprobada es la que de verdad queda libre.
        comprobar_recursos()
        res = diarizar(audio, mn, mx, a.trozos, device, lote, cache, a.max_entero)
    escribir_json(salida, res)
    shutil.rmtree(cache, ignore_errors=True)
    log(f"escrito {salida}")


if __name__ == "__main__":
    main()
