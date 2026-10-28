#!/usr/bin/env python3
"""Etapa 6: quién habla en cada tramo (hablantes.json + emb/).

Entrada (por episodio): trabajo/<id>/palabras.json, diar.json, audio16k.wav y
oficiales/<id>.json. Pasos:
  1. Etiqueta de diarización por palabra (la de `exclusivo` en el punto medio) y marca
     `solape` (palabra a ±0,1 s de un intervalo de `solapes`).
  2. Hablante oficial por palabra, comprobación cruzada con alineado LOCAL (los Docs
     pueden estar reordenados, ser parciales o recopilatorios): índice de 4-gramas del
     transcript oficial, voto por diagonal para hallar la ventana de cada trozo de ASR y
     difflib solo dentro de esa ventana. Solo las palabras en bloques iguales (>=2)
     reciben hablante oficial; el resto es `null` (sin cobertura).
  3. ECAPA (speechbrain/spkrec-ecapa-voxceleb, SIEMPRE en CPU) sobre tramos exclusivos sin
     solape de >=3 s (recortados a 10 s): un centroide por etiqueta. Se lee el audio por
     ventanas con seek, nunca el episodio entero.
  4. Etiqueta -> hablante por voto ponderado por palabras con hablante oficial. Etiquetas de
     trozos distintos (T0_..., T1_...) se unen por coseno de centroides (nunca dentro del
     mismo trozo). Estados:
       ok         acuerdo >= 0,8 con >= 200 palabras con cobertura y, si existe centroide
                  global del hablante de OTRO episodio, coseno >= 0,55. Que el hablante no sea
                  de los `hablantes` esperados del episodio solo añade un aviso;
       dudoso     cualquier otro caso con algo de evidencia (hay que preguntar al usuario);
       descartado < 30 s de habla o sin evidencia.
  5. Tramos: rachas de palabras consecutivas con la misma etiqueta `ok`, sin solape y sin
     hueco interno > 1,5 s. Por tramo: sim (coseno ECAPA del tramo contra el centroide del
     hablante, si dura >= 1,5 s), n_off, n_desacuerdo. Desacuerdo > 20 % de n_off ->
     descartado; n_off == 0 -> sin_cobertura (solo vale con sim >= 0,65).
     Además un tramo se descarta si su sim < umbral_cos (motivo sim_baja), si su peor ventana
     de 10 s < umbral_vent (sim_baja_ventana; se guarda `sim_min`), si es >1,5 s y no tiene
     sim (sin_sim) o si tiene poca cobertura oficial (n_off < 30 % de sus palabras) y
     sim < umbral_alto. Los tramos se cortan también cuando, en un hueco >0,2 s entre dos
     palabras suyas, hay >=0,15 s de solape o de turno de otra etiqueta (p. ej. un "mm-hm"
     que Whisper omite).
     Varias etiquetas ok del mismo hablante: con 2, si suenan distinto, ambas pasan a dudosas;
     con 3 o más, solo la que se aparta de la media ponderada de las demás.
     w0/w1 son el campo `i` de la primera y de la ULTIMA palabra del tramo (ambos inclusive).

Salidas:
  trabajo/<id>/hablantes.json        formato del CONTRATO (con campos extra: votos, motivo,
                                     params, stats; no estorban a los lectores)
  trabajo/<id>/emb06.npz             caché de embeddings POR VENTANA (t0, t1); se vuelca cada ~200
                                     ventanas, así un corte retoma donde iba; con ella --global y
                                     --asignar no necesitan ECAPA. Solo se embeben los tramos de
                                     etiquetas que pueden acabar ok (>= min_segundos o manuales)
  emb/<hablante>.npy                 centroide global (media normalizada de los centroides ok
                                     por fuente; cada fuente pesa igual). naval NO incluye nav072
  emb/naval_kapil.npy                Naval en nav072 (solo esa fuente). No se borran otros .npy
  emb/centroides.json                de qué fuentes y etiquetas sale cada uno
  emb/_por_fuente.npz                vector de cada (hablante, fuente) para el leave-one-out

`cos_global` de una etiqueta se mide contra el centroide de las OTRAS fuentes (no se
confirma a sí misma). Si no hay otra fuente, es null y el criterio no se aplica.

Imprime al final una tabla de etiquetas y un bloque DUDOSAS (con votos, instantes y texto)
para que el orquestador las consulte con el usuario. Se resuelven con:
    06_hablantes.py <id> --asignar SPEAKER_01=brett   (o =descartado)
(se guarda en trabajo/<id>/hablantes_manual.json y se recalcula desde la caché).

Uso: 06_hablantes.py <id> [--forzar] [--asignar ETIQ=hablante ...]
     06_hablantes.py --global
Pruebas: --datos DIR sustituye ~/naval-datos (trabajo/, oficiales/, emb/) sin tocar el real;
el modelo ECAPA se busca siempre en <NAVAL_DATOS>/modelos (--ecapa-dir para otro sitio).
Orden de escritura: centroides (emb/) primero y hablantes.json el último, porque su existencia
es lo que hace que la etapa se dé por hecha.
"""
import argparse
import bisect
import difflib
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

# Esta etapa NUNCA usa la GPU (hay un ASR largo en ella): ECAPA corre en CPU.
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np

import common
from common import candado_gpu, comprobar_recursos, escribir_json, leer_json, log

MODELO_ECAPA = "speechbrain/spkrec-ecapa-voxceleb"
ECAPA_DIR = common.DATOS / "modelos" / "spkrec-ecapa-voxceleb"   # respeta NAVAL_DATOS
SR = 16000
DIM = 192

GAP_TRAMO = 1.5        # hueco interno máximo de un tramo (s)
TOL_SOLAPE = 0.1       # margen alrededor de los solapes (s)
MIN_TRAMO_EMB = 1.5    # duración mínima de un tramo para calcular sim (s)
MIN_VENT_ETIQ = 3.0    # tramo exclusivo mínimo para el centroide de etiqueta (s)
MAX_VENT = 10.0        # recorte de las ventanas (s)
GAP_CORTE = 0.2        # hueco entre palabras a partir del cual se mira si hay otra voz (s)
MIN_CHOQUE = 0.15      # solape mínimo con otra voz dentro de ese hueco para cortar el tramo (s)
POCA_COB = 0.3         # n_off < POCA_COB * palabras del tramo: cobertura oficial pobre
CKPT_VENT = 200        # guardado parcial de la caché de embeddings cada tantas ventanas
CKPT_S = 180           # ... o cada tantos segundos
SOLO_KAPIL = ("nav072",)   # Naval en estas fuentes va a naval_kapil y no a naval
NGRAMA = 4
MAX_HITS_NGRAMA = 50   # 4-gramas más repetidos que esto no dan evidencia de posición
MIN_CHUNK_TOK = 25     # los segmentos ASR cortos se juntan hasta tener al menos esto
MAX_CHUNK_TOK = 120


