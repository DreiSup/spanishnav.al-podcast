from common import *
import random, statistics as st, math
from collections import defaultdict
sys_asign=__import__('sys')
sys_asign.path.insert(0,R+'/fabrica')
eps=load_all(); cj=json.load(open(R+'/cortos.json'))
cortos=set(c for v in cj['grupos'].values() for c in v)
base={k:v for k,v in eps.items() if k not in cortos and num(k)!=52}
# voz asignada con la regla de Kapil
def plan(j):
    sp={b['speaker'] for b in j['contenido']}; v={s:voz(s) for s in sp}
    if 'kapil' in set(v.values()):
        v={s:('naval_kapil' if x=='naval' else x) for s,x in v.items()}
    return [(v[b['speaker']],[f.strip() for f in b['frases'] if f.strip()]) for b in j['contenido']]
CPS=14.6
def steps(t,noise=None): 
    s=len(t)/CPS*12.5
    return s*noise() if noise else s
def tam_de(n,lote): return -(-n // -(-n // lote))
def cost_blocks(blocks,lote,noise=None):
    """blocks: lista de listas de longitudes (steps). Devuelve (batches, sum_max, sum_len, padded)"""
    nb=0;sm=0;sl=0;pad=0
    for b in blocks:
        o=sorted(b); tam=tam_de(len(o),lote)
        for g in range(0,len(o),tam):
            ch=o[g:g+tam]; m=max(ch); nb+=1; sm+=m; sl+=sum(ch); pad+=len(ch)*m-sum(ch)
    return nb,sm,sl,pad
def run(lote,seed=0,sigma=0.0):
    rnd=random.Random(seed)
    noise=(lambda: math.exp(rnd.gauss(0,sigma))) if sigma else None
    L=defaultdict(list)   # por voz, global
    S0=[0,0,0,0];S1=[0,0,0,0]
    glob=defaultdict(list)
    for k,j in base.items():
        pv=defaultdict(list)
        blocks=[]
        for v,fs in plan(j):
            ls=[steps(t,noise) for t in fs]; blocks.append(ls); pv[v]+=ls; glob[v]+=ls
        a=cost_blocks(blocks,lote)
        b=cost_blocks(list(pv.values()),lote)
        for i in range(4): S0[i]+=a[i];S1[i]+=b[i]
    S2=[0,0,0,0]
    c=cost_blocks(list(glob.values()),lote)
    return S0,S1,c
allfr=[len(t) for k,j in base.items() for v,fs in plan(j) for t in fs]
allfr.sort()
print('frases base',len(allfr),'chars media',st.mean(allfr),'mediana',st.median(allfr),'p10/p90/p99/max',allfr[len(allfr)//10],allfr[9*len(allfr)//10],allfr[99*len(allfr)//100],allfr[-1])
import collections
bk=collections.Counter(min(l//50*50,400) for l in allfr)
print('histograma chars (tramos de 50):',sorted(bk.items()))
bl=[len(fs) for k,j in base.items() for v,fs in plan(j)]
print('bloques',len(bl),'frases/bloque media',st.mean(bl),'mediana',st.median(bl),'<=3:',sum(1 for x in bl if x<=3)/len(bl),'<=8:',sum(1 for x in bl if x<=8)/len(bl))
print('bloques con 1 frase:',sum(1 for x in bl if x==1))
# distribución de tamaño de lote actual
tams=[]
for k,j in base.items():
    for v,fs in plan(j):
        n=len(fs); t=tam_de(n,8); 
        left=n
        while left>0: tams.append(min(t,left)); left-=t
print('lotes actuales:',len(tams),'tamaño medio',st.mean(tams), 'distribución',sorted(collections.Counter(tams).items()))
for lote in (8,12,16):
  for sigma in (0.0,0.15):
    S0,S1,S2=run(lote,0,sigma)
    f=lambda S:f'lotes={S[0]:5d} Σmax={S[1]/12.5/60:7.1f} min-audio-eq  relleno={100*S[3]/(S[3]+S[2]):5.1f}%'
    print(f'lote={lote} ruido={sigma}:\n   actual(por intervención): {f(S0)}\n   por voz y episodio      : {f(S1)}  ahorro Σmax {100*(1-S1[1]/S0[1]):.1f}%\n   por voz, todos los episod: {f(S2)}  ahorro Σmax {100*(1-S2[1]/S0[1]):.1f}%')

print('\n--- referencia: lotes SIN ordenar por longitud (frases consecutivas de la intervención) ---')
nb=sm=sl=pad=0
for k,j in base.items():
    for v,fs in plan(j):
        ls=[steps(t) for t in fs]; tam=tam_de(len(ls),8)
        for g in range(0,len(ls),tam):
            ch=ls[g:g+tam]; m=max(ch); nb+=1; sm+=m; sl+=sum(ch); pad+=len(ch)*m-sum(ch)
print(f'lotes={nb} Σmax={sm/12.5/60:.1f} relleno={100*pad/(pad+sl):.1f}%')
# modelo de coste: lineal en B (cada elemento paddeado cuesta igual) vs plano (coste por paso independiente de B)
S0,S1,S2=run(8,0,0.0)
lin=lambda S:(S[2]+S[3])
print('Modelo lineal (coste ∝ elementos×pasos): ahorro por voz+episodio %.1f%%, por voz global %.1f%%'%(100*(1-lin(S1)/lin(S0)),100*(1-lin(S2)/lin(S0))))
print('Modelo plano (coste ∝ Σ max): %.1f%% y %.1f%%'%(100*(1-S1[1]/S0[1]),100*(1-S2[1]/S0[1])))
# modelo mixto t(B)=a+bB con a=b*4 (parte fija = 4 elementos)
for a in (2,4,8):
    cost=lambda blocks_info: None
