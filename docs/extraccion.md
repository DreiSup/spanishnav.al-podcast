# Protocolo de extracción de nav.al

## Por qué existe este documento

**nav.al está bloqueado desde las sesiones web de Claude Code.** La política de egress
devuelve 403 en el CONNECT (comprobado con `curl -sS "$HTTPS_PROXY/__agentproxy/status"`),
así que la sesión que escribe el código no puede abrir la web de la que salen los datos.

**Claude web (claude.ai) sí puede.** De ahí este reparto: Claude web extrae, Claude Code
normaliza y versiona.

## El reparto de trabajo

```
   claude.ai                      repo / Claude Code
   ─────────                      ──────────────────
   abre nav.al                    normaliza a los esquemas
   saca el texto literal   ──►    trocea en frases
   marca quién habla              asigna los ids
   entrega JSON crudo             valida y commitea
```

**A Claude web no se le pide el `transcript.en.json` final.** Se le pide un JSON crudo con
los bloques de intervención en texto literal. El troceo en frases y la numeración de ids los
hace un script, por tres razones:

1. **Reproducibilidad.** Un modelo trocea distinto cada vez; un script no. Los ids son la
   pieza que mantiene unidos el transcript, la traducción y los clips de TTS: no pueden
   depender de una tirada concreta.
2. **Revisabilidad.** Si mañana cambia la regla de segmentación, se re-ejecuta el script
   sobre lo ya extraído. No hay que volver a pedir nada.
3. **Menos superficie de error.** Cuanto menos transforme el modelo, menos ocasiones tiene de
   parafrasear sin querer.

## El riesgo real, y cómo se controla

Un modelo al que le pides "extrae este texto" tiende a **resumir, limpiar la gramática o
recortar**. Es el fallo característico de este montaje, y no se detecta a simple vista: el
resultado parece correcto. Los encargos de abajo lo atacan de frente, y las comprobaciones
de la última sección lo verifican.

El otro riesgo es el **relleno**: si una página no carga, un modelo puede reconstruirla de
memoria en vez de decir que falló. Por eso los dos encargos terminan con la misma
instrucción explícita: si no llegas, dilo; no inventes.

## Canal de entrega

Por orden de preferencia:

