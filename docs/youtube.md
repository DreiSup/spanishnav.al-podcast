# El vídeo original de cada episodio

La descripción de YouTube de cada episodio enlaza al vídeo original del canal de Naval.
Es **el único dato de la descripción que cambia entre episodios**: los otros tres enlaces,
el aviso en español y el bloque en inglés son idénticos en los 161.

## Por qué el listado se pide a Claude web

**YouTube está bloqueado desde las sesiones web de Claude Code**, igual que nav.al. La
política de egress devuelve 403 en el CONNECT para `youtube.com`, `youtu.be` y hasta para
el RSS del canal. Comprobado el 2026-09-08:

```
www.youtube.com/@NavalR/videos    403        www.googleapis.com    200
youtube.com/feeds/videos.xml      403        nav.al                403
```

`googleapis.com` sí responde, así que **con una clave de la YouTube Data API v3 el listado
se podría hacer desde aquí** (`YOUTUBE_API_KEY` en `.env`). Mientras no exista esa clave,
la vía es Claude web, igual que se hizo con `catalogo.json`.

La otra vía sin clave es `yt-dlp` en local:

```bash
yt-dlp --flat-playlist --dump-json "https://www.youtube.com/@NavalR/videos" > youtube-naval.jsonl
```

## El prompt para Claude web

```
Necesito el listado COMPLETO de vídeos del canal de YouTube de Naval Ravikant:
https://www.youtube.com/@NavalR

Contexto: estoy doblando al español el podcast de Naval y cada vídeo doblado tiene
que enlazar en su descripción al vídeo original. Necesito emparejar cada episodio
con su vídeo, y para eso me hace falta el título exacto y el ID de cada uno.

Recorre la pestaña Vídeos del canal ENTERA, del más reciente al más antiguo. Si la
página carga por tandas, sigue hasta el final: el canal tiene bastante más de cien
vídeos y necesito todos, no los primeros que veas. Mira también las playlists del
canal por si contienen vídeos que no aparecen en la pestaña Vídeos.

Devuélveme un único bloque JSON con esta forma exacta:

{
  "fuente": "<la url que hayas usado>",
  "extraido_el": "<hoy, AAAA-MM-DD>",
  "canal": "@NavalR",
  "total": <número de vídeos de la lista>,
  "completo": true,
  "notas": "<qué no has podido obtener, o cadena vacía>",
  "videos": [
    {
      "titulo": "<el título tal cual aparece, sin recortar ni traducir>",
      "video_id": "<los 11 caracteres del id>",
      "url": "https://www.youtube.com/watch?v=<video_id>",
      "fecha_publicacion": "<AAAA-MM-DD, o cadena vacía si no la ves>",
      "duracion": "<H:MM:SS o M:SS, o cadena vacía>"
    }
  ]
}

Reglas, por orden de importancia:

1. NO INVENTES NADA. Ni un título, ni un id, ni una fecha. Si no puedes leer un dato,
   déjalo como cadena vacía. Si no llegas al final de la lista, pon "completo": false
   y explica en "notas" hasta dónde llegaste y por qué. Un listado incompleto y
   honesto me sirve; uno completo e inventado me estropea el trabajo.

2. Los títulos, LITERALES. Con sus mayúsculas, sus signos y su puntuación tal cual.
   Los voy a cruzar automáticamente contra otra lista de títulos, así que cualquier
   arreglo tuyo rompe el cruce.

3. Dame TODOS los vídeos, no solo los que parezcan episodios del podcast. En el canal
   hay clips, shorts y entrevistas; ya filtro yo. No decidas tú qué sobra.

4. Si el JSON no te cabe en una respuesta, párte lo en varios mensajes: en cada uno
   repite la misma estructura y añade "parte": 1, "parte": 2, etc. Prefiero cuatro
   mensajes completos a uno recortado con "...".

Fuera del JSON, dime cuántos vídeos has contado y si crees que falta alguno.
```

## Qué se hace con la respuesta

1. **`youtube-naval.json` en la raíz**, un vídeo por línea como `catalogo.json`, para que
   los diffs se lean.
2. **Cruce por título contra `catalogo.json`**, normalizando mayúsculas, tildes y
   puntuación. Salen tres listas: coincidencias exactas, dudosas y sin pareja. **Las
   dudosas no las decide un script**: se revisan a mano.
