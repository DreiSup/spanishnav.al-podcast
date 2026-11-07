# Glosario y criterios de traducción

Objetivo: que todos los episodios suenen a la misma voz. Cuando dudes, apunta
la decisión aquí para no volver a dudar en el episodio siguiente.

## Criterios generales

- **Registro**: tuteo, cercano pero no coloquial. Naval habla en frases cortas
  y afirmativas; conserva esa cadencia en vez de alargar con subordinadas.
- **Vocabulario de España** (decisión del autor, 2-nov): «coche», «ordenador» y el resto del vocabulario
  castellano se mantienen, aunque la voz salga a veces con acento latino. Tuteo en singular. Se siguen
  evitando vosotros y sus verbos, «os», «vale» como interjección y coloquialismos como «chaval», «guay» o
  «mola» (el normalizador los marca), y los localismos de otros países («chévere»).
- **No traduzcas de más**: los términos técnicos ya asentados en inglés se
  dejan en inglés si es como se dicen en español (ver tabla).
- **Pensado para leerse en voz alta**: si una frase se traba al leerla, está
  mal traducida aunque sea correcta. El texto va a pasar por TTS.
- **Cifras y unidades**: escribe los números como se pronuncian («veinte por
  ciento», «setenta y nueve dólares con noventa y cinco»). El TTS lee las cifras
  y los símbolos en alto o se los inventa.
- **Sin puntuación que el TTS vocalice**: nada de comillas de ningún tipo, ni
  guiones largos, ni puntos suspensivos, ni paréntesis. El modelo los pronuncia
  en vez de interpretarlos. El estilo directo se marca cortando la frase y
  dejando que la entonación haga el trabajo, no encomillando. Punto, coma y
  signos de interrogación y exclamación sí: esos los lee como pausas.
  El normalizador avisa si se cuela alguno.
- **Notas del editor de nav.al** (decisión del autor, 6-nov): los corchetes del transcript ([correction: …], [meaning …],
  [bankruptcy] y demás) **no se locutan**, ni como frase ni integrados en la frase, pero **sí se muestran en la web**.
  Van traducidas en el campo `notas_editor` del bloque de `transcript.es.json`, que la fábrica no lee:
  `"notas_editor": [{"tras_frase": 4, "texto": "[de quiebra]", "original": "[bankruptcy]"}]`, donde `tras_frase` es
  el número de la frase (desde 1) tras la que va la nota. Excepción: el 052 conserva sus dos correcciones locutadas
  (b43 y b58), por decisión del autor del 5-nov.
- **Signos de apertura siempre**: toda pregunta lleva su «¿» y toda exclamación
  su «¡». El TTS decide la entonación al empezar la frase, así que sin el signo
  de apertura la lee como afirmación y solo sube al final, cuando ya es tarde.

## Términos

| Inglés | Español | Nota |
|---|---|---|
| leverage | apalancamiento | **Decisión del autor (5-nov):** siempre «apalancamiento» para el concepto de Naval (trabajo, capital, código y medios), aunque no sea financiero: él mismo dice que habla de herramientas (052 b37). «Palanca» solo en la cita de Arquímedes. En una negociación, *leverage* = fuerza negociadora o posición de fuerza (045: «tienes poca fuerza negociadora», no «mal apalancamiento negociador»). |
| equity | equity | **Decisión del autor (5-nov):** *equity* en inglés, siempre. Nunca «capital», que en Naval es uno de los tipos de apalancamiento y el oyente los confundiría (052 b33, b104, b143 y 051 b31 lo traducían así). *Equity holders* = los que tienen equity; *common equity* = acciones ordinarias. Escuchar cómo lo lee el TTS. |
| compounding | interés compuesto | **Decisión del autor (5-nov):** se ancla siempre al interés compuesto, que es la imagen de Naval («Relationships offer a good example of compound interest»). «Componer» no se entiende así en español. *Compounding relationships* = relaciones con interés compuesto; *compounds the effect* = el efecto se multiplica; *the benefits of compounding* = los beneficios del interés compuesto. |
| specific knowledge | conocimiento específico | Término fijo de Naval, no lo varíes. |
| accountability | responsabilidad / asumir la responsabilidad | **Decisión del autor (5-nov):** «responsabilidad» como sustantivo y «asumir la responsabilidad» para *take on accountability*. Si en la misma frase sale *responsibility*, esa va como «cargos de responsabilidad» o «responsabilidades» (052 b104). «Rendición de cuentas» suena burocrático. |
| judgment | criterio | Mejor que «juicio». |
| inputs / outputs | inputs / outputs | **Decisión del autor (5-nov):** en inglés. Ni «entradas y salidas» ni «lo que aportas y lo que obtienes». |
| timely / timeless (specific knowledge, judgment) | del momento / atemporal | **Decisión del autor (5-nov).** «Oportuno» se oye como «conveniente» (052 b278). |
| skin in the game | jugarse la piel | **Decisión del autor (5-nov).** Es el título español del libro de Taleb (ver Siglas y títulos). *Reputational skin in the game* = jugarse la piel con tu reputación. |
| a smart and hardworking crook | un sinvergüenza listo y trabajador | **Decisión del autor (5-nov).** La misma frase sale en 011, 052 b60 y 069 b44: igual en los tres. |
| zero marginal cost of replication / of reproduction | coste marginal de replicación cero | **Decisión del autor (5-nov):** «replicación» siempre, también cuando Naval dice *reproduction*. |
| startup | startup | Se deja en inglés. |
| trade-off | compensación / contrapartida | |
| happiness | felicidad | |
| status game | juego de estatus | |
| wealth (vs. money) | riqueza (frente a dinero) | La distinción es intencionada: mantenla. |
| peace of mind / peace from mind | paz mental / paz frente a la mente | Juego de palabras de Naval; decisión del autor (4-nov). Mantén «paz» en las dos mitades (063, 064). |

