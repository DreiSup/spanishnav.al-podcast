# Segundo encargo a Claude Design: versiones verticales, clips y piezas sueltas

> Escrito el 18-nov por la sesión técnica a partir de `docs/investigacion-formatos-redes.md`. Se pega en la **misma
> sesión de Claude Design** que recibió `docs/prompt-claude-design-video.md` (los 10 diseños en 16:9), cuando haya
> entregado esos diseños o a continuación. Las cifras de zonas seguras son la peor de cada app (Shorts, Reels, TikTok);
> salen de plantillas de terceros y extractos oficiales, y se verificarán con capturas reales antes de fijarlas.

---

Además de los 10 diseños en 16:9 para el episodio completo, quiero que cada diseño tenga **todas las piezas que hacen
falta para publicar en redes**: YouTube Shorts, Instagram Reels y Stories, TikTok, Facebook, Spotify (vídeo y Clips),
X, Threads, Bluesky y LinkedIn. Mantén en todas las piezas la identidad de cada diseño (tipografía, paleta,
composición y forma de animar), adaptada a cada formato. Las normas técnicas del primer encargo siguen valiendo: todo
calculado a partir de `tiempo_s`, sin animaciones que avancen solas, solo Google Fonts, sin imágenes externas y
efectos baratos de renderizar.

## Piezas que necesito de cada diseño

| # | Pieza | Lienzo | fps del render | Para qué |
|---|---|---|---|---|
| A | **Episodio completo** (el que ya tienes), revisado con las zonas seguras de abajo | 1920×1080 | 50 | YouTube, Spotify vídeo, Facebook |
| B | **Clip vertical** de 45–90 s (máximo 180 s) | 1080×1920 | 30 | Shorts, Reels, TikTok, Facebook Reels, Spotify Clips, X, Threads, Bluesky, LinkedIn |
| C | **Portada vertical** (fotograma fijo) | 1080×1920 | — | portada del clip en Shorts, Reels y TikTok |
| D | **Miniatura horizontal** | 1280×720 | — | miniatura del episodio en YouTube |
| E | **Pantalla final** del episodio (últimos 20 s) | 1920×1080 | 50 | invitar al siguiente episodio; deja hueco a los elementos de YouTube |

Un **único** vertical 9:16 sirve para todas las apps: no hagas 4:5 ni 1:1. La zona segura de B ya sobrevive a los
recortes del feed de Instagram (4:5) y de la cuadrícula de perfil (3:4).

## Zonas seguras y maqueta

Coordenadas en px con origen arriba a la izquierda. **Ningún texto fuera de su zona.** Añade al prototipo un
interruptor que dibuje encima las zonas seguras y la silueta aproximada de la interfaz de cada app (Shorts, Reels,
TikTok), para comprobar cada diseño.

### Vertical 1080×1920 (pieza B y C)

- **Zona segura común**: x 120–888, y 288–1248 (768×960). Su centro óptico está en **y ≈ 820**, no en 960.
- Entre **y 840 y 1248**, el texto no pasa de **x 820** (columna de botones de TikTok y Reels a la derecha).
- **Por debajo de y 1248 no va nada** (usuario, descripción, sonido, barra de progreso y navegación de las apps).
  Por encima de y 288 tampoco (búsqueda, pestañas, cámara).
- El fondo sí ocupa los 1080×1920 enteros: las zonas tapadas solo deben ser fondo.

Maqueta de referencia (punto de partida; cada diseño puede reinterpretarla dentro de la zona segura):

| Elemento | Zona | Tipografía de referencia |
|---|---|---|
| Título del episodio | arriba de la zona (y 300–360) | ~40 px, 1 línea, ≤32 caracteres con «…» |
| Hablante actual | debajo del título (y 372–432) | ~48 px, color de acento; cambia con su transición |
| Barra de progreso del clip (opcional) | y ≈ 452 | 4 px de alto |
| **Frase actual** | centrada en (504, 820), caja x 120–888 | **72–76 px**, peso 600–700, ≤3 líneas (4 como límite), 20–24 caracteres por línea |
| Frase siguiente | debajo, hasta y ≈ 1220 | 46–48 px, atenuada al ~55 %, ≤2 líneas |
| Frase anterior | **opcional**: si cabe sin apretar, arriba en 1 línea a ~44 px y al 40–45 %; si no, quítala | — |
| Aviso | y ≈ 1190–1240, o solo los 3 primeros y 3 últimos segundos | 32–36 px, al ~60 %: «Traducción no oficial · voz sintética (IA) · nav.al/philosopher» |