3. **`youtube.url_original` en el `metadata.es.json`** de los episodios que estén en el
   repo y tengan coincidencia exacta.

Sobre el punto 2: los títulos de YouTube y los de nav.al no tienen por qué coincidir, así
que habrá dudosas y habrá vídeos sin pareja. El canal además tiene material que no es del
podcast. Eso no es un fallo del cruce, es cómo son los datos.

## Método nav.al (5-nov)

**El 2026-11-05 nav.al respondía desde la sesión web de Claude Code** (`curl -sSL https://nav.al/seek-wealth`
→ 200), a diferencia de lo que dice la sección «Por qué el listado se pide a Claude web», comprobada el 2026-09-08.
YouTube no se ha probado: no hacía falta.

Por eso el vídeo original no se ha sacado del canal de YouTube cruzando títulos, sino de **la propia página de
cada episodio en nav.al**, que lo enlaza en su fila de cabecera «Apple Podcasts · Spotify · YouTube». Es un dato
de la fuente, sin cruce ni emparejamiento dudoso.

### Cómo se hizo

1. Se descargaron con `curl` las 168 páginas de `catalogo.json`, una a una con 1 s de pausa, a un directorio
   temporal fuera del repo. Solo se leyeron enlaces; nada del texto de los transcripts entra en el repo.
2. De cada página se tomó el `<a>` con texto «YouTube» del bloque de cabecera (`div.podcast-links`, el
   desplegable «Get podcast»), que va justo después del de Spotify. Se aceptan `youtube.com/watch?v=<id>` y
   `youtu.be/<id>`. Los enlaces de YouTube del cuerpo del texto se ignoran: son citas a otros vídeos (en
   `nav.al/infinity` el del cuerpo es `SDZ454K_lBY`; el de cabecera, `jEmJIA0pEf0`).
3. El extractor se probó antes contra seis ids comprobados a mano (seek-wealth, judgment, happiness, infinity,
   future, angel-1): los seis coincidieron.
4. Resultado en **`youtube-originales.json`** (raíz), un episodio por línea con orden, carpeta, número, títulos,
   URL de nav.al, id y URL del vídeo y notas. `youtube_url` va siempre normalizada a
   `https://www.youtube.com/watch?v=<id>`, sin `?si=`, `&t=` ni otros parámetros.
5. `youtube.url_original` rellenado en los `metadata.es.json` de los episodios que ya están en el repo.

### Resultados

- **163 de 168 con vídeo**; **5 sin vídeo**.
- **Duplicados: ninguno.** Ningún id aparece en dos episodios.
- `metadata.es.json`: 114 rellenados; `001-seek-wealth` ya tenía el mismo valor; ninguno tenía un valor distinto.
  `084-end` se queda vacío (no hay vídeo en su cabecera).

Episodios sin vídeo (lo resuelve el autor; no se ha buscado por título en otro sitio):

| Orden | Episodio | Carpeta | Motivo |
|---|---|---|---|
| 1 | On Meditation | — (extra, sin fecha) | la página no tiene fila de cabecera |
| 2 | On Humility | — (extra, sin fecha) | la página no tiene fila de cabecera |
| 3 | A Founder's Anxiety | — (extra, sin fecha) | la página no tiene fila de cabecera |
| 4 | The Need for Indifference | — (extra, sin fecha) | la página no tiene fila de cabecera |
| 88 | There Is No End of Science (`nav.al/end`) | `2021/084-end` | el «YouTube» de cabecera apunta al canal (`youtube.com/c/NavalR`), no a un vídeo |

Los cuatro primeros son los diálogos con Kapil Gupta: `catalogo.json` no les da fecha, así que su `carpeta` queda
vacía en `youtube-originales.json` (docs/extraccion.md los sitúa en enero-febrero de 2019).

Otras observaciones, anotadas en `notas`:

- `054-material` y `068-kapil`: la cabecera solo tiene el enlace de YouTube (sin Apple ni Spotify). Se ha tomado
  ese enlace.
- `077-happiness` (`t=735s`), `130-infinity-2` (`t=4s`), `131-vitalik` (`t=1440s`) y `132-vitalik-2` (`t=1332s`):
  nav.al enlaza el vídeo empezando en un minuto concreto. La URL guardada es la del vídeo sin `t`; conviene
  mirar si el original es un vídeo más largo del que el episodio es solo una parte.
