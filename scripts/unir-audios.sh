#!/usr/bin/env bash
# Concatena los clips de tts/ (uno por intervención) en un único audio.
#
#   ./scripts/unir-audios.sh episodios/2024/como-pensar-con-claridad
#   ./scripts/unir-audios.sh episodios/2024/... --silencio 0.4
#
# Los clips se ordenan alfabéticamente, por eso conviene numerarlos con
# ceros a la izquierda: 0001-naval.wav, 0002-entrevistador.wav, ...
set -euo pipefail

EPISODIO="${1:-}"
SILENCIO="0.35"   # segundos de pausa entre intervenciones

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --silencio) SILENCIO="$2"; shift 2 ;;
    *) echo "opción desconocida: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$EPISODIO" || ! -d "$EPISODIO" ]]; then
  echo "uso: $0 <ruta/del/episodio> [--silencio SEGUNDOS]" >&2
  exit 1
fi
command -v ffmpeg >/dev/null || { echo "error: falta ffmpeg" >&2; exit 1; }

TTS="$EPISODIO/tts"
SALIDA="$EPISODIO/audio/episodio.es.mp3"
mkdir -p "$EPISODIO/audio"

mapfile -t CLIPS < <(find "$TTS" -maxdepth 1 -type f \
  \( -name '*.wav' -o -name '*.mp3' -o -name '*.m4a' -o -name '*.flac' \) | sort)

if [[ ${#CLIPS[@]} -eq 0 ]]; then
  echo "error: no hay clips de audio en $TTS" >&2
  exit 1
fi
echo "clips encontrados: ${#CLIPS[@]}"

TRABAJO="$(mktemp -d)"
trap 'rm -rf "$TRABAJO"' EXIT

# Silencio intercalado, con el mismo formato que los clips normalizados
ffmpeg -v error -y -f lavfi -t "$SILENCIO" -i anullsrc=r=44100:cl=mono \
  -ar 44100 -ac 1 "$TRABAJO/silencio.wav"

LISTA="$TRABAJO/concat.txt"
: > "$LISTA"
for i in "${!CLIPS[@]}"; do
  # Normaliza cada clip para que concat no falle por formatos mezclados
  NORM="$TRABAJO/$(printf '%05d' "$i").wav"
  ffmpeg -v error -y -i "${CLIPS[$i]}" -ar 44100 -ac 1 "$NORM"
  printf "file '%s'\n" "$NORM" >> "$LISTA"
  [[ $i -lt $(( ${#CLIPS[@]} - 1 )) ]] && printf "file '%s'\n" "$TRABAJO/silencio.wav" >> "$LISTA"
done

ffmpeg -v error -y -f concat -safe 0 -i "$LISTA" -c:a libmp3lame -b:a 128k "$SALIDA"

echo "generado: $SALIDA"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$SALIDA" \
  | awk '{printf "duración: %d:%02d:%02d\n", $1/3600, ($1%3600)/60, $1%60}'
