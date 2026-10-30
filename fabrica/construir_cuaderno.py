#!/usr/bin/env python3
"""Genera el cuaderno de Colab de la fábrica de voz: fabrica/fabrica.ipynb.

    python3 fabrica/construir_cuaderno.py

El .ipynb es GENERADO: se edita este fichero y se regenera. La lógica está en fabrica/fabrica.py y la
configuración (voces, adaptadores, pausas, verificación, rutas) en fabrica/voces.json.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
RAMA = "claude/quirky-dirac-x18c3n"
REPO = "https://github.com/DreiSup/spanishnav.al-podcast"


def md(texto):
    return {"cell_type": "markdown", "metadata": {}, "source": texto.strip("\n")}


def code(texto):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": texto.strip("\n")}


CELDAS = [
    md("""
# Fábrica de voz — doblar episodios

Le dices qué episodios quieres y deja en Drive **un clip por intervención**, en el orden del transcript:
`001nivi.wav`, `002naval.wav`… dentro de `naval-podcast/transcripts/<año>/<NNN Título>/tts/`. Es lo que
luego se limpia en Audacity.

Para cada episodio:

1. Lee su `transcript.es.json` del repo y decide la voz de cada hablante con `fabrica/voces.json`: qué
   referencia y qué LoRA usa cada uno (si no tiene LoRA, Qwen base). En los episodios con Kapil Gupta,
   Naval usa su modelo `naval_kapil`.
2. Genera frase a frase con Qwen3-TTS en modo solo timbre. **Whisper revisa cada frase** y, si no dice el
   texto o deja una cola rara, la repite con otra semilla (hasta 2 veces).
3. Recorta los silencios y une las frases con **0,12 s** de pausa, el ritmo que elegiste.
4. Deja junto a `tts/` un **`informe_tts.md`** con las frases que siguen sospechosas y el segundo exacto
   donde están, un `registro_tts.jsonl` con el detalle y un `borrador_tts.wav` con todo seguido para una
   escucha rápida.

Si se corta, vuelve a ejecutarlo: los clips que ya están en Drive no se repiten. Para rehacer uno, bórralo
de `tts/` y vuelve a lanzar.

**GPU: L4** (vale T4, más lenta). La celda 3 estima los minutos de audio de cada episodio; la 5 mide al final
cuántos segundos de GPU cuesta cada segundo de audio, para calcular el gasto de los demás episodios.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q qwen-tts==0.1.1 peft==0.17.1 jiwer num2words
"""),
    code("""
# 2. Parámetros
EPISODIOS = ["2019/035-finally-wealthy"]   # carpetas de episodios/ del repo, tantas como quieras
VERIFICAR = True     # revisar cada frase con Whisper y repetir las que fallen (más lento, mucho menos Audacity)
"""),
    code(f"""
# 3. Preparar: código del repo, Drive, voces y plan de cada episodio (sin cargar modelos)
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
CFG["verificacion"]["activa"] = VERIFICAR
DRIVE = Path(CFG["rutas"]["drive"])
RAIZ_VOCES = DRIVE / CFG["rutas"]["voces"]
RAIZ_EPISODIOS = DRIVE / CFG["rutas"]["episodios"]

PLANES, problemas = {{}}, []
for ep in EPISODIOS:
    base = Path("/content/repo/episodios") / ep
    if not (base / "transcript.es.json").is_file():
        problemas.append(f"{{ep}}: no hay transcript.es.json en el repo")
        continue
    tr = json.loads((base / "transcript.es.json").read_text(encoding="utf-8"))
    try:
        PLANES[ep] = fabrica.plan_episodio(tr, CFG)
    except ValueError as e:
        problemas.append(f"{{ep}}: {{e}}")
        continue
    titulo_en = json.loads((base / "metadata.en.json").read_text(encoding="utf-8"))["titulo"]
    carpeta = fabrica.carpeta_episodio(RAIZ_EPISODIOS, ep, titulo_en, crear=False)
    hechos = sum((carpeta / "tts" / p["fichero"]).exists() for p in PLANES[ep])
    print(f"{{ep}} — {{tr['titulo']}}")
    print(f"  Drive: {{carpeta.relative_to(DRIVE)}} ({{hechos}} de {{len(PLANES[ep])}} clips ya hechos)")
    print(fabrica.resumen_plan(PLANES[ep], CFG))

VOCES = sorted({{p["voz"] for plan in PLANES.values() for p in plan}})
for v in VOCES:
    datos = CFG["voces"][v]
    if not (RAIZ_VOCES / datos["ref"]).is_file():
        problemas.append(f"voz {{v}}: falta la referencia {{datos['ref']}}")
    if datos.get("adaptador") and not (RAIZ_VOCES / datos["adaptador"] / "adapter_model.safetensors").is_file():
        problemas.append(f"voz {{v}}: falta el adaptador {{datos['adaptador']}}")
if problemas:
    print("RESULTADO: REVISAR")
    for p in problemas:
        print("  -", p)
    raise SystemExit("Corrige lo de arriba antes de cargar modelos: todavía no se ha gastado nada.")
print("RESULTADO: OK")
"""),
    code("""
# 4. Cargar Qwen con los adaptadores de las voces que hacen falta, y Whisper para revisar
MOTOR = fabrica.MotorQwen(CFG, VOCES, RAIZ_VOCES)
ASR = None
if VERIFICAR:
    import medir
    ASR = medir.Asr()
    print("Whisper large-v3 cargado")
"""),
    code("""
# 5. Generar los episodios
for ep, plan in PLANES.items():
    base = Path("/content/repo/episodios") / ep
    titulo_en = json.loads((base / "metadata.en.json").read_text(encoding="utf-8"))["titulo"]
    carpeta = fabrica.carpeta_episodio(RAIZ_EPISODIOS, ep, titulo_en)
    print(f"=== {ep} → {carpeta.relative_to(DRIVE)}")
    fabrica.generar_episodio(plan, MOTOR.sintetizar, ASR, carpeta, CFG)
    print(f"Informe: {(carpeta / 'informe_tts.md').relative_to(DRIVE)}")
"""),
    code("""
# 6. Subir a Drive y desconectar
comun.desconectar()
"""),
]


def main():
    nb = {"nbformat": 4, "nbformat_minor": 0,
          "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "L4"},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}},
          "cells": CELDAS}
    destino = RAIZ / "fabrica.ipynb"
    destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("escrito", destino)


if __name__ == "__main__":
    main()
