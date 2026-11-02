# Pipeline local de clips de voz (`scripts/dataset/`)

Cómo instalar, lanzar y relanzar el pipeline que saca clips de referencia por hablante del
audio original del podcast. Es la Fase 1a de `docs/fabrica-de-voz.md`; el prompt de la sesión
local está en `docs/prompt-dataset-local.md`. Formatos de cada fichero y umbrales:
`scripts/dataset/CONTRATO.md` (si un script y el contrato discrepan, manda el contrato).

## Para qué sirve y dónde quedan los datos

Descarga las 7 fuentes de `fuentes_podcast.json`, las transcribe, alinea palabra a palabra,
diariza, decide quién habla en cada tramo y propone clips candidatos de 6, 12 y 25 s por
hablante. El usuario escucha y elige.

- **Todo vive en `~/naval-datos/`**, fuera del repo. **Nunca va a git**: ni audio, ni
  transcripts de terceros, ni centroides. En git solo scripts, `requirements.txt` y docs.
- **Drive: `rclone copy`, nunca `sync`**, y después `rclone check` para verificar:

```bash
rclone copy ~/naval-datos/speaker_refs/naval gdrive:fine_tunned_naval/speaker_refs/naval -P
rclone check ~/naval-datos/speaker_refs/naval gdrive:fine_tunned_naval/speaker_refs/naval
```

| Ruta bajo `~/naval-datos` | Contenido |
|---|---|
| `venv/` | Python 3.12 con las dependencias |
| `fuentes/<id>/`, `trabajo/<id>/` | audio original, `orig.wav` (44,1 kHz), `audio16k.wav`, `asr.json`, `palabras.json`, `diar.json`, `hablantes.json` |
| `oficiales/` | Google Docs exportados y transcripts de nav.al (solo comprobación cruzada) |
| `emb/` | centroides ECAPA por hablante |
| `speaker_refs/` | candidatos, `candidatos.json`, `refs.json`, `escuchar.html` |
| `logs/recursos.log` | salida de `vigilante.sh` |
| `requirements.lock.txt` | `pip freeze` del venv que funciona |

## Instalación

1. **venv con Python 3.12**: `python3.12 -m venv ~/naval-datos/venv`, y
   `pip install -r scripts/dataset/requirements.txt --extra-index-url https://download.pytorch.org/whl/cu128`
   (torch 2.8.0 con CUDA 12.8).
2. **Dos arreglos que ya están en `requirements.txt` / `common.py`**:
   - `av==15.1.0`: con av 19 faster-whisper falla con `metadata_errors`.
   - `LD_LIBRARY_PATH` debe incluir `site-packages/nvidia/cublas/lib` y `.../cudnn/lib` para
     ctranslate2. `common.asegurar_entorno_cuda()` lo hace solo (reejecuta el script con el
     entorno corregido); no hay que exportar nada a mano.
3. **Token de Hugging Face** (`common.token_hf()`), con los términos aceptados en la web de
   cada modelo: `pyannote/segmentation-3.0`, `pyannote/speaker-diarization-3.1` y
   `pyannote/speaker-diarization-community-1`. Sin los tres, la etapa 04 falla al descargar.
4. **rclone** en `~/.local/bin` con el remoto `gdrive` (ver `docs/almacenamiento.md`).
   Aviso: el `client_id` compartido de rclone caduca en 2026; si Drive empieza a dar errores
   de autorización, crear un `client_id` propio en Google Cloud y repetir `rclone config`.
5. También hacen falta `ffmpeg`/`ffprobe` y `yt-dlp` (este último en el venv).

## Etapas

Máquina de referencia: GTX 1650 de 4 GB compartida con el escritorio y ~6 GB de RAM libre.
Una sola etapa pesada a la vez (candado `gpu.lock`).

| # | Script | Qué hace | Entrada | Salida | GPU | Tiempo medido |
|---|---|---|---|---|---|---|
| 01 | `01_descargar.py` | Descarga el MP3 (yt-dlp) y decodifica una vez | `fuentes_podcast.json` | `fuentes/<id>/`, `trabajo/<id>/orig.wav`, `audio16k.wav` | no | depende de la red |
| 02 | `02_asr.py` | ASR literal faster-whisper large-v3 int8, por lotes | `audio16k.wav` | `asr.json` | sí | ~4,5-6x tiempo real con lote 2 |
| 03 | `03_alinear.py` | Alineado WhisperX: tiempos finos por palabra | `asr.json`, `audio16k.wav` | `palabras.json` | sí | ~45x tiempo real |
| 04 | `04_diarizar.py` | Diarización pyannote community-1 | `audio16k.wav` | `diar.json` | sí | ~4-5 min por hora de audio (nav056, 3,6 h, por trozos) |
| 05 | `05_oficiales.py` | Parsea los transcripts de nav.al por hablante | `oficiales/docs/*.txt` | `oficiales/<id>.json` | no | segundos |
| 06 | `06_hablantes.py` | Etiqueta por palabra, ECAPA, etiqueta a hablante, tramos | etapas 03-05 | `hablantes.json`, `emb/` | no (ECAPA en CPU) | ~4-10 min por fuente |
| 07 | `07_candidatos_ref.py` | Ventanas limpias, métricas, corte y re-ASR del clip | `hablantes.json`, `orig.wav`, `emb/` | `speaker_refs/` | sí (solo el re-ASR) | ~10 min para 5 hablantes |
| 08 | `08_clips.py` | Parte 2: corta los tramos en clips de 3-15 s por pausas >= 0,25 s (programación dinámica) y mide cada clip: sim, asr_conf, DNSMOS, LUFS, pico, re-ASR literal | `hablantes.json`, `orig.wav`, `emb/` | `trabajo/<id>/clips_<h>.json` (sin audio) | sí (re-ASR) | |
| 09 | `09_montar.py` | Parte 2: aplica umbrales, reparte train/eval, ganancia fija a -20 LUFS, escribe WAV y metadatos | `clips_<h>.json`, `dataset_<h>.json` | `datasets/<h>/`, `revision/<h>/escuchar.html` | no | |

