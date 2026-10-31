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
