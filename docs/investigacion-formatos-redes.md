# Investigación: formatos de vídeo por plataforma (18-nov)

> Workflow de 8 agentes (orquestador + 6 investigadores + síntesis). **Las páginas oficiales estaban bloqueadas desde la sesión**: las cifras [OFICIAL] salen de extractos del buscador. Comprobar las críticas en la propia plataforma antes de fijarlas. Informes completos en `docs/investigacion-formatos-redes-informes.md`.


Orquestador, fase final. Fecha: 18-nov-2026.

**Cómo se ha verificado.** Ninguno de los seis investigadores pudo abrir las páginas oficiales (support.google.com, help.instagram.com, developers.facebook.com, tiktok.com, support.spotify.com, help.x.com, linkedin.com). Todos dieron ENOTFOUND o un bloqueo del proxy. Las cifras [OFICIAL] salen de extractos del buscador, no de una lectura completa de la página. No he repetido la verificación web porque los dominios bloqueados son los mismos. Sí he comprobado una cosa en el repo que cambia el análisis de riesgos (ver §4.1): **las voces son clones de las personas reales**. `fabrica/voces.json` usa Qwen3-TTS en modo `x_vector` con referencias `speaker_refs/naval/naval_ref02.wav`, `nivi/…`, `brett/…`, `deutsch/…` y otras, y `docs/fabrica-de-voz.md` dice: «El clon tiene que ser lo más perfecto posible… se cortan 2 o 3 clips del propio episodio original».

## Resumen accionable

1. **Hay que generar dos másters.**
   - **16:9 de 1920x1080 a 50 fps** para el episodio completo (YouTube, Spotify y, si acaso, Facebook o X Premium).
   - **9:16 de 1080x1920 a 30 fps** para los clips, uno solo que sirva para todas las apps verticales.
   - No compensa generar 4:5 ni 1:1 si el texto del vertical está dentro de la zona segura común.
2. **Zona segura común del vertical, donde va todo el texto importante:** **x 120–888 e y 288–1248**, un rectángulo de 768x960 px. Entre y 840 y 1248 el texto no debe pasar de x ≈ 820, por la columna de botones de TikTok y Reels. Por debajo de y 1248 no va nada.
3. **El tambor en vertical tiene dos frases, no tres.** La actual va a 72–76 px, en 3 líneas como máximo de unos 20–24 caracteres, centrada ópticamente en y ≈ 820. La siguiente va a 46–48 px, atenuada al 55 %. La anterior queda desactivada por defecto. El título y el hablante van en la cabecera (y 300–440), nunca abajo.
4. **El tambor en 16:9:** la frase actual a 84 px dentro de x 192–1728, la siguiente sin pasar de y ≈ 860, y y 900–1080 libre para los controles y los subtítulos de YouTube. En los últimos 20 s se deja hueco para la pantalla final.
5. **Duración de los clips:** el valor por defecto es de 45 a 90 s, que cabe en todas las plataformas, Spotify Clips incluido. El techo es de 180 s. De 140 a 180 s ya no entra en X con cuenta gratuita. De 90 a 180 s no entra en Spotify Clips.
6. **Los episodios largos tienen que caber en 10 GB.** Es lo que recomienda Spotify y el límite duro de Facebook, que además exige menos de 240 min. Con 4 h eso deja unos 5,5 Mbps de media en total. Un vídeo de texto sobre fondo liso queda muy por debajo con CRF.
7. **Subtítulos.** Subir un **.srt en español** generado desde `transcript.es.json` en YouTube, Facebook (Página), LinkedIn y X. **Desactivar** los subtítulos automáticos de Instagram y TikTok y el **doblaje automático de YouTube**.
8. **Etiqueta de IA en todas las plataformas, siempre:** YouTube («alterado/sintético: sí»), TikTok («AI-generated content»), Meta («AI info») y un texto en el post de LinkedIn. Además, un aviso en pantalla y en la descripción: «Traducción no oficial · voz sintética (IA) · nav.al/<slug>».
9. **El mayor riesgo no es técnico.** Sin permiso de Naval hay dos problemas: la traducción es una obra derivada no autorizada, y **la voz es un clon de personas reales**. La política de suplantación de Spotify retira los programas que imitan la voz de alguien sin su permiso, aunque se presenten como «versión IA». Los Shorts, Reels y TikToks multiplican la superficie expuesta. Conviene tener el permiso, o al menos haberlo pedido, antes de publicar clips en volumen.

---

## 1. Tabla maestra por plataforma

