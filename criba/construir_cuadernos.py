#!/usr/bin/env python3
"""Genera los cuadernos de Colab de la criba en criba/cuadernos/.

    python3 criba/construir_cuadernos.py

Los .ipynb son GENERADOS: para cambiar un cuaderno se edita este fichero y se regenera.
Así todos comparten exactamente la misma estructura de celdas.
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
    colab = {"provenance": []}
    if gpu:
        colab["gpuType"] = gpu
    nb = {
        "nbformat": 4, "nbformat_minor": 0,
        "metadata": {
            **({"accelerator": "GPU"} if gpu else {}),
            "colab": colab,
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"},
        },
        "cells": celdas,
    }
    DESTINO.mkdir(exist_ok=True)
    (DESTINO / nombre).write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("escrito", DESTINO / nombre)


def cabecera(titulo, gpu, minutos, que):
    return md(f"""
# Criba de motores TTS — {titulo}

{que}

**GPU:** {gpu}. **Tiempo estimado:** {minutos}, incluida la instalación.

**Cómo se usa** (es igual en todos los cuadernos de la criba):

1. *Entorno de ejecución → Cambiar tipo de entorno* → **{gpu}**.
2. Ejecuta la **celda 1** (instalación). Cuando termine, *Entorno de ejecución → Reiniciar sesión*.
3. Ejecuta las demás celdas **en orden**, de la 2 a la última. La celda 2 comprueba que estén las
   referencias y las frases antes de cargar ningún modelo: si dice `RESULTADO: REVISAR`, para ahí.
4. La última celda **desconecta la GPU sola** para que no siga gastando unidades.

Si la sesión se corta a medias, vuelve a empezar por la celda 1: lo que ya esté en Drive no se
genera otra vez.

Salida: `fine_tunned_naval/outputs/criba/<variante>/` en Drive, un `.wav` por item (`n01`, `v01`,
`b01`, `k01`…) más `registro.jsonl`, `parametros.json` y `entorno.json`.
""")


def preparar(voces="None"):
    return code(f"""
# 2. Preparar: código del repo, Drive, frases y referencias
import os, sys, subprocess
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path.insert(0, "/content/repo/criba")
import comun

print(sys.version.split()[0], "|", subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                                                  capture_output=True, text=True).stdout.strip())
comun.montar_drive()
ITEMS, SILENCIO_MS = comun.cargar_items({voces})
REFS = comun.comprobar(ITEMS)
""")


def cierre(variantes):
    return code(f"""
# Última celda: resumen y desconexión de la GPU
import json
for variante in {variantes!r}:
    reg = comun.SALIDA / variante / "registro.jsonl"
    if not reg.exists():
        print(f"{{variante}}: sin registro")
        continue
    filas = [json.loads(l) for l in reg.read_text(encoding="utf-8").splitlines()]
    ok = sum(f["ok"] for f in filas)
    print(f"{{variante}}: {{ok}} items correctos, {{len(filas) - ok}} con error")
