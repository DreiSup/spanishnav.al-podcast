# spanishnav.al-podcast

Traducción al español del podcast de Naval. Este repositorio guarda **el texto** del
proceso: transcripciones originales, traducciones y metadatos de todos los episodios,
de 2019 al último de 2026.

El audio, los clips de TTS y los vídeos **no están aquí**: viven en Google Drive y se
enlazan desde cada episodio por *file ID*.

> Si vas a trabajar en este repo —persona o agente— lee **[CLAUDE.md](CLAUDE.md)** primero.
> Explica la estructura, los esquemas, el vínculo con Drive y cómo operar.

## Qué hay en cada episodio

```
episodios/<año>/<NNN>-<slug>/
  transcript.en.json     original            ← fuente de verdad
  transcript.es.json     traducción          ← fuente de verdad
  metadata.en.json       datos de la fuente
  metadata.es.json       título es, YouTube, estado y punteros a Drive
  transcript.*.md        generados, no editar
```

Índice de episodios: [INDICE.md](INDICE.md) · Criterios de traducción:
[GLOSARIO.md](GLOSARIO.md)

## Cómo se enlaza con Google Drive

GitHub no puede montar una carpeta de Drive. El vínculo son dos piezas:

- **`drive.json`** guarda el ID de la carpeta raíz y el de cada año; el `metadata.es.json`
  de cada episodio guarda los de sus ficheros. Los IDs sobreviven a renombrados.
- **rclone** mueve los bytes desde local cuando se lo pides. No hay sincronización
  automática.

Detalles y comandos en [docs/almacenamiento.md](docs/almacenamiento.md).

## Estado

La estructura está montada y los años 2019–2026 creados, en el repo y en Drive. **Todavía no
se ha extraído ningún episodio.**

nav.al está bloqueado desde las sesiones web de Claude Code, así que la extracción la hace
Claude web y esta sesión normaliza lo que entrega. El protocolo está en
[docs/extraccion.md](docs/extraccion.md).

## Derechos

El contenido original es de sus autores. Cada `metadata.en.json` guarda la URL de origen del
episodio, y la descripción de YouTube acredita la fuente.
