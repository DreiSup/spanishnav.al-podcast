# Informe: no generar audio que no hace falta

Datos: los 134 `transcript.es.json` del repo (2019/001 a 2022/134). Scripts en esta misma carpeta
(`a1_cortos.py`, `a2_052.py`, `a3_global.py`, `a4_lotes.py`, `calibrar_tope.py`, `common.py`). Conversión: 14,6
caracteres por segundo de audio (medido en el registro de simulación; `fabrica-de-voz.md` dice ~15) y 5 unidades/hora
de audio (la cifra del encargo; con `voces.json`, 2,2 s/s x 1,96 u/h, salen 4,3). Si el ritmo real es 16 c/s (el 052
real dura ~247 min, no los 274 que salen aquí), todas las cifras en minutos bajan ~10 %.

No hay `registro_tts.jsonl` ni `informe_tts.md` reales en el repo (solo los de simulación en el scratchpad, sin
reintentos). Lo de los reintentos sale de `fabrica/README.md` y `docs/estado.md`.

## 1. Cortos dentro de largos (077, 105, 130)

Resultado: **coincidencia del 100 % a nivel de bloque** en los tres grupos (71 cortos).

| Largo | Cortos | Bloques largo | Bloques del corto idénticos (voz + frases) | Frases idénticas | Casi idénticas | Distintas | Caracteres | Minutos | Unidades (5 u/h) |
|---|---|---|---|---|---|---|---|---|---|
| 077 | 15 | 49 | 49/49 | 309/309 | 0 | 0 | 27.445 | 31,3 | 2,6 |
| 105 | 32 | 73 | 73/73 | 704/704 | 0 | 0 | 71.053 | 81,1 | 6,8 |
| 130 | 24 | 35 | 35/35 | 567/567 | 0 | 0 | 61.202 | 69,9 | 5,8 |
| Total | 71 | 157 | 157/157 | 1.580/1.580 | 0 | 0 | 159.700 | **182,3** | **15,2** (13,1 con 4,3 u/h) |

Los caracteres de los cortos suman exactamente los del largo en cada grupo (sin frases propias, sin huecos, sin
solapes). El script avanza "hacia delante" por el largo, como pide `docs/cortos-y-largos.md`.

Ahorro: generar solo el largo evita 182 min de audio, unas 15 unidades (el doc dice ~20; con 5 u/h salen 15 y con
la tarifa de `voces.json` 13). Más el ahorro de tiempos muertos de sesión por 71 episodios menos.

**Obstáculo real (no está en el doc): `speaker` NO sirve para emparejar.** En el 105 el largo escribe "Brett Hall" y
el corto "Brett" (y los ids son `b14-brett-hall` frente a `b01-brett`). Con `speaker` como clave, el emparejamiento
cae al 52 % de bloques (38/73) y al 44 % de frases en el 105. Con la **voz resuelta** (`asignar_voces`/alias de
`voces.json`) vuelve a 73/73. Hay que comparar `p["voz"]` + `p["frases"]` (lo que ya usa `clip_al_dia`), no `speaker`
ni `bloque`. Con la regla de Kapil, `voz` ya resuelve `naval_kapil`.

Otros puntos comprobados:
- Los bloques coinciden de forma exacta, así que no hace falta emparejar por frase: basta sembrar clips enteros y su
  carpeta `tts/frases/`. Es el diseño del doc (sembrar `NNNvoz.wav` y `NNNvoz_KK.wav` con la numeración del corto y
  copiar la fila del registro con `origen`). Se confirma que es suficiente y que no hace falta fusionar/partir.
- El `fichero` depende del número de bloque dentro del corto (`001naval.wav`), no del largo: hay que renumerar, y
  `bloque` (id) también se toma del plan del corto.
- Bloques consecutivos del mismo hablante en el largo (b13, b14, b15 de Brett Hall en el 105) están separados igual
  en los cortos: en el master llevan 0,6 s entre ellos, igual que en el largo.
