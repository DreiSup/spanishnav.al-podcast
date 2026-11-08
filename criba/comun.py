"""Piezas comunes de los cuadernos de la criba (fase 1a de docs/fabrica-de-voz.md).

Cada cuaderno de motor solo define cómo se sintetiza una frase; esto se encarga del resto:
montar Drive, comprobar referencias y frases, generar los 55 items saltándose los que ya
existen, dejar registro y desconectar la GPU al terminar.

Rutas en Drive:
    fine_tunned_naval/speaker_refs/<ref>/<ref>_refNN.wav + .txt     entrada
    fine_tunned_naval/outputs/criba/<variante>/<item>.wav           salida
    fine_tunned_naval/outputs/criba/<variante>/registro.jsonl       una línea por item
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

DRIVE = Path("/content/drive/MyDrive/fine_tunned_naval")
REFS = DRIVE / "speaker_refs"
SALIDA = DRIVE / "outputs" / "criba"
FRASES = Path(__file__).resolve().parent / "frases.json"

# Clip de referencia que se usa por defecto: el de ~12 s. Es el punto medio que todos los
# motores aceptan (XTTS rinde hasta ~11 s; Chatterbox usa los primeros 6-10 s).
REF_POR_DEFECTO = "ref02"
SEMILLA = 1234


def montar_drive():
    if not Path("/content/drive/MyDrive").is_dir():
        from google.colab import drive
        drive.mount("/content/drive")


def cargar_items(voces=None):
    datos = json.loads(FRASES.read_text(encoding="utf-8"))
    items = datos["items"]
    if voces is not None:
        items = [it for it in items if it["voz"] in voces]
    return items, datos["silencio_entre_frases_ms"]


def comprobar(items, slot=REF_POR_DEFECTO):
    """Comprueba que cada referencia necesaria existe y tiene transcripción.

    Devuelve {ref: {"wav": ruta, "texto": str, "segundos": float}}. Si falta algo, imprime
    RESULTADO: REVISAR y lanza un error antes de que se cargue ningún modelo.
    """
    import soundfile as sf

    necesarias = sorted({it["ref"] for it in items})
    refs, problemas = {}, []
    print(f"Referencias ({slot}) en {REFS}:")
    for ref in necesarias:
        wav = REFS / ref / f"{ref}_{slot}.wav"
        txt = REFS / ref / f"{ref}_{slot}.txt"
        if not wav.is_file():
            problemas.append(f"falta {wav}")
            print(f"  {ref:12s} FALTA el wav")
            continue
        if not txt.is_file() or not txt.read_text(encoding="utf-8").strip():
            problemas.append(f"falta o está vacío {txt}")
            print(f"  {ref:12s} FALTA el txt")
            continue
        info = sf.info(str(wav))
        refs[ref] = {
            "wav": str(wav),
            "texto": txt.read_text(encoding="utf-8").strip(),
            "segundos": info.duration,
        }
        aviso = "" if 4 <= info.duration <= 30 else "  <- duración rara"
        print(f"  {ref:12s} {info.duration:5.1f} s  {info.samplerate} Hz  {info.channels} canal(es){aviso}")
    print(f"Items a generar: {len(items)}")
    if problemas:
        print("RESULTADO: REVISAR")
        for p in problemas:
            print("  -", p)
        raise SystemExit("Faltan referencias. No sigas: no se ha gastado nada en cargar modelos.")
    print("RESULTADO: OK")
    return refs


def fijar_semilla(semilla):
    random.seed(semilla)
    np.random.seed(semilla)
    try:
        import torch
        torch.manual_seed(semilla)
        torch.cuda.manual_seed_all(semilla)
    except ImportError:
        pass


def _a_mono_float(audio):
    try:
        import torch
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().float().cpu().numpy()
    except ImportError:
        pass
    audio = np.asarray(audio, dtype=np.float32).squeeze()
    if audio.ndim > 1:
        audio = audio.mean(axis=0)
    return audio


def generar(variante, sintetizar, items, refs, silencio_ms, params=None):
    """Genera todos los items de una variante.

    `sintetizar(texto, ref)` recibe una frase y el dict de su referencia y devuelve
    (audio, sample_rate). Los items que ya existen en Drive se saltan: si la sesión se
    corta, al relanzar no se paga dos veces. Un error en un item se registra y se sigue.
    """
    import soundfile as sf

    destino = SALIDA / variante
    destino.mkdir(parents=True, exist_ok=True)
    registro = destino / "registro.jsonl"
    (destino / "parametros.json").write_text(
        json.dumps({"variante": variante, "params": params or {}, "silencio_ms": silencio_ms,
                    "semilla": SEMILLA, "refs": {k: Path(v["wav"]).name for k, v in refs.items()}},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    hechos = saltados = errores = 0
    t_total = time.time()
    for n, it in enumerate(items):
        wav_out = destino / f"{it['id']}.wav"
        if wav_out.exists():
            saltados += 1
            continue
        fijar_semilla(SEMILLA + n)
        t0 = time.time()
        try:
            trozos, sr = [], None
            for frase in it["frases"]:
                audio, sr_frase = sintetizar(frase, refs[it["ref"]])
                audio = _a_mono_float(audio)
                if sr is None:
                    sr = sr_frase
                trozos.append(audio)
                trozos.append(np.zeros(int(sr * silencio_ms / 1000), dtype=np.float32))
            audio = np.concatenate(trozos[:-1])
            pico = float(np.abs(audio).max()) if audio.size else 0.0
            if pico > 1.0:
                audio = audio / pico * 0.99
            tmp = destino / f".{it['id']}.tmp.wav"
            sf.write(str(tmp), audio, sr, subtype="PCM_16")
            tmp.rename(wav_out)
            fila = {"id": it["id"], "ref": it["ref"], "ok": True, "segundos_audio": round(len(audio) / sr, 2),
                    "segundos_generacion": round(time.time() - t0, 2), "sr": sr, "pico_original": round(pico, 3)}
            hechos += 1
            print(f"  {it['id']}  {fila['segundos_audio']:6.1f} s de audio en {fila['segundos_generacion']:5.1f} s")
        except Exception as e:  # un item roto no debe tirar la tanda entera
            fila = {"id": it["id"], "ref": it["ref"], "ok": False, "error": f"{type(e).__name__}: {e}"[:500]}
            errores += 1
            print(f"  {it['id']}  ERROR {fila['error'][:120]}")
        with registro.open("a", encoding="utf-8") as f:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")
    minutos = (time.time() - t_total) / 60
    print(f"{variante}: {hechos} generados, {saltados} ya existían, {errores} con error, {minutos:.1f} min")
    return {"hechos": hechos, "saltados": saltados, "errores": errores}


def guardar_entorno(variante, paquetes):
    """Deja en Drive las versiones exactas de lo instalado, para poder repetir la prueba."""
    from importlib.metadata import distributions
    destino = SALIDA / variante
    destino.mkdir(parents=True, exist_ok=True)
    claves = {p.lower().replace("_", "-") for p in paquetes}
    lineas = sorted(f"{d.metadata['Name']}=={d.version}" for d in distributions()
                    if (d.metadata["Name"] or "").lower().replace("_", "-") in claves)
    gpu = ""
    try:
        gpu = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                             capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        pass
    (destino / "entorno.json").write_text(json.dumps({"python": sys.version, "gpu": gpu, "paquetes": lineas},
                                                     ensure_ascii=False, indent=2), encoding="utf-8")
    print("Entorno:", gpu, "|", ", ".join(lineas))


def liberar():
    """Vacía la memoria de la GPU. Antes, borra tú las variables del modelo (del modelo)."""
    import gc
    gc.collect()
    try:
        import torch
        torch.cuda.empty_cache()
    except ImportError:
        pass


def desconectar():
    """Sube a Drive lo pendiente y suelta la GPU para que deje de consumir unidades.

    Colab escribe en Drive a través de una caché local que se sube en segundo plano. Si se
    suelta la GPU sin vaciarla, lo generado en los últimos minutos se pierde.
    """
    from google.colab import drive, runtime
    print("Subiendo a Drive lo pendiente (puede tardar unos minutos)...")
    drive.flush_and_unmount()
    print("Drive al día. Desconectando el entorno para no gastar más unidades...")
    runtime.unassign()
