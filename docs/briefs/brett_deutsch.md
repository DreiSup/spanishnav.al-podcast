# Brief del grupo «Brett Hall y David Deutsch»

Para traductores y revisores de: los 56 cortos de 2021 sobre *El comienzo del infinito* (072 a 104 y 106 a
129, en los lotes `brett_deutsch-lote-072` a `brett_deutsch-lote-128`), las dos recopilaciones (105
*The Beginning of Infinity, Part 1* y 130 *Part 2*) y las dos entrevistas de 2023 con David Deutsch (133
`david-deutsch` y 134 `david-deutsch-2`, en tres partes cada una: `trabajo/partes_en/david-deutsch*.pN.json`).

Preparado el 4-nov-2026. Fuentes internas: GLOSARIO.md, docs/revision-episodios.md, docs/traduccion.md,
docs/hablantes.md, trabajo/plan.json, los cortos aprobados de 2020 (053 a 067, en `trabajo/f5/`) y el brief
`naval_nivi.md` (para no contradecirlo). No hay traducciones previas de esta serie: **este brief fija la
terminología de toda la serie**. Si una decisión de aquí choca con algo aprobado, manda lo aprobado y se
apunta en `decisiones`.

---

## 0. Lo primero: las dos recopilaciones son los cortos, bloque a bloque

Comprobado con un script el 4-nov sobre `trabajo/f0/`:

| Recopilación | Fuentes (plan.json) | Bloques | Coincidencia |
|---|---|---|---|
| **105 infinity** | los 32 cortos 072 a 104 | 73 = 73 | Los 73 bloques son, uno a uno y en el mismo orden, los bloques de los cortos. Los 289 párrafos son idénticos letra a letra. |
| **130 infinity-2** | los 24 cortos 106 a 129 | 35 = 35 | Igual, 35 a 35. Solo dos párrafos difieren, y en nada que afecte al español: 112 *agi* [0] «text-matching» frente a «text matching», y 115 *intelligent* [0] «planet Earth» frente a «planet earth». |

Consecuencias:

1. **Se traducen los cortos; las recopilaciones se montan con el español aprobado de los cortos, sin tocar una
   palabra.** Mismo texto, misma traducción, mismo troceado: así hasta se podrán reutilizar los clips de TTS.
   Si al montar la recopilación se encuentra un error en un corto aprobado, no se corrige solo en un sitio: se
   apunta en `decisiones` para corregir los dos a la vez.
2. **Los `titulos_seccion` de las recopilaciones son los títulos y los `titulo_seccion` de los cortos**, en
   orden (65 en la 105, 48 en la 130). Por eso el `titulo` y el `titulo_seccion` de cada corto tienen que ser
   definitivos y se copian tal cual. En el apartado 7 propongo los títulos de todos los cortos para que nadie
   los invente dos veces.
3. El primer elemento de `titulos_seccion` de la 105 es una nota del editor que se coló ahí: «A collection of
   all the episodes on The Beginning of Infinity.». Se traduce en su sitio para no descuadrar el número de
   títulos (*Una recopilación de todos los episodios sobre El comienzo del infinito.*) y se explica en `notas`.
   No se locuta.
4. **El campo `speaker` se copia exacto**, y aquí cambia según el fichero:
   - `Brett Hall` en 074 *nullius* (bloque [1]), en toda la 105 *infinity* y en la 134 *david-deutsch-2*.
   - `Brett` en todos los demás cortos y en la 130 *infinity-2*.
   - `David Deutsch` en 133 y 134. `Naval` en todos.
   Al montar la 105 desde los cortos, el hablante sale del f0 de la 105 (`Brett Hall`), no del corto.
5. Notas del editor que van a `notas` traducidas y no se locutan: 130 «Part 2 of my interview with Brett Hall
   about The Beginning of Infinity. Also see Part 1.»; 133 «I interview David Deutsch, physicist and author of
   The Beginning of Infinity. Also see Part 2.»; 134 «Brett Hall and I interview David Deutsch, physicist and
   author of The Beginning of Infinity. Also see Part 1.».

---

## 1. Quiénes hablan y cómo suena cada uno

### Naval Ravikant
Aquí no habla de dinero sino de epistemología, y se presenta como «un físico fracasado» y «estudiante de
ciencia». Es el mismo Naval de los cortos de 2020: frases cortas y afirmativas, tesis y ejemplo.

- **Registro**: divulgador entusiasta. Resume a Deutsch en listas («A good explanation, first and foremost, is
  testable… The second piece… Finally…») y en fórmulas rotundas («Pessimism is self-fulfilling», «The new oil
  is ideas»). Conserva las enumeraciones con su orden y sus marcadores: *En primer lugar… La segunda pieza…
  Por último…*.
- **Anáforas que son su firma**: 120 *ideas* «Call me when they invent something new. Call me when…» (seis
  veces) → *Avísame cuando…* seis veces, sin variar. 129 *caveman* «we needed more stretchy shoes, we needed
  more durable shoes…» → *necesitábamos zapatillas más elásticas, necesitábamos zapatillas más resistentes…*.
- **Muletillas**: *It's interesting that* → «Es curioso que»; *The reality is* → «La realidad es que»;
  *In other words* → «Es decir»; *Of course* → «Claro»; *I would argue* → «Yo diría»; *At some deep level* →
  «En el fondo». *Right?* al final de una pregunta a Brett → «¿no?».
- **Con Deutsch (133, 134)** es más largo y más reverente: preguntas de un párrafo entero que acaban en una
  pregunta corta. Parte el párrafo y deja la pregunta sola al final, con su ¿.
- Lo que **no** hacer: «Cabe destacar», «Es por ello que», «En este sentido». Él diría «Por eso».

### Brett Hall
Divulgador australiano de Sídney, formado en física y filosofía de la ciencia (UNSW) y en enseñanza de
ciencias y matemáticas; conductor de **ToKCast**, un podcast dedicado casi por entero a explicar, capítulo a
capítulo, *La estructura de la realidad* y *El comienzo del infinito*. Su usuario en Twitter es «ToKTeacher».

- **Registro**: profesor. Explica con experimentos caseros y con instrucciones al oyente: «Take a piece of
  paper, take a pen, draw two dots…», «Put a beaker of water on a heat source…». Tradúcelo en imperativo de
  tú: *Coge una hoja de papel, coge un bolígrafo y dibuja dos puntos.* Nunca en vosotros.
- **Muletillas**: *Precisely.* (al empezar a contestar) → «Exacto.» fundido con la frase siguiente, nunca suelto;
  *Now,* → «Ahora bien,»; *In fact,* → «De hecho,»; *Of course,* → «Por supuesto,»; *Guess what?* → «¿Y sabes
  qué?»; *It's not to say that…* → «No es que…». Usa mucho «this vision of…» → «esta visión de…», y
  «so far as we know» → «hasta donde sabemos».
- Habla en párrafos largos con subordinadas encadenadas: es el que más frases de más de 35 palabras genera.
  Parte por la conjunción y repite el sujeto si hace falta para que cada frase se entienda sola.
- Tiene un punto combativo: «which is nonsense», «nothing but the appeal to the supernatural», «immoral
  bastards», «moral midgets». Mantén la fuerza sin vulgaridad: *lo cual es absurdo*, *canallas inmorales*,
  *enanos morales*.

### David Deutsch
Físico de Oxford, pionero de la computación cuántica (formuló el principio de Church-Turing-Deutsch y el primer
algoritmo cuántico), defensor de la interpretación de los muchos mundos de Everett y de la epistemología de
Popper; autor de *La estructura de la realidad* y *El comienzo del infinito*, y padre de la teoría de
constructores con Chiara Marletto. Cofundador de la filosofía educativa *Taking Children Seriously*.

