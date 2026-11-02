# Prompt para la sesión de traducción

Se pega entero en una sesión nueva de Claude Code sobre este repositorio. Es autosuficiente: lo único que
supone es que la sesión leerá los documentos que manda leer.

```
Trabajo en el repositorio spanishnav.al-podcast: el doblaje al español del podcast de Naval Ravikant. Tu
trabajo en esta sesión es SOLO la traducción: convertir episodios en inglés en el transcript.es.json que
después lee la fábrica de voz. La parte técnica (modelos de voz, cuadernos de Colab, la fábrica, Drive) la
lleva otra sesión; no la toques.

RAMA: trabaja en claude/quirky-dirac-x18c3n. Es la que clona la fábrica: un episodio que no esté en esta
rama no existe para ella. Otras sesiones también suben a esta rama: antes de cada push haz
"git pull --no-rebase origin claude/quirky-dirac-x18c3n" (merge, nunca rebase ni force-push). No abras PRs.

LEE ANTES DE EMPEZAR, en este orden:
1. CLAUDE.md entero: estructura, esquemas JSON y por qué el audio no vive en git.
2. GLOSARIO.md: criterios de traducción y términos fijos. Si decides algo nuevo, apúntalo ahí.
3. docs/extraccion.md: cómo llega el inglés desde nav.al (copiado a mano por el autor; nav.al está
   bloqueado desde estas sesiones y no se intenta descargar).
4. docs/revision-episodios.md: el protocolo de revisión y subida de cada episodio. Lo sigues tal cual.
5. Un episodio ya hecho como modelo: episodios/2019/035-finally-wealthy/ (corto) y
   episodios/2019/051-angel-1/ (largo).

EL FLUJO DE CADA EPISODIO
1. El autor te da el inglés: el texto copiado de nav.al, o ya en JSON. Lo conviertes a f0 (inglés literal,
   formato 0) y produces la traducción f5 (formato 5: el español ya troceado en frases para TTS). Si tienes
   la skill spanishnav-formatos, úsala: define esos formatos. Si no, el esquema de entrada está en el
   docstring de scripts/normalizar-extraccion.py: {fecha, titulo, titulo_seccion, titulos_seccion,
   contenido: [{speaker, frases}]}.
2. Mismos bloques y mismos hablantes en los dos idiomas, uno a uno. Los ids (b01-nivi…) NO los pones tú:
   los pone el normalizador.
3. Revisión y subida según docs/revision-episodios.md: cobertura bloque a bloque, normalizar-extraccion.py
   --simular con CERO avisos, revisión del español, y después sin --simular, scripts/indice.py, la
   comprobación de que no hay audio en git, un commit por episodio y push.

CÓMO SE ESCRIBE PARA LA FÁBRICA DE VOZ (lo más importante)
El texto no se lee: se sintetiza con TTS (Qwen3-TTS) y se limpia a mano en Audacity. Cada error de texto es
trabajo manual después.
- Cada elemento de "frases" se genera POR SEPARADO, y Whisper lo revisa: si no dice exactamente el texto, se
  repite. Por eso:
  - Frases de 8 a 35 palabras como norma; ninguna de más de 45. Parte las largas por un punto o un punto y
    coma natural.
  - Funde las muy cortas («Sí.», «Exacto.», «Claro.») con la frase siguiente o la anterior del mismo bloque.
    Una frase de una o dos palabras sale con entonación rara y Whisper la revisa mal. Excepción: si es la
    única frase del bloque (una respuesta suelta), se queda como está.
  - Cada frase tiene que tener sentido completo leída sola: el modelo no ve la anterior.
- Entre frase y frase la fábrica deja una pausa corta (0,12 s; Brett 0,30 y Deutsch 0,20). Si un corte
  pide una pausa más larga, que sea un punto, no una coma.
- Sin nada que el TTS vocalice: ni comillas, ni guiones largos, ni paréntesis, ni puntos suspensivos, ni
  símbolos (%, $, &, /). El normalizador avisa de casi todo; cero avisos.
- Cifras, fechas, porcentajes y unidades en letra, como se pronuncian.
- Signos de apertura ¿ y ¡ siempre.
- Siglas y nombres propios como se leen; si una sigla se deletrea, escríbela como se pronuncia solo si de
  otro modo se leería mal, y apúntalo en GLOSARIO.md.
- Tuteo, español neutro, frases cortas y afirmativas como habla Naval (GLOSARIO.md).

LOS HABLANTES
El campo "speaker" decide qué voz suena, así que tiene que coincidir con lo que conoce la fábrica
(fabrica/voces.json, sección "alias"): Naval, Nivi, Brett Hall (o Brett), David Deutsch (o David), Kapil
Gupta, Matt Ridley, Vitalik Buterin, Haseeb Qureshi, Max Hodak, Guillermo Rauch, Blake Scholl. Escríbelos
siempre igual en todo el episodio. Si aparece un hablante que no está en esa lista, NO lo inventes ni lo
asimiles a otro: avisa al autor, porque hace falta darle una voz en la fábrica (eso lo hace la sesión
técnica).

QUÉ EPISODIOS
Los decide el autor. Para la primera prueba de la fábrica le vienen bien unos pocos episodios cortos o
medianos. Ya hay 10 traducidos: 035, 036, 040 a 045, 051 y 052 (episodios/2019/); no los rehagas salvo que
te lo pida. Los episodios 1 a 34 son "heredados" (CLAUDE.md): ya tienen audio publicado a mano y no se
vuelven a sintetizar; traducirlos tiene poca prioridad y solo si el autor lo pide. El autor puede tener
traducciones antiguas de algunos episodios; si te las pasa, úsalas como punto de partida, pero el resultado
tiene que cumplir todo lo de arriba.

QUÉ NO TOCAS
fabrica/, piloto/, criba/, scripts/dataset/, docs/fabrica-de-voz.md, docs/estado.md ni nada de Drive. Nunca
un .mp3, .wav, .mp4 o .aup3 en git. El inglés no se corrige nunca (es referencia; los artefactos del copiado
se señalan y se dejan). El troceado del español es tuyo, con los criterios de arriba.

QUÉ DECIDE EL AUTOR
Lo de docs/revision-episodios.md: los errores objetivos (tildes, signos de apertura, erratas) los arreglas
y los listas; las decisiones de traducción (un juego de palabras, un término que choca con el glosario) se
las propones con opciones y una recomendación, y no subes ese episodio hasta que responda.

AL TERMINAR CADA EPISODIO
Dale al autor un resumen corto: número y título, bloques, frases, palabras, minutos de audio estimados
(palabras en español / 150), hablantes, lo que arreglaste y lo que le preguntas. Lleva un registro en
docs/traduccion.md (lo creas tú): una línea por episodio con fecha, estado y notas. Es el único documento
de estado que mantienes.
```

## Por qué estas reglas

- **Frases de 8 a 35 palabras y fundir las de una palabra:** la fábrica genera cada frase por separado y la
  revisa con Whisper (`fabrica/fabrica.py`). Las frases sueltas muy cortas salen con mala entonación y
  Whisper las puntúa mal; las muy largas alucinan más.
- **Hablantes que coincidan con `fabrica/voces.json`:** si no, la fábrica se para en la celda de
  comprobación con «Hablantes sin voz en voces.json».
- **Misma rama:** la fábrica clona `claude/quirky-dirac-x18c3n` (`fabrica/construir_cuaderno.py`).
- **Un documento de estado propio** (`docs/traduccion.md`): `docs/estado.md` lo mantiene la sesión técnica,
  y dos sesiones escribiendo el mismo fichero acaban en conflictos.
