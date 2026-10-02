#!/usr/bin/env python3
"""Formato 0: captura verbatim de una pagina de nav.al.

Uso: python f0.py raw.txt salida_dir --modelo "Modelo, esfuerzo X"
Cabecera: 1a linea no vacia = fecha, 2a = titulo, 3a = subtitulo.
Todo lo anterior al primer turno con prefijo se descarta y se informa.
"""
import json, re, sys
from datetime import datetime
from pathlib import Path

PREFIJO = re.compile(r"^(Naval|Nivi): (.*)$")
DURACION = re.compile(r"^\[?\d{1,2}:\d{2}(:\d{2})?(\]\(.*\))?$")
INTERFAZ = {"Get podcast"}
ABREV = {"Mr.", "Mrs.", "Ms.", "Dr.", "U.S.", "etc.", "e.g.", "i.e.", "vs.", "St.", "Jr.", "Sr."}
CORTE = re.compile(r"([.?!][\"\u201d\u2019')]*)\s+")


def frases(texto):
    out, ini = [], 0
    for m in CORTE.finditer(texto):
        fin = m.end(1)
        palabra = texto[:fin].split()[-1].strip("\"\u201c\u201d\u2019'(")
        if palabra in ABREV or re.fullmatch(r"(?:[A-Z]\.)+", palabra):
            continue  # abreviatura o iniciales (J.D. Rockefeller)
        out.append(texto[ini:fin])
        ini = m.end()
    resto = texto[ini:]
    if resto.strip():
        out.append(resto)
    return out


def es_titulo(linea):
    return len(linea) < 120 and linea[-1] not in ".?!"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("raw"); ap.add_argument("salida"); ap.add_argument("--modelo", required=True)
    a = ap.parse_args()
    raw, salida, MODELO = Path(a.raw), Path(a.salida), a.modelo
    lineas = [l.rstrip("\n") for l in raw.read_text(encoding="utf-8").splitlines()]
    no_vacias = [l for l in lineas if l.strip()]
    fecha, titulo, subtitulo = no_vacias[0], no_vacias[1], no_vacias[2]

    cuerpo = lineas[lineas.index(subtitulo) + 1:]
    contenido, titulos, descartadas = [], [], []
    for linea in cuerpo:
        s = linea.strip()
        if not s:
            continue
        m = PREFIJO.match(linea)
        if m:
            contenido.append({"speaker": m.group(1), "frases": frases(m.group(2))})
        elif DURACION.match(s) or s in INTERFAZ:
            descartadas.append(linea)
        elif not contenido:
            descartadas.append(linea)  # texto de pagina previo al primer turno
        elif es_titulo(s):
            titulos.append(linea)
        else:
            contenido[-1]["frases"].extend(frases(linea))

    datos = {"generado_por": MODELO, "fecha": fecha, "titulo": titulo, "titulo_seccion": subtitulo,
             "contenido": contenido, "titulos_seccion": titulos}

    try:
        f = datetime.strptime(fecha, "%b %d %Y").strftime("%Y-%m-%d")
    except ValueError:
        f = re.sub(r"\s+", "-", fecha.strip())
    slug = re.sub(r"[^a-z0-9]+", "-", titulo.lower()).strip("-")
    destino = salida / f"{f}_{slug}.json"
    destino.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(destino)
    print("DESCARTADAS:")
    for d in descartadas:
        print("  ", repr(d))
    print("TURNOS:", [(t["speaker"], len(t["frases"])) for t in contenido])
    print("TITULOS:", titulos)


if __name__ == "__main__":
    main()
