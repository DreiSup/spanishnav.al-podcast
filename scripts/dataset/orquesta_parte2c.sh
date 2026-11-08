#!/usr/bin/env bash
# Parte 2c: medición (08) de las fuentes sin transcript, con etiquetas ya asignadas por
# embeddings (06 --asignar). Espera a que termine orquesta_parte2b.sh (comparten GPU).
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
etapa() { ./etapa.sh "$@" || { paso "PARADA: falló $*"; exit 1; }; }
LOG2B="${NAVAL_DATOS:-$HOME/naval-datos}/logs/orquesta_parte2b.log"
until grep -qE "### FIN parte2b|PARADA" "$LOG2B"; do sleep 60; done
grep -q PARADA "$LOG2B" && { paso "PARADA: parte2b no terminó bien"; exit 1; }
paso "08 brett"; etapa 08_clips.py brett tok221
paso "08 nivi"; etapa 08_clips.py nivi niv001 niv002 niv003 nav163
paso "FIN parte2c"
