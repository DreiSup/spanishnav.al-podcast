"""La fábrica de voz: de un transcript.es.json a un clip por intervención en Drive.

Para cada bloque de hablante del transcript sale un clip, `001naval.wav`, `002nivi.wav`…, en la carpeta
`tts/` del episodio. Cada frase se genera por separado, se revisa con Whisper (y se repite si no dice el
texto), se le recortan los silencios y se une a las demás con la pausa fijada en voces.json (la general
de `ritmo` o la propia de la voz).

Junto a `tts/`, en la carpeta del episodio:
  audio/<NNN>-<slug>.mp3  el master: los clips seguidos, a -16 LUFS, listo para publicar si suena bien
  informe_tts.md       duración, reintentos, dónde empieza cada clip en el master y las frases sospechosas
  registro_tts.jsonl   una línea por clip, con el detalle de cada frase, su texto y con qué voz se hizo

Este módulo no sabe nada de Qwen: recibe una función `sintetizar(texto, voz, intento)` y un ASR. El motor
real está en `MotorQwen`; las pruebas usan uno falso.
"""
import json
import re
import sys
import time
import zlib
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import soundfile as sf

RAIZ = Path(__file__).resolve().parent
VOCES_JSON = RAIZ / "voces.json"
BORDE_INICIO, BORDE_FINAL = 0.05, 0.15     # silencio al principio y al final de cada clip
RECORTE_INICIO, RECORTE_FINAL = 0.02, 0.05  # lo que se deja a cada frase antes de unirla
SILENCIO_ENTRE = 0.6                        # entre intervenciones, en el master
MASTER = {"lufs": -16.0, "pico_db": -1.5, "sr": 44100, "kbps": 128}   # volumen y formato del master (podcast)


# ---------------------------------------------------------------- configuración y plan

def cargar_config(ruta=VOCES_JSON):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def normalizar(nombre, alias):
    n = re.sub(r"\s+", " ", nombre.strip().lower())
    return alias.get(n, n)


def asignar_voces(transcript, cfg):
    """{speaker tal como viene en el transcript: clave de voz}, con las reglas aplicadas (p. ej. Kapil)."""
    hablantes = sorted({b["speaker"] for b in transcript["contenido"]})
    mapa = {h: normalizar(h, cfg["alias"]) for h in hablantes}
    presentes = set(mapa.values())
    for regla in cfg.get("reglas", []):
        if regla["si_habla"] in presentes:
            mapa = {h: regla["usar"].get(v, v) for h, v in mapa.items()}
    desconocidos = sorted(h for h, v in mapa.items() if v not in cfg["voces"])
    if desconocidos:
        raise ValueError(f"Hablantes sin voz en voces.json: {desconocidos}. Añádelos a 'voces' o a 'alias'.")
    return mapa


def plan_episodio(transcript, cfg):
    """Un elemento por bloque, en el orden del JSON (que es el de montaje)."""
    mapa = asignar_voces(transcript, cfg)
    plan = []
    for n, b in enumerate(transcript["contenido"], 1):
        voz = mapa[b["speaker"]]
        nombre = cfg["voces"][voz].get("fichero", voz)
        frases = [f.strip() for f in b["frases"] if f.strip()]
        plan.append({"n": n, "bloque": b["id"], "speaker": b["speaker"], "voz": voz,
                     "fichero": f"{n:03d}{nombre}.wav", "frases": frases})
    return plan


def carpeta_episodio(raiz_episodios, episodio, titulo_en, crear=True):
    """La carpeta del episodio en Drive: <raíz>/<año>/<NNN Título en inglés>/.

    Si ya existe una carpeta que empieza por el número (como las que hay en naval-podcast/transcripts), se
    usa esa; si no, se crea. Los extras sin número usan el nombre de su carpeta del repo.
    """
    anio, nombre = episodio.split("/")
    numero = nombre.split("-")[0]
    dir_anio = Path(raiz_episodios) / anio
    if numero.isdigit():
        existentes = sorted(p for p in dir_anio.glob(f"{numero} *") if p.is_dir()) if dir_anio.is_dir() else []
        if existentes:
            return existentes[0]
        limpio = re.sub(r'[\\/:*?"<>|]', "", titulo_en).strip()
        destino = dir_anio / f"{numero} {limpio}"
    else:
        destino = dir_anio / nombre
    if crear:
        destino.mkdir(parents=True, exist_ok=True)
    return destino


def resumen_plan(plan, cfg, cps=15.0):
    """Texto con lo que se va a generar: bloques, caracteres, minutos estimados y modelo de cada voz."""
    por_voz = {}
    for p in plan:
        d = por_voz.setdefault(p["voz"], {"bloques": 0, "frases": 0, "caracteres": 0})
        d["bloques"] += 1
        d["frases"] += len(p["frases"])
        d["caracteres"] += sum(len(f) for f in p["frases"])
    lineas = []
    for voz, d in por_voz.items():
        modelo = "LoRA " + cfg["voces"][voz]["adaptador"] if cfg["voces"][voz].get("adaptador") else "Qwen base"
        lineas.append(f"  {voz:12s} {d['bloques']:4d} bloques · {d['frases']:5d} frases · "
                      f"~{d['caracteres'] / cps / 60:5.1f} min de audio · {modelo}")
    return "\n".join(lineas)


# ---------------------------------------------------------------- cronómetro

class Cronometro:
    """Cuánto tarda cada fase: «qwen» (generar), «whisper» (oír), «revision» (comparar con el texto), «ritmo»
    (recortar silencios), «escritura» (wav a Drive) y «master» (ffmpeg). También el pico de memoria de la GPU de
    cada fase y el detalle de cada lote. Solo mide: no cambia nada del audio.

    Antes y después de cada fase espera a que la GPU acabe (synchronize), para que cada una cuente su propio
    trabajo. `t` y `lotes` son del clip en curso (se vacían con `nuevo_clip`); `sesion` acumula toda la sesión.
    """

    def __init__(self):
        self.sesion = {}
        self.nuevo_clip()

    def nuevo_clip(self):
        self.t, self.pico, self.lotes = {}, {}, []

    @staticmethod
    def _cuda():
        torch = sys.modules.get("torch")   # sin importar torch: las pruebas sin GPU no lo tienen
        return torch if torch is not None and torch.cuda.is_available() else None

    @contextmanager
    def fase(self, clave):
        torch = self._cuda()
        if torch:
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
        t0 = time.perf_counter()
        try:
            yield
        finally:
            if torch:
                torch.cuda.synchronize()
                gb = torch.cuda.max_memory_allocated() / 2 ** 30
                self.pico[clave] = max(self.pico.get(clave, 0.0), gb)
            dt = time.perf_counter() - t0
            self.t[clave] = self.t.get(clave, 0.0) + dt
            self.sesion[clave] = self.sesion.get(clave, 0.0) + dt

    def contar(self, clave, n=1):
        self.t[clave] = self.t.get(clave, 0) + n
        self.sesion[clave] = self.sesion.get(clave, 0) + n

    def del_clip(self, total):
        """Lo que se guarda en el registro de un clip que ha tardado `total` segundos."""
        tiempos = {k: round(v, 2) for k, v in self.t.items() if not k.startswith("oom")}
        tiempos["otros"] = round(max(0.0, total - sum(tiempos.values())), 2)
        fila = {"tiempos": tiempos, "lotes": self.lotes}
        if self.pico:
            fila["pico_gb"] = {k: round(v, 2) for k, v in self.pico.items()}
        oom = {k: v for k, v in self.t.items() if k.startswith("oom")}
        if oom:
            fila["oom"] = oom
        return fila