- **Registro**: preciso, seco, irónico y británico. Corrige al entrevistador sin rodeos («They're universal
  computers. As far as we know, they're not universal quantum computers.») y matiza cada término («that kind
  of formulation is Popper's, not mine»). En español: frases limpias, sin intensificadores que él no pone.
  Si dice *Yes.* o *Exactly.* al empezar, fúndelo con lo que sigue: *Sí. Tenemos lo necesario para…*.
- **Humor deadpan**: «Go home and take a couple of aspirin», «Give me a body, or I will sue», los
  «snailiens». Que se note la broma por la frase, no por un adorno.
- **Ejemplos marca de la casa**: la botella de champán en la nevera del laboratorio, el escarabajo bombardero,
  la hoguera, el principio de precaución que se refuta a sí mismo, el solipsista que sueña al hombre del traje
  amarillo. Si un término suyo aparece en la tabla, va así siempre.
- Hace preguntas retóricas en serie («Why Tuesday? Why not Wednesday?»): cada una con su ¿, y pueden ir
  solas.

---

## 2. Términos clave: inglés → español fijo para todo el grupo

No hay episodio aprobado de esta serie, así que todos son propuesta de este brief. Los marcados **[G]** salen de
GLOSARIO.md y son obligatorios. La edición española de *The Beginning of Infinity* (Biblioteca Buridán, 2012,
trad. de Josep Sarret Grau) existe, pero no he podido consultar su texto; donde la terminología estándar en
español es clara (epistemología popperiana, física) la sigo, y donde no lo es, lo digo.

### Epistemología (Popper y Deutsch)

| Inglés | Español fijo | Fuente o motivo |
|---|---|---|
| good explanation / bad explanation | buena explicación / mala explicación | Concepto central; es «buenas y malas explicaciones» en la descripción de la editorial de la edición española (Polifemo) |
| hard to vary / easy to vary | difícil de variar / fácil de variar | Literal y transparente; la reseña en inglés lo define como explicación que no se puede modificar sin dejar de explicar. «Difícil de modificar» se aceptaría, pero fija **variar** porque Naval y Deutsch juegan con *vary/variant* |
| reach (de una explicación) / to reach | alcance / alcanzar | «Explanations that reach the entire universe» → *explicaciones que alcanzan a todo el universo* |
| universal explainer(s) | explicador universal / explicadores universales | Neologismo calcado del de Deutsch, es el único que conserva el concepto; el TTS lo lee bien. Ver D2 |
| explanatory creativity | creatividad explicativa | Literal |
| knowledge creation / to create knowledge | creación de conocimiento / crear conocimiento | |
| knowledge-bearing entity | una entidad que porta conocimiento | |
| conjecture / conjectural / bold conjectures | conjetura / conjetural / conjeturas audaces | Término de Popper (*Conjeturas y refutaciones*) |
| guess (sustantivo, sentido epistemológico) / creative guess | conjetura / conjetura creativa | Fijo para que «todo conocimiento es conjetural» y «everything is a guess» suenen a lo mismo. El verbo *to guess* va según el contexto: *conjeturar*, *suponer* o *adivinar* («You'll never guess» → *Nunca lo adivinarías*) |
| criticism / to criticize | crítica / criticar | |
| criticize-ability | que se pueda criticar / la posibilidad de criticarla | «Criticabilidad» existe pero se traba en voz alta; resuélvelo en la frase |
| immunize itself against criticism | blindarse contra la crítica | Más natural que «inmunizarse»; se entiende igual |
| refute / refutation | refutar / refutación | Popper |
| falsifiable / falsifiability / falsify | falsable / falsabilidad / falsar | Término estándar de la tradición popperiana en español. **No** «falsificable» (eso es falsificar un billete) |
| testable / testability / to test | comprobable / que se pueda comprobar / poner a prueba | Para el oyente lego, «comprobable» se entiende al instante; «contrastable» es el término académico de Tecnos y suena técnico. Ver D3 |
| crucial experiment / crucial test | experimento crucial | Término estándar |
| risky predictions / narrow predictions | predicciones arriesgadas / predicciones concretas | «Estrechas» es calco. *Narrowness* → *concreción*. *Narrow and precise* → *concretas y precisas* |
| sticking your neck out | arriesgarse, mojarse | Deutsch lo usa como sinónimo de *risky*: «mojarse» es la imagen española |
| error correction / error-correcting mechanism / to error-correct | corrección de errores / mecanismo de corrección de errores / corregir errores | |
| the means of error correction | los medios para corregir errores | «Don't destroy the means of error correction» → *No destruyas los medios para corregir errores* |
| fallible / fallibilism / fallibilist | falible / falibilismo / falibilista | |
| induction / inductivist | inducción / inductivista | |
| Bayesian / Bayesianism / Bayes' theorem | bayesiano / bayesianismo / teorema de Bayes | Estándar en estadística en español |
| update my priors | actualizar mis probabilidades previas | «Priors» no se deja en inglés |
| justified true belief | creencia verdadera justificada | Fórmula clásica de la epistemología en español |
| justify / justificationism | justificar / justificacionismo | |
| epistemology / theory of knowledge | epistemología / teoría del conocimiento | Naval los da como sinónimos; respeta cuál usa en cada frase |
| worldview | visión del mundo | No «cosmovisión», que suena solemne |
| mental models | modelos mentales | |
| the seen in terms of the unseen | lo visible a partir de lo invisible | «Explain the seen in terms of the unseen» → *explicar lo visible a partir de lo invisible* |
| problem situation | la situación del problema | Término de Popper; si suena raro, *el problema que había planteado* |
| mathematician's misconception | el error de concepto de los matemáticos | Término de Deutsch (cap. 8 del libro). Si el TTS lo atropella, *la idea equivocada de los matemáticos* |
| necessary truth | verdad necesaria | |
| proof / to prove / theorem / axiom | demostración / demostrar / teorema / axioma | En matemáticas es *demostrar*, no «probar» |
| settled (science, mathematics) / the science is settled | definitiva / la ciencia ya está zanjada | «No settled science, no settled mathematics» → *No hay ciencia definitiva, no hay matemáticas definitivas* |
| foundationalism | fundacionalismo | Término estándar de filosofía |
| anthropomorphic delusions | delirios antropomórficos | 133 [0] |
| self-refuting / refutes itself | que se refuta a sí misma | |
| taking theories seriously | tomarse en serio las teorías | 134, título de sección incluido |
| experiment / demonstration / measurement | experimento / demostración / medición | La distinción de Deutsch en 134 [5]. «Demostración» aquí es una demostración en clase, no matemática: si queda ambiguo, *una demostración práctica* |
| heuristic | heurístico | |

### Física, computación y biología

| Inglés | Español fijo | Fuente o motivo |
|---|---|---|
| quantum theory / quantum mechanics / quantum physics | teoría cuántica / mecánica cuántica / física cuántica | Respeta cuál usa |
| multiverse / universes | multiverso / universos | |
| many-worlds interpretation / Everettian / Everett interpretation | interpretación de los muchos mundos / everettiano / interpretación de Everett | Estándar |
| Copenhagen theorists | partidarios de la interpretación de Copenhague | |
| wave function (collapse) / unitary quantum mechanics | (colapso de la) función de onda / mecánica cuántica unitaria | |
| interference / entanglement | interferencia / entrelazamiento | |
| double-slit experiment / twin slit | experimento de la doble rendija | Los dos ingleses → lo mismo |
| particle-wave duality | dualidad onda-partícula | Sin guion en el texto: *dualidad onda partícula* (ver apartado 4) |
| photoelectric effect / interference pattern | efecto fotoeléctrico / patrón de interferencia | |
| general relativity / theory of relativity | relatividad general / teoría de la relatividad | |
| space-time | espacio tiempo | Sin guion para el TTS |
| standard model / string theory / gauge bosons | modelo estándar / teoría de cuerdas / bosones gauge | Apuntar *gauge* para escucha |
| Planck length / time / mass | longitud de Planck / tiempo de Planck / masa de Planck | |
| discrete / continuous / infinitely divisible | discreto / continuo / infinitamente divisible | |
| nonlocality / locality | no localidad / localidad | |
| quantum computer / quantum computation | ordenador cuántico / computación cuántica | «Ordenador», por el criterio de vocabulario de España del GLOSARIO |
| universal computer | ordenador universal | Deutsch: «They're universal computers» → *Son ordenadores universales* |
| theory of computation / computable | teoría de la computación / computable | |
| Church-Turing(-Deutsch) principle | principio de Church Turing (Deutsch) | Sin guiones; ver apartado 4 |
| constructor theory | teoría de constructores | Muy Interesante, en su extracto de *La ciencia de lo posible* de Marletto, usa «teoría de los constructores»; vale cualquiera de las dos, pero fija una: **teoría de constructores** |
| compute power / computational power | potencia de cálculo | |
| AGI / artificial general intelligence | inteligencia artificial general | Nunca la sigla. Después de la primera mención puede bastar *una inteligencia general* |
| AI / narrow AI | inteligencia artificial / inteligencia artificial limitada | |
| pattern matching | reconocimiento de patrones | |
| evolution by natural selection | evolución por selección natural | |
| genetic / memetic evolution; meme | evolución genética / memética; meme | |
| selfish gene | gen egoísta | Dawkins, *El gen egoísta* (Salvat) |
| Neo-Darwinist / Darwinian | neodarwinista / darwinista | |
| unit of selection / fit / fitness | unidad de selección / apto / aptitud | |
| convergent feature of evolution | rasgo convergente de la evolución | |
| evolutionary algorithms | algoritmos evolutivos | |
| single-cell / multicellular | unicelular / pluricelular | |
| latent heat / escape velocity / kinetic energy | calor latente / velocidad de escape / energía cinética | |
| Fermi paradox | paradoja de Fermi | |
| Dark Forest Hypothesis | hipótesis del bosque oscuro | Prensa en español (National Geographic, DW); viene de *El bosque oscuro* de Liu Cixin |
| Dyson spheres | esferas de Dyson | |
| simulation hypothesis | hipótesis de la simulación | |
| Rare Earth (la hipótesis) | la hipótesis de la Tierra rara | Así la llama Miquel Barceló en la revista *Universo* |
| cosmological principle | principio cosmológico | |
| observable universe | universo observable | |
| aliens / alien species | extraterrestres / una especie extraterrestre | «Alienígenas» solo en el juego de palabras de los snailiens (ver D5) |

### Sociedad, optimismo y recursos

| Inglés | Español fijo | Fuente o motivo |
|---|---|---|
| rational optimism / optimist | optimismo racional / optimista | Ridley, *El optimista racional* (Taurus, 2011) |
| pessimism is self-fulfilling | el pesimismo se cumple a sí mismo | |
| doomsayers / Cassandras / Malthusians | agoreros / casandras / maltusianos | |
| risk of ruin / go to zero | riesgo de ruina / quedarse a cero, perderlo todo | |
| ergodic reasoning / ensemble | razonamiento ergódico / el conjunto | Taleb |
| resources / finite resources | recursos / recursos finitos | |
| wealth **[G]** | riqueza | Deutsch la define como «el conjunto de transformaciones físicas que podemos llevar a cabo» |
| physical transformations that we can affect | transformaciones físicas que podemos llevar a cabo | *affect* es errata por *effect*: tradúcelo por el sentido |
| sustainability / spaceship Earth | sostenibilidad / la nave espacial Tierra | |
| precautionary principle | principio de precaución | |
| natalism | natalismo | |
| feedback / feedback from reality / feedback loop | retroalimentación / la retroalimentación de la realidad / bucle de retroalimentación | Fija **retroalimentación**. No hay precedente aprobado; ver propuestas de glosario |
| free markets | mercados libres | |
| credibility stamps / credibility capital | sellos de credibilidad / capital de credibilidad | |
| Schelling point / coordination point | punto de Schelling / punto de coordinación | |
| groupthink | pensamiento de grupo | |
| decentralization / centralization | descentralización / centralización | |
| frontier | frontera | En el sentido del Salvaje Oeste |
| regulatory capture | captura regulatoria | |
| compromise (sustantivo) | término medio / solución de compromiso | En España «compromiso» suele ser *commitment*: no lo dejes solo. Ver D6 |
| strong opinions, loosely held | opiniones fuertes, sostenidas con poca fuerza | Ver D7 |
| for-profit / non-profit | empresa con ánimo de lucro / entidad sin ánimo de lucro | |
| diminishing marginal utility | utilidad marginal decreciente | |
| crypto / cryptocurrencies | cripto / criptomonedas | [051] |
| smart contracts / coins fork | contratos inteligentes / las monedas se bifurcan | |
| social sciences / natural sciences | ciencias sociales / ciencias naturales | |
| Enlightenment | la Ilustración | |
| judgment **[G]** | criterio | Solo el sustantivo *judgment*. «Make a judgment on France» → *juzgar a Francia*; «judge one explanation against another» → *comparar una explicación con otra* |

---

## 3. Libros, obras y textos citados

Comprobado en al menos una fuente (catálogo de biblioteca o ficha de editorial o librería) cuando digo «edición
española». Todos van **sin comillas ni cursiva** en el texto del TTS.

| Obra citada | En el texto español | Fuente / decisión |
|---|---|---|
| *The Beginning of Infinity* (Deutsch, 2011) | **El comienzo del infinito** | Biblioteca Buridán, Barcelona, 2012, trad. de Josep Sarret Grau, ISBN 978-84-15216-75-9 (registro de catálogo; ficha de Marcial Pons y Polifemo). Subtítulo: *Explicaciones que transforman el mundo* |
| *The Fabric of Reality* (Deutsch, 1997) | **La estructura de la realidad** | Anagrama, col. Argumentos, trad. de David Sempau, 1999 (catálogo SIIDCA; reedición de 2002) |
| *Objective Knowledge: An Evolutionary Approach* (Popper) | **Conocimiento objetivo**, con su subtítulo *un enfoque evolucionista* | Tecnos, Madrid, 1974, trad. de Carlos Solís Santos. 109 [4] dice que «está subtitulado An Evolutionary Approach»: *Popper tiene un libro titulado Conocimiento objetivo, con el subtítulo Un enfoque evolucionista.* |
| *Conjectures and Refutations* (Popper) | Conjeturas y refutaciones | Paidós, trad. de Néstor Míguez. No se cita por título, pero es la fuente de «In our infinite ignorance we are all equal» |
| *The Poverty of Historicism* (Popper), aludido en 124 *The Poverty of Compromise* | La miseria del historicismo | Taurus, 1961, y Alianza, trad. de Pedro Schwartz. Por eso propongo *La miseria del término medio* para el título (D6) |
| *Unended Quest* (Popper), origen de «It is impossible to speak in such a way that you cannot be misunderstood» | Búsqueda sin término | Tecnos, 1977. No se nombra; la cita va en estilo indirecto |
| *Gödel, Escher, Bach* (Hofstadter) | **Gödel, Escher, Bach** | Tusquets (col. Metatemas), con el subtítulo *Un eterno y grácil bucle*. Basta el título corto. Ver la pronunciación en el apartado 4 |
| *The Wealth of Nations* (Adam Smith) | La riqueza de las naciones | Título clásico en español |
| *The Selfish Gene* (Dawkins), como idea | la idea del gen egoísta | Salvat, *El gen egoísta. Las bases biológicas de nuestra conducta* |
| *Genome* (Ridley) | Genoma | Taurus, *Genoma. La autobiografía de una especie en 23 capítulos* (Lecturalia; catálogo) |
| *The Rational Optimist* (Ridley) | El optimista racional | Taurus, 2011, ISBN 978-84-306-0810-2 |
| El libro de Ridley sobre innovación (134 [3], sin título) | no se nombra | Es *How Innovation Works* (2020); no he encontrado edición española. No hace falta nombrarlo |
| *Rare Earth* (Ward y Brownlee, 2000) | **un libro de Peter Ward y Donald Brownlee, Rare Earth, sobre la hipótesis de la Tierra rara** | **Sin edición española** (solo inglés y alemán en las búsquedas). El TTS leerá mal *Rare Earth*: recomendado *Hay un libro de Peter Ward y Donald Brownlee sobre la llamada hipótesis de la Tierra rara.* Ver D8 |
| *The Hitchhiker's Guide to the Galaxy* (Adams) | Guía del autoestopista galáctico | Anagrama. «The Vogons… hyperspace bypass» → *los vogones demolían la Tierra para hacer sitio a una vía de circunvalación hiperespacial* |
| *Principia* (Newton) | los Principia de Newton | Título latino, se dice así en español |
| *Elements* (Euclid) | los Elementos de Euclides | |
| *The Black Swan* (Taleb), como idea | el cisne negro | Paidós, 2008, *El cisne negro. El impacto de lo altamente improbable* |
| *Planet of the Apes* (la hipótesis de Lineweaver) | la hipótesis de El planeta de los simios | Título español de la película |
| *The Empire Strikes Back* | la fase de El Imperio contraataca | Título español de la película |
| *Catch-22* (133 [10]) | la pescadilla que se muerde la cola | La novela se tituló *Trampa 22* en español, pero como expresión no se usa en España. Ver D9 |
| «Let's Make a Deal» (concurso de Monty Hall, 100 [4]) | un concurso de la televisión estadounidense | El título en inglés lo lee mal el TTS y no aporta |
| Charla TED de Deutsch «Chemical Scum That Dream of Distant Quasars» (133 [1]) | una charla que se titula algo así como Escoria química que sueña con quásares lejanos | **No he encontrado título español oficial** (la única charla de Deutsch con título español localizado es otra, de 2019). Se traduce el título y se marca con «algo así como»; nota en `notas` con el original |
| «Theory of Knowledge-Cast» (ToKCast) | el podcast de la teoría del conocimiento | Ver apartado 4 |
| Nullius in verba (lema de la Royal Society) | nulius in verba, el lema de la Royal Society, que significa no te fíes de la palabra de nadie | Ver apartado 4 y T6 |
| Taking Children Seriously (TCS) | la filosofía de tomarse en serio a los niños | No hay nombre español asentado; traducido y sin sigla. Primera mención: *la filosofía Taking Children Seriously, es decir, tomarse en serio a los niños* si el TTS lo lee bien; si no, solo la traducción |

---

## 4. Nombres propios y siglas para el TTS

Los nombres no se traducen. Esta lista va a `notas` de cada episodio donde salgan, para escucharlos antes de
sintetizar.

**Formas españolas asentadas (se escriben así):** Platón, Demócrito (el inglés trae «Democrates», errata),
Zenón (paradoja de Zenón), Euclides, Perséfone, Hades, Zeus, Júpiter, Nike, Galileo, Lamarck, Darwin, Kepler,
Newton. **Acción de Gracias** por *Thanksgiving*. **Reino Unido** por *the U.K.*. **Australia Occidental** por
*Western Australia*. **la Estación Espacial Internacional**, **el Proyecto Manhattan**, **Silicon Valley**,
**Wall Street**, **el Salvaje Oeste**.

**Nombres que pueden sonar mal (escuchar):**

| Nombre | Riesgo | Recomendación |
|---|---|---|
| Deutsch | Puede salir «de-utch» o «deuch» | Se escribe Deutsch. Si suena mal, en el texto del TTS «Doich» (decisión del autor) |
| David Deutsch | — | La primera vez en cada episodio, nombre completo |
| Popper, popperiano | Bien | |
| Bayes, bayesiano, bayesianismo | El TTS lee «ba-yes»: es como se dice en español | |
| Everett, everettiano | «Éverett» | Escuchar |
| Feynman | Puede leer «feinman» | Escuchar |
| Gödel | La ö puede saltarse o deletrearse | Escuchar; si falla, «Gódel» |
| Hofstadter, Escher, Bach | Hofstadter es difícil | Escuchar |
| Hawking | «Jóquin» suele salir bien | |
| Eddington, Cavendish, Christopher Wren | | Escuchar |
| Chaitin, Solomonoff | | Escuchar |
| Hugh Everett | «Hugh» suele salir mal | *Hugh Everett*; si falla, solo «Everett» con la fecha |
| Thomas Young | | |
| Charley Lineweaver | Difícil | Escuchar |
| Neil deGrasse Tyson | Difícil | Escuchar |
| Vaidman, Semmelweis, Lister, Olbers | | Escuchar. «Olber's paradox» es errata por *Olbers*: *la paradoja de Olbers* |
| Chiara (Marletto) | «Kiara» | Deutsch dice solo «Chiara»: déjalo así y aclara en `notas` que es Chiara Marletto |
| Shor (algoritmo de Shor) | | |
| Church Turing Deutsch | Los guiones pueden leerse | *el principio de Church Turing* / *el principio de Church Turing Deutsch*, sin guiones |
| Rory Sutherland, Paul Graham, Marc Andreessen, Steve Jobs, Warren Buffett, Charlie Munger, Nassim Taleb, Adam Smith, Thomas Edison, Nikola Tesla, Enrico Fermi, Christian Dior, Matt Ridley, Monty Hall, Stephen Hawking, Richard Dawkins, Thomas Kuhn | | Escuchar los de pronunciación inglesa |
| Y Combinator | La Y suelta | *Y Combinator, la aceleradora de startups*; escuchar |
| Royal Society | Inglés | Se deja así; escuchar. Alternativa: *la Real Sociedad de Londres* |
| OpenAI | «open a i» | Escuchar |
| Twitter, Facebook, Patreon, Amazon, Shopify, DoorDash, Roblox, iPad, YouTube | Marcas | Sin tocar; escuchar Patreon y DoorDash |
| ITV (129 *caveman*) | Sigla | *la cadena británica ITV*; si se deletrea mal, *una cadena de televisión británica* y el nombre a `notas` |
| ToKCast | La mezcla de mayúsculas | Se escribe *Tokcast* y se explica: *su podcast, Tokcast, que viene de podcast de la teoría del conocimiento* |
| @illacertus (076 *read*) | La arroba se vocaliza | *un usuario de Twitter que se hace llamar ilacertus*, sin arroba |

**Siglas y cifras resueltas en la frase:**

| Original | En el texto | Nota |
|---|---|---|
| AGI | inteligencia artificial general | Nunca la sigla |
| AI | inteligencia artificial | «IA» se deletrea |
| GPT-3 | GPT tres | El TTS español suele decir «ge pe te». Si deletrea mal, *el modelo de lenguaje GPT tres de OpenAI* o *ge pe te tres*. Escuchar |
| DALL·E, Stable Diffusion | Dall E, Stable Diffusion | El punto medio es un símbolo: fuera. Escuchar |
| TCS | tomarse en serio a los niños | |
| DNA | ADN **[G]** | |
| PhD / PhDs | doctorado / doctores | «One Einstein is worth a legion of PhD drones» → *doctores autómatas* |
| GDP / GDP per citizen | el PIB / la renta por habitante | El TTS lee «pib» como palabra, que es como se dice en España. Escuchar |
| MP | diputado | |
| VR / VR space | realidad virtual | |
| 3D printing | impresión en tres dimensiones | |
| LCD screens | pantallas de cristal líquido | |
| ETH (130 *failure*) | Ethereum | |
| TED Talk | una charla TED | |
| U.K. / U.S. | el Reino Unido / Estados Unidos | |
| x plus zero must equal x | equis más cero tiene que ser igual a equis | |
| person A / idea X / theory Z (124 *compromise*) | la persona A, la idea equis, la idea i griega, la teoría zeta | Las letras sueltas el TTS las lee como preposición o las deletrea mal (GLOSARIO, 063 y 065). Ver D10 |
| °C | grados | «20°C to 30°C» → *de veinte a treinta grados* |
| kg | kilo | «1 kg» → *un kilo*; «1.1 kg» → *un kilo cien*; «1.2» → *un kilo doscientos* |
| 1/10^100 | uno entre un uno seguido de cien ceros | 116 *existence*. Ver T8 |

---

## 5. Trampas previsibles y solución

**T1. Artefactos del copiado en el inglés (no se tocan, se traduce por el sentido y se apuntan en `notas`).**
Restos de enlaces de nav.al que se colaron en el texto:

- 080 *predict* [1]: «doomsayers, Cassandras), and…»: paréntesis suelto.
- 091 *probability* [3]: «A measure) is a way…»: paréntesis suelto. *Una medida es una forma de hablar de infinitos.*
- 089 *substrate* [0]: «You run the infinite series) and sum it»: paréntesis suelto.
- 117 *program* [0]: «evolutionary algorithms%2C,mutation%2C%20recombination%2C%20and%20selection.)»: basura de URL.
  Se traduce solo *algoritmos evolutivos*.
