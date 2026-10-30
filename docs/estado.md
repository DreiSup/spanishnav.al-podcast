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
  Escuchado el 30-oct: «no suena mal», pero **el autor quiere entrenar Naval igualmente**.
- **Dataset de Naval** montado en la sesión local: 69,9 min de train (35,0 conversación y
  34,9 monólogo, 363 clips) y 4,2 min de eval (nav139, nav135 y nav081). Sin nav072.
  44,1 kHz mono. Subido a `fine_tunned_naval/datasets/naval/` (388 ficheros, `rclone check` sin
  diferencias).

- **Dataset `naval_kapil`** subido a `fine_tunned_naval/datasets/naval_kapil/`: train 15,6 min
  (15,2 de nav072 a 44,1 kHz + 0,4 de nav003 a 16 kHz), eval nav001 entero (50 s).
- **LoRA de Qwen, variante B** (`04_lora_qwen`), 30-oct: 158 pasos completos, checkpoints 40, 80,
  120 y 158. Pérdida de evaluación en inglés 2,93 → 2,66 y en español 2,82 → 2,45, bajando en
  todos los checkpoints (sin sobreajuste). Prueba en `piloto/lora_qwen/B/prueba/`.
- **Ritmo**: el autor nota que todas las versiones van lentas (~15 c/s frente a 19,5 de Naval).
  Acelerar sin cambiar el tono se descarta; **acortar las pausas a 0,12 s queda fijado para la
  fábrica** (`docs/fabrica-de-voz.md`, sección *Ritmo*).
- **Escucha a ciegas del LoRA B** (30-oct, `piloto/resultados/resumen.md`): base 3,67 de media;
  pasos 80, 120 y 158 empatados en torno a 4 (naturalidad 3 → 4; el acento no cambia, 4). **Se
  elige `paso_0158`**: sin ninguna nota por debajo de 4 y con la menor pérdida de evaluación.

## Esperando a que termine

| Qué | Dónde corre | Resultado esperado |
|---|---|---|
| Datasets de Nivi, Brett y Deutsch | Sesión local (`orquesta_parte2b.sh`) | Tabla de fuentes, informe y escucha de cada uno, para el OK del autor |

## Pendiente del autor

1. **`04_lora_qwen`, variante kapil**, con `PARTIR_DE = "B/paso_0158"`.
2. **Después, `05_lora_omnivoice`**, si tras escuchar Qwen sigue mereciendo la comparación
   (ojo: los pesos de OmniVoice serían no comerciales).
3. **Datasets de Nivi, Brett y Deutsch** en la sesión local: aprobar la tabla de fuentes, la
   escucha y la subida de cada uno. Nada se sube a Drive sin el OK del autor.

## Pendiente de Claude

> Orden de los fine-tunings: primero el piloto con Naval decide motor y receta; después
> Nivi, Brett y Deutsch con esa receta (y su español sintético, que sí gasta unidades). Los
> invitados menores (Vitalik, Ridley, Hodak, Rauch, Scholl, Qureshi) van en zero-shot.

1. ~~Cuaderno LoRA de Qwen3-TTS~~: hecho el 30-oct, `piloto/cuadernos/04_lora_qwen`
   (entrenador en `piloto/lora_qwen.py`, probado en CPU con un modelo diminuto). Variante B
   por defecto: 2 épocas, 158 pasos, lr 2e-6, r 64 / alpha 128, checkpoints cada 40 pasos.
2. ~~`naval_kapil`~~: hecho el 30-oct como variante `kapil` del mismo `04_lora_qwen`. Parte del
   checkpoint de Naval que elija el autor (`PARTIR_DE`), 3 épocas con los 15,6 min de la sesión con
   Kapil + español sorteado al 40 % (73 pasos, checkpoints cada 15). Prueba: k05, k07 y k10 frente a
   sus gemelas con la referencia normal.
3. ~~Cuaderno LoRA de OmniVoice~~: hecho el 30-oct, `piloto/cuadernos/05_lora_omnivoice`
   (`piloto/lora_omnivoice.py`, entrenador oficial de OmniVoice, probado en CPU con un modelo
   diminuto). Mismos datos y variantes que el 04. lr 1e-4, r 16 / alpha 32, 4 épocas (unos 212
   pasos en B). La referencia va como tokens delante del clip, con `clean_start_token_idx`; un
   10 % de ejemplos sin condicionamiento para la guía. Se lanza después de escuchar el de Qwen.
4. **Cuaderno de evaluación de checkpoints**: las 55 frases de la criba, WER, similitud y
   escucha a ciegas frente al modelo base.
5. **Después: fase 4**, el registro de voces (`voces.json`) y el cuaderno general de la
   fábrica.
6. **Arreglar `drive.json`**: sus IDs de año ya no existen. Las carpetas reales son
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
