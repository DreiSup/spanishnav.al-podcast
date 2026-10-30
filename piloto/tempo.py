"""Acelerar el habla sin cambiar el tono, para el cuaderno 06_tempo.

Usa Rubber Band (el programa `rubberband`), que estira el tiempo conservando el tono y el timbre. Si su
motor fino (R3, opción -3) existe se usa; si no, el estándar. Si `rubberband` no está, cae a `atempo` de
ffmpeg, que también conserva el tono pero suena algo peor en voz.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

import soundfile as sf


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