comun.desconectar()
""")


# ---------------------------------------------------------------- Chatterbox
cuaderno("01_chatterbox.ipynb", [
    cabecera("Chatterbox Multilingual (V2, V3 y pack es-es)", "T4", "unos 60 min",
             "Tres variantes del mismo motor, una detrás de otra: **V2** (la que ganó tu criba de junio), "
             "**V3** y **V3 con el pack de español de España** (`ResembleAI/Chatterbox-Multilingual-es-es`). "
             "Parámetros por defecto de la librería: `exaggeration=0.5`, `cfg_weight=0.5`, `temperature=0.8`."),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# chatterbox-tts fija torch 2.6.0, transformers 5.2.0 y numpy<2: por eso hay que reiniciar.
# Se instala desde GitHub: la 0.1.7 de PyPI es anterior a la V3 y solo carga la V2.
# torchvision se fija a la versión que casa con torch 2.6.0: la que trae Colab pide otro torch.
# El aviso rojo "pip's dependency resolver..." que sale después es normal.
!pip install -q "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git@master" torchvision==0.21.0
"""),
    preparar(),
    code("""
# 3. Funciones de carga y síntesis
import os, shutil, torch
from pathlib import Path
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from huggingface_hub import snapshot_download

INFO = {}

def cargar(variante):
    if variante == "chatterbox_v2":
        return ChatterboxMultilingualTTS.from_pretrained(device="cuda", t3_model="v2")
    if variante == "chatterbox_v3":
        return ChatterboxMultilingualTTS.from_pretrained(device="cuda", t3_model="v3")
    if variante == "chatterbox_v3_es":
        # El pack es un fine-tune de T3. Se combina con las piezas comunes del repo base.
        base = Path(snapshot_download("ResembleAI/chatterbox", allow_patterns=[
            "ve.pt", "s3gen.pt", "grapheme_mtl_merged_expanded_v1.json", "conds.pt", "Cangjie5_TC.json"]))
        pack = Path(snapshot_download("ResembleAI/Chatterbox-Multilingual-es-es"))
        print("Ficheros del pack es-es:", sorted(p.name for p in pack.rglob("*") if p.is_file()))
        if (pack / "README.md").exists():
            print("--- README del pack (primeras líneas) ---")
            print("\\n".join((pack / "README.md").read_text(encoding="utf-8").splitlines()[:40]))
            print("---")
        junto = Path("/content/chatterbox_es_es")
        junto.mkdir(exist_ok=True)
        for origen in (base, pack):
            for p in origen.rglob("*"):
                if p.is_file() and p.suffix in {".pt", ".json", ".safetensors"}:
                    shutil.copy(p, junto / p.name)
        t3s = sorted(p.name for p in pack.rglob("t3*.safetensors"))
        assert t3s, "El pack no trae ningún t3*.safetensors: revisa la lista de ficheros de arriba"
        t3 = t3s[0]
        print("T3 del pack:", t3)
        # El pack trae su propio decodificador (s3gen_v3). Se intenta con él; si no casa con
        # el código instalado, se vuelve al s3gen base y queda anotado en parametros.json.
        if (pack / "s3gen_v3.pt").exists():
            shutil.copy(pack / "s3gen_v3.pt", junto / "s3gen.pt")
            try:
                INFO[variante] = {"t3": t3, "s3gen": "s3gen_v3.pt del pack"}
                return ChatterboxMultilingualTTS.from_local(junto, "cuda", t3_model=t3)
            except Exception as e:
                print(f"s3gen_v3 del pack no carga ({type(e).__name__}: {str(e)[:200]}); pruebo con el s3gen base")
                shutil.copy(base / "s3gen.pt", junto / "s3gen.pt")
        INFO[variante] = {"t3": t3, "s3gen": "s3gen.pt base"}
        return ChatterboxMultilingualTTS.from_local(junto, "cuda", t3_model=t3)
    raise ValueError(variante)

PARAMS = dict(exaggeration=0.5, cfg_weight=0.5, temperature=0.8)

def hacer_sintetizar(modelo):
    ref_cargada = {"wav": None}
    def sintetizar(texto, ref):
        if ref_cargada["wav"] != ref["wav"]:
            modelo.prepare_conditionals(ref["wav"], exaggeration=PARAMS["exaggeration"])
            ref_cargada["wav"] = ref["wav"]
        wav = modelo.generate(texto, language_id="es", **PARAMS)
        return wav, modelo.sr
    return sintetizar
print("OK")
"""),
    code("""
# 4. Generar las tres variantes (se salta lo que ya esté en Drive)
for variante in ["chatterbox_v2", "chatterbox_v3", "chatterbox_v3_es"]:
    print(f"\\n=== {variante}")
    try:
        modelo = cargar(variante)
    except Exception as e:
        print(f"No se pudo cargar {variante}: {type(e).__name__}: {e}. Paso a la siguiente.")
        continue
    comun.guardar_entorno(variante, ["chatterbox-tts", "torch", "transformers", "numpy"])
    comun.generar(variante, hacer_sintetizar(modelo), ITEMS, REFS, SILENCIO_MS,
                  params={**PARAMS, "language_id": "es", **INFO.get(variante, {})})
    del modelo
    comun.liberar()
"""),
    cierre(["chatterbox_v2", "chatterbox_v3", "chatterbox_v3_es"]),
], gpu="T4")

