"""LoRA de OmniVoice (k2-fsa) para el cuaderno 05_lora_omnivoice.

Usa el entrenador oficial (`omnivoice.training`: build_model_and_tokenizer, build_dataloaders y OmniTrainer)
con el LoRA oficial, que entró en el commit 38e992b y se instala desde git en 08be0b4. Lo que cambia respecto
al ejemplo `examples/run_finetune_lora.sh` (detalles en piloto/investigacion-lora.md, §2):

- Referencia de OTRO clip de la misma voz. El procesador oficial solo usa como prompt un trozo inicial del
  mismo clip. Aquí cada ejemplo es [tokens de la referencia][tokens del clip], con el texto
  "texto_ref texto" y `clean_start_token_idx` = número de tokens de la referencia. Con esa clave el
  procesador no pone pérdida en la referencia, añade <|denoise|> y no tira el condicionamiento
  (omnivoice/data/processor.py:71-73, 102-103, 132-148): es la misma entrada que monta generate() con
  ref_audio y ref_text (omnivoice/models/omnivoice.py:1220-1264).
- Se concatenan TOKENS, no audio. La referencia se tokeniza con la función de la inferencia
  (create_voice_clone_prompt: volumen, recorte de silencios, múltiplo del hop y punto final en el texto) y el
  clip con la del script oficial extract_audio_tokens. Así la frontera queda igual que al generar y no hace
  falta calcular el hop a mano.
- Guía sin condicionamiento (CFG). Los ejemplos con `clean_start_token_idx` nunca tiran el condicionamiento,
  así que un 10 % de los ejemplos (lo que tira el preentrenamiento, drop_cond_ratio=0.1) va sin referencia
  ni clave y con `drop_cond_ratio=1.0`: el procesador los convierte en ejemplos sin texto ni prompt, que es
  la rama incondicional que usa generate() con guidance_scale.
- Idioma por ejemplo ("en"/"es") en `language_id`.
- `instruct_ratio`, `only_instruct_ratio` y `use_pinyin_ratio` a 0: los valores por defecto del dataclass
  (1.0, 0.5 y 0.3) quitarían el prompt de audio a la mitad de los ejemplos.
- Pasos fijados por épocas: los 5000 del ejemplo serían más de cien épocas.
- A Drive solo va el adaptador de cada checkpoint, más el optimizador del último para reanudar. El
  checkpoint oficial guarda además el modelo entero (unos 2,5 GB cada vez).
- Silencio final de 0,1–0,2 s en cada clip de entrenamiento (issue #116: el modelo se come el final).
"""
import json
import math
import os
import random
from pathlib import Path

import numpy as np

MODELO = "k2-fsa/OmniVoice"
TOKENIZADOR_AUDIO = "eustlb/higgs-audio-v2-tokenizer"   # el que usa from_pretrained si el modelo no trae el suyo
SR = 24000
COLA_MIN, COLA_OBJETIVO = 0.10, 0.20   # segundos de silencio final: si hay menos del mínimo, se rellena
SILENCIO_DBFS = -50                    # el umbral de remove_silence de OmniVoice
PROB_INCONDICIONAL = 0.1               # el drop_cond_ratio del preentrenamiento

