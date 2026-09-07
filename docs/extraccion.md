# Protocolo de extracción de nav.al

## Por qué existe este documento

**nav.al está bloqueado desde las sesiones web de Claude Code.** La política de egress
devuelve 403 en el CONNECT (comprobado con `curl -sS "$HTTPS_PROXY/__agentproxy/status"`),
así que la sesión que escribe el código no puede abrir la web de la que salen los datos.

Se probaron dos vías y cada una sirve para una cosa distinta:

| Vía | Sirve para | No sirve para |
|---|---|---|
| **Claude web** (claude.ai) | Reconocimiento: catálogo, estructura de la página, reglas de parseo | El texto de los transcripts: su fetch corta a ~100 KB y no reproduce el cuerpo entero |
| **Script en local** | Descargar y parsear los 168 episodios de forma determinista | Nada. Es la vía de producción |

La conclusión: **Claude web reconoce, el script descarga, Claude Code normaliza y versiona.**

## El reparto de trabajo

```
   claude.ai                 tu máquina                       repo / Claude Code
   ─────────                 ──────────                       ──────────────────
   catálogo                  descargar-episodios.py           normalizar-extraccion.py
   reglas de parseo   ──►    baja la API de WordPress   ──►   trocea en frases
   estructura                parsea el HTML                   asigna ids, valida, commitea
                             deja JSON crudo en trabajo/
```

**El troceo en frases y la numeración de ids nunca los hace un modelo.** Los hace un script,
por tres razones:

1. **Reproducibilidad.** Un modelo trocea distinto cada vez; un script no. Los ids son la
   pieza que mantiene unidos el transcript, la traducción y los clips de TTS.
2. **Revisabilidad.** Si cambia la regla de segmentación, se re-ejecuta sobre lo ya
   descargado. No hay que volver a bajar nada.
3. **Menos superficie de error.** Cuanto menos transforme un modelo, menos ocasiones tiene
   de parafrasear sin querer.

## Lo que ya se ha hecho

- **Catálogo completo**: `catalogo.json` en la raíz del repo, 168 entradas del archivo de
  nav.al, extraído por Claude web el 2026-09-07. El JSON crudo original está también en
  Drive, en `naval-podcast/_extraccion/`.
- **Regla de parseo del HTML**, confirmada por Claude web contra una página real y
  codificada en `scripts/descargar-episodios.py`:
  - `<p>` que empieza por `<strong>Nombre:</strong>` abre un turno de ese hablante
  - `<p>` cuyo contenido entero es un `<strong>` es un encabezado de sección
  - `<p>` sin etiqueta continúa el turno abierto; tras un encabezado, el hablante se hereda
- **Fecha** en `<meta property="article:published_time">` y, mejor, en la API.

## Descarga: `scripts/descargar-episodios.py`

Se ejecuta **en local**. Solo biblioteca estándar; no hay que instalar nada.

```bash
python3 scripts/descargar-episodios.py --solo finally-wealthy   # uno, para probar
python3 scripts/descargar-episodios.py --anio 2019              # un año
python3 scripts/descargar-episodios.py                          # los 168
python3 scripts/descargar-episodios.py --sin-red                # reprocesa sin descargar
```

**Fuente principal: la API REST de WordPress** de nav.al
(`/wp-json/wp/v2/posts?per_page=100&_fields=…`). Devuelve fecha, título y el HTML del
contenido de todos los posts en dos o tres peticiones. Es más rápida y más estable que
rascar 168 páginas, y resuelve de paso las 59 fechas que el archivo no mostraba.

**Respaldo**: `--modo paginas` descarga cada URL del catálogo y parsea el `<article>`. Para
cuando la API no responda.

Salida, por episodio, en `trabajo/extraccion/<slug>.json`:

```json
{
  "url": "https://nav.al/…",
  "titulo": "…",
  "fecha": "2019-05-21",
  "fecha_gmt": "2019-05-21T19:22:57",
  "idioma": "en",
  "bloques": [
    { "tipo": "intervencion", "speaker": "Nivi", "texto": "…" },
    { "tipo": "seccion", "texto": "…" },
    { "tipo": "intervencion", "speaker": "Naval", "texto": "…", "speaker_inferido": true }
  ],
  "completo": true,
  "notas": "bloque 4: hablante inferido (Naval) tras un encabezado",
  "fuente": "wp-json",
  "descargado_el": "2026-09-07"
}
```

`trabajo/` está en `.gitignore`. Es el directorio de trabajo; lo que se versiona sale del
normalizador. Las respuestas crudas de la API quedan en `trabajo/wp-json/` como evidencia y
como fixtures para depurar el parser sin red.

