# SOP: subir el audio de un episodio a R2

> **Parte 1 (infraestructura): validada** el 2026-10-31.
> **Parte 2 (subida por episodio): borrador.** Se valida con el Ep. 1 y entonces se
> completan el formato del MP3 y los datos que se apuntan en el repo.

El audio que escucha el público vive en **Cloudflare R2** y se sirve en
`https://audio.spanishnav.al`. Lo leen la web y, más adelante, el feed de Spotify y Apple.
No confundir con Google Drive, que guarda el material de trabajo (clips, proyectos de
Audacity, vídeos): ver [`docs/almacenamiento.md`](../almacenamiento.md).

## Parte 1: infraestructura (una sola vez)

### Lo que hay montado

| Pieza | Valor |
|---|---|
| Bucket | `spanishnaval` (cuenta de Cloudflare de Andrei) |
| Dominio público | `audio.spanishnav.al`, conectado en R2 → bucket → Settings → Custom Domains |
| URL de desarrollo `r2.dev` | **Desactivada** el 2026-10-31. Tiene límite de peticiones y Cloudflare la desaconseja para producción |
| Token de la API | **Account API token**, permiso **Object Read & Write**, solo para el bucket `spanishnaval` |
| Endpoint S3 | `https://d7303b40fa9d03af787d56d0360e6f97.r2.cloudflarestorage.com` |
| rclone | Remoto **`r2`** en el ordenador del autor, en `~/.config/rclone/rclone.conf` (permisos 600) |
| Web | `AUDIO_BASE = 'https://audio.spanishnav.al'` en `lib/site.ts` de `spanishnaval-web` |

**Las claves del token no están en ningún repo ni en ningún chat.** Solo en
`rclone.conf`, escritas a mano en el asistente de rclone. Si se pierden, se crea un token
nuevo y se revoca el antiguo; no hay forma de recuperarlas.

### Rehacer la configuración de rclone (ordenador nuevo o token perdido)

1. **Crear el token.** Cloudflare → R2 → **Manage API Tokens** → **Create Account API
   token**. Permiso **Object Read & Write**, aplicado solo al bucket `spanishnaval`.
   Cloudflare enseña una vez la Access Key ID, la Secret Access Key y el endpoint.
2. **Crear el remoto, en una terminal normal, no en un chat:**

   ```bash
   rclone config
   ```

   `n` (nuevo) → nombre `r2` → **Amazon S3 Compliant Storage Providers** → **Cloudflare
   R2** → `env_auth` **false** → pegar Access Key ID y Secret Access Key → `region` por
   defecto → `endpoint` el de la tabla. `bucket_object_lock_enabled`: Enter (false).
   **Edit advanced config: `n`**. `y` para guardar, `q` para salir.

   Se usa el asistente y no `rclone config create …` para que la clave no quede en el
   historial de la terminal.
3. **Corregir lo que el asistente deja mal.** La primera vez el resumen salió sin endpoint
   y con `provider: Cloudflare R2`. Este comando lo arregla y no lleva claves:

   ```bash
   rclone config update r2 provider=Cloudflare endpoint=https://d7303b40fa9d03af787d56d0360e6f97.r2.cloudflarestorage.com no_check_bucket=true
   ```

4. **Comprobar** sin enseñar la clave: `rclone config show r2 | grep -v secret`.

### Prueba de humo

Es la que se pasó el 2026-10-31, con una sesión local de Claude Code que **no** veía las
claves:

```bash
rclone listremotes                                   # debe salir r2:
rclone lsf r2:spanishnaval --max-depth 1             # lista lo que hay
echo prueba > /tmp/rclone-ok.txt
rclone copyto /tmp/rclone-ok.txt r2:spanishnaval/pruebas/rclone-ok.txt
curl -sI https://audio.spanishnav.al/pruebas/rclone-ok.txt   # debe dar 200
rclone deletefile r2:spanishnaval/pruebas/rclone-ok.txt
curl -sI https://audio.spanishnav.al/pruebas/rclone-ok.txt   # debe dar 404
```

## Parte 2: subir un episodio (borrador)

### Nombre del archivo

```
<año>/<NNN>-<slug-del-título>.mp3
```

Es el mismo nombre que la carpeta del episodio en el repo, con `.mp3`. Por ejemplo, el
episodio en `episodios/2019/001-seek-wealth-not-money-or-status/` va en
`2019/001-seek-wealth-not-money-or-status.mp3`, y se oye en
`https://audio.spanishnav.al/2019/001-seek-wealth-not-money-or-status.mp3`.

**Esa dirección no cambia nunca una vez publicada.** El feed de Spotify y Apple la usará
como enlace permanente: si cambia, el episodio deja de sonar en todas las apps.

### Pasos

1. **Exportar el MP3** desde el audio final de Audacity.
   *Pendiente:* calidad, mono o estéreo y etiquetas. Se fijan con el Ep. 1, comprobando
   antes los requisitos actuales de Apple y Spotify en sus fuentes oficiales.
2. **Subirlo:**

   ```bash
   rclone copyto <archivo.mp3> r2:spanishnaval/<año>/<NNN>-<slug-del-título>.mp3 -P
   ```

3. **Comprobar** que responde con el tipo correcto:

   ```bash
   curl -sI https://audio.spanishnav.al/<año>/<NNN>-<slug-del-título>.mp3
   ```

   Debe dar `200` y `content-type: audio/mpeg`.
4. **Escucharlo** abriendo esa dirección en el navegador.
5. **Apuntarlo en el repo.**
   *Pendiente:* qué campos de `metadata.es.json` recogen el audio (clave, duración, bytes).
   Se decide con el Ep. 1.

### Reglas

- Solo `copy` y `copyto`. **Nunca `rclone sync` ni `rclone delete`** sobre el bucket: borran
  lo que no esté en origen.
- Para sustituir un audio ya publicado, se sube con el mismo nombre y se avisa: las apps
  pueden tardar en ver el cambio por la caché.
- La subida se hace desde el ordenador del autor. Las sesiones web de Claude Code no llegan
  a R2: su red lo bloquea.

## Automatización prevista

Cuando la parte 2 esté validada, un script (`scripts/subir-audio.sh`) hará en un solo paso:
convertir a MP3, nombrar desde la carpeta del repo, subir a R2 y a la carpeta `audio/` de
Drive, comprobar la dirección y apuntar duración y tamaño en `metadata.es.json`.
