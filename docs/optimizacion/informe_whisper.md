# Informe: optimizar la verificación (Whisper) de la fábrica de voz

Solo investigación; no se ha tocado el repo. Fecha 2026-11-06.

## 0. Conclusión corta

1. **Whisper es probablemente el 5–12 % del tiempo de GPU (central ~8 %), Qwen el 88–95 %.** Es una estimación
   por primeros principios, no una medida: `registro_tts.jsonl` guarda `segundos_generacion` por clip (Qwen +
   Whisper + escritura a Drive + ritmo, todo junto) y no separa nada. Por tanto **optimizar solo la verificación
   tiene un techo de ~5–12 %** (aunque Whisper costara 0). Las ganancias grandes están en el lado Qwen
   (lotes más grandes entre intervenciones, merge del LoRA, etc.), que es otro ángulo.
2. Lo que sí aporta la verificación al resto: **memoria** (Whisper large-v3 fp16 son ~3,1 GB de pesos más
   activaciones y atenciones eager) y **simplicidad de lotes** (hoy baja solo a 2 o 1 por OOM; con batch 2, el
   coste por frase de Whisper se duplica respecto a batch 4 porque el decoder va limitado por lanzamientos).
3. Orden recomendado: (a) cronometrar (0 coste), (b) microbenchmark de Whisper sobre las frases ya guardadas
   en Drive (2–3 min de GPU, sin Qwen), (c) probar `large-v3-turbo` con reproducción de decisiones sobre esas
   mismas frases, (d) solo si (a) confirma >8 %, solapar revisión y generación o CTC.
4. **faster-whisper/CTranslate2 en GPU no está disponible en Colab** (CUDA 13 vs libcublas 12; ver
   `piloto/medir.py` cabecera y `docs/estado.md:202`). No lo cuento como opción en GPU.

## 1. ¿Cuánto se lleva Whisper? (estimación)

Hechos del código:
- `medir.Asr`: pipeline HF `openai/whisper-large-v3`, fp16, `chunk_length_s=30`, `return_timestamps="word"`.
  El encoder **siempre procesa 30 s (1500 posiciones)** por frase aunque dure 6 s: ~80 % del cómputo del encoder
  es relleno. El decoder (32 capas) genera ~25–45 tokens por frase; con marcas por palabra se guardan atenciones
  cruzadas (eager).
- Tamaño de lote efectivo: 4, y según el contexto baja a 2 o 1 por OOM (`lote_que_cabe` se recuerda).
- Tras cada lote Qwen se hace `gc.collect()` + `empty_cache()` (libera y vuelve a reservar, cuesta algo).
- Las frases se escriben una a una a Drive (`_escribir_wav`) dentro del bucle del clip: posible coste de E/S oculto.

Estimación por frase de ~6 s en T4 (sin cifra publicada exacta para T4; ver §Fuentes):
- Encoder 32 capas × 1500 posiciones, eager: ~0,10–0,25 s por frase.
- Decoder 32 capas, ~35 pasos, limitado por lanzamientos de kernels (~25–40 ms/paso en HF eager): ~1,0–1,4 s
  **por lote** (casi independiente del tamaño del lote). Batch 4 → ~0,3 s/frase; batch 2 → ~0,6 s/frase.
- Extracción del log-mel en CPU (numpy, 30 s rellenos, 128 mel) en el preprocesado del pipeline: posiblemente
  0,05–0,2 s/frase en 2 vCPU (sospecha a verificar; es un coste oculto que no aparece en "GPU").
- Total: ~0,5–1,0 s por frase = 0,08–0,17 s por segundo de audio, frente a 2,2 s/s medidos → **4–8 % con batch 4,
  8–12 % con batch 2/1**. Más los reintentos (0–7 por episodio: despreciables).

Contraste: Qwen genera 12,5 pasos/s de audio con talker + sub-talker de 16 códigos; el resto de los ~2,0 s/s
es suyo. Coherente con la memoria del traspaso ("GPU poco usada, dominada por lanzamientos").

## 2. Cómo medir el reparto en la próxima ejecución

