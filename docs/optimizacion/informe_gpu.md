# Informe de coste: GPU y economía de Colab (2026-11-06)

Solo investigación; no se ha tocado el repo. Limitación: WebFetch no pudo abrir mccormickml.com, explainx.ai ni la FAQ de Colab
(hosts fuera de la red permitida de la sesión). Todo lo web viene de resúmenes de WebSearch, de segunda mano. Lo que no he podido
verificar va marcado **[NV]**. No hay benchmarks públicos de Qwen3-TTS por lotes en T4/L4/A100: las velocidades por GPU son
**estimaciones mías**, no medidas.

## 0. Conclusiones en cinco líneas

1. Lo que está en juego es poco dinero. Con Colab pay-as-you-go (100 unidades = 9,99 USD, **[NV]**, página de precios vista en
   WebSearch el 2026-09-21), las ~110 unidades pendientes son ~11 USD. Optimizar tiene sentido hasta cierto punto.
2. **Las tarifas de `voces.json` (T4 1,96 / L4 4,82 / A100 11,77) parecen más altas que las medidas recientes** (T4 1,19, L4 1,71,
   A100-40 GB ~5,4). Si las recientes valen, el gasto real es ~40 % menor y L4 compensa. Se comprueba gratis (apartado 6, prueba A).
3. Con las tarifas supuestas, cambiar de GPU apenas ahorra (A100 y L4 salen igual o peor que T4). Con las medidas, L4 con lote 32
   puede ahorrar ~25 unidades. La decisión depende de un dato que el autor puede leer en "Ver recursos".
4. Los gastos de sesión (carga, pip, descarga) son ~0,1-0,2 unidades por sesión: **no merece cachear nada**. Lo que sí duele es un
   rato parado: cada hora olvidada cuesta lo que ~25 min de audio.
5. Paralelizar no ahorra unidades (se paga por GPU-segundo). Kaggle sí ahorra todo (gratis), pero cuesta esfuerzo y sale del flujo preferido.

## 1. Tarifas de Colab (unidades/hora)

| Hardware | Tarifa en `voces.json` | Medida/publicada | Fuente y fecha | Fiabilidad |
|---|---|---|---|---|
| T4 | 1,96 | **1,19** (medida; "fluctúa un poco"); otras: 1,58 (oct-2024), 1,76 (Spheron 2026), 1,96 (DEV, antigua) | McCormick, actualizado mar-2026; varlog.info 2024-10-01; Spheron 2026 | media: las cifras divergen entre sí |
| L4 | 4,82 | **1,71** (resumen en gpuperhour.com de la tabla de McCormick); un foro alemán dice 1,7-2,1 | McCormick mar-2026; mydealz 2026 | media-baja |
| A100 40 GB | 11,77 | ~5,4 (mar-2024); un artículo de 2026 dice que la UI muestra ~5,38/h | McCormick 2024; explainx 2026 | media; 11,77 y 15 son cifras antiguas |
| A100 80 GB | (sin dato) | sin cifra encontrada | | **[NV]** |
| H100 | (sin dato) | **sin cifra en unidades**. Colab Enterprise (facturación en dólares, no unidades) ~11,76 USD/h vs T4 0,42 USD/h (21-sep-2026) | cloud.google.com/colab/pricing | no aplica a Colab normal |
| TPU v5e / v6e | | sin cifra; Colab los ofrece (plan AI Pro dice desbloquearlos con 200 unidades) | mydealz 2026 | **[NV]**. Además Qwen3-TTS en PyTorch/HF no corre en TPU sin portarlo |
| CPU / CPU High-RAM | | no encontré cifra. De memoria (histórico, **no verificado**) la CPU es ~0,08 u/h y High-RAM algo más | | **[NV]** |

Preguntas concretas:

- **¿Cambia con High-RAM?** No encontré datos. En Colab la GPU T4 con High-RAM activado ha sido históricamente algo más cara; hay que
  mirarlo en "Ver recursos" con el interruptor puesto y quitado. Si la fábrica cabe sin High-RAM (¿cuánta RAM del sistema usa?), no lo actives.
- **¿Se cobra por sesión conectada aunque la GPU esté ociosa?** Sí, es lo que dicen todas las fuentes: las unidades se gastan por hora de
  runtime asignado, no por uso. Por eso existe `runtime.unassign()`. (Kaggle igual: una sesión interactiva activa cuenta contra las 30 h aunque no corra nada.)