El orquestador no lanza 01 ni 05: hay que ejecutarlas antes con `etapa.sh` (`./etapa.sh 01_descargar.py`,
`./etapa.sh 05_oficiales.py`). La 05 no usa torch.

## Cómo lanzarlo

**Normal**: `orquesta_refs.sh` encadena todo en serie. Es reanudable: cada etapa se salta si su
salida ya existe, así que tras un corte basta relanzarlo.

```bash
cd ~/Documentos/spanishnav.al-podcast/scripts/dataset
systemd-inhibit --what=sleep:idle --why="pipeline voz" \
  ./orquesta_refs.sh >> ~/naval-datos/logs/orquesta.log 2>&1
```

- **Bloque 1** (nav109, nav072, nav056): naval, nivi, brett, naval_kapil, kapil.
- **Bloque 2** (nav139, nav135, nav074, nav167): deutsch, vitalik, ridley, hodak, rauch,
  scholl, qureshi; y al final `06_hablantes.py --global` (recalcula centroides con todas las
  fuentes).
- Si una etapa se abandona, el orquestador para y deja `PARADA: falló ...` en el log.

**Una etapa suelta**: `./etapa.sh 04_diarizar.py nav056 --trozos 3600`. Aplica un tope de
cgroup de 5,5 GB (`MEM_MAX`, más `SWAP_MAX=1G`), de modo que si se desboca el kernel mata solo
esa etapa y no el escritorio (rc 137 = memoria). Reintenta 3 veces (`REINTENTOS`) con 20 s de
pausa. `--forzar` rehace una etapa cuya salida ya existe.

**Desarrollo**: `./prueba.sh script.py args`. Sin GPU, con candado propio y tope de 2,5 GB.
Es obligatorio para cualquier `python` que importe torch, whisperx, pyannote o speechbrain
mientras corre una etapa pesada. Nunca procesar un episodio entero en una prueba.

**Vigilancia**: `./vigilante.sh &` anota cada 15 s RAM libre, swap, VRAM y disco en
`~/naval-datos/logs/recursos.log`. Escribe `ALERTA` si la RAM baja de 2000 MB o el disco de
15 GB, y con RAM libre < 1200 MB mata el proceso pesado de las etapas 02-09.

**Bloquear la suspensión**: lanzar siempre con `systemd-inhibit` (arriba). Una suspensión del
equipo dejó CUDA inservible a mitad de un ASR; se recupera reiniciando el proceso (o el
equipo), no reanudando.

## Decisiones y por qué

Aprendido en la ejecución real del 2026-10-28.

| Decisión | Motivo |
|---|---|
| ASR **sin prompt** de muletillas | En la prueba hizo que Whisper se saltara 21 s de habla; el podcast ya viene editado sin muletillas. `--con-prompt` lo reactiva. |
| ASR **por trozos de ~10 min** cortados en el punto más silencioso, con punto de control en `trabajo/<id>/asr_trozos/` | Un fallo o corte solo repite su trozo y no se parten palabras. |
| **Lote 2** | Con 8, y a veces 4, la GTX 1650 se queda sin VRAM; con 2 se pierde ~10 % de velocidad. |
| Tras un OOM **recargar el modelo** | Si no, todo falla con `invalid device ordinal`. |
| Texto del clip = **ASR literal** | Los transcripts de nav.al están editados y no coinciden palabra por palabra. Solo sirven como **comprobación cruzada**. |
| Tramo con desacuerdo embeddings/transcript: **se descarta** | Regla del usuario: si no coinciden, fuera (>20 % de las palabras con hablante oficial). |
| `naval_kapil` sale **solo de nav072**; el centroide principal de `naval` **lo excluye** | La prueba de tono compara a Naval en dos contextos; mezclarlos contaminaría el centroide. |
| **Sin Demucs** por defecto | Sus artefactos empeoran el fine-tuning (decisión del autor). Solo para fuentes con música de fondo, marcando los clips con `"demucs": true`. En las referencias, además, un clip con ruido se descarta, no se limpia. |
| Referencias **sin normalizar ni limpiar** | Corte exacto de `orig.wav`, PCM16 mono a la sr original; LUFS solo se anota. |
| En 08, un borde de tramo solo es punto de corte si la palabra vecina de fuera tiene tiempo propio (`ts_ok`) | Con tiempo interpolado el hueco medido es ficticio y el clip podía arrastrar una palabra (revisión del 2026-10-30: 6 clips de los datasets subidos, todos con la palabra del propio hablante; ninguno con otra voz). |
| `naval_kapil.npy` ponderado por segundos | nav072 (~18 min, con transcript) debe mandar sobre los segundos de las fuentes de 2019 a 16 kHz. Los datasets naval y naval_kapil ya aprobados se montaron con el centroide anterior. |
| `09_montar.py --fuentes` exige `--salida` | Montar un subconjunto con la salida por defecto pisaba el dataset aprobado. |
| Diarización de nav056 por trozos de 60 min | El clustering es O(n²) y con el tope de 5,5 GB el kernel mataba el proceso. |