CRONO = Cronometro()


def reparto(tiempos):
    """«qwen 85 % · whisper 9 % · …» de un diccionario de segundos por fase."""
    total = sum(v for k, v in tiempos.items() if not k.startswith("oom")) or 1.0
    orden = sorted(((k, v) for k, v in tiempos.items() if not k.startswith("oom")), key=lambda x: -x[1])
    return " · ".join(f"{k} {100 * v / total:.0f} %" for k, v in orden)


# ---------------------------------------------------------------- generación

def semilla(texto, intento):
    return zlib.crc32(texto.encode("utf-8")) + 7919 * intento


def revisar(texto, audio, sr, asr, cfg_ver, transcripcion=None):
    """(ok, errores, palabras, sobra_final, transcripción) de una frase generada.

    `transcripcion` = (texto, inicio, fin) si Whisper ya la ha oído (en lote); si no, la pide aquí.
    """
    import medir
    hyp, _, fin = transcripcion if transcripcion is not None else asr.transcribe_audio(audio, sr)
    palabras = max(len(medir.normaliza(texto).split()), 1)
    errores = round(medir.wer(texto, hyp) * palabras)
    dur = len(audio) / sr
    sobra = round(dur - fin, 2) if fin is not None else dur
    permitidos = max(1, palabras * cfg_ver["errores_por_cada_10_palabras"] // 10)
    ok = errores <= permitidos and sobra <= cfg_ver["sobra_final_max"]
    return ok, errores, palabras, sobra, hyp


def generar_frase(texto, voz, sintetizar, asr, cfg_ver, pausa_max):
    """La mejor versión de una frase: la primera que pasa la revisión o, si ninguna, la de menos errores."""
    import ritmo
    intentos = 1 + (cfg_ver["reintentos"] if asr is not None else 0)
    mejor = None
    for intento in range(intentos):
        audio, sr = sintetizar(texto, voz, intento)
        cand = {"audio": np.asarray(audio, dtype=np.float32).squeeze(), "sr": sr, "ok": None}
        if asr is not None:
            ok, errores, palabras, sobra, hyp = revisar(texto, cand["audio"], sr, asr, cfg_ver)
            cand.update(ok=ok, errores=errores, palabras=palabras, sobra_final=sobra, transcripcion=hyp)
        if mejor is None or cand["ok"] or (cand["errores"], cand["sobra_final"]) < (mejor["errores"],
                                                                                   mejor["sobra_final"]):
            mejor = cand
        if cand["ok"] is not False:
            break
    mejor["intentos"] = intento + 1
    # Silencios de la frase: casi nada en los bordes y ninguna pausa interna por encima del máximo
    mejor["audio"] = ritmo.acortar_pausas(mejor["audio"], mejor["sr"], pausa_max=pausa_max,
                                          inicio=RECORTE_INICIO, final=RECORTE_FINAL)
    return mejor


def tope_pasos(texto):
    """Máximo de pasos del modelo (12,5 por segundo) para una frase: el doble de lo que dura leída despacio, más
    3 s. Una frase que alucina y no se para se corta aquí en vez de llegar a 2048 pasos (164 s); Whisper la ve
    mal y se repite."""
    return int(12.5 * (len(texto) / 7.0 + 3.0))


def generar_bloque(frases, voz, sintetizar_lote, asr, cfg_ver, pausa_max, lote=8, intento_base=0):
    """Como generar_frase, para todas las frases de una intervención a la vez.

    `sintetizar_lote(textos, voz, intento)` devuelve (audios, sr). Las frases se mandan en lotes de `lote`,
    agrupadas por longitud para que ninguna espere mucho a la más larga. Las que no pasan la revisión se repiten
    juntas, con otra semilla, hasta `reintentos` veces. Devuelve una lista como la de generar_frase, en orden.
    `intento_base` desplaza las semillas: para rehacer una frase y que no salga igual que la vez anterior.
    """
    import ritmo
    intentos = 1 + (cfg_ver["reintentos"] if asr is not None else 0)
    mejor = [None] * len(frases)
    pendientes = list(range(len(frases)))
    for intento in range(intentos):
        if not pendientes:
            break
        orden = sorted(pendientes, key=lambda i: len(frases[i]))
        tam = -(-len(orden) // -(-len(orden) // lote))   # lotes iguales: 17 frases → 6, 6 y 5, no 8, 8 y 1
        nuevos = []
        for g in range(0, len(orden), tam):
            idx = orden[g:g + tam]
            t0 = time.perf_counter()
            with CRONO.fase("qwen"):
                audios, sr = sintetizar_lote([frases[i] for i in idx], voz, intento_base + intento)
            hechos = [(i, np.asarray(a, dtype=np.float32).squeeze(), sr) for i, a in zip(idx, audios)]
            durs = [len(a) / sr for _, a, _ in hechos]
            CRONO.lotes.append({"fase": "qwen", "intento": intento, "n": len(idx),
                                "s": round(time.perf_counter() - t0, 2), "audio_max": round(max(durs), 2),
                                "audio_suma": round(sum(durs), 2),
                                "tope": max(tope_pasos(frases[i]) for i in idx)})
            nuevos += hechos
        oidos = None
        if asr is not None:
            t0 = time.perf_counter()
            with CRONO.fase("whisper"):
                oidos = asr.transcribe_lote([a for _, a, _ in nuevos], nuevos[0][2])
            CRONO.lotes.append({"fase": "whisper", "intento": intento, "n": len(nuevos),
                                "s": round(time.perf_counter() - t0, 2),
                                "audio_suma": round(sum(len(a) / s for _, a, s in nuevos), 2),
                                "batch": getattr(asr, "lote_que_cabe", None)})
        siguen = []
        with CRONO.fase("revision"):
            revisados = [revisar(frases[i], audio, sr, asr, cfg_ver, oidos[n]) if asr is not None else None
                         for n, (i, audio, sr) in enumerate(nuevos)]
        for n, (i, audio, sr) in enumerate(nuevos):
            cand = {"audio": audio, "sr": sr, "ok": None, "intentos": intento + 1}
            if asr is not None:
                ok, errores, palabras, sobra, hyp = revisados[n]
                cand.update(ok=ok, errores=errores, palabras=palabras, sobra_final=sobra, transcripcion=hyp)
            m = mejor[i]
            if m is None or cand["ok"] or (cand["errores"], cand["sobra_final"]) < (m["errores"], m["sobra_final"]):
                mejor[i] = cand
            mejor[i]["intentos"] = intento + 1
            if cand["ok"] is False:
                siguen.append(i)
        pendientes = siguen
    with CRONO.fase("ritmo"):
        for m in mejor:
            m["audio"] = ritmo.acortar_pausas(m["audio"], m["sr"], pausa_max=pausa_max,
                                              inicio=RECORTE_INICIO, final=RECORTE_FINAL)
    return mejor


def refs_de(datos_voz):
    """Las referencias de una voz como lista: en voces.json "ref" puede ser una ruta o varias (se promedian)."""
    ref = datos_voz["ref"]
    return [ref] if isinstance(ref, str) else list(ref)


def refs_espanol(raiz_voces, sintetico="piloto/sintetico", n=1, duracion=(6, 15)):
    """Los n clips de español sintético (Chatterbox V2) más parecidos a la voz, de entre 6 y 15 s, relativos a
    raiz_voces. Es la regla del cuaderno 08 (versiones lora_ref_es1 y lora_ref_es5)."""
    filas = [json.loads(l) for l in (Path(raiz_voces) / sintetico / "seleccion.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    filas = [f for f in filas if f["variante"] == "chatterbox_v2" and duracion[0] <= f["segundos"] <= duracion[1]]
    filas.sort(key=lambda f: -f["similitud"])
    return [f["audio"] for f in filas[:n]]


def firma(voz, cfg):
    """Lo que define cómo suena una voz: adaptador, referencias, temperatura y pausa. Si cambia en voces.json, los
    clips ya hechos con la firma anterior se rehacen solos al relanzar la fábrica."""
    d = cfg["voces"][voz]
    return {"adaptador": d.get("adaptador"), "ref": refs_de(d), "temperatura": d.get("temperatura"),
            "pausa_max": pausa_de(voz, cfg)}


def clip_al_dia(fila, p, cfg):
    """¿El clip de esta fila del registro sigue valiendo para el bloque `p` del plan?

    Vale si se generó con el mismo texto (las frases que guarda el registro) y con la voz que dice ahora voces.json.
    Los clips anteriores al 3-nov no guardan la firma de la voz: solo su adaptador, y se generaron sin temperatura
    propia (la referencia y la pausa de cada voz no han cambiado desde entonces).
    """
    if [d.get("texto") for d in fila.get("frases", [])] != p["frases"]:
        return False
    actual = firma(p["voz"], cfg)
    if "firma" in fila:
        return fila["firma"] == actual
    return fila.get("adaptador") == actual["adaptador"] and actual["temperatura"] is None


def pausa_de(voz, cfg):
    """La pausa máxima de una voz: la suya si la tiene en voces.json, si no la general de 'ritmo'."""
    return cfg["voces"][voz].get("pausa_max", cfg["ritmo"]["pausa_max"])


def ensamblar(audios, sr, hueco):
    """Las frases de una intervención en un clip: bordes de silencio y `hueco` entre frases. Devuelve el audio y el
    segundo en que empieza cada frase dentro del clip."""
    trozos, inicios, cursor = [], [], BORDE_INICIO
    for k, a in enumerate(audios):
        if k:
            trozos.append(np.zeros(int(sr * hueco), dtype=np.float32))
            cursor += hueco
        inicios.append(round(cursor, 2))
        trozos.append(a)
        cursor += len(a) / sr
    audio = np.concatenate([np.zeros(int(sr * BORDE_INICIO), dtype=np.float32), *trozos,
                            np.zeros(int(sr * BORDE_FINAL), dtype=np.float32)])
    pico = float(np.abs(audio).max()) if audio.size else 0.0
    if pico > 1.0:
        audio = audio / pico * 0.99
    return audio, inicios


def ruta_frase(tts_dir, fichero, k):
    """Cada frase, ya recortada, se guarda aparte para poder rehacer solo esa: tts/frases/002naval_07.wav es la frase 7
    (numeradas desde 1, como en el informe y en indice_master.tsv; `k` es el índice desde 0)."""
    return Path(tts_dir) / "frases" / f"{Path(fichero).stem}_{k + 1:02d}.wav"


def _escribir_wav(ruta, audio, sr):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(f".{ruta.name}.tmp.wav")
    sf.write(str(tmp), audio, sr, subtype="PCM_16")
    tmp.rename(ruta)


def generar_episodio(plan, sintetizar_lote, asr, carpeta, cfg, avisar=print, master=None, titulo=None, rehacer=None,
                     libro_coste=None, episodio=None):
    """Genera los clips que falten en <carpeta>/tts/, monta el master (si están todos) y reescribe el informe.

    `sintetizar_lote(textos, voz, intento)` → (audios, sr): las frases de cada intervención se generan juntas
    (generar_bloque). Lo que ya existe no se repite: si se corta, se vuelve a lanzar y sigue por donde iba.

    `rehacer` = {"002naval.wav": [7, 12]}: rehace solo esas frases (numeradas desde 1, como en el informe) con
    semillas nuevas y rearma el clip con las demás intactas. Si el clip es anterior al 4-nov y no tiene sus frases
    guardadas aparte, lo rehace entero (también con semillas nuevas) y desde ahí ya se puede ir frase a frase.
    """
    cfg_ver = cfg["verificacion"]
    rehacer = rehacer or {}
    tts_dir = Path(carpeta) / "tts"
    tts_dir.mkdir(parents=True, exist_ok=True)
    registro = Path(carpeta) / "registro_tts.jsonl"
    hechos = leer_registro(carpeta)
    t_total, s_total = 0.0, 0.0
    fases = {}   # segundos por fase de todo el episodio
    agrupar = cfg["motor"].get("agrupar", "intervencion")
    previas = {}   # agrupar «voz»: fichero → (frases ya generadas en una tanda, su parte del tiempo y las medidas)

    def entero_pendiente(q):
        """¿Hay que generar este clip entero (no frases sueltas)? Lo mismo que decide el bucle de abajo."""
        if rehacer.get(q["fichero"]):
            return False
        w, ant = tts_dir / q["fichero"], hechos.get(q["fichero"])
        return not w.exists() or not (ant is None or clip_al_dia(ant, q, cfg))

    def tanda_de_voz(i):
        """Genera de una vez las frases de varias intervenciones seguidas de la misma voz (la de plan[i] y las
        siguientes de esa voz que estén pendientes, hasta `motor.tanda_voz` frases), en lotes de `motor.lote_voz`
        agrupados por longitud. Así los lotes van llenos aunque las intervenciones sean cortas. Deja el resultado en
        `previas` y cada clip se escribe después en su turno, como siempre. Si se corta a mitad de una tanda, al
        relanzar se repite esa tanda (lo ya escrito no)."""
        voz, grupo = plan[i]["voz"], [plan[i]]
        n = len(plan[i]["frases"])
        for q in plan[i + 1:]:
            if n >= cfg["motor"].get("tanda_voz", 48):
                break
            if q["voz"] == voz and q["fichero"] not in previas and entero_pendiente(q):
                grupo.append(q)
                n += len(q["frases"])
        frases = [f for q in grupo for f in q["frases"]]
        CRONO.nuevo_clip()
        t0 = time.time()
        hechas = generar_bloque(frases, voz, sintetizar_lote, asr, cfg_ver, pausa_de(voz, cfg),
                                lote=cfg["motor"].get("lote_voz", 16))
        tw = time.time() - t0
        med = CRONO.del_clip(tw)
        dur = [len(h["audio"]) / h["sr"] for h in hechas]
        total, pos = sum(dur) or 1.0, 0
        for j, q in enumerate(grupo):
            parte = sum(dur[pos:pos + len(q["frases"])]) / total
            previas[q["fichero"]] = (hechas[pos:pos + len(q["frases"])], {
                "segundos": tw * parte, "tiempos": {k: v * parte for k, v in med["tiempos"].items()},
                "lotes": med["lotes"] if j == 0 else [], "pico_gb": med.get("pico_gb"),
                "tanda": [x["fichero"] for x in grupo]})
            pos += len(q["frases"])
        if len(grupo) > 1:
            avisar(f"  tanda de {voz}: {len(grupo)} intervenciones ({grupo[0]['fichero']}…{grupo[-1]['fichero']}), "
                   f"{len(frases)} frases a la vez, {tw:.0f} s")

    for i, p in enumerate(plan):
        wav = tts_dir / p["fichero"]
        anterior = hechos.get(p["fichero"])
        pedidas = sorted({int(k) - 1 for k in rehacer.get(p["fichero"], [])})
        if pedidas and (min(pedidas) < 0 or max(pedidas) >= len(p["frases"])):
            raise ValueError(f"{p['fichero']} tiene {len(p['frases'])} frases: no existe la {[k + 1 for k in pedidas]}")
        if wav.exists() and not pedidas:
            if anterior is None or clip_al_dia(anterior, p, cfg):
                continue
            avisar(f"  {p['fichero']}: ha cambiado su texto o su voz desde que se generó; lo rehago")
        if agrupar == "voz" and not pedidas and p["fichero"] not in previas:
            tanda_de_voz(i)
        t0 = time.time()
        CRONO.nuevo_clip()
        extra = None
        pausa = pausa_de(p["voz"], cfg)
        hueco = max(0.0, pausa - RECORTE_INICIO - RECORTE_FINAL)
        lote = cfg["motor"].get("lote", 8)
        parcial = (pedidas and wav.exists() and anterior is not None and clip_al_dia(anterior, p, cfg)
                   and all(ruta_frase(tts_dir, p["fichero"], k).exists() for k in range(len(p["frases"]))))
        if parcial:
            avisar(f"  {p['fichero']}: rehago las frases {[k + 1 for k in pedidas]}")
            detalle = [dict(d) for d in anterior["frases"]]
            veces = 1 + max(detalle[k].get("rehecha", 0) for k in pedidas)
            nuevas = generar_bloque([p["frases"][k] for k in pedidas], p["voz"], sintetizar_lote, asr, cfg_ver, pausa,
                                    lote=lote, intento_base=100 * veces)
            audios, sr = [], None
            for k in range(len(p["frases"])):
                if k in pedidas:
                    r = nuevas[pedidas.index(k)]
                    a, sr_k = r["audio"], r["sr"]
                    with CRONO.fase("escritura"):
                        _escribir_wav(ruta_frase(tts_dir, p["fichero"], k), a, sr_k)
                    detalle[k].update(intentos=r["intentos"], ok=r["ok"], errores=r.get("errores"),
                                      sobra_final=r.get("sobra_final"), transcripcion=r.get("transcripcion"),
                                      rehecha=veces)
                else:
                    with CRONO.fase("escritura"):
                        a, sr_k = sf.read(str(ruta_frase(tts_dir, p["fichero"], k)), dtype="float32")
                sr = sr or sr_k
                audios.append(a)
        else:
            if pedidas:
                avisar(f"  {p['fichero']}: sin sus frases guardadas aparte; lo rehago entero con semillas nuevas")
            veces = 1 + max((d.get("rehecha", 0) for d in (anterior or {}).get("frases", [])), default=0) \
                if pedidas else 0
            if p["fichero"] in previas:
                hechas, extra = previas.pop(p["fichero"])
            else:
                hechas = generar_bloque(p["frases"], p["voz"], sintetizar_lote, asr, cfg_ver, pausa, lote=lote,
                                        intento_base=100 * veces)
            sr = hechas[0]["sr"]
            audios, detalle = [], []
            for k, (frase, r) in enumerate(zip(p["frases"], hechas)):
                with CRONO.fase("escritura"):
                    _escribir_wav(ruta_frase(tts_dir, p["fichero"], k), r["audio"], r["sr"])
                audios.append(r["audio"])
                detalle.append({"k": k, "texto": frase, "intentos": r["intentos"], "ok": r["ok"],
                                "errores": r.get("errores"), "sobra_final": r.get("sobra_final"),
                                "transcripcion": r.get("transcripcion"), **({"rehecha": veces} if veces else {})})
        audio, inicios = ensamblar(audios, sr, hueco)
        for d, ini in zip(detalle, inicios):
            d["inicio_s"] = ini
        with CRONO.fase("escritura"):
            _escribir_wav(wav, audio, sr)
        seg, dt = len(audio) / sr, time.time() - t0
        medidas = CRONO.del_clip(dt)
        if extra:   # su parte de la tanda de voz en la que se generó
            dt += extra["segundos"]
            for k, v in extra["tiempos"].items():
                medidas["tiempos"][k] = round(medidas["tiempos"].get(k, 0.0) + v, 2)
            medidas["lotes"] = extra["lotes"]
            medidas["tanda"] = extra["tanda"]
            if extra.get("pico_gb"):
                medidas["pico_gb"] = extra["pico_gb"]
        t_total, s_total = t_total + dt, s_total + seg
        for k, v in medidas["tiempos"].items():
            fases[k] = fases.get(k, 0.0) + v
        fila = {"fichero": p["fichero"], "bloque": p["bloque"], "voz": p["voz"], "segundos": round(seg, 2),
                "segundos_generacion": round(dt, 1), "sr": sr, "frases": detalle,
                "adaptador": cfg["voces"][p["voz"]].get("adaptador"), "firma": firma(p["voz"], cfg),
                "gpu": cfg["motor"].get("gpu"), "asr": f"{asr.modelo} ({getattr(asr, 'marcas', 'palabra')})" if hasattr(asr, "modelo") else None,
                "fecha": time.strftime("%Y-%m-%dT%H:%M:%S"), **medidas}
        with registro.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(fila, ensure_ascii=False) + "\n")
        hechos[p["fichero"]] = fila
        malas = sum(1 for d in detalle if d["ok"] is False)
        avisar(f"  {p['fichero']}: {seg:6.1f} s en {dt:6.1f} s · {len(detalle)} frases"
               + (f" · {malas} sospechosas" if malas else ""))
    if s_total:
        avisar(f"Generado: {s_total / 60:.1f} min de audio en {t_total / 60:.1f} min "
               f"({t_total / s_total:.2f} s de GPU por segundo de audio)")
        avisar(f"Reparto del tiempo: {reparto(fases)}")
    master = Path(master) if master else Path(carpeta) / "audio" / "master.mp3"
    inicios, t_master = None, 0.0
    if all((tts_dir / p["fichero"]).exists() for p in plan):
        t0 = time.perf_counter()
        with CRONO.fase("master"):
            inicios = montar_master(plan, tts_dir, master, titulo=titulo)
        t_master = time.perf_counter() - t0
        avisar(f"Master: {master.name} ({inicios['_total'] / 60:.1f} min, montado en {t_master:.0f} s)")
    escribir_informe(plan, hechos, carpeta, inicios, master, cfg)
    if libro_coste and t_total:
        gpu = cfg["motor"].get("gpu")
        anotar_coste(libro_coste, {"tipo": "episodio", "episodio": episodio or Path(carpeta).name,
                                   "fecha": time.strftime("%Y-%m-%dT%H:%M:%S"), "gpu": gpu,
                                   "segundos_gpu": round(t_total, 1), "minutos_audio_generado": round(s_total / 60, 2),
                                   "unidades_estimadas": round(unidades(t_total, gpu, cfg), 3),
                                   "rehacer": bool(rehacer), "tiempos": {k: round(v, 1) for k, v in fases.items()},
                                   "segundos_master": round(t_master, 1)})
        avisar(f"Coste: {t_total / 60:.1f} min de {gpu} ≈ {unidades(t_total, gpu, cfg):.2f} unidades")
    return hechos


def montar_cortos(largo, plan_largo, carpeta_largo, cortos, cfg, avisar=print):
    """Los cortos que son un tramo exacto de un largo (cortos.json), montados con los clips del largo, sin GPU.

    `cortos` = [(episodio, plan, carpeta, titulo_es), …]. Cada intervención del corto se empareja con la del largo que
    tiene **la misma voz y exactamente las mismas frases** (no por `speaker`: el largo y el corto pueden escribirlo
    distinto, «Brett Hall» y «Brett»). Copia su clip y sus frases sueltas con el nombre del corto, apunta en el registro
    del corto de qué clip del largo sale (`de_largo`, 0 s de GPU), monta el master y escribe el informe. Lo que ya
    está al día no se repite. Las intervenciones sin pareja (o cuyo clip del largo aún no existe) se quedan sin hacer y
    se listan: se generan después con la fábrica normal sobre ese corto, que hará solo esas.
    Devuelve [(episodio, clips hechos, clips totales, [ficheros sin pareja])].
    """
    import shutil
    tts_l = Path(carpeta_largo) / "tts"
    hechos_l = leer_registro(carpeta_largo)
    indice = {}
    for p in plan_largo:
        fila = hechos_l.get(p["fichero"])
        if (fila and (tts_l / p["fichero"]).exists() and clip_al_dia(fila, p, cfg)
                and all(ruta_frase(tts_l, p["fichero"], k).exists() for k in range(len(p["frases"])))):
            indice.setdefault((p["voz"], tuple(p["frases"])), (p, fila))
    resumen = []
    for episodio, plan, carpeta, titulo in cortos:
        carpeta = Path(carpeta)
        tts = carpeta / "tts"
        (tts / "frases").mkdir(parents=True, exist_ok=True)
        registro = carpeta / "registro_tts.jsonl"
        hechos = leer_registro(carpeta)
        sin_pareja = []
        for p in plan:
            previa = hechos.get(p["fichero"])
            if (tts / p["fichero"]).exists() and previa and clip_al_dia(previa, p, cfg):
                continue
            par = indice.get((p["voz"], tuple(p["frases"])))
            if par is None:
                sin_pareja.append(p["fichero"])
                continue
            pl, fila = par
            shutil.copyfile(tts_l / pl["fichero"], tts / p["fichero"])
            for k in range(len(p["frases"])):
                shutil.copyfile(ruta_frase(tts_l, pl["fichero"], k), ruta_frase(tts, p["fichero"], k))
            nueva = {k: v for k, v in fila.items() if k not in ("tiempos", "lotes", "tanda", "pico_gb", "oom")}
            nueva.update(fichero=p["fichero"], bloque=p["bloque"], segundos_generacion=0.0,
                         de_largo=f"{largo}/{pl['fichero']}", fecha=time.strftime("%Y-%m-%dT%H:%M:%S"))
            with registro.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(nueva, ensure_ascii=False) + "\n")
            hechos[p["fichero"]] = nueva
        master = carpeta / "audio" / f"{episodio.split('/')[1]}.mp3"
        inicios = None
        if not sin_pareja:
            inicios = montar_master(plan, tts, master, titulo=titulo)
        escribir_informe(plan, hechos, carpeta, inicios, master, cfg)
        hechos_ok = len(plan) - len(sin_pareja)
        avisar(f"  {episodio}: {hechos_ok} de {len(plan)} clips del largo"
               + (f" · master {inicios['_total'] / 60:.1f} min" if inicios else "")
               + (f" · SIN PAREJA: {sin_pareja}" if sin_pareja else ""))
        resumen.append((episodio, hechos_ok, len(plan), sin_pareja))
    return resumen


def verificar_cortos(largo, cortos, cfg, wer_max=0.15):
    """Revisa, frase a frase, cortos ya montados con montar_cortos. Para cada corto: que cada intervención del plan
    tiene clip y fila en el registro, que la fila sale de `largo` (de_largo), que sus frases son las del transcript,
    y por frase que pasó la revisión (ok), que lo que oyó Whisper se parece al texto (WER ≤ wer_max) y que no sobra
    nada al final (sobra_final ≤ verificacion.sobra_final_max). Devuelve [(episodio, frases, [problemas])]."""
    import medir
    sobra_max = cfg["verificacion"]["sobra_final_max"]
    salida = []
    for episodio, plan, carpeta, _ in cortos:
        carpeta = Path(carpeta)
        hechos = leer_registro(carpeta)
        problemas, n = [], 0
        for p in plan:
            fila = hechos.get(p["fichero"])
            if fila is None or not (carpeta / "tts" / p["fichero"]).exists():
                problemas.append(f"{p['fichero']}: falta el clip o su fila del registro")
                continue
            if not str(fila.get("de_largo", "")).startswith(largo + "/"):
                problemas.append(f"{p['fichero']}: no sale de {largo} (de_largo = {fila.get('de_largo')})")
            textos = [d.get("texto") for d in fila.get("frases", [])]
            if textos != p["frases"]:
                problemas.append(f"{p['fichero']}: sus frases no son las del transcript")
            for d in fila.get("frases", []):
                n += 1
                hyp = d.get("transcripcion") or ""
                w = medir.wer(d.get("texto", ""), hyp)
                sobra = d.get("sobra_final")
                if d.get("ok") is False or w > wer_max or (sobra is not None and sobra > sobra_max):
                    problemas.append(f"{p['fichero']} frase {d['k'] + 1}: ok={d.get('ok')} WER={w:.2f} "
                                     f"sobra={sobra} · texto: {d.get('texto')} · oído: {hyp}")
        salida.append((episodio, n, problemas))
    return salida


def unidades(segundos, gpu, cfg):
    """Unidades de Colab estimadas para `segundos` de una GPU, con las tarifas de voces.json («coste»)."""
    tarifas = cfg.get("coste", {}).get("unidades_por_hora", {})
    nombre = next((k for k in tarifas if k.lower() in str(gpu or "").lower()), cfg.get("coste", {}).get("por_defecto"))
    return segundos / 3600 * tarifas.get(nombre, 0)


def anotar_coste(libro, fila):
    """Una línea más en coste_fabrica.jsonl (naval-podcast/): el libro de lo que ha costado la fábrica."""
    with Path(libro).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(fila, ensure_ascii=False) + "\n")


def _gpu_actual():
    try:
        import torch
        return torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    except ImportError:
        return "CPU"


def anotar_sesion(libro, cfg, t_inicio, episodios, t_carga=None, error=False):
    """Apunta la sesión entera (desde la celda 3) en coste_fabrica.jsonl con su reparto: cargar modelos, cada fase
    de la generación (CRONO.sesion) y el resto (preparar, esperas, ratos parados). Devuelve el texto para el cuaderno."""
    gpu = cfg["motor"].get("gpu") or _gpu_actual()
    seg = time.time() - t_inicio
    uds = unidades(seg, gpu, cfg) if gpu != "CPU" else 0.0
    fases = {k: round(v, 1) for k, v in CRONO.sesion.items() if not k.startswith("oom")}
    carga = round(t_carga, 1) if t_carga else 0.0
    resto = max(0.0, seg - carga - sum(fases.values()))
    fila = {"tipo": "sesion", "fin": time.strftime("%Y-%m-%dT%H:%M:%S"), "gpu": gpu, "segundos": round(seg),
            "unidades_estimadas": round(uds, 3), "episodios": list(episodios), "carga_modelos_s": carga,
            "tiempos": fases, "resto_s": round(resto)}
    oom = {k: v for k, v in CRONO.sesion.items() if k.startswith("oom")}
    if oom:
        fila["oom"] = oom
    if error:
        fila["error"] = True
    anotar_coste(libro, fila)
    partes = [f"cargar modelos {carga / 60:.1f}"] + [f"{k} {v / 60:.1f}" for k, v in
                                                       sorted(fases.items(), key=lambda x: -x[1])]
    partes.append(f"resto (preparar, esperas, parado) {resto / 60:.1f}")
    return (f"Esta sesión: {seg / 60:.0f} min de {gpu} ≈ {uds:.2f} unidades\n"
            f"  En minutos: {' · '.join(partes)}")


def coste_de_carpeta(carpeta, cfg):
    """Tiempo de GPU y unidades de un episodio, sumando TODAS las líneas de su registro (también lo rehecho). Las
    líneas anteriores al 5-nov no guardan la GPU: se toma la de 'por_defecto' (T4)."""
    registro = Path(carpeta) / "registro_tts.jsonl"
    if not registro.exists():
        return None
    filas = [json.loads(l) for l in registro.read_text(encoding="utf-8").splitlines() if l.strip()]
    seg = sum(f.get("segundos_generacion", 0) for f in filas)
    uds = sum(unidades(f.get("segundos_generacion", 0), f.get("gpu"), cfg) for f in filas)
    gpus = sorted({f.get("gpu") or f"{cfg.get('coste', {}).get('por_defecto', '?')} (supuesta)" for f in filas})
    return {"segundos_gpu": seg, "unidades": uds, "gpus": gpus, "lineas": len(filas)}


def leer_registro(carpeta):
    """{fichero: última fila del registro_tts.jsonl}."""
    registro = Path(carpeta) / "registro_tts.jsonl"
    hechos = {}
    if registro.exists():
        for l in registro.read_text(encoding="utf-8").splitlines():
            if l.strip():
                f = json.loads(l)
                hechos[f["fichero"]] = f
    return hechos


def rehacer_master(plan, carpeta, master, titulo=None, avisar=print, cfg=None):
    """Solo el master y el informe, sin GPU: para cuando se ha arreglado a mano un clip de tts/ (Audacity)."""
    tts_dir = Path(carpeta) / "tts"
    faltan = [p["fichero"] for p in plan if not (tts_dir / p["fichero"]).exists()]
    if faltan:
        avisar(f"  faltan clips, no hay master: {faltan}")
        return None
    inicios = montar_master(plan, tts_dir, master, titulo=titulo)
    escribir_informe(plan, leer_registro(carpeta), carpeta, inicios, master, cfg)
    avisar(f"  master: {Path(master).name} ({inicios['_total'] / 60:.1f} min)")
    return inicios


def _mmss(segundos):
    decimas = int(round(segundos * 10))   # redondear antes de partir: 179,98 s es 3:00.0, no 2:60.0
    return f"{decimas // 600}:{decimas % 600 / 10:04.1f}"


def escribir_informe(plan, hechos, carpeta, inicios=None, master=None, cfg=None):
    """informe_tts.md: qué clips hay, cuánto duran, dónde empiezan en el master y qué frases son sospechosas."""
    total = sum(f["segundos"] for f in hechos.values())
    coste = coste_de_carpeta(carpeta, cfg) if cfg else None
    linea_coste = (f"Generarlo ha costado {coste['segundos_gpu'] / 60:.1f} min de GPU ({', '.join(coste['gpus'])}), "
                   f"unas **{coste['unidades']:.2f} unidades** de Colab, rehechos incluidos. " if coste else "")
    fases = {}
    for f in hechos.values():
        for k, v in f.get("tiempos", {}).items():
            fases[k] = fases.get(k, 0.0) + v
    if fases:   # solo los clips generados desde el 6-nov guardan el tiempo de cada fase
        linea_coste += f"Reparto del tiempo: {reparto(fases)}. "
    lineas = [f"# Clips de TTS — {Path(carpeta).name}", "",
              f"{len(hechos)} de {len(plan)} clips · {total / 60:.1f} min. " + linea_coste
              + (f"Master: `audio/{Path(master).name}`. " if inicios else "Sin master: faltan clips. ")
              + "Las frases **sospechosas** no pasaron la revisión de Whisper ni con los reintentos: si al escuchar el "
              "master algo suena raro, empieza por ahí (el minuto es el del master).",
              "", "| Clip | Voz | En el master | Duración | Frases | Reintentos | Sospechosas |",
              "|---|---|---|---|---|---|---|"]
    sospechas = []
    for p in plan:
        f = hechos.get(p["fichero"])
        if not f:
            lineas.append(f"| {p['fichero']} | {p['voz']} | — | — | {len(p['frases'])} | — | sin generar |")
            continue
        reint = sum(d["intentos"] - 1 for d in f["frases"])
        malas = [d for d in f["frases"] if d["ok"] is False]
        inicio = inicios.get(p["fichero"]) if inicios else None
        lineas.append(f"| {p['fichero']} | {f['voz']} | {_mmss(inicio) if inicio is not None else '—'} | "
                      f"{f['segundos']:.1f} s | {len(f['frases'])} | {reint} | {len(malas) or ''} |")
        sospechas += [(p["fichero"], d, inicio) for d in malas]
    if sospechas:
        lineas += ["", "## Frases sospechosas", ""]
        for fichero, d, inicio in sospechas:
            donde = f"minuto {_mmss(inicio + d['inicio_s'])} del master" if inicio is not None else "sin master"
            lineas += [f"- **{donde}** ({fichero}, frase {d['k'] + 1}; {d['errores']} errores, "
                       f"{d['sobra_final']} s tras la última palabra)",
                       f"  - Texto: {d['texto']}", f"  - Whisper oyó: {d['transcripcion']}"]
    (Path(carpeta) / "informe_tts.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    if inicios:
        escribir_indice(plan, hechos, inicios, Path(carpeta) / "indice_master.tsv")


def escribir_indice(plan, hechos, inicios, destino):
    """indice_master.tsv: dónde empieza cada frase en el master (minuto, segundo, clip, número de frase desde 1). Con
    él y el texto del repo se localiza cualquier minuto o cualquier frase: «fallo en el 7:21» → clip y frase."""
    lineas = ["minuto\tsegundo\tclip\tfrase"]
    for p in plan:
        f = hechos.get(p["fichero"])
        if not f:
            continue
        for d in f["frases"]:
            seg = inicios[p["fichero"]] + d["inicio_s"]
            lineas.append(f"{_mmss(seg)}\t{seg:.1f}\t{p['fichero']}\t{d['k'] + 1}")
    Path(destino).write_text("\n".join(lineas) + "\n", encoding="utf-8")


def montar_master(plan, tts_dir, destino, titulo=None, silencio=SILENCIO_ENTRE, ajustes=MASTER):
    """El audio final del episodio: los clips en el orden del transcript (que es el de montaje), con `silencio`
    segundos entre intervenciones, a -16 LUFS y en MP3 mono. Devuelve {fichero: segundo en que empieza en el master}
    y '_total' con la duración.

    El volumen se ajusta con loudnorm de ffmpeg en dos pasadas (mide y después aplica una ganancia lineal), así que
    no comprime ni cambia la dinámica de la voz.
    """
    import subprocess
    import tempfile
    trozos, inicios, cursor, sr = [], {}, 0.0, None
    for n, p in enumerate(plan):
        audio, sr_clip = sf.read(str(Path(tts_dir) / p["fichero"]), dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        sr = sr or sr_clip
        if n:
            trozos.append(np.zeros(int(sr * silencio), dtype=np.float32))
            cursor += silencio
        inicios[p["fichero"]] = round(cursor, 2)
        trozos.append(audio)
        cursor += len(audio) / sr
    inicios["_total"] = round(cursor, 2)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    norma = f"I={ajustes['lufs']}:TP={ajustes['pico_db']}:LRA=11"
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "master.wav"
        sf.write(str(wav), np.concatenate(trozos), sr, subtype="PCM_16")
        medida = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(wav), "-af",
                                 f"loudnorm={norma}:print_format=json", "-f", "null", "-"],
                                capture_output=True, text=True, check=True).stderr
        m = json.loads(medida[medida.rindex("{"):medida.rindex("}") + 1])
        filtro = (f"loudnorm={norma}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                  f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
                  f"linear=true")
        salida = Path(tmp) / "master.mp3"
        orden = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav), "-af", filtro,
                 "-ar", str(ajustes["sr"]), "-ac", "1", "-c:a", "libmp3lame", "-b:a", f"{ajustes['kbps']}k"]
        if titulo:
            orden += ["-metadata", f"title={titulo}"]
        subprocess.run(orden + [str(salida)], check=True)
        destino.write_bytes(salida.read_bytes())   # copia de una vez: en Drive no queda un mp3 a medias
    return inicios


