"""LoRA de Qwen3-TTS-12Hz-1.7B-Base en modo solo timbre (x-vector), para el cuaderno 04_lora_qwen.

Entrenador propio, basado en el de Alexandria (`app/train_lora.py`), porque el oficial convierte el
modelo en `custom_voice` y rompe la clonación. Cambios respecto a Alexandria (ver
piloto/investigacion-lora.md):

- referencia por ejemplo: cada clip lleva el x-vector de OTRO clip de la misma voz;
- idioma por ejemplo: token de idioma "english" o "spanish" en el prefijo, como en la inferencia;
- el EOS se entrena: la última posición de audio predice `codec_eos`, igual que el SFT oficial;
- la pérdida del sub-talker se calcula a mano, sin el doble desplazamiento de `forward_finetune`.

La entrada replica la que `generate` construye en modo x-vector y `non_streaming_mode=True`.
"""
import json
import random

import librosa
import numpy as np
import soundfile as sf
import torch
import torch.nn.functional as F

IDIOMAS = {"en": "english", "es": "spanish"}
PESO_SUB = 0.3   # el del SFT oficial y Alexandria


def texto_asistente(texto):
    # El mismo que Qwen3TTSModel._build_assistant_text
    return f"<|im_start|>assistant\n{texto}<|im_end|>\n<|im_start|>assistant\n"


# ---------------------------------------------------------------- datos

def leer_jsonl(ruta):
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def asignar_referencias(ejemplos, semilla, clave="grupo_ref"):
    """A cada ejemplo, la ruta de otro clip de su mismo grupo (misma voz y, si se puede, misma fuente)."""
    rng = random.Random(semilla)
    grupos = {}
    for e in ejemplos:
        grupos.setdefault(e[clave], []).append(e["audio"])
    for e in ejemplos:
        otros = [a for a in grupos[e[clave]] if a != e["audio"]]
        e["ref"] = rng.choice(otros)
    return ejemplos


def mezcla_por_epoca(ingles, espanol, frac_es, epocas, semilla):
    """Orden de entrenamiento: en cada época todo el español y un subconjunto del inglés, elegido al azar,
    de modo que el español sea `frac_es` de los minutos. Con dos épocas se ve casi todo el inglés."""
    rng = random.Random(semilla)
    min_es = sum(e["segundos"] for e in espanol)
    objetivo_en = min_es * (1 - frac_es) / frac_es if frac_es < 1 else 0
    orden = []
    for _ in range(epocas):
        en = ingles[:]
        rng.shuffle(en)
        elegidos, acum = [], 0.0
        for e in en:
            if acum >= objetivo_en:
                break
            elegidos.append(e)
            acum += e["segundos"]
        epoca = elegidos + espanol
        rng.shuffle(epoca)
        orden.append(epoca)
    return orden


def audio_24k(ruta):
    a, _ = librosa.load(str(ruta), sr=24000, mono=True)
    return a.astype(np.float32)


def xvector(hf, ruta):
    """El x-vector que usaría generate_voice_clone con esa referencia (24 kHz, mismos mels)."""
    from qwen_tts.core.models.modeling_qwen3_tts import mel_spectrogram
    mels = mel_spectrogram(torch.from_numpy(audio_24k(ruta)).unsqueeze(0), n_fft=1024, num_mels=128,
                           sampling_rate=24000, hop_size=256, win_size=1024, fmin=0, fmax=12000).transpose(1, 2)
    with torch.no_grad():
        e = hf.speaker_encoder(mels.to(hf.device).to(hf.dtype))[0]
    return e.float().cpu().clone()


