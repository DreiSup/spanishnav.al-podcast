# SOP: del master a la publicación

> **Borrador**, en construcción con el autor (desde el 4-nov). Sigue a `docs/sop-episodio.md`: empieza cuando un
> episodio está en estado `montaje` (master escuchado y bueno). Cada apartado se da por **validado** solo cuando se
> ha hecho a mano de principio a fin; hasta entonces lo dice arriba.

## La ruta: un solo feed RSS para todo (decisión del autor, 4-nov)

```
master (Drive)  ──►  R2 (audio.spanishnav.al)  ──►  feed RSS (spanishnav.al)  ──►  YouTube
                                                                              ├─►  Spotify
                                                                              ├─►  Apple Podcasts
                                                                              └─►  web spanishnav.al
```

- **No se monta vídeo.** YouTube lee el feed y crea él mismo cada vídeo con la imagen fija del podcast (alta de un
  podcast por RSS en YouTube Studio; España está entre los países admitidos). Descartado montar el `.mp4` en Colab o
  en local: haría falta además subirlo a mano, y Spotify y Apple seguirían necesitando el feed.
- **Publicar un episodio = subir su master a R2 y añadirlo al feed.** Las plataformas leen el feed solas.
- **Una imagen para todo el podcast**, de momento. Se puede cambiar más adelante: en Spotify, Apple y en los
  vídeos nuevos de YouTube se actualiza desde el feed; los vídeos de YouTube ya publicados se quedan con la imagen
  con la que se crearon (su miniatura se puede cambiar a mano, una a una, en YouTube Studio).

Cómo funciona un feed, en `docs/rss.md`.

## 1. El podcast en el feed (datos fijos)

> **Decidido** con el autor el 4-nov; pendiente de validar al dar de alta el feed en cada plataforma.

Se escriben una vez y valen para todo el podcast.

| Campo | Valor |
|---|---|
| Título | Naval Podcast en español |
| Autor | spanishnav.al |
| Idioma | `es` |
| Categoría | Negocios (`Business`); alternativa, Educación |
| Correo del propietario | `podcast@spanishnav.al` (a él llega la verificación de YouTube y de Apple) |
| Contenido explícito | No |
| Descripción | Traducción no oficial al español, hecha con inteligencia artificial, del podcast de Naval Ravikant sobre riqueza, felicidad y conocimiento. Episodios originales en nav.al. La traducción y la voz se generan con IA y puede haber errores. Contacto: podcast@spanishnav.al |
| Portada | `https://spanishnav.al/portada.jpg` |
| Imagen rectangular (YouTube) | `https://spanishnav.al/portada-youtube.jpg` |

### Las imágenes

| Archivo | Tamaño | Peso | Uso |
|---|---|---|---|
| `portada.jpg` | 2000 × 2000, JPG, RGB | 296 KB | Portada del podcast en Apple, Spotify y YouTube |
| `portada-youtube.jpg` | 1677 × 938, JPG, RGB (casi 16:9) | 183 KB | Imagen rectangular para los vídeos de YouTube, si la plataforma la admite (sin confirmar en la documentación oficial) |

Viven en el repo de la web (`DreiSup/spanishnaval-web`, carpeta `public/`) y se sirven desde el dominio propio. **Sus
direcciones no deben cambiar**: el feed apunta a ellas.

Requisitos que cumplen (comprobados el 4-nov):

