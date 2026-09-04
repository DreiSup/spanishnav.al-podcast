# Contexto del proyecto — traducción del podcast de Naval

> Documento de traspaso. Recoge el estado real verificado en local, los cambios ya
> aplicados y las decisiones pendientes.
>
> Última actualización: **2026-09-03**
> Ubicación: raíz del repo (`CONTEXTO.md`). Origen previo:
> `/home/ysst/Documentos/naval/CONTEXTO.md`.

---

## 1. Estado actual

### 1.1 Repositorio

- Remoto: `https://github.com/DreiSup/spanishnav.al-podcast`
- Rama: `claude/naval-podcasts-translation-web-b7sy21`
- Un único commit: "Estructura inicial del repo de trabajo de traducción". Sin PR abierto.
- **El repo NO está clonado en local.** `/home/ysst/Documentos/naval` no es un repositorio
  git; es la carpeta de trabajo con el material real. Decidir dónde se clona (dentro de
  esta carpeta o al lado) sigue pendiente.

### 1.2 Herramientas locales (verificado)

| Herramienta | Estado |
|---|---|
| ffmpeg / ffprobe | ✅ 6.1.1-3ubuntu5 |
| python3 | ✅ 3.12.3 |
| git | ✅ 2.43.0 |
| bash | ✅ 5.2.21 |
| `gh` (GitHub CLI) | ❌ no instalado |
| `git-lfs` | ❌ no instalado |
| rclone | ❌ no instalado (necesario para el puente con Drive) |

### 1.3 Estructura local real

```
/home/ysst/Documentos/naval/
├── audio_completo_naval.wav
├── CEIABD presentación/              23 M   — fuera de ámbito
├── good_products_are_hard_to_vary/   13 M   — fuera de ámbito
├── img/                             1,4 M   — banners, logo_es.png, feynman_naval_4k.jpg
├── reference_audios/                8,3 G   — referencias de voz para XTTS. NO REGENERABLE
│   └── curate people, googledrive, modern_wisdom_podcast, naval, nivi,
│       XTTS_fine_tunning_reference
└── spanishpodcast/                  2,6 G
    ├── description.txt                     — plantilla global de descripción de YouTube
    ├── Naval_-_October_2025_-_Curate_People_-_Edited.aup3
    ├── 999 template/                       — solo contiene naval4k.png
    └── 2019/                               — 52 carpetas de episodio
```

---

## 2. Hallazgos sobre los datos reales

Varios contradicen las suposiciones con las que se creó el repo en la sesión web.

### 2.1 Episodios

- Un solo año: **2019**, con **52 carpetas**.
- Nombre de carpeta: `NN Título original en inglés` (p. ej. `26 Judgment Is the Decisive Skill`).
  Llevan número de episodio delante, espacios, tildes y comillas tipográficas (` ’ “ ” `).
- El **número de episodio** es información que el `metadata.json` del repo no contempla.
  Hace falta un campo `numero`.

### 2.2 Transcripciones

**41 ficheros de texto para 52 episodios → 11 episodios sin ninguna transcripción.**

Formato dominante: **JSON, no markdown**.

```json
{
  "fecha": "Apr 29 2019",
  "titulo": "El juicio es la habilidad decisiva",
  "contenido": [
    { "speaker": "Nivi",  "frases": ["...", "..."] },
    { "speaker": "Naval", "frases": ["...", "..."] }
  ],
  "titulos_seccion": ["...", "..."]
}
```

Reparto real de los 41 ficheros:

| Estado | Nº | Detalle |
|---|---|---|
| JSON válido | 25 | esquema de arriba |
| Lista JSON suelta | 1 | ep 20, empieza por `[` sin objeto envolvente |
| JSON roto / truncado | 1 | ep 42 |
| Texto plano | 14 | formato anterior: `Nivi:` + líneas entrecomilladas |

**Solo hay español.** No existe ningún transcript original en inglés en todo el disco;
incluso el campo `titulo` de los JSON viene ya traducido.

Nombres de fichero inconsistentes: `transcript.txt`, `transcript_es.txt`,
`13_transcript_Es.txt`, `14transcript_es.txt`, `15transcript.txt`.

### 2.3 Audio

- **34 episodios tienen audio; 18 no** (eps 35–52 están vacíos de media).
- Audio final del episodio, nombres variables: `fullaudio.mp3` (eps 03–17),
  `fullaudio.wav` (eps 18–34), `completo.mp3` (ep 01), `02completo.mp3` (ep 02).
