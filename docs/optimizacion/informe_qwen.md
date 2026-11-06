# Velocidad de inferencia de Qwen3-TTS en la fábrica (T4): informe

Fecha: 2026-11-06. Solo investigación: no se ha tocado el repo. Fuentes leídas:

- `qwen-tts==0.1.1` (wheel de PyPI, descomprimido en `qwen_src/ext/`). Las citas `modeling:N` son de
  `qwen_tts/core/models/modeling_qwen3_tts.py`, `inference:N` de `qwen_tts/inference/qwen3_tts_model.py` y
  `tokenizer:N` de `qwen_tts/core/tokenizer_12hz/modeling_qwen3_tts_tokenizer_v2.py`.
- `transformers==4.57.3`, la versión que fija qwen-tts (`METADATA: Requires-Dist: transformers==4.57.3`), en
  `tf_src/ext/`. Las citas `hf_utils:N` son de `transformers/generation/utils.py`.
- `faster-qwen3-tts==0.5.4` (wheel de PyPI, en `ext_repos/fq/ext/`).
- `fabrica/fabrica.py`, `fabrica/voces.json`, `docs/contexto-fabrica.md` y los 134 `transcript.es.json` del repo
  (simulación de lotes: `scripts/sim_lotes.py`).

Bloqueado desde esta sesión: huggingface.co (no he podido leer el `config.json` real del 1.7B; uso las dimensiones
publicadas: talker de 28 capas, hidden 2048, 16 cabezas, 8 KV, head_dim 128; sub-talker de 5 capas, hidden 1024),
docs.vllm.ai y la API de GitHub para repos ajenos. No había torch instalado y no he instalado nada pesado, así que
**ninguna cifra de tiempo es medida aquí**: son estimaciones a partir del código, más las cifras publicadas por
faster-qwen3-tts.

---

## 1. Resumen y lista priorizada

| # | Cambio | Ahorro estimado en el tiempo de Qwen | ¿Cambia el audio? | Esfuerzo | Prueba sin GPU / prueba mínima en GPU |
|---|---|---|---|---|---|
| 0 | **Medir antes de nada**: tiempo de Qwen, de Whisper y del resto por clip, pasos por lote, ms/paso por tamaño de lote, memoria pico | 0 % (sirve para decidir) | No | 1 h | Motor falso / 0 min extra (va con la producción) |
| 1 | **Lotes entre intervenciones de la misma voz** (todo el episodio), lote 16–24, ordenados por longitud | **40–60 %** (simulado: el coste baja al 41–59 % del actual con lote 16 y al 31–54 % con lote 24) | **Sí** (otra agrupación y otras semillas; misma calidad esperada) | Medio (≈1 día) | Motor falso que registra lotes / 10 min de T4 |
| 1b | Requisitos de 1: decodificar en sub-lotes y no guardar los estados ocultos de las 28 capas | 0 % (memoria: libera ≈ lo mismo que ocupa la caché KV) | No (decodificar: prácticamente idéntico; estados ocultos: idéntico) | Bajo | Pruebas de lógica / 5 min de T4 midiendo memoria |
| 2 | **Tope por frase dentro del lote** (criterio de parada por fila), y recalibrar `tope_pasos` con los registros | 0–10 % (sube cuanto mayor es el lote) | **No** para las frases normales; solo corta antes las desbocadas | Bajo-medio | Prueba de lógica / 3 min de T4 |
| 3 | Bucle propio del sub-talker en vez de `code_predictor.generate()` de HF, con las mismas operaciones | 5–10 % | **No** (idéntico bit a bit si replica las operaciones; hay que comprobarlo) | Medio | Modelo diminuto de pesos aleatorios en CPU (Colab sin GPU) / 2 min de T4 |
| 4 | **CUDA graph del sub-talker por lote** (caché estática de 17 posiciones, temperatura en un tensor) | **45–60 %** | **Sí** (otra caché, otras reducciones y otro consumo del RNG) | Medio-alto (1–2 días) | Igual que 3, más una comparación de distribuciones / 10 min de T4 y una escucha a ciegas |
| 5 | Fusionar el LoRA en los pesos por voz (restaurando desde una copia, no con `unmerge`) | 15–20 % en eager; 2–5 % si ya está 4 | **Sí** (redondeo fp16 del peso fusionado) | Bajo-medio | Prueba de restauración exacta en CPU / 5 min de T4 y escucha A/B de las erres de Naval |
| 6 | CUDA graph también del talker (28 capas, caché estática) | 15–25 % adicional sobre 4 | Sí | Alto | Igual que 4 |
| 7 | `torch.compile` | Incierto | Sí | Alto y frágil | No recomendado |
| 8 | Cambiar de motor (faster-qwen3-tts, vllm-omni, GGUF, TensorRT) | — | Sí | Alto | No recomendado hoy; faster-qwen3-tts sirve como código de referencia para 4 y 6 |

Ya está hecho: `attn_implementation="sdpa"` (`fabrica.py:547`; el modelo lo respeta en `modeling:788-789`).
`torch.backends.cuda.matmul.allow_tf32` no influye en una T4: Turing no tiene TF32 y se trabaja en fp16.

