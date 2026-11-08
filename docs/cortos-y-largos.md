# Episodios cortos que son trozos de un largo

Análisis del 5-nov (sesión de dirección), a petición del autor: **no generar dos veces el mismo texto**. Método:
comparación del inglés por n-gramas de 8 palabras (repo y Google Docs anuales «20XX all podcasts»); en los grupos
ya traducidos, también del español frase a frase.

## Resumen

| Largo (número) | Cortos dentro | Cobertura del largo | Qué hacer |
|---|---|---|---|
| **077** Happiness | 053–067 (15) | 100 % | Generar el largo; montar los cortos con sus clips |
| **105** The Beginning of Infinity, Part 1 | 072–076 y 078–104 (32) | 100 % | Ídem |
| **130** The Beginning of Infinity, Part 2 | 106–129 (24) | 100 % | Ídem |
| **154** In the Arena (2025) | 139–145 y 147–153 (14; el 146 es un anuncio suelto) | 99,7 % | Ídem, tras traducir **solo el largo** |
| **160** The AI Industrial Revolution (2026) | las 3 partes sin número (Waste Tokens, Vibe Coding Hardware, The Regulatory Frontier) | 74,6 % (el resto es una «parte 4» que no salió como episodio) | Ídem |
| **052** How to Get Rich (recopilación) | 001–050 (salvo 039) | 95 % | **Se genera entero desde su propia traducción** (decisión del autor, 6-nov) |

Números según la regla de `docs/extraccion.md` (orden del archivo − 4; los de 2026, − 7).

## Los grupos que se cortan (077, 105, 130)

Comprobado en el repo:

- Cada corto es un **tramo seguido** de frases del largo, en el mismo orden, sin texto propio, y entre todos lo
  cubren entero.
- **El español es idéntico**: cada corto coincide frase a frase con su tramo del largo.
- **Todos empiezan en un bloque de hablante.** Por eso el master de un corto es la unión de los clips de sus bloques
  (los que la fábrica deja en `tts/` al generar el largo): sin GPU y sin recortar audio.

### Verificación al 100 % (5-nov)

Alineado palabra a palabra, el inglés de cada largo frente a la unión de sus cortos:

| Largo | Palabras | Idénticas en orden | Cortos que empiezan a mitad de una intervención |
|---|---|---|---|
| 077 | 4.652 | 100 % | 0 |
| 105 | 11.774 | 100 % | 0 |
| 130 | 9.965 | 100 % | 0 |

En español, cada corto es un tramo exacto de bloques del largo (mismos hablantes, mismas frases, mismo orden), sin
frases fuera de algún corto y sin solapes. La lista de grupos para la fábrica está en `cortos.json`.

## 154 In the Arena y 160 The AI Industrial Revolution (aún sin traducir)

- Sus cortos solo están en los Google Docs de 2025 y 2026 (inglés). Para que el truco funcione, la sesión de
  traducción debe **traducir el largo y sacar el `transcript.es.json` de cada corto copiando su tramo de frases tal
  cual**, con los cortes en límite de bloque.
- Texto propio de los cortos (hablado):
  - *Inspiration All the Way Down* (139): unas 35 palabras de intro de Nivi que el largo recorta.
  - *Waste Tokens, Save Time*: «Welcome, you're listening to the» (5 palabras).

  O se genera ese bloque aparte (segundos de GPU) o se acepta la intro del largo.
- Las notas «See Part I here» y «Part 3 of our four part discussion…» son texto de la web, no audio.
- Verificado en inglés (5-nov, Docs):
  - **In the Arena**: el 99,8 % es idéntico y en orden. Tres diferencias:
    1. *Inspiration* (139) trae 29 palabras más de intro de Nivi.
    2. El largo tiene una frase que no está en ningún corto, entre el 139 y el 140: «But when it comes to execution,
       you've got to do it yourself».
    3. *You Have to Enjoy It a Lot* (145) **empieza a mitad de una intervención de Naval**. El largo dice «For example,
       if you look at marketing, marketing is an open problem…» y el corto empieza en «Marketing is an open
       problem…».
  - **AI Industrial Revolution**: las tres partes están dentro al 99,4 %, en orden, y cada una empieza en un cambio
    de hablante. Quedan fuera de los cortos las 2.725 palabras finales (la «parte 4»). Al principio del largo hay
    una nota web («Full episode with 20 minutes of new material…») que no es audio.
