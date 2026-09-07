#!/usr/bin/env python3
"""Regenera INDICE.md recorriendo los metadata.es.json de cada episodio.

    python3 scripts/indice.py            # reescribe INDICE.md
    python3 scripts/indice.py --check    # solo comprueba que está al día
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EPISODIOS = RAIZ / "episodios"
INDICE = RAIZ / "INDICE.md"

ESTADOS = {
    "pendiente": "⚪ pendiente",
    "traduciendo": "🟡 traduciendo",
    "revision": "🟠 en revisión",
    "tts": "🔵 generando TTS",
    "montaje": "🟣 montaje",
    "publicado": "🟢 publicado",
}


def cargar_episodios() -> list[dict]:
    episodios = []
    for meta_path in sorted(EPISODIOS.glob("*/*/metadata.es.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"aviso: {meta_path.relative_to(RAIZ)} no es JSON válido ({e})", file=sys.stderr)
            continue
        carpeta = meta_path.parent
        meta["_carpeta"] = carpeta.relative_to(RAIZ).as_posix()
        meta["_nombre"] = carpeta.name
        meta["_anio"] = str(meta.get("anio") or carpeta.parent.name)
        meta["_tiene_es"] = (carpeta / "transcript.es.json").exists()
        episodios.append(meta)
    return episodios


def escapar(texto) -> str:
    return str(texto or "").replace("|", "\\|").strip()


def construir(episodios: list[dict]) -> str:
    publicados = sum(1 for e in episodios if e.get("estado") == "publicado")
    pendientes = sum(1 for e in episodios if e.get("estado") == "pendiente")
    lineas = [
        "# Índice de episodios",
        "",
        "<!-- Generado por scripts/indice.py. No editar a mano. -->",
        "",
        f"**{len(episodios)}** episodios · **{publicados}** publicados · "
        f"**{pendientes}** sin empezar",
        "",
    ]

    por_anio: dict[str, list[dict]] = {}
    for ep in episodios:
        por_anio.setdefault(ep["_anio"], []).append(ep)

    for anio in sorted(por_anio, reverse=True):
        lineas += [
            f"## {anio}",
            "",
            "| # | Episodio | Título en español | Estado | Drive | YouTube |",
            "|---|---|---|---|---|---|",
        ]
        for ep in sorted(por_anio[anio], key=lambda e: e["_nombre"]):
            numero = ep.get("numero") or "—"
            enlace = f"[{escapar(ep['_nombre'])}]({ep['_carpeta']})"
            titulo_es = escapar(ep.get("titulo_es")) or "—"
            estado = ESTADOS.get(ep.get("estado", ""), escapar(ep.get("estado")) or "—")
            carpeta_id = (ep.get("drive") or {}).get("carpeta_id")
            drive = f"[📁](https://drive.google.com/drive/folders/{carpeta_id})" if carpeta_id else "—"
            url = (ep.get("youtube") or {}).get("url")
            yt = f"[▶]({url})" if url else "—"
            lineas.append(f"| {numero} | {enlace} | {titulo_es} | {estado} | {drive} | {yt} |")
        lineas.append("")

    if not episodios:
        lineas += [
            "_Todavía no hay episodios descargados. El descargador de nav.al se ejecuta en "
            "local; ver [CLAUDE.md](CLAUDE.md)._",
            "",
        ]

    return "\n".join(lineas)


def main() -> int:
    contenido = construir(cargar_episodios())
    if "--check" in sys.argv:
        actual = INDICE.read_text(encoding="utf-8") if INDICE.exists() else ""
        if actual != contenido:
            print("INDICE.md está desactualizado: ejecuta `python3 scripts/indice.py`", file=sys.stderr)
            return 1
        print("INDICE.md al día")
        return 0
    INDICE.write_text(contenido, encoding="utf-8")
    print(f"escrito {INDICE.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
