#!/usr/bin/env python3
"""Valida la salida JSON de los formatos de spanishnav.al.

Uso:
    python validate.py archivo.json --formato 4

El Formato 0 es verbatim en ingles: no se le aplican las reglas de simbolos
prohibidos ni de cifras escritas con letras. Los formatos 3, 4 y 5 si.
"""

import argparse
import json
import re
import sys

HABLANTES = {"Naval", "Nivi"}

SIMBOLOS_PROHIBIDOS = {
    "\u2014": "guion largo (em dash)",
    "\u2013": "guion medio (en dash)",
    ";": "punto y coma",
    "[": "corchete de apertura",
    "]": "corchete de cierre",
    "{": "llave de apertura",
    "}": "llave de cierre",
    "*": "asterisco",
    "\u201c": "comilla tipografica de apertura",
    "\u201d": "comilla tipografica de cierre",
    "(": "parentesis de apertura",
    ")": "parentesis de cierre",
    "\u00ab": "comilla latina de apertura",
    "\u00bb": "comilla latina de cierre",
    "\u2039": "comilla simple angular de apertura",
    "\u203a": "comilla simple angular de cierre",
    "\"": "comilla recta",
}

CLAVES = {
    "0": ["generado_por", "fecha", "titulo", "titulo_seccion", "contenido", "titulos_seccion"],
    "4": ["fecha", "titulo", "contenido", "titulos_seccion"],
    "5": ["generado_por", "fecha", "titulo", "titulo_seccion", "contenido", "titulos_seccion"],
}


class Informe:
    def __init__(self):
        self.errores = []
        self.avisos = []

    def error(self, mensaje):
        self.errores.append(mensaje)

    def aviso(self, mensaje):
        self.avisos.append(mensaje)


def revisar_texto(texto, ubicacion, informe, traducido):
    if not isinstance(texto, str):
        informe.error(f"{ubicacion}: se esperaba texto, hay {type(texto).__name__}")
        return
    if not texto.strip():
        informe.error(f"{ubicacion}: texto vacio")
        return
    if not traducido:
        return
    for simbolo, nombre in SIMBOLOS_PROHIBIDOS.items():
        if simbolo in texto:
            informe.error(f"{ubicacion}: contiene {nombre} -> {texto[:70]}")
    if re.search(r"\d", texto):
        informe.error(f"{ubicacion}: cifra sin escribir con letras -> {texto[:70]}")


def revisar_turnos(contenido, informe, traducido):
    if not isinstance(contenido, list):
        informe.error("contenido: se esperaba una lista de turnos")
        return
    if not contenido:
        informe.error("contenido: esta vacio")
        return
    for i, turno in enumerate(contenido):
        etiqueta = f"contenido[{i}]"
        if not isinstance(turno, dict):
            informe.error(f"{etiqueta}: se esperaba un objeto")
            continue
        sobran = set(turno) - {"speaker", "frases"}
        if sobran:
            informe.error(f"{etiqueta}: claves inesperadas {sorted(sobran)}")
        hablante = turno.get("speaker")
        if hablante not in HABLANTES:
            informe.aviso(f"{etiqueta}: hablante no habitual -> {hablante!r}")
        frases = turno.get("frases")
        if not isinstance(frases, list) or not frases:
            informe.error(f"{etiqueta}.frases: se esperaba una lista no vacia")
            continue
        for j, frase in enumerate(frases):
            revisar_texto(frase, f"{etiqueta}.frases[{j}]", informe, traducido)
            cierres = ".?!\"'\u201d\u2019"
            if isinstance(frase, str) and frase.strip() and frase.strip()[-1] not in cierres:
                informe.aviso(
                    f"{etiqueta}.frases[{j}]: no termina en signo de cierre -> {frase[:70]}"
                )


def revisar_titulos(titulos, informe, traducido):
    if not isinstance(titulos, list):
        informe.error("titulos_seccion: se esperaba una lista")
        return
    for i, titulo in enumerate(titulos):
        revisar_texto(titulo, f"titulos_seccion[{i}]", informe, traducido)


def validar(datos, formato, informe):
    traducido = formato != "0"

    if formato == "3":
        if not isinstance(datos, list):
            informe.error("raiz: el Formato 3 debe ser un array")
            return
        revisar_turnos(datos, informe, traducido)
        return

    if not isinstance(datos, dict):
        informe.error(f"raiz: el Formato {formato} debe ser un objeto")
        return

    esperadas = CLAVES[formato]
    presentes = list(datos)
    faltan = [c for c in esperadas if c not in presentes]
    sobran = [c for c in presentes if c not in esperadas]
    if faltan:
        informe.error(f"raiz: faltan claves {faltan}")
    if sobran:
        informe.error(f"raiz: claves inesperadas {sobran}")
    if not faltan and not sobran and presentes != esperadas:
        informe.error(f"raiz: orden de claves incorrecto, se esperaba {esperadas}")

    if "generado_por" in datos and not (isinstance(datos["generado_por"], str) and datos["generado_por"].strip()):
        informe.error("generado_por: se esperaba texto no vacio")
    if "fecha" in datos and not isinstance(datos["fecha"], str):
        informe.error("fecha: se esperaba texto")
    if "titulo" in datos:
        revisar_texto(datos["titulo"], "titulo", informe, traducido)
    if "titulo_seccion" in datos:
        valor = datos["titulo_seccion"]
        # En Formato 0 la cadena vacia es legitima: hay episodios sin subtitulo.
        if not (formato == "0" and valor == ""):
            revisar_texto(valor, "titulo_seccion", informe, traducido)
    if "contenido" in datos:
        revisar_turnos(datos["contenido"], informe, traducido)
    if "titulos_seccion" in datos:
        revisar_titulos(datos["titulos_seccion"], informe, traducido)


def main():
    parser = argparse.ArgumentParser(description="Valida un JSON de spanishnav.al")
    parser.add_argument("archivo")
    parser.add_argument("--formato", required=True, choices=["0", "3", "4", "5"])
    args = parser.parse_args()

    informe = Informe()
    try:
        with open(args.archivo, encoding="utf-8") as f:
            datos = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"FALTA  JSON invalido: {exc}")
        return 1
    except OSError as exc:
        print(f"FALTA  no se puede leer el archivo: {exc}")
        return 1

    validar(datos, args.formato, informe)

    for aviso in informe.avisos:
        print(f"AVISO  {aviso}")
    for error in informe.errores:
        print(f"FALTA  {error}")

    if informe.errores:
        print(f"\nFALTA  {len(informe.errores)} error(es) en Formato {args.formato}")
        return 1

    print(f"OK  Formato {args.formato} valido ({len(informe.avisos)} aviso(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
