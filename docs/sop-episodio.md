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
| `indice_master.tsv` | En qué segundo del master empieza **cada frase** (clip y número de frase) |
| `tts/001naval.wav`… | Una intervención por fichero, y en `tts/frases/` cada frase aparte (`002naval_07.wav` es la frase 7). Solo hacen falta para arreglar algo |
| `registro_tts.jsonl` | El detalle de cada frase: texto, intentos, lo que oyó Whisper y con qué voz se hizo |

Estado: `tts`.

## 3. Control de calidad: escuchar el master

1. Abre `informe_tts.md`. Si hay frases sospechosas, escucha primero esos minutos.
2. Escucha el master entero cuando puedas. Busca: **alucinaciones** (palabras que no están en el texto, repeticiones,
   murmullos), **sonidos raros**, **silencios largos**, y pronunciaciones que chirríen.
3. Si todo está bien: el episodio está **listo**. Estado `montaje` (pasa a vídeo y publicación). Fin.
4. **Registro de la escucha**, en el bloque `escucha` de su `metadata.es.json` (por defecto, sin escuchar):

       "escucha": {"escuchado": true, "resultado": "bueno", "fecha": "2026-11-05", "feedback": "bien; 2:15 frase rehecha"}

   `resultado`: `bueno` (pasa a `montaje`) o `revisar` (sigue en `tts` hasta arreglarlo y volver a escucharlo).

   Lo apunta cualquier sesión cuando el autor dice «he escuchado el 003, bien» o le da feedback. La columna
   «Escuchado» de `INDICE.md` (`python3 scripts/indice.py`) muestra cuáles faltan. Escuchar no es lo mismo que
   publicar: un episodio puede estar publicado sin escuchar entero, y queda a la vista.
5. Si algo está mal, apunta el minuto y elige uno de los arreglos.

## 4. Arreglos (solo si hace falta)

**Localizar el fallo.** Basta con decirle a Claude «en el 037, minuto 1:21 falla» o «en el 037 falla la frase que
dice …». Con el texto le basta el repo; con el minuto lee el `indice_master.tsv` del episodio en Drive. Responde con la
intervención, el número de frase y la línea para la fábrica. Lo hace `fabrica/localizar.py`:

    python3 fabrica/localizar.py 2019/038-accountability --texto "noventa por ciento"
    python3 fabrica/localizar.py 2019/038-accountability --minuto 3:05 --indice indice_master.tsv
    → REHACER_FRASES = {"2019/038-accountability": {"005naval.wav": [3]}}

**A. Rehacer solo esa frase** (lo normal para una alucinación; no se toca ningún audio a mano): lanza la fábrica con
ese episodio y la línea `REHACER_FRASES` en la celda 2. Rehace esa frase con semillas nuevas (cada vez otras),
rearma la intervención con las demás frases intactas y rehace el master. Segundos de GPU. Los episodios generados
antes del 4-nov no tienen las frases guardadas aparte: la primera vez rehace la intervención entera, y desde ahí ya
va frase a frase.

**A bis. Rehacer una intervención entera:** borra su `.wav` de `tts/` y lanza la fábrica con `RONDA = 1` (o 2, 3…
para otras semillas).

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

## 5. La cola de publicación: del visto bueno al cuaderno de vídeo (8-nov)

El autor escucha cuando puede y se lo dice a la sesión de dirección («el 009 está bien», «el 011 hay que revisarlo en
el 2:15»). La sesión lo apunta en el repo, que es lo que hay detrás del tablero (https://spanishnav-tablero.vercel.app/):

1. **Escucha**: `python3 scripts/lote.py escucha <NNN> bueno|revisar "<lo que dijo el autor>"`. `bueno` → estado
   `montaje` (columna «Listo para el cuaderno»); `revisar` → sigue en `tts` con la nota.
2. **Cola**: `python3 scripts/lote.py cola` lista los listos sin fecha y los que tienen fecha.
3. **Lote**: cuando el autor aprueba el lote, `python3 scripts/lote.py programar` da fecha (uno al día, a partir del
   último programado), **en orden numérico estricto** (decisión del autor, 9-nov: se para en el primer episodio
   que aún no esté listo; los listos de detrás, como el 042, esperan su turno), escribe `publicacion` y el título y la descripción de YouTube, e imprime el `EPISODIOS` para el
   cuaderno de vídeo. Siguen en «Listo para el cuaderno» hasta que el audio está en R2.
4. El autor pasa el lote por `video/video.ipynb` (vídeo, R2, YouTube programado) y pasa a la sesión los bloques
   «Datos para la web» y «Vídeos subidos a YouTube». La sesión carga los episodios en la web y apunta los enlaces.
5. Tras cada cambio: `python3 scripts/indice.py` y `python3 scripts/tablero.py --web ../spanishnaval-web --r2`, commit y push.

Si el visto bueno es de una ronda nueva (p. ej. `ronda1/` del 009), su master tiene que estar en `audio/` antes del
cuaderno de vídeo, que solo lee `audio/<NNN>-<slug>.mp3`.
