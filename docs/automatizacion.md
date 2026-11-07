# Automatización de la publicación

Cómo se publica un episodio sin tocar nada a mano, pieza a pieza. Se escribe a medida que cada pieza se prueba de
verdad; lo que no esté marcado como validado, no lo está. Es la base del prompt de la sesión programada (punto 6).

## La idea (decisión del autor, 6–7-nov)

El autor genera y escucha los episodios a su ritmo. Cuando tiene un lote revisado, lo aprueba; la sesión de dirección
le asigna **una fecha por episodio, seguidas, un episodio al día**, y desde ahí todo sale solo. El OK del autor es por
lote (al aprobar las fechas), no diario.

## Qué publica y qué no

| Pieza | ¿Publica? | Qué hace |
|---|---|---|
| Master en Drive | No | Sale de la fábrica |
| Audio en R2 | **No** | Solo almacena: `audio.spanishnav.al/<año>/<NNN>-<slug>.mp3`. Nadie lo enlaza hasta que la web lo hace |
| Entrada en la web (`lib/episodes.ts` + `content/episodios/…json`) | **Sí, en su fecha** | Página del episodio y `<item>` del feed, que leen Spotify, Apple y Substack |
| Vídeo en YouTube | Sí, en su fecha si se programa | Va aparte: YouTube no lee el feed |

Orden obligatorio: **audio en R2 antes** de que llegue la fecha del episodio en la web (si no, el feed apunta a un audio
que no existe).

## 1. Audio a R2 — validado el 7-nov

Cuaderno `video/video.ipynb` con `SUBIR_R2 = True` (detalles en `docs/sop-publicacion.md`, apartado 2). Token propio
`colab-spanishnaval` en los Secretos de Colab. Nunca pisa un audio que ya esté. Al final imprime `bytes` y
`duracion_s` de cada master: los datos de la entrada de la web.

## 2. Web con fechas — probado en local el 7-nov, pendiente de producción

En el repo de la web (`DreiSup/spanishnaval-web`):

- Cada episodio de `lib/episodes.ts` lleva `published: 'AAAA-MM-DD'`. Sale a las **12:00 UTC** de ese día (la hora del
  `<pubDate>` del feed).
- `publishedEpisodes()` deja solo los que ya han llegado a su hora. La portada, el archivo, la búsqueda, las
  categorías, las páginas de episodio y `podcast.xml` usan esa lista y tienen `revalidate = 3600`: Next.js (16.2) los
  regenera como mucho cada hora, **sin desplegar**. Un episodio programado da 404 hasta su día.
- Prueba: `next start` con un episodio programado a +90 s y `revalidate = 10`: entró solo en el feed, la portada y su
  página al llegar su hora.
- Por tanto, el episodio del día aparece entre las 12:00 y las 13:00 UTC, y las plataformas lo recogen después
  (Spotify y Apple tardan de minutos a horas).

### Qué es «actualizarse cada hora»

No es un push a `main` ni un despliegue de Vercel. Es la **regeneración incremental** (ISR) de Next.js: Vercel guarda
cada página y el feed ya hechos; cuando alguien los pide y la copia tiene más de una hora, Vercel le sirve la copia y,
por detrás, rehace esa página con el código ya desplegado (sin build, sin push, sin coste apreciable). Como
`publishedEpisodes()` mira la hora en ese momento, la copia nueva ya incluye el episodio del día. Con «cada día»
(`revalidate = 86400`) el episodio podría salir hasta 24 h tarde, porque el reloj de cada página empieza cuando se
regeneró la última vez, no a las 12:00.

## 3. YouTube — preparado el 7-nov, sin probar con la API real

Cuaderno `video/video.ipynb` con `SUBIR_YOUTUBE = True`:

- Título y descripción de `metadata.es.json` → `youtube`, que deja la sesión de dirección con
  `python3 scripts/descripcion.py <año>/<NNN>-<slug> --guardar` (la misma plantilla que el feed; `--comprobar` la
  compara con el feed publicado).
- Programado para las 12:00 UTC de `publicacion.fecha` (`status.publishAt`); si esa hora ya pasó, público al momento.
  `YOUTUBE_MODO = "privado"` lo sube sin programar.
- Categoría Educación (27), idioma `es`, «no es para niños», `containsSyntheticMedia: true`, miniatura y lista
  «Naval Podcast en español». Si la miniatura o la lista fallan, lo avisa y sigue.
- No sube dos veces: lo salta si el repo ya tiene `youtube.url` o si el canal ya tiene un vídeo con ese título.
- Credenciales: cliente OAuth de escritorio en los Secretos `YT_CLIENT_ID` y `YT_CLIENT_SECRET`; la autorización se
  guarda en Drive, `naval-podcast/_privado/youtube_token.json` (nunca en el repo ni en el chat).
- Prueba: 003 (7-nov, hoy) y 004 (8-nov) — ¿YouTube respeta `publishAt` o los deja en privado?

## Pendiente

- Validar el punto 2 en producción (Vercel) con el primer lote.
- Generar las entradas de `lib/episodes.ts` desde el repo del podcast (bloque `publicacion` de `metadata.es.json`),
  sin escribirlas a mano.
- YouTube programado (API con `publishAt`, o programar en YouTube Studio).
- La sesión programada diaria: comprueba el episodio del día (página, feed, audio), apunta el enlace de YouTube, marca
  `publicado` y avisa si algo falla o si quedan menos de 7 episodios programados.
