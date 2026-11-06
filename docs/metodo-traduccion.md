# Método de traducción por serie

Lo que funcionó en la sesión de Naval y Nivi (5 y 6-nov) para traducir y revisar una serie entera sin errores de
término. Complementa el bloque común de `docs/prompts-revision-por-invitado.md`, que sigue mandando: este documento
explica **cómo** hacerlo en la práctica. Vale para cualquier hablante.

## 1. El orden de trabajo

1. **Leer todo el inglés de la serie antes de preguntar ni traducir.** No el brief: los transcripts. El brief lo
   escribió otro agente; lo que hace falta es entender al hablante de primera mano.
   - Sin leer dos veces lo mismo: compara las frases inglesas de cada episodio con las de las recopilaciones (052,
     077, 105, 130, 154…). Lee el largo entero y, de los cortos, solo lo que no esté en él.
   - En 2019 eran 87 000 palabras, pero sin repetir quedaron 60 000: el 052, el 051, el 069, el 077 y las frases
     sueltas de los cortos.
2. **Volver al autor con lo aprendido, no con preguntas.** El autor lo pidió así. En ese informe van:
   - de qué hablan y cómo hablan;
   - **por qué usa el hablante sus palabras y no otras**: busca las veces que él mismo lo explica (Naval: «specific
     knowledge, porque los demás términos estaban gastados»; «leverage no lo digo en sentido financiero»);
   - las parejas de conceptos que hay que mantener distintas;
   - las imágenes que se repiten entre episodios y tienen que sonar igual;
   - el registro real (palabrotas, coloquialismos);
   - las trampas estructurales (quién lee tuits, a quién se habla en plural).
3. **Cruzar con el español que ya existe**, con datos y no de memoria. Un script que cuente, por episodio, cómo se
   traduce hoy cada término clave. Así aparecieron:
   - *equity* traducido unas veces como «participación» y otras como «capital», que choca con el capital como
     apalancamiento;
   - «entradas y salidas» en un episodio y «lo que aportas» en otro;
   - el mismo «crook» como «sinvergüenza», «ladrón» y «estafador» en tres episodios.
4. **Preguntar al autor con este formato**:
   - una pregunta por término;
   - qué hay hoy y dónde (episodio, bloque, cuántas veces);
   - dos o tres opciones con su coste;
   - la recomendada primero;
   - y al final se le pide que conteste en una línea, del tipo «1A 2B 3A…».

   El cuadro de preguntas con botones lo ignoró dos veces; la lista en texto la contestó entera. Las preguntas
   abiertas también valen: «busca la definición en internet y usa la más correcta» es una respuesta.
5. **Apuntar las decisiones en GLOSARIO.md y hacer commit antes de traducir.** Con fecha y «decisión del autor».
6. **Traducir episodio a episodio.** Borrador, revisión frase a frase, simulación con cero avisos, notas, commit y
   push. Un episodio no se da por terminado hasta que ha pasado por todo.

## 2. La parte técnica que lo hizo posible

- **El inglés sale de los Google Docs anuales de Drive** («<año> all podcasts», con el conector). nav.al está
  bloqueado.
  - Se puede delegar la extracción a un subagente.
  - Antes, **calibra con un episodio que ya esté en el repo**: el agente extrae ese, lo compara con su
    `transcript.en.json` y ajusta las reglas de corte hasta que cuadra (con el 016 cuadró palabra a palabra).
  - Después comprueba que las palabras del `.txt` más las quitadas suman las del documento.
- **Del `.json` de `extraer-episodios.py` al formato del normalizador**:
  - las «intervenciones» pasan a `contenido`;
  - las «secciones», a `titulos_seccion`;
  - el subtítulo es la primera línea bajo el título.
  - No hay que fundir bloques por hablante: el script parte en cada título de sección, y eso es lo que mejor casa
    con las recopilaciones.
- **Reutilizar el español de una recopilación.**
  - Se casan los bloques por el inglés normalizado (sin comillas y con los espacios colapsados).
  - Los que no casan letra a letra casi siempre son artefactos del copiado (zero sum frente a zero-sum, un corchete
    distinto, un acento grave suelto) o un título de sección que en el largo está dentro del texto. Hay que mirarlos
    uno a uno.
  - Reutilizar no es copiar: el texto del largo también se revisa frase a frase, y en el 052 aparecieron tres casos
    de vosotros.
- **Herramientas** (copias en el scratchpad de la sesión del 5-nov; reescríbelas si no están):
  - Un **parche por episodio**: solo los bloques que cambian, con sus frases completas, sobre el borrador.
  - Un script que aplica el parche y simula. Imprime el ratio es/en de cada bloque, marca las frases de más de 35
    palabras y pasa el normalizador con `--simular`.
  - Para cambios en episodios ya subidos, **sustitución exacta**: [episodio, bloque, texto viejo, texto nuevo], y
    falla si el texto viejo no aparece exactamente una vez. Evita cambios a ciegas.
  - Al final, **una búsqueda por expresión regular** de las formas viejas en todos los episodios. Debe salir vacía,
    salvo los que se dejan a propósito.
- **El normalizador no lo caza todo.** Se le escaparon «dadme», «hablarais» y «estuvierais». Busca tú las formas de
  vosotros: -áis, -éis, -ais y -eis del subjuntivo, los imperativos en -ad y -ed, y «os».
- **Antes de tocar un episodio ya subido, mira su estado y `docs/estado.md`.**
  - Si ya tiene audio generado (tts, montaje o publicado, o generado aunque siga en «revision»), no cambies sus
    frases sin preguntar.
  - Dale al autor la lista exacta de frases que cambiarían: la fábrica rehace solo esas con `REHACER_FRASES`.
  - El 001, publicado, no se toca.
