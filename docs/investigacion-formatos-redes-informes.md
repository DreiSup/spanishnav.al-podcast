# Informes completos de los 6 investigadores (18-nov)

> Material de apoyo de `docs/investigacion-formatos-redes.md`.

## Informe 1: YouTube: vídeo largo y Shorts

# Investigador 1 de 6: YouTube, vídeo largo y Shorts

**Cómo se hizo la investigación.** WebFetch no funcionó en esta sesión. Los hosts `support.google.com`, `blog.youtube`, `ppc.land` y `argil.ai` no resuelven por la red de la sesión, así que ninguna página se abrió entera. Todo lo que sigue sale de los extractos que devuelve el buscador (WebSearch), consultados el 18-nov-2026. Cuando un dato del Centro de ayuda de YouTube aparece en esos extractos lo marco [OFICIAL]. Lo que solo dan terceros va como [TERCEROS]. Lo deducido o contradictorio va como [NO CONFIRMADO]. Algunas cifras de la tabla oficial de bitrates no aparecieron completas en los extractos: las completo de memoria y lo indico con [OFICIAL, cotejo parcial]. Para cerrar esos puntos hay que permitir `support.google.com` en la red de la sesión y volver a consultar.

## Resumen accionable

1. **Vídeo largo.** MP4 con *fast start* (moov al principio), H.264 High Profile, progresivo, VBR, 4:2:0, BT.709, GOP cerrado de la mitad del framerate: **25 fotogramas a 50 fps**. Bitrate de **12 Mbps** para 1080p50 SDR. Audio AAC-LC estéreo a **384 kbps / 48 kHz** [OFICIAL]. Sonoridad: **−14 LUFS integrados** con *true peak* ≤ −1 dBTP [TERCEROS; YouTube no publica la cifra].
2. **Subir en 1440p** (escalado desde 1080p, a 24 Mbps) para forzar VP9/AV1 es un truco de la comunidad sin respaldo oficial, y hay informes en contra. Con texto plano sobre fondo liso, 1080p nativo basta. Si se prueba, que sea una prueba A/B con un solo episodio.
3. **Duración.** Un episodio de 3-4 h no da problemas: el límite es **12 h o 256 GB**, lo que llegue antes, y la cuenta tiene que estar verificada para pasar de 15 min [OFICIAL]. 4 h a 12 Mbps son unos 21,6 GB.
4. **Shorts.** Vídeo vertical o cuadrado de ≤3 min, subido a partir del 15-oct-2024 [OFICIAL]. Lienzo de **1080×1920, 50 fps**. **Desde el 24-sep-2026** un Short nuevo de 1 a 3 min con reclamación de Content ID ya no se bloquea automáticamente (citado de la ayuda por terceros; la página en inglés de EE. UU. todavía decía lo contrario). Para este proyecto no importa: el audio es TTS propio, sin música.
5. **Zona segura de Shorts.** No hay cifra oficial. Plantilla conservadora: texto dentro de **x 48–888, y 288–1248 px** (márgenes: arriba 288, derecha 192, abajo 672, izquierda 48) [TERCEROS]. La frase actual del tambor va centrada hacia **y ≈ 760–800**, no en el centro geométrico (960).
6. **Vídeo largo, zonas del reproductor.** Conviene dejar libre el **15 % inferior, unos 160 px de 1080**, que es donde salen los controles y los CC por defecto. También la esquina inferior derecha para la marca de agua y los **últimos 20 s** para la pantalla final; un vídeo necesita ≥25 s para tener pantalla final [OFICIAL para 20 s/25 s; los px son NO CONFIRMADO].
7. **Subtítulos.** Subir un **.srt en español** generado del mismo `transcript.es.json`: UTF-8 y SRT básico, sin estilos [OFICIAL]. **Desactivar el doblaje automático**, porque doblaría al inglés un doblaje del inglés. La traducción automática de subtítulos se puede dejar activa.
8. **Shorts.** Se puede poner miniatura personalizada desde escritorio desde el 24/25-jul-2026, con despliegue gradual y, según una fuente, solo para el YPP. Sin YPP lo realista es elegir fotograma: tres sugeridos en escritorio o cualquiera en la app. Diseñar un fotograma "portada" legible dentro del Short.
9. **Vincular cada Short a su episodio** con "Vídeo relacionado", a mano en Studio de escritorio. La API de subida no lo admite [TERCEROS]. Un solo enlace por Short, a un vídeo del mismo canal.
10. **Derechos.** Según la ayuda oficial de YouTube, una traducción es obra derivada y "suele requerir permiso del titular". Sin el permiso de Naval, cada vídeo queda expuesto a una retirada por DMCA. No monetizar no cambia eso [OFICIAL].

## Tabla de especificaciones

| Parámetro | Vídeo largo 1920×1080 | Short 1080×1920 | Confianza |
|---|---|---|---|
| Contenedor | MP4, moov al inicio (*fast start*) | igual | [OFICIAL] |
| Códec de vídeo | H.264, progresivo, High Profile, 2 B-frames consecutivos, CABAC, VBR, 4:2:0 | igual | [OFICIAL] (H.264, fast start, VBR y 4:2:0 vistos en extractos; perfil y B-frames de memoria) |
| GOP | cerrado, mitad del framerate: **25 a 50 fps** (`-g 25 -bf 2 -flags +cgop`) | igual | [OFICIAL] |
| Espacio de color | BT.709: primarias, TRC y matriz; es lo que YouTube asume sin metadatos. Rango limitado (tv) | igual | [OFICIAL] |
| Framerate | el de origen (24/25/30/48/50/60); 50 fps vale | 24–60; 50 vale | [OFICIAL] / [TERCEROS] |
| Bitrate SDR | 1080p: 8 Mbps (24-30 fps) / **12 Mbps (48-60 fps)**. 1440p: 16 / 24. 4K: 35-45 / 53-68 | 1080×1920 a 50 fps: **12 Mbps** | [OFICIAL, cotejo parcial] |
| Bitrate HDR (solo como referencia) | 1080p 10/15; 1440p 20/30 | — | [OFICIAL] (son las cifras de los extractos sin cabecera) |
| Resolución máxima | hasta 8K | 1080p máx. según una guía que cita la ayuda; otras dicen 4K | [TERCEROS, contradictorio] |
| Audio | AAC-LC (también Opus); estéreo **384 kbps**, mono 128 kbps; **48 kHz** (o 96 kHz) | igual | [OFICIAL] |
| Sonoridad | −14 LUFS integrados; YouTube baja el volumen de lo más fuerte y, según la fuente, no sube lo más bajo | igual | [TERCEROS] |
| Tamaño y duración máximos | 256 GB o 12 h, lo que llegue antes. Más de 15 min requiere cuenta verificada | ≤3 min y vertical o cuadrado para que cuente como Short | [OFICIAL] |
| Miniatura | 1280×720, mínimo 640 de ancho, JPG/PNG/GIF (BMP). Peso: **2 MB** (histórico y en móvil) o **50 MB** desde ordenador | escritorio: tres fotogramas sugeridos o imagen propia si está disponible (guía de terceros: 1080×1920) | [OFICIAL] para la resolución; peso y formato de Shorts [TERCEROS, contradictorio] |
| Subtítulos | .srt / .sbv básicos en UTF-8; iTT (subconjunto de TTML) con posición; SCC; WebVTT | igual | [OFICIAL] salvo WebVTT [TERCEROS] |
| Pantalla final | últimos 5-20 s; vídeo ≥25 s; hasta 4 elementos en 16:9 | no aplica en la práctica | [OFICIAL] / [TERCEROS] |
| Capítulos | primero en 0:00, ≥3 marcas, cada capítulo ≥10 s, en la descripción | no | [TERCEROS citando la ayuda] |
| Miniatura de podcast | cuadrada, **1280×1280** | — | [OFICIAL] |

**Comando ffmpeg orientativo** (sale de lo anterior, no lo ha publicado YouTube):

```
-c:v libx264 -profile:v high -pix_fmt yuv420p -r 50 -g 25 -bf 2 -flags +cgop -b:v 12M -maxrate 16M -bufsize 24M -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 384k -ar 48000 -movflags +faststart
```

Para un vídeo de texto también vale `-crf 18` en lugar de `-b:v`.

## Respuestas, pregunta por pregunta

### 1. Especificaciones de subida del vídeo largo

- **Formato.** MP4 con *fast start*, VBR y 4:2:0, al framerate de origen [OFICIAL, support.google.com/youtube/answer/1722171]. El GOP es cerrado y de la mitad del framerate [OFICIAL, misma página]. Si el vídeo no trae metadatos de color, YouTube asume BT.709 [OFICIAL, misma página]. El audio puede ir en AAC-LC, Opus o Eclipsa Audio, a 48 kHz y 384 kbps en estéreo [OFICIAL].
- **Bitrate a 50 fps.** 50 cae en la franja de 48-60 fps de la tabla, así que en SDR son **12 Mbps** para 1080p. Varias guías de terceros dan esa misma cifra (postfa.st, ffmpeg-cookbook). En los extractos del buscador, la tabla oficial aparecía sin cabeceras con "10/15 Mbps" para 1080p y "20/30" para 1440p: son las cifras HDR. Las SDR 16/24 para 1440p salen de terceros (VideoProc y otros) y coinciden con mi recuerdo de la página oficial. Quedan como [OFICIAL, cotejo parcial].
- **¿1440p o 4K para conseguir VP9/AV1?** No es oficial. Lo repiten blogs de herramientas de escalado (VideoProc, VMake, Timeskip, VanceAI), y en el foro de VideoHelp un usuario informa de que su subida a 1440p salió *peor* que la de 1080p nativo [NO CONFIRMADO]. Lo que cambia en este caso: el contenido es texto blanco o gris sobre un fondo liso y con poco movimiento. Ese material se comprime muy bien en H.264 y la ventaja de VP9 es pequeña. Recomendación: generar en 1920×1080 nativo. Si hace falta, hacer una sola prueba A/B (el mismo episodio en 1080p y escalado a 2560×1440 a 24 Mbps) y comparar el stream de 1080p en móvil y en TV. Escalar a 1440p duplica el tamaño y el tiempo de render: con episodios de 4 h, unos 43 GB por vídeo.
- **Lo que no es oficial.** YouTube no publica un objetivo de sonoridad. La cifra de −14 LUFS es de terceros (productionadvice.co.uk, Meterplugs 2019 [ANTIGUO: 2019], youlean). Para voz TTS: normalizar a −14 LUFS integrados con TP ≤ −1 dBTP. Así el mismo master sirve también para el RSS y Spotify, aunque el objetivo de Spotify lo verifica otro investigador.

### 2. Límites de tamaño y duración

- **Límite.** 256 GB o 12 h, lo que llegue antes. Sin verificar, la cuenta solo admite 15 min; la verificación se hace por SMS o por llamada [OFICIAL, support.google.com/youtube/answer/71673]. Hay terceros que hablan de "512 GB si verificas": contradice a la ayuda oficial, descártalo [TERCEROS, erróneo].
- **Vídeos de 3-4 h.** Ningún límite impide subirlos. Lo que sí pasa [NO CONFIRMADO, por experiencia general]: el procesado en HD tarda varias horas más que el de SD, así que conviene subir en privado o programado y publicar cuando la HD esté lista. Para la pantalla final y los capítulos no hay límites distintos.

### 3. Shorts: formato, duración y Content ID

- **Detección.** Desde el 15-oct-2024 es Short todo vídeo **cuadrado o vertical de ≤3 min**. Un 16:9 sigue siendo vídeo largo aunque dure menos de 3 min [OFICIAL, support.google.com/youtube/answer/15424877]. El hashtag #Shorts no hace falta [TERCEROS].
- **Formato.** Lienzo de 1080×1920 a 9:16 y 50 fps (mismo framerate que el vídeo largo), a 12 Mbps. Sobre la resolución máxima hay contradicción: "1080p máximo según la ayuda" frente a "admite 4K" [TERCEROS, contradictorio]. 1080×1920 es lo seguro.
- **Content ID en Shorts de más de 1 min.** Antes: un Short de 1 a 3 min con cualquier reclamación activa se **bloqueaba en todo el mundo** [OFICIAL]. Desde el **24-sep-2026**, según el texto de la ayuda que reproducen terceros (argil.ai, newmediadispatch, extracto de support.google.com/youtube/answer/15424877?hl=en-GB): "los Shorts nuevos de más de un minuto (y menos de tres) con una reclamación activa de Content ID ya no se bloquearán automáticamente y podrán seguir reproduciéndose". La reclamación sigue existiendo y afecta a la monetización. Una fuente advierte de que la página en inglés de EE. UU. aún no lo reflejaba [NO CONFIRMADO].
- **Lo que cambia en este caso.** El audio es TTS propio en español, sin música, así que un fingerprint de audio del original en inglés no debería coincidir. El riesgo real son las **reclamaciones manuales o las retiradas por DMCA** del titular (ver la pregunta 10), no Content ID. No añadir música de fondo con licencia de terceros.

### 4. Zonas seguras de Shorts sobre 1080×1920

YouTube no publica rectángulos oficiales. Las plantillas de terceros dan estas cifras:

| Zona | Qué la tapa | Margen | Fuente |
|---|---|---|---|
| Arriba | búsqueda, menú, cámara, "Shorts" | **288 px** (y 0-288) | socialync [TERCEROS] |
| Derecha | columna de like, dislike, comentarios, compartir, remix y el disco del sonido | **192 px** (x 888-1080); hay otras que dan 120 | revid, socialync / hopperhq, poster.ly [TERCEROS] |
| Abajo | nombre del canal, botón Suscribirse, título o descripción, sonido, barra de progreso y la barra de navegación de la app | **672 px** (y 1248-1920, alrededor del 35 %); otras dan 380-390 o 300 | socialync, revid / poster.ly, hopperhq, blitzcut [TERCEROS] |
| Izquierda | — (margen visual) | **48 px** | upload-post [TERCEROS] |

- **Rectángulo seguro conservador.** x 48 a 888 e y 288 a 1248, es decir, **840×960 px**. El centro de ese rectángulo cae en **(468, 768)**, no en (540, 960).
- **Aplicado al tambor.**
  - Frase actual: centrada en la caja segura, en y ≈ 700-830, con un máximo de 3 líneas de unos 22-26 caracteres a 64-72 px en sans-serif negrita [recomendación propia, NO CONFIRMADO].
  - Frase anterior y siguiente: dentro de y 300-1240, en ≤2 líneas cada una.
  - Título del episodio y hablante: debajo de la cabecera (y ≈ 300-400). Nunca abajo, porque ahí YouTube ya pone su propio título.
  - Centrado horizontal: para quedar a la vez dentro de la caja segura de Shorts, Reels y TikTok se puede usar un margen de 120 px a la izquierda y 192 px a la derecha. Esa unificación la tienen que confirmar los otros investigadores.
- **Comprobación.** Las cifras varían mucho entre plantillas. Hay que revisar un Short de prueba en un móvil real, Android e iOS, antes de fijar la plantilla.

### 5. Zonas que tapa el reproductor en el vídeo largo (1920×1080)

- **Pantalla final.** El vídeo necesita **≥25 s**. Ocupa entre los últimos 5 y 20 s. Lleva hasta **4 elementos** en 16:9. No funciona en vídeos marcados como "para niños" ni en la web móvil, salvo en iPad [OFICIAL, support.google.com/youtube/answer/6388789]. Los elementos se colocan en cualquier parte del lienzo. Recomendación: en los últimos 20 s, quitar el tambor o reducirlo a la mitad superior, y dejar libre el rectángulo central-inferior de unos 1200×500 px para los elementos [NO CONFIRMADO, criterio propio]. En este caso hay una ventaja: se puede alargar el master con 20 s de cierre ("Escucha el episodio completo...").
- **Controles y barra de progreso.** Aparecen al pasar el ratón o tocar la pantalla y ocupan el 10-12 % inferior, unos **110-130 px de 1080** [NO CONFIRMADO; sin fuente oficial ni plantilla encontrada].
- **CC de YouTube.** Por defecto salen abajo y centrados, con hasta 2 líneas en torno al 80-90 % de la altura (y ≈ 860-1000), y se desplazan hacia arriba cuando aparecen los controles [NO CONFIRMADO]. Hasta donde llegó la búsqueda, el espectador no tiene ningún ajuste para moverlos. La posición sí se puede fijar en el archivo: iTT/TTML con estilos y posición [OFICIAL] o WebVTT con `line:0%` para mandarlos arriba [TERCEROS; un usuario de Stack Overflow informa de que el TTML no respetaba la posición, ANTIGUO: 2018].
- **Marca de agua de la marca.** Esquina inferior derecha, unos 150×150 px. Tarjetas: el aviso sale arriba a la derecha [NO CONFIRMADO, conocimiento general].
- **Dónde no poner el texto.** El tambor tiene la frase anterior arriba, la actual en el centro y la siguiente abajo. La frase **siguiente** no debe bajar de **y ≈ 860**, para dejar el 20 % inferior a los controles y los CC. El hablante y el título van arriba a la izquierda (y ≤ 120, x ≥ 96). Esquina inferior derecha libre.

### 6. Subtítulos y captions

- **Formatos.** SRT y SBV en versión básica, sin estilos y en UTF-8. iTT, subconjunto de TTML 1.0, admite estilo y posición. TTML está en "implementación parcial". También SCC y LRC [OFICIAL, support.google.com/youtube/answer/2734698]. WebVTT [TERCEROS, Rev].
- **¿Conviene subir un .srt además del texto incrustado?** Sí.
  1. Se genera de forma determinista desde `transcript.es.json`, con los mismos tiempos del tambor.
  2. Activa la traducción automática de subtítulos a otros idiomas.
  3. Mejora la accesibilidad con lectores de pantalla y en TV.
  4. Sustituye a los subtítulos automáticos, que con voz TTS pueden fallar.

  No se encontró ninguna cifra oficial sobre su efecto en la búsqueda [no encontrado]. Hay una pega: si el espectador activa los CC, el texto sale duplicado con el incrustado. Por eso el tambor tiene que respetar la franja inferior (pregunta 5).
- **Doblaje automático.** Llegó a todo el YPP en abril de 2025 y en febrero de 2026 se amplió a 27 idiomas, "para todos los usuarios". Content ID, un idioma no admitido o un idioma no detectado lo impiden [TERCEROS: socialmediatoday, indiatvnews, ppc.land]. El interruptor es "Permitir doblaje automático" en Configuración > Valores predeterminados de subida > Configuración avanzada [TERCEROS]. **Recomendación: desactivarlo.** Generaría pistas en inglés u otros idiomas a partir de una voz sintética que ya es traducción, cuando el original en inglés ya existe y es de Naval. Eso empeora el problema de derechos y no aporta nada a la audiencia hispanohablante. La traducción automática de subtítulos no crea una obra nueva y puede quedarse activa.

### 7. Miniatura

- **Vídeo largo.** 1280×720, mínimo 640 de ancho, para cuenta verificada [OFICIAL, support.google.com/youtube/answer/72431]. Sobre el peso hay contradicción: **2 MB** (ayuda archivada en 2022 [ANTIGUO: 2022] y desde móvil) frente a **50 MB desde ordenador** (guías de 2025-2026) [TERCEROS]. Exportar en JPG de ≤2 MB vale para los dos casos. La API admite JPEG y PNG [TERCEROS].
- **Shorts.**
  - La miniatura personalizada se sube desde escritorio desde el **24/25-jul-2026**, con despliegue gradual. Según ppc.land está "limitada al Partner Program", sin pruebas A/B. Además, se puede elegir uno de **3 fotogramas sugeridos** en escritorio; en la app móvil, cualquier fotograma [TERCEROS citando blog.youtube/news-and-events/youtube-studio-custom-thumbnail-updates/].
  - No hay especificación técnica propia; una guía de terceros recomienda 1080×1920.
  - Lo que cambia en este caso: el canal no está en el YPP, así que puede que no tenga la subida personalizada. Hay que hornear un **fotograma de portada** dentro del Short, por ejemplo los primeros 0,5-1 s o un fotograma fijo, con el título grande dentro de la zona segura, y elegirlo desde la app.

### 8. Capítulos, listas y Podcasts en YouTube

- **Capítulos.** En la descripción, empezando en `0:00`, con ≥3 marcas en orden ascendente y cada capítulo de ≥10 s. Para más de 1 h el formato es `H:MM:SS` [TERCEROS citando la ayuda]. Si no se cumplen los requisitos, fallan sin avisar. Un requisito antiguo de 1.000 suscriptores no está confirmado [NO CONFIRMADO]. Para este proyecto: `titulos_seccion` y los tiempos de los bloques permiten generar los capítulos automáticamente.
- **Lista como podcast.** En Studio: Contenido > Listas > Establecer como podcast. Para editar los detalles hace falta una **miniatura cuadrada de 1280×1280** [OFICIAL, support.google.com/youtube/answer/12751636]. YouTube a veces marca listas como podcast por su cuenta, y se puede deshacer [OFICIAL]. Una fuente habla de un límite de 10 MB [TERCEROS].
- **RSS en YouTube.** Ruta: Crear > Nuevo podcast > Enviar feed RSS [OFICIAL, support.google.com/youtube/answer/13973017]. Requisitos y efectos:
  - Solo está disponible en algunos países [OFICIAL, /answer/13525207].
  - El feed necesita email de propietario (`itunes:owner`) y ≥1 episodio, y tiene que poder rastrearse [TERCEROS: Captivate, Blubrry].
  - **Crea vídeos de imagen fija a partir de la portada.**
  - Los episodios nuevos se publican solos.
- **Recomendación.** Marcar como podcast la lista de vídeos subidos a mano: aparece en YouTube Music y en la pestaña Podcasts. **No** activar la ingesta por RSS, porque duplicaría cada episodio con un vídeo estático sin el tambor. Una lista por año o temporada, y otra lista "Podcast" con todo.

### 9. Vincular un Short a su episodio y metadatos de Shorts

- **Vídeo relacionado.** Un solo enlace por Short, hacia cualquier vídeo, Short o directo **del mismo canal**. Se pone en Studio de escritorio > Detalles > barra lateral, y se puede añadir a Shorts antiguos. **La API de publicación no lo admite**, así que hay que hacerlo a mano después de subir [TERCEROS: searchengineland 2023 [ANTIGUO: 2023], post-bridge, adaptlypost, opus.pro]. Una medición de terceros da "unos cientos de clics por cada 100.000 vistas" [TERCEROS, outlierkit].
- **Hashtags.** Pueden ir en el título o en la descripción, y YouTube muestra hasta 3. Sobre el límite hay contradicción: más de 15 o más de 60 hacen que se ignoren todos [TERCEROS]. #Shorts no influye en la clasificación. No se encontró ninguna guía oficial con datos sobre títulos de Shorts [no encontrado].