# examples/config/train_config_finetune_lora.json con los cambios del piloto. Los que se calculan
# (steps, save_steps) y los que se eligen en el cuaderno se pasan a config_entrenamiento().
CONFIG = {
    "llm_name_or_path": "Qwen/Qwen3-0.6B",
    "audio_vocab_size": 1025,
    "audio_mask_id": 1024,
    "num_audio_codebook": 8,
    "audio_codebook_weights": [8, 8, 6, 6, 4, 4, 2, 2],
    "drop_cond_ratio": 1.0,          # solo afecta a los ejemplos sin referencia: son los incondicionales
    "prompt_ratio_range": [0.0, 0.3],
    "mask_ratio_range": [0.0, 1.0],
    "language_ratio": 0.8,
    "use_pinyin_ratio": 0.0,
    "instruct_ratio": 0.0,
    "only_instruct_ratio": 0.0,
    "resume_from_checkpoint": None,
    "init_from_checkpoint": MODELO,
    "use_lora": True,
    "lora_r": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "lora_bias": "none",
    "lora_target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "lora_modules_to_save": ["audio_embeddings", "audio_heads"],
    "learning_rate": 1e-4,
    "weight_decay": 0.01,
    "max_grad_norm": 1.0,
    "seed": 1234,
    "lr_scheduler_type": "cosine",
    "warmup_type": "ratio",
    "warmup_ratio": 0.05,            # el 0.01 del ejemplo, con 200 pasos, serían 2 pasos de calentamiento
    "warmup_steps": 0,
    "attn_implementation": "sdpa",
    "max_sample_tokens": 2000,
    "min_sample_tokens": 50,
    "max_batch_size": 64,
    "batch_tokens": 4096,
    "gradient_accumulation_steps": 2,
    "num_workers": 2,
    "mixed_precision": "bf16",
    "allow_tf32": True,
    "logging_steps": 10,
    "eval_steps": 10 ** 9,           # la evaluación la hace guardar(), por idioma y con máscaras fijas
    "save_steps": 10 ** 9,
    "keep_last_n_checkpoints": -1,
}


def config_entrenamiento(**cambios):
    """CONFIG con `cambios`, comprobando que cada clave existe en TrainingConfig: from_json() descarta en
    silencio las claves que no conoce (omnivoice/training/config.py:116-123)."""
    from omnivoice.training.config import TrainingConfig
    cfg = {**CONFIG, **cambios}
    desconocidas = sorted(set(cfg) - set(TrainingConfig.__annotations__))
    if desconocidas:
        raise ValueError(f"Claves que TrainingConfig no conoce: {desconocidas}")
    return cfg


def clave(e):
    """Nombre del clip sin extensión. Sin puntos: WebDataset parte la clave en el primer punto."""
    return Path(e["audio"]).stem.replace(".", "_")


# ---------------------------------------------------------------- tokens de audio

def cargar_tokenizador(dispositivo="cuda"):
    """El tokenizador de audio que usa OmniVoice.from_pretrained (el del modelo si lo trae), y su extractor."""
    from transformers import AutoFeatureExtractor, HiggsAudioV2TokenizerModel
    from omnivoice.models.omnivoice import _resolve_model_path
    ruta = os.path.join(_resolve_model_path(MODELO), "audio_tokenizer")
    if not os.path.isdir(ruta):
        ruta = _resolve_model_path(TOKENIZADOR_AUDIO)
    tok = HiggsAudioV2TokenizerModel.from_pretrained(ruta, device_map=dispositivo)
    return tok, AutoFeatureExtractor.from_pretrained(ruta)


def silencio_final(wav):
    """Segundos de silencio al final de `wav` ([1, T] a 24 kHz), con el umbral de OmniVoice."""
    from pydub.silence import detect_leading_silence
    from omnivoice.utils.audio import numpy_to_audiosegment
    return detect_leading_silence(numpy_to_audiosegment(wav, SR).reverse(), silence_threshold=SILENCIO_DBFS) / 1000


def tokens_destino(tok, fe, ruta):
    """Tokens del clip como destino: lo mismo que extract_audio_tokens con --input_jsonl (JsonlDatasetReader
    normaliza el pico a 0,9 y process_single_sample tokeniza), con el silencio final completado."""
    import torch
    import omnivoice.scripts.extract_audio_tokens as eat
    from omnivoice.utils.audio import load_audio
    wav = load_audio(str(ruta), SR)
    cola = silencio_final(wav)
    if cola < COLA_MIN:
        relleno = np.zeros((1, int(round((COLA_OBJETIVO - cola) * SR))), dtype=np.float32)
        wav = np.concatenate([wav, relleno], axis=1)
    wav = wav / (np.abs(wav).max() + 1e-7) * 0.9
    eat.worker_tokenizer, eat.worker_feature_extractor = tok, fe
    r = eat.process_single_sample({"audio": torch.from_numpy(wav), "label": {"id": Path(ruta).stem}})
    if r["status"] != "success":
        raise RuntimeError(f"No se pudo tokenizar {ruta}: {r['error_msg']}")
    return {"tokens": r["audio_tokens"], "cola": round(cola, 3)}