- Diseño mínimo si algún día hay discrepancia (154/160, aún sin traducir): para cada bloque del corto, buscar hacia
  delante en el largo un bloque con la misma `voz` y mismas `frases` (comparación exacta; opcionalmente con
  `norm()` de `common.py`: minúsculas, sin puntuación). Los no emparejados se generan como siempre. Para el 154
  falta partir el bloque de Naval antes de "Marketing is an open problem" (ya anotado en el doc).
- Si el largo se arregla (`REHACER_FRASES`), hay que volver a sembrar. Ya contemplado en el punto 6 del doc.

Cambia el audio ya aprobado: no (los cortos 053–067, 072–076 y 078–129 aún no se han generado; el largo se escucha
una vez).

## 2. Episodio 052 frente a 001–050

052: 288 bloques, 2.883 frases, 239.681 caracteres = 274 min a 14,6 c/s (22,8 u).

**El español del 052 se tradujo aparte** y solo coincide con los cortos en una parte:

| Medida | Resultado |
|---|---|
| Frases del 052 idénticas (voz + texto normalizado) a alguna frase de 001–050 | 996/2.883 = **34,5 %** (79.897 car., 31 % de caracteres) |
| Casi idénticas (similitud >= 0,9, no exactas) | 478 frases, 48.464 car. (son paráfrasis: "su hilo de tuits titulado Cómo..." frente a "su hilo de tuits sobre cómo...") |
| Realmente distintas | 1.409 frases, 111.320 car. |
| Bloques del 052 idénticos a un bloque de algún corto | 30/288 |
| Bloques del 052 con todas sus frases en algún corto | 32/288 (13.198 car.) |

Por tramos: los cortos 046–050 están al 96–100 % dentro del 052, 017–045 entre el 40 y el 75 % (por frases), y 001–016
entre el 5 y el 30 %. Es decir, las traducciones de 2019 inicial y el 052 son distintas.

- **Opción A (unir masters de 001–050):** 0 unidades extra de GPU frente a las ~22,8 u de generar el 052 entero
  (ahorro 22,8 u; 19,7 u con la tarifa de `voces.json`). Hay que añadir ~10 min de cola sin corto (1.832 palabras,
  ~0,8 u) y el `transcript.es.json` del 052 debería sustituirse por la unión de los de los cortos (si no, el texto
  publicado no corresponde al audio). Queda solo la decisión de publicar el 052.
- **Opción B (reutilizar frases idénticas y generar el resto):** reutiliza ~31 % de los caracteres, ahorra ~7 u
  (de 22,8 a ~15,7) y, para reutilizar frases sueltas de un bloque distinto, hay que ensamblar frase a frase con
  entonación cortada (la prosodia depende del bloque entero: la fábrica genera un clip por bloque). Peor en todo:
  más caro (15,7 u frente a 0), mezcla de frases de distintos episodios en un clip y riesgo de discontinuidad.
- Recomendación: A. B solo valdría si el autor quiere que el 052 conserve su traducción distinta, y aun así sale
  mucho más caro que A.

## 3. Frases repetidas en el catálogo (caché global por voz+texto)

Sobre el corpus sin duplicados de cortos/052 (62 episodios, 7.571 frases, 743.276 caracteres):
**2 copias repetidas en total (36 caracteres, 0,0 %)**. No hay saludos ni fórmulas repetidas en el texto traducido
(el troceado largo y la traducción libre hacen que no se repitan). **No merece caché global por (voz, texto)**: ahorro
cero. Lo útil es la caché por "origen" de los cortos (punto 1), que es un caso especial de lo mismo.

Dato complementario: el corpus total traducido hoy son 1.304 min (108,7 u); el trabajo único (62 episodios) son 848
min (70,7 u). Con 1 y 2 se evitan 456 min (37,9 u). De esos 848 min, 575 min (48 u) están pendientes (001–039 y 068
ya hechos o en marcha; incluye los tres largos 077/105/130: 182 min).

