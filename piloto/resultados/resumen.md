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
