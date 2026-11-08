"""Genera la criba con dots.tts desde un Python 3.12 aparte.

dots-tts exige Python < 3.13 y Colab ya trae 3.13, así que el cuaderno 04 crea un entorno
3.12 con uv y ejecuta este script dentro. Drive ya está montado por el cuaderno.

    /content/venv_dots/bin/python /content/repo/criba/motores/dots_generar.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import comun  # noqa: E402

import torch  # noqa: E402
from dots_tts.runtime import DotsTtsRuntime  # noqa: E402

VARIANTE = "dots_soar"

items, silencio_ms = comun.cargar_items()
refs = comun.comprobar(items)
comun.guardar_entorno(VARIANTE, ["dots-tts", "torch", "transformers"])

precision = "bfloat16" if torch.cuda.is_bf16_supported() else "float16"
modelo = DotsTtsRuntime.from_pretrained("dots-studio/dots.tts-soar", precision=precision, optimize=False)
params = dict(language="es", num_steps=10, guidance_scale=1.2)
print("Modelo cargado,", precision, flush=True)


def sintetizar(texto, ref):
    r = modelo.generate(text=texto, prompt_audio_path=ref["wav"], prompt_text=ref["texto"], **params)
    return r["audio"], r["sample_rate"]


comun.generar(VARIANTE, sintetizar, items, refs, silencio_ms,
              params={"modelo": "dots-studio/dots.tts-soar", "precision": precision, **params})
