# Por qué el audio y el vídeo no están en el repo

## El problema

GitHub rechaza archivos de más de 100 MB y avisa a partir de 50 MB. Un episodio
de podcast de una hora son ~60 MB en mp3 y varios cientos de MB en wav; los
clips sueltos de TTS, decenas más. Además git guarda **cada versión** de cada
binario para siempre: regeneras el audio tres veces y el repo pesa el triple,
incluso después de borrar los archivos.

## La decisión

`.gitignore` excluye `*.mp3 *.wav *.mp4 ...` y las carpetas `tts/`, `audio/` y
`video/` de cada episodio. Se versiona lo que es fuente y no se puede
regenerar: transcripciones, traducciones, metadatos, notas y thumbnails (que
pesan poco y son parte del entregable).

Si mañana pierdes la carpeta local, con el repo puedes reconstruir cualquier
episodio: la traducción está, el TTS se vuelve a generar y los scripts hacen el
resto.

## Si aun así quieres versionar el audio

Tres opciones, de menos a más fricción:

1. **Git LFS** — `.gitattributes` ya trae los patrones preparados, comentados.
   Descoméntalos, quita esos mismos patrones de `.gitignore` y ejecuta
   `git lfs install`. Ojo: la cuota gratuita de GitHub es de 1 GB de
   almacenamiento y 1 GB/mes de tráfico; se agota rápido con audio.
2. **Publicar el final como GitHub Release** — sube el mp3/mp4 de cada episodio
   como adjunto de una release (hasta 2 GB por archivo). No infla el repo y
   deja el entregable descargable con una URL estable.
3. **Almacenamiento externo** — Drive, S3, Backblaze B2. Guarda solo el enlace
   en `metadata.json`.

Para un repo de trabajo, la opción 2 cubre casi siempre lo que hace falta.
