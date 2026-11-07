"""¿Puede Whisper large-v3-turbo sustituir a large-v3 en la revisión de la fábrica?

La revisión no cambia el audio: solo decide qué frases se repiten. Así que basta con comprobar que el modelo nuevo toma
las mismas decisiones que el de siempre sobre frases ya generadas, y que caza igual de bien los fallos que la revisión
existe para cazar. El cuaderno `fabrica/comparar_whisper.ipynb` lo hace en una T4 (unos 15 min, ~0,5 unidades):

1. Toma frases reales de episodios ya generados (`tts/frases/*.wav` y su texto del registro), con todas las que
   quedaron sospechosas.
2. Les añade **averías fabricadas**, que deberían marcarse como malas:
   - «cola»: tras la frase, 1,5 s de otra frase (lo que deja una alucinación al final);
   - «corte»: solo el primer 55 % de la frase (el TTS se calla antes de tiempo).
3. Las oyen los dos modelos, con la misma regla de la fábrica (`fabrica.revisar` y `voces.json` → verificacion), y
   compara decisiones, errores, el silencio final y la velocidad.

Veredicto: turbo vale si coincide en al menos el 97 % de las frases reales y no caza menos averías que large-v3.
"""
import random

import numpy as np

import fabrica

SR = 16000


def frases_de(carpetas, n, semilla=0):
    """Hasta `n` frases reales de esas carpetas de episodio: todas las sospechosas y el resto al azar (fijo)."""
    todas = []
    for carpeta in carpetas:
        tts = carpeta / "tts"
        for fichero, fila in fabrica.leer_registro(carpeta).items():
            for d in fila.get("frases", []):
                ruta = fabrica.ruta_frase(tts, fichero, d["k"])
                if ruta.exists():
                    todas.append({"episodio": carpeta.name, "clip": fichero, "k": d["k"] + 1, "texto": d["texto"],
                                  "ruta": ruta, "ok_registro": d.get("ok"), "tipo": "real"})
    malas = [f for f in todas if f["ok_registro"] is False]
    resto = [f for f in todas if f["ok_registro"] is not False]
    random.Random(semilla).shuffle(resto)
    return malas + resto[:max(0, n - len(malas))]


def con_averias(items, n, semilla=0):
    """Las frases reales (con su audio a 16 kHz en `audio`) más `n` averías fabricadas a partir de ellas."""
    rng = random.Random(semilla)
    reales = [i for i in items if i["tipo"] == "real" and len(i["audio"]) > SR * 2]
    averias = []
    for j in range(n):
        base = reales[j % len(reales)]
        if j % 2 == 0:
            otra = reales[rng.randrange(len(reales))]["audio"]
            mitad = len(otra) // 2
            trozo = otra[max(0, mitad - int(0.75 * SR)): mitad + int(0.75 * SR)]
            audio = np.concatenate([base["audio"], np.zeros(int(0.15 * SR), np.float32), trozo])
            tipo = "cola"
        else:
            audio = base["audio"][: int(len(base["audio"]) * 0.55)]
            tipo = "corte"
        averias.append({**base, "audio": audio.astype(np.float32), "tipo": tipo, "ok_registro": False})
    return items + averias


def decidir(items, oidos, cfg_ver):
    """La decisión de la fábrica (fabrica.revisar) para cada item, con lo que oyó un modelo."""
    salida = []
    for item, oido in zip(items, oidos):
        ok, errores, palabras, sobra, hyp = fabrica.revisar(item["texto"], item["audio"], SR, None, cfg_ver, oido)
        salida.append({"ok": ok, "errores": errores, "sobra": sobra, "hyp": hyp})
    return salida


def informe(items, a, b, tiempo_a, tiempo_b, nombre_a, nombre_b):
    """(texto markdown, turbo_vale) comparando las decisiones `a` (modelo de siempre) y `b` (candidato)."""
    reales = [n for n, i in enumerate(items) if i["tipo"] == "real"]
    averias = [n for n, i in enumerate(items) if i["tipo"] != "real"]
    iguales = sum(a[n]["ok"] == b[n]["ok"] for n in reales)
    acuerdo = iguales / max(1, len(reales))
    caza_a = sum(a[n]["ok"] is False for n in averias)
    caza_b = sum(b[n]["ok"] is False for n in averias)
    dif_sobra = [abs(a[n]["sobra"] - b[n]["sobra"]) for n in reales]
    audio_s = sum(len(i["audio"]) for i in items) / SR
    vale = acuerdo >= 0.97 and caza_b >= caza_a
    lineas = [
        f"# {nombre_b} frente a {nombre_a}", "",
        f"**Veredicto: {'VALE' if vale else 'NO VALE'}** (pide ≥ 97 % de decisiones iguales en frases reales y cazar "
        "al menos las mismas averías).", "",
        "| | " + nombre_a + " | " + nombre_b + " |", "|---|---|---|",
        f"| Frases reales que da por buenas | {sum(a[n]['ok'] for n in reales)} de {len(reales)} | "
        f"{sum(b[n]['ok'] for n in reales)} de {len(reales)} |",
        f"| Averías cazadas | {caza_a} de {len(averias)} | {caza_b} de {len(averias)} |",
        f"| Tiempo de GPU | {tiempo_a:.0f} s ({tiempo_a / audio_s:.2f} s por s de audio) | "
        f"{tiempo_b:.0f} s ({tiempo_b / audio_s:.2f} s por s de audio) |", "",
        f"Decisiones iguales en frases reales: **{iguales} de {len(reales)} ({100 * acuerdo:.1f} %)**. "
        f"Diferencia media del silencio final: {np.mean(dif_sobra) if dif_sobra else 0:.2f} s. "
        f"Audio oído: {audio_s / 60:.1f} min por modelo.", "",
    ]
    distintas = [n for n in range(len(items)) if a[n]["ok"] != b[n]["ok"]]
    if distintas:
        lineas += ["## Donde no coinciden", ""]
        for n in distintas:
            i = items[n]
            lineas += [f"- **{i['tipo']}** · {i['episodio']} · {i['clip']} frase {i['k']}: {nombre_a} "
                       f"{'bien' if a[n]['ok'] else 'mal'} ({a[n]['errores']} err., {a[n]['sobra']} s), {nombre_b} "
                       f"{'bien' if b[n]['ok'] else 'mal'} ({b[n]['errores']} err., {b[n]['sobra']} s)",
                       f"  - Texto: {i['texto']}", f"  - {nombre_a}: {a[n]['hyp']}", f"  - {nombre_b}: {b[n]['hyp']}"]
    return "\n".join(lineas) + "\n", vale