### 10. Políticas que tocan a este canal (contenido reutilizado, IA y derechos)

- **Contenido alterado o sintético.** Se declara contenido realista hecho o alterado de forma significativa con medios sintéticos. Una voz que imita a una persona real diciendo algo que no dijo se considera sintética. YouTube puede poner la etiqueta por su cuenta [TERCEROS citando la política, 2024-2025]. Declarar "sí" es lo correcto, porque XTTS clona el timbre de Naval y Nivi. Recomendación añadida: decir en la descripción "Voz sintética (TTS). Traducción no oficial."
- **Contenido "inauténtico".** Desde el 15-jul-2025 la categoría "repetitivo" del YPP pasó a llamarse "inauténtico": contenido masivo o con plantilla [TERCEROS: gulfnews, SEJ, ppc.land]. Como no se monetiza, no se aplica directamente. Aun así, una plantilla idéntica en 160 episodios más cientos de Shorts encaja en la descripción, así que conviene variar el título y la descripción y añadir valor en ellos (contexto, capítulos).
- **Derechos.** La ayuda oficial incluye las **traducciones entre las obras derivadas**, que "suelen requerir el permiso del titular". Que el uso no tenga ánimo de lucro es solo un factor, y citar al autor no protege [OFICIAL, support.google.com/youtube/answer/2797466 y /2797449].
- **Lo que cambia en este caso.** Sin el permiso de Naval, cada vídeo o Short puede recibir una retirada, y **3 avisos por derechos de autor = cierre del canal** (regla general de YouTube, no la he verificado en esta sesión). Los Shorts multiplican la superficie expuesta. Prioridad: conseguir el permiso antes de publicar en volumen.

## Qué evitar

- Poner texto en los 672 px inferiores o en los 192 px de la derecha de un Short, o el título del episodio abajo.
- Poner la frase "siguiente" del tambor por debajo de y ≈ 860 en 16:9, donde choca con los CC y los controles.
- Subir un vídeo largo vertical de más de 3 min esperando que cuente como Short: no lo será.
- Activar la ingesta por RSS en YouTube, que genera vídeos estáticos duplicados.
- Activar el doblaje automático.
- Música de fondo de terceros.
- Exportar con GOP abierto o largo, en 4:4:4 o 10 bits SDR, o con el moov al final.
- Miniaturas de más de 2 MB si se suben desde móvil o por API.
- Escalar a 1440p o 4K por sistema sin una prueba A/B: duplica el render y la subida en episodios de 4 h.
- Fiarse de que el vídeo relacionado se pueda poner por API.

## Dudas abiertas / no confirmado

1. Las cifras exactas de la tabla SDR (8/12, 16/24, 35-45/53-68 Mbps): los extractos no traían cabeceras. Hay que verificarlo en support.google.com/youtube/answer/1722171 cuando el host esté permitido.
2. El peso máximo de la miniatura, 2 MB o 50 MB.
3. Si la miniatura personalizada de Shorts llega a canales sin YPP.
4. El cambio de Content ID en Shorts del 24-sep-2026: lo citan terceros, y la versión de EE. UU. de la ayuda no lo reflejaba.
5. La resolución máxima de Shorts, 1080p o 4K.
6. Los rectángulos en px de los controles y CC del reproductor de vídeo largo: no hay fuente oficial ni plantilla. Hay que medirlos con capturas.
7. Las zonas seguras de Shorts: las plantillas de terceros discrepan entre 120 y 192 px a la derecha y entre 300 y 672 px abajo.
8. Si YouTube respeta la posición en TTML/iTT o WebVTT.
9. El objetivo de sonoridad: −14 LUFS no es oficial.
10. Si el doblaje automático admite el español como idioma de origen, y si el interruptor por canal sigue en la misma ruta.
11. Los requisitos actuales de capítulos, en particular el umbral de suscriptores.
12. En qué países está disponible la ingesta RSS.

## Fuentes (consultadas el 18-nov-2026 vía buscador; páginas sin fecha visible salvo que se indique)

- YouTube Help, Recommended upload encoding settings: https://support.google.com/youtube/answer/1722171 [OFICIAL]
- YouTube Help, Video and audio formatting specifications: https://support.google.com/youtube/answer/4603579 [OFICIAL]
- YouTube Help, Upload videos longer than 15 minutes: https://support.google.com/youtube/answer/71673 [OFICIAL]
- YouTube Help, Understand three-minute YouTube Shorts: https://support.google.com/youtube/answer/15424877 (también ?hl=en-GB) [OFICIAL]
- YouTube Help, Music eligibility for Shorts: https://support.google.com/youtube/answer/13486873 [OFICIAL]
- YouTube Help, Add end screens: https://support.google.com/youtube/answer/6388789 [OFICIAL]
- YouTube Help, Supported subtitle and closed caption files: https://support.google.com/youtube/answer/2734698 [OFICIAL]
- YouTube Help, Add video thumbnails: https://support.google.com/youtube/answer/72431 y la copia archivada en 2022 https://webcf.waybackmachine.org/web/20220630092903/https://support.google.com/youtube/answer/72431 [OFICIAL, ANTIGUO: 2022]
- YouTube Help, Create a podcast in YouTube Studio: https://support.google.com/youtube/answer/12751636 [OFICIAL]
- YouTube Help, Deliver podcasts using an RSS feed: https://support.google.com/youtube/answer/13525207 [OFICIAL]
- YouTube Help, Publish or disconnect RSS episodes: https://support.google.com/youtube/answer/13973017 [OFICIAL]
- YouTube Help, Copyright on YouTube: https://support.google.com/youtube/answer/2797466 y Common copyright myths: https://support.google.com/youtube/answer/2797449 [OFICIAL]
- YouTube Blog, Studio custom thumbnail updates (jul-2026): https://blog.youtube/news-and-events/youtube-studio-custom-thumbnail-updates/ [OFICIAL, solo extracto]
- ppc.land, Shorts thumbnails sin A/B (jul-2026): https://ppc.land/youtube-ends-2-year-wait-for-shorts-thumbnails-but-blocks-a-b-testing/ [TERCEROS]
- thetechoutlook (25-jul-2026): https://www.thetechoutlook.com/news/apps/custom-thumbnails-coming-soon-to-youtube-shorts/ [TERCEROS]
- argil.ai, Shorts length / Content ID 24-sep-2026: https://www.argil.ai/blog/how-long-can-youtube-shorts-be [TERCEROS]
- newmediadispatch, What counts as a Short: https://newmediadispatch.com/platforms/what-counts-as-a-short [TERCEROS]
- postfa.st, YouTube video specs: https://postfa.st/sizes/youtube/video [TERCEROS]
- ffmpeg-cookbook: https://ffmpeg-cookbook.pages.dev/en/articles/youtube-ffmpeg-settings/ [TERCEROS]
- magichour.ai: https://magichour.ai/blog/best-video-formats-for-youtube [TERCEROS]
- VideoProc, 1440p trick: https://www.videoproc.com/resource/how-to-improve-youtube-video-quality.htm [TERCEROS]
- VideoHelp forum, contraejemplo: https://forum.videohelp.com/showthread.php?p=2778685 [NO CONFIRMADO]
- Production Advice, YouTube loudness: https://productionadvice.co.uk/youtube-loudness/ [TERCEROS]
- Meterplugs, −14 LUFS (2019): https://www.meterplugs.com/blog/2019/09/18/youtube-changes-loudness-reference-to-14-lufs.html [ANTIGUO: 2019]
- socialync, safe zones de Shorts: https://www.socialync.io/tools/safe-zones/youtube-shorts [TERCEROS]
- revid: https://www.revid.ai/youtube-shorts-safe-zone [TERCEROS]
- hopperhq: https://www.hopperhq.com/blog/youtube-shorts-dimensions/ [TERCEROS]
- poster.ly: https://www.poster.ly/tools/youtube-shorts-safe-zone-checker [TERCEROS]
- upload-post: https://www.upload-post.com/tools/safe-zone-checker/ [TERCEROS]
- blitzcutai: https://blitzcutai.com/blog/best-caption-placement-short-form-video [TERCEROS]
- searchengineland, enlazar Shorts y vídeos largos (2023): https://searchengineland.com/youtube-enables-linking-shorts-long-form-videos-430655 [ANTIGUO: 2023]
- post-bridge, límite de la API: https://support.post-bridge.com/social-media-scheduling/can-i-link-youtube-shorts-to-long-form-videos [TERCEROS]
- adaptlypost: https://adaptlypost.com/en/support/youtube-shorts-linking [TERCEROS]
- outlierkit, medición de clics del vídeo relacionado: https://outlierkit.com/resources/youtube-shorts-to-long-form/ [TERCEROS]
- socialmediatoday, doblaje automático para todos los creadores: https://www.socialmediatoday.com/news/youtube-expands-auto-dubbing-to-all-creators/811375/ [TERCEROS]
- indiatvnews, 27 idiomas (5-feb-2026): https://www.indiatvnews.com/technology/news/youtube-auto-dubbing-feature-expands-to-all-users-now-supports-27-languages-2026-02-05-1029070 [TERCEROS]
- vozo.ai, desactivar el doblaje automático (2026): https://www.vozo.ai/es/blogs/how-to-turn-off-youtube-auto-dubbing-for-viewers-and-creators [TERCEROS]
- gulfnews, política de contenido inauténtico (jul-2025): https://gulfnews.com/technology/youtube-updates-monetisation-policies-ai-and-repetitive-content-ban-begins-july-15-1.500192660 [TERCEROS]
- SEJ, aclaración de la política: https://www.searchenginejournal.com/youtube-clarifies-monetization-update-targeting-spam-not-reaction-channels/550123/ [TERCEROS]
- subscribr, divulgación de IA: https://subscribr.ai/p/youtube-ai-disclosure-rules [TERCEROS]
- Captivate, RSS en YouTube: https://www.captivate.fm/?p=11193 [TERCEROS]
- Blubrry, RSS en YouTube: https://blubrry.com/manual/podcast-promotion/submit-podcast-youtube/ [TERCEROS]
- adaptlypost, requisitos de capítulos: https://adaptlypost.com/es/blog/youtube-chapters-requirements [TERCEROS]
- exemplary.ai, hashtags de Shorts: https://exemplary.ai/blog/best-hashtags-for-youtube-shorts [TERCEROS]
- Stack Overflow, posición en TTML (2018, espejo): https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/43144169/positioning-in-ttml-subtitles-for-youtube [ANTIGUO: 2018]

---

## Informe 2: Meta: Instagram (Reels, feed, Stories) y Facebook

# Informe investigador 2/6: Meta (Instagram Reels, feed y Stories; Facebook)

**Cómo se ha investigado.** Desde esta sesión no se pueden abrir los dominios de Meta: facebook.com, developers.facebook.com y help.instagram.com fallan con ENOTFOUND porque no están en la lista de red permitida. Los datos marcados [OFICIAL] salen de los fragmentos de páginas oficiales que devuelve el buscador, no de haber leído la página entera. Si se quiere comprobar línea a línea, hay que permitir esos tres dominios en la configuración de red de la sesión. Fecha de consulta de todo: 18-nov-2026.

## Resumen accionable

1. **Vertical para Instagram y Facebook.**
   - Master de 1080x1920 (9:16), H.264 High, MP4, SDR, AAC-LC estéreo a 48 kHz y 128 kbps o más.
   - Bitrate de vídeo de 8 a 12 Mbps VBR; el tope oficial de la API es 25 Mbps.
   - Clips de 15 s a 3 min: por encima de 180 s Instagram no recomienda el Reel a no seguidores [OFICIAL].
2. **Frecuencia de imagen.**
   - Instagram admite de 23 a 60 fps por API [OFICIAL], así que 50 fps entra.
   - Varios informes de terceros dicen que lo alto se recomprime a 30 fps [NO CONFIRMADO]. No hay nada publicado sobre 50 fps en concreto.
   - Para texto que se mueve en "tambor", conviene exportar el vertical a 30 fps (25 fps si se quiere coherencia PAL con el master de 50). Así la conversión de la plataforma no mete saltos irregulares. Esto es una recomendación propia, no un dato.
3. **Rectángulo seguro único para el vertical.** x 90–960, y 290–1250 sobre 1080x1920.
   - Sale de la zona segura oficial de anuncios de Meta (14 % arriba, 35 % abajo y 6 % por lado), combinada con los recortes 4:5 del feed y 3:4 de la cuadrícula.
   - La frase actual centrada en y ≈ 770 queda visible en Reels, feed, cuadrícula y Stories.
   - Si la composición es solo para Reels orgánico, se puede bajar el límite inferior hasta y ≈ 1500. La UI orgánica tapa unos 280–420 px abajo [TERCEROS].
4. **Facebook.**
   - Desde jun-2025 todo vídeo nuevo es Reel, sin límite de duración ni de formato [OFICIAL, about.fb.com].
   - La subida de vídeo a Página admite hasta 10 GB y menos de 240 min [OFICIAL]. Un episodio de 1 a 4 h en 1920x1080 cabe si dura menos de 4 h. Los episodios de 4 h o más hay que partirlos.
5. **Subtítulos.**
   - Hay que desactivar los subtítulos automáticos en cada Reel de Instagram para que no se solapen con el texto incrustado. Instagram no admite subir .srt.
   - Facebook sí admite .srt en vídeos de Página con el nombre `archivo.es_ES.srt` [OFICIAL].
6. **Política.**
   - Hay que poner la etiqueta "AI info" (o "Información de IA"): Meta pone como ejemplo de lo que la requiere un Reel con locución de IA realista [OFICIAL].
   - El contenido de un tercero reutilizado sin permiso cae en las políticas de "unoriginal content": menos distribución en Facebook desde jul-2025 y menos recomendaciones en Instagram desde abr-2026.
   - La traducción con doblaje y la reedición visual cuentan como "mejora significativa" según la guía de Meta, pero sin permiso de Naval sigue habiendo riesgo de derechos de autor (retirada por denuncia).
7. **Publicación cruzada Instagram→Facebook.** Funciona con cuentas profesionales sin monetizar, pero hay un informe de 30 a 40 % menos alcance que la subida nativa [NO CONFIRMADO, anecdótico]. Es mejor subir de forma nativa a cada plataforma, o desde Meta Business Suite.

## Tabla de especificaciones

| Formato | Lienzo | Relación | fps | Códec / bitrate | Tamaño máx. | Duración | Nivel |
|---|---|---|---|---|---|---|---|
| IG Reel (API Graph) | ancho máx. 1920 px; recomendado 1080x1920 | 9:16 (admite 0.01:1 a 10:1 [NO CONFIRMADO]) | 23–60 | HEVC o H.264, progresivo, GOP cerrado, 4:2:0, VBR ≤ 25 Mbps; audio AAC | 300 MB (API) | 3 s – 15 min (API) | [OFICIAL] developers.facebook.com, IG User Media |
| IG Reel (app) | 1080x1920 (mín. 720x1280) | 9:16 | rec. 30 | — | 4 GB [TERCEROS] | hasta 20 min (grabación y subida, despliegue nov-2025) | [OFICIAL] about.instagram.com/features/reels; [TERCEROS] PetaPixel 25-nov-2025 |
| IG Reel recomendable a no seguidores | — | — | — | — | — | ≤ 3 min | [OFICIAL] help.instagram.com/225190788256708 |
| IG Reel desde Meta Business Suite (escritorio) | 1080x1920 | 9:16 | — | — | 250 MB [TERCEROS] | 90 s según guías [NO CONFIRMADO, posiblemente antiguo] | [TERCEROS] socialbu, posteverywhere 2026 |
| IG vídeo de feed desde web | 1080x1350 (4:5) o 1080x1080 | 1:1, 4:5, 1.91:1 | 30 | — | < 4 GB | hasta 60 min (web); en móvil lo largo pasa a Reel | [TERCEROS] Kapwing, post-bridge 2025-26 |
| IG Story | 1080x1920 | 9:16 | 30 (24–60) | — | 100 MB (API) [NO CONFIRMADO] | 60 s por segmento | [OFICIAL] help.instagram.com/270963803047681 "60-second maximum length" |
| FB vídeo/Reel en Página | ≤ 1080p recomendado; 1920x1080 o 1080x1920 | cualquiera desde jun-2025 | — | MP4; AAC estéreo ≥ 128 kbps | 10 GB | < 240 min | [OFICIAL] facebook.com/business/help/163131210928551 |
| FB Reel por API (Reels Publishing API) | 1080x1920 | 9:16 | 24–60 | — | — | 3–90 s | [OFICIAL] developers.facebook.com/documentation/video-api/guides/reels-publishing |
| FB anuncio de vídeo en feed (referencia) | — | — | — | — | 4 GB | 1 s – 241 min | [OFICIAL] ads-guide |
| FB Premiere | — | — | — | — | 10 GB | 4 h | [OFICIAL] business/help/268843097150181 |

## Zonas seguras en píxeles

### Vertical 1080x1920

| Fuente | Arriba | Abajo | Izquierda | Derecha | Rectángulo libre |
|---|---|---|---|---|---|
| Meta, anuncios en Reels y Stories [OFICIAL, ads-guide/image/instagram-reels y business/help/980593475366490] | 14 % = 269 px | 35 % = 672 px | 6 % = 65 px | 6 % = 65 px | x 65–1015, y 269–1248 (950x979) |
| Hopper 2026 [TERCEROS] | 14 % | 35 %, y 40 % en la esquina inferior derecha | 6 % | 6 % | igual, sin la esquina inferior derecha |
| TryMyPost 2026, Reels orgánico [TERCEROS] | — | 280 px | — | 90 px | — |
| Screensnap [TERCEROS] | 250 px | 350 px | — | — | franja de 1320 px |
| PostEverywhere [TERCEROS] | 220 px | — | — | — | — |
| Frameo / Fliki [TERCEROS] | — | — | — | — | 1080x1440 / 1080x1420 centrados |
| Stories [TERCEROS] | 250 px | 250–340 px; stickers a más de 300 px del borde | — | — | aprox. 1080x1390 |

Qué tapa cada zona:
- **Arriba (0–220/270 px):** cabecera "Reels" con el icono de cámara. En Stories, la barra de progreso, el avatar, el nombre y el botón de cerrar.
- **Abajo (aprox. 1250–1920 px en anuncios, aprox. 1500–1920 px en orgánico):**
  - en Reels, el avatar, el nombre de usuario, el botón Seguir, la descripción en 1–2 líneas expandibles, la pista de audio y la barra de navegación;
  - en anuncios, además, el botón de llamada a la acción;
  - en Stories, la barra "Enviar mensaje" y las reacciones.
- **Derecha (aprox. 90–140 px desde el borde, de y ≈ 1100 a 1800):** la columna de me gusta, comentar, compartir, guardar, tres puntos y el disco de audio.

Cifras orgánicas: no hay ninguna oficial. Meta solo publica la zona segura para anuncios, y la ofrece como plantilla descargable (ppt, psd, keynote) en facebook.com/business/ads/facebook-instagram-reels-ads.

### Recortes de feed y cuadrícula sobre un 9:16

- **Cuadrícula del perfil 3:4** (desde ene-2025) [TERCEROS: Buffer, Planoly, Kapwing]. Toma la franja central 1080x1440, es decir y 240–1680. Las cifras de la vista previa discrepan entre fuentes: 1012, 1013 o 1015 x 1350.
- **Feed 4:5.** Sería la franja central 1080x1350, es decir y 285–1635. Las fuentes no se ponen de acuerdo sobre si el feed principal recorta los Reels a 4:5 o los muestra a pantalla completa (Hopper y Moda dicen 9:16) [NO CONFIRMADO]. Lo prudente es diseñar como si recortara.
- **Intersección de todo** (zona de anuncios, 4:5 y 3:4): **x 65–1015, y 285–1248**. Con 25 px de colchón queda **x 90–990, y 310–1225**.

Propuesta concreta para el "tambor" en 1080x1920:
- título del episodio en y 310–420;
- frase anterior en y 480–640;
- frase actual centrada en y ≈ 770, de 2 a 4 líneas, en la franja y 650–900;
- frase siguiente en y 920–1080;
- hablante en y 1100–1220;
- margen derecho del texto a 120 px del borde, por la columna de botones.

### Horizontal 1920x1080 (Facebook e Instagram)

- No hay superposición de UI publicada. En el feed de Facebook el vídeo se ve en 16:9. En el visor de Reels un 16:9 aparece con barras negras arriba y abajo (letterbox) [TERCEROS].
- Basta el margen clásico de título-seguro: 5 % (96 px a cada lado y 54 px arriba y abajo). Se recomienda dejar 120 px abajo por la barra de progreso y los controles. Esto es una recomendación, no un dato de la plataforma.

## Respuestas pregunta por pregunta

**1. Reels: especificaciones y duración.**
- **API (oficial):** HEVC o H.264, 23–60 fps, VBR de 25 Mbps como máximo, 300 MB, de 3 s a 15 min, audio AAC. "Ancho máximo 1920 px" sale de la misma página según guías [NO CONFIRMADO].
- **App:** hasta 20 min, según la página de funciones de Instagram ("one or multiple clips that add up to 20 minutes") [OFICIAL] y PetaPixel del 25-nov-2025. Hubo pruebas desde jun-2025 (onlinemarketing.de) y el despliegue fue gradual: algunas cuentas veían todavía 90 s o 3 min (Buffer).
- **Meta Business Suite:** guías de 2026 hablan de 90 s y 250 MB [NO CONFIRMADO, probablemente antiguo]. Hay que comprobarlo en la propia interfaz.
- **Distribución:** solo los Reels de 3 min o menos son elegibles para recomendación a no seguidores [OFICIAL, help.instagram.com/225190788256708; creators.instagram.com].
- **50 fps:** está dentro del rango oficial de 23–60. Que se conserve o se convierta a 30 no está documentado. Un usuario de Samsung informa de que 60 fps acaba en 30 fps, y varias guías recomiendan 30 fps porque lo alto se comprime más [NO CONFIRMADO].
- **Resolución:** 1080x1920. El 4K se reduce [TERCEROS].

