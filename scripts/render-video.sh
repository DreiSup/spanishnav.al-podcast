#!/usr/bin/env bash
# Une el audio final con el thumbnail para crear el .mp4 de YouTube.
#
#   ./scripts/render-video.sh episodios/2024/como-pensar-con-claridad
#
# Vídeo: imagen estática a 1920x1080, códec H.264, un fotograma cada 5s
# (fps bajo + -tune stillimage => archivo pequeño y subida rápida).
set -euo pipefail

EPISODIO="${1:-}"
if [[ -z "$EPISODIO" || ! -d "$EPISODIO" ]]; then
  echo "uso: $0 <ruta/del/episodio>" >&2
  exit 1
fi
command -v ffmpeg >/dev/null || { echo "error: falta ffmpeg" >&2; exit 1; }

AUDIO="$(find "$EPISODIO/audio" -maxdepth 1 -type f \( -name '*.mp3' -o -name '*.wav' \) 2>/dev/null | sort | head -1)"
IMAGEN="$(find "$EPISODIO" -maxdepth 1 -type f \( -name 'thumbnail.*' -o -name 'portada.*' \) | sort | head -1)"
SALIDA="$EPISODIO/video/episodio.es.mp4"

[[ -n "$AUDIO"  ]] || { echo "error: no hay audio en $EPISODIO/audio (ejecuta antes unir-audios.sh)" >&2; exit 1; }
[[ -n "$IMAGEN" ]] || { echo "error: no hay thumbnail.* en $EPISODIO" >&2; exit 1; }

mkdir -p "$EPISODIO/video"
echo "audio:     $AUDIO"
echo "thumbnail: $IMAGEN"

ffmpeg -v error -stats -y \
  -loop 1 -framerate 1 -i "$IMAGEN" \
  -i "$AUDIO" \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -c:v libx264 -tune stillimage -preset veryfast -crf 23 -r 5 -g 50 \
  -c:a aac -b:a 192k \
  -shortest -movflags +faststart \
  "$SALIDA"

echo "generado: $SALIDA"
