# Piloto de fine-tuning

Fase 1b de `docs/fabrica-de-voz.md`. Se entrena un LoRA de **Qwen3-TTS** y otro de
**OmniVoice** con los mismos datos, y se elige el motor definitivo por acento y timbre.

## Datos

| Parte | Peso | De dónde sale | Qué enseña |
|---|---|---|---|
| Inglés real de Naval | 60 % (~60 min) | `fine_tunned_naval/datasets/naval/`, de la sesión local (`docs/dataset.md`) | Timbre y naturalidad |
| Español sintético | 40 % (~40 min) | Generado aquí con Chatterbox V2 y XTTS base, y filtrado | Pronunciación española |
| Evaluación | — | Las 55 frases de `criba/frases.json`, que nunca se entrenan | Medir el antes y el después |

Primer intento: el español sintético tal cual. Cada ejemplo lleva como referencia otro clip
del mismo profesor y la etiqueta de idioma `es`. Si al modelo se le pega el timbre de los
profesores, el segundo intento pasa ese español por un conversor de voz entrenado con
Naval.

## Ficheros

- `elegir_frases.py` → `frases_sinteticas.json`: 400 frases de Naval, de 60 a 220
  caracteres, sin ninguna de la criba.
- `lora_qwen.py`: el entrenador LoRA de Qwen. Replica la entrada de `generate` en modo x-vector y
  non-streaming, con referencia e idioma por ejemplo, EOS entrenado y la pérdida del sub-talker
  corregida. Probado en CPU con un modelo diminuto: el prefill es idéntico al de `generate`.
- `medir.py`: WER con Whisper large-v3 (sin tildes y con las cifras pasadas a letra) y
  similitud ECAPA.
- `construir_cuadernos.py` → `cuadernos/`, que son generados:

| Cuaderno | Qué hace | GPU |
|---|---|---|
| `01_sintetico_chatterbox.ipynb` | 400 clips con Chatterbox V2 → `piloto/sintetico/chatterbox_v2/` | T4 |
| `02_sintetico_xtts.ipynb` | 400 clips con XTTS base → `piloto/sintetico/xtts_base/` | T4 |
| `03_filtrar_sintetico.ipynb` | Mide, filtra (WER ≤ 5 %, velocidad normal) y elige la mejor versión de cada frase hasta 40 min → `seleccion.jsonl` | T4 |
| `04_lora_qwen.ipynb` | LoRA de Qwen3-TTS en modo solo timbre (variante B: 60 % inglés real + 40 % español de Chatterbox; A: solo español; kapil: repaso corto de `naval_kapil` encima del checkpoint de Naval elegido), checkpoints, pérdida de evaluación y una escucha a ciegas de 3 frases → `piloto/lora_qwen/<variante>/` | L4 |
| `05_lora_omnivoice.ipynb` | LoRA de OmniVoice con el entrenador oficial (`lora_omnivoice.py`) y los mismos datos y variantes que el 04: referencia de otro clip por ejemplo (`clean_start_token_idx`), idioma por ejemplo, 10 % sin condicionamiento y 4 épocas. Un adaptador por época, pérdida de evaluación por idioma y la misma escucha a ciegas → `piloto/lora_omnivoice/<variante>/` | L4 |

Rutas en Drive, bajo `fine_tunned_naval/`.
