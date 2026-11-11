"""Elige las frases de prueba de las voces nuevas para la escucha a ciegas del cuaderno 04 (LoRA de Qwen).

Tres por voz, de su propia traducción (lo que dirá en la fábrica), con una regla fija para que salgan siempre las
mismas: 01 una frase media (110-170 caracteres, sin pregunta, que no abra intervención), 02 la frase más larga hasta
330 caracteres y 03 un bloque de 4 frases seguidas (300-500 caracteres). Escribe piloto/frases_prueba_voces.json.

    python3 piloto/elegir_prueba_voces.py
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VOCES = {"ridley": "ri", "vitalik": "vi", "qureshi": "qu", "hodak": "ho", "rauch": "ra", "scholl": "sc"}
SALIDA = RAIZ / "piloto" / "frases_prueba_voces.json"


def bloques_de(voz, alias):
    """[(episodio, bloque)] de esa voz, en orden de episodio. Los extra (repetidos del 160) no cuentan."""
    salida = []
    for f in sorted((RAIZ / "episodios").glob("*/*/transcript.es.json")):
        if f.parent.name.startswith("extra-"):
            continue
        ep = f"{f.parent.parent.name}/{f.parent.name}"
        for b in json.loads(f.read_text(encoding="utf-8"))["contenido"]:
            s = b["speaker"].lower()
            if alias.get(s, s) == voz:
                salida.append((ep, b))
    return salida


def elegir(voz, prefijo, alias):
    bloques = bloques_de(voz, alias)
    sueltas = [(ep, b["id"], k, fr) for ep, b in bloques for k, fr in enumerate(b["frases"], 1)]
    medias = [x for x in sueltas if 110 <= len(x[3]) <= 170 and "?" not in x[3] and x[2] > 1]
    media = medias[len(medias) // 2]
    larga = max((x for x in sueltas if len(x[3]) <= 330 and x != media), key=lambda x: len(x[3]))
    bloque = None
    for ep, b in bloques[len(bloques) // 3:] + bloques:
        for i in range(1, len(b["frases"]) - 3):
            trozo = b["frases"][i:i + 4]
            if 300 <= sum(map(len, trozo)) <= 500 and media[3] not in trozo and larga[3] not in trozo:
                bloque = (ep, b["id"], i + 1, trozo)
                break
        if bloque:
            break
    elegidas = [(media, [media[3]], "media"), (larga, [larga[3]], "larga"), (bloque, bloque[3], "bloque")]
    return [{"id": f"{prefijo}{n:02d}", "voz": voz, "ref": voz, "frases": frases,
             "origen": f"{x[0]}#{x[1]}/{x[2]}", "etiquetas": [etiqueta]}
            for n, (x, frases, etiqueta) in enumerate(elegidas, 1)]


def main():
    alias = json.loads((RAIZ / "fabrica" / "voces.json").read_text(encoding="utf-8"))["alias"]
    items = [it for voz, prefijo in VOCES.items() for it in elegir(voz, prefijo, alias)]
    datos = {"schema": 1,
             "_comentario": "Frases de prueba de las voces con LoRA nuevo (ridley, vitalik, qureshi, hodak, rauch y "
                            "scholl) para la escucha a ciegas del cuaderno 04 del piloto. Tres por voz, de su propia "
                            "traducción: una media (01), una larga (02) y un bloque de 4 frases (03). Generado por "
                            "piloto/elegir_prueba_voces.py.",
             "silencio_entre_frases_ms": 250, "items": items}
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for it in items:
        print(it["id"], it["origen"], sum(map(len, it["frases"])), "caracteres")


if __name__ == "__main__":
    main()
