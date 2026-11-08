# Resultados de la criba en zero-shot (2026-10-29)

Dos fuentes: las **métricas automáticas** del cuaderno 06, con 55 items por motor, y la
**escucha a ciegas del autor** del cuaderno 07, con 4 audios largos por motor.

- `puntuaciones_escucha_larga.csv`: las notas tal como salieron de la página.
- `clave_escucha_larga.json`: qué motor es cada letra.

## Escucha a ciegas

Notas del 1 (peor) al 5 (mejor). Cada celda es la media de los 4 audios: `n25` Naval,
`k10` Naval con la referencia de Kapil, `b10` Brett y `v10` Nivi. «Tono» solo se puntúa en
`k10`. La media es la de los cuatro primeros criterios.

| Motor | Parecido | Acento nativo | Naturalidad | Sin alucinaciones | Tono | Media |
|---|---|---|---|---|---|---|
| **omnivoice** | 4,75 | 3,00 | **4,75** | 4,75 | 3 | **4,31** |
| qwen3tts_1.7b | 3,75 | 1,75 | 4,50 | 4,75 | 4 | 3,69 |
| dots_soar | **5,00** | 1,25 | 3,75 | 4,00 | 4 | 3,50 |
| chatterbox_v3_es | 2,25 | 3,50 | 2,75 | **5,00** | 4 | 3,38 |
| chatterbox_v2 | 1,75 | 4,25 | 2,25 | **5,00** | 3 | 3,31 |
| xtts_base | 2,00 | **4,75** | 2,75 | 3,00 | 3 | 3,12 |

Detalle que pesa:

- **qwen3tts.** Acento 1 en Naval, en Kapil y en Brett; 4 en Nivi. Parecido 1 en Nivi y 5
  en Naval y Brett.
- **omnivoice.** Acento 3, 3, 2 y 4: el mejor de los motores naturales.
- **xtts_base.** Alucina en los dos bloques de Naval (`n25` y `k10`, nota 1), aunque tiene
  el mejor acento.
- **chatterbox_v2.** Acento 4–5 y ninguna alucinación, pero se parece poco y suena plano.

## Métricas automáticas (55 items por motor)

| Motor | WER | Items con WER > 15 % | Similitud ECAPA | UTMOSv2 | RTF |
|---|---|---|---|---|---|
| chatterbox_v2 | 1,2 % | 0 | 0,57 | 3,09 | 0,93 |
| chatterbox_v3_es | 1,5 % | 0 | 0,59 | 3,06 | 0,89 |
| chatterbox_v3 | 1,6 % | 0 | 0,57 | 3,00 | 0,89 |
| omnivoice | 2,6 % | 2 | 0,70 | 3,20 | 0,70 |
| xtts_base | 2,9 % | 3 | 0,42 | 2,91 | 0,51 |
| qwen3tts_1.7b | 3,6 % | 3 | 0,73 | 3,42 | 2,31 |
| xtts_navalchris | 4,0 % | 3 | 0,43 | 2,88 | 0,51 |
| dots_soar | 9,4 % | 7 | 0,74 | 3,01 | 2,23 |

La similitud se mide contra la referencia en inglés, así que también premia el acento
inglés. El acento solo lo juzga el oído.

## Lectura

- **Ningún motor tiene a la vez timbre, naturalidad y acento nativo.** Los que suenan a la
  persona (OmniVoice, Qwen3-TTS, dots.tts) arrastran el acento inglés. Los que pronuncian
  como nativos (XTTS, Chatterbox) no suenan a la persona.
- **A ciegas gana OmniVoice:** el mejor equilibrio y el menor acento entre los naturales.
  Qwen3-TTS queda segundo por el acento (1 en tres de cuatro audios) y por el parecido
  de Nivi.
- **Profesor de pronunciación para el fine-tuning:**
  - XTTS tiene el mejor acento, pero alucina en bloques largos.
  - Chatterbox V2 tiene casi el mismo acento y ninguna alucinación, así que se perderían
    menos clips al filtrar.
  - Los dos son candidatos.
- **Muestra pequeña:** 4 audios por motor y un solo oyente. Sirve para elegir dirección,
  no para cerrar la decisión.

## Qwen3-TTS: modo normal frente a modo solo timbre (x_vector_only)

Escucha a ciegas del autor (cuaderno 03c): 10 frases, cada una en los dos modos.

- `puntuaciones_escucha_xvector.csv`: las notas.
- `clave_escucha_xvector.json`: qué modo es cada letra.

| Modo | Parecido | Acento nativo | Naturalidad | Sin alucinaciones |
|---|---|---|---|---|
| Normal (grabación + transcripción) | **4,10** | 2,40 | **4,70** | 5,00 |
| Solo timbre (`x_vector_only`) | 3,70 | **4,60** | 3,89 | 5,00 |

Por voz, como parecido / acento:

| Voz | Normal | Solo timbre |
|---|---|---|
| Naval (`n05`, `n12`, `n25`) | 5, 5, 4 / 3, 2, 2 | **5, 5, 4 / 5, 5, 5** |
| Nivi (`v05`, `v10`) | 4, 2 / 2, 2 | 2, 3 / 4, 4 |
| Brett (`b10`) | 5 / 2 | 3 / 5 |
| Deutsch (`d02`, `d03`) | 5, 5 / 2, 2 | 3, 3 / 5, 3 |
| Kapil (`g01`, `g03`) | 2, 4 / 5, 2 | 4, 5 / 5, 5 |

La naturalidad y las alucinaciones de `n12` en modo solo timbre quedaron sin puntuar.

**Lectura.**

- El modo solo timbre **casi elimina el acento inglés**: pasa de 2,4 a 4,6.
- **Con Naval no pierde parecido** (5, 5, 4 en los dos modos) y el acento sube a 5 en las
  tres frases.
- Con Nivi, Brett y Deutsch el parecido baja a 2–3. Con Kapil sube.
- La naturalidad baja de 4,7 a 3,9.
- En este modo la referencia ya no transmite el tono de cada episodio.
