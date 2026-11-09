# Prompt: sesión local para el dataset de Matt Ridley

Se pega en una sesión de **Claude Code en local** (el portátil del autor, la misma máquina y el mismo
`~/naval-datos/` donde se hicieron los datasets de Naval, Brett, Deutsch y Nivi). Deja en Drive un dataset de
clips de Ridley para entrenar su LoRA de Qwen3-TTS en Colab, como se hizo con Brett (`docs/dataset.md`, parte 2b).

Por qué: en la fábrica Ridley va sin LoRA (clonación zero-shot, solo timbre). Toma su timbre de un clip, pero la
entonación y los giros son los de Qwen base, siempre iguales, y en episodios largos (070 y 071, ~70 min) cansa. Un
LoRA aprende su manera real de entonar.

## El prompt

```
Trabajo en spanishnav.al, el doblaje al español del podcast de Naval Ravikant. En esta sesión vamos a
construir, en local, el dataset de voz de Matt Ridley para fine-tunear su voz, con el mismo pipeline que ya
usamos para Naval, Brett, Deutsch y Nivi.

## 0. Antes de nada

1. Repo DreiSup/spanishnav.al-podcast, rama claude/quirky-dirac-x18c3n (no main). Haz pull.
2. Lee, en este orden: CLAUDE.md, docs/dataset.md (sobre todo «Etapas», «Parte 2» y «Parte 2b»),
   scripts/dataset/CONTRATO.md, scripts/dataset/dataset_brett.json y orquesta_parte2b.sh. La receta es
   la de Brett: cópiala, no la reinventes.
3. Comprueba que siguen en su sitio ~/naval-datos/venv, el remoto rclone "gdrive" y el token de
   Hugging Face de pyannote. Mira si ~/naval-datos/trabajo/nav074/ ya tiene asr.json, palabras.json,
   diar.json y hablantes.json (nav074 se procesó en la Fase 1a para sacar la referencia de Ridley) y si
   existe ~/naval-datos/emb/ridley.npy. Dime qué hay antes de lanzar nada.

## Reglas (las de siempre)

- Cero unidades de Colab: todo en local, en la GTX 1650. Una etapa pesada a la vez.
- Un paso cada vez, con mi confirmación. Las métricas filtran; la calidad la apruebo yo escuchando.
- Nada de audio ni de transcripts de terceros en git (el repo es público). Datos en ~/naval-datos/,
  a Drive con rclone copy (nunca sync) y después rclone check.
- Sin espacios, paréntesis ni "+" en las rutas.

## Fuentes

| id | Fuente | Ridley | Notas |
|---|---|---|---|
| nav074 | Naval: Matt Ridley, How Innovation Works, Part 1 (ya en fuentes_podcast.json) | ~13 min | Probablemente llamada remota |
| nav075 | Naval: Matt Ridley, How Innovation Works, Part 2 (https://nav.al/matt-ridley-2) | ~15 min | Añadir a fuentes_podcast.json. El MP3 de Libsyn sigue el patrón de nav074 (Naval-Ep70.mp3), probablemente Naval-Ep71.mp3: compruébalo con la página o el feed antes de descargar |
| eco001 | EconTalk, Matt Ridley on the Evolution of Everything (22-feb-2016, ~1h09) | ~30-35 min | Conversación con buen audio. Sin transcript oficial: etiquetas por embeddings (06 --asignar contra emb/ridley.npy), como tok221 |

Opcional, solo si me lo propones y lo apruebo: el audiolibro How Innovation Works leído por él (audio de
estudio, horas de material). Es material comprado: no se descarga ni se usa sin mi decisión expresa.

Los transcripts en inglés de nav074 y nav075 también están en el repo
(episodios/2020/070-matt-ridley/transcript.en.json y 071-matt-ridley-2/transcript.en.json), por si 05 los
necesita como oficial; para el texto de entrenamiento vale solo el re-ASR literal (08), como siempre.

## Pasos

1. Verifica las tres fuentes (URL, duración, cuánto habla Ridley, calidad) y dame la tabla. Apruebo.
2. scripts/dataset/dataset_ridley.json copiando dataset_brett.json:
   train 30-45 min = nav074 + eco001 (conversación); eval 3-4 min = nav075 con --muestra-min 4.
   Mismos umbrales que Brett (sim_min 0.6, asr_media_min 0.85, dnsmos_ovrl_min 3.0…). Si la llamada
   remota de nav074/nav075 no pasa DNSMOS 3.0, enséñame la distribución y decido.
3. 01 → 05 → 02, 03, 04 (diarizar --min 2 --max 2; en eco001 quizá 2-3) → 06 por fuente; para eco001,
   06 --asignar SPEAKER_XX=ridley (y el entrevistador =descartado) con los cosenos delante.
4. 08_clips.py ridley nav074 eco001 y 08_clips.py ridley nav075 --muestra-min 4.
5. 09_montar.py ridley → datasets/ridley/ y revision/ridley/escuchar.html: escucho 20 clips al azar y
   10 rechazados. Ajustamos umbrales si hace falta (sin volver a medir).
6. Cuando lo apruebe: rclone copy ~/naval-datos/datasets/ridley gdrive:fine_tunned_naval/datasets/ridley -P
   y rclone check sin diferencias.
7. Repo: dataset_ridley.json, la entrada nueva de fuentes_podcast.json, un orquesta_ridley.sh si lo
   usas, y una sección «Parte 2d: dataset de ridley» en docs/dataset.md con minutos de train/eval por
   fuente y lo que se descartó. Antes de cada commit:
       git ls-files | grep -E '\.(mp3|wav|mp4|aup3)$'    # no debe devolver nada
   Commit, git pull --no-rebase y push a claude/quirky-dirac-x18c3n.

Al terminar, dime los minutos finales de train y eval: con eso la sesión técnica (Colab) prepara el
español sintético, el filtro y el LoRA de Ridley.
```

## Después (sesión técnica, Colab)

Con `gdrive:fine_tunned_naval/datasets/ridley/` subido: añadir `ridley` como variante en
`piloto/cuadernos` 01 (español sintético), 03 (filtro) y 04 (LoRA), entrenar (~1-2 u), escucha a ciegas de los
pasos, poner el elegido en `fabrica/voces.json` y regenerar 070 y 071 (la fábrica rehace solo los clips de
Ridley). Total estimado: ~3-4 unidades.
