# Contexto de la sesión de dirección

Memoria de la sesión global (dirección del proyecto) para retomarla tras un `/compact` o en una sesión nueva.
Última actualización: 2026-11-05. Rama: `claude/quirky-dirac-x18c3n`.

Se lee después de `CLAUDE.md` y `docs/contexto-sesion-global.md` (traspaso de la sesión técnica, con sus
decisiones). Aquí está lo que **no** está en esos dos: infraestructura de publicación, decisiones tomadas con el
autor en esta sesión, cómo trabaja el autor y lo pendiente.

## 1. El papel de esta sesión

Dirección: visión de conjunto, coordinación entre sesiones (técnica, traducción, contenido) y los SOP, escritos con
el autor **haciendo cada proceso a mano la primera vez**. No toca `fabrica/`, `piloto/`, `criba/` ni los
transcripts: si un SOP necesita un cambio técnico, se describe y el autor se lo pasa a la sesión técnica.

## 2. Cómo trabaja el autor

- Un paso cada vez, con su confirmación explícita. Cada decisión técnica, explicada.
- Nada se publica fuera (subidas, altas en plataformas, despliegues a producción, push a `main` de la web) sin su
  OK.
- Antes de afirmar algo de una plataforma (límites, requisitos), verificarlo con una fuente actual y citarla.
- Todo en español. Quiere todos los procesos documentados; un SOP solo es «validado» si se ha hecho a mano.
- Prefiere mínimo gasto de Colab y decide escuchando.
- Lleva tareas en Google Tasks, lista **spanishnav.al** (id `NXZwU0dMMk50MnRKS2M2OA`). El conector a veces pide
  autorización de nuevo.

## 3. Decisiones tomadas en esta sesión

| Fecha | Decisión |
|---|---|
| 28-oct | Web: rediseño de Claude Design implementado (repo `DreiSup/spanishnaval-web`). |
| 29-oct | Audio público en **Cloudflare R2**, no en GitHub ni Vercel (comparativa de límites hecha). |
| 31-oct | DNS de `spanishnav.al` pasado de Upflare a **Cloudflare**; `audio.spanishnav.al` conectado al bucket; `r2.dev` desactivado. Detalle en `docs/infraestructura-dns.md` y `docs/infraestructura-r2.md`. |
| 2-nov | La fábrica manda: los datos se moldean a ella. Carpetas `<NNN>-<slug>` con el slug de nav.al (se deshizo el cambio a slug por título). `main` y `quirky-dirac` quedaron idénticas ese día; desde entonces todo se sube a `quirky-dirac`. |
| 4-nov | **Publicación por RSS** (opción B): un solo feed alimenta YouTube (crea los vídeos con imagen fija), Spotify, Apple y la web. **No se monta vídeo.** |
| 4-nov | Nombre del podcast: **Naval Podcast en español**. Una portada para todo, de momento. |
| 4-nov | Datos fijos del feed y plantilla de descripción: `docs/sop-publicacion.md`, apartados 1 y 3. |
| 4-nov | Modelos en la descripción con nombre concreto: **Claude Opus 5.5 (esfuerzo alto)** y **Qwen3-TTS**. |
| 4-nov | Primer episodio que estrena el SOP completo: **001 Seek Wealth** (se publica en orden desde el 1). |
| 5-nov | **YouTube a mano, sin RSS, hasta tener permiso de Naval.** Las condiciones del servicio de RSS de YouTube obligan a garantizar que tienes los derechos; el autor no las aceptó. Se sube el `.mp4` (imagen fija + audio, con ffmpeg) en YouTube Studio, declarando «contenido alterado: sí». Spotify y Apple sí van por el feed. Riesgo aceptado mientras llega el permiso: también las condiciones generales de YouTube, Spotify y Apple piden derechos. |
| 5-nov | Dominio principal **`spanishnav.al`** (sin www), sin redirección; `www` también sirve la web. Feed: `https://spanishnav.al/podcast.xml`. |
| 5-nov | **Portada nueva del feed** (logo «en español» del autor), en `public/portada.jpg` (2000×2000, ampliada de la 1254 que llegó por el chat), ya en `main`. La rectangular de YouTube no cambia. Carpeta `naval-podcast/portadas` en Drive (id `1AZ-AILhxbmgraVm_QxIwnmAOq_xo1i9L`): el autor sube ahí la 4K original y la de 2000. |
| 5-nov | **Cortos dentro de largos** (`docs/cortos-y-largos.md`, `cortos.json`): 077, 105 y 130 se generan una vez y sus 71 cortos se montan con sus clips. In the Arena y AI Industrial Revolution, igual cuando se traduzcan. El 052 se monta uniendo los cortos 001–050. Instrucciones para la sesión técnica escritas; **el autor las pasará cuando quiera**, no es prioridad. |