## Nombres propios y marcas

No se traducen. Comprueba en `NOTAS.md` del episodio cómo los pronuncia el TTS
y, si hace falta, escríbelos fonéticamente solo en el texto que va al TTS.

## Siglas y títulos

Cómo se escriben para que el TTS los lea bien. Una línea por decisión: la sigla o el título, cómo queda en el
texto en español y por qué.

| Original | En el texto | Nota |
|---|---|---|
| ADN | ADN | Se lee bien como sigla |
| BOCTAOE (Scott Adams) | «unas siglas en inglés que venían a decir que, por supuesto, hay excepciones obvias» | No se lee: se explica en la frase (012) |
| The Wealth of Nations | La riqueza de las naciones | Título publicado en español (016) |
| On the Origin of Species | El origen de las especies | Título publicado en español (016) |
| The Eighth Day of Creation | El octavo día de la creación | Traducción literal (016) |
| Six Easy Pieces | Seis piezas fáciles | Título publicado en español (016) |
| The Intelligent Investor | El inversor inteligente | Título publicado en español (014) |
| tit-for-tat | el toma y daca | Término de teoría de juegos; «ojo por ojo» connota venganza (010). El 052 conserva «ojo por ojo» (b52, b101) por decisión del autor (5-nov) |
| Skin in the Game (Taleb) | Jugarse la piel | Título publicado en España (Paidós, 2019). Decisión del autor (5-nov) |
| net present value (NPV) | valor actual neto | Forma que se enseña en España. Decisión del autor (5-nov). La sigla no se dice |
| S-1 (folleto de la SEC para salir a bolsa) | folletos de salida a bolsa | La sigla con guion y cifra la vocaliza el TTS; se resuelve en la frase (060) |
| Lao Tzu | Lao Tse | Forma asentada en español, como Sócrates o Confucio (065) |
| IQ test | test de inteligencia | «IQ» y «CI» se deletrean mal; se resuelve en la frase (065) |
| If A, then B | si pasa A, entonces pasa B | Decisión del autor (4-nov). Alternativa si el TTS lee mal la «A» suelta: si pasa uno, entonces pasa dos (065) |
| A eats B; B eats C… | uno se come a otro, ese otro se come a un tercero, y así sucesivamente | Las letras en cadena el TTS las lee como preposición o las deletrea (063) |
| Part 1 / Part 2, Files II… (títulos de episodio con partes) | literal: «, parte 1», «, parte 2»; Files II = Documentos II | **Decisión del autor (7-nov):** como en el original, con la cifra o el número romano que traiga. El título no se locuta (solo va a la etiqueta del MP3). Sustituye a «primera parte» y a «parte uno». Aplicado el 7-nov en 051, 069, 070, 071, 105, 130, 131, 132, 133 y 134 |

## Términos por invitado (propuestos el 4-nov, pendientes de visto bueno del autor)

Los fijó el especialista de cada grupo en su brief (docs/briefs/) tras investigar las ediciones españolas y los
transcripts, y se aplicaron en los episodios del workflow del 4-nov. Si el autor cambia alguno, se cambia aquí y en
esos episodios.

### Kapil Gupta (068) — confirmado por el autor el 4-nov

Toda la tabla tiene el visto bueno del autor (4-nov). Vale para el 068 y para los cuatro diálogos de 2019 si se
hacen. Con Kapil el vocabulario es el contenido: cada término suyo va siempre con la misma palabra española. Contexto
y fuentes en docs/briefs/kapil.md, apartado 8.