# ---------------------------------------------------------------- OmniVoice
cuaderno("02_omnivoice.ipynb", [
    cabecera("OmniVoice", "T4", "unos 30 min",
             "`k2-fsa/OmniVoice` en modo clonación (referencia + su transcripción), `language=\"es\"`, "
             "float16 y el resto de parámetros por defecto."),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
!pip install -q omnivoice==0.2.1
"""),
    preparar(),
    code("""
# 3. Cargar el modelo
import torch
from omnivoice import OmniVoice
comun.guardar_entorno("omnivoice", ["omnivoice", "torch", "transformers"])
modelo = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0", dtype=torch.float16)
SR = modelo.sampling_rate or 24000

def sintetizar(texto, ref):
    audios = modelo.generate(text=texto, language="es", ref_audio=ref["wav"], ref_text=ref["texto"])
    return audios[0], SR
print("OK, sale a", SR, "Hz")
"""),
    code("""
# 4. Generar
comun.generar("omnivoice", sintetizar, ITEMS, REFS, SILENCIO_MS,
              params={"modelo": "k2-fsa/OmniVoice", "language": "es", "dtype": "float16"})
"""),
    cierre(["omnivoice"]),
], gpu="T4")

# ---------------------------------------------------------------- OmniVoice: prueba de acento
cuaderno("02b_omnivoice_acento.ipynb", [
    cabecera("OmniVoice, prueba de acento", "L4 o T4", "unos 15 min",
             "¿Se puede rebajar el acento inglés de OmniVoice sin entrenar? Repite **10 frases de Naval** con tres "
             "ajustes y las deja junto a las del cuaderno 02 para comparar el mismo item:\n\n"
             "| Variante | Referencia | `guidance_scale` |\n|---|---|---|\n"
             "| `omnivoice` (ya hecha, cuaderno 02) | `naval_ref02` (~12 s) | 2,0 (por defecto) |\n"
             "| `omnivoice_ref01` | `naval_ref01` (~6 s) | 2,0 |\n"
             "| `omnivoice_g3` | `naval_ref02` | 3,0 |\n"
             "| `omnivoice_ref01_g3` | `naval_ref01` | 3,0 |\n\n"
             "Por qué: OmniVoice recomienda referencias de 3–10 s; cuanto más larga, más forma de hablar inglesa copia. "
             "Una guía más alta lo ciñe más al texto y a la etiqueta de idioma `es`."),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
!pip install -q omnivoice==0.2.1
"""),
    code(f"""
# 2. Preparar: código del repo, Drive, frases y las dos referencias de Naval
import os, sys, subprocess
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path.insert(0, "/content/repo/criba")
import comun

comun.montar_drive()
TODOS, SILENCIO_MS = comun.cargar_items(["naval"])
ESCOGIDOS = ["n01", "n03", "n05", "n07", "n10", "n12", "n14", "n17", "n21", "n25"]
ITEMS = [it for it in TODOS if it["id"] in ESCOGIDOS]
REF02 = comun.comprobar(ITEMS, slot="ref02")
REF01 = comun.comprobar(ITEMS, slot="ref01")
"""),
    code("""
# 3. Cargar el modelo
import torch
from pathlib import Path
from omnivoice import OmniVoice
modelo = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0", dtype=torch.float16)
SR = modelo.sampling_rate or 24000

def hacer_sintetizar(guia):
    def sintetizar(texto, ref):
        audios = modelo.generate(text=texto, language="es", ref_audio=ref["wav"], ref_text=ref["texto"],
                                 guidance_scale=guia)
        return audios[0], SR
    return sintetizar
print("OK, sale a", SR, "Hz")
"""),
    code("""
# 4. Generar las tres variantes
VARIANTES = [("omnivoice_ref01", REF01, 2.0), ("omnivoice_g3", REF02, 3.0), ("omnivoice_ref01_g3", REF01, 3.0)]
for variante, refs, guia in VARIANTES:
    print(f"\\n=== {variante}")
    comun.guardar_entorno(variante, ["omnivoice", "torch", "transformers"])
    comun.generar(variante, hacer_sintetizar(guia), ITEMS, refs, SILENCIO_MS,
                  params={"modelo": "k2-fsa/OmniVoice", "language": "es", "dtype": "float16",
                          "guidance_scale": guia, "ref": Path(refs["naval"]["wav"]).name})
"""),
    cierre(["omnivoice_ref01", "omnivoice_g3", "omnivoice_ref01_g3"]),
], gpu="L4")

