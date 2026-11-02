"""Utilidades compartidas por las etapas del pipeline de datasets de voz.

Contrato de rutas (todo fuera del repo, bajo ~/naval-datos):
  fuentes/<id>/      descarga original + fuente.json
  trabajo/<id>/      orig.wav, audio16k.wav y los JSON de cada etapa
  oficiales/         transcripts de nav.al (solo comprobación cruzada)
  speaker_refs/      clips de referencia (Fase 1a)
  datasets/          datasets de fine-tuning (parte 2)
  logs/              logs de etapas y del vigilante

Ninguna ruta lleva espacios, paréntesis ni "+".
"""
import contextlib
import fcntl
import json
import os
import shutil
import sys
import time
from pathlib import Path

DATOS = Path(os.environ.get("NAVAL_DATOS", Path.home() / "naval-datos"))
VENV = DATOS / "venv"
REPO_DATASET = Path(__file__).resolve().parent
FUENTES_JSON = REPO_DATASET / "fuentes_podcast.json"

FUENTES = DATOS / "fuentes"
TRABAJO = DATOS / "trabajo"
OFICIALES = DATOS / "oficiales"
SPEAKER_REFS = DATOS / "speaker_refs"
DATASETS = DATOS / "datasets"
LOGS = DATOS / "logs"
GPU_LOCK = DATOS / "gpu.lock"

# Umbrales del guardián de recursos
MIN_RAM_MB = 2500
MIN_DISCO_GB = 15

# Naval en estas fuentes es "naval_kapil" (su tono con Kapil Gupta) y no entra en "naval"
SOLO_KAPIL = ("nav072", "nav001", "nav002", "nav003", "nav004")
HABLANTES = ["naval", "nivi", "brett", "deutsch", "kapil", "vitalik", "ridley",
             "hodak", "rauch", "scholl", "qureshi"]


def fuente_dir(fid: str) -> Path:
    d = FUENTES / fid
    d.mkdir(parents=True, exist_ok=True)
    return d


def trabajo_dir(fid: str) -> Path:
    d = TRABAJO / fid
    d.mkdir(parents=True, exist_ok=True)
    return d


def cargar_fuentes() -> list[dict]:
    with open(FUENTES_JSON, encoding="utf-8") as f:
        return json.load(f)["fuentes"]


def fuente(fid: str) -> dict:
    for f in cargar_fuentes():
        if f["id"] == fid:
            return f
    raise KeyError(f"fuente desconocida: {fid}")


def leer_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def escribir_json(path: Path, data) -> None:
    """Escritura atómica: un corte a medias nunca deja un JSON roto."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def ram_disponible_mb() -> int:
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    return 0


def disco_libre_gb(path: Path = DATOS) -> float:
    return shutil.disk_usage(path).free / 2**30


def comprobar_recursos(min_ram_mb: int = MIN_RAM_MB, min_disco_gb: float = MIN_DISCO_GB,
                       esperar_s: int = 300) -> None:
    """Espera hasta `esperar_s` a que haya RAM y disco; si no, aborta la etapa."""
    t0 = time.time()
    while True:
        ram, disco = ram_disponible_mb(), disco_libre_gb()
        if ram >= min_ram_mb and disco >= min_disco_gb:
            return
        if time.time() - t0 > esperar_s:
            sys.exit(f"RECURSOS INSUFICIENTES: RAM {ram} MB (min {min_ram_mb}), "
                     f"disco {disco:.1f} GB (min {min_disco_gb})")
        log(f"esperando recursos: RAM {ram} MB, disco {disco:.1f} GB")
        time.sleep(15)


def asegurar_entorno_cuda() -> None:
    """ctranslate2 necesita cuBLAS/cuDNN del venv en LD_LIBRARY_PATH.

    El enlazador dinámico solo lee LD_LIBRARY_PATH al arrancar el proceso, así que si
    falta se re-ejecuta el script con el entorno corregido.
    """
    nv = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" \
        / "site-packages" / "nvidia"
    libs = [str(nv / "cublas" / "lib"), str(nv / "cudnn" / "lib")]
    actual = os.environ.get("LD_LIBRARY_PATH", "")
    if all(l in actual.split(":") for l in libs):
        return
    os.environ["LD_LIBRARY_PATH"] = ":".join(libs + ([actual] if actual else []))
    os.execv(sys.executable, [sys.executable] + sys.argv)


@contextlib.contextmanager
def candado_gpu():
    """Un único proceso pesado (GPU o torch) a la vez en toda la máquina."""
    GPU_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(GPU_LOCK, "w") as fh:
        log("esperando candado GPU…")
        fcntl.flock(fh, fcntl.LOCK_EX)
        log("candado GPU adquirido")
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def token_hf() -> str:
    tok = os.environ.get("HF_TOKEN")
    if tok:
        return tok
    p = Path.home() / ".cache" / "huggingface" / "token"
    return p.read_text().strip()
