# Modelos TTS con clonación de voz para el doblaje EN→ES del podcast de Naval

> Investigación del 2026-10-27. No se ha ejecutado ni instalado nada.
> Objetivo: elegir un único motor base que clone desde audio en **inglés** y hable **español**,
> que se pueda fine-tunear por hablante con 30–70 min y que quepa en Colab.

## 0. Resumen ejecutivo

- **Hay novedades desde la última criba.** Han salido modelos nuevos con pesos abiertos, licencia
  comercial y español:
  - OmniVoice (marzo de 2026).
  - dots.tts (junio).
  - Confucius4-TTS (junio–agosto).
  - FireRedTTS3 (agosto).
  - IndexTTS-2.5 (agosto), que ya habla español.
  - Ming-3.0-tts (20 de octubre).
  - Chatterbox Multilingual V3 (junio), con un **pack monolingüe de español** (`es-es` y
    `es-mx-latam`).
- **Las licencias descartan media lista:**
  - XTTS v2 sigue bajo la CPML, que es **no comercial**, y Coqui ya no existe para venderte una
    licencia. Afecta al trabajo ya hecho con XTTS.
  - También descartan Fish S2 Pro, Higgs Audio v3, Voxtral TTS, Breeze TTS 2, F5-TTS y X-Voice.
- **El problema de fondo está documentado en casi todos los modelos.** Al clonar desde inglés, el
  acento inglés se filtra al español. Hay issues sobre ello en Qwen3-TTS, OmniVoice, VoxCPM2 y
  Chatterbox. Ningún benchmark público mide EN→ES con acento: la cifra más cercana es zh→es, en la
  tabla de IndexTTS-2.5. Por eso la criba propia sigue siendo imprescindible.
- **Recomendación:**
  - Criba zero-shot con:
    1. Chatterbox Multilingual V3, el general y el pack de español.
    2. OmniVoice.
    3. Qwen3-TTS-12Hz-1.7B-Base.
    4. dots.tts.
  - Piloto de fine-tuning con **OmniVoice** (LoRA oficial) y **Chatterbox V3** (LoRA comunitario
    sobre T3, o ajuste solo de la parte acústica).
  - En los dos pilotos, el inglés real se mezcla con español sintético del mismo hablante.
  - Plan B barato: TTS español nativo + conversión de voz (Seed-VC o RVC).
