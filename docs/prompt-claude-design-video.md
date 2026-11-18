# Encargo a Claude Design: 10 diseños para el vídeo «lectura» del podcast

> Escrito el 18-nov por la sesión técnica a petición del autor. Se pega tal cual en Claude Design. Contexto y forma de
> integrarlo en `docs/video-dinamico.md`. Los datos de ejemplo son reales (tiempos del 053 sacados de su
> `indice_master.tsv`); los del 070 tienen tiempos inventados, para probar un invitado y frases extremas.

---

Quiero que diseñes la interfaz de los vídeos de mi podcast, con el mejor gusto posible, y que me propongas **10 diseños
totalmente distintos entre sí** para elegir.

## Qué es

**Naval Podcast en español**: el podcast de Naval Ravikant (filosofía práctica sobre riqueza, felicidad, salud y
pensamiento) traducido al español y doblado con voz sintética. Cada episodio será un vídeo de YouTube y Spotify en el
que **el transcript aparece en pantalla, sincronizado con la voz**. Duran de 1 minuto a 4 horas; la gente los escucha
mientras lee, así que el texto es el protagonista y tiene que leerse sin esfuerzo durante horas. No es un vídeo de
anuncio: es una lectura tranquila, elegante y seria, a la altura del contenido.

## La mecánica, igual en los 10 diseños: un tambor que gira

Piensa en los números de un **candado de combinación** o en una **ruleta vertical**:

- la **frase que se está diciendo** está en el **centro**, grande, bien legible y **resaltada**;
- la **frase anterior** está **arriba**, más pequeña y **sombreada/atenuada**;
- la **frase siguiente** está **abajo**, más pequeña y **sombreada/atenuada**;
- cuando empieza una frase nueva, **toda la columna gira hacia arriba**: la del centro sube y se atenúa, la de abajo
  sube al centro y se resalta, por abajo asoma la siguiente y por arriba desaparece la que ya pasó.

La animación tiene que ser **muy, muy suave** (sin saltos, sin parpadeos, con arranque y frenada progresivos). Cada
diseño puede interpretar el tambor a su manera (curvatura, perspectiva, desenfoque, máscara de degradado, ritmo), pero
la idea anterior/actual/siguiente se mantiene.

## Lo que tiene que aparecer en pantalla

Obligatorio en todos:

1. **Título del episodio** (y su número).
2. **Quién está hablando ahora**, que cambia cuando cambia el hablante, con una transición propia. Hay anfitriones
   (Naval, Nivi) e invitados (p. ej. Matt Ridley); cada hablante debe distinguirse (color, posición, estilo…).
3. **El transcript** en tambor, como se describe arriba.
4. **Progreso** del episodio (barra, tiempo transcurrido/total, o lo que mejor encaje).
5. El nombre del podcast, **Naval Podcast en español**, discreto.

Opcional, si el diseño lo aprovecha bien: **título de la sección** actual (algunos episodios tienen secciones),
título original en inglés, rol del hablante (anfitrión / invitado), crédito discreto a la fuente («Original: nav.al»).

## 10 diseños de verdad distintos

- Cada uno con **otra tipografía** (sans, serif, mono, display, editorial, humanista, geométrica…), **otra paleta**
  (oscuros y claros, al menos 3 claros), **otra composición** (centrado, asimétrico, columnas, marco, etc.) y **otra
  forma de animar** el tambor y el cambio de hablante.
- Ponle a cada uno un **nombre** y una frase de concepto (p. ej. «Editorial», «Terminal», «Pergamino»…).
- Que no sean variaciones de color del mismo diseño.

## Requisitos técnicos (importantes: el diseño se convertirá en vídeo)

1. **Formato**: 16:9, lienzo fijo de **1920×1080** (escálalo para verlo, pero diseña a ese tamaño).
2. **Todo se calcula a partir de un tiempo**: cada diseño es un componente React que recibe `datos` (el JSON de abajo)
   y `tiempo_s` (segundos desde el inicio), y dibuja ese instante exacto. **Nada de animaciones CSS (`@keyframes`,
   `transition`), `setTimeout`, `requestAnimationFrame` ni nada que avance solo**: la misma entrada debe dar siempre
   la misma imagen, porque el vídeo se fabrica fotograma a fotograma (50 por segundo). Las curvas de aceleración,
   calcúlalas tú en el código a partir de `tiempo_s`.
