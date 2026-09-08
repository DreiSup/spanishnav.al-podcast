# Protocolo de revisión y subida de episodios

Este documento tiene dos partes: **el prompt** que se pega en una sesión nueva de Claude
Code, y **el porqué** de cada regla, para quien lo mantenga.

El prompt es autosuficiente: no supone que la sesión haya leído nada de este repo salvo
`CLAUDE.md`, que es lo primero que manda leer.

## El prompt

```
Trabajo en el repositorio spanishnav.al-podcast, la traducción al español del podcast
de Naval. Lee CLAUDE.md entero antes de tocar nada; ahí está la estructura, los esquemas
y por qué el audio no vive en git.

Te voy a ir pasando transcripts de episodios, dos JSON por episodio: primero el f0
(inglés) y después el f5 (español, ya troceado para TTS). Cógelos en orden y sin
apresurarte. Revisa un episodio entero, súbelo, y solo entonces pasa al siguiente.

Por cada episodio, en este orden:

1. ESTRUCTURA. Que los dos idiomas tengan el mismo número de bloques y los mismos
   hablantes uno a uno, y el mismo número de titulos_seccion. Localiza el episodio en
   catalogo.json por el título inglés para saber su número del feed, su slug y su fecha.

2. COBERTURA BLOQUE A BLOQUE. Calcula el ratio de palabras es/en de cada bloque, no solo
   el total: un bloque al que le falte texto se esconde detrás de un total sano. Mira en
   contexto cualquier bloque fuera de 0,85-1,45 y di si falta contenido o si es que el
   español comprime.

3. AVISOS DEL NORMALIZADOR. Ejecuta:
       python3 scripts/normalizar-extraccion.py <f0.json> <f5.json> --simular
   Avisa de puntuación que el TTS vocaliza, interrogaciones sin signo de apertura,
   bloques sin hablante y bloques vacíos. Deben salir cero.

4. ESPAÑOL. Ortografía y acentos, longitud de las frases (ninguna debería pasar de 45
   palabras) y coherencia con GLOSARIO.md.

5. SUBIR. Quita --simular, añade --fecha AAAA-MM-DD si el catálogo no trae la fecha (hay
   59 episodios sin ella; está en la página, bajo el título). Después:
       python3 scripts/indice.py
       git ls-files | grep -E '\.(mp3|wav|mp4|aup3)$'    # no debe devolver nada
   Un commit por episodio, con lo que encontraste en el mensaje. Push a la rama de
   trabajo, nunca a main.

QUÉ HACES CON LO QUE ENCUENTRES:

- Lo arreglas tú y me listas cada cambio: tildes, ¿ y ¡ que falten, erratas objetivas.
  Son errores, no decisiones, y cambian cómo lee el TTS. Antes de aplicar un arreglo,
  comprueba que no cambia ninguna palabra.
- Me preguntas y NO subes: cualquier decisión de traducción. Un juego de palabras que no
  cuadra en español, un término que choca con el glosario, un conteo que no se sostiene.
  Propón opciones con su coste y recomienda una, pero decido yo.
- Lo subes y lo anotas en el campo notas de metadata.es.json: hallazgos que no bloquean
  pero que hay que recordar antes de sintetizar el audio.

EL INGLÉS NO SE TOCA NUNCA. Es referencia, no pasa por el TTS. Si trae artefactos del
copiado, me los señalas y los dejas.

El troceado en frases del español tampoco se toca: es una decisión de doblaje mía. El
del inglés lo hace el script solo.
```

## El porqué

**Por qué bloque a bloque y no solo el total.** Un episodio de 40 bloques con un bloque
entero perdido sigue dando un ratio global plausible. El ratio por bloque lo caza.

**Por qué el inglés no se toca.** No pasa por el TTS, así que sus erratas son cosméticas,
y `CLAUDE.md` fija que las correcciones van al origen y se vuelve a normalizar. Tocarlo a
mano rompe que los mismos datos den siempre lo mismo.

**Por qué la frontera entre arreglar y preguntar.** Una tilde que falta tiene una sola
respuesta correcta y el TTS la lee mal: arreglarla no gasta el tiempo de nadie. Una
traducción que no cuadra tiene varias salidas con costes distintos y la elección es del
autor. Confundir las dos cosas hace que la revisión se pare en cada episodio, o peor, que
alguien decida por el autor sin decírselo.

**Por qué un commit por episodio.** Para poder revertir uno sin arrastrar a los demás y
para que el diff se lea.

**Por qué cero avisos y no "pocos avisos".** Los avisos del normalizador son todos
mecánicos: si sale uno, o hay un error real o el aviso sobra. Las dos cosas piden mirar.
