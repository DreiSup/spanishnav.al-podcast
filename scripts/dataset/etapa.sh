#!/usr/bin/env bash
# Lanza una etapa del pipeline con tope de memoria (cgroup) y reintentos.
#   etapa.sh <script.py> [args...]
# El tope evita que una etapa desbocada tumbe el escritorio: si pasa de MEM_MAX,
# el kernel mata solo esa etapa. El candado de GPU lo toma el propio script.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
DATOS="${NAVAL_DATOS:-$HOME/naval-datos}"
PY="$DATOS/venv/bin/python"
MEM_MAX="${MEM_MAX:-5500M}"
SWAP_MAX="${SWAP_MAX:-1G}"
REINTENTOS="${REINTENTOS:-3}"
script="$1"; shift
for intento in $(seq 1 "$REINTENTOS"); do
  echo "[$(date +%H:%M:%S)] etapa $script $* (intento $intento, MemoryMax=$MEM_MAX)"
  systemd-run --user --scope -q -p MemoryMax="$MEM_MAX" -p MemorySwapMax="$SWAP_MAX" -- \
    "$PY" "$DIR/$script" "$@"
  rc=$?
  if [ "$rc" -eq 0 ]; then echo "[$(date +%H:%M:%S)] etapa OK $script $*"; exit 0; fi
  echo "[$(date +%H:%M:%S)] etapa FALLO rc=$rc $script $*"
  [ "$rc" -eq 137 ] && echo "  (137 = matada por memoria)"
  sleep 20
done
echo "[$(date +%H:%M:%S)] etapa ABANDONADA $script $*"
exit 1