### 2.1 Cronómetros (lo primero; ~15 líneas, 0 GPU extra)
En `fabrica/fabrica.py`:
```python
from collections import defaultdict
from contextlib import contextmanager
CRONO = defaultdict(float)
@contextmanager
def crono(clave):
    import torch
    if torch.cuda.is_available(): torch.cuda.synchronize()
    t = time.perf_counter()
    try: yield
    finally:
        if torch.cuda.is_available(): torch.cuda.synchronize()
        CRONO[clave] += time.perf_counter() - t
```
Dónde envolver:
- `generar_bloque`, llamada `sintetizar_lote(...)` → `crono("qwen")`; contar `CRONO["n_lotes_qwen"]` y frases.
- `generar_bloque`, llamada `asr.transcribe_lote(...)` → `crono("whisper")`; sumar `len(audio)/sr` revisados y
  `CRONO["n_lotes_whisper"]`. Dentro de `Asr.transcribe_lote`: separar `resample` (CPU), llamada al pipeline, y
  tiempo perdido en OOM (`crono("whisper_oom")`), y guardar `batch_size` real usado.
- `revisar` + bucle de candidatos → `crono("decision")` (WER, jiwer, num2words: CPU puro).
- `ritmo.acortar_pausas` → `crono("ritmo")`; `_escribir_wav` + `ensamblar` + escritura de la fila → `crono("escritura")`.
- Memoria: `torch.cuda.reset_peak_memory_stats()` antes de cada fase y `max_memory_allocated()` después
  (`pico_qwen_gb`, `pico_whisper_gb`); también `memory_reserved()` tras el `empty_cache`.
- En `generar_episodio`: tomar `antes = dict(CRONO)` al empezar cada clip y escribir en `fila` la diferencia
  (`s_qwen`, `s_whisper`, `s_ritmo`, `s_escritura`, `s_otros = segundos_generacion − suma`). El `registro_tts.jsonl`
  ya es el sitio (una fila por clip) y `resumen_coste` puede sumarlo. Indicador final: `s_whisper / segundos_generacion`.
- Con dos o tres clips (p. ej. un episodio corto con retries 0–2) basta; no hace falta un episodio entero.

### 2.2 Microbenchmark de Whisper aislado (prueba mínima en GPU, 2–3 min, sin Qwen)
Las frases ya generadas están en Drive: `tts/frases/NNNvoz_KK.wav` + `registro_tts.jsonl` (con `transcripcion`,
`errores`, `sobra_final`, `ok` de large-v3). Un cuaderno corto: carga solo Whisper, coge ~64 frases de 2 episodios
y mide s/frase con batch 1, 2, 4, 8, 16 (sin Qwen en memoria cabe más), con y sin `return_timestamps="word"`.
Con eso: `share ≈ n_frases_del_clip × s_por_frase / segundos_generacion` usando el registro existente → reparto
**sin gastar una sola sesión de generación**. Y sirve de banco de pruebas para las alternativas del §3.

### 2.3 Sin GPU (en el entorno técnico)
Probar la instrumentación con los motores falsos que ya usa la sesión técnica (comprobar que las claves salen en
la fila y que `s_otros ≥ 0`).

## 3. Alternativas (con cifras)

Cifras de partida: ahorro como % del tiempo GPU total usando S = parte de Whisper = 8 % (rango 5–12 %).

| # | Propuesta | Ahorro est. (% total) | Riesgo de dejar pasar fallos | Esfuerzo | ¿Cambia el audio? |
|---|---|---|---|---|---|
| A | Medir (§2) | 0 | — | muy bajo | no |
| B | `large-v3-turbo` en el mismo pipeline | 3–6 % | bajo-medio | bajo | solo si cambian decisiones |
| C | Quitar el pipeline: processor + `generate` a mano, mel en GPU, lote mayor | 1–3 % | nulo | medio | no |
| D | Marcas de segmento (no de palabra) + SDPA | 1–3 % (+ memoria) | medio (hay que validar) | bajo-medio | solo si cambian decisiones |
| E | Solapar: revisar lote N mientras Qwen genera N+1 (proceso aparte) | 4–8 % (hasta S) | nulo | alto | no (semillas independientes del orden) |
| F | Dos fases por episodio (Qwen solo, luego Whisper solo, luego reintentos) | 2–5 % + memoria | nulo | medio | no |
| G | CTC español (wav2vec2/MMS) como revisor principal, Whisper solo para dudosas | 5–9 % | medio-alto hasta calibrar | alto | solo si cambian decisiones |
| H | Revisión selectiva (riesgo + muestra) | 3–6 % | medio | bajo-medio | sí, si se deja pasar algo |
| I | Whisper en CPU en paralelo | ~0 (inviable con large; small posible) | alto | alto | — |