Orden recomendado: **0 → 1+1b+2 → 3 → 4 → 5**. 1 y 4 se multiplican: 1 reduce cuántos pasos hay que dar por
minuto de audio y 4 abarata cada paso. Juntos podrían dejar Qwen en **un 20–35 % de lo actual**. Cuánto baja el
total depende de qué parte del tiempo es Whisper, y eso hoy no está medido (ver el punto 0).

---

## 2. Cómo genera Qwen3-TTS (lo que dice el código)

### 2.1 La cadena de llamadas

1. `generate_voice_clone` (`inference:470-633`) tokeniza el texto, junta los argumentos de muestreo
   (`_merge_generate_kwargs`, `inference:287-354`) y llama a `self.model.generate(...)` (`inference:603-610`).
2. `Qwen3TTSForConditionalGeneration.generate` (`modeling:2022-2292`) construye el prefill de cada frase con la
   huella x-vector en una posición del prompt (`modeling:2170-2172`). Después lo rellena **a la izquierda** y genera
   la máscara de atención (`modeling:2239-2254`), y llama a **`self.talker.generate(...)`, es decir, al
   `GenerationMixin.generate` de transformers** (`modeling:2272-2278`).
3. En cada paso del talker, `Qwen3TTSTalkerForConditionalGeneration.forward` llama **otra vez a un `generate()` de
   HF**, el del sub-talker: `self.code_predictor.generate(inputs_embeds=..., max_new_tokens=15, do_sample=...,
   output_hidden_states=True, return_dict_in_generate=True)` (`modeling:1671-1680`). Son 15 pasos (un prefill de 2
   posiciones y 14 de decodificación). El sub-talker no tiene EOS (su config no define `eos_token_id`), así que da
   siempre los 15.
4. Con los 16 códigos se suman sus 16 embeddings y se calcula la entrada del siguiente paso del talker
   (`modeling:1681-1692`). Después corren el modelo de 28 capas y `codec_head` (`modeling:1713-1727`).
5. **Los códigos no se devuelven como `sequences`: se sacan de `hidden_states`.** El forward devuelve
   `hidden_states=(outputs.hidden_states, codec_ids)` (`modeling:1738`). `generate` fuerza
   `output_hidden_states=True` (`modeling:2064`; el `getattr(kwargs, ...)` sobre un dict devuelve siempre el valor por
   defecto) y recoge `hid[-1]` (`modeling:2280`). Por eso HF guarda, paso a paso, **los estados ocultos de las 29
   salidas de capa de todo el lote** (`hf_utils:2819`), aunque solo se use la última capa (`modeling:2281`). Y
   `generate_voice_clone` la descarta (`talker_codes_list, _ = ...`, `inference:603`).
6. La parada de cada frase se calcula al final: primer EOS del código 0 (`modeling:2283-2289`).
7. La decodificación a onda es `speech_tokenizer.decode` sobre **todo el lote a la vez**, relleno con −1
   (`qwen3_tts_tokenizer.py:328-329`). Va por trozos de 300 tramas (24 s) con 25 de contexto izquierdo
   (`tokenizer:886-896`, `tokenizer:1015`). Es una sola pasada no autorregresiva: un transformer de 8 capas a 12,5 Hz
   y convoluciones causales hasta 24 kHz (`decoder_dim=1536`, factores 8·5·4·3 y 2·2). Estimo unos 100 GFLOP por
   segundo de audio, del orden de 5–10 ms de T4 por segundo: **menos del 1 % del coste**. No hay que optimizarla por
   velocidad, pero sí por memoria (ver 3.1b).

### 2.2 Caché, atención y sincronizaciones

- **Caché KV dinámica** en los dos modelos: `DynamicCache()` (`modeling:1083`, `modeling:1487`), que concatena en
  cada paso (`cache_utils.py:119`, `self.keys = torch.cat([...])`). Copia la caché entera de cada capa en cada paso,
  con un tráfico de O(L²) por frase.
- **SDPA sin GQA en lote**: con máscara de relleno (lote > 1) transformers no usa `enable_gqa` y **repite K y V de
  8 a 16 cabezas en cada capa y cada paso** (`integrations/sdpa_attention.py:65-70`, `use_gqa_in_sdpa` exige
  `attention_mask is None`).
- **La RoPE multimodal se recalcula en cada capa** (`modeling:705-712`, con clone y copias estriadas en las 28 capas
  aunque el cos/sin es el mismo).
- **Sincronizaciones CPU↔GPU por paso**: en el bucle de HF, `this_peer_finished = unfinished_sequences.max() == 0`
  (`hf_utils:2843`) se evalúa como bool de Python en `_has_unfinished_sequences` (`hf_utils:2597`). Es una
  sincronización por token, así que **16 por paso del talker** (1 del talker y 15 del sub-talker). Hay otra en
  `cache_position[0] == 0` (`modeling:1696`). Además, cada `code_predictor.generate()` repite todo el preparado de
  HF: copia de `generation_config`, validación, lista de procesadores de logits y criterios de parada, y una caché
  nueva.