- **Apple**: cuadrada, de 1400 × 1400 a 3000 × 3000 (recomienda 3000), JPG o PNG.
  [Fuente](https://podcasters.apple.com/support/artwork-requirements).
- **RGB y menos de unos 500 KB**: no lo dice la página de Apple, pero lo piden guías de alojadores y aparece en
  rechazos reales de validación.
- **Spotify**: 1:1, de 640 a 10 000 px, JPG o PNG.
  [Fuente](https://artists.spotify.com/help/article/cover-art-requirements).
- Legibilidad a tamaño de app: «Naval» se lee siempre, «Podcast» hasta 160 px, «en español» por debajo de 160 px ya
  no. Aceptado: el nombre se resume en «Naval».

Para cambiar la portada: se sustituye `public/portada.jpg` en la web **con el mismo nombre**, sin pasar de 500 KB.

## 2. Subir el master a R2

> **Hecho a mano con el 001 el 4-nov** (respuesta `200`). Infraestructura y reglas: `docs/infraestructura-r2.md`.

Desde el ordenador del autor (las sesiones web de Claude no llegan a R2):

1. Bajar el master de Drive: `transcripts/<año>/<NNN Título>/audio/<NNN>-<slug>.mp3`. Sale de la fábrica en su
   formato final; no se exporta nada.
2. Subirlo con **el mismo nombre**:

   ```bash
   rclone copyto ~/Descargas/<NNN>-<slug>.mp3 r2:spanishnaval/<año>/<NNN>-<slug>.mp3 -P
   ```

3. Comprobarlo: `curl -sI https://audio.spanishnav.al/<año>/<NNN>-<slug>.mp3` → `200` y `content-type: audio/mpeg`.

Esa dirección **no cambia nunca**: es el enlace del episodio en el feed. Nunca `rclone sync` ni `delete` sobre el
bucket.

**Sin ordenador: el cuaderno de Colab `video/video.ipynb`** con `SUBIR_R2 = True` (7-nov). Sube el master de Drive a
`spanishnaval/<año>/<NNN>-<slug>.mp3` con `Content-Type: audio/mpeg`, **nunca pisa** un audio que ya esté (si está con
otro tamaño, falla y lo deja) y comprueba que `https://audio.spanishnav.al/…` responde `audio/mpeg` con el tamaño del
master. Usa un token propio de R2 (`colab-spanishnaval`, Object Read & Write, solo el bucket) guardado por el autor en
los Secretos de Colab `R2_ACCESS_KEY_ID` y `R2_SECRET_ACCESS_KEY`; nunca pasa por el chat ni por el repo. Al final
imprime el tamaño y la duración de cada master, que es lo que necesita la web. **Subir a R2 no publica nada.**
**Validado el 7-nov** con el R2 real: el 002 lo saltó (ya estaba) y subió 003, 004 y 005 (200, `audio/mpeg`, tamaño del master).

## 3. La descripción de cada episodio

> **Decidido** con el autor el 4-nov, sobre la descripción que usaba en los vídeos hechos con XTTS. Pendiente de
> validar con el 001.

Es la misma en YouTube, Spotify y Apple: sale del feed. Por eso empieza por el episodio (las apps solo enseñan las
dos o tres primeras líneas antes de «más») y los enlaces van completos, con `https://`, para que se puedan pulsar en
todas.

### Plantilla

Lo que va entre `{llaves}` cambia en cada episodio; el resto es fijo.

```
Episodio {número} de la traducción al español del podcast de Naval Ravikant.
{título en español}: {subtítulo en español}.

▶ Episodio original en YouTube: https://www.youtube.com/watch?v={id del vídeo original}
▶ Transcripción original en inglés: https://nav.al/{slug}
▶ Este episodio en español, con su transcripción: https://spanishnav.al/{slug}
▶ Canal original de Naval: https://www.youtube.com/@NavalR

Traducción no oficial. Contenido original de Naval Ravikant, publicado en nav.al.

Este podcast se ha traducido al español con inteligencia artificial. Puede haber errores o inconsistencias tanto en la traducción como en la dicción.
La transcripción se ha traducido del inglés al español con Claude Opus 5.5 (esfuerzo alto), de Anthropic. La voz en español se ha generado con Qwen3-TTS, un modelo de voz de código abierto fine-tuned con las voces de Naval y de otros participantes.

¿Algún problema o queja? Escríbeme a podcast@spanishnav.al

—

Unofficial Spanish translation of Naval Ravikant's podcast. Original content by Naval Ravikant at nav.al.
This podcast has been translated into Spanish using artificial intelligence. There may be errors or inconsistencies in both the translation and the diction.
The transcript was translated from English to Spanish with Anthropic's Claude Opus 5.5 (high effort). The Spanish audio was generated with Qwen3-TTS, an open-source voice model fine-tuned on the voices of Naval and other participants.
If you run into any problems or have a complaint, reach me at podcast@spanishnav.al
```

### De dónde sale cada dato

| Dato | Fuente | Ejemplo (001) |
|---|---|---|
| Número | `metadata.en.json` → `numero` | 1 |
| Título en español | `transcript.es.json` → `titulo` | Busca riqueza, no dinero ni estatus |
| Subtítulo en español | `transcript.es.json` → `subtitulo` | La riqueza son activos que generan ingresos mientras duermes |
| Id del vídeo original | `metadata.es.json` → `youtube.url_original` (campo nuevo; sale del listado del canal @NavalR, `docs/youtube.md`) | `jemPACNo1_I` |
| Slug | `metadata.en.json` → `slug` (el de nav.al; la web usa el mismo) | `seek-wealth` |

Al copiar el enlace del vídeo original desde YouTube, se le quita el `?si=…`: es un parámetro de seguimiento de quien
comparte. Se guarda limpio: `https://www.youtube.com/watch?v=<id>`.

### Criterios fijados

- **Español**, no castellano, como el nombre del podcast. «Puede haber errores» (haber impersonal).
- **Modelos con su nombre concreto** (Claude Opus 5.5 con esfuerzo alto, Qwen3-TTS). Si cambia el motor de traducción o de voz, se
  cambia esta plantilla y vale para los episodios nuevos; los ya publicados en YouTube no se actualizan solos.
- **Una frase de voces general**, que vale para todos los episodios: Naval, Brett y Deutsch llevan fine-tuning; Nivi
  y los invitados, no (`docs/contexto-sesion-global.md`, §4). Por eso dice «Naval y otros participantes» y no «Naval y
  Nivi».
- **Atribución explícita** («Traducción no oficial. Contenido original…»), como pide `CLAUDE.md` en *Derechos*.
- **Más adelante**: capítulos de YouTube con los minutos de cada sección, que la fábrica ya conoce
  (`indice_master.tsv`).

## 4. El feed RSS (web)

> **Hecho el 4-nov** con el 001: `https://spanishnav.al/podcast.xml`, validado como XML en local. Pendiente de
> validar en producción y en las tres plataformas.

Lo genera la web (`DreiSup/spanishnaval-web`) al desplegar: `app/podcast.xml/route.ts` y `lib/feed.ts`. Los datos
fijos (apartado 1) están en `lib/site.ts` → `podcast`; la descripción de cada episodio (apartado 3) la escribe
`lib/feed.ts` → `episodeDescription`. **La dirección del feed no cambia nunca.**

Cada episodio entra en el feed con:

| Etiqueta | De dónde sale | 001 |
|---|---|---|
| `title` | `transcript.es.json` → `titulo` | Busca riqueza, no dinero ni estatus |
| `enclosure` (url, bytes, `audio/mpeg`) | R2 y el tamaño del master | `…/2019/001-seek-wealth.mp3`, 6 633 103 |
| `itunes:duration` | duración del master, en segundos | 415 |
| `guid` | `spanishnav.al/<año>/<slug>`. **No cambia nunca**: si cambia, las apps lo ven como un episodio nuevo | `spanishnav.al/2019/seek-wealth` |
| `pubDate` | fecha de publicación **de la traducción**, no la del original | 2026-11-04 |
| `itunes:episode` | número del feed | 1 |

Los mismos datos se apuntan en `metadata.es.json` → `publicacion` (`fecha`, `audio_url`, `audio_bytes`,
`duracion_s`, `feed_guid`).

## 5. Alta en las plataformas (una sola vez)

> Requisito: el feed en producción con al menos un episodio. YouTube por RSS está aparcado (apartado 5 bis).

**YouTube por RSS (aparcado)** ([ayuda de Google](https://support.google.com/youtube/answer/13973017)): YouTube Studio del canal →
**Crear** → **Nuevo podcast** → **Enviar feed RSS** → aceptar las condiciones → pegar el feed → código del correo →
elegir cuántos episodios importar → publicar. Si no sale «Enviar feed RSS», falta verificar el canal o la función no
está en la región.

**Spotify** — hecho el 5-nov; se da por validado cuando el programa muestre el feed. El autor ya tenía el programa en Spotify for Creators, alojado allí con episodios
antiguos, así que **no se dio de alta de nuevo: se redirigió** ([ayuda de Spotify](https://support.spotify.com/us/creators/article/switching-away-from-spotify-for-creators-with-a-301-redirect/)):

1. `creators.spotify.com` **desde el ordenador** (la app móvil no deja) → ajustes del programa → **Redirect your
   podcast** → pegar `https://spanishnav.al/podcast.xml` → **Redirect**.
2. Tarda hasta 7 días. Mientras tanto, y al menos una semana, **no se borra** el programa ni la cuenta de Spotify for
   Creators. Si hubiera Suscripciones activas, se desactivan antes en **Monetize**.
3. Al aplicarse, el programa pasa a mostrar solo lo que hay en el feed (nombre, portada y episodios); los antiguos
   desaparecen, como decidió el autor el 4-nov. Conserva sus seguidores y su enlace:
   https://open.spotify.com/show/033up4yw5viytCxxHH6D7f
4. Si el programa redirigido hubiera estado también en Apple, la redirección le llega a Apple y el alta de Apple sobra
   (no era el caso).

Para un programa que no exista ya en Spotify: creators.spotify.com → menú del perfil → **Add a new show** → alojado
**en otro sitio** → pegar el feed → código de 8 cifras del correo → país, idioma (español) y categoría → enviar
([ayuda de Spotify](https://support.spotify.com/us/creators/article/claiming-your-podcast-on-spotify-for-creators/)).
Sin validar.

**Apple** — hecho el 5-nov, pendiente de la revisión de Apple:

1. Cuenta de Apple para `podcast@spanishnav.al` con verificación en dos pasos, **método de pago añadido** (si no,
   Podcasts Connect pide «activar» la cuenta; no cobra nada) y los términos de Apple Media Services aceptados.
2. Primer acceso a Podcasts Connect: **Account name** = `spanishnav.al`.
3. **+** → **Nuevo programa**: crea un borrador «alojado en Apple», con campos para rellenar a mano. **No se rellenan.**
4. **More Actions → Add RSS Feed** → pegar el feed. El programa pasa a «Untitled» y «We're still processing your show
   details» mientras Apple lee el feed; luego se ve con el nombre, la portada y los episodios del feed.
5. **Content Rights**: lo elige el autor. → **Publish**. Apple revisa (puede tardar días) y avisa por correo.
6. Id del programa: `6831305665`. Enlace público, que funciona cuando Apple lo aprueba:
   https://podcasts.apple.com/es/podcast/id6831305665

Al terminar, el enlace público de cada plataforma va a `lib/site.ts` → `platforms` en la web (hoy a `null`, sale
«Próximamente»).

## 5 bis. YouTube a mano, sin RSS (decisión del 5-nov, hasta tener permiso de Naval)

> **Validado con el 001** (5-nov): https://www.youtube.com/watch?v=s10rGZckyEo

1. **Vídeo**, en el ordenador del autor, junto al master (YouTube recomienda MP4 con H.264 y audio AAC a 48 kHz,
   [Google](https://support.google.com/youtube/answer/1722171)):

   ```bash
   curl -O https://spanishnav.al/portada-youtube.jpg
   ```

   ```bash
   ffmpeg -loop 1 -framerate 25 -i portada-youtube.jpg -i <NNN>-<slug>.mp3 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p" -c:v libx264 -preset veryfast -tune stillimage -crf 20 -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart <NNN>-<slug>.mp4
   ```

   El `.mp4` no va a git; si se guarda, en la carpeta `video/` del episodio en Drive.

   **Sin ordenador: `video/video.ipynb` en Colab** (entorno de CPU, sin GPU). Se abre con
   https://colab.research.google.com/github/DreiSup/spanishnav.al-podcast/blob/claude/quirky-dirac-x18c3n/video/video.ipynb ,
   se ponen los episodios en la celda 1 (`EPISODIOS = "004"`, `"006-037"` o `"006, 008, 010-012"`) y se ejecuta
   todo. Por cada episodio (si uno falla, lo apunta y sigue; los ya hechos y los no escuchados los salta):
   - copia el master de Drive a Colab y comprueba que se decodifica sin errores;
   - hace el vídeo con el comando de arriba, con dos cambios: audio **estéreo** (`-ac 2`, lo que recomienda YouTube)
     y la duración fijada con `-t` en vez de `-shortest`;
   - comprueba formato, duraciones, que vídeo y audio se decodifican sin errores y que el audio del vídeo es el del
     master (SNR en 12 tramos: mediana ≥ 20 dB y ninguno < 12);
   - comprueba en el repo que el master está escuchado y dado por bueno (`SOLO_ESCUCHADOS`);
   - al final, un resumen y 30 s de cada vídeo para escucharlos en el propio cuaderno: **no se juzga el sonido por la vista previa de Drive**, que recién
     subido reproduce a calidad baja;
   - copia el `.mp4` a `video/` del episodio y espera a que Drive sincronice (`flush_and_unmount`).

   El cuaderno busca la carpeta del episodio en todos los años de Drive por su número. El 6-nov se retiró el modo «rápido» (repetir un clip sin recodificar): al autor le sonaron mal los dos modos de la
   primera versión. **Sin validar en Colab**: se valida con el 002.
2. **YouTube Studio → Crear → Subir vídeos.** Campos fijos, iguales en todos los vídeos (de referencia; el autor ya
   los conoce y no se le repiten):

   | Campo | Valor |
   |---|---|
   | Título | **Solo el título original traducido**: `transcript.es.json` → `titulo`, sin nombre del podcast ni número (decisión del autor, 5-nov). Ej.: «Busca riqueza, no dinero ni estatus» |
   | Descripción | La del apartado 3, entera |
   | Miniatura | `portada-youtube.jpg` (el canal tiene que estar verificado por teléfono) |
   | Lista | «Naval Podcast en español» |
   | Público | No es contenido para niños |
   | Contenido alterado | **Sí**: voz sintética que se parece a una persona real ([Google](https://support.google.com/youtube/answer/14328491)) |
   | Idioma / categoría | Español / Educación |
   | Visibilidad | Pública |

3. Apuntar el enlace del vídeo en `metadata.es.json` → `youtube.url`.

### Qué le da la sesión al autor en cada subida (regla del autor, 5-nov)

Cuando el autor va a subir un vídeo, la sesión le da **solo dos cosas**, cada una en su bloque para copiar:

1. **Título**: el título traducido, tal cual (`transcript.es.json` → `titulo`).
2. **Descripción**: la del apartado 3, entera, la misma que lleva el feed (`episodeDescription` de `lib/feed.ts` en
   la web). Antes de dársela, se comprueban sus enlaces: el vídeo original es el que enlaza la página de nav.al del
   episodio, `nav.al/<slug>` responde, y `spanishnav.al/<slug>` existe en la web desplegada.

Nada más: ni los campos fijos, ni la explicación de cada pantalla.

## 6. Publicar cada episodio (después del alta)

1. Master escuchado y bueno: estado `montaje` (`docs/sop-episodio.md`).
2. Subirlo a R2 (apartado 2).
3. En la web: copiar `transcript.es.json` a `content/episodios/<año>/<NNN>-<slug>.json` y añadir el episodio a
   `lib/episodes.ts` con `audioKey`, `audioBytes`, `durationSec`, `published` y `youtubeOriginal`. Desplegar
   (`main`).
4. Las plataformas leen el feed solas (YouTube, Spotify y Apple tardan de minutos a horas).
5. En `metadata.es.json`: bloque `publicacion`, `youtube.url` del vídeo que crea YouTube, y estado `publicado`.

**Automatizable más adelante:** el paso 3 sale entero del repo del podcast (texto, tamaño y duración del master).

## Pendiente

- X: descartado (5-nov). Instagram, Facebook y TikTok: apuntados como opción futura, sin investigar.
- Substack: «Distribute to Substack» → «I have a podcast hosted elsewhere» → feed (no «Import an existing podcast»,
  que muda el alojamiento). Validado el 5-nov: el 001 salió solo
  (https://spanishnavalravikant.substack.com/).

- Validar los apartados 1, 3, 4 y 5 en producción con el 001.
- Capítulos de YouTube con `indice_master.tsv`.
