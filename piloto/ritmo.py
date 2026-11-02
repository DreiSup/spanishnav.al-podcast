"""Ritmo del habla generada, para el cuaderno 06_ritmo.

- acortar_pausas: recorta los silencios largos y deja el habla intacta.
- acelerar: estira el tiempo sin cambiar el tono. Probado el 30-oct y descartado de momento: pierde
  naturalidad. Usa Rubber Band (el programa `rubberband`), que estira el tiempo conservando el tono y el timbre. Si su
motor fino (R3, opción -3) existe se usa; si no, el estándar. Si `rubberband` no está, cae a `atempo` de
ffmpeg, que también conserva el tono pero suena algo peor en voz.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

import soundfile as sf

# Decidido por el autor el 30-oct, escuchando 0,35 / 0,25 / 0,18 / 0,12 en 06_ritmo: gana el más apretado.
PAUSA_FABRICA = 0.12


def _ejecutar(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def acelerar(audio, sr, factor):
    """Devuelve (audio acelerado, método usado). factor 1.10 = un 10 % más rápido, mismo tono."""
    if abs(factor - 1.0) < 1e-6:
        return audio, "original"
    with tempfile.TemporaryDirectory() as d:
        ent, sal = Path(d) / "ent.wav", Path(d) / "sal.wav"
        sf.write(str(ent), audio, sr, subtype="FLOAT")
        if shutil.which("rubberband"):
            for motor, opciones in (("rubberband R3", ["-3"]), ("rubberband", [])):
                if _ejecutar(["rubberband", "-q", *opciones, "-T", str(factor), str(ent), str(sal)]):
                    return sf.read(str(sal), dtype="float32")[0], motor
        if _ejecutar(["ffmpeg", "-v", "error", "-y", "-i", str(ent), "-filter:a", f"atempo={factor}", str(sal)]):
            return sf.read(str(sal), dtype="float32")[0], "ffmpeg atempo"
    raise RuntimeError("No se ha podido acelerar: faltan rubberband y ffmpeg")


def _tramos_silencio(audio, sr, umbral_db, ventana=0.02, salto=0.01):
    """Tramos [inicio, fin) en muestras cuyo nivel está `umbral_db` por debajo del pico del clip."""
    import numpy as np
    v, s = int(sr * ventana), int(sr * salto)
    if len(audio) < v:
        return []
    marcos = np.lib.stride_tricks.sliding_window_view(audio, v)[::s]
    db = 20 * np.log10(np.sqrt((marcos ** 2).mean(axis=1)) + 1e-10)
    callado = db < db.max() + umbral_db
    tramos, ini = [], None
    for i, c in enumerate(callado):
        if c and ini is None:
            ini = i
        elif not c and ini is not None:
            tramos.append((ini * s, i * s + v // 2))
            ini = None
    if ini is not None:
        tramos.append((ini * s, len(audio)))
    return tramos


def acortar_pausas(audio, sr, pausa_max=PAUSA_FABRICA, inicio=0.05, final=0.15, umbral_db=-40.0, fundido=0.01):
    """Acorta los silencios sin tocar el habla.

    - Silencio inicial: se deja en `inicio` segundos. Silencio final: en `final`.
    - Silencio interno de más de `pausa_max`: se le quita el centro y queda en `pausa_max`, con medio a cada
      lado y un fundido corto en el empalme. Los más cortos (comas, respiraciones, oclusivas) no se tocan.
    Silencio = más de `umbral_db` por debajo del pico del clip, en ventanas de 20 ms.
    """
    import numpy as np
    tramos = _tramos_silencio(audio, sr, umbral_db)
    if not tramos:
        return audio
    trozos, cursor, f = [], 0, int(sr * fundido)
    for a, b in tramos:
        if a == 0:                                   # silencio inicial
            cursor = max(0, b - int(sr * inicio))
            continue
        if b >= len(audio):                          # silencio final
            trozos.append(audio[cursor:min(len(audio), a + int(sr * final))])
            cursor = len(audio)
            break
        if (b - a) / sr > pausa_max:                 # pausa interna larga
            mitad = int(sr * pausa_max / 2)
            izq, der = audio[cursor:a + mitad], audio[b - mitad:b]
            if f and len(izq) > f and len(der) > f:  # fundido cruzado en el empalme (dentro del silencio)
                rampa = np.linspace(0, 1, f, dtype=audio.dtype)
                mezcla = izq[-f:] * (1 - rampa) + der[:f] * rampa
                izq = np.concatenate([izq[:-f], mezcla])
                der = der[f:]
            trozos += [izq, der]
            cursor = b
    trozos.append(audio[cursor:])
    return np.concatenate(trozos)
