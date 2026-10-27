# Prompt: sesión local para construir los datasets de fine-tuning

Este prompt se pega en una sesión de **Claude Code en local** (el portátil del autor). La
sesión descarga podcasts, los segmenta y deja un dataset de clips limpios por hablante,
listo para el fine-tuning. Es la fase 2 de `docs/fabrica-de-voz.md`.

Va en local por dos razones: Claude Code web no llega a YouTube ni a nav.al, y la regla del
proyecto es no gastar unidades de Colab en nada que no sea estrictamente necesario.

## El prompt

```
Trabajo en spanishnav.al, el doblaje al español del podcast de Naval Ravikant. En esta
sesión vamos a construir, en local, los datasets de audio para fine-tunear un modelo de
voz por cada hablante del podcast. Vas a descargar podcasts y entrevistas en inglés,
segmentarlos en clips de un solo hablante con su transcripción literal, filtrar los
malos y subir los buenos a Google Drive.

## 0. Antes de nada

1. El repo es DreiSup/spanishnav.al-podcast. Si no está clonado, clónalo; si lo está,
   haz pull. La documentación que necesitas está en la rama
   claude/quirky-dirac-x18c3n, no en main. Trabaja en esa rama.
2. Lee, en este orden: CLAUDE.md, docs/fabrica-de-voz.md y docs/hablantes.md. El
   segundo explica para qué sirven estos datos; el tercero dice quién habla en el
   podcast y de dónde sacar audio de cada uno.
3. Busca en mi disco el pipeline que hice para el TFC, que iba yt-dlp → WhisperX →
   pyannote → Demucs → alineado → clips. Mira en /home/ysst/Documentos/naval,
   sobre todo en reference_audios/. Si encuentras scripts, léelos y dime qué
   reaprovechas antes de escribir nada nuevo.
4. Comprueba el entorno y dime qué falta: GPU (tengo una GTX 1650 de 4 GB), ffmpeg,
   python, yt-dlp, rclone con un remoto llamado "gdrive", y un token de Hugging Face
   con los términos de los modelos de pyannote aceptados. No instales nada a nivel
   de sistema sin preguntarme.

## Reglas

- **Cero unidades de Colab.** Todo se ejecuta en local. Si algo es inviable en mi
  GPU, me lo dices con tiempos estimados y decido yo; no propongas Colab por tu cuenta.
- **Un paso cada vez y con mi confirmación explícita.** Antes de cada paso me dices
  qué vas a hacer y por qué. Cada decisión técnica tiene que poder explicarse.
- **Yo soy el human in the loop.** Las métricas filtran, pero la calidad la apruebo yo
  escuchando.
- **Nada de audio en git.** Ni .wav, ni .mp3, ni transcripciones de podcasts de
  terceros: el repo es público. En git solo entran los scripts, sus requirements con
  las versiones fijadas y la documentación. Los datos van en ~/naval-datos/, fuera
  del repo, y a Drive con rclone.
- **rclone copy, nunca sync.**
- **Sin espacios, paréntesis ni "+" en ninguna ruta que crees.** Un nombre como
  "wavs + txts" ya nos dio problemas.

## Qué es un buen clip

- Un solo hablante, sin solapes, sin risas ni música, sin sintonía ni anuncios.
- Entre 3 y 15 s. Se corta en una pausa de 250 ms o más, usando los tiempos por
  palabra, nunca a mitad de palabra, con 100–200 ms de margen. Lo ideal es que el clip
  coincida con frases completas.
- Transcripción LITERAL de lo que se oye, con muletillas y repeticiones, con
  puntuación y en inglés. No uses los transcripts oficiales de nav.al como texto de
  entrenamiento: están editados y no coinciden palabra por palabra con el audio.
- El master se guarda en WAV PCM de 16 bits, mono, a la frecuencia de la fuente, sin
  remuestrear. La conversión a la frecuencia de cada motor se hará al entrenar,
  porque el motor aún no está elegido.
- Normalización suave de sonoridad por clip, a unos -20 LUFS, sin compresión.
- Demucs NO se aplica por defecto: sus artefactos empeoran el fine-tuning. Solo en una
  fuente con música de fondo, y marcando los clips como "demucs": true.

## El pipeline, por fuente

1. **Descarga** con yt-dlp, del formato de mayor calidad disponible. Guarda la URL, el
   título, la duración y el bitrate.
2. **Transcripción** con WhisperX (large-v3 si cabe en int8 en mi GPU; si no, dime las
   alternativas) y alineado por palabra.
3. **Diarización** con pyannote. Descarta los tramos con solape.
4. **Identificar al hablante.** Compara el embedding de cada etiqueta de pyannote con mis
   referencias de esa persona (ECAPA o el embedding de pyannote) y aplica un umbral de
   similitud coseno. Si una etiqueta queda en zona dudosa, me preguntas. La primera
   referencia la saco yo a mano; si no la tengo, propón tú un tramo largo de monólogo y
   lo confirmo escuchándolo.
5. **Segmentación** según las reglas de arriba.
6. **Control de calidad por clip:**
   - similitud con la referencia del hablante;
   - confianza media y mínima de las palabras del ASR;
   - calidad estimada con DNSMOS o UTMOS, que van en CPU;
   - duración y caracteres.
   Los umbrales los propones tú con la distribución delante y los apruebo yo.
7. **Reparto:** unos 3–5 min por hablante, de fuentes distintas, van a "eval" y nunca
   se entrenan con ellos. El resto, a "train".

## Estructura de salida

~/naval-datos/datasets/<hablante>/
  wavs/<hablante>_<fuente>_<00001>.wav
  metadata.jsonl   una línea por clip: id, file, text, speaker, source_id, source_url,
                   start, end, dur, sr, sim, asr_conf, mos, demucs, tono, split
  metadata.csv     estilo LJSpeech (file|text|speaker), generado desde el jsonl
  fuentes.json     las fuentes usadas: url, título, fecha, duración y tono
                   (calmado, enérgico, conversacional, leído)
  informe.md       minutos por fuente y split, distribución de métricas,
                   descartes y por qué

Los nombres de hablante, en minúsculas: naval, nivi, brett, deutsch, kapil.

## Metas por hablante

| Hablante | Meta de clips aprobados | Nota |
|---|---|---|
| naval   | 60–70 min | Registro variado: monólogo calmado y entrevistas enérgicas |
| brett   | 45–60 min | ToKCast en solitario es la mejor fuente |
| deutsch | 45–60 min | The Deutsch Files más entrevistas |
| nivi    | todo lo que haya | Solo hay unos 60 min suyos en el podcast; busca más fuentes |
| kapil   | 30 min    | Opcional; me preguntas antes de empezar |

La variedad de tono importa tanto como los minutos. Si un hablante solo tiene un
registro, avísame.

## Orden de trabajo y puntos de control

1. **Plan y entorno** (sección 0). Me lo enseñas y espero tu OK.
2. **Lista de fuentes por hablante.** Parte de docs/hablantes.md. Esos enlaces no
   están verificados: compruébalos y dame la tabla con URL, duración, cuánto habla esa
   persona y su tono. Apruebo la lista antes de descargar nada.
3. **Piloto con una sola fuente de Naval** de principio a fin. Escucho 20 clips al azar,
   te digo qué falla y ajustamos los umbrales.
4. **Lotes por hablante**, empezando por Naval. Al terminar cada hablante, me das
   informe.md y 20 clips al azar para escuchar. Hasta que no lo apruebe no pasas al
   siguiente.
5. **Subida a Drive:**
   rclone copy ~/naval-datos/datasets/<hablante> "gdrive:fine_tunned_naval/datasets/<hablante>" -P
   Después verifica con "rclone check" contra el origen. Si la carpeta datasets/ no
   existe en Drive, me preguntas antes de crearla.
6. **Repo.** Los scripts van a scripts/dataset/, con su requirements.txt de versiones
   fijadas, y la documentación de uso a docs/dataset.md. Un commit por paso con
   sentido, a la rama claude/quirky-dirac-x18c3n, nunca a main. Antes de cada commit:
       git ls-files | grep -E '\.(mp3|wav|mp4|aup3)$'    # no debe devolver nada

## Extra, si sale barato

Mientras proceses las fuentes del propio podcast de Naval, propón candidatos para mis
clips de referencia de la fase 1: 3 tramos de 6, 12 y 25 s de Naval, de Nivi y de
Brett, y 2 o 3 de Naval en el episodio con Kapil Gupta. Las reglas están en
docs/fabrica-de-voz.md, sección "Fase 1a". Los escucho y elijo yo.

Empieza por el punto 0 y no avances sin mi confirmación.
```

## Por qué está escrito así

- **Transcripción por ASR y no los transcripts de nav.al.** El TTS aprende a alinear texto
  con sonido; si el texto está limpio de muletillas y el audio las tiene, aprende mal. Los
  transcripts oficiales están editados.
- **Sin Demucs por defecto.** La separación de voz deja artefactos que el modelo aprende
  como parte del timbre. Solo compensa si hay música de fondo.
- **Master sin remuestrear.** El motor no está elegido y cada uno quiere una frecuencia
  (24 kHz, 44,1 kHz, 48 kHz). Remuestrear se hace en el momento de entrenar; perder calidad
  en el master es irreversible.
- **Split de eval por fuente.** Sirve para medir el olvido del español y elegir checkpoint
  sin hacer trampa con clips que el modelo ya ha visto.
- **Similitud contra la referencia.** pyannote diariza bien pero no sabe quién es quién;
  la referencia evita meter al entrevistador en el dataset de Naval.
