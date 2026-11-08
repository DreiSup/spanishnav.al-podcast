#!/usr/bin/env python3
"""Etapa 5: transcripts oficiales de nav.al por hablante (solo comprobación cruzada).

No usa torch ni GPU: parsea ~/naval-datos/oficiales/docs/<año>_all_podcasts.txt (Google Docs
exportados) y, para cada fuente de fuentes_podcast.json, extrae los turnos por hablante.

Formato del Doc (una pasada lineal, RAM O(tamaño del Doc), el mayor pesa ~0,5 MB):
  [Naval] [* Archive ...]  <fecha "May 13 2020">  <título>  [subtítulo]  <duración>  "Get podcast"
  cuerpo ...  "Related"  (enlaces relacionados, se ignoran)
- El ancla de cada episodio es la línea `Get podcast`; hacia atrás se busca la fecha (≤8 líneas)
  y el título es la línea siguiente a la fecha.
- Prefijos `Nombre:` (variantes de nombre completo, ver ALIAS; el espacio tras los dos puntos es
  opcional y un "." suelto tras ellos se descarta) abren un turno. Las líneas sin prefijo continúan
  al último hablante (se unen con "\\n"). Las líneas anteriores al primer prefijo (descripción del
  episodio) no se asignan a nadie y se ignoran.
- Títulos de sección (se ignoran), línea sin prefijo: <=15 palabras sin puntuación final; o <=12
  palabras acabadas en "?" o comilla de cierre con mayoría de palabras largas en mayúscula
  ("What Is Ethereum?"); o cita corta con la comilla de cierre pegada a una letra.
- Se descartan la nota "This transcript has been edited..." y las anotaciones entre corchetes
  ("[correction: ...]"). El cierre de nav109 ("Here we take the stance...", "So stay optimistic.")
  SÍ se pronuncia (comprobado en su asr.json) y se conserva.
- Si el cuerpo trae una línea `Transcript` (nav072: bloque `Highlights` con citas sueltas y luego
  `Transcript` con la conversación entera), se descarta todo lo anterior: los highlights son
  citas repetidas del propio transcript y duplicarían palabras. Con esto nav072 sale con ~7385
  palabras en 40:46 (183 palabras/min, igual que el resto): el Doc SÍ trae la conversación
  completa, a diferencia de lo que dice CONTRATO.md ("son highlights"). Ver `cobertura`.

Deduplicación entre entradas de una fuente (nav167): las entradas se procesan con la propia fuente
primero; un párrafo de >=3 palabras de otra entrada se omite si su texto normalizado (casefold, sin
acentos ni signos) ya está en las anteriores, o si >80 % de sus shingles de 8 palabras lo están
(párrafos partidos de otra forma). Las entradas 164-166 salen casi enteras dentro de la 167.

Qué entradas del Doc forman cada fuente (decisiones):
- Por defecto, la entrada cuyo título (normalizado) es el de la fuente en catalogo.json.
- nav167: recopilatorio. Entradas de los órdenes 164, 165, 166 y 167 del catálogo (títulos de
  catalogo.json); la propia entrada de la fuente (167) va primero y fija la duración esperada.
- nav056 (How to Get Rich): se usa la propia entrada "How to Get Rich" del Doc de 2019 (28 dic
  2019, 3:35:35). Es el recopilatorio ya editado y contiene el texto de los episodios 5-54 más
  el material extra: es la versión que corresponde al audio. NO se añaden las entradas sueltas
  de los episodios 5-54: son la versión sin editar del mismo contenido y duplicarían las palabras
  (el alineado local de la etapa 06 buscaría igualmente en ambas, pero esto evita el doble
  recuento y mantiene el fichero manejable). Si la entrada no aparece, falla con error claro.
- Si un título aparece en varias entradas (duplicados del Doc), se usa la primera y se avisa.

`cobertura`: "parcial" si el texto da menos del 70 % de las palabras esperadas por la duración del
audio (`fuentes/<id>/fuente.json`, o la cabecera del Doc si aún no se ha descargado; 150
palabras/min, la media real del podcast es ~180); si no, "completa". `--cobertura id=valor`
fuerza el valor (p. ej. `--cobertura nav072=parcial` si se prefiere el criterio del contrato).

Salida oficiales/<id>.json:
  {"id", "entradas": [títulos], "cobertura": "completa|parcial",
   "turnos": [{"speaker", "texto"}], "palabras_por_hablante": {speaker: n}}

Uso: 05_oficiales.py [id ...] [--forzar] [--salida DIR] [--docs DIR] [--cobertura id=valor]
     (sin id: las 7 fuentes)
"""
import argparse
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from common import FUENTES, OFICIALES, REPO_DATASET, cargar_fuentes, escribir_json, leer_json, log

