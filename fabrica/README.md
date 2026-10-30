# Fábrica de voz

El paso 3 del flujo de `CLAUDE.md`: de un `transcript.es.json` a un clip de audio por intervención en
Drive, listo para Audacity.

| Fichero | Qué es |
|---|---|
| `voces.json` | **La configuración.** Qué referencia y qué LoRA usa cada hablante, alias de nombres, la regla de Kapil (en sus episodios Naval usa `naval_kapil`), la pausa (0,12 s), la verificación con Whisper y las rutas de Drive |
| `fabrica.py` | La lógica: plan del episodio, carpeta en Drive, generación frase a frase con revisión y reintentos, recorte de pausas, informe y borrador. `MotorQwen` carga Qwen3-TTS base con un adaptador por voz |
| `construir_cuaderno.py` → `fabrica.ipynb` | El cuaderno de Colab (generado: se edita el `.py` y se regenera) |

## Uso

1. Abre `fabrica/fabrica.ipynb` en Colab con L4:
   `https://colab.research.google.com/github/DreiSup/spanishnav.al-podcast/blob/claude/quirky-dirac-x18c3n/fabrica/fabrica.ipynb`
2. Celda 1 y reiniciar sesión. En la celda 2, la lista de `EPISODIOS` (carpetas de `episodios/` del repo).
3. La celda 3 comprueba todo sin cargar modelos: transcript, voces, referencias y adaptadores. Si dice
   `RESULTADO: REVISAR`, no sigas.
4. El resto en orden. Salida, por episodio, en `naval-podcast/transcripts/<año>/<NNN Título>/`:
   - `tts/001naval.wav`, `tts/002nivi.wav`… — los clips, en el orden del transcript;
   - `informe_tts.md` — clips, reintentos y **frases sospechosas con el segundo exacto**: empieza por ahí
     en Audacity;
   - `borrador_tts.wav` — todos los clips seguidos, para una escucha rápida;
   - `registro_tts.jsonl` — el detalle de cada frase.

Lo que ya está en `tts/` no se repite. Para rehacer un clip, bórralo y relanza.

## Cambiar una voz

Todo se cambia en `voces.json`, sin tocar código:

- **Nuevo LoRA** (por ejemplo, cuando se entrene Nivi): pon en `adaptador` la carpeta del checkpoint elegido,
  relativa a `rutas.voces`. `null` = Qwen base.
- **Otra referencia:** cambia `ref`.
- **Hablante nuevo:** añade una entrada en `voces` (y en `alias` si el transcript lo escribe de otra forma).
  Si un transcript trae un hablante que no está, la celda 3 lo dice antes de gastar nada.
