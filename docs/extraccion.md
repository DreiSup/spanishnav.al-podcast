# Protocolo de extracción de nav.al

## La decisión

**Los transcripts se cogen a mano.** Se abre la página del episodio en nav.al, se copia el
transcript y se pega en un fichero de texto del directorio de trabajo. Un script lo convierte
al formato del protocolo y el normalizador hace el resto.

Es una decisión del autor, tomada tras probar las dos alternativas automáticas:

| Vía | Qué pasó |
|---|---|
| **Claude web** (claude.ai) | Sirvió para el reconocimiento: catálogo, estructura de la página, reglas de parseo. Para el cuerpo del transcript, no: su fetch corta a ~100 KB y no reproduce el texto entero |
| **Script en local** contra nav.al | Escrito y probado contra fixtures, pero **nunca ejecutado contra la web real** (nav.al está bloqueado desde las sesiones web de Claude Code). Queda como alternativa, no como flujo |

## El reparto de trabajo

```
   tú, en el navegador          trabajo/manual/<slug>.txt      extraer-episodios.py        normalizar-extraccion.py
   ────────────────────         ─────────────────────────      ────────────────────        ────────────────────────
   abres nav.al/<slug>    ──►   pegas el transcript      ──►   lo convierte a bloques ──►  trocea en frases, asigna ids,
   copias el texto              marcas los encabezados         y deja JSON crudo            escribe los ficheros del repo
```

**Los ids de bloque los pone el normalizador, nunca una persona ni un modelo.** Son
`bNN-<speaker>` (`b01-nivi`, `b02-naval`, …) y salen de la posición del bloque, así que los
mismos datos dan siempre los mismos ids.

El **troceado en `frases` dentro de cada bloque es otra cosa**: no genera ficheros, es cómo
se le entrega el texto al TTS para que respire. En español lo decide quien traduce, porque
partir una frase larga o fundir un "Sí." suelto con la siguiente es una decisión de doblaje.
Por eso el número de frases no tiene por qué coincidir entre idiomas, y no coincide: en
`035-finally-wealthy` son 65 en inglés y 68 en español, con los mismos 4 bloques.

## Cómo se pega un episodio

Un fichero por episodio en `trabajo/manual/<slug>.txt`, donde `<slug>` es el de la URL
(`nav.al/finally-wealthy` → `finally-wealthy.txt`). El script cruza el slug con
`catalogo.json` y saca de ahí la URL y el título, así que no hace falta escribirlos.

```
fecha: 2019-05-21

Nivi: Primera intervención, tal como está en la página.

Naval: Segunda intervención.

Párrafo sin etiqueta: continúa la intervención de Naval.

## Encabezado de sección, tal como aparece en la página

Párrafo tras el encabezado: hereda el último hablante (Naval).

Nivi: Otra intervención.
```

Las reglas, que son las mismas que sigue la página:

| En el fichero | Significa |
|---|---|
| `Nombre: texto` al principio de un párrafo | Abre un turno de ese hablante |
| `## texto` | Encabezado de sección. **Hay que ponerle el `##` a mano**: al copiar, la negrita se pierde y sin la marca parecería un párrafo más |
| Párrafo sin etiqueta | Continúa el turno abierto. Tras un encabezado, hereda el hablante anterior |
| Línea en blanco | Separa párrafos. Las líneas seguidas dentro de un párrafo se unen |
| `fecha: AAAA-MM-DD` en la primera línea | Solo si el catálogo no la tiene (59 episodios de 2019 y 2020 vienen sin fecha). Está en la página, bajo el título |

`url:` y `titulo:` también se admiten en la cabecera, pero no hacen falta si el slug está en
el catálogo.

**Lo que no hay que hacer:** no trocear en frases, no corregir el texto, no traducir, no
quitar los nombres de los hablantes. Cuanto más literal, mejor.

## Conversión: `scripts/extraer-episodios.py`

```bash
python3 scripts/extraer-episodios.py                      # todos los .txt de trabajo/manual/
python3 scripts/extraer-episodios.py --solo finally-wealthy
```

Lee `trabajo/manual/*.txt`, aplica las reglas de arriba y deja un JSON por episodio en
`trabajo/extraccion/<slug>.json` con el formato del protocolo:

```json
{
  "url": "https://nav.al/finally-wealthy",
  "titulo": "A Calm Mind, a Fit Body, a House Full of Love",
  "fecha": "2019-05-21",
  "idioma": "en",
  "bloques": [
    { "tipo": "intervencion", "speaker": "Nivi", "texto": "…" },
    { "tipo": "intervencion", "speaker": "Naval", "texto": "…" },
    { "tipo": "seccion", "texto": "…" },
    { "tipo": "intervencion", "speaker": "Naval", "texto": "…", "speaker_inferido": true }
  ],
  "completo": true,
  "notas": "bloque 4: hablante inferido (Naval) tras un encabezado",
  "fuente": "manual"
}
```

Imprime una línea por episodio con bloques, palabras, hablantes y avisos. Los avisos son
la señal de revisar: un slug que no está en el catálogo, una fecha que falta, un hablante
que aparece una sola vez (probable errata al pegar).

`trabajo/` está en `.gitignore`: es el directorio de trabajo, no el repo.

Los modos `--modo api` y `--modo paginas` bajan de nav.al directamente. Existen, están
probados contra fixtures y no contra la web real, y **no forman parte del flujo**.

## Verificación antes de normalizar

1. **El contenido está en inglés.** Buscar palabras funcionales del español (`que`, `de`,
   `el`, `con`) en los bloques.
2. **Ningún bloque está vacío** ni contiene marcas de recorte: `[...]`, `…continúa`, `etc.`
3. **La longitud es plausible.** A ritmo de habla, ~130-160 palabras por minuto. Un episodio
   de 40 minutos por debajo de 3.000 palabras es que se pegó a medias.
4. **Los `speaker` son consistentes** dentro del episodio y entre episodios: `Naval`,
   `Nivi`, no `naval` en unos y `NAVAL` en otros. Un nombre que aparece una sola vez es
   casi seguro una errata.
5. **Los bloques `seccion` están intercalados**, no agrupados. Si aparecen todos juntos, se
   olvidó marcar alguno con `##` y el parser los ha tomado por párrafos.

Si algo falla, **se corrige el `.txt` y se relanza el script**. No se toca el JSON a mano.

## Reconocimiento con Claude web

Claude web sí llega a nav.al y sirve para lo que no requiere reproducir texto largo. Ya
se usó para:

- **El catálogo completo**: `catalogo.json` en la raíz, 168 entradas del archivo de nav.al
  (2026-09-07). El crudo está también en Drive, en `naval-podcast/_extraccion/`.
- **La regla de parseo de la página**, que es la que codifica el script: `<p>` con
  `<strong>Nombre:</strong>` abre turno; `<p>` todo en negrita es sección; `<p>` sin etiqueta
  continúa el turno y hereda el hablante tras un encabezado.

Para ampliar el catálogo cuando salgan episodios nuevos, en una conversación nueva de
claude.ai:

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

`scripts/normalizar-extraccion.py` — **por escribir, contra el primer episodio pegado de
verdad** — convierte `trabajo/extraccion/*.json` en los ficheros del repo:

- Trocea cada intervención en frases y asigna ids correlativos (`0001`, `0002`, …)
- Aplica la regla de numeración de arriba para decidir carpeta y `numero`
- Escribe `transcript.en.json` y `metadata.en.json` en `episodios/<año>/<NNN>-<slug>/`
- Crea `metadata.es.json` en estado `pendiente`
- Deja un informe de lo que ha creado, actualizado y saltado