| Original | En el texto | Nota |
|---|---|---|
| prescription(s) | prescripción, prescripciones | Término clave. Derivados: prescriptionize = convertir en prescripción; prescriptively = de forma prescriptiva; prescription givers = los que dan prescripciones; non-prescriptive = no prescriptivo. No «recetas». |
| truth | la verdad | Su término central. Evita la muletilla «la verdad es que» (suena a «sinceramente»): «Pues la verdad es esta, …» (068, b52). Para *really* en sus frases, mejor «en serio» o «realmente» que «de verdad» cuando choca con «la verdad» (b74). straight truth = la verdad sin rodeos; raw truth = la verdad en bruto. |
| the understanding (como concepto) | la comprensión | Siempre el sustantivo cuando es su concepto: «la comprensión de que…», «la libertad viene de la comprensión de dónde vienen las cosas» (068, b28, b32, b54, b68, b74, b76). Frente a *knowledge* = conocimiento. «Entender» queda para el uso corriente. |
| freedom from the mind | libertad frente a la mente | En paralelo con paz frente a la mente. «Libertad de la mente» significaría lo contrario. |
| There is no other | no hay otro | **Decisión del autor (4-nov)**, en lugar de «No existe el otro» (068, b36 a b38). |
| sincerity / seriousness / genuine | sinceridad / seriedad / auténtico | En Kapil, sinceridad es querer llegar de verdad, no solo no mentir. *Unserious* = los que no van en serio. |
| watch your thoughts | observar tus pensamientos | La práctica de meditación que critica; siempre «observar», nunca «vigilar» (068, b32 y b68). |
| examination / examine | examinar | «el instrumento para examinar» (068, b84). «Examen» suena a colegio. |
| seek / seeker | buscar / buscador | Forma asentada en el lenguaje espiritual en español. |
| self-conflict / self-improvement / self image | conflicto con uno mismo / superación personal / la imagen de uno mismo | |
| journey / destination | el camino / el destino | 068, b48 a b55. En b55 «I'm on the journey» = estoy haciendo el recorrido. |
| should / shouldn't (sustantivados) | los debería / los no debería | Fórmula de Karen Horney en español: la tiranía de los debería. |
| self inquiry | autoindagación | Forma de las traducciones españolas de Ramana Maharshi. |
| zero | el cero | Su concepto: la comprensión de que los problemas se pueden resolver para siempre. |
| titrate | dosificar | Metáfora médica (068, b60). |
| mindfulness / coach | mindfulness / coach | Así se dicen en España; escuchar cómo los lee el TTS. |
| X como variable en una cita (I want to go to X) | tal sitio, tal cosa | La letra suelta se resuelve en la frase, como A come a B en el 063. |
| a pound (peso) | medio kilo | Conversión aproximada para un oyente español (068, b05). |
| the English language | el lenguaje en inglés | 068, b32: los que dan prescripciones se han apropiado del lenguaje en inglés. |
| Siddha Performance / Kapil / Atmamun | sin traducir | Nombres propios; escuchar el acento de Kapil y cómo lee Siddha el TTS antes de sintetizar. |

### Naval y Nivi (001–052, 069, 077) — revisado con el autor el 5-nov

El autor repasó la tabla el 5-nov. Lo marcado «confirmado» tiene su visto bueno; las decisiones nuevas de ese día
(leverage, equity, compounding, accountability, inputs y outputs, timely, skin in the game, crook, replicación, valor
actual neto) están en la tabla general de Términos. Las filas sin marca siguen como las propuso el especialista.

**052 frente a los cortos (decisión del autor, 5-nov):** en la práctica no manda ninguno. Los cortos se producen y
publican primero; el 052 se produce después con su propia traducción. Si chocan, gana el largo. Las correcciones del
editor que el 052 locuta («Corrección: …», b43 y b58) se quedan en el 052; en los cortos rigen las reglas del 008 y
el 010.

