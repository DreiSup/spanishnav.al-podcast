# Prompts para las sesiones de revisión por invitado

Una sesión por invitado o tema, para revisar los transcripts y las traducciones de su serie. Se pega el
**bloque común** y, debajo, el **bloque del invitado**. Versión del 4-nov, tras el workflow que tradujo los 72
episodios que faltaban hasta 2023 y el fallo de «recetas» en el 068.

## Bloque común

```
Trabajo en el repositorio spanishnav.al-podcast: el doblaje al español del podcast de Naval Ravikant. Esta
sesión es de REVISIÓN de una sola serie (la indico abajo): revisar el inglés y la traducción de sus
episodios, fijar con el autor su terminología y dejarlos listos para la fábrica de voz. La parte técnica
(fábrica, voces, Colab, Drive) la lleva otra sesión; no la toques.

RAMA: claude/quirky-dirac-x18c3n, la que clona la fábrica. Antes de cada push:
"git pull --no-rebase origin claude/quirky-dirac-x18c3n" (merge, nunca rebase ni force-push). No abras PRs.

LEE ANTES DE EMPEZAR:
1. CLAUDE.md entero.
2. GLOSARIO.md: criterios generales, términos fijos y la sección «Términos por invitado» de tu serie. Esos
   términos los propuso un agente especialista el 4-nov y ESTÁN PENDIENTES DE VISTO BUENO DEL AUTOR.
3. docs/briefs/<grupo>.md: el brief de tu serie (registro de cada hablante, términos con su fuente, títulos
   publicados en español, nombres difíciles para el TTS, trampas).
4. docs/revision-episodios.md (protocolo de revisión) y docs/traduccion.md (registro de lo hecho).

LO PRIMERO, ANTES DE TOCAR NINGÚN EPISODIO: repasa con el autor los términos clave de tu serie (los del
GLOSARIO y las decisiones que figuran en el campo notas de cada metadata.es.json) y pídele que los confirme
o los cambie. Es lo que falló en el 068: «prescriptions» se tradujo como «recetas», el episodio se sintetizó
antes de que el autor lo confirmara y tuvo que corregirse a «prescripciones». Un término clave no se da por
bueno hasta que el autor lo dice.

CÓMO REVISAS CADA EPISODIO:
- Lee episodios/<año>/<NNN>-<slug>/transcript.en.json y transcript.es.json enteros, bloque a bloque y
  frase a frase: fidelidad (nada omitido ni añadido, cifras, negativos, quién dice qué), naturalidad leída
  en voz alta (fuera calcos), terminología confirmada y reglas para el TTS (las de GLOSARIO.md: sin
  comillas, guiones, paréntesis, punto y coma ni cifras; ¿ y ¡ siempre; castellano de España en tuteo
  singular; citas en estilo indirecto; frases de 8 a 35 palabras y ninguna afirmación suelta de una o dos).
- Edita solo las frases y los títulos de transcript.es.json: nunca ids, hablantes ni número de bloques. El
  inglés no se toca (sus artefactos del copiado están señalados en notas).
- Comprueba con
    python3 scripts/normalizar-extraccion.py episodios/<año>/<ep>/transcript.en.json \
      episodios/<año>/<ep>/transcript.es.json --slug <slug> --simular
  hasta cero avisos. NUNCA lo lances sin --simular: pisaría metadata.es.json.
- Apunta lo que cambias en el campo notas de metadata.es.json, ejecuta python3 scripts/indice.py, un commit
  por episodio, su línea en docs/traduccion.md y push. No cambies el estado: el paso a «tts» lo da el autor.

DEPENDENCIAS ENTRE EPISODIOS (si cambias una frase, cámbiala en todos donde esté):
- 046–050 son fragmentos de 052 How to Get Rich y reutilizan su texto.
- 077 Happiness es la recopilación de 053–067.
- 105 y 130 (The Beginning of Infinity, partes 1 y 2) son las recopilaciones de 072–104 y 106–129.
- Un término que cambia en un episodio cambia en toda la serie y en GLOSARIO.md.

AVISO SOBRE EL INGLÉS: el troceo del normalizador se come la comilla de cierre que sigue a un punto, así que
en transcript.en.json algunas citas parecen abiertas. En el documento original están cerradas. No es un
fallo de la traducción; está anotado para la sesión técnica.

AL TERMINAR CADA TANDA: resumen corto para el autor (episodios revisados, qué cambiaste, qué le preguntas) y
una línea con los números de episodio listos para verificar.
```