El parser está probado contra un fixture sintético que reproduce la estructura de
`finally-wealthy` tal como la describió Claude web (10 bloques: 7 intervenciones y 3
secciones, hablante heredado tras cada encabezado). **No se ha ejecutado todavía contra la
web real.** La primera ejecución en local es la prueba de verdad.

## Verificación al recibir

Sobre la salida del script, antes de normalizar:

1. **El contenido está en inglés.** Buscar palabras funcionales del español (`que`, `de`,
   `el`, `con`) en los bloques. Fue el fallo del primer intento con Claude web.
2. **Parsea como JSON**, tiene las claves del esquema y `completo` es `true`.
3. **Ningún bloque está vacío** ni contiene marcas de recorte: `[...]`, `…continúa`, `etc.`
4. **La longitud es plausible.** A ritmo de habla, ~130-160 palabras por minuto. Un episodio
   de 40 minutos por debajo de 3.000 palabras es sospechoso.
5. **Los `speaker` son consistentes** dentro del episodio y entre episodios: `Naval`,
   `Nivi`, no `naval` en unos y `NAVAL` en otros.
6. **Los bloques `seccion` están intercalados**, no agrupados. Si vienen todos juntos, el
   parser ha perdido su posición.
7. **`NO ENCONTRADOS` y `SIN BLOQUES` del informe final están vacíos** o explicados: un
   episodio sin transcript en la página es legítimo; uno que la API no devuelve, no.

Un episodio que no pase 3 o 6 apunta a un caso del HTML que el parser no contempla. Se
guarda el HTML, se añade al fixture y se corrige el parser; **no se parchea el JSON a mano**.

## Encargo de reconocimiento (Claude web)

Se conserva para cuando salgan episodios nuevos y haya que ampliar el catálogo. Se pega
en una conversación nueva de claude.ai:

```
Localiza en nav.al el índice de episodios del podcast. Necesito el catálogo
COMPLETO, del primer episodio al último publicado. Si está paginado, recórrelo
entero.

Devuélveme un único bloque JSON:

{
  "fuente": "<url del índice que has usado>",
  "extraido_el": "<hoy, AAAA-MM-DD>",
  "total": <número de episodios>,
  "episodios": [
    {"orden": 1, "titulo": "<literal, en inglés>", "fecha": "<AAAA-MM-DD o vacío>",
     "url": "<url completa>", "tiene_transcript": true}
  ]
}

- "orden" es la posición cronológica ascendente: 1 = el más antiguo.
- No inventes entradas. Si una página no carga, dilo.
Fuera del JSON, dime cuántos episodios hay por año.
```

Las entradas nuevas se añaden a `catalogo.json` con su `orden` a continuación del último.

## Del catálogo a la numeración

El archivo de nav.al lista **168** entradas. El podcast, según Apple Podcasts, tiene
**161** episodios. La diferencia son 7 entradas que no son episodios del feed:

| Orden en el archivo | Qué es | Trato |
|---|---|---|
| 1–4 | Diálogos con Kapil Gupta, enero-febrero 2019, anteriores al primer episodio | `extra-<slug>`, sin número |
| 164–166 | Partes sueltas de *The AI Industrial Revolution*, ya retiradas del RSS | `extra-<slug>`, sin número |

La decisión es **numerar por el feed**, porque es lo que ve un oyente y porque coincide con
la numeración de las carpetas locales antiguas (comprobado: *Judgment* era la carpeta 26 y
en el archivo es el orden 30, desfase exactamente 4).

Regla de correspondencia, `orden` del archivo → `numero` del episodio:

```
orden 1–4      → extra (sin número)
orden 5–163    → numero = orden − 4        (1 … 159)
orden 164–166  → extra (sin número)
orden 167–168  → numero = orden − 7        (160, 161)
```

Los extras se guardan en `episodios/<año>/extra-<slug>/` con los mismos cuatro ficheros
y `numero: null` en ambos metadata. Nada queda fuera del repo.

## Después de la verificación

`scripts/normalizar-extraccion.py` — **por escribir, contra la primera salida real** —
convierte `trabajo/extraccion/*.json` en los ficheros del repo:

- Trocea cada intervención en frases y asigna ids correlativos (`0001`, `0002`, …)
- Aplica la regla de numeración de arriba para decidir carpeta y `numero`
- Escribe `transcript.en.json` y `metadata.en.json` en `episodios/<año>/<NNN>-<slug>/`
- Crea `metadata.es.json` en estado `pendiente`
- Deja un informe de lo que ha creado, actualizado y saltado
