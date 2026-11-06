from common import *
import difflib
eps=load_all()
big=eps['2019/052-rich']; BF=frases(big)
print('052 bloques',len(big['contenido']),'frases',len(BF),'chars',sum(len(t) for _,_,t in BF), 'min~',sum(len(t) for _,_,t in BF)/14.6/60)
small={k:v for k,v in eps.items() if k.startswith('2019/') and 1<=num(k)<=50}
print('cortos disponibles',len(small))
pool={}
for k,v in small.items():
    for _,s,t in frases(v): pool.setdefault((voz(s),norm(t)),[]).append(k)
ex=nm=0;exch=nmch=0;dch=0;d=0;tot=len(BF)
for _,s,t in BF:
    key=(voz(s),norm(t))
    if key in pool: nm+=1; nmch+=len(t)
    else: d+=1; dch+=len(t)
print(f'frase a frase (voz+texto normalizado, en cualquier corto): coincide {nm}/{tot} ({100*nm/tot:.1f}%) chars {nmch}; distintas {d} chars {dch}')
# por corto: porcentaje de frases del corto presentes en 052
tn=set((voz(s),norm(t)) for _,s,t in BF)
print('\nCorto: frases, %en 052 (exacta norm), %chars')
rows=[]
for k,v in sorted(small.items()):
    F=frases(v); inn=[(voz(s),norm(t)) in tn for _,s,t in F]
    ch=sum(len(t) for _,_,t in F); chin=sum(len(t) for (_,_,t),i in zip(F,inn) if i)
    rows.append((k,len(F),100*sum(inn)/len(F),100*chin/ch,ch))
    print(f'{k:40s} {len(F):4d} {100*sum(inn)/len(F):5.1f}% {100*chin/ch:5.1f}%')
print('total corto chars',sum(r[4] for r in rows),' chars cubiertos',sum(r[3]*r[4]/100 for r in rows))
# casi idénticas: ratio texto
import itertools
# cobertura aproximada via ratio >=0.9 para las no exactas
smallp={}
for k,v in small.items():
    for _,s,t in frases(v): smallp.setdefault(voz(s),[]).append(norm(t))
approx=0;apch=0;remain=[]
for _,s,t in BF:
    if (voz(s),norm(t)) in pool: continue
    n=norm(t); best=0
    for c in smallp.get(voz(s),[]):
        if abs(len(c)-len(n))>0.3*len(n): continue
        r=difflib.SequenceMatcher(None,n,c).quick_ratio()
        if r<0.9: continue
        r=difflib.SequenceMatcher(None,n,c).ratio()
        if r>best: best=r
        if best>=0.9: break
    if best>=0.9: approx+=1;apch+=len(t)
    else: remain.append(len(t))
print(f'casi idénticas (ratio>=0.9) entre las no exactas: {approx} frases, {apch} chars; realmente distintas {len(remain)} frases, {sum(remain)} chars')
# bloque a bloque
sb=set()
for k,v in small.items():
    for b in v['contenido']: sb.add((voz(b['speaker']),tuple(norm(f) for f in b['frases'] if f.strip())))
bi=sum(1 for b in big['contenido'] if (voz(b['speaker']),tuple(norm(f) for f in b['frases'] if f.strip())) in sb)
print('bloques del 052 idénticos (voz+frases) a un bloque de un corto:',bi,'/',len(big['contenido']))
# bloque con todas sus frases presentes
full=0;fch=0
for b in big['contenido']:
    fs=[f for f in b['frases'] if f.strip()]
    if all((voz(b['speaker']),norm(f)) in pool for f in fs): full+=1;fch+=sum(len(f) for f in fs)
print('bloques del 052 cuyas frases existen todas en algún corto:',full,'/',len(big['contenido']),'chars',fch)
