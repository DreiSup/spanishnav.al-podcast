# Optimización de la fábrica (investigación del 6-nov)

Cuatro investigaciones en paralelo, solo lectura y sin GPU. Los informes completos están en esta carpeta y los
scripts de análisis en `scripts/`:

- `informe_qwen.md`: velocidad del modelo, con el código fuente de qwen-tts 0.1.1 leído.
- `informe_whisper.md`: la revisión.
- `informe_gpu.md`: GPU y tarifas de Colab.
- `informe_trabajo.md`: audio que no hace falta generar.

**Ninguna cifra de tiempo está medida en GPU**: son estimaciones a partir del código y de simulaciones con los
transcripts del repo. Lo único medido sigue siendo ~2,2 s de T4 por segundo de audio, que da unas 5 u por hora de
audio.

Punto de partida: quedan ~1.300 min de audio traducido, unas **109 u** al ritmo actual.

## Lo que se ha aprendido

1. **Casi todo el tiempo es Qwen** (~90 %); Whisper se lleva ~5–12 %, según una estimación sin medir. Aligerar
   Whisper (large-v3-turbo) da poco: ~3–6 %.
2. **El lote paga por su frase más larga.** El bucle de generación sigue calculando las frases que ya acabaron
   hasta que acaba la última (`generation/utils.py:2835`). Hoy el lote medio tiene 5,5 frases de 8, con un 23 % de
   relleno, porque solo agrupa frases de **una** intervención. El 29 % de las intervenciones tienen 3 frases o
   menos.
3. **Qwen está limitado por Python y por los lanzamientos de kernels, no por la GPU.** Usa dos `generate()` de
   Hugging Face anidados: el sub-talker repite el preparado de HF 16 veces por paso, con una sincronización CPU-GPU
   en cada token. Por eso una GPU más cara apenas acelera cada paso. La ganancia está en lotes más llenos y en
   quitar el coste fijo de Python.
4. **Los 71 cortos coinciden al 100 % con su largo** (1.580 de 1.580 frases idénticas). El **052 no coincide**
   con 001–050: se tradujo aparte y solo el 34 % de sus frases es igual.
5. **No hay frases repetidas** en el catálogo, así que una caché global de frases no ahorra nada.
6. **El audio de una frase depende de con qué frases va en el lote**, por la semilla del lote y el relleno. Cambiar
   la forma de agrupar cambia el audio de lo que aún no está generado, nunca el de lo ya aprobado mientras no se
   regenere.
7. **Las tarifas de `voces.json` (T4 1,96 u/h) pueden estar infladas.** Fuentes de 2026, de segunda mano, dan T4
   ≈ 1,2 y L4 ≈ 1,7. El dato real está en Colab → *Ver recursos*.
8. **Riesgo de pagar GPU parada**: si falla una celda con «Ejecutar todo», la celda 7 (desconectar) no se ejecuta.

## Primera medida real (6-nov, 041–045, T4)

| Fase | s de GPU por s de audio | Parte del tiempo |
|---|---|---|
| Qwen | 1,37–1,73 | ~60 % |
| **Whisper** | **0,83–1,13** | **~36–42 %** |
| Revisión, ritmo, escritura, master | ~0 | <1 % |

**Whisper pesa mucho más de lo estimado** (se suponía 5–12 %). El motivo está en el registro: Whisper revisa **de una
en una** (`batch: 1`), porque en algún momento de la sesión se quedó sin memoria con 4 y con 2, y la fábrica recuerda el
tamaño que cupo hasta el final. Pico de memoria: Qwen 7–8,5 GB, Whisper 11,8 GB (con Qwen cargado al lado). Esto
sube al primer puesto **Whisper large-v3-turbo** (decoder de 4 capas en vez de 32, ~1,5 GB menos): podría quitar
buena parte de ese 40 % **sin cambiar el audio**, y con memoria libre volvería a revisar en lotes.

## Lotes por voz (8-nov): activado por defecto

Prueba con el 042 (6,5 min) en `042 …/lotes_voz/`, T4, con lotes por voz y Whisper turbo · segmento:

| | Qwen | Whisper | Total | s de GPU por s de audio | Unidades |
|---|---|---|---|---|---|
| 042 original (6-nov: por intervención, large-v3 · palabra) | 528 s | 320 s | 849 s | 2,20 | 0,46 |
| 042 lotes por voz + turbo (8-nov) | **212 s** (−60 %) | **27 s** (−92 %) | **241 s** | **0,62** | **0,13** |

Cero reintentos y cero sospechosas. **3,5 veces más barato por minuto de audio.** El autor lo escuchó (8-nov): «suena perfecto». Activado en `voces.json` (`motor.agrupar = voz`).


`voces.json` → `motor.agrupar`: `intervencion` (por defecto, lo de siempre) o `voz`. Con `voz`, la fábrica junta las
frases de varias intervenciones seguidas de la misma voz (hasta `tanda_voz`, 48) y las genera en lotes de hasta
`lote_voz` (16), ordenadas por longitud; cada clip se escribe después en su turno, como siempre. Si Qwen se queda sin
memoria, parte el lote y recuerda el tamaño que cabe. Si se corta a mitad de una tanda, al relanzar se repite esa tanda.
Probado sin GPU (motor falso): con `intervencion` el audio sale idéntico byte a byte; con `voz` el 042 se genera en 5
pasadas (16+16+16+14 de Naval y 2 de Nivi) en vez de 14, y reanuda bien tras un corte. **Cambia el audio de lo que se
genere** (otras semillas y otra agrupación): primero, prueba de escucha con el 042 en una subcarpeta
(`AGRUPAR = "voz"` en la celda 2).

