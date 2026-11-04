# Contexto de la sesión de dirección

Memoria de la sesión global (dirección del proyecto) para retomarla tras un `/compact` o en una sesión nueva.
Última actualización: 2026-11-04. Rama: `claude/quirky-dirac-x18c3n`.

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

## 4. Infraestructura de publicación (todo montado)

| Pieza | Dónde | Detalle |
|---|---|---|
| Dominio | Registrado en **Upflare** | DNS en Cloudflare (`ara`/`jasper.ns.cloudflare.com`), zona activa desde el 31-oct |
| Web | **Vercel**, repo `DreiSup/spanishnaval-web` | Next.js 16. `main` = producción. Rama de trabajo `claude/cool-heisenberg-5ecig9` |
| Audio público | **R2**, bucket `spanishnaval` | `https://audio.spanishnav.al/<año>/<NNN>-<slug>.mp3` (aún vacío) |
| Subida a R2 | **rclone**, remoto `r2`, en el ordenador del autor | Account API token, Object Read & Write, solo `spanishnaval`. La clave nunca pasa por un chat |
| Portadas | Repo de la web, `public/portada.jpg` (2000×2000) y `public/portada-youtube.jpg` (1677×938) | En la rama `claude/cool-heisenberg-5ecig9`, **aún no en `main`** |
| Correo | **Zoho**, `podcast@spanishnav.al` | DMARC `p=reject`: cuidado con los TXT |

Las sesiones web de Claude **no llegan** a R2, `audio.spanishnav.al`, `spanishnav.al`, YouTube ni nav.al (proxy).
Vercel sí se consulta por su conector (`get_domain_config`). Drive, por el conector (no audio).

### La web hoy

- Episodios escritos a mano en `lib/episodes.ts` (dos de prueba: `seek-wealth` con un audio de XTTS y
  `ethical-wealth` en inglés). **Siguen públicos.** Hay que sustituirlos por el 001 real.
- `lib/site.ts`: `AUDIO_BASE = 'https://audio.spanishnav.al'`, plataformas a `null` (se muestran como
  «Próximamente»), `feed: null`.
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

## 8. Pendiente inmediato (4-nov)

1. **Comprobar el master del 001** en Drive (`transcripts/2019/001 …/audio/001-seek-wealth.mp3`): duración,
   formato (MP3 mono 44,1 kHz 128 kbps, -16 LUFS), informe sin sospechosas. Lo escucha el autor.
2. **Campo `youtube.url_original`** en `metadata.es.json` (plantilla y 001:
   `https://www.youtube.com/watch?v=jemPACNo1_I`). Propuesto; falta el OK del autor.
3. **Subir el 001 a R2** con el autor (rclone en su ordenador) y comprobar `https://audio.spanishnav.al/2019/001-seek-wealth.mp3`.
4. **Web**: quitar los dos episodios de prueba, poner el 001 real, publicar las portadas.
5. **Feed RSS** en la web y su validación.
6. **Altas** en YouTube Studio (Crear → Nuevo podcast → Enviar feed RSS; verificación al correo del feed),
   Spotify for Creators y Apple Podcasts Connect.
7. Ir apuntando cada paso en `docs/sop-publicacion.md` a medida que se hace.

Otros pendientes del autor, sin prisa: Substack, X, contenido corto (Instagram, Facebook, TikTok); limpiar los
registros DNS sobrantes de Upflare (`mail`, `ftp`, la parte `ip4`/`mailchannels` del SPF); el 052 (recopilación de
1–50), decisión pendiente en `docs/contexto-sesion-global.md` §7.
