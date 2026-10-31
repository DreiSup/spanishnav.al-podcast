# SOP de la fábrica

Un SOP por proceso, desde el transcript de nav.al hasta cada plataforma.

**Regla del autor: un SOP solo se da por bueno cuando el proceso se ha hecho a mano al
menos una vez.** Hasta entonces es un borrador y lo dice arriba. Lo que se descubre al
hacerlo a mano se escribe aquí en el momento, no de memoria después.

Estados:

- **Validado**: hecho a mano de principio a fin y funcionando. Se puede seguir tal cual.
- **Borrador**: escrito antes de hacerlo o hecho solo en parte. Seguirlo con cuidado y
  corregirlo al hacerlo.
- **Sin hacer**: todavía no hay SOP.

## Procesos

| # | Proceso | Documento | Estado |
|---|---|---|---|
| 1 | Copiar el transcript de nav.al y convertirlo | [`docs/extraccion.md`](../extraccion.md) | Validado (episodios 035–052) |
| 2 | Traducir, revisar y subir el transcript al repo | [`docs/revision-episodios.md`](../revision-episodios.md) | Validado (episodios 035–052) |
| 3 | Generar la voz: un clip por intervención | [`docs/fabrica-de-voz.md`](../fabrica-de-voz.md) | En construcción (otra sesión) |
| 4 | Limpiar y montar el audio en Audacity | — | Sin hacer |
| 5 | Subir el audio final a R2 | [`audio-r2.md`](audio-r2.md) | Infraestructura validada; subida por episodio en borrador |
| 6 | Publicar el episodio en la web | — | Sin hacer |
| 7 | Montar el vídeo y subirlo a YouTube | — | Sin hacer |
| 8 | Spotify y Apple Podcasts (feed RSS) | [`docs/rss.md`](../rss.md) (explicación) | Aparcado |
| 9 | Substack | — | Sin hacer |
| 10 | X | — | Sin hacer |
| 11 | Contenido corto: Instagram, Facebook, TikTok | — | Sin hacer |

## Infraestructura (se configura una vez)

| Pieza | Documento | Estado |
|---|---|---|
| Dominio, DNS, web y correo | [`dominio-y-dns.md`](dominio-y-dns.md) | Validado |
| Audio público en R2 y rclone | [`audio-r2.md`](audio-r2.md), primera parte | Validado |
| Google Drive y rclone | [`docs/almacenamiento.md`](../almacenamiento.md) | Validado |

## Cómo se escribe un SOP

- Pasos numerados, en el orden real, con el comando exacto o el menú exacto.
- Qué debe verse al terminar cada paso para saber que ha ido bien.
- Qué hacer si falla, con el error que salió cuando falló de verdad.
- Nunca claves ni contraseñas: solo dónde están guardadas.
- Fecha de la última vez que se siguió de principio a fin.