## Whisper turbo con marcas por segmento (8-nov): activado

`fabrica/comparar_whisper.ipynb`, con 200 frases reales de 018, 027, 034, 041, 051 y 068 y 60 averías fabricadas,
comparado con la decisión que tomó large-v3 (marcas por palabra) al generarlas:

| Configuración | Iguales | Averías | s/s de audio | Pico | |
|---|---|---|---|---|---|
| turbo · segmento | 97,0 % | 58/60 | 0,06 | 4,7 GB | **elegida** |
| large-v3 · segmento | 97,0 % | 56/60 | 0,32 | 13,8 GB | no vale |
| turbo · palabra | 97,5 % | 59/60 | 0,52 | 7,7 GB | vale, pero junto a Qwen iría de una en una |

En producción large-v3 con marcas por palabra iba a ~0,9 s/s (de una en una: las marcas por palabra guardan la atención
de todas las capas, ~3 GB por frase). Las «no coincide» en frases reales son casi todas a favor de los nuevos (reglas
de normalización posteriores: adonde, cifras). Se escapan 2 de 30 colas fabricadas, cuando Whisper no escribe lo que
sobra y el segmento llega al final del audio; lo cubre la escucha del master. Activado en `voces.json` el 8-nov
(`modelo_asr`, `marcas_asr`); no rehace clips. Ahorro esperado: ~1/3 del tiempo de cada episodio.

## Decisiones del autor (6-nov)

- **Paso 1 (medir y seguro de desconexión): hecho.** Está en la rama, probado sin GPU, y el audio sale idéntico. Se
  estrena en la próxima ejecución normal.
- **Cortos desde el largo (paso 2): sí.** Se genera el 077, el 105 y el 130, y los cortos se montan con sus clips.
- **052 (paso 3): no se monta.** Se genera entero desde su propia traducción, como un episodio más (~23 u).

## Plan priorizado

| # | Medida | Ahorro estimado | ¿Cambia el audio? | Coste de probarlo |
|---|---|---|---|---|
| 1 | **Medir**: cronómetros por fase (Qwen, Whisper, escritura), pasos y memoria pico en `registro_tts.jsonl`, y desconexión garantizada aunque falle una celda | 0 (decide todo lo demás); evita GPU parada | No | 0 u: se mide en la próxima ejecución normal |
| 2 | **Cortos desde el largo**: sembrar los clips de 053–067, 072–076, 078–104 y 106–129 con los del 077, 105 y 130, emparejando por voz + frases (el nombre del hablante no coincide: «Brett Hall» frente a «Brett») | **~15 u** | No (los cortos aún no están generados) | 0 u: se monta sin GPU |
| 3 | **052 uniendo masters de 001–050** (+ ~10 min propios) | **~23 u** | No, pero **se descarta la traducción propia del 052**: decide el autor | 0 u |
| 4 | **Lotes por voz en todo el episodio** (frases de varias intervenciones de la misma voz, ordenadas por longitud, lote 16–24; guardar solo la última capa de estados ocultos para que quepa) | **40–60 % del tiempo de Qwen** | Sí, en episodios futuros: escucha rápida en el cuaderno | ~0,5 u |
| 5 | **CUDA graph del sub-talker** (sobre un bucle propio en vez de `generate()`; base: faster-qwen3-tts, MIT) | **otro 45–60 %** de Qwen, que se multiplica con el 4 | Sí: escucha rápida | ~0,5 u; 1–2 días de trabajo |
| 6 | Fusionar el LoRA por voz (restaurando desde una copia, sin merge/unmerge) | 15–20 % sin el 5; 2–5 % con él | Sí (redondeo fp16): escuchar las erres de Naval | ~0,2 u |
| 7 | Whisper large-v3-turbo | 3–6 % y −1,5 GB | No, si toma las mismas decisiones: se comprueba con frases ya generadas | ~0,2 u |
| 8 | Pequeños: reintentos agrupados al final; rehacer solo las frases cuyo texto cambió; tope de pasos por frase | 2–5 % | No | 0 |

Descartado: `torch.compile` (recompila sin parar), Whisper en CPU, caché global de frases, H100/TPU, paralelizar
sesiones (no ahorra unidades) y motores alternativos (ninguno cubre a la vez Base + x-vector + LoRA + lotes + T4).

**Cuenta a ojo**: 2 + 3 bajan lo pendiente de ~109 a ~71 u; con 4, a ~40; con 5, a ~25. Más rápido en la misma
proporción. Las cifras de 4 y 5 son estimaciones: el punto 1 dirá si se cumplen. La simulación predecía ~4× por
lotes, pero lo medido fue ~2×, y falta saber por qué.

GPU: con lotes grandes, la T4 probablemente sigue siendo la más barata. Si las tarifas reales fueran T4 1,2 y L4
1,7, convendría una prueba de 5 min en L4. Ojo: en L4/A100 la fábrica usa bf16 y el audio cambia.
