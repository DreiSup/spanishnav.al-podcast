#!/usr/bin/env bash
# Procesa nav081 (Happiness) de punta a punta: descarga, oficiales, ASR, alineado, diarización, hablantes.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
etapa() { ./etapa.sh "$@" || { paso "PARADA: falló $*"; exit 1; }; }
for s in 01_descargar.py 05_oficiales.py 02_asr.py 03_alinear.py 04_diarizar.py 06_hablantes.py; do
  paso "$s nav081"; etapa "$s" nav081
done
paso "FIN nav081"
