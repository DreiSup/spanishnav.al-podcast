# Conclusiones de la investigación de optimización (12-nov)

Workflow de investigación parado a medias por lento: terminaron los 7 frentes (qwen, revisión, colab, lora, trabajo,
calidad, fuera) y se verificaron con tres lentes (ahorro, calidad, viabilidad) las propuestas de qwen, revisión y lora.
Las de colab, trabajo, calidad y fuera **no se verificaron**: se citan como hipótesis. Todas las cifras de ahorro son
estimaciones salvo donde dice «medido».

## 1. Dónde está el gasto que queda

- **Fábrica**: poco. 137–138 en marcha; 160 (~65 min reales, sin generar); regenerar invitados (~76 min reales en
  070/071/131/132 + el 160). Ritmo medido 0,58–0,75 s de T4 por s de audio. Total ≈ 6–10 u.
- **LoRA de los 6 invitados**: el 80–90 % del Colab pendiente.
  - 01 medido en Ridley: 49 min de T4 para 47 min de audio (400/400).
  - **03 medido: ~36–38 min de medida por voz** (Nivi, Brett, Deutsch, y Ridley va a ~5,2 s/clip), unos 40 min con carga.
    No los ~15 que decía estado.md.
  - 04: ~10 min de entrenamiento en L4 y una prueba de escucha frase a frase que cuesta lo mismo o más (Deutsch: 10 min
    de entrenamiento y 33 de prueba).
- **El coste dominante ya no es la GPU, es la escucha del autor**: ≈ 1.280 min (~21 h) por escuchar. En 51 masters
  escuchados hubo un solo hallazgo (009, acento inglés en nombres).
- 100 u ≈ 10 USD: optimizar el motor apenas ahorra dinero; lo que importa es el tiempo de reloj y el del autor.

## 2. Qué se adopta (ordenado por valor)

1. **No escuchar 070, 071, 131 ni 132 hasta regenerarlos** con su LoRA, y **no generar el 160** hasta que hodak, rauch y
   scholl estén elegidos o descartados (comprobar antes que el 160 no esté ya generado). Ahorra horas de escucha y
   ~0,9 u. Coste cero.
2. **Regenerar por grupos según estén listas las voces**, no todo al final. Ridley sirve de prueba de la receta: 070/071
   regenerados y escuchadas solo las intervenciones de Matt antes de pagar el 04 de las demás. Antes de cada
   regeneración, listar qué clips cambian de firma (script local, solo lectura): si sale alguno de naval o nivi, parar.
3. **01 con N por voz en vez de 400** (solo voces sin empezar). Ahorra ~50–85 min de T4. Condiciones:
   - N = objetivo × 60 / duración media de los clips que pasan / tasa de paso × 1,2–1,25, con los datos reales del 03
     de Ridley;
   - antes, simulación sin GPU sobre los `medidas.jsonl` de nivi, brett y deutsch: llegar al objetivo y que la
     similitud media de los elegidos baje ≤ 0,02;
   - **Qureshi se queda en 400**: con solo 11 min de objetivo, la selección por similitud es lo que más le ayuda;
   - si el 03 avisa de que faltan minutos, se relanza el 01 con N mayor (la semilla va por índice: sigue donde iba).
4. **Prueba de escucha del 04 en lote**, como la fábrica: ~8 min menos de L4 por voz. Cambia el audio de las muestras
   frente a las pruebas de Nivi, Brett y Deutsch (más fiel a producción); el autor debe aceptarlo.
5. **Master**: no rehacerlo si no ha cambiado ningún clip (medido: ~180 s tirados el 11-nov) y medir con `ebur128` +
   `volume` en vez de dos pasadas de `loudnorm` (medido en local: 4× más rápido; ~110 s por hora de audio). Registrar si
   loudnorm cayó en modo dinámico.
6. **Leer la tarifa real** de T4 y L4 en «Ver recursos» y el saldo antes/después de una sesión: 0 u, corrige todas las
   cuentas (voces.json dice T4 1,96 / L4 4,82; fuentes de 2026 dicen 1,19 / 1,71).

## 3. Qué se aplaza o descarta

- **03 con Whisper turbo por segmentos**: ahorraría ~30 min por voz, pero en el 03 no hay escucha detrás y lo que se
  cuele entra al entrenamiento del LoRA. La regla de cola (SOBRA_MAX 0,8) está a ~0,2 s de la línea base de Chatterbox
  (~0,6 s) y calibrada con marcas por palabra. Solo tras revalidar con los 400 clips de Brett (~0,1 u): < 3 % de cambios
  y ningún clip rechazado por la cola que ahora pase. Alternativa más segura: turbo con marcas por palabra en lotes.
- **Una sola sesión para el 01 y el 03**: no se instala. El entorno de Chatterbox (torch 2.6, transformers 5.2) rompe
  speechbrain/ECAPA. Como mucho dos sesiones: A = 01 de todas las voces pendientes; B = 03 de las que estén.
- **Una sola sesión L4 para los 6 LoRA**: obliga a esperar a la última voz (retrasa días a Ridley), solo ahorra
  ~15–20 min de arranque y arriesga contaminar una voz con la anterior si el PEFT no se desmonta bien. Descartada.
- **Motor de Qwen (lotes de 32, bucle propio del sub-talker, grafos CUDA, LoRA fusionado)**: el paso está limitado por
  CPU y lanzamientos de kernels (~0,41 s por paso, casi igual con lote 5 que con 16), así que habría margen. Pero con lo
  poco que queda de fábrica el ahorro neto es 0–1 u y casi todas cambian el audio. Solo si hubiera regeneraciones
  grandes. Base de código si algún día: faster-qwen3-tts 0.3.2 + BatchedEngine de qwen3-tts-triton 0.3.0.
- **Pasar el 01/03 a L4**: solo si la aceleración medida de Chatterbox en L4 supera el cociente de tarifas.
- **Whisper en lotes de 16, solapar Whisper con Qwen, normalización de la revisión**: < 1–4 % cada una.

## 4. Sin verificar, para otra vuelta si interesa

- Escucha dirigida: el autor escucha solo los tramos de riesgo de cada master. Un filtro de texto trivial (mayúsculas a
  mitad de frase, grafías inglesas) marcaba las 8 frases del fallo del 009 y dejaba fuera el ~76 % del episodio.
- Indicador de acento barato (identificación de idioma) validado con las escuchas ya puntuadas.
- Guardarraíl objetivo (`fabrica/guardarrail.py`) para comparar dos versiones de las mismas frases con umbral A/A.
- Sacar el 01/03 a la GTX 1650 local si faltaran unidades.