def tokens_referencia(tok, ruta, texto):
    """Tokens y texto del clip como referencia, con la misma función que generate(ref_audio=..., ref_text=...).
    create_voice_clone_prompt solo usa el tokenizador de audio y la frecuencia: se le pasa eso."""
    from types import SimpleNamespace
    import torch
    from omnivoice.models.omnivoice import OmniVoice
    with torch.inference_mode():
        p = OmniVoice.create_voice_clone_prompt(SimpleNamespace(audio_tokenizer=tok, sampling_rate=SR),
                                                ref_audio=str(ruta), ref_text=texto)
    return {"tokens": p.ref_audio_tokens.to(torch.int16).cpu().numpy(), "texto": p.ref_text}


def _guardar_pt(objeto, ruta):
    import torch
    tmp = ruta.with_name(ruta.name + ".tmp")
    torch.save(objeto, tmp)
    os.replace(tmp, ruta)


def preparar_tokens(ejemplos, cache, dispositivo="cuda", avisar=print):
    """Tokeniza una sola vez cada clip (como destino) y cada referencia, y lo guarda en `cache` (un .pt en
    Drive, de pocos MB). Si se corta, lo ya calculado no se repite. Cada ejemplo necesita `audio`, `texto`
    y `ref` (la ruta de otro ejemplo de la lista)."""
    import torch
    hecho = torch.load(cache, weights_only=False) if cache.exists() else {"destino": {}, "ref": {}}
    texto = {e["audio"]: e["texto"] for e in ejemplos}
    destinos = sorted(set(texto) - set(hecho["destino"]))
    refs = sorted({e["ref"] for e in ejemplos} - set(hecho["ref"]))
    if destinos or refs:
        tok, fe = cargar_tokenizador(dispositivo)
        hecho["frame_rate"], hecho["hop"] = tok.config.frame_rate, tok.config.hop_length
        avisar(f"Tokenizador de audio: hop {hecho['hop']} muestras a {SR} Hz = {hecho['frame_rate']} tokens/s")
        for n, a in enumerate(destinos, 1):
            hecho["destino"][a] = tokens_destino(tok, fe, a)
            if n % 100 == 0 or n == len(destinos):
                _guardar_pt(hecho, cache)
                avisar(f"  clips: {n}/{len(destinos)}")
        for n, r in enumerate(refs, 1):
            hecho["ref"][r] = tokens_referencia(tok, r, texto[r])
            if n % 100 == 0 or n == len(refs):
                _guardar_pt(hecho, cache)
                avisar(f"  referencias: {n}/{len(refs)}")
        del tok, fe
    return hecho


# ---------------------------------------------------------------- ejemplos y WebDataset

def muestra(e, tokens, nombre, incondicional=False):
    """(tokens [8, T] int16, etiqueta) de un ejemplo, en el formato de extract_audio_tokens."""
    from omnivoice.models.omnivoice import _combine_text
    d = tokens["destino"][e["audio"]]["tokens"]
    if incondicional:
        return d, {"id": nombre, "text": e["texto"], "language_id": e["idioma"], "incondicional": True}
    r = tokens["ref"][e["ref"]]
    return np.concatenate([r["tokens"], d], axis=1), {
        "id": nombre, "text": _combine_text(text=e["texto"], ref_text=r["texto"]), "language_id": e["idioma"],
        "clean_start_token_idx": int(r["tokens"].shape[1]), "ref": Path(e["ref"]).stem}


def plan(orden, tokens, semilla, prob_incondicional=PROB_INCONDICIONAL):
    """Todas las épocas de `orden` en una sola pasada de datos. Cada ejemplo lleva la época en la clave
    (`e1_s001`), así que un clip de español aparece una vez por época."""
    rng = random.Random(semilla)
    return [muestra(e, tokens, f"e{n}_{clave(e)}", incondicional=rng.random() < prob_incondicional)
            for n, epoca in enumerate(orden, 1) for e in epoca]