- 118 *far-away* [0]: «Rare Earth),»: paréntesis suelto.
- 122 *credibility* [0]: «Schelling point#:~:text=In%20game…(1960).)»: basura de URL. Solo *punto de Schelling*.

Erratas evidentes del transcript, que se traducen por el sentido:

- 088 *discrete* [0]: «Democrates» → Demócrito.
- 089 *substrate* [1]: «transverse an infinite number of points» → *recorrer* (es *traverse*).
- 086 *methods* [0]: «quarks are fundamental and electrons and fundamental» → *y los electrones también*.
- 086 *methods* [0]: «So, too in mathematics.» frase sin verbo → *Lo mismo pasa en las matemáticas.*
- 092 *light* [1]: «Young came along and shined a line through two slits» → *hizo pasar luz por dos rendijas*.
  Mismo bloque: «interfere with one other» → *interfieren entre sí*.
- 108 *gravity* [0]: «what I would call species of scientism» → *una especie de cientificismo*.
- 121 *einstein* [0]: «bachelor of engineers» → *ingenieros*.
- 126 *social* [0]: «an harmonious» → *una sociedad armoniosa*.
- 083 *vary* [4]: «starlight gets bent around an eclipse» → *la luz de las estrellas se curva durante un eclipse*.
- 133 [10]: «physical transformations that we can affect» → *llevar a cabo*.
- 133 [24]: «It increased its stat us» → *su estatus*.
- 134 [0]: «lying on the same chairs» → *tumbados en hamacas* (antes ha dicho *sun chairs*).
- 134 [1]: «tells you to go to fallible and anti-authoritarianism» → *te lleva al falibilismo y al antiautoritarismo*.
- 134 [3]: «variation of selection» → *variación y selección*.
- 134 [11]: «it's a particle in a wave at the same time» → *es una partícula y una onda a la vez*.
- 134 [15]: «coverture of space-time» → *curvatura del espacio tiempo*; «Olber's paradox» → *paradoja de Olbers*.
- 103 *pessimism* [1]: «doomsayer podcasts about enders blowing up the Earth». Es su conversación de 2019 con Rob
  Reid en *After On* («End Games»), sobre riesgo existencial. *Enders* parece el término de esa conversación
  para quien podría acabar con el mundo: *uno de esos podcasts catastrofistas sobre gente capaz de hacer
  saltar la Tierra por los aires*. Duda en `notas`.

