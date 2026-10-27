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

Cada vez que se pida traducir un podcast se sigue un SOP. Lo que hay hasta ahora:

1. Se lee el contexto mínimo necesario sobre el proyecto y sus reglas.
2. *(pendiente: el autor lo completa)*

## Pendiente del autor

- El proceso que cree que hace falta seguir para llegar al objetivo.
- Lo que quiere comprobar personalmente en cada fase.
- El resto del SOP.

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
