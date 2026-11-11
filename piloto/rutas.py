"""Rutas en Drive del entrenamiento de voces, en un solo sitio.

Todo cuelga de comun.DRIVE (fine_tunned_naval). Naval fue el piloto y conserva sus rutas antiguas; las
demás voces van en una subcarpeta con su nombre. Si se reorganiza Drive, se cambia aquí y nada más.
"""
from pathlib import Path

# Voces con dataset propio para LoRA (además de naval). Las seis últimas, en preparación en la sesión local (11-nov).
VOCES_LORA = ["nivi", "brett", "deutsch", "ridley", "vitalik", "qureshi", "hodak", "rauch", "scholl"]

# Frases de prueba de cada voz para la escucha a ciegas tras entrenar: (fichero de frases, relativo al repo, ids).
# Las de Naval, Kapil, Nivi y Brett van en criba/frases.json; las de Deutsch y la voz de Kapil, en
# criba/frases_xvector.json; las de las voces nuevas (11-nov), en piloto/frases_prueba_voces.json, que sale de
# piloto/elegir_prueba_voces.py con frases de su propia traducción.
PRUEBA = {
    "naval": ("criba/frases.json", ["n12", "n18", "n25"]),
    "naval_kapil": ("criba/frases.json", ["k05", "k07", "k10"]),
    "nivi": ("criba/frases.json", ["v07", "v09", "v10"]),
    "brett": ("criba/frases.json", ["b05", "b08", "b10"]),
    "deutsch": ("criba/frases_xvector.json", ["d01", "d02", "d03"]),
    "kapil": ("criba/frases_xvector.json", ["g01", "g02", "g03"]),
    "ridley": ("piloto/frases_prueba_voces.json", ["ri01", "ri02", "ri03"]),
    "vitalik": ("piloto/frases_prueba_voces.json", ["vi01", "vi02", "vi03"]),
    "qureshi": ("piloto/frases_prueba_voces.json", ["qu01", "qu02", "qu03"]),
    "hodak": ("piloto/frases_prueba_voces.json", ["ho01", "ho02", "ho03"]),
    "rauch": ("piloto/frases_prueba_voces.json", ["ra01", "ra02", "ra03"]),
    "scholl": ("piloto/frases_prueba_voces.json", ["sc01", "sc02", "sc03"]),
}


def dataset(drive, voz):
    """Clips reales en inglés de la voz, montados por la sesión local."""
    return Path(drive) / "datasets" / voz


def sintetico(drive, voz):
    """Español sintético generado con la voz: <aquí>/chatterbox_v2/sNNN.wav, medidas.jsonl, seleccion.jsonl."""
    base = Path(drive) / "piloto" / "sintetico"
    return base if voz == "naval" else base / voz


def lora(drive, variante):
    """Checkpoints del LoRA de Qwen de una variante (B y A son Naval; kapil es naval_kapil)."""
    return Path(drive) / "piloto" / "lora_qwen" / variante