# ---------------------------------------------------------------- Qwen3-TTS
cuaderno("03_qwen3tts.ipynb", [
    cabecera("Qwen3-TTS 1.7B Base", "L4", "unos 40 min",
             "`Qwen/Qwen3-TTS-12Hz-1.7B-Base` en modo clonación (referencia + su transcripción), "
             "`language=\"Spanish\"`, atención SDPA (sin flash-attn, que no compila en Colab sin esperar mucho). "
             "Ojo: su fine-tuning oficial deja la voz fija y ya no acepta referencia; aquí solo se mide el zero-shot."),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
!pip install -q qwen-tts==0.1.1
"""),
    preparar(),
    code("""
# 3. Cargar el modelo
import torch
from qwen_tts import Qwen3TTSModel
comun.guardar_entorno("qwen3tts_1.7b", ["qwen-tts", "torch", "transformers", "accelerate"])
DTYPE = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
modelo = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cuda:0",
                                       dtype=DTYPE, attn_implementation="sdpa")
_prompts = {}

def sintetizar(texto, ref):
    if ref["wav"] not in _prompts:
        _prompts[ref["wav"]] = modelo.create_voice_clone_prompt(ref_audio=ref["wav"], ref_text=ref["texto"],
                                                                x_vector_only_mode=False)
    wavs, sr = modelo.generate_voice_clone(text=texto, language="Spanish",
                                           voice_clone_prompt=_prompts[ref["wav"]])
    return wavs[0], sr
print("OK,", DTYPE)
"""),
    code("""
# 4. Generar
comun.generar("qwen3tts_1.7b", sintetizar, ITEMS, REFS, SILENCIO_MS,
              params={"modelo": "Qwen/Qwen3-TTS-12Hz-1.7B-Base", "language": "Spanish",
                      "dtype": str(DTYPE), "x_vector_only_mode": False})
"""),
    cierre(["qwen3tts_1.7b"]),
], gpu="L4")

# ---------------------------------------------------------------- dots.tts
cuaderno("04_dots.ipynb", [
    cabecera("dots.tts (SOAR)", "L4", "unos 45 min",
             "`dots-studio/dots.tts-soar`, el checkpoint de mayor similitud y base de su fine-tuning, en modo "
             "continuación (referencia + su transcripción), `language=\"es\"`, `num_steps=10`, `guidance_scale=1.2`.\n\n"
             "dots.tts solo admite Python 3.10–3.12 y Colab ya trae 3.13: la celda 1 crea un Python 3.12 aparte "
             "(con `uv`) solo para él, y la celda 3 genera desde ahí con `criba/motores/dots_generar.py`."),
    code("""
# 1. Instalación: un Python 3.12 aparte solo para dots.tts (unos 5 min)
# Aquí no hace falta reiniciar la sesión, pero no pasa nada si lo haces.
!pip install -q uv
!uv python install 3.12
!uv venv -q --clear --python 3.12 /content/venv_dots
# torch y torchaudio tienen que ir a juego: se fijan las versiones que recomienda dots.tts
# (constraints/recommended.txt). transformers 4.57.0 está retirada de PyPI: se usa la 4.57.1.
!uv pip install -q --python /content/venv_dots/bin/python dots-tts==0.3.1 torch==2.8.0 torchaudio==2.8.0 transformers==4.57.1 soundfile numpy
!/content/venv_dots/bin/python -c "import dots_tts, torch; print('dots-tts OK | torch', torch.__version__, '| CUDA', torch.cuda.is_available())"
"""),
    preparar(),
    code("""
# 3. Generar (en el Python 3.12 aparte; se salta lo que ya esté en Drive)
!/content/venv_dots/bin/python -u /content/repo/criba/motores/dots_generar.py
"""),
    cierre(["dots_soar"]),
], gpu="L4")

# ---------------------------------------------------------------- XTTS
cuaderno("05_xtts.ipynb", [
    cabecera("XTTS v2 (base y tu fine-tune navalchris)", "T4", "unos 40 min",
             "La referencia de lo que ya tienes. Dos variantes: **XTTS v2 base** en zero-shot con las 55 frases, "
             "y tu **fine-tune `xtts_finetunned_navalchris`** solo con las de Naval (`n` y `k`), que nunca llegó a "
             "medirse. Mismos parámetros que tu cuaderno de producción: `temperature=0.75`, "
             "`repetition_penalty=3.0`, `top_p=0.8`, `top_k=60`."),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# Las mismas versiones con las que se entrenó navalchris.
!pip install -q coqui-tts==0.27.5 "coqui-tts-trainer>=0.3.0,<0.4.0" "transformers==4.57.1"
"""),
    preparar(),
    code("""
# 3. Funciones de carga y síntesis
import os, torch
os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

PESOS = comun.DRIVE / "weights"
GEN = dict(temperature=0.75, repetition_penalty=3.0, top_p=0.8, top_k=60, length_penalty=1.0,
           enable_text_splitting=False)

def cargar(variante):
    if variante == "xtts_base":
        return TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda").synthesizer.tts_model
    carpeta = PESOS / "xtts_finetunned_navalchris"
    config = XttsConfig(); config.load_json(str(carpeta / "config.json"))
    m = Xtts.init_from_config(config)
    m.load_checkpoint(config, checkpoint_path=str(carpeta / "best_model.pth"),
                      vocab_path=str(PESOS / "vocab.json"), use_deepspeed=False)
    return m.cuda()

def hacer_sintetizar(modelo):
    latentes = {}
    def sintetizar(texto, ref):
        if ref["wav"] not in latentes:
            latentes[ref["wav"]] = modelo.get_conditioning_latents(
                audio_path=[ref["wav"]], gpt_cond_len=12, gpt_cond_chunk_len=6, max_ref_length=12)
        gpt, spk = latentes[ref["wav"]]
        out = modelo.inference(texto, "es", gpt, spk, **GEN)
        return out["wav"], 24000
    return sintetizar
print("OK")
"""),
    code("""
# 4. Generar las dos variantes
SOLO_NAVAL = [it for it in ITEMS if it["voz"] == "naval"]
for variante, items in [("xtts_base", ITEMS), ("xtts_navalchris", SOLO_NAVAL)]:
    print(f"\\n=== {variante} ({len(items)} items)")
    try:
        modelo = cargar(variante)
    except Exception as e:
        print(f"No se pudo cargar {variante}: {type(e).__name__}: {e}. Paso a la siguiente.")
        continue
    comun.guardar_entorno(variante, ["coqui-tts", "torch", "transformers"])
    comun.generar(variante, hacer_sintetizar(modelo), items, REFS, SILENCIO_MS, params=GEN)
    del modelo
    comun.liberar()
"""),
    cierre(["xtts_base", "xtts_navalchris"]),
], gpu="T4")

