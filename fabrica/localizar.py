#!/usr/bin/env python3
"""Dónde está un fallo del master: de un minuto o de un trozo de frase a la intervención y la frase que hay que
rehacer, con la línea lista para la celda 2 de la fábrica.

    python3 fabrica/localizar.py 2019/037-productize-yourself --texto "productízate a ti mismo"
    python3 fabrica/localizar.py 2019/037-productize-yourself --minuto 1:21 --indice indice_master.tsv

Por texto basta el repo. Por minuto hace falta el `indice_master.tsv` del episodio (está en su carpeta de Drive,
junto al informe): dice en qué segundo del master empieza cada frase.
"""
import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "fabrica"))
import fabrica  # noqa: E402


def _plano(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", texto)).strip()


def _segundos(minuto):
    partes = [float(x.replace(",", ".")) for x in minuto.split(":")]
    return partes[0] * 60 + partes[1] if len(partes) == 2 else partes[0]


def frases_del_plan(episodio):
    tr = json.loads((RAIZ / "episodios" / episodio / "transcript.es.json").read_text(encoding="utf-8"))
    plan = fabrica.plan_episodio(tr, fabrica.cargar_config())
    return [(p["fichero"], k + 1, f) for p in plan for k, f in enumerate(p["frases"])]


def por_texto(episodio, texto, n=3):
    buscado = _plano(texto)
    puntos = []
    for clip, k, frase in frases_del_plan(episodio):
        plano = _plano(frase)
        nota = 1.0 if buscado in plano else difflib.SequenceMatcher(None, buscado, plano).ratio()
        puntos.append((nota, clip, k, frase))
    return sorted(puntos, reverse=True)[:n]


def por_minuto(episodio, minuto, indice):
    filas = [l.split("\t") for l in Path(indice).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    seg = _segundos(minuto)
    antes = [f for f in filas if float(f[1]) <= seg] or filas[:1]
    _, ini, clip, k = antes[-1]
    textos = {(c, kk): f for c, kk, f in frases_del_plan(episodio)}
    return clip, int(k), float(ini), textos.get((clip, int(k)), "?")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episodio", help="carpeta del repo, p. ej. 2019/037-productize-yourself")
    ap.add_argument("--texto", help="un trozo de la frase que suena mal")
    ap.add_argument("--minuto", help="minuto del master, p. ej. 7:21")
    ap.add_argument("--indice", help="indice_master.tsv del episodio (para --minuto)")
    a = ap.parse_args()
    if a.texto:
        for nota, clip, k, frase in por_texto(a.episodio, a.texto):
            print(f"{nota:.2f}  {clip} frase {k}: {frase}")
        _, clip, k, _ = por_texto(a.episodio, a.texto, 1)[0]
    elif a.minuto and a.indice:
        clip, k, ini, frase = por_minuto(a.episodio, a.minuto, a.indice)
        print(f"{a.minuto} → {clip} frase {k} (empieza en {fabrica._mmss(ini)}): {frase}")
    else:
        ap.error("pasa --texto, o --minuto con --indice")
    print(f'\nREHACER_FRASES = {{"{a.episodio}": {{"{clip}": [{k}]}}}}')


if __name__ == "__main__":
    main()
