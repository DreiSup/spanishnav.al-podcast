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
    """gpu=None: cuaderno de CPU, sin acelerador."""
    meta = {"colab": {"provenance": []}, "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"}}
    if gpu:
        meta["accelerator"] = "GPU"
        meta["colab"]["gpuType"] = gpu
    nb = {"nbformat": 4, "nbformat_minor": 0, "metadata": meta, "cells": celdas}
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
    md("""
# Piloto de fine-tuning — español sintético con Chatterbox V2

Genera la parte en español del entrenamiento de cada voz: las **400 frases** de
`piloto/frases_sinteticas.json` (unos 45 min de audio) dichas con la voz del hablante, clonada con
Chatterbox V2 a partir de su referencia `speaker_refs/<voz>/<voz>_ref02.wav`. Chatterbox V2 es el profesor
sin alucinaciones: en la escucha a ciegas sacó 4,25 de acento nativo y 5 de «sin alucinaciones». Parámetros
por defecto (`exaggeration=0.5`, `cfg_weight=0.5`, `temperature=0.8`), los mismos que con Naval.

Salida en Drive: `fine_tunned_naval/piloto/sintetico/<voz>/chatterbox_v2/` (`s001` … `s400`). Naval ya
está hecho (en `piloto/sintetico/chatterbox_v2/`). Después, el cuaderno 03 filtra los clips de cada voz.

**GPU:** T4 (o L4). **Tiempo estimado:** unos 60 min por voz en T4. Se puede hacer una voz por sesión:
pon solo esa en `VOCES`.

Uso: celda 1, *Entorno de ejecución → Reiniciar sesión*, y el resto en orden. Si se corta, vuelve a empezar:
lo que ya esté en Drive no se genera otra vez. La última celda sube todo a Drive y desconecta la GPU.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# Desde GitHub: la 0.1.7 de PyPI no tiene el parámetro t3_model. torchvision a juego con torch 2.6.0.
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git@master" torchvision==0.21.0
"""),
    code("""
# 2. Parámetros
VOCES = ["nivi", "brett", "deutsch"]   # Naval ya está hecho
PARAMS = dict(exaggeration=0.5, cfg_weight=0.5, temperature=0.8)
"""),
    code(f"""
# 3. Preparar: código del repo, Drive, frases y referencias
import os, sys, subprocess, json
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/criba", "/content/repo/piloto"]
import comun, rutas

comun.montar_drive()
comun.FRASES = Path("/content/repo/piloto/frases_sinteticas.json")
FRASES, SILENCIO_MS = comun.cargar_items()
# Las mismas 400 frases para cada voz; solo cambia la referencia
ITEMS = {{voz: [{{**it, "voz": voz, "ref": voz}} for it in FRASES] for voz in VOCES}}
REFS = comun.comprobar([it for items in ITEMS.values() for it in items])
for voz in VOCES:
    hechos = len(list((rutas.sintetico(comun.DRIVE, voz) / "chatterbox_v2").glob("s*.wav")))
    print(f"  {{voz}}: {{hechos}} de {{len(ITEMS[voz])}} clips ya generados")
"""),
    code("""
# 4. Generar, voz a voz
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
VARIANTE = "chatterbox_v2"
modelo = ChatterboxMultilingualTTS.from_pretrained(device="cuda", t3_model="v2")

def sintetizar(texto, ref):
    return modelo.generate(texto, language_id="es", **PARAMS), modelo.sr

for voz in VOCES:
    print(f"=== {voz}")
    comun.SALIDA = rutas.sintetico(comun.DRIVE, voz)
    modelo.prepare_conditionals(REFS[voz]["wav"], exaggeration=PARAMS["exaggeration"])
    comun.guardar_entorno(VARIANTE, ["chatterbox-tts", "torch", "transformers", "numpy"])
    comun.generar(VARIANTE, sintetizar, ITEMS[voz], REFS, SILENCIO_MS, params={**PARAMS, "language_id": "es", "voz": voz})
"""),
    code("""
# 5. Resumen, subir a Drive y desconectar
for voz in VOCES:
    reg = rutas.sintetico(comun.DRIVE, voz) / "chatterbox_v2" / "registro.jsonl"
    filas = [json.loads(l) for l in reg.read_text(encoding="utf-8").splitlines() if l.strip()]
    ok = [f for f in filas if f["ok"]]
    print(f"{voz}: {len(ok)} clips correctos ({sum(f['segundos_audio'] for f in ok) / 60:.0f} min), "
          f"{len(filas) - len(ok)} con error")
comun.desconectar()
"""),
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

Se ejecuta **después** del cuaderno 01, para una voz cada vez (`VOZ`). Mide cada clip sintético y se queda
con los buenos:

1. **WER** con Whisper large-v3: descarta los que no dicen exactamente el texto (alucinaciones, saltos).
2. **Audio que sobra al final**: descarta los que tienen más de 0,8 s después de la última palabra. Ahí
   suelen estar los murmullos o sílabas alucinadas que el WER no ve. (El del principio no se puede medir:
   Whisper marca siempre la primera palabra en 0,0 s.)
3. **Velocidad de habla** en caracteres por segundo: descarta los cortados o estirados.
4. **Similitud** con las referencias de la voz (ECAPA): no descarta, ordena. Entre dos clips buenos de la
   misma frase gana el que más se parece.

Después elige **una versión por frase** hasta los minutos objetivo: por defecto, los que hacen falta para
que el español sea el **40 %** frente al inglés real de su dataset (`datasets/<voz>/`).

Salida en `fine_tunned_naval/piloto/sintetico/<voz>/` (la de Naval, en `piloto/sintetico/`):
`medidas.jsonl` (todas las medidas), `seleccion.jsonl` (los elegidos, con texto, duración y medidas) e
`informe.md`. Solo se usa el profesor Chatterbox V2: XTTS quedó descartado.

**GPU:** T4. **Tiempo estimado:** unos 15 min por voz. Uso: celda 1, reiniciar sesión, y el resto en orden.
Lo ya medido no se vuelve a medir. Para otra voz, cambia `VOZ` y ejecuta de la celda 2 en adelante.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
!pip install -q jiwer speechbrain librosa soundfile num2words
"""),
    code(f"""
# 2. Preparar
VOZ = "nivi"          # nivi, brett o deutsch (naval ya está hecho)

import os, sys, subprocess, json
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/criba", "/content/repo/piloto"]
import comun, medir, rutas

comun.montar_drive()
comun.FRASES = Path("/content/repo/piloto/frases_sinteticas.json")
SINT = rutas.sintetico(comun.DRIVE, VOZ)
ITEMS, _ = comun.cargar_items()
TEXTO = {{it["id"]: it["frases"][0] for it in ITEMS}}
PROFESORES = ["chatterbox_v2"]
CLIPS = [(v, i) for v in PROFESORES for i in TEXTO if (SINT / v / f"{{i}}.wav").exists()]
print(VOZ, "| clips a medir:", len(CLIPS))
if not CLIPS:
    raise SystemExit(f"No hay clips en {{SINT / 'chatterbox_v2'}}: ejecuta antes el cuaderno 01 con esta voz.")
"""),
    code("""
# 3. Medir: WER, velocidad de habla y similitud con la voz
MEDIDAS = SINT / "medidas.jsonl"
hecho = medir.cargar(MEDIDAS)
pendientes = [(v, i) for v, i in CLIPS if (v, i) not in hecho]
print("Pendientes:", len(pendientes))
if pendientes:
    asr, ecapa = medir.Asr(), medir.Ecapa()
    ref_voz = ecapa.referencia(sorted((comun.REFS / VOZ).glob(f"{VOZ}_ref0*.wav")))
    for n, (v, i) in enumerate(pendientes, 1):
        wav = SINT / v / f"{i}.wav"
        hyp, inicio, fin = asr.transcribe(wav)
        dur = medir.duracion(wav)
        fila = {"variante": v, "id": i, "wer": medir.wer(TEXTO[i], hyp), "transcripcion": hyp,
                "segundos": round(dur, 2), "cps": round(len(TEXTO[i]) / dur, 1),
                "sobra_inicio": round(inicio, 2) if inicio is not None else None,
                "sobra_final": round(dur - fin, 2) if fin is not None else None,
                "similitud": ecapa.similitud(wav, ref_voz)}
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
SOBRA_MAX = 0.8       # segundos de audio después de la última palabra: más suele ser un murmullo alucinado
FRAC_ES = 0.4         # el español, 40 % de los minutos del entrenamiento
en_train = [json.loads(l) for l in (rutas.dataset(comun.DRIVE, VOZ) / "metadata.jsonl").read_text(
    encoding="utf-8").splitlines() if l.strip()]
