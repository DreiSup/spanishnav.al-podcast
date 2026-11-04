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
