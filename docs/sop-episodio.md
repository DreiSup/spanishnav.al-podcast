# SOP: de la traducción al audio final

Decidido por el autor el 4-nov: **los episodios no pasan por Audacity por defecto.** La fábrica entrega el audio
final; el autor lo escucha cuando puede y solo lo arregla si oye algo mal. Audacity es la excepción, no un paso.

## 1. Traducción

La sesión de traducción sube el episodio a la rama `claude/quirky-dirac-x18c3n` con cero avisos del normalizador
(`docs/prompt-sesion-traduccion.md`). Estado en `metadata.es.json`: `revision`.

## 2. Fábrica (Colab, T4)

`fabrica/fabrica.ipynb`, con los episodios en la celda 2 y `SOLO_MASTER = False`, `RONDA = 0`,
`REF_ES_NAVAL = 0`, `SUBCARPETA = ""`. Coste: unos 2–2,5 s de T4 por segundo de audio (unas 5 unidades por hora de
audio). Si se corta, se relanza: lo hecho no se repite.

Deja en `naval-podcast/transcripts/<año>/<NNN Título>/`:

| Fichero | Qué es |
|---|---|
| `audio/<NNN>-<slug>.mp3` | **El master**: todas las intervenciones seguidas, en el orden del transcript, con 0,6 s entre una y otra, a -16 LUFS (pico -1,5 dB), MP3 mono 44,1 kHz 128 kbps, con el título en español en las etiquetas |
| `informe_tts.md` | En qué minuto del master empieza cada intervención y, si las hay, las frases **sospechosas** con su minuto |
| `tts/001naval.wav`… | Una intervención por fichero. Solo hacen falta para arreglar algo |
| `registro_tts.jsonl` | El detalle de cada frase: texto, intentos, lo que oyó Whisper y con qué voz se hizo |

Estado: `tts`.

## 3. Control de calidad: escuchar el master

1. Abre `informe_tts.md`. Si hay frases sospechosas, escucha primero esos minutos.
2. Escucha el master entero cuando puedas. Busca: **alucinaciones** (palabras que no están en el texto, repeticiones,
   murmullos), **sonidos raros**, **silencios largos**, y pronunciaciones que chirríen.
3. Si todo está bien: el episodio está **listo**. Estado `montaje` (pasa a vídeo y publicación). Fin.
4. Si algo está mal, apunta el minuto y elige uno de los arreglos.

## 4. Arreglos (solo si hace falta)

Mira en `informe_tts.md` qué intervención (`00Nvoz.wav`) contiene ese minuto.

**A. Regenerarla con otra semilla** (lo normal para una alucinación; no se toca ningún audio a mano):
1. Borra ese `.wav` de `tts/` en Drive.
2. Lanza la fábrica con ese episodio y `RONDA = 1` (si vuelve a salir mal, `RONDA = 2`…). Solo se genera lo que
   falta, con semillas nuevas, y se rehace el master.

**B. Arreglarla en Audacity** (un sonido o un silencio concreto):
1. Descarga ese `.wav` de `tts/`, arréglalo en Audacity y expórtalo en WAV con **el mismo nombre**.
2. Súbelo a `tts/` reemplazando el anterior.
3. Lanza la fábrica con ese episodio y `SOLO_MASTER = True`: no carga modelos ni gasta GPU (sirve un entorno sin
   GPU); solo rehace el master y el informe.
4. Pon `"audio_editado_a_mano": true` en su `metadata.es.json`: desde ahí el audio ya no se puede regenerar
   desde el texto sin perder el arreglo. Guarda el `.aup3` en `proyecto/` si lo hay.

**C. El fallo es del texto** (una frase mal traducida, una cifra, una sigla que se lee mal): se corrige en el
`transcript.es.json` del repo (sesión de traducción) y se relanza la fábrica: rehace sola las intervenciones cuyo
texto cambió.

Después del arreglo, vuelve al paso 3 solo con ese minuto.

## Pendiente de definir con el autor

- Vídeo para YouTube (`scripts/render-video.sh`, sin ejecutar nunca), título, descripción con la atribución a
  nav.al, tags y miniatura.
- Web y RSS (con la sesión de contenido).
- Si el master lleva intro o cierre (sintonía, aviso de doblaje con IA) y dónde.