- Muestreo: HF pasa los logits a float32 (`hf_utils:2800`), aplica temperatura, top-k=50 y top-p=1,0 (se omite) y
  llama a `torch.multinomial` (`hf_utils:2829`). En el talker se añaden la penalización de repetición 1,05 y la
  supresión de 1023 tokens (`modeling:2058-2063`).

### 2.3 Cuántas operaciones hay por paso (estimación por lectura, no medida)

Por capa en eager hay unas 60–70 operaciones de GPU: RMSNorm son ~8 (`modeling:605-610`) y hay 4 por capa
(entrada, salida, q_norm y k_norm), más 4 proyecciones, RoPE, caché, SDPA y MLP.

| Parte | Operaciones por paso del talker |
|---|---|
| Talker: 28 capas × ~70 | ~2.000 |
| Sub-talker: 15 pasadas × 5 capas × ~60, más muestreo y contabilidad de HF | ~4.900 |
| LoRA sin fusionar (q,k,v,o: ~4 operaciones extra por módulo; **se aplica también a las 5 capas del sub-talker**, porque `target_modules=["q_proj","k_proj","v_proj","o_proj"]` casa por nombre: `piloto/construir_cuadernos.py:510`) | 28×16 + 75×16 ≈ 1.650 |
| **Total** | **~8.500**, de las que **~70 % son del sub-talker** y **~19 % del LoRA** |

faster-qwen3-tts habla de «~500 lanzamientos pequeños por paso». Sospecho que cuenta solo los grandes. En
cualquier caso, la conclusión es la misma: la GPU apenas trabaja y el tiempo se va en Python y en lanzamientos.
**Hay que confirmarlo con `torch.profiler` (2 min de T4, prueba G1).**

Mínimo físico en T4 (memoria): leer los pesos del talker (~2,8 GB) más 15 veces los del sub-talker (~0,16 GB por
pasada) son ~5 GB por paso, unos 20–25 ms a 220–300 GB/s **para cualquier lote hasta ~32** (sigue limitado por
memoria, no por cómputo: a B=32 son ~170 GFLOP por paso). faster-qwen3-tts mide en T4 con CUDA graphs y lote 1
**RTF 0,925 para el 1.7B (≈86 ms por paso, ≈1,08 s de GPU por s de audio)**, unas 2 veces mejor que su referencia
en eager.

### 2.4 Memoria por frase del lote (estimación)

- Caché KV del talker: 28 capas × 2 × 8 cabezas × 128 × 2 B ≈ **112 KB por token**.
- Estados ocultos acumulados (punto 5 de 2.1): 29 × 2048 × 2 B ≈ **119 KB por token**.
- Una frase de 20 s son ~250 pasos más ~60 de prefill, unos **70 MB por fila**. Con B=32 son ~2,3 GB, más
  temporales (repeat_kv y la concatenación de la caché).
- **Decodificador**: activaciones de 96 canales a 24 kHz más los temporales de SnakeBeta y las unidades residuales.
  Estimación gruesa: **0,1–0,5 GB por fila** según la duración (todo el lote rellenado a la más larga). **Es
  probablemente el pico de memoria del lote**, y llega *después* de haber gastado la generación. Hay que medirlo
  (G2).

---

## 3. Evaluación de cada propuesta

### 3.0 Medir primero (imprescindible)

Hoy `segundos_generacion` (`fabrica.py:367`) mezcla Qwen, Whisper, reintentos, recorte y escritura en Drive. Los
números no cuadran con un modelo puramente limitado por lanzamientos: según la simulación, pasar de lote 1 a lotes
medios de 5,5 debería abaratar Qwen unas 4 veces, y lo medido es 4,58 (L4, frase a frase) → 2,2 (T4, lotes). Puede
que Whisper ya sea una parte grande, o que la T4 (a menudo limitada por potencia en Colab) no esté tan desocupada
como se cree. Sin separar los tiempos no se sabe dónde está el premio.

Qué añadir al registro: `t_qwen` (con `torch.cuda.synchronize()` antes de cada medida), `t_whisper`, `t_resto`,
`pasos` (la longitud de los códigos más larga del lote), `tam_lote` y `torch.cuda.max_memory_allocated()` por
lote. No cambia el audio. Prueba sin GPU: el motor falso devuelve tiempos y comprueba que el registro los suma.

### 3.1 Lotes mayores y lotes entre intervenciones

**Lo que dice el código:**

- El coste de un lote es **el número de pasos de la frase más larga por el coste de un paso**. HF solo para
  cuando todas las filas han dado EOS (`hf_utils:2843`) o al llegar a `max_new_tokens`. Las filas acabadas siguen
  calculándose con un token de relleno (`hf_utils:2835`), y el sub-talker corre igual para todo el lote
  (`modeling:1671`).
- Mientras se esté limitado por lanzamientos, el paso cuesta casi lo mismo con 1 que con 32 filas. El coste
  marginal crece por el tráfico de la caché: con B=8 y L=300, concatenar más repeat_kv mueve ~0,8 GB por paso
  (~3 ms); con B=32 y L=500, ~5,5 GB (~20 ms, un 10 % de un paso eager). En la simulación lo he modelado como
  β = 0–0,08 por fila extra.

