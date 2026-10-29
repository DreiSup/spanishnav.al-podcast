#!/usr/bin/env python3
"""Genera los cuadernos de Colab del piloto de fine-tuning en piloto/cuadernos/.

    python3 piloto/construir_cuadernos.py

Los .ipynb son GENERADOS: se edita este fichero y se regenera. El código común está en
criba/comun.py (Drive, generación sin repetir, desconexión) y piloto/medir.py (WER, similitud).
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / "cuadernos"
RAMA = "claude/quirky-dirac-x18c3n"
REPO = "https://github.com/DreiSup/spanishnav.al-podcast"


def md(texto):
    return {"cell_type": "markdown", "metadata": {}, "source": texto.strip("\n")}


def code(texto):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": texto.strip("\n")}


def cuaderno(nombre, celdas, gpu="T4"):
    nb = {"nbformat": 4, "nbformat_minor": 0,
          "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": gpu},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}},
          "cells": celdas}
    DESTINO.mkdir(exist_ok=True)
    (DESTINO / nombre).write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("escrito", DESTINO / nombre)


PREPARAR = f"""
# 2. Preparar: código del repo, Drive, frases y referencia de Naval
import os, sys, subprocess
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/criba", "/content/repo/piloto"]
import comun

comun.montar_drive()
comun.FRASES = Path("/content/repo/piloto/frases_sinteticas.json")
comun.SALIDA = comun.DRIVE / "piloto" / "sintetico"
ITEMS, SILENCIO_MS = comun.cargar_items()
REFS = comun.comprobar(ITEMS)
"""


def cierre(variante):
    return code(f"""
# Última celda: resumen y desconexión de la GPU
import json
filas = [json.loads(l) for l in (comun.SALIDA / "{variante}" / "registro.jsonl").read_text(encoding="utf-8").splitlines()]
ok = sum(f["ok"] for f in filas)
minutos = sum(f.get("segundos_audio", 0) for f in filas if f["ok"]) / 60
print(f"{variante}: {{ok}} clips correctos ({{minutos:.0f}} min), {{len(filas) - ok}} con error")
comun.desconectar()
""")


def cabecera(titulo, que, minutos):
    return md(f"""
# Piloto de fine-tuning — {titulo}

{que}

Genera las **400 frases** de `piloto/frases_sinteticas.json` (unos 45 min de audio) con la voz de Naval,
usando `speaker_refs/naval/naval_ref02.wav` como referencia. Salida: `fine_tunned_naval/piloto/sintetico/`
en Drive, un `.wav` por frase (`s001` … `s400`).

**GPU:** T4 (o L4 si no hay T4). **Tiempo estimado:** {minutos}.

Uso: celda 1, *Entorno de ejecución → Reiniciar sesión*, y el resto en orden. Si se corta, vuelve a empezar:
lo que ya esté en Drive no se genera otra vez. La última celda sube todo a Drive y desconecta la GPU.
""")


# ---------------------------------------------------------------- Chatterbox V2
cuaderno("01_sintetico_chatterbox.ipynb", [
    cabecera("español sintético con Chatterbox V2",
             "Chatterbox V2 es el profesor sin alucinaciones: en la escucha a ciegas sacó 4,25 de acento nativo "
             "y 5 de «sin alucinaciones». Parámetros por defecto (`exaggeration=0.5`, `cfg_weight=0.5`, "
             "`temperature=0.8`), los mismos de la criba.", "unos 60 min"),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# Desde GitHub: la 0.1.7 de PyPI no tiene el parámetro t3_model. torchvision a juego con torch 2.6.0.
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git@master" torchvision==0.21.0
"""),
    code(PREPARAR),
    code("""
# 3. Generar
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
VARIANTE = "chatterbox_v2"
PARAMS = dict(exaggeration=0.5, cfg_weight=0.5, temperature=0.8)
modelo = ChatterboxMultilingualTTS.from_pretrained(device="cuda", t3_model="v2")
modelo.prepare_conditionals(REFS["naval"]["wav"], exaggeration=PARAMS["exaggeration"])

def sintetizar(texto, ref):
    return modelo.generate(texto, language_id="es", **PARAMS), modelo.sr

comun.guardar_entorno(VARIANTE, ["chatterbox-tts", "torch", "transformers", "numpy"])
comun.generar(VARIANTE, sintetizar, ITEMS, REFS, SILENCIO_MS, params={**PARAMS, "language_id": "es"})
"""),
    cierre("chatterbox_v2"),
])