**T2. Insertos del editor entre corchetes (solo en 134).** Se integran sin corchetes y se explican en `notas`:
[0] «[They think] what we're trying to achieve…» → *Creen que lo que intentamos conseguir…*; [5] «[showed]
you can measure the constant» → *demostró que se puede medir la constante*; [15] «it can [also] make
ellipses»; [17] «[Doctors] didn't just reject a theory» → *Los médicos no solo rechazaron una teoría*; [25]
«social change [and] economic change»; [26] «I don't think this is doable, [but]…».

**T3. El 134 [5] empieza a media conversación.** «When you do this experiment with the acid and base…»
remite a un experimento del que no hay rastro antes: la página recortó la conversación. Se traduce tal cual
(*Cuando haces este experimento con el ácido y la base…*) y se explica en `notas`. No inventes el contexto.

**T4. Mil millones y billones.** *Billion* = mil millones; *trillion* = billón. En el grupo: 080 *predict*
«hundred billion galaxies» (cien mil millones de galaxias); 095 *expand* «hundreds of billions of stars»
(cientos de miles de millones); 114 *aliens* «200 billion… 400 billion… 200 to 300 billion» (doscientos mil
millones… cuatrocientos mil millones… entre doscientos mil y trescientos mil millones); 116 *existence*
«trillions of planets» (billones de planetas); 115 *intelligent* «three and a half billion years», «two and a
half billion years» (tres mil quinientos millones de años, dos mil quinientos millones de años); 133 [5]
«billions and billions of species» (miles y miles de millones de especies).

