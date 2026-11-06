# Contexto para la sesión global (dirección del proyecto)

Traspaso de la **sesión técnica** (fábrica de voz, cuadernos de Colab, Drive) a la **sesión global**, que lleva la
visión de conjunto y escribe los SOP. Fecha: 2026-11-04. Rama de trabajo: `claude/quirky-dirac-x18c3n`.

Lo que sigue son **decisiones tomadas**: no se reabren sin el autor. Al final están las que faltan.

## 1. Dónde estamos, en una frase

**La fábrica de voz está en producción.** De un `transcript.es.json` del repo sale, en Colab (T4), el audio final de
un episodio en Drive, a unas **5 unidades de Colab por hora de audio**, sin pasar por Audacity salvo que el autor
oiga algo mal. El cuello de botella ya no es el audio: es **publicar** (vídeo, YouTube, web, RSS), que es lo que esta
sesión tiene que convertir en SOP.

## 2. Cómo está repartido el trabajo

| Sesión | Qué lleva | Qué documento mantiene |
|---|---|---|
| **Global (esta)** | Visión, prioridades, SOP, coordinación entre sesiones | Los SOP que escriba |
| Técnica | `fabrica/`, `piloto/`, `criba/`, cuadernos de Colab, organización de Drive | `docs/estado.md`, `docs/fabrica-de-voz.md`, `fabrica/README.md` |
| Traducción | Inglés → `transcript.es.json` | `docs/traduccion.md` (prompt: `docs/prompt-sesion-traduccion.md`) |
| Contenido | Web spanishnav.al, RSS, plataformas | `docs/fabrica-de-contenido.md`, `docs/rss.md`, `docs/youtube.md` |

Reglas comunes: todas suben a `claude/quirky-dirac-x18c3n` con `git pull --no-rebase` antes de cada push (merge,
nunca rebase ni force-push); nadie abre PRs sin que lo pida el autor. **GitHub guarda texto y punteros; Drive guarda
bytes** (CLAUDE.md): nunca un `.mp3`, `.wav`, `.mp4` o `.aup3` en git. El autor decide escuchando y prefiere un paso
cada vez, con su confirmación, y el mínimo gasto de Colab. Todo en español.

## 3. El principio que ordena el proyecto (decisión del autor, 4-nov)

- **Los datos son estables.** Una traducción, una vez revisada, es la fuente de verdad del episodio y no se toca
  salvo para corregirla.
- **La tecnología, la organización de Drive y los SOP evolucionan.** Están montados para poder cambiar sin
  rehacer el trabajo: hay un solo cuaderno de fábrica, que siempre descarga la última versión del repo, y el estado de
  cada episodio vive en su carpeta de Drive. Si un texto se corrige, la fábrica rehace solo esa intervención; si
  cambia una voz, solo los clips de esa voz; el master se puede rehacer sin GPU.

## 4. Decisiones tomadas

### Producción

| Decisión | Fecha |
|---|---|
| **Se rehacen todos los episodios con la fábrica, empezando por el 1.** Los 34 producidos a mano en 2019 no se publican; se usan sus traducciones, no su audio. La regla de los «heredados» está retirada (CLAUDE.md) | 4-nov |
| **Sin Audacity por defecto.** La fábrica entrega el master; el autor lo escucha y solo arregla lo que suene mal (`docs/sop-episodio.md`) | 4-nov |
| **Sin intro ni cierre** de momento. Si se añaden, se rehacen los masters sin GPU | 4-nov |
| **Un solo cuaderno de fábrica**, no uno por episodio: las copias se quedarían con código viejo | 4-nov |
| Vocabulario de **castellano de España** («coche», «ordenador»), tuteo en singular; sin vosotros, «vale», «chaval» | 2-nov |

### Voces (`fabrica/voces.json`, todas Qwen3-TTS 1.7B en modo solo timbre)

| Hablante | Modelo | Pausa entre frases | Elegido |
|---|---|---|---|
| Naval | LoRA `B/paso_0120`, **temperatura 0,7** (la r y la rr sonaban inglesas con el paso 158 a 0,9) | 0,12 s | 3-nov, escuchando |
| Naval en los episodios con Kapil | El mismo LoRA con la referencia de esa sesión | 0,12 s | 31-oct / 3-nov |
| Nivi | Qwen sin LoRA (su LoRA le devolvía acento) | 0,20 s | 2-nov |
| Brett | LoRA `brett/paso_0130`, conserva algo de acento australiano | 0,30 s | 2-nov |
| Deutsch | LoRA `deutsch/paso_0120`, conserva algo de acento británico | 0,20 s | 2-nov |
| Kapil, Vitalik, Ridley, Qureshi, Hodak, Rauch, Scholl | Qwen sin LoRA | 0,12 s | — |