El tambor sigue siendo un tambor en vertical: con letra grande y 960 px de alto suele caber la actual y la siguiente
(y la anterior solo si el diseño lo resuelve con elegancia). Prueba los dos casos y dime cuál eliges en cada diseño.

**Arranque del clip**: el clip empieza a mitad de episodio, así que los **primeros 0,5–1 s** muestran la portada (título
grande) y enseguida el tambor arranca con la primera frase ya en el centro. **Final del clip** (últimos 2–3 s): cierre
con «Episodio completo en YouTube y Spotify» y el nombre del podcast, dentro de la zona segura.

### Portada vertical 1080×1920 (pieza C)

Título del episodio grande (80–96 px) con el texto **dentro de x 120–888 / y 420–1248** (TikTok recorta más la
cuadrícula), nombre del podcast y número de episodio. Debe funcionar como primer fotograma del clip.

### Horizontal 1920×1080 (piezas A y E), revisión de lo que ya tienes

- Margen de seguridad: 96 px a los lados y 54 px arriba y abajo.
- **Nada de texto por debajo de y 900**: ahí van los controles y los subtítulos de YouTube. Las esquinas inferior y
  superior derecha, libres (marca de agua del canal, tarjetas).
- Frase actual de referencia: ~84 px, ≤2 líneas (3 como límite), 36–42 caracteres por línea, centrada en (960, 585),
  caja x 192–1728. Frase siguiente sin pasar de y 860.
- **Pantalla final (E)**, últimos 20 s: el tambor se encoge a la mitad izquierda o superior y deja libre la zona
  x 960–1824 / y 200–900 para los elementos de YouTube (vídeo 613×343, suscripción 294×294); texto «Escucha el
  siguiente episodio».

### Miniatura 1280×720 (pieza D)

Título del episodio legible en pequeño (se ve a ~250 px de ancho en móvil), número de episodio y nombre del podcast;
nada importante en la esquina inferior derecha (ahí YouTube pone la duración). Sin fotos de Naval ni logos de nav.al.

## Reglas de texto (todas las piezas)

- Contraste: la frase actual muy contrastada; las atenuadas, **no por debajo del 45 %** de opacidad sobre fondo
  oscuro (en diseños claros, el equivalente con contraste ≥ 4,5:1). Mejor atenuar con un color plano que con alfa.
- Tamaño mínimo: 44 px en vertical y 48 px en horizontal para el texto secundario.
- Interlineado 1,15–1,25. Nada de pesos ≤ 300 ni trazos de 1–2 px (la compresión de las apps los deshace); nada de
  rojo o azul muy saturados en el texto. Si hay contorno, 2–3 px del color del fondo.
- Fondos planos o casi planos; si hay degradado, con un 1–2 % de grano para que no salgan bandas al recomprimir.
- Sin destellos ni parpadeos. El giro del tambor sigue siendo **muy suave**; en el vertical, a 30 fps, cuida que siga
  viéndose fluido (giros de unos 0,4–0,6 s mejor que muy rápidos).
- Comprueba ¿ ¡ ñ á é í ó ú ü « » en cada fuente. «¿» y «¡» nunca a final de línea.
- Prohibido: usar el nombre o la foto de Naval como marca del canal, logos de nav.al, logos de otras apps.

## Datos de ejemplo del clip

Usa el episodio 053 del primer encargo. El clip es el tramo **`inicio_s` 22.1 → 63.9** (de «Pero si vives lo
suficiente…» a «En eso nos centramos…»): sus tiempos dentro del clip son `tiempo_s - 22.1`, y dura 41,8 s. Para el
caso del invitado, el tramo 0–60 s del 070. Estructura que recibirá el componente vertical:

```json
{
  "episodio": { "numero": 53, "titulo": "Vive lo suficiente y te convertirás en filósofo", "slug": "philosopher" },
  "clip": { "inicio_s": 22.1, "fin_s": 63.9 },
  "frases": "las del episodio; se muestran las que caen dentro del clip"
}
```

## Qué entregarme

1. El prototipo ampliado: selector de diseño (1–10) y de pieza (A–E), reproductor y deslizador de tiempo, y el
   interruptor de zonas seguras con las siluetas de Shorts, Reels y TikTok.
2. Para cada diseño, la ficha del vertical: tamaños, posiciones (x, y, ancho, alto), si muestra 2 o 3 frases y la
   tabla de animaciones a 30 fps.
3. Una vista de galería con las 5 piezas de cada diseño una al lado de otra.
4. Si algún diseño no funciona en vertical sin perder su esencia, dilo y propón cómo adaptarlo.
