"""Medidas para filtrar el español sintético del piloto: WER con Whisper y similitud con ECAPA.

Whisper va por transformers y no por faster-whisper: Colab trae CUDA 13 y CTranslate2 pide
CUDA 12. El audio se carga a mano por el mismo motivo (el lector de faster-whisper no casa
con el PyAV de Colab).
"""
import json
import re
import unicodedata

import jiwer
import librosa
import numpy as np
import soundfile as sf


def _cifras_a_letras(texto):
    # Whisper escribe "8" o "1.000"; las frases llevan los números en letra
    try:
        from num2words import num2words
    except ImportError:
        return texto
    texto = re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", texto)
    texto = re.sub(r"\s*%", " por ciento", texto)   # "90%" → "90 por ciento" (las frases lo llevan en letra)
    return re.sub(r"\d+", lambda m: f" {num2words(int(m.group()), lang='es')} ", texto)


def normaliza(texto):
    # Sin tildes: Whisper a veces las omite ("que" por "qué") y eso no es un error de lectura del TTS
    texto = _cifras_a_letras(texto)
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\ba donde\b", "adonde", texto)   # «adónde» y «a dónde» se oyen igual
    return re.sub(r"\s+", " ", texto).strip()


def wer(referencia, hipotesis):
    ref, hyp = normaliza(referencia), normaliza(hipotesis)
    return jiwer.wer(ref, hyp) if hyp else 1.0


def audio_16k(ruta):
    a, sr = sf.read(str(ruta), dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    return librosa.resample(a, orig_sr=sr, target_sr=16000) if sr != 16000 else a


class Asr:
    def __init__(self, modelo="openai/whisper-large-v3", marcas="palabra"):
        """`modelo`: el de siempre, large-v3, o "openai/whisper-large-v3-turbo" (el mismo codificador con 4 capas de
        decodificador en vez de 32).

        `marcas`: "palabra" (lo de siempre) da dónde acaba la última palabra, pero para calcularlo Whisper guarda la
        atención de todas sus capas por frase (~3 GB cada una en una T4: por eso revisaba de una en una). "segmento"
        da dónde acaba el último trozo que transcribe: sin guardar atenciones, con atención rápida (sdpa) y en lotes
        grandes. Lo único que usa la fábrica es ese final, para ver si sobra algo detrás."""
        import torch
        from transformers import pipeline
        self.modelo, self.marcas = modelo, marcas
        extra = {"model_kwargs": {"attn_implementation": "sdpa"}} if marcas == "segmento" else {}
        self.p = pipeline("automatic-speech-recognition", model=modelo,
                          torch_dtype=torch.float16, device="cuda:0", chunk_length_s=30, **extra)
        self._ts = "word" if marcas == "palabra" else True

    def transcribe(self, ruta):
        """Devuelve (texto, inicio, fin): cuándo empieza la primera palabra y acaba la última.

        Con eso se detecta lo que el WER no ve: murmullos, sílabas o ruido antes o después de la
        frase, que Whisper suele omitir en el texto.
        """
        return self.transcribe_audio(audio_16k(ruta), 16000)

    def transcribe_audio(self, audio, sr):
        """Como transcribe(), con el audio ya en memoria (mono, float32)."""
        a = np.asarray(audio, dtype=np.float32)
        if sr != 16000:
            a = librosa.resample(a, orig_sr=sr, target_sr=16000)
        salida = self.p({"raw": a, "sampling_rate": 16000}, return_timestamps=self._ts,
                        generate_kwargs={"language": "spanish", "task": "transcribe"})
        marcas = [c["timestamp"] for c in salida.get("chunks", []) if c.get("timestamp")]
        inicio = next((t[0] for t in marcas if t[0] is not None), None)
        fin = next((t[1] for t in reversed(marcas) if t[1] is not None), None)
        return salida["text"].strip(), inicio, fin

    def transcribe_lote(self, audios, sr, batch_size=4):
        """transcribe_audio de varios audios en una pasada de Whisper.

        Si la GPU se queda sin memoria, libera y lo intenta con lotes más pequeños hasta llegar a uno a uno, y
        recuerda el tamaño que cupo para las siguientes llamadas. El reintento va fuera del `except`: dentro, la
        excepción aún retiene la memoria del intento fallido.
        """
        import gc
        import torch
        batch_size = min(batch_size, getattr(self, "lote_que_cabe", batch_size))
        if sr != 16000:
            audios = [librosa.resample(np.asarray(a, dtype=np.float32), orig_sr=sr, target_sr=16000) for a in audios]
        audios = [np.asarray(a, dtype=np.float32) for a in audios]
        while True:
            fallo = None
            try:
                # Diccionarios nuevos en cada intento: el pipeline les quita "raw" y "sampling_rate" al leerlos
                entradas = [{"raw": a, "sampling_rate": 16000} for a in audios]
                salidas = self.p(entradas, batch_size=batch_size, return_timestamps=self._ts,
                                 generate_kwargs={"language": "spanish", "task": "transcribe"})
                salidas = list(salidas)
                break
            except torch.cuda.OutOfMemoryError:
                fallo = batch_size
            gc.collect()
            torch.cuda.empty_cache()
            if fallo == 1:
                raise torch.cuda.OutOfMemoryError("Whisper no cabe en la GPU ni con una frase")
            batch_size = max(1, fallo // 2)
            self.lote_que_cabe = batch_size
            print(f"  (Whisper sin memoria con {fallo} a la vez; pruebo con {batch_size} y sigo así)")
        res = []
        for salida in salidas:
            marcas = [c["timestamp"] for c in salida.get("chunks", []) if c.get("timestamp")]
            inicio = next((t[0] for t in marcas if t[0] is not None), None)
            fin = next((t[1] for t in reversed(marcas) if t[1] is not None), None)
            res.append((salida["text"].strip(), inicio, fin))
        return res


class Ecapa:
    def __init__(self):
        from speechbrain.inference.speaker import EncoderClassifier
        self.m = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                                                savedir="/content/ecapa", run_opts={"device": "cuda"})

    def embed(self, ruta):
        import torch
        sig = torch.from_numpy(audio_16k(ruta)).unsqueeze(0)
        with torch.no_grad():
            e = self.m.encode_batch(sig.to("cuda")).squeeze()
        return e / e.norm()

    def referencia(self, rutas):
        import torch
        m = torch.stack([self.embed(r) for r in rutas]).mean(0)
        return m / m.norm()

    def similitud(self, ruta, ref):
        return float((self.embed(ruta) * ref).sum())


def cargar(ruta):
    """Lee un .jsonl de medidas como {(variante, id): fila}."""
    if not ruta.exists():
        return {}
    filas = (json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip())
    return {(f["variante"], f["id"]): f for f in filas}


def anadir(ruta, fila):
    with ruta.open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def duracion(ruta):
    return sf.info(str(ruta)).duration