Las pruebas a ciegas y sus notas están en `piloto/resultados/resumen.md`. **Brett, Deutsch, Kapil y los invitados
aún no han pasado por la fábrica**: falta una muestra (ver §7).

## 5. Cómo funciona la fábrica (lo que un SOP necesita saber)

Cuaderno: `fabrica/fabrica.ipynb` en Colab, GPU T4. Se le da una lista de episodios en la celda 2.

Por cada episodio deja en Drive, en `naval-podcast/transcripts/<año>/<NNN Título>/`:

| Fichero | Para qué |
|---|---|
| `audio/<NNN>-<slug>.mp3` | **El master**: lo que se publica. MP3 mono 44,1 kHz 128 kbps, -16 LUFS (pico -1,5 dB), 0,6 s entre intervenciones, título en español en las etiquetas |
| `informe_tts.md` | Minuto del master de cada intervención y frases **sospechosas** (Whisper no oyó el texto) |
| `indice_master.tsv` | Segundo del master en que empieza cada frase |
| `tts/`, `tts/frases/`, `registro_tts.jsonl` | Clips, frases sueltas y su registro: solo para arreglos |

Control de calidad (`docs/sop-episodio.md`): el autor escucha el master. Si algo falla, dice el minuto o la frase y
la sesión técnica le devuelve qué rehacer (`fabrica/localizar.py`). Se rehace **solo esa frase** en segundos de
GPU; o se arregla el clip en Audacity y se rehace el master sin GPU. Hasta ahora (035–045): **cero alucinaciones**.

Coste medido: unos 2–2,5 s de T4 por segundo de audio → **unas 5 unidades por hora de audio**.

## 6. Números

- Traducido y en la rama (4-nov): **100 episodios, unas 16,5 h de audio** (035–052 de 2019, todo 2020, 2021, 2022 y
  2023). Generados con la voz final: 035–040 (041–045, pendientes de relanzar).
- Falta traducir: **001–034**, los 4 diálogos con Kapil de 2019 (extras sin número), y **2024–2026** (135–161 y
  los extras de *The AI Industrial Revolution*). Lo lleva la sesión de traducción, en ese orden.
- Producir lo ya traducido: unas **80 unidades**. El catálogo entero, a ojo, unas 150.
- Estados de `metadata.es.json`: `revision` (traducido) → `tts` (generado) → `montaje` (escuchado y bueno) →
  `publicado`. Hoy nadie los mueve después de `revision`: **hay que decidir en un SOP quién y cuándo**.

## 7. Decisiones pendientes

1. **El 052, *How to Get Rich*** (247 min): es la recopilación de los episodios 1 a 50, con traducción propia.
   El autor propone producirlo entero y cortarlo en episodios. **Recomendación técnica: al revés.** Producir los
   episodios 1–50 (cada uno desde su propio transcript, que es la regla del proyecto) y **montar el 052 uniendo
   sus masters**, sin GPU y sin cortes manuales, con capítulos de YouTube gratis en cada unión. Mismo gasto de GPU;
   cortar exigiría que la traducción del 052 coincidiera palabra por palabra con la de cada episodio, y no coincide.
   **Decidido por el autor (6-nov): el 052 se genera entero desde su propia traducción**, como un episodio más.
   Los cortos dentro de largos (077, 105, 130), en cambio, se montan con los clips del largo.
2. **Muestra de las voces nuevas** antes de producir en serie: `MUESTRA = 3` con 068 (Kapil), 070 (Ridley), 132
   (Vitalik y Qureshi) y 134 (Brett y Deutsch). Menos de 1 unidad. Conviene cerrar las voces antes de producir en
   serie: cambiar una voz después rehace todos sus clips.
3. **Publicación** (lo que esta sesión tiene que escribir): vídeo para YouTube (`scripts/render-video.sh`, nunca
   ejecutado: audio + miniatura fija), título, descripción con atribución a nav.al, tags, miniatura, subida (la API
   sube en privado hasta que Google verifique la app: ver CLAUDE.md), web spanishnav.al y RSS (sesión de contenido).
4. **Reorganizar Drive** cuando el flujo esté estable: propuesta en `docs/organizacion-drive.md` (sin ejecutar).
   Además, `drive.json` tiene mal el id de 2019: la carpeta real es `naval-podcast/transcripts/2019`.

## 8. Qué leer, por orden

1. `CLAUDE.md` — reglas del repo.
2. Este documento.
3. `docs/sop-episodio.md` — el SOP que ya existe: traducción → fábrica → escucha → arreglos.
4. `docs/estado.md` — estado técnico al día.
5. `docs/fabrica-de-contenido.md`, `docs/rss.md`, `docs/youtube.md` — lo que hay pensado para publicar.
6. `fabrica/README.md`, `docs/fabrica-de-voz.md` — si hace falta el detalle técnico.