- `Naval-Ep1.mp3` y `Naval-Ep2.mp3` son el **original en inglés** — confirmado por duración:
  ep 01 `Naval-Ep1.mp3` 366 s ≡ `original_english.mp4` 366 s, frente a `completo.mp3` 462 s.
- Los clips de TTS eran un clip **por bloque de hablante**, no por frase, y con numeración
  irregular: `01nivi.wav`, `02naval.wav`, `naval.wav`, `_naval2.wav`, `naval02.wav`,
  `ep01_naval (1).wav`, `CTOnaval.wav`, y un `01nivi` **sin extensión**.
- Miniaturas: `naval.jpg`, `naval4k.png`, `naval_podcast_es_4k.png`.
- Vídeo: `output.mp4`, `español.mp4`.
- Proyectos de Audacity `.aup3` en 6 episodios (binarios y pesados → van a Drive, no a git).

---

## 3. Cambios ya aplicados — 2026-09-03

Reorganización del audio dentro de `spanishpodcast/2019/`:

- Creada carpeta `audio/` en **33 carpetas** de episodio.
- Movidos **116 ficheros** de clips sueltos a `<episodio>/audio/`.
- El audio final de cada episodio **permanece en la raíz** de su carpeta.
- Ep 02 no recibió carpeta `audio/`: no tenía clips.
- Verificado de forma independiente: 33 carpetas, 116 ficheros, 32 `fullaudio.*` en raíz.
- Fuera de ámbito, sin tocar: `reference_audios` (8,3 G), `img`, `CEIABD presentación`.

Registros:
- `scratchpad/movimientos.log` — 116 líneas `OK<TAB>origen<TAB>destino`
- `scratchpad/deshacer.sh` — revierte los 116 movimientos

> El scratchpad es efímero (`/tmp/claude-1000/.../scratchpad`). Si el `deshacer.sh` importa,
> copiarlo a un sitio permanente.

### Ficheros deliberadamente dejados en raíz, pendientes de decisión

| Fichero | Por qué |
|---|---|
| `25/ep01_naval.wav` (346 s), `25/ep01_naval (1).wav` (355 s) | Renders casi completos frente a `fullaudio.wav` 375 s. No son clips. |
| `26/ep01_naval.wav` (399,479083 s) | Duración **idéntica** a su `fullaudio.wav`. Duplicado exacto. |
| `21/descarga` | WAV sin extensión, 186 s, sin identificar. |

Riesgo si se mueven a `audio/`: cualquier script que concatene esa carpeta generará un
episodio doblado. Decidir entre borrarlos o llevarlos a un `descartes/`.

---

## 4. Flujo objetivo

Reparto: **GitHub = texto · Google Drive = bytes**.

### Va a GitHub
- Transcripciones originales en inglés
- Transcripciones traducidas al español
- Notebooks de Google Colab
- Plantilla de YouTube: título y descripción (la miniatura ya existe)
- `metadata.json`, glosario, scripts

### Va a Drive
- Clips de TTS
- Audio final montado y limpio
- Proyectos `.aup3` de Audacity
- Vídeo `.mp4`

### Pipeline

| # | Paso | Dónde | Estado |
|---|---|---|---|
| 1 | Coger el transcript original en inglés | GitHub | por definir |
| 2 | Traducir al español | web | por definir |
| 3 | Generar los clips TTS y guardarlos en Drive | web / Colab (GPU) | por definir |
| 4 | Juntar clips, quitar ruido y alucinaciones | **local, Audacity — manual** | manual por diseño |
| 5 | Subir el audio limpio a Drive | local | por definir |
| 6 | Generar el `.mp4` (audio + miniatura) | automatizable | script existe, sin probar |
| 7 | Subir a YouTube con título, descripción y miniatura | automatizable | por definir |

El paso 4 es irreducible: requiere Audacity y criterio humano.

---

## 5. Decisiones y recomendaciones

### 5.1 El formato canónico debe ser JSON, no markdown

El repo se creó asumiendo `original.en.md` + `traduccion.es.md`, una intervención por línea
y el mismo número de líneas en ambos. **Esa suposición es falsa** frente a los datos reales,
y además el JSON existente es *mejor* para este flujo:

- `frases` es exactamente la unidad de generación TTS.
- `speaker` es exactamente lo que selecciona la voz de referencia XTTS.
- Añadiendo un **id estable por frase**, el clip se nombra desde el id y el script de unión
  reconstruye el orden **leyendo el JSON**, no ordenando nombres alfabéticamente.

Esto último elimina una clase entera de errores: la numeración irregular observada
(`01nivi` sin extensión, `_naval2.wav`, `naval02.wav`) deja de importar.

