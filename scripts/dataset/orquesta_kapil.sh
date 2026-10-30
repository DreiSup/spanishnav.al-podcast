#!/usr/bin/env bash
# Parte 2, naval_kapil: espera a orquesta_parte2.sh y a las asignaciones de 06 (Kapil 2019)
# y mide los clips de Naval (naval_kapil) y de Kapil (aparte) en las 5 fuentes.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
while pgrep -f "orquesta_parte2.sh|06_hablantes.py" >/dev/null; do sleep 30; done
F="nav072 nav001 nav002 nav003 nav004"
for h in naval_kapil kapil; do
  paso "08 $h"; ./etapa.sh 08_clips.py $h $F || { paso "PARADA 08 $h"; exit 1; }
done
paso "FIN kapil"
