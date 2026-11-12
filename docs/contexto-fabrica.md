# Contexto de la fábrica de voz (traspaso, 2026-11-06)

Todo lo que hace falta para seguir produciendo episodios y para optimizar la fábrica sin releer la historia. Lo
mantiene la sesión técnica. Rama: `claude/quirky-dirac-x18c3n` (pull --no-rebase antes de cada push; sin PRs).

## Reglas del autor

- Mínimo gasto de unidades de Colab. Un paso cada vez, con su confirmación. Decide escuchando (a ciegas si se
  comparan versiones; para pruebas rápidas, escucha directa en el cuaderno). Todo en español. Celdas completas.
- El autor ejecuta Colab; la sesión técnica prepara y prueba los cuadernos **sin GPU** (motores falsos) antes de
  subirlos.
- Git guarda texto; Drive guarda bytes. Nunca audio en git.
- **Esta sesión es solo la parte técnica de generar** (fábrica, cuadernos, Colab, optimización). Las tareas del
  autor (Google Tasks), las escuchas y sus decisiones las lleva otra sesión: aquí no se preguntan ni se gestionan.

## Cómo se genera un episodio

Cuaderno: `https://colab.research.google.com/github/DreiSup/spanishnav.al-podcast/blob/claude/quirky-dirac-x18c3n/fabrica/fabrica.ipynb`
(generado por `fabrica/construir_cuaderno.py`; la lógica está en `fabrica/fabrica.py`, la configuración en
`fabrica/voces.json`). GPU **T4**. Celda 1 → *Reiniciar sesión* → celda 2 con los episodios → celdas 2 a 7.

Celda 2 completa (plantilla):

```python
# 2. Parámetros
EPISODIOS = ["2019/017-math-logic"]   # carpetas de episodios/ del repo
VERIFICAR = True     # revisar cada frase con Whisper y repetir las que fallen (más lento, mucho menos Audacity)

# Arreglos tras escuchar el master (docs/sop-episodio.md). Para producir normal: SOLO_MASTER = False y RONDA = 0
SOLO_MASTER = False  # True = no genera nada ni usa GPU: rehace el master con los clips de tts/ (p. ej. uno arreglado en Audacity)
RONDA = 0            # 1, 2…: otras semillas para los clips que borres de tts/ (el mismo número da siempre el mismo audio)
REHACER_FRASES = {}  # p. ej. {"2019/037-productize-yourself": {"002naval.wav": [7]}}: solo esas frases (números del informe)
MUESTRA = 0          # 3 = solo las 3 primeras intervenciones de cada voz, en <episodio>/muestra/ (probar voces nuevas)

# Pruebas de voz. Para producir normal: REF_ES_NAVAL = 0 y SUBCARPETA = ""
REF_ES_NAVAL = 0     # 0 = la referencia de voces.json; 1 = el mejor clip de Naval en español (lora_ref_es1 del 08); 5 = media de 5
SUBCARPETA = ""      # p. ej. "prueba_ref_es1": la prueba va a <episodio>/<subcarpeta>/ y no toca los clips de verdad
```

Celdas: 3 prepara y comprueba (sin GPU; debe acabar en `RESULTADO: OK`) y activa el **seguro**: si cualquier celda
falla, en 10 min anota el coste y desconecta, salvo que se pulse Detener; 4 carga Qwen + LoRA + Whisper, 5 genera,
6 anota el coste de la sesión (con su reparto) y rehace el resumen, 7 desconecta. En una sesión ya abierta con las mismas voces basta
2, 3 y 5 (+6, 7). Tras cambiar código en la rama hay que **reiniciar la sesión** (los módulos ya importados no se
recargan). Si Colab corta, se relanza la misma celda: lo hecho no se repite.

Antes de mandar episodios: `git pull` y comprobar con `fabrica.plan_episodio` + el normalizador (`--simular`) que
el transcript existe, no tiene avisos y sus hablantes tienen voz.

## Qué deja en Drive (`naval-podcast/transcripts/<año>/<NNN Título>/`)

`audio/<NNN>-<slug>.mp3` (master: 0,6 s entre intervenciones, -16 LUFS, MP3 mono 44,1 kHz 128 kbps),
`informe_tts.md` (minuto de cada clip, sospechosas, coste), `indice_master.tsv` (segundo de cada frase),
`tts/NNNvoz.wav` + `tts/frases/NNNvoz_KK.wav` (frase KK, desde 1), `registro_tts.jsonl` (texto, intentos, firma de
la voz, GPU, segundos de generación por clip). Libro de coste: `naval-podcast/coste_fabrica.jsonl` (episodios y
sesiones) y resumen `naval-podcast/coste_fabrica.md`.

