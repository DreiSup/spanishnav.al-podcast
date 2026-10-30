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

- **Datasets de Nivi, Brett y Deutsch** subidos (`docs/dataset.md`, parte 2b): deutsch 60,0 min de
  train + 4,1 de eval; brett 46,8 + 4,1; nivi 62,7 + 5,0. Kapil (23,6 min) sigue solo en local.
- **Entrenamiento de cualquier voz** (30-oct): `piloto/rutas.py` centraliza las rutas; 01 genera el
  español sintético de nivi, brett y deutsch; 03 lo filtra por voz; 04 acepta `VARIANTE` = nivi, brett
  o deutsch.
- **La fábrica** (30-oct): `fabrica/voces.json`, `fabrica/fabrica.py` y `fabrica/fabrica.ipynb`. Probada
  en CPU con un motor falso sobre el 035: plan, regla de Kapil, carpeta en Drive, reintentos, pausas de
  0,12 s, reanudación e informe. Sin probar todavía en GPU.

## Esperando a que termine

| Qué | Dónde corre | Resultado esperado |
|---|---|---|
| `04_lora_qwen`, variante kapil | Colab, lanzado por el autor el 30-oct | `piloto/lora_qwen/kapil/` y su página de escucha |

## Pendiente del autor

1. **Escuchar a ciegas `lora_qwen_kapil.html`** y elegir checkpoint. Después, apuntarlo en
   `fabrica/voces.json` (`naval_kapil.adaptador`), o pedírselo a Claude.
2. **Probar la fábrica** con un episodio corto ya traducido (por ejemplo `2019/043-kelly-criterion`, unos
   2 min) y medir el coste por minuto de audio que imprime la celda 5.
3. **Español sintético de Nivi, Brett y Deutsch**: `piloto/cuadernos/01_sintetico_chatterbox` (T4, ~1 h
   por voz) y después `03_filtrar_sintetico` con cada `VOZ`.
4. **LoRA de Nivi, Brett y Deutsch**: `04_lora_qwen` con `VARIANTE` = cada voz; escuchar y elegir.
5. **Aprobar la organización de Drive** (`docs/organizacion-drive.md`); se ejecuta cuando estén todas las
   voces.
6. Opcional: `05_lora_omnivoice` (pesos no comerciales) y el LoRA de la voz de Kapil (dataset en local).

## Pendiente de Claude

1. **Tras cada escucha**, apuntar el checkpoint elegido en `fabrica/voces.json`.
2. **Cuaderno de evaluación** amplio (las 55 frases de la criba, WER y similitud), si hace falta
   comparar más a fondo que con las páginas de 3 frases.
3. **Reorganizar Drive** cuando el autor la apruebe, y actualizar `voces.json`, `piloto/rutas.py` y
   `drive.json`.
4. Si la fábrica sigue sonando lenta: probar a generar 2–3 frases de una vez y referencia en español en
   modo normal (`docs/fabrica-de-voz.md`, sección *Ritmo*).

Hecho el 30-oct: cuadernos LoRA de Qwen (B, kapil y cualquier voz) y de OmniVoice, `06_ritmo`, la fábrica.

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
