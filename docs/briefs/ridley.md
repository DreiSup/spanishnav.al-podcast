# Brief del grupo «Matt Ridley»

> **Aviso (7-nov):** el autor decidió los términos de la serie el 7-nov. Están en GLOSARIO.md, sección Matt Ridley, y donde chocan con este brief manda el GLOSARIO (gobernantes, sacerdotes y ladrones, decidido el 9-nov tras pasar por jefes; Cómo funciona la innovación; inmunidad de rebaño; cuarentena y el covid; obreros y oficinistas; los siglos oscuros; nombres en forma fonética).

Para traductores y revisores de los dos episodios con Matt Ridley, grabados en 2020 a raíz de su libro
*How Innovation Works*:

| Nº | Slug | Título inglés | Fecha | Bloques | Palabras en | Partes (`trabajo/plan.json`) |
|---|---|---|---|---|---|---|
| **070** | `matt-ridley` | Matt Ridley: How Innovation Works, Part 1 | 2020-07-09 | 21 | 5.453 | p1 = b01–b14, p2 = b15–b21 |
| **071** | `matt-ridley-2` | Matt Ridley: How Innovation Works, Part 2 | 2020-07-15 | 40 | 5.767 | p1 = b01–b12, p2 = b13–b24, p3 = b25–b40 |

Los bloques se citan como **bNN**, contando desde uno en el orden del f0. Son los ids que pondrá el
normalizador y coinciden con el campo `n` de `trabajo/partes_en/*.json`.

Preparado el 4-nov-2026. Fuentes internas: GLOSARIO.md, docs/revision-episodios.md, docs/traduccion.md,
docs/hablantes.md, fabrica/voces.json y los episodios aprobados 051, 052 y 053 a 067. Fuentes externas al
final. Desde esta sesión solo funcionó la búsqueda web. La lectura directa de páginas (WebFetch) estaba
bloqueada por la red, así que los datos editoriales vienen de fichas de catálogo y de reseñas que salían en
los resultados de búsqueda. Cuando un dato no lo he podido confirmar, lo digo.

Hay términos que aparecen en las cinco partes y que, por tanto, ninguna parte puede decidir por su cuenta:
**invención e innovación**, **gobernantes, sacerdotes y ladrones**, **la gallina de los huevos de oro**,
**los títulos de los libros de Ridley**, **cripto y cadena de bloques**, **de arriba abajo y de abajo arriba**,
**la teoría del gran hombre** y **hija de la libertad y madre de la prosperidad**.

---

## 1. Quiénes hablan y cómo suena cada uno

`speaker` se copia **exacto** del inglés, que aquí es `Naval` y `Matt`. La fábrica resuelve `Matt` a la voz
`ridley` (alias en `fabrica/voces.json`: invitado menor, sin LoRA). No lo cambies a «Matt Ridley».

**Ojo en 071:** b26 y b27 son dos bloques seguidos de Naval. El primero acaba en la privacidad digital y el
segundo abre el tema de la automatización. Se mantienen los dos, uno a uno, aunque no haya cambio de hablante.

### Matt Ridley

Matthew White Ridley, nacido en 1958. Se doctoró en Zoología en Oxford en 1983 y trabajó en *The Economist*
como editor de ciencia y después como corresponsal en Washington. Es vizconde y fue par conservador en la
Cámara de los Lores de 2013 a 2021. De 2004 a 2007 presidió el banco Northern Rock, y salió de ahí tras la
primera retirada masiva de depósitos de un banco británico en siglo y medio. Lo cuenta él mismo en 071 b40
con modestia: no soy innovador, no he montado ningún negocio, soy escritor.

Ideas que vertebran su obra y que salen en esta conversación:

- **La innovación es evolutiva, gradual y colectiva.** La hacen equipos, no genios solitarios. Por eso
  distingue invención de innovación.
- **El optimismo racional**: el progreso sale del intercambio y de la especialización.
- **El orden espontáneo**: nadie dirige el sistema y aun así funciona. Es el ejemplo del almuerzo de
  Londres en 071 b09.
- **La libertad como condición de la innovación**: «la innovación es hija de la libertad y madre de la
  prosperidad».
- **Lo que mata la innovación** son los gobernantes, los sacerdotes y los ladrones, la regulación y el
  ecologismo planetario.

**Cómo habla.** Es inglés de clase alta, culto y comedido. Construye frases largas y bien hiladas, matiza
mucho y practica el *understatement* británico. Tiene muletillas que hay que reconocer y no calcar:

| Inglés | Qué hace | Cómo trasladarlo |
|---|---|---|
| *if you like* («chiefs, priests and thieves, if you like») | Rebaja una fórmula que sabe que es suya | **por así decirlo**, **si se quiere**. Puede omitirse si en español sobra. Nunca «si te gusta» |
| *as it were* | Igual que la anterior | **por así decirlo** |
| *I reckon* | Opinión prudente | **diría yo**, **creo** |
| *funny enough* | Corrige con humor | **curiosamente** |
| *quite*, *surprisingly*, *on the whole* | Gradúa | **bastante**, **sorprendentemente**, **en general**. No los multipliques |
| *It wasn't a pretty sight* | Ironía británica | **y no fue nada bonito** |
| *I stand corrected* | Fórmula cortés | **acepto la corrección** |
| *I'm a bit of a fraud* | Autoironía | **soy un poco impostor** |

Registro en español: un punto más formal y culto que Naval, pero sin rigidez. Tutea a Naval, que lo trata de
Matt, así que se tutean. Nunca usted. Parte sus frases largas por el punto natural, que suele ser un *and*,
un *which* o un punto y coma, sin perder los matices.

### Naval

