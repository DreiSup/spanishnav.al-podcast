#!/usr/bin/env python3
"""Título y descripción de YouTube de un episodio, idénticos a los del feed de la web.

    python3 scripts/descripcion.py 2019/003-free-markets            # los imprime
    python3 scripts/descripcion.py 2019/003-free-markets --guardar  # además, a metadata.es.json → youtube

La plantilla es la de episodeDescription() en lib/feed.ts de la web (docs/sop-publicacion.md, apartado 3). Si cambia
allí, hay que cambiarla aquí: --comprobar compara con el feed publicado los episodios que ya están en él.
"""
import json, sys, urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parent.parent
WEB, EMAIL = "https://spanishnav.al", "podcast@spanishnav.al"


def descripcion(numero, titulo, subtitulo, slug, youtube_original):
    lineas = [f"Episodio {numero} de la traducción al español del podcast de Naval Ravikant.",
              f"{titulo}: {subtitulo}.", ""]
    if youtube_original:
        lineas.append(f"▶ Episodio original en YouTube: {youtube_original}")
    lineas += [
        f"▶ Transcripción original en inglés: https://nav.al/{slug}",
        f"▶ Este episodio en español, con su transcripción: {WEB}/{slug}",
        "▶ Canal original de Naval: https://www.youtube.com/@NavalR",
        "",
        "Traducción no oficial. Contenido original de Naval Ravikant, publicado en nav.al.",
        "",
        "Este podcast se ha traducido al español con inteligencia artificial. Puede haber errores o inconsistencias tanto en la traducción como en la dicción.",
        "La transcripción se ha traducido del inglés al español con Claude Opus 5.5 (esfuerzo alto), de Anthropic. La voz en español se ha generado con Qwen3-TTS, un modelo de voz de código abierto fine-tuned con las voces de Naval y de otros participantes.",
        "",
        f"¿Algún problema o queja? Escríbeme a {EMAIL}",
        "",
        "—",
        "",
        "Unofficial Spanish translation of Naval Ravikant's podcast. Original content by Naval Ravikant at nav.al.",
        "This podcast has been translated into Spanish using artificial intelligence. There may be errors or inconsistencies in both the translation and the diction.",
        "The transcript was translated from English to Spanish with Anthropic's Claude Opus 5.5 (high effort). The Spanish audio was generated with Qwen3-TTS, an open-source voice model fine-tuned on the voices of Naval and other participants.",
        f"If you run into any problems or have a complaint, reach me at {EMAIL}",
    ]
    return "\n".join(lineas)


def de_episodio(ep):
    carpeta = RAIZ / "episodios" / ep
    t = json.loads((carpeta / "transcript.es.json").read_text(encoding="utf-8"))
    m = json.loads((carpeta / "metadata.es.json").read_text(encoding="utf-8"))
    return t["titulo"], descripcion(t["numero"], t["titulo"], t["subtitulo"], m["slug"], m["youtube"].get("url_original", ""))


def comprobar():
    req = urllib.request.Request(f"{WEB}/podcast.xml", headers={"User-Agent": "spanishnav-check/1.0"})
    raiz = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
    ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
    fallos = 0
    for item in raiz.iter("item"):
        guid = item.find("guid").text                    # spanishnav.al/<año>/<slug>
        anio, slug = guid.split("/")[1:3]
        ep = next(p.parent.relative_to(RAIZ / "episodios").as_posix()
                  for p in (RAIZ / "episodios" / anio).glob("*/metadata.es.json")
                  if json.loads(p.read_text(encoding="utf-8"))["slug"] == slug)
        titulo, desc = de_episodio(ep)
        ok = titulo == item.find("title").text and desc == item.find("itunes:summary", ns).text
        fallos += not ok
        print(("OK   " if ok else "DISTINTO ") + ep)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    if sys.argv[1:] == ["--comprobar"]:
        comprobar()
    ep = sys.argv[1]
    titulo, desc = de_episodio(ep)
    print(titulo, "\n", desc, sep="\n")
    if "--guardar" in sys.argv:
        p = RAIZ / "episodios" / ep / "metadata.es.json"
        m = json.loads(p.read_text(encoding="utf-8"))
        m["youtube"]["titulo"], m["youtube"]["descripcion"] = titulo, desc
        p.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
