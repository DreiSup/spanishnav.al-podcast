#!/usr/bin/env bash
# Ejecuta una prueba de desarrollo SIN GPU, de una en una y con tope de memoria.
#   prueba.sh <script.py> [args...]      (rutas relativas a scripts/dataset/)
# Toda prueba que importe torch, whisperx, pyannote o speechbrain DEBE pasar por aquí:
# el candado serializa las pruebas y el cgroup mata la prueba si pasa de 2,5 GB,
# así nunca compite con la etapa pesada que esté corriendo.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
DATOS="${NAVAL_DATOS:-$HOME/naval-datos}"
cd "$DIR"
exec flock "$DATOS/prueba.lock" \
  systemd-run --user --scope -q -p MemoryMax="${MEM_MAX:-2500M}" -p MemorySwapMax=512M -- \
  env CUDA_VISIBLE_DEVICES= NAVAL_PRUEBA=1 "$DATOS/venv/bin/python" "$@"