CATALOGO = REPO_DATASET.parent.parent / "catalogo.json"

# Prefijo (minúsculas) -> hablante canónico
ALIAS = {
    "naval": "naval", "naval ravikant": "naval",
    "nivi": "nivi", "babak nivi": "nivi",
    "brett": "brett", "brett hall": "brett",
    "david": "deutsch", "david deutsch": "deutsch",
    "kapil": "kapil", "kapil gupta": "kapil",
    "matt": "ridley", "matt ridley": "ridley",
    "vitalik": "vitalik", "vitalik buterin": "vitalik",
    "haseeb": "qureshi", "haseeb qureshi": "qureshi",
    "max": "hodak", "max hodak": "hodak",
    "guillermo": "rauch", "guillermo rauch": "rauch",
    "blake": "scholl", "blake scholl": "scholl",
}

# Fuentes recopilatorio: órdenes del catálogo cuyas entradas se incluyen (además de la propia
# entrada si el título de la fuente no es el de ninguno de esos órdenes).
MIN_PALABRAS_DUP = 3  # párrafos de >=3 palabras ya presentes en otra entrada de la fuente se omiten
SHINGLE = 8  # tamaño (palabras) de los shingles para detectar párrafos partidos de otra forma
UMBRAL_SHINGLES = 0.80  # se omite el párrafo si más de este % de sus shingles ya estaban en la fuente
ORDENES_EXTRA = {"nav167": [164, 165, 166, 167]}

MESES = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
RE_FECHA = re.compile(rf"^({MESES}) \d{{1,2}} \d{{4}}$")
RE_DURACION = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")
RE_PREFIJO = re.compile(r"^([^:]{1,40}?):\s*(.*)$")
RE_PUNTO_SUELTO = re.compile(r"^\.(?!\.)\s*")  # "David:. Yes" -> "Yes" (sin tocar puntos suspensivos)
RE_CORCHETES = re.compile(r"\[[^\]]*\]")  # anotaciones "[correction: ...]"
RE_CITA_TITULO = re.compile(r"[‘“\"].*[A-Za-z0-9][’”\"]$")
RE_ESPACIO_PUNT = re.compile(r"\s+([.,;:!?])")
RE_NOTA_EDICION = re.compile(r"^This transcript has been edited", re.I)
RE_PREFIJO_NOMBRE = re.compile(r"^[A-Z][\w.'’-]*( [A-Z][\w.'’-]*){0,2}$")
PUNT_FINAL = tuple('.?!:;,)"”’…\'»')
CIERRE_TITULO = tuple('?"”’\'»')  # un título puede acabar en "?" o en comilla de cierre
PALABRAS_ESPERADAS_MIN = 150
UMBRAL_COBERTURA = 0.70


def norm_titulo(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).casefold()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def limpiar_linea(l: str) -> str:
    return l.replace("﻿", "").replace("\xa0", " ").replace("​", "").strip()


def duracion_a_s(d: str | None) -> int | None:
    if not d:
        return None
    p = [int(x) for x in d.split(":")]
    s = 0
    for x in p:
        s = s * 60 + x
    return s


def duracion_audio_s(fid: str) -> float | None:
    p = FUENTES / fid / "fuente.json"
    try:
        return float(leer_json(p)["duracion_s"])
    except (OSError, KeyError, TypeError, ValueError):
        return None


