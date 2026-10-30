"""La fábrica de voz: de un transcript.es.json a un clip por intervención en Drive.

Para cada bloque de hablante del transcript sale un clip, `001naval.wav`, `002nivi.wav`…, en la carpeta
`tts/` del episodio. Cada frase se genera por separado, se revisa con Whisper (y se repite si no dice el
texto), se le recortan los silencios y se une a las demás con la pausa fijada en voces.json.

Junto a `tts/`, en la carpeta del episodio:
  informe_tts.md       duración, reintentos y las frases sospechosas, con el segundo donde están
  registro_tts.jsonl   una línea por clip, con el detalle de cada frase
  borrador_tts.wav     todos los clips seguidos, para una escucha rápida antes de Audacity

Este módulo no sabe nada de Qwen: recibe una función `sintetizar(texto, voz, intento)` y un ASR. El motor
real está en `MotorQwen`; las pruebas usan uno falso.
"""
import json
import re
import time
import zlib
from pathlib import Path

import numpy as np
import soundfile as sf

RAIZ = Path(__file__).resolve().parent
VOCES_JSON = RAIZ / "voces.json"
BORDE_INICIO, BORDE_FINAL = 0.05, 0.15     # silencio al principio y al final de cada clip
RECORTE_INICIO, RECORTE_FINAL = 0.02, 0.05  # lo que se deja a cada frase antes de unirla
SILENCIO_BORRADOR = 0.6                     # entre intervenciones, en el borrador


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


# ---------------------------------------------------------------- generación

def semilla(texto, intento):
    return zlib.crc32(texto.encode("utf-8")) + 7919 * intento


def revisar(texto, audio, sr, asr, cfg_ver):
    """(ok, errores, palabras, sobra_final, transcripción) de una frase generada."""
    import medir
    hyp, _, fin = asr.transcribe_audio(audio, sr)
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


def generar_episodio(plan, sintetizar, asr, carpeta, cfg, avisar=print):
    """Genera los clips que falten en <carpeta>/tts/ y reescribe el informe y el borrador.

    Lo que ya existe no se repite: si se corta, se vuelve a lanzar y sigue por donde iba.
    """
    pausa = cfg["ritmo"]["pausa_max"]
    cfg_ver = cfg["verificacion"]
    tts_dir = Path(carpeta) / "tts"
    tts_dir.mkdir(parents=True, exist_ok=True)
    registro = Path(carpeta) / "registro_tts.jsonl"
    hechos = {}
    if registro.exists():
        for l in registro.read_text(encoding="utf-8").splitlines():
            if l.strip():
                f = json.loads(l)
                hechos[f["fichero"]] = f
    t_total, s_total = 0.0, 0.0
    for p in plan:
        wav = tts_dir / p["fichero"]
        if wav.exists():
            continue
        t0 = time.time()
        trozos, detalle, sr, cursor = [], [], None, BORDE_INICIO
        hueco = max(0.0, pausa - RECORTE_INICIO - RECORTE_FINAL)
        for k, frase in enumerate(p["frases"]):
            r = generar_frase(frase, p["voz"], sintetizar, asr, cfg_ver, pausa)
            sr = sr or r["sr"]
            if k:
                trozos.append(np.zeros(int(sr * hueco), dtype=np.float32))
                cursor += hueco
            trozos.append(r["audio"])
            detalle.append({"k": k, "inicio_s": round(cursor, 2), "texto": frase, "intentos": r["intentos"],
                            "ok": r["ok"], "errores": r.get("errores"), "sobra_final": r.get("sobra_final"),
                            "transcripcion": r.get("transcripcion")})
            cursor += len(r["audio"]) / sr
        audio = np.concatenate([np.zeros(int(sr * BORDE_INICIO), dtype=np.float32), *trozos,
                                np.zeros(int(sr * BORDE_FINAL), dtype=np.float32)])
        pico = float(np.abs(audio).max()) if audio.size else 0.0
        if pico > 1.0:
            audio = audio / pico * 0.99
        tmp = tts_dir / f".{p['fichero']}.tmp.wav"
        sf.write(str(tmp), audio, sr, subtype="PCM_16")
        tmp.rename(wav)
        seg, dt = len(audio) / sr, time.time() - t0
        t_total, s_total = t_total + dt, s_total + seg
        fila = {"fichero": p["fichero"], "bloque": p["bloque"], "voz": p["voz"], "segundos": round(seg, 2),
                "segundos_generacion": round(dt, 1), "sr": sr, "frases": detalle,
                "adaptador": cfg["voces"][p["voz"]].get("adaptador")}
        with registro.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(fila, ensure_ascii=False) + "\n")
        hechos[p["fichero"]] = fila
        malas = sum(1 for d in detalle if d["ok"] is False)
        avisar(f"  {p['fichero']}: {seg:6.1f} s en {dt:6.1f} s · {len(detalle)} frases"
               + (f" · {malas} sospechosas" if malas else ""))
    if s_total:
        avisar(f"Generado: {s_total / 60:.1f} min de audio en {t_total / 60:.1f} min "
               f"({t_total / s_total:.2f} s de GPU por segundo de audio)")
    escribir_informe(plan, hechos, carpeta)
    escribir_borrador(plan, tts_dir, Path(carpeta) / "borrador_tts.wav")
    return hechos