def escribir_webdataset(muestras, destino, frame_rate, n_shards=4):
    """Escribe tars + jsonl + data.lst como extract_audio_tokens (`<tar> <jsonl> <n> <segundos>` por línea,
    omnivoice/data/dataset.py:158-186). Las muestras se reparten por turnos entre `n_shards`: con
    num_workers=2 cada worker de DataLoader lee shards distintos (wds.split_by_worker)."""
    import shutil
    import webdataset as wds
    import omnivoice.scripts.extract_audio_tokens as eat
    if destino.exists():
        shutil.rmtree(destino)
    (destino / "audios").mkdir(parents=True)
    (destino / "txts").mkdir()
    n_shards = max(1, min(n_shards, len(muestras)))
    lineas = []
    for s in range(n_shards):
        tar, jsonl = destino / "audios" / f"shard-{s:06d}.tar", destino / "txts" / f"shard-{s:06d}.jsonl"
        escritor, segundos, mias = wds.TarWriter(str(tar)), 0.0, muestras[s::n_shards]
        with jsonl.open("w", encoding="utf-8") as f:
            for toks, etiqueta in mias:
                etiqueta = {**etiqueta, "num_tokens": int(toks.shape[1]),
                            "audio_duration": round(toks.shape[1] / frame_rate, 3)}
                escritor.write(eat.serialise_numpy(etiqueta["id"], toks.astype(np.int16)))
                f.write(eat._encode_metadata(etiqueta).decode("utf-8") + "\n")
                segundos += etiqueta["audio_duration"]
        escritor.close()
        lineas.append(f"{tar.resolve()} {jsonl.resolve()} {len(mias)} {segundos:.2f}")
    (destino / "data.lst").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    config = destino / "data_config.json"
    config.write_text(json.dumps({"train": [{"manifest_path": [str((destino / "data.lst").resolve())]}]},
                                 indent=1), encoding="utf-8")
    return config


def estimar_pasos(orden, segundos, batch_tokens, acumulacion, frame_rate=25, relleno=0.8):
    """Pasos de optimizador aproximados, antes de tokenizar: audio de referencia + clip a `frame_rate` y unos
    0,3 tokens de texto por carácter. `relleno` es la fracción útil de cada lote. El número exacto lo da
    contar_lotes() con los datos ya escritos."""
    tokens = 0.0
    for epoca in orden:
        for e in epoca:
            tokens += (segundos[e["ref"]] + e["segundos"]) * frame_rate + 0.3 * 2 * len(e["texto"]) + 20
    return math.ceil(tokens / (batch_tokens * relleno) / acumulacion)


def contar_lotes(data_lst, procesador, config):
    """Lotes que da la primera pasada por los datos con el agrupado por longitud oficial
    (StreamLengthGroupDataset), imitando lo que hace el entrenador: set_epoch(0) baraja los shards y cada
    worker del DataLoader se queda con los suyos (wds.split_by_worker) y agrupa por su cuenta."""
    from omnivoice.data.batching import StreamLengthGroupDataset
    from omnivoice.data.dataset import WebDatasetReader, webdataset_manifest_reader
    manifiestos = webdataset_manifest_reader(str(data_lst))
    todos = WebDatasetReader(manifests=manifiestos, evaluation=False)
    todos.set_epoch(0)
    total = 0
    workers = max(1, config["num_workers"])
    for w in range(workers):
        lector = WebDatasetReader(manifests=manifiestos, evaluation=False)
        lector.urls = todos.urls[w::workers]
        lotes = StreamLengthGroupDataset(lector, batch_duration=config["batch_tokens"],
                                         min_length=config["min_sample_tokens"],
                                         max_length=config["max_sample_tokens"],
                                         max_sample=config["max_batch_size"], processor=procesador,
                                         length_fn=lambda s: s["length"])
        total += sum(1 for _ in lotes)
    return total


# ---------------------------------------------------------------- evaluación