Es la misma voz que en 053-067: frases cortas y afirmativas, cercano pero no coloquial. Aquí está
**entusiasmado** y lleva el peso de la conversación. Suelta monólogos larguísimos (070 b17 tiene 671 palabras
y 070 b21 tiene 1.033), encadena **listas de sustantivos** («code, capital, media, labor, intelligence») y usa
jerga de Silicon Valley (*VC*, *early adopters*, *network effect*, *hype cycle*, *green shoots*). Sus
muletillas son *obviously*, *of course*, *by the way* y *that said*: tradúcelas con **obviamente**,
**por supuesto**, **por cierto** y **dicho esto**, y quita alguna si en español se amontonan. Muchas de sus
frases empiezan por *There's this…* o *This is…*: no lo calques con «Hay este…».

Las listas sin verbo hay que **verbalizarlas** para que cada frase se entienda leída sola. Por ejemplo,
«Se apalancan con el código, el capital, los medios, el trabajo y la inteligencia».

Coherencia con el corpus aprobado, comprobada en `episodios/*/transcript.es.json`: **startup**,
**capital riesgo**, **efecto de red**, **cripto**, **apalancamiento**, **tuit**, **Silicon Valley**, **riesgo a la baja**.

---

## 2. Términos clave, fijos para todo el grupo

| Inglés | Español fijo | Fuente o motivo |
|---|---|---|
| invention / innovation | **invención / innovación** | Es la distinción central de Ridley (070 b07-b08). Nunca «inventiva». *Innovator* = innovador, *inventor* = inventor |
| *innovation is the child of freedom and the parent of prosperity* | **la innovación es hija de la libertad y madre de la prosperidad** | Así la cita la prensa en español (El Comercio). «Madre de» es idiomático. Vale para 070 b05, 071 b39 y los `titulo_seccion` |
| *innovation famine / feast* | **hambruna de innovación / festín de innovación** | 071 b01. Conserva el contraste |
| *chiefs, priests and thieves* | **gobernantes, sacerdotes y ladrones** | 070 b18-b21. «Jefes» suena a jefe de trabajo. Ver §6, decisión 2 |
| *golden goose / the goose that lays the golden eggs* | **la gallina de los huevos de oro** | 070 b15 y b20. Es un modismo español exacto. «Matar la gallina de los huevos de oro» |
| *rational optimism / optimist* | **optimismo racional / optimista racional** | Título de la edición de Taurus |
| *great man theory of history* | **la teoría del gran hombre** | Término asentado (Carlyle). 071 b35 dice *great man or great woman theory*: **la teoría del gran hombre o la gran mujer** |
| *trial and error* | **ensayo y error** | Término asentado |
| *evolutionary process / breakthrough process* | **proceso evolutivo / proceso de grandes avances** | 070 b11 |
| *spontaneous order / disorder* | **orden espontáneo / desorden espontáneo** | Término de Hayek. El juego de 070 b20 funciona igual |
| *top-down / bottom-up (bottoms-up)* | **de arriba abajo / de abajo arriba** | Forma española. Nunca «top-down» |
| *command and control* | **de ordeno y mando** | Modismo español. «Un ecologismo global de ordeno y mando» (070 b21) |
| *environmentalism / environmental movement / conservation movement* | **ecologismo / movimiento ecologista / movimiento conservacionista** | 070 b21 y 071 b01-b03 |
| *network effect* | **efecto de red** | Corpus aprobado (052) |
| *venture capital / VC* | **capital riesgo / un inversor de capital riesgo** | Corpus aprobado. La sigla VC se resuelve en la frase |
| *early adopters* | **los primeros en adoptarla** o **los primeros clientes** | Según la frase |
| *critical mass* | **masa crítica** | |
| *leveraged / most leveraged people* | **apalancado / las personas con más apalancamiento** | GLOSARIO |
| *deadweight loss* | **pérdida irrecuperable** | Término económico. «Una pérdida irrecuperable enorme para la sociedad» |
| *zero-sum game* | **juego de suma cero** | |
| *the cloud* | **la nube** | |
| *crypto* | **cripto** | Corpus aprobado. *Cryptoland* = **el mundo cripto** |
| *blockchain* | **cadena de bloques** | Fundéu. El TTS la lee sin problema. Ver §6, decisión 4 |
| *decentralized finance* | **finanzas descentralizadas** | |
| *smart contracts* | **contratos inteligentes** | |
| *tokens* | **tokens** | Sin equivalente asentado. Ver §6, decisión 4 |
| *hype cycle / hype bubble* | **ciclo de euforia / burbuja de euforia** | |
| *green shoots* | **brotes verdes** | Modismo español exacto |
| *plumbing (infrastructure)* | **la fontanería de internet** | Uso habitual en tecnología en España |
| *Byzantine generals problem* | **el problema de los generales bizantinos** | Término asentado |
| *Spaceship Earth* | **la nave espacial Tierra** | Fuller. *Blue marble* = **la canica azul**, que es como se conoce la foto en español |
| *universal explainers* | **explicadores universales** | Término de Deutsch. No he podido verificar la forma de la edición española de *El comienzo del infinito*: coordínalo con el grupo Brett-Deutsch |
| *lockdown* | **confinamiento** | Uso de España en 2020 |
| *herd immunity* | **inmunidad de grupo** | El diccionario médico de la CUN recoge «de grupo», «colectiva» y «de rebaño». «De rebaño» es calco. Ver §6, decisión 5 |
| *flatten / crush the curve* | **aplanar / aplastar la curva** | Conserva el juego (071 b10 y b16) |
| *social distancing* | **distanciamiento social**; *safe distance* = **distancia de seguridad** | |
| *super-spreaders* | **supercontagiadores** | |
| *infection fatality rate* | **la tasa de letalidad de la infección** | |
| *reproductive rate* | **la tasa de reproducción del virus** | |
| *care homes* | **residencias de mayores** | |
| *filter bubble / echo chambers* | **burbuja de filtros / cámaras de eco** | Ver §6, decisión 6 |
| *Amara's Law* | **la ley de Amara** | |
| *Gell-Mann Amnesia* | **la amnesia de Gell-Mann** | Crichton, 2002 |
| *availability bias* | **sesgo de disponibilidad** | |
| *monopoly on violence* | **monopolio de la violencia** | |
| *GMOs* | **organismos modificados genéticamente**, o **transgénicos** si se repite | 071 b01 |
| *genome editing* | **edición genómica** | |
| *billion* | **mil millones** | NUNCA «billón». *8 or 9 billion people* = **ocho o nueve mil millones de personas** |
| *GDP* | **producto interior bruto** | La sigla se resuelve en la frase |
| *AI / AGI* | **inteligencia artificial / inteligencia artificial general** | Naval ya desarrolla la sigla. Sin siglas |
| *machine learning* | **aprendizaje automático** | |
| *think tanks* | **laboratorios de ideas** | Evita el anglicismo, que el TTS lee mal |
| *big box retailers* | **las grandes superficies** | Uso de España |
| *blue collar / white collar* | **trabajadores manuales / trabajadores de oficina** | Evita «cuello azul / cuello blanco», que suenan a calco |

