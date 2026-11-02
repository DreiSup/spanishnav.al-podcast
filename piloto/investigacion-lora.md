# LoRA con clonación por referencia: Qwen3-TTS-12Hz-1.7B-Base y OmniVoice

Investigación para los cuadernos de Colab del piloto de doblaje (Naval → español). Fecha: 2026-10-29.

**Leyenda**: **[V]** comprobado en el código o la documentación (cito fichero:línea). **[S]** suposición
o estimación mía, no comprobada.

**Fuentes leídas** (clones en `scratchpad/src/`, nada ejecutado):

| Fuente | Revisión |
|---|---|
| `QwenLM/Qwen3-TTS` | HEAD `022e286` (2026-03-17). El paquete `qwen_tts/` es **idéntico** al wheel `qwen-tts==0.1.1` de PyPI (diff vacío) [V] |
| `instavar/qwen3-tts-lora-finetuning` | HEAD `079db4b` (2026-08-14); parche aplicado sobre una copia del oficial en `src/qwen_patched/` |
| `Finrandojin/alexandria-audiobook` | HEAD `be6343d` (2026-08-02). Es el autor de la discusión #230 |
| `k2-fsa/OmniVoice` | HEAD `08be0b4` (2026-08-24). El soporte LoRA entró en `38e992b` (2026-08-05, PR #243) |
| wheel `omnivoice==0.2.1` (PyPI) | **No trae LoRA**: le faltan `omnivoice/utils/lora.py` y `omnivoice/cli/merge_lora.py` [V, diff] |
| `transformers==4.57.3` (wheel) | Lo leí para comprobar el desplazamiento de etiquetas de la pérdida |
| Discusiones e issues | Qwen #230, #121 y #134 (la #134 es un issue); OmniVoice #127 y #116, leídos con WebFetch |

---

## 0. Conclusiones en una página

1. **Qwen3-TTS, SFT oficial: confirmado que mata la clonación.** `finetuning/sft_12hz.py:134` escribe
   `config_dict["tts_model_type"] = "custom_voice"` y `:137` registra un `spk_id` fijo (3000) con el
   x-vector del **primer lote** horneado en `codec_embedding[3000]` (`:156`). Después,
   `generate_voice_clone` lanza `ValueError` si `tts_model_type != "base"`
   (`qwen_tts/inference/qwen3_tts_model.py:548`) [V]. Además arrastra dos errores de alineación
   (ver §1.2).
2. **Qwen3-TTS con LoRA: la clonación se conserva si cargas el adaptador sobre el Base y no cambias
   `tts_model_type`.** Ni instavar ni Alexandria hornean al hablante en el LoRA. El hablante entra
   **por ejemplo**, como x-vector calculado del `ref_audio` de cada línea. Pruebas:
   - instavar: `sft_12hz_lora.py:55-71`.
   - Alexandria: `train_lora.py:139` y, en inferencia, `tts.py:615` + `:895` + `:913-916`, que usan
     `generate_voice_clone(..., x_vector_only_mode=True, non_streaming_mode=True)` con el LoRA
     cargado [V].

   El modo **ICL** no lo entrena ningún repositorio: funcionará mecánicamente, pero queda fuera de
   la distribución del entrenamiento [S]. **Usa x-vector**: es lo entrenado y además arrastra menos
   acento (ver §1.6).
3. **Qwen3-TTS acepta una referencia distinta por ejemplo**: el campo `ref_audio` de cada línea del
   JSONL (`finetuning/dataset.py:127`) [V]. El README oficial *recomienda* usar la misma para todo
   (`finetuning/README.md:26-28`), pero no lo exige. **El idioma, en cambio, se ignora**: se lee en
   `dataset.py:126` y nunca se usa. El prefijo de entrenamiento siempre es `nothink` (idioma "auto")
   (`dataset.py:182-185`). Para nuestro caso hay que parchearlo (§1.5).
4. **OmniVoice: el LoRA oficial conserva la clonación.** Inferencia con `--lora_adapter` +
   `--ref_audio` + `--ref_text` (`docs/lora_finetuning.md:113-124`; `omnivoice/cli/infer.py:133-144`)
   [V]. Pero **el prompt de entrenamiento es siempre un trozo inicial (0–30 %) del mismo clip**
   (`omnivoice/data/processor.py:82,135`) [V]. No hay campo para indicar otro clip como referencia.
   Hay un atajo limpio que no toca el código, usando `clean_start_token_idx` (§2.3).
5. **Lo más importante para el acento**: OmniVoice y Qwen admiten que la clonación entre idiomas
   lleva el acento del idioma de la referencia.
   - OmniVoice: README `:194` [V]. En el issue #127 el mantenedor dice que el modelo "no puede
     desacoplar" acento y timbre por diseño [V].
   - Alexandria (#230): un LoRA entrenado en un solo idioma impone su acento
     (`lora.md:78-80`) [V].

   Mezclar 60 % de Naval en **inglés** dentro del mismo LoRA juega **en contra** del objetivo
   [S, razonado]. Recomiendo etiquetar cada ejemplo con su idioma y comparar en el piloto dos
   variantes: **LoRA solo-español** frente a **mezcla 60/40**.
6. **Entornos incompatibles**: `qwen-tts` fija `transformers==4.57.3` y `accelerate==1.12.0`
   (`pyproject.toml`) [V]; OmniVoice exige `transformers>=5.3.0` [V]. **Van en cuadernos (runtimes)
   separados.**

---

## 1. Modelo 1 — Qwen3-TTS-12Hz-1.7B-Base

### 1.1 Cómo funciona el condicionamiento (lo necesario para entender los LoRA)

- **Dos modos de clonación** (`qwen3_tts_model.py:401-466`) [V]:
  - **x-vector**: un vector de un encoder ECAPA (`speaker_encoder`) que va en una sola posición del
    prefijo.
  - **ICL**: el x-vector más `ref_text` y los códigos de audio de la referencia, delante del texto
    objetivo (`modeling_qwen3_tts.py:1968-2019, 2188-2196`).
- **Prefijo de códec** (`modeling_qwen3_tts.py:2111-2146`) [V]:
  - Con idioma: `[think, think_bos, <lang_id>, think_eos] + spk + pad + bos`.
  - Con `language="auto"`: `[nothink, think_bos, think_eos] + spk + pad + bos`, sin token de idioma.
- **Frecuencias de muestreo**:
  - x-vector: exige 24 kHz (`modeling_qwen3_tts.py:1941-1942`, `assert sr == 24000`) [V].
  - En inferencia, `create_voice_clone_prompt` remuestrea la referencia solo (`:440-444`) [V].
  - El tokenizador de 12 Hz también remuestrea al codificar (`qwen3_tts_tokenizer.py:156,204`) [V].
  - **En entrenamiento** `dataset.py` carga la referencia con `librosa.load(sr=None)` y hace
    `assert sr == 24000` (`dataset.py:105`) [V]. **Los `ref_audio` tienen que estar en 24 kHz en
    disco.** Los `audio` de destino pueden ir a 44,1/48 kHz porque `prepare_data.py` los pasa por
    `Qwen3TTSTokenizer.encode`, que remuestrea [V].
- **Layout de entrenamiento oficial = modo non-streaming** (`dataset.py:170-205`; contrastado con
  `modeling_qwen3_tts.py:2203-2228`) [V]: todo el texto primero, luego `tts_pad+codec_bos` y luego
  los códigos. En inferencia `generate_voice_clone` usa por defecto `non_streaming_mode=False`
  (`qwen3_tts_model.py:478`) [V]. Para no desalinear con lo entrenado, **infiere con
  `non_streaming_mode=True`**, como hace Alexandria (`tts.py:916`) [V].

### 1.2 SFT oficial (`finetuning/sft_12hz.py`): confirmaciones y errores

| Hallazgo | Dónde | |
|---|---|---|
| Convierte a `custom_voice`; registra `spk_id={speaker_name: 3000}` | `sft_12hz.py:134-142` | [V] |
| Hornea el x-vector del primer lote en `codec_embedding[3000]` | `sft_12hz.py:82-84, 156` | [V] |
| Tras eso, `generate_voice_clone` y `create_voice_clone_prompt` fallan | `qwen3_tts_model.py:401, 548` | [V] |
| **Doble desplazamiento de etiquetas en codec-0**: pasa `labels=codec_0_labels[:, 1:]` y HF vuelve a desplazar dentro de `ForCausalLMLoss` (`transformers/loss/loss_utils.py:57-60`; `loss_type` ForConditionalGeneration → ForCausalLM, `:158`) | `sft_12hz.py:103` | [V] |
| **Estado oculto del sub-talker desalineado**: usa `codec_mask[:, :-1]`. Lo correcto, y lo que usan instavar (`sft_12hz_lora.py:96`) y Alexandria (`train_lora.py:476`), es el oculto de la posición anterior | `sft_12hz.py:108` | [V] código; el diagnóstico de "incorrecto" es [V] razonado contra `generate` |
| Falta `text_projection` sobre los embeddings de texto | `sft_12hz.py:89` (`text_embedding(...)` sin proyección) | [V] |
| Necesita `flash_attention_2` en duro | `sft_12hz.py:51` | [V] |
| LR por defecto 2e-5 → ruido y falta de EOS según instavar (issue #39) | `sft_12hz.py` args; instavar `README.md:26` | [V] doc |

**Error adicional que no corrige nadie (ni instavar ni Alexandria)** [V código / S impacto]. La
pérdida del sub-talker (códigos 1–15) usa `code_predictor.forward_finetune(..., labels=codec_ids[:, 1:])`
(`modeling_qwen3_tts.py:1627-1628`). Ahí los logits ya están alineados: `lm_head[i-1](hidden[:, i])`
predice el código *i* (`:1236-1238`). Pero luego se llama a `self.loss_function`
(`:1242`) = `ForCausalLMLoss`, que **vuelve a desplazar**. Resultado: `lm_head[k]` aprende el código
k+2 y el último no recibe pérdida. Con LoRA sobre `q/k/v/o` del code predictor, esto empuja la
predicción de los códigos residuales en la dirección equivocada. Arreglo (calcular la pérdida a mano):

```python
import torch, torch.nn.functional as F

def sub_talker_loss_fixed(talker, codec_ids, hidden):
    """codec_ids: [N,16] long; hidden: [N,H] = oculto del talker en la posición que predijo el frame."""
    embs = [hidden.unsqueeze(1), talker.get_input_embeddings()(codec_ids[:, :1])]
    for i in range(1, 15):  # mismo bucle que forward_sub_talker_finetune (modeling_qwen3_tts.py:1619-1624)
        embs.append(talker.code_predictor.get_input_embeddings()[i - 1](codec_ids[:, i:i + 1]))
    out = talker.code_predictor.forward_finetune(inputs_embeds=torch.cat(embs, 1), labels=None)
    logits = out.logits.float()                      # [N,15,V], ya alineados con codec_ids[:,1:]
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)), codec_ids[:, 1:].reshape(-1))
```

Alternativa más conservadora [S]: excluir el code predictor del LoRA con un regex en
`target_modules`, por ejemplo `r"^.*talker\.model\.layers\.\d+\.(self_attn|mlp)\.\w+_proj$"`, y no
entrenar el sub-talker.

### 1.3 `instavar/qwen3-tts-lora-finetuning`, leído entero

**Qué es.** Un parche (`patches/0001-qwen3-tts-lora.patch`) que añade:

- `finetuning/sft_12hz_lora.py`;
- `infer_lora_custom_voice.py`;
- `eval_sft_12hz.py` y `bench_lora_step.py`;
- validación en `sft_12hz.py`.

Lo demás son scripts de ciclo de vida y evaluación, más informes de un caso (IMDA NSC FEMALE_01,
inglés de Singapur). README:3-9 [V].

> El parche **no aplica limpio sobre HEAD `022e286`**: el hunk de `sft_12hz.py` falla en la línea 69.
> Está fijado a `0c6a7cb` (README:8, CHANGELOG "Regenerated the sft_12hz.py patch context"). Los
> ficheros nuevos sí aplican [V, `git apply --check`]. Para Colab basta con copiar
> `sft_12hz_lora.py` junto al `dataset.py` oficial.

**Formato de datos.** Es el oficial (`finetuning/README.md:12-24` + `dataset.py:121-139`) [V].

```jsonl
{"audio": "/content/data/es/xtts_0001.wav", "text": "Texto literal.", "ref_audio": "/content/data/ref24k/xtts_0007.wav", "language": "spanish"}
```

- Campos obligatorios: `audio`, `text` y `ref_audio`. `prepare_data.py` añade `audio_codes`
  (lista T×16 de enteros) (`prepare_data.py:49-61`) [V].
- `language` se acepta pero **no se usa** (`dataset.py:126`) [V].
- `ref_audio` es **por ejemplo** y puede apuntar a cualquier fichero de 24 kHz. Así puedes poner,
  para un clip del profesor XTTS, otro clip del mismo profesor [V].

**Preprocesado** [V]:

1. instavar recomienda remuestrear todo a 24 kHz mono con ffmpeg
   (`scripts/resample_to_24k.sh:1-24`), por el `assert` de las referencias.
2. Después, `prepare_data.py` del oficial (tokenizador `Qwen/Qwen3-TTS-Tokenizer-12Hz`, lotes de 32
   en GPU) genera los códigos 12 Hz × 16 grupos.

**Entrenamiento** (`sft_12hz_lora.py`) [V]:

- Lo que corrige:
  - `text_projection` (`:66-69`);
  - pérdida codec-0 con `F.cross_entropy` sin doble desplazamiento (`:80-93`);
  - alineación del oculto del sub-talker (`:96`).
- Pérdida total = `codec_0_loss + sub_talker_loss` (peso 1.0; el oficial usa 0.3) (`:103`). El
  sub-talker sigue teniendo el doble desplazamiento de §1.2.
- `get_peft_model(qwen3tts.model, LoraConfig(task_type=CAUSAL_LM, ...))` sobre **todo** el modelo
  (`:175-183`). Afecta a todas las capas con nombre `q/k/v/o/gate/up/down_proj`: talker **y** code
  predictor (`modeling_qwen3_tts.py:740-746, 848, 898`).
- El x-vector se calcula **por lote** a partir de los `ref_mels`, con `no_grad` (`:55-58`), y se
  inyecta en la posición 6 (`:71`). Es decir, el LoRA aprende **condicionado al x-vector de cada
  ejemplo**.
- Por defecto (`:126-150` y `scripts/run_lora_train.sh:28-40`):

  | Parámetro | Valor |
  |---|---|
  | lr | 2e-6 |
  | épocas | 3 en el script; README:430-438 recomienda 10 |
  | batch | 4 (2 en el .py) |
  | grad_accum | 4 |
  | bf16 | sí |
  | r / alpha / dropout | 16 / 32 / 0.05 |
  | attn | `flash_attention_2`, con argumento `--attn_implementation` |
  | scheduler | ninguno |
  | AdamW wd | 0.01 |
  | clip | 1.0 |

- **VRAM y tiempo**: no publican cifras del LoRA. README:436 dice "Batch size 4 — fits 24 GB GPU
  with gradient accumulation" [V]. El full SFT del 0.6B alcanzó un pico de 9,1 GB
  (`reports/full-sft-bounded-gpu-2026-08-14.md:43`) [V]. La inferencia, unos 4,7–5 GB
  (`reports/runtime-smoke-2026-08-12.md:13`) [V].

**Guardado** (`sft_12hz_lora.py:234-260`) [V]: `save_pretrained` del PEFT
(`adapter_config.json` + `adapter_model.safetensors`) por época en `checkpoint-epoch-N/`, más un
`config.json` con `tts_model_type="custom_voice"` y `speaker_embedding.safetensors` (x-vector del
primer lote). **No guarda optimizador**; reanuda con `--resume_adapter` + `--start_epoch`
(`:132-133, 168-173`).

**Carga** (`infer_lora_custom_voice.py`) [V]:

1. Carga el Base y hace `PeftModel.from_pretrained(tts.model, adapter)` con escala por defecto 0.3
   (`:118, 138-143`).
2. **Luego fuerza `custom_voice`** (`:66-67`) y escribe el x-vector en el `spk_id` 3000
   (`:82-86`).
3. Genera con `generate_custom_voice` (`:158`).

**Lo más importante: ¿sigue funcionando `generate_voice_clone` con su LoRA?**

**Sí, si no usas su script de inferencia.** El cambio a `custom_voice` lo hace el script de
inferencia en memoria (`infer_lora_custom_voice.py:66-67`), no el adaptador: el
`adapter_config.json` de PEFT no lleva `tts_model_type`. El `config.json` del checkpoint no lo lee
`PeftModel.from_pretrained` [V/S: comportamiento estándar de PEFT]. Cargando el Base +
`PeftModel.from_pretrained` + `merge_and_unload()` (o solo sobre `tts.model.talker`, como
Alexandria), el modelo sigue siendo `base` y `generate_voice_clone(ref_audio=..., x_vector_only_mode=True)`
pasa la comprobación de `qwen3_tts_model.py:548` [V].

Como el LoRA se entrenó con el x-vector de cada ejemplo en la misma posición que usa
`generate_voice_clone`, **el modo x-vector es exactamente lo entrenado** (salvo el idioma y el modo
streaming, §1.1). El modo ICL no se entrenó [S: funcionará, pero sin garantías]. El propio instavar
solo compara "Base ICL sin adaptador" frente a "LoRA custom_voice"
(`reports/matched-long-form-base-adapter-2026-08-13.md`) [V]; no prueba LoRA + clonación.

**Escollos documentados** (README:22-34) [V]:

- doble desplazamiento;
- `text_projection`;
- LR 2e-5 → ruido y falta de EOS;
- referencia no a 24 kHz;
- escala LoRA 1.0 sobredirige (usar 0.3–0.35);
- fallos de EOS (~0,5 %): limitar `max_new_tokens`;
- distorsión del primer frame en arranque en frío;
- deriva de timbre entre trozos (fijar semilla);
- sobreajuste a partir de la época 10.

### 1.4 Otros repos de LoRA para Qwen3-TTS

- **`Finrandojin/alexandria-audiobook`** (`app/train_lora.py`, `lora.md`, `app/tts.py`). Es **el
  único que conserva la clonación explícitamente y el autor de la receta de la #230**.
  - LoRA solo en `talker` (que incluye el code predictor), `q/k/v/o`, con gradient checkpointing
    (`train_lora.py:390-404`) [V].
  - Construye la secuencia replicando `generate` (non-streaming, **con token de idioma**,
    `:240-244`). Pérdida codec-0 a mano y bien alineada (`:466-476`). Pérdida total
    `talker + 0.3·sub` (`:484`) [V].
  - **Una sola referencia para todo el dataset** (`ref.wav`, `:109-139`) y **un solo idioma** por
    ejecución (`--language`, `:46`) [V]. Batch 1.
  - Inferencia: `PeftModel` sobre el talker + `create_voice_clone_prompt(x_vector_only_mode=True)` +
    `generate_voice_clone(non_streaming_mode=True)` (`tts.py:615, 892-916`) [V].
  - `lora.md` es la mejor guía práctica que hay [V]:

    | Muestras | Épocas | lr | r/alpha | Pérdida objetivo |
    |---|---|---|---|---|
    | ~30 | 10–15 | 5e-6 | 64/128 | 4,1–4,2 |
    | ~120 | 3 | 2e-6 | 64/128 | 4,1–4,2 |

    - Por debajo de 4,1 el audio sale farfullado; por debajo de 3,5 farfullado o sin EOS (`:5-18, 33-39`).
    - Exposición total (muestras × épocas) de unos 250–400 pases; más de 600 lleva al sobreajuste (`:16`).
    - Idioma nuevo: catalán, 2321 muestras, 1 época, **lr 2e-7**, pérdida 5,38, "clean Catalan".
      Con lr 1e-5 salió farfullado (`:84-93, 125-126`).
    - Ojo: sus pérdidas usan sub-loss con peso 0.3 y el doble desplazamiento del sub-talker. **No
      son comparables** si corriges la pérdida [S].
- `mozi1924/Qwen3-TTS-EasyFinetuning` y `DarioFT/ComfyUI-Qwen3-TTS`: el README de instavar
  (`:449-450`) los cita como full SFT. EasyFinetuning "no incluye LoRA ni los arreglos" [V doc, no
  leídos].
- `sruckh/Qwen3-TTS-finetune`: aparece en la búsqueda. Es un envoltorio de preparación más SFT; no
  lo he leído [S].
- No he encontrado ningún repo que entrene el modo **ICL** (referencia con texto y códigos) [S,
  búsqueda negativa].

### 1.5 Discusiones del repo oficial

- **#230 "Spanish with unwanted English accent"** (jromal, 2026-02-24). Finrandojin (14 y 15 de
  marzo) cuenta que la única solución fiable fue **entrenar con datos nativos**. Su receta:
  1. generar con **Voice Design unas 30 frases en francés**;
  2. entrenar un LoRA con ellas;
  3. todo con el pipeline de Alexandria.

  Resultado: desaparece el "bleed" americano en 30–40 generaciones. Avisa de que **el LoRA hace que
  el inglés salga con acento extranjero**. **En el hilo no hay hiperparámetros ni detalle de la
  referencia** [V, WebFetch]. Por el código de Alexandria [V] sabemos cómo puso la referencia: **una
  sola `ref.wav` del propio dataset sintético** (la elige el usuario en el Dataset Builder,
  `lora.md:48`), x-vector, **idioma fijado** con `--language` y non-streaming. Los hiperparámetros
  para ~30 muestras están en la tabla de `lora.md:7` [V]. Que usara exactamente esos valores en el
  francés es [S].
- **#121** (JaviCru, 2026-01-28): el SFT oficial da el timbre pero pierde el seguimiento de
  instrucciones. Sin solución ni respuesta de mantenedores; elaredo8 propone una columna
  `instruct` [V, WebFetch]. Para nosotros no es relevante: no usamos instrucciones.
- **#134** (es un *issue*, cerrado como "not planned" por inactividad): voces inglesas clonadas a
  italiano, alemán o "africano" salen con acento americano. Un usuario afinó con 3 h y siguió con
  acento [V, WebFetch]. Ni código ni hiperparámetros.

### 1.6 ¿Cómo indicar referencia e idioma por ejemplo? (lo que necesitamos)

- **Referencia por ejemplo**: el campo `ref_audio` del JSONL oficial lo permite ya [V]. Para el clip
  español del profesor XTTS se pone como `ref_audio` otro clip del mismo profesor (24 kHz).
- **Idioma por ejemplo**: el `collate_fn` oficial no lo implementa [V]. Hay dos opciones:
  - **(a)** Mi recomendación [S]: escribir un entrenador pequeño a partir de
    `build_teacher_forcing_input` de Alexandria (`train_lora.py:198-347`), que ya pone el idioma y
    replica `generate`, cambiando tres cosas:
    1. `spk_embedding` **por muestra**, a partir de su `ref_audio`;
    2. `language` **por muestra** (`"spanish"` / `"english"`);
    3. la pérdida del sub-talker de §1.2.
  - **(b)** Parchear `dataset.py:collate_fn` para usar un prefijo de longitud variable: con idioma,
    `codec[3:9] = [think, think_bos, lang, think_eos, SPK, pad]`, la posición del x-vector pasa de 6
    a 7 y todo lo que sigue se desplaza en uno. Hay que cambiar también la posición fija
    `[:, 6, :]` del entrenador.
- **Las claves de idioma** son `talker_config.codec_language_id[language.lower()]`
  (`modeling_qwen3_tts.py:2113-2116`) [V]. Que sean `"spanish"` y `"english"` es [S]: Alexandria
  usa `"english"` (`train_lora.py:46`). Compruébalo en el cuaderno con
  `model.get_supported_languages()`.
- **Sobre el modo de referencia en inferencia**: el blog de ocdevel encontrado en la búsqueda dice
  que el modo x-vector evita el "bleed" de acento de la referencia y que ICL lo arrastra [S, fuente
  secundaria]. Encaja con el mecanismo: en ICL el modelo **continúa** los códigos de la referencia
  inglesa (`modeling_qwen3_tts.py:2188-2196`) [V].

### 1.7 Esquema del entrenador recomendado (Qwen, para el cuaderno)

```python
# Pseudocódigo, partiendo de alexandria/app/train_lora.py:198-347 [V] con cambios [S]
for s in samples:                          # bs=1, grad_accum=8
    spk = model.speaker_encoder(mels24k(s.ref_audio)).detach()   # x-vector POR MUESTRA
    emb, labels, codes, P = build_teacher_forcing_input(s, hf_model, dev, dtype,
                                                       language=s.language)  # 'spanish'/'english'
    h = talker_model(inputs_embeds=emb, use_cache=False).last_hidden_state
    logits = talker.codec_head(h)
    l0 = F.cross_entropy(logits[:, :-1].flatten(0, 1).float(), labels[:, 1:].flatten())
    hid = h[0, P - 1:P + codes.shape[0] - 1]                       # alineación correcta (Alexandria:476)
    loss = l0 + 0.3 * sub_talker_loss_fixed(talker, codes, hid)
```

Inferencia del piloto:

```python
tts = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cuda:0",
                                    dtype=torch.bfloat16, attn_implementation="sdpa")
tts.model.talker = PeftModel.from_pretrained(tts.model.talker, ADAPTER)   # como alexandria tts.py:615
# barrido de escala 0.3/0.5/0.7/1.0 (instavar README:116) con module.set_scale (infer_lora_custom_voice.py:89-101)
prompt = tts.create_voice_clone_prompt(ref_audio=REF_EPISODIO, x_vector_only_mode=True)
wavs, sr = tts.generate_voice_clone(text=frases, language="spanish", voice_clone_prompt=prompt,
                                    non_streaming_mode=True, max_new_tokens=1024)
```

(`generate_voice_clone` no tiene parámetro `seed` (`qwen3_tts_model.py:470-480`) [V]: fija
`torch.manual_seed` antes de cada llamada.)

---

## 2. Modelo 2 — OmniVoice (k2-fsa)

### 2.1 Instalación y compatibilidad

- **PyPI 0.2.1 no trae LoRA** [V, diff del wheel]. Hay que instalar desde git:
  `pip install "omnivoice[lora] @ git+https://github.com/k2-fsa/OmniVoice@08be0b4"`, con el extra
  `lora = ["peft>=0.20.0"]` (`pyproject.toml`) [V]. PyPI tiene peft 0.21.2, que solo pide
  `transformers` sin versión mínima [V].
- `transformers>=5.3.0`, `torch>=2.4`, `torchaudio>=2.4`, `requires-python>=3.10` [V].
- Python 3.13, torch 2.11 y transformers ≥5.3: no hay nada que lo impida en los metadatos [V]. De
  torchaudio solo se usa `torchaudio.functional` (resample) y `compliance` en el denoiser [V, grep];
  eso existe en 2.11 [S]. Que funcione de verdad no lo he probado [S].
- **SDPA para GPU sin flex_attention**:
  - `examples/config/train_config_finetune_lora.json` ya trae `"attn_implementation": "sdpa"` [V].
  - Con SDPA no se empaqueta: agrupa por longitud y rellena con padding.
  - Se aplican `max_sample_tokens=2000`, `min_sample_tokens=50` y `max_batch_size=64`; las muestras
    fuera de rango **se descartan** (`docs/training.md:275-312`) [V].
  - El valor por defecto global es `flex_attention` (`training/config.py:103`) [V].
  - En la L4 (Ada) flex funcionaría probablemente [S]; SDPA es más sencillo y es lo que prueba
    `tests/test_lora.py` [V].

### 2.2 Formato de datos y tokenización

- **Entrada** (`docs/data_preparation.md:8-19`) [V]:

  ```jsonl
  {"id": "...", "audio_path": "...", "text": "...", "language_id": "es"}
  ```

  - Cualquier sample rate: se remuestrea a 24 kHz.
  - Los **campos extra pasan tal cual** a los metadatos (`omnivoice/data/dataset.py:406-436`;
    `scripts/extract_audio_tokens.py:243-244`) [V].
- **Tokenización**: `python -m omnivoice.scripts.extract_audio_tokens` con el tokenizador
  `eustlb/higgs-audio-v2-tokenizer` (8 códigos). Genera **WebDataset**: tars de `.npy` int16 [8,T],
  más jsonl de etiquetas, más un `data.lst` con `<tar> <jsonl> <n> <dur>` (`data_preparation.md:24-152`)
  [V]. Ejemplo para una GPU: `examples/run_finetune_lora.sh:43-71` (cambiar `GPU_IDS` y `--nj_per_gpu`).
  El tokenizador va a ~25 Hz [S, deducido del fallback "Nice to meet you." = 25 tokens en
  `omnivoice.py:1172-1174`].
- **Etiqueta de idioma**: `language_id` en cada línea.
  - El procesador la usa con probabilidad `language_ratio=0.8`; si no, pone `None`
    (`processor.py:84, 93-96, 105`) [V].
  - Ids `en` y `es` (`docs/lang_id_name_map.tsv:165,167`) [V].
  - En el `data_config`, `language_id` es solo organizativo (`data_preparation.md:178`) [V].

### 2.3 ¿Cómo se elige la referencia al entrenar?

- **Siempre un prefijo del mismo clip**: `prompt_ratio ~ U(prompt_ratio_range)` (por defecto
  `[0.0, 0.3]`); los primeros `int(T·ratio)` tokens quedan sin máscara y sin pérdida, y el texto es
  **el del clip entero** (`processor.py:82, 122-148`) [V]. En inferencia ocurre lo mismo:
  `texto = ref_text + " " + text` (`omnivoice.py:1237, 1698-1701`) y `[estilo][texto][tokens_ref][MASK…]`
  (`:1255-1264`) [V].
- Con `drop_cond_ratio=0.1` se tira todo el condicionamiento, para el CFG (`processor.py:71-80`) [V].
- **No hay campo para "otro clip como referencia"** [V]. Sí existe una vía documentada para fijar la
  longitud del prompt: si la etiqueta trae `clean_start_token_idx`, entonces
  `prompt_length = clean_start_token_idx`, **sin drop_cond** y con `<|denoise|>` en el estilo
  (`processor.py:71-73, 102-103, 132-133`) [V]. La usa el aumento de ruido
  (`extract_audio_tokens_add_noise.py:428-432`) [V].

  `<|denoise|>` es justo lo que pone la inferencia por defecto cuando hay referencia
  (`OmniVoiceGenerationConfig.denoise=True`, `omnivoice.py:183, 1223-1224`) [V].

**Atajo para referencia entre clips** [mecanismo V, efecto S]:

1. Concatenar en disco `ref.wav + 0,15 s de silencio + target.wav` (24 kHz).
2. Poner como `text` = `ref_text + " " + target_text`.
3. Añadir en el JSONL `"clean_start_token_idx": ceil((len(ref)+len(sil))/hop)`, con hop = 960 [S].

El procesador hará entonces exactamente lo que hace la inferencia: el prefijo de la referencia sin
pérdida y la pérdida en el destino. No hace falta tocar código.

```jsonl
{"id":"es_xtts_0001__ref0007","audio_path":"/content/cat/es_xtts_0001__ref0007.wav","text":"<ref_text> <target_text>","language_id":"es","clean_start_token_idx":143}
```

Recuerda que la inferencia recorta los silencios de la referencia (`remove_silence`,
`omnivoice.py:786-792`) y concatena los tokens tal cual [V]. Entrenar con unos 0,1–0,2 s de silencio
entre ambos imita eso [S].

### 2.4 Hiperparámetros LoRA por defecto

`examples/config/train_config_finetune_lora.json` [V]:

| Grupo | Valores |
|---|---|
| LoRA | r 16, alpha 32, dropout 0.05, bias none |
| `target_modules` | `q,k,v,o,gate,up,down_proj` del LLM (Qwen3-0.6B) |
| `modules_to_save` | `audio_embeddings`, `audio_heads` (entrenados enteros) |
| Optimización | lr **1e-4**, wd 0.01, clip 1.0, warmup ratio 0.01, coseno, bf16, tf32 |
| Pasos y guardado | **steps 5000**, save/eval cada 500 |
| Batch | `batch_tokens` 8192, `max_batch_size` 64 |
| Ratios | `language_ratio` 0.8, `instruct_ratio` 0, `use_pinyin_ratio` 0 |

- Parámetros entrenables: 19,3 M de 632 M, un 3 % (`docs/lora_finetuning.md:81-85`) [V].
- **Trampa**: si se omiten `instruct_ratio`, `only_instruct_ratio` o `use_pinyin_ratio`, los
  valores por defecto del dataclass son 1.0, 0.5 y 0.3 (`training/config.py:50-52`) [V]. Con
  `only_instruct_ratio=0.5` **la mitad de los ejemplos pierde el prompt de audio**
  (`processor.py:85-87`). Hay que fijarlos siempre a 0.
- **Trampa 2**: con 100 min de audio, unos 150 k tokens de audio por época [S], y
  `batch_tokens=8192`, una época son unos **20–40 pasos**. Los 5000 pasos del ejemplo equivalen a
  >100 épocas: sobreajuste seguro [S]. Fija `steps` según las épocas deseadas.
- El modelo base se carga en **fp32** para entrenar (`training/builder.py:87-94`) [V].

### 2.5 Guardado, carga e inferencia con el adaptador

- **Checkpoint** (`training/checkpoint.py:130-145`; `docs/lora_finetuning.md:160-177`) [V]:
  `accelerator.save_state` (**estado completo, del tamaño del modelo base**) + `save_pretrained`
  del PEFT (`adapter_config.json`, `adapter_model.safetensors`) + tokenizer + `train_config.json`.
  - Para Drive copia solo `adapter_*` y `tokenizer*`.
  - `keep_last_n_checkpoints` rota los antiguos.
  - Reanudar exige los mismos `init_from_checkpoint` y `lora_*` (`lora_finetuning.md:99-109`).
- **Inferencia** [V]:
  - Python: `load_lora_adapter(model, path, merge=True)` → `PeftModel.from_pretrained(...).merge_and_unload()`
    (`omnivoice/utils/lora.py:32-59`).
  - CLI: `omnivoice-infer --lora_adapter` (`cli/infer.py:133-137`).
  - Fusionado: `omnivoice-merge-lora` (`cli/merge_lora.py`), que guarda en fp32
    (`lora_finetuning.md:158`).
- **Sigue usando `ref_audio` y `ref_text`**: es el `generate()` normal (`lora_finetuning.md:113-124`)
  [V]. Si falta `ref_text`, lo transcribe con un ASR que carga al vuelo
  (`omnivoice.py:808-814`) [V]: pásalo siempre.
- La longitud de salida **no la decide un EOS**: el modelo es no autorregresivo y la duración se
  estima a partir de la proporción texto/audio de la referencia (`omnivoice.py:1169-1181`) [V].
  Con una referencia **inglesa** y un destino español, el ritmo hereda la velocidad de Naval en
  inglés [S].

### 2.6 Issues #127 y #116: ¿algo nuevo?

- **#127** (acento PT-BR, 2026-04-25). zhu-han (27 de abril): el modelo "cannot decouple the factors
  present in reference audio due to its architectural design"; cambiarlo exigiría cambios de
  arquitectura. Cerrado como completado el 15 de julio sin cambio técnico [V, WebFetch]. **Lo único
  nuevo desde entonces es que ya existe el LoRA oficial** (PR #243, 5 de agosto), que es lo que
  pedía la solución 2 del issue. La documentación de LoRA no habla de acento [V]. El README:194 sigue
  avisando de que la clonación entre idiomas lleva el acento de la referencia [V].
- **#116** (español: se come la vocal o consonante final antes de coma o punto, 2026-04-19).
  - Primera respuesta de zhu-han: culpa de la inferencia por trozos (`fade_and_pad_audio`, fade de
    0,1 s); sugiere bajar `speed` o `fade_duration`. El commit `398b611` (2026-07-03) expone
    `pad_duration` y `fade_duration` [V].
  - El PR #183 de agonzalezd arregla "muchos, no todos" los casos.
  - **18 de junio, zhu-han**: la causa raíz es que **parte de los datos de entrenamiento están
    truncados al final** y el modelo lo aprendió. Se intentará en "la próxima versión" [V, WebFetch].
  - En el `git log` hasta `08be0b4` no hay pesos nuevos ni otro arreglo [V].
  - **Implicación para el LoRA** [S]: nuestros clips deben llevar **0,1–0,3 s de silencio final sin
    recortar** (propuesta de agonzalezd, 16 de junio). El LoRA puede ayudar a reaprender finales
    completos en español. En la evaluación, usa `fade_duration` bajo (0.04) y frases cortas
    (`audio_chunk_threshold=30 s` → frases <30 s no se trocean, `omnivoice.py:186-187`) [V].

---

## 3. Para ambos modelos

### 3.1 Diseño de datos para quitar el acento (lo crítico)

Hechos [V]: el acento sigue a la referencia y al idioma de los datos del LoRA (OmniVoice README:194,
#127; Alexandria `lora.md:78-80`; Qwen #134 y #230). Mi lectura [S]: el 60 % de Naval en **inglés**
enseña sobre todo timbre, cosa que la referencia ya aporta, y **refuerza la asociación
"timbre de Naval ↔ fonética inglesa"**, que es justo lo que queremos romper. Propuesta para el
piloto, en dos brazos con los mismos pasos:

| Brazo | Datos | Referencia por ejemplo | Idioma |
|---|---|---|---|
| A "solo-es" | 40 min de español sintético | otro clip **del mismo profesor** | es |
| B "mezcla" | 60 min de Naval en inglés + 40 min de español (sobremuestreado hasta ≥50 % de los pasos) | Naval→otro clip de Naval; profesor→otro clip del profesor | en / es |
| (C, opcional) | como B, pero en el español la ref es **un clip inglés de Naval** | Naval-EN → destino ES | es |

- C enseña explícitamente "referencia inglesa → salida española nativa". Riesgo: el modelo aprende
  a **ignorar el timbre de la referencia** y deriva hacia el timbre peor del profesor [S]. Solo
  tiene sentido si los clips XTTS/Chatterbox se generaron clonando a Naval.
- Evaluación: las 55 frases con referencia = clip de Naval del episodio (en inglés), idioma es,
  midiendo:
  - acento: ASR español / CER y escucha;
  - timbre: similitud ECAPA con Naval.

  Compara contra el modelo base sin LoRA.

### 3.2 Cuaderno de Colab de una sola sesión (pasos mínimos)

**Común**: montar Drive; copiar los WAV de Drive a `/content` (disco local, no entrenar leyendo de
Drive); tener la lista de las 55 frases y los clips de referencia de evaluación.

**Qwen3-TTS** (runtime propio):

1. `pip install qwen-tts==0.1.1 "peft>=0.17"`. Baja transformers a 4.57.3 y accelerate a 1.12.0
   [V] → reiniciar el runtime. **No instalar flash-attn**: usar `attn_implementation="sdpa"`
   (soportado: `modeling_qwen3_tts.py:473-474, 504-505`) [V].
2. Remuestrear todo a 24 kHz mono (ffmpeg o librosa) [V: necesario para `ref_audio`]. Construir el
   JSONL `{audio, text, ref_audio, language}` (ref = otro clip del mismo hablante).
3. `prepare_data.py` (tokenizador 12 Hz) → JSONL con `audio_codes`. **Copiarlo a Drive** para no
   repetirlo [S: unos minutos para 100 min].
4. Entrenar con el entrenador de §1.7: bs 1, grad_accum 8, lr 1e-6–2e-6, r 16–64 / alpha 2r, 1–3
   épocas. Cada N pasos (p. ej. 100), `peft_talker.save_pretrained("/content/drive/.../step-N")`
   (decenas de MB) y registrar la pérdida en un CSV en Drive.
5. Generar las 55 frases para 2–3 checkpoints × escalas {0.5, 1.0} con
   `generate_voice_clone(x_vector_only_mode=True, non_streaming_mode=True, language=es)`, con
   `max_new_tokens` limitado (≈ 12,5 tokens/s × 2 × duración esperada) y la semilla fija. Guardar
   los WAV en Drive en cuanto salen.

**OmniVoice** (runtime propio):

1. `pip install "omnivoice[lora] @ git+https://github.com/k2-fsa/OmniVoice@08be0b4"` [V: PyPI no
   sirve].
2. JSONL `{id, audio_path, text, language_id[, clean_start_token_idx]}`: concatenados para la
   referencia entre clips (§2.3) y/o clips sueltos. Dejar 0,1–0,3 s de silencio final.
3. `python -m omnivoice.scripts.extract_audio_tokens --input_jsonl ... --nj_per_gpu 1 --loader_workers 2 --min_num_shards 1`
   → copiar el `data.lst` con sus tars a Drive.
4. `train_config`: partir del de LoRA; `steps` = épocas × pasos por época (≈ 300–600), `save_steps`
   50–100, `keep_last_n_checkpoints` 3, `num_workers` 2, `batch_tokens` 4096–8192, y
   `instruct_ratio`, `only_instruct_ratio` y `use_pinyin_ratio` = 0. Lanzar en segundo plano con
   `accelerate launch --num_processes 1 -m omnivoice.cli.train ...` (o `python -m`) **con
   `output_dir` local**. Un bucle de la celda copia `adapter_config.json`, `adapter_model.safetensors`
   y `tokenizer*` de cada `checkpoint-*` nuevo a Drive. No copiar `model.safetensors` ni
   `optimizer.bin`.
5. Por checkpoint: `OmniVoice.from_pretrained("k2-fsa/OmniVoice", dtype=bf16)` →
   `load_lora_adapter(model, ckpt)` → `model.generate(text=frases, language="es", ref_audio=REF, ref_text=REF_TXT, fade_duration=0.04)`.
   Guardar en Drive.

### 3.3 Riesgos conocidos

| Riesgo | Qwen3-TTS | OmniVoice |
|---|---|---|
| Errores del script | SFT oficial: doble desplazamiento, oculto desalineado, sin `text_projection`, convierte a `custom_voice` [V]. **Sub-talker con doble desplazamiento en todos los repos** [V] | PyPI 0.2.1 sin LoRA [V]; trampa `instruct_ratio` [V]; 5000 pasos por defecto [V] |
| Colapso de EOS | Documentado con lr 2e-5 y con pérdida <3,5–4,1 (instavar README:26,29; Alexandria `lora.md:17,39`) [V]. Mitigar con lr ≤2e-6, `max_new_tokens`, frases cortas en el dataset (`lora.md:54,103`) | No aplica (no autorregresivo) [V]; en su lugar, error de duración estimada [V] y finales truncados (#116) [V] |
| Olvido | El LoRA impone su idioma o acento a los demás idiomas (`lora.md:78`, #230) [V]; deseable aquí. Escala LoRA <1 suaviza [V instavar] | `audio_embeddings` y `audio_heads` se entrenan enteros [V] → más riesgo de sobreajuste con 100 min [S] |
| Acento frente a timbre | x-vector: el acento viene de los pesos (lo que corrige el LoRA) [S] | El acento está en la referencia y no se desacopla (#127) [V]; con referencia inglesa en inferencia volverá parte del acento [S] |
| Entorno | transformers fijado a 4.57.3 [V]; flash-attn sin wheels para torch 2.11/CUDA 13 [S] → sdpa | transformers ≥5.3 [V]; compatibilidad con py3.13 sin probar [S] |
| Disco | — | Cada checkpoint guarda el estado completo (≈ modelo fp32, unos 2,5 GB) [V doc + S tamaño] |

### 3.4 VRAM y tiempo en una L4 (100 min, pocas épocas) — todo [S]

- **Qwen 1.7B LoRA**:
  - Memoria: pesos bf16 ≈ 4 GB más activaciones. Con bs 1 y gradient checkpointing, **8–12 GB**;
    con bs 4 sin checkpointing, 14–20 GB (instavar: "bs 4 cabe en 24 GB").
  - Volumen: unos 1000 clips de 6 s de media → secuencias de ~100–200 frames más el texto.
  - Tiempo estimado: **~5–10 min por época** en la L4; 2–3 épocas más la preparación (~5 min) y la
    evaluación de 55 frases × 3 checkpoints × 2 escalas (~15 min) ≈ **1–1,5 h de sesión**.
- **OmniVoice LoRA**:
  - Memoria: modelo fp32 ≈ 2,5 GB; con `batch_tokens` 8192 y bf16 autocast, **8–14 GB**.
  - Volumen: ~150 k tokens por época (~300 k con referencias concatenadas) → 20–40 pasos por época.
  - Tiempo: 300–600 pasos a ~1–2 s/paso ≈ **10–20 min**; la tokenización de 100 min, ~5 min; la
    evaluación, rápida (32 pasos de difusión por frase) ≈ 5–10 min. **Menos de 1 h de sesión.**
- La A100 no hace falta para ninguno de los dos; la L4 basta [S].

---

## 4. Receta recomendada para el piloto

1. **Primero Qwen3-TTS en modo x-vector** con un entrenador propio basado en Alexandria. Encaja
   mejor con el requisito, porque la referencia queda reducida a un x-vector de timbre y la fonética
   la ponen los pesos:
   - referencia e idioma por muestra;
   - pérdida del sub-talker corregida;
   - lr 1e-6–2e-6, r 32 / alpha 64 aprox.;
   - 1–3 épocas;
   - checkpoints cada 100 pasos a Drive;
   - inferencia `generate_voice_clone(x_vector_only_mode=True, non_streaming_mode=True, language="spanish")`
     con barrido de escala LoRA.

   Brazos A ("solo-es") y B ("mezcla").
2. **OmniVoice como segundo candidato**: LoRA oficial desde git, SDPA, `steps` fijados por épocas,
   ratios de instrucción a 0, referencia entre clips con `clean_start_token_idx` y silencio final
   en los clips. Esperar que el acento vuelva en parte con la referencia inglesa de Naval (#127).
3. **Decisión** por escucha más CER en español más similitud ECAPA sobre las 55 frases, frente al
   modelo base sin LoRA.