def codificar(hf, ruta):
    """Códigos 12 Hz × 16 grupos del clip, a su frecuencia original (el tokenizador remuestrea)."""
    a, sr = sf.read(str(ruta), dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    with torch.no_grad():
        return hf.speech_tokenizer.encode(a, sr=sr).audio_codes[0].cpu().long()


def tokenizar(processor, texto):
    ids = processor(text=texto_asistente(texto), return_tensors="pt", padding=True)["input_ids"]
    return (ids if ids.dim() == 2 else ids.unsqueeze(0)).cpu()


def preparar(hf, processor, ejemplos, cache, avisar=print):
    """Calcula códigos, x-vectors y tokens de texto una sola vez y los guarda en `cache` (un .pt en Drive).
    Si se corta, lo ya calculado no se repite."""
    hecho = torch.load(cache, weights_only=False) if cache.exists() else {"codigos": {}, "xvec": {}}
    pendientes = [e for e in ejemplos if e["audio"] not in hecho["codigos"]]
    for n, e in enumerate(pendientes, 1):
        hecho["codigos"][e["audio"]] = codificar(hf, e["audio"])
        if n % 50 == 0 or n == len(pendientes):
            torch.save(hecho, cache)
            avisar(f"  códigos: {n}/{len(pendientes)}")
    refs = sorted({e["ref"] for e in ejemplos} - set(hecho["xvec"]))
    for r in refs:
        hecho["xvec"][r] = xvector(hf, r)
    if refs:
        torch.save(hecho, cache)
        avisar(f"  x-vectors: {len(refs)}")
    for e in ejemplos:
        e["codigos"] = hecho["codigos"][e["audio"]]
        e["spk"] = hecho["xvec"][e["ref"]]
        e["text_ids"] = tokenizar(processor, e["texto"])
    return ejemplos


# ---------------------------------------------------------------- entrada y pérdida

def construir_entrada(hf, talker, ej):
    """Secuencia de teacher forcing de un ejemplo, idéntica al prefill de generate (x-vector, non-streaming)
    seguida de los códigos reales.

    Devuelve (embeds [1, P+T, D], etiquetas codec-0 [1, P+T+1], códigos [T, G], P). La etiqueta extra del
    final es codec_eos: la predice la última posición de audio.
    """
    cfg, tc = hf.config, hf.config.talker_config
    dev = talker.device
    codigos = ej["codigos"].to(dev)
    text_ids = ej["text_ids"].to(dev)
    emb_codec = talker.get_input_embeddings()
    emb_texto = lambda ids: talker.text_projection(talker.get_text_embeddings()(ids))
    tid = lambda lista: torch.tensor([lista], device=dev, dtype=torch.long)

    tts_bos, tts_eos, tts_pad = emb_texto(tid([cfg.tts_bos_token_id, cfg.tts_eos_token_id,
                                                cfg.tts_pad_token_id])).chunk(3, dim=1)
    idioma = tc.codec_language_id[IDIOMAS[ej["idioma"]]]
    prefijo = emb_codec(tid([tc.codec_think_id, tc.codec_think_bos_id, idioma, tc.codec_think_eos_id]))
    spk = ej["spk"].to(dev, prefijo.dtype).view(1, 1, -1)
    codec = torch.cat([prefijo, spk, emb_codec(tid([tc.codec_pad_id, tc.codec_bos_id]))], dim=1)

    rol = emb_texto(text_ids[:, :3])                                   # <|im_start|>assistant\n
    cabeza = torch.cat([tts_pad.expand(-1, codec.shape[1] - 2, -1), tts_bos], dim=1) + codec[:, :-1]
    contenido = text_ids[:, 3:-5]
    texto = torch.cat([emb_texto(contenido), tts_eos], dim=1) + emb_codec(
        torch.full((1, contenido.shape[1] + 1), tc.codec_pad_id, device=dev, dtype=torch.long))
    fin = tts_pad + emb_codec(tid([tc.codec_bos_id]))
    prefill = torch.cat([rol, cabeza, texto, fin], dim=1)
    P = prefill.shape[1]

    # Cada paso de audio: suma de los 16 grupos + tts_pad (trailing_text_hidden en non-streaming)
    grupos = [emb_codec(codigos[:, :1])]
    for g in range(1, tc.num_code_groups):
        grupos.append(talker.code_predictor.get_input_embeddings()[g - 1](codigos[:, g:g + 1]))
    audio = torch.cat(grupos, dim=1).sum(dim=1) + tts_pad.squeeze(0)

    T = codigos.shape[0]
    etiquetas = torch.full((1, P + T + 1), -100, device=dev, dtype=torch.long)
    etiquetas[0, P:P + T] = codigos[:, 0]
    etiquetas[0, P + T] = tc.codec_eos_token_id
    return torch.cat([prefill, audio.unsqueeze(0)], dim=1), etiquetas, codigos, P


def perdida_sub(talker, codigos, ocultos):
    """Pérdida de los grupos 1–15 sin el doble desplazamiento: los logits de forward_finetune ya están
    alineados con codigos[:, 1:], así que se usa cross_entropy directa."""
    embs = [ocultos.unsqueeze(1), talker.get_input_embeddings()(codigos[:, :1])]
    for i in range(1, talker.config.num_code_groups - 1):
        embs.append(talker.code_predictor.get_input_embeddings()[i - 1](codigos[:, i:i + 1]))
    logits = talker.code_predictor.forward_finetune(inputs_embeds=torch.cat(embs, 1), labels=None).logits.float()
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)), codigos[:, 1:].reshape(-1))


def perdida(hf, talker, ej):
    """(total, codec-0, sub) de un ejemplo. `talker` es el talker con el LoRA ya aplicado (sin envolver)."""
    embeds, etiquetas, codigos, P = construir_entrada(hf, talker, ej)
    T = codigos.shape[0]
    h = talker.model(inputs_embeds=embeds, use_cache=False).last_hidden_state
    logits = talker.codec_head(h).float()                       # [1, P+T, V]
    l0 = F.cross_entropy(logits[0], etiquetas[0, 1:], ignore_index=-100)
    lsub = perdida_sub(talker, codigos, h[0, P - 1:P + T - 1])   # el oculto que predijo cada frame
    return l0 + PESO_SUB * lsub, l0, lsub


