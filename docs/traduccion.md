# Registro de traducción

Una línea por episodio traducido o arreglado en las sesiones de texto. Es el único documento de estado
que mantiene la sesión de traducción; lo técnico (fábrica, voces, Drive) está en `docs/estado.md`.

**De dónde sale el inglés.** De los Google Docs anuales de Drive (`naval-podcast/transcripts/<año>/`),
leídos con el conector. Cada episodio se corta desde la cabecera «Naval» + fecha hasta «## Related», se
pasa a `trabajo/manual/<slug>.txt` sin tocar el texto y lo trocea `scripts/extraer-episodios.py`. Se
comprueba que las palabras del resultado más las quitadas a propósito suman exactamente las del documento.

**Lo que no entra en el inglés**, por decisión del autor (3-nov):

- Las notas del editor de nav.al (la cursiva del principio, «This interview… was exclusively for my email
  list», «Submitted by…»): van al campo `notas` del episodio.
- Las citas destacadas entre comillas de la página: repiten frases que ya están en la conversación.
- La sección «Highlights» del 068 (Kapil Gupta): son citas resumidas que no están literalmente en la
  conversación.
- Los episodios sin «Get podcast» (sin audio), como *Finding Time to Invest in Yourself* (13-ene-2020):
  quedan como posible bonus al final.

Dos líneas sin negrita en el documento son títulos de sección y no se dicen (confirmado por el autor):
«Can you increase happiness without losing your drive?» (058) y «Are good investors piling in the round
with you?» (069).

**Para la sesión técnica** (hallazgo del 3-nov, no tocado): el troceo del inglés en
`scripts/normalizar-extraccion.py` (`trocear`, el `["”]?` fuera del lookbehind) consume la comilla de
cierre que sigue a un punto. En el documento las citas están cerradas; en `transcript.en.json` quedan
abiertas («…talk about sex.» sin «”»). Afecta solo al inglés, que no se locuta, pero altera el texto.

**Para la sesión técnica y la de contenido** (6-nov): las notas del editor de nav.al ya no se locutan; van en un campo
nuevo y opcional de cada bloque de `transcript.es.json`, `notas_editor` (lista de `{tras_frase, texto, original}`,
formato en GLOSARIO.md). La fábrica solo lee `speaker` y `frases`, así que no le afecta. Dos avisos: la web tiene que
leer ese campo para mostrar las notas, y `scripts/normalizar-extraccion.py` no lo conserva si se vuelve a normalizar un
episodio. Episodios con notas a 6-nov: 008, 010, 017, 018, 020 y 052.

