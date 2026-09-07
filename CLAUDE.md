# CLAUDE.md

Guía operativa del repositorio. Léela entera antes de tocar nada.

## Propósito

Producir y publicar **la traducción al español del podcast de Naval**. El resultado final
son vídeos en YouTube: audio doblado con TTS sobre una miniatura fija.

Este repositorio es la **fuente de verdad textual** de ese proceso. No es una web, no es
una publicación y no se despliega en ningún sitio.

## La regla que lo explica todo

> **GitHub guarda texto y punteros. Google Drive guarda bytes.**

En git entra solo lo que es fuente y no se puede regenerar: transcripciones, traducciones,
metadatos y scripts. El audio, los clips de TTS, los proyectos de Audacity y los vídeos
viven en Drive y se enlazan desde el repo por *file ID*.

Nunca añadas un `.mp3`, `.wav`, `.mp4` o `.aup3` al repo. `.gitignore` los bloquea; si algo
se cuela, es un error, no una excepción.

## Estructura del repositorio

```
episodios/<año>/<NNN>-<slug>/
  transcript.en.json     original descargado de nav.al       ← FUENTE DE VERDAD
  transcript.es.json     traducción al español               ← FUENTE DE VERDAD
  metadata.en.json       datos del episodio según la fuente  ← lo escribe el descargador
  metadata.es.json       título/descripción es, YouTube,
                         estado y punteros a Drive           ← lo autoramos nosotros
  transcript.en.md       GENERADO — no editar
  transcript.es.md       GENERADO — no editar

catalogo.json            los 168 episodios del archivo de nav.al ← entrada del descargador
drive.json               IDs de Drive de la raíz y de cada año  ← el vínculo con Drive
INDICE.md                GENERADO por scripts/indice.py — no editar
GLOSARIO.md              criterios de traducción y términos fijos
CONTEXTO.md              histórico: hallazgos sobre los datos antiguos
plantillas/episodio/     los cuatro .json en blanco
scripts/                 automatización
docs/                    decisiones sobre el repo
```

Años presentes: **2019 a 2026**. Las carpetas están creadas y vacías; los episodios se
crearán al descargarlos.

### Nombres

- **Carpeta de episodio**: `<NNN>-<slug>` — número de episodio a tres dígitos, guion, slug.
  Ejemplo: `026-judgment`.
- **El número es el del feed del podcast**, no el del archivo de nav.al. El archivo lista
  168 entradas; el podcast tiene 161 episodios (Apple Podcasts). Los 7 de diferencia son
  4 diálogos con Kapil Gupta de enero-febrero de 2019 (anteriores al primer episodio) y
  3 partes sueltas de *The AI Industrial Revolution*. Esos 7 van en
  `episodios/<año>/extra-<slug>/`, sin número. La regla y la tabla de correspondencia
  están en `docs/extraccion.md`.
- **Slug**: el de la URL de nav.al, tal cual. Ejemplo: `nav.al/judgment` → `judgment`.
- **Estados** de `metadata.es.json`: `pendiente` → `traduciendo` → `revision` → `tts` →
  `montaje` → `publicado`.

## Los esquemas JSON

### `transcript.en.json` / `transcript.es.json`

```json
{
  "schema": 1,
  "idioma": "en",
  "episodio": "2019/007-slug",
  "fecha": "2019-04-29",
  "titulo": "…",
  "fuente_url": "…",
  "titulos_seccion": ["…"],
  "contenido": [
    { "speaker": "Nivi",  "frases": [ {"id": "0001", "texto": "…"} ] },
    { "speaker": "Naval", "frases": [ {"id": "0002", "texto": "…"} ] }
  ]
}
```

Tres cosas que hay que entender:

1. **La frase es la unidad de generación de TTS.** Un clip de audio por frase.
2. **`speaker` selecciona la voz de referencia** del modelo XTTS.
3. **El `id` es lo que mantiene todo unido.** El clip se llama desde el id, y el orden de
   montaje **se lee del JSON**, nunca ordenando nombres de fichero alfabéticamente. Esto no
   es una preferencia estética: en el material antiguo los clips estaban sueltos y con
   numeración irregular (`_naval2.wav`, `naval02.wav`, uno sin extensión) y cualquier
   montaje por orden alfabético salía mal.

`transcript.es.json` lleva **exactamente los mismos ids** que su `.en`. Eso da alineación
frase a frase gratis, y permite validar que no falta ni sobra nada.

### `metadata.en.json`

Inmutable y re-descargable. No lo edites a mano: si está mal, se arregla el descargador y se
vuelve a bajar.

### `metadata.es.json`

Todo lo que autoramos: `titulo_es`, `estado`, el bloque `youtube` (título, descripción, tags,
url) y el bloque `drive` con los file IDs. `audio_editado_a_mano: true` marca los episodios
que pasaron por Audacity: a partir de ese punto el audio **ya no es regenerable** desde la
traducción, y el proyecto `.aup3` pasa a ser un artefacto que hay que conservar en Drive.

## El vínculo con Google Drive

GitHub **no puede montar** una carpeta de Drive. Esa función no existe: ni con submódulos,
ni con Actions, ni con nada. El vínculo se construye con dos piezas:

**1. Los file IDs, guardados en el repo.** `drive.json` tiene el ID de la carpeta raíz y el
de cada año. El `metadata.es.json` de cada episodio tiene los de su carpeta y sus ficheros.
Un ID es estable frente a renombrados y a mover la carpeta; una URL o una ruta no lo son.
Se resuelve así:

