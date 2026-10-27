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