| Original | En el texto | Nota |
|---|---|---|
| compounding relationships / compounds (efecto) | relaciones con interés compuesto / el efecto se multiplica | Decisión del autor (5-nov), ver compounding en Términos. Sustituye a «relaciones que (se) componen» |
| zero marginal cost of replication | coste marginal de replicación cero | Decisión del autor (5-nov): «replicación» siempre |
| consumer surplus / producer surplus | excedente del consumidor / excedente del productor | 052, 048 |
| price discrimination | discriminación de precios | 052, 047 |
| net present value (NPV) | valor actual neto | Decisión del autor (5-nov), sustituye a «valor presente neto» (049, 052). La sigla no se dice |
| externality / mispriced externality | externalidad / externalidad mal valorada | 052, 050 |
| deal / dealflow / pass on | operación / flujo de operaciones / pasar de | 051, 069. **Dealflow: «flujo de operaciones», decisión del autor (6-nov)** tras buscar la traducción: es la traducción literal que da la prensa de emprendimiento en España (Emprendedores), que por lo demás usa el anglicismo, y casa con deal = operación, que es lo que dice todo el corpus. «Flujo de tratos» obligaría a cambiar deal por trato, que suena a acuerdo de palabra |
| non-consensus right | acertar contra el consenso | 051, 069 |
| VC / venture capital | capital riesgo, fondo o inversor de capital riesgo | Confirmado (5-nov). La sigla no se escribe |
| carry | participación en beneficios | 051 |
| due diligence | diligencia debida | 069 |
| FOMO | el miedo a quedarse fuera | Sigla resuelta en la frase (069) |
| pivot | pivotar (verbo), giro (sustantivo) | 069 |
| first-time founder / repeat founder | fundador primerizo / fundador que repite | Confirmado (5-nov). 069 |
| coachable / coachability | que se deja aconsejar / dejarse aconsejar | Confirmado (5-nov). 069 |
| access (to deals) | acceso | Confirmado (5-nov). 051, 069 |
| billion / trillion | mil millones / billón | Trampa recurrente |
| SaaS | software como servicio | Siglas y títulos: resuelta en la frase |
| Dunning-Kruger | Dunning Kruger | Siglas y títulos: sin guion para el TTS |
| Glengarry Glen Ross | la película Éxito a cualquier precio | Confirmado (5-nov). Título en España (1992); «la película» delante para que se entienda como título |
| How to Angel Invest, Part 1 / Part 2 | Cómo invertir como ángel, parte 1 / parte 2 | Títulos del 051 y el 069. Confirmado como «parte uno / parte dos» el 5-nov; pasa a «parte 1 / parte 2» por la regla general de títulos con partes del autor (7-nov, ver Siglas y títulos) |
| Warren Buffett | Warren Buffett | Corregir la errata «Buffet» de 051 b35 |

### Naval y Nivi 2025 y 2026 (139–159) — decisiones del autor del 7-nov

Las preguntas salieron de leer entero el inglés de 2025 (139–155) y 2026 (156–159). Lo que no está aquí sigue la
tabla general y la de Naval y Nivi de arriba.

| Original | En el texto | Nota |
|---|---|---|
| agency / high agency | capacidad de actuar / mucha capacidad de actuar | Para 2025 y 2026. Naval la define como creer que puedes cambiar las cosas. 148: Cúlpate de todo y conserva tu capacidad de actuar. «Agencia» suena a agencia de viajes |
| In the Arena / Life is lived in the arena / The Man in the Arena (Roosevelt) | En la arena / La vida se vive en la arena / el hombre en la arena | Es como circula el discurso en español. Título del 154: En la arena |
| Curate people | Elige bien a la gente | Título y máxima final del 155 |
| the «cult» in culture | Por algo cultura y culto comparten raíz | Se mantiene el juego. Título del 155: Los primeros equipos parecen sectas |
| bankster | banquero mafioso | 142, 148, 154 |
| opinionated | con opiniones muy firmes | También para productos (155) |
| Impossible, Inc. (The Impossible Company) | la empresa se llama, literalmente, la empresa imposible, Impossible Inc. | Se mantiene el chiste (141, 154). Después, Impossible a secas |
| AI | la inteligencia artificial, y luego la IA / las IA | Mixto: «la inteligencia artificial» al principio de cada bloque y cuando es el concepto; «la IA», «una IA», «las IA» (plural invariable) en el resto. **Hay que escuchar «la IA» en la fábrica antes de sintetizar.** En títulos, IA |
| vibe coding / vibe coders | vibe coding / la gente que hace vibe coding | En inglés, glosado la primera vez en cada episodio. Escuchar; reserva fonética «vaib coding» |
| prompt / prompting / prompt engineering | prompt / ingeniería de prompts | En inglés siempre |
| debug / bug / hack | debug / bug / hack | En inglés |
| feedback | feedback | En inglés en los episodios de Naval y Nivi de 2025 y 2026. Los de Brett y Deutsch (072–134) y Ridley conservan retroalimentación mientras el autor no diga otra cosa |
| libraries / pull request / test harness / context window / cron jobs | bibliotecas / pull request / banco de pruebas / ventana de contexto / tareas programadas | pull request en inglés porque Naval bromea con el nombre |
| Productos y empresas (Claude, Gemini, ChatGPT, Nvidia, Grok, Codex…) | tal cual | Prueba conjunta en la fábrica antes de sintetizar; fonética solo de reserva (Clod, Yémini, Envidia). Versiones con palabras: GPT cinco punto dos, Claude Opus cuatro punto cinco, C más más |
| Títulos 156–159 | Una moto para la mente / La vuelta al código / Se acabó lo de que nunca pasa nada / Vende la verdad | Aprobados |
| tokens / a trillion tokens | tokens / un billón de tokens | Glosado la primera vez en 157 b03: los trozos de texto con los que trabajan. Trillion = billón |
| one-shot / one-shotting / one-shotted | one-shot | En inglés, también el juego de 157 b05 |
| jagged intelligence | inteligencia dentada | Karpathy (157 b10, 158 b06) |
| unaligned AI / unaligned humans with AI | IA desalineada / humanos desalineados con IA | Se mantiene el juego (156 b18) |
| There is no demand for average | No hay demanda para lo promedio | Decisión del autor (7-nov). Título de sección del 156 y su cuerpo (b10, b13) |
| evangelical sale / sell | vender como un evangelizador / venta evangelizadora | 159 b13 a b15. «Evangélica» suena a protestante |
| 10x / 100x / 1000x programmers | programadores que rinden por diez, por cien, por mil | 156 b22. Sin la x |
| taste / tastemaker | gusto / alguien con buen gusto | Judgment sigue siendo criterio. No «prescriptor», que choca con Kapil |
| A taste of freedom can make you unemployable / homeschooled… unschoolable | probar la libertad puede hacerte inempleable / un niño que ha estudiado en casa ya no hay quien lo escolarice | 159 b11 |
| bullshitting / shitty startup / pooping | inventárselo / una startup muy mala / ir al baño | Decisión del autor (7-nov): sin palabrotas (156 b31, 159 b15, 156 b17) |
| Comillas irónicas (sales, techniques, bioethicists…) | lo que llaman vender, la supuesta técnica, los llamados bioéticos | Reformuladas. «Entre comillas» dicho en voz alta, como mucho una vez por episodio |
| Influence / Pre-Suasion (Cialdini) | Influencia. La psicología de la persuasión / Pre-suasión | HarperCollins, 2022 / Conecta. CLASSR no se dice: se dicen los seis principios |
| Wind, Sand and Stars / Airman's Odyssey (Saint-Exupéry) | Tierra de hombres / una recopilación de sus libros de aviación | Airman's Odyssey solo existe en inglés |
| Liftoff (Berger) / The Macintosh Way (Kawasaki) / The Soul of a New Machine (Kidder) | Liftoff / The Macintosh Way, con descripción / El alma de una nueva máquina | Sin edición española confirmada (159 b12) |
| The Wolf of Wall Street / sell me this pen | El lobo de Wall Street / véndeme este bolígrafo | 159 b14 |
| Skynet (Terminator) | la hora que dice Naval | 156 b41: no se corrige (la real es 2:14 del 29 de agosto) |

