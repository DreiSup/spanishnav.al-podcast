#!/usr/bin/env python3
"""Convierte un par de transcripts (inglés + español) en los ficheros del repo.

    python3 scripts/normalizar-extraccion.py <en.json> <es.json>
    python3 scripts/normalizar-extraccion.py <en.json> <es.json> --slug finally-wealthy
    python3 scripts/normalizar-extraccion.py <en.json> <es.json> --simular

Entrada: los dos JSON tal y como salen del proceso manual, con esta forma:

    { "fecha": "…", "titulo": "…", "titulo_seccion": "…",
      "contenido": [ {"speaker": "Nivi", "frases": [...] o "…"} ],
      "titulos_seccion": [...] }

El episodio se identifica cruzando el **título inglés** con catalogo.json. Si el
título no aparece o es ambiguo, hay que pasar --slug.

Salida, en episodios/<año>/<NNN>-<slug>/:

    transcript.en.json  transcript.es.json  metadata.en.json  metadata.es.json

Lo que hace, y nada más:

  - añade schema, idioma, episodio, numero, fecha ISO y fuente_url desde el catálogo
  - pone un id por bloque de hablante: b01-nivi, b02-naval, …
  - renombra titulo_seccion (singular) a subtitulo
  - si `frases` es un string, lo trocea en frases; si ya es una lista, la respeta
  - si el episodio es uno de los 34 producidos a mano en 2019, lo marca como heredado

Y marca `tiene_transcript: true` en catalogo.json para ese episodio: si el transcript
está en el repo, es que existe. Con --simular no toca el catálogo.

El texto no se toca nunca.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "catalogo.json"
PLANTILLAS = RAIZ / "plantillas" / "episodio"

# Entradas del archivo de nav.al que no son episodios del feed (ver docs/extraccion.md)
EXTRAS = set(range(1, 5)) | set(range(164, 167))

# Episodios ya producidos con el método manual de 2019 (auditado en disco el 2026-09-06).
# Su audio existe y NO se re-sintetiza. Ver "Episodios heredados" en CLAUDE.md.
HEREDADOS = set(range(1, 35))          # 1-34 tienen audio montado
HEREDADOS_SIN_VIDEO = {34}             # el 34 es el único sin vídeo
AUDITADO_EL = "2026-09-06"


def numero_de_episodio(orden: int) -> int | None:
    """orden en el archivo de nav.al -> número de episodio del feed, o None si es extra."""
    if orden in EXTRAS:
        return None
    if orden <= 163:
        return orden - 4
    return orden - 7


def slugificar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")


def slug_de_url(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def trocear(texto: str) -> list[str]:
    """Trocea un bloque en frases. Determinista: los mismos datos dan lo mismo."""
    texto = re.sub(r"\s+", " ", texto).strip()
    partes = re.split(r'(?<=[.!?])["”]?\s+(?=[“"A-Z])', texto)
    return [p.strip() for p in partes if p.strip()]


def frases_de(bloque: dict) -> list[str]:
    valor = bloque.get("frases", bloque.get("texto", ""))
    if isinstance(valor, str):
        return trocear(valor)
    return [f if isinstance(f, str) else f.get("texto", "") for f in valor]


def localizar(entrada_en: dict, slug_forzado: str | None) -> dict:
    catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))["episodios"]
    if slug_forzado:
        coincidencias = [e for e in catalogo if slug_de_url(e["url"]) == slug_forzado]
        criterio = f"slug '{slug_forzado}'"
    else:
        titulo = (entrada_en.get("titulo") or "").strip()
        coincidencias = [e for e in catalogo if e["titulo"].strip() == titulo]
        criterio = f"título {titulo!r}"
    if not coincidencias:
        raise SystemExit(f"error: {criterio} no aparece en catalogo.json. Usa --slug.")
    if len(coincidencias) > 1:
        raise SystemExit(f"error: {criterio} aparece {len(coincidencias)} veces. Usa --slug.")
    return coincidencias[0]


def construir_transcript(origen: dict, idioma: str, ficha: dict) -> tuple[dict, list[str]]:
    avisos: list[str] = []
    contenido = []
    for i, bloque in enumerate(origen.get("contenido", []), 1):
        speaker = (bloque.get("speaker") or "").strip()
        if not speaker:
            avisos.append(f"{idioma}: bloque {i} sin speaker")
        frases = [f.strip() for f in frases_de(bloque) if f.strip()]
        if not frases:
            avisos.append(f"{idioma}: bloque {i} sin frases")
        contenido.append({
            "id": f"b{i:02d}-{slugificar(speaker) or 'sin-hablante'}",
            "speaker": speaker,
            "frases": frases,
        })

    transcript = {
        "schema": 1,
        "idioma": idioma,
        "episodio": ficha["episodio"],
        "numero": ficha["numero"],
        "fecha": ficha["fecha"],
        "titulo": (origen.get("titulo") or "").strip(),
        "subtitulo": (origen.get("titulo_seccion") or origen.get("subtitulo") or "").strip(),
        "fuente_url": ficha["url"],
        "titulos_seccion": origen.get("titulos_seccion", []),
        "contenido": contenido,
    }
    return transcript, avisos


def bloque_heredado(numero: int | None) -> dict | None:
    """Ficha del material producido a mano en 2019, si este episodio es uno de ellos."""
    if numero is None or numero not in HEREDADOS:
        return None
    return {
        "audio_existente": True,
        "origen": "produccion-manual-2019",
        "ruta_local": f"spanishpodcast/2019/{numero:02d}",
        "corresponde_al_transcript": False,
        "tiene_master": False,
        "video_resolucion": "" if numero in HEREDADOS_SIN_VIDEO else "1376x768",
        "auditado_el": AUDITADO_EL,
    }


def marcar_en_catalogo(slug: str, simular: bool) -> str:
    """Pone tiene_transcript: true en la entrada del episodio. Devuelve qué hizo."""
    catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))
    entradas = [e for e in catalogo["episodios"] if slug_de_url(e["url"]) == slug]
    if not entradas:
        return f"no se pudo marcar: '{slug}' no está en el catálogo"
    entrada = entradas[0]
    if entrada.get("tiene_transcript") is True:
        return "tiene_transcript ya estaba en true"
    anterior = entrada.get("tiene_transcript")
    if simular:
        return f"[simulado] tiene_transcript: {json.dumps(anterior)} -> true"
    entrada["tiene_transcript"] = True
    # Una entrada por línea, para que los diffs sigan siendo revisables
    lineas = ["{", f'  "fuente": {json.dumps(catalogo["fuente"])},',
              f'  "extraido_el": {json.dumps(catalogo["extraido_el"])},',
              f'  "total": {catalogo["total"]},', '  "episodios": [']
    eps = catalogo["episodios"]
    for i, e in enumerate(eps):
        lineas.append("    " + json.dumps(e, ensure_ascii=False) + ("," if i < len(eps) - 1 else ""))
    lineas += ["  ]", "}"]
    CATALOGO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    json.loads(CATALOGO.read_text(encoding="utf-8"))  # no dejar el catálogo roto
    return f"tiene_transcript: {json.dumps(anterior)} -> true"


def escribir(ruta: Path, datos: dict, simular: bool) -> None:
    if simular:
        print(f"    [simulado] escribiría {ruta.relative_to(RAIZ)}")
        return
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"    escrito {ruta.relative_to(RAIZ)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("en", help="JSON del transcript en inglés")
    ap.add_argument("es", help="JSON del transcript en español")
    ap.add_argument("--slug", help="fuerza el episodio en vez de buscarlo por título")
    ap.add_argument("--fecha", help="fecha AAAA-MM-DD, para los 59 episodios que el catálogo no trae fechados")
    ap.add_argument("--simular", action="store_true", help="no escribe nada")
    ap.add_argument("--forzar", action="store_true", help="sobrescribe una carpeta existente")
    ap.add_argument("--sin-heredado", action="store_true",
                    help="no marcar como heredado aunque el número esté entre los 34 producidos")
    args = ap.parse_args()

    origen_en = json.loads(Path(args.en).read_text(encoding="utf-8"))
    origen_es = json.loads(Path(args.es).read_text(encoding="utf-8"))

    entrada = localizar(origen_en, args.slug)
    orden = entrada["orden"]
    numero = numero_de_episodio(orden)
    slug = slug_de_url(entrada["url"])
    fecha = args.fecha or entrada["fecha"]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha or ""):
        raise SystemExit(
            f"error: no hay fecha ISO para '{slug}' (el catálogo trae {entrada['fecha']!r}).\n"
            f"       Búscala en {entrada['url']} y pásala con --fecha AAAA-MM-DD.")
    anio = fecha[:4]
    nombre = f"{numero:03d}-{slug}" if numero is not None else f"extra-{slug}"
    destino = RAIZ / "episodios" / anio / nombre
    ficha = {"episodio": f"{anio}/{nombre}", "numero": numero, "fecha": fecha, "url": entrada["url"]}

    print(f"episodio: {entrada['titulo']}")
    print(f"  orden en el archivo: {orden}  ->  número de episodio: {numero if numero is not None else 'extra'}")
    print(f"  carpeta: episodios/{anio}/{nombre}")
    if destino.exists() and not args.forzar and not args.simular:
        raise SystemExit(f"error: ya existe {destino.relative_to(RAIZ)}. Usa --forzar.")

    tr_en, avisos_en = construir_transcript(origen_en, "en", ficha)
    tr_es, avisos_es = construir_transcript(origen_es, "es", ficha)
    avisos = avisos_en + avisos_es

    # --- comprobaciones de emparejamiento ---
    bloques_en, bloques_es = tr_en["contenido"], tr_es["contenido"]
    if len(bloques_en) != len(bloques_es):
        avisos.append(f"los bloques no casan: {len(bloques_en)} en inglés y {len(bloques_es)} en español")
    else:
        for a, b in zip(bloques_en, bloques_es):
            if a["speaker"] != b["speaker"]:
                avisos.append(f"bloque {a['id']}: hablante '{a['speaker']}' en inglés y '{b['speaker']}' en español")
    if len(tr_en["titulos_seccion"]) != len(tr_es["titulos_seccion"]):
        avisos.append("distinto número de titulos_seccion entre idiomas")

    pal_en = sum(len(f.split()) for b in bloques_en for f in b["frases"])
    pal_es = sum(len(f.split()) for b in bloques_es for f in b["frases"])
    print(f"  bloques: {len(bloques_en)} en / {len(bloques_es)} es")
    print(f"  frases:  {sum(len(b['frases']) for b in bloques_en)} en / {sum(len(b['frases']) for b in bloques_es)} es")
    print(f"  palabras: {pal_en} en / {pal_es} es  (ratio {pal_es / pal_en:.2f})")
    print(f"  ids: {', '.join(b['id'] for b in bloques_en)}")

    if avisos:
        print("  AVISOS:")
        for a in avisos:
            print(f"    ⚠ {a}")

    # --- metadata ---
    meta_en = {
        "schema": 1,
        "_comentario": "Datos del episodio según la fuente. Sale del catálogo; no editar a mano.",
        "numero": numero,
        "anio": int(anio),
        "slug": slug,
        "titulo": tr_en["titulo"],
        "subtitulo": tr_en["subtitulo"],
        "fecha_publicacion": fecha,
        "fuente_url": entrada["url"],
        "orden_archivo": orden,
        "en_feed": numero is not None,
        "participantes": sorted({b["speaker"] for b in bloques_en if b["speaker"]}),
        "tiene_transcript": True,
        "normalizado_el": date.today().isoformat(),
    }
    meta_es = json.loads((PLANTILLAS / "metadata.es.json").read_text(encoding="utf-8"))
    meta_es.update(numero=numero, anio=int(anio), slug=slug, titulo_es=tr_es["titulo"], estado="revision")
    meta_es["youtube"]["titulo"] = tr_es["titulo"]

    heredado = None if args.sin_heredado else bloque_heredado(numero)
    if heredado:
        meta_es["heredado"] = heredado
        meta_es["audio_editado_a_mano"] = True
        meta_es["estado"] = "heredado"
        print(f"  HEREDADO: audio de {heredado['origen']} en {heredado['ruta_local']}")
        print("            no se re-sintetiza; el transcript es referencia textual, no su fuente")

    escribir(destino / "transcript.en.json", tr_en, args.simular)
    escribir(destino / "transcript.es.json", tr_es, args.simular)
    escribir(destino / "metadata.en.json", meta_en, args.simular)
    escribir(destino / "metadata.es.json", meta_es, args.simular)
    print(f"    catalogo.json: {marcar_en_catalogo(slug, args.simular)}")

    if not args.simular:
        print("\nsiguiente paso: python3 scripts/indice.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