def es_titulo_seccion(linea: str) -> bool:
    """Título de sección: <=15 palabras sin puntuación final, o (<=12 palabras, >=3) acabado en "?" o
    comilla de cierre en el que >=60 % de las palabras de >=4 letras empiezan en mayúscula
    ("What Is Ethereum?"), o una cita corta sin puntuación antes de la comilla final. Un "?" final
    sin esas mayúsculas ("What do you think?") es habla."""
    pal = linea.split()
    if len(pal) <= 15 and not linea.endswith(PUNT_FINAL):
        return True
    if 3 <= len(pal) <= 12 and linea.endswith(CIERRE_TITULO):
        largas = [re.sub(r"^[^A-Za-z]+", "", w) for w in pal]
        largas = [w for w in largas if len(re.sub(r"[^A-Za-z]", "", w)) >= 4]
        if len(largas) >= 2 and sum(w[:1].isupper() for w in largas) / len(largas) >= 0.60:
            return True
    # cita-título: línea corta que es solo una cita, con la comilla de cierre pegada a una letra
    # ("Eth is ‘simple at the base’"); el habla cierra la comilla tras puntuación (.” ?”)
    return len(pal) <= 12 and bool(RE_CITA_TITULO.search(linea))


def clave_norm(p: str) -> str:
    """Texto normalizado para comparar párrafos entre entradas (casefold, sin acentos ni signos)."""
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", p).casefold()).strip()


class Huella:
    """Párrafos (clave normalizada) y shingles de SHINGLE palabras ya vistos en una fuente."""

    def __init__(self):
        self.claves: set[str] = set()
        self.shingles: set[str] = set()

    def anadir(self, toks: list[str]) -> None:
        self.claves.add(" ".join(toks))
        self.shingles.update(" ".join(toks[i:i + SHINGLE]) for i in range(len(toks) - SHINGLE + 1))

    def update(self, otra: "Huella") -> None:
        self.claves |= otra.claves
        self.shingles |= otra.shingles

    def contiene(self, toks: list[str]) -> bool:
        """Párrafo ya visto: misma clave normalizada o >UMBRAL_SHINGLES de sus shingles ya vistos
        (cubre párrafos partidos o unidos de otra forma en las otras entradas)."""
        if " ".join(toks) in self.claves:
            return True
        n = len(toks) - SHINGLE + 1
        if n <= 0:
            return False
        return sum(" ".join(toks[i:i + SHINGLE]) in self.shingles for i in range(n)) / n > UMBRAL_SHINGLES


def parsear_doc(path: Path) -> list[dict]:
    """Devuelve las entradas del Doc: {titulo, fecha, duracion, ini, fin, lineas}.

    Lee el fichero una vez; las líneas del cuerpo se guardan como referencia (rango) sobre la
    lista única de líneas, sin copiar el Doc por episodio.
    """
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        lineas = [limpiar_linea(l) for l in f]
    anclas = [i for i, l in enumerate(lineas) if l == "Get podcast"]
    cabeceras = []
    for a in anclas:
        fi = next((j for j in range(a - 1, max(a - 9, -1), -1) if RE_FECHA.match(lineas[j])), None)
        if fi is None:
            log(f"  aviso: 'Get podcast' sin fecha en {path.name} línea {a + 1}")
            continue
        meta = [l for l in lineas[fi + 1:a] if l]
        dur = meta[-1] if meta and RE_DURACION.match(meta[-1]) else None
        titulo = meta[0] if meta else ""
        cabeceras.append({"titulo": titulo, "fecha": lineas[fi], "duracion": dur,
                          "cab": fi, "cuerpo_ini": a + 1})
    entradas = []
    for k, h in enumerate(cabeceras):
        limite = cabeceras[k + 1]["cab"] if k + 1 < len(cabeceras) else len(lineas)
        fin = limite
        for j in range(h["cuerpo_ini"], limite):
            if lineas[j] == "Related":
                fin = j
                break
        else:  # sin "Related": se quitan las líneas de cabecera del siguiente episodio
            while fin > h["cuerpo_ini"] and (lineas[fin - 1] in ("", "Naval") or lineas[fin - 1].startswith("* ")):
                fin -= 1
        entradas.append({**h, "ini": h["cuerpo_ini"], "fin": fin, "lineas": lineas})
    return entradas