## 4. Reintentos, `tope_pasos` y lotes

### 4.1 Cómo es el código realmente
- `generar_bloque` YA ordena por longitud dentro de cada intervención y reparte en lotes iguales. El relleno no es el
  de "frases consecutivas" (esa variante daría 34,8 % de relleno), sino el de lotes ordenados.
- La semilla de cada lote depende de los textos del lote (`semilla("|".join(textos), intento)`): cambiar el agrupado
  cambia el muestreo de las frases. Tiene efecto solo en clips que se generen de nuevo (los aprobados no se tocan).

### 4.2 Distribución de frases (7.571 frases base)
Caracteres por frase: media 98, mediana 94, p10 47, p90 157, p99 201, máx 248.
Histograma: 0–49: 884; 50–99: 3.227; 100–149: 2.480; 150–199: 892; 200+: 88.
Intervenciones: 902, mediana 6 frases (media 8,4); el 29 % tiene <= 3 frases y 109 tienen una sola.
Lotes actuales: 1.393, tamaño medio **5,4** (de 8 posibles): 110 lotes de 1, 78 de 2, 76 de 3, 124 de 4, 234 de 5,
251 de 6, 255 de 7 y 265 de 8. Es decir, la GPU va a ~68 % de la capacidad de lote.

### 4.3 Relleno si cada lote corre hasta la frase más larga (pasos = caracteres/14,6 x 12,5)
| Estrategia (lote 8) | Lotes | Relleno | Σ máx de cada lote (min-audio) |
|---|---|---|---|
| Actual: ordenado dentro de la intervención | 1.393 | **23,4 %** (25,6 % con ruido log-normal del 15 %) | 201,8 |
| Mezclar frases de la misma voz de todo el episodio, ordenadas por longitud | 1.010 | 6,6 % | 124,6 (-38 %) |
| Lo mismo entre episodios (una sola cola por voz en la sesión) | 951 | 0,8 % | 108,0 (-46 %) |
| (referencia) sin ordenar, frases consecutivas | 1.393 | 34,8 % | 228,5 |

Con lote 12 el ahorro sube a -49 % / -59 %; con lote 16 a -56 % / -66 %, pero la memoria de la T4 está justa (Whisper
baja solo a 2) y Qwen ya parte el lote si no cabe.

El ahorro real depende de cómo escala el tiempo por paso con el tamaño del lote, que el repo no permite medir:
- Si el paso cuesta lo mismo con 3 que con 8 frases (dominado por lanzamientos de kernels, como dicen los docs): el
  ahorro de tiempo de Qwen es el de la columna "Σ máx", **38–46 %**.
- Si el coste fuera lineal en elementos x pasos (techo opuesto): solo se quita el relleno, **18–23 %**.
- Lo verosímil es el intervalo 18–46 %. Dado que 2,2 s/s con lote medio de 5,4 frente a 4,58 s/s frase a frase es una
  mejora de solo 2x con 5,4x más frases, el coste por paso crece bastante con el lote: el valor real estará más cerca
  de la parte baja (~20–30 %).
- Aplicado a los 575 min pendientes (48 u) y suponiendo que Qwen es ~85 % del tiempo: **~8–19 u** (central ~11 u).
  Whisper no mejora (revisa todas las frases igual).

Cómo hacerlo: generar por voz y episodio (o por voz y sesión) con una cola de frases ordenada por longitud, guardando
cada frase en `tts/frases/` al terminar su lote, y montar los clips por bloque al final. La reanudación sigue
funcionando a nivel de frase. Afecta a `generar_episodio`/`generar_bloque` (reestructuración media-alta).