**Simulación con los 134 transcripts** (12.034 frases, ~1.290 min de audio; duración = caracteres/15 con una
variación aleatoria fija por frase de σ=15 %; reparto en lotes iguales como `generar_bloque`; 3 pasos de prefill por
lote). Resultado de `scripts/sim_lotes.py`:

| Estrategia | Tamaño medio del lote | Relleno | Coste relativo al actual (β=0 / 0,03 / 0,08) |
|---|---|---|---|
| Frase a frase | 1,0 | 0 % | 404 % / 356 % / 297 % |
| **Actual: por intervención, lote 8** | **5,54** | 28,5 % | 100 % |
| Por intervención, lote 16 | 7,64 | 37,4 % | 79 / 84 / 91 % |
| Misma voz en el episodio, lote 8 | 7,46 | 20,5 % | 69 / 72 / 76 % |
| **Misma voz, lote 16** | 13,7 | 26,7 % | **41 / 49 / 59 %** |
| **Misma voz, lote 24** | 19,1 | 30,6 % | **31 / 41 / 54 %** |
| Misma voz, lote 32 | 23,6 | 33,7 % | 26 / 38 / 52 % |

Hoy 1.421 de las 12.034 frases (11,8 %) van en lotes de 1 a 4. Una intervención media tiene 8,9 frases, pero un
episodio tiene solo ~10 intervenciones de 2–3 voces. Por eso **subir el lote sin cruzar intervenciones apenas sirve
(−16/−21 %)**, y cruzarlas sí.

- **Entre episodios**: aporta poco más. Un episodio ya tiene ~90 frases, casi todas de Naval y Nivi; solo ayudaría
  a los invitados con pocas frases. Añade complejidad (dos carpetas de Drive, reanudación). Solo tiene sentido como
  parte de «encadenar episodios en una sesión», y no por el lote.
- **Mismo adaptador y misma temperatura**: la temperatura es un escalar de `generate` (`modeling:2032-2039`) y el
  adaptador se elige por lote (`fabrica.py:612-618`), así que el lote tiene que ser de una sola voz. Mezclar voces
  en un lote (PEFT `adapter_names` más temperatura por fila) exigiría reescribir el muestreo: no compensa.
- **Ordenar por longitud**: ya se hace dentro de la intervención (`fabrica.py:178`). Con el conjunto de la voz
  entera, el relleno baja del 28,5 al 20,5 % con el mismo lote 8.
- **Cuidado con las frases desbocadas**: una frase que no para obliga a todo el lote a llegar a
  `max(tope_pasos)` del lote (`fabrica.py:625`). Para una frase de 95 caracteres eso es ≈ 2,6 veces su duración
  normal (`tope_pasos` = 12,5·(c/7+3) frente a 12,5·c/15). Con lotes de 24 cada desbocada encarece 24 frases, de ahí
  la propuesta 2.

**Cuánto cabe en la T4**: pesos de Qwen ~4,3 GB (el talker con su embedding de texto, el sub-talker, el codificador
de huella y el tokenizador de voz) más Whisper large-v3 ~3,1 GB dejan ~7 GB. Con 1b (sin estados ocultos de todas
las capas y con decodificación en sub-lotes de 8), **B=24–32 debería caber con Whisper cargado**; sin 1b, B=16 ya
es arriesgado por el pico del decodificador. Qwen y Whisper no necesitan memoria de activaciones a la vez porque
corren uno detrás del otro, así que **no hace falta sacar a Whisper de la GPU**, solo no solapar sus picos (ya se
libera con `empty_cache` entre ellos, `fabrica.py:601-602`). Mover Whisper a la CPU (2 vCPU) sería mucho más lento.
Estimaciones a confirmar con G2.

**Cómo hacerlo** (esbozo): `generar_episodio` reúne las frases pendientes de **todos** los clips, agrupadas por voz.
`generar_bloque` las genera y revisa como hoy, con lote 16–24 y los reintentos juntos por voz. Cada frase se
escribe en `tts/frases/` al salir (ya existe `ruta_frase`, `fabrica.py:293-296`), para poder reanudar. Después se
arman los clips, el registro, el master y el informe como ahora. `rehacer` no cambia: ya agrupa solo lo pedido.

**¿Cambia el audio?** Sí (ver §4): otra composición del lote, otra semilla (`semilla("|".join(textos))`,
`fabrica.py:620`) y otra posición en el lote. La calidad esperada es la misma, porque el relleno a la izquierda con
máscara y las posiciones RoPE calculadas desde la máscara (`modeling:1699-1704`, `modeling:1794-1798`) hacen cada
fila equivalente a generarla sola. Los episodios ya aprobados no se tocan salvo que se regeneren.

**Pruebas sin GPU**: un motor falso que (a) registra cada llamada a `sintetizar_lote` (textos, voz, intento) y
(b) devuelve audio de duración proporcional a los caracteres. Comprobar: una sola voz por llamada, como mucho
`lote` frases, cada frase exactamente una vez por intento, clips armados en el orden del JSON, reanudación tras
cortar a mitad (matar el proceso en la llamada k) y `rehacer` igual que hoy.
**GPU (G2, ~10 min de T4)**: 32 frases reales de Naval, B ∈ {8, 16, 24, 32} con Whisper cargado. Medir s/paso,
s de GPU por s de audio y memoria pica en generación y en decodificación.

