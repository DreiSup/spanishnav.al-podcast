#!/usr/bin/env bash
# Parte 2e: fuentes nuevas de vitalik, qureshi, hodak, rauch y scholl (01-06), en serie y detrás de
# orquesta_ridley.sh. Las externas no tienen transcript: 06 deja sus etiquetas sin resolver y se
# asignan a mano (06_hablantes.py <id> --asignar ...). La medición (08) se lanza después.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
etapa() { ./etapa.sh "$@" || { paso "PARADA: falló $*"; exit 1; }; }
while pgrep -f orquesta_ridley.sh >/dev/null; do sleep 60; done
IDS="nav136 lex080 wsh104 cmm009 npr001 acq001 evr047 hii153 cwt277"
paso "01"; etapa 01_descargar.py $IDS
paso "05"; etapa 05_oficiales.py $IDS
for id in $IDS; do
  case $id in nav*) D="";; *) D="--min 2 --max 3";; esac
  for s in 02_asr.py 03_alinear.py; do paso "$s $id"; etapa "$s" "$id"; done
  paso "04 $id $D"; etapa 04_diarizar.py "$id" $D
done
for id in $IDS; do paso "06 $id"; ./etapa.sh 06_hablantes.py "$id" || paso "06 $id sin etiquetas ok"; done
paso "FIN procesado invitados"