Modismos que tienen equivalente español exacto. Úsalo:

| Inglés | Español |
|---|---|
| *ideas are a dime a dozen* | las ideas abundan, no valen nada |
| *standing on the shoulders of giants* | a hombros de gigantes |
| *pay lip service* | de boquilla |
| *cast in iron* | grabado en piedra |
| *lose their shirt* | dejarse hasta la camisa |
| *history is written by the victors / to the victor go the spoils* | la historia la escriben los vencedores / al vencedor, el botín |
| *history doesn't repeat, it rhymes* | la historia no se repite, pero rima |
| *the right magic soup* | el caldo de cultivo adecuado |
| *lose its mojo* | perder la chispa |
| *as a wag might say* | como diría un bromista |
| *the oil reservoir that will always be gushing* | el yacimiento de petróleo que nunca deja de manar |
| *keep the show on the road* | mantener la función en marcha, o mantener viva la llama |
| *Soviet-style glop rations* | raciones de rancho al estilo soviético |
| *the mushy middle* | un centro templado y sin aristas |
| *a long run on Broadway* | una temporada muy larga en cartel en Broadway |

---

## 3. Libros y obras citados

| Original | En el texto español | Edición española y verificación |
|---|---|---|
| *Genome* (1999) | **Genoma** | *Genoma. La autobiografía de una especie en 23 capítulos*, Taurus. Las fichas dan 2000 o 2001. Confirmado en Lecturalia, es-academic y un librero (Hamelyn, ISBN 9788430604142) |
| *The Rational Optimist* (2010) | **El optimista racional** | *El optimista racional. ¿Tiene límites la capacidad de progreso de la especie humana?*, Taurus, 2011 (ISBN 9788430608102). Confirmado en Quelibroleo, Marcial Pons y Lecturalia |
| *How Innovation Works* (2020) | **Claves de la innovación** | Antoni Bosch editor, Barcelona, 2021, traducción de Dulcinea Otero-Piñeiro (impreso 9788412176513, ebook 9788412176520). Confirmado en el catálogo de la Universidad Arturo Prat (Chile) y en la reseña de *Economía Industrial* del Ministerio de Industria. Se usa siempre este título, aunque saliera después del podcast |
| *The Agile Gene* | **Qué nos hace humanos** | *The Agile Gene* es el título de la edición estadounidense en rústica de *Nature via Nurture* (2003). En español es *Qué nos hace humanos*, Taurus, 2004, traducción de Teresa Carretero e Irene Cifuentes, confirmado en catálogos CSUCA y AbeBooks (ISBN 9788430605422). Que sean el mismo libro lo sé por mi cuenta, no por una fuente consultada. Ver §6, decisión 3 |
| *The Red Queen* (1993) | **La reina roja** | **No he encontrado edición española.** Los títulos que circulan son traducciones informales. Se traduce porque la «hipótesis de la Reina Roja» (Van Valen) es como se conoce el concepto en español. Ver §6, decisión 3 |
| *The Origins of Virtue* (1996) | **El origen de la virtud** | **Edición española no verificada.** Una fuente académica la cita como *Los orígenes de la virtud*, sin editorial ni año. Ver §6, decisión 3 |
| *The Evolution of Everything* (2015) | **La evolución de todo** | **No he encontrado edición española.** Traducción literal. Ver §6, decisión 3 |
| *I, Pencil*, de Leonard Read (1958) | **Yo, el lápiz** | Ensayo con traducciones españolas que circulan con este título (FEE). BBC Mundo usa *Yo, lápiz*. Se elige *Yo, el lápiz*, que se entiende mejor al oído |
| *Second Nature*, de Haim Ofek (Cambridge University Press, 2001) | **Segunda naturaleza** | **Sin edición española.** El TTS no lee bien el título inglés. Se traduce y va a `notas`: «Second Nature: Economic Origins of Human Evolution, sin traducción al español» |
| *The Beginning of Infinity*, de Deutsch (no se nombra, pero se alude en 071 b02) | **El comienzo del infinito** | Biblioteca Buridán, Barcelona, 2012, traducción de Josep Sarret Grau. Confirmado en descubridor.academia.cl y en Marcial Pons. *We're always at the beginning of this infinity, as he says* = **siempre estamos en el comienzo del infinito, como dice él**. Conviene que suene al título |
| Yuval Noah Harari (solo el nombre, 071 b06) | — | Para contexto: *Sapiens* es *De animales a dioses*, Debate, 2014 |
| *filter bubble* (Eli Pariser) | ver §6, decisión 6 | *El filtro burbuja*, Taurus, 2017 |
| *Operating Manual for Spaceship Earth* (Fuller) | solo la metáfora | No he encontrado edición española. Solo sale la expresión |

---

## 4. Nombres propios y siglas para el TTS

Los nombres no se traducen. Esta lista es para escucharlos antes de sintetizar: apunta en `notas` los que
salgan en tu parte.

**Personas que el TTS puede leer mal**