| Plataforma / formato | Exportar | fps | Códec / bitrate | Audio | Duración máx. → óptima | Tamaño máx. | Subtítulos | Portada | Vía de subida |
|---|---|---|---|---|---|---|---|---|---|
| **YouTube largo** | 1920x1080 16:9 | 50 (admitido) | H.264 High, 4:2:0, BT.709, GOP cerrado de 25 fotogramas, moov al inicio. Recomendación de YouTube: 12 Mbps para 1080p50 SDR [OFICIAL, cotejo parcial]. Para texto basta CRF 18–20 | AAC-LC 48 kHz, estéreo a 384 kbps [OFICIAL]. Sonoridad: −14 LUFS y −1 dBTP [TERCEROS] | 12 h o 256 GB; más de 15 min exige cuenta verificada [OFICIAL] | 256 GB | .srt en UTF-8, sin estilos [OFICIAL] | 1280x720, JPG de ≤2 MB (los 50 MB desde escritorio no están confirmados) | Studio web a mano (ya decidido). Más adelante, por API: sube en privado con `containsSyntheticMedia=true` y se publica a mano |
| **YouTube Shorts** | 1080x1920 9:16 (también 1:1) | 30 (también se admiten 24–60) | H.264, 8–12 Mbps | ídem, 192 kbps | **≤3 min** para que cuente como Short [OFICIAL] → 45–90 s | — | .srt opcional | Miniatura propia desde escritorio desde jul-2026, quizá solo con YPP [TERCEROS]. Sin eso, se elige un fotograma, así que conviene preparar un fotograma de portada | Studio de escritorio. Allí se enlaza el «vídeo relacionado» con el episodio, a mano, porque la API no lo permite [TERCEROS] |
| **Instagram Reels** | 1080x1920 | 30. La API admite 23–60 [OFICIAL]; que conserve 50 fps no está confirmado | H.264 High, 8–12 Mbps. Tope de la API: 25 Mbps VBR y 300 MB [OFICIAL] | AAC 48 kHz, −14 LUFS [TERCEROS] | App: 20 min. API: 15 min. **Se recomienda a no seguidores solo si dura ≤3 min** [OFICIAL] → 45–90 s | API: 300 MB. App: unos 4 GB [TERCEROS] | **No admite .srt.** Hay que quitar el sticker de subtítulos automáticos | 1080x1920. La cuadrícula del perfil muestra la franja central 3:4 (y 240–1680) | App o Meta Business Suite, con «AI info» activado. Comprobar que Business Suite muestra esa opción |
| **Instagram Stories** | 1080x1920 | 30 | ídem | ídem | 60 s por segmento [OFICIAL] | — | — | — | App. El sticker de enlace solo se pone a mano |
| **Facebook (todo es Reel desde jun-2025)** | 1080x1920 para clips; 1920x1080 para episodios | 30 / 50 | H.264, ≤1080p | AAC estéreo a ≥128 kbps [OFICIAL] | Página: **<240 min y 10 GB** [OFICIAL]. Los episodios de 4 h o más se parten | 10 GB | **.srt sí**, con el nombre `archivo.es_ES.srt` en vídeo de Página [OFICIAL] | — | Business Suite, de forma nativa. Mejor no usar la publicación cruzada desde Instagram |
| **TikTok** | 1080x1920. No subir 4K, porque lo baja a 1080p | 30. La API admite 23–60 [OFICIAL]; que conserve 50 fps no se ha encontrado | H.264 High, 10–15 Mbps [NO CONFIRMADO] | AAC, −14 LUFS [NO CONFIRMADO] | Web: 60 min [OFICIAL, 2023]. API: 10 min → 45–90 s | Web: 10 GB [OFICIAL, 2023; hay cifras contradictorias]. API: 4 GB | **No.** Desactivar los subtítulos automáticos | Se elige un fotograma; que se pueda subir una imagen propia es contradictorio. La cuadrícula recorta a unos 3:4 | TikTok Studio en escritorio, con «AI-generated content» activado. La API sin auditar solo publica en privado |
| **Spotify (episodio)** | **Solo 1920x1080 16:9.** Un vertical sale con bandas | 50 [OFICIAL] | H.264 MP4, SDR Rec.709. Se recomienda 1 keyframe por segundo; el mínimo obligatorio es 1 cada 60 s [OFICIAL]. Para texto, 2–5 Mbps | AAC-LC a ≥128 kbps, estéreo | Admite hasta 12 h; se recomiendan <4 h | Admite 60 GB; **se recomiendan <10 GB** | Spotify genera los suyos | 1920x1080 16:9 [OFICIAL] | S4C web, «Upload video» sobre el episodio que llega por RSS. Comprobar en la cuenta real que la opción existe para RSS externo (ver §6) |
| **Spotify Clips** | 1080x1920 (mínimo 768x1024) | — | MP4/MOV | obligatorio | **15–90 s** [OFICIAL], **1 por episodio** | 1 GB | automáticos, que se revisan | — | Solo desde la web. No está confirmado que lo admitan programas con RSS externo |
| **X** | 1080x1920 para clips; 1920x1080 para el episodio con Premium | 30 (≤60) | H.264 + AAC | — | Cuenta gratuita: **140 s y 512 MB**. Premium: 4 h en web e iOS [TERCEROS] | 512 MB / 8–16 GB | **.srt sí**, desde la web [OFICIAL] | — | Web |
| **Bluesky** | 1080x1920 | 30 | MP4 | — | 10 min, desde ago-2026 [TERCEROS] | 300 MB | no encontrado | — | App o web |
| **Threads** | 1080x1920 | 30 | MP4 | — | 5 min [TERCEROS] | 1 GB | no encontrado | — | App |
| **LinkedIn** | 1080x1920 (admite de 1:2,4 a 2,4:1) | 10–60 | H.264 | — | 15 min en escritorio, 10 min en móvil [TERCEROS] | 5 GB [OFICIAL] | **.srt sí**, solo desde escritorio, con formato estricto | — | Web. Prioridad baja |
| Apple Podcasts | solo audio | — | — | — | — | — | — | — | El vídeo HLS solo entra vía un host con Podcasts Connect API, así que se descarta |
| Pinterest, Snapchat | — | — | — | — | — | — | — | — | Descartar: no hay specs oficiales verificables y no encajan con este contenido |

