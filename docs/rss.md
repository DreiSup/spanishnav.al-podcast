# Cómo funciona un feed RSS de podcast

> Explicación para el autor (2026-10-28), como base del SOP de Spotify y Apple Podcasts.
> Contexto general en `docs/fabrica-de-contenido.md`.

## Qué es

Un feed RSS es **un solo fichero de texto** (en formato XML) publicado en una dirección fija,
por ejemplo `https://spanishnav.al/podcast.xml`. Funciona como el **índice del podcast**:

- dice cómo se llama el podcast, quién lo hace y qué portada tiene;
- lista todos los episodios, cada uno con su título, su descripción, su fecha y **un enlace al
  MP3**.

**El feed no contiene el audio, solo apunta a él.** El MP3 vive en otro sitio; en este
proyecto, en Cloudflare R2.

```
spanishnav.al/podcast.xml   ← el índice: texto, unos pocos KB
        │
        ├─ Episodio 053 → enlace a  r2.../053.mp3   ← el audio, decenas de MB
        ├─ Episodio 052 → enlace a  r2.../052.mp3
        └─ …
```

## Quién lo lee y cómo

Spotify, Apple Podcasts, Pocket Casts, Overcast y casi cualquier app de podcasts **visitan el
feed cada pocas horas** para ver si hay algo nuevo. Nadie les envía nada: son ellas las que
vienen a mirar.

1. **Una sola vez:** se da de alta la dirección del feed en Spotify for Creators y en Apple
   Podcasts Connect. Ellos revisan tres cosas:
   - que la portada sea válida;
   - que haya al menos un episodio;
   - que el correo del propietario sea del autor.

   En unos días el podcast queda publicado.
2. **Cada episodio nuevo:** se añade una entrada al feed y se sube el MP3 a R2. Nada más. En
   unas horas aparece en todas las apps, sin entrar en ninguna de ellas.

Publicar un episodio pasa a ser **actualizar un fichero**.

## Qué lleva dentro

Versión simplificada:

```xml
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <!-- Datos del podcast: se escriben una vez -->
    <title>Naval en español</title>
    <link>https://spanishnav.al</link>
    <language>es</language>
    <description>Traducción al español del podcast de Naval Ravikant…</description>
    <itunes:image href="https://spanishnav.al/portada.jpg"/>   <!-- cuadrada, 1400–3000 px -->
    <itunes:category text="Business"/>
    <itunes:owner><itunes:email>podcast@spanishnav.al</itunes:email></itunes:owner>

    <!-- Un <item> por episodio: se añade uno cada vez -->
    <item>
      <title>Una mente en calma, un cuerpo en forma, una casa llena de amor</title>
      <description>Episodio original: nav.al/finally-wealthy …</description>
      <pubDate>Mon, 03 Nov 2026 07:00:00 GMT</pubDate>
      <enclosure url="https://audio.spanishnav.al/2019/035.mp3" length="7340032" type="audio/mpeg"/>
      <guid isPermaLink="false">spanishnav-2019-035</guid>
      <itunes:duration>612</itunes:duration>
      <itunes:episode>35</itunes:episode>
    </item>
  </channel>
</rss>
```

Las piezas que importan:

- **`enclosure`**: el enlace al MP3 y su tamaño en bytes. Es lo que las apps descargan y
  reproducen.
- **`guid`**: el identificador único del episodio. **No debe cambiar nunca.** Si cambia, las
  apps creen que es un episodio nuevo y lo duplican.
- **`pubDate`**: la fecha de publicación. Ordena los episodios. Con una fecha futura, la
  mayoría de las apps no lo muestran hasta ese día, lo que permite programar la publicación
  diaria.

## Reglas de oro

1. **La dirección del feed es para siempre.** Se puede redirigir, pero es delicado. Por eso
   conviene que viva en el dominio propio (`spanishnav.al/…`) y no en el de un servicio que
   mañana puede cambiar.
2. **Los enlaces a los MP3 tampoco deben cambiar.** Si se mueve un fichero, ese episodio deja
   de sonar en todas las apps.
3. **El feed es público.** Así funcionan todos los podcasts.

## Dos maneras de tenerlo

| | **Feed propio** (lo genera la web) | **Servicio de hosting** (Spotify for Creators, Buzzsprout…) |
|---|---|---|
| Quién crea el XML | La web, a partir de los datos del repo | El servicio, al subir el audio en su página |
| Dónde está el audio | R2 propio | Sus servidores |
| Publicar un episodio | Automatizable del todo: un commit y una subida a R2 | Subida manual en su web, o por su API si la tiene |
| Estadísticas | Hay que montarlas aparte | Incluidas |
| Coste | Ya pagado: Vercel y R2 | Gratis o de pago, según el servicio |
| Control | Total, y la dirección es propia | La dirección del feed es suya |

**Recomendación: feed propio.** Las piezas ya existen:

- el repo guarda título, descripción y fecha de cada episodio;
- R2 aloja el audio;
- la web en Vercel puede generar `podcast.xml` sola a partir del repo.

Publicar en Spotify y Apple sería: subir el MP3 a R2 y marcar el episodio como publicado en
el repo. El workflow puede hacer las dos cosas.

La pega son las estadísticas de escucha. Se pueden añadir con un servicio intermedio gratuito
que cuenta las descargas sin tocar nada más. Se decide al llegar ahí.