MIN_INGLES = sum(f["dur"] for f in en_train if f["split"] == "train") / 60
MIN_OBJETIVO = MIN_INGLES * FRAC_ES / (1 - FRAC_ES)

def limpio(f):
    return f["sobra_final"] is not None and f["sobra_final"] <= SOBRA_MAX

filas = list(hecho.values())
buenos = [f for f in filas if f["wer"] <= WER_MAX and CPS[0] <= f["cps"] <= CPS[1] and limpio(f)]
# Una versión por frase: la de menor WER y, a igualdad, la que más se parece a la voz
mejor = {}
for f in sorted(buenos, key=lambda f: (f["wer"], -f["similitud"])):
    mejor.setdefault(f["id"], f)
ordenados = sorted(mejor.values(), key=lambda f: (f["wer"], -f["similitud"]))
relativa = SINT.relative_to(comun.DRIVE)
seleccion, minutos = [], 0.0
for f in ordenados:
    if minutos >= MIN_OBJETIVO:
        break
    seleccion.append({**f, "texto": TEXTO[f["id"]], "audio": f"{relativa}/{f['variante']}/{f['id']}.wav"})
    minutos += f["segundos"] / 60

(SINT / "seleccion.jsonl").write_text("".join(json.dumps(s, ensure_ascii=False) + "\\n" for s in seleccion),
                                      encoding="utf-8")
lineas = [f"# Español sintético de {VOZ}: filtro y selección", "",
          f"Umbrales: WER <= {WER_MAX}, caracteres/s entre {CPS[0]} y {CPS[1]}, como mucho {SOBRA_MAX} s de audio "
          f"después de la última palabra. Objetivo: {MIN_OBJETIVO:.1f} min, el {FRAC_ES:.0%} frente a "
          f"{MIN_INGLES:.1f} min de inglés real.", "",
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
if minutos < MIN_OBJETIVO:
    lineas += ["", f"Aviso: faltan {MIN_OBJETIVO - minutos:.1f} min para el objetivo. El LoRA mezclará con lo que "
               f"hay y el español pesará algo menos del {FRAC_ES:.0%}."]
informe = "\\n".join(lineas)
(SINT / "informe.md").write_text(informe + "\\n", encoding="utf-8")
print(informe)
"""),
    code("""
# 5. Subir a Drive y desconectar
comun.desconectar()
"""),
])

# ---------------------------------------------------------------- LoRA de Qwen3-TTS
cuaderno("04_lora_qwen.ipynb", [
    md("""
# Piloto de fine-tuning — LoRA de Qwen3-TTS para Naval

Entrena un **LoRA** sobre `Qwen/Qwen3-TTS-12Hz-1.7B-Base` que se usa en **modo solo timbre** (x-vector), el
modo que en la escucha a ciegas dio a Naval parecido 5 y acento 5. El objetivo del LoRA es ganar naturalidad
en español sin perder el timbre. No se usa el SFT oficial de Qwen porque rompe la clonación por referencia
(detalles en `piloto/investigacion-lora.md`). El entrenador está en `piloto/lora_qwen.py`.

**Variantes** (se elige en la celda 2)

| Variante | Modelo | Qué entra en cada época |
|---|---|---|
| **B** (por defecto) | `naval` | Todo el español sintético de Chatterbox V2 (unos 36 min) + inglés real de Naval (`datasets/naval`) hasta que el español sea el **40 %** de los minutos. El inglés se sortea en cada época: en dos épocas se ve casi entero |
| **A** | `naval` | Solo el español sintético. Para comparar, si quieres |
| **kapil** | `naval_kapil` | Parte del checkpoint de Naval que elijas (`PARTIR_DE`) y hace un repaso corto con la sesión con Kapil (`datasets/naval_kapil`, 15,6 min) + español sintético sorteado hasta el 40 %, para no recuperar acento |
| **nivi**, **brett**, **deutsch** | su voz | Como B, con su dataset (`datasets/<voz>`) y su español sintético (`piloto/sintetico/<voz>/`, cuadernos 01 y 03) |

Cada clip lleva su **etiqueta de idioma** y, como referencia, el timbre de **otro clip de la misma voz**.
Los 19 clips de XTTS quedan fuera, como decidiste.

**Salida** en `fine_tunned_naval/piloto/lora_qwen/<variante>/`:

| Fichero | Qué es |
|---|---|
| `paso_0040/`, `paso_0080/`… | Los checkpoints del LoRA (unos pocos MB cada uno) |
| `estado.json` | La pérdida de evaluación de cada checkpoint, en inglés y en español |
| `registro.jsonl` | La pérdida de cada paso |
| `prueba/` | Tres frases de la criba con cada versión del modelo |
| `prueba/escucha/lora_qwen_<variante>.html` | La página de escucha a ciegas de esas frases |

En **nivi**, **brett** y **deutsch**, la prueba usa tres frases suyas de la criba con su referencia
(`piloto/rutas.py`, `PRUEBA`). En **kapil**, la prueba usa las frases k05, k07 y k10 con la referencia de la sesión con Kapil, y compara el
modelo sin LoRA, el LoRA de Naval de partida y cada checkpoint nuevo. La página trae además, en cada versión,
la misma frase con la referencia normal de Naval, para puntuar si se nota el cambio de tono.

**GPU: L4** (necesita bf16; con T4 el cuaderno se para al principio sin gastar casi nada).
**Tiempo estimado:** 30–45 min con B, unos 25 con kapil. Uso: celda 1, *Entorno de ejecución → Reiniciar
sesión*, y el resto en orden. Si se corta, vuelve a ejecutarlo: los códigos ya calculados, los pasos ya
entrenados y los audios ya generados no se repiten.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q qwen-tts==0.1.1 peft==0.17.1
"""),
    code("""
# 2. Parámetros
VARIANTE = "B"       # Naval: "B" (60 % inglés + 40 % español) o "A" (solo español) · "kapil": naval_kapil
                     # · "nivi", "brett" o "deutsch": la voz de ese hablante
PARTIR_DE = "B/paso_0158"   # solo para "kapil": el checkpoint de Naval que elegiste al escuchar

LR = 2e-6            # el de Alexandria para unos cientos de ejemplos; más alto farfulla
LORA_R, LORA_ALPHA = 64, 128   # en "kapil" tienen que ser los mismos que en el LoRA de partida
ACUMULACION = 8      # batch efectivo de 8 clips
EVAL_ES = 16         # clips del español sintético que se apartan para medir la pérdida
SEMILLA = 1234
if VARIANTE == "kapil":
    EPOCAS = 3       # unos 15 min de inglés + 10 de español por época: tres pasadas cortas
    GUARDAR_CADA = 15
else:
    EPOCAS = 2
    GUARDAR_CADA = 40    # pasos de optimizador entre checkpoints
"""),
    code(f"""
# 3. Preparar: código del repo, Drive y los ejemplos
import os, sys, subprocess, json, random
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/criba", "/content/repo/piloto"]
import comun, lora_qwen, rutas

comun.montar_drive()
D = comun.DRIVE
# La voz que se entrena, de dónde sale su inglés real y de dónde su español sintético
VOZ = {{"B": "naval", "A": "naval", "kapil": "naval_kapil"}}.get(VARIANTE, VARIANTE)
DATASET = VOZ
VOZ_ES = "naval" if VOZ in ("naval", "naval_kapil") else VOZ
DATOS = rutas.dataset(D, DATASET)
SALIDA = rutas.lora(D, VARIANTE)
for necesario, falta in [(DATOS / "metadata.jsonl", "el dataset de la sesión local"),
                         (rutas.sintetico(D, VOZ_ES) / "seleccion.jsonl", "los cuadernos 01 y 03 con esta voz")]:
    if not necesario.is_file():
        raise SystemExit(f"Falta {{necesario}}: hace falta {{falta}}. No sigas.")

def ingles(split):
    return [{{"audio": str(DATOS / f["file"]), "texto": f["text"], "idioma": "en", "segundos": f["dur"],
             "grupo_ref": "en:" + f["source_id"]}}
            for f in lora_qwen.leer_jsonl(DATOS / "metadata.jsonl") if f["split"] == split]

espanol = [{{"audio": str(D / s["audio"]), "texto": s["texto"], "idioma": "es", "segundos": s["segundos"],
            "grupo_ref": "es"}}
           for s in lora_qwen.leer_jsonl(rutas.sintetico(D, VOZ_ES) / "seleccion.jsonl")
           if s["variante"] == "chatterbox_v2"]
random.Random(SEMILLA).shuffle(espanol)
es_eval, es_train = espanol[:EVAL_ES], espanol[EVAL_ES:]
en_train, en_eval = ingles("train"), ingles("eval")
if VARIANTE == "A":
    en_train = []
TODOS = en_train + en_eval + es_train + es_eval
faltan = [e["audio"] for e in TODOS if not Path(e["audio"]).is_file()]
if (not en_train and VARIANTE != "A") or not espanol:
    faltan.append(f"datos de {{VOZ}}: {{len(en_train)}} clips en inglés y {{len(espanol)}} en español "
                  "(¿están el dataset y el cuaderno 03 de esta voz?)")
if VARIANTE == "kapil":
    ADAPTADOR_INICIAL = D / "piloto" / "lora_qwen" / PARTIR_DE
    if not (ADAPTADOR_INICIAL / "adapter_model.safetensors").is_file():
        faltan.append(str(ADAPTADOR_INICIAL / "adapter_model.safetensors"))
if faltan:
    raise SystemExit(f"Faltan {{len(faltan)}} ficheros en Drive, por ejemplo {{faltan[0]}}. No sigas.")
lora_qwen.asignar_referencias(TODOS, SEMILLA)
ORDEN = lora_qwen.mezcla_por_epoca(en_train, es_train, 0.4 if VARIANTE != "A" else 1.0, EPOCAS, SEMILLA)
EVAL = en_eval + es_eval

m = lambda xs: sum(e["segundos"] for e in xs) / 60
print(f"Variante {{VARIANTE}} ({{DATASET}}). Disponible: inglés {{m(en_train):.1f}} min ({{len(en_train)}} clips), "
      f"español {{m(es_train):.1f}} min ({{len(es_train)}} clips)")
if VARIANTE == "kapil":
    print(f"Parte de: {{PARTIR_DE}}")
for n, ep in enumerate(ORDEN, 1):
    en_ = [e for e in ep if e["idioma"] == "en"]
    es_ = [e for e in ep if e["idioma"] == "es"]
    print(f"  época {{n}}: {{len(ep)}} clips · inglés {{m(en_):.1f}} min · español {{m(es_):.1f}} min "
          f"({{m(es_) / max(m(ep), 1e-9):.0%}} de español)")
pasos = -(-sum(len(ep) for ep in ORDEN) // ACUMULACION)
print(f"Pasos de optimizador: {{pasos}}; checkpoints cada {{GUARDAR_CADA}}. "
      f"Evaluación: {{len(en_eval)}} clips en inglés y {{len(es_eval)}} en español.")
print("RESULTADO: OK")
"""),
    code("""
# 4. Cargar Qwen y calcular códigos y x-vectors (una sola vez: quedan en Drive)
import torch
if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
    raise SystemExit("Este cuaderno necesita una GPU con bf16 (L4 o A100). Cambia el tipo de entorno.")
from qwen_tts import Qwen3TTSModel
tts = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cuda:0",
                                    dtype=torch.bfloat16, attn_implementation="sdpa")
hf = tts.model
idiomas = hf.get_supported_languages()
assert "english" in idiomas and "spanish" in idiomas, idiomas
SALIDA.mkdir(parents=True, exist_ok=True)
lora_qwen.preparar(hf, tts.processor, TODOS, D / "piloto" / "lora_qwen" / "cache_qwen.pt")
largo = max(e["codigos"].shape[0] for e in TODOS)
print(f"Listo: {len(TODOS)} clips; el más largo tiene {largo} frames ({largo / 12:.1f} s)")
"""),
    code("""
# 5. Entrenar el LoRA
from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
from safetensors.torch import load_file
comun.SALIDA = D / "piloto" / "lora_qwen"
comun.guardar_entorno(VARIANTE, ["qwen-tts", "peft", "torch", "transformers", "accelerate"])
(SALIDA / "parametros.json").write_text(json.dumps({
    "variante": VARIANTE, "dataset": DATASET, "partir_de": PARTIR_DE if VARIANTE == "kapil" else None,
    "epocas": EPOCAS, "lr": LR, "lora_r": LORA_R, "lora_alpha": LORA_ALPHA,
    "acumulacion": ACUMULACION, "guardar_cada": GUARDAR_CADA, "semilla": SEMILLA,
    "modelo": "Qwen/Qwen3-TTS-12Hz-1.7B-Base", "peso_sub": lora_qwen.PESO_SUB,
    "ejemplos": [{k: e[k] for k in ("audio", "idioma", "ref", "segundos")} for e in TODOS]},
    ensure_ascii=False, indent=1), encoding="utf-8")

torch.manual_seed(SEMILLA)
peft_talker = get_peft_model(hf.talker, LoraConfig(
    r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0.05, bias="none",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]))
