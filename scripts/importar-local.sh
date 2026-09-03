#!/usr/bin/env bash
# Migra tu carpeta local de trabajo a la estructura del repo.
#
#   ./scripts/importar-local.sh ~/naval-podcasts            # simulación (no toca nada)
#   ./scripts/importar-local.sh ~/naval-podcasts --aplicar  # copia de verdad
#
# Espera una carpeta con la forma:  <origen>/<anio>/<episodio>/...
# Clasifica por heurística lo que encuentra dentro de cada episodio:
#   *.jpg|*.png sueltos      -> thumbnail.<ext>
#   texto con "es|esp|spa|traduc" en el nombre -> transcripciones/traduccion.es.md
#   el otro texto            -> transcripciones/original.en.md
#   carpeta con varios audios-> tts/            (NO se versiona)
#   audio suelto             -> audio/          (NO se versiona)
#   vídeo suelto             -> video/          (NO se versiona)
#
# Copia, nunca mueve: tu carpeta original se queda intacta.
set -euo pipefail

ORIGEN="${1:-}"
APLICAR=0
[[ "${2:-}" == "--aplicar" ]] && APLICAR=1

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -z "$ORIGEN" || ! -d "$ORIGEN" ]]; then
  echo "uso: $0 <carpeta/local/origen> [--aplicar]" >&2
  exit 1
fi
ORIGEN="$(cd "$ORIGEN" && pwd)"

(( APLICAR )) || echo "=== SIMULACIÓN (añade --aplicar para copiar de verdad) ==="
echo "origen:  $ORIGEN"
echo "destino: $RAIZ/episodios"
echo

# Convierte "Cómo pensar con claridad" -> "como-pensar-con-claridad"
normalizar() {
  python3 -c '
import re, sys, unicodedata
t = unicodedata.normalize("NFKD", sys.argv[1])
t = "".join(c for c in t if not unicodedata.combining(c)).lower()
sys.stdout.write(re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-"))
' "$1"
}

ejecutar() {
  if (( APLICAR )); then "$@"; else echo "    [simulado] $*"; fi
}

TOTAL=0
for DIR_ANIO in "$ORIGEN"/*/; do
  ANIO="$(basename "$DIR_ANIO")"
  [[ "$ANIO" =~ ^[0-9]{4}$ ]] || { echo "salto '$ANIO' (no parece un año)"; continue; }

  for DIR_EP in "$DIR_ANIO"*/; do
    [[ -d "$DIR_EP" ]] || continue
    NOMBRE="$(basename "$DIR_EP")"
    SLUG="$(normalizar "$NOMBRE")"
    DEST="$RAIZ/episodios/$ANIO/$SLUG"
    TOTAL=$(( TOTAL + 1 ))

    echo "[$ANIO/$SLUG]  <- $NOMBRE"
    ejecutar mkdir -p "$DEST/transcripciones" "$DEST/tts" "$DEST/audio" "$DEST/video"

    # --- textos -------------------------------------------------
    ES=""; EN=""
    while IFS= read -r f; do
      base="$(basename "$f")"
      if [[ "$(normalizar "$base")" =~ (^|-)(es|esp|spa|espanol|traducc?ion|traducido)(-|$|\.) ]]; then
        [[ -z "$ES" ]] && ES="$f"
      else
        [[ -z "$EN" ]] && EN="$f"
      fi
    done < <(find "$DIR_EP" -maxdepth 2 -type f \( -name '*.txt' -o -name '*.md' -o -name '*.srt' -o -name '*.vtt' \) | sort)

    [[ -n "$EN" ]] && { echo "    original    <- $(basename "$EN")";   ejecutar cp "$EN" "$DEST/transcripciones/original.en.md"; }
    [[ -n "$ES" ]] && { echo "    traducción  <- $(basename "$ES")";   ejecutar cp "$ES" "$DEST/transcripciones/traduccion.es.md"; }

    # --- thumbnail ----------------------------------------------
    IMG="$(find "$DIR_EP" -maxdepth 1 -type f \( -name '*.jpg' -o -name '*.jpeg' -o -name '*.png' -o -name '*.webp' \) | sort | head -1)"
    if [[ -n "$IMG" ]]; then
      echo "    thumbnail   <- $(basename "$IMG")"
      ejecutar cp "$IMG" "$DEST/thumbnail.${IMG##*.}"
    fi

    # --- audio de TTS (carpeta con varios audios) ---------------
    while IFS= read -r sub; do
      N="$(find "$sub" -maxdepth 1 -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.m4a' \) | wc -l)"
      if (( N > 1 )); then
        echo "    tts/        <- $(basename "$sub")/ ($N clips, no se versiona)"
        if (( APLICAR )); then
          find "$sub" -maxdepth 1 -type f \( -name '*.wav' -o -name '*.mp3' -o -name '*.m4a' \) \
            -exec cp {} "$DEST/tts/" \;
        else
          echo "    [simulado] cp $sub/*.{wav,mp3,m4a} $DEST/tts/"
        fi
      fi
    done < <(find "$DIR_EP" -mindepth 1 -maxdepth 1 -type d)

    # --- audio y vídeo finales (sueltos en la raíz) -------------
    while IFS= read -r a; do
      echo "    audio/      <- $(basename "$a") (no se versiona)"
      ejecutar cp "$a" "$DEST/audio/"
    done < <(find "$DIR_EP" -maxdepth 1 -type f \( -name '*.mp3' -o -name '*.wav' \) | sort)

    while IFS= read -r v; do
      echo "    video/      <- $(basename "$v") (no se versiona)"
      ejecutar cp "$v" "$DEST/video/"
    done < <(find "$DIR_EP" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.mov' \) | sort)

    # --- metadata -----------------------------------------------
    if [[ ! -f "$DEST/metadata.json" ]]; then
      echo "    metadata.json (rellénalo después)"
      if (( APLICAR )); then
        python3 - "$RAIZ/plantillas/episodio/metadata.json" "$DEST/metadata.json" "$SLUG" "$ANIO" "$NOMBRE" <<'PY'
import json, sys
plantilla, destino, slug, anio, nombre = sys.argv[1:6]
with open(plantilla, encoding="utf-8") as f:
    meta = json.load(f)
meta.update(slug=slug, anio=int(anio), titulo_original=nombre)
with open(destino, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
      fi
      (( APLICAR )) || true
    fi
    (( APLICAR )) && cp -n "$RAIZ/plantillas/episodio/NOTAS.md" "$DEST/NOTAS.md" 2>/dev/null || true
  done
done

echo
echo "episodios detectados: $TOTAL"
if (( APLICAR )); then
  echo "hecho. Ahora: rellena los metadata.json y ejecuta  python3 scripts/indice.py"
else
  echo "nada copiado. Repite con --aplicar cuando el reparto de arriba te cuadre."
fi
