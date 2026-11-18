# Vídeo dinámico con el transcript en pantalla (desde el 052)

> Plan del autor del 18-nov, guardado como contexto. **No está en marcha**: el autor lo retomará cuando acabe tareas
> más urgentes. Escrito por la sesión técnica (fábrica de voz), que lo llevará cuando se active.

## Qué quiere el autor

- **A partir del episodio 052**, en vez de la imagen fija, un **vídeo con el transcript en pantalla** sincronizado con
  la voz. Del 001 al 051 se quedan como están (imagen fija + audio).
- Subirlo a **YouTube** y a **todas las plataformas que admitan vídeo** (Spotify, como mínimo).
- **No se monetiza.** Decisión firme del autor (repetida el 18-nov; ya estaba en `docs/fabrica-de-voz.md`). Todo lo
  que dependa de monetizar (Partner Program de Spotify, ingresos de YouTube) queda fuera de este plan.

Esto modifica la decisión del 4-nov «No se monta vídeo» (`docs/contexto-sesion-direccion.md`): sigue valiendo para
el 001–051; desde el 052 sí se monta vídeo.

## La ventaja de partida: la sincronía ya existe

La fábrica genera frase a frase y escribe en la carpeta de Drive de cada episodio **`indice_master.tsv`**: el segundo
del master en que empieza cada frase (clip y número de frase). Lo escriben tanto la fábrica como `montar_cortos`
(los episodios montados desde un largo también lo tienen; comprobado en el código el 18-nov). El `registro_tts.jsonl`
guarda además la duración de cada clip.

Consecuencia: el texto en pantalla va **exacto por construcción**, sin Whisper, sin alineación forzada y sin gastar
unidades de Colab. El texto sale de `transcript.es.json` (mismas frases que leyó el TTS).

## Formato de vídeo propuesto (pendiente de que el autor lo vea en un prototipo)

16:9, 1080p, estilo «lectura»:

- la **frase que suena, grande y centrada**; la anterior y la siguiente atenuadas encima y debajo;
- **quién habla** (Naval, Nivi, invitado) con nombre y un color por voz;
- **título del episodio y de la sección** arriba; **barra de progreso** fina abajo;
- **fondo fijo** de marca, sin animaciones caras.

Karaoke palabra a palabra: **no de entrada** (exige tiempos por palabra; resaltar la frase basta con frases de TTS de
pocos segundos). Se puede añadir después alineando con el texto conocido.

## Cómo se renderiza (propuesta técnica)

1. Script nuevo en `scripts/` que lee `transcript.es.json` + `indice_master.tsv` y escribe un subtítulo **ASS**
   (estilos, posiciones, colores por hablante, frase actual y vecinas).
2. **ffmpeg** quema el ASS sobre el fondo, con el master como audio → `.mp4` H.264 + AAC, `+faststart`.
3. CPU basta (local o Colab sin GPU). Medir la velocidad con un episodio antes de dar cifras; si fuera lenta, la T4
   de Colab tiene NVENC.

Descartados: **Remotion** (React) y generar fotogramas con Python. Un episodio de 2 h son ~180.000 fotogramas a 25 fps;
mucho más lento y sin ventaja para este formato.

Subproductos casi gratis del mismo script:

- **`.srt`** para subir a YouTube como subtítulos (accesibilidad, búsqueda, traducción automática).
- **Capítulos** en la descripción de YouTube, si `titulos_seccion` se puede situar en bloques (por comprobar).
- **Clips verticales 9:16** (Shorts, Reels, clips de Spotify) con otra plantilla del mismo motor.

`scripts/render-video.sh` (imagen fija) sigue sirviendo para el 001–051.

## Plataformas, encajadas con lo ya decidido

La publicación ya montada (`docs/contexto-sesion-direccion.md`, `docs/rss.md`, `docs/sop-publicacion.md`):
feed propio `https://spanishnav.al/podcast.xml` con el audio en R2. Spotify y Apple leen ese feed. YouTube se sube
**a mano** en YouTube Studio («contenido alterado: sí»), sin RSS, hasta tener permiso de Naval.