hf.talker = peft_talker
if VARIANTE == "kapil":
    # Arranca con los pesos del LoRA de Naval elegido (si se reanuda, entrenar() carga luego los suyos)
    set_peft_model_state_dict(peft_talker, load_file(str(ADAPTADOR_INICIAL / "adapter_model.safetensors")))
    print("Pesos iniciales:", PARTIR_DE)
peft_talker.base_model.model.model.gradient_checkpointing_enable(
    gradient_checkpointing_kwargs={"use_reentrant": False})
peft_talker.print_trainable_parameters()
ESTADO = lora_qwen.entrenar(hf, peft_talker, ORDEN, EVAL, SALIDA, lr=LR, accum=ACUMULACION,
                            guardar_cada=GUARDAR_CADA)
print()
print("Pérdida de evaluación por checkpoint (más baja = mejor; si sube, empieza a sobreajustar):")
for nombre, ev in ESTADO["checkpoints"].items():
    print(f"  {nombre}: inglés {ev.get('en', '-')} · español {ev.get('es', '-')}")
"""),
    code("""
# 6. Prueba de escucha: tres frases con cada versión del modelo
# Mismo modo que en producción: solo timbre y non-streaming.
peft_talker.eval()
CHECKPOINTS = sorted(p.name for p in SALIDA.glob("paso_*") if p.name != "paso_0000")
for c in CHECKPOINTS:
    if c not in peft_talker.peft_config:
        peft_talker.load_adapter(str(SALIDA / c), adapter_name=c)
VERSIONES = ["base"] + CHECKPOINTS
if VARIANTE == "kapil":
    peft_talker.load_adapter(str(ADAPTADOR_INICIAL), adapter_name="naval")
    VERSIONES = ["base", "naval"] + CHECKPOINTS

comun.SALIDA = SALIDA / "prueba"
fichero, FRASES_PRUEBA = rutas.PRUEBA[VOZ]
comun.FRASES = Path("/content/repo/criba") / fichero
items, silencio_ms = comun.cargar_items()
por_id = {it["id"]: it for it in items}
# En kapil se generan también las frases gemelas con la ref normal, para puntuar el cambio de tono
ids = FRASES_PRUEBA + [por_id[i]["mismo_texto_que"] for i in FRASES_PRUEBA if por_id[i].get("mismo_texto_que")]
ITEMS = [por_id[i] for i in ids]
REFS = comun.comprobar(ITEMS)
prompts = {r: tts.create_voice_clone_prompt(ref_audio=v["wav"], x_vector_only_mode=True) for r, v in REFS.items()}

def sintetizar(texto, ref):
    clave = next(r for r, v in REFS.items() if v["wav"] == ref["wav"])
    wavs, sr = tts.generate_voice_clone(text=texto, language="Spanish", voice_clone_prompt=prompts[clave],
                                        non_streaming_mode=True)
    return wavs[0], sr

PARAMS = {"modo": "x_vector_only", "non_streaming_mode": True, "slot_ref": comun.REF_POR_DEFECTO}
for v in VERSIONES:
    if v == "base":
        with peft_talker.disable_adapter():
            comun.generar(v, sintetizar, ITEMS, REFS, silencio_ms, params=PARAMS)
    else:
        peft_talker.set_adapter(v)
        comun.generar(v, sintetizar, ITEMS, REFS, silencio_ms, params={**PARAMS, "adaptador": v})

import escucha
escucha.construir_pagina(FRASES_PRUEBA, VERSIONES, nombre=f"lora_qwen_{VARIANTE}")
"""),
    code("""
# 7. Subir a Drive y desconectar
comun.desconectar()
"""),
], gpu="L4")

# ---------------------------------------------------------------- LoRA de OmniVoice
cuaderno("05_lora_omnivoice.ipynb", [
    md("""
# Piloto de fine-tuning — LoRA de OmniVoice para Naval

