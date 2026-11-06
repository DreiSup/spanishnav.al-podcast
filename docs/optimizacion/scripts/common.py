import json,re,glob,os,unicodedata
R='/home/user/spanishnav.al-podcast'
def norm(s):
    s=unicodedata.normalize('NFKC',s).lower()
    s=re.sub(r'[^\w\s]',' ',s); return re.sub(r'\s+',' ',s).strip()
def load_all():
    eps={}
    for p in sorted(glob.glob(R+'/episodios/*/*/transcript.es.json')):
        d=os.path.dirname(p); key=d.split('episodios/')[1]
        j=json.load(open(p)); 
        if j.get('contenido'): eps[key]=j
    return eps
def num(key): 
    m=re.search(r'/(\d{3})-',key); return int(m.group(1)) if m else None
def frases(j): return [(b['id'],b['speaker'],f.strip()) for b in j['contenido'] for f in b['frases'] if f.strip()]

CFG=json.load(open(R+'/fabrica/voces.json'))
def voz(sp):
    n=re.sub(r"\s+"," ",sp.strip().lower()); return CFG['alias'].get(n,n)