**Corte del 145 dentro del 154 (decisión del autor):** «For example, if you look at marketing,» va al final del bloque
del largo que corresponde al 144. Ese bloque del largo deja de ser idéntico al del corto 144, que se genera aparte.

**Fechas (decisión del autor, 7-nov):** manda la fecha de la página del episodio (la que aparece bajo el título en nav.al y
en los Google Docs anuales), no la del índice nav.al/archive. Corregidas en catalogo.json y en el episodio 139, 140, 141,
144, 147, 148, 149, 150, 151, 153 y 154.

**2026, resto (decisión del autor, 7-nov):** el Nivi repetido del 159 (b20 y b21) se traduce dos veces, fiel al inglés;
el 158 b09 (Wuhan, vacunas, bioéticos) se traduce fiel, sin suavizar; las frases hechas y la lista de términos sin
pregunta del informe de 2026 quedan aprobadas tal cual.

### Brett Hall y David Deutsch (072–134) — decisiones del autor del 7-nov

Las preguntas salieron de leer entero el inglés de la serie (los 56 cortos y las entrevistas 133 y 134) y de contar
cómo estaba traducido cada término en el repo. Toda la tabla tiene el visto bueno del autor (7-nov): lo marcado «decisión del autor» lo eligió entre
opciones, y lo marcado «confirmado» lo aprobó tal cual. Las recopilaciones 105 y 130 son la fuente y cada corto es la
copia exacta de su tramo (docs/cortos-y-largos.md): un cambio va al largo y a su corto a la vez.