**T5. Cifras frecuentes, todas en letra:** veintitrés grados (083); un kilo, un kilo cien, un kilo doscientos
(083); de veinte a treinta grados, diez grados más cada minuto, mil grados, unos cien grados (097); cien
puertas, noventa y ocho de las noventa y nueve restantes, una entre cien, noventa y nueve entre cien (100);
mil novecientos diecinueve (108); los años cincuenta, mil novecientos cincuenta y cinco (092, 133); el siglo
veinte (099); hace sesenta años (128); el veinte por ciento (123); diez frente a cincuenta mil, con un cien por
cien de eficacia (121); sesenta explicaciones por hora (133); doscientos cincuenta y seis errores seguidos, la
mitad de la velocidad de la luz, el noventa y nueve por ciento de la velocidad de la luz (134); los años
treinta (134); un niño de seis años (134); de cero a uno (121). «20 years ago» → *hace veinte años*.

**T6. Nullius in verba (074).** Lema latino: se mantiene porque es el título del episodio y Naval lo traduce
él mismo. Para el TTS, **nulius in verba** con una sola ele (con dos, el TTS español lo lee «nuyius»): *Me
encanta el viejo lema de la Royal Society, nulius in verba, que significa no te fíes de la palabra de nadie.*
El título del episodio sí se escribe bien: *Nullius in verba*. La grafía del TTS va a `notas`.

**T7. Citas en estilo directo: sin comillas.** Hay muchísimas: Einstein, «God does not play dice with the
universe» → *Dios no juega a los dados con el universo*, con verbo introductorio y coma; Planck, «Science
advances one funeral at a time» → *la ciencia avanza de funeral en funeral*; Popper, «In our infinite ignorance
we are all equal» → *en nuestra infinita ignorancia, todos somos iguales*; Deutsch, «If you can't program it,
you haven't understood it» → *si no puedes programarlo, no lo has entendido*; Feynman, «If you think you
understand quantum theory, you don't understand quantum theory» → *si crees que entiendes la teoría cuántica,
es que no la entiendes*; los libertarios de Texas, «Two hands, one mouth» → *dos manos, una boca*;
«born as a particle, lives as a wave, dies as a particle» → *nace como partícula, vive como onda y muere como
partícula*; «The Englishman's home is his castle» → *la casa de un inglés es su castillo*; Andreessen (ver D7);
Sutherland, «Marketing is the science of knowing what economists are wrong about» → *el marketing es la ciencia
de saber en qué se equivocan los economistas*; Hawking, «chemical scum…» (ver T9).
Los diálogos imaginados de Naval y Brett («And I would say, "Yes, it is."») se pasan a estilo indirecto o se
cortan en frases con el verbo delante: *Yo les diría que sí. Y ellos me preguntarían cómo lo sé.* Las preguntas
pueden ir en estilo directo sin comillas: *¿Cómo lo sabes?*.

**T8. La cadena de probabilidades de 116 *existence*.** «one in 10, times one in 10, times one in 10…100 times.
This is one over 10, all to the power of 100—which is one over one followed by 100 zeroes.» Sin símbolos ni
puntos suspensivos: *Uno entre diez, por uno entre diez, por uno entre diez, así cien veces. Es uno entre diez
elevado a cien, es decir, uno entre un uno seguido de cien ceros.*

