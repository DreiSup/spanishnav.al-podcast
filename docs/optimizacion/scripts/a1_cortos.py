from common import *
eps=load_all(); print(len(eps),'con es')
cj=json.load(open(R+'/cortos.json'))
tot=dict(chars_long=0)
res=[]
for largo,cortos in cj['grupos'].items():
    if largo not in eps: print('largo sin es',largo); continue
    L=eps[largo]; LF=frases(L); Lnorm=[(voz(s),norm(t)) for _,s,t in LF]
    Lblocks=[(voz(b['speaker']),tuple(norm(f) for f in b['frases'] if f.strip())) for b in L['contenido']]
    lchars=sum(len(t) for _,_,t in LF)
    print('\n==',largo,'bloques',len(L['contenido']),'frases',len(LF),'chars',lchars)
    sumch=0;sumbl=0;ident=0;casi=0;dist=0;blk_id=0;blk_tot=0;nfr=0;present=0
    pos=0
    for c in cortos:
        if c not in eps: continue
        present+=1
        C=eps[c]; CF=frases(C); nfr+=len(CF)
        ch=sum(len(t) for _,_,t in CF); sumch+=ch
        # frase a frase: busqueda hacia delante en el largo (misma voz, texto exacto / normalizado)
        exact=set(t for _,_,t in LF); nexact=0; nnorm=0; nd=0; dch=0
        p=pos; last=pos
        # secuencial greedy ventana
        for _,s,t in CF:
            tn=norm(t); found=None
            for q in range(p,min(p+400,len(Lnorm))):
                if Lnorm[q]==(voz(s),tn): found=q;break
            if found is not None:
                if LF[found][2]==t: nexact+=1
                else: nnorm+=1
                p=found+1
            else: nd+=1; dch+=len(t)
        pos=p
        ident+=nexact;casi+=nnorm;dist+=nd
        # bloques
        cb=[(voz(b['speaker']),tuple(norm(f) for f in b['frases'] if f.strip())) for b in C['contenido']]
        bi=sum(1 for x in cb if x in Lblocks); blk_id+=bi; blk_tot+=len(cb)
        spk_ok = all(s in {x[0] for x in Lblocks} for s,_ in cb)
        flag='' if nd==0 else ' <<'
        print(f'{c:34s} fr={len(CF):4d} exact={nexact:4d} norm={nnorm:3d} dist={nd:3d} bloques_ident={bi}/{len(cb)}{flag}')
    print(f'TOTAL cortos presentes {present}/{len(cortos)} frases={nfr} exact={ident} norm={casi} dist={dist}; chars cortos={sumch} vs largo={lchars}; bloques ident {blk_id}/{blk_tot}')