| Original | En el texto | Nota |
|---|---|---|
| guess (sustantivo, epistemológico) / conjecture | conjetura | **Decisión del autor (7-nov).** Siempre, también con el hijo de Naval (134 b04): la tesis es que toda suposición es una conjetura. El verbo *to guess* según el contexto: conjeturar, suponer, adivinar («Guess what?» = ¿Y sabes qué?). *Assumption* = suposición |
| testable / testability | contrastable / que se pueda contrastar, contrastabilidad | **Decisión del autor (7-nov)**, en lugar de «comprobable»: es el término de las traducciones de Popper. El verbo *to test* y el sustantivo *test* siguen como comprobar, poner a prueba, prueba |
| universal explainer(s) | explicador universal, explicadores universales | **Decisión del autor (7-nov).** Familia con ordenador universal (133 b40) y universalidad explicativa (134 b22) |
| hard to vary / hard to come by | difícil de variar / difícil de conseguir | **Decisión del autor (7-nov).** La cadena de 133 b29 tiene que sonar paralela. El título de sección del 133 (*hard to find*) también va con «conseguir» |
| reach (de una explicación) | alcance / alcanzar | **Decisión del autor (7-nov).** Mantiene el juego de 133 b38: ni siquiera alcance a tu vecino |
| narrow and risky predictions | predicciones concretas y arriesgadas | **Decisión del autor (7-nov).** *Narrow and precise* = concretas y precisas (083) |
| demonstration (frente a experiment y measurement, 134) | demostración práctica la primera vez, luego demostración | **Decisión del autor (7-nov).** Para que no se confunda con la demostración matemática (*proof*), que es demostrar |
| mathematician's misconception | el error de concepto de los matemáticos | **Decisión del autor (7-nov).** 085 b02, 090 b01 |
| error correction / the means of error correction | corrección de errores / los medios para corregir errores | **Decisión del autor (7-nov).** |
| settled (science, mathematics) / final theory | definitiva, la ciencia ya está zanjada / teoría definitiva | **Decisión del autor (7-nov).** |
| feedback | retroalimentación | **Decisión del autor (7-nov)** para esta serie (14 frases y el título del 125). Los episodios de Naval y Nivi de 2025 y 2026 dicen feedback (ver su tabla) |
| compromise (sustantivo) | término medio / solución de compromiso | **Decisión del autor (7-nov).** Título del 124: La miseria del término medio, por La miseria del historicismo de Popper. «Compromiso» a secas se entiende como *commitment* |
| AGI / artificial general intelligence | inteligencia artificial general | **Decisión del autor (7-nov): siempre la forma larga**, sin abreviar a «inteligencia general» ni usar la sigla |
| strong opinions, loosely held (Andreessen) | opiniones fuertes, sostenidas con poca fuerza | **Decisión del autor (7-nov).** Las combinaciones del 125 en paralelo |
| One Einstein is worth a legion of PhD drones | Un Einstein vale más que una legión de doctores autómatas | **Decisión del autor (7-nov).** Título del 121; en el texto, autómatas con doctorados en física |
| It's Mind Blowing That Our Minds Can't Be Blown | Lo alucinante es que nada puede alucinarnos | **Decisión del autor (7-nov).** Título del 113; en el texto, lo alucinante es que nada puede alucinarte |
| snailiens | caracolienígenas | **Decisión del autor (7-nov).** 133 b12 |
| Catch-22 | la pescadilla que se muerde la cola | **Decisión del autor (7-nov).** 133 b11 |
| believe in science, which is an oxymoron | creer en la ciencia, lo cual es un oxímoron | **Decisión del autor (7-nov).** 072 b01 y 105 |
| the human race | la raza humana | **Decisión del autor (7-nov)**, también en los títulos de 133 y 134 y en su título de sección |
| Corchetes del editor que completan la frase (134: [They think], [showed], [also], [Doctors], [and], [but]) | fuera de la voz, en notas_editor | **Decisión del autor (7-nov):** se aplica la regla general de notas del editor aunque sean palabras que completan la frase. La frase española se escribe para que se sostenga sin ellas |
| good explanation | buena explicación | Confirmado por el autor (7-nov) |
| falsifiable / falsify | falsable / falsar | Confirmado por el autor (7-nov). Nunca «falsificable» |
| aliens | extraterrestres | Confirmado por el autor (7-nov). «Alienígenas» solo dentro de caracolienígenas |
| worldview / taking (theories, children) seriously | visión del mundo / tomarse en serio | Confirmado por el autor (7-nov) |
| universal computer / Bayesian | ordenador universal / bayesiano | Confirmado por el autor (7-nov) |
| prove (matemáticas) / test (ciencia) | demostrar / comprobar, poner a prueba | Confirmado por el autor (7-nov) |
| The Beginning of Infinity | El comienzo del infinito | Confirmado por el autor (7-nov). Biblioteca Buridán, 2012 |
| The Fabric of Reality | La estructura de la realidad | Confirmado por el autor (7-nov). Anagrama, 1999 |
| Nullius in verba | Nullius in verba en el título; nulius in verba en el texto | Confirmado por el autor (7-nov). Una sola ele para que el TTS no lea «nuyius» (074) |
| Deutsch | Deutsch | Confirmado por el autor (7-nov). «Doich» solo si el TTS lo lee mal |
| GPT-3 | GPT tres | Confirmado por el autor (7-nov). Escuchar; alternativa «ge pe te tres» |
| Church-Turing | Church Turing | Sin guion |
| person A, idea X, theory Z | una persona, una idea, la otra, una tercera idea | Letras sueltas resueltas en la frase, como en 063 (124, D10) |
| ToKCast | Tokcast | Confirmado por el autor (7-nov). Con su explicación la primera vez: podcast de la teoría del conocimiento |