# ---------------------------------------------------------------- el motor real

class MotorQwen:
    """Qwen3-TTS base con un adaptador LoRA por voz (los que tengan), en modo solo timbre."""

    def __init__(self, cfg, voces, raiz_voces):
        import torch
        from qwen_tts import Qwen3TTSModel
        self.torch, self.cfg = torch, cfg
        cfg["motor"]["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        self.tts = Qwen3TTSModel.from_pretrained(cfg["motor"]["modelo"], device_map="cuda:0", dtype=dtype,
                                                 attn_implementation="sdpa")
        self.peft = None
        con_lora = [v for v in voces if cfg["voces"][v].get("adaptador")]
        if con_lora:
            from peft import PeftModel
            for v in con_lora:
                ruta = str(Path(raiz_voces) / cfg["voces"][v]["adaptador"])
                if self.peft is None:
                    self.peft = PeftModel.from_pretrained(self.tts.model.talker, ruta, adapter_name=v)
                else:
                    self.peft.load_adapter(ruta, adapter_name=v)
            self.tts.model.talker = self.peft
            self.peft.eval()
        self.prompts = {v: self._huella([Path(raiz_voces) / r for r in refs_de(cfg["voces"][v])]) for v in voces}
        print(f"Qwen cargado ({dtype}); con LoRA: {con_lora or 'ninguna'}; sin LoRA: "
              f"{[v for v in voces if v not in con_lora] or 'ninguna'}")

    def _muestreo(self, voz):
        """Temperatura de la voz si voces.json la fija ("temperatura"); si no, la de Qwen (0,9). Se aplica igual a
        los dos niveles del modelo, como en piloto/cuadernos/09_erres_naval."""
        t = self.cfg["voces"][voz].get("temperatura")
        return {} if t is None else {"temperature": t, "subtalker_temperature": t}

    def _huella(self, rutas_audio):
        """Prompt de solo timbre. Con varias referencias, la media de sus huellas (con su norma media), como en
        piloto/cuadernos/08_acento_naval."""
        import dataclasses
        it = self.tts.create_voice_clone_prompt(ref_audio=[str(r) for r in rutas_audio], x_vector_only_mode=True)
        if len(it) == 1:
            return it
        embs = self.torch.stack([x.ref_spk_embedding for x in it])
        media = embs.mean(0)
        media = media / media.norm() * embs.norm(dim=-1).mean()
        return [dataclasses.replace(it[0], ref_spk_embedding=media)]

    def sintetizar(self, texto, voz, intento):
        audios, sr = self.sintetizar_lote([texto], voz, intento, semilla_lote=semilla(texto, intento))
        return audios[0], sr

    def sintetizar_lote(self, textos, voz, intento, semilla_lote=None):
        """Varias frases de la misma voz en una sola pasada del modelo.

        Si la GPU se queda sin memoria, libera y parte el lote en dos (hasta llegar a una frase). Después de cada
        pasada libera la memoria del modelo para que Whisper tenga sitio.
        """
        import gc
        cabe = getattr(self, "lote_que_cabe", None)
        if cabe and len(textos) > cabe:   # ya se sabe que no cabe: a trozos, sin volver a probar
            audios, sr = [], None
            for g in range(0, len(textos), cabe):
                a, sr = self.sintetizar_lote(textos[g:g + cabe], voz, intento, semilla_lote)
                audios += a
            return audios, sr
        fallo = False
        try:
            return self._sintetizar_lote(textos, voz, intento, semilla_lote)
        except self.torch.cuda.OutOfMemoryError:
            if len(textos) == 1:
                raise
            fallo = True
            CRONO.contar("oom_qwen")
        finally:
            gc.collect()
            self.torch.cuda.empty_cache()
        if fallo:   # fuera del except, para que la excepción no retenga la memoria del intento fallido
            mitad = len(textos) // 2
            self.lote_que_cabe = max(1, mitad)   # y se recuerda para los lotes siguientes
            print(f"  (sin memoria con {len(textos)} frases a la vez; las parto en {mitad} y {len(textos) - mitad})")
            a1, sr = self.sintetizar_lote(textos[:mitad], voz, intento, semilla_lote)
            a2, _ = self.sintetizar_lote(textos[mitad:], voz, intento, semilla_lote)
            return a1 + a2, sr

    def _sintetizar_lote(self, textos, voz, intento, semilla_lote=None):
        from contextlib import nullcontext
        if self.peft is None:
            ctx = nullcontext()
        elif self.cfg["voces"][voz].get("adaptador"):
            self.peft.set_adapter(voz)
            ctx = nullcontext()
        else:
            ctx = self.peft.disable_adapter()
        with ctx:
            base = semilla_lote if semilla_lote is not None else semilla("|".join(textos), intento)
            self.torch.manual_seed(base + 104729 * self.cfg["motor"].get("ronda", 0))
            wavs, sr = self.tts.generate_voice_clone(
                text=list(textos), language=self.cfg["motor"]["idioma"], voice_clone_prompt=self.prompts[voz],
                non_streaming_mode=self.cfg["motor"]["non_streaming_mode"],
                max_new_tokens=max(tope_pasos(t) for t in textos), **self._muestreo(voz))
        return list(wavs), sr