## Resultados de la Fase 1a (2026-10-28)

- 7 fuentes procesadas, **0 etiquetas dudosas**; acuerdo con el transcript oficial del 90 al
  100 % en todas las etiquetas.
- **101 candidatos para 12 juegos**: naval, nivi, brett, naval_kapil, kapil, deutsch, vitalik,
  ridley, hodak, rauch, scholl, qureshi. Todos WAV PCM16 mono 44,1 kHz, verificados sin otra
  voz ni solape dentro del clip.
- Subidos a `gdrive:fine_tunned_naval/speaker_refs/<hablante>/candidatos/`.
- **Elige el usuario** escuchando (`~/naval-datos/speaker_refs/escuchar.html`, local, no
  publicar). Los elegidos pasan a `<h>_ref01.wav|.txt`, `<h>_ref02...`, `<h>_ref03...` en
  `speaker_refs/<h>/`. `refs.json` guarda fuente y tiempos de todos los candidatos para que la
  parte 2 no los meta nunca en el split `eval`.

## Parte 2: dataset de fine-tuning de Naval (2026-10-29)

Piloto LoRA con Qwen3-TTS y OmniVoice; los demás hablantes esperan al motor ganador.
Fuentes, split y registro en `scripts/dataset/dataset_naval.json`: train = nav056, nav167,
nav072, nav109, nav074; eval = nav139, nav135 y nav081 (Happiness, añadido para tener
monólogo en eval). Ninguna referencia elegida sale de una fuente eval y 09 lo comprueba igual.

```bash
./etapa.sh 08_clips.py naval nav056 nav167 ...   # mide (GPU, re-ASR)
./prueba.sh 09_montar.py naval                    # monta; --umbral sim_min=0.65 para probar
```

Resultado (aprobado y subido a `gdrive:fine_tunned_naval/datasets/naval/`): train 69,9 min
(35 conversación + 35 monólogo; nav072 fuera), eval 4,2 min de nav139, nav135 y nav081.

**naval_kapil** (`dataset_naval_kapil.json`): Naval solo con Kapil; nav072 entero en train y
nav001 (On Meditation, 2019) entero en eval. Las 4 fuentes de 2019 (nav001-nav004) no tienen
transcript: `05_oficiales.py` escribe un oficial vacío (`sin_transcript`) y las etiquetas se
asignaron por embeddings (`06_hablantes.py <id> --asignar SPEAKER_0X=naval ...`, coseno contra
`emb/naval_kapil.npy` y `emb/kapil.npy`). Vienen a 16 kHz: se dejan así, `sr` por clip en el
manifiesto y minutos por frecuencia en el informe. Los clips de Kapil (`dataset_kapil.json`) se
montan en `datasets/kapil/` solo en local.

Los umbrales se ajustan en `dataset_<h>.json` sin volver a medir. `revision/naval/escuchar.html`
trae 20 clips al azar y 10 rechazados para calibrar; queda fuera del dataset y no se sube.

## Parte 2b: datasets de deutsch, brett y nivi (2026-10-30)

Fuentes nuevas procesadas con `orquesta_parte2b.sh`; las que no tienen transcript oficial (tok221,
niv001-niv003, nav163) se etiquetan solo por embeddings (`06_hablantes.py <id> --asignar ...`,
cosenos de 0,74 a 0,93 contra el centroide del hablante) y se miden con `orquesta_parte2c.sh`.

| Dataset | train | eval | Notas |
|---|---|---|---|
| deutsch | 60,0 min (nav139 + nav140, recortado al tope) | 4,1 min (nav141) | todo conversación |
| brett | 46,8 min (nav109 35,6 conversación + tok221 11,2 monólogo) | 4,1 min (nav139) | tok221 pierde 13 min por DNSMOS < 3,0 y pico a 0 dBFS (MP3 masterizado a fondo de escala); se dejó así |
| nivi | 62,7 min (40,7 monólogo de Twitter Spaces + 22,0 conversación) | 5,0 min (nav163 + nav055) | nav055 pasó a eval porque nav163 solo daba 2,7 min |

Los tres están aprobados por escucha y subidos a `gdrive:fine_tunned_naval/datasets/<h>/` con
`rclone copy`; `rclone check` sin diferencias.