### Matt Ridley (070, 071)

| Original | En el texto | Nota |
|---|---|---|
| invention / innovation | invención / innovación | Distinción de Ridley; an invention = un invento. Fijo para el grupo Ridley y para cualquier mención posterior. |
| How Innovation Works (Matt Ridley) | Claves de la innovación | Título publicado (Antoni Bosch, 2021). Va en la tabla de Siglas y títulos. |
| The Rational Optimist / Genome / Nature via Nurture (The Agile Gene) | El optimista racional / Genoma / Qué nos hace humanos | Ediciones de Taurus. The Agile Gene es el título estadounidense de Nature via Nurture. |
| The Beginning of Infinity (Deutsch) | El comienzo del infinito | Biblioteca Buridán, 2012. Afecta también al grupo Brett-Deutsch. |
| network effect | efecto de red | Ya usado en 052; conviene fijarlo. |
| venture capital | capital riesgo | Ya usado en 051 y 052; la sigla VC se resuelve como un inversor de capital riesgo. |
| blockchain / tokens | blockchain / tokens | Decisión del autor (7-nov), en la sección de Vitalik. smart contracts también en inglés. |
| crypto | cripto (cryptoland = el mundo cripto) | Ya usado en el corpus aprobado. |
| top-down / bottom-up | de arriba abajo / de abajo arriba | Nunca el anglicismo. |
| herd immunity / lockdown | inmunidad de grupo / confinamiento | Decisión pendiente; alternativa: inmunidad de rebaño. |
| great man theory | teoría del gran hombre |  |
| billion | mil millones | Nunca billón. Para Cifras y unidades. |
| siglos (1100s, 15th century) | el siglo doce, el siglo quince | En letra y sin números romanos, que el TTS deletrea. |
| GDP / STEM / AGI / NSA | producto interior bruto / las ciencias, la tecnología, la ingeniería y las matemáticas / inteligencia artificial general / la Agencia de Seguridad Nacional | Siglas resueltas en la frase. |
| Pets.com / dot-com | Pets punto com / puntocom | El punto lo vocaliza o lo convierte en pausa. |
| chiefs, priests and thieves (Ridley) | gobernantes, sacerdotes y ladrones | Decisión pendiente; alternativas: jefes, sacerdotes y ladrones o caciques, curas y ladrones. |
| universal explainers (Deutsch) | explicadores universales | Coordinar con el grupo Brett-Deutsch. |

### Vitalik Buterin y Haseeb Qureshi (131, 132) — decisiones del autor del 7-nov

Toda la tabla tiene el visto bueno del autor (7-nov, respuestas 1 a 49 de la ronda de preguntas). Estrategia general
(respuesta 1): **mixta**. Español donde circula y el oyente lo entiende; inglés donde el autor lo ha decidido o no hay
equivalente vivo. Regla de aplicación: manda la palabra inglesa del original. *Chain* sola sigue siendo «cadena»
(«en la cadena», «dos cadenas», «la cadena de Ethereum»); solo *blockchain* pasa a blockchain. Todos los anglicismos
van a la lista de escucha del episodio antes de dar el audio por bueno.

