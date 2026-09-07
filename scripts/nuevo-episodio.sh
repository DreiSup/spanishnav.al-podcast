#!/usr/bin/env bash
# Crea la carpeta de un episodio con los cuatro .json de plantillas/episodio.
#
#   ./scripts/nuevo-episodio.sh 2019 7 how-to-get-rich "How to Get Rich"
#
# Normalmente los episodios los crea el descargador de nav.al; este script es
# para darlos de alta a mano.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 3 ]]; then
  echo "uso: $0 <anio> <numero> <slug> [titulo original]" >&2
  echo "ej.: $0 2019 7 how-to-get-rich \"How to Get Rich\"" >&2
  exit 1
fi

ANIO="$1"; NUMERO="$2"; SLUG="$3"; TITULO="${4:-}"

[[ "$ANIO"   =~ ^[0-9]{4}$ ]] || { echo "error: el año debe tener 4 dígitos (recibido: $ANIO)" >&2; exit 1; }
[[ "$NUMERO" =~ ^[0-9]+$   ]] || { echo "error: el número debe ser entero (recibido: $NUMERO)" >&2; exit 1; }
[[ "$SLUG"   =~ ^[a-z0-9-]+$ ]] || { echo "error: el slug solo admite minúsculas, números y guiones (recibido: $SLUG)" >&2; exit 1; }

NNN="$(printf '%03d' "$NUMERO")"
DESTINO="$RAIZ/episodios/$ANIO/$NNN-$SLUG"
[[ -e "$DESTINO" ]] && { echo "error: ya existe $DESTINO" >&2; exit 1; }

mkdir -p "$DESTINO"
cp "$RAIZ"/plantillas/episodio/*.json "$DESTINO/"

python3 - "$DESTINO" "$ANIO" "$NUMERO" "$SLUG" "$TITULO" <<'PY'
import json, sys
from datetime import date
from pathlib import Path

destino, anio, numero, slug, titulo = sys.argv[1:6]
destino, anio, numero = Path(destino), int(anio), int(numero)
episodio = f"{anio}/{numero:03d}-{slug}"


def parchear(nombre, cambios):
    ruta = destino / nombre
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    datos.update(cambios)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


comun = {"episodio": episodio, "titulo": titulo}
parchear("transcript.en.json", comun)
parchear("transcript.es.json", {"episodio": episodio, "titulo": ""})
parchear("metadata.en.json", {
    "numero": numero, "anio": anio, "slug": slug, "titulo": titulo,
    "descargado_el": date.today().isoformat(),
})
parchear("metadata.es.json", {"numero": numero, "anio": anio, "slug": slug})
PY

echo "creado: episodios/$ANIO/$NNN-$SLUG"
echo
echo "siguientes pasos:"
echo "  1. rellena transcript.en.json (una frase por entrada, con id correlativo)"
echo "  2. traduce a transcript.es.json conservando los MISMOS ids"
echo "  3. crea la carpeta del episodio en Drive y anota los IDs en metadata.es.json"
echo "  4. python3 scripts/indice.py"