### 4.4 Reintentos
Por `README`/`estado.md`: 037–039 tuvieron 7 reintentos (038) y 1 sospechosa falsa; 001–016 y 035–040 cero
sospechosas; 044 ninguno. Con ~122 frases por episodio, 0–7 reintentos = 0–6 %. El coste hoy: cada intervención reintenta
sus frases fallidas **sola** en su propio lote, con otra semilla, hasta 2 veces. Con k fallos repartidos en k intervenciones
son k lotes de 1 frase (cada uno cuesta ~una frase de pasos, pero con el modelo de lanzamientos, ~un lote entero de
tiempo). Aplazar los reintentos al final del episodio y juntarlos (ceil(k/8) lotes) ahorra ~(k-1) lotes pequeños por
episodio: unos 60–90 s en un episodio con 3 fallos; **~2–3 u** en todo el catálogo. Esfuerzo bajo. No cambia el audio
aprobado (solo el orden en que se retienen).

### 4.5 `tope_pasos`
`tope = 12,5 x (c/7 + 3)` frente a la duración real media de c/14,6: es **2,1x + 3 s** de margen, 2,5x para una frase
mediana de 98 c (212 pasos frente a 84). El margen solo cuesta cuando una frase no para (alucinación): ese lote corre
hasta el tope en vez de hasta su frase más larga (en una frase mediana: +128 pasos, ~1,5 lotes de coste). No afecta al
resto. No hay forma de medir con qué frecuencia ocurre sin los registros reales. Con 0–7 reintentos/episodio y varios de
ellos por WER y no por tope, el coste es como máximo de ~0–3 % del tiempo. Un tope más justo (p. ej. c/9 + 2 s, que
sigue siendo >1,6x la duración media) ahorra entre un 20 y un 35 % de ese coste en lotes con alucinación, es decir
<= 1 % del total. **Poco rentable**; lo correcto es calibrarlo con datos reales: `calibrar_tope.py <registro_tts.jsonl...>`
(en esta carpeta) calcula la distribución real de c/s por frase y el margen. Cuidado: bajarlo mucho trunca frases
lentas legítimas (Brett, Deutsch, pausas de 0,2–0,3 s).

## 5. Otro trabajo evitable detectado en el código

1. **Cambio de una frase = rehacer el bloque entero.** `clip_al_dia` compara la lista completa de frases del
   bloque; cualquier edición regenera todo el clip aunque `tts/frases/*.wav` ya tenga las demás. El tamaño medio
   del bloque visto desde una frase es **17,4 frases** (máx 87). Una corrección de traducción de 1 frase cuesta ~17x
   lo necesario. Arreglo: comparar frase a frase (la fila del registro ya guarda `texto` por frase y los wavs por
   frase existen): reutilizar las frases con el mismo texto y misma firma y generar solo las nuevas; es el mismo
   mecanismo que `parcial`/`REHACER_FRASES`, solo que activado por diferencia de texto. Ahorro: proporcional a las
   correcciones de traducción (p. ej. revisiones como la del 009 o glosario); sin cifras reales, pero cada caso evita
   ~94 % del coste de esa intervención. Esfuerzo bajo-medio, riesgo bajo, no cambia lo aprobado (solo se aplica a
   ediciones futuras). Es además la pieza genérica que usa el punto 1 si algún día hay cortos con frases propias.
3. **`pausa_max` está en la firma** y `acortar_pausas` se aplica antes de guardar `tts/frases/*.wav`, así que
   cambiar la pausa de una voz (Nivi 0,20; Brett 0,30; Deutsch 0,20 se cambiaron el 2-nov) obliga a regenerar todos
   sus clips con GPU, aunque solo es posprocesado. Guardar también la frase cruda (antes de `acortar_pausas`; ~2,4 GB
   para 848 min a 24 kHz/16 bit) permitiría reaplicar la pausa sin GPU. Solo merece la pena si el autor prevé
   volver a tocar pausas; hasta hoy cada cambio habría costado hasta 100 u si hubiera habido catálogo hecho.
