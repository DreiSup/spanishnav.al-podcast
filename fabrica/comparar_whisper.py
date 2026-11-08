"""¿Puede un Whisper más rápido sustituir al de siempre en la revisión de la fábrica?

La revisión no cambia el audio: solo decide qué frases se repiten. Así que basta con comprobar que la configuración
nueva toma las mismas decisiones que la de siempre (large-v3 con marcas por palabra) sobre frases ya generadas, y que
caza los fallos que la revisión existe para cazar. El cuaderno `fabrica/comparar_whisper.ipynb` lo hace en una T4:

1. Toma frases reales de episodios ya generados (`tts/frases/*.wav`, su texto y **la decisión que tomó large-v3 al
   generarlas**, del registro), con todas las que quedaron sospechosas. Así no hace falta volver a pasar large-v3.
2. Les añade **averías fabricadas**, que deberían marcarse como malas:
   - «cola»: tras la frase, 1,5 s de otra frase (lo que deja una alucinación al final);
   - «corte»: solo el primer 55 % de la frase (el TTS se calla antes de tiempo).
3. Cada configuración las oye **en un proceso aparte** (`python comparar_whisper.py oir …`): al acabar, la GPU queda
   limpia del todo para la siguiente (el 8-nov, cargar turbo detrás de large-v3 en el mismo proceso agotó la memoria).
4. Aplica la regla de la fábrica (`fabrica.revisar` y `voces.json` → verificacion) y compara.

Una configuración vale si coincide con la decisión de large-v3 en al menos el 97 % de las frases reales y caza al
menos el 95 % de las averías.
"""
import json
import pickle
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parent.parent / "piloto")]
import fabrica  # noqa: E402

SR = 16000
ACUERDO_MIN, CAZA_MIN = 0.97, 0.95