## 4. Infraestructura de publicación (todo montado)

| Pieza | Dónde | Detalle |
|---|---|---|
| Dominio | Registrado en **Upflare** | DNS en Cloudflare (`ara`/`jasper.ns.cloudflare.com`), zona activa desde el 31-oct |
| Web | **Vercel**, repo `DreiSup/spanishnaval-web` | Next.js 16. `main` = producción. Rama de trabajo `claude/cool-heisenberg-5ecig9` |
| Audio público | **R2**, bucket `spanishnaval` | `https://audio.spanishnav.al/<año>/<NNN>-<slug>.mp3`. Tiene el 001 |
| Subida a R2 | **rclone**, remoto `r2`, en el ordenador del autor | Account API token, Object Read & Write, solo `spanishnaval`. La clave nunca pasa por un chat |
| Portadas | Repo de la web, `public/portada.jpg` (2000×2000) y `public/portada-youtube.jpg` (1677×938) | En `main` (producción) |
| Correo | **Zoho**, `podcast@spanishnav.al` | DMARC `p=reject`: cuidado con los TXT |

Las sesiones web de Claude **no llegan** a R2, `audio.spanishnav.al`, `spanishnav.al`, YouTube ni nav.al (proxy).
Vercel sí se consulta por su conector (`get_domain_config`). Drive, por el conector (no audio).

### La web hoy

- **En producción el 001 real** (5-nov), sin los episodios de prueba. Su texto sale de
  `content/episodios/2019/001-seek-wealth.json` (copia del `transcript.es.json`); audio y fechas en `lib/episodes.ts`.
- Feed **`/podcast.xml`** (`lib/feed.ts`, estático): datos fijos en `lib/site.ts` → `podcast`, descripción de cada
  episodio con la plantilla del SOP. Fecha de cada episodio = la de publicación de la traducción.
- `lib/site.ts`: plataformas a `null` («Próximamente») hasta tener los enlaces; `feed: '/podcast.xml'`.
- Rutas: `/`, `/<slug>`, `/archivo`, `/suscribirse`, `/buscar`, `/categoria/<slug>`, 404. `/riqueza` redirige a
  `/seek-wealth`.
- El feed RSS **no existe todavía**: se generará en la web (`spanishnav.al/podcast.xml`, a confirmar).

## 5. Drive (ids útiles)

| Qué | Id |
|---|---|
| `naval-podcast/transcripts/` (carpetas de episodio de la fábrica) | `1QskPXdV5i848dlmAL4-XAb78EtCpZKkz` |
| `transcripts/2019` | `1QStnJngv2OC16AzM26Lfs3nqTv4cbtd0` |
| `transcripts/2020` | `1CDVbuLApf8SevsBqzvAvaTdtGZDcTz2Q` |
| Google Doc «2019 all podcasts» (inglés de nav.al, 53 episodios) | `1Wt_qYUA9xmXGgCcr1SszkaeCWad4yzIopvhPxBn9aIs` |
| «2020 all podcasts» | `1ypm4YCDL6dPqen2JWgaZmXlEFOJQxrVTYq3ADUc9D6o` |
| «2021» … «2026 all podcasts» | `1QZKfa3e…`, `1kg3_IKD…`, `1dGW9DL5…`, `1VSsMsKo…`, `1rSia1_l…`, `1bD9xr8B…` (búscalos por título) |

Cada episodio en Drive: `transcripts/<año>/<NNN Título en inglés>/` con `audio/<NNN>-<slug>.mp3` (master),
`informe_tts.md`, `indice_master.tsv`, `tts/`. Las muestras de voces nuevas van en subcarpetas `muestra/` (no son
masters publicables).

## 6. Coordinación con las otras sesiones

- **Traducción**: sube directamente a `quirky-dirac` (no a Drive, aunque se le propuso). Su registro:
  `docs/traduccion.md`. Cuando el autor lo pide, esta sesión **revisa** los episodios: normalizador con
  `--simular` (cero avisos; `--slug` si el título lleva apóstrofo curvo), cobertura es/en por bloque entre 0,85 y
  1,45, hablantes en `fabrica/voces.json`, caracteres que el TTS vocaliza, y lectura del español frente al inglés.
  Revisados y aprobados: 036, 040, 052 (arreglos), 053–062 y 065–067. 063 y 064 no estaban.