| Nombre | Dónde | Riesgo y forma recomendada |
|---|---|---|
| **Cecil Salmon** | 070 b12 | **Puede leerlo «salmón», como el pez.** Escríbelo tal cual y escúchalo. Si falla, la alternativa fonética es «Cecil Sálmon» |
| **Haim Ofek** | 071 b32 | La H española es muda, así que dirá «Aim». Pronunciación hebrea: «Jaím». Escríbelo tal cual y escúchalo |
| **Gell-Mann** | 071 b37 | El guion corto no está en la lista de signos vetados, pero escúchalo. Si se vocaliza o se traba, escribe **Gell Mann** |
| **Leibniz**, **Voltaire**, **Gutenberg**, **Fibonacci** | 070 b11, 071 b03, 070 b16, 070 b20 | Nombres asentados en español. Escúchalos |
| **Charles Townes** | 070 b08 | El inglés dice *Towns*, que es error del copiado (ver §5). Se pronuncia igual |
| **Burton Bayles** | 070 b12 | El inglés dice *Bales*, que también es error del copiado. Se pronuncia igual |
| **Orville Vogel**, **Gonjiro Inazuka**, **Norman Borlaug**, **Douglas MacArthur** | 070 b12 | Escúchalos. Borlaug se acentúa en la primera sílaba |
| **M. S. Swaminathan** | 070 b12 | Con iniciales sueltas el TTS dirá «eme ese». Recomiendo **el genetista indio Swaminathan**, sin iniciales, que no quitan contenido. Va a `notas` |
| **John Constable** | 070 b06 | Amigo de Ridley, analista de energía, no el pintor. No hace falta aclararlo en el texto |
| **Mark Lynas**, **Paul Romer**, **Yuval Noah Harari**, **Leonard Read**, **David Deutsch** | 071 | Escúchalos |
| **Brian Chesky**, **Mark Zuckerberg**, **Jonathan Abrams**, **Satoshi Nakamoto**, **Elon Musk** | 070-071 | Escúchalos |
| **Bernard of Clairvaux** | 070 b20 | Forma española asentada: **Bernardo de Claraval** |
| **Martin Luther** | 071 b19 | Forma española asentada: **Martín Lutero** |
| **Leonardo DaVinci** | 071 b36 | **Leonardo da Vinci** |
| **Oliver and Wilbur Wright** | 070 b11 | **Orville y Wilbur Wright**. Ver §5 |

**Empresas y marcas**

| Original | En el texto | Nota |
|---|---|---|
| Pets.com | **Pets punto com** | El TTS lee el punto como pausa o lo vocaliza |
| *dot-com bubble* | **la burbuja puntocom** | Fundéu |
| VRBO | **Vrbo** | La empresa se pronuncia «verbo». Escúchalo. Si lo deletrea, escribe **Verbo** y apúntalo en notas |
| eBay India | **eBay en la India** | Escucha cómo dice «eBay» |
| DoorDash, Instacart, Postmates, Webvan, Kozmo, Airbnb, Myspace, Friendster, HomeAway, Couchsurfing, Craigslist, Facebook, Twitter, Amazon, Apple, Google | tal cual | Escúchalos |
| Bitcoin, Ethereum | **Bitcoin**, **Ethereum** | El corpus aprobado usa «Bitcoin». Fundéu propone «bitcóin» para la moneda, pero aquí se nombra el sistema |
| Sand Hill Road | **el modelo de capital riesgo de Sand Hill Road** | Escúchalo. Si se traba: **el modelo de capital riesgo de Silicon Valley**, y lo apuntas en notas |

**Lugares**

| Original | En el texto |
|---|---|
| Bay area | **la zona de la bahía de San Francisco** la primera vez, después **la bahía** |
| Mumbai / Bangalore / Delhi / Shanghai | **Bombay** (Fundéu), **Bangalore**, **Delhi**, **Shanghái** |
| Oregon | **Oregón** |
| Taiwan / Singapore / New Zealand / Switzerland | **Taiwán / Singapur / Nueva Zelanda / Suiza** |
| the low countries | **los Países Bajos** |
| Victorian Britain / Renaissance Italy / ancient Greece | **la Gran Bretaña victoriana / la Italia del Renacimiento / la antigua Grecia** |
| Fujian China / Ganges Valley | **la provincia china de Fujian / el valle del Ganges** |
| Song dynasty / Ming China / Abbasid Arabia | **la dinastía Song / la China de los Ming / la Arabia abasí** |
| Hoover Dam | **la presa Hoover** |
| Magna Carta | **la Carta Magna** |
| Mona Lisa | **la Gioconda** (uso de España) |

**Siglas, que se resuelven en la frase**

| Original | En el texto |
|---|---|
| VC (070 b13) | **un inversor de capital riesgo** |
| STEM (070 b21) | **las ciencias, la tecnología, la ingeniería y las matemáticas** |
| GDP (071 b22) | **producto interior bruto**. Dilo una vez y no lo repitas: «…por el veinte por ciento del producto interior bruto de Estados Unidos se hará por el uno por ciento en el mundo cripto» |
| NSA (071 b26, dos veces) | **la Agencia de Seguridad Nacional** la primera vez, después **esa agencia** o **los servicios de inteligencia** |
| AI / AGI (071 b26-b27) | **inteligencia artificial / inteligencia artificial general** |
| U.K. / U.S. | **el Reino Unido / Estados Unidos** |
| COVID, Covid-19 | **la covid** o **la pandemia**. Nunca «diecinueve» en cifra. *Covid-19 land* = **hoy, en plena pandemia** |
| CRISPR (071 b01) | **crísper**, como se pronuncia, con tilde para fijar el acento. Va a `notas` para escucharlo |

---

## 5. Trampas previsibles y solución

### 5.1. Errores del copiado en el inglés

El inglés no se toca. Se traduce lo que se dijo y cada error va a `notas`.

