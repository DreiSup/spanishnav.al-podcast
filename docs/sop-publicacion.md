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
La transcripción se ha traducido del inglés al español con Claude Opus 5, de Anthropic. La voz en español se ha generado con Qwen3-TTS, un modelo de voz de código abierto fine-tuned con las voces de Naval y de otros participantes.

¿Algún problema o queja? Escríbeme a podcast@spanishnav.al

—

Unofficial Spanish translation of Naval Ravikant's podcast. Original content by Naval Ravikant at nav.al.
This podcast has been translated into Spanish using artificial intelligence. There may be errors or inconsistencies in both the translation and the diction.
The transcript was translated from English to Spanish with Anthropic's Claude Opus 5. The Spanish audio was generated with Qwen3-TTS, an open-source voice model fine-tuned on the voices of Naval and other participants.
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
- **Modelos con su nombre concreto** (Claude Opus 5, Qwen3-TTS). Si cambia el motor de traducción o de voz, se
  cambia esta plantilla y vale para los episodios nuevos; los ya publicados en YouTube no se actualizan solos.
- **Una frase de voces general**, que vale para todos los episodios: Naval, Brett y Deutsch llevan fine-tuning; Nivi
  y los invitados, no (`docs/contexto-sesion-global.md`, §4). Por eso dice «Naval y otros participantes» y no «Naval y
  Nivi».
- **Atribución explícita** («Traducción no oficial. Contenido original…»), como pide `CLAUDE.md` en *Derechos*.
- **Más adelante**: capítulos de YouTube con los minutos de cada sección, que la fábrica ya conoce
  (`indice_master.tsv`).

## Pendiente, en este orden

2. **Subir el master a R2**: nombre `<año>/<NNN>-<slug>.mp3` (el mismo que el master de la fábrica) y comprobación
   del enlace público.
4. **Generar el feed** desde la web (`spanishnav.al/podcast.xml`, a confirmar).
5. **Alta, una sola vez**, en YouTube Studio, Spotify for Creators y Apple Podcasts Connect.
6. **Publicar cada episodio** y quién mueve el estado a `publicado` en `metadata.es.json`.