def lotes_evaluacion(ejemplos, tokens, procesador, collator, max_tokens, repeticiones=4, semilla=1234):
    """Lotes de evaluación fijos, por idioma. Las máscaras del procesador son aleatorias; aquí se sortean una
    vez con semilla fija y `repeticiones` veces por clip, así todos los checkpoints se miden con la misma
    entrada y la diferencia de pérdida es solo del modelo."""
    import torch
    estado_py, estado_t = random.getstate(), torch.get_rng_state()
    random.seed(semilla)
    torch.manual_seed(semilla)
    por_idioma = {}
    try:
        for _ in range(repeticiones):
            for e in ejemplos:
                toks, etiqueta = muestra(e, tokens, f"eval_{clave(e)}")
                p = procesador({"audio_tokens": torch.from_numpy(toks), "label": etiqueta})
                por_idioma.setdefault(e["idioma"], []).append(p)
    finally:
        random.setstate(estado_py)
        torch.set_rng_state(estado_t)
    lotes = {}
    for idioma, ps in sorted(por_idioma.items()):
        ps.sort(key=lambda p: p["length"])
        lotes[idioma], actual = [], []
        for p in ps:
            if actual and p["length"] * (len(actual) + 1) > max_tokens:
                lotes[idioma].append(collator(actual))
                actual = []
            actual.append(p)
        lotes[idioma].append(collator(actual))
    return lotes


def evaluar(modelo, lotes, dispositivo):
    """Pérdida media por idioma (la misma pérdida ponderada por libro de códigos que el entrenamiento)."""
    import torch
    modelo.eval()
    res = {}
    with torch.no_grad():
        for idioma, ls in lotes.items():
            v = [modelo(**{k: t.to(dispositivo) for k, t in b.items()}).loss.item() for b in ls]
            res[idioma] = round(float(np.mean(v)), 4)
    modelo.train()
    return res


# ---------------------------------------------------------------- entrenamiento

class SaltarLotes:
    """Envuelve el DataLoader para saltar los `n` primeros lotes al reanudar, y así no repetir lo ya
    entrenado. Solo salta la primera vez que se itera.

    El orden de los ejemplos es determinista (shards y búfer barajados con semilla = época). Los lotes
    también lo son si la etiqueta de idioma ("es", "en" o "None", que se sortea) ocupa siempre lo mismo en
    tokens, como se espera del tokenizador de Qwen3. Si no fuera así, el salto sería aproximado: algún
    ejemplo de más o de menos en la frontera."""

    def __init__(self, cargador, n):
        self.cargador, self.n, self.dataset = cargador, n, cargador.dataset

    def __iter__(self):
        it = iter(self.cargador)
        n, self.n = self.n, 0
        for _ in range(n):
            next(it)
        return it


