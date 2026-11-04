# Prompt para la sesión de traducción

Se pega entero en una sesión nueva de Claude Code sobre este repositorio. Es autosuficiente: lo único que
supone es que la sesión leerá los documentos que manda leer. Versión del 2-nov, tras la primera prueba de la
fábrica y la auditoría de las traducciones antiguas.

```
Trabajo en el repositorio spanishnav.al-podcast: el doblaje al español del podcast de Naval Ravikant. Tu
trabajo en esta sesión es SOLO el texto: pasar el inglés de cada episodio al formato del repo y traducirlo
al transcript.es.json que después lee la fábrica de voz. La parte técnica (modelos de voz, cuadernos de
Colab, la fábrica, Drive) la lleva otra sesión; no la toques.

RAMA: trabaja en claude/quirky-dirac-x18c3n. Es la que clona la fábrica: un episodio que no esté en esta
rama no existe para ella. Otras sesiones también suben a esta rama: antes de cada push haz
"git pull --no-rebase origin claude/quirky-dirac-x18c3n" (merge, nunca rebase ni force-push). No abras PRs.

DÓNDE ESTÁ EL PROYECTO (2-nov)
- La fábrica de voz ya funciona: el 2-nov generó el 044 entero y el autor lo dio por bueno de estructura y
  ritmo. Cada frase se genera aparte, Whisper la revisa y, si no dice el texto, se repite. Cada error de
  texto que se te escape es trabajo a mano en Audacity o un minuto de GPU tirado.
- Una auditoría de las 16 traducciones antiguas de 2019 que hay en Drive (episodios 001–016) concluyó que el
  método funciona: buen sentido, sin omisiones, cero avisos del normalizador. Los fallos que se repetían
  son los que corrigen las reglas nuevas de abajo: troceado copiado del inglés, notas del copiado locutadas
  y siglas o títulos sin criterio.
- El normalizador avisa ahora de más cosas (ver EL FLUJO). "Cero avisos" significa listo para la fábrica.

LEE ANTES DE EMPEZAR, en este orden:
1. CLAUDE.md entero: estructura, esquemas JSON y por qué el audio no vive en git.
2. GLOSARIO.md: criterios de traducción, términos fijos y la sección «Siglas y títulos». Si decides algo
   nuevo, apúntalo ahí.
3. docs/extraccion.md: cómo llega el inglés desde nav.al (copiado a mano por el autor; nav.al está
   bloqueado desde estas sesiones y no se intenta descargar) y cómo se numeran los episodios.
4. docs/revision-episodios.md: el protocolo de revisión y subida de cada episodio. Lo sigues tal cual.
5. Un episodio ya hecho como modelo: episodios/2019/044-schelling-point/ (el que ya pasó por la fábrica) y
   episodios/2019/051-angel-1/ (largo).

EL FLUJO DE CADA EPISODIO
1. EL INGLÉS (f0). El autor copia el texto de nav.al a trabajo/manual/<slug>.txt y
   "python3 scripts/extraer-episodios.py" lo convierte en JSON en trabajo/extraccion/ (docs/extraccion.md).
   Si el autor te pega el texto en el chat, guárdalo tú en trabajo/manual/<slug>.txt con el formato de
   docs/extraccion.md y lanza el script: el troceo del inglés lo hace siempre el script, nunca tú. Si tienes
   la skill spanishnav-formatos, úsala para los formatos (f0 inglés literal, f5 español troceado para TTS).
   Si el autor te lo indica y tienes el conector de Drive, el inglés de todo 2019 está también en el Google
   Doc «2019 all podcasts» (naval-podcast/transcripts/2019); solo lectura.
2. LA TRADUCCIÓN (f5): mismos bloques y mismos hablantes que el inglés, uno a uno. Los ids (b01-nivi…) NO
   los pones tú: los pone el normalizador.
3. REVISIÓN Y SUBIDA según docs/revision-episodios.md:
   - cobertura bloque a bloque (ratio de palabras es/en de cada bloque entre 0,85 y 1,45);
   - "python3 scripts/normalizar-extraccion.py <f0> <f5> --simular" con CERO avisos. Avisa de: caracteres
     que el TTS vocaliza (comillas, guiones, paréntesis, cifras, símbolos), preguntas sin ¿ o exclamaciones
     sin ¡, frases de más de 45 palabras, frases de una o dos palabras que no están solas en su bloque
     (salvo preguntas y exclamaciones) y palabras vetadas por el GLOSARIO (vosotros, os, vale…);
   - trampas conocidas: si el título lleva apóstrofo tipográfico (’) y el catálogo el recto ('), pasa
     --slug; si el catálogo no trae la fecha, pasa --fecha AAAA-MM-DD (está en la página, bajo el título);
   - revisión del español; después sin --simular, scripts/indice.py, la comprobación de que no hay audio en
     git ("git ls-files | grep -E '\.(mp3|wav|mp4|aup3)$'" vacío), un commit por episodio y push.

CÓMO SE ESCRIBE PARA LA FÁBRICA DE VOZ (lo más importante)
- Cada elemento de "frases" se genera por separado (el modelo no ve la frase anterior) y Whisper lo revisa.
  Por eso:
  - El troceado se rehace PARA EL OÍDO. No copies el troceado del inglés frase a frase: en las traducciones
    antiguas eso dejó frases de 60 palabras y «No.» sueltas. Une y parte según cómo suena en español.
  - Frases de 8 a 35 palabras como norma; ninguna de más de 45. Parte las largas por un punto o un punto y
    coma natural.
  - Funde las de una o dos palabras («Sí.», «Exacto.», «Claro.») con la siguiente o la anterior del mismo
    bloque: salen con entonación rara. Excepciones: si es la única frase del bloque, y las preguntas o
    exclamaciones cortas («¿Dónde quedaremos?»), que en el 044 sonaron bien.
  - Cada frase tiene que tener sentido completo leída sola.
- Entre frase y frase la fábrica deja una pausa corta (0,12 s; Brett 0,30, Deutsch y Nivi 0,20). Si un corte
  pide una pausa más larga, que sea un punto, no una coma.
- Sin nada que el TTS vocalice: ni comillas, ni guiones largos, ni paréntesis, ni puntos suspensivos, ni
  símbolos (%, $, &, /). Cifras, fechas, porcentajes y unidades en letra, como se pronuncian.
- Signos de apertura ¿ y ¡ siempre.
- VOCABULARIO: castellano de España. Decisión del autor (2-nov): «coche», «ordenador» y el resto del
  vocabulario de España se mantienen, aunque la voz salga a veces con acento latino. Tuteo en singular. Lo que
  el GLOSARIO sigue vetando, y el normalizador marca: vosotros y sus verbos (podéis, tenéis, estáis), «os»,
  «vale» como interjección, «chaval», «guay», «mola». Si el autor cambia este criterio, se cambia en
  GLOSARIO.md y en el normalizador; no lo decides tú.
- NOTAS DEL COPIADO ([correction: …], [sic], [inaudible], aclaraciones del editor de nav.al): NO se locutan
  ni se convierten en frases de un hablante. El hablante dice lo que dijo; la nota va, traducida, al campo
  "notas" de metadata.es.json, y se la señalas al autor en el resumen. Ejemplo real a evitar: «[correction:
  the tweet is by @mmay3r]» acabó como una frase de Nivi, «aunque en realidad el tuit era de otra persona».
- SIGLAS Y TÍTULOS EN INGLÉS: si hay traducción publicada y conocida en español, úsala; si no, deja el título
  en inglés solo si el TTS lo puede leer razonablemente. Las siglas que se deletrean o se leen raro
  (BOCTAOE) se resuelven en la frase o se escriben como se pronuncian. Cada decisión, en «Siglas y títulos»
  de GLOSARIO.md.
- Registro: frases cortas y afirmativas, como habla Naval (GLOSARIO.md).

LOS HABLANTES
El campo "speaker" decide qué voz suena, así que tiene que coincidir con lo que conoce la fábrica
(fabrica/voces.json, sección "alias"): Naval, Nivi, Brett Hall (o Brett), David Deutsch (o David), Kapil
Gupta, Matt Ridley, Vitalik Buterin, Haseeb Qureshi, Max Hodak, Guillermo Rauch, Blake Scholl. Escríbelos
siempre igual en todo el episodio. Si aparece un hablante que no está en esa lista, NO lo inventes ni lo
asimiles a otro: avisa al autor, porque hace falta darle una voz en la fábrica (eso lo hace la sesión
técnica).

QUÉ EPISODIOS, en este orden salvo que el autor diga otra cosa
1. DEL 001 AL 034 (decisión del autor, 4-nov: se rehacen TODOS los episodios con la fábrica, empezando por el 1;
   la regla de los «heredados» está retirada, ver CLAUDE.md). El autor ya tiene traducciones de estos episodios
   (las de 001–016 están en Drive, en naval-podcast/transcripts/2019/<NNN Título>/, y una auditoría del 2-nov las
   dio por buenas de sentido): úsalas como punto de partida y aplícales todas las reglas de arriba, sobre todo el
   troceado para el oído, las notas [correction] fuera del audio y el vocabulario. Ojo: el 001 de Drive tiene el
   inglés del 002 mal colocado. Normaliza sin --heredado (por defecto ya no se marca).
2. LOS CUATRO DIÁLOGOS CON KAPIL GUPTA de 2019 (extras sin número: On Meditation, On Humility, A Founder's
   Anxiety, The Need for Indifference; docs/extraccion.md).
3. 2024 A 2026: 135–161 y los extras de The AI Industrial Revolution. Si aparece un hablante nuevo, avisa.
Lo que ya está en la rama (035–134) no se rehace salvo que el autor lo pida. El 052 (How to Get Rich, la
recopilación de los episodios 1 a 50) tiene su propia traducción: no la toques; el autor decidirá si su audio se
monta uniendo los de esos episodios.

QUÉ NO TOCAS
fabrica/, piloto/, criba/, scripts/ (salvo ejecutarlos), docs/fabrica-de-voz.md, docs/estado.md ni nada de
Drive (solo lectura, si el autor te lo pide). Nunca un .mp3, .wav, .mp4 o .aup3 en git. El inglés no se
corrige nunca (es referencia; los artefactos del copiado se señalan y se dejan). Si el normalizador avisa
de algo que crees que es un falso aviso, no lo cambies: díselo al autor, que se lo pasará a la sesión técnica.

QUÉ DECIDE EL AUTOR
Lo de docs/revision-episodios.md: los errores objetivos (tildes, signos de apertura, erratas) los arreglas
y los listas; las decisiones de traducción (un juego de palabras, un término que choca con el glosario, una
nota del copiado) se las propones con opciones y una recomendación, y no subes ese episodio hasta que
responda.

AL TERMINAR CADA EPISODIO
Dale al autor un resumen corto: número y título, bloques, frases, palabras, minutos de audio estimados
(palabras en español / 170, medido en la fábrica), hablantes, lo que arreglaste y lo que le preguntas. Lleva
un registro en docs/traduccion.md (créalo si no existe): una línea por episodio con fecha, estado y notas.
Es el único documento de estado que mantienes.
```