Automatismos: rehace solo los clips cuyo **texto** cambió en el repo o cuya **voz** (adaptador, ref, temperatura,
pausa) cambió en `voces.json`; `REHACER_FRASES` rehace frases sueltas con semillas nuevas; `fabrica/localizar.py`
pasa de minuto o texto a clip + frase (`--minuto 3:05 --indice indice_master.tsv` o `--texto "…"`).

## Voces (`fabrica/voces.json`, Qwen3-TTS 12Hz 1.7B Base, solo timbre, español)

| Voz | Modelo | Temp. | Pausa |
|---|---|---|---|
| naval | LoRA `piloto/lora_qwen/B/paso_0120` + `naval_ref02` | 0,7 | 0,12 s |
| naval_kapil (Naval en episodios con Kapil, regla automática) | mismo LoRA + `naval_kapil_ref02` | 0,7 | 0,12 s |
| nivi | sin LoRA | 0,9 | 0,20 s |
| brett | `brett/paso_0130` | 0,9 | 0,30 s |
| deutsch | `deutsch/paso_0120` | 0,9 | 0,20 s |
| kapil, vitalik, ridley, qureshi, hodak, rauch, scholl | sin LoRA | 0,9 | 0,12 s |

Muestras de Kapil, Vitalik y Ridley aprobadas por el autor; Brett y Deutsch (134) sin comentario.

## Estado de producción (6-nov)

- Escuchados y buenos (`montaje`): 001 (ya `publicado`), 002–008, 010. **009 para revisar** (acento inglés en
  nombres: Facebook, YouTube, PewDiePie, Joe Rogan… frases 3, 10, 25, 45, 46, 48, 49, 62 de `002naval.wav`; el
  autor dará minutos).
- Generados sin escuchar (`tts`): 011–051 (017–036 el 6-nov: 95 min, ~6,4 u; 5 frases sospechosas en 018,
  027, 028 y 034; 040–051 el 6 y 7-nov) y 068 (Kapil, 39,7 min). 052 (recopilación de 001–050, desde su propia traducción): generado el 8-nov, 233,7 min, 9,45 u. **2019 completo.**
- Cortos dentro de largos (`docs/cortos-y-largos.md`, `cortos.json`): 053–067 ⊂ **077**, 072–076 y 078–104 ⊂
  **105**, 106–129 ⊂ **130** (mismo español, 1.580 de 1.580 frases idénticas). **Decidido (6-nov): se genera solo
  el largo y los cortos se montan con sus clips**; hecho el 8-nov: `fabrica/cortos.ipynb` (sin GPU) (~15 unidades; emparejar por voz + frases,
  no por `speaker`: «Brett Hall» frente a «Brett»).
- Registro de escucha: bloque `escucha` de `metadata.es.json` (`escuchado`, `resultado` bueno/revisar, `fecha`,
  `feedback`); `INDICE.md` lo muestra (`python3 scripts/indice.py`). Las altas en plataformas las lleva otra sesión.

## Pendiente: cortos del 154 que pasan por la fábrica

Al montar los cortos del **154** con `cortos.ipynb`, dos intervenciones no tienen pareja en el largo y se quedan sin
hacer (el cuaderno las lista): **`2025/139-inspiration` → `001nivi.wav`** (intro propia de Nivi) y
**`2025/144-find` → `001naval.wav`** (el largo b15 lleva además «Por ejemplo, fíjate en el marketing.»). Después de
montar, lanzar la fábrica normal sobre esos dos episodios: genera solo esas dos intervenciones (las demás ya están
al día) y monta sus masters. Celda 2: `EPISODIOS = ["2025/139-inspiration", "2025/144-find"]`, el resto como
siempre. Segundos de GPU. Los cortos de 077, 105, 130 y 160 emparejan al 100 %: no necesitan este paso.

## Pendiente: LoRA de los seis invitados (11-nov)

La sesión local construye los datasets de **ridley, vitalik, qureshi, hodak, rauch y scholl** (en serie, Ridley
primero; train 30-45 min, eval 3-4 min, receta de Brett; mitad o más del train sale de podcasts externos, otro micro
y otra sala). Cada uno llega a `gdrive:fine_tunned_naval/datasets/<voz>/` solo tras la escucha y el OK del autor, con
los minutos finales. **Hasta entonces no se lanza nada que dependa de ellos.**