def entrenar(cfg, data_config, ejemplos_eval, tokens, epocas, salida, local, avisar=print):
    """Entrena con el bucle oficial (OmniTrainer). Una pasada por `data_config` son todas las épocas.

    Deja en `salida/` (Drive), en cada checkpoint (uno por época) y al final:
      paso_NNNN/      el adaptador (adapter_config.json + adapter_model.safetensors) y train_config.json
      reanudar.pt     optimizador y planificador del último checkpoint
      estado.json     último paso guardado, pasos totales y pérdida de evaluación por idioma de cada checkpoint
      registro.jsonl  la pérdida de entrenamiento cada `logging_steps` pasos
    Si `salida/estado.json` existe, reanuda desde ese paso: lo ya entrenado no se repite.
    """
    import gc
    import shutil
    import time
    import torch
    import omnivoice.training.trainer as tr
    from omnivoice.training.builder import build_dataloaders, build_model_and_tokenizer
    from omnivoice.training.config import TrainingConfig

    salida.mkdir(parents=True, exist_ok=True)
    local.mkdir(parents=True, exist_ok=True)
    estado = {"paso": 0, "total": None, "guardar_cada": None, "checkpoints": {}}
    if (salida / "estado.json").exists():
        estado = json.loads((salida / "estado.json").read_text(encoding="utf-8"))
        if estado["total"] and estado["paso"] >= estado["total"]:
            avisar(f"Ya estaba terminado ({estado['total']} pasos). Nada que hacer.")
            return estado

    config = TrainingConfig(**cfg)
    config.output_dir, config.data_config = str(local), str(data_config)
    modelo, tokenizer = build_model_and_tokenizer(config)
    cargador, _ = build_dataloaders(config, tokenizer)
    procesador, collator = cargador.dataset.processor, cargador.collate_fn

    acumulacion = config.gradient_accumulation_steps
    lotes = contar_lotes(Path(data_config).with_name("data.lst"), procesador, cfg)
    pasos = max(1, lotes // acumulacion)    # una pasada justa: no se empieza otra por un lote suelto
    guardar_cada = math.ceil(pasos / epocas)
    if estado["paso"] and (estado["total"], estado["guardar_cada"]) != (pasos, guardar_cada):
        raise SystemExit(f"El entrenamiento a medias era de {estado['total']} pasos y ahora salen {pasos}: han "
                         f"cambiado los datos o los parámetros. Vuelve a los de antes o borra {salida}.")
    config.steps, config.save_steps = pasos, guardar_cada
    estado["total"], estado["guardar_cada"] = pasos, guardar_cada
    avisar(f"{lotes} lotes en la pasada → {pasos} pasos de optimizador, un checkpoint cada {guardar_cada}")
    lotes_eval = lotes_evaluacion(ejemplos_eval, tokens, procesador, collator, config.batch_tokens,
                                  semilla=config.seed)

    if estado["paso"]:
        from peft import set_peft_model_state_dict
        from safetensors.torch import load_file
        set_peft_model_state_dict(modelo, load_file(str(salida / f"paso_{estado['paso']:04d}" /
                                                        "adapter_model.safetensors")))

    def escribir_estado():
        tmp = salida / "estado.json.tmp"
        tmp.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, salida / "estado.json")

    class Registro(tr.TrainLogger):
        def log_metrics(self, step, metrics):
            super().log_metrics(step, metrics)
            with (salida / "registro.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps({"paso": step, **{k.split("/")[-1]: v for k, v in metrics.items()}}) + "\n")

    class Entrenador(tr.OmniTrainer):
        def save_checkpoint(self, step):
            nombre = f"paso_{step:04d}"
            if nombre in estado["checkpoints"]:     # el guardado final repite el último si cae en múltiplo
                return
            dir_local = local / nombre
            self.accelerator.unwrap_model(self.model).save_pretrained(str(dir_local))
            self.config.save_to_json(str(dir_local / "train_config.json"))
            destino = salida / nombre
            destino.mkdir(exist_ok=True)
            for f in ("adapter_config.json", "adapter_model.safetensors", "train_config.json"):
                shutil.copy(dir_local / f, destino / f)
            _guardar_pt({"paso": step, "opt": self.optimizer.state_dict(),
                         "sched": self.lr_scheduler.state_dict()}, salida / "reanudar.pt")
            ev = evaluar(self.model, lotes_eval, self.accelerator.device)
            estado["paso"] = step
            estado["checkpoints"][nombre] = ev
            escribir_estado()
            avisar(f"  guardado {nombre} · pérdida de evaluación {ev}")

    tr.TrainLogger = Registro
    entrenador = Entrenador(model=modelo, config=config, train_dataloader=cargador, eval_dataloader=None,
                            tokenizer=tokenizer)
    if estado["paso"]:
        o = torch.load(salida / "reanudar.pt", weights_only=False)
        if o["paso"] != estado["paso"]:
            raise SystemExit(f"reanudar.pt es del paso {o['paso']} y estado.json del {estado['paso']}.")
        entrenador.optimizer.load_state_dict(o["opt"])
        entrenador.lr_scheduler.load_state_dict(o["sched"])
        entrenador.global_step = estado["paso"]
        entrenador.train_dataloader = SaltarLotes(cargador, estado["paso"] * acumulacion)
        avisar(f"Reanudo desde el paso {estado['paso']} de {pasos}.")
    elif "paso_0000" not in estado["checkpoints"]:
        estado["checkpoints"]["paso_0000"] = evaluar(entrenador.model, lotes_eval, entrenador.accelerator.device)
        escribir_estado()
        avisar(f"Pérdida de evaluación sin entrenar: {estado['checkpoints']['paso_0000']}")

    t0 = time.time()
    try:
        entrenador.train()
    finally:
        tr.TrainLogger = Registro.__mro__[1]
    avisar(f"Entrenamiento terminado en {(time.time() - t0) / 60:.0f} min.")
    del entrenador, modelo, cargador
    gc.collect()
    torch.cuda.empty_cache()
    return estado