4. **Cuidado con cambios de `voces.json` que no afectan al sonido**: `firma` incluye las rutas `ref` y `adaptador` tal
   como están escritas. Renombrar o mover un directorio (p. ej. `paso_0120` a otra ruta equivalente) invalida todos
   los clips de esa voz sin necesidad. `nota`, `_comentario`, `lote` y `ronda` no entran en la firma (bien). Conviene
   que la firma use un hash del contenido del adaptador/ref, o una versión manual ("voz_v": 2) en lugar de la ruta.
5. **Whisper revisa todas las frases** (incluidos clips sembrados desde el largo; no se vuelven a revisar porque
   `clip_al_dia` los da por buenos: bien). Fuera del encargo, ya cubierto por los informes de Whisper/GPU.
6. **Sesión**: encadenar todos los episodios pendientes en una sola sesión evita pagar 2–5 min de carga de modelos
   varias veces (cada recarga ~0,1–0,2 u). También permite la cola por voz "entre episodios" del punto 4.3.

## 6. Lista priorizada

| # | Medida | Unidades ahorradas (est.) | Esfuerzo | Riesgo | ¿Cambia audio ya aprobado? |
|---|---|---|---|---|---|
| 1 | Montar el 052 uniendo masters de 001–050 (más 10 min de cola, ~0,8 u); sustituir su `transcript.es.json` por la unión | **~22,8 u** (19,7 con tarifa de `voces.json`) frente a generarlo entero | Bajo (función de unión + decisión del autor de publicarlo) | Bajo | No. Sí cambia el texto del 052 (la traducción propia del 052 se descarta) |
| 2 | `CORTOS`: sembrar clips del largo en los cortos (077, 105, 130; emparejar por `voz`+`frases`, nunca por `speaker`) | **~15,2 u** (182 min; 13–15 según tarifa) | Medio (~100 líneas, prueba sin GPU ya descrita en el doc) | Bajo (100 % de bloques idénticos en los 71 cortos) | No (cortos aún sin generar) |
| 3 | Lotes por voz con frases ordenadas por longitud (por episodio o por sesión) | **~8–19 u** sobre los 575 min pendientes (central ~11); más si se sube el lote a 12 | Medio-alto (reestructurar `generar_bloque`/`generar_episodio`, guardar por frase) | Medio: cambia semillas y composición del lote; hace falta una prueba A/B a ciegas en 1 episodio y vigilar memoria de Whisper | No en lo aprobado; sí cambia el audio de los episodios aún no generados (otro muestreo) |
| 4 | Reutilizar frases ya generadas al cambiar una frase del bloque (rehacer solo las distintas) | Variable: ~94 % del coste de cada intervención editada; sin datos de cuántas ediciones habrá | Bajo-medio | Bajo | No |
| 5 | Reintentos aplazados al final del episodio y agrupados | ~2–3 u | Bajo | Bajo | No |
| 6 | Calibrar `tope_pasos` con registros reales (`calibrar_tope.py`) | <= 1 % (≈0,5 u); solo si los registros muestran muchos topes | Bajo | Medio si se aprieta de más (trunca frases lentas) | No |
| 7 | Guardar la frase cruda para cambiar pausas sin GPU | 0 hoy; evita cientos de unidades si se toca una pausa más | Bajo | Bajo (más espacio en Drive) | No |
| — | Caché global por (voz, texto) | **0**: 2 duplicados en 7.571 frases | — | — | — |
| — | 052 con reutilización de frases idénticas (opción B) | ~7 u frente a 22,8 u de la opción A | Alto | Medio | — (descartada) |

Resumen de ahorro total frente al plan "generar todo": 1 + 2 ≈ **38 u** (456 min evitados, de 108,7 a 70,7 u), más 3 ≈ 8–19 u
sobre lo que queda por generar. Los puntos 1 y 2 son los de mayor ahorro y menor riesgo.
