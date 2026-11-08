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
2. Genera con Qwen3-TTS en modo solo timbre, **varias frases de una intervención a la vez** (en lotes de
   `motor.lote` de `voces.json`, 8), que es mucho más barato que una a una. **Whisper revisa cada frase** y las
   que no dicen el texto o dejan una cola rara se repiten juntas con otra semilla (hasta 2 veces).
3. Recorta los silencios y une las frases con la pausa de cada voz, la que elegiste escuchando: 0,12 s
   Naval, 0,20 Nivi y Deutsch, 0,30 Brett.
4. Monta el **master**, `audio/<NNN>-<slug>.mp3`: todos los clips seguidos, a -16 LUFS, listo para publicar si al
   escucharlo suena bien. Junto a `tts/` deja un **`informe_tts.md`** con el minuto del master donde empieza cada
   clip y dónde están las frases sospechosas, y un `registro_tts.jsonl` con el detalle.

Si se corta, vuelve a ejecutarlo: los clips que ya están en Drive no se repiten. Para rehacer uno, bórralo
de `tts/` y vuelve a lanzar.

**GPU: T4** (la más barata; L4 también vale). Cada episodio anota su tiempo de GPU y sus unidades estimadas en su
`informe_tts.md` y en `naval-podcast/coste_fabrica.jsonl`; la celda 6 añade el coste de la sesión entera y rehace el
resumen de todo lo generado en `naval-podcast/coste_fabrica.md`. La celda 3 estima los minutos de audio de cada episodio; la 5 mide al final
cuántos segundos de GPU cuesta cada segundo de audio, para calcular el gasto de los demás episodios.
"""),
    code("""
# 1. Instalación (después: Entorno de ejecución → Reiniciar sesión)
# El aviso rojo "pip's dependency resolver..." es normal.
!pip install -q qwen-tts==0.1.1 peft==0.17.1 jiwer num2words
"""),
    code("""
# 2. Parámetros
EPISODIOS = []      # carpetas de episodios/ del repo, p. ej. ["2019/051-angel-1"] (vacío: no hace nada)
VERIFICAR = True     # revisar cada frase con Whisper y repetir las que fallen (más lento, mucho menos Audacity)

# Arreglos tras escuchar el master (docs/sop-episodio.md). Para producir normal: SOLO_MASTER = False y RONDA = 0
SOLO_MASTER = False  # True = no genera nada ni usa GPU: rehace el master con los clips de tts/ (p. ej. uno arreglado en Audacity)
RONDA = 0            # 1, 2…: otras semillas para los clips que borres de tts/ (el mismo número da siempre el mismo audio)
REHACER_FRASES = {}  # p. ej. {"2019/037-productize-yourself": {"002naval.wav": [7]}}: solo esas frases (números del informe)
MUESTRA = 0          # 3 = solo las 3 primeras intervenciones de cada voz, en <episodio>/muestra/ (probar voces nuevas)

# Pruebas de voz. Para producir normal: REF_ES_NAVAL = 0 y SUBCARPETA = ""
REF_ES_NAVAL = 0     # 0 = la referencia de voces.json; 1 = el mejor clip de Naval en español (lora_ref_es1 del 08); 5 = media de 5
SUBCARPETA = ""      # p. ej. "prueba_ref_es1": la prueba va a <episodio>/<subcarpeta>/ y no toca los clips de verdad
"""),
    code(f"""
# 3. Preparar: código del repo, Drive, voces y plan de cada episodio (sin cargar modelos)
import os, sys, subprocess, json
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")   # menos memoria perdida en huecos
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/fabrica", "/content/repo/piloto", "/content/repo/criba"]
import comun, fabrica, time
T_INICIO = time.time()   # para el coste de la sesión (celda 6)

comun.montar_drive()
CFG = fabrica.cargar_config()
CFG["verificacion"]["activa"] = VERIFICAR
CFG["motor"]["ronda"] = RONDA
CFG["motor"]["agrupar"] = globals().get("AGRUPAR", CFG["motor"].get("agrupar", "intervencion"))
if CFG["motor"]["agrupar"] == "voz":
    print(f"LOTES POR VOZ: hasta {{CFG['motor']['tanda_voz']}} frases de una voz a la vez, en lotes de {{CFG['motor']['lote_voz']}}")
