#!/usr/bin/env bash
# Parte 2d: dataset de ridley. nav074 (Fase 1a) y nav075 ya procesadas; eco001 descartada. Procesa mwi923 y sfy001 (01-06).
# Las externas no tienen transcript: 06 deja sus etiquetas sin resolver y se asignan a mano con
# 06_hablantes.py <id> --asignar ... (cosenos delante). La medición (08) se lanza después.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
etapa() { ./etapa.sh "$@" || { paso "PARADA: falló $*"; exit 1; }; }
IDS="mwi923 sfy001"
paso "01"; etapa 01_descargar.py $IDS
paso "05"; etapa 05_oficiales.py $IDS
for id in $IDS; do
  case $id in mwi*|sfy*) D="--min 2 --max 3";; *) D="--min 2 --max 2";; esac
  for s in 02_asr.py 03_alinear.py; do paso "$s $id"; etapa "$s" "$id"; done
  paso "04 $id $D"; etapa 04_diarizar.py "$id" $D
done
for id in $IDS; do paso "06 $id"; ./etapa.sh 06_hablantes.py "$id" || paso "06 $id sin etiquetas ok"; done
paso "FIN procesado ridley"
