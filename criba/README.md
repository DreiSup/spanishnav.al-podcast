# Criba de motores TTS

Fase 1a de `docs/fabrica-de-voz.md`: elegir el motor de voz que se usará para todos los
hablantes. Aquí va todo lo que es texto: las frases de prueba y, más adelante, los
cuadernos de Colab. El audio va a Drive, en `fine_tunned_naval/outputs/criba/<motor>/<voz>/`.

## `frases.json`

Hay 55 items por motor. Cada item es un audio:

| Prefijo | Voz | Referencia (`speaker_refs/`) | Items | Para qué |
|---|---|---|---|---|
| `n` | Naval | `naval` | 25 | La voz principal: cortas, medias, largas, preguntas, nombres en inglés, cifras en letra y un bloque de 9 frases seguidas |
| `v` | Nivi | `nivi` | 10 | Leer tuits y preguntar |
| `b` | Brett | `brett` | 10 | Un invitado con otro acento. Reutiliza 10 textos de Naval (`mismo_texto_que`) |
| `k` | Naval | `naval_kapil` | 10 | Prueba de tono: los mismos textos que 10 items `n`, con una referencia del episodio de Kapil Gupta |

Sobre las frases:

- **Todas salen literalmente de los `transcript.es.json` del repo.** `origen` dice de dónde
  (`episodio#bloque/frase`).
- **Cada frase se sintetiza por separado y se unen con 250 ms de silencio**, igual que en
  producción. El item `n25` (bloque de 9 frases de `035-finally-wealthy`) mide si la voz se
  mantiene estable de una frase a la siguiente: sin saltos de volumen ni deriva de timbre.
- **Ninguna frase lleva caracteres que el TTS vocalice ni cifras**, y ninguna pasa de 239
  caracteres; la más larga tiene 217.
- **Hay 9 frases cortas**, de menos de 60 caracteres. Es donde XTTS alucinaba: la criba
  tiene que ver si los motores nuevos lo resuelven sin reagrupar frases.
- **Los items `b` y `k` repiten textos de los `n`.** Así se puede comparar el mismo texto
  entre voces y entre referencias.

## Cuadernos

Están en `cuadernos/` y son **generados**: se editan en `construir_cuadernos.py` y se
regeneran con `python3 criba/construir_cuadernos.py`. El código común (Drive, frases,
referencias, generación sin repetir lo ya hecho, desconexión) está en `comun.py`, y cada
cuaderno lo trae clonando el repo.

| Cuaderno | Variantes (carpeta en `outputs/criba/`) | GPU |
|---|---|---|
| `01_chatterbox.ipynb` | `chatterbox_v2`, `chatterbox_v3`, `chatterbox_v3_es` | T4 |
| `02_omnivoice.ipynb` | `omnivoice` | T4 |
| `02b_omnivoice_acento.ipynb` | `omnivoice_ref01`, `omnivoice_g3`, `omnivoice_ref01_g3` (10 frases de Naval) | L4 o T4 |
| `03_qwen3tts.ipynb` | `qwen3tts_1.7b` | L4 |
| `04_dots.ipynb` | `dots_soar` (en un Python 3.12 aparte: Colab trae 3.13 y dots-tts no lo admite) | L4 |
| `05_xtts.ipynb` | `xtts_base`, `xtts_navalchris` (solo Naval) | T4 |
| `06_metricas_y_escucha.ipynb` | `metricas/` y `escucha/` | T4 |

Se abren en Colab directamente desde GitHub:
`https://colab.research.google.com/github/DreiSup/spanishnav.al-podcast/blob/claude/quirky-dirac-x18c3n/criba/cuadernos/<cuaderno>`

Todos siguen el mismo patrón:

1. celda 1, instalación, y reiniciar la sesión;
2. celda 2, que comprueba las referencias y las frases antes de cargar nada;
3. carga del modelo y generación;
4. la última celda desconecta la GPU sola.

Usan la referencia `<voz>_ref02` (~12 s) y una semilla fija por item.