def evaluar(hf, talker, ejemplos):
    talker.eval()
    tot = {"en": [], "es": []}
    with torch.no_grad():
        for e in ejemplos:
            tot[e["idioma"]].append(perdida(hf, talker, e)[0].item())
    talker.train()
    return {k: round(float(np.mean(v)), 4) for k, v in tot.items() if v}


# ---------------------------------------------------------------- bucle de entrenamiento

def entrenar(hf, peft_talker, orden, eval_ej, salida, lr, accum, guardar_cada, calentamiento=10, avisar=print):
    """Entrena con `orden` (lista de épocas, cada una lista de ejemplos), batch 1 y acumulación `accum`.

    Cada `guardar_cada` pasos de optimizador (y al final) deja en `salida/`:
      paso_NNNN/      el adaptador (adapter_config.json + adapter_model.safetensors)
      optim.pt        optimizador y planificador, para reanudar
      estado.json     último paso guardado y pérdidas de evaluación de cada checkpoint
      registro.jsonl  la pérdida media de cada paso
    Si `salida/estado.json` existe, reanuda desde ese paso: lo ya entrenado no se repite.
    """
    import math
    import time
    from peft import set_peft_model_state_dict
    from safetensors.torch import load_file

    base = peft_talker.base_model.model
    salida.mkdir(parents=True, exist_ok=True)
    plano = [e for epoca in orden for e in epoca]
    total = math.ceil(len(plano) / accum)
    params = [p for p in peft_talker.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / calentamiento))

    estado = {"paso": 0, "total": total, "checkpoints": {}}
    if (salida / "estado.json").exists():
        estado = json.loads((salida / "estado.json").read_text(encoding="utf-8"))
        if estado["paso"] >= total:
            avisar(f"Ya estaba terminado ({total} pasos). Nada que hacer.")
            return estado
        ultimo = salida / f"paso_{estado['paso']:04d}"
        set_peft_model_state_dict(peft_talker, load_file(str(ultimo / "adapter_model.safetensors")))
        o = torch.load(salida / "optim.pt", weights_only=False)
        opt.load_state_dict(o["opt"])
        sched.load_state_dict(o["sched"])
        avisar(f"Reanudo desde el paso {estado['paso']} de {total}.")

    def guardar(paso):
        nombre = f"paso_{paso:04d}"
        peft_talker.save_pretrained(str(salida / nombre))
        torch.save({"opt": opt.state_dict(), "sched": sched.state_dict()}, salida / "optim.pt")
        ev = evaluar(hf, base, eval_ej)
        estado["paso"] = paso
        estado["checkpoints"][nombre] = ev
        (salida / "estado.json").write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
        avisar(f"  guardado {nombre} · pérdida de evaluación {ev}")

    if estado["paso"] == 0 and "paso_0000" not in estado["checkpoints"]:
        estado["checkpoints"]["paso_0000"] = evaluar(hf, base, eval_ej)
        avisar(f"Pérdida de evaluación sin entrenar: {estado['checkpoints']['paso_0000']}")

    base.train()
    t0 = time.time()
    hechos_aqui = 0
    for paso in range(estado["paso"] + 1, total + 1):
        lote = plano[(paso - 1) * accum:paso * accum]
        suma = {"total": 0.0, "codec0": 0.0, "sub": 0.0}
        validos = 0
        for e in lote:
            try:
                tot, l0, ls = perdida(hf, base, e)
                (tot / len(lote)).backward()
            except torch.cuda.OutOfMemoryError:
                opt.zero_grad(set_to_none=True)
                torch.cuda.empty_cache()
                avisar(f"  sin memoria con {e['audio']} ({e['segundos']:.1f} s): lo salto")
                continue
            suma["total"] += tot.item()
            suma["codec0"] += l0.item()
            suma["sub"] += ls.item()
            validos += 1
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        sched.step()
        opt.zero_grad(set_to_none=True)
        hechos_aqui += 1
        fila = {"paso": paso, **{k: round(v / max(validos, 1), 4) for k, v in suma.items()},
                "lr": sched.get_last_lr()[0], "idiomas": "".join(e["idioma"][0] for e in lote)}
        with (salida / "registro.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(fila) + "\n")
        if paso % 5 == 0 or paso == total:
            resta = (time.time() - t0) / hechos_aqui * (total - paso) / 60
            avisar(f"paso {paso}/{total} · pérdida {fila['total']:.3f} (codec-0 {fila['codec0']:.3f}, "
                   f"sub {fila['sub']:.3f}) · quedan ~{resta:.0f} min")
        if paso % guardar_cada == 0 or paso == total:
            guardar(paso)
    avisar(f"Entrenamiento terminado en {(time.time() - t0) / 60:.0f} min.")
    return estado
