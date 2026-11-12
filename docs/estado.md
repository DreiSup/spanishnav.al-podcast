# Estado y pendientes

> **Al retomar la fábrica, lee primero `docs/contexto-fabrica.md`** (traspaso del 6-nov: cómo generar, voces, estado
> de producción y base para optimizar).

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

- **Español sintético** (`01_sintetico_chatterbox`), 30–31 oct: 400 de 400 clips en las tres voces
  (nivi, brett 44,0 min, deutsch 49,4 min).
- **Filtro de Nivi** (`03_filtrar_sintetico`), 31-oct: 354 de 400 pasan; se eligen 299 clips,
  41,9 min (objetivo 41,8). Similitud media 0,58 (Naval: 0,67).
- **Filtro de Brett**, 1-nov: 360 de 400 pasan; se eligen 275 clips, 31,3 min (objetivo 31,2).
  Similitud media 0,49.
- **Filtro de Deutsch**, 1-nov: 366 de 400 pasan; se eligen 323 clips, 40,1 min (objetivo 40,0).
  Similitud media 0,47, la más baja de las tres voces.
- **LoRA de Brett** (`04_lora_qwen`, `VARIANTE = "brett"`), 1-nov: 130 pasos completos, checkpoints
  40, 80, 120 y 130. Pérdida de evaluación en inglés 3,14 → 2,93 y en español 2,89 → 2,60, bajando en
  todos. Falta la escucha: `piloto/lora_qwen/brett/prueba/escucha/lora_qwen_brett.html`.
- **LoRA de Deutsch** (`04_lora_qwen`, `VARIANTE = "deutsch"`), 2-nov: 155 pasos completos, checkpoints
  40, 80, 120 y 155. Pérdida de evaluación en inglés 3,10 → 2,77 y en español 2,65 → 2,45, bajando en
  todos.
- **Escucha de Nivi, Brett y Deutsch** (2-nov, `piloto/resultados/resumen.md`): Nivi se queda **sin LoRA**
  (el LoRA le devolvía acento), Brett `paso_0130`, Deutsch `paso_0120`. Ya en `fabrica/voces.json`. Para Brett y
  Deutsch el autor quiere conservar un poco de su acento.
- **LoRA de Nivi** (`04_lora_qwen`, `VARIANTE = "nivi"`), 1-nov: 159 pasos completos, checkpoints
  40, 80, 120 y 159. Pérdida de evaluación en inglés 2,63 → 2,43 y en español 2,85 → 2,56, bajando
  en todos. Falta la escucha: `piloto/lora_qwen/nivi/prueba/escucha/lora_qwen_nivi.html`.

- **Primera prueba de la fábrica en GPU** (2-nov, 044, L4): 1,7 min de audio en 8 min (4,58 s de GPU por s de
  audio), 27 frases sin un reintento. Estructura y ritmo bien según el autor; **Naval suena demasiado inglés**:
  cuaderno `piloto/cuadernos/08_acento_naval` (huella en español y LoRA a media fuerza). Escucha del 2-nov: **gana
  la versión actual** (4,67; parecido y naturalidad 5); las demás no mejoran el acento. Naval se queda igual.
- **Auditoría de las traducciones de Drive** (2-nov): los 16 de 2019 (001–016, heredados) son buenos; 9 listos y 7
  con decisiones menores. Problemas repetidos: palabras de España, troceado copiado del inglés, notas
  `[correction]` locutadas, siglas y títulos en inglés. Se mantiene el SOP con reglas nuevas.

- **Fábrica por lotes** (2-nov): genera juntas las frases de cada intervención (lotes de 8), Whisper las revisa
  en lote, tope de pasos por frase y cuaderno por defecto en T4. Probado sin GPU (reintentos y reanudación).
  **Medido el 2-nov con 037–039 en T4:** 10,6 min de audio en unos 22 min (2–2,8 s de GPU por s de audio),
  unas 5 unidades por hora de audio frente a 22 antes. Una sola frase sospechosa y era falsa («noventa por
  ciento» frente a «90%» de Whisper; corregido en `medir.normaliza`). Faltan 035, 036, 040–043 y 045.

