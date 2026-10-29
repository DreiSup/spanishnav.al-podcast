# Fábrica de contenido: publicar cada episodio en todas partes

> Memoria de trabajo, fijada el 2026-10-28. Recoge lo que el autor quiere conseguir
> después de la fábrica de voz (`docs/fabrica-de-voz.md`). Los SOP concretos se escriben
> **con el autor, al subir el primer episodio de prueba a cada plataforma**, no antes.

## El objetivo

Con un episodio ya limpio en Audacity, el autor lanza **un solo workflow** y el episodio
queda publicado en todas las plataformas. Para eso hace falta un SOP por plataforma.

```
audio limpio (Drive)  ──►  workflow de publicación  ──►  web spanishnav.al
                                                     ├─► YouTube
                                                     ├─► Spotify
                                                     ├─► Apple Podcasts
                                                     ├─► Substack
                                                     └─► X (por confirmar)
```

## Tareas principales (urgentes)

1. **La web spanishnav.al**, lista para alojar todos los episodios igual que nav.al. El
   dominio ya está comprado. Según el contexto del proyecto:
   - stack: Next.js 15 en Vercel;
   - estética: réplica minimalista de nav.al;
   - audio: entregado desde Cloudflare R2.
2. **El SOP de YouTube.** Claude Code tiene que poder:
   - **montar el vídeo**: audio más imagen fija con FFmpeg (`scripts/render-video.sh`,
     sin probar). En el futuro, quizá un vídeo con los subtítulos del podcast en tiempo
     real;
   - **preparar un documento con el título y la descripción**. La descripción enlaza tres
     cosas:
     - el episodio original en el canal de YouTube de Naval;
     - el episodio en nav.al;
     - el episodio en spanishnav.al;
   - **subirlo él mismo** si puede conectarse a la cuenta de YouTube. Si no, lo sube el
     autor a mano.
3. **Spotify.**
4. **Apple Podcasts.**
5. **Substack.**
6. **X**, si se puede sin suscripción. Está por confirmar.

## Extra

- **Un SOP de contenido corto** a partir de cada episodio, para Instagram, Facebook y
  TikTok.

## Lo que ya se sabe (de CLAUDE.md, docs/youtube.md y el contexto del proyecto)

- **YouTube**:
  - El canal y la cuenta de marca ya están creados.
  - Mientras la app OAuth no pase la verificación de Google, los vídeos que suba la API
    quedan en **privado**. La vía viable: la API sube en privado con título, descripción y
    miniatura, y el autor publica a mano en YouTube Studio.
- **El enlace al vídeo original de Naval** sale del listado del canal @NavalR. Hay un
  listado parcial hecho con yt-dlp (`navalr_videos.json`: 268 vídeos, 177 sin fecha); el
  procedimiento está en `docs/youtube.md`.
- **Spotify y Apple Podcasts** se alimentan de **un único feed RSS**, que se configura una
  sola vez. Ese feed es la pieza clave: con él, las dos plataformas se actualizan solas
  con cada episodio nuevo.
- **La descripción** ya tiene plantilla: `metadata.es.json → youtube.descripcion`, ver
  `035-a-calm-mind-a-fit-body-a-house-full-of-love`.
- **El aviso de IA** va en cada episodio, en español y en inglés.

## Pendiente de decidir con el autor

- **Dónde vive el código de la web.** No está en este repo.
- **Quién genera el feed RSS.** Lo natural es que lo genere la web a partir de los
  `metadata.es.json` del repo, con el audio en R2.
- **Si Substack** lee el mismo feed o necesita una subida por episodio.
- **Si X** permite vídeos largos sin suscripción Premium.