DRIVE = Path(CFG["rutas"]["drive"])
RAIZ_VOCES = DRIVE / CFG["rutas"]["voces"]
RAIZ_EPISODIOS = DRIVE / CFG["rutas"]["episodios"]
LIBRO_COSTE = RAIZ_EPISODIOS.parent / "coste_fabrica.jsonl"   # naval-podcast/coste_fabrica.jsonl
# Si una celda falla (también con «Ejecutar todo»), en 10 min anota el coste y desconecta, salvo que pulses Detener
comun.desconectar_si_falla(antes=lambda: print(fabrica.anotar_sesion(
    LIBRO_COSTE, CFG, T_INICIO, globals().get("PLANES", {{}}), t_carga=globals().get("T_CARGA"), error=True)))
if REF_ES_NAVAL:
    CFG["voces"]["naval"]["ref"] = fabrica.refs_espanol(RAIZ_VOCES, n=REF_ES_NAVAL)
    print(f"PRUEBA: Naval con la huella de {{REF_ES_NAVAL}} clip(s) en español: {{CFG['voces']['naval']['ref']}}")
if SUBCARPETA:
    print(f"PRUEBA: todo va a la subcarpeta {{SUBCARPETA}}/ de cada episodio")

def carpeta_de(ep, titulo_en, crear=True):
    c = fabrica.carpeta_episodio(RAIZ_EPISODIOS, ep, titulo_en, crear=crear)
    sub = SUBCARPETA or ("muestra" if MUESTRA else "")
    return c / sub if sub else c
if MUESTRA:
    print(f"MUESTRA: solo {{MUESTRA}} intervenciones de cada voz, en la subcarpeta muestra/ de cada episodio")
for ep, pedidas in REHACER_FRASES.items():
    print(f"REHACER: {{ep}} → {{pedidas}}")

PLANES, problemas = {{}}, []
if not EPISODIOS:
    problemas.append("EPISODIOS está vacío: pega en la celda 2 los episodios que quieres generar")
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
    if MUESTRA:   # las MUESTRA primeras intervenciones de cada voz, en su orden
        vistas, muestra = {{}}, []
        for p in PLANES[ep]:
            vistas[p["voz"]] = vistas.get(p["voz"], 0) + 1
            if vistas[p["voz"]] <= MUESTRA:
                muestra.append(p)
        PLANES[ep] = muestra
    titulo_en = json.loads((base / "metadata.en.json").read_text(encoding="utf-8"))["titulo"]
    carpeta = carpeta_de(ep, titulo_en, crear=False)
    hechos = sum((carpeta / "tts" / p["fichero"]).exists() for p in PLANES[ep])
    print(f"{{ep}} — {{tr['titulo']}}")
    print(f"  Drive: {{carpeta.relative_to(DRIVE)}} ({{hechos}} de {{len(PLANES[ep])}} clips ya hechos)")
    print(fabrica.resumen_plan(PLANES[ep], CFG))

VOCES = sorted({{p["voz"] for plan in PLANES.values() for p in plan}})
for v in VOCES:
    datos = CFG["voces"][v]
    for r in fabrica.refs_de(datos):
        if not (RAIZ_VOCES / r).is_file():
            problemas.append(f"voz {{v}}: falta la referencia {{r}}")
    if datos.get("adaptador") and not (RAIZ_VOCES / datos["adaptador"] / "adapter_model.safetensors").is_file():
        problemas.append(f"voz {{v}}: falta el adaptador {{datos['adaptador']}}")
if problemas:
    print("RESULTADO: REVISAR")
    for p in problemas:
        print("  -", p)
    raise RuntimeError("Corrige lo de arriba antes de cargar modelos (o pulsa Detener para no desconectar).")
print("RESULTADO: OK")
"""),
    code("""
# 4. Cargar Qwen con los adaptadores de las voces que hacen falta, y Whisper para revisar
t0 = time.time()
if SOLO_MASTER:
    print("SOLO_MASTER: no se carga ningún modelo")
