# Estado y pendientes

> Punto de partida de cualquier sesión que retome el trabajo. Última actualización:
> 2026-10-30. Rama de trabajo: `claude/quirky-dirac-x18c3n`. Presupuesto de Colab: unas
> 360 unidades el 29-oct, antes de los últimos cuadernos.

## Dónde estamos

La **fase 1** (elegir motor) está casi cerrada:

- **Criba en zero-shot**: 8 variantes de 5 motores, más métricas y dos escuchas a ciegas.
  Resultados en `criba/resultados/resumen.md`.
- **Qwen3-TTS en modo solo timbre** (`x_vector_only`):
  - con Naval da parecido 5 y acento 5;
  - con Nivi, Brett y Deutsch pierde parecido (2–3);
  - la naturalidad baja (3,9);
  - el tono del episodio no pasa por la referencia.
- **Piloto de fine-tuning** (fase 1b): LoRA de Qwen3-TTS y de OmniVoice con los mismos
  datos. Receta en `piloto/investigacion-lora.md`.
- **Dos modelos de Naval**: `naval` y `naval_kapil`. Ver `docs/fabrica-de-voz.md`.

## Hecho recientemente

- **Filtro del español sintético** (`piloto/cuadernos/03_filtrar_sintetico`), 29-oct.
  En `piloto/sintetico/`: `seleccion.jsonl`, `medidas.jsonl` e `informe.md`.
  - Chatterbox V2: 368 de 400 pasan; se eligen 365 (37,8 min, similitud 0,67).
  - XTTS base: 335 de 400 pasan; se eligen 19 (2,2 min, similitud 0,39–0,53).
  - Total: 384 clips y 40,0 min. No sobra margen: son todas las frases con alguna versión buena.
  - El control de audio sobrante **al inicio no funciona**: Whisper marca siempre la
    primera palabra en 0,0 s. El del final sí funciona (descartó el s057 de XTTS, 8,6 s
    sobrantes).
  - **Decidido (30-oct): fuera los 19 de XTTS** (timbre lejano a Naval y único profesor que
    alucina). El cuaderno del LoRA los descarta al leer la selección: quedan 365 clips de
    Chatterbox V2, 37,8 min, un 39 % frente a 60 min de inglés.
- **Episodio 035 en Qwen** (`criba/cuadernos/03d_qwen_episodio`), 29-oct. En
  `outputs/criba/episodio_035/`: `episodio_xvec.wav` y `episodio_nivi_normal.wav`.
  Falta la escucha del autor.
- **Dataset de Naval** montado en la sesión local: 69,9 min de train (35,0 conversación y
  34,9 monólogo, 363 clips) y 4,2 min de eval (nav139, nav135 y nav081). Sin nav072.
  44,1 kHz mono. Autorizado a subirse a `fine_tunned_naval/datasets/naval/`.

## Esperando a que termine

| Qué | Dónde corre | Resultado esperado |
|---|---|---|
| Subida del dataset de Naval | Sesión local, tras la escucha del autor | `fine_tunned_naval/datasets/naval/` (376 MB) |
| Dataset `naval_kapil` (nav072 + los diálogos 1–4 de 2019) | Sesión local, midiendo | `datasets/naval_kapil/`; una fuente entera a eval. Ojo: los de 2019 vienen a 16 kHz y nav072 a 44,1 |

## Pendiente del autor

1. **Escuchar el episodio 035** (ya generado, en `outputs/criba/episodio_035/`) entero en
   modo solo timbre. Decide si Naval en zero-shot es publicable, y qué versión de Nivi
   prefiere: solo timbre o normal.
2. **Aprobar en la sesión local** la última escucha de los datasets de Naval y de
   `naval_kapil`.
3. **Decidir las variantes del LoRA.** Tras el modo solo timbre, la propuesta es:
   - **B**, la mezcla 60 % inglés real + 40 % español sintético, con etiqueta de idioma,
     como principal;
   - **A**, solo español sintético, como comparación opcional.
4. **Enviar a la sesión local** los datasets de Nivi, Brett y Deutsch, cuando Naval esté
   cerrado. El mensaje está preparado en la conversación del 29-oct. Metas:
   - nivi: todo lo que haya, buscando también su podcast propio;
   - brett y deutsch: 45–60 min cada uno.

## Pendiente de Claude

1. **Cuaderno de entrenamiento LoRA de Qwen3-TTS** en modo x-vector:
   - entrenador propio, basado en el de Alexandria, con la referencia y el idioma por
     ejemplo y la pérdida del sub-talker corregida;
   - lr de 1e-6 a 2e-6, 1–3 épocas, batch 1 con grad_accum 8, atención sdpa;
   - checkpoints a Drive cada 100 pasos;
   - inferencia con `PeftModel` sobre el Base y `generate_voice_clone(x_vector_only_mode=True, non_streaming_mode=True)`.
2. **Cuaderno de entrenamiento LoRA de OmniVoice**:
   - instalado desde git (el 0.2.1 de PyPI no trae LoRA);
   - truco de `clean_start_token_idx` para fijar la referencia;
   - `instruct_ratio=0`;
   - pocas épocas.
3. **Cuaderno de evaluación de checkpoints**: las 55 frases de la criba, WER, similitud y
   escucha a ciegas frente al modelo base.
4. **Después: fase 4**, el registro de voces (`voces.json`) y el cuaderno general de la
   fábrica.
5. **Arreglar `drive.json`**: sus IDs de año ya no existen. Las carpetas reales son
   `naval-podcast/transcripts/<año>`.

## Otros frentes

- **Fábrica de contenido** (web, RSS, YouTube y plataformas). La lleva otra sesión, con el
  prompt de `docs/prompt-sesion-contenido.md`. Contexto en `docs/fabrica-de-contenido.md`
  y `docs/rss.md`.

## Datos útiles

- **Drive** (todo bajo `fine_tunned_naval/`, id `1UWzNvgMXq-YTZzTvyJP1a5ARwTdA3TKA`):

  | Carpeta | Id |
  |---|---|
  | `speaker_refs/` | `1chF7NTFEjnzUJpv-J8RBH7u34RuQ2Ixh` |
  | `outputs/criba/` | `1c8_Ut0bTT2cDEGgij5kJiZBjqts18tQG` |
  | `piloto/` | `1RS0_ti_Ht65cPx64nvSsAW_edZDORY6K` |

- **Cuadernos**: se abren con
  `https://colab.research.google.com/github/DreiSup/spanishnav.al-podcast/blob/claude/quirky-dirac-x18c3n/<ruta>`.
  Son generados por `criba/construir_cuadernos.py` y `piloto/construir_cuadernos.py`.
- **Trampas de Colab ya resueltas**, a tener en cuenta en cuadernos nuevos:
  - Python 3.13 y CUDA 13.
  - dots-tts necesita un venv 3.12 con uv y torch/torchaudio 2.8.0 a juego.
  - chatterbox-tts de PyPI (0.1.7) no trae V3: se instala desde git, con
    torchvision 0.21.0.
  - faster-whisper no funciona (falta libcublas 12 y el PyAV no casa): se usa Whisper vía
    `transformers`.
  - Hay que vaciar la caché de Drive (`flush_and_unmount`) antes de soltar la GPU.
  - Si falla el montaje de Drive, se reintenta.
  - El aviso rojo de pip sobre el resolutor de dependencias es normal.
