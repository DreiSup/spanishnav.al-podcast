# Contrato del pipeline de datasets de voz

Reglas y formatos que comparten todas las etapas de `scripts/dataset/`. Si un script y este
documento discrepan, manda este documento.

## Entorno

- Python del venv: `~/naval-datos/venv/bin/python` (3.12). Versiones en
  `~/naval-datos/requirements.lock.txt`: whisperx 3.8.6, faster-whisper 1.2.1, ctranslate2
  4.8.4, torch 2.8.0+cu128, pyannote.audio 4.0.7, speechbrain 1.1.2, pyloudnorm 0.2.0,
  soundfile, librosa, av==15.1.0 (fijado: con av 19 faster-whisper no abre audio).
- Todo script importa `common.py` (rutas, `escribir_json` atómico, `log`,
  `comprobar_recursos`, `asegurar_entorno_cuda`, `candado_gpu`, `token_hf`, `fuente`).
- Un script que use GPU llama a `asegurar_entorno_cuda()` al principio de `main()` y hace
  todo el trabajo de GPU dentro de `with candado_gpu():`. Libera la VRAM entre modelos
  (`del`, `gc.collect()`, `torch.cuda.empty_cache()`).
- GTX 1650 de 4 GB compartida con el escritorio; unos 6 GB de RAM libre. Una etapa pesada
  cada vez. Las etapas se lanzan con `etapa.sh` (tope de cgroup de 5,5 GB).
- **Pruebas de desarrollo**: solo con `./prueba.sh script.py args` (sin GPU, candado propio,
  tope de 2,5 GB). Nunca ejecutar a mano `python` con torch/whisperx/pyannote/speechbrain
  fuera de `prueba.sh`. Nunca procesar un episodio entero en una prueba.
- Datos de prueba: `~/naval-datos/pruebas/nav109_3min.wav` (16 kHz, minuto 10 a 13 de
  nav109, Naval y Brett Hall) y su ASR `~/naval-datos/pruebas/asr_sinprompt_b8.json`
  (formato `asr.json`, tiempos relativos al fragmento). Fixtures nuevos, en
  `~/naval-datos/pruebas/`.
- Cada etapa se salta si su salida ya existe (salvo `--forzar`) y escribe con
  `escribir_json`. Así un corte de sesión se reanuda desde los ficheros.
- Nada de audio ni de transcripts de terceros en el repo. Rutas sin espacios, paréntesis ni "+".

## Rutas y ficheros (bajo `~/naval-datos`)

| Fichero | Lo escribe | Contenido |
|---|---|---|
| `fuentes/<id>/fuente.json` | 01 | id, orden, titulo, url_episodio, url_audio, fecha, hablantes, codec, sr, canales, bitrate, duracion_s |
| `trabajo/<id>/orig.wav` | 01 | PCM16 mono a la sr de la fuente (44100). **Los cortes finales salen de aquí** |
| `trabajo/<id>/audio16k.wav` | 01 | 16 kHz mono derivado de orig.wav: misma línea de tiempo |
| `trabajo/<id>/asr.json` | 02 | ver abajo |
| `trabajo/<id>/palabras.json` | 03 | ver abajo |
| `trabajo/<id>/diar.json` | 04 | ver abajo |
| `oficiales/<id>.json` | 05 | ver abajo |
| `trabajo/<id>/hablantes.json` | 06 | ver abajo |
| `emb/<hablante>.npy` + `emb/centroides.json` | 06 | centroides ECAPA globales |
| `speaker_refs/...` | 07 | candidatos de referencia |

`<id>`: nav109, nav072, nav056, nav139, nav135, nav074, nav167 (ver `fuentes_podcast.json`:
`hablantes` esperados, `doc_anio` del Google Doc).

### asr.json (etapa 02, ya existe)
```json
{"modelo": "...", "params": {...}, "duracion_s": 3969.9, "segments": [
  {"start": 0.0, "end": 27.1, "text": "...", "avg_logprob": -0.2, "no_speech_prob": 0.01,
   "compression_ratio": 1.5,
   "words": [{"word": " Hello,", "start": 0.0, "end": 0.4, "prob": 0.98}]}]}
```
Segmentos de ≤30 s (VAD). `prob` es la probabilidad por palabra de faster-whisper: será `asr_conf`.

### palabras.json (etapa 03: alineado WhisperX)
WhisperX `load_align_model("en")` + `align()` sobre los segmentos de asr.json y audio16k.wav,
solo para **tiempos finos**. La probabilidad sale de asr.json.
```json
{"modelo_alineado": "...", "stats": {"n": 41213, "sin_tiempo": 12, "sin_prob": 30, "desajuste_pct": 0.4},
 "words": [{"i": 0, "w": "Hello,", "start": 0.02, "end": 0.38, "prob": 0.98,
            "align_score": 0.91, "seg": 0, "ts_ok": true}]}
```
- El emparejado palabra WhisperX ↔ palabra faster-whisper se hace **por segmento y por texto
  normalizado** (difflib sobre tokens en minúsculas sin puntuación), nunca por índice global.
  Se registra el porcentaje de desajuste.
