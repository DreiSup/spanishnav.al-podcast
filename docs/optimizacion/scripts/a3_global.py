from common import *
from collections import defaultdict,Counter
eps=load_all(); cj=json.load(open(R+'/cortos.json'))
cortos=set(c for v in cj['grupos'].values() for c in v)
base={k:v for k,v in eps.items() if k not in cortos and num(k)!=52}
print('episodios totales',len(eps),'base (sin cortos de largos ni 052)',len(base))
def chars(d): return sum(len(t) for v in d.values() for _,_,t in frases(v))
print('chars totales',chars(eps),'min',chars(eps)/14.6/60,'; base',chars(base),'min',chars(base)/14.6/60)
cnt=Counter();first={};chs={}
occ=defaultdict(list)
for k,v in base.items():
    for _,s,t in frases(v):
        key=(voz(s),norm(t)); cnt[key]+=1; occ[key].append(k); chs[key]=len(t)
dupfr=sum(c-1 for c in cnt.values() if c>1); dupch=sum((c-1)*chs[k] for k,c in cnt.items() if c>1)
tot=sum(cnt.values()); totch=sum(c*chs[k] for k,c in cnt.items())
print(f'base: frases {tot}, duplicadas (copias extra) {dupfr} ({100*dupfr/tot:.1f}%), chars extra {dupch} ({100*dupch/totch:.2f}%) = {dupch/14.6/60:.1f} min')
# misma frase en el mismo episodio vs entre episodios
inter=0;interch=0
for k,c in cnt.items():
    eps_set=set(occ[k])
    if len(eps_set)>1:
        # copias extra entre episodios = nº de episodios-1 (primer episodio genera)
        inter+= len(eps_set)-1; interch+=(len(eps_set)-1)*chs[k]
print('copias extra entre episodios distintos (1ª aparición por episodio cuenta):',inter,'chars',interch,f'{interch/14.6/60:.1f} min')
# reutilizables dentro de un mismo episodio (misma voz)? 
print('\nTop 25 frases repetidas (voz, texto, veces, episodios):')
for k,c in sorted(cnt.items(),key=lambda x:-x[1]*len(x[0][1]))[:25]:
    if c>1: print(c,len(set(occ[k])),k[0],'|',k[1][:90])
# por longitud: repeticiones de frases cortas (<=25 chars) vs largas
sh=sum((c-1) for k,c in cnt.items() if c>1 and chs[k]<=25); lg=dupfr-sh
print('\nduplicadas cortas (<=25 chars):',sh,' mayores:',lg)
# frases de <=12 chars totales
print('histograma de chars de las copias extra:')
b=Counter()
for k,c in cnt.items():
    if c>1: 
        L=chs[k]; b['<=15' if L<=15 else '<=40' if L<=40 else '<=100' if L<=100 else '>100']+=(c-1)*L
print(dict(b))
# mismo analisis pero incluyendo TODO (con cortos) para ver solapamiento
# vecinos: nivi intros