- **Tono por episodio tras el fine-tuning** (sección 3.9).
  - **Encajan** los modelos cuyo fine-tuning deja intacta la entrada de audio de referencia:
    Chatterbox (LoRA de T3), OmniVoice (LoRA), VoxCPM2 (LoRA), dots.tts y Confucius4 (fine-tuning
    solo de S2A). Con ellos, la identidad va en los pesos y un fragmento del episodio original en
    inglés aporta la energía y el ritmo de cada episodio.
  - **No encaja el SFT oficial de Qwen3-TTS:**
    - Convierte el modelo en `custom_voice` con voz fija y deja de aceptar referencia [V, código].
    - Los usuarios dicen que el 1.7B-Base fine-tuneado ignora las instrucciones de estilo (#121).
    - En el 0.6B, las instrucciones se descartan sin avisar.
  - Control explícito de estilo:
    - VoxCPM2: instrucción en el texto combinada con la referencia.
    - IndexTTS-2.5: referencia de emoción separada de la de timbre, pero sin fine-tuning.
    - Chatterbox: solo parámetros (`exaggeration` y `cfg_weight`).
  - El mismo canal que transfiere la energía de la referencia inglesa transfiere su acento. Ningún
    estudio público mide esa transferencia EN→ES: la criba debe incluir una prueba de referencia
    calmada frente a referencia enérgica.

## 1. Método, fuentes y límites

**Fuentes que sí se pudieron leer.** Desde este contenedor solo respondían GitHub y
`raw.githubusercontent.com`. Se leyeron completos los README, LICENSE, `pyproject.toml` y guías de
fine-tuning de cada repositorio, además de issues y discusiones concretas.

**Fuentes bloqueadas.** Hugging Face, arXiv, ACL Anthology, Artificial Analysis, readthedocs,
jsdelivr, X y los blogs de los fabricantes daban DNS o 403, tanto con WebFetch como con curl. Lo
que viene de ahí se ha tomado de los extractos del buscador.

Leyenda usada en todo el informe:

- **[V]**: verificado en fuente primaria leída en esta sesión: README, LICENSE o issue oficial del
  repositorio.
- **[S]**: solo extracto de buscador, blog, agregador o paper que no se pudo abrir. Tómese como
  indicio.
- Las cifras de los README son **autoinformadas por cada fabricante**, con su propio protocolo.
  Cuando dos tablas dan cifras distintas para el mismo modelo, se señala.

## 2. Lista amplia

Columnas:

- **ES**: si el modelo habla español.
- **Clona**: si admite clonación zero-shot.
- **Licencia**: licencia de los pesos y si permite monetizar.
- **FT**: si hay código de fine-tuning.

| Modelo (versión, fecha) | ES | Clona | Licencia (pesos) | FT | Veredicto |
|---|---|---|---|---|---|
| **Chatterbox Multilingual V3** + Single Language Pack (Resemble, 10-jun-2026 [S]) | Sí: 23 idiomas, más packs `es-es` y `es-mx-latam` [V] | Sí | MIT [V] | Solo comunitario | **Finalista** |
| **Qwen3-TTS** 12Hz 0.6B/1.7B Base (22-ene-2026) | Sí, 10 idiomas [V] | Sí | Apache-2.0 [V] | Oficial (SFT), con bugs | **Finalista** |
| **OmniVoice** (k2-fsa, ~mar-2026) | Sí, más de 600 idiomas [V] | Sí | Apache-2.0 [V] | Oficial: completo y LoRA [V] | **Finalista** |
| **VoxCPM2** (OpenBMB, abr-2026) | Sí, 30 idiomas [V] | Sí | Apache-2.0 [V] | Oficial: SFT y LoRA [V] | **Finalista** |
| **dots.tts** (rednote, jun-2026) | Sí [V] | Sí | Apache-2.0 [V] | Oficial [V] | **Finalista** |
| **IndexTTS-2.5** (bilibili, 10-ago-2026) | Sí: zh, en, ja, es, ar [V] | Sí | bilibili Model Use License, comercial por debajo de umbrales [V] | No oficial | **Finalista** (solo zero-shot) |
| **Confucius4-TTS** (NetEase Youdao, 2026) | Sí, 14 idiomas [V] | Sí, sin transcripción [V] | Código Apache-2.0 [V]; pesos sin confirmar | Oficial: T2S y S2A [V] | **Finalista** (reserva) |
| **Fun-CosyVoice3-0.5B-2512** (dic-2025) | Sí, 9 idiomas [V] | Sí, cross-lingual [V] | Apache-2.0 [S] | Oficial: scripts [V] | **Finalista** (reserva) |
| Ming-3.0-tts 0.5B / tiny (Ant, oct-2026) | Sí, 7 idiomas [V] | Sí | MIT [V] | **No** hay código de FT | Vigilar: n.º 1 open en AA Controlled Voice, pero sin FT y con similitud baja en idiomas nuevos [V] |
| FireRedTTS3 (ago-2026) | Sí, 24 idiomas [V] | Sí | Apache-2.0, pero el README dice que la clonación es «solely for academic research purposes» [V] | No se vio | Vigilar: ambigüedad de uso y sin FT |
| Fish Audio S2 Pro (mar-2026) | Sí, nivel 2 [S] | Sí | Fish Audio Research License: **no comercial** [V] | Sí | Descartado por licencia |
| Fish Audio Drama 3 (oct-2026, 35B-A3B) | Sí, 83 idiomas [S] | Sí | Community License: comercial con ingresos < 500 k USD, **prohíbe imitar a una persona identificable sin consentimiento** [V] | Sí | Descartado: pide 48 GB en FP8 [S] y su FT es inviable en Colab |
| Higgs Audio v3 / Higgs TTS 3 (4B, jun-2026) | Sí, más de 100 idiomas [S] | Sí | Research & Non-Commercial [V]; posible «Creator Use Grant» [S] | No oficial | Descartado por licencia, y su FT no está permitido sin licencia [S] |
| Voxtral TTS (Mistral, mar-2026) | Sí, 9 idiomas [S] | Sí | CC BY-NC 4.0 [S] | — | Descartado por licencia |
| Breeze TTS 2 (BreezeBlue, 2026) | ¿? | Sí | Pesos no comerciales [S] | — | Descartado por licencia |
| XTTS v2 (Coqui; código mantenido por idiap) | Sí | Sí | **CPML: no comercial** [V], sin nadie que venda licencia | Sí | **Descartado por licencia**, también para lo ya entrenado |
| F5-TTS / F5-Spanish / Cross-Lingual F5-TTS 2 | Sí | Sí | Pesos base CC-BY-NC (por Emilia) [V] | Sí | Descartado por licencia |
| X-Voice (abr-2026, basado en F5) | Sí, 30 idiomas | Sí, sin transcripción | CC-BY-NC [V] | Sí | Descartado por licencia |
| MOSS-TTS 1.5 (OpenMOSS, may-2026, ~8B) | Sí, 31 idiomas [S] | Sí | Apache-2.0 [S] | Sin guía para 1.5 [S] | Descartado: 8B y en zh→es tiene la peor similitud de la tabla (56,6) |
| VibeVoice (Microsoft) | Experimental [S] | No oficial | MIT, pero el TTS largo se retiró [S] | — | Descartado: el repositorio hoy es sobre todo ASR [V] |
| Spark-TTS | No: solo zh y en [V] | Sí | Apache-2.0 | Sí | Descartado: no habla español |
| Llasa (1B multilingual, feb-2025) | Parcial | Sí | — | Sí | Descartado: sin actividad desde feb-2025 y superado |
| MaskGCT (Amphion) | No: entrenado con Emilia, sin español | Sí | — | — | Descartado: no habla español |
| Zonos v0.1 | No: en, ja, zh, fr, de [V] | Sí | Apache-2.0 | — | Descartado: no habla español |
| Dia (Nari Labs) | No: solo inglés [V] | Sí | Apache-2.0 | — | Descartado: no habla español |
| Orpheus multilingüe (abr-2025) | Sí, en la colección «research release» [S] | Débil | Research release | Sí | Descartado: release de investigación, sin cuidar la clonación cross-lingual |
| Step-Audio-EditX | No: el español figura como pendiente en el TODO [V] | — | — | — | Descartado: no habla español |
| Kokoro-82M | Sí, con pocas voces [V] | **No** | Apache-2.0 [V] | — | Descartado: no clona. Útil solo como TTS fuente en la vía de conversión de voz |
| Magpie TTS Multilingual (NVIDIA) | Sí, voces fijas [S] | No: la variante que clona es solo inglés y está restringida [S] | NVIDIA | — | Descartado: no clona en español |
| Supertonic 3 | Sí, 31 idiomas [S] | No [S] | OpenRAIL-M [S] | — | Descartado: no clona y la empresa se disolvió en jul-2026 [S] |
| LongCat-AudioDiT (1B/3.5B) | Sin confirmar | Sí | Sin confirmar | — | Descartado: sin datos de español ni de licencia |
| Qwen-Audio-3.0-TTS / Fun-CosyVoice 3.5 | Sí | Sí | **Solo API** [S] | — | Descartados: no son open-weights |

## 3. Fichas de los finalistas

### 3.1 Chatterbox Multilingual V3 y Single Language Pack de español (Resemble AI)

- **Versión.** Multilingual V3 (0,5B) y el Single Language Pack: finetunes dedicados de 500M para
  `es-es` (España) y `es-mx-latam` [V].
  - Fecha: el commit «v3 multilingual and single language pack release» es del 10-jun-2026 [S].
  - La ficha de NVIDIA dice 26-may-2026 [S].
- **Español.** Nativo en el modelo general y, además, con modelos dedicados por variante [V].
  - Antes de V3 hubo quejas de que el español sonaba latinoamericano (seseo) y no castellano
    (issue #451, ene-2026) [V]. El pack `es-es` responde a eso.
  - La ficha de NVIDIA menciona problemas de pronunciación en castellano con el modelo general [S].
  - Para «español neutro» (GLOSARIO.md) conviene probar los dos packs.
- **Cross-lingual EN→ES.**
  - Soportado. V3 dice mejorar la «preservación de identidad y acento entre idiomas» y reducir las
    alucinaciones [V].
  - Hay un aviso oficial: si la referencia no está en el idioma del `language_id`, la salida
    hereda el acento de la referencia. Se mitiga con `cfg_weight=0` [V].
  - Hay quejas de que **V3 suena peor que V2** en danés y sueco, con acento extranjero
    (issue #551, ago–sep-2026, sin respuesta oficial) [V]. No hay quejas equivalentes en español.
    Hay que comprobarlo frente al resultado de V2 que ya se tiene.
- **Fine-tuning.**
  - **No hay código oficial** [V]: el README no trae script de entrenamiento y los issues #487 y
    #494 siguen sin respuesta.
  - Hay varios repositorios comunitarios:
    - `stlohrey/chatterbox-finetuning`, en desarrollo [S].
    - `gokhaneraslan/chatterbox-finetuning`, con LoRA, completo y 23 idiomas [V], aunque no dice
      si soporta V3.
    - Adaptadores LoRA sobre V3 para amhárico y oromo (gabar-tech) [S].
    - Un LoRA de T3 para español latinoamericano que entrena en unos **3,7 GB de VRAM** [V], así
      que cabe en una T4.
  - Arquitectura: T3, un LM Llama de unos 0,5B que pasa de texto a tokens, más S3Gen, que pasa de
    tokens a mel y lleva el timbre. Los LoRA comunitarios congelan S3Gen y el codificador de voz y
    tocan solo T3 [S].
  - Forgetting:
    - Un LoRA de rango 32 sobre q/k/v/o de T3 «no observó olvido» al añadir idiomas índicos [S].
    - Riesgo concreto del proyecto: tocar T3 solo con inglés es justo lo que mueve el acento y la
      prosodia. Tu LoRA anterior empeoró la similitud, aunque `fabrica-de-voz.md` documenta fallos
      de método que lo invalidan como prueba.
- **Licencia.** MIT [V]. Toda salida lleva la marca de agua PerTh [V]; no impide monetizar.
- **Estabilidad y alucinaciones.**
  - V3 dice reducir «continuación, repetición y habla fuera del prompt» [V].
  - Siguen abiertos issues sobre colas alucinadas, silencios o respiraciones al final (#388) y
    artefactos del multilingüe (#287) [V].
  - **No necesita la transcripción de la referencia** [V].
- **Colab.**
  - Inferencia de 0,5B: cabe en una T4.
  - Fija `torch==2.6.0` y `numpy<2` [V], así que en Colab fuerza a reinstalar torch. Es engorroso,
    pero ya se hizo funcionar.
- **Control del tono tras el fine-tuning.**
  - El fine-tuning (LoRA de T3) no cambia la interfaz. Cada llamada sigue condicionándose con el
    audio de referencia [V, `mtl_tts.py`]:
    - T3 recibe el embedding de voz, los tokens de los **primeros 6 s** de la referencia y el
      escalar `exaggeration`.
    - S3Gen recibe los primeros 10 s.
  - Controles disponibles:
    - `exaggeration`: intensidad emocional.
    - `cfg_weight`: un valor más bajo da un ritmo más pausado.
    - `temperature`.
  - El README dice que los valores por defecto «funcionan bien en todos los idiomas» [V]. No hay
    control por instrucciones de texto.
  - La referencia en inglés sí transfiere su manera de hablar. La prueba indirecta es que transfiere
    el acento, y que la mitigación es `cfg_weight=0` [V]. No se encontró una medición de energía o
    ritmo EN→ES.

### 3.2 Qwen3-TTS 12Hz 1.7B y 0.6B Base (Alibaba Qwen)

- **Versión.** Publicado el 22-ene-2026 [V]. Desde entonces no ha salido otra versión abierta. El
  sucesor, Qwen-Audio-3.0-TTS (jul-2026), solo está disponible por API [S].
- **Español.** Nativo, uno de 10 idiomas [V].
  - En el test multilingüe de MiniMax, el 1.7B-Base da WER 1,126 y SIM 0,814. MiniMax-Speech da
    1,029 y 0,762, y ElevenLabs 1,084 y 0,615 [V, tabla del fabricante].
  - En la evaluación subjetiva del paper de X-Voice, Qwen3-TTS tuvo la mejor similitud en español
    (SMOS 4,28) [S].
- **Cross-lingual EN→ES.**
  - Soportado, pero con **muchas quejas de acento**:
    - Issue #134: clonar inglés a italiano o alemán deja un «strong American accent». Se cerró por
      inactividad y sin respuesta [V].
    - Discusión #230: español con acento inglés [V].
    - Discusión #288: doblaje de inglés a francés que conserva el acento inglés [V].
  - Diagnóstico de la comunidad: el modelo aprende la manera de hablar de los códigos acústicos de
    entrenamiento, así que el acento debe estar en el audio de entrenamiento [V].
  - En zh→es (CV3-eval, medido por IndexTTS) tiene la **mejor similitud** de la tabla: 68,0, con
    WER 5,15 [V, tabla de un tercero].
- **Fine-tuning.**
  - Hay script oficial, `sft_12hz.py`, para **un solo hablante** y fine-tuning completo; no hay
    LoRA oficial [V].
  - El script **tiene fallos documentados** [V]:
    - Doble desplazamiento de etiquetas en el sub-talker (PR #178, abierto).
    - `text_projection`, ya corregido en el PR #188.
    - Un learning rate por defecto de 2e-5 demasiado alto, que genera ruido.
    - Colapsos de EOS.
  - Repositorio comunitario con todo eso corregido: `instavar/qwen3-tts-lora-finetuning`
    (ago-2026) [V]. Usa LoRA r16/α32, lr 2e-6 y 10 épocas, y con batch 4 cabe en 24 GB (una L4).
    No publica métricas de calidad.
  - El informe técnico afirma que un hablante fine-tuneado **solo con datos monolingües** generaliza
    a los 10 idiomas. Un CustomVoice fine-tuneado da WER 1,33 en español [V, del fabricante y con
    su propio pipeline, no con el script público].
  - Si se entrena solo con inglés, el riesgo es la deriva de acento más que el olvido. Mitigación:
    mezclar español; un usuario arregló el acento francés entrenando un LoRA con unas 30 frases
    nativas [V, discusión #230].
- **Licencia.** Apache-2.0 [V].
- **Estabilidad.**
  - En textos largos (long-en) el 1.7B-CustomVoice da WER 2,8 [V].
  - Hay reportes de EOS que no se detiene en modelos fine-tuneados [V].
  - **Necesita `ref_text`**; `x_vector_only_mode` lo evita, aunque con peor clonación [V].
- **Colab.**
  - Inferencia: unos 4 GB para el 0.6B y 8 GB para el 1.7B [S].
  - Fija `transformers==4.57.3` [V].
  - FlashAttention-2 exige bf16/fp16 y no funciona en una T4 (Turing), así que en una T4 va más
    lento. Mejor una L4.
- **Control del tono tras el fine-tuning. Es el punto débil.**
  - **El SFT oficial «hornea» la voz.**
    - Reescribe la config a `tts_model_type: "custom_voice"` y registra el hablante como un
      `spk_id` fijo [V, `sft_12hz.py`].
    - A partir de ahí, `generate_voice_clone`, que es la vía con audio de referencia, **lanza un
      error** porque solo acepta modelos `base` [V, `qwen3_tts_model.py`].
    - Solo queda `generate_custom_voice(text, speaker, instruct=…)`.
  - **Instrucciones:**
    - En el **0.6B** el código descarta `instruct` sin avisar [V].
    - En el 1.7B se aceptan, pero un usuario que fine-tuneó el **1.7B-Base** informa de que el
      modelo resultante **ignora** instrucciones como «más lento» o «tono enfadado». Los CustomVoice
      oficiales sí las siguen (discusión #121, ene–jul-2026, sin respuesta oficial) [V].
    - Ideas sin probar: fine-tunear desde el checkpoint CustomVoice o añadir una columna
      `instruct` a los datos.
  - **Sin fine-tuning**, el Base en modo ICL (referencia más `ref_text`) sí copia la manera de
    hablar de la referencia, acento incluido [V, issues de acento].

### 3.3 OmniVoice (k2-fsa, equipo de Daniel Povey)

- **Versión.** Paper arXiv 2604.00688; publicado hacia el 31-mar-2026 [S]; paquete PyPI `omnivoice`
  0.2.1 [V]. Unos 0,8B sobre Qwen3-0.6B [S]. Es una arquitectura de «diffusion LM»; RTF de hasta
  0,025 [V].
- **Español.** Nativo.
  - MiniMax-MLS, según la tabla de Confucius4: WER 0,81 (el mejor) y SIM 0,814 [V, tabla de un
    tercero].
  - CV3-eval es: 3,52 y 74,1 [V, tabla de IndexTTS].
- **Cross-lingual EN→ES.**
  - zh→es: WER 5,84 y SIM 62,1 [V, tabla de IndexTTS].
  - En IWSLT 2026 (EN→AR/FR/ZH, habla científica), OmniVoice ganó la mayoría de las comparaciones
    frente a Chatterbox y VoxCPM, y se usó como base del sistema enviado [S].
    - Extracto del buscador: en francés, SIM de 0,753 para OmniVoice, 0,619 para Chatterbox y
      0,533 para Qwen3-TTS [S, sin verificar].
    - El modelo fine-tuneado dio la mayor similitud del test, 0,719 [S].
  - **Problema reconocido por el mantenedor** (issue #127, abr-2026): la arquitectura «cannot
    decouple the factors present in reference audio», así que el acento inglés pasa al portugués.
    Se cerró sin solución [V].
- **Fine-tuning.**
  - **Oficial y documentado**: completo y LoRA vía PEFT [V].
    - LoRA por defecto: r16, α32, lr 1e-4, sobre las proyecciones de atención y MLP del LLM, con
      `audio_embeddings` y `audio_heads` totalmente entrenables.
    - Hay config SDPA para GPUs sin `flex_attention`.
  - No se encontró un dato fiable de VRAM: un estimador de terceros dice unos 2 GB en LoRA, lo que
    parece bajo [S]. Por el tamaño, debería caber en una L4.
  - **Hay evidencia de fine-tuning con datos sintéticos cross-lingual:** el paper de IWSLT 2026
    («One Voice, Many Tongues») fine-tunea OmniVoice con datos destilados de un ensemble y mejora
    el WER/CER y la similitud [S]. Es lo más parecido a nuestro caso que se ha encontrado.
- **Licencia.** Apache-2.0 [V]. El descargo de responsabilidad prohíbe la clonación no autorizada
  [V].
- **Estabilidad.**
  - **Issue #116: en español se comen la última vocal o consonante antes de coma o punto** [V].
    - Causa: un fundido de 0,1 s al trocear, más audio de entrenamiento truncado.
    - El mantenedor dice que no hay arreglo completo; el PR #183 lo corrige en parte.
    - Para la limpieza en Audacity eso supone trabajo añadido.
  - Crepitaciones en textos largos con muchas vacilaciones, que se mitigan troceando (#144) [V].
  - `ref_text` es opcional: si falta, transcribe con Whisper [V].
- **Colab.**
  - Tiene **cuaderno de Colab oficial** [V].
  - Pide `transformers>=5.3.0` y torch ≥ 2.4 [V]. La rama 5.x de transformers puede chocar con
    otros paquetes del mismo entorno.
- **Control del tono tras el fine-tuning.**
  - Con el adaptador LoRA se sigue infiriendo **con `--ref_audio` y `--ref_text`**: el ejemplo
    oficial de inferencia con adaptador los usa [V, `lora_finetuning.md`]. La identidad va en el
    LoRA y la referencia sigue entrando en cada llamada.
  - Controles disponibles:
    - Por parámetros: `speed` y `duration` [V].
    - Por instrucciones (`instruct`): **solo en modo voice design**, no combinado con clonación, y
      entrenado únicamente con chino e inglés [V].
  - La prosodia de la referencia se transfiere toda junta, energía y ritmo incluidos, pero
    **también el acento**: el mantenedor reconoce que el modelo no puede separar esos factores
    (#127) [V].

### 3.4 VoxCPM2 (OpenBMB)

- **Versión.** Publicado en abr-2026; informe técnico arXiv 2606.06928 [V]. Tiene 2B parámetros,
  30 idiomas y salida a 48 kHz [V].
- **Español.** Nativo.
  - MiniMax-MLS: WER 1,438 y SIM 83,1, la mejor similitud de su propia tabla [V].
  - Su referencia ASR interna da WER 1,33 % [V].
  - En CV3-eval es se contradicen las fuentes: 3,80 según VoxCPM [V] y 5,49 según IndexTTS [V].
- **Cross-lingual EN→ES.** Aquí está la **señal de alarma**:
  - En zh→es (CV3-eval, medido por IndexTTS) da un **WER de 16,38**, el peor de la tabla, con SIM
    64,9 [V, tabla de un tercero].
  - En el modo «Ultimate Cloning», que usa referencia más transcripción, el acento de la
    referencia pasa al idioma destino. El mantenedor recomienda la clonación normal, sin
    transcripción (issue #321) [V].
  - Hay un issue abierto de alucinación en frases de una sola palabra (#357) [V].
- **Fine-tuning.**
  - **Oficial: LoRA y completo**, con WebUI [V].
  - Según la documentación oficial [S]:
    - Unos **20 GB de VRAM con LoRA** y unos 40 GB con fine-tuning completo.
    - LoRA r32 alcanza «~98 % de la similitud del fine-tuning completo».
    - Recomiendan entre 5 y 50 clips para clonar un hablante.
  - Config por defecto: r32/α32, lr 1e-4, 1000 pasos [V].
  - La documentación aconseja **mezclar datos para reducir el olvido** al añadir idiomas [S].
- **Licencia.** Apache-2.0, apto para uso comercial [V].
- **Estabilidad.** El README admite variabilidad entre ejecuciones («generar 1–3 veces») [V]. La
  causa más común de un final que no se detiene es el silencio largo al final de los clips de
  entrenamiento [S].
- **Colab.**
  - Inferencia con unos 8 GB [V]: cabe en una T4 o L4.
  - El LoRA pide una L4 de 24 GB, justa.
  - Requisitos: Python 3.10–3.12 y torch ≥ 2.5 [V].
- **Control del tono tras el fine-tuning.**
  - La API tiene `load_lora`, `set_lora_enabled`, etc. [S, changelog], y se usa con los mismos
    argumentos de audio. Hay un script comunitario que infiere con LoRA más `prompt_wav_path` [S].
  - No se encontró confirmación oficial de que, tras el LoRA, la referencia siga mandando sobre la
    voz aprendida.
  - Es el finalista con **más control explícito** [V]:
    - «Controllable cloning»: referencia aislada para el timbre más una instrucción entre
      paréntesis al principio del texto, por ejemplo `(slightly faster, cheerful tone)…`, para
      ajustar velocidad, emoción y estilo.
    - «Ultimate cloning» (`prompt_wav_path` más `prompt_text`): reproduce ritmo, emoción y estilo
      de la referencia.
  - No hay datos de si las instrucciones funcionan con texto en español.
  - En cross-lingual, el modo «ultimate» arrastra el acento de la referencia (#321) [V]. La
    combinación prometedora es referencia aislada más instrucción de estilo.

### 3.5 dots.tts (rednote-hilab)

- **Versión.** Publicado en jun-2026; checkpoints `mf-2steps` y `mf-1step` en ago-2026 [V]. Tiene
  2B parámetros, es continuo y genera a 48 kHz [V].
- **Español.** Hay contradicción entre fuentes:
  - Su propia tabla MiniMax-MLS: WER 0,80–1,27 y **SIM 84,0** [V].
  - La tabla de Ming-3.0-tts le atribuye un WER de 2,593 en español [V]. Los protocolos ASR
    difieren.
- **Cross-lingual.**
  - Solo publican en→zh y zh→en; en ambos lidera en similitud, con 75,0 y 72,8 [V].
  - No hay datos de →es.
  - Admite clonación «x-vector only», sin transcripción, que según OpenBMB es la que menos acento
    arrastra en VoxCPM. En dots.tts no está comprobado.
- **Fine-tuning.**
  - Oficial: `scripts/train_dots_tts.py` con una config de humo sobre LJSpeech [V].
  - No menciona LoRA; parece fine-tuning completo.
  - No se encontraron datos de VRAM de entrenamiento ni de forgetting.
- **Licencia.** Apache-2.0, código y checkpoints [V].
- **Estabilidad.** Pico de VRAM en inferencia de 5,6–10,5 GB según la longitud [V]. Admite
  continuación con transcripción, la de mejor similitud, o x-vector sin transcripción [V].
- **Colab.** Python < 3.13, torch ≥ 2.8 y versiones fijadas en `constraints/recommended.txt` [V].
  Usa bf16, así que mejor una L4.
- **Control del tono tras el fine-tuning.**
  - Un checkpoint fine-tuneado de un solo hablante **puede generar sin referencia**: la voz queda
    horneada [V].
  - `--prompt-audio` sigue disponible, en continuación o solo x-vector [V]. Con continuación, la
    referencia transfiere la manera de hablar; con x-vector, sobre todo el timbre.
  - Controles disponibles:
    - Parámetros: `--guidance-scale` y `--language` (etiqueta de idioma).
    - No hay instrucciones de estilo en el TTS.
    - El modelo aparte **dots.tts.edit** cambia emoción, tono, velocidad y pausas sobre un audio ya
      generado (etiquetas `<emo>`, `<pitch>`, `<rate>`), pero su benchmark es solo inglés y chino
      [V].
  - En IWSLT 2026, un equipo informa de que la **etiqueta de idioma** fue lo que más redujo la
    fuga de acento [S]. Encaja con el flag `--language` de dots.tts.

### 3.6 IndexTTS-2.5 (bilibili)

- **Versión.** Publicado el 10-ago-2026; añade español y árabe [V].
- **Español.** Nativo.
  - CV3-eval es: 3,75 y 76,4; la versión RL da 3,33 y 76,7 [V, del fabricante].
- **Cross-lingual.**
  - Diseñado para ello: separa timbre y emoción.
  - zh→es: 5,17 y 65,5; la versión RL da 4,86 y 64,5 [V].
- **Fine-tuning.**
  - **No hay código oficial** [V].
  - El LoRA comunitario `asr-pub/index-tts-lora` es para la v1 y no se ha confirmado que funcione
    con la 2.x [S].
  - Por eso queda descartado como motor fine-tuneable.
- **Licencia.** bilibili Model Use License [V]:
  - Permite el uso comercial salvo por encima de 100 M de usuarios activos al mes o 1.000 M de RMB
    de facturación.
  - El README invita a contactar para uso comercial, y un agregador dice que hace falta
    autorización escrita [S]. La LICENSE leída no lo exige por debajo de esos umbrales.
  - Además, la licencia define el «Model» como «bilibili indextts2»; habría que confirmar que cubre
    la 2.5.
- **Colab.**
  - **`requires-python <3.12`, `flash-attn==2.8.3.post1` y `torch==2.8.*`** [V]: choca de frente
    con el Python de Colab. Probablemente es la causa del abandono anterior.
  - Solo es viable con un entorno `uv` con Python 3.11 aparte.
- **Control del tono.** No se puede fine-tunear, pero es el único finalista con **timbre y emoción
  separados por diseño** [V]:
  - `spk_audio_prompt` da la voz.
  - Para la emoción hay varias vías:
    - `emo_audio_prompt`, una segunda referencia, con `emo_alpha` para la intensidad.
    - `emo_vector`, un vector de 8 emociones.
    - `use_emo_text`, que deriva la emoción del texto con Qwen.
  - `duration_factor` (0,5×–2×) controla la velocidad.
  - Se podría usar una referencia limpia de Naval para el timbre y un fragmento del episodio
    original en inglés para la emoción. No se ha comprobado cuánto acento arrastra la referencia
    de emoción.

### 3.7 Confucius4-TTS (NetEase Youdao), reserva

- **Versión.** Paper arXiv 2608.11650; unos 1,3B [S]; 14 idiomas, incluido el español [V].
- **Puntos fuertes, según el fabricante** [V]:
  - Clonación **sin transcripción** de la referencia.
  - «Unaccented speech synthesis across 14 languages»: apunta justo a nuestro problema.
  - En español, WER 1,02 y SIM 0,778 en MiniMax-MLS.
  - En cross-lingual solo publica pares →zh y →en.
- **Fine-tuning.**
  - Oficial y en dos módulos: T2S, un LLM, y S2A, un flow-matching [V].
  - En el entrenamiento de S2A, **T2S y los codificadores de hablante y de estilo quedan
    congelados** [V]. Se podría ajustar el timbre (S2A) con inglés sin tocar el modelo que decide
    la fonética del español.
  - Hipótesis sin verificar: menos riesgo de olvido.
- **Licencia.** Código Apache-2.0 [V]. Varias fuentes dicen Apache también para los pesos [S],
  pero no se pudo leer la ficha de modelo.
- **Colab.** Requiere w2v-BERT 2.0, Amphion/MaskGCT y CAMPPlus [V]: más piezas que instalar.
- **Control del tono.**
  - Anuncia «Seamless Emotion Transfer: clone the feeling, not just the voice», es decir, emoción
    tomada de la referencia, a la vez que habla «sin acento» entre idiomas [V, del fabricante].
  - Si solo se fine-tunea S2A, la inferencia sigue tomando `prompt_wav`, y el codificador de estilo
    (CAMPPlus) queda congelado [V].
  - En teoría es el que mejor encaja con «identidad fija, tono del episodio». Nadie lo ha
    verificado de forma independiente.
  - No tiene instrucciones de texto.

### 3.8 Fun-CosyVoice3-0.5B-2512 (Alibaba Tongyi), reserva

- **Versión.** Dic-2025: modelo base, RL y scripts de entrenamiento e inferencia [V]. CosyVoice 3.5
  (mar-2026) es solo API [S].
- **Español.** Nativo, 9 idiomas [V]. CV3-eval es: 4,04 y 78,9 [V, tabla de IndexTTS].
- **Cross-lingual.** zh→es: 4,58 y 64,0 [V]. Es de los mejores en WER.
- **Fine-tuning.**
  - Scripts oficiales en `examples/libritts` [V].
  - Un estudio sobre inglés de Singapur fine-tuneó CosyVoice 3 [S]:
    - Ajustar **el LLM** fue lo que más mejoró el acento.
    - **Ajustar el vocoder degradó la calidad** con artefactos.
- **Control del tono.**
  - Admite instrucciones de idioma, dialecto, emoción, velocidad y volumen [V], además de clonación
    con referencia.
  - Que esas instrucciones sobrevivan a un fine-tuning por hablante es algo que no se ha
    verificado.
- **Por qué es solo reserva.** Ya se abandonó por dependencias (pynini, ttsfrd), es el más antiguo
  de la lista y no está claro que vaya a mantenerse en abierto.

### 3.9 Control del tono después del fine-tuning: comparativa

**Requisito del autor.** Fine-tunear la identidad de cada voz **una sola vez** y que el tono de
cada episodio (más calmado, más enérgico) siga al del episodio original en inglés.

Columnas:

- **(a)**: si el modelo ya fine-tuneado sigue aceptando una referencia y si esta transfiere
  prosodia, energía y ritmo.
- **(b)**: si hay control de estilo por instrucciones o parámetros, y si funciona en español.
- **(c)**: si la prosodia de una referencia en inglés llega a la salida en español.

| Finalista | (a) Referencia tras el fine-tuning | (b) Control de estilo | (c) Prosodia EN → salida ES |
|---|---|---|---|
| **Chatterbox V3 / pack es** | **Sí.** La arquitectura no cambia con el LoRA de T3. Cada llamada usa los primeros 6 s de la referencia en T3 y 10 s en S3Gen [V, código] | Parámetros: `exaggeration`, `cfg_weight` y `temperature`. Según el README «funcionan en todos los idiomas» [V]. Sin instrucciones de texto | Sí, pero con acento. `cfg_weight=0` mitiga el acento [V], y no está documentado qué le hace a la prosodia |
| **Qwen3-TTS** | **No.** El SFT oficial lo convierte en `custom_voice` con un `spk_id` fijo, y `generate_voice_clone` da error [V, código] | Solo con `instruct`, y solo en el 1.7B: en el 0.6B se descarta sin avisar [V]. Un usuario informa de que el 1.7B-Base fine-tuneado **ignora las instrucciones** (#121) [V]. En español, sin datos | Solo sin fine-tuning: el Base en modo ICL copia la manera de hablar y el acento de la referencia [V] |
| **OmniVoice** | **Sí.** La inferencia con adaptador LoRA usa `--ref_audio` y `--ref_text` [V, docs] | `speed` y `duration` [V]. `instruct` solo en voice design, sin clonación, y entrenado solo con zh y en [V] | Sí: energía y ritmo pasan, pero también el acento, porque el modelo no separa esos factores (#127) [V] |
| **VoxCPM2** | Probablemente sí: hay API LoRA y la referencia sigue entrando como argumento [S]. Falta confirmación oficial | **El más completo.** Instrucción entre paréntesis al principio del texto, del tipo «(más rápido, alegre)», para velocidad, emoción y estilo, combinable con la referencia aislada [V]. En español, sin datos | El modo «ultimate» reproduce ritmo, emoción y estilo, y arrastra el acento (#321) [V]. Mejor referencia aislada más instrucción |
| **dots.tts** | Sí: `--prompt-audio` en continuación o x-vector. Además puede generar **sin** referencia si se fine-tunea a un solo hablante [V] | `--guidance-scale` y la etiqueta `--language` [V]. Emoción, tono y velocidad, solo editando después con `dots.tts.edit` (benchmark en en/zh) [V] | La continuación transfiere la manera de hablar; el x-vector, sobre todo el timbre. Sin datos EN→ES |
| **IndexTTS-2.5** | No aplica: no hay fine-tuning oficial | **Timbre y emoción separados**: `emo_audio_prompt` con `emo_alpha`, `emo_vector`, `use_emo_text` y `duration_factor` [V] | La emoción puede venir de un fragmento en inglés del episodio y el timbre de otra referencia. Cuánto acento arrastra está por medir |
| **Confucius4-TTS** | Sí, si solo se fine-tunea S2A: T2S y el codificador de estilo quedan congelados y la inferencia usa `prompt_wav` [V] | Sin instrucciones; «emotion transfer» desde la referencia [V] | El fabricante dice que transfiere la emoción **sin acento** entre idiomas [V, autoinformado y sin verificar] |
| CosyVoice3 (reserva) | Sí: zero-shot con referencia [V]. Si sobrevive al SFT, sin verificar | Instrucciones de emoción, velocidad, volumen e idioma [V] | Sin datos |

**Conclusiones:**

1. **Lo que encaja con «identidad fija y tono del episodio»** son los modelos cuyo fine-tuning
   **deja intacta la entrada de referencia**: Chatterbox, OmniVoice, VoxCPM2, dots.tts y
   Confucius4 (este último entrenando solo S2A).
   - En cada episodio se pasa como referencia un fragmento de **ese mismo episodio en inglés** del
     mismo hablante. El LoRA aporta el timbre y la referencia aporta la energía y el ritmo.
   - Idea a futuro: como los ids de bloque coinciden entre `.en` y `.es`, se podría usar como
     referencia de cada bloque español el audio inglés de su bloque. Haría falta tener marcas de
     tiempo del audio original por bloque, que hoy no existen.
2. **El mismo canal que trae la energía trae el acento inglés.** Las mitigaciones son:
   - Separar timbre y estilo: IndexTTS-2.5 por diseño; VoxCPM2 con referencia aislada más
     instrucción.
   - Usar la etiqueta de idioma: dots.tts y la experiencia del KIT en IWSLT 2026 [S].
   - Bajar `cfg_weight` en Chatterbox.
   - Elegir referencias cortas y poco marcadas.
3. **El SFT oficial de Qwen3-TTS va en contra de este requisito.** Hornea la voz, elimina la
   referencia y, según la comunidad, pierde el seguimiento de instrucciones. Qwen3-TTS queda como
   candidato para zero-shot, no para el piloto de fine-tuning.
4. **No se encontró ningún estudio** que mida la transferencia de energía o ritmo de una
   referencia inglesa a una salida española. Hay que medirlo en la criba:
   - Dos referencias del mismo hablante, una calmada y otra enérgica.
   - Las mismas frases en español.
   - Comparar la velocidad de habla, la variación de F0 y la energía RMS, y escuchar.

## 4. Vía alternativa: TTS español nativo más conversión de voz (VC)

**Idea.** Sintetizar en español con una voz **nativa**, sin clonar desde inglés, y pasar el
resultado por un conversor de voz entrenado con el inglés de cada hablante.

**¿Es viable en 2026?** Sí, y es barata. Los componentes:

| Conversor | Estado | Licencia | Entrenamiento | Datos |
|---|---|---|---|---|
| **Seed-VC** v1 / v2 | Changelog hasta mar-2025 [V]; v2 «voice & accent conversion» | Código GPL-3.0 [V]; pesos sin verificar | Fine-tuning de «mínimo 100 pasos, 2 min en T4» [V] | Clips de 1 a 30 s [V] |
| **RVC v2 / Applio** | Mantenido por la comunidad | MIT | Por hablante; 30–70 min es su rango ideal | Encaja con lo que hay |
| **Chatterbox VC** (`example_vc.py`) | Mismo paquete que Chatterbox [V] | MIT | Zero-shot | — |
| OpenVoice v2 | 2024, sin cambios | MIT [V] | Zero-shot | Similitud inferior (0,755 frente a 0,868 de Seed-VC en la evaluación de Seed-VC) [S] |
| CosyVoice VC | Modo VC de CosyVoice | Apache | Zero-shot | — |

**Calidad reportada.** No se encontró **ninguna** evaluación publicada de la cadena «TTS nativo →
VC» para doblaje cross-lingual. Lo disponible:

- Seed-VC zero-shot en LibriTTS (inglés): SECS 0,868, frente a 0,844 de CosyVoice y 0,755 de
  OpenVoice [S, evaluación propia del repositorio].
- El README de Seed-VC avisa de que el fine-tuning «mejora mucho la similitud, pero puede subir
  ligeramente el WER» [V].
- Seed-VC v2 «suprime mejor los rasgos del hablante de origen» [V], que es lo que interesa aquí.
- Un paper de 2024 sobre VC políglota dice que se conserva el acento del audio fuente sin datos
  multilingües del objetivo [S].

**¿Evita el olvido del español?** **Sí, por construcción**:

- El TTS no se fine-tunea nunca y el VC solo aprende timbre.
- El contenido (fonemas y acento) viene del audio español nativo, a través de un codificador de
  contenido multilingüe: Whisper en Seed-VC y HuBERT/ContentVec en RVC.
- También evita el acento inglés: la fuente ya suena nativa.

**Contras:**

- **Se pierde la prosodia de Naval.** Ritmo, pausas y entonación son los del hablante fuente; el VC
  solo cambia el timbre.
- Dos etapas suman artefactos: el VC puede meter ruido metálico o errores en sonidos poco vistos en
  inglés, como la «rr» o la «ñ». Esto es una hipótesis sin medir.
- Las alucinaciones del TTS fuente siguen ahí; el VC no las crea ni las corrige.

**Cómo probarlo sin gastar entrenamiento:**

1. Coger la mejor salida española de la criba, por ejemplo Chatterbox `es-es` con una referencia
   nativa neutra.
2. Pasarla por Seed-VC zero-shot con una referencia de Naval.
3. Medir la similitud ECAPA con el mismo cuaderno de métricas. Unos minutos de T4.
4. Si se acerca al TTS directo, fine-tunear Seed-VC o RVC con los 67 min de Naval. El coste es
  marginal.

## 5. Benchmarks con datos de español o cross-lingual

Avisos sobre todas estas cifras:

- Son cifras de **fabricantes**, salvo donde se indica.
- El test MiniMax-MLS clona con **referencia en el mismo idioma**, así que no mide EN→ES.
- El WER no detecta el acento.

**MiniMax-MLS-test, español (WER %, SIM).** Cada columna es la tabla de un fabricante:

| Modelo | Tabla VoxCPM [V] | Tabla Confucius4 [V] | Tabla Ming-3.0 [V] | Tabla propia [V] |
|---|---|---|---|---|
| Qwen3-TTS 1.7B | 1,126 / 81,4 | 1,13 / 0,814 | — | 1,126 / 0,814 |
| Fish S2 (Pro) | 0,910 / 77,6 | 0,95 / 0,734 | 1,216 / 0,748 | — |
| VoxCPM2 | 1,438 / 83,1 | 1,32 / 0,829 | 1,324 / 0,836 | — |
| OmniVoice | — | **0,81** / 0,814 | — | — |
| dots.tts | — | — | 2,593 / 0,839 | 0,80–1,27 / 84,0 |
| FireRedTTS3 | — | — | 1,086 / **0,868** | 1,21 / 86,3 |
| Confucius4-TTS | — | — | — | 1,02 / 0,778 |
| Ming-3.0-tts 0.5b / tiny | — | — | — | 1,099 / 0,763 · 0,971 / 0,797 |
| MiniMax-Speech / ElevenLabs | 1,029 / 76,2 · 1,084 / 61,5 | 1,03 / 0,762 · 1,08 / 0,615 | — | — |

**Contradicciones entre fuentes:**

- dots.tts en español: 0,80–1,27 en su tabla, 2,59 en la de Ming.
- La similitud de Fish S2 va de 0,734 a 0,776 según la tabla.
- VoxCPM2 en CV3-eval es: 3,80 según VoxCPM, 5,49 según IndexTTS.

**CV3-eval, cross-lingual con prompt chino → español** (la tabla de IndexTTS-2.5 [V]). Es la única
cifra pública de clonación hacia el español desde otro idioma:

| Modelo | WER zh→es ↓ | SIM ↑ |
|---|---|---|
| Qwen3-TTS 1.7B | 5,15 | **68,02** |
| IndexTTS-2.5 / -RL | 5,17 / 4,86 | 65,48 / 64,47 |
| VoxCPM2 | **16,38** | 64,89 |
| CosyVoice3-0.5B | 4,58 | 64,04 |
| OmniVoice | 5,84 | 62,08 |
| FireRedTTS-2 | 12,25 | 58,31 |
| MOSS-TTS 1.5 | **4,32** | 56,63 |
| Fish S2 Pro | 4,46 | 55,57 |

**Otras evaluaciones:**

- **IWSLT 2026, tarea de clonación cross-lingual** (EN→AR/FR/ZH, habla científica; Abebe y
  Moslem): OmniVoice superó a Chatterbox, VoxCPM y Qwen3-TTS, y el fine-tuning con datos
  sintéticos mejoró el WER y la similitud [S].
- **Artificial Analysis** [S, no se pudo abrir la web]:
  - Controlled Voice Arena (8 voces clonadas en inglés), oct-2026: Ming-3.0-tts es el n.º 1 de
    los modelos abiertos, con 1069 de Elo [V, según el README de Ming]. Le siguen Drama 3 Preview
    con 1059 y Breeze TTS 2 con 1019 [S].
  - En julio: Fish S2 Pro 1034, Voxtral 1024 y Chatterbox 930 [S].
  - Desde el 22-sep-2026 hay arenas multilingües con español: Cartesia Sonic 3.6 (cerrado) es el
    n.º 1 en español [S]. No se encontró qué modelo abierto lidera en español; Higgs v3 lidera en
    4 de los 9 idiomas, pero no en español [S].
- **Hugging Face Open TTS Leaderboard** (30-sep-2026): mide WER (con Qwen3-ASR), similitud
  (WavLM) y velocidad, y permite filtrar por idioma. Como multilingües fuertes cita OmniVoice,
  Fish S2 Pro y CosyVoice3 [S, leído en un espejo del blog en GitHub]. No se obtuvieron las cifras
  de español.
- **TTS Arena V2** (HF): no se encontraron datos actuales de modelos abiertos.
- **Tu propia criba** (11 frases, referencia de Naval en inglés):
  - Es la **única medición EN→ES** del informe.
  - La similitud ECAPA no es comparable con las cifras WavLM de las tablas.

## 6. Olvido del español y deriva de acento: qué se sabe y cómo mitigarlo

**Dos fenómenos distintos:**

1. **Olvido.** El modelo pierde la capacidad de hablar español. Es tu caso con XTTS a lr 1e-4.
2. **Deriva de acento.** Sigue hablando español, pero con fonética inglesa. Es la queja recurrente
   en Qwen3, OmniVoice, VoxCPM y Chatterbox.

**Evidencia:**

- Qwen afirma que un fine-tuning monolingüe generaliza a otros idiomas [V, del fabricante].
- La comunidad de Qwen dice que el acento se aprende del audio de entrenamiento [V].
- VoxCPM aconseja mezclar datos para no olvidar [S].
- En ASR (Whisper), entrenar solo con un idioma nuevo provoca olvido grave, y mezclar datos lo
  reduce [S].
- LoRA de rango bajo «no observó olvido» en Chatterbox con idiomas índicos [S].

**Mitigaciones, de más a menos respaldadas:**

1. **Mezclar español sintético del mismo hablante.**
   - Cómo: generar 15–30 min de frases en español con el mejor modelo zero-shot y la referencia de
     Naval, filtrarlas por WER (con faster-whisper) y similitud, y mezclarlas con el inglés real.
   - Es la receta del sistema de IWSLT 2026, de Cross-Lingual F5-TTS 2 (prompts sintéticos) y de
     la discusión #230 de Qwen3.
   - Riesgo: hereda el acento de quien genera los datos. Por eso el filtrado y la escucha son
     clave.
2. **Mezclar un poco de español nativo multihablante.** Por ejemplo, con un corpus libre. Así el
   LM sigue viendo fonética española.
3. **LoRA de rango bajo (r 8–16), learning rate bajo y elegir el checkpoint por la validación en
   español**, no el último. Tu LoRA anterior se quedó con el último aunque la pérdida de validación
   subía.
4. **Ajustar solo la etapa acústica o de timbre:**
   - Qué: S3Gen en Chatterbox, S2A en Confucius4, flow en CosyVoice.
   - Por qué: deja intacto el LM que decide la fonética.
   - Respaldo: Confucius4 lo trae así de serie. En CosyVoice 3, en cambio, ajustar el vocoder
     degradó la calidad [S].
   - Es una hipótesis razonable que hay que medir.
5. **En inferencia, clonar sin transcripción de la referencia:** x-vector o modo «regular». En
   VoxCPM2 el mantenedor lo recomienda para no arrastrar acento [V].
6. **Medir el olvido en cada checkpoint:** WER en español con faster-whisper large-v3 sobre las
   11 frases fijas más un párrafo largo. Opcional: la confianza del detector de idioma de Whisper
   como indicador de acento.

## 7. Recomendación final

### Criba zero-shot

Cuatro modelos, todos con inferencia en una T4 o L4, misma referencia de Naval, las 11 frases y un
párrafo largo de unos 60 s para ver la estabilidad:

1. **Chatterbox Multilingual V3**: el general y los packs `es-es` y `es-mx-latam`, con `cfg_weight`
   0 y 0,5.
   - Es el ganador actual (si lo medido fue V2, hay que comprobar si V3 mejora o empeora, porque
     hay quejas en otros idiomas).
   - MIT, pequeño, y ya se sabe instalar.
2. **OmniVoice**, con y sin `ref_text`.
   - El mejor WER en español de las tablas ajenas.
   - El único con evidencia publicada de clonación desde inglés a otros idiomas mejorada con
     fine-tuning.
   - Apache, rápido y con cuaderno de Colab oficial.
   - Hay que vigilar el corte de sílabas finales (#116).
3. **Qwen3-TTS-12Hz-1.7B-Base**, en modo completo y en `x_vector_only_mode`.
   - La mejor similitud en zh→es y en la evaluación subjetiva en español [S].
   - Apache.
   - Hay que vigilar el acento inglés, el problema más documentado.
4. **dots.tts** (`soar` o `mf-2steps`), con continuación y con x-vector.
   - La mejor similitud en español de su propia tabla. Apache, de junio de 2026.

Reservas, si sobra presupuesto:

- VoxCPM2, ya en tu lista: barato de probar, pero su WER zh→es de 16 es mala señal.
- Confucius4-TTS: sin transcripción y diseñado contra el acento.
- Una prueba de la vía VC: Chatterbox `es-es` con referencia nativa → Seed-VC zero-shot con
  referencia de Naval.

IndexTTS-2.5 solo si la instalación con Python 3.11 resulta sencilla, porque no se puede
fine-tunear.

### Los dos favoritos para el piloto de fine-tuning

1. **OmniVoice con LoRA.**
   - Es el único finalista con LoRA **oficial y documentado**, licencia Apache y precedente
     publicado de fine-tuning cross-lingual con datos sintéticos que mejora el WER y la similitud.
   - Receta:
     - Los 67 min de Naval.
     - Más unos 20 min de español sintético filtrado.
     - LoRA r16 y 2–3 checkpoints evaluados en español.
   - En una L4.
2. **Chatterbox Multilingual V3** (o el pack de español que gane la criba).
   - Por qué:
     - Es el mejor zero-shot medido con tu propia voz de referencia.
     - Licencia MIT; el LoRA de T3 cabe en unos 4 GB, así que basta una T4.
     - Su arquitectura en dos etapas permite probar el ajuste solo del timbre.
     - El LoRA anterior no está invalidado: tenía fallos de método documentados.
   - Riesgo: no hay código oficial y hay que elegir un repositorio comunitario.

**Cambio de favorito.** Si en la criba dots.tts supera con claridad a los dos anteriores en acento,
al oído del autor, debe sustituir al segundo favorito con su script oficial.

**Qwen3-TTS queda fuera del piloto de fine-tuning** por el requisito del tono (sección 3.9): su SFT
oficial hornea la voz y elimina la referencia. Solo volvería si alguien demuestra que un
fine-tuning desde CustomVoice conserva las instrucciones en español. Mientras tanto, se puede usar
en zero-shot con una referencia del episodio.

**Prueba de tono que hay que añadir a la criba.** Para cada modelo:

1. Generar las mismas 3–4 frases en español con dos referencias del mismo hablante: una calmada y
   otra enérgica, ambas en inglés.
2. Medir la velocidad de habla, la desviación de F0 y la energía, y escuchar.
3. En VoxCPM2, repetir con instrucción de estilo. En Chatterbox, con `exaggeration` 0,3 y 0,8.

Así se sabe, antes de gastar en fine-tuning, qué motor deja que el tono del episodio mande.

### Por qué no otros

- Fish, Higgs, Voxtral, Breeze, F5, X-Voice y XTTS: su licencia impide monetizar.
- Drama 3: no cabe en Colab para fine-tuning.
- Ming-3.0-tts y FireRedTTS3: no tienen código de fine-tuning, y FireRedTTS3 restringe la
  clonación a investigación. Merece la pena volver a mirarlos en unos meses.

## 8. Dudas abiertas

1. **Consentimiento.** Clonar a Naval, Nivi, Brett Hall o David Deutsch sin su consentimiento choca
   con:
   - Cláusulas de licencia: Fish Community License IV(b)(i) [V].
   - Descargos de responsabilidad: OmniVoice, Ming, FireRed, VoxCPM [V].
   - Las políticas de YouTube sobre contenido sintético.
   Es independiente del motor y conviene resolverlo antes de monetizar. No es asesoramiento
   jurídico.
2. **XTTS v2 no es monetizable** (CPML [V]). Los 45 GB de checkpoints de XTTS en Drive pierden
   valor si se busca uso comercial.
3. **No hay ningún benchmark EN→ES.** La única tabla hacia el español parte del chino. La decisión
   dependerá de la criba propia y del oído del autor.
4. **Faltan datos que no se pudieron leer:**
   - Las fichas de Hugging Face de Chatterbox V3 y de los packs de español, con métricas.
   - La licencia de los pesos de Confucius4.
   - La tabla completa del paper de IWSLT 2026.
   - La arena española de Artificial Analysis.
   - La VRAM real del LoRA de OmniVoice.
5. **Chatterbox V3 frente a V2 en español.** Hay que confirmar con qué versión se hizo la criba
   anterior.
6. **El nombre de los clips** (`001naval.wav` frente a `b01-naval`) ya está decidido en
   `fabrica-de-voz.md`. No afecta a la elección del motor.

## Fuentes

### Primarias leídas en esta sesión [V]

- Chatterbox: <https://github.com/resemble-ai/chatterbox> (README, pyproject)
  - Issues: [#451](https://github.com/resemble-ai/chatterbox/issues/451) · [#487](https://github.com/resemble-ai/chatterbox/issues/487) · [#551](https://github.com/resemble-ai/chatterbox/issues/551)
- Qwen3-TTS: <https://github.com/QwenLM/Qwen3-TTS> (README, finetuning/README.md, pyproject)
  - Issue [#134](https://github.com/QwenLM/Qwen3-TTS/issues/134)
  - Discusiones [#230](https://github.com/QwenLM/Qwen3-TTS/discussions/230) · [#288](https://github.com/QwenLM/Qwen3-TTS/discussions/288)
- Fine-tuning comunitario de Qwen3-TTS: <https://github.com/instavar/qwen3-tts-lora-finetuning>
- Código de Qwen3-TTS:
  - SFT, que escribe `tts_model_type: custom_voice`: <https://github.com/QwenLM/Qwen3-TTS/blob/main/finetuning/sft_12hz.py>
  - Inferencia, con las restricciones por tipo de modelo y el descarte de `instruct` en el 0.6B: <https://github.com/QwenLM/Qwen3-TTS/blob/main/qwen_tts/inference/qwen3_tts_model.py>
- Qwen3-TTS, discusión [#121](https://github.com/QwenLM/Qwen3-TTS/discussions/121): el modelo fine-tuneado ignora las instrucciones.
- Chatterbox, condicionamiento por referencia y `exaggeration`: <https://github.com/resemble-ai/chatterbox/blob/master/src/chatterbox/mtl_tts.py>
- Seguimiento de instrucciones en Qwen3-TTS:
  - Instrucción descartada en el 0.6B [S]: <https://dev.to/hexisteme/qwen3-tts-silently-dropped-my-instruction-and-my-ab-never-noticed-3kca>
  - Fichas de los artículos de IWSLT 2026 [S]: <https://aclanthology.org/2026.iwslt-1.12.pdf> · <https://aclanthology.org/2026.iwslt-1.8.pdf>
- Referencia de la API de VoxCPM, modos de audio y LoRA [S]: <https://voxcpm.readthedocs.io/en/latest/reference/api.html>
- OmniVoice: <https://github.com/k2-fsa/OmniVoice> (README, LICENSE, docs/training.md, docs/lora_finetuning.md, pyproject)
  - Issues: [#116](https://github.com/k2-fsa/OmniVoice/issues/116) · [#127](https://github.com/k2-fsa/OmniVoice/issues/127)
- VoxCPM2: <https://github.com/OpenBMB/VoxCPM> (README, `conf/voxcpm_v2/voxcpm_finetune_lora.yaml`, pyproject)
  - Issue [#321](https://github.com/OpenBMB/VoxCPM/issues/321)
- dots.tts: <https://github.com/rednote-hilab/dots.tts> (README, pyproject)
- IndexTTS-2.5: <https://github.com/index-tts/index-tts> (README, LICENSE, pyproject)
- Confucius4-TTS: <https://github.com/netease-youdao/Confucius4-TTS>
- CosyVoice: <https://github.com/FunAudioLLM/CosyVoice>
- Ming-3.0-tts: <https://github.com/inclusionAI/Ming-3.0-tts>
- FireRedTTS3: <https://github.com/FireRedTeam/FireRedTTS3>
- Fish Speech, S2 Pro y Drama 3: <https://github.com/fishaudio/fish-speech> (README y LICENSE, Fish Audio Community License v1.0)
- Higgs Audio: <https://github.com/boson-ai/higgs-audio>
- X-Voice: <https://github.com/sunnyxrxrx/X-Voice>
- F5-TTS: <https://github.com/SWivid/F5-TTS>
- XTTS: <https://github.com/idiap/coqui-ai-TTS> (docs/source/models/xtts.md, licencia CPML)
- VibeVoice: <https://github.com/microsoft/VibeVoice>
- Descartados por idioma u otras razones:
  - Spark-TTS: <https://github.com/SparkAudio/Spark-TTS>
  - Zonos: <https://github.com/Zyphra/Zonos>
  - Dia: <https://github.com/nari-labs/dia>
  - Orpheus: <https://github.com/canopyai/Orpheus-TTS>
  - Step-Audio-EditX: <https://github.com/stepfun-ai/Step-Audio-EditX>
  - Kokoro: <https://github.com/hexgrad/kokoro>
  - LLaSA: <https://github.com/zhenye234/LLaSA_training>
- Conversión de voz:
  - Seed-VC: <https://github.com/Plachtaa/seed-vc> (README y LICENSE)
  - OpenVoice: <https://github.com/myshell-ai/OpenVoice>
  - RVC: <https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI>
- LoRA de Chatterbox para español: <https://github.com/jeffersonquispe/LoRa>
- Toolkit de fine-tuning de Chatterbox: <https://github.com/gokhaneraslan/chatterbox-finetuning>

### Secundarias o solo vistas en extractos de buscador [S]

- Fichas de modelo en Hugging Face:
  - Chatterbox: <https://huggingface.co/ResembleAI/chatterbox>
  - VoxCPM2: <https://huggingface.co/openbmb/VoxCPM2>
  - Fun-CosyVoice3: <https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512>
  - Fish S2 Pro: <https://huggingface.co/fishaudio/s2-pro>
  - Higgs Audio v3: <https://huggingface.co/bosonai/higgs-audio-v3-tts-4b>
  - FireRedTTS3: <https://huggingface.co/FireRedTeam/FireRedTTS3>
  - Ming-3.0-tts: <https://huggingface.co/inclusionAI/Ming-3.0-tts-0.5B>
- Guía de fine-tuning de VoxCPM: <https://voxcpm.readthedocs.io/en/latest/finetuning/finetune.html>
- Papers:
  - IWSLT 2026, «One Voice, Many Tongues»: <https://arxiv.org/abs/2604.26136> · <https://aclanthology.org/2026.iwslt-1.25/>
  - Qwen3-TTS Technical Report: <https://arxiv.org/abs/2601.15621>
  - OmniVoice: <https://arxiv.org/abs/2604.00688>
  - X-Voice: <https://arxiv.org/abs/2605.05611>
  - Confucius4-TTS: <https://arxiv.org/abs/2608.11650>
  - IndexTTS 2.5: <https://arxiv.org/abs/2601.03888>
  - FireRedTTS3: <https://arxiv.org/abs/2608.17492>
  - Cross-Lingual F5-TTS 2: <https://arxiv.org/abs/2609.15184>
  - VoxCPM2 Technical Report: <https://arxiv.org/abs/2606.06928>
  - Fish Audio S2: <https://arxiv.org/abs/2603.08823>
  - CosyVoice 3: <https://arxiv.org/abs/2505.17589>
  - Fine-tuning de CosyVoice 3 para inglés de Singapur: <https://arxiv.org/abs/2607.23027>
  - Zero-VC: <https://arxiv.org/abs/2606.20218>
- Resemble AI, anuncio de V3: <https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages>
- Ficha de NVIDIA de Chatterbox Multilingual: <https://build.nvidia.com/resembleai/chatterbox-multilingual-tts/modelcard>
- Artificial Analysis:
  - Leaderboard: <https://artificialanalysis.ai/text-to-speech/leaderboard>
  - Leaderboard de modelos abiertos: <https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice/open-weights>
  - Anuncio de Ming-3.0-tts: <https://x.com/ArtificialAnlys/status/2112389514404462613>
  - Anuncio de las arenas multilingües: <https://x.com/ArtificialAnlys/status/2102490340678856997>
- Hugging Face Open TTS Leaderboard: <https://huggingface.co/blog/open-tts-leaderboard> (leído a través del espejo <https://github.com/hanzhad/squelch-news-engine/issues/1244>)
- TTS Arena V2: <https://tts-agi-tts-arena-v2.hf.space/about>
- Blog de Higgs TTS 3: <https://www.boson.ai/blog/higgs-audio-v3-tts> · Licencia y VRAM de Higgs TTS 3: <https://localaimaster.com/blog/higgs-tts-3-licence-and-vram>
- Fish Audio Drama 3:
  - MarkTechPost: <https://www.marktechpost.com/2026/10/14/fish-audio-drama-3-open-weight-tts-model/>
  - audio.cpp: <https://github.com/0xShug0/audio.cpp/blob/main/docs/models/fish_drama3.md>
- Voxtral TTS: <https://the-decoder.com/mistrals-first-open-weight-tts-model-voxtral-clones-voices-from-three-seconds-of-audio-across-nine-languages/>
- Breeze TTS 2: <https://wavespeed.ai/blog/commercial-compliance/breeze-tts-2-review/>
- MOSS-TTS 1.5: <https://aiweekly.co/alerts/openmoss-ships-tts-v15-with-multi-speaker-cloning>
- Fun-CosyVoice 3.5: <https://gaga.art/blog/fun-cosyvoice3-5-and-fun-audiogen-vd/>
- Qwen-Audio-3.0-TTS: <https://www.datalearner.com/en/ai-models/pretrained-models/qwen-audio-3-0-tts-plus>
- Magpie TTS: <https://build.nvidia.com/nvidia/magpie-tts-multilingual/modelcard>
- Supertonic 3: <https://huggingface.co/mlx-community/supertonic-3-mlx>
- LoRA índico de Chatterbox: <https://huggingface.co/reenigne314/chatterbox-indic-lora>
- LoRA de IndexTTS: <https://osrepos.com/repo/asr-pub-index-tts-lora>
- Qwen3-TTS en Medium: <https://medium.com/@zh.milo/qwen3-tts-the-complete-2026-guide-to-open-source-voice-cloning-and-ai-speech-generation-1a2efca05cd6>