| Original | En el texto | Nota |
|---|---|---|
| blockchain / blockchains | **blockchain**, femenino: la blockchain, las blockchains | Decisión del autor (7-nov). Sustituye a «cadena de bloques». En referencias cortas a *the chain*, «la cadena». smart contract blockchain = blockchain de smart contracts. Escuchar |
| smart contract(s) | **smart contract**, masculino: el smart contract, los smart contracts | Decisión del autor (7-nov). Sustituye a «contrato inteligente» también en 070, 127 y 130. *Contract* solo (el objeto que define Vitalik) = contrato. Escuchar |
| proof-of-work / proof-of-stake | **proof of work** / **proof of stake**, sin guiones; masculino si lleva artículo | Decisión del autor (7-nov). Sustituye a «prueba de trabajo» y «prueba de participación» en la serie. El uso figurado del 029 y el 052 («tener prueba de trabajo») está pendiente del autor. Escuchar |
| staking / stakers / staking pools | staking / quienes hacen staking / **grupos de staking** | Sin «pools». Escuchar staking |
| sharding | fragmentación; unsharded = sin fragmentar |  |
| roll-ups | rollups | Escuchar; fonética de reserva rólaps |
| Layer 1 / Layer 2 | capa uno / capa dos; Layer 2s = las soluciones de capa dos |  |
| Eth | Ethereum (la red) / ether (el activo) | Si ether suena a éter: la moneda de Ethereum |
| wallet(s) | **wallet**, femenino: la wallet, las wallets | Decisión del autor (7-nov). Sustituye a «monedero». multisig wallet = wallet multifirma; social recovery wallet = wallet de recuperación social. Escuchar |
| fork / hard fork / the DAO fork | bifurcar / bifurcación dura / la bifurcación de la DAO |  |
| hack / hacked / hacker | **hackeo / hackear / hacker**, en todos los sentidos | Decisión del autor (7-nov). Sustituye a ataque y atacante cuando el inglés dice hack. *Attacker* y *attack* siguen siendo atacante y ataque. young hacker = joven hacker |
| run a node | **ejecutar un nodo** | Decisión del autor (7-nov). Sustituye a «tener un nodo» |
| on-chain / off-chain | en la cadena / fuera de la cadena |  |
| block space | **espacio en los bloques** | Decisión del autor (7-nov). Sustituye a «espacio de bloque» |
| throughput | capacidad de procesamiento; transacciones por segundo si hay cifra | Performance = rendimiento |
| permissionless / permissioned | sin pedir permiso a nadie / lo que más permisos exige |  |
| trade-off | según la frase: sacrificar algo a cambio de algo, cambiar datos por computación, curva de compensación, equilibrio | No se unifica |
| enshrined | consagrar |  |
| store of value | depósito de valor | No reserva de valor, que choca con moneda de reserva |
| free-rider effect | efecto polizón |  |
| altcoin / stable coins | **altcoin**, femenino / **stablecoins** | Decisión del autor (7-nov). Sustituye a «moneda alternativa» y «monedas estables». Escuchar |
| AMM / DeFi / VPN | creador de mercado automatizado / finanzas descentralizadas / redes privadas virtuales | Siglas resueltas en la frase |
| digital rock | la roca digital | Imagen de Vitalik |
| encrypt / encryption / encrypted | **encriptar / encriptación / encriptado** | Decisión del autor (7-nov). Sustituye a «cifrar» y «cifrado», también en 071. encryption-decryption key = clave de encriptación y desencriptación |
| moon math | matemáticas de otro planeta |  |
| crypto / crypto-land / crypto-head | cripto / el mundo cripto / un fanático de las criptomonedas |  |
| OG / OGs | uno de los pioneros, el original (Bitcoin) / los veteranos |  |
| maxis / maximalist | los maximalistas / maximalista |  |
| memelord | maestro de los memes |  |
| hustle / alpha / edges | filón / margen que sacar / ventajas | Haseeb |
| bang for the buck | más te vale sacar mucho a cambio |  |
| shilling | hacer propaganda |  |
| uppity young entrepreneur | el joven emprendedor descarado |  |
| elder statesman | **el viejo estadista** | Decisión del autor (7-nov). Sustituye a «el gran estadista veterano» |
| stake in the ground | fijar una postura |  |
| slings and arrows / open season / watershed moment | recibir palos por todas partes / barra libre / punto de inflexión |  |
| white knights | supuestos salvadores autoproclamados |  |
| navel gazing (juego Naval/navel, 132 b45) | **se recupera** el juego en la frase | Decisión del autor (7-nov): «ni porque nos estemos mirando el ombligo, y eso que mi nombre en inglés suena a ombligo» |
| my Bitcoin trip | **mi gira por el mundo de Bitcoin**, y después mi gira | Decisión del autor (7-nov). Sustituye a «mi viaje de Bitcoin» |
| single-handedly | por sí sola |  |
| mean (be mean) | desagradable; meanness = dureza |  |
| compound interest | interés compuesto | Como en todo el corpus |
| Bitcoin / bitcoins | Bitcoin (la red, con mayúscula) / bitcoins (las unidades) | Decisión del autor (7-nov). Mayúscula también en 006 b02 y 052 b37 (no cambia el audio) |
| The DAO | la DAO |  |
| EIP-1559, EIP-4488 / EIP | la propuesta de mejora mil quinientos cincuenta y nueve / cuatro mil cuatrocientos ochenta y ocho / propuesta de mejora de Ethereum | Sin sigla |
| Vitalik | Vitalik | Escuchar primero; fonética de reserva Vitálik |
| Sharding leads to more centralization (131, título 16) | La fragmentación lleva a más centralización | Fiel, aunque contradice el texto; anotado en notas |
| Vitalik: Ethereum, Part 1 / Part 2 | Vitalik: Ethereum, parte 1 / parte 2 | Ver Siglas y títulos |
| Eth got saved (131 b67) | en mi opinión, ese ecosistema salvó a Ethereum | Interpretación por el contexto; anotada |
| vetocracy | vetocracia | Fukuyama, Deusto 2016 |
| Covid | la covid | FundéuRAE |
| tweet / retweet | tuit / retuitear | FundéuRAE |
| NFT | NFT, plural invariable |  |
| IYI (Taleb) | intelectuales pero idiotas | Jugarse la piel, Paidós 2019 |
| Vladimir Putin | Vladímir Putin | FundéuRAE; fija el acento |