- **¿Mínimo?** No encontré mínimo por sesión; el consumo es continuo (fracción de hora). **[NV]**
- Lo que la fábrica estima en `coste_fabrica.jsonl` sale de `fabrica.unidades(segundos, gpu, cfg)` = segundos/3600 × tarifa de `voces.json`.
  Está bien como mecanismo, pero **si la tarifa está inflada, todo el libro de costes lo está**.
  Nota: el nombre de GPU se casa por subcadena ("T4" en "Tesla T4"); "A100" no distingue 40/80 GB.
- Precio de la unidad: 9,99 USD por 100 (Colab Pro, **[NV]**, un resumen de 21-sep-2026 y otro dice 12,67 USD con 500 u/mes: no cuadran, mirar la página).

## 2. Rendimiento por GPU para una carga limitada por latencia de kernels

Razonamiento (inferencia, sin benchmark directo):

- Cada paso del talker = 1 paso del modelo grande + sub-talker de 16 códigos: cientos de kernels pequeños con tensores diminutos.
  El tiempo por paso lo fija la **latencia de lanzamiento (CPU del host + driver)**, no los FLOPs ni el ancho de banda. Por eso T4 → L4 → A100
  da poco por paso: espero **1,0-1,4x** (L4/A100 con CPU de host algo mejor, bf16 nativo, kernels SDPA mejores), no los 5-8x que dicen los blogs para
  modelos de 3B con lote 1 (esos miden decode limitado por ancho de banda; fuente deploybase, sin fecha clara, no extrapolable).
- La ganancia real viene del **lote**: cada paso procesa N secuencias por el mismo coste de lanzamiento. L4 (24 GB) y A100 (40/80 GB) permiten
  lotes 3-8 veces mayores que T4 (15 GB, ya "justa" con lote 8 y Whisper en memoria).
- OJO, el escalado observado **no es lineal**: de 4,58 s/s (L4, frase a frase) a 2,2 s/s (T4, lote 8) hay 2,1x con 8x de lote (aunque son GPU
  distintas). Causas probables: el lote dura lo que la frase más larga (relleno), Whisper revisa todo sin lote grande, los lotes de intervenciones
  cortas son pequeños, la parte no autoregresiva (codec, Whisper, I/O a Drive) no escala. **No se sabe qué fracción es Whisper**: es la medida más urgente (prueba B).
- bf16: `MotorQwen` elige bf16 si la GPU lo soporta (línea ~543 de fabrica.py): en L4/A100 saldrá bf16 y en T4 fp16. Las muestras cambiarán
  ligeramente; hay que escuchar una antes de mezclar (los clips ya hechos no se rehacen salvo que cambie la firma de voz).

### Estimación de GPU-segundos por s de audio (mis supuestos)

| Configuración | s GPU / s audio (central; rango) | Supuestos |
|---|---|---|
| T4, lote 8 (actual) | **2,2** (medido; 2,0-2,8) | medido |
| T4, lote 12-16, ordenar por longitud, Whisper fuera de GPU o más ligero | 1,6 (1,3-2,0) | memoria permite; escalado ~50 % |
| L4, lote 32 | 0,8 (0,6-1,2) | 24 GB; escalado ~50 % del lineal sobre lote 8; paso ~igual que T4 |
| A100, lote 64 | 0,35 (0,25-0,6) | 40/80 GB; Whisper tampoco escala |
| H100 | ~0,3 (0,2-0,5) | igual que A100; tarifa en unidades desconocida |

### Coste por hora de audio y para los ~1.300 min (21,7 h de audio)

Unidades = GPU-s/s × tarifa. Dos columnas: tarifas de `voces.json` (supuestas) y las medidas recientes. Sin sobrecarga de sesión.

| Opción | u / h de audio (voces.json) | u / h de audio (medidas) | Total 1.300 min (voces.json) | Total 1.300 min (medidas) | Incertidumbre |
|---|---|---|---|---|---|
| T4 lote 8 (hoy) | 4,3 | 2,6 | 94 | 57 | baja en velocidad, media en tarifa |
| T4 lote 12-16 optimizado | 3,1 | 1,9 | 68 | 41 | media |
| L4 lote 32 | 3,9 (2,9-5,8) | 1,4 (1,0-2,0) | 84 (63-125) | 30 (22-44) | alta |
| A100 lote 64 | 4,1 (2,9-7,1) | 1,9 (1,4-3,2) | 89 (62-154) | 41 (30-70) | alta |
| H100 | ¿? | ¿? | ¿? | ¿? | sin tarifa; no recomendable sin dato |
| CPU High-RAM | no viable: autoregresivo 1,7B en 2-4 vCPU, órdenes de magnitud más lento | | | | |
| TPU | no viable sin portar a torch_xla/JAX | | | | |

