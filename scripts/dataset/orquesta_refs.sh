#!/usr/bin/env bash
# Orquesta la Fase 1a (clips de referencia) de principio a fin, en serie.
#   Bloque 1: fuentes de la criba (nav109, nav072, nav056) -> candidatos de naval, nivi,
#             brett, naval_kapil y kapil.
#   Bloque 2: resto de fuentes -> candidatos de deutsch, vitalik, ridley, hodak, rauch,
#             scholl y qureshi.
# Cada etapa se salta si su salida ya existe, así que relanzarlo continúa donde se quedó.
# Si una etapa se abandona, el orquestador para y lo deja escrito en el log.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
etapa() { ./etapa.sh "$@" || { paso "PARADA: falló $*"; exit 1; }; }

esperar_asr() {
  until [ -f "$HOME/naval-datos/trabajo/$1/asr.json" ]; do sleep 30; done
}

bloque() {  # bloque <ids...> -- <hablantes...>
  local ids=() habl=() d=0
  for x in "$@"; do
    if [ "$x" = "--" ]; then d=1; elif [ $d -eq 0 ]; then ids+=("$x"); else habl+=("$x"); fi
  done
  for id in "${ids[@]}"; do
    paso "ASR $id"; esperar_asr_o_lanzar "$id"
    paso "alinear $id"; etapa 03_alinear.py "$id"
    paso "diarizar $id"; etapa 04_diarizar.py "$id"
  done
  for id in "${ids[@]}"; do
    paso "hablantes $id"; etapa 06_hablantes.py "$id"
  done
  paso "candidatos ${habl[*]}"; etapa 07_candidatos_ref.py "${habl[@]}"
}

esperar_asr_o_lanzar() {
  if pgrep -f "02_asr.py $1" >/dev/null; then esperar_asr "$1"; else etapa 02_asr.py "$1"; fi
}

paso "INICIO orquesta_refs"
bloque nav109 nav072 nav056 -- naval nivi brett naval_kapil kapil
paso "BLOQUE 1 TERMINADO"
bloque nav139 nav135 nav074 nav167 -- deutsch vitalik ridley hodak rauch scholl qureshi
paso "hablantes --global"; etapa 06_hablantes.py --global
paso "FIN orquesta_refs"
