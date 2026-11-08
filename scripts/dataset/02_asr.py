#!/usr/bin/env python3
"""Etapa 2: ASR literal con faster-whisper large-v3 (int8, GPU, por lotes).

- Modo por lotes (BatchedInferencePipeline): el VAD de Silero trocea en ventanas de
  ≤30 s y cada ventana se transcribe sin condicionarse a la anterior, así que no hay
  bucles de alucinación y el `initial_prompt` con muletillas se aplica a TODAS las
  ventanas (no solo a la primera, como en el modo secuencial).
- Sin prompt por defecto: en la prueba (nav109, 3 min) el prompt de muletillas hizo
  que Whisper se saltara los primeros 21 s, y el podcast ya viene editado sin muletillas.
- word_timestamps=True: guarda la probabilidad por palabra, que será `asr_conf`.
  Los tiempos finos salen después del alineado de WhisperX (etapa 3).
- Lote 2: con 8, y a veces con 4, la GTX 1650 de 4 GB se queda sin memoria; con 2 se
  pierde solo un ~10 % de velocidad.
  Si aun así falla, solo se repite el trozo afectado, con un lote más pequeño.
- Por trozos de ~10 min cortados en el punto más silencioso, con punto de control por
  trozo en trabajo/<id>/asr_trozos/: un corte o un fallo no obliga a empezar de cero.

Salida trabajo/<id>/asr.json:
  {"modelo", "params", "duracion_s", "segments": [
     {"start", "end", "text", "avg_logprob", "no_speech_prob", "compression_ratio",
      "words": [{"word", "start", "end", "prob"}]}]}

Uso: 02_asr.py <id> [--batch 2] [--beam 5] [--con-prompt]
     02_asr.py --audio x.wav --out y.json   (pruebas sobre un fragmento)
"""
import argparse
import json
import time
from pathlib import Path

from common import (asegurar_entorno_cuda, candado_gpu, comprobar_recursos, escribir_json, log,
                    trabajo_dir)

PROMPT_MULETILLAS = ("Um, so, uh, I mean, you know, I- I think, like, it's, uh... "
                     "Yeah. Hmm. Right, right. So, so the thing is, uh, basically.")


TROZO_S = 600          # ~10 min por trozo: un fallo de VRAM solo repite su trozo
BUSCA_SILENCIO_S = 15  # el corte entre trozos se mueve al tramo más silencioso de ±15 s
SR = 16000


