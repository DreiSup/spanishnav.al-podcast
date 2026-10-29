# Prompt: sesión de la fábrica de contenido

Prompt para abrir una sesión nueva de Claude Code dedicada a publicar los episodios (web,
feed RSS, YouTube, Spotify, Apple Podcasts, Substack, X y contenido corto). Otra sesión
lleva en paralelo la fábrica de voz; esta no la toca.

```
Trabajo en spanishnav.al, el doblaje al español del podcast de Naval Ravikant. En esta
sesión quiero avanzar con la FÁBRICA DE CONTENIDO: que, con un episodio ya doblado y
limpio en Audacity, un solo workflow lo publique en todas las plataformas. La fábrica
de VOZ (elegir el motor TTS, fine-tuning, cuadernos de Colab) la lleva otra sesión en
paralelo: no la toques.

## Contexto que tienes que leer, en este orden

El repo es DreiSup/spanishnav.al-podcast. La documentación está en la rama
claude/quirky-dirac-x18c3n, no en main. Haz fetch de esa rama y léela desde ahí.

1. CLAUDE.md, entero. Estructura del repo, esquemas JSON y reglas. La más importante:
   GitHub guarda texto y punteros, Google Drive guarda bytes.
2. docs/fabrica-de-contenido.md: el objetivo de esta sesión y lo pendiente de decidir.
3. docs/rss.md: cómo funciona el feed RSS y por qué recomendamos un feed propio.
4. docs/youtube.md: cómo se consigue el enlace al vídeo original de Naval.
5. docs/almacenamiento.md: Drive, rclone y por qué el audio nunca entra en git.
6. Un episodio de ejemplo completo: episodios/2019/035-finally-wealthy/, sobre todo
   metadata.es.json, que ya trae la plantilla de la descripción de YouTube.
7. catalogo.json (solo su estructura) e INDICE.md.
8. scripts/render-video.sh (está sin probar).
9. Solo los apartados "Reglas" y "Objetivo final" de docs/fabrica-de-voz.md, para
   saber qué produce la otra sesión: un .wav por intervención de cada hablante, que yo
   limpio y monto en Audacity.

## Contexto que no está en el repo

- **Web.** El dominio spanishnav.al ya está comprado y apunta a Vercel. El stack es
  Next.js 15, TypeScript, Tailwind y shadcn/ui, con shadcn solo como primitivas
  accesibles y sin su estilo. La web es un clon fiel de la estética minimalista de
  nav.al: una columna centrada de unos 640 px, fondo blanco, separadores finos y un
  reproductor de audio propio. En todas las páginas, arriba a la derecha, va un botón
  "Ver original ↗" que enlaza a nav.al con el mismo slug. Orden de construcción: Home →
  Episodio → Archivo → Suscribirse → Categoría → Búsqueda → casos límite. El código de
  la web NO está en este repo: pregúntame dónde está antes de tocar nada.
- **Audio para el público.** Va en Cloudflare R2. El bucket y las carpetas ya están
  creados, con una URL pública de desarrollo activa.
- **Correo.** podcast@spanishnav.al, con Zoho Mail y SPF, DKIM y DMARC configurados.
- **YouTube.**
  - La cuenta de marca y el canal ya existen.
  - Cada vídeo es la imagen fija más el MP3, montado con FFmpeg.
  - La descripción enlaza tres cosas: el vídeo original en el canal de Naval
    (@NavalR), el episodio en nav.al y el episodio en spanishnav.al.
  - Cada episodio lleva el aviso de IA, en español y en inglés.
  - Tengo en local un listado del canal de Naval sacado con yt-dlp
    (navalr_videos.json): 268 vídeos, 177 de ellos sin fecha.
- **Ya decidido.** Spotify y Apple Podcasts se alimentan de un único feed RSS propio:
  lo genera la web a partir de los metadata del repo y el audio sale de R2.
- **Seguimiento.** Tengo una base de 169 episodios en Notion con las etapas de
  producción.

## Qué quiero de esta sesión

Tareas principales, por este orden de importancia:
1. La web lista para alojar todos los episodios, como nav.al.
2. El feed RSS y el alta en Spotify y Apple Podcasts.
3. El SOP de YouTube. Claude monta el vídeo, prepara un documento con el título y la
   descripción, y lo sube si puede. Ojo: mientras la app OAuth no esté verificada por
   Google, lo que suba la API queda en privado y la publicación la hago yo a mano en
   YouTube Studio. Más adelante, quizá vídeos con subtítulos en tiempo real.
4. Substack.
5. X, si se puede sin suscripción Premium.

Extra: un SOP de contenido corto para Instagram, Facebook y TikTok.

## Reglas

- **Un paso cada vez y con mi confirmación explícita.** Cada decisión técnica tiene
  que poder explicarse. Primero lo mínimo que funcione; se optimiza después.
- **Los SOP de cada plataforma se escriben conmigo al subir el primer episodio de
  prueba**, no antes y no por suposición.
- **Nada se publica fuera sin mi OK explícito**: ni subidas, ni altas en plataformas,
  ni posts, ni despliegues a producción.
- **Todo en español**, en UTF-8. Nunca audio ni vídeo en git.
- **Trabaja en tu propia rama y no toques** criba/, scripts/dataset/ ni
  docs/fabrica-de-voz.md, que son de la otra sesión. No abras pull requests salvo que
  te lo pida.
- **Antes de dar algo por hecho sobre una plataforma** (límites de X, si Substack lee
  un RSS, requisitos de Apple), verifícalo con una fuente actual y dime de dónde sale.

Empieza leyendo el contexto y dame un resumen corto de lo que has entendido, las
decisiones que veas pendientes y tu propuesta de primer paso. No avances sin mi OK.
```
