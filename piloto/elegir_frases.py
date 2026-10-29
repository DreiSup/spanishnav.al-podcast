#!/usr/bin/env python3
"""Elige las frases en español con las que los profesores generan el audio sintético.

    python3 piloto/elegir_frases.py

Salen de los transcript.es.json del repo, siempre de bloques de Naval, con estas reglas:

  - entre 60 y 220 caracteres: clips de unos 4 a 14 s, el rango que usa el dataset real;
  - nunca una frase de la criba (criba/frases.json): esas son el conjunto de evaluación;
  - sin repetidas (052-rich es un recopilatorio y repite frases de otros episodios);
  - reparto proporcional entre episodios y semilla fija, para que salga siempre lo mismo.
"""
import json
import random
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
N = 400
SEMILLA = 2026

criba = {f for it in json.loads((RAIZ / "criba" / "frases.json").read_text(encoding="utf-8"))["items"]
         for f in it["frases"]}
vistas, por_episodio = set(), defaultdict(list)
for ruta in sorted(RAIZ.glob("episodios/*/*/transcript.es.json")):
    d = json.loads(ruta.read_text(encoding="utf-8"))
    for b in d["contenido"]:
        if b["speaker"] != "Naval":
            continue
        for n, frase in enumerate(b["frases"]):
            if not 60 <= len(frase) <= 220 or frase in criba or frase in vistas:
                continue
            vistas.add(frase)
            por_episodio[d["episodio"]].append({"origen": f"{d['episodio']}#{b['id']}/{n}", "frase": frase})

total = sum(len(v) for v in por_episodio.values())
rnd = random.Random(SEMILLA)
elegidas = []
for ep, frases in sorted(por_episodio.items()):
    cupo = max(1, round(N * len(frases) / total))
    elegidas += rnd.sample(frases, min(cupo, len(frases)))
rnd.shuffle(elegidas)
elegidas = elegidas[:N]

items = [{"id": f"s{n:03d}", "voz": "naval", "ref": "naval", "frases": [e["frase"]], "origen": e["origen"]}
         for n, e in enumerate(elegidas, 1)]
salida = {
    "schema": 1,
    "_comentario": "Frases para el español sintético del piloto de fine-tuning (docs/fabrica-de-voz.md). "
                   "Generadas por piloto/elegir_frases.py: no editar a mano.",
    "silencio_entre_frases_ms": 250,
    "items": items,
}
(RAIZ / "piloto" / "frases_sinteticas.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n",
                                                        encoding="utf-8")
chars = sum(len(i["frases"][0]) for i in items)
print(f"{len(items)} frases de {len(por_episodio)} episodios, {chars} caracteres "
      f"(~{chars / 15 / 60:.0f} min de audio a 15 caracteres/s)")