- **Reglas para la sesión de traducción** (para que los cortos salgan del largo):
  1. Traducir el largo. Cada corto es la copia exacta de su tramo de bloques: mismas frases, mismos hablantes.
  2. Cortar el bloque del largo donde empieza un corto, aunque siga hablando el mismo. En el 154, partir la
     intervención de Naval antes de «Marketing is an open problem…»; «For example, if you look at marketing» queda al
     final del bloque anterior.
  3. La frase «But when it comes to execution…» va en su propio bloque del largo y no entra en ningún corto.
  4. La intro larga de Nivi del 139 va como bloque propio del corto: es lo único que la fábrica tendrá que generar
     para él.
  5. Las notas de la web no se traducen como frases.

## 052 How to Get Rich: al revés

- El inglés de 001–050 está en el 052 (017–034, en un bloque continuo y en orden).
- **El español del 052 se tradujo aparte**: los cortos 001–045 solo comparten entre el 26 y el 63 % del texto con él.
  Cortarlo daría cortos cuyo audio no corresponde a su transcripción.
- Ya hay 19 cortos generados (001–016, 037–039).
- Por eso: generar los cortos y **montar el 052 uniendo sus masters**, como ya recomendaba la sesión técnica
  (`docs/contexto-sesion-global.md`, §7.1). Así, además, cada unión puede ser un capítulo de YouTube.
- Quedan unas 1.800 palabras del 052 sin corto: el final, que parece *Finding Time to Invest in Yourself*
  (13-ene-2020). No está en el catálogo ni en los Docs.
- **Decisión del autor (6-nov): el 052 se genera entero desde su propia traducción**, como un episodio más
  (~23 unidades). No se monta con los masters de 001–050. Lo de arriba queda como contexto.

### Verificación al 100 % (5-nov): unir 001–050 da el 052

Alineado palabra a palabra el inglés del 052 (`transcript.en.json`) con la unión de los 50 cortos: 001–016 y
035–050 del repo; 017–034 del Doc «2019 all podcasts».

- **Orden:** los 50 cortos van seguidos dentro del 052, exactamente en orden numérico (001 → 050), sin solaparse
  entre sí y sin huecos entre uno y otro.
- **Coincidencia:** el 95,4 % de las palabras del 052 son idénticas y en el mismo orden. El resto:
  - **Final del 052 sin corto:** 1.832 palabras, unos 10 min, que empiezan por «A common question we get: how do I
    find the time to start investing in myself…». Parece *Finding Time to Invest in Yourself* (13-ene-2020), que
    no está en el catálogo. Sin esa pieza, el 052 montado acaba en el 050.
  - **001:** nav.al publicó el corto con otra edición del texto, con el mismo contenido y otras palabras (71
    diferencias de 1–3 palabras). No falta ninguna frase.
  - **Una frase de más en tres cortos**, que el 052 no trae. 042: «Puedo resumir el problema del principal y el
    agente con una cita…». 046: la intro de Nivi «Antes hablamos del interés compuesto…». 048: la definición de
    excedente del consumidor.
  - **039 y 043:** 2–3 palabras.
  - **017–034:** las citas destacadas del Doc (13–20 palabras en 017, 018, 021, 022, 023, 024 y 027) **no son
    audio**. Al traer esos episodios al repo no deben entrar como frases. Se comprueba de nuevo cuando lleguen.
- **Español:** los 32 cortos traducidos tienen los mismos bloques y hablantes que su inglés. Los 9 bloques fuera
  del rango 0,85–1,45 (preguntas cortas de Nivi) están leídos y completos. Las citas destacadas que se colaron en el
  inglés de 046 y 048 no se dicen dos veces en español.


## Largos sin cortos (se generan tal cual)

051, 069 (angel investing), 068 (Kapil), 070, 071 (Ridley), 131, 132 (Vitalik), 133, 134 (Deutsch), The Deutsch
Files I–IV, Curate People, A Motorcycle for the Mind, A Return to Code, 'Nothing Ever Happens' Is Over, Sell the
Truth.

## Sin comprobar

- Los 4 diálogos con Kapil Gupta de 2019 (extras): no hay texto en Drive ni en el catálogo.
- *Live in the Future* (161): el Doc solo trae la descripción.

## Instrucciones para la sesión técnica (fábrica)

> Para pegar tal cual en la sesión técnica.