- **Reglas nuevas de traducción** (2-nov, tras la auditoría): el normalizador avisa ahora de frases de más de 45
  palabras, de frases de una o dos palabras sueltas (salvo preguntas y exclamaciones) y de palabras de España;
  el prompt de traducción pide trocear para el oído, no locutar notas `[correction]` y criterio para siglas y
  títulos (sección nueva en GLOSARIO.md). Con las reglas nuevas, ya en el repo: 036 (3 avisos), 040 (2) y 052
  (40, 14 de ellos de vocabulario vetado). El autor decide (2-nov) mantener «coche» y «ordenador»: vocabulario
  de España. Prompt de traducción reescrito con todo esto.

- **Las erres de Naval** (3-nov): el autor sigue oyendo giros ingleses en la r y la rr. Cuaderno
  `piloto/cuadernos/09_erres_naval`. Escucha del 3-nov: la actual es la peor en acento (3,33); empatan arriba
  el paso 120 (4,33) y la actual con temperatura 0,7 (4,33, acento 4,67). **Decisión del autor: paso 120 con
  temperatura 0,7** para Naval y naval_kapil, ya en voces.json. La fábrica rehace sola, al relanzar, los clips
  hechos con otra voz (037, 038, 039 y 044: solo los de Naval).

- **Fábrica con la voz final de Naval** (3-nov, T4): 035, 036, 037, 038, 039 y 040 hechos o rehechos, **cero frases
  sospechosas**, unos 2,1 s de GPU por s de audio. La ejecución se cortó al empezar el 041 (carpeta vacía). Faltan
  041–045 y rehacer Naval en el 044. Desde el 4-nov la fábrica rehace sola los clips cuyo **texto** cambió en el
  repo (además de los de voz cambiada): compara las frases guardadas en el registro.
- **Traducción** (3–4 nov): 053–067 subidos (cortos, casi todos solo Naval). 368 min traducidos en total.

- **Sin Audacity por defecto** (decisión del autor, 4-nov): la fábrica monta ya el **master**
  (`audio/<NNN>-<slug>.mp3`, -16 LUFS, MP3 mono 128 kbps) y el informe da el minuto de cada clip y de cada frase
  sospechosa. El autor lo escucha y solo arregla lo que suene mal: otra semilla (`RONDA`) o el clip en Audacity y
  `SOLO_MASTER`. Procedimiento en `docs/sop-episodio.md`. Pendiente: vídeo, YouTube, web y RSS, e intro o cierre.

- **Arreglos frase a frase** (4-nov): la fábrica guarda cada frase en `tts/frases/` y escribe `indice_master.tsv`
  (segundo del master de cada frase). `REHACER_FRASES` rehace solo las frases pedidas; `fabrica/localizar.py` las
  encuentra por minuto o por texto. `MUESTRA = 3` prueba voces nuevas con 3 intervenciones de cada una.

- **Decisiones del autor (4-nov):** se rehacen **todos** los episodios con la fábrica desde el 1 (regla de los
  heredados retirada; el normalizador ya no los marca); sin intro ni cierre; un solo cuaderno de fábrica. El 052 es
  la recopilación de 1–50: recomendación técnica, montarlo uniendo masters (pendiente del autor). Traspaso a la
  sesión global en `docs/contexto-sesion-global.md`.

- **001–016 generados** (5-nov) con la voz final, cero frases sospechosas (estado `tts`). **El 001, escuchado entero
  por el autor y dado por bueno** (estado `montaje`, listo para publicar); 002–016, pendientes de escucha.

- **Coste por episodio** (5-nov): la fábrica anota tiempo de GPU y unidades estimadas en cada informe, en
  `naval-podcast/coste_fabrica.jsonl` (episodios y sesiones) y en `naval-podcast/coste_fabrica.md` (resumen de todo,
  celda 6). Tarifas en `voces.json` («coste»). 068 Kapil generado: 39,7 min de audio.

## Esperando a que termine

| Qué | Dónde corre | Resultado esperado |
|---|---|---|
| — | — | Nada corriendo a fecha del 1-nov |