**T9. Hawking (080 *predict*).** «The human race is just a chemical scum on a moderate-sized planet, orbiting
around a very average star in the outer suburb of one among a hundred billion galaxies.» No he encontrado una
traducción española asentada de la cita. Recomendado: *Stephen Hawking dijo una vez que la raza humana no es
más que escoria química en un planeta de tamaño mediano, que gira alrededor de una estrella muy corriente en las
afueras de una galaxia entre cien mil millones.* Y en frase aparte: *Dijo que somos tan insignificantes que no
podía creer que todo el universo existiera para nuestro beneficio.* La misma «escoria química» en la charla TED
del 133 [1].

**T10. Juegos de palabras y frases hechas** (decisión aplicada; las que marcan la serie están en el apartado 6):
- 078 *knowledge* «Problems are solvable, or "soluble," as he writes» → *Los problemas tienen solución, son solubles,
  como escribe él.* «Soluble» en ese sentido existe en español (RAE: «que se puede resolver»): el guiño funciona.
- 088 *discrete* «It's particles all the way down, to paraphrase Feynman» (la frase original es la de las tortugas) →
  *Son partículas y más partículas hasta el fondo, por parafrasear a Feynman.*
- 103 «sounds a little bit kumbaya» → *suena un poco a buenismo*.
- 098 el pavo de Acción de Gracias: *Hasta que llega el día de Acción de Gracias, y se lleva un buen susto.*
- 072/105 «"believe in science"—which is an oxymoron» → *cuando nos dicen que hay que creer en la ciencia, que
  es un oxímoron*.
- 121 «Creativity goes zero to one» → *La creatividad va de cero a uno.*
- 123 «Steve Jobs… and people like him wouldn't last a day…»: los puntos suspensivos fuera; *Paul Graham tuiteó
  algo así como que Steve Jobs y la gente como él no durarían ni un día dentro de las empresas que ellos mismos
  crearon.*
- 134 [17] «when Christian Dior says, "Put up your hemline,"» → *cuando Christian Dior decía que había que subir
  el bajo de la falda* (sin imperativo plural).
- 076 *read*: «I started reading it, and I started reading it, and I started reading it»: la repetición es la gracia, mantenla: *empecé a leerlo, y empecé
  a leerlo, y empecé a leerlo.*

**T11. Vosotros escondido.** Brett da instrucciones al oyente («Anyone might want to try this experiment for
themselves: Take a piece of paper…»): tú singular. Naval a varios: «we're hoping to break it down for you» →
*esperamos desmenuzártelo*. Deutsch, 133 [41]: «OK guys, you can stop now… You can all go home» → aquí sí habla
a un grupo de empresas: pásalo a tercera persona o impersonal: *Les dirías a esas empresas que ya pueden parar,
que es un ordenador y es cuántico, que se pueden ir a casa, que ya lo han conseguido.*

**T12. Conceptos que en español se confunden.**
- *Prove* (matemáticas) = **demostrar**; *test* (ciencia) = **comprobar o poner a prueba**. Nunca «probar un
  teorema».
- *Demonstration* (134) = demostración práctica, no matemática. En el 134 [5] di *demostración* la primera vez
  con «práctica» si hay riesgo de confusión.
- *Experiment* frente a *measurement* frente a *demonstration* (134 [5] y [6]): mantén los tres términos fijos,
  Naval los resume justo después.
- *Explanation* frente a *prediction* (097): no los intercambies por variar.
- *Resource* frente a *wealth*: recurso y riqueza, nunca «bienes».
- *Knowledge* siempre *conocimiento* (singular), salvo «a piece of knowledge» → *un conocimiento*.
- *Information* frente a *knowledge* (081, 134 [26]): información y conocimiento, distintos a propósito.
- *Theory of everything / final theory*: *teoría definitiva*, no «teoría final».
- *Universe* frente a *multiverse* frente a *universes*: con el plural, Brett habla de universos paralelos
  dentro del multiverso.

**T13. Bloques de una sola frase corta.** Varios cortos tienen bloques mínimos: 083 *vary* [2] «Right. Or you need
a different kind of grass.» y [3]; 076 *read* [1] «And the audio version.»; 100 *theories* [1]; 134 [28] «No shortcuts.»,
[29] y [31] «Yes.». Son la única frase del bloque: se dejan solos. *Exacto. O necesitas otro tipo
de hierba.* va junto en una sola frase.

**T14. Deutsch corrige a Naval (133 [38] a [41]).** Naval dice «universal quantum computers» y Deutsch le corrige:
«universal computers… not universal quantum computers». La corrección tiene que oírse: *Ordenadores universales.
Hasta donde sabemos, no son ordenadores cuánticos universales.* No lo «arregles» en la pregunta de Naval.

**T15. Atribuciones dudosas que hay que dejar como están.** 099 «I think it was Planck who said» (lo dijo Planck,
en paráfrasis): *Creo que fue Planck quien dijo*. 083 «I believe in relativity it was Eddington»: *creo que fue
Eddington*. 118 «I think Stephen Hawking said»: *creo que Stephen Hawking dijo*. Las dudas son del hablante:
consérvalas.

---

## 6. Decisiones que propongo (aplicar la recomendada y describirla en `decisiones`)

**D1. Recopilaciones (105, 130): reutilizar el español de los cortos sin cambiar nada.** Alternativa: traducir de
nuevo. Coste: incoherencia y doble trabajo de revisión, y se pierde la opción de reutilizar los clips.

**D2. *Universal explainer* → explicador universal.** Alternativas: *explicador universal* (recomendada, una
palabra por concepto, calca un término que Deutsch acuñó); *ser capaz de explicarlo todo* (natural, pero larga y
pierde que es un término técnico que se repite en diez episodios); *explicadores universales* con glosa la
primera vez en cada episodio (*capaces de explicar cualquier cosa que se pueda explicar*). Coste de la
recomendada: neologismo; se compensa porque el contexto lo define siempre.

**D3. *Testable* → comprobable.** Alternativas: *contrastable* (término académico de las traducciones de Popper en
Tecnos; exacto, pero el oyente lego no lo entiende a la primera); *verificable* (incorrecto en Popper, que
precisamente niega la verificación). *Falsifiable* sí va con su término técnico, *falsable*, porque no tiene
alternativa llana y Naval lo usa como término de Popper.

**D4. Título 113 *It's Mind Blowing That Our Minds Can't Be Blown*.** Recomendada: *Lo alucinante es que nada
puede alucinarnos*. La frase dentro (130 [9]): «the mind-blowing thing here is that your mind cannot be blown»
→ *lo alucinante es que nada puede alucinarte*. Conserva la repetición, que es el chiste. Alternativas: *Lo que
te vuela la cabeza es que nada puede volarte la cabeza* (más fiel a la imagen, más coloquial y larga); *Lo
asombroso es que nuestra mente no tiene límites* (clara, pero pierde el juego).

**D5. *Snailiens* (133 [11]).** Deutsch inventa una palabra, caracol más alienígena. Recomendada:
*caracolienígenas*: conserva el invento y se entiende. Alternativas: *unos alienígenas con forma de caracol*
(clara, pierde la broma); *snailiens* (el TTS lo destroza). Escuchar.

**D6. *Compromise* y el título 124 *The Poverty of Compromise*.** Recomendada: título *La miseria del término
medio*, que conserva el guiño a *La miseria del historicismo* de Popper; en el texto, *término medio* o *solución
de compromiso* según la frase, nunca *compromiso* a secas (en España se entiende *commitment*). Alternativa: *La
pobreza del compromiso* (calco, y ambiguo).

**D7. *Strong opinions, loosely held* (124/125, Andreessen).** Las cuatro combinaciones de Naval tienen que
quedar paralelas: *opiniones fuertes, sostenidas con poca fuerza*; *opiniones fuertes sostenidas con fuerza*;
*opiniones débiles sostenidas con poca fuerza*. Alternativa: *opiniones firmes, pero sin aferrarse a ellas*
(más natural para la fórmula suelta, pero no permite el juego de las cuatro combinaciones).

**D8. *Rare Earth* (118 *far-away*), libro sin edición española.** Recomendada: nombrar autores y la hipótesis
sin el título inglés. Alternativa: *un libro titulado Rare Earth* (fiel, pero el TTS lo lee mal y el oyente no
lo entiende). El título original va a `notas`.