```
https://drive.google.com/drive/folders/<carpeta_id>
https://drive.google.com/file/d/<file_id>/view
```

**2. rclone, para mover bytes.** En Linux no hay cliente oficial de Drive. rclone es un
binario de línea de comandos —"rsync para la nube"— que habla el API de Drive.

```bash
sudo apt install rclone
rclone config          # asistente: Google Drive → autorizar → llamar al remoto "gdrive"
rclone copy ./clips "gdrive:naval-podcast/2019/007-slug/tts" -P
rclone copy "gdrive:naval-podcast/2019/007-slug/audio" ./audio -P
```

`copy` solo transfiere lo que falta o ha cambiado; relanzarlo es barato. **`sync` no se usa
en este flujo**: borra en destino lo que no esté en origen.

No hay sincronización automática. Nada se sube solo. rclone mueve bytes cuando se lo pides.

### Estructura en Drive

```
naval-podcast/<año>/<NNN>-<slug>/
  tts/         un clip por frase, nombrado por el id de la frase
  audio/       audio final montado
  video/       .mp4 subido a YouTube
  proyecto/    .aup3 de Audacity
```

La raíz y los ocho años ya existen (IDs en `drive.json`). Las carpetas de episodio se crean
al procesar cada episodio.

Desde una sesión de Claude con el conector de Google Drive se pueden crear carpetas y leer y
escribir ficheros pequeños. **No subas audio por el conector**: son gigas, eso es trabajo de
rclone.

## Flujo de trabajo

| # | Paso | Dónde | Estado |
|---|---|---|---|
| 1 | Descargar el transcript original de nav.al | **local**, `descargar-episodios.py` | escrito, sin ejecutar contra la web real |
| 2 | Traducir al español a `transcript.es.json` | web / local | por definir |
| 3 | Generar un clip de TTS por frase y subirlo a Drive | Colab (GPU) | por definir |
| 4 | Juntar clips, quitar ruido y alucinaciones | **local, Audacity** | manual por diseño |
| 5 | Subir el audio limpio a Drive con rclone | local | — |
| 6 | Montar el `.mp4` con la miniatura | local | script sin probar |
| 7 | Subir a YouTube con título, descripción y miniatura | por definir | ver aviso abajo |

El paso 4 es irreducible: requiere criterio humano.

## Restricciones del entorno

**nav.al está bloqueado desde las sesiones web de Claude Code.** La política de egress
devuelve 403 en el CONNECT; `itunes.apple.com` igual. Comprobado con
`curl -sS "$HTTPS_PROXY/__agentproxy/status"`.

Consecuencia: **la descarga se ejecuta en la máquina local** con
`scripts/descargar-episodios.py`, que usa la API REST de WordPress de nav.al. Claude web
sirvió para el reconocimiento (catálogo, reglas de parseo) pero **no para los cuerpos**: su
fetch corta a 100 KB y no reproduce el texto entero. No insistas por esa vía. El protocolo
completo está en **`docs/extraccion.md`**; léelo antes de tocar nada de la descarga.

La idea que lo gobierna: el troceo en frases y la asignación de ids son deterministas y los
hace un script, nunca un modelo, para que los mismos datos den siempre los mismos ids.

GitHub y el conector de Google Drive sí funcionan desde las sesiones web.

**Aviso sobre YouTube**: mientras la app OAuth no pase la verificación de Google, los vídeos
que suba la API quedan forzados a `private` y no se pueden hacer públicos por API. Verifícalo
antes de invertir esfuerzo en automatizar el paso 7. Alternativa que sí funciona: la API sube
en privado ya con título, descripción y miniatura puestos, y la publicación se hace a mano en
YouTube Studio.

## Scripts

| Script | Estado |
|---|---|
| `scripts/nuevo-episodio.sh` | Crea la carpeta de un episodio con los cuatro `.json`. Al día |
| `scripts/indice.py` | Regenera `INDICE.md`. Al día |
| `scripts/descargar-episodios.py` | Baja los episodios de nav.al a `trabajo/extraccion/` como JSON crudo. **Se ejecuta en local.** Probado contra fixture sintético; nunca contra la web real |
| `scripts/unir-audios.sh` | **Nunca ejecutado y desactualizado.** Ordena los clips alfabéticamente; debe reescribirse para leer el orden y los ids de `transcript.es.json`. No lo uses todavía |
| `scripts/render-video.sh` | **Nunca ejecutado.** Opera sobre un directorio de trabajo local, no sobre el repo |

Por escribir: `normalizar-extraccion.py` (convierte `trabajo/extraccion/*.json` en los
ficheros del repo; se escribe contra la primera salida real del descargador), el generador de
los `.md`, el validador de esquemas y el creador de carpetas de episodio en Drive.

## Al trabajar en este repo

- Los `.md` de transcripción y `INDICE.md` son **generados**. Edita el `.json` y regenera.
- Después de tocar cualquier `metadata.es.json`, ejecuta `python3 scripts/indice.py`.
- Todo el texto va en UTF-8 y el proyecto se documenta en español.
- Las claves de API van en `.env`, que está ignorado. Parte de `.env.example`.
- Antes de commitear: `git ls-files | grep -E '\.(mp3|wav|mp4|aup3)$'` no debe devolver nada.

## Derechos

El repositorio es público por decisión del autor. Los transcripts originales son obra de sus
autores; `metadata.en.json` guarda la `fuente_url` de cada episodio para que la atribución
viaje con el dato, y la descripción de YouTube debe acreditar la fuente.