(El autor estima ~110 u hoy; mi 94 + ~15 por cargas y ratos parados es coherente.)

Lectura: con las tarifas supuestas **ninguna GPU grande gana de forma clara a una T4 bien aprovechada**; con las medidas, L4 gana ~2x. El umbral
es sencillo: una GPU compensa si su aceleración (con el lote que quepa) supera su cociente de tarifa respecto a T4 (L4: 1,4x con tarifas medidas,
2,5x con las supuestas; A100: ~4,5x medidas, 6x supuestas). La aceleración esperable de L4 es ~2,5-3x, de A100 ~6x.

## 3. Gastos de sesión

Datos del repo: celda 1 `pip install qwen-tts==0.1.1 peft==0.17.1 jiwer num2words` (y hay que "Reiniciar sesión"); celda 3 clona/actualiza el repo
y monta Drive; celda 4 carga Qwen + LoRA + Whisper (2-5 min, medido); las pesas se bajan de HF en cada sesión nueva (`from_pretrained` sin `cache_dir`).

| Concepto | Tiempo estimado | Coste en T4 (1,96-1,19 u/h) | ¿Merece la pena actuar? |
|---|---|---|---|
| pip install (1-2 min) | | 0,03-0,07 u | No |
| Descarga de pesas HF (Qwen ~4 GB + Whisper ~3 GB; ~1-2 min a 50-150 MB/s, **[NV]**) | | 0,03-0,07 u | No. Leerlas de Drive suele ser **igual o más lento** que HF y llena Drive |
| Carga a GPU (medido 2-5 min) | | 0,07-0,16 u | Solo encadenando |
| Total por sesión | ~5-9 min | **~0,15-0,3 u** | |
| 30 sesiones sueltas frente a 10 encadenadas | | ahorro ~3-6 u | Solo si es gratis de hacer |
| **Una hora parada** (autor olvida desconectar) | 60 min | **1,2-2 u (T4)**, 1,7-4,8 (L4) | **Sí: es el riesgo real** |

Propuestas ordenadas por rentabilidad:

1. **Cadena larga por sesión**: la celda 2 ya acepta una lista `EPISODIOS`. Mandar 10-20 episodios (6-10 h de GPU) por sesión elimina cargas y esperas del
   autor, y el riesgo pasa a ser "se cae a mitad" (el código ya retoma sin repetir). Mejor límite práctico: 8-10 h, por el tope de sesión.
2. **Desconexión garantizada.** La celda 7 es la última celda: se ejecuta sola con "Ejecutar todo" **solo si ninguna celda anterior falla** (Colab detiene
   la ejecución al primer error). Por tanto, si 4 o 5 fallan (OOM, Drive caído), la GPU queda asignada y pagando. Propuesta: envolver la celda 5 en
   `try/except` que imprima el error y deje pasar a 6-7, o llamar a `comun.desconectar()` en un `finally`. (Riesgo: ocultar un fallo; mitigar escribiendo el
   error en el informe de Drive antes de desconectar.) Además `drive.flush_and_unmount()` puede tardar o fallar con muchos ficheros: poner un `try` y
   desconectar igualmente tras un reintento.
   Ojo: la celda 1 exige reiniciar la sesión tras el pip, así que "Ejecutar todo" en una sesión fresca no es un flujo de un solo toque; lo robusto es: celda 1,
   reiniciar, y entonces "Ejecutar todo" (la celda 1 se repite sin coste, pip ya está instalado). Hay que probar que esa segunda ejecución de pip no rompe nada.
3. **"Ejecutar después" / ejecución programada.** Colab tiene programación de cuadernos, pero lo que he encontrado es la de **Colab Enterprise** (usa cuota de
   Compute Engine, se factura en dólares), no la de Colab Pro (ejecución en segundo plano; **[NV]** cómo factura las unidades). La utilidad real sería
   que el autor no tenga que estar delante para desconectar. No la recomiendo hasta confirmar en su cuenta que (a) existe, (b) el runtime se libera al acabar, (c) la sesión no
   se cuelga esperando a Drive. Es una prueba de ~10 min con un episodio corto.
