#!/usr/bin/env python3
"""Descarga los episodios de nav.al y los deja como JSON crudo en trabajo/extraccion/.

SE EJECUTA EN LOCAL. nav.al está bloqueado desde las sesiones web de Claude Code.

    python3 scripts/descargar-episodios.py                    # todo el catálogo
    python3 scripts/descargar-episodios.py --solo finally-wealthy
    python3 scripts/descargar-episodios.py --anio 2019
    python3 scripts/descargar-episodios.py --sin-red          # reprocesa lo ya descargado
    python3 scripts/descargar-episodios.py --modo paginas     # si la API no responde

Fuente principal: la API REST de WordPress de nav.al. Devuelve fecha, título y el HTML
del contenido de todos los posts en dos o tres peticiones, sin rascar página a página.
Si la API no está disponible, --modo paginas descarga cada URL del catálogo y parsea
el <article>.

Salida por episodio, en el formato del protocolo (docs/extraccion.md):

    trabajo/extraccion/<slug>.json
      { url, titulo, fecha, fecha_gmt, idioma, bloques[], completo, notas, fuente }

trabajo/ está en .gitignore: es el directorio de trabajo, no el repo. Lo que se
versiona sale después de scripts/normalizar-extraccion.py.

Solo usa la biblioteca estándar. No hay que instalar nada.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

RAIZ = Path(__file__).resolve().parent.parent
TRABAJO = RAIZ / "trabajo"
DIR_API = TRABAJO / "wp-json"
DIR_HTML = TRABAJO / "html"
DIR_SALIDA = TRABAJO / "extraccion"

API = "https://nav.al/wp-json/wp/v2/posts"
CAMPOS_API = "id,date,date_gmt,link,slug,title,content"
USER_AGENT = "spanishnav-al-podcast/1.0 (+https://github.com/DreiSup/spanishnav.al-podcast)"
PAUSA = 1.0  # segundos entre peticiones

# "Naval:", "Nivi:", "Matt Ridley:", "David Deutsch:" … hasta 40 caracteres, sin saltos
RE_HABLANTE = re.compile(r"^\s*([A-Z][^:\n]{0,40}?)\s*:\s*$")


# ----------------------------------------------------------------------------
# Red
# ----------------------------------------------------------------------------

def descargar(url: str) -> tuple[bytes, dict]:
    peticion = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json, text/html"})
    with urlopen(peticion, timeout=30) as respuesta:
        return respuesta.read(), dict(respuesta.headers)


def descargar_api() -> list[dict]:
    """Baja todas las páginas de la API y las guarda en trabajo/wp-json/."""
    DIR_API.mkdir(parents=True, exist_ok=True)
    posts: list[dict] = []
    pagina = 1
    while True:
        url = f"{API}?per_page=100&page={pagina}&_fields={CAMPOS_API}"
        print(f"  API página {pagina} … ", end="", flush=True)
        try:
            cuerpo, cabeceras = descargar(url)
        except HTTPError as e:
            if e.code == 400 and pagina > 1:  # WP responde 400 al pasarse de páginas
                print("fin")
                break
            raise
        (DIR_API / f"posts-p{pagina}.json").write_bytes(cuerpo)
        lote = json.loads(cuerpo)
        posts.extend(lote)
        total_paginas = int(cabeceras.get("X-WP-TotalPages", cabeceras.get("x-wp-totalpages", "1")))
        print(f"{len(lote)} posts (de {total_paginas} páginas)")
        if pagina >= total_paginas or not lote:
            break
        pagina += 1
        time.sleep(PAUSA)
    return posts


def cargar_api_local() -> list[dict]:
    posts: list[dict] = []
    for fichero in sorted(DIR_API.glob("posts-p*.json")):
        posts.extend(json.loads(fichero.read_text(encoding="utf-8")))
    return posts


# ----------------------------------------------------------------------------
# Parseo del HTML del contenido
# ----------------------------------------------------------------------------

class ParserArticulo(HTMLParser):
    """Convierte el HTML del artículo en una lista de párrafos clasificados.

    Regla (confirmada contra la página real por reconocimiento):
      - <p> que empieza por <strong>Nombre:</strong>  → abre un turno de ese hablante
      - <p> cuyo contenido entero es un <strong>       → encabezado de sección
      - <h2>/<h3>/<h4>                                 → encabezado de sección
      - <p> sin etiqueta                               → continúa el turno abierto
    """

    IGNORAR = {"script", "style", "noscript", "figure", "figcaption", "iframe", "svg"}
    ENCABEZADOS = {"h2", "h3", "h4"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parrafos: list[tuple[str, str, str]] = []  # (tipo, hablante, texto)
        self._en_p = 0
        self._en_strong = 0
        self._en_encabezado: str | None = None
        self._ignorando = 0
        self._segmentos: list[tuple[bool, str]] = []  # (es_strong, texto)

    # -- eventos --------------------------------------------------------------
    def handle_starttag(self, etiqueta: str, atributos) -> None:
        if etiqueta in self.IGNORAR:
            self._ignorando += 1
        elif self._ignorando:
            return
        elif etiqueta == "p":
            self._en_p += 1
            self._segmentos = []
        elif etiqueta in ("strong", "b"):
            self._en_strong += 1
        elif etiqueta in self.ENCABEZADOS:
            self._en_encabezado = etiqueta
            self._segmentos = []
        elif etiqueta == "br":
            self._segmentos.append((self._en_strong > 0, " "))

    def handle_endtag(self, etiqueta: str) -> None:
        if etiqueta in self.IGNORAR:
            self._ignorando = max(0, self._ignorando - 1)
        elif self._ignorando:
            return
        elif etiqueta == "p" and self._en_p:
            self._en_p -= 1
            self._cerrar_parrafo()
        elif etiqueta in ("strong", "b"):
            self._en_strong = max(0, self._en_strong - 1)
        elif etiqueta in self.ENCABEZADOS and self._en_encabezado == etiqueta:
            texto = limpiar(" ".join(t for _, t in self._segmentos))
            if texto:
                self.parrafos.append(("seccion", "", texto))
            self._en_encabezado = None
            self._segmentos = []

    def handle_data(self, datos: str) -> None:
        if self._ignorando:
            return
        if self._en_p or self._en_encabezado:
            self._segmentos.append((self._en_strong > 0, datos))

    # -- clasificación --------------------------------------------------------
    def _cerrar_parrafo(self) -> None:
        # Fusiona segmentos consecutivos del mismo tipo
        fusionados: list[tuple[bool, str]] = []
        for es_strong, texto in self._segmentos:
            if fusionados and fusionados[-1][0] == es_strong:
                fusionados[-1] = (es_strong, fusionados[-1][1] + texto)
            else:
                fusionados.append((es_strong, texto))
        self._segmentos = []

        texto_total = limpiar("".join(t for _, t in fusionados))
        if not texto_total:
            return

        strong = [t for es, t in fusionados if es]
        normal = [t for es, t in fusionados if not es]
        texto_normal = limpiar("".join(normal))

        # ¿Todo el párrafo es negrita? → sección
        if strong and not texto_normal:
            self.parrafos.append(("seccion", "", texto_total))
            return

        # ¿Empieza por "<strong>Nombre:</strong> …"? → turno
        if fusionados and fusionados[0][0]:
            etiqueta = fusionados[0][1]
            cuerpo = "".join(t for _, t in fusionados[1:])
            m = RE_HABLANTE.match(etiqueta)
            if not m and not etiqueta.strip().endswith(":") and cuerpo.lstrip().startswith(":"):
                # "<strong>Naval</strong>: texto" — el dos puntos fuera de la negrita
                m = RE_HABLANTE.match(etiqueta.strip() + ":")
                cuerpo = cuerpo.lstrip()[1:]
            if m:
                self.parrafos.append(("turno", m.group(1).strip(), limpiar(cuerpo)))
                return

        self.parrafos.append(("continuacion", "", texto_total))


def limpiar(texto: str) -> str:
    texto = html.unescape(texto).replace("\xa0", " ")
    return re.sub(r"[ \t\r\f\v]+", " ", texto).strip()


def construir_bloques(parrafos: list[tuple[str, str, str]]) -> tuple[list[dict], list[str]]:
    """Agrupa los párrafos en bloques del protocolo. Devuelve (bloques, avisos)."""
    bloques: list[dict] = []
    avisos: list[str] = []
    abierto: dict | None = None
    ultimo_hablante = ""

    for tipo, hablante, texto in parrafos:
        if tipo == "seccion":
            abierto = None
            bloques.append({"tipo": "seccion", "texto": texto})
        elif tipo == "turno":
            abierto = {"tipo": "intervencion", "speaker": hablante, "texto": texto}
            bloques.append(abierto)
            ultimo_hablante = hablante
        else:  # continuación
            if abierto is None:
                abierto = {"tipo": "intervencion", "speaker": ultimo_hablante, "texto": texto}
                if ultimo_hablante:
                    abierto["speaker_inferido"] = True
                    avisos.append(f"bloque {len(bloques) + 1}: hablante inferido ({ultimo_hablante}) tras un encabezado")
                else:
                    avisos.append(f"bloque {len(bloques) + 1}: párrafo sin hablante antes del primer turno")
                bloques.append(abierto)
            else:
                abierto["texto"] += "\n\n" + texto
    return bloques, avisos


# ----------------------------------------------------------------------------
# Modo páginas (respaldo)
# ----------------------------------------------------------------------------

RE_ARTICLE = re.compile(r"<article\b.*?</article>", re.S | re.I)
RE_META = re.compile(r'<meta\s+(?:property|name)="([^"]+)"\s+content="([^"]*)"', re.I)
RE_H1 = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.S | re.I)


def extraer_de_pagina(html_pagina: str) -> tuple[str, str, str, str]:
    """Devuelve (html_articulo, titulo, fecha, fecha_gmt) de una página completa."""
    metas = {k.lower(): v for k, v in RE_META.findall(html_pagina)}
    titulo = html.unescape(metas.get("og:title", ""))
    if not titulo:
        m = RE_H1.search(html_pagina)
        titulo = limpiar(re.sub(r"<[^>]+>", "", m.group(1))) if m else ""
    fecha_gmt = metas.get("article:published_time", "")
    fecha = fecha_gmt[:10]
    m = RE_ARTICLE.search(html_pagina)
    return (m.group(0) if m else html_pagina), titulo, fecha, fecha_gmt


# ----------------------------------------------------------------------------
# Principal
# ----------------------------------------------------------------------------

def normalizar_url(url: str) -> str:
    u = urlparse(url.strip())
    return f"{u.netloc.lower()}{u.path.rstrip('/')}"


def slug_de(url: str) -> str:
    return urlparse(url).path.strip("/")


def procesar(slug: str, url: str, html_contenido: str, titulo: str, fecha: str, fecha_gmt: str,
             fuente: str, notas_extra: list[str]) -> dict:
    parser = ParserArticulo()
    parser.feed(html_contenido)
    bloques, avisos = construir_bloques(parser.parrafos)
    notas = notas_extra + avisos
    return {
        "url": url,
        "titulo": titulo,
        "fecha": fecha,
        "fecha_gmt": fecha_gmt,
        "idioma": "en",
        "bloques": bloques,
        "completo": bool(bloques),
        "notas": "; ".join(notas),
        "fuente": fuente,
        "descargado_el": date.today().isoformat(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalogo", default=str(RAIZ / "catalogo.json"))
    ap.add_argument("--solo", action="append", default=[], metavar="SLUG", help="solo este episodio (repetible)")
    ap.add_argument("--anio", type=int, help="solo los de este año")
    ap.add_argument("--sin-red", action="store_true", help="no descarga: reprocesa trabajo/")
    ap.add_argument("--modo", choices=["api", "paginas"], default="api")
    args = ap.parse_args()

    catalogo = json.loads(Path(args.catalogo).read_text(encoding="utf-8"))
    episodios = catalogo["episodios"]
    if args.solo:
        episodios = [e for e in episodios if slug_de(e["url"]) in set(args.solo)]
        if not episodios:
            print(f"error: ningún episodio del catálogo coincide con {args.solo}", file=sys.stderr)
            return 1
    print(f"catálogo: {len(catalogo['episodios'])} episodios; a procesar: {len(episodios)}")

    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    resultados: list[dict] = []
    no_encontrados: list[str] = []
    sin_bloques: list[str] = []

    if args.modo == "api":
        posts = cargar_api_local() if args.sin_red else descargar_api()
        if not posts:
            print("error: no hay posts. Sin --sin-red descarga; con él necesita trabajo/wp-json/", file=sys.stderr)
            return 1
        por_url = {normalizar_url(p["link"]): p for p in posts}
        print(f"posts en la API: {len(posts)}")
        for e in episodios:
            slug = slug_de(e["url"])
            post = por_url.get(normalizar_url(e["url"]))
            if post is None:
                no_encontrados.append(slug)
                continue
            titulo = limpiar(re.sub(r"<[^>]+>", "", post["title"]["rendered"]))
            fecha = post["date"][:10]
            r = procesar(slug, e["url"], post["content"]["rendered"], titulo, fecha, post.get("date_gmt", ""),
                         "wp-json", [])
            r["wp_id"] = post.get("id")
            resultados.append(r)
    else:
        DIR_HTML.mkdir(parents=True, exist_ok=True)
        for i, e in enumerate(episodios):
            slug = slug_de(e["url"])
            fichero = DIR_HTML / f"{slug}.html"
            if args.sin_red:
                if not fichero.exists():
                    no_encontrados.append(slug)
                    continue
                pagina = fichero.read_text(encoding="utf-8", errors="replace")
            else:
                print(f"  [{i + 1}/{len(episodios)}] {slug} … ", end="", flush=True)
                try:
                    cuerpo, _ = descargar(e["url"])
                except (HTTPError, URLError) as err:
                    print(f"FALLO ({err})")
                    no_encontrados.append(slug)
                    continue
                pagina = cuerpo.decode("utf-8", errors="replace")
                fichero.write_text(pagina, encoding="utf-8")
                print("ok")
                time.sleep(PAUSA)
            articulo, titulo, fecha, fecha_gmt = extraer_de_pagina(pagina)
            resultados.append(procesar(slug, e["url"], articulo, titulo or e["titulo"], fecha or e["fecha"],
                                       fecha_gmt, "pagina", []))

    # Filtro por año (se resuelve aquí porque la fecha puede venir de la descarga)
    if args.anio:
        resultados = [r for r in resultados if r["fecha"].startswith(str(args.anio))]

    # Escritura y resumen
    palabras_total = 0
    for r in resultados:
        slug = slug_de(r["url"])
        if not r["bloques"]:
            sin_bloques.append(slug)
        palabras = sum(len(b["texto"].split()) for b in r["bloques"] if b["tipo"] == "intervencion")
        palabras_total += palabras
        (DIR_SALIDA / f"{slug}.json").write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        hablantes = sorted({b["speaker"] for b in r["bloques"] if b["tipo"] == "intervencion"})
        aviso = "  ⚠ " + r["notas"] if r["notas"] else ""
        print(f"  {r['fecha'] or '????-??-??'}  {slug:<32} {len(r['bloques']):>3} bloques {palabras:>6} palabras  {','.join(hablantes)}{aviso}")

    print()
    print(f"escritos: {len(resultados)} episodios en {DIR_SALIDA.relative_to(RAIZ)}/  ({palabras_total} palabras)")
    if no_encontrados:
        print(f"NO ENCONTRADOS ({len(no_encontrados)}): {' '.join(no_encontrados)}")
    if sin_bloques:
        print(f"SIN BLOQUES ({len(sin_bloques)}): {' '.join(sin_bloques)}")
    print("siguiente paso: python3 scripts/normalizar-extraccion.py")
    return 0 if not no_encontrados else 2


if __name__ == "__main__":
    raise SystemExit(main())
