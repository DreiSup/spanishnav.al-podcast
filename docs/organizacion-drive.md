# Organización de Drive: propuesta (2026-10-30)

> **Propuesta, sin ejecutar.** Drive no se toca hasta que el autor la apruebe, y no se borra nada: lo
> antiguo se archiva tal cual.

## El problema

Hoy hay dos raíces que crecieron sin plan:

- **`fine_tunned_naval/`** mezcla todo: referencias, datasets, el dataset antiguo de XTTS de junio, la
  criba de motores, el piloto de fine-tuning (sintético, LoRA, pruebas, cachés) y salidas sueltas.
- **`naval-podcast/`** tiene los episodios en `transcripts/<año>/<NNN Título>/` y el buzón `_extraccion`.

Para producir solo hacen falta tres cosas: **los episodios**, **las voces** (referencia y LoRA de cada
hablante) y, por si hay que reentrenar, **el material de entrenamiento**. Lo demás es historia.

## La estructura nueva

```
spanishnav/
  LEEME.md                         qué hay en cada carpeta, en cinco líneas
  episodios/<año>/<NNN Título>/    todo lo de un episodio
    tts/                           los clips de la fábrica: 001naval.wav, 002nivi.wav…
    informe_tts.md                 frases sospechosas para Audacity
    borrador_tts.wav               escucha rápida
    audio/                         el audio limpio, salido de Audacity
    proyecto/                      el .aup3
    video/                         el .mp4 que se sube a YouTube
  voces/<voz>/                     lo que la fábrica necesita para que hable cada uno
    referencia.wav                 la ref02 elegida
    referencia.txt
    lora/                          el adaptador elegido (adapter_config.json + adapter_model.safetensors)
    ficha.md                       de dónde sale: dataset, checkpoint, fecha y notas de escucha
  entrenamiento/                   solo para reentrenar o añadir voces
    datasets/<voz>/
    sintetico/<voz>/
  archivo/                         lo de antes, tal cual
    fine_tunned_naval/
    naval-podcast_extraccion/
```

Tres reglas para que no vuelva a crecer sin plan:

1. **Producción y pruebas no se mezclan.** Lo que usa la fábrica vive en `voces/` y `episodios/`. Las
   pruebas de un modelo nuevo van a `entrenamiento/`, y solo el checkpoint elegido se copia a `voces/<voz>/lora/`.
2. **Un episodio, una carpeta.** Todo lo suyo dentro, con el mismo nombre de siempre (`<NNN Título>`).
3. **El repo manda.** `fabrica/voces.json` y `piloto/rutas.py` son los únicos sitios donde están las rutas;
   si algo se mueve, se cambia ahí.

## Cuándo y cómo

Cuando estén todas las voces entrenadas (decisión del autor, 30-oct):

1. Crear `spanishnav/` con las carpetas vacías y el `LEEME.md`.
2. **Mover** (no copiar) los episodios de `naval-podcast/transcripts/` a `spanishnav/episodios/`. Mover en
   Drive conserva los IDs y es instantáneo.
3. Para cada voz, **copiar** su referencia y el checkpoint elegido a `voces/<voz>/` y escribir su `ficha.md`.
4. Mover `datasets/` y los `sintetico/` a `entrenamiento/`.
5. Mover `fine_tunned_naval/` entero y lo que quede de `naval-podcast/` a `archivo/`.
6. En el repo: actualizar `fabrica/voces.json` (`rutas` y las rutas de cada voz), `piloto/rutas.py` y
   `drive.json`, y probar la fábrica con un episodio corto.

Los movimientos se hacen a mano en Drive (arrastrar carpetas) o con `rclone move` desde local, que mueve en
el servidor sin descargar nada. Por el conector de Drive solo se crean carpetas y ficheros de texto, nunca
se mueve audio.