- Palabras sin `start`/`end` en WhisperX (números, símbolos): se interpolan entre vecinas y
  llevan `ts_ok: false`. **Una palabra con `ts_ok: false` nunca sirve de punto de corte ni
  de pausa.** Si WhisperX no da tiempo pero faster-whisper sí, se usa el de faster-whisper
  con `ts_ok: false`.
- `w` conserva mayúsculas y puntuación (texto literal del clip).

### diar.json (etapa 04: pyannote)
`pyannote/speaker-diarization-community-1` en GPU, token con `common.token_hf()`.
`min_speakers = len(hablantes)`, `max_speakers = len(hablantes) + 1` (no `num_speakers` exacto).
```json
{"modelo": "...", "trozos": null,
 "turnos": [{"start": 1.2, "end": 9.8, "label": "SPEAKER_00"}],
 "exclusivo": [{"start": 1.2, "end": 9.8, "label": "SPEAKER_00"}],
 "solapes": [{"start": 9.5, "end": 9.8}],
 "embeddings": {"SPEAKER_00": [0.1, ...]}}
```
- `turnos`: diarización normal (con solapes). `exclusivo`: la `exclusive_speaker_diarization`
  de pyannote 4. `solapes`: intervalos donde ≥2 etiquetas de `turnos` coinciden.
- `embeddings`: los de pyannote por etiqueta, si la salida los trae.
- Episodios largos (nav056 dura 3,6 h): por encima de 5.400 s (`--max-entero`) se diariza
  directamente por trozos, para no arriesgar la RAM en el clustering. Con `--trozos 3600`
  diariza por trozos de 60 min con 30 s de solape; las etiquetas pasan a `T0_SPEAKER_00`,
  `T1_SPEAKER_00`… y `trozos` guarda los límites. La etapa 06 las une por embeddings.

### oficiales/<id>.json (etapa 05: transcripts de nav.al, solo comprobación cruzada)
Fuente: `~/naval-datos/oficiales/docs/<año>_all_podcasts.txt` (Google Docs exportados).
Cada episodio del Doc empieza con una línea `Naval`, la fecha (`May 13 2020`), el título,
la duración (`40:46`) y `Get podcast`; el cuerpo acaba en la línea `Related`. Hay títulos de
sección (líneas cortas sin puntuación final) que se ignoran. Las líneas sin prefijo son del
último hablante. Prefijos con variantes: Naval/Naval Ravikant → naval; Nivi/Babak Nivi →
nivi; Brett/Brett Hall → brett; David/David Deutsch → deutsch; Kapil/Kapil Gupta → kapil;
Matt/Matt Ridley → ridley; Vitalik/Vitalik Buterin → vitalik; Haseeb/Haseeb Qureshi →
qureshi; Max/Max Hodak → hodak; Guillermo/Guillermo Rauch → rauch; Blake/Blake Scholl → scholl.
```json
{"id": "nav072", "entradas": ["Kapil Gupta: Conquering the Mind"], "cobertura": "parcial",
 "turnos": [{"speaker": "naval", "texto": "..."}],
 "palabras_por_hablante": {"naval": 3963, "kapil": 3801}}
```
- El de nav072 lleva el título «Highlights» y títulos de sección, pero es **completo**:
  Naval 3.963 y Kapil 3.801 palabras para 40:46 (~190 palabras/min), igual que
  https://nav.al/kapil (copia en `~/naval-datos/oficiales/web/nav072.txt`).
  `cobertura` se calcula: palabras oficiales / (duración en min × 170); <0,6 → "parcial".
- nav167 es un recopilatorio: incluye las entradas de los órdenes 164, 165, 166 y 167 del
  catálogo (`catalogo.json` del repo da los títulos). nav056 (*How to Get Rich*) es el
  recopilatorio de los episodios 5–54 del Doc de 2019, más el material extra.

### hablantes.json (etapa 06: quién habla)
Entrada: palabras.json, diar.json, oficiales/<id>.json, orig o audio16k.
1. **Etiqueta por palabra**: la de `exclusivo` en el punto medio de la palabra; `solape: true`
   si la palabra toca un intervalo de `solapes` (±0,1 s).
2. **Hablante oficial por palabra** (comprobación cruzada): alineado **local**, no global
   (los Docs pueden estar reordenados, ser parciales o recopilatorios). Por cada segmento
   ASR se busca la ventana del transcript oficial con más n-gramas compartidos y se
   alinea con difflib. Resultado por palabra: hablante oficial o `null` (sin cobertura).
3. **Embeddings**: ECAPA de speechbrain (`speechbrain/spkrec-ecapa-voxceleb`, en CPU) sobre
   tramos exclusivos, sin solape, de ≥3 s (recortados a 10 s). Centroide por etiqueta.