# ----------------------------------------------------------------------------------------
# Rutas
# ----------------------------------------------------------------------------------------
class Rutas:
    def __init__(self, datos: Path):
        self.datos = Path(datos)
        self.emb = self.datos / "emb"

    def trabajo(self, fid):
        return self.datos / "trabajo" / fid

    def oficial(self, fid):
        return self.datos / "oficiales" / f"{fid}.json"


def unit(v):
    if v is None:
        return None
    n = float(np.linalg.norm(v))
    return None if n < 1e-9 else (v / n).astype(np.float32)


def media_unit(rows):
    """Media L2-normalizada de las filas finitas (None si no hay)."""
    if rows is None or len(rows) == 0:
        return None
    rows = rows[np.isfinite(rows).all(axis=1)]
    if len(rows) == 0:
        return None
    return unit(rows.mean(axis=0))


def centroide_robusto(rows):
    """Centroide de ventanas; con >=6 ventanas descarta las muy lejanas de la mediana
    (trozos mal diarizados) antes de promediar."""
    rows = rows[np.isfinite(rows).all(axis=1)]
    if len(rows) >= 6:
        c = unit(rows.mean(axis=0))
        cs = rows @ c
        keep = cs >= max(0.2, float(np.median(cs)) - 0.25)
        if keep.sum() >= 3:
            rows = rows[keep]
    return media_unit(rows)


def coseno(a, b):
    if a is None or b is None:
        return None
    return float(np.dot(a, b))


# ----------------------------------------------------------------------------------------
# 1. Etiqueta por palabra
# ----------------------------------------------------------------------------------------
def fusionar(intervalos):
    out = []
    for s, e in sorted(intervalos):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def etiquetar_palabras(ws, we, exclusivo, solapes):
    """(etiquetas, solape) por palabra. Búsqueda con bisect, sin bucles anidados."""
    iv = sorted((float(x["start"]), float(x["end"]), x["label"]) for x in exclusivo)
    starts = [x[0] for x in iv]
    pm, m = [], -1.0
    for x in iv:
        m = max(m, x[1])
        pm.append(m)
    ms_me = fusionar((float(x["start"]), float(x["end"])) for x in solapes)
    ms = [x[0] for x in ms_me]
    me = [x[1] for x in ms_me]
    etiq, sol = [], []
    for s, e in zip(ws, we):
        if s is None or e is None:
            etiq.append(None)
            sol.append(False)
            continue
        t = (s + e) / 2
        k = bisect.bisect_right(starts, t) - 1
        mejor, mejor_c, pasos = None, -1.0, 0
        while k >= 0 and pm[k] > t and pasos < 64:
            if iv[k][0] <= t < iv[k][1]:
                c = min(t - iv[k][0], iv[k][1] - t)  # en solape de trozos, el más central
                if c > mejor_c:
                    mejor, mejor_c = iv[k][2], c
            k -= 1
            pasos += 1
        etiq.append(mejor)
        j = bisect.bisect_right(ms, e + TOL_SOLAPE) - 1
        sol.append(j >= 0 and me[j] >= s - TOL_SOLAPE)
    return etiq, sol


# ----------------------------------------------------------------------------------------
# 2. Hablante oficial por palabra (alineado local)
# ----------------------------------------------------------------------------------------
def norm_tok(s: str) -> str:
    s = s.lower().replace("’", "").replace("‘", "").replace("'", "")
    return re.sub(r"[\W_]+", "", s)


def tokens_oficiales(turnos):
    vocab, ids, spk, nombres = {}, [], [], []
    for t in turnos:
        sp = t.get("speaker")
        if sp not in nombres:
            nombres.append(sp)
        si = nombres.index(sp)
        for raw in re.split(r"[\s—–]+", t.get("texto", "")):
            tk = norm_tok(raw)
            if tk:
                ids.append(vocab.setdefault(tk, len(vocab)))
                spk.append(si)
    return vocab, np.array(ids, dtype=np.int64), np.array(spk, dtype=np.int32), nombres


_PRIMOS = np.array([1000003, 998244353, 1000000007, 19260817], dtype=np.uint64)


def hash_ngramas(ids):
    """Hash uint64 de cada 4-grama (ids >= 0)."""
    a = ids.astype(np.uint64)
    with np.errstate(over="ignore"):
        return (a[:-3] * _PRIMOS[0] + a[1:-2] * _PRIMOS[1] + a[2:-1] * _PRIMOS[2]
                + a[3:] * _PRIMOS[3])


def trozos_asr(segs, tok):
    """Grupos de posiciones de palabra (con token) a alinear: segmentos ASR; los cortos se
    juntan hasta MIN_CHUNK_TOK y los largos se parten en MAX_CHUNK_TOK."""
    grupos, cur, ultimo = [], [], object()
    for i, sg in enumerate(segs):
        if not tok[i]:
            continue
        if cur and sg != ultimo and len(cur) >= MIN_CHUNK_TOK:
            grupos.append(cur)
            cur = []
        cur.append(i)
        ultimo = sg
    if cur:
        grupos.append(cur)
    out = []
    for g in grupos:
        if len(g) <= MAX_CHUNK_TOK:
            out.append(g)
        else:
            k = math.ceil(len(g) / (MAX_CHUNK_TOK * 0.8))
            tam = math.ceil(len(g) / k)
            out.extend(g[j:j + tam] for j in range(0, len(g), tam))
    return out


