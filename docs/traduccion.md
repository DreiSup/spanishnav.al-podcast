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

| Fecha | Episodio | Estado | Bloques | Frases es | Palabras es | Min. | Notas |
|---|---|---|---|---|---|---|---|
| 2026-11-03 | 053 Live Long Enough and You'll Become a Philosopher | revision | 5 | 23 | 264 | 1,6 | Cero avisos. b02 en 0,84 por compresión de las preguntas |