3. **Controles para revisarlo**: un reproductor con play/pausa (que solo avance `tiempo_s`), un deslizador de tiempo,
   selector de episodio de ejemplo (053 y 070) y selector de diseño (1–10). Si puedes, una vista de galería con los 10
   en miniatura en el mismo instante.
4. **Sincronía**: la frase `i` es la actual desde su `inicio_s` hasta el `inicio_s` de la siguiente. El giro puede
   empezar un poco antes (unos 0,3 s) para que llegue al centro cuando empieza a sonar. Las frases duran **entre 1 y
   10 s** (hay seguidas de 1 s: «¿Cómo me hago rico?»), así que el giro debe durar **≤ 0,6 s** y acortarse si la
   frase anterior es muy corta. Las frases miden hasta **~250 caracteres**: tienen que caber (varias líneas, o el
   cuerpo de letra baja) sin pisar nada. También hay frases de una palabra («Sí.»).
5. **Fuentes**: solo **Google Fonts**. Sin imágenes externas (si quieres textura o fondo, hazlo con CSS/SVG).
6. **Coste de render**: cada fotograma se capturará en un navegador sin pantalla, durante horas de vídeo. Prefiere
   transformaciones (translate, scale), opacidad, color y desenfoques moderados; evita `backdrop-filter`, sombras
   enormes animadas, partículas o vídeo de fondo. Fondo estático o casi estático.
7. Texto en **español** con tildes, ñ, ¿ ¡ y comillas «».

## Qué entregarme

1. El prototipo con los **10 diseños** funcionando con los datos de ejemplo.
2. Para **cada diseño**, una ficha:
   - nombre y concepto;
   - tipografías (familia, peso y tamaño de cada elemento) y paleta (hex);
   - **tabla de animaciones**: qué se mueve, propiedad (posición, escala, opacidad, color, desenfoque…), duración,
     retardo y curva (p. ej. `cubic-bezier(0.65, 0, 0.35, 1)`);
   - si usa algo más allá de posición, escala, opacidad, color, desenfoque y recorte (máscaras, perspectiva 3D,
     degradados animados…), dilo: decide cómo se renderizará.
3. Tu recomendación de los 3 mejores y por qué.

## Datos de ejemplo

### Episodio 053 (tiempos reales)