**2. Zonas seguras.** Ver la tabla anterior. El rectángulo concreto con fuente oficial es x 65–1015, y 269–1248, el de anuncios.

**3. Recorte en feed y cuadrícula.** Ver arriba: zona común x 65–1015, y 285–1248. Si se ignora la zona de anuncios y solo se tienen en cuenta los recortes, la franja es y 285–1635 y x 0–1080.

**4. Portada.**
- Se sube a 1080x1920. Se puede elegir un fotograma del vídeo o una imagen del carrete [TERCEROS: Later, Planoly, Oktopost].
- En la cuadrícula se ve el recorte central 3:4, 1080x1440 (y 240–1680). Hay que meter el texto de la portada en y 300–1620 con márgenes laterales de 60 px.
- "Ajustar vista previa" permite reencuadrar después de publicar [TERCEROS].
- La API acepta `cover_url` y `thumb_offset` (documentación de IG User Media) [OFICIAL, según el fragmento del buscador].
- La cifra de 420x654 no aparece en ninguna fuente actual: "no encontrado".

**5. Vídeo de feed frente a Reel.**
- Desde 2022 los vídeos que se suben en el móvil se publican como Reel. Según guías de 2025-26, el móvil recorta a 20 min lo que pasa de esa duración y lo convierte en Reel [TERCEROS].
- Desde la web (instagram.com en escritorio) se puede subir un vídeo de feed de hasta 60 min y menos de 4 GB [TERCEROS: Kapwing, post-bridge].
- En el feed y los carruseles se admiten 1:1 (1080x1080), 4:5 (1080x1350) y 1.91:1 (1080x566) [TERCEROS; ads-guide instagram-feed OFICIAL para anuncios].
- En la práctica, todo vídeo nuevo es un Reel salvo los vídeos largos subidos desde la web.

**6. Stories.**
- 1080x1920, 60 s por segmento [OFICIAL].
- Zonas: arriba 250 px y abajo de 250 a 340 px, con el sticker de enlace a más de 300 px del borde [TERCEROS].
- El sticker de enlace no se puede publicar por API, solo a mano desde la app [TERCEROS]. Sirve para avisar de un episodio nuevo con un enlace a YouTube o Spotify. No se ha encontrado ninguna medición de clics.

**7. Facebook.**
- Desde el 17-jun-2025 todo vídeo nuevo, en perfiles y en Páginas, se clasifica como Reel, "sin límite de duración ni de formato", tanto vertical corto como horizontal largo [OFICIAL, about.fb.com/news/2025/06/making-it-easier-create-videos-facebook]. La pestaña "Vídeo" pasa a llamarse "Reels". Los directos siguen aparte.
- Subida a Página: 10 GB y menos de 240 min, MP4, 1080p o menos, AAC estéreo a 128 kbps o más [OFICIAL]. Un episodio de 1 a 4 h en 1920x1080 sí cabe. Los de 4 h o más se parten en partes.
- A 1080p, 4 h en 10 GB dan unos 5,5 Mbps de media en total. Para episodios largos hay que exportar a 4–5 Mbps de vídeo, cosa viable para un vídeo de texto sobre fondo estático. Es un cálculo propio.
- La Reels Publishing API sigue documentando 3–90 s y 24–60 fps. Para lo largo hay que subir a mano o usar la Video API normal.
- Zonas seguras de Facebook Reels: la misma zona unificada de anuncios (14 %, 35 % y 6 %). Hay blogs que hablan de una "zona unificada" desde mar-2026 [NO CONFIRMADO].

**8. Publicación cruzada.**
- Requiere tener las dos cuentas en el mismo Accounts Center y compartir desde la app de Instagram, Android o iPhone [OFICIAL, help.instagram.com/iphone-app/459497729122868]. Ruta: Accounts Center → Compartir entre perfiles. Funciona con cuentas Business o Creator. La monetización no importa.
- Pegas:
  - un consultor mide de 30 a 40 % menos alcance que la subida nativa [NO CONFIRMADO];
  - hay informes de Reels que en Facebook aparecen como imagen de portada estática [NO CONFIRMADO];
  - una migración de cuentas hacia el 23-abr-2026 desactivó interruptores de compartir [NO CONFIRMADO].
- Recomendación: subir de forma nativa a cada sitio, o desde Business Suite publicando a la vez en Instagram y Facebook.

**9. Audio y subtítulos.**
- **Audio:** AAC [OFICIAL]. Para Facebook, AAC estéreo a 128 kbps o más [OFICIAL]. 48 kHz según Ayrshare [TERCEROS]; 44,1 kHz también se acepta.
- **Sonoridad:** no hay objetivo oficial. Meta usa xHE-AAC y delega la normalización en el reproductor (engineering.fb.com, 11-abr-2023 [ANTIGUO: 2023]). Los terceros recomiendan -14 LUFS integrados y -1 dBTP; una fuente da de -14 a -16 LUFS.
- **Subtítulos automáticos de Instagram:**
  - se desactivan para toda la cuenta en Ajustes → Accesibilidad → Subtítulos, solo a partir de ese momento;
  - en cada Reel, se quita el sticker "Subtítulos" en el editor antes de publicar;
  - en un Reel ya publicado, "Quitar subtítulos para todos", que no se puede deshacer [TERCEROS; las rutas cambian según la versión].
- **.srt:** Instagram no lo admite ("no encontrado" en ninguna fuente). Facebook sí en vídeo de Página: Opciones de vídeo → subir .srt con el nombre `archivo.es_ES.srt` [OFICIAL, business/help/1675722002698686 y facebook.com/help/569371393126980]. Para Reels de Facebook no está confirmado que se pueda.

**10. Calidad de subida.**
- **App:** activar "Subir con la máxima calidad" en Ajustes → Uso de datos y calidad multimedia, y desactivar el ahorro de datos [TERCEROS].
- No se ha encontrado documentación oficial que compare la calidad del móvil con la de Business Suite.
- **Recompresión:** hay recodificación siempre [TERCEROS].
- Para minimizarla:
  - entregar exactamente 1080x1920 SDR a 30 fps;
  - H.264 High a 8–12 Mbps (las guías citan 3,5–5 Mbps como suficiente) y 25 Mbps como máximo, que es el tope de la API;
  - evitar HDR, porque se convierte mal a SDR [TERCEROS];
  - el 4K no compensa porque se reduce a 1080p.
- En un vídeo de texto plano, los degradados suaves de fondo provocan bandas al recomprimir. Mejor fondos lisos o con un grano ligero. Es una recomendación propia.

## Qué cambia en este caso (lectura con texto, voz sintética, traducción de un tercero, sin monetizar)

- **Etiqueta de IA.**
  - Meta "puede exigir" la etiqueta "AI info" en audio que suene realista y esté creado o alterado con IA. Pone como ejemplo un Reel con locución de IA realista, y puede penalizar si falta [OFICIAL, meta.com/help/artificial-intelligence/1783222608822690].
  - Hay que activar la opción "Etiqueta de IA" al publicar en Instagram y Facebook.
- **Contenido no original.**
  - **Facebook (14-jul-2025):** las cuentas que reutilizan de forma repetida contenido de otros "sin permiso o sin mejoras significativas" pierden distribución en todo su contenido; las copias detectadas, también [OFICIAL, creators.facebook.com/blog/combating-unoriginal-content].
  - **Instagram (30-abr-2026):** las cuentas que repiten contenido no original dejan de ser elegibles para recomendaciones, también en fotos y carruseles [TERCEROS: PetaPixel].
  - La traducción con doblaje y el diseño propio ayudan, porque Meta cita voiceovers y comentario como mejora.
  - Lo que no se puede evitar es que el original lo reclame por derechos de autor, porque no hay permiso. Hay que acreditar a Naval y a nav.al en la descripción.
- **Monetización.** No hay ninguna especificación técnica que dependa de monetizar. Las sanciones por contenido no original incluyen perder la monetización, algo que aquí no aplica, pero también reducen la distribución, y eso sí aplica.

## Qué evitar

- Reels de más de 180 s si se busca alcance.
- Texto por debajo de y ≈ 1250 o en los 120 px de la derecha si el vídeo va a servir también como anuncio o como Story. En orgánico, nunca por debajo de y ≈ 1500.
- Texto fuera de la franja y 285–1635, porque se pierde en el feed 4:5 y en la cuadrícula 3:4.
- Dejar los subtítulos automáticos activados. Se solapan con el tambor y su transcripción de la voz sintética puede ser errónea.
- HDR, 4K, más de 25 Mbps y 60 fps sin necesidad.
- Fiarse de la publicación cruzada automática para Facebook.
- Subir episodios de 4 h o más a una Página sin partirlos.
- Publicar sin la etiqueta de IA.

## Dudas abiertas / no confirmado

- Si 50 fps se conserva o se pasa a 30 en Reels: no hay fuente. Hay que hacer una prueba: subir el mismo clip a 25, 30 y 50 fps y descargarlo con `ffprobe`.
- La duración máxima real de un Reel desde Business Suite y desde instagram.com en escritorio a fecha de nov-2026: hay fuentes con 90 s, 15 min y 20 min.
- Si el feed principal de Instagram recorta los Reels a 4:5.
- La medida exacta de la UI orgánica de Reels en px: solo hay plantillas de terceros, todas distintas.
- Si existe hoy una zona segura unificada de Meta (mar-2026) distinta de 14/35/6 %.
- Si se puede subir .srt a un Reel de Facebook.
- La sonoridad objetivo de Meta.
- El tamaño máximo de un Reel subido desde la app: 4 GB según terceros.
- Qué cuenta exactamente como "mejora significativa" ante un reclamo de derechos sin permiso.

## Fuentes

**Oficiales**

| Fuente | Fecha |
|---|---|
| Meta for Developers, IG User Media (especificaciones de Reels): https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/ | consulta 18-nov-2026, vía buscador |
| Meta for Developers, Reels Publishing API: https://developers.facebook.com/documentation/video-api/guides/reels-publishing | consulta 18-nov-2026 |
| Meta, Graph API Video Captions: https://developers.facebook.com/docs/graph-api/reference/video/captions/ | consulta 18-nov-2026 |
| Instagram Reels, página de funciones (20 min): https://about.instagram.com/features/reels | consulta 18-nov-2026 |
| Instagram Help, grabar un reel (más de 3 min no se recomienda): https://help.instagram.com/225190788256708 | consulta 18-nov-2026 |
| Instagram Help, máximo de 60 s (Stories): https://help.instagram.com/270963803047681 | consulta 18-nov-2026 |
| Instagram Help, compartir en Facebook: https://help.instagram.com/iphone-app/459497729122868 | consulta 18-nov-2026 |
| Instagram Creators, recomendaciones: https://creators.instagram.com/blog/instagram-recommendations-eligibility-tips-creators | [ANTIGUO: 2023] |
| Meta, zona segura de anuncios en Stories y Reels: https://www.facebook.com/business/help/980593475366490/ | consulta 18-nov-2026 |
| Meta Ads Guide, imagen en Instagram Reels (14/35/6 %): https://www.facebook.com/business/ads-guide/update/image/instagram-reels | consulta 18-nov-2026 |
| Meta, anuncios en Reels y plantillas de zona segura: https://www.facebook.com/business/ads/facebook-instagram-reels-ads | consulta 18-nov-2026 |
| Facebook, subir un vídeo (10 GB, menos de 240 min): https://www.facebook.com/business/help/163131210928551 | consulta 18-nov-2026 |
| Facebook, requisitos de Premieres: https://www.facebook.com/business/help/268843097150181 | consulta 18-nov-2026 |
| Facebook, subtítulos .srt: https://www.facebook.com/business/help/1675722002698686 | consulta 18-nov-2026 |
| Facebook, publicar o editar un vídeo en una Página: https://www.facebook.com/help/569371393126980 | consulta 18-nov-2026 |
| Meta Newsroom, "Making it Easier to Create Videos on Facebook": https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/ | 17-jun-2025 |
| Facebook Creators, "Combating unoriginal content": https://creators.facebook.com/blog/combating-unoriginal-content | 14-jul-2025 |
| Meta Help, identificar contenido de IA: https://www.meta.com/en-gb/help/artificial-intelligence/1783222608822690/ | consulta 18-nov-2026 |
| Meta, etiquetado de IA: https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/ | [ANTIGUO: abr-2024] |
| Meta Engineering, xHE-AAC: https://engineering.fb.com/2023/04/11/video-engineering/high-quality-audio-xhe-aac-codec-meta/ | [ANTIGUO: 2023] |

**Terceros**

| Fuente | Fecha |
|---|---|
| PetaPixel, Reels de 20 min: https://petapixel.com/2025/11/25/instagram-updates-camera-so-you-can-film-20-minute-reels | 25-nov-2025 |
| PetaPixel, Instagram contra el contenido reposteado: https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/ | 30-abr-2026 |
| TechCrunch, todo vídeo de Facebook será Reel: https://techcrunch.com/2025/06/17/facebook-announces-that-all-videos-on-its-platform-will-soon-be-shared-as-reels | 17-jun-2025 |
| TechCrunch, contenido no original en Facebook: https://techcrunch.com/2025/07/14/following-youtube-meta-announces-crackdown-on-unoriginal-facebook-content | 14-jul-2025 |
| Buffer, duración de Reels: https://buffer.com/resources/instagram-reels-length | 2025 |
| Buffer, cuadrícula: https://buffer.com/resources/instagram-grid/ | 2025 |
| Planoly, cuadrícula vertical: https://planoly.com/blog/guide-to-instagrams-new-vertical-grid | 2025 |
| Kapwing, cuadrícula: https://www.kapwing.com/resources/instagrams-new-grid-layout-size-and-dimensions-2025/ | 2025-26 |
| Kapwing, vídeo largo en Instagram: https://www.kapwing.com/resources/how-to-post-a-long-video-on-instagram-feed-live-igtv/ | 2025-26 |
| Hopper, tamaño de Reel: https://www.hopperhq.com/blog/instagram-reel-size/ | 2026 |
| TryMyPost, zonas seguras: https://www.trymypost.com/blog/instagram-reels-safe-zones-2026 | 2026 |
| Screensnap, guía de Reels: https://www.screensnap.pro/blog/instagram-reels-size-guide | 2026 |
| PostEverywhere, relación de aspecto de Reels: https://posteverywhere.ai/blog/instagram-reels-aspect-ratio | 2026 |
| AdKit, zonas seguras de Meta: https://adkit.so/tools/safe-zones/meta | actualizado 10-sep-2026 |
| AdsUploader, zonas seguras de anuncios de Meta: https://adsuploader.com/blog/meta-ads-safe-zones | 2026 |
| Postsyncer, Stories: https://postsyncer.com/tips/instagram-stories-dimensions-and-safe-zones | 2025-26 |
| Metricool, publicación cruzada: https://metricool.com/crossposting-instagram-facebook/ | 2025 |
| TimeToPost, publicación cruzada: https://timetopost.co/blog/instagram-facebook-crossposting-guide/ | 2026 |
| SocialBu, programar Reels: https://socialbu.com/blog/schedule-instagram-reels-and-posts | 2026 |
| Ayrshare, Facebook Pages: https://ayrshare.com/docs/media-guidelines/facebook_pages | consulta 18-nov-2026 |
| OpenClip, normalización de audio: https://openclip.app/learn/audio-normalization | consulta 18-nov-2026 |
| SlashGear, quitar subtítulos automáticos: https://www.slashgear.com/904133/how-to-remove-auto-generated-captions-from-your-instagram-video | sin fecha |
| Visnalize, compresión: https://visnalize.com/blog/instagram-media-specs-compression-guide | sin fecha |
| Samsung Community, 60 fps a 30 fps: https://r2.community.samsung.com/t5/Galaxy-A/Instagram-60fps-video-upload/td-p/13804972 | [NO CONFIRMADO, foro] |


---

## Informe 3: TikTok

# Informe del investigador 3 de 6: TikTok (consultado el 18-nov-2026)

**Aviso de método.** WebFetch no ha podido abrir ningún dominio de TikTok (developers.tiktok.com, ads.tiktok.com, www.tiktok.com) ni varios de terceros (trymypost.com, adkit.so, relevantaudience.com): da `ENOTFOUND` porque esos dominios no están permitidos en la red de esta sesión. Todo lo marcado [OFICIAL] sale de los fragmentos de las páginas oficiales que devuelve el buscador, no de una lectura completa de cada página. Para leerlas enteras hay que permitir esos dominios en la configuración de red de la sesión.

## Resumen accionable

1. **Formato maestro para TikTok:** 1080x1920 en 9:16, MP4 con H.264 y audio AAC. La API acepta de 23 a 60 fps, así que 50 fps está dentro del rango. Ninguna fuente confirma que TikTok entregue el vídeo a 50 fps: hay que probarlo.
2. **No subas 4K.** Varias fuentes coinciden en que TikTok baja todo a 1080p y vuelve a comprimir. Para que el texto fino salga nítido, conviene exportar en 1080p con un bitrate alto: de 8 a 15 Mbps [sin confirmar].
3. **Zona segura para el texto del tambor sobre 1080x1920:** x = 60–940 e y = 160–1436. Eso deja 160 px arriba, 484 px abajo, 140 px a la derecha y 60 px a la izquierda. La frase actual conviene centrarla hacia y ≈ 800, no en 960. Si un clip lleva una descripción larga, el borde inferior seguro sube.
4. **Subtítulos automáticos:** no actives los de TikTok. El texto ya va incrustado y se duplicaría.
5. **Voz sintética:** TikTok no obliga a etiquetar el TTS genérico que no imita a nadie. Una voz clonada de Naval o de Nivi sí cuenta como imitar a una persona real y hay que etiquetarla. Activa siempre el interruptor "AI-generated content".
6. **Distribución:** se puede subir desde la web (TikTok Studio) hasta 60 min. Un vídeo de 16:9 de más de 60 s muestra un botón de pantalla completa. Aun así, para clips lo recomendable es el vertical nativo.
7. **Mayor riesgo:** la regla de contenido "no original" del For You feed y la política de propiedad intelectual. Una traducción doblada con texto propio probablemente añade valor, pero sin el permiso de Naval una sola reclamación basta para que TikTok retire el vídeo.
8. **Portada:** diséñala en 1080x1920. El título debe caber en la franja central de 1080x1440, porque la cuadrícula del perfil recorta en 3:4.
9. **Carruseles de fotos:** hasta 35 imágenes, en JPEG o WebP y de hasta 20 MB cada una por API. Tienen sentido como formato secundario para citas sueltas.

## Tabla de especificaciones

| Parámetro | App móvil | Web (TikTok Studio) | API (Content Posting) | Confianza |
|---|---|---|---|---|
| Duración máxima | 10 min grabando con la cámara; hasta 60 min subiendo desde el dispositivo, según terceros | 60 min | 10 min. El usuario puede recortar si su cuenta tiene un límite menor (3, 5 o 10 min según la cuenta) | Web [OFICIAL] por un artículo de Creator Academy de hace unos 3 años [ANTIGUO: 2023]; API [OFICIAL]; app [TERCEROS] |
| Tamaño máximo | 72 MB en Android y 287,6 MB en iOS | 10 GB según Creator Academy [ANTIGUO: 2023]. Los terceros dan 30 GB, 4 GB, 1 GB o 500 MB | 4 GB | App [TERCEROS, sin confirmar]; web [OFICIAL, antiguo] contra cifras de terceros contradictorias; API [OFICIAL] |
| Resolución | 1080x1920 recomendada; mínimo 720x1280 | "720p o superior", horizontal o vertical | 360 a 4096 px en cada lado | API [OFICIAL]; web [OFICIAL, antiguo]; el resto [TERCEROS] |
| Relación de aspecto | 9:16 nativo; 16:9 y 1:1 aceptados con bandas | igual | sin restricción citada | [TERCEROS]; anuncios: 9:16, 16:9 y 1:1 [OFICIAL] |
| fps | 30 es lo habitual; 60 admitido | — | entre 23 y 60 fps | API [OFICIAL]. La conservación de 50 fps está **no encontrada** |
| Contenedor y códec | MP4 o MOV; H.264 y AAC | igual | MP4 (recomendado), WebM o MOV; H.264 (recomendado), H.265, VP8 o VP9 | API [OFICIAL] |
| Bitrate | Los terceros dicen que por encima de unos 8 Mbps no se gana nada y que la entrega real ronda 2–4 Mbps; otros hablan de que recomprime por encima de unos 15 Mbps | — | — | [NO CONFIRMADO]. Anuncios in-feed de subasta: mínimo 516 kbps; anuncios de reserva: mínimo 2500 kbps [OFICIAL, de hace unos 470–640 días] |
| 4K | se reduce a 1080p | se reduce a 1080p | máximo 4096 px | [TERCEROS] |
| Audio | AAC. Sonoridad: lo más citado es −14 LUFS integrados y −1 dBTP de pico; también aparecen −9 a −14 y −10 a −12 | — | — | [NO CONFIRMADO]: no hay documento oficial |
| Fotos o carrusel | hasta 35 fotos; 9:16 de 1080x1920 recomendado | — | hasta 35 imágenes, JPEG o WebP, 20 MB por imagen, resolución máxima "1080p". Sin auditar, todo queda en privado | API [OFICIAL]; tamaño visual [TERCEROS] |
| Portada | 1080x1920, JPG o PNG, ≤10 MB; elegir fotograma o, según algunas fuentes, subir imagen | — | — | [TERCEROS, contradictorio] |

## Respuestas, pregunta por pregunta

### 1. Especificaciones y duración

- **Límites de subida.**
  - API: 23–60 fps, 360–4096 px por lado, ≤4 GB y ≤10 min. Fuente: Media Transfer Guide (developers.tiktok.com/doc/content-posting-api-media-transfer-guide). El buscador la marca como actualizada hace unos 100 días; no pude leer la fecha exacta. [OFICIAL]
  - Web: hasta 60 min y 10 GB en "TikTok.com y TikTok Studio" (Creator Academy, "creating-videos-longer-than-one-minute"). La página tiene unos 1100 días [ANTIGUO: 2023]. [OFICIAL]
  - Contradicción sobre el tamaño en web: otros terceros dicen 30 GB (atribuido a Creator Academy, sin verificar), 4 GB, 1 GB o 500 MB.