4. Alertas: `coste_fabrica.jsonl` ya registra sesión frente a generación; añadir "min parados = sesión - GPU generando" avisa del derroche.
5. No cachear wheels ni pesas en Drive (ahorro < 0,1 u por sesión, más complejidad). Excepción: si HF falla o limita descargas.

## 4. Alternativas fuera de Colab (solo comparación)

| Opción | Precio | Coste por h de audio con mis estimaciones | Total 21,7 h | Notas |
|---|---|---|---|---|
| Colab T4 lote 8 (9,99 USD/100 u) | 0,12-0,2 USD/h GPU | 0,26-0,43 USD | 5,6-9,3 USD | actual |
| Kaggle T4×2 o P100 | **gratis**, ~30 h GPU/semana (fuentes dicen 9-12 h por sesión; reinicio semanal con día contradictorio) | 0 | 0 | 2 GPU = doble ritmo si se parte el trabajo en 2 procesos; ver apartado 5 |
| RunPod L4 | 0,39 USD/h (Secure Cloud, jun/ago-2026) | 0,8 h × 0,39 = **0,31 USD** | ~6,8 USD | por hora; sin gestión de unidades. Rango 0,23-0,47 USD |
| Modal L4 | 0,80 USD/h (ago-2026) o ~0,40 (abr-2026, contradicción) | 0,3-0,64 USD | 7-14 USD | factura por segundo (no paga ratos parados) |
| Lightning AI, Vast.ai | **no investigados** (sin datos fiables) | | | Vast.ai suele ser más barato pero con máquinas dispares |

Conclusión: el precio es del mismo orden que Colab. **Ninguna alternativa de pago ahorra algo que justifique cambiar de flujo.** Kaggle es la única que elimina
el gasto, pero hay que (a) montar Drive sin `drive.mount` (token de rclone o API de Drive como secreto de Kaggle), (b) verificar teléfono para activar internet,
(c) mantener un segundo cuaderno. Opcional, el autor prefiere Colab.

## 5. ¿2 GPU de Kaggle o varias sesiones Colab en paralelo?

- Colab: se paga por GPU-segundo. Dos cuadernos con la mitad de episodios cada uno cuestan **lo mismo en unidades** (más una carga extra, +0,1-0,2 u) y acaban en la mitad
  de tiempo. Solo sirve para acortar el reloj, no el gasto. Dos cuadernos con los mismos episodios gastarían el doble por nada. Colab Pro permite sesiones simultáneas con límite **[NV]**.
- Kaggle T4×2: las 30 h cuentan por tiempo de sesión, no por GPU, así que dos procesos (uno por GPU, `CUDA_VISIBLE_DEVICES`) duplican el rendimiento gratis:
  ~60 GPU-h/semana frente a las ~48 GPU-h que pide T4 lote 8 -> **todo el podcast en ~1 semana de cuota**. Aun así hay que partir los episodios a mano.
  P100 (16 GB, sin tensor cores fp16 de T4, ~mismo orden por paso) también vale.

## 6. Pruebas mínimas que confirman cada estimación

| Id | Qué se confirma | Prueba | Coste |
|---|---|---|---|
| A | Tarifas reales | En T4, L4 y A100 abrir "Ver recursos" y anotar el consumo mostrado ("X unidades/hora"). Alternativa: unidades antes/después de 15 min | ~0 u (solo ver el panel) o ~0,3-1 u |
| B | Reparto del tiempo (generar / Whisper / otros) | En la T4 de siempre, 1 episodio corto (5-10 min de audio) con `VERIFICAR=True` y `False`, o con cronómetros en `generar_episodio` | ~0,3-0,5 u |
| C | Lote máximo y escalado en T4 | Mismo clip de prueba con `lote` 8/12/16 (`voces.json`), anotando `torch.cuda.max_memory_allocated()` y s/s | ~0,4 u |
| D | L4 lote 32 | 5 min en L4: una intervención larga de Naval (~3 min de audio), `lote` 16 y 32, `VERIFICAR=False` y luego `True`; leer s/s, memoria pico y unidades del panel | ~0,3 u (a 1,7-4,8 u/h) |
| E | A100 lote 64 | Lo mismo en A100, 5 min | ~0,5-1 u |
| F | Sesión: cuánto cuesta el arranque | Medir `time` de celdas 1, 3 y 4 en sesión fresca (el cuaderno ya guarda `T_INICIO`) | gratis (ya registrado) |
| G | Desconexión tras error | Provocar un error en celda 5 (episodio inexistente) y comprobar que se libera la GPU con "Ejecutar todo" | ~0,05 u |
| H | bf16 vs fp16 | Escuchar a ciegas una frase de L4 (bf16) y una de T4 (fp16) | gratis (con D) |