def turnos_de_entrada(e: dict, desconocidos: Counter, vistos: Huella) -> tuple[list[dict], int, int, Huella]:
    """Turnos del cuerpo de una entrada.

    Devuelve (turnos, títulos de sección descartados, párrafos descartados por estar ya en
    `vistos` -párrafos de entradas anteriores de la misma fuente-, huella de esta entrada).
    """
    turnos: list[dict] = []
    titulos = dups = 0
    propios = Huella()
    cuerpo = e["lineas"][e["ini"]:e["fin"]]
    if "Transcript" in cuerpo:
        cuerpo = cuerpo[cuerpo.index("Transcript") + 1:]
    for linea in cuerpo:
        if RE_NOTA_EDICION.match(linea):  # nota editorial, no se habla
            continue
        if "[" in linea:  # anotaciones "[correction: ...]": se quitan y se recoloca la puntuación
            linea = RE_ESPACIO_PUNT.sub(r"\1", RE_CORCHETES.sub("", linea))
        linea = " ".join(linea.split())
        if not linea:
            continue
        m = RE_PREFIJO.match(linea)
        if m:
            pref = m.group(1).strip()
            hab = ALIAS.get(pref.casefold())
            if hab:
                resto = RE_PUNTO_SUELTO.sub("", m.group(2).strip()).strip()
                turnos.append({"speaker": hab, "partes": [resto] if resto else []})
                continue
            if RE_PREFIJO_NOMBRE.match(pref) and len(pref.split()) <= 3 and not RE_DURACION.match(pref):
                desconocidos[pref] += 1
        if not turnos:  # descripción previa al primer prefijo
            continue
        if es_titulo_seccion(linea):
            titulos += 1
            continue
        turnos[-1]["partes"].append(linea)
    salida = []
    for t in turnos:
        partes = []
        for p in t["partes"]:
            toks = clave_norm(p).split()
            if len(toks) >= MIN_PALABRAS_DUP:
                if vistos.contiene(toks):
                    dups += 1
                    continue
                propios.anadir(toks)
            partes.append(p)
        if partes:
            salida.append({"speaker": t["speaker"], "texto": "\n".join(partes)})
    return salida, titulos, dups, propios


def titulos_buscados(fid: str, fu: dict, catalogo: dict) -> list[str]:
    ordenes = ORDENES_EXTRA.get(fid)
    if not ordenes:
        return [fu["titulo"]]
    por_orden = {e["orden"]: e["titulo"] for e in catalogo["episodios"]}
    faltan = [o for o in ordenes if o not in por_orden]
    if faltan:
        sys.exit(f"{fid}: órdenes {faltan} no están en {CATALOGO}")
    titulos = [por_orden[o] for o in ordenes]
    # la entrada propia de la fuente primero: es el recopilatorio, las demás solo aportan lo que
    # no esté ya en él (el recopilatorio repite casi literalmente los episodios sueltos)
    titulos.sort(key=lambda t: norm_titulo(t) != norm_titulo(fu["titulo"]))
    return titulos


