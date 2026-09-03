#!/usr/bin/env python3
"""Regenera INDICE.md recorriendo los metadata.json de cada episodio.

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
    for meta_path in sorted(EPISODIOS.glob("*/*/metadata.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"aviso: {meta_path.relative_to(RAIZ)} no es JSON válido ({e})", file=sys.stderr)
            continue
        meta["_carpeta"] = meta_path.parent.relative_to(RAIZ).as_posix()
        meta["_anio"] = meta.get("anio") or meta_path.parent.parent.name
        episodios.append(meta)
    return episodios


def escapar(texto: str) -> str:
    return str(texto or "").replace("|", "\\|").strip()


def construir(episodios: list[dict]) -> str:
    lineas = [
        "# Índice de episodios",
        "",
        "<!-- Generado por scripts/indice.py. No editar a mano. -->",
        "",
        f"Total: **{len(episodios)}** episodios · "
        f"**{sum(1 for e in episodios if e.get('estado') == 'publicado')}** publicados",
        "",
    ]

    por_anio: dict[str, list[dict]] = {}
    for ep in episodios:
        por_anio.setdefault(str(ep["_anio"]), []).append(ep)

    for anio in sorted(por_anio, reverse=True):
        lineas += [f"## {anio}", "", "| Episodio | Título en español | Estado | YouTube |", "|---|---|---|---|"]
        for ep in sorted(por_anio[anio], key=lambda e: e.get("slug", "")):
            titulo_es = escapar(ep.get("titulo_es")) or "—"
            enlace = f"[{escapar(ep.get('slug'))}]({ep['_carpeta']})"
            estado = ESTADOS.get(ep.get("estado", ""), escapar(ep.get("estado")) or "—")
            yt = f"[▶]({ep['youtube_url']})" if ep.get("youtube_url") else "—"
            lineas.append(f"| {enlace} | {titulo_es} | {estado} | {yt} |")
        lineas.append("")

    if not episodios:
        lineas += ["_Todavía no hay episodios. Crea el primero con `./scripts/nuevo-episodio.sh`._", ""]

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
