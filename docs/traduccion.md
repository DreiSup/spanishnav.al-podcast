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
| 2026-11-03 | 052 How to Get Rich (arreglo) | revision | 288 | 2883 | 42076 | 248 | 40 avisos a cero: 14 por vosotros, os, vale y chaval, 26 frases cortas fundidas. Detalle en notas y en el commit |
| 2026-11-03 | 057 Desire Is a Contract You Make to Be Unhappy | revision | 3 | 15 | 226 | 1,3 | Cero avisos |
| 2026-11-03 | 058 If You’re So Smart, Why Aren’t You Happy? | revision | 4 | 31 | 484 | 2,8 | Cero avisos. Título de sección confirmado por el autor; citas en estilo indirecto |
| 2026-11-03 | 059 Being Unhappy Is Extremely Inefficient | revision | 3 | 20 | 346 | 2,0 | Cero avisos. Artefacto del copiado en el inglés señalado en notas |
| 2026-11-03 | 060 Work the Least for It | revision | 2 | 17 | 302 | 1,8 | Cero avisos. S-1 resuelto en la frase |
| 2026-11-03 | 061 The Modern Struggle Is Fighting Weaponized Addiction | revision | 2 | 14 | 270 | 1,6 | Cero avisos. Citas en estilo indirecto |
| 2026-11-03 | 062 Breaking Addiction Is Socially Unacceptable | revision | 3 | 18 | 306 | 1,8 | Cero avisos |
| 2026-11-03 | 065 The Closer You Are to the Truth, the More Silent You Become Inside | revision | 2 | 13 | 224 | 1,3 | Cero avisos. Lao Tse, test de inteligencia y si A entonces B resueltos en la frase (GLOSARIO) |
