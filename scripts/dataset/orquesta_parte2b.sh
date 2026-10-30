#!/usr/bin/env bash
# Parte 2b: fuentes nuevas de deutsch, brett y nivi (01-06) y medición (08) de las que tienen
# transcript oficial. Las sin transcript (tok221, niv001-003, nav163) necesitan antes asignar
# etiquetas por embeddings (06 --asignar); se miden después a mano.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
etapa() { ./etapa.sh "$@" || { paso "PARADA: falló $*"; exit 1; }; }
IDS="nav140 nav141 nav055 nav158 nav163 tok221 niv001 niv002 niv003"
paso "01"; etapa 01_descargar.py $IDS
paso "05"; etapa 05_oficiales.py $IDS
for id in $IDS; do
  case $id in niv*) D="--min 1 --max 8";; tok*) D="--min 1 --max 2";; *) D="";; esac
  for s in 02_asr.py 03_alinear.py; do paso "$s $id"; etapa "$s" "$id"; done
  paso "04 $id $D"; etapa 04_diarizar.py "$id" $D
done
for id in $IDS; do paso "06 $id"; ./etapa.sh 06_hablantes.py "$id" || paso "06 $id sin etiquetas ok"; done
paso "FIN procesado"
paso "08 deutsch"; etapa 08_clips.py deutsch nav139 nav140
etapa 08_clips.py deutsch nav141 --muestra-min 8
paso "08 brett"; etapa 08_clips.py brett nav109 nav139
paso "08 nivi"; etapa 08_clips.py nivi nav056 nav167 nav055 nav158
paso "FIN parte2b"
