#!/usr/bin/env python3
"""Escribe el Formato 5 desde un JSON de datos (fecha, titulo, titulo_seccion, contenido, titulos_seccion).
Uso: python f5.py datos.json salida.json --modelo "Modelo, esfuerzo X"
Pone generado_por como primera clave y dos lineas en blanco entre turnos de distinto hablante."""
import argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("datos"); ap.add_argument("salida"); ap.add_argument("--modelo", required=True)
a = ap.parse_args()
MODELO = a.modelo
d = json.load(open(a.datos, encoding="utf-8"))


def j(v, nivel):
    return json.dumps(v, indent=2, ensure_ascii=False).replace("\n", "\n" + "  " * nivel)


partes = []
for i, t in enumerate(d["contenido"]):
    if i:
        partes.append(",\n\n\n" if t["speaker"] != d["contenido"][i - 1]["speaker"] else ",\n")
    partes.append("    " + j(t, 2))

e = lambda v: json.dumps(v, ensure_ascii=False)
salida = (
    "{\n"
    f'  "generado_por": {e(MODELO)},\n'
    f'  "fecha": {e(d["fecha"])},\n'
    f'  "titulo": {e(d["titulo"])},\n'
    f'  "titulo_seccion": {e(d["titulo_seccion"])},\n'
    '  "contenido": [\n' + "".join(partes) + "\n  ],\n"
    f'  "titulos_seccion": {j(d["titulos_seccion"], 1)}\n'
    "}\n"
)
open(a.salida, "w", encoding="utf-8").write(salida)
print(a.salida)
