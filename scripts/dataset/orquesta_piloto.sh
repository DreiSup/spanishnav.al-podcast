#!/usr/bin/env bash
# Piloto de la Parte 2: espera a que termine nav081 y mide los clips de Naval en nav056.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
while pgrep -f orquesta_nav081.sh >/dev/null; do sleep 30; done
echo "[$(date +%H:%M:%S)] ### 08_clips naval nav056"
./etapa.sh 08_clips.py naval nav056 || { echo "PARADA"; exit 1; }
echo "[$(date +%H:%M:%S)] ### FIN piloto"