| Bloque | Inglés | Qué es | Qué haces en español |
|---|---|---|---|
| 070 b01 | «And most recently,¶¶Matt wrote…» | Salto de párrafo a mitad de frase | Una sola frase continua |
| 070 b08 | «a new social practice innovation» | Sobra una palabra | **una nueva práctica social** |
| 070 b11 | «Oliver and Wilbur Wright» | Es Orville | **Orville y Wilbur Wright**. Ver §6, decisión 1 |
| 070 b11 | «I see the evolutionary process eternally» | Probablemente *internally*, desde dentro | **lo veo desde dentro, como un proceso evolutivo, y no como una sucesión de grandes avances** |
| 070 b12 | «Burton Bales» | Es Burton Bayles | **Bayles**. Se pronuncia igual |
| 070 b08 | «Charles Towns» | Es Charles Townes | **Townes**. Se pronuncia igual |
| 070 b14 | «the harbor process» | Es el **proceso de Haber** (Haber-Bosch), que fija el nitrógeno del aire | **el proceso de Haber** |
| 070 b14 | «won;t» | Errata | Sin efecto |
| 070 b17 | «moved the cloud» / «attractive to live» sin punto / «contract laws» | Faltan *to*, el punto y *contract law* | **se mudaran a la nube**, frase cerrada, **derecho contractual** |
| 070 b20 | «Europes», «very, restrictive» | Erratas | Sin efecto |
| 070 b21 | «not an integration destination» | Es *immigration* | **no es un destino de inmigración** |
| 071 b05 | «Leonard Reed», «I Pencil», «contributed to its manufacturer» | Leonard Read, *I, Pencil*, *manufacture* | **Leonard Read**, **Yo, el lápiz**, **contribuyeron a fabricarlo** |
| 071 b08 | «converging and whatever political bias» | Es *converging on* | **acaban coincidiendo, como por milagro, con el sesgo político que…** |
| 071 b13 | «things. but» | Errata | Sin efecto |
| 071 b14 | «it’ infects», «vaccine immediate herd immunity» | Es *vaccine-mediated* | **la inmunidad de grupo por vacuna** |
| 071 b16 | «filter bubble/silo», «Journalists serve all taken sides» | Barra, y *have all taken sides* | **atrapado en su burbuja, en su silo**, **los periodistas han tomado partido todos** |
| 071 b21 | Acaba en coma: «…if government ever allows it to, of course,» | Frase cortada | Ciérrala con punto |
| 071 b24 | «canon» | Es *cannon* | **el cañón** |
| 071 b26 | «So crypto the attacker can throw unlimited compute power at it» | Sintaxis rota | **Con la criptografía, el atacante puede lanzar toda la potencia de cálculo que quiera…** |
| 071 b31 | «you democratize consumption, where not everybody can have access to everything» | Contradice la idea. Casi seguro es *now everybody can* | Traduce el sentido evidente: **democratizas el consumo, y ahora todo el mundo puede acceder a todo**. Va a `decisiones` |
| 071 b39 | «I highly recommend Genome as well, to figure out the rational basis behind ethics and the origin of virtue» | Naval mezcla *Genome* con *The Origins of Virtue* | Fiel: **Te recomiendo también Genoma, y para entender la base racional de la ética, el origen de la virtud**. Va a `notas` |

### 5.2. Insertos del editor y paréntesis

No hay `[Laughter]` ni corchetes. Hay un paréntesis en 071 b10: «(The best one would have been if we had
isolated and crushed the curve like Hong Kong and Taiwan did.)». **Intégralo sin paréntesis**: «No porque sea
necesariamente el mejor, el mejor habría sido aislarnos y aplastar la curva como hicieron Hong Kong y
Taiwán».

La nota del editor de nav.al («Naval interviews Matt Ridley, the author of The Red Queen and, recently, How
Innovation Works. Also see Part 2/1») **no se locuta**: va a `notas`, traducida. Las citas destacadas que se
quitaron de la página (en `plan.json`) tampoco.

### 5.3. Estilo directo y citas

Hay muchas comillas. Todas se resuelven en estilo indirecto, o en directo con verbo introductorio y coma:

- **070 b03**: las preguntas del emprendedor («Do I file patents? How important…?»). Hazlas indirectas:
  **cosas como si debes solicitar patentes, qué importancia tiene la ciencia, qué papel juega el gobierno…**
- **070 b06**: el diálogo con John Constable. En directo con coma: «Volvió y me dijo, el tema de fondo es la
  libertad, ¿te has dado cuenta? Y le contesté, pues no, no me había dado cuenta».
- **070 b08 y 071 b37**: el chiste del castor. Ver el párrafo de ejemplo (§7). En 071 b37 Naval le da la
  vuelta: el pobre Jonathan Abrams es el castor que mira la presa y dice, **¿de quién es esta presa?**
- **070 b12**: la cita de Ridley sobre Borlaug («If you then jump back… and say, “Yes, but he didn’t persuade
  India single-handedly. He talked to M.S. Swaminathan…”»). La cita se cierra al final del párrafo, pero
  todo es la voz de Ridley. Pásala a indirecto: **si vuelves a Borlaug, ves que tampoco convenció a la India
  él solo, sino que habló con el genetista indio Swaminathan, que…**
- **071 b22**: los cuatro operadores de Wall Street entrecomillados. Únelos en una enumeración indirecta:
  **operadores que quieren hacer una apuesta concreta, que tienen una opinión, que quieren cubrirse de una
  forma determinada o comprar un activo que el sistema financiero actual no les deja comprar, y que tienen
  que pasarse a Bitcoin o a Ethereum y hacerlo con finanzas descentralizadas.**
- **071 b39**: la cita del libro, «Innovation is the child of freedom because…», va con verbo introductorio y
  sin comillas: **La cita dice así, la innovación es hija de la libertad porque es un intento libre y
  creativo de satisfacer deseos humanos expresados libremente.**

### 5.4. Juegos de palabras