# ---------------------------------------------------------------- XTTS base
cuaderno("02_sintetico_xtts.ipynb", [
    cabecera("español sintético con XTTS v2 base",
             "XTTS v2 base es el profesor con mejor acento: 4,75 de acento nativo en la escucha a ciegas. Alucina "
             "en bloques largos, pero aquí cada clip es una sola frase y el cuaderno 03 descarta los que fallen. "
             "Parámetros de tu cuaderno de producción: `temperature=0.75`, `repetition_penalty=3.0`, "
             "`top_p=0.8`, `top_k=60`.", "unos 40 min"),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
!pip install -q coqui-tts==0.27.5 "coqui-tts-trainer>=0.3.0,<0.4.0" "transformers==4.57.1"
"""),
    code(PREPARAR),
    code("""
# 3. Generar
import os
os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS
VARIANTE = "xtts_base"
GEN = dict(temperature=0.75, repetition_penalty=3.0, top_p=0.8, top_k=60, length_penalty=1.0,
           enable_text_splitting=False)
modelo = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda").synthesizer.tts_model
GPT, SPK = modelo.get_conditioning_latents(audio_path=[REFS["naval"]["wav"]], gpt_cond_len=12,
                                           gpt_cond_chunk_len=6, max_ref_length=12)

def sintetizar(texto, ref):
    return modelo.inference(texto, "es", GPT, SPK, **GEN)["wav"], 24000

comun.guardar_entorno(VARIANTE, ["coqui-tts", "torch", "transformers"])
comun.generar(VARIANTE, sintetizar, ITEMS, REFS, SILENCIO_MS, params=GEN)
"""),
    cierre("xtts_base"),
])

# ---------------------------------------------------------------- Filtrar y seleccionar
cuaderno("03_filtrar_sintetico.ipynb", [
    md("""
# Piloto de fine-tuning — filtrar y seleccionar el español sintético

Se ejecuta **después** de los cuadernos 01 y 02. Mide cada clip sintético y se queda con los buenos:

1. **WER** con Whisper large-v3: descarta los que no dicen exactamente el texto (alucinaciones, saltos).
2. **Audio que sobra**: descarta los que tienen más de 0,8 s antes de la primera palabra o después de la
   última. Ahí suelen estar los murmullos o sílabas alucinadas que el WER no ve.
3. **Velocidad de habla** en caracteres por segundo: descarta los cortados o estirados.
4. **Similitud** con las referencias de Naval (ECAPA): no descarta, ordena. Entre dos clips buenos de la
   misma frase gana el que más se parece a Naval.

Después elige **una versión por frase** (la mejor de los dos profesores) hasta llegar a los minutos
objetivo, por defecto **40 min**, el 40 % de un entrenamiento con 60 min de inglés real.

Salida en `fine_tunned_naval/piloto/sintetico/`: `medidas.jsonl` (todas las medidas), `seleccion.jsonl`
(los elegidos, con texto, profesor, duración y medidas) e `informe.md`.

**GPU:** T4. **Tiempo estimado:** unos 30 min. Uso: celda 1, reiniciar sesión, y el resto en orden.
Lo ya medido no se vuelve a medir.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
!pip install -q jiwer speechbrain librosa soundfile num2words
"""),
    code(f"""
# 2. Preparar
import os, sys, subprocess, json
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/criba", "/content/repo/piloto"]
import comun, medir

comun.montar_drive()
comun.FRASES = Path("/content/repo/piloto/frases_sinteticas.json")
SINT = comun.DRIVE / "piloto" / "sintetico"
ITEMS, _ = comun.cargar_items()
TEXTO = {{it["id"]: it["frases"][0] for it in ITEMS}}
PROFESORES = sorted(p.name for p in SINT.iterdir() if (p / "registro.jsonl").exists())
CLIPS = [(v, i) for v in PROFESORES for i in TEXTO if (SINT / v / f"{{i}}.wav").exists()]
print("Profesores:", PROFESORES, "| clips a medir:", len(CLIPS))
"""),
    code("""
# 3. Medir: WER, velocidad de habla y similitud con Naval
MEDIDAS = SINT / "medidas.jsonl"
hecho = medir.cargar(MEDIDAS)
pendientes = [(v, i) for v, i in CLIPS if (v, i) not in hecho]
print("Pendientes:", len(pendientes))
if pendientes:
    asr, ecapa = medir.Asr(), medir.Ecapa()
    ref_naval = ecapa.referencia(sorted((comun.REFS / "naval").glob("naval_ref0*.wav")))
    for n, (v, i) in enumerate(pendientes, 1):
        wav = SINT / v / f"{i}.wav"
        hyp, inicio, fin = asr.transcribe(wav)
        dur = medir.duracion(wav)
        fila = {"variante": v, "id": i, "wer": medir.wer(TEXTO[i], hyp), "transcripcion": hyp,
                "segundos": round(dur, 2), "cps": round(len(TEXTO[i]) / dur, 1),
                "sobra_inicio": round(inicio, 2) if inicio is not None else None,
                "sobra_final": round(dur - fin, 2) if fin is not None else None,
                "similitud": ecapa.similitud(wav, ref_naval)}
        medir.anadir(MEDIDAS, fila)
        hecho[(v, i)] = fila
        if n % 50 == 0:
            print(f"  {n}/{len(pendientes)}")
    del asr, ecapa
    comun.liberar()
print("Medidos:", len(hecho))
"""),
    code("""
# 4. Filtrar y seleccionar
WER_MAX = 0.05        # tolera una palabra mal transcrita por el ASR en una frase larga
CPS = (9, 22)         # fuera de ahí, el clip está cortado o estirado
SOBRA_MAX = 0.8       # segundos de audio antes de la primera palabra o después de la última:
                      # más que eso suele ser un murmullo o una sílaba alucinada que el WER no ve
MIN_OBJETIVO = 40     # minutos de español: 40 % frente a 60 min de inglés real

def limpio(f):
    return (f["sobra_inicio"] is not None and f["sobra_final"] is not None
            and f["sobra_inicio"] <= SOBRA_MAX and f["sobra_final"] <= SOBRA_MAX)

filas = list(hecho.values())
buenos = [f for f in filas if f["wer"] <= WER_MAX and CPS[0] <= f["cps"] <= CPS[1] and limpio(f)]
# Una versión por frase: la de menor WER y, a igualdad, la que más se parece a Naval
mejor = {}
for f in sorted(buenos, key=lambda f: (f["wer"], -f["similitud"])):
    mejor.setdefault(f["id"], f)
ordenados = sorted(mejor.values(), key=lambda f: (f["wer"], -f["similitud"]))
seleccion, minutos = [], 0.0
for f in ordenados:
    if minutos >= MIN_OBJETIVO:
        break
    seleccion.append({**f, "texto": TEXTO[f["id"]], "audio": f"piloto/sintetico/{f['variante']}/{f['id']}.wav"})
    minutos += f["segundos"] / 60

(SINT / "seleccion.jsonl").write_text("".join(json.dumps(s, ensure_ascii=False) + "\\n" for s in seleccion),
                                      encoding="utf-8")
lineas = ["# Español sintético: filtro y selección", "",
          f"Umbrales: WER <= {WER_MAX}, caracteres/s entre {CPS[0]} y {CPS[1]}, como mucho {SOBRA_MAX} s de audio "
          f"antes de la primera palabra o después de la última. Objetivo: {MIN_OBJETIVO} min.", "",
          "| Profesor | Clips | Pasan el filtro | Elegidos | Min elegidos | WER medio | Similitud media |",
          "|---|---|---|---|---|---|---|"]
for v in PROFESORES:
    tot = [f for f in filas if f["variante"] == v]
    ok = [f for f in buenos if f["variante"] == v]
    sel = [f for f in seleccion if f["variante"] == v]
    lineas.append(f"| {v} | {len(tot)} | {len(ok)} | {len(sel)} | {sum(f['segundos'] for f in sel) / 60:.1f} | "
                  f"{sum(f['wer'] for f in tot) / max(len(tot), 1):.3f} | "
                  f"{sum(f['similitud'] for f in tot) / max(len(tot), 1):.3f} |")
lineas += ["", f"**Total elegido: {len(seleccion)} clips, {minutos:.1f} min**, de {len(mejor)} frases con al menos "
           f"una versión buena."]
informe = "\\n".join(lineas)
(SINT / "informe.md").write_text(informe + "\\n", encoding="utf-8")
print(informe)
"""),
    code("""
# 5. Subir a Drive y desconectar
comun.desconectar()
"""),
])