- **¿Conserva 50 fps?** No encontrado. Una guía de terceros recomienda evitar 24 y 25 fps "porque se recodifican", lo que sugiere que con 50 fps puede pasar lo mismo [NO CONFIRMADO]. Mi recomendación es exportar la versión de TikTok a 60 fps o a 30 fps, porque 50 no tiene ventaja en móvil y 30 o 60 son las cadencias habituales. Para salir de dudas: subir una prueba a 50 y otra a 60, descargarlas y comparar con `ffprobe -show_streams` (`r_frame_rate`, `avg_frame_rate`, `bit_rate`).
- **Duración recomendada por TikTok para la distribución:** no encontrada ninguna cifra oficial.
  - Creator Rewards solo paga vídeos de más de 60 s, y TikTok dice que valora "originalidad, tiempo de reproducción, valor de búsqueda y engagement". Fuentes: newsroom y Creator Academy. [OFICIAL]
  - No afecta directamente porque el proyecto no monetiza. Es un indicio de que TikTok empuja los vídeos de más de 1 min [inferido].
  - Los anuncios de reserva recomiendan 9–15 s dentro de 5–60 s, pero eso es para anuncios.

### 2. Zonas seguras sobre 1080x1920

**Oficial.** TikTok Ads no publica márgenes fijos. Ofrece plantillas descargables (In-Feed Standard, In-Feed with Anchor y versión árabe), y la zona segura cambia según la relación de aspecto, la longitud de la descripción y los complementos interactivos. Fuente: ads.tiktok.com, "tiktok-auction-in-feed-ads". [OFICIAL] No pude descargar las plantillas porque el dominio está bloqueado.

**Mediciones de terceros:**

| Fuente | Arriba | Abajo | Derecha | Izquierda | Área útil |
|---|---|---|---|---|---|
| Cadenus, AdaptlyPost y otras (orgánico 2026) | 130 | 484 (mínimo; crece con la descripción) | 140 | — | ~896x1470 |
| Guía que cita la plantilla In-Feed de TikTok Ads | 240 | 660 | 120 + columna de acciones | 120 | ~840x1020 |
| Otra guía de anuncios In-Feed Standard | 160 | 440 | 80 | 80 | 920x1320 |
| Guía "outlier" | 108 | 320 | 120 | 60 | 900x1492 |
| Preset conservador de una herramienta | 140 | 400 | 180 | — | — |
| Proporción | — | ~22 % (≈422 px) | ~13 % (≈140 px) | — | — |

**Qué tapa cada zona** [TERCEROS]:

- **Arriba, unos 130–160 px:** la cabecera "Siguiendo / Para ti", el icono de búsqueda y LIVE.
- **Abajo, unos 420–484 px o más:** el nombre de usuario, la descripción (puede expandirse), el nombre del sonido, la barra de progreso, la etiqueta "AI-generated" (abajo a la izquierda, según TikTok [OFICIAL]) y la barra de navegación.
- **Derecha, unos 120–180 px de ancho**, entre y ≈ 900 y 1700: el avatar, me gusta, comentarios, guardar, compartir y el disco del sonido.

**Recomendación para el tambor:**

- Caja de texto en x 60–940 (880 px de ancho) e y 160–1436.
- Para el caso conservador que cubre las descripciones largas, usa y 240–1260.
- Coloca la frase actual en y ≈ 700–900, la anterior hacia y ≈ 450–600 y la siguiente hacia y ≈ 1000–1150.
- El título del episodio va arriba, en y 170–260. El hablante va encima de la frase actual, nunca en la franja inferior.
- Deja el borde derecho del texto en x ≤ 920 a la altura de los botones (y > 900).

### 3. Vídeo horizontal 16:9

- En el feed se muestra con bandas. Ancho de 1080, así que el vídeo ocupa una franja de 1080x608 en el centro. Todo se reduce a 0,5625: un texto de 64 px en el original de 1920x1080 se ve a unos 36 px [cálculo propio].
- Si el vídeo dura más de 60 s, TikTok añade el botón "Pantalla completa" para girar el móvil. Con menos de 60 s, solo bandas negras. [TERCEROS: Kapwing y otras; la prueba empezó en dic-2022 (TechCrunch y Social Media Today) [ANTIGUO: 2022]]. No encontré confirmación oficial de 2025-2026.
- La web acepta horizontal y vertical [OFICIAL, antiguo].
- **Conclusión:** para clips de 15 s a 3 min, siempre vertical nativo. El horizontal solo tendría sentido para subir episodios largos enteros, y aun así el texto queda pequeño.

### 4. Portada

- Se elige un fotograma del vídeo. Que se pueda subir una imagen propia (JPG o PNG, ≤10 MB) es contradictorio: Moda dice que sí y SocialRails que no. [TERCEROS]
- La cuadrícula del perfil recorta al centro en unos 3:4: zona visible de unos 1080x1440, con unos 240 px perdidos arriba y otros tantos abajo. Es una estimación de SocialRails, no una especificación. [NO CONFIRMADO] No encontré ningún anuncio oficial del cambio a 3:4; el cambio documentado de enero de 2025 es el de Instagram.
- **Recomendación:** pon un fotograma de portada al inicio del clip, de 0,1–0,5 s, con el título en y 300–1400 y el texto dentro del 80 % central.
- El editor de la app permite poner texto de portada sobre el fotograma [TERCEROS].

### 5. Subtítulos automáticos

- **Oficial (newsroom, "Introducing auto captions" [ANTIGUO: 2021]):**
  - Quien crea el vídeo los activa en la pantalla de edición y puede editar el texto.
  - Quien lo ve puede apagarlos desde el panel de compartir, en el botón de subtítulos.
- No encontré confirmación de que se pueda subir un .srt de forma nativa. La mayoría de terceros dice que no y recomienda incrustar el texto. [TERCEROS]
- **Posición:** por defecto, cerca de la parte inferior, donde está la descripción. Si se pueden arrastrar es contradictorio: unas guías dicen que sí, Opus dice que no.
- **Para este proyecto:** no los actives. El texto incrustado ya cumple esa función y evita que salgan dos textos superpuestos.

### 6. Audio

- AAC estéreo, 44,1 o 48 kHz, unos 128–320 kbps [TERCEROS].
- **Sonoridad:** no hay especificación oficial. Lo más citado es −14 LUFS integrados con pico de −1 dBTP [NO CONFIRMADO]; otras fuentes dan −9 a −14 o −10 a −12. No está claro si TikTok sube el volumen de lo que llega bajo.
- **Recomendación:** masterizar los clips a −14 LUFS y −1 dBTP. Es el mismo objetivo que YouTube, así que se reutiliza el master.
- **Voz sintética** [OFICIAL, página "Supporting responsible, transparent AI-generated content" y Community Guidelines 2025H2]:
  - Hay que etiquetar el contenido de IA realista y el audio que imita la voz de una persona real.
  - El TTS genérico que no es reconocible como una persona concreta no necesita etiqueta.
  - Si las voces XTTS están clonadas de Naval o de Nivi, se aplica la obligación de etiquetar. Es más: crear contenido que parezca que una figura pública dice algo puede estar prohibido aunque se etiquete, si induce a error. Para un podcast traducido y declarado probablemente no induce a error [inferido].
  - El interruptor "AI-generated content" añade la etiqueta "Disclosed by creator as AI-generated" abajo a la izquierda. La etiqueta que pone la plataforma (por C2PA o por la marca de agua invisible) no la puede quitar el creador.
- **Novedad de nov-2025** (TechCrunch, 18-11-2025): cada usuario tiene un control en Ajustes > Preferencias de contenido > Administrar temas para ver menos contenido de IA, y TikTok prueba marcas de agua invisibles. **Efecto:** un vídeo etiquetado como IA puede llegar a menos gente entre los usuarios que bajen ese control [inferido]. No hay penalización documentada para el resto.

### 7. Recompresión y calidad

- El ajuste "Subir en HD" o "Permitir subidas en alta calidad" está en "Más opciones" de la pantalla de publicación de la app. Viene desactivado por defecto y se queda activado una vez se enciende. En la web estaría activado por defecto. [TERCEROS, sin confirmar oficialmente]
- 4K no aporta nada porque se reduce a 1080p. Para texto fino, 1080p nativo es mejor que dejar que TikTok reescale el 4K [TERCEROS e inferido].
- Diferencia de calidad entre subir desde el móvil y desde la web: no hay mediciones publicadas. Que la web acepte ficheros grandes (≥4 GB) permite subir con un bitrate alto sin la recompresión previa que hace el móvil al exportar [inferido].
- **Recomendación para texto:** fuente de ≥48 px para las frases atenuadas y ≥72 px para la actual, sin trazos de menos de 3 px, fondo plano oscuro (los degradados generan bandas al recomprimir), H.264 High a 1080p con 10–15 Mbps, y subirlo desde la web.

### 8. Contenido con mucho texto o "de lectura"

- **Hay riesgo oficial.** En la elegibilidad del For You feed (Creator Academy y la página de política de originalidad):
  - no son elegibles el contenido "reproducido o no original subido sin ediciones nuevas o creativas" ni el que es "una combinación de fuentes con poco valor añadido";
  - entre los ejemplos de baja calidad están las "imágenes de baja calidad o slide videos".
- Un tambor animado de texto sobre audio doblado se acerca a "slide video" [inferido, NO CONFIRMADO]. Para reducir el riesgo:
  - dale movimiento real (la animación del tambor);
  - añade una marca visual propia;
  - deja visible que es una traducción y un doblaje propios;
  - no reutilices logos ni marcas de agua de terceros (un logo ajeno expulsa explícitamente del For You feed).
- La elegibilidad se puede recurrir durante 80 días [OFICIAL].
- **Indexación del texto en pantalla para la búsqueda:** muchos terceros de SEO dicen que TikTok aplica OCR al texto en pantalla y reconocimiento de voz al audio. No encontré confirmación oficial de TikTok [NO CONFIRMADO]. Aun así, incluir en la descripción palabras clave en español ("Naval Ravikant en español", el tema del clip) es lo único verificable que se controla.

### 9. Carruseles de fotos

- **API [OFICIAL]:** hasta 35 imágenes, JPEG o WebP, ≤20 MB por imagen, resolución máxima "1080p" (sin especificar el aspecto). Las URL tienen que estar en un dominio verificado. Una app sin auditar solo publica en privado.
- **En la app [TERCEROS]:** 9:16 de 1080x1920 recomendado. El mínimo de imágenes es contradictorio (2 o 4).
- **Encaje en el proyecto:** sirve para hilos de citas de un episodio, por ejemplo 5–10 tarjetas de 1080x1920 con una frase cada una, la misma zona segura y audio del episodio.
  - Son baratos de generar con el mismo renderizador (un fotograma por frase).
  - El riesgo de que se consideren "slide" o de baja calidad es mayor que con el vídeo [inferido].
  - Formato secundario, no principal.

### 10. Derechos (aplicado al caso)

- Política de propiedad intelectual [OFICIAL]: TikTok retira el contenido infractor y banea las cuentas reincidentes. Admite excepciones (fair use o fair dealing), pero una traducción es una obra derivada.
- Entre jul y dic de 2025 recibió más de 470 000 solicitudes y retiró 4,9 M de elementos por propiedad intelectual (transparency report).
- **Sin el permiso de Naval**, basta una reclamación para que retiren el vídeo y la cuenta acumule faltas. Hay que conseguir el permiso antes de publicar en volumen.

## Qué evitar

- Subir 4K o 1440p: se reduce y se recomprime dos veces.
- Exportar a 25 o 50 fps sin haberlo probado; mejor 30 o 60.
- Poner texto por debajo de y = 1436 o en x > 940 entre y 900 y 1700, o el título por encima de y = 160.
- Centrar la frase actual en y = 960: queda demasiado cerca de la descripción.
- Activar los subtítulos automáticos de TikTok además del texto incrustado.
- Publicar con voces clonadas de personas reales sin activar la etiqueta de IA.
- Publicar con logos o marcas de agua de nav.al, de YouTube o de otras apps.
- Subir 16:9 en clips de menos de 60 s: solo bandas, sin botón de pantalla completa.
- Fondos con degradados finos o texto con trazo fino de 1–2 px, que se estropean al recomprimir.
- Usar la API sin auditar esperando publicar en público: todo queda en privado.

## Dudas abiertas / no confirmado

- Si TikTok conserva los 50 fps o los convierte a 30 (no encontrado; hay que probarlo).
- El tamaño máximo actual por la web: 10 GB oficial pero antiguo, contra 30, 4, 1 GB o 500 MB en terceros. Y los límites de la app (72 MB y 287,6 MB, solo terceros).
- Las plantillas oficiales de zona segura de TikTok Ads: no descargadas por el bloqueo de dominio. Tampoco hay zona segura orgánica oficial.
- El bitrate de entrega real y el objetivo de sonoridad: ninguno de los dos es oficial.
- Si se puede subir una portada personalizada y el recorte exacto de la cuadrícula a 3:4.
- Si los subtítulos automáticos se pueden mover y si se puede subir un .srt.
- Si el OCR del texto en pantalla alimenta la búsqueda.
- Si un "tambor" de texto cuenta como "slide video" para el For You feed.
- La regla actual del botón de pantalla completa para 16:9 (fuentes de 2022 y de terceros).
- Si las voces XTTS del proyecto son reconocibles como Naval o Nivi: eso decide si la etiqueta de IA es obligatoria. Recomiendo etiquetar siempre.

## Fuentes

**Oficiales** (fecha: la que indica el buscador, o la de consulta, 18-11-2026):

- TikTok for Developers, Media Transfer Guide (actualizada hace unos 100 días): https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide
- TikTok for Developers, Upload / Direct Post / Photo Post: https://developers.tiktok.com/docs/en/content-posting-api-reference-upload-video · https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post · https://developers.tiktok.com/docs/en/content-posting-api-reference-photo-post
- Creator Academy, vídeos de más de 1 min (hace unos 1100 días) [ANTIGUO: 2023]: https://tiktok.com/creators/creator-portal/en-us/tiktok-content-strategy/creating-videos-longer-than-one-minute
- TikTok Ads, Auction In-Feed Ads (hace unos 470–640 días): https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads
- TikTok Ads, Reservation In-Feed: https://ads.tiktok.com/resources/help/article/tiktok-reservation-in-feed-ads-reach-frequency?lang=en
- TikTok Ads, Video Ads Specifications: https://ads.tiktok.com/help/article/video-ads-specifications
- Política de contenido de IA: https://www.tiktok.com/safety/en/policies-and-engagement/supporting-responsible-transparent-ai-generated-content
- Community Guidelines, Integrity & Authenticity (2025H2): https://www.tiktok.com/community-guidelines/en-GB/integrity-authenticity?cgversion=2025H2update
- Newsroom, etiquetas de IA: https://newsroom.tiktok.com/en-us/new-labels-for-disclosing-ai-generated-content
- Estándares de elegibilidad del For You feed: https://www.tiktok.com/safety/en/policies-and-engagement/fyf-standards
- Creator Academy, política de originalidad: https://www.tiktok.com/creator-academy/article/tiktok-originality-policy
- Creator Rewards: https://www.tiktok.com/creator-academy/article/creator-rewards-program/?lang=en
- Newsroom, Auto captions [ANTIGUO: 2021]: https://newsroom.tiktok.com/en-us/introducing-auto-captions
- Política de propiedad intelectual: https://www.tiktok.com/legal/page/global/copyright-policy/en
- Informe de propiedad intelectual (jul–dic 2025): https://www.tiktok.com/transparency/en/intellectual-property-removal-requests/

**Terceros:**

- TechCrunch, control de contenido de IA y marca de agua invisible (18-11-2025): https://techcrunch.com/2025/11/18/tiktok-now-lets-you-choose-how-much-ai-generated-content-you-want-to-see/
- Cadenus, zona segura 2026: https://cadenus.io/resources/blog/tiktok-safe-zone/
- AdaptlyPost, zonas seguras 2026: https://adaptlypost.com/blog/social-media-safe-zones-2026-complete-guide
- PostPlanify, zonas seguras 2026: https://postplanify.com/blog/social-media-safe-zones-2026-complete-guide
- Revid, zona segura: https://www.revid.ai/tiktok-safe-zone
- Relevant Audience, especificaciones de anuncios: https://www.relevantaudience.com/tiktok-ads/tiktok-video-size-ad-specs/
- TryMyPost, especificaciones de anuncios 2026: https://www.trymypost.com/blog/tiktok-ad-specs-2026-safe-zones
- Emplifi, especificaciones de anuncios: https://emplifi.io/resources/blog/tiktok-ad-specs
- Kapwing, TikTok horizontal: https://kapwing.com/resources/horizontal-tiktoks
- Social Media Today, prueba de pantalla completa (2022): https://www.socialmediatoday.com/news/TikTok-Tests-Horizontal-Full-Width-Video-Display/638786/
- SocialRails, tamaño de miniatura: https://socialrails.com/blog/tiktok-thumbnail-size-guide
- Moda, miniatura: https://moda.app/resources/sizes/tiktok-thumbnail
- Postfa.st, carrusel: https://postfa.st/sizes/tiktok/carousel
- OpenClip, tamaño de slideshow: https://openclip.app/learn/tiktok-slideshow-size
- OpenClip, normalización de audio: https://openclip.app/learn/audio-normalization
- Metricool, duración de vídeos: https://metricool.com/tiktok-video-length/
- Search Engine Land, prueba de 60 min (2024): https://searchengineland.com/tiktok-testing-60-minute-video-uploads-440588
- Submagic, subida en alta calidad: https://www.submagic.co/blog/high-quality-upload-tiktok
- Gadget Hacks, ajuste HD: https://smartphones.next.gadgethacks.com/how-to/hidden-setting-is-trick-uploading-hd-videos-your-tiktok-profile-0384314
- Compresto, compresión para TikTok (2026): https://compresto.app/blog/compress-video-for-tiktok
- Ayrshare, guía de medios: https://www.ayrshare.com/docs/media-guidelines/tiktok
- Opus, subtítulos: https://www.opus.pro/blog/how-to-add-captions-on-tiktok
- Iamtypist, subtítulos y SRT: https://iamtypist.dev/blog/how-to-add-captions-on-tiktok
- SEO Sherpa, búsqueda en TikTok 2026: https://seosherpa.com/tiktok-search-engine/

---

## Informe 4: Spotify, LinkedIn, X y otras plataformas

# Investigador 4/6: Spotify, Apple Podcasts, LinkedIn, X, Threads, Bluesky, Pinterest y Snapchat

**Limitación de método:** desde esta sesión no se pudieron abrir `support.spotify.com`, `www.linkedin.com` ni `help.x.com`. El proxy los bloquea y habría que permitir esos dominios en la red de la sesión. Los datos de esas páginas oficiales vienen de los extractos de búsqueda que las citan, no de una lectura directa. `developer.apple.com` sí se leyó entero. Fecha de consulta de todo: **18-nov-2026**.

## Resumen accionable

1. **Spotify (episodio largo):** se sube **solo en 16:9, 1920x1080**, H.264 + AAC-LC, MP4, a 50 fps (admitido). Un vídeo vertical se muestra con bandas negras. Como el RSS es propio y no de un host socio, la vía es subir el vídeo a mano en Spotify for Creators sobre el episodio que ya llegó por RSS. Ese vídeo solo se ve en Spotify y no se puede monetizar (da igual, no monetizamos). Hay una página oficial que se contradice; ver sección 1.
2. **Spotify Clips:** duran **de 15 a 90 s**, con un mínimo de 768x1024, hasta 1 GB, en MP4 o MOV. Se recomienda vertical. Se admite **un clip por episodio** y solo se sube desde la web. **Que lo admitan los podcasts con RSS externo no está confirmado.** Los clips de 90 s a 3 min no caben en Spotify.
3. **Apple Podcasts:** el vídeo HLS **solo entra a través de un host con acceso al Podcasts Connect API**, así que un RSS propio no puede. El MP4 clásico en `<enclosure>` sigue funcionando [TERCEROS], pero un episodio de 4 h pesa entre 2 y 9 GB por fichero. **No merece la pena:** Apple sigue recibiendo el audio por RSS y nada más.
4. **X:** el clip vertical de 1080x1920 cabe en una cuenta gratuita si dura **≤140 s y pesa ≤512 MB**. Con Premium se puede subir el episodio largo: hasta 4 h en web e iOS y 10 min en Android. Admite **.srt** subido desde la web. X tiene audiencia hispanohablante relevante. **Prioridad media-alta.**
5. **Bluesky:** **sí admite 3 min.** Desde agosto de 2026 el límite es de **10 min y 300 MB** [TERCEROS, a partir del anuncio de @bsky.app]. **Threads:** 5 min y 1 GB [TERCEROS]. Basta con reutilizar el mismo MP4 vertical.
6. **LinkedIn:** admite de 1:2.4 a 2.4:1, hasta 5 GB, de 10 a 60 fps, y de 15 min en escritorio o 10 min en móvil. El .srt solo se sube desde escritorio. **Prioridad baja:** la audiencia es profesional y está más en inglés. Si se usa, que sea con el mismo vertical.
7. **Pinterest y Snapchat Spotlight: ignorar.** No hay especificaciones oficiales verificables ni zonas seguras publicadas, y no encajan con un vídeo de lectura en español.
8. **Riesgo de derechos (crítico):** en **mayo de 2026 Spotify anunció que retira los programas que imitan la voz o la imagen de otro creador sin permiso, también con clonación de voz por IA.** Si el XTTS usa como referencia la voz real de Naval, sin su permiso, **el canal entero puede ser retirado.** Esto aplica igual a las demás plataformas.
9. **Formatos a renderizar:** (a) 1920x1080 a 50 fps, para YouTube, Spotify y X Premium; (b) **1080x1920 a 50 fps de ≤140 s**, que vale para X gratis, Threads, Bluesky, LinkedIn y Spotify Clips si dura ≤90 s; (c) opcionalmente, una versión de ≤90 s para Spotify Clips.

## Tabla de especificaciones

