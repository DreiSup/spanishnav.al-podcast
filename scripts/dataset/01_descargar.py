#!/usr/bin/env python3
"""Etapa 1: descarga + decodificación única.

Por fuente:
  fuentes/<id>/audio.<ext>       original de mayor calidad (yt-dlp, sin recodificar)
  fuentes/<id>/audio.info.json   metadatos de yt-dlp
  fuentes/<id>/fuente.json       url, título, fecha, duración, bitrate, sr, canales
  trabajo/<id>/orig.wav          PCM 16 bits, mono, a la frecuencia de la fuente
  trabajo/<id>/audio16k.wav      16 kHz mono, derivado de orig.wav (misma línea de tiempo)

Los cortes finales salen de orig.wav; ASR, alineado y diarización usan audio16k.wav.
Se salta lo que ya existe.

Uso: 01_descargar.py [id ...]   (sin ids: todas, por prioridad)
"""
import glob
import json
import subprocess
import sys
import time

from common import (cargar_fuentes, escribir_json, fuente_dir, log, trabajo_dir,
                    comprobar_recursos)


def ffprobe(path: str) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
                          "-show_streams", "-select_streams", "a:0", path],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st, fm = d["streams"][0], d["format"]
    return {"codec": st.get("codec_name"), "sr": int(st["sample_rate"]),
            "canales": int(st["channels"]), "bitrate": int(fm.get("bit_rate") or st.get("bit_rate") or 0),
            "duracion_s": round(float(fm["duration"]), 3)}


def procesar(f: dict) -> None:
    fid = f["id"]
    fd, td = fuente_dir(fid), trabajo_dir(fid)
    comprobar_recursos(min_ram_mb=800)
    existentes = [p for p in glob.glob(str(fd / "audio.*")) if not p.endswith(".json") and not p.endswith(".part")]
    if not existentes:
        log(f"{fid}: descargando {f['url_audio'][:80]}…")
        subprocess.run(["yt-dlp", "--no-progress", "-f", "bestaudio/best", "--no-playlist",
                        "--write-info-json", "-o", str(fd / "audio.%(ext)s"), f["url_audio"]],
                       check=True)
        existentes = [p for p in glob.glob(str(fd / "audio.*")) if not p.endswith(".json") and not p.endswith(".part")]
    audio = existentes[0]
    meta = ffprobe(audio)
    if not (fd / "fuente.json").exists():
        escribir_json(fd / "fuente.json", {
            "id": fid, "orden": f["orden"], "titulo": f["titulo"], "url_episodio": f["url_episodio"],
            "url_audio": f["url_audio"], "fecha": f["fecha"], "hablantes": f["hablantes"],
            "fichero": audio.rsplit("/", 1)[-1], **meta,
            "descargado_el": time.strftime("%Y-%m-%d"),
        })
    orig, a16 = td / "orig.wav", td / "audio16k.wav"
    if not orig.exists():
        log(f"{fid}: decodificando a WAV mono {meta['sr']} Hz")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", audio, "-ac", "1", "-c:a", "pcm_s16le",
                        str(orig) + ".tmp.wav"], check=True)
        (td / "orig.wav.tmp.wav").rename(orig)
    if not a16.exists():
        log(f"{fid}: derivando 16 kHz")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(orig), "-ar", "16000", "-ac", "1",
                        "-c:a", "pcm_s16le", str(a16) + ".tmp.wav"], check=True)
        (td / "audio16k.wav.tmp.wav").rename(a16)
    d_orig, d_16 = ffprobe(str(orig))["duracion_s"], ffprobe(str(a16))["duracion_s"]
    log(f"{fid}: OK {meta['codec']} {meta['bitrate']//1000}k {meta['sr']} Hz {meta['canales']}ch "
        f"dur {meta['duracion_s']:.0f}s | orig {d_orig:.2f}s 16k {d_16:.2f}s")


def main():
    fuentes = sorted(cargar_fuentes(), key=lambda f: f["prioridad"])
    ids = sys.argv[1:]
    if ids:
        fuentes = [f for f in fuentes if f["id"] in ids]
    for f in fuentes:
        procesar(f)


if __name__ == "__main__":
    main()