else:
    from transformers.utils import logging as hf_logging
    hf_logging.set_verbosity_error()   # sin los avisos repetidos de pad_token_id y de "pipelines sequentially"
    MOTOR = fabrica.MotorQwen(CFG, VOCES, RAIZ_VOCES)
    ASR = None
    if VERIFICAR:
        import medir
        ASR = medir.Asr(CFG["verificacion"].get("modelo_asr", "openai/whisper-large-v3"),
                        CFG["verificacion"].get("marcas_asr", "palabra"))
        print(f"Whisper cargado: {ASR.modelo} (marcas por {ASR.marcas})")
T_CARGA = time.time() - t0
print(f"Carga: {T_CARGA / 60:.1f} min")
"""),
    code("""
# 5. Generar los episodios
for ep, plan in PLANES.items():
    base = Path("/content/repo/episodios") / ep
    titulo_en = json.loads((base / "metadata.en.json").read_text(encoding="utf-8"))["titulo"]
    carpeta = carpeta_de(ep, titulo_en)
    titulo_es = json.loads((base / "transcript.es.json").read_text(encoding="utf-8"))["titulo"]
    master = carpeta / "audio" / f"{ep.split('/')[1]}.mp3"
    print(f"=== {ep} → {carpeta.relative_to(DRIVE)}")
    if SOLO_MASTER:
        fabrica.rehacer_master(plan, carpeta, master, titulo=titulo_es, cfg=CFG)
    else:
        fabrica.generar_episodio(plan, MOTOR.sintetizar_lote, ASR, carpeta, CFG, master=master, titulo=titulo_es,
                                 rehacer=REHACER_FRASES.get(ep), libro_coste=LIBRO_COSTE, episodio=ep)
    print(f"Informe: {(carpeta / 'informe_tts.md').relative_to(DRIVE)}")
"""),
    code("""
# 6. Coste. Anota esta sesión (desde la celda 3: carga de modelos y ratos parados incluidos) en
#    naval-podcast/coste_fabrica.jsonl y rehace el resumen de todo lo generado, naval-podcast/coste_fabrica.md
print(fabrica.anotar_sesion(LIBRO_COSTE, CFG, T_INICIO, PLANES, t_carga=globals().get("T_CARGA")))
resumen = fabrica.resumen_coste(RAIZ_EPISODIOS, CFG, RAIZ_EPISODIOS.parent / "coste_fabrica.md")
print(resumen.split("| Episodio")[0].strip())
"""),
    code("""
# 7. Subir a Drive y desconectar
comun.desconectar()
"""),
]


CELDAS_WHISPER = [
    md("""
# ¿Un Whisper más rápido para la revisión?

La revisión de la fábrica no toca el audio: solo decide qué frases se repiten. Este cuaderno comprueba, con frases ya
generadas, que una configuración más rápida de Whisper decide igual que la de siempre (**large-v3 con marcas por
palabra**, cuya decisión está en el registro de cada episodio) y caza las averías que la revisión existe para cazar
(una cola de más al final, una frase cortada). Lógica en `fabrica/comparar_whisper.py`.

Prueba tres configuraciones, cada una en su propio proceso (la GPU queda limpia entre una y otra):
**turbo con marcas por segmento**, **large-v3 con marcas por segmento** y **turbo con marcas por palabra**.

**GPU: T4.** Unos 15–20 min (~0,6 unidades). No genera audio ni toca los episodios: deja el resultado en
`naval-podcast/pruebas/whisper_turbo.md` y desconecta. Ejecuta las celdas 1 a 6 seguidas («Ejecutar todo»).
"""),
    code("""
# 1. Instalación (no hace falta reiniciar)
!pip install -q jiwer num2words
"""),
    code("""
# 2. Parámetros: de qué episodios ya generados se toman las frases, y qué configuraciones se prueban
EPISODIOS = ["2019/018-skill-business", "2019/027-hourly-rate", "2019/034-reject-advice", "2019/041-envy",
             "2019/051-angel-1", "2020/068-kapil"]
N_FRASES = 200    # frases reales (todas las sospechosas entran siempre)
N_AVERIAS = 60    # averías fabricadas: la mitad con cola de más, la mitad cortadas
CONFIGURACIONES = [   # (nombre, modelo, marcas, frases a la vez)
    ("turbo · segmento", "openai/whisper-large-v3-turbo", "segmento", 16),
    ("large-v3 · segmento", "openai/whisper-large-v3", "segmento", 16),
    ("turbo · palabra", "openai/whisper-large-v3-turbo", "palabra", 2),
]
"""),
    code(f"""
