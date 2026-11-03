# Fábrica de voz

El paso 3 del flujo de `CLAUDE.md`: de un `transcript.es.json` a un clip de audio por intervención en
Drive, listo para Audacity.

| Fichero | Qué es |
|---|---|
| `voces.json` | **La configuración.** Qué referencia y qué LoRA usa cada hablante, alias de nombres, la regla de Kapil (en sus episodios Naval usa `naval_kapil`), la pausa de cada voz (0,12 s por defecto), la verificación con Whisper y las rutas de Drive |
| `fabrica.py` | La lógica: plan del episodio, carpeta en Drive, generación de cada intervención en lotes de frases (`motor.lote`, 8) con revisión de Whisper y reintentos, tope de duración por frase, recorte de pausas, informe y borrador. `MotorQwen` carga Qwen3-TTS base con un adaptador por voz |
| `construir_cuaderno.py` → `fabrica.ipynb` | El cuaderno de Colab (generado: se edita el `.py` y se regenera) |

## Uso

1. Abre `fabrica/fabrica.ipynb` en Colab con T4 (o L4):
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
- **Otra referencia:** cambia `ref`. Puede ser una ruta o una lista de rutas: con varias, la fábrica usa la media de
  sus huellas (como `lora_ref_es5` del cuaderno 08).
- **Probar una voz en un episodio sin tocar los clips buenos:** en la celda 2, `SUBCARPETA = "prueba_…"` manda
  todo a `<episodio>/prueba_…/`. `REF_ES_NAVAL = 1` (o 5) cambia, solo para esa ejecución, la referencia de Naval
  por su mejor clip en español (o la media de 5), como `lora_ref_es1` y `lora_ref_es5` del cuaderno 08.
- **Otro ritmo para una voz:** añade `"pausa_max"` a su entrada (Brett lleva 0,30); si no lo tiene, usa el
  general de `ritmo` (0,12).
- **Hablante nuevo:** añade una entrada en `voces` (y en `alias` si el transcript lo escribe de otra forma).
  Si un transcript trae un hablante que no está, la celda 3 lo dice antes de gastar nada.

## Coste

Primera prueba (2-nov, 044, L4, frase a frase): **4,58 s de GPU por segundo de audio**, unas 22 unidades por hora
de audio. Casi todo es Qwen esperando entre pasos pequeños, no Whisper ni los reintentos (ninguno en el 044).
Desde el 2-nov las frases de cada intervención se generan en lotes (`motor.lote`) y cada frase lleva un tope
de pasos proporcional a su texto (`tope_pasos`), para que una alucinación no llegue a 164 s. La celda 5 imprime
la cifra nueva al acabar.

Con lotes en T4 (2-nov, 037–039, 10,6 min de audio): **unos 2–2,8 s de GPU por segundo de audio** (calculado con
las horas de los ficheros en Drive; el 038 tuvo 7 reintentos). Whisper no cabe en la T4 con lotes de 4 junto a
Qwen y baja solo a 2. Con la T4 a unas 2 unidades por hora, **unas 5 unidades por hora de audio**, frente a 22
antes.
