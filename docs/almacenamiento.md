# Dónde vive cada cosa

> **GitHub guarda texto y punteros. Google Drive guarda bytes.**

## Por qué

GitHub rechaza archivos de más de 100 MB y avisa a partir de 50. Un episodio de una hora son
~60 MB en mp3 y varios cientos en wav; los clips sueltos de TTS, decenas más. Y git guarda
**cada versión** de cada binario para siempre: regeneras el audio tres veces y el repo pesa
el triple, incluso después de borrar los archivos.

Git LFS tampoco resuelve esto: la cuota gratuita de GitHub es de 1 GB de almacenamiento y
1 GB/mes de tráfico, que con audio se agota en unos pocos episodios. El repo no tiene
configuración de LFS y no debe tenerla.

Drive, en cambio, ya está pagado y tiene espacio de sobra.

## El reparto

| Va a git | Va a Drive |
|---|---|
| `transcript.en.json` / `transcript.es.json` | Clips de TTS (uno por frase) |
| `metadata.en.json` / `metadata.es.json` | Audio final montado |
| `.md` generados, `INDICE.md`, `GLOSARIO.md` | Proyectos `.aup3` de Audacity |
| Scripts y documentación | Vídeos `.mp4` |

## Cómo se enlazan

**Por file ID, guardado en el texto.** `drive.json` tiene el ID de la raíz y de cada año; el
`metadata.es.json` de cada episodio tiene los suyos. Un ID sobrevive a renombrar la carpeta o
moverla; una ruta o una URL, no.

```
https://drive.google.com/drive/folders/<carpeta_id>
https://drive.google.com/file/d/<file_id>/view
```

## rclone

En Linux no existe cliente oficial de Google Drive. rclone es un binario de línea de comandos
—"rsync para la nube"— que habla el API de Drive directamente.

Configuración, una sola vez:

```bash
sudo apt install rclone
rclone config     # Google Drive → autorizar en el navegador → llamar al remoto "gdrive"
rclone lsd gdrive:naval-podcast      # comprobar que ve el árbol
```

Uso diario:

```bash
rclone copy ./clips "gdrive:naval-podcast/2019/007-slug/tts" -P      # subir
rclone copy "gdrive:naval-podcast/2019/007-slug/audio" ./audio -P    # bajar
rclone ls "gdrive:naval-podcast/2019"                                # listar
```

`copy` solo transfiere lo que falta o ha cambiado, así que relanzarlo es barato. `-P` muestra
progreso.

**`sync` no se usa en este flujo.** Espeja el origen en el destino, y eso significa *borrar*
en destino lo que no esté en origen. Si alguna vez lo necesitas, `--dry-run` primero.

El token de rclone queda en `~/.config/rclone/rclone.conf`, fuera del repo. `rclone.conf`
está en `.gitignore` por si acaso.

## Lo que esto no es

No hay carpeta mágica que se sincronice sola, ni GitHub ve nada de Drive, ni Drive sabe que
este repo existe. El vínculo es el ID guardado en el texto; el movimiento de bytes lo lanzas
tú.