## 7. Recomendaciones priorizadas (ahorro estimado sobre ~110 u)

| # | Acción | Ahorro estimado | Esfuerzo | Riesgo |
|---|---|---|---|---|
| 1 | Leer tarifas reales (prueba A) y corregir `voces.json`. Decide todo lo demás | 0 directo; evita decidir con una tarifa errónea (hasta 40 % de diferencia en las estimaciones) | minutos | ninguno |
| 2 | Perfilar (B, C): ordenar frases por longitud dentro del lote, lote 12-16 en T4, medir Whisper | 15-30 u | bajo-medio | bajo (audio idéntico salvo semillas) |
| 3 | Probar L4 lote 32 (D) y A100 solo si D sale bien. Pasar a L4 si speedup/ratio de tarifa > 1,3 | 10 u (tarifas supuestas) a 27 u (medidas); 0 si sale peor | medio | medio: bf16 distinto, 24 GB, otra firma de voz |
| 4 | Garantizar desconexión con fallo (try/finally) y encadenar 10+ episodios por sesión | 3-8 u (sesiones) + evita pérdidas puntuales de 2-5 u | bajo | bajo |
| 5 | Cortos dentro de largos (ya identificado en `contexto-fabrica.md`) | ~20 u | medio | bajo |
| 6 | Kaggle T4×2 como alternativa opcional | hasta ~100 u (≈10 USD) | alto | medio: otro entorno, Drive |
| 7 | "Ejecutar después" | comodidad, no unidades | bajo, tras prueba G | no verificado |
| - | No hacer: cachear pesas/wheels en Drive, TPU, CPU, H100, paralelizar para ahorrar | | | |

Los ahorros de 2, 3 y 5 no se suman linealmente (se solapan).

## 8. Fuentes (consultadas vía WebSearch, resúmenes de segunda mano; ninguna abierta completa)

- McCormick, "Colab GPUs Features & Pricing", actualizado mar-2026: https://mccormickml.com/2024/04/23/colab-gpus-features-and-pricing/ (T4 1,19; L4 1,71; A100 5,40)
- varlog.info, "Colab credit consumption comparison", 2024-10-01 (T4 1,58)
- Spheron, "Google Colab alternatives 8 GPU clouds compared 2026" (T4 ~1,76, 57 h por 100 u)
- explainx.ai, "Google AI Pro Colab A100 H100 200 compute units claimed vs verified 2026" (A100-40 ~5,38 u/h)
- Colab Enterprise pricing, consulta de 21-sep-2026: https://cloud.google.com/colab/pricing (T4 0,42 USD/h, H100 ~11,76 USD/h; dólares, no unidades)
- gpuperhour.com, "Google Colab alternatives and what a GPU costs by the hour" (resumen de tarifas y precios 2026)
- Programación de cuadernos (solo Colab Enterprise): https://docs.cloud.google.com/colab/docs/schedule-notebook-run
- deploybase.ai (l4-vs-t4, tesla-t4-vs-a100) y clarifai.com (t4-vs-l4): cifras de decode de modelos 3-8B, sin fecha clara; usadas solo como contexto, no para estimar
- Kaggle: aimultiple.com/free-cloud-gpu, geeksforgeeks (30 h/semana, T4×2/P100; día de reinicio contradictorio entre fuentes)
- RunPod L4 0,39 USD/h (computeprices.com, jun/ago-2026); Modal L4 0,80 USD/h (ago-2026) frente a ~0,40 (hostfleet.pages.dev, abr-2026)
- Datos del repo: `docs/contexto-fabrica.md`, `fabrica/voces.json`, `fabrica/fabrica.py` (`unidades`, `MotorQwen`), `fabrica/construir_cuaderno.py` (celdas 1, 6, 7), `criba/comun.py` (`desconectar`).