| Canal | Cuándo |
|---|---|
| **Google Drive** | El mejor. Claude web escribe en `naval-podcast/_extraccion/`, y Claude Code lo lee desde ahí con el conector. Sin pasos manuales |
| | La carpeta ya existe: [`_extraccion`](https://drive.google.com/drive/folders/1mYhx3hrYcs2QtCJTL9dHNvL0yIwR6BPs) — su ID está en `drive.json` |
| **Rama del repo** | Para lotes grandes: guardas los JSON, `git push` a una rama `extraccion/...` y aquí se hace fetch |
| **Pegado en el chat** | Para un episodio suelto o para probar |

---

## Prompt maestro

Esto se pega **una vez** al empezar la conversación con Claude web. Fija las reglas y los
dos formatos; después basta con ir mandando URLs.

```
Estoy construyendo un repositorio con las transcripciones del podcast de Naval
(nav.al) para después traducirlas al español. Tu papel es EXTRAER; la traducción
y el procesado los hace otro sistema.

Necesito que entiendas por qué importa la literalidad: el texto que me des se
convierte en la fuente de verdad del proyecto. Si resumes, corriges o traduces,
nadie podrá detectarlo después, porque el sistema que recibe tu salida no puede
abrir nav.al.

REGLAS, en orden de importancia:

1. NO TRADUZCAS. Devuelve el texto en el idioma en que está la página, que es
   inglés. Ni una palabra en español dentro del contenido.
2. NO TROCEES en frases. Cada intervención va entera en un solo campo de texto.
   El troceo lo hace un script después, y tiene que ser reproducible.
3. NO RESUMAS, no parafrasees, no acortes, no corrijas erratas ni gramática,
   no reordenes, no omitas nada.
4. NO INVENTES. Si no consigues abrir una página o no la lees entera, dilo
   claramente. Nunca la reconstruyas de memoria.
5. Devuelve SIEMPRE un único bloque de código JSON válido, sin texto explicativo
   dentro del bloque.

Te voy a pedir dos cosas distintas. Cada una tiene su formato exacto.
```

## Encargo 1 — El catálogo

Se lanza **una sola vez**. De aquí salen la lista de URLs, los años y la numeración.

```
ENCARGO: CATÁLOGO

Localiza en nav.al el índice de episodios del podcast. Necesito el catálogo
COMPLETO, del primer episodio al último publicado. Si está paginado, recórrelo
entero.

Formato de salida:

{
  "fuente": "<url del índice que has usado>",
  "extraido_el": "<hoy, AAAA-MM-DD>",
  "total": <número de episodios>,
  "episodios": [
    {
      "orden": 1,
      "titulo": "<título literal, en inglés>",
      "fecha": "<AAAA-MM-DD>",
      "url": "<url completa>",
      "tiene_transcript": true
    }
  ]
}

- "orden" es la posición cronológica ascendente: 1 = el más antiguo de todos.
- "fecha" SIEMPRE en AAAA-MM-DD. Si no la sabes, pon "" y dímelo aparte.
- "tiene_transcript": true solo si lo has comprobado. Si no, null.

Fuera del bloque JSON, dime cuántos episodios hay por cada año.
```

Se entrega como `catalogo.json`.

## Encargo 2 — Un episodio

Se repite **por cada URL** del catálogo.

```
ENCARGO: EPISODIO
URL: <pega aquí la url>

Extrae la transcripción completa de esa página, en inglés y literal.

Formato de salida:

{
  "url": "<la url que te he dado>",
  "titulo": "<título literal de la página, en inglés>",
  "fecha": "<AAAA-MM-DD>",
  "idioma": "en",
  "bloques": [
    { "tipo": "seccion", "texto": "<encabezado tal como aparece>" },
    { "tipo": "intervencion", "speaker": "Naval", "texto": "<intervención entera>" }
  ],
  "completo": true,
  "notas": ""
}

Sobre "bloques", que es lo importante:
- Un elemento por cada cosa que aparece en la página, EN EL MISMO ORDEN.
- Los encabezados de sección van como bloques "seccion" EN SU SITIO, entre las
  intervenciones que separan. No los saques a una lista aparte: necesito saber
  dónde cae cada uno.
- "speaker" es el nombre tal y como aparece en la página, siempre igual escrito.
- "texto" es la intervención COMPLETA. Sin trocear en frases.
- Conserva comillas, guiones y énfasis como texto plano.

Otros campos:
- "completo": false si te has dejado algo por cualquier motivo.
- "notas": cualquier cosa rara que hayas visto. Vacío si no hay nada.
- Si la página no tiene transcripción: "bloques": [] y dímelo.

Fuera del bloque JSON dime tres datos: cuántos bloques, cuántas palabras
aproximadamente, y si el texto está completo o cortado.
```

Se entrega como `<slug>.json`.

### Si el episodio no cabe en una respuesta

Que corte **por bloque completo**, nunca a mitad de uno, ponga `"completo": false` y siga
con:

```
Continúa desde el bloque <N>, mismo formato. Solo los bloques que faltan,
sin repetir los anteriores.
```

Al unir las partes los bloques deben quedar consecutivos y sin solapamiento.

## Verificación al recibir

Antes de dar por bueno un episodio se comprueba, en este orden:

0. **El contenido está en inglés.** La primera comprobación, porque es el fallo que ya
   ocurrió una vez: se pidió el original y llegó traducido al español. Basta con buscar
   palabras funcionales del español (`que`, `de`, `el`, `con`) en el texto de los bloques.
1. **Parsea como JSON**, tiene las claves del esquema y `completo` es `true`.
2. **El número de bloques coincide** con el que declaró el modelo.
3. **Ningún bloque está vacío** ni contiene marcas de recorte: `[...]`, `…continúa`,
   `(resumen)`, `etc.`
4. **La longitud es plausible.** A ritmo de habla normal, ~130-160 palabras por minuto. Un
   episodio de 40 minutos por debajo de 3.000 palabras es sospechoso de resumen, no de
   brevedad.
5. **Los `speaker` son consistentes** en todo el episodio y entre episodios. `Naval`,
   `Nivi`, no `naval` en unos y `NAVAL` en otros.
5. **Los bloques `seccion` están intercalados**, no agrupados al principio ni al final. Si
   vienen todos juntos, el modelo ha perdido su posición en el texto.
6. **Prueba de determinismo, por muestreo.** Una de cada diez extracciones se repite en una
   conversación nueva y se comparan. Si el texto difiere más allá de espacios, el modelo está
   reescribiendo y hay que endurecer el encargo.

Un episodio que no pase 3 o 4 se vuelve a pedir. No se parchea a mano: si el texto llegó
mal, el original es la fuente de verdad, no nuestra corrección.

## Después de la verificación

`scripts/normalizar-extraccion.py` — **por escribir** — convierte los JSON crudos en los
ficheros del repo:

- Trocea cada `bloque.texto` en frases y les asigna ids correlativos (`0001`, `0002`, …)
- Escribe `transcript.en.json` y `metadata.en.json` en `episodios/<año>/<NNN>-<slug>/`
- Crea `metadata.es.json` en estado `pendiente`
- Deriva el slug del título y el `NNN` del `orden` del catálogo

Se escribe cuando llegue la primera extracción real, para poder probarlo contra datos de
verdad en vez de contra un ejemplo inventado.

Los JSON crudos se conservan en una rama aparte o en Drive, no en la rama de trabajo: son la
evidencia de qué se extrajo y cuándo, pero no son fuente de verdad. La fuente de verdad es
`transcript.en.json`.