## Por qué estas reglas

- **Frases de 8 a 35 palabras y fundir las de una o dos:** la fábrica genera cada frase por separado y la
  revisa con Whisper (`fabrica/fabrica.py`). Las frases sueltas muy cortas salen con mala entonación y
  Whisper las puntúa mal; las muy largas alucinan más. Las preguntas cortas son la excepción: en el 044
  («¿Cuándo quedaremos?», «¿Dónde quedaremos?») sonaron bien.
- **Hablantes que coincidan con `fabrica/voces.json`:** si no, la fábrica se para en la celda de
  comprobación con «Hablantes sin voz en voces.json».
- **Misma rama:** la fábrica clona `claude/quirky-dirac-x18c3n` (`fabrica/construir_cuaderno.py`).
- **Un documento de estado propio** (`docs/traduccion.md`): `docs/estado.md` lo mantiene la sesión técnica,
  y dos sesiones escribiendo el mismo fichero acaban en conflictos.
- **Lo que añadió la auditoría del 2-nov** (16 traducciones antiguas de 2019 en Drive, todas buenas de
  sentido): los fallos que se repetían eran palabras de España en 8 de 16, troceado copiado del inglés (9
  frases de más de 45 palabras y 15 de una o dos), notas `[correction]` convertidas en frases locutadas y
  siglas o títulos en inglés sin criterio. De ahí las reglas de troceado, notas y siglas, y los avisos nuevos
  del normalizador.
- **Vocabulario de España** (decisión del autor, 2-nov): «coche» y «ordenador» se quedan. El normalizador
  sigue marcando vosotros, «os», «vale», «chaval», «guay» y «mola», que el GLOSARIO vetaba antes de esta
  decisión.
- **170 palabras por minuto:** medido en el 044 (299 palabras, 1,7 min de audio con las pausas recortadas).
