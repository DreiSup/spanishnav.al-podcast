# Contexto de la fábrica de voz (traspaso, 2026-11-06)

Todo lo que hace falta para seguir produciendo episodios y para optimizar la fábrica sin releer la historia. Lo
mantiene la sesión técnica. Rama: `claude/quirky-dirac-x18c3n` (pull --no-rebase antes de cada push; sin PRs).

## Reglas del autor

- Mínimo gasto de unidades de Colab. Un paso cada vez, con su confirmación. Decide escuchando (a ciegas si se
  comparan versiones; para pruebas rápidas, escucha directa en el cuaderno). Todo en español. Celdas completas.
- El autor ejecuta Colab; la sesión técnica prepara y prueba los cuadernos **sin GPU** (motores falsos) antes de
  subirlos.
- Git guarda texto; Drive guarda bytes. Nunca audio en git.

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
  027, 028 y 034; 040–051 el 6 y 7-nov) y 068 (Kapil, 39,7 min). Pendiente de 2019: el 052 = recopilación de 001–050: **se genera entero desde su propia traducción** (decisión del autor,
  6-nov).
- Cortos dentro de largos (`docs/cortos-y-largos.md`, `cortos.json`): 053–067 ⊂ **077**, 072–076 y 078–104 ⊂
  **105**, 106–129 ⊂ **130** (mismo español, 1.580 de 1.580 frases idénticas). **Decidido (6-nov): se genera solo
  el largo y los cortos se montan con sus clips**; falta implementarlo (~15 unidades; emparejar por voz + frases,
  no por `speaker`: «Brett Hall» frente a «Brett»).
- Registro de escucha: bloque `escucha` de `metadata.es.json` (`escuchado`, `resultado` bueno/revisar, `fecha`,
  `feedback`); `INDICE.md` lo muestra (`python3 scripts/indice.py`). Las altas en plataformas las lleva otra sesión.

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
- Whisper large-v3 revisa todas las frases (con marcas de tiempo por palabra para detectar cola alucinada).
- Lote = frases de una misma intervención (máx. 8); intervenciones cortas → lotes pequeños (poco aprovechamiento).
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
