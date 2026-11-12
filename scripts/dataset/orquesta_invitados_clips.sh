#!/usr/bin/env bash
# Parte 2e: asignación de etiquetas externas (aprobada por el autor, 2026-11-12), medición (08) y montaje (09)
# de vitalik, qureshi, hodak, rauch y scholl. En serie: una etapa pesada a la vez.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
paso() { echo "[$(date +%H:%M:%S)] ### $*"; }
etapa() { ./etapa.sh "$@" || { paso "PARADA: falló $*"; exit 1; }; }
asig() { local id=$1; shift; local a=(); for x in "$@"; do a+=(--asignar "$x"); done; paso "06 $id"; etapa 06_hablantes.py "$id" "${a[@]}"; }
asig lex080 T0_SPEAKER_01=vitalik T1_SPEAKER_00=vitalik T0_SPEAKER_00=descartado T1_SPEAKER_01=descartado
asig wsh104 T0_SPEAKER_00=qureshi T0_SPEAKER_01=qureshi T1_SPEAKER_01=qureshi T0_SPEAKER_02=descartado T1_SPEAKER_00=descartado
asig cmm009 SPEAKER_00=hodak SPEAKER_01=descartado
asig npr001 SPEAKER_00=hodak SPEAKER_01=descartado
asig acq001 SPEAKER_02=rauch SPEAKER_00=descartado SPEAKER_01=descartado
asig evr047 SPEAKER_02=rauch SPEAKER_00=descartado SPEAKER_01=descartado
asig hii153 SPEAKER_00=scholl SPEAKER_01=descartado
asig cwt277 SPEAKER_01=scholl SPEAKER_00=descartado
dataset() { local h=$1 train=$2 ev=$3 m=$4
  paso "08 $h train $train"; etapa 08_clips.py "$h" $train
  paso "08 $h eval $ev"; etapa 08_clips.py "$h" "$ev" $m
  paso "09 $h"; ./prueba.sh 09_montar.py "$h" || { paso "PARADA: falló 09 $h"; exit 1; }
}
dataset vitalik "nav135 lex080" nav136 "--muestra-min 4"
dataset qureshi "nav135 wsh104" nav136 ""
dataset hodak   "nav167 cmm009" npr001 "--muestra-min 4"
dataset rauch   "nav167 acq001" evr047 "--muestra-min 4"
dataset scholl  "nav167 hii153" cwt277 "--muestra-min 4"
paso "FIN invitados clips"