---

## 2. Zonas seguras

### 2.1 Vertical 1080x1920: qué tapa cada app (en px)

| App (fuente) | Arriba | Abajo | Izq. | Der. | Qué tapa | Confianza |
|---|---|---|---|---|---|---|
| YouTube Shorts (plantilla atribuida a Google, anuncios) | 288 | 672 | 48 | 192 | Arriba: búsqueda, menú y cámara. Derecha: like, dislike, comentarios, compartir, remix y disco. Abajo: canal, Suscribirse, título, sonido, barra de progreso y navegación | [TERCEROS] |
| Shorts orgánico | 154–180 | 380–400 | — | 120 | lo mismo | [NO CONFIRMADO] |
| Meta Reels/Stories (anuncios: 14 % / 35 % / 6 %) | 269 | 672 (768 con aviso legal) | 65 | 65 | Arriba: cabecera «Reels» y cámara. Abajo: avatar, usuario, Seguir, descripción, audio y CTA. Derecha (y ≈ 1100–1800): me gusta, comentar, compartir, guardar y disco | [OFICIAL vía extracto] |
| Reels orgánico | 220–250 | 280–420 | — | 84–140 | lo mismo | [TERCEROS] |
| Stories | 250 | 250–340 | — | — | barra de progreso, avatar y cerrar; «Enviar mensaje» | [TERCEROS] |
| TikTok, plantilla In-Feed (720x1280 escalada x1,5) | 240 | 660 | 120 | 120, más la columna de botones (180–300 px de ancho) desde y ≈ 840 | Arriba: Siguiendo / Para ti, búsqueda y LIVE. Derecha: avatar, me gusta, comentarios, guardar, compartir y disco. Abajo: usuario, descripción (crece si es larga), sonido, etiqueta de IA (abajo a la izquierda) y navegación | [TERCEROS] medido sobre la plantilla oficial |
| TikTok orgánico | 108–160 | 320–484 | 40–120 | 120–180 | lo mismo | [NO CONFIRMADO] |
| X, visor vertical | — | unos 400 | — | unos 140 | controles y botones | [NO CONFIRMADO] |
| LinkedIn | unos 150 | unos 300 | — | unos 100 | — | [NO CONFIRMADO] |
| Spotify Clips | no encontrado | no encontrado | — | — | — | — |

**Zona común estricta** (la peor cifra de cada borde): **arriba 288, abajo 672, izquierda 120, derecha 192**. Queda el rectángulo **x 120–888, y 288–1248** (768x960). Su centro óptico está en **y ≈ 820**, no en 960. **Excepción:** entre y 840 y 1248 hay que limitar el borde derecho del texto a **x ≤ 820**, porque ahí empieza la columna de botones de TikTok y Reels. Con texto centrado de 3 líneas casi nunca se llega a ese borde.

**Recortes de las vistas previas:** el feed 4:5 de Instagram muestra y 285–1635, y la cuadrícula 3:4 de Instagram y TikTok muestra y 240–1680. La zona estricta ya cae dentro de ambas, así que **no hace falta un render aparte en 4:5**. El único caso que no cubre es el recorte pesimista de TikTok (y 420–1500, sin confirmar), y solo afecta a la portada. Por eso el fotograma de portada se diseña con el texto en **y 420–1248**.

**Tolerancia en orgánico** (no se diseña para ella, pero tranquiliza): x 96–900, y 250–1440. Si algo se sale un poco de la zona estricta, no lo tapan del todo.

### 2.2 Horizontal 1920x1080 (YouTube, Spotify y Facebook)