- **Técnica**: lleva `docs/estado.md`. Falsos avisos de Whisper detectados para pasarle: «adonde» / «a donde»
  (muestra del 068).

## 7. El SOP de publicación: estado

`docs/sop-publicacion.md`:

| Apartado | Estado |
|---|---|
| Ruta (RSS para todo) | Decidido |
| 1. Datos fijos del feed y portadas | Decidido, sin validar |
| 2. Subir el master a R2 | Por hacer con el 001 (infraestructura validada: `docs/infraestructura-r2.md`) |
| 3. Descripción de cada episodio | Decidido, sin validar |
| 4. Generar el feed (web) | Pendiente |
| 5. Alta en YouTube, Spotify y Apple (una vez) | Pendiente |
| 6. Publicar cada episodio y mover el estado a `publicado` | Pendiente |

## 8. Estado del 001 y lo siguiente (5-nov, tarde)

**El 001 está publicado.** Escuchado entero por el autor: bueno, sin arreglos.

| Dónde | Cómo | Estado |
|---|---|---|
| Web y feed | `spanishnav.al/seek-wealth`, `podcast.xml` | Publicado |
| YouTube | A mano (SOP 5 bis), canal `@spanishNavalR` | https://www.youtube.com/watch?v=s10rGZckyEo |
| Spotify | Redirección 301 del programa que el autor ya tenía en Spotify for Creators → nuestro feed | Hecha el 5-nov; tarda hasta 7 días. No borrar el programa ni la cuenta antes del 12-nov |
| Apple Podcasts | Borrador + Add RSS Feed → Publish | En revisión (id `6831305665`) |
| Substack | «Distribute to Substack» → «I have a podcast hosted elsewhere» → feed | Publicado solo desde el feed: https://spanishnavalravikant.substack.com/ (post del 001: https://substack.com/home/post/p-223678266) |
| X | — | **Descartado** por el autor (5-nov): sin RSS y sin Premium solo 2:20 de vídeo |

Web (`lib/site.ts` → `platforms`): YouTube y Spotify en `main`. Substack, en la rama de la web a la espera
del OK para `main`. Falta Apple (cuando lo aprueben).

**Cada episodio nuevo, desde ahora:** master → R2 → episodio en la web y push a `main` (con OK del autor) → Spotify,
Apple y Substack lo cogen del feed solos. YouTube, a mano: la sesión le da al autor solo título y descripción.

**Entorno de las sesiones (7-nov):** «spanishnav.al» (personal), con `spanishnav.al`, `www.spanishnav.al` y
`audio.spanishnav.al` permitidos además de `nav.al`: la sesión ya puede comprobar web, feed y audios de R2 (antes daban
403 en el proxy). YouTube, Substack y las páginas de ayuda de Apple siguen fuera.

**Idea del autor (6-nov): dejar listos todos los episodios traducidos y publicar uno al día, programado.** Piezas:
- R2: subir los masters por adelantado (la dirección no se anuncia hasta que el feed la incluye).
- Web y feed: cargar todos los episodios con su fecha `published` futura, que la web y el feed solo muestren los de
  fecha ≤ hoy, y una reconstrucción diaria de Vercel (el feed es estático: sin redeploy no aparece el del día).
- YouTube: subirlos por la API con `publishAt` (programados). Depende de si la API deja los vídeos en privado
  (sin aclarar; se prueba con el 003). Tarea del autor para el 7-nov: configurar Google Cloud (proyecto, YouTube Data
  API v3, consentimiento «In production», cliente OAuth de escritorio en los Secretos de Colab).
- 002: publicado el 6-nov (YouTube a mano, R2, web y feed). Falta apuntar el enlace del vídeo en `youtube.url`.

**Ideas apuntadas, sin empezar:** subir los episodios (o trozos) a Instagram, Facebook y TikTok. Ninguna lee RSS de
podcast que se sepa; investigarlo cuando toque.

Pendiente aparte: correo a Naval pidiendo permiso (ofrecido redactarlo); con el sí, pasar YouTube a RSS.

Otros pendientes del autor, sin prisa: contenido en Instagram, Facebook y TikTok; limpiar los
registros DNS sobrantes de Upflare (`mail`, `ftp`, la parte `ip4`/`mailchannels` del SPF); el 052 (recopilación de
1–50), decisión pendiente en `docs/contexto-sesion-global.md` §7.