### 3.1b Memoria: estados ocultos y decodificación por sub-lotes

- **Estados ocultos**: un parche que haga que el forward del talker devuelva solo la última capa,
  `hidden_states=((outputs.hidden_states[-1],), codec_ids)`, porque `modeling:2281` solo usa `hid[0][-1]`. Ahorra
  ~119 KB por token y fila (≈ tanto como la caché KV). **Salida idéntica.** Lo mismo con `output_hidden_states=True`
  del sub-talker (`modeling:1678`): no se usa.
- **Decodificar en sub-lotes**: llamar a `self.tts.model.generate(...)` directamente (es reproducir ~25 líneas de
  `generate_voice_clone` para el caso x-vector, sin `ref_code`) y decodificar en trozos de 4–8 frases. El
  decodificador no muestrea y es causal, así que el resultado por frase no depende del lote salvo diferencias de
  coma flotante de ~1e-6 si cuDNN elige otro algoritmo: **inaudible, aunque no se garantiza igualdad bit a bit**.
  Sin GPU: test de que el troceo devuelve los audios en orden y con su longitud
  (`audio_lengths = (codes > -1).sum * 1920`, `tokenizer:1012`). GPU: incluido en G2.

### 3.2 `tope_pasos`: influye solo en las desbocadas

- En lote, el bucle se para cuando **todas** las filas dan EOS (`hf_utils:2843`) o al llegar a
  `max_new_tokens = max(tope_pasos(t) for t in textos)` (`fabrica.py:625`). Para las frases normales `tope_pasos`
  no cuesta nada: solo pone un techo.
- Problema: el tope es por lote, así que una frase corta que se desboca hereda el tope de la más larga. Además
  `Qwen3TTSForConditionalGeneration.generate` **no reenvía** kwargs extra al `talker.generate` (solo pasa
  `talker_kwargs`, `modeling:2044-2066` y `modeling:2272-2278`), así que no se puede pasar un `stopping_criteria`
  desde `generate_voice_clone`.
- Propuesta: parchear `self.tts.model.talker.generate` en cada llamada (con `functools.partial`) para inyectar un
  `StoppingCriteria` **por fila**: `input_ids.shape[1] >= tope_tensor` (con `inputs_embeds`, `input_ids` solo
  contiene lo generado). HF admite que el criterio devuelva un BoolTensor de tamaño B. **Las frases normales salen
  idénticas**: mientras el bucle sigue, el RNG se consume igual para todas las filas, y solo cambia cuándo termina
  la fila desbocada, que se repite de todos modos.
- Recalibrar: con los `registro_tts.jsonl` de Drive (no están en el repo) calcular el máximo observado de pasos por
  carácter de las frases que pasaron Whisper, por voz (Brett habla más despacio), y fijar el tope en ese máximo
  ×1,3 + 1 s en lugar de c/7 + 3 s. No cambia el audio de las frases buenas.
- Ahorro: depende de cuántas desbocadas hay (los reintentos son 0–7 por episodio y no todos son desbocadas).
  Estimo 0–5 % con lote 8 y 5–10 % con lote 24.
- Sin GPU: el criterio con tensores falsos en CPU (no hace falta el modelo). GPU (3 min): con lotes reales, comprobar que
  las frases que paran solas salen iguales bit a bit con y sin el criterio (y forzar una desbocada con un tope por
  fila artificialmente bajo para ver que esa fila se corta y las demás no cambian).

### 3.3 Sub-talker sin `generate()` de HF (salida idéntica)

Sustituir `self.code_predictor.generate(...)` (`modeling:1671-1680`) por un bucle de 15 `forward` con
`DynamicCache` y **exactamente** el mismo muestreo que HF: logits a float32 (`hf_utils:2800`), temperatura,
top-k=50 con −inf, top-p omitido porque vale 1,0, softmax y `torch.multinomial`, en el mismo orden. Quita 15
sincronizaciones y el preparado de HF por paso. Ahorro: 5–10 % del tiempo de Qwen (es solo Python). **Debería ser
idéntico bit a bit**, porque son los mismos kernels con las mismas formas y el mismo consumo del RNG. Es la base
para 3.4.

- Sin GPU: instanciar `Qwen3TTSForConditionalGeneration` con una config diminuta y pesos aleatorios en CPU (un
  runtime de Colab **sin GPU**, que no gasta unidades, o cualquier máquina con torch). Comparar los códigos de HF y
  del bucle propio con la misma semilla: deben ser iguales.
- GPU (2 min): 4 frases reales con la misma semilla; los wav tienen que ser idénticos (`np.array_equal`).

### 3.4 CUDA graph del sub-talker (el mayor ahorro por paso)

