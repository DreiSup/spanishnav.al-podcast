"""Uso: python3 calibrar_tope.py registro_tts.jsonl [...]  (los de Drive: naval-podcast/transcripts/<año>/<ep>/registro_tts.jsonl)
Mide, por frase, caracteres/segundo reales y compara con el tope de pasos vigente (12,5*(c/7+3)). Sirve para fijar un
tope más ajustado (p. ej. p99,9 de la duración por carácter) y para contar reintentos reales."""
import json,sys,statistics as st
BORDE_FINAL=0.0
dur=[];ch=[];reint=[];ep_reint={};nfr=0
for f in sys.argv[1:]:
    n=0
    for l in open(f,encoding='utf-8'):
        if not l.strip(): continue
        r=json.loads(l); fr=r['frases']
        for i,d in enumerate(fr):
            nfr+=1; n+=d.get('intentos',1)-1
            if i+1<len(fr) and 'inicio_s' in d and 'inicio_s' in fr[i+1]:
                dd=fr[i+1]['inicio_s']-d['inicio_s']-0.12   # menos el hueco; aproximado
                if dd>0.3: dur.append(dd); ch.append(len(d['texto']))
    ep_reint[f]=n
print('frases',nfr,'reintentos por episodio',ep_reint)
r=[c/d for c,d in zip(ch,dur)]; r.sort()
q=lambda p:r[int(p*(len(r)-1))]
print('cps p0.1/p1/p50/p99/p99.9 =',[round(q(p),1) for p in (.001,.01,.5,.99,.999)])
tope_c=lambda c:(c/7+3)
sob=[tope_c(c)/d for c,d in zip(ch,dur)]
print('tope/duración real: mediana',round(st.median(sob),2),'mínimo',round(min(sob),2))