def audio_16k(ruta):
    """El wav de una frase, mono a 16 kHz, sin librosa: en Colab, librosa tira de numba y numba puede romperse tras un
    pip sin reiniciar («module 'numba' has no attribute 'core'», 8-nov). scipy remuestrea igual de bien para esto."""
    from math import gcd
    import soundfile as sf
    from scipy.signal import resample_poly
    a, sr = sf.read(str(ruta), dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    if sr != SR:
        g = gcd(SR, sr)
        a = resample_poly(a, SR // g, sr // g).astype(np.float32)
    return a


def frases_de(carpetas, n, semilla=0):
    """Hasta `n` frases reales de esas carpetas de episodio: todas las sospechosas y el resto al azar (fijo)."""
    todas = []
    for carpeta in carpetas:
        tts = carpeta / "tts"
        for fichero, fila in fabrica.leer_registro(carpeta).items():
            for d in fila.get("frases", []):
                ruta = fabrica.ruta_frase(tts, fichero, d["k"])
                if ruta.exists() and d.get("ok") is not None:
                    todas.append({"episodio": carpeta.name, "clip": fichero, "k": d["k"] + 1, "texto": d["texto"],
                                  "ruta": str(ruta), "ok_registro": d.get("ok"), "tipo": "real"})
    malas = [f for f in todas if f["ok_registro"] is False]
    resto = [f for f in todas if f["ok_registro"] is not False]
    random.Random(semilla).shuffle(resto)
    return malas + resto[:max(0, n - len(malas))]


def con_averias(items, n, semilla=0):
    """Las frases reales (con su audio a 16 kHz en `audio`) más `n` averías fabricadas a partir de ellas."""
    rng = random.Random(semilla)
    reales = [i for i in items if i["tipo"] == "real" and len(i["audio"]) > SR * 2]
    averias = []
    for j in range(n):
        base = reales[j % len(reales)]
        if j % 2 == 0:
            otra = reales[rng.randrange(len(reales))]["audio"]
            mitad = len(otra) // 2
            trozo = otra[max(0, mitad - int(0.75 * SR)): mitad + int(0.75 * SR)]
            audio = np.concatenate([base["audio"], np.zeros(int(0.15 * SR), np.float32), trozo])
            tipo = "cola"
        else:
            audio = base["audio"][: int(len(base["audio"]) * 0.55)]
            tipo = "corte"
        averias.append({**base, "audio": audio.astype(np.float32), "tipo": tipo, "ok_registro": False})
    return items + averias


def decidir(items, oidos, cfg_ver):
    """La decisión de la fábrica (fabrica.revisar) para cada item, con lo que oyó un modelo."""
    salida = []
    for item, oido in zip(items, oidos):
        ok, errores, palabras, sobra, hyp = fabrica.revisar(item["texto"], item["audio"], SR, None, cfg_ver,
                                                            tuple(oido))
        salida.append({"ok": ok, "errores": errores, "sobra": sobra, "hyp": hyp})
    return salida


def oir(modelo, marcas, items_pkl, salida_json, lote):
    """Lo que corre en el proceso aparte: carga una configuración, oye todos los items y guarda lo oído y el tiempo."""
    import torch
    import medir
    from transformers.utils import logging as hf_logging
    hf_logging.set_verbosity_error()
    items = pickle.loads(Path(items_pkl).read_bytes())
    asr = medir.Asr(modelo, marcas)
    asr.transcribe_lote([items[0]["audio"]], SR)   # calentar: la primera llamada no cuenta
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    oidos = asr.transcribe_lote([i["audio"] for i in items], SR, batch_size=lote)
    torch.cuda.synchronize()
    res = {"modelo": modelo, "marcas": marcas, "segundos": time.time() - t0, "oidos": oidos,
           "pico_gb": torch.cuda.max_memory_allocated() / 2 ** 30, "lote": getattr(asr, "lote_que_cabe", lote)}
    Path(salida_json).write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    print(f"{modelo} ({marcas}): {res['segundos']:.0f} s, pico {res['pico_gb']:.1f} GB, lote {res['lote']}")


def informe(items, resultados, cfg_ver):
    """(texto markdown, {nombre: vale}). `resultados` = {nombre: lo que guardó `oir`}; la referencia de las frases
    reales es la decisión de large-v3 del registro, y la de las averías, que son malas."""
    reales = [n for n, i in enumerate(items) if i["tipo"] == "real"]
    averias = [n for n, i in enumerate(items) if i["tipo"] != "real"]
    audio_s = sum(len(i["audio"]) for i in items) / SR
    lineas = ["# Whisper para la revisión: configuraciones frente a large-v3 (marcas por palabra)", "",
              f"{len(reales)} frases reales ({sum(items[n]['ok_registro'] is False for n in reales)} que large-v3 "
              f"marcó sospechosas al generarlas) y {len(averias)} averías fabricadas; {audio_s / 60:.1f} min de "
              f"audio. Vale si coincide con large-v3 en ≥ {ACUERDO_MIN:.0%} de las reales y caza ≥ {CAZA_MIN:.0%} de "
              "las averías.", "",
              "| Configuración | Decisiones iguales (reales) | Averías cazadas | Tiempo | s por s de audio | "
              "Pico GPU | Lote | Veredicto |", "|---|---|---|---|---|---|---|---|"]
    veredictos, detalle = {}, []
    for nombre, r in resultados.items():
        dec = decidir(items, r["oidos"], cfg_ver)
        iguales = sum(dec[n]["ok"] == items[n]["ok_registro"] for n in reales)
        caza = sum(dec[n]["ok"] is False for n in averias)
        acuerdo, cazado = iguales / max(1, len(reales)), caza / max(1, len(averias))
        vale = acuerdo >= ACUERDO_MIN and cazado >= CAZA_MIN
        veredictos[nombre] = vale
        lineas.append(f"| {nombre} | {iguales} de {len(reales)} ({100 * acuerdo:.1f} %) | {caza} de {len(averias)} | "
                      f"{r['segundos']:.0f} s | {r['segundos'] / audio_s:.2f} | {r['pico_gb']:.1f} GB | {r['lote']} | "
                      f"**{'VALE' if vale else 'NO VALE'}** |")
        malas = [n for n in reales if dec[n]["ok"] != items[n]["ok_registro"]] + \
                [n for n in averias if dec[n]["ok"] is not False]
        if malas:
            detalle += ["", f"## {nombre}: donde no coincide", ""]
            for n in malas[:40]:
                i, d = items[n], dec[n]
                esperado = ("mal" if i["ok_registro"] is False else "bien") if i["tipo"] == "real" else "mal"
                detalle += [f"- **{i['tipo']}** · {i['episodio']} · {i['clip']} frase {i['k']}: debía salir "
                            f"{esperado}, sale {'bien' if d['ok'] else 'mal'} ({d['errores']} err., "
                            f"{d['sobra']} s tras la última marca)",
                            f"  - Texto: {i['texto']}", f"  - Oyó: {d['hyp']}"]
    return "\n".join(lineas + detalle) + "\n", veredictos


if __name__ == "__main__" and len(sys.argv) >= 6 and sys.argv[1] == "oir":
    oir(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6]) if len(sys.argv) > 6 else 8)
