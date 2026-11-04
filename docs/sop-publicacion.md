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

## Pendiente, en este orden

2. **Subir el master a R2**: nombre `<año>/<NNN>-<slug>.mp3` (el mismo que el master de la fábrica) y comprobación
   del enlace público.
3. **El episodio en el feed**: título, descripción (vídeo original de Naval, nav.al, spanishnav.al, aviso de IA),
   fecha, duración, tamaño y número.
4. **Generar el feed** desde la web (`spanishnav.al/podcast.xml`, a confirmar).
5. **Alta, una sola vez**, en YouTube Studio, Spotify for Creators y Apple Podcasts Connect.
6. **Publicar cada episodio** y quién mueve el estado a `publicado` en `metadata.es.json`.