Coste: normalizar los 16 ficheros no conformes (14 texto plano + ep 20 + ep 42).

### 5.2 Los originales en inglés no existen

Hay que traerlos de nav.al y **alinearlos frase a frase** con la traducción ya existente.
Es trabajo episodio a episodio, no un script. Para episodios nuevos no hay problema: el
inglés entra primero y el español sale alineado de él.

### 5.3 El repo se simplifica

Como el audio nunca entra en git y vive en Drive:
- Se puede eliminar toda la preparación de **Git LFS** en `.gitattributes`.
- No hacen falta GitHub Releases como adjuntos.
- No hacen falta carpetas `tts/`, `audio/`, `video/` vacías en el árbol del repo.
- `docs/almacenamiento.md` se reduce a "el media vive en Drive".

### 5.4 Trampa de YouTube

Mientras la app OAuth no pase la verificación de Google, **los vídeos que suba la API
quedan forzados a `private` y no se pueden hacer públicos por API**. Verificar antes de
invertir esfuerzo ahí.

Alternativa que funciona sin verificación: la API sube en privado ya con título,
descripción y miniatura puestos, y la publicación se hace a mano en YouTube Studio.

Cuota: 1600 unidades por subida sobre 10.000/día ≈ 6 vídeos/día. No es limitante.

`spanishpodcast/description.txt` ya es la plantilla global (24 líneas con huecos `(yt link)`).
Lo natural: dejarla en el repo como plantilla y que los campos por episodio salgan del
`metadata.json`.

### 5.5 Puente local ↔ Drive

En Linux no hay cliente oficial de Google Drive. La opción práctica es **rclone**.

### 5.6 Audacity rompe la regeneración

A partir del paso 4 el audio final ya no es derivable de la traducción. El `.aup3` pasa a
ser un artefacto que hay que conservar en Drive, no un fichero desechable. Conviene además
anotar en las notas del episodio que el audio lleva edición manual.

---

## 6. Puntos abiertos

1. **¿"Desde web" significa Colab para el TTS y Claude Code web para traducir?**
   Es la hipótesis de trabajo (XTTS necesita GPU), pero cambia la arquitectura si no.
   Si el notebook además tiene que commitear, necesita un PAT en Colab Secrets; si solo
   lee, basta con clonar. **Sin responder.**
2. **¿Los originales en inglés se quieren para los 41 episodios ya traducidos, o solo de
   aquí en adelante?** Retroactivo = alinear uno a uno. **Sin responder.**
3. Dónde se clona el repo en local.
4. Qué hacer con los ficheros del apartado 3 (eps 21, 25, 26).
5. Los 11 episodios sin transcripción y los 18 sin audio: ¿entran en el repo como
   pendientes o se ignoran?
6. Cómo se nombra y numera el episodio en `metadata.json` (falta campo `numero`).
7. `GLOSARIO.md` lleva términos y criterios propuestos por la sesión web, no revisados
   por el autor: *leverage*, *specific knowledge*, *judgment*, *wealth* vs *money*.
8. **Derechos**: el contenido original es de sus autores. Verificar permiso o condiciones
   de la fuente antes de publicar, y acreditarla en `metadata.json` (`fuente_url`) y en la
   descripción de YouTube.

---

## 7. Convenciones del repo que quedan invalidadas

| Convención original | Realidad |
|---|---|
| `original.en.md` + `traduccion.es.md` en markdown | Los transcripts son JSON y solo en español |
| Una intervención por línea, mismo nº de líneas en ambos idiomas | La unidad real es *frase* dentro de un bloque de *speaker* |
| Clips en `tts/`, numerados `0001-naval.wav` | Los clips estaban sueltos, uno por bloque de hablante, con numeración irregular |
| `importar-local.sh`: "subcarpeta con >1 audio → `tts/`" | No disparaba: los clips no estaban en subcarpeta. Tras la reorganización del apartado 3, ahora sí |
| Git LFS preparado en `.gitattributes` | Innecesario: el audio va a Drive |
| Origen esperado `<origen>/<año>/<episodio>/` | Correcto: `spanishpodcast/2019/<episodio>/` |

### Scripts del repo y su estado

| Script | Estado |
|---|---|
| `nuevo-episodio.sh` | Probado. Necesita campo `numero` |
| `importar-local.sh` | Probado contra carpeta sintética. Heurística a reajustar |
| `unir-audios.sh` | **Nunca ejecutado.** Debería leer el orden del JSON, no ordenar por nombre |
| `render-video.sh` | **Nunca ejecutado.** ffmpeg ya está disponible en local |
| `indice.py` | Probado |