| Fecha | Episodio | Estado | Bloques | Frases es | Palabras es | Min. | Notas |
|---|---|---|---|---|---|---|---|
| 2026-11-03 | 053 Live Long Enough and You'll Become a Philosopher | revision | 5 | 23 | 264 | 1,6 | Cero avisos. b02 en 0,84 por compresión de las preguntas |
| 2026-11-03 | 054 Happiness Without Material Comfort Is Playing on Hard Mode | revision | 5 | 32 | 434 | 2,5 | Cero avisos. Citas de Osho y Confucio en estilo indirecto. Retoque del autor en b04 (3-nov) |
| 2026-11-03 | 055 Happiness Is Not Science or Math | revision | 3 | 22 | 280 | 1,6 | Cero avisos |
| 2026-11-03 | 056 Happiness Is a Skill You Can Develop | revision | 3 | 16 | 244 | 1,4 | Cero avisos. Retoque del autor en b03 (3-nov) |
| 2026-11-03 | 036 There Are No Get Rich Quick Schemes (arreglo) | revision | 6 | 66 | 953 | 5,6 | 3 avisos a cero: dos frases de más de 45 palabras partidas y «Resulta sospechoso.» fundida |
| 2026-11-03 | 040 Being Ethical Is Long-Term Greedy (arreglo) | revision | 7 | 45 | 687 | 4,0 | 2 avisos a cero: «Tienes confianza.» y «Tienes reputación.» fundidas |
| 2026-11-03 | 052 How to Get Rich (arreglo) | revision | 288 | 2883 | 42076 | 248 | 40 avisos a cero: 14 por vosotros, os, vale y chaval, 26 frases cortas fundidas. Detalle en notas y en el commit. Retoques de la revisión (4-nov) |
| 2026-11-03 | 057 Desire Is a Contract You Make to Be Unhappy | revision | 3 | 15 | 226 | 1,3 | Cero avisos |
| 2026-11-03 | 058 If You’re So Smart, Why Aren’t You Happy? | revision | 4 | 32 | 483 | 2,8 | Cero avisos. Título de sección confirmado por el autor; citas en estilo indirecto. Retoques de la revisión (4-nov) |
| 2026-11-03 | 059 Being Unhappy Is Extremely Inefficient | revision | 3 | 20 | 346 | 2,0 | Cero avisos. Artefacto del copiado en el inglés señalado en notas |
| 2026-11-03 | 060 Work the Least for It | revision | 2 | 17 | 302 | 1,8 | Cero avisos. S-1 resuelto en la frase |
| 2026-11-03 | 061 The Modern Struggle Is Fighting Weaponized Addiction | revision | 2 | 14 | 273 | 1,6 | Cero avisos. Citas en estilo indirecto. Retoques de la revisión (4-nov) |
| 2026-11-03 | 062 Breaking Addiction Is Socially Unacceptable | revision | 3 | 18 | 306 | 1,8 | Cero avisos |
| 2026-11-03 | 065 The Closer You Are to the Truth, the More Silent You Become Inside | revision | 2 | 13 | 222 | 1,3 | Cero avisos. Lao Tse y test de inteligencia resueltos en la frase; si A entonces B según el autor (4-nov) |
| 2026-11-03 | 066 Groups Search for Consensus, Individuals Search for Truth | revision | 3 | 20 | 369 | 2,2 | Cero avisos |
| 2026-11-03 | 067 The Path to Peace Is Truth | revision | 3 | 17 | 312 | 1,8 | Cero avisos |
| 2026-11-03 | 063 Finding Peace from Mind | revision | 4 | 24 | 408 | 2,4 | Cero avisos. Paz frente a la mente (opción C del autor); A come a B resuelto con palabras |
| 2026-11-03 | 064 Happiness Is Peace in Motion | revision | 4 | 26 | 398 | 2,3 | Cero avisos. Paz frente a la mente (opción C del autor) |
| 2026-11-04 | 046 Compounding Relationships Make Life Easier | revision | 5 | 25 | 434 | 2,6 | Cero avisos. Workflow de especialistas (4-nov); 6 decisiones aplicadas, ver notas |
| 2026-11-04 | 047 Price Discrimination: Charge Some People More | revision | 3 | 13 | 219 | 1,3 | Cero avisos. Workflow de especialistas (4-nov); 3 decisiones aplicadas, ver notas |
| 2026-11-04 | 048 Consumer Surplus: Getting More Than You Paid For | revision | 1 | 12 | 171 | 1,0 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 049 Net Present Value: What Future Income Is Worth Today | revision | 3 | 11 | 212 | 1,2 | Cero avisos. Workflow de especialistas (4-nov); 4 decisiones aplicadas, ver notas |
| 2026-11-04 | 050 Externalities: Calculating the Hidden Costs of Products | revision | 4 | 19 | 324 | 1,9 | Cero avisos. Workflow de especialistas (4-nov); 3 decisiones aplicadas, ver notas |
| 2026-11-04 | 068 Kapil Gupta: Conquering the Mind | revision | 84 | 438 | 7675 | 45,1 | Cero avisos. Workflow de especialistas (4-nov); 16 decisiones aplicadas, ver notas |
| 2026-11-04 | 069 How to Angel Invest, Part 2 | revision | 59 | 368 | 6203 | 36,5 | Cero avisos. Workflow de especialistas (4-nov); 23 decisiones aplicadas, ver notas |
| 2026-11-04 | 070 Matt Ridley: How Innovation Works, Part 1 | revision | 21 | 304 | 5761 | 33,9 | Cero avisos. Workflow de especialistas (4-nov); 13 decisiones aplicadas, ver notas |
| 2026-11-04 | 071 Matt Ridley: How Innovation Works, Part 2 | revision | 40 | 289 | 6080 | 35,8 | Cero avisos. Workflow de especialistas (4-nov); 15 decisiones aplicadas, ver notas |
| 2026-11-04 | 072 Science Is the Engine That Pulls Humanity Forward | revision | 1 | 29 | 461 | 2,7 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 073 This Book Changed the Way I Think | revision | 1 | 17 | 344 | 2,0 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 074 Nullius in Verba | revision | 2 | 22 | 358 | 2,1 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 075 Explanations That Reach the Entire Universe | revision | 3 | 16 | 301 | 1,8 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 076 Read the Best 100 Books Over and Over Again | revision | 3 | 29 | 470 | 2,8 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 077 Happiness | revision | 49 | 309 | 4867 | 28,6 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 078 We’re at the Beginning of an Infinity of Knowledge | revision | 3 | 24 | 358 | 2,1 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 079 People Are a Force of Nature | revision | 1 | 22 | 381 | 2,2 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 080 It’s Impossible to Predict the Growth of Knowledge | revision | 2 | 19 | 362 | 2,1 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 081 Humans Are Unique in Our Ability to Understand Things | revision | 1 | 12 | 225 | 1,3 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 082 Good Explanations Are Acts of Creativity | revision | 1 | 20 | 345 | 2,0 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 083 Good Explanations Are Hard to Vary | revision | 5 | 28 | 484 | 2,8 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 084 There Is No End of Science | revision | 1 | 22 | 415 | 2,4 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 085 There Is No Settled Mathematics | revision | 2 | 28 | 555 | 3,3 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 086 The Methods of Mathematics Are Fallible | revision | 2 | 27 | 509 | 3,0 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 087 All Knowledge Is Conjectural | revision | 1 | 34 | 531 | 3,1 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 088 Is the Universe Discrete or Continuous? | revision | 2 | 25 | 407 | 2,4 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 089 Every Theory Is Held Inside a Physical Substrate | revision | 3 | 23 | 385 | 2,3 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 090 We Can’t Prove Most Theorems with Known Physics | revision | 1 | 16 | 291 | 1,7 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 091 Probability Is Subjective | revision | 4 | 20 | 390 | 2,3 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 092 Is Light a Particle or a Wave? | revision | 2 | 32 | 637 | 3,7 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 093 The Multiverse | revision | 1 | 15 | 278 | 1,6 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 094 We Explain the Seen in Terms of the Unseen | revision | 2 | 15 | 276 | 1,6 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 095 Science Expands Our Vision of Reality | revision | 1 | 17 | 292 | 1,7 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 096 Science Is an Error-Correcting Mechanism | revision | 2 | 19 | 388 | 2,3 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 097 Theories Are Explanations, Not Predictions | revision | 3 | 24 | 413 | 2,4 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 098 Make Bold Guesses and Weed Out the Failures | revision | 3 | 24 | 387 | 2,3 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 099 Science Advances One Funeral at a Time | revision | 3 | 12 | 219 | 1,3 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 100 It’s Rare to Have Competing, Viable, Scientific Theories | revision | 6 | 41 | 669 | 3,9 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 101 We’re All Equal in Our Infinite Ignorance | revision | 3 | 17 | 303 | 1,8 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 102 It’s Easy to Extrapolate How Things Will Get Worse | revision | 3 | 15 | 321 | 1,9 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 103 Pessimism Seems Like an Intellectually Serious Position | revision | 2 | 19 | 353 | 2,1 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 104 Rational Optimism Is the Way Out | revision | 3 | 21 | 381 | 2,2 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 105 The Beginning of Infinity, Part 1 | revision | 73 | 704 | 12489 | 73,5 | Cero avisos. Workflow de especialistas (4-nov); 4 decisiones aplicadas, ver notas |
| 2026-11-04 | 106 With a Good Theory of Knowledge, You Can Decide What Else Is True | revision | 1 | 17 | 326 | 1,9 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 107 No Truth Can Be Justified | revision | 1 | 20 | 427 | 2,5 | Cero avisos. Workflow de especialistas (4-nov); 3 decisiones aplicadas, ver notas |
| 2026-11-04 | 108 There Can Be No Final Theory of Gravity | revision | 2 | 38 | 644 | 3,8 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 109 Genetic Evolution Was a Prelude to Memetic Evolution | revision | 1 | 21 | 471 | 2,8 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 110 Humans Are Exceptional | revision | 1 | 24 | 429 | 2,5 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 111 We Are Qualitatively Different From Other Species | revision | 1 | 17 | 302 | 1,8 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 112 More Compute Power Doesn’t Produce AGI | revision | 1 | 15 | 319 | 1,9 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 113 It’s Mind Blowing That Our Minds Can’t Be Blown | revision | 2 | 30 | 546 | 3,2 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 114 Where Are the Aliens? | revision | 2 | 12 | 191 | 1,1 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 115 Intelligent Species Have Risen Only Once on Planet Earth | revision | 1 | 31 | 584 | 3,4 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 116 The Probability of Human Existence Is Infinitesimally Small | revision | 1 | 11 | 222 | 1,3 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 117 If You Can’t Program It, You Haven’t Understood It | revision | 1 | 6 | 123 | 0,7 | Cero avisos. Workflow de especialistas (4-nov) |
| 2026-11-04 | 118 Aliens Might Just Be Too Far Away | revision | 2 | 22 | 467 | 2,7 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 119 Aliens Would Visit for Knowledge, Not Resources | revision | 2 | 26 | 475 | 2,8 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 120 Ideas Are the New Oil | revision | 1 | 29 | 553 | 3,3 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 121 One Einstein Is Worth A Legion Of PhD Drones | revision | 2 | 14 | 250 | 1,5 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 122 Don’t Rely on Credibility Stamps | revision | 3 | 22 | 370 | 2,2 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 123 Innovation Requires Decentralization and a Frontier | revision | 1 | 35 | 648 | 3,8 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 124 The Poverty of Compromise | revision | 1 | 32 | 572 | 3,4 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 125 Free Markets Provide the Best Feedback | revision | 2 | 30 | 556 | 3,3 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 126 Making Something Social Destroys the Truth of It | revision | 1 | 27 | 490 | 2,9 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 127 Groups Never Admit Failure | revision | 1 | 27 | 442 | 2,6 | Cero avisos. Workflow de especialistas (4-nov); 1 decisiones aplicadas, ver notas |
| 2026-11-04 | 128 Knowledge Makes the Existence of Resources Infinite | revision | 2 | 26 | 535 | 3,1 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 129 To a Caveman Very Few Things Are Resources | revision | 2 | 35 | 611 | 3,6 | Cero avisos. Workflow de especialistas (4-nov); 3 decisiones aplicadas, ver notas |
| 2026-11-04 | 130 The Beginning of Infinity, Part 2 | revision | 35 | 567 | 10553 | 62,1 | Cero avisos. Workflow de especialistas (4-nov); 2 decisiones aplicadas, ver notas |
| 2026-11-04 | 131 Vitalik: Ethereum, Part 1 | revision | 82 | 503 | 9334 | 54,9 | Cero avisos. Workflow de especialistas (4-nov); 20 decisiones aplicadas, ver notas |
| 2026-11-04 | 132 Vitalik: Ethereum, Part 2 | revision | 59 | 313 | 5332 | 31,4 | Cero avisos. Workflow de especialistas (4-nov); 17 decisiones aplicadas, ver notas |
| 2026-11-04 | 133 David Deutsch: Knowledge Creation and The Human Race, Part 1 | revision | 49 | 414 | 7736 | 45,5 | Cero avisos. Workflow de especialistas (4-nov); 16 decisiones aplicadas, ver notas |
| 2026-11-04 | 134 David Deutsch: Knowledge Creation and The Human Race, Part 2 | revision | 33 | 330 | 6033 | 35,5 | Cero avisos. Workflow de especialistas (4-nov); 14 decisiones aplicadas, ver notas |
| 2026-11-04 | 068 Kapil Gupta: Conquering the Mind (corrección) | revision | 84 | 438 | 7673 | 45,1 | Decisión del autor: prescriptions = prescripciones, no recetas (30 frases). Hay que volver a sintetizarlo |
| 2026-11-04 | 001 Seek Wealth, Not Money or Status | revision | 4 | 100 | 1253 | 7,4 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada como lista el 2-nov). Cero avisos: fundidas «Llamémoslo dinero.» y «Es jerárquico.». Sin la nota editorial de cabecera (no se locuta) |
| 2026-11-04 | 002 Make Abundance for the World | revision | 1 | 59 | 617 | 3,6 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada como lista el 2-nov). Cero avisos, sin cambios |
| 2026-11-04 | 003 Free Markets Are Intrinsic to Humans | revision | 3 | 71 | 838 | 4,9 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. «vosotros» resuelto sin plural («cualquiera de los que estamos aquí»); fundido «Así es.» |
| 2026-11-04 | 004 Making Money Isn’t About Luck | revision | 3 | 76 | 1034 | 6,1 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Sin cambios |
| 2026-11-04 | 005 Make Luck Your Destiny | revision | 8 | 39 | 832 | 4,9 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Partida la frase de 60 palabras; fundidos «Sí, totalmente.» y «Sí.» |
| 2026-11-04 | 006 You Won’t Get Rich Renting Out Your Time | revision | 2 | 67 | 1006 | 5,9 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Fundido «Usamos herramientas.» |
| 2026-11-04 | 007 Live Below Your Means for Freedom | revision | 2 | 32 | 497 | 2,9 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. «vale» → «bueno»; «tipos marginales» se queda (vocabulario de España) |
| 2026-11-04 | 008 Give Society What It Doesn’t Know How to Get | revision | 4 | 40 | 560 | 3,3 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Fundido «Así es.»; partida una frase de 46. Danny Hillis se mantiene (corrección de nav.al, en notas) |
| 2026-11-04 | 010 Play Long-term Games With Long-term People | revision | 8 | 86 | 1330 | 7,8 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Partidas 3 frases largas; «podéis» → «puedes»; «ojo por ojo» → «toma y daca»; nota [correction] fuera del audio (en notas) |
| 2026-11-04 | 009 The Internet Has Massively Broadened Career Possibilities | revision | 2 | 72 | 970 | 5,7 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Fundidas 7 frases de una o dos palabras; partida la de 47; «chaval» → «chico» |
| 2026-11-04 | 012 Partner With Rational Optimists | revision | 6 | 87 | 1159 | 6,8 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. BOCTAOE resuelto en la frase («unas siglas en inglés que venían a decir…»); «chaval» → «chico»; fundido «Sí.» |
| 2026-11-04 | 011 Pick Partners With Intelligence, Energy and Integrity | revision | 3 | 76 | 1097 | 6,5 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Fundido «Sí.» |
| 2026-11-04 | 013 Arm Yourself With Specific Knowledge | revision | 2 | 69 | 1301 | 7,7 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Partidas 2 frases de 46 y 48 |
| 2026-11-04 | 014 Specific Knowledge Is Highly Creative or Technical | revision | 5 | 59 | 1112 | 6,5 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. «The Intelligent Investor» → «El inversor inteligente» |
| 2026-11-04 | 015 Learn to Sell, Learn to Build | revision | 4 | 66 | 1099 | 6,5 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Partida la de 56; «pila de habilidades» → «combinación de habilidades» |
| 2026-11-04 | 016 Read What You Love Until You Love to Read | revision | 2 | 56 | 971 | 5,7 | Traído por la sesión técnica desde la traducción antigua de Drive (auditada el 2-nov). Cero avisos. Títulos de libros en español (La riqueza de las naciones, El origen de las especies, El octavo día de la creación, Seis piezas fáciles) |
| 2026-11-04 | 068 Kapil Gupta: Conquistando la mente (segunda revisión) | revision | 84 | 438 | 7682 | 45,2 | Revisión con el autor tras investigar el vocabulario de Kapil (brief, apartado 8). Términos confirmados en GLOSARIO.md. There is no other = no hay otro; the understanding = la comprensión (8 frases); observar, no vigilar; sin la muletilla la verdad es que; título como el original. Cero avisos. Hay que volver a sintetizarlo |
| 2026-11-05 | 070 Matt Ridley: Claves de la innovación, parte 1 (revisión) | revision | 21 | 304 | 5761 | 33,9 | Revisión de la serie Ridley, bloque a bloque. Cero avisos. Título con dos puntos y número (decisión del autor). Sin más cambios en las frases. Términos de la serie pendientes de visto bueno, ver notas |
| 2026-11-05 | 071 Matt Ridley: Claves de la innovación, parte 2 (revisión) | revision | 40 | 291 | 6078 | 35,8 | Revisión de la serie Ridley, bloque a bloque. Cero avisos. Título con dos puntos y número (decisión del autor). Ajustadas 4 frases de 36 palabras (b14, b22, b24, b40), «Recomiendo también Genoma» (b39) y un punto en medio de frase (b39). Términos pendientes de visto bueno, ver notas |
| 2026-11-05 | 017 The Foundations Are Math and Logic | revision | 4 | 29 | 565 | 3,3 | Cero avisos. Parte del 052 (b95–b98) con los términos del 5-nov; citas en estilo indirecto; dos frases cortas fundidas; [of pseudoscience] fuera del audio |
| 2026-11-05 | 018 There's No Actual Skill Called "Business" | revision | 5 | 65 | 1153 | 6,8 | Cero avisos. Parte del 052 (b99–b103); casos prácticos; toma y daca; ocho frases cortas fundidas y dos largas partidas; [reading] y [not repetitions] fuera del audio |
| 2026-11-05 | 019 Embrace Accountability to Get Leverage | revision | 5 | 52 | 948 | 5,6 | Cero avisos. Parte del 052 (b104–b108); cargos de responsabilidad y equity en b01; 17 frases cortas fundidas y tres largas partidas; calcos fuera |
| 2026-11-05 | 020 Take Accountability to Earn Equity | revision | 6 | 54 | 965 | 5,7 | Cero avisos. Parte del 052 (b109–b114); equity en inglés; Jugarse la piel; nueve frases cortas fundidas; [bankruptcy] fuera del audio |
| 2026-11-05 | 021 Labor and Capital Are Old Leverage | revision | 6 | 49 | 951 | 5,6 | Cero avisos. Parte del 052 (b115–b120); Arquímedes en estilo indirecto, sin el dadme del 052; 13 frases cortas fundidas y dos largas partidas |
| 2026-11-05 | 022 Product and Media are New Leverage | revision | 7 | 54 | 1082 | 6,4 | Cero avisos. Parte del 052 (b121–b127); 17 frases cortas fundidas y una larga partida; título en paralelo con el 021 |
| 2026-11-05 | 023 Product Leverage is Egalitarian | revision | 7 | 51 | 1062 | 6,2 | Cero avisos. Parte del 052 (b128–b134); inputs y outputs en inglés; nueve frases cortas fundidas y una larga partida; el final se queda en Nivi, como en el 052 |
| 2026-11-05 | 024 Pick a Business Model With Leverage | revision | 7 | 62 | 1224 | 7,2 | Cero avisos. Parte del 052 (b135–b141); replicación; corregido un hablarais (vosotros) que el 052 b140 sigue teniendo; cinco frases cortas fundidas |
| 2026-11-05 | 025 Example: From Laborer to Entrepreneur | revision | 5 | 56 | 1107 | 6,5 | Cero avisos. Parte del 052 (b142–b146); equity; responsabilidad y hacerse cargo en b02; estilo indirecto; ocho frases cortas fundidas y dos largas partidas |
| 2026-11-05 | 026 Judgment Is the Decisive Skill | revision | 10 | 63 | 1242 | 7,3 | Cero avisos. Parte del 052 (b147–b156); jugarse la piel; interés compuesto; estilo indirecto; siete frases cortas fundidas y dos largas reescritas |
| 2026-11-05 | 027 Set an Aspirational Hourly Rate | revision | 6 | 47 | 692 | 4,1 | Cero avisos. Parte del 052 (b157–b162); tarifa ambiciosa siempre; estilo indirecto; nueve frases cortas fundidas |
| 2026-11-05 | 028 Work As Hard As You Can | revision | 6 | 61 | 949 | 5,6 | Cero avisos. Parte del 052 (b163–b168); corregido un estuvierais (vosotros) que el 052 b163 sigue teniendo; estilo indirecto; 25 frases cortas fundidas |
| 2026-11-05 | 029 Be Too Busy to 'Do Coffee' | revision | 6 | 44 | 693 | 4,1 | Cero avisos. Parte del 052 (b169–b174); estilo indirecto; 15 frases cortas fundidas; quedar a tomar café en todo el episodio |
| 2026-11-05 | 030 Keep Redefining What You Do | revision | 3 | 22 | 397 | 2,3 | Cero avisos. Parte del 052 (b175–b177); estilo indirecto; diez frases cortas fundidas |
| 2026-11-05 | 031 Escape Competition Through Authenticity | revision | 7 | 63 | 977 | 5,7 | Cero avisos. Parte del 052 (b178–b184); estilo indirecto; 20 frases cortas fundidas; profesión y afición |
| 2026-11-05 | 032 Play Stupid Games, Win Stupid Prizes | revision | 3 | 26 | 464 | 2,7 | Cero avisos. Parte del 052 (b185–b187); la máxima del título en una sola frase; diez frases cortas fundidas |
| 2026-11-05 | 033 Eventually You Will Get What You Deserve | revision | 4 | 43 | 724 | 4,3 | Cero avisos. Parte del 052 (b188–b191); la pregunta final es título de sección y no se dice; interés compuesto; estilo indirecto; 18 frases cortas fundidas |
| 2026-11-05 | 034 Reject Most Advice | revision | 4 | 29 | 525 | 3,1 | Cero avisos. Parte del 052 (b192–b195); boleto de lotería premiado en todo el episodio; estilo indirecto; diez frases cortas fundidas |
| 2026-11-06 | 052 How to Get Rich (términos del 5 y 6-nov) | revision | 288 | 2883 | 42084 | 247,6 | Cero avisos. Equity, inputs y outputs, interés compuesto, replicación, valor actual neto, del momento, jugarse la piel, sinvergüenza; tres vosotros corregidos; cinco notas del editor a notas_editor |
| 2026-11-06 | 046 Compounding Relationships Make Life Easier (términos del 5 y 6-nov) | revision | 5 | 25 | 438 | 2,6 | Cero avisos. Interés compuesto en el texto y en el título; sigue idéntico al 052 b258–b260 |
| 2026-11-06 | 049 Net Present Value: What Future Income Is Worth Today (términos del 5 y 6-nov) | revision | 3 | 11 | 212 | 1,2 | Cero avisos. Valor actual neto en el texto y en el título |
| 2026-11-06 | 051 How to Angel Invest, Part 1 (términos del 5 y 6-nov) | revision | 81 | 525 | 8368 | 49,2 | Cero avisos. Equity, acciones ordinarias, replicación, Buffett, interés compuesto, jugarse la piel |
| 2026-11-06 | 045 Turn Short-Term Games Into Long-Term Games (términos del 5 y 6-nov) | revision | 5 | 28 | 462 | 2,7 | Cero avisos. Fuerza negociadora en b05 y posición de fuerza en el subtítulo |
| 2026-11-06 | 069 How to Angel Invest, Part 2 (términos del 5 y 6-nov) | revision | 59 | 368 | 6203 | 36,5 | Cero avisos. Sinvergüenza en b44; flujo de operaciones confirmado |
| 2026-11-06 | 018 There's No Actual Skill Called "Business" (términos del 5 y 6-nov) | revision | 5 | 65 | 1152 | 6,8 | Cero avisos. [reading] fuera de la voz; dos notas del editor a notas_editor |
| 2026-11-06 | 017 The Foundations Are Math and Logic (términos del 5 y 6-nov) | revision | 4 | 29 | 565 | 3,3 | Nota del editor a notas_editor; texto sin cambios |
| 2026-11-06 | 020 Take Accountability to Earn Equity (términos del 5 y 6-nov) | revision | 6 | 54 | 965 | 5,7 | Nota del editor a notas_editor; texto sin cambios |
| 2026-11-06 | 008 Give Society What It Doesn’t Know How to Get (términos del 5 y 6-nov) | montaje | 4 | 40 | 560 | 3,3 | Nota del editor a notas_editor; frases sin cambios, el audio sigue valiendo |
| 2026-11-06 | 010 Play Long-term Games With Long-term People (términos del 5 y 6-nov) | montaje | 8 | 86 | 1330 | 7,8 | Nota del editor a notas_editor; frases sin cambios, el audio sigue valiendo |
| 2026-11-07 | 154 In the Arena | revision | 31 | 527 | 8952 | 52,7 | Cero avisos. Largo que recopila 139–145 y 147–153; cada corto es un tramo de sus bloques. Decisiones del autor del 7-nov (capacidad de actuar, en la arena, banquero mafioso, feedback); For example, if you look at marketing al final de b15; fecha del catálogo, la página dice 14-oct |
| 2026-11-07 | 139 Inspiration All the Way Down | revision | 5 | 33 | 581 | 3,4 | Cero avisos. Corto: tramo b02–b05 del 154 más intro propia de Nivi (b01, se genera aparte); fecha del catálogo, la página dice 15-jul |
| 2026-11-07 | 140 Life is Lived in The Arena | revision | 3 | 29 | 454 | 2,7 | Cero avisos. Corto: tramo b07–b09 del 154; fecha del catálogo, la página dice 17-jul |
| 2026-11-07 | 141 If You Want to Learn, Do | revision | 1 | 17 | 272 | 1,6 | Cero avisos. Corto: tramo b10 del 154; fecha del catálogo, la página dice 21-jul |
| 2026-11-07 | 142 In Most Difficult Things in Life, The Solution is Indirect | revision | 1 | 15 | 267 | 1,6 | Cero avisos. Corto: tramo b11 del 154; banquero mafioso |
| 2026-11-07 | 143 When You Truly Work for Yourself | revision | 3 | 33 | 561 | 3,3 | Cero avisos. Corto: tramo b12–b14 del 154 |
| 2026-11-07 | 144 Find Your Specific Knowledge Through Action | revision | 1 | 25 | 427 | 2,5 | Cero avisos. Corto: tramo b15 del 154 sin su última frase (decisión del autor): este bloque se genera aparte; fecha del catálogo, la página dice 29-jul |
| 2026-11-07 | 145 You Have to Enjoy It a Lot | revision | 1 | 37 | 601 | 3,5 | Cero avisos. Corto: tramo b16 del 154; empieza en Marketing is an open problem |
| 2026-11-07 | 147 Pause, Reflect, See How Well it Did | revision | 1 | 23 | 354 | 2,1 | Cero avisos. Corto: tramo b17 del 154; fecha del catálogo, la página dice 6-ago |
| 2026-11-07 | 148 Blame Yourself for Everything, and Preserve Your Agency | revision | 2 | 62 | 1024 | 6,0 | Cero avisos. Corto: tramo b18–b19 del 154; capacidad de actuar en el título; fecha del catálogo, la página dice 25-ago |
| 2026-11-07 | 149 It Is Impossible to Fool Mother Nature | revision | 3 | 59 | 919 | 5,4 | Cero avisos. Corto: tramo b20–b22 del 154; feedback en inglés; fecha del catálogo, la página dice 22-sep |
| 2026-11-07 | 150 The Best Authors Respect the Reader's Time | revision | 2 | 34 | 595 | 3,5 | Cero avisos. Corto: tramo b23–b24 del 154; fecha del catálogo, la página dice 24-sep |
| 2026-11-07 | 151 Most Books Should Be Skimmed, A Few Should Be Devoured | revision | 2 | 45 | 795 | 4,7 | Cero avisos. Corto: tramo b25–b26 del 154; fecha del catálogo, la página dice 26-sep |
| 2026-11-07 | 152 Good Products Are Hard to Vary | revision | 1 | 41 | 719 | 4,2 | Cero avisos. Corto: tramo b27 del 154 |
| 2026-11-07 | 153 Find the Simplest Thing That Works | revision | 4 | 73 | 1394 | 8,2 | Cero avisos. Corto: tramo b28–b31 del 154; fecha del catálogo, la página dice 1-oct |
| 2026-11-07 | 155 Curate People | revision | 38 | 578 | 10342 | 60,8 | Cero avisos. Episodio aparte. Decisiones del autor del 7-nov: Elige bien a la gente, cultura y culto comparten raíz, opiniones muy firmes, feedback, capacidad de actuar; reclutar, levantar capital, gusto |
| 2026-11-07 | 156 A Motorcycle for the Mind | revision | 41 | 517 | 10861 | 63,9 | Cero avisos. Una moto para la mente. Decisiones del autor del 6 y 7-nov: la inteligencia artificial y luego la IA, vibe coding, prompt, feedback, debug y bug en inglés, capacidad de actuar, IA desalineada, no hay demanda para lo promedio, Impossible; lapsus de Naval sin corregir (binary sort, Skynet, nanotubos) |
| 2026-11-07 | 157 A Return to Code | revision | 14 | 293 | 6177 | 36,3 | Cero avisos. La vuelta al código. Decisiones del autor del 6 y 7-nov: vibe coding glosado en b03, one-shot, tokens glosados en b03, pull request, bug, hack y feedback en inglés, inteligencia dentada, un billón de tokens; en el software puro no se puede invertir |
| 2026-11-07 | 158 'Nothing Ever Happens' Is Over | revision | 12 | 195 | 4026 | 23,7 | Cero avisos. Se acabó lo de que nunca pasa nada (--slug over). Decisiones del autor del 6 y 7-nov: ojalá vivas tiempos interesantes, inteligencia artificial general, inteligencia dentada, vibe coding glosado en b09, b09 fiel sin suavizar, los llamados bioéticos; cientos o miles frente a cientos de miles, tal cual en el inglés |
| 2026-11-07 | 159 Sell the Truth | revision | 22 | 281 | 5852 | 34,4 | Cero avisos. Vende la verdad. Decisiones del autor del 7-nov: Nivi repetido traducido dos veces (b20 y b21), comillas irónicas reformuladas, una startup muy mala, vender como un evangelizador, Influencia, Tierra de hombres, El alma de una nueva máquina, seis principios de Cialdini en vez de CLASSR; deal = acuerdo |
| 2026-11-07 | 072 Science Is the Engine That Pulls Humanity Forward (revisión con el autor) | revision | 1 | 29 | 461 | 2,7 | Revisión con el autor (7-nov): testable = contrastable (1 frase). Cero avisos |
| 2026-11-07 | 073 This Book Changed the Way I Think (revisión con el autor) | revision | 1 | 17 | 344 | 2,0 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 074 Nullius in Verba (revisión con el autor) | revision | 2 | 22 | 358 | 2,1 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 075 Explanations That Reach the Entire Universe (revisión con el autor) | revision | 3 | 16 | 301 | 1,8 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 076 Read the Best 100 Books Over and Over Again (revisión con el autor) | revision | 3 | 29 | 470 | 2,8 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 078 We’re at the Beginning of an Infinity of Knowledge (revisión con el autor) | revision | 3 | 24 | 358 | 2,1 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 079 People Are a Force of Nature (revisión con el autor) | revision | 1 | 22 | 381 | 2,2 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 080 It’s Impossible to Predict the Growth of Knowledge (revisión con el autor) | revision | 2 | 19 | 362 | 2,1 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 081 Humans Are Unique in Our Ability to Understand Things (revisión con el autor) | revision | 1 | 12 | 225 | 1,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 082 Good Explanations Are Acts of Creativity (revisión con el autor) | revision | 1 | 20 | 345 | 2,0 | Revisión con el autor (7-nov): testable = contrastable (2 frases). Cero avisos |
| 2026-11-07 | 083 Good Explanations Are Hard to Vary (revisión con el autor) | revision | 5 | 28 | 483 | 2,8 | Revisión con el autor (7-nov): testable = contrastable (5 frases). Cero avisos |
| 2026-11-07 | 084 There Is No End of Science (revisión con el autor) | revision | 1 | 22 | 415 | 2,4 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 085 There Is No Settled Mathematics (revisión con el autor) | revision | 2 | 28 | 555 | 3,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 086 The Methods of Mathematics Are Fallible (revisión con el autor) | revision | 2 | 27 | 509 | 3,0 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 087 All Knowledge Is Conjectural (revisión con el autor) | revision | 1 | 34 | 531 | 3,1 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 088 Is the Universe Discrete or Continuous? (revisión con el autor) | revision | 2 | 25 | 407 | 2,4 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 089 Every Theory Is Held Inside a Physical Substrate (revisión con el autor) | revision | 3 | 23 | 385 | 2,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 090 We Can’t Prove Most Theorems with Known Physics (revisión con el autor) | revision | 1 | 16 | 291 | 1,7 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 091 Probability Is Subjective (revisión con el autor) | revision | 4 | 20 | 390 | 2,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 092 Is Light a Particle or a Wave? (revisión con el autor) | revision | 2 | 33 | 640 | 3,8 | Revisión con el autor (7-nov): partida una frase de 38 palabras. Cero avisos |
| 2026-11-07 | 093 The Multiverse (revisión con el autor) | revision | 1 | 15 | 278 | 1,6 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 094 We Explain the Seen in Terms of the Unseen (revisión con el autor) | revision | 2 | 15 | 276 | 1,6 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 095 Science Expands Our Vision of Reality (revisión con el autor) | revision | 1 | 17 | 292 | 1,7 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 096 Science Is an Error-Correcting Mechanism (revisión con el autor) | revision | 2 | 19 | 388 | 2,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 097 Theories Are Explanations, Not Predictions (revisión con el autor) | revision | 3 | 24 | 413 | 2,4 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 098 Make Bold Guesses and Weed Out the Failures (revisión con el autor) | revision | 3 | 24 | 387 | 2,3 | Revisión con el autor (7-nov): testable = contrastable (1 frase). Cero avisos |
| 2026-11-07 | 099 Science Advances One Funeral at a Time (revisión con el autor) | revision | 3 | 12 | 219 | 1,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 100 It’s Rare to Have Competing, Viable, Scientific Theories (revisión con el autor) | revision | 6 | 40 | 669 | 3,9 | Revisión con el autor (7-nov): fundida una frase corta. Cero avisos |
| 2026-11-07 | 101 We’re All Equal in Our Infinite Ignorance (revisión con el autor) | revision | 3 | 17 | 303 | 1,8 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 102 It’s Easy to Extrapolate How Things Will Get Worse (revisión con el autor) | revision | 3 | 15 | 321 | 1,9 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 103 Pessimism Seems Like an Intellectually Serious Position (revisión con el autor) | revision | 2 | 19 | 353 | 2,1 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 104 Rational Optimism Is the Way Out (revisión con el autor) | revision | 3 | 21 | 381 | 2,2 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 105 The Beginning of Infinity, Part 1 (revisión con el autor) | revision | 73 | 704 | 12491 | 73,5 | Revisión con el autor (7-nov): título parte 1; cambios de 072, 082, 083, 092, 098 y 100 copiados de los cortos. Cero avisos |
| 2026-11-07 | 106 With a Good Theory of Knowledge, You Can Decide What Else Is True (revisión con el autor) | revision | 1 | 17 | 326 | 1,9 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 107 No Truth Can Be Justified (revisión con el autor) | revision | 1 | 20 | 427 | 2,5 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 108 There Can Be No Final Theory of Gravity (revisión con el autor) | revision | 2 | 38 | 644 | 3,8 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 109 Genetic Evolution Was a Prelude to Memetic Evolution (revisión con el autor) | revision | 1 | 21 | 471 | 2,8 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 110 Humans Are Exceptional (revisión con el autor) | revision | 1 | 24 | 429 | 2,5 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 111 We Are Qualitatively Different From Other Species (revisión con el autor) | revision | 1 | 17 | 302 | 1,8 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 112 More Compute Power Doesn’t Produce AGI (revisión con el autor) | revision | 1 | 15 | 319 | 1,9 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 113 It’s Mind Blowing That Our Minds Can’t Be Blown (revisión con el autor) | revision | 2 | 30 | 546 | 3,2 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 114 Where Are the Aliens? (revisión con el autor) | revision | 2 | 12 | 191 | 1,1 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 115 Intelligent Species Have Risen Only Once on Planet Earth (revisión con el autor) | revision | 1 | 31 | 584 | 3,4 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 116 The Probability of Human Existence Is Infinitesimally Small (revisión con el autor) | revision | 1 | 11 | 222 | 1,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 117 If You Can’t Program It, You Haven’t Understood It (revisión con el autor) | revision | 1 | 6 | 123 | 0,7 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 118 Aliens Might Just Be Too Far Away (revisión con el autor) | revision | 2 | 22 | 467 | 2,7 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 119 Aliens Would Visit for Knowledge, Not Resources (revisión con el autor) | revision | 2 | 26 | 475 | 2,8 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 120 Ideas Are the New Oil (revisión con el autor) | revision | 1 | 29 | 553 | 3,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 121 One Einstein Is Worth A Legion Of PhD Drones (revisión con el autor) | revision | 2 | 14 | 250 | 1,5 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 122 Don’t Rely on Credibility Stamps (revisión con el autor) | revision | 3 | 22 | 370 | 2,2 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 123 Innovation Requires Decentralization and a Frontier (revisión con el autor) | revision | 1 | 35 | 648 | 3,8 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 124 The Poverty of Compromise (revisión con el autor) | revision | 1 | 32 | 572 | 3,4 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 125 Free Markets Provide the Best Feedback (revisión con el autor) | revision | 2 | 30 | 556 | 3,3 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 126 Making Something Social Destroys the Truth of It (revisión con el autor) | revision | 1 | 27 | 490 | 2,9 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
| 2026-11-07 | 127 Groups Never Admit Failure (revisión con el autor) | revision | 1 | 27 | 442 | 2,6 | Revisión con el autor (7-nov): sin cambios. Cero avisos |
