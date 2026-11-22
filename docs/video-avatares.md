# Avatares animados por hablante (idea del autor, 22-nov)

Para el vídeo dinámico (`docs/video-dinamico.md`): **a la izquierda, el avatar de quien habla, animado** (cara, parte
del cuerpo y algún elemento de fondo moviéndose); **a la derecha, la transcripción en tiempo real** (lo que ya hace el
vídeo lectura). Cuando cambia el hablante, cambia la animación.

Las imágenes las hace el autor con una IA generativa de imágenes (ChatGPT); Claude no genera imágenes. La animación
es una secuencia de fotogramas que se repite en bucle mientras habla esa persona.

## Dónde van (Drive, nunca en git)

`naval-podcast/diseno-video/` — https://drive.google.com/drive/folders/1O09eZ570K33KfNLLwPl6akdYFTKsyNbS

| Carpeta | Para qué | ID |
|---|---|---|
| `_estilo/` | Referencias del estilo general: la imagen que ya se usa de portada, paletas, ilustraciones que gusten | `1mkNL3omStcT6n6XamFifodMyfXlJLhKx` |
| `naval/` | Fotos de referencia de Naval y sus fotogramas | `1jnGvgzST2HFepqdOP6JDCqO2LsyGwb1A` |
| `nivi/` | Ídem, Nivi | `16sXqQg9hMHRz9H-KCrWFbknr3xfX99tw` |
| `brett/` | Ídem, Brett Hall | `1swmQbkLBHE3UcgbmuUtPDnEn8WYEZ3Ud` |
| `deutsch/` | Ídem, David Deutsch | `15xry-YiDjbamdO2fZlOZkesHgflCDbkU` |

El nombre de la carpeta es el de la voz en `fabrica/voces.json`: así el montaje sabe qué animación poner por bloque
sin tablas aparte. Invitados con pocos episodios (kapil, vitalik, ridley, qureshi, hodak, rauch, scholl): se crean
sus carpetas cuando toque; mientras, pueden usar una animación genérica.

Dentro de cada hablante:

- `ref-01.png`, `ref-02.png`… — las imágenes de referencia que se le dan a ChatGPT.
- `ficha.png` — la imagen «buena» del personaje ya en el estilo elegido; de ella salen todos los fotogramas.
- `f01.png`, `f02.png`… — los fotogramas del bucle, en orden.

## Cómo tienen que ser los fotogramas

- **Tamaño**: todos iguales. Si el avatar ocupa el tercio izquierdo de un vídeo 1920×1080, **720×1080** (vertical).
  Se puede ajustar cuando esté el diseño de pantalla, pero que todos los de un hablante midan lo mismo.
- **PNG** (no JPG: los bordes del dibujo se ensucian). Fondo incluido en la imagen si el fondo también se mueve.
- **8–12 fotogramas** por bucle, que el último enlace con el primero (si no, se nota el salto al repetir).
- Cambios **pequeños** entre fotogramas: boca, parpadeo, un gesto de mano, algo del fondo. Con IA cuesta mantener
  el mismo personaje: mejor generar primero la `ficha.png` y pedir cada fotograma «igual que esta imagen, cambiando
  solo …».

**GIF solo para verlo**: el GIF tiene 256 colores y pesa mucho; para el vídeo final se usan los PNG directamente
(ffmpeg los repite en bucle a la velocidad que se elija, p. ej. 8 fotogramas por segundo). Si el autor quiere
previsualizar, el GIF se puede generar a partir de los PNG.

## Aviso pendiente

Ilustraciones reconocibles de Naval, Nivi y los invitados: mismo riesgo que la voz clonada (políticas de
suplantación de las plataformas, `docs/investigacion-formatos-redes.md` §4.1). Conviene que el permiso que se pida a
Naval cubra también su imagen y la de los participantes.
