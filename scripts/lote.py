#!/usr/bin/env python3
"""La cola de publicación: apuntar escuchas y dar fecha a los episodios listos.

    python3 scripts/lote.py escucha 009 bueno "nota del autor"     # escuchado y bueno → listo para el cuaderno
    python3 scripts/lote.py escucha 011 revisar "2:15 acento raro"  # escuchado, hay que arreglarlo
    python3 scripts/lote.py cola                                    # qué está listo y qué tiene fecha
    python3 scripts/lote.py programar                               # da fecha (uno al día) a los listos sin fecha

`programar` pone a cada episodio listo sin fecha el día siguiente al último programado (o mañana, si ese ya pasó),
en orden de número, y deja escritos `publicacion` (fecha, audio_url, feed_guid) y el título y la descripción de
YouTube (la misma plantilla que el feed, scripts/descripcion.py). Al final imprime el valor de EPISODIOS para el
cuaderno de vídeo. No sube nada: eso lo hacen el cuaderno (R2 y YouTube) y la web (lib/episodes.ts).

Después de cualquier cambio: python3 scripts/indice.py y python3 scripts/tablero.py --web ../spanishnaval-web --r2.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from descripcion import de_episodio  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
AUDIO = "https://audio.spanishnav.al"


def episodios():
    """{número: (carpeta relativa 'año/NNN-slug', ruta del metadata, metadata)} de los episodios con número."""
    salida = {}
    for p in sorted((RAIZ / "episodios").glob("*/*/metadata.es.json")):
        m = json.loads(p.read_text(encoding="utf-8"))
        if m.get("numero"):
            salida[int(m["numero"])] = (p.parent.relative_to(RAIZ / "episodios").as_posix(), p, m)
    return salida


def guardar(p, m):
    p.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def listo(m):
    es = m.get("escucha") or {}
    return m.get("estado") == "montaje" and es.get("escuchado") and es.get("resultado") == "bueno"


def escucha(numero, resultado, feedback):
    if resultado not in ("bueno", "revisar"):
        sys.exit("El resultado es «bueno» o «revisar».")
    if not str(numero).isdigit():
        sys.exit(f"«{numero}» no es un número de episodio.")
    eps = episodios()
    if int(numero) not in eps:
        sys.exit(f"No hay episodio {numero} en el repo.")
    ep, p, m = eps[int(numero)]
    if m.get("estado") not in ("tts", "montaje"):
        sys.exit(f"{ep} está en «{m.get('estado')}»: solo se apunta la escucha de un audio hecho y sin publicar.")
    fecha = (m.get("publicacion") or {}).get("fecha")
    if resultado == "revisar" and fecha:
        sys.exit(f"{ep} ya tiene fecha ({fecha}) y puede estar cargado en la web y en YouTube: hay que desprogramarlo "
                 "a mano antes de mandarlo a revisar.")
    hoy = dt.date.today().isoformat()
    anterior = ((m.get("escucha") or {}).get("feedback") or "").strip()
    m["escucha"] = {"escuchado": True, "resultado": resultado, "fecha": hoy,
                    "feedback": (anterior + " | " if anterior else "") + f"{hoy}: {resultado}. {feedback}".strip()}
    m["estado"] = "montaje" if resultado == "bueno" else "tts"
    guardar(p, m)
    print(f"{ep}: escucha «{resultado}» → estado {m['estado']}")


def cola():
    eps = episodios()
    hoy = dt.date.today().isoformat()
    listos = [(n, e) for n, (e, _, m) in eps.items() if listo(m) and not (m.get("publicacion") or {}).get("fecha")]
    futuros = [(m["publicacion"]["fecha"], n, e) for n, (e, _, m) in eps.items()
               if (m.get("publicacion") or {}).get("fecha", "") >= hoy and m.get("estado") != "publicado"]
    print(f"Listos sin fecha ({len(listos)}): " + (", ".join(e for _, e in listos) or "ninguno"))
    print(f"Con fecha, sin publicar ({len(futuros)}):")
    for f, n, e in sorted(futuros):
        print(f"  {f}  {e}")


def programar():
    eps = episodios()
    hoy = dt.date.today()
    fechas = [dt.date.fromisoformat(m["publicacion"]["fecha"]) for _, _, m in eps.values()
              if (m.get("publicacion") or {}).get("fecha")]
    siguiente = max([hoy] + fechas) + dt.timedelta(days=1)
    originales = {re.sub(r"/+$", "", x["nav_al"]).split("/")[-1]: x.get("youtube_url", "")
                  for x in json.loads((RAIZ / "youtube-originales.json").read_text(encoding="utf-8"))["episodios"]}
    hechos = []
    for n in sorted(eps):
        ep, p, m = eps[n]
        pu = m.get("publicacion") or {}
        if not listo(m) or pu.get("fecha"):
            continue
        anio, nombre = ep.split("/")
        pu.update(fecha=siguiente.isoformat(), audio_url=f"{AUDIO}/{anio}/{nombre}.mp3",
                  feed_guid=f"spanishnav.al/{anio}/{m['slug']}")
        pu.setdefault("audio_bytes", 0)
        pu.setdefault("duracion_s", 0)
        m["publicacion"] = pu
        if not m["youtube"].get("url_original") and originales.get(m["slug"]):
            m["youtube"]["url_original"] = originales[m["slug"]]
        guardar(p, m)                                   # de_episodio lee url_original del metadata guardado
        m["youtube"]["titulo"], m["youtube"]["descripcion"] = de_episodio(ep)
        guardar(p, m)
        hechos.append((n, ep, siguiente))
        siguiente += dt.timedelta(days=1)
    if not hechos:
        print("No hay episodios listos sin fecha.")
        return
    for n, ep, f in hechos:
        print(f"  {f}  {ep}")
    print(f'\nEn el cuaderno de vídeo: EPISODIOS = "{", ".join(f"{n:03d}" for n, _, _ in hechos)}"')


if __name__ == "__main__":
    orden = sys.argv[1:] or ["cola"]
    if orden[0] == "escucha" and len(orden) >= 3:
        escucha(orden[1], orden[2], " ".join(orden[3:]))
    elif orden[0] == "cola":
        cola()
    elif orden[0] == "programar":
        programar()
    else:
        sys.exit(__doc__)
