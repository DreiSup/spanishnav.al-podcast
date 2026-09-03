# spanishnav.al-podcast

Repositorio de trabajo del proceso de traducción al español de los podcasts de Naval.

No es una web ni una publicación: es el sitio donde vive **el proceso** —
transcripciones, traducciones, metadatos, notas y los scripts que automatizan
el montaje. El audio y el vídeo se generan en local y **no** se versionan
(ver [docs/almacenamiento.md](docs/almacenamiento.md)).

Índice de episodios: [INDICE.md](INDICE.md)

## Estructura

```
episodios/
  2024/
    como-pensar-con-claridad/
      metadata.json              ← ficha del episodio (versionado)
      NOTAS.md                   ← decisiones de traducción y montaje (versionado)
      thumbnail.jpg              ← portada para el vídeo (versionado)
      transcripciones/
        original.en.md           ← transcripción original (versionado)
        traduccion.es.md         ← traducción al español (versionado)
      tts/                       ← 1 clip por intervención  ✗ NO versionado
      audio/                     ← episodio final .mp3/.wav ✗ NO versionado
      video/                     ← .mp4 para YouTube        ✗ NO versionado
plantillas/episodio/             ← esqueleto que copia nuevo-episodio.sh
scripts/                         ← automatización
docs/                            ← decisiones sobre el repo
GLOSARIO.md                      ← criterios de traducción y términos fijos
```

Regla de oro: **lo que es texto se versiona, lo que es media no.** El audio y
el vídeo son regenerables a partir de la traducción y el TTS; las
transcripciones no lo son, y son lo único que de verdad quieres tener con
historial, diffs y copia de seguridad.

## Flujo de trabajo

```bash
# 1. Crear el episodio
./scripts/nuevo-episodio.sh 2024 como-pensar-con-claridad "How to Think Clearly"

# 2. Pegar la transcripción original y traducirla
#    episodios/2024/como-pensar-con-claridad/transcripciones/original.en.md
#    episodios/2024/como-pensar-con-claridad/transcripciones/traduccion.es.md

# 3. Generar los clips de TTS en tts/ (0001-*.wav, 0002-*.wav, ...)
#    Un clip por intervención, numerado con ceros a la izquierda.

# 4. Unir los clips en el audio final
./scripts/unir-audios.sh episodios/2024/como-pensar-con-claridad

# 5. Montar el .mp4 con el thumbnail
./scripts/render-video.sh episodios/2024/como-pensar-con-claridad

# 6. Actualizar la ficha (estado, youtube_url) y regenerar el índice
python3 scripts/indice.py
git add -A && git commit -m "2024/como-pensar-con-claridad: traducción y montaje"
git push
```

### Convenciones

- **Slug**: minúsculas, números y guiones. Sin tildes ni espacios.
- **Intervenciones**: una por línea, con el hablante delante (`NAVAL: ...`).
  El original y la traducción deben tener el **mismo número de líneas**: así
  el clip `0007-*.wav` corresponde siempre a la intervención 7.
- **Estados** de `metadata.json`: `pendiente` → `traduciendo` → `revision` →
  `tts` → `montaje` → `publicado`.

## Scripts

| Script | Qué hace |
|---|---|
| `scripts/nuevo-episodio.sh` | Crea la carpeta de un episodio a partir de la plantilla. |
| `scripts/importar-local.sh` | Migra tu carpeta local existente al repo. Simula por defecto. |
| `scripts/unir-audios.sh` | Concatena los clips de `tts/` en un solo mp3, con pausas. |
| `scripts/render-video.sh` | Une audio + thumbnail en un mp4 listo para YouTube. |
| `scripts/indice.py` | Regenera `INDICE.md` desde los `metadata.json`. |

Requisitos: `bash`, `python3` y `ffmpeg` (solo para los dos scripts de media).

## Migrar tu carpeta local

```bash
./scripts/importar-local.sh ~/ruta/a/tu/carpeta            # simulación: no toca nada
./scripts/importar-local.sh ~/ruta/a/tu/carpeta --aplicar  # copia de verdad
```

Copia, nunca mueve: tu carpeta original se queda intacta. Revisa el reparto de
archivos que imprime la simulación antes de aplicarlo, y después rellena los
`metadata.json` y ejecuta `python3 scripts/indice.py`.

## Secretos

Las claves de API van en `.env` (ignorado por git). Parte de `.env.example`.

## Derechos

El contenido original es de sus autores; este repositorio guarda el trabajo de
traducción. Antes de publicar cada episodio, asegúrate de tener permiso o de
que el uso encaje con las condiciones de la fuente, y acredítala en
`metadata.json` (`fuente_url`) y en la descripción de YouTube.