- **Notas del editor de nav.al** ([correction: …], [meaning …], [bankruptcy]…):
  - no se locutan, ni como frase ni metidas en la frase;
  - van en `notas_editor` del bloque de `transcript.es.json` (formato en GLOSARIO.md) para que las muestre la web;
  - las frases no cambian, así que no obliga a regenerar el audio.
- **Git.**
  - Un commit por episodio, con lo cambiado en el mensaje.
  - Antes de cada push, `git pull --no-rebase` de la rama.
  - Si trabajan varios agentes a la vez, que **solo uno escriba en el repo**; los demás, en `trabajo/`.

## 3. La revisión frase a frase: lo que de verdad hubo que corregir

Esto es lo que salió una y otra vez al revisar 18 episodios y el 052. Vale como lista de comprobación.

- **Estilo indirecto.** Los tuits que se leen en alto, las citas, las órdenes («rompe esa piedra»), lo que alguien
  dijo («Le dicen: Warren, tú haz lo tuyo») y las preguntas que alguien se hace van en indirecto. Los dos puntos de
  presentar una cita también se quitan.
- **Fundir frases cortas** de menos de 8 palabras con la vecina, con un conector natural: y, porque, así que, pero.
  - Una pregunta corta puede ir con su respuesta en el mismo elemento («¿Por qué ibas a ir a una torre Trump? Pues
    por Trump.»).
  - Las enumeraciones de frases sueltas («Tiene que acertar en todo. Tiene que tener criterio. Tiene que…») se juntan
    en una.
- **Partir las de más de 35 palabras** por un punto natural. Que cada mitad se entienda sola.
- **Choques entre términos en la misma frase.**
  - accountability y responsibility juntos: «cargos de responsabilidad».
  - Términos del marco que se pisan, como equity y capital.
  - Un término del glosario que en esa frase significa otra cosa: *leverage* en una negociación pasa a «fuerza
    negociadora».
- **Calcos que se colaron en una traducción revisada**, con su arreglo:
  - bottom of the barrel → el último escalón
  - flies off the shelves → se agota en las tiendas
  - the public eye → el punto de mira
  - put your name out there → exponer tu nombre
  - talking past each other → no se entienden
  - hardwired / we're evolved to → programados / la evolución nos ha preparado
  - critical → crucial
  - glib → ocurrente o simplista, según el caso
  - domain → campo
  - lifestyle business → un negocio para vivir tranquilo
  - case studies → casos prácticos
  - law clerk → letrado de un juez
  - the Olympics of startups → los Juegos Olímpicos de las startups
  - screw up → equivocarse (no «liarla»)
  - the guy → él (no «el tío»)
- **Coherencia dentro del episodio y con su título.** La misma expresión cada vez que vuelve: «tarifa ambiciosa» y
  no «aspiracional», «boleto de lotería premiado», «peón», «quedar a tomar café», «profesión y afición». Si el
  subtítulo dice «en un plazo lo bastante largo», el cuerpo también.
- **Las máximas, cortas y en una sola frase** cuando salen dichas: «Estás jugando a un juego estúpido, y vas a ganar
  un premio estúpido». Así se reconocen.
- **Títulos de libros con su edición española**, buscada: *Jugarse la piel* (Paidós, 2019). Va también en
  «Siglas y títulos» de GLOSARIO.md.
- **Fidelidad.** Comprueba que la traducción de origen no mete ni quita nada: el 052 decía «diez grupos» donde el
  inglés dice diez personas.
- **Cifras en letra.** Y nada de lo que el TTS lee en alto: comillas, guiones, paréntesis o punto y coma.
- **El ratio es/en por bloque**: si queda fuera de 0,85–1,45, escribe en notas si es compresión o falta algo.
- **Las notas de cada episodio** en `metadata.es.json`:
  - de dónde sale el inglés;
  - qué se cambió respecto a la fuente, con el porqué;
  - los artefactos del inglés, señalados y sin tocar;
  - las notas del editor que se quitaron;
  - los nombres que hay que escuchar en el TTS.

## 4. Decisiones del autor que valen para todas las series

- **El autor confirma cada término clave antes de sintetizar.** Ninguno se da por bueno hasta que él lo dice. Así
  falló «recetas» en el 068.
- **Recopilaciones**:
  - El 052 va al revés: primero se producen y publican los cortos, y el largo después, con su propia traducción. Si
    chocan, gana el largo.
  - En las demás (077, 105, 130, 154, 160) se traduce el largo y cada corto es la copia exacta de su tramo de
    bloques. Ver `docs/cortos-y-largos.md`.
- **Anglicismos.** Cuando el autor lo decide, el término va en inglés (*equity*, *inputs*, *outputs*). Las siglas se
  resuelven siempre en la frase.
- **Notas del editor**: fuera de la voz y en la web (`notas_editor`).
- **Si el autor pide buscar**, busca en la web y cita la fuente en GLOSARIO.md. Dealflow se fijó así: «flujo de
  operaciones», según Emprendedores.

## 5. Para delegar en subagentes (por año o por invitado)

- El encargo tiene que bastarse solo: qué episodios (número, slug y qué queda fuera), qué leer antes, de dónde sale
  el inglés (el fileId del Doc), las reglas de escritura, las de subida y git, y qué devolver.
- Un agente lee, aprende y o bien traduce, o bien, si encuentra un término clave sin decidir, **para y devuelve
  preguntas** con opciones y recomendación. No traduce nada a medias.
- Que el agente de un tema técnico (IA, cripto, física) investigue la terminología española en la web (FundéuRAE,
  RAE, prensa del sector) antes de preguntar.
