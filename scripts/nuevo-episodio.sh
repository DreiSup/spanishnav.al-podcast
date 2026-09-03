#!/usr/bin/env bash
# Crea el esqueleto de un episodio nuevo a partir de plantillas/episodio.
#
#   ./scripts/nuevo-episodio.sh 2024 como-pensar-con-claridad
#
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 2 ]]; then
  echo "uso: $0 <anio> <slug> [titulo original]" >&2
  echo "ej.: $0 2024 como-pensar-con-claridad \"How to Think Clearly\"" >&2
  exit 1
fi

ANIO="$1"
SLUG="$2"
TITULO="${3:-}"
DESTINO="$RAIZ/episodios/$ANIO/$SLUG"

if [[ ! "$ANIO" =~ ^[0-9]{4}$ ]]; then
  echo "error: el año debe tener 4 dígitos (recibido: $ANIO)" >&2
  exit 1
fi
if [[ ! "$SLUG" =~ ^[a-z0-9-]+$ ]]; then
  echo "error: el slug solo admite minúsculas, números y guiones (recibido: $SLUG)" >&2
  exit 1
fi
if [[ -e "$DESTINO" ]]; then
  echo "error: ya existe $DESTINO" >&2
  exit 1
fi

cp -r "$RAIZ/plantillas/episodio" "$DESTINO"
mkdir -p "$DESTINO"/{tts,audio,video}

# tts/, audio/ y video/ están en .gitignore; los .gitkeep no bastan para
# que git las siga, pero sí para que existan si algún día se desingoran.
for d in tts audio video; do : > "$DESTINO/$d/.gitkeep"; done

python3 - "$DESTINO/metadata.json" "$SLUG" "$ANIO" "$TITULO" <<'PY'
import json, sys
ruta, slug, anio, titulo = sys.argv[1:5]
with open(ruta, encoding="utf-8") as f:
    meta = json.load(f)
meta["slug"] = slug
meta["anio"] = int(anio)
meta["titulo_original"] = titulo
with open(ruta, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY

echo "creado: episodios/$ANIO/$SLUG"
echo
echo "siguientes pasos:"
echo "  1. pega la transcripción en  episodios/$ANIO/$SLUG/transcripciones/original.en.md"
echo "  2. traduce a                 episodios/$ANIO/$SLUG/transcripciones/traduccion.es.md"
echo "  3. genera los clips TTS en   episodios/$ANIO/$SLUG/tts/  (0001-*.wav, 0002-*.wav, ...)"
echo "  4. ./scripts/unir-audios.sh episodios/$ANIO/$SLUG"
echo "  5. ./scripts/render-video.sh episodios/$ANIO/$SLUG"