El sub-talker es un bucle **corto y de forma fija**: 15 pasadas, como mucho 17 posiciones y lote B constante
durante toda la generación. Es el caso ideal para capturarlo entero en un `torch.cuda.CUDAGraph`. Así lo hace
`faster_qwen3_tts/predictor_graph.py` (MIT): `StaticCache` de 17 posiciones (`:60`), posiciones y máscaras
precalculadas (`:63-66`, `:107-113`), las 15 pasadas desenrolladas con muestreo dentro (`:115-167`) y captura con
calentamiento (`:169-202`). Ese código es **solo lote 1**: el buffer de entrada es `[1, 2, H]` (`:69`). Hay que
generalizarlo a B, con un grafo por B o con cubos (8/16/24/32) rellenando filas falsas. La temperatura del
sub-talker **queda fija al capturar** (`model.py:215-224` la pone a 0,9), así que hay que meterla como tensor
(`logits / temp_buf`) o capturar un grafo por temperatura. Si no, **la `subtalker_temperature` 0,7 de Naval
(`fabrica.py:568`) no se respetaría**.

- Compatibilidad: los CUDA graphs funcionan en sm_75 (faster-qwen3-tts publica cifras en T4); fp16 sin problema. El
  `torch.multinomial` dentro del grafo usa el generador con offset registrado, así que es reproducible con
  `manual_seed`. Pide PyTorch ≥ 2.5.1 (faster-qwen3-tts avisa de capturas poco fiables con ≤ 2.5.0). El LoRA sin
  fusionar se captura sin problema: son más kernels dentro del grafo, de coste casi nulo al reproducirlo.
- Ahorro: el sub-talker es ~70 % de las operaciones. Con grafo, su paso baja al mínimo de la GPU (~10–15 ms frente
  a unos 100+ ms estimados en eager). **45–60 % del tiempo de Qwen** si de verdad se está limitado por lanzamientos
  (G1 lo confirma).
- **Cambia el audio**: SDPA sobre 17 posiciones con máscara en lugar de una caché que crece cambia las reducciones
  en fp16, y el RNG se consume de otra manera. Misma distribución; faster-qwen3-tts declara paridad perceptiva y
  tests de paridad de prefijo, no igualdad bit a bit.
- Sin GPU: la lógica del bucle desenrollado (sin grafo) con el modelo diminuto en CPU; con muestreo greedy debe
  dar lo mismo que HF. GPU (~10 min): captura para B ∈ {8, 16, 24}, ms/paso y una escucha a ciegas de ~10 frases
  de Naval (comparar la tasa de fallos de Whisper con el camino eager).

### 3.5 Fusionar el LoRA por voz

- Hoy: `PeftModel` sin fusionar, `set_adapter` por lote y `disable_adapter()` para las voces sin LoRA
  (`fabrica.py:549-559`, `fabrica.py:612-618`). Son ~1.650 operaciones extra por paso (§2.3) más el Python de cada
  capa LoRA: **15–20 % del tiempo de Qwen en eager**. Con CUDA graphs (3.4/3.6) el ahorro baja al tiempo de GPU de
  esas matmuls pequeñas (2–5 %).
- Cambiar de voz: no usar `merge_adapter`/`unmerge_adapter` una y otra vez, porque restar en fp16 deriva con cada
  ciclo. Guardar **una vez** una copia de los q/k/v/o originales (≈ 28×12,6 M + 5×6,3 M ≈ 384 M parámetros ≈
  **0,77 GB** fp16, en GPU o en RAM fijada) y, por voz, restaurar y sumar `B@A·escala`, calculado en fp32 y pasado a
  fp16. Coste: <0,5 s por cambio. Con 3.1 hay 2–6 cambios por episodio; sin 3.1, uno por intervención (~10 por
  episodio), que también es despreciable.
- **Cambia el audio**: el peso fusionado se redondea a fp16. El error por elemento es ≤ ½ ulp de W (≈ 2,4e-4·|W|),
  del orden del redondeo que ya tiene el modelo en fp16. No debería perderse el efecto del LoRA, pero **es justo lo
  que fija el acento** (las erres de Naval, cuaderno 09). Hay que hacer una escucha A/B antes de adoptarlo.
- Sin GPU: test en CPU de que restaurar y fusionar es exacto (los pesos restaurados son iguales a los originales
  bit a bit tras N cambios) y de que el resultado coincide con PEFT sin fusionar en fp32 (tolerancia 1e-5). GPU
  (5 min): ms/paso con y sin fusión, más 10 frases de Naval para la escucha A/B.

### 3.6 Talker con caché estática y CUDA graph

Mismo principio con las 28 capas: `StaticCache` de tamaño máximo, máscara de relleno por paso y `rope_deltas` por
fila (`modeling:1699-1711`). faster-qwen3-tts lo tiene para lote 1 (`talker_graph.py`) y faster-qwen3-tts-batch
para lotes (pero solo lo documenta con el 0.6B). El ahorro restante es el ~25–30 % de operaciones que no son del
sub-talker, y elimina además la concatenación O(L²) y el repeat_kv dinámico. Esfuerzo alto, porque la RoPE
multimodal y el relleno a la izquierda complican el grafo: hacerlo solo si después de 3.4 Qwen sigue siendo lo
que más pesa.

### 3.7 `torch.compile`

No lo recomiendo, por tres motivos:

