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

## Encargo 1 — El catálogo

Se hace **una sola vez**. De aquí salen la lista de URLs, los años y la numeración.

```
Ve a nav.al y localiza el índice de episodios del podcast de Naval.

Necesito el catálogo COMPLETO, desde el primer episodio hasta el último publicado.
Si el índice está paginado, recórrelo entero.

Devuélveme un único bloque JSON con esta forma exacta:

{
  "fuente": "<url del índice que has usado>",
  "extraido_el": "<fecha de hoy AAAA-MM-DD>",
  "total": <número de episodios>,
  "episodios": [
    {
      "orden": 1,
      "titulo": "<título literal>",
      "fecha": "<AAAA-MM-DD>",
      "url": "<url completa>",
      "tiene_transcript": true
    }
  ]
}

Reglas:
- "orden" es la posición cronológica ascendente: 1 = el más antiguo de todos.
- Títulos literales: no los traduzcas ni los normalices.
- Si no puedes determinar la fecha de alguno, pon "" y menciónalo aparte.
- "tiene_transcript": true solo si has comprobado que la página tiene transcript.
  Si no lo has comprobado, pon null.
- Si alguna página no carga, dilo explícitamente. NO inventes entradas.

Al terminar, dime cuántos episodios has encontrado por cada año.
```

Se entrega como `catalogo.json`.

## Encargo 2 — Un episodio

Se repite **por cada URL** del catálogo.

```
Abre <URL> y extrae el transcript.

CRÍTICO: quiero el texto LITERAL, palabra por palabra. No resumas, no parafrasees,
no acortes, no arregles la gramática y no omitas nada. Si el transcript es largo,
prefiero varias respuestas encadenadas a una sola respuesta recortada.

Devuélveme un único bloque JSON con esta forma:

{
  "url": "<url>",
  "titulo": "<título literal de la página>",
  "fecha": "<AAAA-MM-DD>",
  "titulos_seccion": ["<encabezados que aparezcan dentro del transcript, en orden>"],
  "bloques": [
    {
      "speaker": "<nombre tal y como aparece en la página>",
      "texto": "<texto literal e íntegro de esa intervención>"
    }
  ]
}

Reglas:
- Un objeto en "bloques" por cada intervención, en el orden en que aparecen.
- "texto" es el bloque entero de esa intervención. NO lo trocees en frases:
  de eso se encarga un script después.
- Conserva las comillas, los guiones y los énfasis como texto plano.
- Si la página no tiene transcript, devuelve "bloques": [] y dilo.
- Si no consigues abrir la página, dilo. NO la reconstruyas de memoria.

Al terminar, dime dos números: cuántos bloques has devuelto y cuántas palabras
tiene el transcript aproximadamente.
```

Se entrega como `<slug>.json`.

### Si el episodio no cabe en una respuesta

Que corte por bloque completo, nunca a mitad de uno, y que siga con:

```
Continúa desde el bloque <N>, con el mismo formato. Solo el JSON de los bloques
que faltan, sin repetir los anteriores.
```

Al unir las partes, los bloques deben quedar consecutivos y sin solapamiento.

---

## Verificación al recibir

Antes de dar por bueno un episodio se comprueba, en este orden:

1. **Parsea como JSON** y tiene las claves del esquema.
2. **El número de bloques coincide** con el que declaró el modelo.
3. **Ningún bloque está vacío** ni contiene marcas de recorte: `[...]`, `…continúa`,
   `(resumen)`, `etc.`
4. **La longitud es plausible.** A ritmo de habla normal, ~130-160 palabras por minuto. Un
   episodio de 40 minutos por debajo de 3.000 palabras es sospechoso de resumen, no de
   brevedad.
5. **Los `speaker` son consistentes** en todo el episodio y entre episodios. `Naval`,
   `Nivi`, no `naval` en unos y `NAVAL` en otros.
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