| Dónde | Juego | Solución |
|---|---|---|
| 070 b08 | *inspiration / perspiration*, *perspirators / inspirators* | Edison en español es «uno por ciento de inspiración y noventa y nueve por ciento de transpiración», la forma conocida. Para los sustantivos, ver §6, decisión 2 |
| 070 b19 | «Chiefs, priests and thieves, what's the difference?» | Funciona con cualquier traducción: **Gobernantes, sacerdotes y ladrones, ¿qué diferencia hay?** |
| 070 b20 | *spontaneous order / spontaneous disorder* | **mucho orden espontáneo, y también mucho desorden espontáneo** |
| 070 b21 | *They fall from grace, and they fall out of the garden* | **Caen en desgracia, y con ella salen del jardín** |
| 071 b10 y b16 | *flatten / crush the curve* | **aplanar / aplastar la curva** |
| 071 b13 | *scare / unscare* | **es fácil asustar a la gente y no tan fácil quitarle el miedo** |
| 071 b31 | *consolidate production / democratize consumption* | **concentrar la producción / democratizar el consumo** |
| 071 b32 | *specialized in what we produce, diversified in what we consume* | Es la idea central de *El optimista racional*: **cada vez más especializados en lo que producimos y más diversificados en lo que consumimos** |

### 5.5. Cifras y unidades

Todo en letra. Las trampas concretas son estas:

- ***billion* = mil millones.** «Siete mil millones de personas» (071 b04, dos veces), «ocho o nueve mil
  millones» (071 b01), «más de quinientos millones de dólares» (*half a billion*, 070 b09).
- **Siglos en letra y sin romanos**: «el siglo doce» (*the 1100s*, 070 b20), «el siglo quince» (070 b16),
  «principios del siglo veinte» (071 b17). Nunca «XII».
- **Décadas**: «los años noventa», «los años cincuenta».
- **Años**: «mil novecientos noventa y seis», «mil novecientos noventa y nueve», «dos mil nueve», «dos mil
  veinte».
- **Porcentajes**: «un uno por ciento de inspiración y un noventa y nueve por ciento de transpiración»;
  «entre un setenta y un ochenta por ciento», «entre un veinte y un treinta por ciento» (071 b35).
- **Concordancia**: «otras **veintiuna** personas» (071 b35, *21 other people*). «Veintiún personas» es error.
- **Rangos**: «entre diecisiete y veinte meses» (071 b01), «en los próximos cinco o diez años» (070 b17),
  «cincuenta, cien o doscientos años» (070 b17), «unos diez millones de personas» (071 b09), «seis o siete
  ejemplares» (070 b01).
- **Amara** (071 b22): «solemos sobrestimar lo que pasará en diez años y subestimar lo que pasará en veinte,
  así que el punto de cruce está en los quince».

### 5.6. Datos discutibles: se traducen tal cual

El intérprete no corrige a los hablantes. Si dicen algo inexacto, se traduce igual y se apunta en `notas`
solo si un revisor podría tomarlo por error de traducción:

- La empresa de comida para perros comprada por Amazon por más de quinientos millones (070 b09).
- Que la palabra «optimismo» la acuñó Voltaire (071 b03). Se acuñó para describir a Leibniz y Voltaire la
  satirizó en *Cándido*.
- Que Abbasid Arabia y París son «más o menos de la misma época» (070 b20).

### 5.7. Conceptos que en español se confunden

- **invención / invento / innovación.** *An invention* (el objeto) = **un invento**. *Invention* (el
  proceso) = **la invención**. No mezcles.
- ***technology business*** = **el negocio de la tecnología**, no «negocio tecnológico».
- ***democratic consumption*** = **un consumo democrático**, o **democratiza el consumo**.
- ***extra-sovereign*** (070 b17) = **fuera de cualquier soberanía, al margen del Estado**.
- ***extra-judiciary system*** (071 b22) = **un sistema que escape a su jurisdicción**. «Extrajudicial» en
  español significa otra cosa.
- ***the money printing press*** = **la máquina de imprimir dinero**.
- ***guys with guns*** = **tipos armados que hacen lo que tú quieras**.
- ***the attacker / the defender*** = **el atacante / el defensor**.
- ***castle wall / moat*** = **la muralla / el foso**.
- ***trench warfare*** = **la guerra de trincheras**.

### 5.8. Calcos que vigilar

- «Hacer sentido» por *makes sense*. Es **tiene sentido**.
- «Al final del día». Es **al fin y al cabo**.
- «Es por eso que». Es **por eso**.
- «Aplicar a» por *apply to*. Es **solicitar**.
- «Sustentable». Es **sostenible**.
- *I'm very encouraged* no es «estoy muy animado» sino **me alegra mucho**.
- *Fun, historical reading* = **una lectura de historia entretenida**.
- *Must-read* = **de lectura obligada**.
- *Actionable* = **práctico, aplicable**. Evita «accionable».
- *Playbook* = **un manual práctico**.

---

## 6. Decisiones que se proponen al autor

Aplica la opción recomendada y descríbela en `decisiones` del episodio, con sus alternativas.

1. **Nombres mal transcritos.** Cuando el error suena igual que el nombre correcto (Haber por *harbor*,
   Townes por *Towns*, Read por *Reed*, Bayles por *Bales*), escribe la forma correcta: el audio no cambia.
   Para **Orville** frente a *Oliver* (070 b11) el sonido sí cambia. **Recomiendo Orville**, porque el
   copiado de nav.al tiene erratas de oído y el hermano de Wilbur es Orville. Alternativa: «Oliver», fiel
   al texto pero falso. Coste: ninguno, y queda en notas.

2. **Fórmulas de Ridley.**
   - *Chiefs, priests and thieves*. **Recomiendo «gobernantes, sacerdotes y ladrones»**. Alternativas:
     «jefes, sacerdotes y ladrones», más literal pero «jefes» suena a jefe de oficina; «caciques, curas y
     ladrones», con más color y aliteración, pero «curas» rebaja el registro de Ridley.
   - *Perspirators / inspirators*. **Recomiendo «rescatar del olvido a los del sudor y quitar un poco de
     protagonismo a los de la inspiración»**. Es claro al oído y enlaza con la cita de Edison. Alternativa:
     «los que transpiran / los que inspiran», más pegada pero ambigua («los que inspiran» parece «los que
     inspiran a otros»).