| Plataforma | Cómo llega el vídeo | Notas |
|---|---|---|
| **YouTube** | Subida a mano del `.mp4` dinámico en vez del de imagen fija | Mismo proceso del 5-nov; subir también el `.srt` |
| **Spotify** | En **Spotify for Creators**, en cada episodio que ya llegó por el feed: ⋯ → *Upload video* | Función para programas **no alojados en Spotify**: sustituye el audio por vídeo solo dentro de Spotify. El feed propio no cambia. Esos episodios no se pueden monetizar (irrelevante: no se monetiza). Subida solo desde la web; MP4, 16:9 |
| **Apple Podcasts** | Solo audio, por el feed | Apple admite vídeo desde feb-2026 solo por HLS y desde ciertos alojamientos (Acast, Transistor, Omny, Podigee, Buzzsprout…). Con feed propio en R2, no. No compensa cambiar de alojamiento |
| Resto (Amazon, iVoox, Substack…) | Solo audio, por el feed | — |

Spotify no se aloja en Spotify for Creators: el 5-nov el programa antiguo de Spotify for Creators se redirigió (301)
a nuestro feed. La subida de vídeo se hace igualmente desde Spotify for Creators, sobre el programa reclamado.

## Riesgos

- **Derechos**: el plan aumenta la exposición (vídeo en dos plataformas, ~100 episodios). Sigue vigente el riesgo
  aceptado el 5-nov mientras llega el permiso de Naval; sin monetizar es menor, pero no desaparece.
- **Política de YouTube sobre contenido «no auténtico»/reutilizado**: afecta sobre todo a la monetización. Sin
  monetizar, el riesgo práctico es bajo; mantener la declaración de contenido alterado.

## Estado (18-nov)

- Decidido por el autor: estilo **lectura**, se empieza con pruebas pequeñas y se refuerza; render **en Colab**
  (CPU); pruebas con el **053 en adelante** (el 052 dura horas).
- Hecho: `scripts/video_lectura.py` (ASS + ffmpeg, fondo liso, barra de progreso, también escribe el `.srt`) y el
  cuaderno `scripts/video_lectura.ipynb`. Probado en local con los tiempos reales del 053 y audio mudo: 1,5 min de
  vídeo en 13 s (7× tiempo real, 4 núcleos). Colab CPU tiene 2: esperar ~3×.
- **Prueba del autor en Colab con el 053: funciona** (18-nov). Siguiente: el estilo (fuente, animación del texto).

## Animaciones (18-nov): cómo integrar un diseño de Claude Design

El autor quiere que Claude Design diseñe las animaciones. Claude Design entrega HTML/CSS/React; hay dos formas de
llevarlo al vídeo:

1. **Traducirlo al ASS actual** (lo que hace libass: fundidos, desplazamientos `\move`, escala y color animados con
   `\t`, desenfoque, revelado con `\clip`, resaltado palabra a palabra). Render rápido (~7× tiempo real en local).
   Límites: curvas de aceleración pobres, sin muelles, sin sombras ni degradados animados.
2. **Renderizar el diseño tal cual con Remotion** (React → vídeo, fotograma a fotograma en Chromium). Fiel al diseño,
   pero mucho más lento: un fotograma de navegador por cada 1/25 s. Licencia gratuita para particulares.

Decisión: pedir a Claude Design un prototipo **gobernado por el tiempo** (ver el encargo en la respuesta del 18-nov) y,
con el diseño delante, elegir: ASS si cabe en su vocabulario, Remotion si no, midiendo antes con el 053.

## Primer paso cuando se active (versión original)

Prototipo de **2 minutos del 052** (fondo, frase centrada, hablante, barra) para que el autor elija el estilo antes de
renderizar nada largo. Decisiones que quedan para entonces: **estilo** (lectura centrada, recomendado, o subtítulos
abajo) y **dónde renderizar** (local o Colab).

## Fuentes (consultadas el 18-nov)

- Spotify: [vídeo en programas no alojados en Spotify](https://support.spotify.com/us/creators/article/video-episodes-for-shows-not-hosted-with-spotify/),
  [especificaciones de vídeo](https://support.spotify.com/us/podcasters/article/video-specs/),
  [publicar vídeos](https://support.spotify.com/us/podcasters/article/uploading-video-files/).
- Apple: [vídeo en Apple Podcasts (feb-2026)](https://www.apple.com/newsroom/2026/02/apple-introduces-a-new-video-podcast-experience-on-apple-podcasts/),
  [alojamientos con HLS (Transistor)](https://transistor.fm/apple-podcasts-video/).