| Plataforma / formato | Resolución recomendada | Aspecto | fps | Duración máx. | Tamaño máx. | Códec / contenedor | .srt | Confianza |
|---|---|---|---|---|---|---|---|---|
| Spotify, episodio de vídeo | ≥1080p (1920x1080) | 16:9 (otros con bandas) | 24, 25, 30, **50**, 60; progresivo | recomendado <4 h; admitido hasta 12 h | recomendado <10 GB; admitido hasta 60 GB | H.264, MP4 (MOV admitido; FLV y AVI no); AAC-LC ≥128 kbps estéreo; SDR Rec.709; 1 keyframe/s recomendado (obligatorio al menos 1 cada 60 s); 25 Mbps CBR orientativo a 1080p | no encontrado (Spotify genera transcripción propia) | [OFICIAL] |
| Spotify, miniatura de vídeo | 1920x1080 | 16:9 | — | — | no encontrado | imagen | — | [OFICIAL] |
| Spotify, portada del programa | 3000x3000 (mín. 640x640) | 1:1 | — | — | 4 MB [TERCEROS] | JPG, PNG | — | [TERCEROS] |
| Spotify Clips | mín. 768x1024; recomendado vertical 1080x1920 | se recomienda vertical; horizontal admitido | no especificado | **15–90 s** | 1 GB | MP4, MOV; con audio obligatorio | subtítulos generados y revisados en S4C | [OFICIAL] + [TERCEROS: Reap, oct-2026] |
| Apple Podcasts, HLS | escalera adaptativa | no especificado | keyframe cada 2–6 s, GOP cerrado | — | — | H.264 / HEVC; AAC-LC 48 kHz 192 kbps estéreo; Rec.709 | WebVTT dentro de HLS | [OFICIAL] |
| Apple Podcasts, MP4 por RSS | — | — | — | — | — | MP4 / M4V en `<enclosure>` | no | [TERCEROS] |
| LinkedIn, vídeo orgánico | de 256x144 a 4096x2304 | de 1:2.4 a 2.4:1 | 10–60 | 15 min en escritorio; 10 min en móvil; mín. 3 s | de 75 KB a 5 GB | MP4 H.264 recomendado | **sí**, solo desde escritorio | [OFICIAL] (duración: [TERCEROS]) |
| X, cuenta gratuita (app/web) | 1920x1080 / 1080x1920 [TERCEROS] | de 1:3 a 3:1 (API heredada) | ≤60 | **140 s** | **512 MB** | MP4 H.264 + AAC | **sí**, desde la web | [OFICIAL heredado] + [TERCEROS] |
| X Premium (app/web) | ídem | ídem | ≤60 | 4 h en web e iOS; **10 min en Android** | hasta 16 GB [TERCEROS] (otros dicen 8 GB) | ídem | sí | [TERCEROS] citando el Help Center |
| X por API (desde 1-sep-2026) | — | — | — | 20 min estándar; 125 min Premium | 8 GB estándar; 16 GB Premium | — | — | [TERCEROS] citando el changelog |
| Threads | 1080x1920 | 9:16 recomendado | no encontrado | **5 min** | 1 GB | MP4 / MOV | no encontrado | [TERCEROS] |
| Bluesky | 1080x1920 | 9:16 / 16:9 | no encontrado | **10 min** (desde 25–26 ago 2026; antes 3 min) | **300 MB** (antes 100 MB) | MP4 | no encontrado | [TERCEROS] |
| Pinterest, vídeo | 1080x1920 o 1000x1500 | 9:16 / 2:3 | — | de 4 s a 15 min (otra fuente: 5 min) | 2 GB | MP4 / MOV, H.264 + AAC | no encontrado | [NO CONFIRMADO] |
| Snapchat Spotlight | 1080x1920 | 9:16 | — | 3 min [TERCEROS: Kompozy] | no encontrado | MP4 | no | [NO CONFIRMADO] |

## Respuestas pregunta por pregunta

### 1. Spotify for Creators: vídeo de podcast

**Especificaciones** [OFICIAL, support.spotify.com/creators/article/video-specs]:
- 1080p o más, H.264, MP4 (MOV admitido).
- 24, 25, 30, 50 o 60 fps, progresivo.
- SDR Rec.709; el HDR se convierte a SDR.
- 16:9 recomendado.
- Audio AAC-LC a ≥128 kbps, estéreo.
- Keyframe cada 1 s recomendado; obligatorio al menos 1 cada 60 s.
- Duración recomendada <4 h, admitida hasta 12 h.
- Tamaño recomendado <10 GB, admitido hasta 60 GB.
- Una copia regional de la página dice «180p» como mínimo. Una guía de terceros (vidpros) lo interpreta como mínimo real («no pensado para usarse»).

**Qué implica para nosotros:**
- **50 fps vale.**
- Un episodio de 4 h a 1080p necesita un bitrate bajo para no pasar de 10 GB: 10 GB son ~5,5 Mbps de media en 14 400 s. Un vídeo de texto sobre fondo fijo comprime muy bien, así que **2–4 Mbps en CRF es suficiente**. La cifra de 25 Mbps CBR es para vídeo filmado.
- Para un 4 h, el umbral de 10 GB no es negociable en la práctica, aunque se admitan 60 GB.

**Vertical:** las guías de terceros dicen que «los vídeos que no son 16:9 llevan bandas negras» (vidpros, 2026). **Para Spotify se sube la versión 16:9, nunca la vertical.**

**«Replace audio with video» con RSS externo:**
- La página oficial «Publishing video episodes if you're not hosted with Spotify» (versión US, consultada vía búsqueda) dice:
  - Si el host no es socio con Distribution API (Audioboom, Audiomeans, Libsyn, Podigee, Podspace, en vigor desde el 14-may-2026), **se pueden reemplazar episodios de audio por vídeo directamente en Spotify for Creators**.
  - Pasos: Episodes → «⋯» → Upload video → Preview → Publish.
  - Ese vídeo **solo está en las apps de Spotify y en el reproductor web**. El RSS sigue llevando audio a las demás apps y no se duplican episodios.
  - Esos episodios **no se pueden monetizar**.
  - Si ya subiste vídeo por el API del host, no puedes usar esta vía.
- **Contradicción:** otra versión de la página «Replacing an existing episode with video», fechada el 26-mar-2026, dice que la función es **solo para programas alojados en Spotify**. La versión más reciente y RSS.com dicen lo contrario. [NO CONFIRMADO cuál rige]
- **Hay que verificarlo en la cuenta real**: entrar en S4C con el programa reclamado por RSS y ver si aparece «Upload video».

**Interfaz en móvil:** **no encontrado.** No hay ninguna fuente oficial ni de terceros con rectángulos en px de lo que tapa el reproductor de vídeo de Spotify. Se buscó en support.spotify.com, creators.spotify.com y guías de 2026.
- Inferencia [NO CONFIRMADO]: en horizontal dentro de la app, la barra de controles y el título van debajo o encima del vídeo; a pantalla completa los controles se superponen de forma temporal.
- Regla prudente: deja libres **~90 px abajo y ~60 px arriba sobre 1920x1080** (el área de acción del 5 %, estándar de TV) para el título y la frase inferior.

### 2. Spotify Clips

- **Qué son:** vídeos cortos asociados a un episodio que aparecen en la página del episodio y en los feeds de descubrimiento de Spotify («Clips y Previews»). [OFICIAL + TERCEROS]
- **Especificaciones** [OFICIAL, support.spotify.com/us/creators/article/clips-content-policy]:
  - **15–90 s**, mínimo 768x1024, ≤1 GB, MP4 o MOV, con audio obligatorio.
  - Se recomienda vertical; horizontal admitido.
- **Cómo se suben** [OFICIAL, …/article/clips]: **solo desde Spotify for Creators web**, **un clip por episodio**. Se revisan los subtítulos automáticos.
- **Programas no alojados en Spotify:** **no confirmado.** Ninguna fuente dice si un programa reclamado por RSS puede subir Clips. La página de monetización empuja a «cambiar el host a Spotify for Creators».
- **Qué cambia en nuestro caso:**
  - Los clips de 90 s a 3 min no sirven aquí. Hay que cortar una versión de ≤90 s.
  - Con un solo clip por episodio, hay que elegir el mejor fragmento.
  - Política de contenido de Clips: hay que respetar los derechos de terceros. Ver el riesgo de derechos más abajo.
- **Spotify Clips para artistas** es otro producto: menos de 30 s y mín. 1280x720. Dejó de aceptar clips nuevos el 17-jun-2026 [TERCEROS: Syntax Academy]. **No aplica.**
- **Portadas:**
  - Miniatura de episodio de vídeo: **16:9, 1920x1080 sugerido** [OFICIAL, …/article/thumbnails].
  - Portada del programa: **1:1, 3000x3000**; mínimo 640x640, JPG o PNG, 4 MB [TERCEROS].

### 3. Apple Podcasts y vídeo

- **HLS (2026)** [OFICIAL, developer.apple.com/documentation/http-live-streaming/hls-for-podcasts]:
  - El vídeo HLS se asocia a episodios RSS normales **mediante el Podcasts Connect API**. Ese API es para hosts, que piden acceso con una encuesta.
  - No entra por una etiqueta del RSS. Lo confirman Podder y Triton: «Apple no consume HLS desde RSS».
  - Socios de lanzamiento: Acast, ART19, Omny y Simplecast; después Transistor, Podbean, Captivate, RSS.com, Podigee, Blubrry y Flightcast [TERCEROS].
  - Spotify anunció en mayo de 2026 que su vídeo llegará también a Apple vía HLS, para programas alojados en Spotify o Megaphone [TERCEROS: ppc.land].
- **Codificación** [OFICIAL, …/encoding-media]:
  - Varias calidades, H.264 o HEVC.
  - Keyframe cada **2–6 s** (con 50 fps: 100–300 frames), GOP cerrado, 2–3 B-frames (H.264).
  - Rec.709.
  - Audio AAC-LC a **48 kHz y 192 kbps**, estéreo.
  - Subtítulos en WebVTT.
  - No hay requisitos publicados de aspecto ni de resolución en esa página.
- **MP4 clásico en `<enclosure>`:** «el MP4 vía RSS sigue soportado» y ahora se reproduce bien a pantalla completa [TERCEROS: Triton, 17-feb-2026; Podcast Rex]. No encontrado en documentación de Apple de 2025-2026.
- **¿Merece la pena?** **No.**
  - Con un RSS propio no hay acceso a HLS.
  - La alternativa es un MP4 en el enclosure, que **sustituiría al audio** en ese feed o exigiría un segundo feed de vídeo. Un episodio de 4 h a 1080p con 1,5–5 Mbps pesa 2,7–9 GB: es ancho de banda caro y sin ganancia para un vídeo de lectura.
  - Hay que mantener Apple solo con audio.

### 4. LinkedIn

- **Límites oficiales** [OFICIAL, linkedin.com/help/linkedin/answer/a548372, citada vía búsqueda]:
  - De 75 KB a 5 GB.
  - De 256x144 a 4096x2304.
  - De 10 a 60 fps (50 fps vale).
  - De 1:2.4 a 2.4:1, así que admite 16:9, 1:1, 4:5 y 9:16.
- **Duración:** 15 min en escritorio y 10 min en móvil, mínimo 3 s [TERCEROS, coinciden varias guías de 2026].
- **Subtítulos:** **.srt** adjunto antes de publicar, **solo desde escritorio**, en perfiles y en páginas [OFICIAL, answer/a552177]. Editable después con «⋯ → Edit captions». Formato estricto: número de secuencia obligatorio y `HH:MM:SS,mmm --> …` con un solo espacio a cada lado de la flecha [TERCEROS].
- **Pestaña o feed vertical:** existe un carril de vídeo vertical [NO CONFIRMADO: blogs de marketing, sin anuncio oficial encontrado].
- **Zonas tapadas en 9:16** [NO CONFIRMADO, blog sin fuente]: ~150 px arriba, **~300 px abajo** y ~100 px a la derecha. Área segura central de ~980x1470.
- **Portada:** no encontrado como especificación oficial para vídeo orgánico.
- **¿Tiene sentido?** Poco. La audiencia de LinkedIn es profesional y en gran parte anglófona, y Naval tiene tirón ahí en inglés. Se puede publicar el mismo vertical de ≤10 min sin coste extra. **Prioridad baja.**

### 5. X (Twitter)

- **Cuenta gratuita:** **140 s y 512 MB** [TERCEROS citando el Help Center; coincide con la página heredada del API, «0,5–140 s, 512 MB»].
- **Premium:**
  - **Hasta 4 h en web e iOS, 10 min en Android** [TERCEROS citando el Help Center].
  - Tamaño: 16 GB según opentweet (oct-2026); otras fuentes dicen 8 GB. Otra fuente da «2 h a 1080p» [discrepancia].
- **API** (changelog del 1-sep-2026, vía opentweet): 20 min y 8 GB en estándar; 125 min y 16 GB en Premium.
- **Resolución, fps y bitrate:**
  - Página heredada del API: 32x32 a 1280x1024, ≤60 fps, aspecto de 1:3 a 3:1.
  - Media Studio FAQ: máximo 1920x1080 horizontal [OFICIAL].
  - Terceros: 1920x1200 y 1200x1900, 25 Mbps [NO CONFIRMADO].
  - Quickstart nueva del API: mín. 5000 kbps, 30 o 60 fps.
  - **Implicación: 50 fps entra en «≤60», pero las recomendaciones solo nombran 30 y 60.** Si se ve tartamudeo, exportar a 30 o 60 [inferido].
- **Timeline:** el vertical se muestra reducido o recortado en el feed y a pantalla completa en el visor inmersivo [TERCEROS, contradictorio]. No hay documentación oficial del recorte.
- **.srt:** sí, uno por vídeo, subido desde el compositor web (botón bajo el vídeo); el espectador lo activa con «CC» [OFICIAL, help.x.com/en/using-x/upload-caption-srt-file].
- **Zonas tapadas en el visor vertical** [NO CONFIRMADO, texto truncado de terceros]: **~400 px abajo y ~140 px a la derecha** sobre 1080x1920.
- **Qué cambia en nuestro caso:**
  - El clip de ≤2:20 cabe en una cuenta gratuita.
  - El episodio largo exige Premium.
  - X tiene una política de medios sintéticos y manipulados; no se investigó en detalle en este encargo.

### 6. Threads y Bluesky

- **Threads:** **5 min** (subió de 90 s en julio de 2024) y **1 GB**; 1080x1920 recomendado [TERCEROS: Ayrshare, Postfast, socialk.it]. No se encontró documentación de Meta.
- **Bluesky:**
  - **Sí admite 3 min**: 3 min y 100 MB desde el 10-mar-2025 (v1.99) [TERCEROS: TechCrunch, MacRumors].
  - **Desde el 25–26 de agosto de 2026: 10 min y 300 MB**, con subidas más rápidas. El anuncio fue de @bsky.app [TERCEROS: Engadget, TechTimes del 27-ago-2026, opentweet].
  - Algunas fichas aún dicen 100 MB [discrepancia].
- Para ambas sirve el mismo MP4 vertical.

### 7. Pinterest y Snapchat Spotlight

- **Pinterest:**
  - 9:16 (1080x1920) o 2:3 (1000x1500).
  - Duración de 4 s a 15 min (otra fuente: 5 min).
  - 2 GB, MP4 o MOV, H.264 + AAC.
  - Todo [NO CONFIRMADO, solo terceros]. **No se encontró ninguna zona segura en px.**
- **Snapchat Spotlight:**
  - 1080x1920, 3 min por subida [TERCEROS: Kompozy, mar-2026].
  - No se encontró confirmación de 5 min ni zonas seguras.
- **Recomendación: ignorar ambas.** Pinterest es visual y aspiracional, y Snapchat tiene un público joven de consumo rápido. No hay datos oficiales verificables, y un podcast de lectura en español no encaja.

## Tabla comparativa final y prioridades

| Plataforma | Formato a usar | Resolución | Aspecto | fps | Duración máx. | Tamaño máx. | Códec | .srt | Prioridad |
|---|---|---|---|---|---|---|---|---|---|
| Spotify (episodio) | largo horizontal | 1920x1080 | 16:9 | 50 ok | 12 h (rec. <4 h) | 60 GB (rec. <10 GB) | H.264 / AAC, MP4 | no | **Alta** (ya decidido) |
| Spotify Clips | corto | 1080x1920 (mín. 768x1024) | vertical | no especificado | 90 s | 1 GB | MP4 / MOV | auto | Media, si se habilita con RSS externo |
| Apple Podcasts | solo audio | — | — | — | — | — | — | — | Vídeo: **descartar** |
| X | corto (gratis) / largo (Premium) | 1080x1920 / 1920x1080 | 1:3–3:1 | ≤60 | 140 s / 4 h | 512 MB / 8–16 GB | H.264 / AAC | **sí** | **Media-alta** |
| Bluesky | corto | 1080x1920 | libre | no encontrado | 10 min | 300 MB | MP4 | no encontrado | Media (coste cero) |
| Threads | corto | 1080x1920 | 9:16 | no encontrado | 5 min | 1 GB | MP4 | no encontrado | Media (coste cero) |
| LinkedIn | corto | 1080x1920 | 1:2.4–2.4:1 | 10–60 | 10 min (móvil) / 15 min (escritorio) | 5 GB | H.264 | **sí** (escritorio) | Baja |
| Pinterest | — | 1080x1920 | 9:16 / 2:3 | — | 5–15 min [discrepancia] | 2 GB | H.264 | — | **Descartar** |
| Snapchat Spotlight | — | 1080x1920 | 9:16 | — | 3 min | — | — | no | **Descartar** |

**Regla práctica para el vertical común:**
- 1080x1920, 50 fps, H.264 High, AAC-LC 48 kHz a 128–192 kbps.
- **≤140 s y ≤512 MB**, para que el mismo fichero valga en X gratis, Threads, Bluesky (≤300 MB) y LinkedIn. Para Bluesky, ojo: 300 MB en 140 s son unos 17 Mbps, de sobra.
- Una versión de ≤90 s para Spotify Clips.
- Zona de texto prudente, sumando lo peor de cada plataforma: **arriba ≥150 px, abajo ≥400 px, derecha ≥140 px, izquierda ≥60 px.** Sale de cifras [NO CONFIRMADO] de LinkedIn y X; los otros investigadores (TikTok, Reels, Shorts) pueden afinarlas.

## Qué evitar

- Subir la versión vertical como episodio de Spotify: sale con bandas negras.
- Codificar el episodio de 4 h a 25 Mbps: unos 45 GB. Hay que bajar a 2–4 Mbps (CRF) para quedarse por debajo de 10 GB.
- GOP abierto o keyframes cada más de 60 s. Spotify lo exige; Apple pide de 2 a 6 s y GOP cerrado.
- Montar un MP4 en el enclosure del RSS propio para Apple.
- Clips de más de 90 s para Spotify, o de más de 140 s si la cuenta de X es gratuita.
- `.srt` con dobles espacios alrededor de `-->` o sin número de secuencia (LinkedIn los rechaza).
- **Publicar con una voz clonada de Naval sin su permiso.** Spotify (mayo de 2026) retira programas y episodios que imitan la voz de otro creador mediante clonación de voz por IA. Una voz TTS genérica y no clonada, con el carácter sintético declarado, reduce ese riesgo, aunque no resuelve los derechos del texto traducido.

## Dudas abiertas / no confirmado

- **«Replace audio with video» con RSS externo:** la versión de la página del 26-mar-2026 dice «solo para alojados en Spotify»; la versión US actual dice que sí está disponible. Hay que comprobarlo en la cuenta real.
- **Spotify Clips con RSS externo:** no encontrado.
- **Zonas tapadas del reproductor de vídeo de Spotify en móvil:** no encontrado en ninguna fuente.
- **X:** la resolución máxima real en la app (1920x1080 frente a 1920x1200), el tamaño en Premium (8 o 16 GB) y si 50 fps se reprocesa o no.
- **Rectángulos de zonas tapadas en LinkedIn y X:** solo hay blogs sin fuente.
- **Threads:** fps y .srt, y si el límite de 5 min sigue vigente en noviembre de 2026 (no hay fuente de Meta).
- **Bluesky:** 300 MB frente a 100 MB.
- **Políticas de medios sintéticos y de contenido reutilizado de X, LinkedIn, Threads y Bluesky:** no se investigaron a fondo en este encargo.
- **Páginas no leídas directamente:** `support.spotify.com`, `linkedin.com` y `help.x.com` estaban bloqueados por la red de la sesión. Si se permiten, conviene releer las páginas oficiales citadas.

## Fuentes (consulta: 18-nov-2026)