**Objetivo.** Hay episodios cortos que son un tramo exacto de un episodio largo: los mismos bloques, con el mismo
hablante y las mismas frases en español. La lista está en `cortos.json` (`grupos`: largo → sus cortos, en orden).
En esos casos se genera solo el largo con GPU, y cada corto se monta con los clips del largo, sin GPU. El análisis y
la verificación están en `docs/cortos-y-largos.md`.

**Qué hay que añadir a la fábrica** (`fabrica/fabrica.py` y la celda 2 de `fabrica/construir_cuaderno.py`):

1. **Una opción nueva en la celda 2**, por ejemplo `CORTOS = ["2021/105-infinity"]`: los largos cuyos cortos se
   quieren montar. Sin GPU, como `SOLO_MASTER`.
2. **Emparejar bloques.** Para cada corto de `cortos.json[grupos][largo]`:
   - `plan_episodio` del corto y del largo.
   - Cada bloque del corto se empareja con un bloque del largo que tenga **la misma voz y exactamente las mismas
     `frases`**, buscando hacia delante desde el último emparejado (en orden, sin volver atrás).
   - Si algún bloque no tiene pareja, ese bloque se genera como siempre. Es el caso de la intro propia de un corto,
     como el 139 de In the Arena.
3. **Sembrar los clips del corto** con los del largo, renombrados con la numeración del corto:
   - `tts/037naval.wav` del largo pasa a `tts/001naval.wav` del corto.
   - `tts/frases/037naval_07.wav` pasa a `tts/frases/001naval_07.wav`.
   - Se copia la fila de `registro_tts.jsonl` del largo con `fichero` y `bloque` del corto, y un campo `origen`
     (`{"episodio": largo, "fichero": "037naval.wav"}`). Así `clip_al_dia` la da por buena: mismo texto y misma
     firma. Un lanzamiento normal del corto no la regenera, y `REHACER_FRASES` y `localizar.py` funcionan con el
     corto.
4. **Montar el master del corto** con lo que ya existe: `rehacer_master` (o el flujo normal, si hubo bloques sin
   pareja que generar). Usa el título en español del corto en las etiquetas. Salen `audio/<NNN>-<slug>.mp3`,
   `informe_tts.md` e `indice_master.tsv` en la carpeta del corto en Drive, con el mismo formato que cualquier
   episodio: 0,6 s entre intervenciones, -16 LUFS, MP3 mono 44,1 kHz 128 kbps.
5. **Comprobaciones que tienen que fallar en voz alta**, no seguir en silencio:
   - Algún clip del largo no existe todavía: hay que generar antes el largo.
   - Ya existe un clip del corto generado por su cuenta, sin `origen`: no se pisa salvo que se pida.
   - Un corto se queda sin ningún bloque emparejado: casi seguro que la lista está mal.
   - Al terminar, imprimir por corto: bloques sembrados, bloques generados y duración del master.
6. **Si se arregla una frase del largo** (`REHACER_FRASES`), relanzar `CORTOS` con ese largo: vuelve a sembrar los
   cortos afectados y rehace sus masters. Sembrar debe poder repetirse sin efectos raros (idempotente).
7. **Prueba sin GPU antes de entregar**: con un largo pequeño y clips falsos, comprobar que la suma de los masters de
   los cortos dura lo mismo que el del largo, más o menos los 0,6 s de cada unión. Para el 077, la suma de las
   frases de 053–067 es exactamente la del 077.

**Orden de uso para el autor:** generar el largo → escucharlo y arreglarlo → lanzar `CORTOS` con ese largo → los
cortos quedan en estado `tts`, con su master, sin escucharlos uno a uno: el audio es el del largo ya escuchado.

**Primer caso real:** el 077 (27 min de audio, ~2 unidades), con 15 cortos (053–067).

## Montaje (8-nov): `fabrica/cortos.ipynb`

Hecho. Con el largo ya generado, `fabrica/cortos.ipynb` (Colab **sin GPU**) llama a `fabrica.montar_cortos`: empareja
cada intervención del corto con la del largo por **voz y frases idénticas** (no por `speaker`), copia su clip y sus
frases sueltas con el nombre del corto, apunta `de_largo` en el registro del corto (0 s de GPU), monta el master y
escribe el informe. Lo hecho no se repite. Comprobado en el repo: 077, 105, 130 y 160 emparejan al 100 %; en el 154
quedan sin pareja `139 001nivi.wav` y `144 001naval.wav` (las dos excepciones conocidas): se generan después con la
fábrica normal sobre esos dos cortos, que hará solo esas intervenciones.

