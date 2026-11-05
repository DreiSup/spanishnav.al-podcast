# Fábrica de voz

El paso 3 del flujo de `CLAUDE.md`: de un `transcript.es.json` a un clip de audio por intervención en
Drive, listo para Audacity.

| Fichero | Qué es |
|---|---|
| `voces.json` | **La configuración.** Qué referencia y qué LoRA usa cada hablante, alias de nombres, la regla de Kapil (en sus episodios Naval usa `naval_kapil`), la pausa de cada voz (0,12 s por defecto), la verificación con Whisper y las rutas de Drive |
| `fabrica.py` | La lógica: plan del episodio, carpeta en Drive, generación de cada intervención en lotes de frases (`motor.lote`, 8) con revisión de Whisper y reintentos, tope de duración por frase, recorte de pausas, master (MP3 a -16 LUFS) e informe. `MotorQwen` carga Qwen3-TTS base con un adaptador por voz |
| `localizar.py` | De un minuto del master o de un trozo de frase a la intervención y la frase que hay que rehacer |
| `construir_cuaderno.py` → `fabrica.ipynb` | El cuaderno de Colab (generado: se edita el `.py` y se regenera) |

## Uso

1. Abre `fabrica/fabrica.ipynb` en Colab con T4 (o L4):
   `https://colab.research.google.com/github/DreiSup/spanishnav.al-podcast/blob/claude/quirky-dirac-x18c3n/fabrica/fabrica.ipynb`
2. Celda 1 y reiniciar sesión. En la celda 2, la lista de `EPISODIOS` (carpetas de `episodios/` del repo).
3. La celda 3 comprueba todo sin cargar modelos: transcript, voces, referencias y adaptadores. Si dice
   `RESULTADO: REVISAR`, no sigas.
4. El resto en orden. Salida, por episodio, en `naval-podcast/transcripts/<año>/<NNN Título>/`:
   - `audio/<NNN>-<slug>.mp3` — **el master**: los clips seguidos con 0,6 s entre intervenciones, a -16 LUFS, MP3
     mono 128 kbps. Si suena bien, es el audio que se publica (`docs/sop-episodio.md`);
   - `informe_tts.md` — en qué minuto del master empieza cada clip y dónde están las **frases sospechosas**;
   - `tts/001naval.wav`, `tts/002nivi.wav`… — los clips, en el orden del transcript;
   - `registro_tts.jsonl` — el detalle de cada frase.

   Los episodios generados antes del 4-nov tienen además un `borrador_tts.wav`: lo sustituye el master.
   Arreglos tras escuchar: `REHACER_FRASES` (solo las frases que fallan; `fabrica/localizar.py` las encuentra por
   minuto o por texto), `RONDA` (otras semillas para los clips borrados de `tts/`) y `SOLO_MASTER` (rehace el master
   sin GPU tras arreglar un clip a mano). `MUESTRA = 3` genera solo las 3 primeras intervenciones de cada voz en
   `muestra/`, para probar voces nuevas. Ver `docs/sop-episodio.md`.

Lo que ya está en `tts/` no se repite. Para rehacer un clip, bórralo y relanza. **Si cambia el texto de una
intervención en el repo, o una voz en `voces.json`** (adaptador, referencia, temperatura o pausa), al relanzar el
episodio la fábrica rehace sola esos clips y deja los demás: cada clip guarda en `registro_tts.jsonl` su texto y
con qué voz se hizo.

## Cambiar una voz

Todo se cambia en `voces.json`, sin tocar código:

- **Nuevo LoRA** (por ejemplo, cuando se entrene Nivi): pon en `adaptador` la carpeta del checkpoint elegido,
  relativa a `rutas.voces`. `null` = Qwen base.
- **Temperatura:** `"temperatura"` en la entrada de la voz (Naval: 0,7). Sin ella, la de Qwen (0,9). Más baja = menos
  variación al elegir cada sonido; a Naval le quitó las erres inglesas.
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

**Registro automático (desde el 5-nov).** Cada clip guarda en `registro_tts.jsonl` su tiempo de generación y la GPU.
Con eso:

- el `informe_tts.md` de cada episodio dice cuánto tiempo de GPU y cuántas unidades ha costado, rehechos incluidos;
- `naval-podcast/coste_fabrica.jsonl` es el libro: una línea por episodio generado y una por sesión de Colab (la
  sesión incluye cargar modelos y los ratos parados, que también se pagan);
- la celda 6 rehace `naval-podcast/coste_fabrica.md`: la tabla de todos los episodios y el total. También se puede
  ejecutar sin GPU (celdas 1–3 y 6), porque solo lee Drive.

Las unidades son una estimación: tiempo × tarifa de la GPU (`voces.json`, «coste»). Si Colab muestra otra tarifa en
«Recursos», se cambia ahí y el resumen se recalcula. Los clips anteriores al 5-nov no guardan la GPU y se cuentan
como T4 (el primer 044 se hizo en una L4 y queda algo por debajo).

### Mediciones

Primera prueba (2-nov, 044, L4, frase a frase): **4,58 s de GPU por segundo de audio**, unas 22 unidades por hora
de audio. Casi todo es Qwen esperando entre pasos pequeños, no Whisper ni los reintentos (ninguno en el 044).
Desde el 2-nov las frases de cada intervención se generan en lotes (`motor.lote`) y cada frase lleva un tope
de pasos proporcional a su texto (`tope_pasos`), para que una alucinación no llegue a 164 s. La celda 5 imprime
la cifra nueva al acabar.

Con lotes en T4 (2-nov, 037–039, 10,6 min de audio): **unos 2–2,8 s de GPU por segundo de audio** (calculado con
las horas de los ficheros en Drive; el 038 tuvo 7 reintentos). Whisper no cabe en la T4 con lotes de 4 junto a
Qwen y baja solo a 2. Con la T4 a unas 2 unidades por hora, **unas 5 unidades por hora de audio**, frente a 22
antes.
