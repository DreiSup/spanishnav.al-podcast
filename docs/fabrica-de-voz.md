# Fábrica de traducción y clonación de voz

> Memoria de trabajo. Recoge lo que el autor ha fijado como objetivo y reglas para la fase
> de clonación de voz, y el estado encontrado en Drive el 2026-10-26. **El prompt completo
> del autor está a medias**: lo que falta va marcado como pendiente y no se rellena por
> suposición.
>
> Fijado: 2026-10-27.

## Reglas

1. **Mínimo de unidades de cómputo.** No se lanza ningún proceso en GPU salvo que sea
   estrictamente necesario o que el autor lo pida de forma explícita. Ante la duda, se
   pregunta antes de gastar.
2. **El autor es el *human in the loop*.** Él decide si cada resultado está bien o no. Las
   métricas automáticas (WER, similitud, UTMOS) ayudan a decidir, pero no deciden.

Presupuesto a 2026-10-27: **459 unidades de Colab**; aproximadamente un tercio caducará
pronto. No hay suscripción activa.

## Objetivo final

Una fábrica de traducción del podcast en la que el trabajo del autor se reduce a decirle a
un agente «quiero traducir el podcast *x*», y el agente tiene todas las herramientas para
hacerlo.

La limpieza de alucinaciones **sigue siendo manual en Audacity**. Por eso la salida es una
pista de audio por intervención, numerada en orden de aparición y con el nombre del
hablante:

```
Naval habla 2 min → Nivi interrumpe 1 min → Naval 4 min → Brett 1 min

001naval.wav  002nivi.wav  003naval.wav  004brett.wav
```

El autor ajusta después el conjunto en Audacity.

> Pendiente de decidir: CLAUDE.md fija que el clip se nombra por el id del bloque
> (`b01-nivi`, `b02-naval`). El formato `001naval.wav` del autor es equivalente en orden y
> en contenido, pero no coincide en forma. Hay que elegir uno antes de escribir el script de
> síntesis.

## Herramientas necesarias

- **Un modelo fine-tuneado por cada integrante del podcast**: Naval, Nivi, Brett Hall,
  David Deutsch, Vitalik Buterin…
- **El clon tiene que ser lo más perfecto posible.** Antes de producir, se itera sobre
  varios modelos y varias comprobaciones hasta dar con el adecuado.
- **Audio limpio con transcript de cada integrante.** Lo recopila el autor, con ayuda de
  Claude.

## SOP por episodio

Cada vez que se pida traducir un podcast se sigue un SOP. Esto es lo que ha fijado el
autor; los detalles se están decidiendo en diálogo y no hay que rellenarlos por suposición.

1. Se lee el contexto mínimo necesario sobre el proyecto y sus reglas.
2. Se lee el texto del podcast, que estará preparado de antemano.
3. Se usan solo los modelos de quienes hablan en ese episodio: si solo hablan Naval y
   Nivi, se cargan solo los fine-tuneados de Naval y de Nivi.
4. **Salida:** un audio por intervención, separados por hablante, guardados en Google
   Drive en una carpeta con el nombre del podcast.

## Decidido (2026-10-27)

- **Un único motor para todas las voces.** Todos los fine-tunes usan el mismo modelo base,
  de modo que un solo cuaderno general sirve para cualquier combinación de hablantes.
- **Colab lo ejecuta el autor.** Claude Code no puede lanzar cuadernos: prepara todo y el
  autor pulsa *Ejecutar todo*. Ese clic es también el control del gasto.
- **Texto de entrada:** `transcript.es.json` del repo. Lleva hablante e id por bloque y
  está validado; los `_es.json` de Drive no llevan ids.
- **Nombre de los clips:** `001naval.wav`. Se deriva del orden del bloque en el JSON
  (`b01-naval` → `001naval.wav`), así que no contradice la regla de los ids.
- **Carpeta en Drive:** la del episodio que ya existe, con una subcarpeta `tts/`:
  `naval-podcast/transcripts/<año>/<NNN Título en inglés>/tts/001naval.wav`. Es la única
  estructura por episodio que hay en Drive hoy, y las subcarpetas por tipo son las que ya
  preveía CLAUDE.md. En Drive no hay audio de episodios en ningún sitio: el material
  antiguo sigue en local (`spanishpodcast/2019/`).

## Identidad y tono son dos cosas distintas

El autor quiere que cada episodio doblado conserve el tono de su original: no suena igual
Naval con Kapil Gupta que en *How to Get Rich*. La solución propuesta, pendiente de
validar en la fase 1:

- **El fine-tuning fija la identidad** —timbre, acento, forma de hablar— y se hace **una
  vez por hablante**, con audio limpio de varias fuentes y de registros variados
  (calmado, enérgico, conversacional). Si solo se entrena con un registro, el modelo tira
  hacia ese registro.