# ---------------------------------------------------------------- Métricas y escucha
cuaderno("06_metricas_y_escucha.ipynb", [
    md("""
# Criba de motores TTS — métricas y página de escucha

Se ejecuta **después** de los cuadernos 01–05; mide lo que haya en `outputs/criba/` aunque falte algún
motor. Reutiliza el método de tu `compare_xtts_vs_chatterbox`:

- **WER** con Whisper large-v3 (vía `transformers`) en español: palabras que el audio no dice como debe. Detecta
  alucinaciones, saltos y repeticiones.
- **Similitud** con ECAPA-TDNN entre cada audio y la media de las 3 referencias de su voz, en inglés.
- **UTMOSv2**: calidad percibida estimada, de 1 a 5.

Después monta **`escucha.html`**, la página de escucha a ciegas: las versiones de cada frase aparecen
con letras al azar, y la clave para descifrarlas se guarda aparte, en `clave.json`.

**GPU:** T4. **Tiempo estimado:** unos 40 min. Mismo uso que los demás: celda 1, reiniciar sesión,
y el resto en orden. Lo ya medido no se vuelve a medir.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
!pip install -q jiwer speechbrain soundfile librosa pandas
!pip install -q git+https://github.com/sarulab-speech/UTMOSv2.git
"""),
    code(f"""
# 2. Preparar
import os, sys, subprocess, json
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path.insert(0, "/content/repo/criba")
import comun
comun.montar_drive()
ITEMS, _ = comun.cargar_items()
POR_ID = {{it["id"]: it for it in ITEMS}}
METRICAS = comun.SALIDA / "metricas"
METRICAS.mkdir(parents=True, exist_ok=True)
VARIANTES = sorted(p.name for p in comun.SALIDA.iterdir() if (p / "registro.jsonl").exists())
AUDIOS = [(v, i) for v in VARIANTES for i in POR_ID if (comun.SALIDA / v / f"{{i}}.wav").exists()]
print("Variantes:", VARIANTES)
print("Audios a medir:", len(AUDIOS))
"""),
    code("""
# 3. WER con Whisper large-v3 (vía transformers: faster-whisper necesita CUDA 12 y Colab trae CUDA 13)
import re, jiwer, torch
import numpy as np, soundfile as sf, librosa
from transformers import pipeline

def normaliza(t):
    t = t.lower()
    t = re.sub(r"[^\\wáéíóúüñ\\s]", " ", t)
    return re.sub(r"\\s+", " ", t).strip()

def audio_16k(ruta):
    a, sr = sf.read(str(ruta), dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    return librosa.resample(a, orig_sr=sr, target_sr=16000) if sr != 16000 else a

def cargar_cache(nombre):
    f = METRICAS / nombre
    return {(d["variante"], d["id"]): d for d in map(json.loads, f.read_text(encoding="utf-8").splitlines())} if f.exists() else {}

def anadir(nombre, fila):
    with (METRICAS / nombre).open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\\n")

asr_hecho = cargar_cache("asr.jsonl")
asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3",
               torch_dtype=torch.float16, device="cuda:0", chunk_length_s=30)
for v, i in AUDIOS:
    if (v, i) in asr_hecho:
        continue
    salida = asr({"raw": audio_16k(comun.SALIDA / v / f"{i}.wav"), "sampling_rate": 16000},
                 generate_kwargs={"language": "spanish", "task": "transcribe"})
    hyp = salida["text"].strip()
    ref = " ".join(POR_ID[i]["frases"])
    fila = {"variante": v, "id": i, "wer": jiwer.wer(normaliza(ref), normaliza(hyp)) if normaliza(hyp) else 1.0,
            "transcripcion": hyp}
    anadir("asr.jsonl", fila)
    asr_hecho[(v, i)] = fila
del asr
comun.liberar()
print("WER hecho:", len(asr_hecho))
"""),
    code("""
# 4. Similitud de hablante con ECAPA-TDNN
import torch, torchaudio
from speechbrain.inference.speaker import EncoderClassifier
spk = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="/content/ecapa",
                                     run_opts={"device": "cuda"})

def embed(ruta):
    sig, sr = torchaudio.load(str(ruta))
    sig = sig.mean(0, keepdim=True)
    if sr != 16000:
        sig = torchaudio.functional.resample(sig, sr, 16000)
    with torch.no_grad():
        e = spk.encode_batch(sig.to("cuda")).squeeze()
    return e / e.norm()

# La identidad se compara siempre con las referencias normales de la voz (los items k también con naval/)
voz_ref = {}
for voz in sorted({it["voz"] for it in ITEMS}):
    clips = sorted((comun.REFS / voz).glob(f"{voz}_ref*.wav"))
    m = torch.stack([embed(c) for c in clips]).mean(0)
    voz_ref[voz] = m / m.norm()
    print(voz, "referencias:", [c.name for c in clips])

sim_hecho = cargar_cache("similitud.jsonl")
for v, i in AUDIOS:
    if (v, i) in sim_hecho:
        continue
    s = float((embed(comun.SALIDA / v / f"{i}.wav") * voz_ref[POR_ID[i]["voz"]]).sum())
    fila = {"variante": v, "id": i, "similitud": s}
    anadir("similitud.jsonl", fila)
    sim_hecho[(v, i)] = fila
del spk
comun.liberar()
print("Similitud hecha:", len(sim_hecho))
"""),
    code("""
# 5. Calidad estimada con UTMOSv2
import utmosv2
mos_modelo = utmosv2.create_model(pretrained=True)
mos_hecho = cargar_cache("utmos.jsonl")
for v, i in AUDIOS:
    if (v, i) in mos_hecho:
        continue
    fila = {"variante": v, "id": i, "utmos": float(mos_modelo.predict(input_path=str(comun.SALIDA / v / f"{i}.wav")))}
    anadir("utmos.jsonl", fila)
    mos_hecho[(v, i)] = fila
del mos_modelo
comun.liberar()
print("UTMOS hecho:", len(mos_hecho))
"""),
    code("""
# 6. Tablas
import pandas as pd
filas = []
for v, i in AUDIOS:
    reg = {}
    for l in (comun.SALIDA / v / "registro.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(l)
        if d["id"] == i and d.get("ok"):
            reg = d
    filas.append({"variante": v, "id": i, "voz": POR_ID[i]["voz"], "ref": POR_ID[i]["ref"],
                  "wer": asr_hecho[(v, i)]["wer"], "similitud": sim_hecho[(v, i)]["similitud"],
                  "utmos": mos_hecho[(v, i)]["utmos"], "seg_audio": reg.get("segundos_audio"),
                  "seg_gen": reg.get("segundos_generacion"), "transcripcion": asr_hecho[(v, i)]["transcripcion"]})
df = pd.DataFrame(filas)
df["alucinacion_probable"] = df["wer"] > 0.15
df.to_csv(METRICAS / "detalle.csv", index=False)

resumen = df.groupby("variante").agg(
    wer_medio=("wer", "mean"), items_con_wer_alto=("alucinacion_probable", "sum"),
    similitud=("similitud", "mean"), utmos=("utmos", "mean"),
    rtf=("seg_gen", "sum")).reset_index()
resumen["rtf"] = resumen["rtf"] / df.groupby("variante")["seg_audio"].sum().values
resumen = resumen.sort_values("wer_medio")
resumen.to_csv(METRICAS / "resumen.csv", index=False)
por_voz = df.pivot_table(index="variante", columns="voz", values=["wer", "similitud"], aggfunc="mean")
por_voz.to_csv(METRICAS / "por_voz.csv")
pd.set_option("display.width", 200)
print("=== RESUMEN (WER: menos es mejor; similitud y UTMOS: más es mejor; rtf<1 es más rápido que tiempo real)")
print(resumen.round(3).to_string(index=False))
print("\\n=== POR VOZ")
print(por_voz.round(3).to_string())
print("\\n=== Peores WER (posibles alucinaciones)")
print(df.sort_values("wer", ascending=False).head(15)[["variante", "id", "wer", "transcripcion"]].to_string(index=False))
"""),
    code("""
# 7. Página de escucha a ciegas (el código está en criba/escucha.py)
# Elige qué se escucha: 14 items representativos y las variantes que quieras (por defecto, todas).
import escucha
ITEMS_ESCUCHA = ["n01", "n05", "n10", "n14", "n17", "n23", "n25", "v02", "v05", "v09", "b03", "b10", "k04", "k09"]
escucha.construir_pagina(ITEMS_ESCUCHA, VARIANTES, nombre="escucha")
"""),
    code("""
# 8. Desconectar la GPU
comun.desconectar()
"""),
], gpu="T4")