3. **Títulos de Ridley sin edición española verificada** (*The Red Queen*, *The Origins of Virtue*, *The
   Evolution of Everything*) y *The Agile Gene*. **Recomiendo traducirlos**: *La reina roja*, *El origen de
   la virtud*, *La evolución de todo*, y para *The Agile Gene* el título publicado, **Qué nos hace humanos**.
   Un título inglés en mitad de la frase el TTS lo lee con acento español y Whisper no lo reconoce.
   Alternativa: dejar el inglés. Para *The Agile Gene*, la alternativa es «El gen ágil». Es fiel a lo que dijo
   Naval, pero no corresponde a ningún libro en español. Coste: si el autor encuentra ediciones españolas
   con otro título, se cambia en dos o tres frases.

4. ***Blockchain* y *tokens*** (070 b17, y marcará también el grupo Vitalik). **Recomiendo «cadena de
   bloques»**, que es la forma de Fundéu y el TTS la lee sin problema. Para *tokens*, **«tokens»** tal cual:
   no hay equivalente asentado y «fichas» confunde. Alternativa: «blockchain», que se usa mucho en España
   pero el TTS en español lo lee raro. Conviene fijarlo en GLOSARIO.md antes de traducir Vitalik.

5. ***Herd immunity*.** **Recomiendo «inmunidad de grupo»**, término médico sin calco. Alternativa: «inmunidad
   de rebaño», muy usada en la prensa de 2020-2021 y elegida por Fundéu como una de las voces del año 2021.
   Las dos se entienden.

6. ***Filter bubble*.** **Recomiendo «burbuja de filtros»**, que pone «burbuja» delante y se entiende al
   oído. Alternativa: «filtro burbuja», que es el título de la edición española de Pariser (Taurus, 2017)
   pero suena raro sin el libro delante. Otra alternativa: «burbuja informativa», más natural pero menos
   técnica.

7. **Títulos del episodio.** **Recomiendo «Matt Ridley, claves de la innovación, parte uno» y «…, parte
   dos»**. Siguen la forma de 051 («Cómo invertir como ángel, parte uno») y usan el título español del
   libro. `titulo_seccion`: «La innovación es hija de la libertad» y «La innovación es madre de la
   prosperidad».

   Títulos de sección de 070: Quién es Matt · El nuevo libro · Invención frente a innovación · Individuos
   frente a equipos · La concentración geográfica de la innovación · Cripto · Fragmentación política e
   innovación.

   Títulos de sección de 071: Hambruna de innovación · La covid · Burbujas de filtros · Más sobre cripto ·
   Automatización · La teoría del gran hombre · El libro.

8. **071 b31** (*not everybody* → *now everybody*). Recomiendo traducir el sentido evidente y dejarlo en
   `decisiones`. Alternativa: la traducción literal, que contradice la frase anterior.

---

## 7. Párrafo de ejemplo (070, b08, Matt)

**Inglés (f0):**

> I try to draw a distinction between invention and innovation. It’s not a distinction that is cast in
> iron, but I think this is the best way to think about it. Invention is the coming up with a prototype of
> a new device or a new social practice innovation. Innovation is the business of turning a new device into
> something practical, affordable and reliable that people will want to use and acquire. It’s the process of
> driving down the price; it’s the process of driving up the reliability and the efficiency of the device;
> and it’s the process of persuading other people to adopt it, too. Thomas Edison captures this point very
> well. I don’t think he used the word “innovation” much—he used the word “invention”—but he is mainly an
> innovator because he’s not necessarily coming up with original ideas. He’s taking other people’s ideas
> and turning them into practical propositions.
>
> Edison said this is a process of 1% inspiration and 99% perspiration. What I’m trying to do in this book is
> rescue the perspirators from obscurity and slightly relegate the inspirators, who will always think they
> deserve the most credit, and who sometimes complain about not getting enough reward because it’s their
> original idea. I like to tell the story that Charles Towns, the inventor of the laser, used to tell, of a
> rabbit and a beaver looking at the Hoover Dam, and the beaver says to the rabbit, “No, I didn’t build it,
> but it’s based on an idea of mine.” That is how inventors quite often think about innovations: “Come on, I
> had the idea!” But it’s a huge amount of work and talent to turn an idea into something practical.

**Español (`frases`, una por línea):**

```json
{ "speaker": "Matt", "frases": [
  "Intento distinguir entre invención e innovación, y aunque no es una distinción grabada en piedra, creo que es la mejor forma de pensar en ello.",
  "La invención consiste en dar con el prototipo de un aparato nuevo o de una nueva práctica social.",
  "La innovación es el trabajo de convertir ese aparato nuevo en algo práctico, asequible y fiable que la gente quiera usar y tener.",
  "Es el proceso de bajar el precio, de mejorar la fiabilidad y la eficiencia del aparato, y también de convencer a los demás para que lo adopten.",
  "Thomas Edison lo ilustra muy bien, aunque no creo que usara mucho la palabra innovación, él hablaba de invención.",
  "Pero sobre todo es un innovador, porque no siempre se le ocurren ideas originales, sino que toma las ideas de otros y las convierte en propuestas prácticas.",
  "Edison decía que esto es un uno por ciento de inspiración y un noventa y nueve por ciento de transpiración.",
  "Lo que intento con este libro es rescatar del olvido a los del sudor y quitar un poco de protagonismo a los de la inspiración.",
  "Los de la inspiración siempre creerán que merecen casi todo el mérito, y a veces se quejan de no recibir suficiente recompensa porque la idea original era suya.",
  "Me gusta contar una historia que contaba Charles Townes, el inventor del láser, sobre un conejo y un castor que miran la presa Hoover.",
  "Y el castor le dice al conejo, no, no la construí yo, pero está basada en una idea mía.",
  "Así ven muchas veces los inventores las innovaciones, y piensan, ¡venga ya, si la idea fue mía!",
  "Pero convertir una idea en algo práctico exige muchísimo trabajo y mucho talento."
] }
```