| Elemento | Zona | Fuente |
|---|---|---|
| Title-safe | 5 % por lado: 96 px a los lados, 54 px arriba y abajo | [OFICIAL EBU/SMPTE] |
| Controles y barra de progreso de YouTube | unos 110–150 px inferiores, al pasar el ratón o en pausa | [NO CONFIRMADO] |
| Subtítulos de YouTube | abajo y centrados, y ≈ 860–1000 | [NO CONFIRMADO] |
| Marca de agua del canal | esquina inferior derecha, unos 150x150 | [NO CONFIRMADO] |
| Icono de tarjetas y menú | arriba a la derecha | [NO CONFIRMADO] |
| Pantalla final | últimos 5–20 s; el vídeo tiene que durar ≥25 s; hasta 4 elementos [OFICIAL]. Cada elemento mide unos 613x343 y el de suscripción 294x294 [TERCEROS] | — |
| Spotify | no hay datos de su UI. Se aplica el 5 % estándar (unos 90 px abajo y 60 arriba) | [NO CONFIRMADO] |

**Regla:** no poner texto en **y > 900**. La esquina inferior derecha y la superior derecha quedan libres. En los últimos 20 s el tambor se reduce a la mitad izquierda o superior, y queda libre x 960–1824 / y 200–900.

---

## 3. Reglas de texto en pantalla