def limites_trozos(audio, trozo_s: int = TROZO_S) -> list[tuple[int, int]]:
    """Límites en muestras, cada ~trozo_s, movidos al mínimo de energía (ventanas de 100 ms)
    para no partir palabras entre trozos."""
    import numpy as np
    n, cortes = len(audio), [0]
    obj = trozo_s * SR
    while n - cortes[-1] > obj + 60 * SR:          # el último trozo puede llegar a trozo_s+60 s
        c = cortes[-1] + obj
        a, b = c - BUSCA_SILENCIO_S * SR, c + BUSCA_SILENCIO_S * SR
        v = audio[a:b]
        hop = SR // 10
        rms = np.sqrt(np.convolve(v.astype("float64") ** 2, np.ones(hop) / hop, mode="valid")[::hop // 4])
        cortes.append(a + int(np.argmin(rms)) * (hop // 4) + hop // 2)
    cortes.append(n)
    return list(zip(cortes[:-1], cortes[1:]))


def transcribir_trozo(pipe, audio, a: int, b: int, batch: int, beam: int, prompt) -> list[dict]:
    off = a / SR
    segs, _ = pipe.transcribe(audio[a:b], language="en", batch_size=batch, beam_size=beam,
                              word_timestamps=True, initial_prompt=prompt,
                              vad_filter=True, temperature=0.0)
    out = []
    for s in segs:
        out.append({
            "start": round(s.start + off, 3), "end": round(s.end + off, 3), "text": s.text.strip(),
            "avg_logprob": round(s.avg_logprob, 4), "no_speech_prob": round(s.no_speech_prob, 4),
            "compression_ratio": round(s.compression_ratio, 3),
            "words": [{"word": w.word, "start": round(w.start + off, 3), "end": round(w.end + off, 3),
                       "prob": round(w.probability, 4)} for w in (s.words or [])],
        })
    return out


def transcribir(audio_path: str, dir_trozos, batch: int, beam: int, prompt) -> dict:
    """Transcribe por trozos con punto de control: cada trozo se guarda en dir_trozos y se
    salta si ya existe. Si la GPU se queda sin memoria, solo ese trozo se repite con un
    lote más pequeño."""
    import gc
    import soundfile as sf
    from faster_whisper import BatchedInferencePipeline, WhisperModel
    audio, sr = sf.read(audio_path, dtype="float32")
    assert sr == SR, f"se esperaba audio a {SR} Hz, no {sr}"
    dur = len(audio) / SR
    lims = limites_trozos(audio)
    dir_trozos.mkdir(parents=True, exist_ok=True)
    def cargar():
        return BatchedInferencePipeline(model=WhisperModel("large-v3", device="cuda",
                                                           compute_type="int8"))
    pipe = cargar()
    t0, lotes, segmentos = time.time(), {}, []
    for k, (a, b) in enumerate(lims):
        fk = dir_trozos / f"trozo_{k:03d}.json"
        if fk.exists():
            segmentos += json.loads(fk.read_text())["segments"]
            continue
        bk = batch
        while True:
            try:
                tk = time.time()
                segs = transcribir_trozo(pipe, audio, a, b, bk, beam, prompt)
                break
            except RuntimeError as e:
                if "out of memory" in str(e).lower() and bk > 1:
                    # Tras un OOM el contexto CUDA de ctranslate2 queda inservible
                    # ("invalid device ordinal"): hay que soltar el modelo y recargarlo.
                    bk //= 2
                    log(f"  trozo {k}: sin memoria en GPU; recargo el modelo y repito con batch={bk}")
                    del pipe
                    gc.collect()
                    time.sleep(10)
                    pipe = cargar()
                    continue
                raise
        lotes[k] = bk
        escribir_json(fk, {"a": a, "b": b, "batch": bk, "segments": segs})
        segmentos += segs
        log(f"  trozo {k+1}/{len(lims)} [{a/SR:.0f}-{b/SR:.0f}s] {len(segs)} seg, "
            f"{(b-a)/SR/(time.time()-tk):.1f}x tiempo real")
    el = time.time() - t0
    log(f"ASR fin: {len(segmentos)} segmentos, {sum(len(s['words']) for s in segmentos)} palabras, "
        f"{el:.0f}s de pared")
    return {"modelo": "faster-whisper large-v3 int8 (batched)",
            "params": {"batch_size": batch, "batch_por_trozo": lotes, "beam_size": beam,
                       "initial_prompt": prompt, "vad_filter": True, "temperature": 0.0,
                       "language": "en", "trozo_s": TROZO_S,
                       "trozos": [[round(a / SR, 3), round(b / SR, 3)] for a, b in lims]},
            "duracion_s": round(dur, 3), "pared_s": round(el, 1), "segments": segmentos}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id", nargs="?")
    ap.add_argument("--audio")
    ap.add_argument("--out")
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--beam", type=int, default=5)
    ap.add_argument("--con-prompt", action="store_true",
                    help="prompt de muletillas; desactivado: en la prueba se saltó 21 s de habla")
    a = ap.parse_args()
    asegurar_entorno_cuda()

    if a.id:
        td = trabajo_dir(a.id)
        audio, salida = str(td / "audio16k.wav"), td / "asr.json"
        if salida.exists():
            log(f"{a.id}: asr.json ya existe, se salta")
            return
    else:
        audio, salida = a.audio, Path(a.out)
    prompt = PROMPT_MULETILLAS if a.con_prompt else None

    comprobar_recursos()
    with candado_gpu():
        log(f"ASR {audio} batch={a.batch} beam={a.beam} prompt={'no' if prompt is None else 'sí'}")
        res = transcribir(audio, salida.parent / (salida.stem + "_trozos"), a.batch, a.beam, prompt)
    escribir_json(salida, res)
    log(f"escrito {salida}")


if __name__ == "__main__":
    main()