def procesar(fu: dict, docs: Path, catalogo: dict, cache: dict, cobertura_forzada: str | None) -> dict:
    fid = fu["id"]
    if fu.get("sin_transcript"):  # sin transcript en los Docs: 06 decide solo por embeddings
        log("  sin transcript oficial: se escribe vacío (cobertura ninguna)")
        return {"id": fid, "entradas": [], "cobertura": "ninguna", "turnos": [],
                "palabras_por_hablante": {}}
    doc = docs / f"{fu['doc_anio']}_all_podcasts.txt"
    if not doc.exists():
        sys.exit(f"{fid}: no existe {doc}")
    if doc not in cache:  # un único Doc en memoria cada vez (los demás se liberan)
        cache.clear()
        cache[doc] = parsear_doc(doc)
        log(f"  {doc.name}: {len(cache[doc])} entradas")
    entradas = cache[doc]
    indice: dict[str, list[dict]] = {}
    for e in entradas:
        indice.setdefault(norm_titulo(e["titulo"]), []).append(e)

    turnos, titulos_ent, secciones, dur_total = [], [], 0, 0
    vistos = Huella()
    desconocidos: Counter = Counter()
    for t in titulos_buscados(fid, fu, catalogo):
        cands = indice.get(norm_titulo(t), [])
        if not cands:
            sys.exit(f"{fid}: la entrada '{t}' no está en {doc.name}")
        if len(cands) > 1:
            log(f"  aviso: '{t}' aparece {len(cands)} veces en {doc.name}; se usa la primera "
                f"({cands[0]['fecha']})")
        e = cands[0]
        tt, nsec, ndup, propios = turnos_de_entrada(e, desconocidos, vistos)
        vistos.update(propios)
        log(f"  entrada '{e['titulo']}' ({e['fecha']}, {e['duracion']}): {len(tt)} turnos"
            + (f", {ndup} párrafos omitidos por estar ya en otra entrada" if ndup else ""))
        turnos += tt
        secciones += nsec
        titulos_ent.append(e["titulo"])
        if not titulos_ent[:-1]:  # recopilatorio (nav167): la duración esperada es la de la entrada propia
            dur_total = duracion_a_s(e["duracion"]) or 0

    pph: Counter = Counter()
    for t in turnos:
        pph[t["speaker"]] += len(t["texto"].split())
    total = sum(pph.values())
    if desconocidos:
        log(f"  aviso: prefijos desconocidos (tratados como texto): {dict(desconocidos.most_common(8))}")
    ajenos = set(pph) - set(fu["hablantes"])
    if ajenos:
        log(f"  aviso: hablantes no esperados según fuentes_podcast.json: {sorted(ajenos)}")
    faltan = set(fu["hablantes"]) - set(pph)
    if faltan:
        log(f"  aviso: hablantes esperados sin texto: {sorted(faltan)}")

    if cobertura_forzada:
        cobertura = cobertura_forzada
    else:
        dur_audio = duracion_audio_s(fid) or dur_total
        esperadas = dur_audio / 60 * PALABRAS_ESPERADAS_MIN if dur_audio else 0
        ratio = total / esperadas if esperadas else 1.0
        cobertura = "parcial" if ratio < UMBRAL_COBERTURA else "completa"
        log(f"  cobertura {cobertura}: {total} palabras, {ratio:.2f} de las esperadas por la duración "
            f"({dur_audio / 60:.1f} min), {secciones} títulos de sección ignorados")
    return {"id": fid, "entradas": titulos_ent, "cobertura": cobertura, "turnos": turnos,
            "palabras_por_hablante": dict(sorted(pph.items(), key=lambda kv: -kv[1]))}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ids", nargs="*", help="ids de fuente (por defecto, todas)")
    ap.add_argument("--forzar", action="store_true", help="reescribe aunque la salida exista")
    ap.add_argument("--salida", type=Path, default=OFICIALES, help="directorio de salida (pruebas)")
    ap.add_argument("--docs", type=Path, default=OFICIALES / "docs")
    ap.add_argument("--cobertura", action="append", default=[], metavar="ID=VALOR",
                    help="fuerza la cobertura de una fuente (completa|parcial)")
    a = ap.parse_args()

    fuentes = cargar_fuentes()
    todos = {f["id"] for f in fuentes}
    if a.ids:
        desc = set(a.ids) - {f["id"] for f in fuentes}
        if desc:
            sys.exit(f"fuentes desconocidas: {sorted(desc)}")
        fuentes = [f for f in fuentes if f["id"] in a.ids]
    forzadas = {}
    for x in a.cobertura:
        fid, _, val = x.partition("=")
        if fid not in todos:
            ap.error(f"--cobertura {x!r}: id de fuente desconocido (formato ID=completa|parcial)")
        if val not in ("completa", "parcial"):
            ap.error(f"--cobertura {x!r}: el valor debe ser completa o parcial (formato ID=VALOR)")
        forzadas[fid] = val
    catalogo = leer_json(CATALOGO)

    # Agrupa por Doc para parsear cada uno una sola vez
    fuentes.sort(key=lambda f: f["doc_anio"] or 0)
    cache: dict = {}
    for fu in fuentes:
        salida = a.salida / f"{fu['id']}.json"
        if salida.exists() and not a.forzar:
            log(f"{fu['id']}: {salida.name} ya existe, se salta")
            continue
        log(f"{fu['id']}: {fu['titulo']} (Doc {fu['doc_anio']})")
        res = procesar(fu, a.docs, catalogo, cache, forzadas.get(fu["id"]))
        escribir_json(salida, res)
        log(f"  escrito {salida}  palabras: {res['palabras_por_hablante']}")


if __name__ == "__main__":
    main()