def escribir_informe(plan, hechos, carpeta):
    total = sum(f["segundos"] for f in hechos.values())
    lineas = [f"# Clips de TTS — {Path(carpeta).name}", "",
              f"{len(hechos)} de {len(plan)} clips · {total / 60:.1f} min. Las frases **sospechosas** no pasaron la "
              "revisión de Whisper ni con los reintentos: mira primero ahí en Audacity (el segundo es el de su clip).",
              "", "| Clip | Voz | Duración | Frases | Reintentos | Sospechosas |", "|---|---|---|---|---|---|"]
    sospechas = []
    for p in plan:
        f = hechos.get(p["fichero"])
        if not f:
            lineas.append(f"| {p['fichero']} | {p['voz']} | — | {len(p['frases'])} | — | sin generar |")
            continue
        reint = sum(d["intentos"] - 1 for d in f["frases"])
        malas = [d for d in f["frases"] if d["ok"] is False]
        lineas.append(f"| {p['fichero']} | {f['voz']} | {f['segundos']:.1f} s | {len(f['frases'])} | {reint} | "
                      f"{len(malas) or ''} |")
        sospechas += [(p["fichero"], d) for d in malas]
    if sospechas:
        lineas += ["", "## Frases sospechosas", ""]
        for fichero, d in sospechas:
            lineas += [f"- **{fichero}**, segundo {d['inicio_s']:.1f} ({d['errores']} errores, "
                       f"{d['sobra_final']} s tras la última palabra)",
                       f"  - Texto: {d['texto']}", f"  - Whisper oyó: {d['transcripcion']}"]
    (Path(carpeta) / "informe_tts.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def escribir_borrador(plan, tts_dir, destino):
    trozos, sr = [], None
    for p in plan:
        wav = tts_dir / p["fichero"]
        if not wav.exists():
            continue
        audio, sr_clip = sf.read(str(wav), dtype="float32")
        sr = sr or sr_clip
        trozos += [audio, np.zeros(int(sr * SILENCIO_BORRADOR), dtype=np.float32)]
    if trozos:
        sf.write(str(destino), np.concatenate(trozos[:-1]), sr, subtype="PCM_16")


# ---------------------------------------------------------------- el motor real

class MotorQwen:
    """Qwen3-TTS base con un adaptador LoRA por voz (los que tengan), en modo solo timbre."""

    def __init__(self, cfg, voces, raiz_voces):
        import torch
        from qwen_tts import Qwen3TTSModel
        self.torch, self.cfg = torch, cfg
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
        self.prompts = {v: self.tts.create_voice_clone_prompt(ref_audio=str(Path(raiz_voces) / cfg["voces"][v]["ref"]),
                                                              x_vector_only_mode=True)
                        for v in voces}
        print(f"Qwen cargado ({dtype}); con LoRA: {con_lora or 'ninguna'}; sin LoRA: "
              f"{[v for v in voces if v not in con_lora] or 'ninguna'}")

    def sintetizar(self, texto, voz, intento):
        from contextlib import nullcontext
        if self.peft is None:
            ctx = nullcontext()
        elif self.cfg["voces"][voz].get("adaptador"):
            self.peft.set_adapter(voz)
            ctx = nullcontext()
        else:
            ctx = self.peft.disable_adapter()
        with ctx:
            self.torch.manual_seed(semilla(texto, intento))
            wavs, sr = self.tts.generate_voice_clone(
                text=texto, language=self.cfg["motor"]["idioma"], voice_clone_prompt=self.prompts[voz],
                non_streaming_mode=self.cfg["motor"]["non_streaming_mode"])
        return wavs[0], sr