Entrena un **LoRA** sobre `k2-fsa/OmniVoice`, el ganador de la escucha a ciegas de la criba (media 4,31), que
clona bien a Naval pero con acento inglés (3 sobre 5). El objetivo del LoRA es **quitar el acento en español
sin perder el timbre**. Es el segundo brazo del piloto: mismos datos y misma prueba que `04_lora_qwen`.

Se usa el entrenamiento **oficial** de OmniVoice con su LoRA, instalado desde git (el 0.2.1 de PyPI no lo trae).
Lo propio del piloto está en `piloto/lora_omnivoice.py` (detalles en `piloto/investigacion-lora.md`, §2):

- Cada ejemplo lleva como **referencia otro clip de la misma voz**, tokenizado igual que en la inferencia, y el
  modelo solo aprende a generar el clip, nunca la referencia. El entrenamiento oficial solo sabe usar un trozo
  del mismo clip.
- Cada ejemplo lleva su **etiqueta de idioma** (`en` o `es`).
- Un 10 % de los ejemplos va **sin condicionamiento**, como en el preentrenamiento, para no estropear la guía
  (`guidance_scale`) que usa la generación.
- Se completa el **silencio final** de los clips hasta 0,2 s: OmniVoice se come el final de las frases en
  español (issue #116).

**Datos** (los mismos que en `04_lora_qwen`: mismo barajado y los mismos 16 clips de español para evaluar)

| Variante | Qué entra en cada época |
|---|---|
| **B** (por defecto) | Todo el español sintético de Chatterbox V2 (unos 36 min) + inglés real de Naval hasta que el español sea el **40 %** de los minutos. El inglés se sortea en cada época |
| **A** | Solo el español sintético. Para comparar, si quieres |

**Salida** en `fine_tunned_naval/piloto/lora_omnivoice/<variante>/`:

| Fichero | Qué es |
|---|---|
| `paso_NNNN/` | Un checkpoint por época: solo el adaptador (unos 100 MB), que es lo que hace falta para cargarlo |
| `estado.json` | La pérdida de evaluación de cada checkpoint, en inglés y en español |
| `registro.jsonl` | La pérdida de entrenamiento cada 10 pasos |
| `reanudar.pt` | El optimizador del último checkpoint, para reanudar si se corta |
| `prueba/` | Tres frases de la criba con el modelo base y con cada checkpoint |
| `prueba/escucha/lora_omnivoice_<variante>.html` | La página de escucha a ciegas de esas frases |

Los tokens de audio quedan en `piloto/lora_omnivoice/cache_tokens.pt` y valen para las dos variantes.

**GPU: L4** (necesita bf16; con T4 el cuaderno se para al principio sin gastar casi nada).
**Tiempo estimado:** 30–45 min en total, la mayor parte en descargar el modelo, leer los audios de Drive y la
prueba de escucha; el entrenamiento son unos 210 pasos. Uso: celda 1, *Entorno de ejecución → Reiniciar sesión*, y el resto
en orden. Si se corta, vuelve a ejecutarlo: los tokens ya calculados, los pasos ya entrenados y los audios ya
generados no se repiten.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# OmniVoice desde git, en el commit investigado: el wheel 0.2.1 de PyPI no trae el LoRA.
# transformers y peft, fijados a las versiones con las que se probó el código en CPU.
# audioop-lts solo se instala con Python 3.13, donde pydub lo necesita.
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q "omnivoice[lora] @ git+https://github.com/k2-fsa/OmniVoice@08be0b4ccbac3e13e374e86fbfead4b4cac343e2" transformers==5.22.0 peft==0.21.2 "audioop-lts; python_version >= '3.13'"
"""),
    code("""
# 2. Parámetros
VARIANTE = "B"       # "B": 60 % inglés real + 40 % español sintético · "A": solo español sintético
EPOCAS = 4           # el objetivo enmascarado solo puntúa parte de los tokens: necesita más pasadas que Qwen
LR = 1e-4            # el del ejemplo oficial de LoRA de OmniVoice
LORA_R, LORA_ALPHA = 16, 32   # los del ejemplo oficial
BATCH_TOKENS = 4096  # tokens por lote, relleno incluido
ACUMULACION = 2      # unos 8192 tokens por paso de optimizador, como el ejemplo oficial
EVAL_ES = 16         # clips del español sintético que se apartan para medir la pérdida (los mismos que en Qwen)
SEMILLA = 1234
FRASES_PRUEBA = ["n12", "n18", "n25"]   # de la criba: una media, una larga y el bloque de 9 frases
"""),
    code(f"""
# 3. Preparar: código del repo, Drive y los ejemplos (todavía no se carga ningún modelo)
import os, sys, subprocess, json, random
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/criba", "/content/repo/piloto"]
import comun, lora_qwen, lora_omnivoice

comun.montar_drive()
D = comun.DRIVE
NAVAL = D / "datasets" / "naval"
SALIDA = D / "piloto" / "lora_omnivoice" / VARIANTE

# Exactamente los ejemplos de 04_lora_qwen: mismo barajado, mismo reparto, mismas referencias y misma mezcla
def ingles(split):
    return [{{"audio": str(NAVAL / f["file"]), "texto": f["text"], "idioma": "en", "segundos": f["dur"],
             "grupo_ref": "en:" + f["source_id"]}}
            for f in lora_qwen.leer_jsonl(NAVAL / "metadata.jsonl") if f["split"] == split]

espanol = [{{"audio": str(D / s["audio"]), "texto": s["texto"], "idioma": "es", "segundos": s["segundos"],
            "grupo_ref": "es"}}
           for s in lora_qwen.leer_jsonl(D / "piloto" / "sintetico" / "seleccion.jsonl")
           if s["variante"] == "chatterbox_v2"]
random.Random(SEMILLA).shuffle(espanol)
es_eval, es_train = espanol[:EVAL_ES], espanol[EVAL_ES:]
en_train, en_eval = ingles("train"), ingles("eval")
if VARIANTE == "A":
    en_train = []
TODOS = en_train + en_eval + es_train + es_eval
faltan = [e["audio"] for e in TODOS if not Path(e["audio"]).is_file()]
if faltan:
    raise SystemExit(f"Faltan {{len(faltan)}} audios en Drive, por ejemplo {{faltan[0]}}. No sigas.")
lora_qwen.asignar_referencias(TODOS, SEMILLA)
ORDEN = lora_qwen.mezcla_por_epoca(en_train, es_train, 0.4 if VARIANTE == "B" else 1.0, EPOCAS, SEMILLA)
EVAL = en_eval + es_eval

# La referencia de la prueba de escucha, antes de gastar nada
items, _ = comun.cargar_items()
comun.comprobar([it for it in items if it["id"] in FRASES_PRUEBA])

m = lambda xs: sum(e["segundos"] for e in xs) / 60
SEG = {{e["audio"]: e["segundos"] for e in TODOS}}
print(f"Variante {{VARIANTE}}. Disponible: inglés {{m(en_train):.1f}} min ({{len(en_train)}} clips), "
      f"español {{m(es_train):.1f}} min ({{len(es_train)}} clips)")
for n, ep in enumerate(ORDEN, 1):
    en_ = [e for e in ep if e["idioma"] == "en"]
    es_ = [e for e in ep if e["idioma"] == "es"]
    con_ref = sum(e["segundos"] + SEG[e["ref"]] for e in ep) / 60
    print(f"  época {{n}}: {{len(ep)}} clips · inglés {{m(en_):.1f}} min · español {{m(es_):.1f}} min "
          f"({{m(es_) / max(m(ep), 1e-9):.0%}} de español) · {{con_ref:.0f}} min con su referencia delante")
pasos = lora_omnivoice.estimar_pasos(ORDEN, SEG, BATCH_TOKENS, ACUMULACION)
print(f"Pasos de optimizador: unos {{pasos}} (el número exacto sale al escribir los datos), un checkpoint "
      f"por época. Evaluación: {{len(en_eval)}} clips en inglés y {{len(es_eval)}} en español.")
print("RESULTADO: OK")
"""),
    code("""
# 4. Tokenizar el audio (una sola vez: queda en Drive y vale para las dos variantes)
import torch
if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
    raise SystemExit("Este cuaderno necesita una GPU con bf16 (L4 o A100). Cambia el tipo de entorno.")
SALIDA.mkdir(parents=True, exist_ok=True)
TOKENS = lora_omnivoice.preparar_tokens(TODOS, D / "piloto" / "lora_omnivoice" / "cache_tokens.pt")
cortos = [e for e in TODOS if TOKENS["destino"][e["audio"]]["cola"] < lora_omnivoice.COLA_MIN]
largo = max(TOKENS["ref"][e["ref"]]["tokens"].shape[1] + TOKENS["destino"][e["audio"]]["tokens"].shape[1]
            for e in TODOS)
print(f"Listo: {len(TODOS)} clips. {len(cortos)} tenían menos de {lora_omnivoice.COLA_MIN} s de silencio final "
      f"y se les ha completado hasta {lora_omnivoice.COLA_OBJETIVO} s.")
print(f"El ejemplo más largo, referencia incluida, tiene {largo} tokens de audio "
      f"({largo / TOKENS['frame_rate']:.1f} s); el límite es 2000 tokens con el texto.")
"""),
    code("""
# 5. Entrenar el LoRA con el entrenador oficial de OmniVoice
comun.SALIDA = D / "piloto" / "lora_omnivoice"
comun.guardar_entorno(VARIANTE, ["omnivoice", "peft", "torch", "transformers", "accelerate", "webdataset"])
LOCAL = Path("/content/lora_omnivoice") / VARIANTE
DATOS = lora_omnivoice.escribir_webdataset(lora_omnivoice.plan(ORDEN, TOKENS, SEMILLA), LOCAL / "datos",
                                           TOKENS["frame_rate"])
CFG = lora_omnivoice.config_entrenamiento(learning_rate=LR, lora_r=LORA_R, lora_alpha=LORA_ALPHA,
                                          batch_tokens=BATCH_TOKENS, gradient_accumulation_steps=ACUMULACION,
                                          seed=SEMILLA)
(SALIDA / "parametros.json").write_text(json.dumps({
    "variante": VARIANTE, "epocas": EPOCAS, "semilla": SEMILLA, "config": CFG,
    "prob_incondicional": lora_omnivoice.PROB_INCONDICIONAL,
    "silencio_final": [lora_omnivoice.COLA_MIN, lora_omnivoice.COLA_OBJETIVO],
    "ejemplos": [{k: e[k] for k in ("audio", "idioma", "ref", "segundos")} for e in TODOS]},
    ensure_ascii=False, indent=1), encoding="utf-8")
ESTADO = lora_omnivoice.entrenar(CFG, DATOS, EVAL, TOKENS, EPOCAS, SALIDA, LOCAL / "checkpoints")
print()
print("Pérdida de evaluación por checkpoint (más baja = mejor; si sube, empieza a sobreajustar):")
for nombre, ev in ESTADO["checkpoints"].items():
    print(f"  {nombre}: inglés {ev.get('en', '-')} · español {ev.get('es', '-')}")
"""),
    code("""
# 6. Prueba de escucha: tres frases con el modelo base y con cada checkpoint
# Los mismos parámetros que la criba (02_omnivoice): float16, language="es", naval_ref02 con su transcripción
# y el resto por defecto. Cada checkpoint se carga como hace omnivoice-infer --lora_adapter (fusionado).
from omnivoice import OmniVoice
from omnivoice.utils.lora import load_lora_adapter
import escucha

comun.SALIDA = SALIDA / "prueba"
items, silencio_ms = comun.cargar_items()
ITEMS = [it for it in items if it["id"] in FRASES_PRUEBA]
REFS = comun.comprobar(ITEMS)
CHECKPOINTS = sorted(p.name for p in SALIDA.glob("paso_*") if p.is_dir())
PARAMS = {"modelo": lora_omnivoice.MODELO, "language": "es", "dtype": "float16", "ref": "naval_ref02"}
for version in ["base"] + CHECKPOINTS:
    if all((comun.SALIDA / version / f"{i}.wav").exists() for i in FRASES_PRUEBA):
        print(f"=== {version}: ya estaba generado")
        continue
    print(f"=== {version}")
    modelo = OmniVoice.from_pretrained(lora_omnivoice.MODELO, device_map="cuda:0", dtype=torch.float16)
    if version != "base":
        modelo = load_lora_adapter(modelo, str(SALIDA / version))

    def sintetizar(texto, ref):
        audios = modelo.generate(text=texto, language="es", ref_audio=ref["wav"], ref_text=ref["texto"])
        return audios[0], modelo.sampling_rate

    comun.generar(version, sintetizar, ITEMS, REFS, silencio_ms, params={**PARAMS, "adaptador": version})
    del modelo
    comun.liberar()

escucha.construir_pagina(FRASES_PRUEBA, ["base"] + CHECKPOINTS, nombre=f"lora_omnivoice_{VARIANTE}")
"""),
    code("""
# 7. Subir a Drive y desconectar
comun.desconectar()
"""),
], gpu="L4")

# ---------------------------------------------------------------- Ritmo
cuaderno("06_ritmo.ipynb", [
    md("""
# Piloto de fine-tuning — acortar las pausas

Verificación rápida: coge audios ya generados en Drive (por defecto, las frases de prueba del LoRA de Qwen) y
**acorta solo los silencios**, sin tocar el habla:

- el silencio del principio queda en 0,05 s y el del final en 0,15 s;
- cada pausa interna de más de `PAUSA_MAX` se queda en `PAUSA_MAX` (se le quita el centro);
- las pausas más cortas (comas, respiraciones) no se tocan.

Los escuchas aquí mismo, uno debajo de otro, con su duración y su velocidad en caracteres por segundo. Como
referencia, Naval en inglés habla a unos 19,5 c/s y Qwen en español sale a unos 15. Lo que más se nota es el
bloque de 9 frases (n25): ahí se acumulan las pausas entre frases.

No genera nada con el modelo ni guarda nada en Drive, salvo que pongas `GUARDAR = True`.

**Entorno: CPU, sin GPU** (*Entorno de ejecución → Cambiar tipo de entorno → CPU*). Tarda un minuto.
Ejecuta las celdas en orden; la última desconecta el entorno.
"""),
    code("""
# 1. Parámetros
CARPETA = "piloto/lora_qwen/B/prueba"     # dentro de fine_tunned_naval; para otra voz, p. ej. ".../brett/prueba"
                                          # o los bloques del cuaderno 07: "piloto/prueba_voz/<voz>"
VERSIONES = ["paso_0158"]                 # añade "base" para comparar con el modelo sin LoRA
FRASES = ["n12", "n18", "n25"]            # nivi: v07 v09 v10 · brett: b05 b08 b10 · deutsch: d01 d02 d03
PAUSAS_MAX = [0.25, 0.18, 0.12]           # segundos; 0,12 es el valor fijado para la fábrica
GUARDAR = False                           # True: deja las versiones en <CARPETA>/pausas/ en Drive
"""),
    code(f"""
# 2. Preparar: código del repo, Drive y los textos de las frases
import os, sys, subprocess
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/criba", "/content/repo/piloto"]
import comun, ritmo

comun.montar_drive()
BASE = comun.DRIVE / CARPETA
TEXTO = {{}}
for fichero in ("frases.json", "frases_xvector.json"):   # las de Deutsch están en el segundo
    comun.FRASES = Path("/content/repo/criba") / fichero
    TEXTO.update({{it["id"]: " ".join(it["frases"]) for it in comun.cargar_items()[0]}})
if (BASE / "textos.json").is_file():   # los bloques que genera el cuaderno 07_prueba_voz
    import json
    TEXTO.update(json.loads((BASE / "textos.json").read_text(encoding="utf-8")))
faltan = [str(BASE / v / f"{{f}}.wav") for v in VERSIONES for f in FRASES if not (BASE / v / f"{{f}}.wav").is_file()]
if faltan:
    raise SystemExit(f"Faltan audios en Drive, por ejemplo {{faltan[0]}}")
print("RESULTADO: OK")
"""),
    code("""
# 3. Acortar las pausas y escuchar
import shutil, time
import soundfile as sf
from IPython.display import Audio, Markdown, display

def leer(ruta, intentos=4):
    # El montaje de Drive a veces falla al abrir un fichero ("System error"): se copia a disco local y se reintenta
    for n in range(intentos):
        try:
            local = Path("/tmp") / ruta.name
            shutil.copyfile(ruta, local)
            return sf.read(str(local), dtype="float32")
        except Exception as e:
            if n == intentos - 1:
                raise
            print(f"  reintento {n + 1} con {ruta.name}: {type(e).__name__}")
            time.sleep(2)

for f in FRASES:
    display(Markdown(f"### {f}\\n*{TEXTO[f]}*"))
    for v in VERSIONES:
        audio, sr = leer(BASE / v / f"{f}.wav")
        for pm in [None] + PAUSAS_MAX:
            corto = audio if pm is None else ritmo.acortar_pausas(audio, sr, pausa_max=pm)
            seg = len(corto) / sr
            nombre = "original" if pm is None else f"pausas ≤ {pm:.2f} s"
            ahorro = "" if pm is None else f", {len(audio) / sr - seg:.1f} s menos"
            display(Markdown(f"**{v} · {nombre}** — {seg:.1f} s, {len(TEXTO[f]) / seg:.1f} c/s{ahorro}"))
            display(Audio(corto, rate=sr))
            if GUARDAR and pm is not None:
                destino = BASE / "pausas" / v
                destino.mkdir(parents=True, exist_ok=True)
                sf.write(str(destino / f"{f}_p{pm:.2f}.wav"), corto, sr, subtype="PCM_16")
"""),
    code("""
# 4. Desconectar (sube a Drive lo pendiente si has guardado algo)
comun.desconectar()
"""),
], gpu=None)

# ---------------------------------------------------------------- Prueba de voz con bloques reales
cuaderno("07_prueba_voz.ipynb", [
    md("""
# Piloto de fine-tuning — prueba de una voz con intervenciones reales

Genera unas cuantas **intervenciones reales** de un hablante, sacadas de los episodios ya traducidos, con el
**mismo modelo que usa la fábrica** para esa voz (`fabrica/voces.json`: su referencia y su LoRA, o Qwen base si
no tiene). Sirve para escuchar bloques largos, de varias frases, antes de producir episodios enteros.

A diferencia de la fábrica, **no recorta las pausas**: une las frases con 250 ms, como las pruebas de los
cuadernos 04. Así, después, el cuaderno **`06_ritmo`** puede probar distintas pausas sobre el mismo audio.

Salida en `fine_tunned_naval/piloto/prueba_voz/<voz>/<versión>/`, un `.wav` por bloque (`052_b23-nivi.wav`…), y
`textos.json` con su texto. La versión es el checkpoint de la voz (`paso_0130`…) o `base`.

**GPU:** T4 (o L4). **Tiempo:** unos 5 minutos. Celda 1, *Reiniciar sesión* y el resto en orden.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q qwen-tts==0.1.1 peft==0.17.1
"""),
    code("""
# 2. Parámetros
VOZ = "nivi"
# Bloques reales de los episodios traducidos: "<año>/<carpeta del episodio>#<id del bloque>"
BLOQUES = ["2019/052-rich#b23-nivi",       # 9 frases
           "2019/052-rich#b134-nivi",      # 7 frases
           "2019/051-angel-1#b56-nivi"]    # 7 frases
SILENCIO_MS = 250
"""),
    code(f"""
# 3. Preparar: código del repo, Drive, el modelo de la voz y el texto de los bloques
import os, sys, subprocess, json
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/fabrica", "/content/repo/piloto", "/content/repo/criba"]
import comun, fabrica

comun.montar_drive()
CFG = fabrica.cargar_config()
RAIZ_VOCES = Path(CFG["rutas"]["drive"]) / CFG["rutas"]["voces"]
datos = CFG["voces"][VOZ]
VERSION = Path(datos["adaptador"]).name if datos.get("adaptador") else "base"
SALIDA = RAIZ_VOCES / "piloto" / "prueba_voz" / VOZ
ITEMS = {{}}
for b in BLOQUES:
    ep, bloque = b.split("#")
    tr = json.loads((Path("/content/repo/episodios") / ep / "transcript.es.json").read_text(encoding="utf-8"))
    frases = next(x["frases"] for x in tr["contenido"] if x["id"] == bloque)
    ITEMS[f"{{ep.split('/')[1].split('-')[0]}}_{{bloque}}"] = frases
for i, frases in ITEMS.items():
    print(f"  {{i}}: {{len(frases)}} frases, {{sum(len(f) for f in frases)}} caracteres")
print(f"Voz {{VOZ}} · {{'LoRA ' + datos['adaptador'] if datos.get('adaptador') else 'Qwen base'}} · salida "
      f"{{(SALIDA / VERSION).relative_to(RAIZ_VOCES)}}")
(SALIDA / VERSION).mkdir(parents=True, exist_ok=True)
(SALIDA / "textos.json").write_text(json.dumps({{i: " ".join(f) for i, f in ITEMS.items()}}, ensure_ascii=False,
                                               indent=1), encoding="utf-8")
print("RESULTADO: OK")
"""),
    code("""
# 4. Generar cada bloque frase a frase, unidas con SILENCIO_MS (sin recortar pausas)
import numpy as np, soundfile as sf
MOTOR = fabrica.MotorQwen(CFG, [VOZ], RAIZ_VOCES)
for i, frases in ITEMS.items():
    destino = SALIDA / VERSION / f"{i}.wav"
    if destino.exists():
        print(f"  {i}: ya existe")
        continue
    trozos, sr = [], None
    for frase in frases:
        audio, sr = MOTOR.sintetizar(frase, VOZ, 0)
        trozos += [np.asarray(audio, dtype=np.float32).squeeze(), np.zeros(int(sr * SILENCIO_MS / 1000), np.float32)]
    audio = np.concatenate(trozos[:-1])
    sf.write(str(destino), audio, sr, subtype="PCM_16")
    print(f"  {i}: {len(audio) / sr:.1f} s")
print(f"Listo. Para escucharlo con distintas pausas, en 06_ritmo: CARPETA = \\"piloto/prueba_voz/{VOZ}\\", "
      f"VERSIONES = [\\"{VERSION}\\"], FRASES = {list(ITEMS)}")
"""),
    code("""
# 5. Subir a Drive y desconectar
comun.desconectar()
"""),
])

# ---------------------------------------------------------------- Acento de Naval
cuaderno("08_acento_naval.ipynb", [
    md("""
# Piloto de fine-tuning — un Naval con acento más español

El autor nota a Naval **demasiado inglés** en la fábrica (LoRA `B/paso_0158` con la referencia `naval_ref02`).
En la escucha del 30-oct el acento sacó 4 en todos los checkpoints: cambiar de checkpoint no lo arregla. Este
cuaderno prueba, sin entrenar nada, dos palancas baratas y sus combinaciones:

- **Referencia en español.** En modo solo timbre, Qwen clona a partir de una huella de voz (x-vector) sacada de
  la referencia. La de ahora sale de Naval hablando **inglés** y arrastra parte de su acento. Aquí la huella sale
  del **español sintético de Naval** (Chatterbox V2, `piloto/sintetico/seleccion.jsonl`): del clip más parecido
  a él, o la media de los `N_REFS_ES` más parecidos.
- **LoRA a media fuerza.** Una mezcla entre la base (algo mejor de acento) y el LoRA (mejor naturalidad).

Versiones (en la página salen con letras al azar):

| Versión | LoRA | Huella |
|---|---|---|
| `actual` | `B/paso_0158` | `naval_ref02` (inglés) — lo que suena hoy en la fábrica |
| `lora_ref_es1` | `B/paso_0158` | el clip español más parecido |
| `lora_ref_es5` | `B/paso_0158` | media de los `N_REFS_ES` clips españoles más parecidos |
| `lora_medio_ref_es5` | `B/paso_0158` a `FUERZA_MEDIA` | media de los clips españoles |
| `base_ref_es5` | ninguno | media de los clips españoles |

Las frases son **intervenciones reales** de Naval de los episodios traducidos, generadas **como en la fábrica**:
misma semilla por frase y pausas recortadas a 0,12 s. La de 044 es la misma que ya escuchaste en el borrador.

Salida en `fine_tunned_naval/piloto/acento_naval/`: un `.wav` por versión y bloque, y la página de escucha a
ciegas en `escucha/acento_naval.html` (la clave, aparte, en `clave_acento_naval.json`: no la abras antes de
puntuar). **El criterio que manda aquí es el acento** (5 = español nativo), sin perder parecido.

**GPU:** T4. **Tiempo:** unos 25–35 minutos (unos 6 minutos de audio). Celda 1, *Reiniciar sesión* y el resto
en orden. Si se corta, vuelve a lanzar: lo que ya esté en Drive no se repite.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q qwen-tts==0.1.1 peft==0.17.1
"""),
    code("""
# 2. Parámetros
# Intervenciones reales de Naval: "<año>/<carpeta del episodio>#<id del bloque>"
BLOQUES = ["2019/044-schelling-point#b02-naval",   # 3 frases, la que ya escuchaste en el borrador
           "2019/041-envy#b02-naval",              # 5 frases
           "2019/040-ethics#b04-naval"]            # 5 frases
N_REFS_ES = 5          # cuántos clips españoles se promedian para la huella
DUR_REF_ES = (6, 15)   # solo clips de entre 6 y 15 s: ni tan cortos que la huella sea pobre ni tan largos
FUERZA_MEDIA = 0.5     # la fuerza del LoRA en la versión lora_medio (1 = completo, 0 = base)
"""),
    code(f"""
# 3. Preparar: código del repo, Drive, texto de los bloques y referencias españolas (sin cargar modelos)
import os, sys, subprocess, json
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/fabrica", "/content/repo/piloto", "/content/repo/criba"]
import comun, fabrica, rutas

comun.montar_drive()
CFG = fabrica.cargar_config()
RAIZ_VOCES = Path(CFG["rutas"]["drive"]) / CFG["rutas"]["voces"]
NAVAL = CFG["voces"]["naval"]
ADAPTADOR = RAIZ_VOCES / NAVAL["adaptador"]
REF_EN = RAIZ_VOCES / NAVAL["ref"]
PAUSA = fabrica.pausa_de("naval", CFG)
SALIDA = RAIZ_VOCES / "piloto" / "acento_naval"
SALIDA.mkdir(parents=True, exist_ok=True)

items = []
for b in BLOQUES:
    ep, bloque = b.split("#")
    tr = json.loads((Path("/content/repo/episodios") / ep / "transcript.es.json").read_text(encoding="utf-8"))
    frases = next(x["frases"] for x in tr["contenido"] if x["id"] == bloque)
    items.append({{"id": f"{{ep.split('/')[1].split('-')[0]}}_{{bloque}}", "voz": "naval", "ref": "naval",
                  "frases": frases, "origen": b}})
    print(f"  {{items[-1]['id']}}: {{len(frases)}} frases, {{sum(len(f.split()) for f in frases)}} palabras")
# La página de escucha lee los items de este fichero
comun.FRASES = SALIDA / "frases.json"
comun.FRASES.write_text(json.dumps({{"schema": 1, "silencio_entre_frases_ms": 0, "items": items}},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
comun.SALIDA = SALIDA

SINT = rutas.sintetico(comun.DRIVE, "naval")
candidatos = [s for s in (json.loads(l) for l in (SINT / "seleccion.jsonl").read_text(encoding="utf-8").splitlines()
                          if l.strip())
              if s["variante"] == "chatterbox_v2" and DUR_REF_ES[0] <= s["segundos"] <= DUR_REF_ES[1]]
candidatos.sort(key=lambda s: -s["similitud"])
REFS_ES = [comun.DRIVE / s["audio"] for s in candidatos[:N_REFS_ES]]
print(f"Huella española: {{len(REFS_ES)}} clips de {{len(candidatos)}} candidatos")
for s in candidatos[:N_REFS_ES]:
    print(f"  {{s['id']}}: {{s['segundos']:.1f}} s · similitud {{s['similitud']:.2f}} · {{s['texto'][:60]}}…")

problemas = [str(p) for p in [REF_EN, ADAPTADOR / "adapter_model.safetensors", *REFS_ES] if not p.is_file()]
if len(REFS_ES) < N_REFS_ES:
    problemas.append(f"solo hay {{len(REFS_ES)}} clips españoles entre {{DUR_REF_ES}} s")
if problemas:
    print("RESULTADO: REVISAR")
    for p in problemas:
        print("  - falta:", p)
    raise SystemExit("Corrige lo de arriba antes de cargar modelos: todavía no se ha gastado nada.")
print(f"Pausas de {{PAUSA}} s, como en la fábrica. Salida: {{SALIDA.relative_to(comun.DRIVE)}}")
print("RESULTADO: OK")
"""),
    code("""
# 4. Cargar Qwen, el LoRA de Naval (entero y a media fuerza) y las tres huellas
import dataclasses, torch
from qwen_tts import Qwen3TTSModel
from peft import PeftModel
dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
tts = Qwen3TTSModel.from_pretrained(CFG["motor"]["modelo"], device_map="cuda:0", dtype=dtype,
                                    attn_implementation="sdpa")
peft = PeftModel.from_pretrained(tts.model.talker, str(ADAPTADOR), adapter_name="entero")
peft.load_adapter(str(ADAPTADOR), adapter_name="medio")
capas = 0
for m in peft.modules():
    if isinstance(getattr(m, "scaling", None), dict) and "medio" in m.scaling:
        m.scaling["medio"] *= FUERZA_MEDIA
        capas += 1
tts.model.talker = peft
peft.eval()
print(f"LoRA cargado; versión 'medio' al {FUERZA_MEDIA:.0%} en {capas} capas")

def huella(rutas_audio):
    \"\"\"Prompt de solo timbre con la media de las huellas de varios clips (con su norma media).\"\"\"
    it = tts.create_voice_clone_prompt(ref_audio=[str(r) for r in rutas_audio], x_vector_only_mode=True)
    embs = torch.stack([x.ref_spk_embedding for x in it])
    media = embs.mean(0)
    media = media / media.norm() * embs.norm(dim=-1).mean()
    return [dataclasses.replace(it[0], ref_spk_embedding=media)]

PROMPTS = {"en": huella([REF_EN]), "es1": huella(REFS_ES[:1]), "es5": huella(REFS_ES)}
sim = torch.nn.functional.cosine_similarity
for k in ("es1", "es5"):
    print(f"Huella {k}: parecido con la inglesa {sim(PROMPTS[k][0].ref_spk_embedding.float(), PROMPTS['en'][0].ref_spk_embedding.float(), dim=0):.2f}")
"""),
    code("""
# 5. Generar cada versión, como en la fábrica (misma semilla por frase y pausas recortadas)
import time, numpy as np, soundfile as sf
from contextlib import nullcontext
VERSIONES = {"actual": ("entero", "en"), "lora_ref_es1": ("entero", "es1"), "lora_ref_es5": ("entero", "es5"),
             "lora_medio_ref_es5": ("medio", "es5"), "base_ref_es5": (None, "es5")}
hueco = max(0.0, PAUSA - fabrica.RECORTE_INICIO - fabrica.RECORTE_FINAL)

for version, (adaptador, clave) in VERSIONES.items():
    (SALIDA / version).mkdir(exist_ok=True)
    def sintetizar(texto, voz, intento):
        if adaptador:
            peft.set_adapter(adaptador)
        with (peft.disable_adapter() if adaptador is None else nullcontext()):
            torch.manual_seed(fabrica.semilla(texto, intento))
            wavs, sr = tts.generate_voice_clone(text=texto, language=CFG["motor"]["idioma"],
                                                voice_clone_prompt=PROMPTS[clave],
                                                non_streaming_mode=CFG["motor"]["non_streaming_mode"])
        return wavs[0], sr
    for it in items:
        destino = SALIDA / version / f"{it['id']}.wav"
        if destino.exists():
            print(f"  {version}/{it['id']}: ya existe")
            continue
        t0, trozos, sr = time.time(), [], None
        for k, frase in enumerate(it["frases"]):
            r = fabrica.generar_frase(frase, "naval", sintetizar, None, CFG["verificacion"], PAUSA)
            sr = r["sr"]
            if k:
                trozos.append(np.zeros(int(sr * hueco), np.float32))
            trozos.append(r["audio"])
        audio = np.concatenate([np.zeros(int(sr * fabrica.BORDE_INICIO), np.float32), *trozos,
                                np.zeros(int(sr * fabrica.BORDE_FINAL), np.float32)])
        sf.write(str(destino), audio, sr, subtype="PCM_16")
        print(f"  {version}/{it['id']}: {len(audio) / sr:.1f} s en {time.time() - t0:.0f} s")
"""),
    code("""
# 6. Página de escucha a ciegas
import escucha
escucha.construir_pagina([it["id"] for it in items], list(VERSIONES), nombre="acento_naval")
print("Ábrela desde Drive (descárgala y ábrela en el navegador). Prioridad: el ACENTO, sin perder parecido.")
"""),
    code("""
# 7. Subir a Drive y desconectar
comun.desconectar()
"""),
])

# ---------------------------------------------------------------- Las erres de Naval
cuaderno("09_erres_naval.ipynb", [
    md("""
# Piloto de fine-tuning — las erres de Naval

El autor sigue oyendo a Naval con giros ingleses, sobre todo en la **r** y la **rr**. El cuaderno 08 descartó la
huella en español. Aquí se prueba **otro paso del LoRA y el modelo sin LoRA**, con frases reales de los episodios
escogidas por tener muchas erres (y sin nombres en inglés, para que lo único que suene inglés sea la voz):

| Versión | Modelo |
|---|---|
| `actual` | LoRA `B/paso_0158`, lo que suena hoy en la fábrica |
| `paso_0120`, `paso_0080`, `paso_0040` | pasos anteriores del mismo LoRA: menos horas oyendo a Naval en inglés |
| `base` | Qwen sin LoRA. En la criba, este modo sacó **5 de acento** con Naval en las tres frases (cuaderno 03c) |
| `actual_t07` | `actual` con temperatura 0,7 en vez de 0,9: menos variación al elegir cada sonido |

Todas con la referencia `naval_ref02` en modo solo timbre, la misma semilla por frase y pausas de 0,12 s, como
la fábrica. Salida en `fine_tunned_naval/piloto/erres_naval/`. La primera ronda se puntuó a ciegas (resultados en
`piloto/resultados/resumen.md`).

**Segunda ronda (3-nov):** la primera escucha dejó empatados el paso 120 y la actual con temperatura 0,7. Se añade
`paso_0120_t07` (las dos mejoras juntas). **No hay que puntuar:** la celda 6 pone aquí mismo, para cada audio, las
versiones de `ESCUCHAR` una debajo de otra, con su nombre. Lo ya generado no se repite: solo se genera la versión
nueva (unos 3–5 minutos).

**GPU:** T4. **Tiempo:** unos 15–20 minutos (unos 4 minutos de audio). Celda 1, *Reiniciar sesión* y el resto
en orden. Si se corta, vuelve a lanzar: lo que ya esté en Drive no se repite.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q qwen-tts==0.1.1 peft==0.17.1
"""),
    code("""
# 2. Parámetros
# Frases reales de Naval con muchas erres, sin nombres en inglés. Dos por audio.
ITEMS = {
    "r1": ["Es una respuesta escurridiza, pero creo que en realidad es la respuesta correcta.",
           "Acabar con un mono naranja en la cárcel o arruinar tu reputación es lo mismo que quedar barrido a cero, así que nunca hagas esas cosas."],
    "r2": ["Mañana podrían ser robots de reparto, robots voladores y robots mecánicos, y drones, que llevan cosas de un lado a otro.",
           "¿Ir corriendo por el barrio donde vive enseñándoselo a la gente en un ordenador o en una pantalla?"],
    "r3": ["Un escalón por encima de eso podrías tener a un contratista, un contratista general al que alguien contrata para venir a arreglar y reparar y levantar su casa.",
           "Quieres trabajar con gente de fiar durante periodos largos sin tener que reevaluar cada conversación ni mirar todo el rato por encima del hombro."],
}
# versión: (checkpoint del LoRA de Naval o None para Qwen sin LoRA, temperatura)
VERSIONES = {"actual": ("paso_0158", 0.9), "paso_0120": ("paso_0120", 0.9), "paso_0080": ("paso_0080", 0.9),
             "paso_0040": ("paso_0040", 0.9), "base": (None, 0.9), "actual_t07": ("paso_0158", 0.7),
             "paso_0120_t07": ("paso_0120", 0.7)}   # añadida el 3-nov: junta las dos mejoras de la primera escucha
# Qué versiones se escuchan en la celda 6, en este orden. Segunda ronda (3-nov): las dos ganadoras, su combinación
# y la actual como referencia. Las que ya están en Drive no se vuelven a generar.
ESCUCHAR = ["actual", "paso_0120", "actual_t07", "paso_0120_t07"]
"""),
    code(f"""
# 3. Preparar: código del repo, Drive y comprobación de los checkpoints (sin cargar modelos)
import os, sys, subprocess, json
from pathlib import Path
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/fabrica", "/content/repo/piloto", "/content/repo/criba"]
import comun, fabrica, rutas

comun.montar_drive()
CFG = fabrica.cargar_config()
RAIZ_VOCES = Path(CFG["rutas"]["drive"]) / CFG["rutas"]["voces"]
LORA = rutas.lora(comun.DRIVE, "B")
REF = RAIZ_VOCES / CFG["voces"]["naval"]["ref"]
PAUSA = fabrica.pausa_de("naval", CFG)
SALIDA = RAIZ_VOCES / "piloto" / "erres_naval"
SALIDA.mkdir(parents=True, exist_ok=True)

items = [{{"id": i, "voz": "naval", "ref": "naval", "frases": f}} for i, f in ITEMS.items()]
comun.FRASES = SALIDA / "frases.json"
comun.FRASES.write_text(json.dumps({{"schema": 1, "silencio_entre_frases_ms": 0, "items": items}},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
comun.SALIDA = SALIDA
CHECKPOINTS = sorted({{c for c, _ in VERSIONES.values() if c}})
problemas = [str(p) for p in [REF, *(LORA / c / "adapter_model.safetensors" for c in CHECKPOINTS)] if not p.is_file()]
if problemas:
    print("RESULTADO: REVISAR")
    for p in problemas:
        print("  - falta:", p)
    raise SystemExit("Corrige lo de arriba antes de cargar modelos: todavía no se ha gastado nada.")
print(f"{{len(VERSIONES)}} versiones · {{len(items)}} audios · checkpoints {{CHECKPOINTS}}")
print("RESULTADO: OK")
"""),
    code("""
# 4. Cargar Qwen con los checkpoints del LoRA de Naval
import torch
from transformers.utils import logging as hf_logging
hf_logging.set_verbosity_error()
from qwen_tts import Qwen3TTSModel
from peft import PeftModel
dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
tts = Qwen3TTSModel.from_pretrained(CFG["motor"]["modelo"], device_map="cuda:0", dtype=dtype,
                                    attn_implementation="sdpa")
peft = PeftModel.from_pretrained(tts.model.talker, str(LORA / CHECKPOINTS[0]), adapter_name=CHECKPOINTS[0])
for c in CHECKPOINTS[1:]:
    peft.load_adapter(str(LORA / c), adapter_name=c)
tts.model.talker = peft
peft.eval()
PROMPT = tts.create_voice_clone_prompt(ref_audio=str(REF), x_vector_only_mode=True)
print(f"Qwen cargado ({dtype}) con {CHECKPOINTS}")
"""),
    code("""
# 5. Generar cada versión, como en la fábrica (misma semilla por frase y pausas recortadas)
import time, numpy as np, soundfile as sf
from contextlib import nullcontext
hueco = max(0.0, PAUSA - fabrica.RECORTE_INICIO - fabrica.RECORTE_FINAL)

for version, (checkpoint, temperatura) in VERSIONES.items():
    (SALIDA / version).mkdir(exist_ok=True)
    def sintetizar(texto, voz, intento):
        if checkpoint:
            peft.set_adapter(checkpoint)
        with (peft.disable_adapter() if checkpoint is None else nullcontext()):
            torch.manual_seed(fabrica.semilla(texto, intento))
            wavs, sr = tts.generate_voice_clone(text=texto, language=CFG["motor"]["idioma"], voice_clone_prompt=PROMPT,
                                                non_streaming_mode=CFG["motor"]["non_streaming_mode"],
                                                temperature=temperatura, subtalker_temperature=temperatura,
                                                max_new_tokens=fabrica.tope_pasos(texto))
        return wavs[0], sr
    for it in items:
        destino = SALIDA / version / f"{it['id']}.wav"
        if destino.exists():
            print(f"  {version}/{it['id']}: ya existe")
            continue
        t0, trozos, sr = time.time(), [], None
        for k, frase in enumerate(it["frases"]):
            r = fabrica.generar_frase(frase, "naval", sintetizar, None, CFG["verificacion"], PAUSA)
            sr = r["sr"]
            if k:
                trozos.append(np.zeros(int(sr * hueco), np.float32))
            trozos.append(r["audio"])
        audio = np.concatenate([np.zeros(int(sr * fabrica.BORDE_INICIO), np.float32), *trozos,
                                np.zeros(int(sr * fabrica.BORDE_FINAL), np.float32)])
        sf.write(str(destino), audio, sr, subtype="PCM_16")
        print(f"  {version}/{it['id']}: {len(audio) / sr:.1f} s en {time.time() - t0:.0f} s")
"""),
    code("""
# 6. Escuchar aquí mismo: cada audio con todas las versiones de ESCUCHAR, una debajo de otra
from IPython.display import Audio, Markdown, display
for it in items:
    display(Markdown(f"### {it['id']}\\n> " + " ".join(it["frases"])))
    for v in ESCUCHAR:
        ruta = SALIDA / v / f"{it['id']}.wav"
        if not ruta.exists():
            display(Markdown(f"**{v}**: no generado"))
            continue
        checkpoint, temperatura = VERSIONES[v]
        display(Markdown(f"**{v}** — {checkpoint or 'sin LoRA'}, temperatura {temperatura}"))
        display(Audio(str(ruta)))
"""),
    code("""
# 7. Subir a Drive y desconectar
comun.desconectar()
"""),
])