4. **Etiqueta → hablante**: voto ponderado por palabras con hablante oficial. Estado:
   - `ok`: acuerdo ≥0,8 con ≥200 palabras con cobertura, y, si ya existe el centroide
     global del hablante de otro episodio, coseno ≥ umbral (por defecto 0,55);
   - `dudoso`: cualquier otro caso con algo de evidencia (**hay que preguntar al usuario**);
   - `descartado`: <30 s de habla o sin evidencia.
   Etiquetas de trozos distintos (`T0_…`, `T1_…`) se unen por coseno de centroides.
5. **Tramos**: rachas máximas de palabras consecutivas con la misma etiqueta `ok`, sin
   solape y sin hueco interno >1,5 s. Por tramo: `sim` (coseno ECAPA del tramo, si dura
   ≥1,5 s, contra el centroide del hablante), `n_off` (palabras con hablante oficial),
   `n_desacuerdo` (oficial ≠ asignado). **Un tramo con desacuerdo >20 % de `n_off` se
   descarta** (regla del usuario: si embeddings y transcript no coinciden, fuera). Un tramo
   con `n_off == 0` se marca `sin_cobertura: true`, y solo vale si `sim` ≥ umbral alto (0,65).
```json
{"id": "nav109",
 "etiquetas": {"SPEAKER_00": {"hablante": "naval", "estado": "ok", "acuerdo": 0.97,
               "n_cobertura": 5400, "segundos": 2100.5, "cos_global": 0.71}},
 "tramos": [{"hablante": "naval", "label": "SPEAKER_00", "start": 12.3, "end": 58.1,
             "w0": 40, "w1": 180, "sim": 0.78, "n_off": 120, "n_desacuerdo": 1,
             "sin_cobertura": false, "descartado": false, "motivo": null}]}
```
`emb/<hablante>.npy`: centroide global (media normalizada de los centroides `ok` de todas
las fuentes procesadas). `emb/centroides.json`: de qué fuentes y etiquetas sale cada uno.
Con `--global` la etapa recalcula los centroides con todas las fuentes y vuelve a puntuar
`sim` en todos los hablantes.json.

### speaker_refs (etapa 07: candidatos de referencia, Fase 1a)
Huecos: `ref01` ≈6 s, `ref02` ≈12 s, `ref03` ≈25 s, con ±20 % (4,8–7,2 / 9,6–14,4 / 20–30 s,
contando el margen). 2–3 candidatos por hueco, ordenados por similitud con el resto de su
voz y por calidad estimada.
- Hablantes y fuentes: `naval` de todas las fuentes **menos nav072**; `naval_kapil` solo de
  nav072 (2–3 clips en total, de cualquier duración entre 6 y 25 s); el resto de hablantes,
  de las fuentes donde aparecen.
- Ventana válida: palabras consecutivas de un tramo no descartado; hueco ≥0,4 s antes de la
  primera palabra y después de la última (respecto a CUALQUIER palabra o turno de
  diarización de cualquiera); ninguna palabra `ts_ok: false` en los bordes; ningún turno
  de otra etiqueta ni solape en `[start-0,2, end+0,2]`; hueco interno máximo de 0,8 s (habla
  continua); prob mínima de palabra ≥0,4 y media ≥0,85; fuera de los 45 s iniciales y
  finales del episodio (sintonía). Preferir ventanas que empiezan tras `.?!` y acaban en `.?!`.
- Corte: de `orig.wav`, en `[start-0,2, end+0,2]`, PCM16 mono a la sr original, **sin
  normalizar ni limpiar**. Se rechaza si hay clipping (pico ≥ -0,1 dBFS).
- Métricas: `sim` (ECAPA del clip contra `emb/<hablante>.npy`), DNSMOS (paquete `speechmos`,
  CPU, sobre una copia a 16 kHz), `asr_conf` media y mínima, LUFS (pyloudnorm, solo se
  anota), duración y caracteres.
- Texto: el clip se **re-transcribe solo** con faster-whisper large-v3 (beam 5, sin prompt,
  GPU con candado). Ese es el `.txt`. Si difiere del texto largo (WER >10 %) se marca.
- Salida:
  - `speaker_refs/<h>/candidatos/<h>_ref01_c1.wav` + `.txt` (c1 = mejor);
  - `speaker_refs/candidatos.json`: por candidato, hablante, hueco, fichero, fuente, start,
    end, dur, texto, texto_largo, wer_largo, sim, dnsmos, asr_conf, lufs y puntuación;
  - `speaker_refs/refs.json`: fuente y tiempos de todos los candidatos, para que la parte 2
    nunca los meta en `eval`;
  - `speaker_refs/escuchar.html`: página local (no publicar) con un `<audio>` por
    candidato (rutas relativas), texto, métricas, agrupada por hablante y hueco.
- Los nombres definitivos (`<h>_ref01.wav`) los pone el usuario al elegir; esta etapa solo
  propone.