## Pendiente del autor

**Plan del autor (2-nov) hasta la versión alfa de la fábrica:**

1. ~~Pausa de Nivi~~: 0,20 s (2-nov). Pausas en la fábrica: Naval 0,12, Brett 0,30, Deutsch y Nivi 0,20.
2. **Sesión de traducción aparte**, con el prompt de `docs/prompt-sesion-traduccion.md`: traduce unos
   cuantos episodios al formato del repo. Lleva su propio registro en `docs/traduccion.md`.
3. **Primera prueba de la fábrica** (`fabrica/fabrica.ipynb`). No hace falta esperar a la traducción: ya hay
   8 episodios cortos traducidos (035, 036, 040–045; unos 36 min, solo Naval y Nivi). Primero el 044 (2 min)
   para comprobar el motor en GPU y medir el coste; después los otros 7 en la misma sesión. El 051 (56 min)
   y el 052 (280 min) quedan fuera de la prueba. Brett, Deutsch y Kapil se prueban cuando haya episodios suyos.
4. **Con el autor, los SOP de publicación:** el `.mp3` principal, el vídeo de YouTube y sus datos, la web y
   el RSS.
5. **Cuando todo funcione:** traducir el resto y poner en marcha la fábrica (versión alfa).

Opcionales: el LoRA de la voz de Kapil y `05_lora_omnivoice`. Al final: reorganizar Drive
(`docs/organizacion-drive.md`).

## Pendiente de Claude

0. **LoRA de los seis invitados (desde el 11-nov; lo lleva Claude, el autor no tiene que acordarse).** La sesión
   local hace los datasets de ridley → vitalik → qureshi → hodak → rauch → scholl y avisa con los minutos de
   train/eval de cada uno al subirlo a `fine_tunned_naval/datasets/<voz>/`. **En cada sesión técnica, comprobar
   en Drive si ha aparecido alguno** (`datasets/<voz>/metadata.jsonl`) y, si está, proponerle al autor sin que lo
   pida las celdas de ese paso. Por voz:
   1. 01 en T4, ~60 min. Hecho: ☑ ridley (12-nov: 400/400, 47 min de audio, 49 min de GPU) ☐ vitalik ☐ qureshi ☐ hodak ☐ rauch ☐ scholl
   2. 03 en T4, ~15 min. Hecho: ☐ ridley ☐ vitalik ☐ qureshi ☐ hodak ☐ rauch ☐ scholl
   3. 04 en L4. Hecho: ☐ ridley ☐ vitalik ☐ qureshi ☐ hodak ☐ rauch ☐ scholl
   4. Escucha a ciegas del autor. Hecha: ☐ ridley ☐ vitalik ☐ qureshi ☐ hodak ☐ rauch ☐ scholl
   5. Paso elegido en `fabrica/voces.json`. Hecho: ☐ ridley ☐ vitalik ☐ qureshi ☐ hodak ☐ rauch ☐ scholl
   6. Regenerar sus clips en la fábrica: ☐ 070, 071 (ridley; **el 070 tiene un arreglo sintético: preguntar al
      autor qué clip/minuto antes de regenerar**) ☐ 131, 132 (vitalik, qureshi) ☐ 160 y extras (hodak, rauch,
      scholl). Si los cortos del 160 ya están montados, volver a montarlos después.

   Detalle en `docs/contexto-fabrica.md` («Pendiente: LoRA de los seis invitados»). Marcar aquí cada paso.

   **Orden decidido (12-nov):** ridley, vitalik, hodak, rauch, scholl y **qureshi el último**. Qureshi solo tiene
   16 min de train (la receta pide 30) y habla ~10 min en todo el doblaje (131 y 132): se entrena con lo que hay
   (el 04 guarda cada 20 pasos para él) y, si en la escucha a ciegas no gana a `base`, se queda sin LoRA y se cierra.
   No se busca más audio (The Chopping Block) salvo que el autor lo pida.
   **El autor avisa cuando la sesión local termine de subir los datasets: entonces, celdas de Ridley.**
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