Preparado sin GPU: los cuadernos 01, 03 y 04 del piloto aceptan las seis voces (`rutas.VOCES_LORA`). Frases de la
escucha a ciegas del 04: tres por voz sacadas de su propia traducción (`piloto/frases_prueba_voces.json`, ids
`ri`, `vi`, `qu`, `ho`, `ra`, `sc` 01-03; regla fija en `piloto/elegir_prueba_voces.py`). Por voz: 01 (T4, ~60 min)
→ 03 (T4, ~15 min) → 04 (L4) → escucha → `voces.json` → regenerar sus clips (070, 071; 131, 132; 160 y extras).

Qureshi (12-nov): 16 min de train; va el último, con checkpoints cada 20 pasos, y si no gana a `base` en la escucha
se queda zero-shot (solo ~10 min de doblaje en 131 y 132).

## Coste y rendimiento medidos (base para optimizar)

- Frase a frase en L4 (2-nov, 044): **4,58 s de GPU por s de audio**.
- Por lotes de 8 frases en T4 (desde el 3-nov): **2,0–2,8 s/s**, típico ~2,2 (≈ 2,2 min de ejecución por minuto de
  audio). 068: 39,7 min de audio en ~92 min. Unas **5 unidades por hora de audio** (tarifa supuesta T4 1,96 u/h).
- Lo traducido (~116 episodios, ~1.300 min) costaría ~110 unidades; con el truco de los largos y el 052 montado,
  bastante menos.

Dónde se va el tiempo y qué limita (para la tarea de optimización):

- Qwen genera paso a paso (12,5 pasos/s de audio × 16 códigos con el sub-talker): GPU poco usada, dominada por
  lanzamientos de kernels; el lote ayuda casi linealmente hasta llenar memoria.
- **Memoria de la T4 (15 GB) justa**: Qwen 1.7B fp16 (T4 no tiene bf16) + LoRA PEFT sin fusionar + Whisper
  large-v3 fp16 con marcas por palabra (atención eager). Whisper no cabe a 4 y baja solo a 2; Qwen parte el lote si
  no cabe. Se libera memoria (gc + empty_cache) tras cada lote.
- Whisper revisa todas las frases: hasta el 8-nov large-v3 con marcas por palabra (~37 % del tiempo); desde el 8-nov **turbo con marcas por segmento** (~15 veces más rápido, `docs/optimizacion/README.md`).
- Lote: hasta el 8-nov, frases de una misma intervención (máx. 8); desde el 8-nov, **lotes por voz**: frases de varias intervenciones seguidas de la misma voz (hasta 48) en lotes de 16. Con turbo, 042: **0,62 s de T4 por s de audio** (antes 2,20), ~1,3 u por hora de audio.
- Tope de pasos por frase: `tope_pasos` = 12,5 × (caracteres/7 + 3).
- Reintentos: hasta 2 con semillas nuevas (pocos en la práctica: 0–7 por episodio).
- Sesión: carga de modelos (~2–5 min) y ratos parados se pagan igual.

Investigación del 6-nov con plan priorizado: `docs/optimizacion/README.md`. **Paso 1 hecho (6-nov):** cada clip
guarda en `registro_tts.jsonl` `tiempos` por fase (qwen, whisper, revision, ritmo, escritura, otros), `lotes`
(tamaño, segundos, audio máx./suma, tope) y `pico_gb`; el informe y la celda 5 dicen el reparto, y la celda 6 el
de la sesión (carga de modelos, fases, resto parado).

Ideas abiertas, sin probar: lotes entre intervenciones de la misma voz; fusionar el LoRA (merge) y quitar PEFT;
Whisper más ligero (large-v3-turbo, distil) o en CPU, o sin marcas por palabra; torch.compile / CUDA graphs /
SDPA; motores de inferencia más rápidos para Qwen3-TTS; L4 o A100 si el lote grande compensa la tarifa; generar
largos y montar cortos; montar el 052; evitar ratos parados (encadenar episodios en una sola sesión).

## Documentos

`docs/sop-episodio.md` (SOP de escucha y arreglos), `fabrica/README.md`, `docs/estado.md`, `docs/fabrica-de-voz.md`,
`docs/contexto-sesion-global.md`, `docs/cortos-y-largos.md`, `piloto/resultados/resumen.md` (todas las escuchas a
ciegas), `docs/prompt-sesion-traduccion.md`.