## Bloques por invitado

### Kapil Gupta

```
SERIE: Kapil Gupta. Episodio: 068 Kapil Gupta: Conquering the Mind (episodios/2020/068-kapil). Brief:
docs/briefs/kapil.md (su decisión D1, «recetas», está anulada).
Ya decidido por el autor: prescriptions = prescripciones (convertir en prescripción, de forma prescriptiva,
los que dan prescripciones). Hay que volver a sintetizar el 068.
Por confirmar: el título (Conquistar la mente, con Kapil Gupta), freedom from the mind = libertad frente a la
mente, There is no other = no existe el otro, journey / destination = el camino / el destino, sincerity =
sinceridad, mindfulness y coach (o atención plena y mentor).
Futuro: los cuatro diálogos de 2019 (extras sin audio: On Meditation, On Humility, A Founder's Anxiety, The
Need for Indifference) usarán la misma terminología si el autor decide hacerlos.
```

### Naval y Nivi

```
SERIE: Naval y Nivi. Episodios: 046–050 (microeconomía, 2019), 069 How to Angel Invest Part 2 y 077
Happiness (recopilación de 053–067). Brief: docs/briefs/naval_nivi.md. Modelos aprobados: 044, 051–067.
Por confirmar: compounding = componer (relaciones que se componen), net present value = valor presente
neto, VC = capital riesgo, dealflow = flujo de operaciones, repeat / first-time founder = fundador que
repite / fundador primerizo, coachable, Glengarry Glen Ross = Éxito a cualquier precio, y el título del 069
(Cómo invertir como ángel, parte dos).
Recuerda: 046–050 comparten texto con 052, y 077 con 053–067; un cambio se propaga.
```

### Brett Hall y David Deutsch

```
SERIE: Brett Hall y David Deutsch. Episodios: 072–130 (serie de 2021 sobre El comienzo del infinito, con
las recopilaciones 105 y 130) y 133–134 (entrevistas de 2023 con Deutsch). Brief:
docs/briefs/brett_deutsch.md. Son 61 episodios: trabaja por tandas en orden de feed.
Por confirmar antes de nada: good explanation = buena explicación, hard to vary = difícil de variar,
reach = alcance, universal explainer = explicador universal, conjecture / guess = conjetura, falsifiable =
falsable, testable = comprobable, error correction = corrección de errores, compromise = término medio
(124: La miseria del término medio), AGI = inteligencia artificial general, aliens = extraterrestres,
The Beginning of Infinity = El comienzo del infinito, The Fabric of Reality = La estructura de la realidad,
Nullius in verba escrito «nulius in verba» para el TTS, y el estilo de títulos de las partes (105, 130,
133, 134: «primera parte» frente al «parte uno» del 051).
Recuerda: 105 y 130 reutilizan las frases de los cortos; un cambio en un corto va también a su recopilación.
```

### Matt Ridley

```
SERIE: Matt Ridley. Episodios: 070 y 071 Matt Ridley: How Innovation Works, Parts 1 y 2. Brief:
docs/briefs/ridley.md.
Por confirmar: How Innovation Works = Claves de la innovación (edición española) y los títulos de los
episodios (Matt Ridley, claves de la innovación, parte uno / parte dos), invention / innovation =
invención / innovación, chiefs, priests and thieves = gobernantes, sacerdotes y ladrones, blockchain =
cadena de bloques, crypto = cripto, y la corrección de «Oliver» a «Orville» Wright (errata del copiado en
el inglés).
```

### Vitalik Buterin

```
SERIE: Vitalik Buterin (con Haseeb Qureshi). Episodios: 131 y 132 Vitalik: Ethereum, Parts 1 y 2. Brief:
docs/briefs/vitalik.md.
Por confirmar: blockchain = cadena de bloques, smart contract = contrato inteligente, proof of work /
proof of stake = prueba de trabajo / prueba de participación, sharding = fragmentación, rollups (en inglés,
escuchar), Layer 1 / Layer 2 = capa uno / capa dos, Eth = Ethereum (la red) o ether (el activo), wallet =
monedero, hack = ataque, y los títulos de los episodios (Vitalik: Ethereum, primera parte / segunda parte).
Muchos términos en inglés: escucha cómo los lee el TTS antes de dar el episodio por bueno.
```