# 3. Preparar: código, Drive y las frases con su audio (sin GPU)
import os, sys, subprocess, json, time, pickle
from pathlib import Path
RAMA = "{RAMA}"
if os.path.isdir("/content/repo"):
    subprocess.run(["git", "-C", "/content/repo", "pull", "-q"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", RAMA, "{REPO}", "/content/repo"], check=True)
sys.path[:0] = ["/content/repo/fabrica", "/content/repo/piloto", "/content/repo/criba"]
import comun, fabrica, medir, comparar_whisper as cw
comun.montar_drive()
comun.desconectar_si_falla()
CFG = fabrica.cargar_config()
RAIZ_EPISODIOS = Path(CFG["rutas"]["drive"]) / CFG["rutas"]["episodios"]
carpetas = []
for ep in EPISODIOS:
    base = Path("/content/repo/episodios") / ep
    titulo_en = json.loads((base / "metadata.en.json").read_text(encoding="utf-8"))["titulo"]
    c = fabrica.carpeta_episodio(RAIZ_EPISODIOS, ep, titulo_en, crear=False)
    if (c / "registro_tts.jsonl").exists():
        carpetas.append(c)
    else:
        print("sin registro, lo salto:", ep)
ITEMS = cw.frases_de(carpetas, N_FRASES)
for i in ITEMS:
    i["audio"] = cw.audio_16k(i["ruta"])
ITEMS = cw.con_averias(ITEMS, N_AVERIAS)
Path("/content/items_whisper.pkl").write_bytes(pickle.dumps(ITEMS))
reales = sum(i["tipo"] == "real" for i in ITEMS)
print(f"{{reales}} frases reales ({{sum(i['ok_registro'] is False for i in ITEMS if i['tipo'] == 'real')}} sospechosas) "
      f"y {{len(ITEMS) - reales}} averías; {{sum(len(i['audio']) for i in ITEMS) / 16000 / 60:.1f}} min de audio")
"""),
    code("""
# 4. Cada configuración las oye en su propio proceso. Si una falla (p. ej. sin memoria), se apunta y se sigue
RES = {}
for n, (nombre, modelo, marcas, lote) in enumerate(CONFIGURACIONES):
    salida = f"/content/whisper_{n}.json"
    print(f"→ {nombre}…", flush=True)
    r = subprocess.run([sys.executable, "/content/repo/fabrica/comparar_whisper.py", "oir", modelo, marcas,
                        "/content/items_whisper.pkl", salida, str(lote)], capture_output=True, text=True)
    lineas = [l for l in (r.stdout + r.stderr).splitlines() if l.strip() and "Warning" not in l]
    if r.returncode == 0 and Path(salida).exists():
        RES[nombre] = json.loads(Path(salida).read_text(encoding="utf-8"))
        print("  ", lineas[-1] if lineas else "hecho")
    else:
        print(f"   FALLÓ ({r.returncode}). Últimas líneas:")
        print("\\n".join("     " + l for l in lineas[-8:]))
"""),
    code("""
# 5. Comparar y dejar el resultado en naval-podcast/pruebas/whisper_turbo.md
texto, VEREDICTOS = cw.informe(ITEMS, RES, CFG["verificacion"])
destino = RAIZ_EPISODIOS.parent / "pruebas" / "whisper_turbo.md"
destino.parent.mkdir(parents=True, exist_ok=True)
destino.write_text(texto, encoding="utf-8")
print(texto.split("\\n## ")[0])
print("RESULTADO:", " · ".join(f"{k}: {'VALE' if v else 'no vale'}" for k, v in VEREDICTOS.items()), "→", destino)
"""),
    code("""
# 6. Subir a Drive y desconectar
comun.desconectar()
"""),
]


def main():
    nb = {"nbformat": 4, "nbformat_minor": 0,
          "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}},
          "cells": CELDAS}
    destino = RAIZ / "fabrica.ipynb"
    destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("escrito", destino)
    otro = dict(nb, cells=CELDAS_WHISPER)
    destino = RAIZ / "comparar_whisper.ipynb"
    destino.write_text(json.dumps(otro, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("escrito", destino)


if __name__ == "__main__":
    main()
