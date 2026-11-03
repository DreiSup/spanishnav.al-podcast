# Resultados del piloto de fine-tuning

## LoRA de Qwen3-TTS, variante B — escucha a ciegas (2026-10-30)

Página `piloto/lora_qwen/B/prueba/escucha/lora_qwen_B.html`: frases n12, n18 y n25 de la criba,
referencia `naval_ref02` en modo solo timbre, sin recorte de pausas. Notas de 1 a 5 del autor
(`puntuaciones_lora_qwen_B.csv`, letras en `clave_lora_qwen_B.json`).

| Versión | Parecido | Acento | Naturalidad | Alucinaciones | Media (sin aluc.) |
|---|---|---|---|---|---|
| base (sin LoRA) | 3,67 | 4,33 | 3,00 | 5 | 3,67 |
| paso_0040 | 3,33 | 4,00 | 2,00 | 5 | 3,11 |
| paso_0080 | 4,33 | 4,00 | 4,00 | 5 | 4,11 |
| paso_0120 | 4,00 | 4,00 | 4,00 | 5 | 4,00 |
| paso_0158 | 4,00 | 4,00 | 4,00 | 5 | 4,00 |

Por frase (parecido, acento, naturalidad):

| | base | 0040 | 0080 | 0120 | 0158 |
|---|---|---|---|---|---|
| n12 | 3 5 2 | 3 4 2 | 5 4 5 | 5 4 5 | 4 4 4 |
| n18 | 3 4 3 | 3 4 2 | 3 4 4 | 4 5 4 | 4 4 4 |
| n25 | 5 4 4 | 4 4 2 | 5 4 3 | 3 3 3 | 4 4 4 |

Lectura:

- **El LoRA mejora a la base** a partir del paso 80, sobre todo en naturalidad (3 → 4) y algo en
  parecido. El paso 40 empeora: es una fase de transición.
- **80, 120 y 158 están empatados** (4,11 / 4,00 / 4,00): con 3 frases por versión, 0,11 de
  diferencia es ruido.
- **Se elige `paso_0158`** como punto de partida de `naval_kapil` y como candidato de Naval: es el
  único sin ninguna nota por debajo de 4, tiene la menor pérdida de evaluación (2,66 en inglés y
  2,45 en español) y el ritmo más vivo en la frase larga (19 c/s en n18).
- **El acento no mejora** con el LoRA: se queda en 4. Lo que aporta es naturalidad.
- Ninguna versión alucina.

## LoRA de Qwen, variante kapil (naval_kapil) — escucha a ciegas (2026-10-31)

Frases k05, k07 y k10 (los textos de n12, n18 y n25) con la referencia `naval_kapil_ref02`, en modo solo
timbre. «naval» es el LoRA B `paso_0158` de partida; los `paso_00NN` son el repaso con la sesión con Kapil.
Notas del autor en `puntuaciones_lora_qwen_kapil.csv`, letras en `clave_lora_qwen_kapil.json`.

| Versión | Parecido | Acento | Naturalidad | Tono | Alucinaciones | Media (4 primeros) |
|---|---|---|---|---|---|---|
| base (sin LoRA) | 3,00 | 4,00 | 3,33 | 3,00 | 5 | 3,33 |
| naval (B/paso_0158) | 3,33 | **4,33** | 4,00 | 3,33 | 5 | 3,75 |
| paso_0015 | 4,33 | 4,00 | 4,00 | 3,00 | 5 | 3,83 |
| paso_0030 | 3,33 | 3,67 | 4,00 | 3,33 | 5 | 3,58 |
| paso_0045 | 3,00 | 3,67 | 3,67 | **4,00** | 5 | 3,58 |
| paso_0060 | 4,00 | 3,33 | **4,67** | 3,33 | 5 | 3,83 |
| paso_0073 | 4,00 | 3,33 | **4,67** | 3,67 | 5 | **3,92** |

Lectura:

- **Cualquier LoRA mejora a la base** (3,33).
- **El repaso con Kapil gana naturalidad** (4,0 → 4,67) **pero pierde acento** (4,33 → 3,33): entrenar con
  más inglés de esa sesión devuelve algo de acento inglés.
- **El tono apenas cambia** (3,0–4,0, sin tendencia clara): con 15 minutos de datos, el modelo propio de
  la sesión aporta poco tono.
- Con 3 frases por versión, las diferencias de medias (3,58–3,92) son ruido; la del acento (1 punto) es la
  más grande de la tabla.

**Decisión del autor (31-oct):** `naval_kapil` usa el LoRA de Naval (`B/paso_0158`) con la referencia de la
sesión con Kapil. El acento manda; el repaso propio queda en `piloto/lora_qwen/kapil/` sin usar.

## LoRA de Nivi, Brett y Deutsch — escucha a ciegas (2026-11-02)

Tres frases de cada voz con su referencia, en modo solo timbre, sin recorte de pausas. Notas del autor en
`puntuaciones_lora_qwen_<voz>.csv`, letras en `clave_lora_qwen_<voz>.json`. **Criterio del acento:** en Nivi,
5 = español nativo; en Brett y Deutsch el autor puntuó alto las versiones que **conservan un poco** su acento
(australiano y británico): quiere un español con un toque inglés que les dé personalidad.