**D9. *Catch-22* (133 [10]).** Recomendada: *la pescadilla que se muerde la cola*. Alternativa: *una trampa
veintidós*, el título español de la novela (casi nadie lo usa en España como expresión).

**D10. Letras sueltas en el ejemplo del término medio (124).** «person A has idea X and person B has idea Y…
theory Z». Recomendada: *una persona tiene una idea y otra persona tiene otra; el término medio es una tercera
idea a medio camino*; luego, *la primera*, *la segunda*, *la tercera*. Sigue el criterio del GLOSARIO para «A
come a B» (063). Alternativa: *la idea equis, la idea i griega, la idea zeta*: fiel, pero el TTS puede leer «y»
como conjunción y el oyente se pierde. Lo mismo en 127 *failure* «We thought A, but the answer's actually B» →
*Pensábamos una cosa, pero la respuesta era otra*.

**D11. *One Einstein is worth a legion of PhD drones* (121).** Recomendada: *Un Einstein vale más que una legión
de doctores autómatas*. Alternativa: *de doctores que solo repiten*.

---

## 7. Títulos propuestos de los cortos (se copian tal cual a los `titulos_seccion` de 105 y 130)

| Nº | Inglés | Español |
|---|---|---|
| 072 | Science Is the Engine That Pulls Humanity Forward | La ciencia es el motor que hace avanzar a la humanidad |
| 073 | This Book Changed the Way I Think | Este libro cambió mi forma de pensar |
| 074 | Nullius in Verba | Nullius in verba |
| 075 | Explanations That Reach the Entire Universe | Explicaciones que alcanzan a todo el universo |
| 076 | Read the Best 100 Books Over and Over Again | Lee los cien mejores libros una y otra vez |
| 078 | We're at the Beginning of an Infinity of Knowledge | Estamos al comienzo de un infinito de conocimiento |
| 079 | People Are a Force of Nature | Las personas son una fuerza de la naturaleza |
| 080 | It's Impossible to Predict the Growth of Knowledge | Es imposible predecir el crecimiento del conocimiento |
| 081 | Humans Are Unique in Our Ability to Understand Things | Los humanos somos únicos en nuestra capacidad de entender |
| 082 | Good Explanations Are Acts of Creativity | Las buenas explicaciones son actos de creatividad |
| 083 | Good Explanations Are Hard to Vary | Las buenas explicaciones son difíciles de variar |
| 084 | There Is No End of Science | La ciencia no tiene fin |
| 085 | There Is No Settled Mathematics | No existen unas matemáticas definitivas |
| 086 | The Methods of Mathematics Are Fallible | Los métodos de las matemáticas son falibles |
| 087 | All Knowledge Is Conjectural | Todo conocimiento es conjetural |
| 088 | Is the Universe Discrete or Continuous? | ¿El universo es discreto o continuo? |
| 089 | Every Theory Is Held Inside a Physical Substrate | Toda teoría reside en un sustrato físico |
| 090 | We Can't Prove Most Theorems with Known Physics | Con la física que conocemos no podemos demostrar la mayoría de los teoremas |
| 091 | Probability Is Subjective | La probabilidad es subjetiva |
| 092 | Is Light a Particle or a Wave? | ¿La luz es una partícula o una onda? |
| 093 | The Multiverse | El multiverso |
| 094 | We Explain the Seen in Terms of the Unseen | Explicamos lo visible a partir de lo invisible |
| 095 | Science Expands Our Vision of Reality | La ciencia amplía nuestra visión de la realidad |
| 096 | Science Is an Error-Correcting Mechanism | La ciencia es un mecanismo de corrección de errores |
| 097 | Theories Are Explanations, Not Predictions | Las teorías son explicaciones, no predicciones |
| 098 | Make Bold Guesses and Weed Out the Failures | Haz conjeturas audaces y descarta las que fallen |
| 099 | Science Advances One Funeral at a Time | La ciencia avanza de funeral en funeral |
| 100 | It's Rare to Have Competing, Viable, Scientific Theories | Es raro tener teorías científicas viables que compitan entre sí |
| 101 | We're All Equal in Our Infinite Ignorance | En nuestra infinita ignorancia, todos somos iguales |
| 102 | It's Easy to Extrapolate How Things Will Get Worse | Es fácil extrapolar cómo empeorarán las cosas |
| 103 | Pessimism Seems Like an Intellectually Serious Position | El pesimismo parece una postura intelectualmente seria |
| 104 | Rational Optimism Is the Way Out | El optimismo racional es la salida |
| 105 | The Beginning of Infinity, Part 1 | El comienzo del infinito, primera parte |
| 106 | With a Good Theory of Knowledge, You Can Decide What Else Is True | Con una buena teoría del conocimiento, puedes decidir qué más es verdad |
| 107 | No Truth Can Be Justified | Ninguna verdad puede justificarse |
| 108 | There Can Be No Final Theory of Gravity | No puede haber una teoría definitiva de la gravedad |
| 109 | Genetic Evolution Was a Prelude to Memetic Evolution | La evolución genética fue el preludio de la evolución memética |
| 110 | Humans Are Exceptional | Los humanos somos excepcionales |
| 111 | We Are Qualitatively Different From Other Species | Somos cualitativamente distintos de las demás especies |
| 112 | More Compute Power Doesn't Produce AGI | Más potencia de cálculo no produce una inteligencia artificial general |
| 113 | It's Mind Blowing That Our Minds Can't Be Blown | Lo alucinante es que nada puede alucinarnos (D4) |
| 114 | Where Are the Aliens? | ¿Dónde están los extraterrestres? |
| 115 | Intelligent Species Have Risen Only Once on Planet Earth | Las especies inteligentes solo han surgido una vez en la Tierra |
| 116 | The Probability of Human Existence Is Infinitesimally Small | La probabilidad de que existamos es infinitesimal |
| 117 | If You Can't Program It, You Haven't Understood It | Si no puedes programarlo, no lo has entendido |
| 118 | Aliens Might Just Be Too Far Away | Quizá los extraterrestres simplemente estén demasiado lejos |
| 119 | Aliens Would Visit for Knowledge, Not Resources | Los extraterrestres vendrían por el conocimiento, no por los recursos |
| 120 | Ideas Are the New Oil | Las ideas son el nuevo petróleo |
| 121 | One Einstein Is Worth A Legion Of PhD Drones | Un Einstein vale más que una legión de doctores autómatas |
| 122 | Don't Rely on Credibility Stamps | No te fíes de los sellos de credibilidad |
| 123 | Innovation Requires Decentralization and a Frontier | La innovación necesita descentralización y una frontera |
| 124 | The Poverty of Compromise | La miseria del término medio (D6) |
| 125 | Free Markets Provide the Best Feedback | Los mercados libres dan la mejor retroalimentación |
| 126 | Making Something Social Destroys the Truth of It | Hacer algo social destruye su verdad |
| 127 | Groups Never Admit Failure | Los grupos nunca admiten el fracaso |
| 128 | Knowledge Makes the Existence of Resources Infinite | El conocimiento hace infinita la existencia de recursos |
| 129 | To a Caveman Very Few Things Are Resources | Para un cavernícola, casi nada es un recurso |
| 130 | The Beginning of Infinity, Part 2 | El comienzo del infinito, segunda parte |
| 133 | David Deutsch: Knowledge Creation and The Human Race, Part 1 | David Deutsch: la creación de conocimiento y la especie humana, primera parte |
| 134 | David Deutsch: Knowledge Creation and The Human Race, Part 2 | David Deutsch: la creación de conocimiento y la especie humana, segunda parte |

Los `titulo_seccion` de los cortos los decide quien traduce cada uno, con dos reglas: se copian igual en la
recopilación, y los que son media frase en inglés (086 «Even if the subject matter is not», 127 «You get a schism
instead») se completan para que se entiendan solos (*Aunque su objeto de estudio no lo sea*; *En su lugar, se
produce un cisma*).