def resumen_coste(raiz_episodios, cfg, destino=None):
    """Coste de todo lo generado: una fila por episodio (sumando su registro_tts.jsonl) y el total. Lo escribe en
    `destino` (coste_fabrica.md) si se pasa. No cuenta el tiempo de cargar modelos ni las sesiones paradas: eso está
    en las líneas «sesion» de coste_fabrica.jsonl."""
    filas = []
    for carpeta in sorted(Path(raiz_episodios).glob("*/*")):
        if not carpeta.is_dir():
            continue
        subs = [carpeta] + sorted(d for d in carpeta.iterdir() if d.is_dir() and (d / "registro_tts.jsonl").exists())
        for sub in subs:
            c = coste_de_carpeta(sub, cfg)
            if not c:
                continue
            audio = sum(f["segundos"] for f in leer_registro(sub).values()) / 60
            nombre = f"{carpeta.parent.name}/{carpeta.name}" + (f" ({sub.name})" if sub != carpeta else "")
            filas.append((nombre, audio, c["segundos_gpu"] / 60, c["unidades"], ", ".join(c["gpus"])))
    tot_a, tot_g, tot_u = (sum(f[i] for f in filas) for i in (1, 2, 3))
    lineas = ["# Coste de la fábrica", "", f"Generado por fabrica.resumen_coste el {time.strftime('%Y-%m-%d %H:%M')}. "
              "Unidades estimadas con las tarifas de voces.json («coste»); solo el tiempo de generación (sin cargar "
              "modelos ni ratos parados, que están en las líneas «sesion» de coste_fabrica.jsonl).", "",
              f"**Total: {len(filas)} carpetas · {tot_a:.1f} min de audio · {tot_g:.1f} min de GPU · "
              f"{tot_u:.2f} unidades**", "", "| Episodio | Audio (min) | GPU (min) | Unidades | GPU |",
              "|---|---|---|---|---|"]
    lineas += [f"| {n} | {a:.1f} | {g:.1f} | {u:.2f} | {gp} |" for n, a, g, u, gp in filas]
    texto = "\n".join(lineas) + "\n"
    if destino:
        Path(destino).write_text(texto, encoding="utf-8")
    return texto