- **El tono de cada episodio sale de la referencia en inferencia.** Se cortan 2 o 3 clips
  del propio episodio original y el modelo fine-tuneado los usa como referencia. Nada de
  fine-tuning por episodio: cuesta unidades cada vez, hay pocos datos, aumenta el riesgo de
  olvidar el español y rompe la automatización.
- Si con la referencia no basta: unos pocos LoRA por registro, reutilizables, nunca por
  episodio. Solo si las pruebas lo piden.
- **Criterio obligatorio al elegir motor:** que el modelo ya fine-tuneado siga aceptando
  audio de referencia, o instrucciones de estilo, y que la prosodia pase del inglés al
  español.

## El camino hasta el objetivo, en este orden

1. **Elegir el motor.** Pruebas con varios modelos y varias iteraciones hasta decidir cuál
   se usa para todos los hablantes. Decide el autor, escuchando.
2. **Reunir material** suficiente de cada hablante: audio limpio con su transcript. Se
   hace en local con el prompt de `docs/prompt-dataset-local.md`; quién habla y de dónde
   sacar audio, en `docs/hablantes.md`.
3. **Fine-tunear** a cada hablante con todo organizado.
4. **Escribir el cuaderno general** y probarlo.

## Fase 1a — material que aporta el autor

En `fine_tunned_naval/speaker_refs/<hablante>/`, por cada voz (Naval y Nivi
obligatorias; un invitado como Brett Hall, opcional):

- 3 clips de unos **6, 12 y 25 s**, en `.wav`, con su frecuencia de muestreo original.
- Sacados del **audio original en inglés del podcast de Naval**: mismo micrófono y misma
  sala que lo que se va a doblar.
- Una sola voz, sin risas, solapes, música ni sintonía. Cortados en silencio, con unos
  200 ms de margen.
- Sin limpieza de ruido agresiva: si un clip trae ruido, se descarta en vez de limpiarlo.
- Cada clip con su `.txt` de transcripción **literal**: `naval_ref01.wav` +
  `naval_ref01.txt`.

Para la prueba de tono, Naval lleva además un segundo juego, `speaker_refs/naval_kapil/`:
2 o 3 clips del episodio con Kapil Gupta, con las mismas reglas. Las mismas frases se
sintetizan con un juego y con el otro, y el autor escucha si el tono cambia.

Las frases de prueba en español las prepara Claude a partir de los `transcript.es.json`
del repo.

## Estado encontrado en Drive (2026-10-26)

Sirve para no repetir el reconocimiento.

**`naval-podcast/`** no es una copia del repo:

- `transcripts/2019/` tiene los episodios **001–016** como `.txt` (F99), `.json` (F0) y
  `_es.json` (F5), en carpetas `NNN Título en inglés`. El repo tiene otros episodios: 035,
  036, 040–045, 051 y 052, ya normalizados.
- Los años 2020–2026 solo tienen un acceso directo `<año> all podcasts`.
- **Los IDs de año de `drive.json` ya no existen.** Las carpetas reales son
  `transcripts/<año>` y tienen otros IDs.
- Dentro de `001 Seek Wealth…` hay un Google Doc «Make Abundance for the World» que está
  fuera de sitio.

**`fine_tunned_naval/`** ocupa unos 59,6 GB:

- **Datos.** `modern_wisdom_podcast_dataset/wavs + txts/` tiene 400 clips de Naval
  (67 min) y 177 de Chris. `dataset/wavs/` tiene 147 clips curados; faltan `naval_081`,
  `_089` y `_094`, y los `.txt` 073, 081, 089 y 093 están vacíos.
- **Pesos.** `weights/` guarda la base de XTTS v2, `xtts_finetunned_navalchris/` y
  `smoketestXTTSv2/`: 8 checkpoints de 5,6 GB, 45 GB en total.
- **Evaluación zero-shot** (`naval(zero-shots)/eval_resultados.csv`, 11 frases y una
  referencia):

  | Modelo | WER % | Similitud | UTMOSv2 |
  |---|---|---|---|
  | Chatterbox | 1,395 | 0,671 | 2,633 |
  | XTTS v2 | 2,326 | 0,497 | 2,605 |
  | F5 | 5,581 | 0,551 | 2,607 |

**Que el fine-tuning sea peor que el zero-shot no está demostrado:**

- **XTTS `navalchris`: nunca se midió.** `compare_xtts_vs_chatterbox.ipynb` falló en la
  primera celda por falta de WAV por frase. Además, el modelo está infraentrenado: 255
  actualizaciones con lr 5e-6, y la loss seguía bajando.
- **LoRA de Chatterbox: tiene varios fallos.**
  - Se quedó el último checkpoint, aunque la val loss subía.
  - El adaptador se perdió en `/content`.
  - Probablemente generó sin referencia de Naval.
  - Las referencias son estéreo.
  - Todos los objetivos miden 750 tokens fijos.
- **El notebook de métricas sí es reutilizable** como banco de pruebas común. Mide WER con
  faster-whisper large-v3, similitud con ECAPA-TDNN y calidad con UTMOSv2.