- Spotify, Video specs: https://support.spotify.com/us/creators/article/video-specs/ (sin fecha visible) [OFICIAL]
- Spotify, Publishing video episodes if you're not hosted with Spotify: https://support.spotify.com/us/creators/article/video-episodes-for-shows-not-hosted-with-spotify/ [OFICIAL]
- Spotify, Replacing an existing episode with video: https://support.spotify.com/us/creators/article/replacing-an-existing-episode-with-video/ (una versión regional fechada el 26-mar-2026) [OFICIAL]
- Spotify, Clips content policy: https://support.spotify.com/us/creators/article/clips-content-policy/ [OFICIAL]
- Spotify, Clips: https://support.spotify.com/us/creators/article/clips [OFICIAL]
- Spotify, Thumbnails: https://support.spotify.com/us/creators/article/thumbnails/ [OFICIAL]
- Spotify, Expanding our video ecosystem (14-may-2026): https://creators.spotify.com/resources/news/expanding-video-partners-and-platforms [OFICIAL]
- Reap, Spotify Clips (verificado el 5-oct-2026): https://reap.video/blog/spotify-podcast-clips [TERCEROS]
- Vidpros, Spotify video podcast (2026): https://vidpros.com/spotify-video-podcast/ [TERCEROS]
- ppc.land, Spotify video API en cinco hosts: https://ppc.land/spotify-video-api-goes-live-on-five-hosting-platforms-apple-hls-deal-follows/ [TERCEROS]
- ppc.land, insignia de verificado y prohibición de clonación de voz (may-2026): https://ppc.land/spotifys-new-verified-badge-and-ai-voice-cloning-ban-shake-up-podcast-trust/ [TERCEROS]
- Music Business Worldwide, insignias de verificado: https://www.musicbusinessworldwide.com/spotify-extends-verified-by-spotify-badges-to-podcasts-further-cracking-down-on-ai-impersonators/ [TERCEROS]
- Syntax Academy, Clips de artistas (17-jun-2026): https://syntaxcreative.com/academy/how-to-use-spotify-clips/ [TERCEROS]
- Apple, HLS for Apple Podcasts (© 2026): https://developer.apple.com/documentation/http-live-streaming/hls-for-podcasts [OFICIAL]
- Apple, Encoding media for HLS (© 2026): https://developer.apple.com/documentation/http-live-streaming/encoding-media [OFICIAL]
- Triton Digital, Video in Apple Podcasts (17-feb-2026): https://tritondigital.com/news-item/February-17-2026/video-in-apple-podcasts-all-the-details [TERCEROS]
- Podder, soporte de hosts para vídeo HLS: https://www.podderapp.com/post/hls-video-podcast-hosting-support [TERCEROS]
- NewscastStudio (16-feb-2026): https://www.newscaststudio.com/2026/02/16/apple-podcasts-hls-features/ [TERCEROS]
- LinkedIn, Video sharing troubleshooting: https://www.linkedin.com/help/linkedin/answer/a548372 [OFICIAL]
- LinkedIn, Add closed captions: https://www.linkedin.com/help/linkedin/answer/a552177 [OFICIAL]
- contentin.io, LinkedIn post specs (8-jun-2026): https://contentin.io/blog/linkedin-post-specs/ [TERCEROS]
- Kapwing, guía de vídeo vertical en LinkedIn: https://www.kapwing.com/resources/linkedin-shorts-video-guide-limit-aspect-ratio-and-how-to-download/ [TERCEROS]
- X, Upload caption (.srt) file: https://help.x.com/en/using-x/upload-caption-srt-file [OFICIAL]
- X, Media Studio FAQs: https://help.x.com/en/using-x/media-studio-faqs [OFICIAL]
- X, API media best practices: https://docs.x.com/x-api/media/quickstart/best-practices [OFICIAL]
- X, página heredada de subida de medios: https://developer.x.com/en/docs/media/upload-media/uploading-media.html [OFICIAL, ANTIGUO]
- opentweet, límite de subida de vídeo por API de X (oct-2026): https://opentweet.io/answers/x-api-video-upload-limit [TERCEROS]
- postfa.st, especificaciones de vídeo de X: https://postfa.st/sizes/x/video [TERCEROS]
- TechCrunch, Bluesky a 3 min (10-mar-2025): https://techcrunch.com/2025/03/10/bluesky-now-lets-users-upload-videos-that-are-up-to-3-minutes-long/ [TERCEROS]
- Engadget, Bluesky a 10 min: https://engadget.com/2244638/bluesky-now-supports-10-minute-videos-larger-file-sizes/ [TERCEROS]
- TechTimes (27-ago-2026): https://www.techtimes.com/articles/325740/20260827/bluesky-matches-tiktok-video-length-still-pays-creators-nothing.htm [TERCEROS]
- opentweet, límites de Bluesky (10-oct-2026): https://opentweet.io/answers/bluesky-limits [TERCEROS]
- Ayrshare, guía de medios de Threads: https://www.ayrshare.com/docs/media-guidelines/threads [TERCEROS]
- postfa.st, especificaciones de vídeo de Threads: https://postfa.st/sizes/threads/video [TERCEROS]
- boomp.net, tamaño de vídeo de Pinterest (2026): https://boomp.net/blog/pinterest-video-size-2026 [TERCEROS]
- Kompozy, límite de duración de Snapchat Spotlight: https://kompozy.io/specs/snapchat-spotlight-video-length-limit [TERCEROS]

---

## Informe 5: Transversal: diseño de texto en vídeo vertical y horizontal

# Investigador 5/6: diseño de texto en vídeo vertical y horizontal

**Cómo se hizo.** Todo sale de búsquedas web. Abrir las páginas directamente falló: no resuelven `backlothelp.netflix.com`, `bbc.co.uk`, `support.google.com`, `remotion.dev`, `manypixels.co` ni `socialync.io`. Así que las cifras de Netflix, BBC y Google vienen de los extractos que da el buscador y de terceros que las citan, no de haber leído la página. Para confirmarlas hay que permitir esos dominios en la red de la sesión. Fecha de consulta de todas las fuentes: 18-nov-2026.

## Resumen accionable

1. **Ninguna plataforma publica una zona segura oficial para vídeo orgánico.** Meta, Google y TikTok la publican solo para anuncios, y las cifras orgánicas son mediciones de terceros. Diseña con la de anuncios, que es la más estricta, y deja la orgánica como margen de tolerancia.
2. **Rectángulo seguro común para todas las apps verticales (1080x1920), modo estricto:** x 120–888, y 288–1248, es decir 768x960 px. Márgenes: arriba 288, abajo 672, izquierda 120, derecha 192.
3. **Si además debe sobrevivir al recorte 4:5 del feed y 3:4 de la cuadrícula del perfil:** x 120–888, y 420–1248 (768x828 px). Lo único que cambia es el borde de arriba.
4. **Tambor en 9:16:**
   - Suprime la frase anterior.
   - Frase actual: caja y 620–1020, cuerpo de 72–80 px, como mucho 3 líneas (4 de límite duro), unos 20–24 caracteres por línea.
   - Siguiente: y 1060–1220, 46–48 px, opacidad 55 %.
   - Título y hablante: cabecera y 300–440.
   - Nada de texto por debajo de y 1248.
5. **Tambor en 16:9:** frase actual de 80–88 px en x 192–1728 (márgenes del 10 %). Deja libres los ~150 px de abajo, que tapan los controles y los subtítulos (CC) de YouTube. Título y logo dentro del title-safe del 5 % (96/54 px).
6. **Tamaño mínimo de letra.** Vertical: 44 px de texto secundario y 64 px de frase activa. Horizontal visto en un teléfono: unos 48 px de secundario y unos 72 px de activa. La referencia de la BBC es una altura de línea del 8 % del vídeo, que son 86 px a 1080 de alto.
7. **Color y contraste:**
   - Blanco sobre #111111 da 18,9:1.
   - Frases atenuadas: opacidad ≥ 45 % (unos 4,5:1). Recomendado 55 % (unos 6,2:1). Por debajo del 35 % baja a unos 3,2:1 y no cumple WCAG AA.
   - Fondo plano oscuro, sin degradados finos. Si se usan, añade un 1–2 % de grano.
   - Evita texto rojo o azul saturado: el submuestreo 4:2:0 deshace sus bordes.
8. **Tipografía.** Atkinson Hyperlegible Next (licencia OFL, 2025, variable de 200 a 800) en peso 600–700. Alternativas: Inter o Noto Sans. Interlineado de 1,15 a 1,25. Trazo de al menos 4–5 px.
9. **Transición entre frases:** desplazamiento más fundido de 200–280 ms (10–14 fotogramas a 50 fps) con ease-out. No escales ni desenfoques el texto. Esta cifra es una inferencia propia, no está en ninguna fuente.
10. **Spotify Clips** dura de 15 a 90 s, no 3 minutos. Los clips largos tienen que salir en versión de ≤ 90 s para Spotify.

## Tabla de especificaciones: zonas que tapa la interfaz en 1080x1920

| Plataforma (fuente) | Arriba | Abajo | Izq. | Der. | Qué tapa | Confianza |
|---|---|---|---|---|---|---|
| TikTok, plantilla oficial In-Feed de anuncios (720x1280, escalada x1,5) | 240 | 660 | 120 | 120, más una columna de botones de 180 px (Socialync) o 300 px (Upload-Post) desde y≈840 | Arriba: pestañas Siguiendo/Para ti. Derecha: avatar, me gusta, comentarios, compartir, disco. Abajo: usuario, pie de texto, sonido, CTA | [TERCEROS] medido sobre la plantilla oficial |
| TikTok orgánico (guías) | 108–160 | 270–480 | 40–120 | 150–164 | Lo mismo | [NO CONFIRMADO], cifras contradictorias |
| Instagram / Facebook Reels, anuncios (Meta) | 269 (14 %) | 672 (35 %); 768 (40 %) si lleva aviso legal | 65 (6 %) | 65 (6 %) | Arriba: cabecera, cámara, audio. Abajo: usuario, pie de texto, audio. Derecha: botones | [TERCEROS] citando a Meta |
| Reels orgánico (guías) | 220 | 320 | – | unos 84 de columna | Lo mismo | [NO CONFIRMADO] |
| Historias de Instagram y Facebook | 250 (14 %) | 340 (20 %) | – | – | Arriba: barra de progreso, avatar, nombre. Abajo: responder, enlace | [TERCEROS] citando a Meta |
| YouTube Shorts, plantilla de Google para anuncios verticales | 288 | 672 | 48 | 192 | Arriba: búsqueda y menú. Derecha: me gusta, no me gusta, comentarios, compartir, remix. Abajo: título, canal, botón Suscribirse, sonido | [TERCEROS] dicen que la figura es de Google; no la he podido verificar |
| YouTube Shorts orgánico (guías) | 154–180 | 380 (hasta unos 400 con la descripción abierta) | – | 120 | Lo mismo | [NO CONFIRMADO] |
| Spotify Clips | no encontrado | no encontrado | – | – | – | Spotify no publica zona segura |
| **Común estricto (envolvente)** | **288** | **672** | **120** | **192** | — | Deducido aquí |

**Recortes:**

| Recorte | Ventana visible sobre 1080x1920 | Fuente |
|---|---|---|
| Vista previa 4:5 del feed de Instagram | 1080x1350 centrado. Visible y 285–1635. Otra guía: unos 255 px por lado | [TERCEROS]; Instagram no lo documenta |
| Cuadrícula 3:4 del perfil de Instagram (desde enero de 2025) | 1080x1440 centrado. Visible y 240–1680 | [TERCEROS], varias guías |
| Cuadrícula 3:4 del perfil de TikTok (afecta a la portada) | Unos 240 px por lado; otra fuente dice 420. Visible y 240–1680 o y 420–1500 | [NO CONFIRMADO] |

**Especificaciones de subida de Spotify Clips** [OFICIAL, support.spotify.com, «Clips content policy»]: de 15 a 90 s, al menos 768x1024, ≤ 1 GB, MP4 o MOV, con audio. Recomiendan vertical, pero admiten horizontal.

**YouTube Shorts** [OFICIAL, support.google.com/youtube/answer/15424877]: desde el 15-oct-2024, todo vídeo cuadrado o vertical de hasta 3 min se clasifica como Short. El 1:1 también cuenta.

## Respuestas pregunta por pregunta

### 1. Zona segura común a todas las apps verticales

**Cómo se calcula.** Se toma el valor más restrictivo de cada borde:

| Borde | Valor | Origen |
|---|---|---|
| Arriba | 288 | Shorts/Google |
| Abajo | 672 | Shorts/Google y Meta Reels |
| Izquierda | 120 | TikTok |
| Derecha | 192 | Shorts/Google |

Queda **x 120–888, y 288–1248 (768x960)**.

La columna de botones de TikTok, si se toma la medición de 300 px, invade la franja derecha desde y≈840 en x ≥ 780. Por eso entre y 840 y 1248 conviene limitar el texto a x ≤ 780, o bien centrarlo y dejar margen.

**Zona práctica para orgánico** (cuando aceptas que algún anuncio tape algo): x 96–900, y 250–1440. No sirve para las cifras de anuncios.

**Versión que sobrevive al recorte.** Se intersecan la zona estricta, la ventana 4:5 (y 285–1635) y la 3:4 (y 240–1680, o y 420–1500 en el caso pesimista de TikTok). Resultado: **x 120–888, y 420–1248**. Su centro geométrico queda en y≈834, no en 960: la interfaz de abajo pesa más que la de arriba. Si se quiere simétrico en horizontal para la portada: x 192–888.

### 2. Zona segura en horizontal 1920x1080

| Referencia | Margen por lado | Px horizontal / vertical | Confianza |
|---|---|---|---|
| Action-safe, EBU R95 / ITU-R BT.1848 (16:9) | 3,5 % | 67 / 38 | [OFICIAL EBU/ITU] vía resultados de búsqueda; R95 no se pudo leer entero |
| Graphics-safe (title), EBU / ITU | 5 % | 96 / 54 | Ídem |
| Action area, SMPTE ST 2046-1 | 93 % del área (3,5 % por lado) | 67 / 38 | [OFICIAL SMPTE] |
| Safe title, SMPTE RP 2046-2 (compatibilidad 4:3) | 90 % (5 % por lado) | 96 / 54 | [OFICIAL SMPTE] |
| Recomendación clásica de «10 %» | 10 % | 192 / 108 | [TERCEROS] |

**Elementos de YouTube:**

- **Controles:** se superponen en la franja inferior cuando el vídeo está en pausa o se pasa el ratón. No hay cifra oficial de altura. Estimación: deja libres 150 px abajo [NO CONFIRMADO]. Una guía de terceros avisa además del contador de duración, unos 60x40 abajo a la derecha.
- **Subtítulos (CC):** aparecen abajo en el centro por defecto. No pongas la frase activa por debajo de y≈900.
- **Pantallas finales** [OFICIAL, support.google.com/youtube/answer/6388789]:
  - El vídeo tiene que durar al menos 25 s.
  - Admiten hasta 4 elementos en 16:9 y se planifican sobre los últimos 20 s. El mínimo de 5 s solo aparece en terceros.
  - Tamaño de los elementos, según terceros: vídeo o lista de unos 613x343 (otra guía dice 615x345); suscripción en círculo de 294x294.
  - Recomendación: en los últimos 20 s, despeja la mitad derecha y la franja inferior. Deja solo el título en y 54–180.

**Píxeles recomendados (horizontal):**

| Elemento | x | y | Tipo |
|---|---|---|---|
| Bloque central del tambor | 192–1728 | 250–860 | — |
| Título | 96–1300 | 54–110 | 40–44 px |
| Hablante | 192 en adelante | 330–380, encima de la frase actual | 44–48 px |
| Logo | 96–184 | 54–142 | — |

El logo va arriba a la izquierda porque abajo a la derecha está la marca de agua del canal de YouTube [sin confirmar], y arriba a la derecha salen el icono de tarjetas y el menú.

### 3. El tambor en 9:16

- **Suprimir la frase anterior.** La lectura en vertical es rápida y la franja disponible mide unos 960 px de alto. Si se mantiene: 1 línea, 40–44 px, opacidad del 40 %, en y 520–580.
- **Título:** se mantiene, pero corto (≤ 32 caracteres, recortado con «…») y pequeño (40 px), en la cabecera.
- **Hablante:** se mantiene, en 48 px bold y con color de acento. En episodios de un solo hablante se puede suprimir.
- **Frase actual:** franja y 620–1020, centrada ópticamente en y≈820. Así queda por encima del pie de texto y la descripción (y > 1248 en el caso estricto, unos 1440 en el práctico) y por encima del arranque de la columna de botones (y≈840) en su mitad superior.
- **Frase siguiente:** y 1060–1220, como mucho 2 líneas.

### 4. Tamaños mínimos de letra

**Fuentes:**

- BBC: altura de línea del 8 % de la altura activa en 16:9 online [TERCEROS citando a la BBC, clevercast.com; la presentación CSUN de la BBC usa el 8 % como referencia]. Son 86 px a 1080 de alto y 154 px a 1920 de alto.
- Otra fuente atribuye a la BBC un mínimo de 44 px en HD [NO CONFIRMADO].
- Regla general de terceros: entre 1/20 y 1/10 de la altura del cuadro [TERCEROS].
- Netflix no fija tamaño de letra en sus guías de idioma (no encontrado).

**Cómo se pasa al teléfono** (cálculo propio):

- Un vídeo vertical a pantalla completa en un móvil de unos 390 pt de ancho escala 1080 px a 390 pt, es decir ×0,36.
- Un 16:9 visto en vertical en un móvil escala 1920 px a unos 390 pt, es decir ×0,20. A pantalla completa en apaisado, unos 844 pt sobre 1920 px, es decir ×0,44.
- Tomando 16 pt como cuerpo mínimo cómodo:

| Uso | Vertical 1080x1920 | Horizontal 1920x1080 |
|---|---|---|
| Cuerpo mínimo (secundario: título, siguiente) | 44 px (unos 16 pt) | 48 px (unos 10 pt en vertical, 21 pt en apaisado) |
| Frase activa, mínimo | 64 px | 72 px |
| Frase activa, recomendado | 72–80 px (26–29 pt) | 80–88 px (aproximadamente el 8 % de la BBC) |
| Hablante | 48 px bold | 44–48 px bold |

### 5. Longitud de línea, número de líneas y velocidad

- **Netflix, español de España y de Latinoamérica:** 42 caracteres por línea y 2 líneas [OFICIAL Netflix, vía extracto de búsqueda].
- **Velocidad:** 17 caracteres/s en adultos y 13 en infantil. Así figura en las guías de danés, eslovaco y sami; para español no lo he confirmado [NO CONFIRMADO].
- **Duración por evento:** mínimo 5/6 s (833 ms), máximo 7 s [OFICIAL Netflix, General Requirements].
- **BBC:** 160–180 palabras por minuto [TERCEROS]. El límite de 37 caracteres es de teletexto y no se aplica aquí. Una línea ocupa el 68 % del ancho en 16:9 [TERCEROS].

**Aplicado al tambor:**

| | Vertical | Horizontal |
|---|---|---|
| Caracteres por línea | 20–24 (a 76 px de cuerpo en 792 px de ancho, unos 0,5 em por carácter en una sans; estimación propia) | 36–42 (a 84 px en 1536 px de ancho) |
| Líneas de la frase activa | 3, como mucho 4 | 2, como mucho 3 |

Si la frase supera ese tope, hay que trocearla en `frases`. Encaja con que el troceado del español sea una decisión de doblaje.

**Duración de cada frase.** La marca el audio del TTS, no la velocidad de lectura. Aun así:

- Funde las frases que duren menos de 833 ms. Equivale a la regla de fundir frases de una palabra.
- Parte las que pasen de 7 s.
- Comprueba que no superan los 17 caracteres por segundo. Si lo hacen, la voz va más rápido de lo que se puede leer y conviene trocear.

**Reglas de corte** (las clásicas de subtitulado; Netflix y la BBC las aplican, aunque aquí no he leído el texto literal [TERCEROS]):

- Corta después de un signo de puntuación.
- No separes artículo y sustantivo, preposición y su término, adjetivo y sustantivo, pronombre átono y verbo, auxiliar y participio («ha / dicho»), ni la negación del verbo.
- No dejes «¿» ni «¡» al final de una línea.
- Prefiere forma de pirámide: la línea de abajo más larga, o líneas equilibradas.

### 6. Tipografía

- **Atkinson Hyperlegible Next** (Braille Institute, 2025). Licencia OFL 1.1, variable de 200 a 800 (una fuente dice de 100 a 900), con subconjunto latin-ext y cobertura de unas 150 lenguas [TERCEROS: fontsource, Adobe Fonts].
- **Alternativas OFL de Google Fonts:** Inter, Noto Sans, Source Sans 3 y Lexend [sin confirmar en esta búsqueda; son OFL conocidas]. Comprueba los glifos ¿ ¡ ñ á é í ó ú ü «» — renderizando una línea de prueba.
- **Pesos:** 600–700 para la frase activa, 500–600 para el texto secundario. Evita ≤ 300: trazos de 2–3 px desaparecen al recomprimir y con el submuestreo de croma 4:2:0 (deducción técnica, no hay fuente).
- **Trazo:** al menos 4–5 px de grosor de asta a 72–80 px de cuerpo, lo que equivale a peso semibold o más.
- **Interlineado:** de 1,15 a 1,25.
- **Tracking:** de 0 a +1 % del cuerpo. No comprimas.
- **Contorno:** si se usa, 2–3 px en el color del fondo, sin sombra difusa.

### 7. Contraste y legibilidad