Qué ilustra:

- **Troceado para el oído.** Son 13 frases de entre 13 y 28 palabras. La primera funde una afirmación de
  6 palabras («Intento distinguir…») con la siguiente. No sigue el troceado del inglés.
- **Sin signos vocalizables.** Ni comillas, ni raya, ni punto y coma, ni %. Los tres *it's the process of*
  separados por punto y coma se funden en una sola frase con verbos.
- **Cifras en letra** y la forma española conocida de la frase de Edison.
- **El chiste en estilo directo con coma**, que conserva la gracia, y la exclamación con ¡ a mitad de frase.
- **Townes** corregido en silencio (se pronuncia igual) y apuntado en notas. *Social practice innovation*
  traducido como **práctica social**, con la palabra sobrante apuntada en notas.
- **Decisión 2** aplicada: los del sudor y los de la inspiración. La frase 9 repite el sujeto para que se
  entienda leída sola.
- **Cobertura**: 285 palabras en español frente a 284 en inglés, ratio 1,00, dentro del margen.

**Notas que irían con este bloque:** «b08: el inglés dice Charles Towns, se escribe Townes (Charles Townes,
inventor del máser y del láser). En social practice innovation sobra innovation, artefacto del copiado».

---

## Fuentes consultadas

Internas: `GLOSARIO.md`, `docs/revision-episodios.md`, `docs/traduccion.md`, `docs/hablantes.md`,
`fabrica/voces.json`, `trabajo/plan.json`, `trabajo/f0/matt-ridley.json`, `trabajo/f0/matt-ridley-2.json`,
`episodios/2019/051-angel-1`, `episodios/2019/052-rich` y `episodios/2020/053-*` a `067-*`.

Externas, todas vistas en los resultados de búsqueda. No pude abrir las páginas.

- Claves de la innovación (Antoni Bosch, 2021), ficha de catálogo: https://catalogobiblio.unach.cl/vufind/Record/DIGANBSCH0035/Description
- Reseña en *Economía Industrial* 421 (Ministerio de Industria): https://www.mintur.gob.es/Publicaciones/Publicacionesperiodicas/EconomiaIndustrial/RevistaEconomiaIndustrial/421/PRIMERA%20CRITICA.pdf
- Ediciones de How Innovation Works (Goodreads): https://www.goodreads.com/work/editions/70216129-how-innovation-works-serendipity-energy-and-the-saving-of-time
- La frase «hija de la libertad y madre de la prosperidad» (El Comercio, Ian Vásquez): https://elcomercio.pe/opinion/mirada-de-fondo/la-innovacion-por-ian-vasquez-noticia/
- El optimista racional (Taurus): https://quelibroleo.com/el-optimista-racional-tiene-limites-la-capacidad-de-progreso-de-la-especie-humana · https://www.marcialpons.es/libros/el-optimista-racional/9788430608102/
- Genoma (Taurus): https://www.lecturalia.com/libro/58738/genoma · https://us.hamelyn.com/second-hand-books/genoma-9788430604142
- Qué nos hace humanos (Taurus, 2004): https://catalogosiidca.csuca.org/Record/CR.UNA01000074833/Description · https://www.abebooks.co.uk/9788430605422/HUMANOS-Ridley-Matt-8430605428/plp
- Bibliografía en español de Ridley: https://es-academic.com/dic.nsf/eswiki/788981 · https://www.lecturalia.com/autor/10428/matt-ridley · https://www.casadellibro.com/libros-ebooks/matt-ridley/18087
- The Red Queen, sin edición española encontrada: https://es-academic.com/dic.nsf/eswiki/1450871
- Biografía (Lores, Northern Rock, The Economist): https://en.wikipedia.org/wiki/Matt_Ridley · https://academia-lab.com/enciclopedia/matt-ridley/ · https://huffingtonpost.co.uk/amp/entry/northern-rock-chairman-house-of-lords_n_2630718
- Entrevista en español sobre los confinamientos (Libre Mercado, 2020): https://www.libertaddigital.com/libremercado/2020-11-10/matt-ridley-coronavirus-covid-19-confinamientos-6679153/
- El comienzo del infinito (Biblioteca Buridán, 2012): https://descubridor.academia.cl/Record/DIGBURIDAN0009/Details · https://www.marcialpons.es/libros/el-comienzo-del-infinito/9788415216759/
- Yo, el lápiz: https://liberwiki.pages.dev/en/economia/yo-lapiz/ · https://www.prensalibre.com/?p=3200158
- Second Nature (Haim Ofek, CUP 2001): https://www.cambridge.org/core/journals/journal-of-economic-history/article/second-nature-economic-origins-of-human-evolution-by-haim-ofek-cambridge-cambridge-university-press-2001-pp-254-7495-cloth-2795-paper/5AE5EFA0BECCDEF7B64F9F0ADADABFA9
- De animales a dioses (Debate, 2014): https://quelibroleo.com/sapiens-de-animales-a-dioses-una-breve-historia-de-la-humanidad
- El filtro burbuja (Taurus, 2017): https://www.marcialpons.es/libros/el-filtro-burbuja/9788430618712/
- Inmunidad de grupo, colectiva o de rebaño (diccionario médico de la CUN): https://www.cun.es/diccionario-medico/terminos/nmunidad-de-grupo
- Bitcóin, según Fundéu: https://www.criptonoticias.com/sin-categoria/bitcoin-candidata-palabra-ano-2017-asociacion-fundeu/
- Amnesia de Gell-Mann (Crichton, 2002): https://en.wiktionary.com/wiki/Gell-Mann_Amnesia_effect