### B. `whisper-large-v3-turbo`
- Es large-v3 con el decoder recortado de 32 a 4 capas (el encoder es el mismo)
  ([OpenAI discussion 2363](https://github.com/openai/whisper/discussions/2363)). Para frases cortas el tiempo está
  en el decoder (pasos secuenciales), así que la mejora relativa es mayor que en audio largo.
- Cifra publicada (faster-whisper, RTX 2080 Ti, clip de 13 min LibriSpeech): turbo fp16 19,2 s frente a large-v3
  fp16 52,0 s (~2,7×), WER 1,92 % vs 2,88 % en inglés limpio
  ([HF discusión "Speed benchmark"](https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2/discussions/3);
  vía búsqueda, la página no se pudo abrir desde esta sesión: huggingface.co no resuelve en la red permitida).
  En audio largo el encoder pesa más; en frases de 6 s el decoder domina, por lo que espero ≥ 2,7× en el decoder.
- Mi estimación: Whisper pasa de ~0,5–1,0 s/frase a ~0,25–0,45 s/frase → ahorra 50–65 % de S = **3–6 % del total**;
  memoria: pesos 3,1 → ~1,6 GB (−1,5 GB).
- Calidad en español: OpenAI dice que turbo rinde mejor en FLEURS (grabaciones limpias, el caso del TTS) y que su
  degradación es mayor en otros idiomas como tailandés o cantonés; no encontré una tabla es-ES large-v3 vs turbo
  fiable (dos fichas de modelos dan 10,18 % y 6,91 % para turbo base en Common Voice 17 es, protocolos distintos).
  Comunidad: más alucinaciones de turbo en clips muy cortos o ruidosos. **Para nuestro caso (TTS limpio) debería bastar,
  pero hay que validarlo con nuestras frases** (§4).
- Marcas por palabra: las `alignment_heads` de turbo existen en su generation_config (sale en scripts de conversión
  de transformers.js), y `return_timestamps="word"` del pipeline funciona; su calidad de marca final con solo 4
  capas de decoder podría ser algo peor → medir `sobra_final` frente a large-v3.

### C. Pipeline a mano
- El pipeline HF con lista de dicts hace en el hilo principal: resample, `WhisperFeatureExtractor` (STFT numpy de 30 s),
  `generate`, y postproceso DTW en CPU. Posibles ahorros: mel en GPU (`device="cuda"` en el extractor, soportado en
  versiones recientes de transformers), `generate(..., language="es", task="transcribe", return_token_timestamps=True)`
  directo, lote mayor, y ordenar por longitud. Ganancia pequeña pero segura, y habilita medir cada fase.

### D. ¿Hacen falta marcas por palabra? ¿SDPA?
- Qué se usa realmente: **solo la marca de fin de la última palabra** (`sobra = dur − fin`). El inicio no se usa
  en `revisar`.
- SDPA vs eager: en transformers las clases SDPA/FlashAttention de Whisper no devuelven `output_attentions`, y las
  marcas por palabra salen de las atenciones cruzadas, de ahí el "eager"
  ([foro HF](https://discuss.huggingface.co/t/whisper-help-me-understand-output-attentions-whispers-attention-mechanism-options/106030);
  no hay respuesta oficial en esa discusión). En versiones recientes suele caer a eager con aviso solo en la llamada
  que lo pide, o admitir configurar el encoder en SDPA y el decoder en eager (a comprobar en la versión instalada en
  Colab; no he podido probarlo aquí: sin descarga de modelos). Un benchmark de L4 con turbo ve que *lote grande con eager
  es más lento que lote pequeño con SDPA*
  ([E2E Networks](https://www.e2enetworks.com/blog/benchmarking-asr-models-nvidia-l4-parakeet-whisper-nemotron.md)).
  Tabla de comunidad: large-v3, fp16, batch 24, SDPA, audio largo: 31,5× tiempo real
  ([comparativa](https://dyl5051.substack.com/p/choosing-a-whisper-serving-framework)).
- Alternativa sin marcas de palabra: `return_timestamps=True` (marcas de segmento, tokens de tiempo de 20 ms). Para
  una frase de una sola ventana, el fin del último segmento suele coincidir con el fin del habla, pero con menos
  resolución y a veces redondeado hacia el final del audio → **hay que validar contra las marcas por palabra** con
  las ~cientos de frases ya guardadas (incluidas las 0–7 sospechosas por episodio, que son los positivos reales).
  Ventaja: SDPA completo, sin almacenar atenciones, lotes mayores.
- Heurísticas gratuitas para la cola alucinada (no requieren ASR):
  1. **Duración vs caracteres por voz**: `dur / len(texto)` tiene poca varianza en TTS; un valor > media + k·σ
     (por voz, calibrado con el registro) sospecha cola. Es barato y ya existe `cps` en el plan.
  2. **Tope de pasos alcanzado**: si `dur ≥ tope_pasos/12,5 − margen`, el modelo no emitió EOS (alucinación
     que no se para). Detectable gratis; mejor aún exponer la longitud de códigos generados desde Qwen.
  3. Energía/VAD en los últimos 0,8 s: sirve para *silencio*, no para balbuceos (que tienen energía): solo
     descarta casos obvios; no sustituye al ASR. `ritmo.acortar_pausas` ya recorta silencios de borde.
  Estas tres sirven como **filtro previo** (§H), no como sustituto.

### E. Solapar generación y revisión
- Qwen está limitado por lanzamientos de kernels (GPU con huecos): los kernels de Whisper podrían ocupar esos huecos.
- Hilo en el mismo proceso: el GIL frena a ambos (las dos cargas son bucles Python lanzando kernels). Proceso aparte
  (`torch.multiprocessing`/`spawn`, cola de entrada con los audios, salida con tuplas `(texto, inicio, fin)`): cada
  proceso consume un vCPU de los 2 de Colab y un contexto CUDA (~0,3–0,5 GB). Viable en tiempo.
- **Determinismo**: la semilla es `crc32("|".join(textos)) + 7919·intento (+ ronda)` y se reasigna con
  `manual_seed` antes de cada llamada → el audio de un lote **no depende del orden** en que se generen los lotes.
  Dentro de un bloque se puede revisar el lote k mientras se genera el k+1 y decidir reintentos al final del
  bloque con exactamente los mismos conjuntos pendientes → **audio idéntico**. Para solapar entre bloques hay que
  diferir los reintentos (composición idéntica por bloque, también idéntico).
- Límite: bloques de un solo lote (la mayoría de intervenciones cortas) no solapan nada; la última revisión de un
  bloque no se oculta. Ganancia real ≈ 50–80 % de S → 4–7 %. Incompatible en parte con B (si Whisper ya es pequeño,
  menos que ocultar).

### F. Dos fases por episodio
- Fase 1: Qwen genera todo con solo Qwen en GPU (15 GB libres); mover Qwen a CPU (≈ 4 GB, segundos) o liberar;
  Fase 2: Whisper (lote 16, sin OOM) revisa todo; Fase 3: reintentos con Qwen vuelto a la GPU, por bloque con la misma
  composición. Elimina los OOM-split de ambos, y permite lotes Qwen mayores (cuando se implementen lotes entre
  intervenciones). Costes: 2 traslados por episodio (+ si hay LoRA con PEFT, mover el modelo entero).
- Audio idéntico si los reintentos conservan la composición actual.

### G. CTC (wav2vec2/MMS) en vez de Whisper
- Un wav2vec2-large (~315 M) procesa la duración real (sin relleno a 30 s) y no es autoregresivo: ~10–40 ms por
  frase de 6 s en T4 (estimación mía) → ~20–50× más barato que Whisper large-v3. Da texto (CTC voraz) y alineación
  de caracteres/palabras; pesa ~0,6 GB.
- Alineación forzada con el texto conocido (`torchaudio` MMS_FA, entrenado con 23 000 h de 1100+ idiomas):
  [tutorial](https://docs.pytorch.org/audio/stable/tutorials/forced_alignment_for_multilingual_data_tutorial.html).
  **Ojo**: esas API están marcadas como obsoletas desde torchaudio 2.8 ("se eliminarán en 2.9"); mejor usar
  `Wav2Vec2ForCTC` de transformers + `torchaudio.functional.forced_align`, o implementar el Viterbi propio (50 líneas, numpy).
- Limitaciones para este uso: (a) alineación forzada con texto conocido **no detecta por sí sola** una cola
  añadida (el CTC absorbe o estira); hay que mirar las probabilidades de no-blanco *después* del último token
  alineado; (b) nombres ingleses, siglas y cifras: CTC en español los escribe mal → falsos positivos de WER;
  la normalización actual (num2words, etc.) tendría que recalibrarse; (c) sin puntuación/LM.
  Por tanto no sustituye a Whisper sin calibrar; sí como **primer filtro** (si CTC dice OK con margen → no se llama a Whisper).
- Distil: `distil-large-v3` oficial es solo inglés. Existen destilados multilingües de terceros:
  [whisper-large-v3-distil-multi7-v0.2](https://huggingface.co/bofenghuang/whisper-large-v3-distil-multi7-v0.2)
  (2 capas de decoder, 7 idiomas europeos incl. español; según la ficha, cercano a large-v3/turbo en español, columnas
  sin etiquetar en lo que pude ver) y `marianbasti/distil-whisper-large-v3-es` (ajustado a Common Voice 16.1, 5,11 %
  de WER). Son opciones a probar solo si turbo no basta; licencia y marcas por palabra sin verificar.
- Medium/small en español: más rápidos (small 244 M: ~0,5 GB), pero con peor WER en español y más alucinación.
  Para TTS limpio podrían bastar, aunque el ahorro adicional frente a turbo es pequeño (turbo ya tiene el
  decoder casi mínimo; el encoder del small es ~10× más barato que el de turbo). Probar solo si se quiere memoria.

### H. Revisión selectiva
Datos: 0 alucinaciones en el master escuchado, 0–7 reintentos por episodio. **Ojo con el sesgo**: ese "0" se mide
*después* de la revisión; no prueba que sin revisión fuera 0. Los reintentos (≈1 % de frases) son los fallos reales.
Propuesta de menor riesgo (en orden):
1. Filtros gratuitos sobre **todas** las frases: duración/carácter fuera de rango, tope de pasos alcanzado.
2. Whisper obligatorio para: frases con dígitos o `%`, siglas en mayúsculas, palabras de la lista de nombres ingleses
   (GLOSARIO.md), > 220 caracteres, y voces sin LoRA/temperatura 0,9 (más variables: nivi, brett, deutsch, etc.).
3. Muestra aleatoria del 20–25 % del resto, por episodio, con **escalada**: si en la muestra falla > X % (p. ej. ≥1 de
   las primeras 20), revisar todo el episodio.
Si se revisa el 40–50 %, ahorro 50 % de S = 3–5 % del total. Riesgo: fallos de una sola palabra en frases
ordinarias que ni la duración ni la muestra detectan. Con 500 frases y 1 % de fallo, una muestra del 25 % deja pasar
~4 fallos por episodio de 5 (sin escalada). **No lo recomiendo hasta tener Whisper barato (turbo): el ahorro
marginal no compensa el riesgo.** Mejor como filtro "no revisar si pasa CTC y duración".

### I. Whisper en CPU de Colab (2 vCPU)
Inviable con large/turbo: el encoder son ~1,9 TFLOP por frase (siempre 30 s), a ~50–100 GFLOPS reales → 20–40 s por
frase; el flujo produce ~1 s de audio cada 2,2 s, es decir ~una frase de 6 s cada 13 s. Incluso con int8 (faster-whisper
CPU-only, sin CUDA — podría instalarse con `av==15.1.0` como en `docs/dataset.md:39`) large-v3 queda en ~1× tiempo real
con 8 hilos en la referencia de faster-whisper, y con 2 vCPU y relleno a 30 s sería varias veces peor. Con
`small` int8 sí sería ~2–3 s por frase, pero compite con el vCPU que Qwen necesita para lanzar kernels (Qwen es
launch-bound y consume 1 vCPU entero). Descartado.

## 4. Cómo probar cada cosa SIN GPU y prueba mínima en GPU

Sin GPU (entorno técnico; **huggingface.co no resuelve desde esta sesión**, no se pueden bajar modelos):
- Instrumentación: motores falsos (ya existen).
- Replay de decisiones: bajar de Drive (conector, ficheros pequeños) los `registro_tts.jsonl` de episodios ya hechos
  (tienen `ok`, `errores`, `sobra_final`, `transcripcion`, `intentos` por frase y `segundos`) y calcular offline,
  con las funciones reales `revisar`/`medir.normaliza`: (i) cuántas frases marcaría un filtro por duración/carácter
  (precisión/recall frente a las que tuvieron `intentos>1`), (ii) cómo cambian las decisiones si el umbral cambia.
  Eso cuantifica los filtros gratuitos (§D, §H) sin Whisper.
- Determinismo del solapamiento: test unitario de `generar_bloque` con `sintetizar_lote` falso que usa solo la semilla
  → mismo resultado con revisión sincrónica y con cola asíncrona/diferida.
- Lógica de alineación CTC: Viterbi con emisiones sintéticas.

Mínima en GPU (por ahorro/propuesta):
- A/§2.2: cuaderno solo-Whisper, 64 frases guardadas, lotes 1/2/4/8/16, con/sin palabra: 2–3 min.
- B (turbo): mismo cuaderno + las mismas 64 frases de 2–3 episodios *incluyendo las frases con `intentos>1`* y unos
  casos fabricados (cola de 1 s de ruido/otra frase añadida al final, palabra cambiada, truncada): comparar para
  large-v3 y turbo `ok` y `sobra_final`. Criterio de aceptación: mismas decisiones en ≥99,5 % de las frases reales;
  **100 % de los positivos reales y fabricados detectados**; error de `sobra_final` < 0,15 s.
- D: la misma prueba con `return_timestamps=True` y SDPA.
- E/F: un episodio de ~5 min con y sin; comparar `registro_tts.jsonl` (audio idéntico: hash del master) y s/s.
- G: CTC sobre las mismas 64 frases: curva ROC de "necesita Whisper".

## 5. Memoria
- Pesos fp16: large-v3 ~3,1 GB; turbo ~1,6 GB; small ~0,5 GB; wav2vec2-large ~0,6 GB. Eager con atenciones por palabra
  añade activaciones (atención 20 cabezas × 1500² por capa por muestra, transitoria) y las atenciones cruzadas
  de todas las capas guardadas durante la generación.
- Liberar 1,5 GB (turbo) a 2,5 GB (CTC/small) sirve para lotes Qwen mayores **solo si Qwen está limitado por memoria**.
  Hoy el lote lo limita `motor.lote = 8` y el número de frases de la intervención, no la memoria: por eso el ahorro de
  memoria solo se cobra cuando se implementen lotes entre intervenciones. Medir `pico_qwen_gb` en §2.1 para decidir.

## 6. Lista priorizada

1. **Cronometrar** (§2.1) y **microbenchmark de Whisper sobre frases guardadas** (§2.2): casi gratis, decide todo lo demás.
2. **`large-v3-turbo`** (B): −3–6 % total, −1,5 GB, esfuerzo bajo, validar con replay (§4). Es la mejor relación.
3. **Pipeline a mano + mel en GPU + lote mayor** (C) y/o **marcas de segmento + SDPA** (D) tras validar: −1–3 % más.
4. **Filtros gratuitos** (duración/carácter, tope de pasos) como alarma extra: no ahorran, **suben la seguridad** y
   preparan H.
5. **Solapar en proceso aparte** (E) solo si el reparto medido deja S > 8 % tras B: −4–7 %, esfuerzo alto.
6. **Dos fases** (F): útil si se implementan lotes Qwen grandes (por memoria).
7. **CTC como primer filtro** (G) y **selectiva** (H): mayor ahorro potencial (5–9 %) pero más riesgo/esfuerzo; en el último lugar.
8. Whisper en CPU (I): descartado.

Techo realista conjunto de la verificación: **~6–10 % del tiempo GPU total** (B + C/D, o B + E). Para más hay que
mirar Qwen.

## Fuentes
- https://github.com/openai/whisper/discussions/2363 (turbo: 4 capas de decoder frente a 32; mejor en FLEURS, peor en tailandés/cantonés)
- https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2/discussions/3 (19,2 s vs 52,0 s; 2080 Ti; vía búsqueda)
- https://discuss.huggingface.co/t/whisper-help-me-understand-output-attentions-whispers-attention-mechanism-options/106030
- https://www.e2enetworks.com/blog/benchmarking-asr-models-nvidia-l4-parakeet-whisper-nemotron.md
- https://dyl5051.substack.com/p/choosing-a-whisper-serving-framework
- https://huggingface.co/bofenghuang/whisper-large-v3-distil-multi7-v0.2 (vía búsqueda)
- https://docs.pytorch.org/audio/stable/tutorials/forced_alignment_for_multilingual_data_tutorial.html
- Repo: `piloto/medir.py` (Asr, transcribe_lote), `fabrica/fabrica.py` (revisar, generar_bloque, generar_episodio,
  _sintetizar_lote), `fabrica/voces.json` (verificacion), `docs/contexto-fabrica.md`, `docs/estado.md:202`, `docs/dataset.md:39`.

Limitaciones: no encontré benchmark de Whisper large-v3 en T4 con frases cortas; las cifras de §1 son estimaciones
razonadas, con rango amplio. Ningún modelo se pudo descargar ni ejecutar aquí.