```json
{
  "podcast": "Naval Podcast en español",
  "numero": 53,
  "titulo": "Vive lo suficiente y te convertirás en filósofo",
  "titulo_original": "Live Long Enough and You’ll Become a Philosopher",
  "fecha_original": "2020-01-27",
  "duracion_s": 92.0,
  "hablantes": {"Naval": {"nombre": "Naval Ravikant", "rol": "anfitrión"}, "Nivi": {"nombre": "Nivi", "rol": "anfitrión"}},
  "secciones": [
    {"inicio_s": 0.1, "titulo": "Los grandes problemas son los de siempre"},
    {"inicio_s": 46.7, "titulo": "Lo que puede hacer un mono, lo puede hacer otro"}
  ],
  "frases": [
    {"inicio_s": 0.1, "hablante": "Naval", "texto": "Hablemos de por qué hacemos este podcast."},
    {"inicio_s": 2.5, "hablante": "Naval", "texto": "En el fondo, es una conversación sobre filosofía muy práctica."},
    {"inicio_s": 6.2, "hablante": "Naval", "texto": "La filosofía, tal como solemos entenderla, no tiene nada de práctica."},
    {"inicio_s": 10.7, "hablante": "Naval", "texto": "Es abstracta y enrevesada, algo que se escribió hace mucho tiempo en un lenguaje rebuscado."},
    {"inicio_s": 16.5, "hablante": "Naval", "texto": "La ponemos en un pedestal y parece inalcanzable, y a veces suena a simples obviedades."},
    {"inicio_s": 22.1, "hablante": "Naval", "texto": "Pero si vives lo suficiente, tú mismo te convertirás en filósofo."},
    {"inicio_s": 26.4, "hablante": "Naval", "texto": "Te habrás pasado la vida entera resolviendo tus grandes problemas."},
    {"inicio_s": 30.8, "hablante": "Naval", "texto": "Los grandes problemas son los de siempre, los que llevamos intentando resolver desde el principio."},
    {"inicio_s": 36.0, "hablante": "Naval", "texto": "¿Cómo sigo siendo feliz?"},
    {"inicio_s": 37.2, "hablante": "Naval", "texto": "¿Cómo consigo estar sano?"},
    {"inicio_s": 38.6, "hablante": "Naval", "texto": "¿Cómo me hago rico?"},
    {"inicio_s": 39.6, "hablante": "Naval", "texto": "¿Cómo formo la familia que quiero?"},
    {"inicio_s": 42.1, "hablante": "Naval", "texto": "Este podcast trata de la filosofía práctica que nos ha funcionado a nosotros."},
    {"inicio_s": 46.7, "hablante": "Naval", "texto": "Lo que puede hacer un mono, lo puede hacer otro."},
    {"inicio_s": 49.3, "hablante": "Naval", "texto": "Queremos que la gente piense que, si esta persona aprendió algo que la hizo más feliz, más sana o más rica, ella también puede hacerlo."},
    {"inicio_s": 57.5, "hablante": "Naval", "texto": "En eso nos centramos, en una filosofía práctica de la salud, la riqueza y la felicidad."},
    {"inicio_s": 63.9, "hablante": "Nivi", "texto": "Si lo resumieras en una sola palabra, sería la salud."},
    {"inicio_s": 67.5, "hablante": "Nivi", "texto": "La salud financiera, la salud mental y la salud física."},
    {"inicio_s": 72.3, "hablante": "Naval", "texto": "La salud es un estado de bienestar."},
    {"inicio_s": 74.3, "hablante": "Naval", "texto": "Lleguemos a un estado de salud financiera en el que no vivamos con miedo día a día."},
    {"inicio_s": 78.7, "hablante": "Naval", "texto": "Por ahí empezamos, y le dedicamos mucho tiempo."},
    {"inicio_s": 81.4, "hablante": "Naval", "texto": "Lleguemos a un estado de salud física en el que no suframos dolencias, enfermedades ni adicciones."},
    {"inicio_s": 86.9, "hablante": "Naval", "texto": "Lleguemos a un estado de salud mental en el que estemos relativamente en paz y bastante contentos con nosotros mismos."}
  ]
}
```

### Episodio 070, con invitado (tiempos inventados para probar casos extremos)

```json
{
  "podcast": "Naval Podcast en español",
  "numero": 70,
  "titulo": "Matt Ridley: Cómo funciona la innovación, parte 1",
  "duracion_s": 60.0,
  "hablantes": {"Naval": {"nombre": "Naval Ravikant", "rol": "anfitrión"}, "Matt": {"nombre": "Matt Ridley", "rol": "invitado"}},
  "secciones": [],
  "frases": [
    {"inicio_s": 0.1, "hablante": "Naval", "texto": "No tengo héroes, pero sí hay personas a las que admiro y de las que he aprendido mucho."},
    {"inicio_s": 5.2, "hablante": "Naval", "texto": "Y Matt Ridley, que está al otro lado de la línea, tiene que estar casi en lo más alto de esa lista."},
    {"inicio_s": 11.0, "hablante": "Matt", "texto": "Naval, es un placer conocerte, y me parece muy interesante oír que has leído tantos libros míos y que has captado lo esencial de ellos, y eso es maravilloso."},
    {"inicio_s": 21.5, "hablante": "Matt", "texto": "Soy alguien que ha disfrutado escribiendo toda la vida."},
    {"inicio_s": 25.0, "hablante": "Naval", "texto": "Leí este libro para preparar esta conversación, así que la lectura acabó teniendo algo de obligación."},
    {"inicio_s": 31.0, "hablante": "Naval", "texto": "Me encanta esa frase, ahí tienes un tuit buenísimo."},
    {"inicio_s": 34.0, "hablante": "Matt", "texto": "Si eres emprendedor en Silicon Valley, Shanghái o Bangalore y piensas crear productos, ya sean redes sociales, el lanzamiento de cohetes, la fabricación de aviones o la ingeniería genética, tienes que leer este libro."},
    {"inicio_s": 47.0, "hablante": "Naval", "texto": "Sí."},
    {"inicio_s": 48.0, "hablante": "Matt", "texto": "Me alegra mucho que te parezca práctico y aplicable, porque era una de las cosas que quería conseguir con este libro."}
  ]
}
```