---

## 7 bis. Párrafo de ejemplo (083 *vary*, bloque [4], Naval; en la 105, bloque [22])

Inglés (308 palabras), troceado del español frase a frase. Ratio es/en: 322/308 = 1,05.

1. La segunda pieza de una buena explicación es que es difícil de variar.
2. Tiene que ser muy precisa, y esa precisión tiene que tener una buena razón de ser.
3. El ejemplo famoso de El comienzo del infinito es la explicación de por qué tenemos estaciones.
4. Está la antigua explicación griega, según la cual dependen de Perséfone, la diosa de la primavera, y de cuándo puede salir del Hades.
5. Era toda una teoría de dioses y diosas, y no solo no era fácil de comprobar, sino que era muy fácil de variar.
6. Perséfone podría haber sido Nike, y Hades podría haber sido Júpiter o Zeus.
7. Es muy fácil variar esa explicación sin que cambien sus predicciones.
8. En cambio, fíjate en la teoría de la inclinación del eje.
9. Dice que la Tierra está inclinada veintitrés grados respecto al Sol, y que por eso el sol debería salir por aquí en invierno y por allí en verano.
10. Los hechos de esa teoría son muy difíciles de variar, y hace predicciones arriesgadas y concretas.
11. La teoría de la inclinación del eje puede predecir cuánto duran exactamente el verano y el invierno en cada latitud, y eso se puede comprobar con precisión.
12. Además de ser una teoría creativa, comprobable y falsable, debería ser difícil variar sus piezas sin destruir la teoría por completo.
13. Y lo que desde luego no quieres es variarla a posteriori, como en tu ejemplo de la hierba.
14. ¿Que no bastaba con un kilo? Pues ahora es un kilo cien, y luego un kilo doscientos.
15. Por último, las predicciones que hace deberían ser concretas y precisas, y deberían ser arriesgadas.
16. Por ejemplo, en el caso de la relatividad, creo que fue Eddington quien hizo el experimento y demostró que la luz de las estrellas se curva durante un eclipse.
17. Era una predicción que Einstein había hecho con la relatividad, y resultó ser cierta.
18. Fue una predicción arriesgada que tardó mucho tiempo en confirmarse.

Qué muestra: términos fijos (*difícil de variar*, *comprobable*, *falsable*, *predicciones arriesgadas y
concretas*); cifras y unidades en letra; la cita inventada de la hierba en estilo directo sin comillas, como
pregunta con su ¿; la frase larga del inglés con raya partida en tres (8, 9 y 10) y cada una con sentido propio;
la duda del hablante («I believe… it was Eddington») conservada; la errata «around an eclipse» resuelta por el
sentido y apuntada en `notas`. Frases de 10 a 29 palabras.

`notas` de este bloque: «around an eclipse» se traduce *durante un eclipse*. Nombres a escuchar: Perséfone,
Nike, Eddington.

---

## Propuestas para GLOSARIO.md

Para la tabla de **Términos**:

| Inglés | Español | Nota |
|---|---|---|
| good explanation / hard to vary | buena explicación / difícil de variar | Deutsch; fijo en toda la serie de 2021 y en 133 y 134 |
| reach | alcance | De una explicación |
| universal explainer | explicador universal | Deutsch (D2) |
| conjecture / guess (epistemológico) | conjetura | Popper |
| falsifiable | falsable | Nunca «falsificable» |
| testable | comprobable | Más llano que «contrastable» (D3) |
| error correction | corrección de errores | |
| AGI | inteligencia artificial general | Nunca la sigla |
| feedback | retroalimentación | Primera vez en el repo; afecta también al grupo de Matt Ridley |
| compromise (sustantivo) | término medio / solución de compromiso | «Compromiso» a secas es *commitment* (D6) |
| aliens | extraterrestres | |
| prove (matemáticas) / test (ciencia) | demostrar / comprobar | |

Para **Siglas y títulos**:

| Original | En el texto | Nota |
|---|---|---|
| The Beginning of Infinity | El comienzo del infinito | Biblioteca Buridán, 2012 |
| The Fabric of Reality | La estructura de la realidad | Anagrama, 1999 |
| Nullius in verba | nulius in verba | Una sola ele en el texto del TTS para que no lea «nuyius» (074) |
| GPT-3 | GPT tres | Escuchar; alternativa *ge pe te tres* |
| Church-Turing | Church Turing | Sin guion |
| person A, idea X | una persona, una idea, la otra | Letras sueltas resueltas en la frase, como en 063 (124) |
| ToKCast | Tokcast | Con su explicación la primera vez |

---

## Fuentes consultadas

Internas: GLOSARIO.md; docs/revision-episodios.md; docs/traduccion.md; docs/hablantes.md; trabajo/plan.json;
trabajo/f0/ de los 60 episodios del grupo; trabajo/f5/ de 053 a 067; trabajo/briefs/naval_nivi.md.

Externas (búsquedas del 4-nov-2026; la consulta directa de goodreads.com y descubridor.academia.cl está bloqueada
desde esta sesión, así que los datos de esas fichas vienen de los resúmenes del buscador):
- El comienzo del infinito, Biblioteca Buridán, trad. Josep Sarret Grau: https://descubridor.academia.cl/Record/DIGBURIDAN0009/Description ; https://www.marcialpons.es/libros/el-comienzo-del-infinito/9788415216759/ ; https://www.polifemo.com/libros/el-comienzo-del-infinito-explicaciones-que-transforman-el-mundo/125134/
- La estructura de la realidad, Anagrama, trad. David Sempau: https://catalogosiidca.csuca.org/Record/UCR.000098341/Description
- Popper en español: https://www.casadellibro.com.co/libro-conocimiento-objetivo/9788430904884/379676 ; https://www.planetadelibros.com/libro-conjeturas-y-refutaciones/19258 ; https://alianzaeditorial.es/primer_capitulo/la-miseria-del-historicismo.pdf ; https://www.marcialpons.es/libros/busqueda-sin-termino/9788430945306/
- Gödel, Escher, Bach (Tusquets): https://www.marcialpons.es/libros/godel-escher-bach/9788483830246/
- Ridley: https://www.lecturalia.com/libro/58738/genoma ; ficha de Taurus de El optimista racional vía https://www.goodreads.com/work/editions/10684114-the-rational-optimist-how-prosperity-evolves
- Rare Earth sin edición española: https://biblio.es/obra/rare-earth-por-ward-peter-d/3986783 ; hipótesis de la Tierra rara en español: https://core.ac.uk/download/185530851.pdf
- Marletto, teoría de los constructores: https://muyinteresante.okdiario.com/?p=532222
- El bosque oscuro: https://openlibrary.org/books/OL27935191M ; https://www.nationalgeographicla.com/ciencia/2024/08/y-si-los-extraterrestres-existen-pero-se-esconden-de-nosotros-conoce-que-dice-la-teoria-del-bosque-oscuro
- Guía del autoestopista galáctico (Anagrama): https://www.casadellibro.com.co/libro-guia-del-autoestopista-galactico/9788433912473/289729
- El cisne negro (Paidós): https://www.planetadelibros.com/libro-el-cisne-negro/395365
- El gen egoísta (Salvat): https://quelibroleo.com/el-gen-egoista-las-bases-biologicas-de-nuestra-conducta
- Brett Hall y ToKCast: https://podcasts.apple.com/us/podcast/feed/id1447087694 ; https://doexplain.buzzsprout.com/1260167/8455182 ; https://substack.com/@bretthall
- Charla TED de Deutsch de 2005: https://www.ted.com/talks/quick-list?page=177
- Taking Children Seriously: https://takingchildrenseriously.com/what-is-taking-children-seriously/
- Naval y Rob Reid, After On 44 «End Games»: https://pocketcasts.com/podcast/the-ars-technicast/438646c0-73c4-012f-1e11-525400c11844/ars-technicast-experimental-133-rob-reid-and-naval-ravikant-3-of-4/d8ce54c5-c40e-4a0c-9d7e-c31afd7eaf6d