- **WCAG 2.x:** 1.4.3 (AA) pide 4,5:1, o 3:1 en texto grande (≥ 18 pt, o ≥ 14 pt en negrita). 1.4.6 (AAA) pide 7:1 [OFICIAL W3C, conocido; no lo he vuelto a buscar].
- **Contrastes calculados aquí** (texto blanco sobre fondo #111111, con la opacidad indicada):

| Opacidad del blanco | Gris equivalente | Contraste | ¿Cumple? |
|---|---|---|---|
| 100 % | #FFFFFF | 18,9:1 | AAA |
| 55 % | #949494 | 6,2:1 | AA, recomendado para la siguiente |
| 45 % | #7C7C7C | 4,5:1 | AA justo, mínimo para la anterior |
| 35 % | — | 3,2:1 | Solo vale para texto grande |

- **Atenuar con color plano en vez de alfa.** En ASS y en Remotion da el mismo resultado y evita mezclas raras al hacer fundidos.
- **Fondo:** plano y oscuro (#0E0E10 a #141416), sin caja. Con un fondo plano el contraste está asegurado y no hacen falta caja ni sombra. Si el fondo es una miniatura o imagen: caja negra al 60–70 % o contorno de 3 px.
- **Banding:** los degradados oscuros suaves «escalonan» con H.264 en 8 bits y con la recodificación de las plataformas. Las soluciones en uso son grano o dither del 1–5 % [TERCEROS: foros de Adobe, PremiumBeat, ProVideoCoalition]. Varios usuarios informan de que subir el bitrate o exportar en 10 bits no lo arregla. Para este caso: evita las viñetas y los degradados radiales oscuros. Si los quieres, un 1–2 % de grano uniforme.

### 8. Subtítulos animados (karaoke, palabra a palabra)

- **Datos de retención:** solo hay cifras de vendedores de herramientas, del +12 % al +34 % en tiempo de visionado o en tasa de finalización, sin metodología publicada [NO CONFIRMADO: clipspeed, opus.pro, eliro]. La cifra del «47 % según TikTok» no tiene fuente primaria. Una de esas fuentes avisa de sobrecarga cognitiva si la imagen es compleja; aquí no lo es.
- **Aplicado aquí:**
  - Opcional: resaltar la palabra activa solo con color (blanco a acento), sin cambiar escala ni peso, para que la línea no se recoloque.
  - Exige marcas de tiempo por palabra, obtenidas por alineado forzado sobre el audio del TTS (por ejemplo WhisperX).
  - Mejor aplicarlo solo en el formato vertical.
- **Transición del tambor** [inferencia propia, sin fuente]:
  - Desplazamiento vertical de la altura de una línea más fundido, de 200 a 280 ms (10–14 fotogramas a 50 fps), con easing ease-out cúbico.
  - Si la frase dura menos de 600 ms, corte seco.
  - Nada de zoom, desenfoque ni rebote: el texto grande en movimiento consume bitrate y genera bloques.
  - Nada de destellos (WCAG 2.3.1: no más de 3 por segundo).

### 9. Elementos fijos

**Logo o marca de agua:**

| Formato | Tamaño | Posición |
|---|---|---|
| Vertical | 64x64 px | x 120–184, y 300–364, en la cabecera junto al título |
| Horizontal | 88x88 px | x 96–184, y 54–142 |

En vertical, nunca abajo (tapa el nombre de usuario) ni a la derecha (columna de botones). TikTok añade su propia marca de agua al descargar.

**Indicador de hablante:** en la cabecera, en y 370–430 (vertical), o encima de la frase actual (horizontal). Un punto o barra de color de 12 px más el nombre.

**Barra de progreso propia:**

- La app ya dibuja la suya abajo: Shorts muestra una línea fina, TikTok y Reels un control de avance (posiciones [sin confirmar]). Una barra propia abajo quedaría tapada.
- Si se quiere una, fina (4 px), en la cabecera (y 452–456, x 120–888), y solo en clips de 60 s o más.
- En horizontal no hace falta: YouTube tiene la suya.

### 10. Plantillas de coordenadas (x, y, ancho, alto en px, origen arriba a la izquierda)

**A) Vertical 1080x1920** (Shorts, Reels, TikTok, Facebook Reels, Historias, Spotify Clips; fondo #111111)

| Caja | x | y | an. | al. | Tipo | Notas |
|---|---|---|---|---|---|---|
| Logo | 120 | 300 | 64 | 64 | — | — |
| Título | 200 | 300 | 688 | 56 | 40 px, peso 600, blanco al 70 % | 1 línea, ≤ 32 caracteres |
| Hablante | 120 | 372 | 768 | 60 | 48 px, peso 700, acento | — |
| (Progreso, opcional) | 120 | 452 | 768 | 4 | — | — |
| Frase anterior (desactivada por defecto) | 120 | 520 | 768 | 60 | 44 px, al 40 % | — |
| Frase actual | 120 | 620 | 768 | 400 | 76 px, peso 700, blanco, interlineado 1,22 | Centrada, 3–4 líneas, alineación central (ASS \an5) en x 504, y 820 |
| Frase siguiente | 120 | 1060 | 768 | 160 | 48 px, peso 500, al 55 % | ≤ 2 líneas |
| Libre (interfaz) | 0 | 1248 | 1080 | 672 | — | Sin texto |

Columnas: x 120–888, que deja 120 px a la izquierda y 192 a la derecha. Toda la plantilla cabe en y 288–1248. La cabecera (y 300–456) queda dentro de 4:5 y de 3:4, pero no dentro de la versión pesimista del recorte de TikTok (y ≥ 420). Para la portada, genera un fotograma aparte con el texto en y 420–1248.

**B) Horizontal 1920x1080** (YouTube, Spotify vídeo)

| Caja | x | y | an. | al. | Tipo |
|---|---|---|---|---|---|
| Logo | 96 | 54 | 88 | 88 | — |
| Título | 200 | 66 | 1300 | 64 | 42 px, peso 600, al 70 % |
| Hablante | 192 | 300 | 1536 | 60 | 46 px, peso 700, acento |
| Frase anterior | 192 | 380 | 1536 | 70 | 50 px, al 45 % (#7C7C7C), 1 línea |
| Frase actual | 192 | 470 | 1536 | 230 | 84 px, peso 700, blanco, ≤ 2 líneas (3 de límite duro), centro en x 960, y 585 |
| Frase siguiente | 192 | 720 | 1536 | 130 | 50 px, al 55 % (#949494), ≤ 2 líneas |
| Libre (controles y CC) | 0 | 900 | 1920 | 180 | — |

Últimos 20 s (pantalla final): oculta la frase anterior y la siguiente, y deja libres x 960–1824 / y 200–900.

**C) 4:5 1080x1350** (feed de Instagram, Facebook, X, LinkedIn; mismo fondo)

| Caja | x | y | an. | al. | Tipo |
|---|---|---|---|---|---|
| Logo | 65 | 65 | 64 | 64 | — |
| Título | 145 | 70 | 870 | 56 | 40 px |
| Hablante | 65 | 150 | 950 | 60 | 48 px bold |
| Frase actual | 65 | 380 | 950 | 420 | 76 px, ≤ 4 líneas, unos 26 caracteres por línea |
| Frase siguiente | 65 | 840 | 950 | 160 | 48 px, al 55 % |
| Libre (pie de texto o recorte) | 0 | 1100 | 1080 | 250 | — |

Márgenes del 6 % (65 px), por analogía con el margen lateral de Meta. Para **1:1 (1080x1080)**, válido también como Short: mismas columnas, frase actual en y 340–700, siguiente en y 730–860, cabecera en y 65–200.

## Qué evitar

- Poner texto por debajo de y 1248 en vertical, o a la derecha de x 888 entre y 840 y 1700 (columna de botones).
- Repetir en vertical el tambor de tres frases del horizontal: no cabe con 72 px o más.
- Opacidades por debajo del 45 % en las frases atenuadas (contraste por debajo de 4,5:1).
- Pesos de 300 o menos, texto rojo o azul saturado sobre negro, y degradados oscuros finos sin grano.
- Animaciones de escala, rebote o desenfoque, y transiciones de más de unos 300 ms entre frases que duran 1–3 s.
- Logo o barra de progreso en la franja inferior de vertical.
- Subir a Spotify Clips clips de más de 90 s.
- Tomar las cifras de anuncios por norma orgánica, y las orgánicas de terceros por oficiales.

## Dudas abiertas / no confirmado

- **Zonas seguras orgánicas oficiales:** no existen para ninguna plataforma. Las de anuncios (Meta 14/35/6 %, plantilla de TikTok 240/660/120, Google 288/672/48/192) llegan citadas por terceros. No he podido abrir business.facebook.com, ads.tiktok.com ni support.google.com.
- **Columna de botones de TikTok:** 180 px o 300 px de ancho, según quién la mida. Recorte de la cuadrícula de TikTok: 240 o 420 px por lado.
- **Velocidad de lectura de Netflix para español:** sin confirmar. 17 caracteres/s es la cifra de otras lenguas.
- **BBC:** el 8 % de altura de línea viene de terceros y la propia BBC lo plantea como pregunta. No he leído bbc.github.io/subtitle-guidelines.
- **Altura de los controles de YouTube y posición de la marca de agua del canal:** no encontrado en fuentes oficiales.
- **Zona segura de Spotify Clips:** no encontrada.
- **Retención del resaltado palabra a palabra:** solo hay datos de vendedores.
- **Duración y easing de las transiciones:** recomendación propia, sin fuente.
- **Rectángulos de interfaz:** mídelos sobre capturas reales en las apps de 2026 antes de dar la plantilla por cerrada. Las interfaces cambian y las mediciones de terceros están fechadas en 2025–2026.

## Fuentes (consultadas el 18-nov-2026 vía buscador; fecha de la página donde consta)

- Spotify, «Clips content policy»: https://support.spotify.com/ca-en/creators/article/clips-content-policy/ [OFICIAL]
- YouTube Help, «Understand three-minute YouTube Shorts»: https://support.google.com/youtube/answer/15424877 [OFICIAL]; Tubefilter, 03-oct-2024: https://www.tubefilter.com/2024/10/03/youtube-shorts-three-minutes-max-length-redesign-trends-templates/ [ANTIGUO: 2024]
- YouTube Help, «Add end screens to videos»: https://support.google.com/youtube/answer/6388789 [OFICIAL]
- Google Ads Help, «Use square and vertical video…» (zona segura de anuncios verticales): https://support.google.com/google-ads/answer/9128498 [OFICIAL, pero sin cifras visibles en el extracto]
- Netflix, Castilian & Latin American Spanish Timed Text Style Guide: https://backlothelp.netflix.com/hc/en-us/articles/217349997 [OFICIAL, vía extracto]
- Netflix, General Requirements: https://backlothelp.netflix.com/hc/en-us/articles/215758617 [OFICIAL, vía extracto]
- Netflix, Danish TTSG (17/13 caracteres/s): https://backlothelp.netflix.com/hc/en-us/articles/216014347 [OFICIAL]
- BBC, CSUN «How big should subtitles be»: https://bbc.github.io/csun/how_big_should_subtitles_be/index.html [OFICIAL BBC]
- Clevercast, «BBC Subtitling Guidelines»: https://clevercast.com/bbc-subtitling-guidelines [TERCEROS]
- EBU R95: https://tech.ebu.ch/docs/r/r095.pdf ; ITU-R BT.1848: https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1848-0-200905-S!!MSW-E.doc ; SMPTE ST 2046-1: https://pub.smpte.org/doc/st2046-1/20091123-pub/st2046-1-2009.pdf ; SMPTE RP 2046-2: https://pub.smpte.org/latest/rp2046-2/rp2046-2-2009.pdf [OFICIAL; ANTIGUO: 2009]
- ManyPixels, «TikTok ad sizes and specs for 2026 (with measured safe zones)», plantilla bajada el 11-nov-2026: https://www.manypixels.co/blog/social-media-design/tiktok-ad-specs [TERCEROS]
- Socialync, safe zones: https://www.socialync.io/tools/safe-zones ; Upload-Post: https://www.upload-post.com/tools/safe-zone-checker/ ; Bundle.social: https://bundle.social/tools/safe-zone-checker [TERCEROS]
- Relevant Audience, TikTok ad specs: https://www.relevantaudience.com/tiktok-ads/tiktok-video-size-ad-specs/ ; Poster.ly: https://www.poster.ly/tools/tiktok-safe-zone-checker ; ScreenSnap: https://www.screensnap.pro/blog/tiktok-video-size-guide [TERCEROS]
- AdMake, Instagram Reels safe zone: https://admakeai.com/free-tools/instagram-reels-safe-zone ; Adkit: https://adkit.so/tools/safe-zones/meta ; adsuploader: https://adsuploader.com/blog/meta-ads-safe-zones ; maketecheasier: https://maketecheasier.com/instagram-story-reel-safe-zone [TERCEROS]
- Recortes 4:5 y 3:4: frameo.ai https://frameo.ai/blog/reel-size/ ; lesfm https://lesfm.net/blog/formatting-videos-for-instagram/ (02-abr-2026) ; Planoly https://planoly.com/blog/instagram-updates-jan-2025 ; Kapwing https://www.kapwing.com/resources/instagrams-new-grid-layout-size-and-dimensions-2025/ ; socialrails https://socialrails.com/blog/tiktok-thumbnail-size-guide [TERCEROS]
- Shorts orgánico: postplanify https://postplanify.com/blog/social-media-safe-zones-2026-complete-guide ; adaptlypost https://adaptlypost.com/blog/social-media-safe-zones-2026-complete-guide ; reap.video https://reap.video/blog/short-form-video-safe-zones ; collabpals (tamaños de pantalla final) https://www.collabpals.com/tools/youtube-end-screen-previewer [TERCEROS]
- Atkinson Hyperlegible Next: https://fontsource.org/fonts/atkinson-hyperlegible-next/about ; https://fonts.adobe.com/fonts/atkinson-hyperlegible-next ; https://lbbonline.com/news/applied-design-launches-atkinson-hyperlegible-next-typeface [TERCEROS]
- Banding: https://www.premiumbeat.com/blog/debanding-footage-davinci-resolve ; https://www.provideocoalition.com/remove-banding-in-after-effects/ ; https://community.adobe.com/questions-729/color-banding-premiere-export-file-h-264-1376539 [TERCEROS/FORO]
- Subtítulos animados (solo vendedores): https://clipspeed.ai/blog/ai-captions-increase-views.html ; https://www.opus.pro/blog/best-caption-presets-styles-boost-retention ; https://eliro.pro/blog/12-caption-styles-increase-watch-time [NO CONFIRMADO]
- WCAG 2.2, 1.4.3 / 1.4.6 / 2.3.1: https://www.w3.org/TR/WCAG22/ [OFICIAL; no la he vuelto a abrir]


---

## Informe 6: Políticas, derechos, IA y mejor vía de subida

# Investigador 6/6: políticas, derechos, IA y la mejor vía de subida

**Limitación de método.** La sesión no pudo abrir páginas directamente. WebFetch falló con ENOTFOUND en support.google.com, creators.facebook.com, www.tiktok.com y developers.tiktok.com. Todo lo que sigue sale de WebSearch, que devuelve el texto de esas páginas oficiales indirectamente o a través de prensa especializada. Fecha de consulta de todo: **18-nov-2026**. Cuando el dato viene de una página oficial, aunque haya llegado por un resultado de búsqueda, va marcado [OFICIAL]. Para leer las páginas tal cual hay que permitir esos dominios en la red de la sesión.

## Resumen accionable

1. **El riesgo nº 1 es el copyright, no el algoritmo.** Traducir es un acto de "transformación". En España exige autorización del autor (TRLPI arts. 17 y 21) y en EE. UU. también (17 USC §106(2)). No ser de pago no lo cambia. Una traducción íntegra es el peor caso para el *fair use*, y en la UE no existe *fair use*. Sin permiso escrito de Naval, cualquier vídeo puede retirarse con un aviso DMCA. En YouTube son 3 strikes en 90 días y el canal se cierra.
2. **Riesgo nº 2, la voz.** Si las voces XTTS o LoRA de `fabrica/voces.json` (naval, nivi, brett, deutsch) se entrenaron con grabaciones reales de esas personas, es **clonación de voz de personas reales**. Eso activa cuatro cosas: el etiquetado obligatorio en YouTube, TikTok y Meta; la política de suplantación de Spotify (retirada sin permiso, también para una "versión IA"); la vía de privacidad de YouTube (retirada a petición de la persona, 48 h de plazo); y el art. 50(4) de la Ley de IA de la UE (deepfakes de audio, vigente desde el 2-ago-2026). **Hay que confirmarlo en el repo.**
3. **Marcar "IA: sí" en todas las plataformas, siempre.** YouTube dice oficialmente que la etiqueta no cambia ni recomendaciones ni monetización. TikTok dice que la casilla no afecta a la distribución. No marcarla sí tiene coste: etiqueta automática (YouTube desde may-2026 y TikTok vía C2PA, en ambos casos irremovible) y posible retirada.
4. **Las políticas de "contenido reutilizado o inauténtico" afectan sobre todo a la monetización (YouTube) y al alcance (TikTok, Instagram, Facebook).** No llevan a retirada por sí solas. Como el proyecto no monetiza, en YouTube casi no aplican. En TikTok e Instagram pueden dejar los clips fuera de For You o de recomendaciones.
5. **Subida: YouTube y Spotify a mano. TikTok, Reels, Shorts y LinkedIn con programadores nativos** (TikTok Studio, Meta Business Suite, YouTube Studio). La API solo merece la pena para YouTube, si se acepta que los vídeos se suban en privado y se publiquen a mano.
6. **Exportar un máster limpio por plataforma**, sin marcas de agua ajenas. Instagram penaliza (2021, sin rectificación posterior) los Reels con logo de TikTok.
7. **Descripción obligatoria en todas partes:** "Traducción no oficial al español", el original con su enlace (nav.al/<slug>), "voz sintética generada con IA" y "sin afiliación con Naval Ravikant".
8. **En cuanto haya permiso:** guardar un PDF o email firmado en Drive, con su file ID en `drive.json` o en el repo. Que el permiso cubra traducción, doblaje con voz sintética (y clonada, si lo es), plataformas y formatos cortos. Además, pedir a Naval que añada el canal a su lista de autorización de Content ID, si la tiene.

## Tabla de políticas por plataforma

| Plataforma | Contenido reutilizado o no original | Consecuencia | Etiqueta IA | ¿Reduce alcance la etiqueta? | Suplantación o voz |
|---|---|---|---|---|---|
| YouTube (largo + Shorts) | "Reused content" (sin cambios) + "inauthentic content" (rebautizado el 15-jul-2025, antes "repetitious") [OFICIAL vía prensa] | Pérdida del YPP, a nivel de canal. **No** es retirada | Casilla "Contenido alterado o sintético" al subir. API: `status.containsSyntheticMedia` (desde el 30-oct-2024) [OFICIAL] | **No** (anuncio del 27-may-2026) [OFICIAL vía prensa] | Retirada por privacidad a petición de la persona (desde jun-2024). Detección de semejanza para creadores del YPP (21-oct-2025) |
| TikTok | "Unoriginal or reproduced content without new or creative changes" → no apto para For You [OFICIAL] | Alcance (FYF). Repetido: la cuenta entera fuera del FYF [OFICIAL] | Casilla "AI-generated content". API: `is_aigc` (etiqueta "Creator labeled as AI-generated") [OFICIAL]. Autoetiqueta por C2PA, irremovible | "No afectará a la distribución" [TERCEROS citando a TikTok] | Exige etiquetar el habla generada por IA realista [TERCEROS] |
| Instagram | Clasificadores de originalidad. Agregadores y reposts menos recomendados (2022, 2024, ampliado en abr-may 2026) [TERCEROS] | Alcance a no seguidores | "AI info" (desde el 1-jul-2024). En contenido solo editado con IA va en el menú (sep-2024) [OFICIAL] | No consta | Obligatorio declarar "realistic-sounding audio" alterado o creado [OFICIAL, 2024] |
| Facebook | 14-jul-2025: reposts repetidos "without permission or meaningful enhancements" [OFICIAL vía prensa] | Sin monetización durante un tiempo + menos distribución de todos los posts. Se ve en el Professional Dashboard | Igual que Instagram | No consta | Igual que Instagram |
| Spotify | Rights Claims (solo vídeo). "Debes tener todos los derechos" (Clips) [OFICIAL] | Retirada o reclamación | No hay etiqueta general para pódcast [no encontrado] | — | **Retira** pódcast que suplante la semejanza (voz incluida) sin permiso, también como "versión IA" [OFICIAL] |
| LinkedIn | No encontrado | — | Icono C2PA o "CR" si el fichero lleva Content Credentials [OFICIAL]. En vídeo, los codificadores suelen borrar el C2PA [TERCEROS] | No consta | No encontrado |

## Tabla de vías de subida y límites

| Plataforma | Manual (app / web) | Programador nativo | API oficial | Límites de API |
|---|---|---|---|---|
| YouTube | Studio web (recomendado; ya se hace así) | Studio: programar al publicar | Data API v3 `videos.insert` | 1.600 unidades por subida de 10.000/día, ≈6 subidas/día [OFICIAL]. Proyectos sin verificar creados después del 28-jul-2020: **vídeo forzado a privado** hasta pasar auditoría [OFICIAL]. Hay webs de 2026 que hablan de ~100 unidades desde dic-2025 [NO CONFIRMADO] |
| TikTok | App o web (TikTok Studio) | TikTok Studio escritorio: **10 días** (Hootsuite, Metricool) o **30 días** (otras guías) [NO CONFIRMADO]. Requiere cuenta Creator o Business. La casilla IA está en "Mostrar más" | Content Posting API (Direct Post) | Cliente sin auditar: todo en privado (`unaudited_client_can_only_post_to_private_accounts`) [OFICIAL]. ≤5 usuarios en 24 h [TERCEROS]. ~15 posts/día por cuenta, compartidos entre todas las apps [TERCEROS]. Auditoría de 2 a 6 semanas [TERCEROS] |
| Instagram | App | Programador de la app y Meta Business Suite: **75 días** de antelación, 25 posts/día. Otras guías dicen 29 días [NO CONFIRMADO] | Graph API Content Publishing | 50 posts por 24 h móviles [OFICIAL] (en versiones antiguas, 100). 400 contenedores/24 h. Los contenedores caducan en 24 h. Todo vídeo sale como Reel. Requiere cuenta profesional: Business seguro; Creator, según la fuente [NO CONFIRMADO]. No se encontró un campo de etiqueta IA en la API |
| Facebook | App o web | Meta Business Suite (igual que Instagram) | Graph API (Pages) | No investigado en detalle |
| Spotify | Spotify for Creators web ("replace audio with video") | Programación al publicar | No hay API pública de subida de vídeo [no encontrado] | — |
| LinkedIn | Web o app. Hasta 5 GB; 15 min en escritorio y 10 min en móvil [TERCEROS, hay fuentes que dicen 10 min] | Programador nativo (plazo no encontrado) | Posts API (no investigada) | — |

## Herramientas de publicación cruzada (planes gratuitos 2026; todas las cifras son [TERCEROS])

| Herramienta | Gratis | Cubre | Notas |
|---|---|---|---|
| Buffer | 3 canales, 10 posts en cola por canal | YouTube Shorts, TikTok (perfil Business), Instagram (Creator o Business), LinkedIn, Facebook | En el plan de pago se paga por canal |
| Metricool | 1 marca, ~20 posts/mes (antes 50). CostBench dice 100 [NO CONFIRMADO] | Facebook, Instagram, Threads, Bluesky, Pinterest, TikTok, YouTube, Twitch y Google Business Profile. Sin LinkedIn ni X | Empresa española |
| Publer | 3 cuentas, 10 posts programados por cuenta | Sin X | 24 h de historial |
| Later | Solo prueba de 14 días | — | — |
| Hootsuite | Sin plan gratuito desde 2023 | — | Prueba de 14 o 30 días |
| Repurpose.io | No hay plan gratuito. De 25 a 35 $/mes (las fuentes no coinciden) | YouTube, Facebook, Instagram, TikTok, LinkedIn, X, Spotify, RSS | Dicen que quita la marca de agua de TikTok al redistribuir [NO CONFIRMADO] |

- **¿Penalizan las plataformas a las herramientas?** No hay ningún estudio independiente que lo pruebe. Los tests de los propios proveedores (Hootsuite, Metricool, Agorapulse) no ven penalización, pero con muestras pequeñas: Hootsuite usó 5 posts por método. La cifra de "−80 %" no tiene metodología localizable [NO CONFIRMADO].
- **Casilla IA desde herramientas.** En TikTok, la API expone `is_aigc`. Ayrshare, upload-post y Postiz la documentan, y Ayrshare dice que no se puede cambiar una vez publicada. Algunos proveedores dicen que la subida a la bandeja de borradores (inbox) no la lleva [NO CONFIRMADO]. En YouTube la API permite `containsSyntheticMedia`. En Instagram y Facebook no se encontró un campo equivalente en la API: **si la herramienta no lo permite, el post sale sin la etiqueta "AI info"**. Motivo para publicar a mano o desde Meta Business Suite.

## Respuestas pregunta por pregunta

### 1. Contenido reutilizado o traducido

- **YouTube.** El 15-jul-2025, "repetitious content" pasó a llamarse "inauthentic content" (contenido producido en masa o repetitivo). YouTube lo presentó como una aclaración, no como una regla nueva, y la política de "reused content" no cambió. Las dos son **políticas del YPP**: si se incumplen, se pierde o se deniega la monetización y la decisión se aplica a nivel de canal. No llevan a retirar vídeos. Entre los ejemplos de contenido reutilizado está "readings of text you didn't write" [TERCEROS citando la ayuda]. Además, la política de reutilizado aplica **aunque tengas permiso** del creador original [TERCEROS]. **Qué cambia en este caso:** como no se monetiza, no hay consecuencia directa. Si algún día se quisiera entrar en el YPP, habría que defender el valor añadido: traducción, doblaje y visualización sincronizada. Las normas de comunidad sobre spam aplican igualmente, monetices o no.
- **TikTok.** El contenido no original o reproducido sin cambios nuevos o creativos queda fuera del For You [OFICIAL]. Si se repite, la cuenta entera puede quedar temporalmente fuera [OFICIAL]. TikTok no publica un umbral. Que la traducción doblada cuente como "cambio creativo" es defendible, pero no está confirmado.
- **Instagram.** Desde 2022 se recomiendan menos los reposts y las cuentas agregadoras, y desde 2024 la copia se sustituye por el original con una etiqueta. En abr-may 2026 se amplió: las cuentas que sobre todo republican podrían no recomendarse a quien no las sigue [TERCEROS: PetaPixel, 30-abr-2026]. Mosseri recomienda añadir voz en off o comentario propio, o hacer un collab con el autor [TERCEROS].
- **Facebook.** El 14-jul-2025 Meta lo definió así: "repeated reposting of content from other creators without permission or meaningful enhancements". Se pierde la monetización durante un tiempo y bajan las distribuciones, y las copias duplicadas también reciben menos alcance. Meta actuó contra ~500.000 cuentas en el primer semestre de 2025 [OFICIAL vía prensa]. "Without permission" encaja con el caso mientras no haya permiso.
- **Spotify.** Exige tener los derechos ("must have all rights to use and post the content", política de Clips). Las Rights Claims se aplican **solo a vídeo** [OFICIAL].
- **Encaje de una traducción doblada sin permiso.** Es una **obra derivada no autorizada**. Las políticas de originalidad (alcance) son el problema menor. El problema real son los derechos (punto 3).

### 2. Etiquetado de IA

- **YouTube** [OFICIAL, ayuda 14328491 vía búsqueda]. Hay que declarar el contenido realista alterado o sintético. Entre los ejemplos está "voice cloning someone else's voice to use it for voiceover". No hace falta declarar lo irreal ni los retoques menores. Hay un matiz: una voz genérica que no se parece a nadie podría no requerir etiqueta [TERCEROS: AIR]. **En este caso, marcar "sí"**: la voz habla en nombre de una persona real y probablemente está clonada de ella. La etiqueta va bajo el reproductor, encima de la descripción; en Shorts, superpuesta al vídeo (anuncio del 27-may-2026). Según 9to5Google, en Shorts va abajo a la izquierda. Desde esa fecha YouTube también detecta y etiqueta automáticamente, en parte con C2PA. Quien no declare de forma reiterada se arriesga a que YouTube ponga la etiqueta, a retiradas y a sanciones del YPP [TERCEROS]. La etiqueta no afecta a recomendaciones ni a monetización [OFICIAL vía prensa].
- **TikTok.** Hay que etiquetar el contenido generado por IA con imágenes, audio o vídeo realistas, incluido el habla generada por IA. TikTok puede retirar el contenido sin etiqueta [TERCEROS citando las normas]. Las cifras de "strike inmediato" y "7 días de restricción" solo salen en blogs [NO CONFIRMADO]. Etiqueta automática por C2PA desde may-2024, irremovible [OFICIAL vía prensa].
- **Meta.** Es obligatorio usar la herramienta de etiquetado en "photorealistic video or realistic-sounding audio that was digitally created or altered", y puede haber sanciones si no se hace (feb-abr 2024) [OFICIAL]. La etiqueta se llama "AI info" desde el 1-jul-2024. No se encontraron datos sobre su efecto en el alcance.
- **Spotify.** No hay etiqueta para pódcast. Sí hay política de suplantación: retira contenido que imite la voz o la imagen de un creador sin permiso, aunque se presente como "AI version". Hay excepciones, como la parodia [OFICIAL, support.spotify.com/creators/article/impersonation-policy]. En mayo de 2026 se reafirmó y llegó la insignia "Verified by Spotify". Las credenciales DDEX de IA (sep-2025) son solo para música.
- **LinkedIn.** Solo lee el C2PA del fichero; no analiza el contenido [OFICIAL]. Lo normal es que ffmpeg o Remotion no escriban C2PA, así que no aparecerá ninguna etiqueta. **Declarar la IA en el texto del post.**
- **Ley de IA de la UE, art. 50(4).** Desde el **2-ago-2026**, quien despliega un sistema que genera deepfakes de audio (que se parecen a personas existentes y pueden parecer auténticos) debe revelar que es artificial [TERCEROS: guías legales sobre la Ley de IA; texto en ai-act-service-desk.ec.europa.eu]. Una voz clonada de Naval leyendo palabras que él dijo, pero en otro idioma, puede encajar. Con declararlo en pantalla y en la descripción basta en la práctica (marco orientativo, no es asesoría legal).

### 3. Derechos de autor y suplantación

- **Copyright.** La traducción es transformación: el autor tiene el derecho exclusivo de autorizarla (TRLPI arts. 17 y 21.1; en EE. UU., 17 USC §106(2)). En *Radji v. Khakbaz* (D.D.C. 1985) y *Merkos v. Otsar* (2d Cir. 2002), traducciones no autorizadas **no** se consideraron *fair use* [TERCEROS: resúmenes de copyright.gov]. Hay cuatro vías de reclamación:
  1. **Content ID.** Probablemente no detecte nada: otro idioma, otra voz, otra imagen [inferido, NO CONFIRMADO].
  2. **Retirada manual por copyright o DMCA.** Es el riesgo real. Cada retirada es un strike: caduca en 90 días si se completa Copyright School, y con 3 en 90 días se cierra el canal y los canales vinculados [TERCEROS: Wikipedia, AIR]. La contranotificación existe, pero tiene riesgo legal. Los 10-14 días hábiles de §512(g) no se verificaron en la ayuda de YouTube.
  3. **Rights Manager de Meta.** Bloquea, monitoriza, reclama ingresos o denuncia [OFICIAL]. Solo funciona si Naval sube sus vídeos como referencia.
  4. **Rights Claims de Spotify** sobre el vídeo.
- **Suplantación de voz.** Si la voz imita a Naval: YouTube tiene una vía de privacidad para contenido sintético que simula a una persona identificable. La pide la propia persona; se valora si es realista, si está declarado y si es parodia; el subidor tiene 48 h; no hay strike [TERCEROS, jul-2024]. La detección de semejanza (21-oct-2025) **solo busca caras**, no voces [TERCEROS]. En Spotify, retirada directa. **Aunque la voz no imite la suya**, presentar el canal como "Naval en español" puede dar pie a una reclamación por suplantación de identidad. Mitigación: canal y portada con el nombre del proyecto, no "Naval Ravikant", y aviso de no afiliación.
- **Imprescindible en la descripción (plantilla):**
  > Traducción NO oficial al español de «<título original>», de Naval Ravikant (<fecha>). Original: https://nav.al/<slug>. Voz sintética generada con IA; no es la voz real de los participantes. Proyecto sin ánimo de lucro, sin afiliación con Naval Ravikant. Derechos del contenido original: sus autores. [Cuando haya permiso: «Publicado con permiso de Naval Ravikant».]

  En TikTok y Reels, una versión corta en pantalla en los primeros 2-3 s o al final: "Traducción no oficial · voz IA · nav.al/<slug>".

### 4. Fair use y excepciones en la UE y España (marco, no asesoría)

- En la UE no hay *fair use*, solo una lista cerrada de excepciones. La cita (TRLPI art. 32) exige fragmentos y fines de análisis, comentario o docencia: no cubre una traducción íntegra. La parodia es otro límite de la transformación, y no aplica aquí. "Sin ánimo de lucro" no es una excepción a la transformación ni a la comunicación pública.
- EE. UU.: no ser comercial ayuda pero no decide. Copiar la obra entera pesa mucho en contra.
- Naval dijo en 2021, en una Q&A de Clubhouse sobre sus tuits: "By all means, translate into whatever languages you want" [TERCEROS: transcripción automática en ceointerviews.ai]. **No es una licencia**: es verbal, se refiere a tuits y no cubre el pódcast ni el doblaje con voz sintética. Además, el pódcast tiene coautores: Nivi y los invitados (Brett Hall, David Deutsch…) tienen derechos sobre lo que dicen ellos.
- **Con permiso escrito, documentar:**
  1. Alcance: traducción, doblaje TTS, uso de voces clonadas (si las hay), vídeo largo y corto, plataformas concretas, territorio y duración.
  2. Atribución exigida.
  3. Revocación.
  4. Firmantes: Naval y, si se puede, Nivi y los invitados.

  Guardarlo en Drive (`naval-podcast/permisos/`), con el file ID en el repo. Pedir que añadan el canal a su **lista de autorización de Content ID** ("Exempt channels from Content ID claims", ayuda 6070344 [OFICIAL vía búsqueda]). Esa lista es por canal, no por vídeo, no libera las reclamaciones anteriores y cada socio titular de un recurso tiene que añadirlo por separado. También conviene enviarlo a Spotify si llega un Rights Claim.

### 5. Vías de subida

Las cifras están en la tabla de arriba. Para este proyecto:

- **YouTube:** web (Studio), con casilla IA y programación.
- **TikTok:** TikTok Studio en escritorio, que sube máster sin recomprimir en el móvil, con la casilla IA y programación de 10 a 30 días.
- **Reels:** Meta Business Suite (75 días, 25 al día), con "AI info" en la app o en Business Suite (comprobar que Business Suite muestre el selector: no confirmado).
- **LinkedIn:** web.

Por API, TikTok e Instagram exigen auditoría o una app de Meta revisada, y TikTok obliga a publicar en privado mientras tanto. No compensa para un creador sin monetizar.

### 6. Herramientas de terceros

Las cifras están en la tabla de herramientas. Metricool o Buffer gratis bastan para 2-3 redes con poco volumen. Riesgo principal: que la herramienta no permita la etiqueta "AI info" de Meta ni la portada personalizada. La portada en TikTok por API está limitada a un fotograma (`video_cover_timestamp_ms`) [inferido, NO CONFIRMADO].

### 7. Marcas de agua cruzadas

Instagram (feb-2021) hace menos descubribles los Reels con logo o marca de agua de TikTok, aunque los seguidores los siguen viendo. Mosseri confirmó que el logo propio no penaliza [TERCEROS: Social Media Today]. No se encontraron datos de 2025-2026 que lo cambien. **Exportar un máster limpio por plataforma** desde el render: la marca del proyecto vale, la de otra app no. Nunca descargar de TikTok para resubir.

### 8. Recomendación final

**Flujo:**

1. El render saca un máster por formato (16:9 largo, 9:16 clip) **sin marcas de otras apps**, con el aviso "Traducción no oficial · voz IA" en pantalla.
2. **A mano:** YouTube largo en Studio (IA: sí, descripción con la plantilla) y Spotify for Creators (vídeo).
3. **Programado de forma nativa:**
   - Shorts en YouTube Studio (IA: sí).
   - TikTok en TikTok Studio, desde escritorio (IA: sí).
   - Reels e Instagram/Facebook en Meta Business Suite (AI info: sí). Si Business Suite no muestra el selector, desde la app.
   - LinkedIn en el programador nativo, con la IA declarada en el texto.
4. **Automatizable más adelante:** solo YouTube por Data API, subiendo en privado con `containsSyntheticMedia=true`, título, descripción y miniatura, y publicando a mano en Studio. Encaja con la decisión ya tomada en `CLAUDE.md`.
5. Antes de abrir TikTok e Instagram, conviene tener el permiso, o al menos haberlo pedido.

**Riesgos mientras no haya permiso, de mayor a menor:**

1. Retirada por copyright o DMCA (Naval, sus representantes o los coautores), con strikes y el cierre del canal de YouTube a los 3.
2. Retirada por suplantación o semejanza de voz, si las voces están clonadas: Spotify (directa), YouTube (privacidad, 48 h) y Meta/TikTok por no etiquetar.
3. Incumplir el art. 50 de la Ley de IA de la UE si no se declara la voz sintética.
4. Pérdida de alcance por "no original" en TikTok (fuera del FYF) e Instagram/Facebook (menos recomendaciones y distribución).
5. Etiqueta automática irremovible o retirada si no se marca la casilla de IA.
6. Que el YPP quede vetado por "reused/inauthentic" si algún día se quiere monetizar.
7. Herramientas de terceros que publiquen sin la etiqueta IA de Meta.

## Qué evitar

- Llamar al canal o la cuenta "Naval Ravikant" o usar su foto como avatar.
- Publicar sin la casilla de IA o sin el aviso "traducción no oficial".
- Resubir vídeos descargados de TikTok con su marca de agua en Reels o Shorts.
- Publicar en Instagram/Facebook con una herramienta que no ponga "AI info".
- Dar por bueno el "translate into whatever languages" de 2021 como licencia.
- Contranotificar un DMCA sin asesoría.
- Publicar muchos clips casi idénticos del mismo episodio: es lo que se considera repetitivo o producido en masa.
- Montar la automatización de TikTok o Instagram por API antes de pasar la auditoría (todo quedaría en privado).

## Dudas abiertas / no confirmado

- **Comprobar en el repo si las voces de `fabrica/voces.json` son clones de los hablantes reales.** Cambia el nivel de riesgo de los puntos 2 y 3.
- Coste real de `videos.insert`: 1.600 unidades frente a ~100 desde dic-2025, y si la subida forzada a privado sigue vigente.
- Plazo de programación de TikTok Studio: 10 o 30 días.
- Meta Business Suite: 75 o 29 días, y si muestra el selector "AI info".
- Instagram API: si las cuentas Creator pueden publicar.
- Si Meta tiene la etiqueta IA en la API.
- TikTok API: límite de 5 usuarios y 15 posts/día; `is_aigc` en la subida a borradores.
- Sanciones concretas de TikTok por no etiquetar (strike o 7 días).
- Posición exacta de la etiqueta IA en Shorts (abajo a la izquierda frente a superpuesta).
- Duración máxima en LinkedIn (10 o 15 min) y su plazo de programación.
- Requisitos y plazos de Rights Manager de Meta en 2025-2026.
- Penalización de Instagram por marca de agua: solo hay datos de 2021.
- Precios de Repurpose.io y si quita la marca de agua.
- Ley española de etiquetado de IA (anteproyecto de 2025): no investigada.

## Fuentes

Todas consultadas el 18-nov-2026 por WebSearch. Las fechas son las de publicación de cada página, cuando se conocen.

**YouTube**
- Ayuda "Disclosing use of altered or synthetic content": https://support.google.com/youtube/answer/14328491 [OFICIAL, sin fecha visible]
- Políticas de monetización del canal (reused/inauthentic): https://support.google.com/youtube/answer/1311392 [OFICIAL]
- Lista de autorización de Content ID: https://support.google.com/youtube/answer/6070344 [OFICIAL]
- Blog de YouTube sobre la etiqueta (mar-2024) [ANTIGUO: 2024]: https://blog.youtube/news-and-events/disclosing-ai-generated-content
- `videos.insert` (1.600 unidades; privado si no está verificado): https://developers.google.com/youtube/v3/docs/videos/insert
- Calculadora de cuota: https://developers.google.com/youtube/v3/determine_quota_cost
- Historial de revisiones de la API (`containsSyntheticMedia`, 30-oct-2024): https://developers.google.com/youtube/v3/revision_history
- Política "inauthentic content", 15-jul-2025: https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/ y https://ppc.land/youtube-clarifies-inauthentic-content-policy-changes/
- Cambio de etiquetas IA y autodetección, 27/28-may-2026: https://9to5google.com/2026/05/27/youtube-updating-ai-content-labels/ , https://www.washingtontimes.com/news/2026/may/28/youtube-automatically-detecting-content-ai-generated/ y https://www.hollywoodreporter.com/business/digital/youtube-ai-label-more-prominent-videos-shorts-1236605979/
- Detección de semejanza, 21-oct-2025: https://techcrunch.com/2025/10/21/youtubes-likeness-detection-technology-has-officially-launched
- Retirada por privacidad de IA, jul-2024 [ANTIGUO: 2024]: https://www.tubefilter.com/2024/07/02/youtube-ai-likeness-removed-privacy-violation/
- Strikes: https://en.wikipedia.org/wiki/YouTube_copyright_strike
- Divulgación de IA según AIR (2026): https://air.io/en/youtube-hacks/youtube-ai-disclosure-in-2026-label-it-yourself-or-youtube-will

**TikTok**
- Normas de integridad y autenticidad (FYF, IA): https://www.tiktok.com/community-guidelines/en/integrity-authenticity/ [OFICIAL]
- Content Posting API, Direct Post (privado sin auditar, `is_aigc`): https://developers.tiktok.com/doc/content-posting-api-reference-direct-post [OFICIAL]
- C2PA, may-2024 [ANTIGUO: 2024]: https://fortune.com/2024/05/09/tiktok-deepfakes-ai-labels-content-credentials-adobe/
- Divulgación de IA en TikTok según Hootsuite: https://blog.hootsuite.com/ai-disclosure-policy-for-tiktok/
- Aprobación de la API (2026): https://bundle.social/blog/tiktok-api-approval y https://adaptlypost.com/blog/why-does-my-app-need-approval-post-tiktok
- `is_aigc` documentado por un proveedor: https://www.ayrshare.com/docs/apis/post/social-networks/tiktok
- Programación: https://adamconnell.me/schedule-tiktok-posts/ y https://postfa.st/blog/how-to-schedule-tiktok-posts-on-desktop

**Meta**
- Blog de creadores "Combating unoriginal content", 14-jul-2025: https://creators.facebook.com/blog/combating-unoriginal-content
- Cobertura: https://www.socialmediatoday.com/news/facebook-cracking-down-unoriginal-content-ai-replicas/753001/
- Etiquetado de IA (abr-2024, actualizado el 1-jul-2024) [ANTIGUO: 2024]: https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/
- Etiquetado de imágenes con IA (feb-2024): https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/
- "AI info" pasa al menú, 12-sep-2024: https://techcrunch.com/2024/09/12/meta-is-making-its-ai-info-label-less-visible-on-content-edited-or-modified-by-ai-tools
- Content Publishing API (50 por 24 h): https://developers.facebook.com/docs/instagram-platform/content-publishing/
- Límite de publicación (`content_publishing_limit`): https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/content_publishing_limit
- Protección de propiedad intelectual / Rights Manager: https://transparency.meta.com/data/intellectual-property/protecting-intellectual-property-rights/
- Reposts en Instagram, 30-abr-2026: https://petapixel.com/2026-04-30/new-instagram-policies-target-reposted-content/
- Marca de agua de TikTok, feb-2021 [ANTIGUO: 2021]: https://tubefilter.com/2021/02/10/instagram-reels-with-tiktok-watermark-less-discoverable/ y https://www.socialmediatoday.com/news/instagram-clarifies-including-your-own-logo-on-a-reel-is-ok/730852
- Programar Reels: https://www.socialpilot.co/blog/schedule-instagram-reels

**Spotify**
- Política de suplantación: https://support.spotify.com/us/creators/article/impersonation-policy/ [OFICIAL]
- Política de Clips: https://support.spotify.com/us/creators/article/clips-content-policy/ [OFICIAL]
- Copyright para creadores: https://creators.spotify.com/resources/copyright-creator-education [OFICIAL]
- Protecciones de IA, sep-2025: https://au.variety.com/2025/digital/news/spotify-new-ai-safeguards-28228
- Verificación y suplantación, may-2026: https://ppc.land/spotifys-new-verified-badge-and-ai-voice-cloning-ban-shake-up-podcast-trust/

**LinkedIn**
- Content credentials: https://www.linkedin.com/help/linkedin/answer/a6282984 [OFICIAL]
- C2PA en vídeo, 26-nov-2024 [ANTIGUO: 2024]: https://fortune.com/2024/11/26/linkedin-content-credentials-labeling-challenges-c2pa/
- Especificaciones de vídeo (2026): https://quso.ai/blog/linkedin-video-specs

**Derecho**
- Ley de IA de la UE, art. 50: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50 [OFICIAL]
- Guía práctica del art. 50: https://artificialintelligenceact.eu/transparency-rules-article-50/
- Entrada en vigor, 2-ago-2026: https://www.traverssmith.com/knowledge/knowledge-container/is-it-a-bot-eu-ai-act-transparency-rules-take-effect-2-august-2026/
- TRLPI (RDL 1/1996): https://www.kids.csic.es/pdf/rdlegislativo1996.pdf
- Derecho de transformación, art. 21: https://vlex.es/vid/derecho-transformacion-articulo-21-679166297
- Radji v. Khakbaz: https://www.copyright.gov/fair-use/summaries/radj-khakbaz-ddc1985.pdf
- Merkos v. Otsar: https://www.copyright.gov/fair-use/summaries/merkos-otsar-2dcir2002.pdf
- Cita de Naval (2021): https://ceointerviews.ai/interview/972748/ [TERCEROS]

**Herramientas**
- Buffer: https://buffer.com/pricing
- Metricool: https://metricool.com/metricool-vs-buffer/ y https://www.socialpilot.co/insights/metricool-pricing
- Publer y Hootsuite: https://publer.com/blog/hootsuite-alternatives/
- Later y Hootsuite: https://costbench.com/compare/later-vs-hootsuite/
- Repurpose.io: https://socialrails.com/blog/repurpose-io-pricing y https://shortsync.app/resources/repurpose-io-pricing-vs-alternatives
- Test de programación de Hootsuite: https://blog.hootsuite.com/experiment-third-party-scheduling-instagram/
- Test de programación de Metricool: https://metricool.com/does-scheduling-social-media-posts-affect-reach/
- Test de terceros en Instagram de Agorapulse: https://agorapulse.com/social-media-lab/instagram-3rd-party-tools