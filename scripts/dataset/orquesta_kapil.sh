#!/usr/bin/env bash
# Parte 2, naval_kapil: lanzar cuando 06 ya tenga asignadas las etiquetas de Kapil 2019;
# y mide los clips de Naval (naval_kapil) y de Kapil (aparte) en las 5 fuentes.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
F="nav072 nav001 nav002 nav003 nav004"
for h in naval_kapil kapil; do
  paso "08 $h"; ./etapa.sh 08_clips.py $h $F || { paso "PARADA 08 $h"; exit 1; }
done
paso "FIN kapil"