def alinear_oficial(palabras, oficial):
    """Devuelve (off, stats): off[i] = hablante oficial de la palabra i o None."""
    n = len(palabras)
    off = [None] * n
    toks = [norm_tok(w.get("w", "")) for w in palabras]
    segs = [w.get("seg", i // 60) for i, w in enumerate(palabras)]
    vocab, oids, ospk, nombres = tokens_oficiales(oficial.get("turnos", []))
    stats = {"tokens_oficiales": int(len(oids)), "trozos": 0, "trozos_alineados": 0}
    if len(oids) < NGRAMA or n == 0:
        return off, stats
    oh = hash_ngramas(oids)
    orden = np.argsort(oh, kind="stable")
    claves = oh[orden]
    for g in trozos_asr(segs, toks):
        stats["trozos"] += 1
        m = len(g)
        ids = np.array([vocab.get(toks[i], -1) for i in g], dtype=np.int64)
        if m < NGRAMA:
            continue
        valido = np.ones(m - NGRAMA + 1, dtype=bool)
        for k in range(NGRAMA):
            valido &= ids[k:m - NGRAMA + 1 + k] >= 0
        hs = hash_ngramas(np.where(ids < 0, 0, ids))
        lo = np.searchsorted(claves, hs, "left")
        hi = np.searchsorted(claves, hs, "right")
        cnt = hi - lo
        diag = []
        for j in np.nonzero(valido & (cnt > 0) & (cnt <= MAX_HITS_NGRAMA))[0]:
            for p in orden[lo[j]:hi[j]]:
                diag.append(int(p) - int(j))
        if len(diag) < 2:
            continue
        diag = np.array(diag)
        ordd = np.argsort(diag, kind="stable")
        diag = diag[ordd]
        W = 20 + m // 2
        fin = np.searchsorted(diag, diag + W, "right")
        votos = fin - np.arange(len(diag))
        b = int(np.argmax(votos))
        if votos[b] < 2:
            continue
        dmin, dmax = int(diag[b]), int(diag[fin[b] - 1])
        slack = max(10, m // 4)
        w0 = max(0, dmin - slack)
        w1 = min(len(oids), dmax + m + slack)
        seq = [int(x) if x >= 0 else -(g[k] + 2) for k, x in enumerate(ids)]
        sm = difflib.SequenceMatcher(None, seq, oids[w0:w1].tolist(), autojunk=False)
        bloques = [bl for bl in sm.get_matching_blocks() if bl.size >= 2]
        if sum(bl.size for bl in bloques) < max(4, 0.2 * m):
            continue
        stats["trozos_alineados"] += 1
        for bl in bloques:
            for t in range(bl.size):
                off[g[bl.a + t]] = nombres[int(ospk[w0 + bl.b + t])]
    return off, stats


# ----------------------------------------------------------------------------------------
# 3. ECAPA (CPU)
# ----------------------------------------------------------------------------------------
class Ecapa:
    def __init__(self, directorio: Path, hilos: int):
        import torch
        torch.set_num_threads(max(1, hilos))
        from speechbrain.inference.classifiers import EncoderClassifier
        directorio.mkdir(parents=True, exist_ok=True)
        fuente_m = str(directorio) if (directorio / "hyperparams.yaml").exists() else MODELO_ECAPA
        self.torch = torch
        self.m = EncoderClassifier.from_hparams(source=fuente_m, savedir=str(directorio),
                                                run_opts={"device": "cpu"})
        self.m.eval()

    def embeber(self, audios):
        """audios: lista de arrays float32 mono 16 kHz -> (B, 192) normalizado L2."""
        torch = self.torch
        mx = max(len(a) for a in audios)
        x = np.zeros((len(audios), mx), dtype=np.float32)
        for i, a in enumerate(audios):
            x[i, :len(a)] = a
        lens = torch.tensor([len(a) / mx for a in audios], dtype=torch.float32)
        with torch.inference_mode():
            e = self.m.encode_batch(torch.from_numpy(x), lens, normalize=False)
        e = e.squeeze(1).cpu().numpy().astype(np.float32)
        return e / np.maximum(np.linalg.norm(e, axis=1, keepdims=True), 1e-9)


def _clave(a, b):
    return (round(float(a), 2), round(float(b), 2))


def _guardar_cache(cache: Path, mem: dict):
    """mem: {(t0, t1): vector}. Escritura atómica (un corte nunca deja la caché rota)."""
    ks = list(mem)
    tmp = cache.with_suffix(".tmp.npz")
    with open(tmp, "wb") as fh:
        np.savez(fh, vent=np.array(ks, dtype=np.float64).reshape(-1, 2),
                 emb=np.array([mem[k] for k in ks], dtype=np.float32).reshape(-1, DIM))
    os.replace(tmp, cache)


def calcular_embeddings(wav: Path, ventanas, get_ecapa, cache: Path, sin_cache: bool):
    """Embeddings de las ventanas [(t0, t1)] en orden. La caché guarda cada ventana por su
    (t0, t1): se reutiliza lo que coincida aunque cambie el conjunto de ventanas, y se vuelca
    a disco cada CKPT_VENT ventanas, así un corte de sesión o un kill por memoria retoma
    desde ahí. Ventanas de audio <0,5 s (o ilegibles) quedan en NaN y no se cachean."""
    N = len(ventanas)
    E = np.full((N, DIM), np.nan, dtype=np.float32)
    if N == 0:
        return E
    mem = {}
    if not sin_cache and cache.exists():
        try:
            with np.load(cache) as z:
                if "vent" in z.files:
                    mem = {_clave(a, b): v for (a, b), v in zip(z["vent"], z["emb"])}
        except Exception as e:  # caché rota: se recalcula
            log(f"caché ilegible ({e}); se recalcula")
            mem = {}
    claves = [_clave(a, b) for a, b in ventanas]
    pend = []
    for i, k in enumerate(claves):
        if k in mem:
            E[i] = mem[k]
        else:
            pend.append(i)
    if not pend:
        log(f"embeddings desde caché ({N} ventanas)")
        return E
    import soundfile as sf
    ecapa = get_ecapa()
    pend.sort(key=lambda i: ventanas[i][1] - ventanas[i][0])
    t0, ultimo, hechos, desde_ckpt, t_ckpt = time.time(), time.time(), 0, 0, time.time()
    log(f"ECAPA CPU: {len(pend)}/{N} ventanas nuevas "
        f"({sum(ventanas[i][1] - ventanas[i][0] for i in pend) / 60:.1f} min de audio; "
        f"{N - len(pend)} desde caché)")
    with sf.SoundFile(str(wav)) as f:
        if f.samplerate != SR:
            raise SystemExit(f"{wav}: se esperaba {SR} Hz y es {f.samplerate} Hz")
        BATCH = 4
        for k in range(0, len(pend), BATCH):
            idx = pend[k:k + BATCH]
            audios, ok = [], []
            for i in idx:
                a, b = ventanas[i]
                f.seek(max(0, int(a * SR)))
                x = f.read(max(1, int((b - a) * SR)), dtype="float32", always_2d=True)
                x = x.mean(axis=1) if x.size else x.reshape(-1)
                if len(x) >= int(0.5 * SR):
                    audios.append(x)
                    ok.append(i)
            if audios:
                E[ok] = ecapa.embeber(audios)
                for i in ok:
                    mem[claves[i]] = E[i]
            hechos += len(idx)
            desde_ckpt += len(idx)
            if desde_ckpt >= CKPT_VENT or time.time() - t_ckpt > CKPT_S:
                _guardar_cache(cache, mem)
                desde_ckpt, t_ckpt = 0, time.time()
            if time.time() - ultimo > 60:
                el = time.time() - t0
                log(f"  {hechos}/{len(pend)} ventanas, ETA {el / hechos * (len(pend) - hechos):.0f}s")
                ultimo = time.time()
    log(f"ECAPA fin: {len(pend)} ventanas en {time.time() - t0:.0f}s")
    _guardar_cache(cache, mem)
    return E


# ----------------------------------------------------------------------------------------
# Preparación de un episodio (todo lo pesado; sin umbrales de decisión)
# ----------------------------------------------------------------------------------------
class Run:
    __slots__ = ("label", "a", "b", "start", "end", "ventanas", "emb", "vemb")

    def __init__(self, label, a, b, start, end):
        self.label, self.a, self.b, self.start, self.end = label, a, b, start, end
        self.ventanas, self.emb, self.vemb = [], None, None


class Prep:
    pass


def _prefijo(l):
    m = re.match(r"^T\d+_", l)
    return m.group(0) if m else ""


def intervalos_otros(exclusivo, solapes):
    """{etiqueta: (starts, ends)}: solapes + turnos exclusivos de OTRAS etiquetas (del mismo
    trozo si son T<k>_...; entre trozos distintos las etiquetas no son comparables), fusionados.
    Sirve para cortar un tramo cuando entre dos palabras suyas habla otra voz que Whisper omitió."""
    sol = [(float(x["start"]), float(x["end"])) for x in solapes]
    por = {}
    for x in exclusivo:
        por.setdefault(x["label"], []).append((float(x["start"]), float(x["end"])))
    out = {}
    for l in por:
        iv = list(sol)
        for l2, v in por.items():
            if l2 != l and _prefijo(l2) == _prefijo(l):
                iv.extend(v)
        f = fusionar(iv)
        out[l] = ([x[0] for x in f], [x[1] for x in f])
    return out


def choque(m, a, b):
    """Segundos de [a, b] cubiertos por los intervalos fusionados m = (starts, ends)."""
    starts, ends = m
    k, tot = bisect.bisect_right(ends, a), 0.0
    while k < len(starts) and starts[k] < b:
        tot += min(b, ends[k]) - max(a, starts[k])
        k += 1
    return tot


def construir_runs(P):
    """Rachas de palabras con la misma etiqueta, sin solape y sin hueco >GAP_TRAMO. Además se
    corta si en un hueco >GAP_CORTE entre dos palabras suyas hay >=MIN_CHOQUE s de solape o de
    turno de otra etiqueta (P.otros; p. ej. un 'mm-hm' que Whisper no transcribió)."""
    runs, a, b, lab = [], None, None, None
    otros = getattr(P, "otros", None)

    def cerrar():
        nonlocal a, b
        if a is None:
            return
        x, y = a, b
        while x <= y and not P.tsok[x]:
            x += 1
        while y >= x and not P.tsok[y]:
            y -= 1
        if x <= y:
            runs.append(Run(lab, x, y, P.start[x], P.end[y]))
        a = b = None

    for i in range(P.n):
        l = P.lab[i]
        ok = l is not None and not P.sol[i]
        if a is not None and (not ok or l != lab or P.start[i] - P.end[b] > GAP_TRAMO):
            cerrar()
        elif (ok and a is not None and otros and lab in otros
              and P.start[i] - P.end[b] > GAP_CORTE
              and choque(otros[lab], P.end[b], P.start[i]) >= MIN_CHOQUE):
            cerrar()
        if ok:
            if a is None:
                a, lab = i, l
            b = i
    cerrar()
    return runs


def restar_solapes(s, e, ms, me):
    """[s, e] menos los solapes fusionados (ms, me)."""
    piezas, cur = [], s
    k = max(0, bisect.bisect_right(me, s) - 0)
    while k < len(ms) and ms[k] < e:
        if ms[k] > cur:
            piezas.append((cur, ms[k]))
        cur = max(cur, me[k])
        k += 1
    if cur < e:
        piezas.append((cur, e))
    return piezas


def preparar(fid, rutas: Rutas, prm, get_ecapa):
    td = rutas.trabajo(fid)
    for nom in ("palabras.json", "diar.json"):
        if not (td / nom).exists():
            sys.exit(f"{fid}: falta {td / nom} (etapas 03/04)")
    if not rutas.oficial(fid).exists():
        sys.exit(f"{fid}: falta {rutas.oficial(fid)} (etapa 05)")
    wav = td / "audio16k.wav"
    if not wav.exists():
        sys.exit(f"{fid}: falta {wav} (etapa 01)")
    pal = leer_json(td / "palabras.json")
    diar = leer_json(td / "diar.json")
    ofi = leer_json(rutas.oficial(fid))
    words = pal["words"]

    P = Prep()
    P.fid, P.n = fid, len(words)
    P.wav = wav
    P.txt = [w.get("w", "") for w in words]
    P.widx = [w.get("i", k) for k, w in enumerate(words)]
    P.start = [w.get("start") if w.get("start") is not None else float("nan") for w in words]
    P.end = [w.get("end") if w.get("end") is not None else float("nan") for w in words]
    P.tsok = [bool(w.get("ts_ok", True)) and not math.isnan(P.start[k]) and not math.isnan(P.end[k])
              for k, w in enumerate(words)]
    exclusivo = diar.get("exclusivo") or diar.get("turnos") or []
    P.lab, P.sol = etiquetar_palabras(
        [None if math.isnan(x) else x for x in P.start],
        [None if math.isnan(x) else x for x in P.end], exclusivo, diar.get("solapes", []))
    P.off, st_al = alinear_oficial(words, ofi)
    del pal

    # votos por etiqueta (palabras con hablante oficial, fuera de solapes)
    P.votos = {}
    for l, s, o in zip(P.lab, P.sol, P.off):
        if l is not None and not s and o is not None:
            P.votos.setdefault(l, Counter())[o] += 1
    n_tok = sum(1 for t in P.txt if norm_tok(t))
    n_off = sum(1 for o in P.off if o is not None)
    P.stats = {"palabras": P.n, "con_etiqueta": sum(1 for l in P.lab if l),
               "con_hablante_oficial": n_off,
               "cobertura_oficial_pct": round(100 * n_off / max(1, n_tok), 1),
               "trozos_asr": st_al["trozos"], "trozos_alineados": st_al["trozos_alineados"],
               "tokens_oficiales": st_al["tokens_oficiales"],
               "cobertura_oficiales": ofi.get("cobertura")}

    # segundos de habla por etiqueta + ventanas para centroides de etiqueta
    por_label = {}
    for x in exclusivo:
        por_label.setdefault(x["label"], []).append((float(x["start"]), float(x["end"])))
    sol_f = fusionar((float(x["start"]), float(x["end"])) for x in diar.get("solapes", []))
    ms, me = [x[0] for x in sol_f], [x[1] for x in sol_f]
    P.otros = intervalos_otros(exclusivo, diar.get("solapes", []))
    try:
        P.esperados = common.fuente(fid)["hablantes"]
    except Exception:
        P.esperados = None
    mp = td / "hablantes_manual.json"
    P.manual = leer_json(mp) if mp.exists() else {}
    V, P.labels = [], {}
    for l, ivs in sorted(por_label.items()):
        ivs.sort()
        seg = sum(e - s for s, e in ivs)
        piezas = [p for s, e in ivs for p in restar_solapes(s, e, ms, me)
                  if p[1] - p[0] >= MIN_VENT_ETIQ]
        if len(piezas) > prm.max_emb_etiqueta:
            sel = np.linspace(0, len(piezas) - 1, prm.max_emb_etiqueta).astype(int)
            piezas = [piezas[k] for k in sel]
        idx = []
        for s, e in piezas:
            c, d = (s + e) / 2, min(e - s, MAX_VENT)
            idx.append(len(V))
            V.append((c - d / 2, c + d / 2))
        P.labels[l] = {"segundos": seg, "idx": idx, "cent": None, "n_vent": len(idx)}

    # Fase 1: centroides de etiqueta (checkpoint en emb06.npz)
    cache = td / "emb06.npz"
    E = calcular_embeddings(wav, V, get_ecapa, cache, prm.sin_cache)
    for l, info in P.labels.items():
        info["cent"] = centroide_robusto(E[info["idx"]]) if info["idx"] else None

    # Fase 2: ventanas de los tramos candidatos, SOLO de etiquetas que pueden acabar `ok`
    # (grupo con >= min_segundos, o con asignación manual); las demás no se embeben.
    utiles = set()
    for g in agrupar(P, prm):
        if g["seg"] >= prm.min_segundos or any(m in P.manual for m in g["miembros"]):
            utiles.update(g["miembros"])
    P.runs = construir_runs(P)
    V2 = []
    for r in P.runs:
        dur = r.end - r.start
        if dur < MIN_TRAMO_EMB or r.label not in utiles:
            continue
        if dur <= MAX_VENT:
            vs = [(r.start, r.end)]
        else:
            k = min(3, math.ceil(dur / MAX_VENT))
            vs = [(s, s + MAX_VENT) for s in np.linspace(r.start, r.end - MAX_VENT, k)]
        r.ventanas = list(range(len(V2), len(V2) + len(vs)))
        V2.extend((float(a), float(b)) for a, b in vs)
    E2 = calcular_embeddings(wav, V2, get_ecapa, cache, False)
    for r in P.runs:
        if r.ventanas:
            r.vemb = E2[r.ventanas]
            r.emb = media_unit(r.vemb)
    P.stats["ventanas_ecapa"] = len(V) + len(V2)
    P.stats["tramos_candidatos"] = len(P.runs)
    return P


# ----------------------------------------------------------------------------------------
# Centroides globales
# ----------------------------------------------------------------------------------------
class Centroides:
    def __init__(self, emb_dir: Path):
        self.dir = emb_dir
        self.meta = {}      # h -> fid -> {"etiquetas": [...], "segundos": s}
        self.vec = {}       # (h, fid) -> vector
        mj, mz = emb_dir / "centroides.json", emb_dir / "_por_fuente.npz"
        if mj.exists() and mz.exists():
            for h, d in leer_json(mj).get("hablantes", {}).items():
                self.meta[h] = d.get("fuentes", {})
            with np.load(mz) as z:
                for k in z.files:
                    h, fid = k.split("__", 1)
                    if fid in self.meta.get(h, {}):
                        self.vec[(h, fid)] = z[k]

    def global_(self, h, excluir=None):
        """Centroide global de h (cada fuente pesa igual). Para naval no entran las fuentes de
        SOLO_KAPIL (nav072): su voz va aparte en naval_kapil.npy (CONTRATO, etapa 07)."""
        vs = [self.vec[(h, f)] for f in self.meta.get(h, {})
              if f != excluir and (h, f) in self.vec
              and not (h == "naval" and f in SOLO_KAPIL)]
        return media_unit(np.array(vs)) if vs else None

    def referencia(self, h, fid):
        """Centroide contra el que se valida h en la fuente fid (leave-one-out). Naval en una
        fuente SOLO_KAPIL no se compara con el resto de episodios (None = sin control cruzado)."""
        if h == "naval" and fid in SOLO_KAPIL:
            return None
        return self.global_(h, excluir=fid)

    def kapil(self):
        """Centroide de naval_kapil: Naval en las fuentes SOLO_KAPIL."""
        vs = [self.vec[("naval", f)] for f in SOLO_KAPIL if ("naval", f) in self.vec]
        return media_unit(np.array(vs)) if vs else None

    def fuentes_de(self, h):
        return sorted(self.meta.get(h, {}))

    def reemplazar_fuente(self, fid, ok_vecs):
        """ok_vecs: {h: (vector, segundos, [etiquetas])}; borra lo anterior de esa fuente."""
        for h in list(self.meta):
            self.meta[h].pop(fid, None)
            self.vec.pop((h, fid), None)
        for h, (v, seg, labs) in ok_vecs.items():
            self.meta.setdefault(h, {})[fid] = {"etiquetas": sorted(labs),
                                                "segundos": round(seg, 1)}
            self.vec[(h, fid)] = v
        for h in [h for h, d in self.meta.items() if not d]:
            del self.meta[h]

    def guardar(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        hab, escritos = {}, set()

        def volcar(nombre, vec):
            tmp = self.dir / f"{nombre}.npy.tmp"
            with open(tmp, "wb") as fh:
                np.save(fh, vec)
            os.replace(tmp, self.dir / f"{nombre}.npy")
            escritos.add(nombre)

        for h, d in sorted(self.meta.items()):
            if not any((h, f) in self.vec for f in d):
                continue
            hab[h] = {"fuentes": d, "n_fuentes": len(d)}
            g = self.global_(h)
            if g is not None:
                volcar(h, g)
            if h == "naval":
                hab[h]["fuentes_en_global"] = [f for f in sorted(d) if f not in SOLO_KAPIL]
        derivados = {}
        k = self.kapil()
        if k is not None:
            volcar("naval_kapil", k)
            derivados["naval_kapil"] = {"fuentes": [f for f in SOLO_KAPIL
                                                    if ("naval", f) in self.vec]}
        # solo se borran los .npy de hablantes conocidos que ya no tienen centroide
        for p in self.dir.glob("*.npy"):
            if p.stem not in escritos and p.stem in (*common.HABLANTES, "naval_kapil"):
                p.unlink()
        tmp = self.dir / "_por_fuente.tmp.npz"
        with open(tmp, "wb") as fh:
            np.savez(fh, **{f"{h}__{f}": v for (h, f), v in self.vec.items() if h in hab})
        os.replace(tmp, self.dir / "_por_fuente.npz")
        escribir_json(self.dir / "centroides.json",
                      {"modelo": MODELO_ECAPA, "dim": DIM, "hablantes": hab,
                       "derivados": derivados})


# ----------------------------------------------------------------------------------------
# 4-5. Decisión: etiqueta -> hablante, estados, tramos (ligero; sin ECAPA)
# ----------------------------------------------------------------------------------------
def top_voto(votos):
    n = sum(votos.values())
    if not n:
        return None, 0.0, 0
    h, nh = votos.most_common(1)[0]
    return h, nh / n, n


def agrupar(P, prm):
    """Une etiquetas de trozos distintos (T<k>_...) por coseno de centroides."""
    patron = re.compile(r"^T(\d+)_")
    labs = sorted(P.labels, key=lambda l: -P.labels[l]["segundos"])
    grupos = []  # {"miembros": [...], "trozos": set, "cent": vec, "votos": Counter}
    for l in labs:
        m = patron.match(l)
        cent = P.labels[l]["cent"]
        v = Counter(P.votos.get(l, {}))
        mejor, mejor_c = None, prm.union_cos
        if m and cent is not None:
            for g in grupos:
                if not g["trozos"] or m.group(1) in g["trozos"] or g["cent"] is None:
                    continue
                h1, a1, n1 = top_voto(v)
                h2, a2, n2 = top_voto(g["votos"])
                if h1 and h2 and h1 != h2 and min(n1, n2) >= 50 and min(a1, a2) >= 0.7:
                    continue  # ambos con voto fuerte a hablantes distintos: no se unen
                c = coseno(cent, g["cent"])
                if c is not None and c >= mejor_c:
                    mejor, mejor_c = g, c
        if mejor is None:
            grupos.append({"miembros": [l], "trozos": {m.group(1)} if m else set(),
                           "cent": cent, "votos": v, "seg": P.labels[l]["segundos"]})
        else:
            tot = mejor["seg"] + P.labels[l]["segundos"]
            mejor["cent"] = unit(mejor["cent"] * mejor["seg"] + cent * P.labels[l]["segundos"])
            mejor["miembros"].append(l)
            mejor["trozos"].add(m.group(1))
            mejor["votos"].update(v)
            mejor["seg"] = tot
    return grupos


def estado_grupo(seg, ncob, acuerdo, h, cos, esperados, prm):
    if seg < prm.min_segundos:
        return "descartado", "pocos_segundos"
    if ncob == 0 or h is None:
        return "descartado", "sin_evidencia"
    motivos = []
    if acuerdo < prm.acuerdo:
        motivos.append("acuerdo_bajo")
    if ncob < prm.min_cobertura:
        motivos.append("pocas_palabras")
    if cos is not None and cos < prm.umbral_cos:
        motivos.append("cos_bajo")
    if h not in common.HABLANTES:      # (que no sea de los esperados del episodio solo avisa)
        motivos.append("hablante_inesperado")
    return ("ok", None) if not motivos else ("dudoso", ",".join(motivos))


def decidir(P, cents: Centroides, prm):
    infos = []
    for g in agrupar(P, prm):
        h, acuerdo, ncob = top_voto(g["votos"])
        ref = cents.referencia(h, P.fid) if h else None
        cos = coseno(g["cent"], ref)
        estado, motivo = estado_grupo(g["seg"], ncob, acuerdo, h, cos, P.esperados, prm)
        infos.append({"g": g, "h": h, "acuerdo": acuerdo, "ncob": ncob, "ref": ref,
                      "cos": cos, "estado": estado, "motivo": motivo})
    # Dos etiquetas de la misma fuente que el transcript atribuye al mismo hablante deben
    # sonar igual. Con exactamente 2, si no coinciden (p. ej. el Doc atribuye a Brett lo que dice
    # Naval) ni los segundos ni el acuerdo dicen cuál es la buena: las dos pasan a dudosas. Con
    # 3 o más se compara cada una con la media (ponderada por segundos) de las demás y solo se
    # marca la que se aparta, para no preguntar por las que son consistentes entre sí.
    for h in {i["h"] for i in infos if i["estado"] == "ok"}:
        oks = [i for i in infos if i["h"] == h and i["estado"] == "ok"]
        malas = set()
        if len(oks) == 2:
            c = coseno(oks[0]["g"]["cent"], oks[1]["g"]["cent"])
            if c is not None and c < prm.cos_misma_voz:
                malas.update((0, 1))
        elif len(oks) >= 3:
            for x in range(len(oks)):
                rest = [o for y, o in enumerate(oks) if y != x and o["g"]["cent"] is not None]
                if oks[x]["g"]["cent"] is None or not rest:
                    continue
                m = unit(sum(o["g"]["cent"] * o["g"]["seg"] for o in rest))
                c = coseno(oks[x]["g"]["cent"], m)
                if c is not None and c < prm.cos_misma_voz:
                    malas.add(x)
        for x in malas:
            otras = "+".join(m for y, o in enumerate(oks) if y != x for m in o["g"]["miembros"])
            oks[x]["estado"], oks[x]["motivo"] = "dudoso", f"voz_distinta_de_{otras}"
    et = {}
    for i in infos:
        g = i["g"]
        for l in g["miembros"]:
            h, estado, motivo, ref = i["h"], i["estado"], i["motivo"], i["ref"]
            man = next((P.manual[x] for x in [l] + g["miembros"] if x in P.manual), None)
            if man and man != "descartado":       # asignación del usuario: manda sobre el voto
                h, estado, motivo = man, "ok", None
                ref = cents.referencia(h, P.fid)
            elif man:
                estado, motivo = "descartado", "manual"
            vl = P.votos.get(l, Counter())
            nl = sum(vl.values())
            c = coseno(P.labels[l]["cent"], ref)
            e = {"hablante": h, "estado": estado,
                 "acuerdo": round(vl[h] / nl, 3) if (h and nl) else None,
                 "n_cobertura": nl, "segundos": round(P.labels[l]["segundos"], 1),
                 "cos_global": round(c, 3) if c is not None else None,
                 "motivo": motivo, "votos": dict(vl.most_common())}
            if man:
                e["manual"] = True
            if estado == "ok" and P.esperados and h not in P.esperados:
                e["aviso"] = "hablante_no_esperado_en_este_episodio"
            if len(g["miembros"]) > 1:
                e["union"] = sorted(g["miembros"])
                e["grupo"] = {"acuerdo": round(i["acuerdo"], 3), "n_cobertura": i["ncob"],
                              "segundos": round(g["seg"], 1),
                              "cos_global": round(i["cos"], 3) if i["cos"] is not None else None}
            et[l] = e

    # centroides propios (solo etiquetas ok) -> vectores por hablante de esta fuente
    acum = {}
    for l, e in et.items():
        c = P.labels[l]["cent"]
        if e["estado"] == "ok" and c is not None:
            a = acum.setdefault(e["hablante"], [np.zeros(DIM, np.float32), 0.0, []])
            a[0] += c * P.labels[l]["segundos"]
            a[1] += P.labels[l]["segundos"]
            a[2].append(l)
    ok_vecs = {h: (unit(a[0]), a[1], a[2]) for h, a in acum.items() if unit(a[0]) is not None}

    # tramos
    tramos = []
    off_h = P.off
    for r in P.runs:
        e = et.get(r.label)
        if not e or e["estado"] != "ok":
            continue
        h = e["hablante"]
        asign = off_h[r.a:r.b + 1]
        n_pal = len(asign)
        n_off = sum(1 for o in asign if o is not None)
        n_des = sum(1 for o in asign if o is not None and o != h)
        if h == "naval" and P.fid in SOLO_KAPIL:   # naval_kapil: se valida contra sí mismo
            ref = ok_vecs[h][0] if h in ok_vecs else None
        else:
            ref = cents.global_(h)
            if ref is None and h in ok_vecs:
                ref = ok_vecs[h][0]
        sim = coseno(r.emb, ref)
        sim_min = None
        if r.vemb is not None and ref is not None:
            cs = r.vemb[np.isfinite(r.vemb).all(axis=1)] @ ref
            sim_min = float(cs.min()) if len(cs) else None
        dur = r.end - r.start
        sin_cob = n_off == 0
        poca_cob = 0 < n_off < POCA_COB * n_pal
        desc, motivo = False, None
        if n_off > 0 and n_des > 0.2 * n_off:
            desc, motivo = True, "desacuerdo"
        elif sin_cob and (sim is None or sim < prm.umbral_alto):
            desc, motivo = True, "sin_cobertura_sim_baja" if sim is not None \
                else "sin_cobertura_sin_sim"
        elif sim is None:
            # un tramo >1,5 s con centroide disponible debería tener sim; sin él no hay control
            if ref is not None and dur > MIN_TRAMO_EMB:
                desc, motivo = True, "sin_sim"
            elif poca_cob:
                desc, motivo = True, "cobertura_baja_sin_sim"
        elif sim < prm.umbral_cos:
            desc, motivo = True, "sim_baja"
        elif sim_min is not None and sim_min < prm.umbral_vent:
            desc, motivo = True, "sim_baja_ventana"
        elif poca_cob and sim < prm.umbral_alto:
            desc, motivo = True, "cobertura_baja_sim_baja"
        tramos.append({"hablante": h, "label": r.label, "start": round(r.start, 3),
                       "end": round(r.end, 3), "w0": P.widx[r.a], "w1": P.widx[r.b],
                       "sim": round(sim, 4) if sim is not None else None,
                       "sim_min": round(sim_min, 4) if sim_min is not None else None,
                       "n_off": n_off, "n_desacuerdo": n_des, "sin_cobertura": sin_cob,
                       "descartado": desc, "motivo": motivo})
    tramos.sort(key=lambda t: t["start"])
    util = [t for t in tramos if not t["descartado"]]
    stats = dict(P.stats)
    stats.update({"tramos": len(tramos), "tramos_descartados": len(tramos) - len(util),
                  "segundos_utiles": round(sum(t["end"] - t["start"] for t in util), 1)})
    hab = {"id": P.fid, "etiquetas": et, "tramos": tramos,
           "params": {"umbral_cos": prm.umbral_cos, "umbral_alto": prm.umbral_alto,
                      "acuerdo": prm.acuerdo, "min_cobertura": prm.min_cobertura,
                      "min_segundos": prm.min_segundos, "union_cos": prm.union_cos,
                      "cos_misma_voz": prm.cos_misma_voz, "umbral_vent": prm.umbral_vent},
           "stats": stats}
    return hab, ok_vecs


# ----------------------------------------------------------------------------------------
# Resumen para el orquestador
# ----------------------------------------------------------------------------------------
def fmt_t(s):
    return f"{int(s // 60)}:{s % 60:04.1f}"


def imprimir_resumen(hab, P=None, cents=None):
    fid = hab["id"]
    st = hab.get("stats", {})
    print(f"\n=== RESUMEN 06 {fid} ===")
    if st:
        print(f"palabras {st.get('palabras')} | con etiqueta {st.get('con_etiqueta')} | "
              f"con hablante oficial {st.get('con_hablante_oficial')} "
              f"({st.get('cobertura_oficial_pct')} %) | trozos ASR alineados "
              f"{st.get('trozos_alineados')}/{st.get('trozos_asr')} | oficial "
              f"{st.get('cobertura_oficiales')}")
        print(f"tramos {st.get('tramos')} (descartados {st.get('tramos_descartados')}) | "
              f"segundos útiles {st.get('segundos_utiles')}")
    print(f"{'etiqueta':<18}{'hablante':<10}{'estado':<11}{'acuerdo':>8}{'n_cob':>7}"
          f"{'seg':>8}{'cos_glob':>9}  motivo")
    for l, e in sorted(hab["etiquetas"].items()):
        ac = "-" if e["acuerdo"] is None else f"{e['acuerdo']:.2f}"
        cg = "-" if e["cos_global"] is None else f"{e['cos_global']:.2f}"
        extra = (" [manual]" if e.get("manual") else "") + \
                (" [AVISO: no esperado en este episodio]" if e.get("aviso") else "") + \
                (f" [unión {'+'.join(e['union'])}]" if e.get("union") else "")
        print(f"{l:<18}{str(e['hablante']):<10}{e['estado']:<11}{ac:>8}{e['n_cobertura']:>7}"
              f"{e['segundos']:>8.1f}{cg:>9}  {e.get('motivo') or ''}{extra}")
    por_h = {}
    for t in hab["tramos"]:
        if not t["descartado"]:
            por_h[t["hablante"]] = por_h.get(t["hablante"], 0) + t["end"] - t["start"]
    if por_h:
        print("segundos útiles por hablante: " +
              ", ".join(f"{h} {s:.0f}s" for h, s in sorted(por_h.items())))
    motivos = Counter(t["motivo"] for t in hab["tramos"] if t["descartado"])
    if motivos:
        print("tramos descartados: " + ", ".join(f"{m} {n}" for m, n in motivos.items()))
    if P is not None and P.esperados:
        vistos = {e["hablante"] for e in hab["etiquetas"].values() if e["estado"] == "ok"}
        falta = [h for h in P.esperados if h not in vistos]
        if falta:
            print(f"AVISO: hablantes esperados sin ninguna etiqueta ok: {', '.join(falta)}")
    dud = {l: e for l, e in hab["etiquetas"].items() if e["estado"] == "dudoso"}
    print(f"DUDOSAS: {len(dud)}")
    for l, e in sorted(dud.items()):
        vot = ", ".join(f"{h} {n}" for h, n in e["votos"].items()) or "sin votos"
        cg = "-" if e["cos_global"] is None else f"{e['cos_global']:.2f}"
        print(f"  DUDOSA {fid} {l}: voto oficial -> {e['hablante']} "
              f"(acuerdo {e['acuerdo']}, n_cobertura {e['n_cobertura']}, "
              f"{e['segundos']:.0f} s, cos_global {cg}); votos: {vot}; motivo: {e['motivo']}")
        if P is not None:
            rs = sorted((r for r in P.runs if r.label == l), key=lambda r: r.start - r.end)[:3]
            for r in sorted(rs, key=lambda r: r.start):
                txt = " ".join(P.txt[r.a:r.b + 1][:30]).strip()
                print(f"      {fmt_t(r.start)}-{fmt_t(r.end)}: \"{txt}\"")
        print(f"      resolver: 06_hablantes.py {fid} --asignar {l}=<hablante|descartado>")


def tabla_cosenos(cents: Centroides):
    for h in sorted(cents.meta):
        fs = cents.fuentes_de(h)
        if len(fs) < 2:
            print(f"  {h}: fuentes {fs}")
            continue
        pares = [f"{a}~{b} {coseno(cents.vec[(h, a)], cents.vec[(h, b)]):.2f}"
                 for i, a in enumerate(fs) for b in fs[i + 1:]]
        print(f"  {h}: fuentes {fs} | cos entre fuentes: {', '.join(pares)}")


# ----------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------
def escribir_resultado(rutas, fid, hab):
    escribir_json(rutas.trabajo(fid) / "hablantes.json", hab)
    log(f"escrito {rutas.trabajo(fid) / 'hablantes.json'}")


def main_global(a, rutas: Rutas, prm, get_ecapa):
    ids = sorted(p.parent.name for p in (rutas.datos / "trabajo").glob("*/hablantes.json"))
    if not ids:
        sys.exit("--global: no hay ningún hablantes.json")
    log(f"--global: fuentes {ids}")
    preps = {fid: preparar(fid, rutas, prm, get_ecapa) for fid in ids}
    cents = Centroides(rutas.emb)
    previo = None
    for ronda in range(1, 4):
        res = {fid: decidir(P, cents, prm) for fid, P in preps.items()}
        for fid, (hab, ok_vecs) in res.items():
            cents.reemplazar_fuente(fid, ok_vecs)
        firma = {fid: sorted((l, e["hablante"]) for l, e in hab["etiquetas"].items()
                             if e["estado"] == "ok") for fid, (hab, _) in res.items()}
        log(f"ronda {ronda}: etiquetas ok " +
            ", ".join(f"{f} {len(v)}" for f, v in firma.items()))
        if firma == previo:
            break
        previo = firma
    # puntuación final con los centroides definitivos (sim de todos los tramos)
    res = {fid: decidir(P, cents, prm) for fid, P in preps.items()}
    for fid, (hab, ok_vecs) in res.items():
        cents.reemplazar_fuente(fid, ok_vecs)
    cents.guardar()
    log(f"centroides globales guardados en {rutas.emb}")
    for fid, (hab, _) in res.items():
        escribir_resultado(rutas, fid, hab)
        imprimir_resumen(hab, preps[fid])
    print("\n=== CENTROIDES GLOBALES ===")
    tabla_cosenos(cents)
    n_dud = sum(1 for hab, _ in res.values() for e in hab["etiquetas"].values()
                if e["estado"] == "dudoso")
    print(f"DUDOSAS totales: {n_dud}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("id", nargs="?")
    ap.add_argument("--global", dest="global_", action="store_true",
                    help="recalcula centroides con todas las fuentes y repuntúa todos los tramos")
    ap.add_argument("--forzar", action="store_true", help="recalcula aunque hablantes.json exista")
    ap.add_argument("--asignar", action="append", default=[], metavar="ETIQ=hablante",
                    help="resuelve una etiqueta dudosa (hablante o 'descartado'); repetible")
    ap.add_argument("--cpu", action="store_true",
                    help="sin efecto: esta etapa solo usa CPU (se acepta por compatibilidad)")
    ap.add_argument("--datos", help="raíz alternativa (trabajo/, oficiales/, emb/) para pruebas")
    ap.add_argument("--ecapa-dir", default=str(ECAPA_DIR))
    ap.add_argument("--umbral-cos", type=float, default=0.55)
    ap.add_argument("--umbral-alto", type=float, default=0.65,
                    help="sim mínima de un tramo sin cobertura oficial")
    ap.add_argument("--umbral-vent", type=float, default=0.4,
                    help="sim mínima de la PEOR ventana de un tramo (las ventanas sueltas son más "
                         "ruidosas que la media, de ahí un umbral más bajo que --umbral-cos)")
    ap.add_argument("--acuerdo", type=float, default=0.8)
    ap.add_argument("--min-cobertura", type=int, default=200)
    ap.add_argument("--min-segundos", type=float, default=30.0)
    ap.add_argument("--union-cos", type=float, default=0.6,
                    help="coseno mínimo para unir etiquetas de trozos distintos")
    ap.add_argument("--cos-misma-voz", type=float, default=0.4,
                    help="dos etiquetas ok del mismo hablante con coseno menor: la menor es dudosa")
    ap.add_argument("--max-emb-etiqueta", type=int, default=60,
                    help="ventanas ECAPA máximas por etiqueta (10 min de audio ya dan un centroide estable)")
    ap.add_argument("--hilos", type=int, default=3)
    ap.add_argument("--sin-cache", action="store_true")
    ap.add_argument("--sin-candado", action="store_true",
                    help="no tomar el candado de torch (por defecto se toma salvo NAVAL_PRUEBA=1)")
    a = ap.parse_args()
    if bool(a.id) == bool(a.global_):
        ap.error("indica un <id> o --global (no ambos)")

    rutas = Rutas(a.datos or common.DATOS)
    ecapa_dir = Path(a.ecapa_dir)
    cache_ecapa = []

    def get_ecapa():
        if not cache_ecapa:
            cache_ecapa.append(Ecapa(ecapa_dir, a.hilos))
        return cache_ecapa[0]

    manual_nuevo = {}
    for s in a.asignar:
        if "=" not in s:
            ap.error(f"--asignar espera ETIQ=hablante, no '{s}'")
        l, h = s.split("=", 1)
        if h != "descartado" and h not in common.HABLANTES:
            ap.error(f"hablante desconocido '{h}' (válidos: {', '.join(common.HABLANTES)})")
        manual_nuevo[l.strip()] = h.strip()

    if a.id and not a.forzar and not manual_nuevo:
        salida = rutas.trabajo(a.id) / "hablantes.json"
        if salida.exists():
            log(f"{a.id}: hablantes.json ya existe, se salta (--forzar para rehacer)")
            imprimir_resumen(leer_json(salida))
            return

    comprobar_recursos(min_ram_mb=1500)
    import contextlib
    usar_candado = not a.sin_candado and os.environ.get("NAVAL_PRUEBA") != "1"
    with (candado_gpu() if usar_candado else contextlib.nullcontext()):
        comprobar_recursos(min_ram_mb=1500)   # el candado puede tardar horas: RAM otra vez
        if a.global_:
            return main_global(a, rutas, a, get_ecapa)
        fid = a.id
        if manual_nuevo:
            mp = rutas.trabajo(fid) / "hablantes_manual.json"
            actual = leer_json(mp) if mp.exists() else {}
            actual.update(manual_nuevo)
            escribir_json(mp, actual)
            log(f"{fid}: asignaciones manuales guardadas en {mp}")
        P = preparar(fid, rutas, a, get_ecapa)
        for l in P.manual:
            if l not in P.labels:
                log(f"AVISO: la etiqueta manual {l} no existe en {fid}")
        cents = Centroides(rutas.emb)
        hab, ok_vecs = decidir(P, cents, a)
        cents.reemplazar_fuente(fid, ok_vecs)
        cents.guardar()                       # primero centroides, luego hablantes.json: un
        escribir_resultado(rutas, fid, hab)   # corte entre ambos no deja la etapa "hecha"
        log(f"centroides actualizados en {rutas.emb} (hablantes con fuente {fid}: "
            f"{', '.join(sorted(ok_vecs)) or 'ninguno'})")
        imprimir_resumen(hab, P)


if __name__ == "__main__":
    main()
