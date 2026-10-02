#!/bin/bash
# uso: scripts/transcripts/verificar.sh NNN  -> valida la salida de un episodio y muestra tamaños y título
cd /home/user/spanishnav.al-podcast || exit 1
N=$1; D=trabajo/transcripts/$N
ls $D | grep -v -E '\.(txt|json)$' && echo "FALTA  archivos extra"
[ "$(ls $D | wc -l)" = 3 ] || { echo "FALTA  no hay 3 archivos"; ls $D; }
B=$(ls $D/*_es.json | sed 's#.*/##; s#_es\.json$##')
python3 scripts/transcripts/validate.py $D/$B.json --formato 0 | tail -1
python3 scripts/transcripts/validate.py $D/${B}_es.json --formato 5 | tail -1
cmp $D/$B.txt trabajo/transcripts/troceo/${N}_*.txt && echo "OK  txt identico al troceo"
python3 - "$D/$B" <<'PY'
import json,sys
b=sys.argv[1]; e=json.load(open(b+'.json')); s=json.load(open(b+'_es.json'))
ok=[t['speaker'] for t in e['contenido']]==[t['speaker'] for t in s['contenido']] and len(e['titulos_seccion'])==len(s['titulos_seccion'])
print(("OK" if ok else "FALTA")+"  turnos y titulos alineados en/es")
PY
echo "TITULO: $(grep -v '^\s*$' $D/$B.txt | sed -n 2p)"
echo "BASE: $B"
wc -c $D/$B.txt $D/$B.json $D/${B}_es.json | head -3