# ---------------------------------------------------------------- Escucha corta (sin GPU)
cuaderno("07_escucha_larga.ipynb", [
    md("""
# Criba de motores TTS — escucha rápida, solo audios largos

Monta una página de escucha a ciegas **más corta** que la del cuaderno 06: solo los audios largos, que
son los que se parecen a producción, y sin las variantes que las métricas ya descartan.

| Item | Qué es |
|---|---|
| `n25` | Naval, bloque de 9 frases seguidas (~30 s) |
| `k10` | El mismo bloque con la referencia del episodio de Kapil: prueba de tono |
| `b10` | Brett, el mismo bloque |
| `v10` | Nivi, su frase más larga (~15 s) |

Variantes: `chatterbox_v2`, `chatterbox_v3_es`, `omnivoice`, `qwen3tts_1.7b`, `dots_soar` y `xtts_base`.
Fuera quedan `chatterbox_v3`, que lo supera su versión con el pack de español, y `xtts_navalchris`, que no
mejora a XTTS base.

**No necesita GPU.** *Entorno de ejecución → Cambiar tipo de entorno → CPU*, y ejecuta las tres celdas en
orden. Tarda un par de minutos.

Sale `outputs/criba/escucha/escucha_larga.html` en Drive. Descárgala, ábrela en el navegador, puntúa y
pulsa «Descargar puntuaciones (CSV)». Sube el CSV a la misma carpeta. No abras `clave_escucha_larga.json`.
"""),
    code(f"""
# 1. Preparar: código del repo y Drive
import os, sys, subprocess
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path.insert(0, "/content/repo/criba")
import comun, escucha
comun.montar_drive()
"""),
    code("""
# 2. Montar la página
ITEMS = ["n25", "k10", "b10", "v10"]
VARIANTES = ["chatterbox_v2", "chatterbox_v3_es", "omnivoice", "qwen3tts_1.7b", "dots_soar", "xtts_base"]
escucha.construir_pagina(ITEMS, VARIANTES, nombre="escucha_larga")
"""),
    code("""
# 3. Subir a Drive y desconectar
comun.desconectar()
"""),
], gpu=None)