### 3.1 Comunes
- **Fondo** plano y oscuro (#0E0E10–#141416), sin degradados ni viñetas. Si se quiere uno, llevará un 1–2 % de grano para evitar bandas al recomprimir [TERCEROS].
- **Contraste:** blanco sobre #111 da 18,9:1. Las frases atenuadas llevan **≥45 % de opacidad** (4,5:1, el mínimo AA) y se recomienda el **55 %** (#949494, 6,2:1). Conviene atenuar con un color plano en lugar de alfa.
- **Tipografía:** Atkinson Hyperlegible Next (OFL, variable) o Inter / Noto Sans, a peso 600–700 en la frase activa y nunca ≤300. El grosor de asta debe ser de 4–5 px o más. Interlineado de 1,15–1,25 y tracking de 0 a +1 %. Hay que comprobar que se ven bien ¿ ¡ ñ á é í ó ú ü « ».
- **Colores:** nada de rojo ni azul saturado (el 4:2:0 deshace sus bordes) ni trazos de 1–2 px. Si se pone contorno, que sea de 2–3 px en el color del fondo.
- **Transición entre frases:** desplazamiento de una línea más fundido, de 200 a 280 ms (10–14 fotogramas a 50 fps, o 6–8 a 30), con ease-out. Si la frase dura menos de 600 ms, corte seco. Sin zoom, rebote ni desenfoque, y sin destellos (WCAG 2.3.1). Esta pauta es una inferencia, no tiene fuente.
- **Troceado** (estilo Netflix y BBC): fundir las frases de menos de 833 ms, partir las de más de 7 s y vigilar que no pasen de unos 17 caracteres por segundo. No se separa artículo de sustantivo, preposición de su término, auxiliar de participio ni negación de verbo. «¿» y «¡» nunca quedan al final de una línea.
- **Resaltado palabra a palabra:** es opcional y solo para el vertical, cambiando solo el color, sin escala ni peso. Exige alineado forzado (WhisperX sobre el TTS). Los datos de retención que lo avalan son solo de vendedores.

### 3.2 Plantilla vertical 1080x1920 (x, y, ancho, alto en px; origen arriba a la izquierda)

| Caja | x | y | an. | al. | Estilo |
|---|---|---|---|---|---|
| Logo (opcional) | 120 | 300 | 64 | 64 | — |
| Título del episodio | 200 | 300 | 688 | 56 | 40 px, peso 600, blanco al 70 %, 1 línea, ≤32 caracteres con «…» |
| Hablante | 120 | 372 | 768 | 60 | 48 px, peso 700, color de acento (se puede quitar si hay un solo hablante) |
| Barra de progreso (opcional, clips ≥60 s) | 120 | 452 | 768 | 4 | — |
| Frase anterior (OFF por defecto) | 120 | 520 | 768 | 60 | 44 px, al 40–45 %, 1 línea |
| **Frase actual** | 120 | 620 | 768 | 400 | **72–76 px**, peso 700, blanco, interlineado 1,22, ≤3 líneas (4 como límite duro), 20–24 caracteres por línea, centrada en (504, 820) |
| Frase siguiente | 120 | 1060 | 768 | 160 | 46–48 px, peso 500, al 55 %, ≤2 líneas |
| Aviso «Traducción no oficial · voz IA · nav.al/<slug>» | 120 | 1190 | 768 | 50 | 32–36 px, al 60 %. Fijo o en los primeros 3 s y los últimos 3 s |
| **Prohibido** | 0 | 1248 | 1080 | 672 | sin texto |

Mínimos: 44 px para el texto secundario y 64 px para la frase activa.

**Fotograma de portada:** se pone en los primeros 0,5–1 s, o como imagen aparte. Lleva el título grande a 80–96 px dentro de x 120–888 / y 420–1248.

### 3.3 Plantilla horizontal 1920x1080

| Caja | x | y | an. | al. | Estilo |
|---|---|---|---|---|---|
| Logo | 96 | 54 | 88 | 88 | — |
| Título | 200 | 66 | 1300 | 64 | 42 px, peso 600, al 70 % |
| Hablante | 192 | 300 | 1536 | 60 | 46 px, peso 700, acento |
| Frase anterior | 192 | 380 | 1536 | 70 | 50 px, al 45 %, 1 línea |
| **Frase actual** | 192 | 470 | 1536 | 230 | **84 px**, peso 700, ≤2 líneas (3 como límite duro), 36–42 caracteres por línea, centrada en (960, 585) |
| Frase siguiente | 192 | 720 | 1536 | 130 | 50 px, al 55 %, ≤2 líneas, nunca por debajo de y 860 |
| **Libre** | 0 | 900 | 1920 | 180 | controles y subtítulos de YouTube |

Mínimos: 48 px para el secundario y 72 px para la activa; la referencia BBC del 8 % da unos 86 px. Hay que tener en cuenta que en TikTok o X un 16:9 se ve reducido a 0,5625, así que no se debe usar el horizontal para clips.

---

## 4. Qué evitar (aplicado a este proyecto)

### 4.1 Políticas y derechos
- **Voz clonada (verificado en el repo).** Las referencias de `fabrica/voces.json` son clips de Naval, Nivi, Brett Hall, David Deutsch y otros invitados, cortados de los episodios originales. Por eso:
  - el etiquetado de IA es obligatorio en YouTube (el ejemplo oficial es «voice cloning someone else's voice»), en TikTok (habla realista que imita a una persona real) y en Meta («realistic-sounding audio»);
  - la **política de suplantación de Spotify** retira programas que imitan la voz de un creador sin permiso, aunque se presenten como versión IA. Afecta también al audio que ya llega por RSS, no solo al vídeo;
  - YouTube tiene una vía de privacidad: la persona afectada puede pedir la retirada y hay 48 h para responder;
  - el art. 50(4) de la Ley de IA de la UE, en vigor desde el 2-ago-2026, obliga a revelar los deepfakes de audio.
- **Traducción sin permiso = obra derivada no autorizada** (TRLPI arts. 17 y 21; 17 USC §106(2)). No monetizar no lo cambia, y en la UE no existe *fair use*. El riesgo real es una retirada manual o un aviso DMCA, más que Content ID, que con otro idioma y otra voz probablemente no salte. En YouTube, 3 avisos en 90 días cierran el canal. La frase de Naval de 2021 («translate into whatever languages») **no es una licencia**. Los coautores (Nivi y los invitados) también tienen derechos.
- **Reutilizado o no original:**
  - En **YouTube** solo afecta al YPP, así que aquí casi no aplica.
  - En **TikTok** puede dejar el vídeo fuera de For You («slide videos», «sin cambios creativos»), y si se repite, la cuenta entera.
  - En **Instagram** (abr-2026) y **Facebook** (jul-2025, «without permission or meaningful enhancements») reduce la distribución.
  - Atenúan el riesgo la animación real del tambor, la marca propia, la traducción y el doblaje a la vista, y no publicar muchos clips casi iguales del mismo episodio.
- **No hacer:**
  - llamar a la cuenta «Naval Ravikant» ni usar su foto;
  - poner logos de nav.al o marcas de agua de otras apps (Instagram penaliza los Reels con logo de TikTok);
  - resubir lo descargado de TikTok;
  - publicar en Meta con una herramienta que no ponga «AI info»;
  - contranotificar un DMCA sin asesoría;
  - activar el **doblaje automático de YouTube**, que generaría pistas en otros idiomas a partir de una voz clonada;
  - activar la **ingesta RSS de YouTube**, que duplicaría cada episodio como vídeo estático.
- **Descripción obligatoria:** «Traducción NO oficial al español de «<título>», de Naval Ravikant (<fecha>). Original: https://nav.al/<slug>. Voz sintética generada con IA; no es la voz real de los participantes. Proyecto sin ánimo de lucro, sin afiliación con Naval Ravikant.»
- **Cuando llegue el permiso:** que sea escrito y cubra traducción, doblaje con **voz clonada**, vídeo largo y corto, plataformas, territorio y revocación. Se guarda en Drive (`naval-podcast/permisos/`) con su file ID en el repo, y se pide que añadan el canal a la lista de autorización de Content ID.

### 4.2 Técnico
- Texto por debajo de y 1248 en el vertical, a la derecha de x 820 entre y 840 y 1248, o el título abajo.
- En 16:9, la frase siguiente por debajo de y 860.
- Usar como clip un 16:9 o un vertical de más de 3 min (en YouTube no cuenta como Short).
- Clips de más de 90 s en Spotify Clips o de más de 140 s en X con cuenta gratuita.
- Subir el vertical como episodio de Spotify.
- 4K, 1440p, HDR, 10 bits, GOP abierto o el moov al final.
- Codificar un episodio de 4 h a 12–25 Mbps (21–45 GB), porque se pasa de los 10 GB de Spotify y Facebook.
- Subir episodios de ≥240 min a Facebook sin partirlos.
- `.srt` con dobles espacios alrededor de `-->` o sin número de secuencia (LinkedIn los rechaza).
- Miniaturas de más de 2 MB.
- Dejar activos los subtítulos automáticos de Instagram o TikTok.

---

## 5. Variantes que hay que generar

| Variante | Uso | Parámetros |
|---|---|---|
| **A. Largo 16:9** (obligatoria) | YouTube, Spotify vídeo, Facebook (<240 min) y X Premium | 1920x1080, **50 fps**, `libx264 -profile:v high -pix_fmt yuv420p -g 25 -bf 2 -flags +cgop -crf 19 -maxrate 8M -bufsize 16M -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart`, `-c:a aac -b:a 384k -ar 48000 -ac 2`, audio a −14 LUFS y −1 dBTP. **Comprobar el tamaño: si pasa de 9,5 GB**, repetir la codificación en 2 pasadas con `-b:v = 9,5 GB × 8 / duración − 0,4 Mbps`. El GOP de 25 cumple a la vez lo que pide YouTube (la mitad del framerate) y lo que pide Spotify (≥1 keyframe por segundo). Cerrar con 20 s de pantalla final («Escucha el episodio completo…») |
| **B. Clip vertical 9:16** (obligatoria) | Shorts, Reels, FB Reels, TikTok, Threads, Bluesky, LinkedIn y X | 1080x1920, **30 fps**, renderizado nativo a 30 fps (no convertido desde 50), H.264 High, `-crf 18 -maxrate 12M -bufsize 24M`, GOP de 15 cerrado, BT.709, faststart, AAC 48 kHz a 192 kbps estéreo, −14 LUFS y −1 dBTP. Duración por defecto **45–90 s**, máximo 180 s. **Con ≤90 s, el mismo fichero vale también para Spotify Clips** (≤1 GB) y con ≤140 s para X gratis (≤512 MB). Los cortes de frase deben coincidir con los límites de los bloques o frases del JSON. Plantilla de §3.2 |
| C. Fotograma de portada | Shorts, Reels y TikTok; miniatura de YouTube | Imagen fija de 1080x1920 (texto en y 420–1248) y otra de 1280x720 JPG de ≤2 MB. Para Spotify, 1920x1080. También se puede incrustar en los primeros 0,5 s del clip |
| D. `.srt` en español | YouTube, Facebook, LinkedIn y X | UTF-8, SRT básico, tiempos idénticos a los del tambor, número de secuencia y ` --> ` con un espacio a cada lado. Uno para el largo y otro para cada clip |
| E. Capítulos | descripción de YouTube | Se generan desde `titulos_seccion` y los tiempos de los bloques: `0:00` primero, ≥3 marcas, cada capítulo ≥10 s, formato `H:MM:SS` en episodios de más de 1 h |
| 4:5 / 1:1 | — | **No compensa por ahora.** La zona segura de B ya sobrevive a los recortes 4:5 y 3:4. Se reconsideraría solo si se hacen vídeos de feed en LinkedIn o X con mucho volumen |
| Carrusel de citas (TikTok, Instagram) | opcional, más adelante | 1080x1920, una frase por tarjeta, misma zona segura. Riesgo mayor de que se considere «slide» o contenido de baja calidad |

**Pruebas antes de fijar la plantilla:**
1. Subir el mismo clip a 30 y a 50 fps en TikTok, Reels y Shorts, descargarlo y comparar con `ffprobe -show_streams` (`r_frame_rate`, `bit_rate`).
2. Hacer capturas reales en Android e iOS de un clip con el rectángulo de la zona segura dibujado.
3. Comprobar en S4C si aparece «Upload video» y «Clips» para el programa que llega por RSS.

---

## 6. Contradicciones y cosas sin confirmar

| Tema | Versiones | Decisión tomada |
|---|---|---|
| fps del vertical | Inf. 1 y 4: 50 vale. Inf. 2 y 3: 30, porque lo alto se recomprime y no hay prueba con 50 | 30 nativo, y probar 50 |
| Bitrate del largo | Inf. 1: 12 Mbps (lo que recomienda YouTube). Inf. 4: 2–4 Mbps para caber en 10 GB | CRF con techo de 8M y control de tamaño |
| Tambor en vertical | Inf. 1, 2 y 3 mantienen 3 frases. Inf. 5 quita la anterior | 2 frases: con 72 px o más no caben 3 en 960 px de alto |
| Posición del hablante en vertical | Inf. 2: abajo (y 1100–1220). Inf. 5: cabecera | Cabecera; abajo choca con la UI de TikTok y Shorts |
| Borde izquierdo y derecho del vertical | izquierda: 48 / 60 / 65 / 120; derecha: 65 / 120 / 140 / 192 | La peor cifra: 120 / 192 |
| Borde inferior | 280–672 según la app y si es orgánico o anuncio | 672 (anuncios de Shorts y Meta) |
| Columna de botones de TikTok | 180 o 300 px de ancho | x ≤ 820 desde y 840 |
| Recorte de la cuadrícula de TikTok | 240 o 420 px por lado | Portada con el texto en y ≥ 420 |
| Spotify «replace audio with video» con RSS externo | La página del 26-mar-2026 dice que solo para programas alojados en Spotify; la versión de EE. UU. actual dice que también para RSS externo | Comprobar en la cuenta |
| Spotify Clips con RSS externo | no encontrado | Comprobar |
| Content ID en Shorts de 1–3 min | Desde el 24-sep-2026 ya no se bloquean (terceros); la página de EE. UU. no lo reflejaba | Poco relevante: el audio es propio |
| Miniatura de YouTube | 2 MB o 50 MB | ≤2 MB |
| Miniatura propia en Shorts sin YPP | dudoso | Fotograma de portada |
| Resolución máxima de Shorts | 1080p o 4K | 1080x1920 |
| Tamaño máximo en TikTok web | 10 GB (oficial, 2023) / 30 / 4 / 1 GB / 500 MB | Irrelevante para clips |
| Duración de un Reel desde Business Suite | 90 s / 15 min / 20 min | Comprobar en la interfaz |
| ¿El feed de Instagram recorta los Reels a 4:5? | sí / no | Se diseña como si los recortara |
| X Premium | 8 o 16 GB; 4 h o 2 h | Prioridad media; comprobar si se usa |
| Bluesky | 100 o 300 MB | Los clips pesan menos de 100 MB a 90 s / 8 Mbps |
| Sonoridad | −14 LUFS no es oficial en ninguna plataforma | −14 LUFS y −1 dBTP para todas |
| Cuota de `videos.insert` | 1.600 unidades o unas 100 desde dic-2025 | No afecta mientras la subida sea manual |
| Selector «AI info» en Business Suite o la API de Meta | no confirmado | Si no aparece, publicar desde la app |
| Zonas de la UI de Spotify, controles de YouTube, X y LinkedIn | no hay ninguna oficial | Medirlas con capturas |
| Velocidad de lectura de Netflix en español | 17 caracteres/s es la cifra de otros idiomas | Usarla como orientación |

---

## 7. Fuentes principales

Fecha de consulta de todas: 18-nov-2026, vía extractos del buscador. Las fechas de publicación se indican cuando constan.

**YouTube [OFICIAL]**
- Encoding: https://support.google.com/youtube/answer/1722171
- Duración y verificación: https://support.google.com/youtube/answer/71673
- Shorts de 3 min: https://support.google.com/youtube/answer/15424877
- Pantallas finales: https://support.google.com/youtube/answer/6388789
- Subtítulos: https://support.google.com/youtube/answer/2734698
- Miniaturas: https://support.google.com/youtube/answer/72431
- Podcasts: https://support.google.com/youtube/answer/12751636
- Contenido sintético: https://support.google.com/youtube/answer/14328491
- Copyright: https://support.google.com/youtube/answer/2797466
- Lista de autorización de Content ID: https://support.google.com/youtube/answer/6070344
- `videos.insert`: https://developers.google.com/youtube/v3/docs/videos/insert
- Miniaturas de Shorts (jul-2026): https://blog.youtube/news-and-events/youtube-studio-custom-thumbnail-updates/
- Etiquetas de IA (27-may-2026): https://9to5google.com/2026/05/27/youtube-updating-ai-content-labels/ [TERCEROS]

**Meta**
- IG User Media (API): https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/
- Reels Publishing API: https://developers.facebook.com/documentation/video-api/guides/reels-publishing
- Reels de 20 min: https://about.instagram.com/features/reels
- Recomendación de Reels de ≤3 min: https://help.instagram.com/225190788256708
- Zona segura de anuncios (14/35/6 %): https://www.facebook.com/business/ads-guide/update/image/instagram-reels y https://www.facebook.com/business/help/980593475366490/
- Subida a Página (10 GB, <240 min): https://www.facebook.com/business/help/163131210928551
- .srt en Facebook: https://www.facebook.com/business/help/1675722002698686
- Todo vídeo es Reel (17-jun-2025): https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/
- Contenido no original (14-jul-2025): https://creators.facebook.com/blog/combating-unoriginal-content
- Etiquetado de IA: https://www.meta.com/en-gb/help/artificial-intelligence/1783222608822690/
- Reposts en Instagram (30-abr-2026): https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/ [TERCEROS]

**TikTok [OFICIAL]**
- Media Transfer Guide: https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide
- Direct Post: https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
- Vídeos de más de 1 min (2023): https://tiktok.com/creators/creator-portal/en-us/tiktok-content-strategy/creating-videos-longer-than-one-minute
- In-Feed Ads: https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads
- Contenido de IA: https://www.tiktok.com/safety/en/policies-and-engagement/supporting-responsible-transparent-ai-generated-content
- Elegibilidad del For You feed: https://www.tiktok.com/safety/en/policies-and-engagement/fyf-standards
- Copyright: https://www.tiktok.com/legal/page/global/copyright-policy/en
- Control de contenido de IA (18-nov-2025): https://techcrunch.com/2025/11/18/tiktok-now-lets-you-choose-how-much-ai-generated-content-you-want-to-see/ [TERCEROS]

**Spotify [OFICIAL]**
- Video specs: https://support.spotify.com/us/creators/article/video-specs/
- Vídeo para programas no alojados en Spotify: https://support.spotify.com/us/creators/article/video-episodes-for-shows-not-hosted-with-spotify/
- Reemplazar un episodio por vídeo (versión del 26-mar-2026): https://support.spotify.com/us/creators/article/replacing-an-existing-episode-with-video/
- Clips content policy: https://support.spotify.com/us/creators/article/clips-content-policy/
- Política de suplantación: https://support.spotify.com/us/creators/article/impersonation-policy/
- Clonación de voz (may-2026): https://ppc.land/spotifys-new-verified-badge-and-ai-voice-cloning-ban-shake-up-podcast-trust/ [TERCEROS]

**Otras**
- Apple HLS for Podcasts (© 2026): https://developer.apple.com/documentation/http-live-streaming/hls-for-podcasts [OFICIAL]
- LinkedIn, vídeo: https://www.linkedin.com/help/linkedin/answer/a548372 [OFICIAL]
- LinkedIn, subtítulos: https://www.linkedin.com/help/linkedin/answer/a552177 [OFICIAL]
- X, .srt: https://help.x.com/en/using-x/upload-caption-srt-file [OFICIAL]
- X, límites de la API (oct-2026): https://opentweet.io/answers/x-api-video-upload-limit [TERCEROS]
- Bluesky a 10 min (27-ago-2026): https://www.techtimes.com/articles/325740/20260827/bluesky-matches-tiktok-video-length-still-pays-creators-nothing.htm [TERCEROS]

**Zonas seguras [TERCEROS, 2025-2026]**
- https://www.socialync.io/tools/safe-zones/youtube-shorts
- https://www.manypixels.co/blog/social-media-design/tiktok-ad-specs (11-nov-2026)
- https://cadenus.io/resources/blog/tiktok-safe-zone/
- https://adkit.so/tools/safe-zones/meta (10-sep-2026)
- https://www.trymypost.com/blog/instagram-reels-safe-zones-2026
- https://www.kapwing.com/resources/instagrams-new-grid-layout-size-and-dimensions-2025/

**Texto en pantalla**
- Netflix, guía de estilo en español: https://backlothelp.netflix.com/hc/en-us/articles/217349997 [OFICIAL]
- BBC CSUN: https://bbc.github.io/csun/how_big_should_subtitles_be/index.html [OFICIAL]
- EBU R95: https://tech.ebu.ch/docs/r/r095.pdf [OFICIAL, 2009]
- WCAG 2.2: https://www.w3.org/TR/WCAG22/ [OFICIAL]
- Atkinson Hyperlegible Next: https://fontsource.org/fonts/atkinson-hyperlegible-next/about

**Derecho**
- Ley de IA de la UE, art. 50: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50 [OFICIAL]
- TRLPI, art. 21: https://vlex.es/vid/derecho-transformacion-articulo-21-679166297
- Radji v. Khakbaz: https://www.copyright.gov/fair-use/summaries/radj-khakbaz-ddc1985.pdf

**Repo** (comprobación propia)
- /home/user/spanishnav.al-podcast/fabrica/voces.json: referencias de voz extraídas de los hablantes reales.
- /home/user/spanishnav.al-podcast/docs/fabrica-de-voz.md: «El clon tiene que ser lo más perfecto posible».
- Ojo: /home/user/spanishnav.al-podcast/fabrica/cortos.ipynb son episodios cortos del podcast montados desde un largo, no clips para redes. No hay que confundirlo con la variante B.