Medias de parecido, acento y naturalidad (alucinaciones: 5 en todas salvo una nota de 4 en Deutsch base):

| Versión | Nivi | Brett | Deutsch |
|---|---|---|---|
| base (sin LoRA) | **4,22** (acento 4,0) | 4,22 | 3,78 |
| paso_0040 | 4,11 | 3,67 | 4,44 |
| paso_0080 | 4,11 | 3,67 | 4,22 |
| paso_0120 | 4,11 (acento 3,33) | 3,67 | **4,67** (4,67 / 4,67 / 4,67) |
| último (159 / 130 / 155) | 3,78 (acento 2,67) | **4,67** (4,33 / 4,67 / 5,0) | 3,89 |

Elegido (en `fabrica/voces.json`):

- **Nivi: Qwen base, sin LoRA.** Es el que más puntúa y el único sin ninguna nota por debajo de 4; el LoRA
  le devolvía acento inglés a medida que entrenaba (4,0 → 2,67).
- **Brett: `paso_0130`.**
- **Deutsch: `paso_0120`.**

Los tres suenan lentos, como Naval antes del recorte: las páginas no llevan el recorte de pausas de 0,12 s
que aplica la fábrica a todas las voces.

## Acento de Naval — escucha a ciegas (2026-11-02)

Cuaderno `piloto/cuadernos/08_acento_naval`: tres intervenciones reales de Naval (044 b02, 041 b02, 040 b04), como
en la fábrica (semilla por frase y pausas de 0,12 s). El autor encontraba a Naval «demasiado inglés» en el 044.
Notas en `puntuaciones_acento_naval.csv`, letras en `clave_acento_naval.json`.

| Versión | Parecido | Acento | Naturalidad | Alucinaciones | Media (3 primeros) |
|---|---|---|---|---|---|
| **actual** (LoRA B/paso_0158 + huella inglesa `naval_ref02`) | **5,00** | 4,00 | **5,00** | 5 | **4,67** |
| lora_ref_es1 (LoRA + huella del mejor clip español) | 4,00 | 4,00 | 4,00 | 5 | 4,00 |
| lora_ref_es5 (LoRA + media de 5 clips españoles) | 3,33 | 4,00 | 3,33 | 5 | 3,56 |
| lora_medio_ref_es5 (LoRA al 50 % + media española) | 3,00 | 4,33 | 3,33 | 5 | 3,56 |
| base_ref_es5 (sin LoRA + media española) | 3,67 | 4,00 | 3,33 | 5 | 3,67 |

Lectura:

- **La huella en español no mejora el acento** (4 en todas) y cuesta parecido y naturalidad: el x-vector del
  español sintético se aleja de Naval. El LoRA a media fuerza gana un tercio de punto de acento y pierde dos de
  parecido.
- **La versión actual gana** con claridad: 5 de parecido y de naturalidad. Su acento varía con el texto: 3 en el
  044 b02 (Thomas Schelling, *The Strategy of Conflict*: nombres y título en inglés) y 5 en el 040 b04. Parte de lo
  «inglés» que se oye en el 044 sale de los nombres y títulos en inglés del texto, no del modelo.

**Decisión:** Naval se queda como está (`B/paso_0158` + `naval_ref02`). Las palancas baratas quedan descartadas.
Si el acento sigue molestando en episodios enteros, lo siguiente sería un LoRA con más español (por ejemplo,
60 % español), que sí cuesta unidades.

## Las erres de Naval — escucha a ciegas (2026-11-03)

Cuaderno `piloto/cuadernos/09_erres_naval`: tres audios de dos frases reales de Naval con muchas erres y sin nombres
en inglés, con la referencia `naval_ref02`, misma semilla por frase y pausas de 0,12 s. El autor oía giros ingleses
en la r y la rr. Notas en `puntuaciones_erres_naval.csv`, letras en `clave_erres_naval.json`.

| Versión | Parecido | Acento | Naturalidad | Alucinaciones | Media (3 primeros) |
|---|---|---|---|---|---|
| actual (`B/paso_0158`, temperatura 0,9) | 3,67 | 3,33 | 4,00 | 5 | 3,67 |
| **paso_0120** | **4,33** | 4,33 | 4,33 | 5 | **4,33** |
| paso_0080 | 3,50 (2 notas) | 4,33 | **4,67** | 5 | 4,17 |
| paso_0040 | 3,67 | 4,33 | 4,00 | 5 | 4,00 |
| base (sin LoRA) | 4,00 | 4,33 | 4,33 | 5 | 4,22 |
| **actual_t07** (`B/paso_0158`, temperatura 0,7) | 4,00 | **4,67** | 4,33 | 5 | **4,33** |

Lectura:

- **Con frases llenas de erres, la versión actual es la peor en acento (3,33)**: confirma lo que oía el autor.
- **Bajar la temperatura a 0,7 da el mejor acento (4,67)** con el mismo modelo: menos variación al elegir cada
  sonido, menos erres a la inglesa. Empata en media con el paso 120.
- **El paso 120** es el más equilibrado y el que más se parece (4,33). Cualquier otra versión mejora el acento de
  la actual.
- Sin probar: el paso 120 con temperatura 0,7, que juntaría las dos mejoras.
- Muestra pequeña: 3 audios por versión.

