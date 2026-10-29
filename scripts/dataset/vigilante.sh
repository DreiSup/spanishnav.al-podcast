#!/usr/bin/env bash
# Vigila RAM, swap, VRAM y disco cada 15 s y lo apunta en ~/naval-datos/logs/recursos.log.
# Escribe "ALERTA" cuando se cruza un umbral; con RAM crítica mata el proceso pesado
# que tenga el candado de GPU (las etapas corren además con tope de cgroup).
set -u
DATOS="${NAVAL_DATOS:-$HOME/naval-datos}"
LOG="$DATOS/logs/recursos.log"
RAM_ALERTA_MB=2000
RAM_CRITICA_MB=1200
DISCO_ALERTA_GB=15
mkdir -p "$DATOS/logs"
while true; do
  ram=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
  swap=$(awk '/SwapTotal/ {t=$2} /SwapFree/ {f=$2} END {print int((t-f)/1024)}' /proc/meminfo)
  disco=$(df -BG --output=avail "$DATOS" | tail -1 | tr -dc '0-9')
  vram=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
  linea="$(date +%H:%M:%S) ram_libre=${ram}MB swap_usada=${swap}MB vram=${vram}MB disco_libre=${disco}GB"
  if [ "$ram" -lt "$RAM_CRITICA_MB" ]; then
    pid=$(pgrep -f "naval-datos/venv/bin/python.*scripts/dataset/0[2-9]" | head -1)
    linea="$linea ALERTA RAM_CRITICA mato_pid=${pid:-ninguno}"
    [ -n "${pid:-}" ] && kill -TERM "$pid"
  elif [ "$ram" -lt "$RAM_ALERTA_MB" ]; then
    linea="$linea ALERTA RAM_BAJA"
  fi
  [ "$disco" -lt "$DISCO_ALERTA_GB" ] && linea="$linea ALERTA DISCO_BAJO"
  echo "$linea" >> "$LOG"
  sleep 15
done
