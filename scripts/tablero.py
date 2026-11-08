#!/usr/bin/env python3
"""Genera tablero.json: el estado de cada episodio del catálogo, para el tablero visual.

Lee catalogo.json y los metadata.es.json del repo. Opcionalmente:
  --web <ruta>   repo de la web: marca qué episodios están cargados en lib/episodes.ts
  --r2           comprueba con HEAD que el audio de cada episodio con fecha está en R2

Uso:  python3 scripts/tablero.py [--web ../spanishnaval-web] [--r2]
Escribe tablero.json en la raíz del repo. No toca nada más.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Las etapas, en el orden del proceso. La primera que no se cumple es donde está el episodio.
ETAPAS = [
    ("sin_traducir", "Sin traducir"),
    ("traducido", "Traducido, falta el audio"),
    ("sin_escuchar", "Audio hecho, falta escucharlo"),
    ("revisar", "Escuchado: hay que arreglarlo"),
    ("listo", "Listo, sin fecha"),
    ("programado", "Programado"),
    ("publicado", "Publicado"),
]


def segundos_estimados(carpeta):
    """Duración estimada del audio: caracteres del español a 15 c/s (ritmo medido de la fábrica)."""
    try:
        t = json.load(open(os.path.join(carpeta, "transcript.es.json"), encoding="utf-8"))
    except FileNotFoundError:
        return 0
    return round(sum(len(f) for b in t.get("contenido", []) for f in b.get("frases", [])) / 15)


def en_r2(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "spanishnav-tablero/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--web", help="ruta del repo de la web")
    ap.add_argument("--r2", action="store_true", help="comprobar los audios en R2")
    a = ap.parse_args()

    hoy = dt.datetime.now(dt.timezone.utc)
    cat = json.load(open(os.path.join(RAIZ, "catalogo.json"), encoding="utf-8"))

    meta = {}
    for p in glob.glob(os.path.join(RAIZ, "episodios", "*", "*", "metadata.es.json")):
        carpeta = os.path.dirname(p)
        nombre = os.path.basename(carpeta)
        slug = re.sub(r"^(\d{3}|extra)-", "", nombre)
        meta[slug] = (carpeta, json.load(open(p, encoding="utf-8")))

    web = set()
    if a.web:
        texto = open(os.path.join(a.web, "lib", "episodes.ts"), encoding="utf-8").read()
        web = set(re.findall(r"slug:\s*'([^']+)'", texto))

    filas = []
    for e in cat["episodios"]:
        slug = e["url"].rstrip("/").split("/")[-1]
        fila = {
            "orden": e["orden"],
            "numero": None,
            "anio": None,
            "slug": slug,
            "titulo_en": e["titulo"],
            "titulo_es": "",
            "etapa": "sin_traducir",
            "fecha": "",
            "minutos": 0,
            "web": slug in web,
            "r2": None,
            "youtube": "",
            "nota": "",
        }
        if slug in meta:
            carpeta, m = meta[slug]
            pu = m.get("publicacion") or {}
            es = m.get("escucha") or {}
            fila.update(
                numero=m.get("numero"),
                anio=m.get("anio"),
                titulo_es=m.get("titulo_es", ""),
                fecha=pu.get("fecha", ""),
                minutos=round((pu.get("duracion_s") or segundos_estimados(carpeta)) / 60, 1),
                youtube=(m.get("youtube") or {}).get("url", ""),
                nota=es.get("feedback", "") if es.get("resultado") == "revisar" else "",
            )
            estado = m.get("estado")
            if estado == "publicado":
                fila["etapa"] = "publicado"
            elif fila["fecha"]:
                fila["etapa"] = "programado"
            elif estado == "montaje":
                fila["etapa"] = "listo"
            elif estado == "tts":
                fila["etapa"] = "revisar" if es.get("resultado") == "revisar" else "sin_escuchar"
            else:
                fila["etapa"] = "traducido"
            if a.r2 and fila["fecha"] and pu.get("audio_url"):
                fila["r2"] = en_r2(pu["audio_url"])
        filas.append(fila)

    # Avisos: lo que rompe la publicación diaria si nadie lo mira.
    avisos = []
    hoy_s = hoy.date().isoformat()
    futuros = sorted(f["fecha"] for f in filas if f["etapa"] == "programado" and f["fecha"] >= hoy_s)
    if futuros:
        ultimo = dt.date.fromisoformat(futuros[-1])
        dias = (ultimo - hoy.date()).days
        avisos.append({
            "nivel": "bad" if dias < 3 else "warn" if dias < 7 else "ok",
            "texto": f"Hay episodios programados hasta el {ultimo.isoformat()} ({dias} días). "
                     "Después no sale nada si no se programan más.",
        })
    else:
        avisos.append({"nivel": "bad", "texto": "No hay ningún episodio programado a partir de hoy."})
    if a.web:
        sin_web = [f for f in filas if f["etapa"] == "programado" and not f["web"]]
        if sin_web:
            primero = min(f["fecha"] for f in sin_web)
            avisos.append({
                "nivel": "bad" if primero <= (hoy.date() + dt.timedelta(days=1)).isoformat() else "warn",
                "texto": f"{len(sin_web)} programados no están cargados en la web; el primero sale el {primero}.",
            })
    if a.r2:
        sin_r2 = [f for f in filas if f["fecha"] and f["r2"] is False]
        if sin_r2:
            avisos.append({"nivel": "bad", "texto": f"{len(sin_r2)} episodios con fecha no tienen el audio en R2."})
    pub_sin_yt = [f for f in filas if f["etapa"] == "publicado" and not f["youtube"]]
    if pub_sin_yt:
        avisos.append({"nivel": "warn", "texto": f"{len(pub_sin_yt)} publicados sin el enlace de YouTube apuntado."})

    resumen = []
    for clave, nombre in ETAPAS:
        fs = [f for f in filas if f["etapa"] == clave]
        resumen.append({
            "etapa": clave, "nombre": nombre, "orden": len(resumen) + 1,
            "episodios": len(fs), "horas": round(sum(f["minutos"] for f in fs) / 60, 1),
        })

    salida = {
        "generado": hoy.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "comprobado_web": bool(a.web),
        "comprobado_r2": a.r2,
        "resumen": resumen,
        "avisos": avisos,
        "episodios": filas,
    }
    with open(os.path.join(RAIZ, "tablero.json"), "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for r in resumen:
        print(f"{r['nombre']:<34} {r['episodios']:>4}  {r['horas']:>5} h")
    for av in avisos:
        print(f"[{av['nivel']}] {av['texto']}")


if __name__ == "__main__":
    main()