1. Con `DynamicCache` las formas cambian en cada paso. HF solo compila automáticamente con una caché compilable
   (`hf_utils`, `_valid_auto_compile_criteria`: `using_compilable_cache`).
2. El sub-talker indexa `lm_head[generation_steps]` y `codec_embedding[generation_steps-1]` con un entero de Python
   (`modeling:1281`, `modeling:1299`): son 15 especializaciones, por encima del `cache_size_limit` por defecto de
   dynamo (8), que vuelve a eager.
3. Inductor genera kernels de Triton y **no he podido confirmar que Triton actual soporte oficialmente sm_75**
   (funciona a menudo en Colab T4, pero no está verificado). La compilación, además, cuesta minutos de sesión
   pagados.

Los CUDA graphs a mano (3.4) consiguen lo mismo sin depender de Triton.

### 3.8 Motores y ports alternativos (estado a 2026-11-06)

| Motor | Base / x-vector | LoRA | Lote | T4 | Encaje |
|---|---|---|---|---|---|
| **faster-qwen3-tts 0.5.4** (MIT, 5-oct-2026) | Sí, 0.6B/1.7B-Base; x-vector (`xvec_only=True` o `voice_clone_prompt` precalculado) | No (habría que fusionar antes de capturar) | **Solo 1** (`generate.py:107-215` trabaja con `[1,1,H]`) | Sí: 1.7B RTF 0,925 (~1,08 s/s), ~2× sobre su base | Exige `transformers>=5.15` y `qwen-tts-hf` (choca con el `qwen-tts 0.1.1` + `transformers 4.57.3` actual), dtype bf16 por defecto y **temperatura del sub-talker fija en 0,9**. Útil como **código de referencia**, no como sustituto |
| faster-qwen3-tts-batch 0.2.0 (mar-2026, un solo autor) | Solo documentado con 0.6B y `ref_text` | No consta | Sí (grafos por lote; continuo opcional) | No consta | Inmaduro; solo para inspirarse en el talker en lote |
| vllm-omni | Base con `x_vector_only_mode` por petición | No he podido confirmarlo (docs bloqueadas) | Sí (servidor) | No consta; vLLM en Turing tiene limitaciones de backend de atención | Instalación pesada en Colab, servidor aparte; hay una incidencia abierta de lentitud en A100 (#1896) |
| qwentts.cpp / GGUF (llama.cpp) | Sí 12 Hz; x-vector no confirmado | Convertir pesos fusionados a GGUF | ? | CUDA genérico | Cuantización (Q8_0…) y otro muestreo: **cambia el audio**; demasiado riesgo para las voces aprobadas |
| TensorRT-Edge-LLM (NVIDIA) | **Solo CustomVoice** 0.6B/1.7B | — | — | — | No sirve (no hay clonación) |
| concurrent-faster-qwen3-server (Rust) | Solo 0.6B-Base | — | 16 | L4 | No sirve (otro modelo) |

Conclusión: ninguno ofrece hoy, ya hecho, la combinación **1.7B-Base + x-vector + LoRA + temperatura del sub-talker
por voz + lote + T4 + fp16**. Lo razonable es implementar 3.1, 3.3 y 3.4 dentro de la fábrica, tomando prestado el
diseño de faster-qwen3-tts.

### 3.9 Nota sobre la GPU (L4 / A100)

- `MotorQwen` elige **bf16 automáticamente si la GPU lo soporta** (`fabrica.py:545`). En L4 o A100 el modelo corre
  en bf16 y en T4 en fp16, así que **el audio de una misma frase con la misma semilla cambia según la GPU**.
- Una vez quitado el cuello de botella de Python (3.4/3.6), el paso queda limitado por el ancho de banda de memoria:
  la **L4 tiene unos 300 GB/s, como la T4 (320 GB/s)**, pero cuesta 2,5 veces más (4,82 frente a 1,96 u/h). La
  A100 (~1,5–2 TB/s) cuesta 6 veces más. Con lotes grandes la T4 probablemente seguirá siendo la más barata por
  minuto de audio. Mientras se esté limitado por la CPU, decide la CPU del host de Colab, que no controlamos.
  Medirlo antes de cambiar.

---

## 4. Determinismo: ¿depende una frase de con quién va en el lote?

**Sí.** Hay tres motivos:

1. **La semilla depende del lote**: `semilla("|".join(textos), intento)` (`fabrica.py:620`), más 104729·ronda
   (`fabrica.py:621`).
2. **El RNG se consume para el lote entero**: `torch.multinomial` de HF (`hf_utils:2829`) recibe probabilidades de
   forma (B, V). Por lo que sé de PyTorch (no verificado en esta sesión), para `num_samples=1` usa el truco
   exponencial (`q = exponential_(...)`, `argmax(p/q)`): los números aleatorios de cada fila dependen de B, de la
   posición de la fila y de la configuración del lanzamiento. Cambiar el tamaño del lote o el orden cambia los
   números que le tocan a cada frase, en el talker y en las 15 pasadas del sub-talker de cada paso.
3. **Numérica**: otras formas de GEMM o de SDPA y otro relleno dan diferencias de fp16 en los logits. Basta un
   token muestreado distinto para que el resto de la frase diverja.

Es reproducible: **los mismos textos en el mismo orden, la misma semilla, el mismo modelo de GPU y las mismas
versiones de las librerías** (cuBLAS y SDPA mem-efficient son deterministas hacia delante con forma fija). No es
reproducible entre T4 y L4 (y además fp16 frente a bf16, §3.9).

Consecuencia para el flujo: lo aprobado escuchando es el wav guardado. Nada de esto lo invalida mientras no se
regenere. Cualquier cambio de agrupación (3.1), de caché o grafo (3.4, 3.6), de pesos (3.5), de tamaño de lote o de
GPU produce **otra realización** de las frases que se generen a partir de entonces. Eso ya ocurre hoy con `rehacer`,
que cambia la semilla a propósito.

## 5. ¿Altera el audio o es solo velocidad?

**Salida idéntica** (salvo error de implementación; comprobable con `np.array_equal`):

- 0 Medir.
- 1b-a Guardar solo la última capa de estados ocultos.
- 2 Tope por fila: idéntico en las frases que paran solas.
- 3 Bucle propio del sub-talker con las mismas operaciones.
- Quitar `gc.collect()`/`empty_cache()` por lote (`fabrica.py:601-602`): ahorro despreciable (<1 %); lo dejaría.

**Prácticamente idéntica** (diferencias de coma flotante ~1e-6, sin muestreo de por medio): 1b-b, decodificar en
sub-lotes.

**Cambian el audio** (misma distribución esperada, pero otra realización; requieren que el autor escuche lo nuevo
como siempre, y para 3.4 y 3.5 una escucha comparativa previa):

- 1 Agrupar entre intervenciones, o cambiar `lote`.
- 4 y 6 CUDA graphs con caché estática.
- 5 LoRA fusionado.
- 7 `torch.compile`.
- 8 Otros motores.
- Cambiar de GPU (por el bf16).

## 6. Pruebas en GPU propuestas (minutos de T4)

| Id | Qué | Duración |
|---|---|---|
| G1 | `torch.profiler` de un lote de 8 frases de Naval durante 20 pasos: % de tiempo en el sub-talker, el talker, LoRA y CPU parada; cuenta real de kernels por paso | 2–3 min |
| G2 | Banco de lotes: 32 frases reales, B ∈ {1, 8, 16, 24, 32}, con Whisper cargado; s/paso, s de GPU por s de audio, `max_memory_allocated` en generación y en decodificación | 8–12 min |
| G3 | Igualdad bit a bit de 3 (y de 2 y 1b) con 4 frases y semilla fija | 2 min |
| G4 | Grafo del sub-talker (3.4) para B ∈ {8, 16, 24}: ms/paso, más 10 frases para escuchar y la tasa de fallos de Whisper frente a eager | 10 min |
| G5 | LoRA fusionado (3.5): ms/paso y 10 frases de Naval para la escucha A/B de las erres | 5 min |

Total ≈ 30–35 min de T4, ~1–1,2 unidades.

## 7. Lo que no he podido verificar

- Las dimensiones exactas del 1.7B (HF bloqueado). Las cuentas de memoria y de pesos usan las cifras publicadas.
- Ninguna cifra de tiempo está medida aquí: el reparto de operaciones (§2.3) y los ahorros son estimaciones por
  lectura de código y por la simulación. G1 y G2 los confirman o corrigen.
- El reparto actual entre Qwen y Whisper en las T4 por lotes (no se registra por separado).
- Los detalles internos de `torch.multinomial` en CUDA (§4.2), descritos de memoria; la conclusión práctica (el
  resultado depende de B) también se sigue de 4.1 y 4.3.
- El soporte oficial de Triton para sm_75, el soporte de LoRA en vllm-omni y su funcionamiento en Turing.
- El pico de memoria del decodificador por fila (estimación gruesa).

## Fuentes

- faster-qwen3-tts en PyPI: https://pypi.org/project/faster-qwen3-tts/ (y su wheel 0.5.4)
- faster-qwen3-tts-batch: https://pypi.org/project/faster-qwen3-tts-batch/
- Speech API de vLLM-Omni (Qwen3-TTS Base, `x_vector_only_mode`): https://docs.vllm.ai/projects/vllm-omni/en/latest/serving/speech_api/
  (citado por el buscador; no se ha podido abrir desde aquí)
- Ejemplo de CUDA graph del code predictor en vllm-omni (espejo): https://bezzam-evals-voxtral.hf.space/vllm-omni/.claude/skills/add-tts-model/references/cuda-graph-example.md
- Qwen3-TTS-GGUF: https://github.com/HaujetZhao/Qwen3-TTS-GGUF · https://huggingface.co/Serveurperso/Qwen3-TTS-GGUF
- TensorRT-Edge-LLM TTS: https://nvidia.github.io/TensorRT-Edge-LLM/0.9.0/user_guide/examples/tts.html
- concurrent-faster-qwen3-server: https://huggingface.co/alfonsodlg/concurrent-faster-qwen3-server
- Incidencia de vllm-omni #1896: https://goodfirstissue.org/vllm-project/vllm-omni/issues/1795
