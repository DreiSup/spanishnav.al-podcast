"""Simula el coste relativo de Qwen (pasos de decodificación ponderados por tamaño de lote) con distintas
estrategias de agrupación, usando los transcript.es.json del repo. Sin GPU."""
import glob, json, sys, random, re
sys.path.insert(0, "/home/user/spanishnav.al-podcast/fabrica")
import fabrica as F

cfg = F.cargar_config()
random.seed(0)
episodios = []
for p in sorted(glob.glob('/home/user/spanishnav.al-podcast/episodios/*/*/transcript.es.json')):
    t = json.load(open(p))
    try:
        plan = F.plan_episodio(t, cfg)
    except ValueError:
        continue
    episodios.append(plan)

CPS = 15.0  # caracteres por segundo (resumen_plan)
def pasos_reales(txt, ruido):
    return 12.5 * len(txt) / CPS * ruido

# ruido fijo por frase (misma "duración real" en todas las estrategias)
RUIDO = {}
def r(txt):
    if txt not in RUIDO:
        RUIDO[txt] = random.lognormvariate(0, 0.15)
    return RUIDO[txt]

def lotes_iguales(frases, lote):
    orden = sorted(frases, key=len)
    if not orden: return []
    tam = -(-len(orden) // -(-len(orden) // lote))
    return [orden[g:g + tam] for g in range(0, len(orden), tam)]

def coste(lotes, beta, prefill=0.0):
    """coste = sum(max_pasos * (1 + beta*(B-1))) + prefill por lote (en pasos equivalentes)."""
    c = 0.0
    for l in lotes:
        c += max(pasos_reales(t, r(t)) for t in l) * (1 + beta * (len(l) - 1)) + prefill
    return c

def estrategia(nombre, lote, cruzar):
    res = []
    for plan in episodios:
        if cruzar:
            porvoz = {}
            for p in plan:
                porvoz.setdefault(p["voz"], []).extend(p["frases"])
            grupos = list(porvoz.values())
        else:
            grupos = [p["frases"] for p in plan]
        ls = []
        for g in grupos:
            ls += lotes_iguales(g, lote)
        res.append(ls)
    return res

audio = sum(pasos_reales(t, r(t)) for plan in episodios for p in plan for t in p["frases"])
print(f"{len(episodios)} episodios, {sum(len(p['frases']) for pl in episodios for p in pl)} frases, "
      f"{audio/12.5/60:.0f} min de audio estimados")
casos = [("frase a frase", 1, False), ("actual: intervención, lote 8", 8, False),
         ("intervención, lote 16", 16, False),
         ("misma voz en el episodio, lote 8", 8, True), ("misma voz, lote 16", 16, True),
         ("misma voz, lote 24", 24, True), ("misma voz, lote 32", 32, True)]
for beta in (0.0, 0.03, 0.08):
    print(f"\nbeta={beta} (coste marginal por frase extra en el lote, relativo a un paso de lote 1); "
          f"prefill = 3 pasos por lote")
    base = None
    for nombre, lote, cruzar in casos:
        ls = estrategia(nombre, lote, cruzar)
        c = sum(coste(l, beta, prefill=3.0) for l in ls)
        nl = sum(len(l) for l in ls)
        tam_medio = sum(len(x) for l in ls for x in l) / nl
        relleno = sum(sum(max(pasos_reales(t, r(t)) for t in x) * len(x) - sum(pasos_reales(t, r(t)) for t in x)
                          for x in l) for l in ls) / sum(max(pasos_reales(t, r(t)) for t in x) * len(x) for l in ls for x in l)
        if nombre.startswith("actual"):
            base = c
        print(f"  {nombre:36s} lotes={nl:6d} tamaño medio={tam_medio:5.2f} relleno={relleno:5.1%} "
              f"coste/audio={c/audio:6.3f}" + (f"  vs actual={c/base:6.1%}" if base else ""))
# distribución de tamaños de lote actuales
from collections import Counter
cnt = Counter(len(x) for l in estrategia("a", 8, False) for x in l)
print("\nTamaños de lote actuales (lotes):", sorted(cnt.items()))
fr = Counter()
for l in estrategia("a", 8, False):
    for x in l: fr[len(x)] += len(x)
print("Frases según el tamaño del lote en que van:", sorted(fr.items()))
