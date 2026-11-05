# Episodios cortos que son trozos de un largo

Análisis del 5-nov (sesión de dirección), a petición del autor: **no generar dos veces el mismo texto**. Método:
comparación del inglés por n-gramas de 8 palabras (repo y Google Docs anuales «20XX all podcasts»); en los grupos
ya traducidos, también del español frase a frase.

## Resumen

| Largo (número) | Cortos dentro | Cobertura del largo | Qué hacer |
|---|---|---|---|
| **077** Happiness | 053–067 (15) | 100 % | Generar el largo; montar los cortos con sus clips |
| **105** The Beginning of Infinity, Part 1 | 072–076 y 078–104 (32) | 100 % | Ídem |
| **130** The Beginning of Infinity, Part 2 | 106–129 (24) | 100 % | Ídem |
| **154** In the Arena (2025) | 139–145 y 147–153 (14; el 146 es un anuncio suelto) | 99,7 % | Ídem, tras traducir **solo el largo** |
| **160** The AI Industrial Revolution (2026) | las 3 partes sin número (Waste Tokens, Vibe Coding Hardware, The Regulatory Frontier) | 74,6 % (el resto es una «parte 4» que no salió como episodio) | Ídem |
| **052** How to Get Rich (recopilación) | 001–050 (salvo 039) | 95 % | **Al revés**: generar los cortos y montar el 052 uniendo sus masters |

Números según la regla de `docs/extraccion.md` (orden del archivo − 4; los de 2026, − 7).

## Los grupos que se cortan (077, 105, 130)

Comprobado en el repo:

- Cada corto es un **tramo seguido** de frases del largo, en el mismo orden, sin texto propio, y entre todos lo
  cubren entero.
- **El español es idéntico**: cada corto coincide frase a frase con su tramo del largo.
- **Todos empiezan en un bloque de hablante.** Por eso el master de un corto es la unión de los clips de sus bloques
  (los que la fábrica deja en `tts/` al generar el largo): sin GPU y sin recortar audio.

## 154 In the Arena y 160 The AI Industrial Revolution (aún sin traducir)

- Sus cortos solo están en los Google Docs de 2025 y 2026 (inglés). Para que el truco funcione, la sesión de
  traducción debe **traducir el largo y sacar el `transcript.es.json` de cada corto copiando su tramo de frases tal
  cual**, con los cortes en límite de bloque.
- Texto propio de los cortos (hablado):
  - *Inspiration All the Way Down* (139): unas 35 palabras de intro de Nivi que el largo recorta.
  - *Waste Tokens, Save Time*: «Welcome, you're listening to the» (5 palabras).

  O se genera ese bloque aparte (segundos de GPU) o se acepta la intro del largo.
- Las notas «See Part I here» y «Part 3 of our four part discussion…» son texto de la web, no audio.

## 052 How to Get Rich: al revés

- El inglés de 001–050 está en el 052 (017–034, en un bloque continuo y en orden).
- **El español del 052 se tradujo aparte**: los cortos 001–045 solo comparten entre el 26 y el 63 % del texto con él.
  Cortarlo daría cortos cuyo audio no corresponde a su transcripción.
- Ya hay 19 cortos generados (001–016, 037–039).
- Por eso: generar los cortos y **montar el 052 uniendo sus masters**, como ya recomendaba la sesión técnica
  (`docs/contexto-sesion-global.md`, §7.1). Así, además, cada unión puede ser un capítulo de YouTube.
- Quedan unas 1.800 palabras del 052 sin corto: el final, que parece *Finding Time to Invest in Yourself*
  (13-ene-2020). No está en el catálogo ni en los Docs.
- **Pendiente: decisión del autor sobre si se publica el 052.**

## Largos sin cortos (se generan tal cual)

051, 069 (angel investing), 068 (Kapil), 070, 071 (Ridley), 131, 132 (Vitalik), 133, 134 (Deutsch), The Deutsch
Files I–IV, Curate People, A Motorcycle for the Mind, A Return to Code, 'Nothing Ever Happens' Is Over, Sell the
Truth.

## Sin comprobar

- Los 4 diálogos con Kapil Gupta de 2019 (extras): no hay texto en Drive ni en el catálogo.
- *Live in the Future* (161): el Doc solo trae la descripción.

## Cambio técnico que hace falta (para la sesión técnica)

> **Montar el master de un corto con los clips del largo.** Entrada: el episodio largo y, para cada corto, qué
> bloques del largo le corresponden (se deduce comparando frases, porque el español es idéntico). Salida: en la
> carpeta del corto en Drive, `audio/<NNN>-<slug>.mp3` (mismo formato, misma pausa de 0,6 s y mismo -16 LUFS que la
> fábrica), su `informe_tts.md` y su `indice_master.tsv`. Sin GPU, como `SOLO_MASTER`.
>
> **Y al revés, para el 052:** unir los masters de los cortos en el orden del 052 (el 042 va entre el 011 y el 012).
