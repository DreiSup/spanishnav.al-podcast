"""Rutas en Drive del entrenamiento de voces, en un solo sitio.

Todo cuelga de comun.DRIVE (fine_tunned_naval). Naval fue el piloto y conserva sus rutas antiguas; las
demás voces van en una subcarpeta con su nombre. Si se reorganiza Drive, se cambia aquí y nada más.
"""
from pathlib import Path

# Frases de prueba de cada voz para la escucha a ciegas tras entrenar: (fichero de frases, ids).
# Las de Naval y Kapil van en criba/frases.json; las de Deutsch y la voz de Kapil, en frases_xvector.json.
PRUEBA = {
    "naval": ("frases.json", ["n12", "n18", "n25"]),
    "naval_kapil": ("frases.json", ["k05", "k07", "k10"]),
    "nivi": ("frases.json", ["v07", "v09", "v10"]),
    "brett": ("frases.json", ["b05", "b08", "b10"]),
    "deutsch": ("frases_xvector.json", ["d01", "d02", "d03"]),
    "kapil": ("frases_xvector.json", ["g01", "g02", "g03"]),
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
