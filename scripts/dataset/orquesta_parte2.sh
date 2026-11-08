#!/usr/bin/env bash
# Parte 2: procesa las 4 fuentes de Kapil de 2019 (01-06) y mide los clips de Naval que faltan
# para el dataset de naval (08). Reanudable: cada etapa se salta si su salida ya existe.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
etapa() { ./etapa.sh "$@" || { paso "PARADA: falló $*"; exit 1; }; }
K="nav001 nav002 nav003 nav004"
paso "01 $K"; etapa 01_descargar.py $K
paso "05 $K"; etapa 05_oficiales.py $K
for id in $K; do
  for s in 02_asr.py 03_alinear.py 04_diarizar.py; do paso "$s $id"; etapa "$s" "$id"; done
done
for id in $K; do paso "06 $id"; ./etapa.sh 06_hablantes.py "$id" || paso "06 $id sin etiquetas ok (esperado sin transcript)"; done
paso "FIN kapil2019"
paso "08 naval"; etapa 08_clips.py naval nav167 nav109 nav074 nav139 nav135 nav081
paso "FIN parte2"
