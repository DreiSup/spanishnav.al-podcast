#!/usr/bin/env python3
"""Vídeo «lectura»: el transcript en pantalla, sincronizado frase a frase con el master.

    python3 scripts/video_lectura.py 2020/053-philosopher --carpeta "/content/drive/.../053 Live Long Enough…"

Lee el texto de `episodios/<ep>/transcript.es.json` y los tiempos de `indice_master.tsv` (lo escribe la fábrica en la
carpeta de Drive del episodio: segundo del master en que empieza cada frase). No hace falta Whisper: la sincronía es
exacta por construcción. Escribe un subtítulo ASS con la maqueta y ffmpeg lo quema sobre un fondo liso con el master
como audio. Plan y decisiones en `docs/video-dinamico.md`.

Maqueta (1920×1080): cabecera con el podcast y el título; en el centro la frase que suena, grande, con el nombre de
quien habla encima; la frase anterior y la siguiente, atenuadas; barra de progreso abajo.

Opciones útiles para probar: `--duracion 60` (solo el primer minuto), `--solo-ass` (no renderiza), `--audio` y
`--indice` para dar los ficheros a mano.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ANCHO, ALTO = 1920, 1080

# Maqueta. Colores en RGB hex; ASS los quiere en &HBBGGRR.
FONDO = "0E0F12"
TEXTO = "F2F2F0"
TENUE = "6E737C"
CABECERA = "8A8F98"
BARRA_PISTA = "24262B"
BARRA = "E8B04B"
COLORES_HABLANTE = {"Naval": "E8B04B", "Nivi": "4FC3B5"}
OTROS_COLORES = ["9D8CF2", "F28C8C", "7FB2F0", "A6D96A"]

FUENTE = "Inter"
T_ACTUAL, T_HABLANTE = 64, 28
ESCALA_VECINA = 0.62              # tamaño de la anterior y la siguiente respecto a la que suena
INTERLINEA = 1.22
HUECO = 46                        # separación vertical entre frases del tambor
Y_HABLANTE = 190                  # nombre de quien habla, fijo sobre el tambor
TRANSICION = 0.6                  # s que tarda en girar el tambor (menos si la frase anterior es muy corta)
ADELANTO = 0.35                   # s antes del inicio de la frase en que empieza a girar
MARGEN = 220                      # margen lateral del texto central
CENTRO_Y = 600                    # centro vertical de la frase que suena (con 4+4+4 líneas el tambor cabe entre 230 y 970)
MAX_LINEAS_ACTUAL = 4             # si no cabe, se reduce el cuerpo
PODCAST = "Naval Podcast en español"


def ass_color(hex_rgb, alfa="00"):
    r, g, b = hex_rgb[0:2], hex_rgb[2:4], hex_rgb[4:6]
    return f"&H{alfa}{b}{g}{r}".upper()


def ruta_fuente(estilo):
    """Fichero de Inter con ese estilo (para medir el texto con PIL y partir las líneas igual que las dibuja libass)."""
    try:
        out = subprocess.run(["fc-match", f"{FUENTE}:style={estilo}", "-f", "%{file}"], capture_output=True,
                             text=True, check=True).stdout.strip()
        if FUENTE.lower() in Path(out).name.lower():
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    sys.exit(f"error: no encuentro la fuente {FUENTE} {estilo} (en Colab: apt-get install -y fonts-inter)")


class Medidor:
    def __init__(self):
        from PIL import ImageFont
        self._f = {}
        self._cargar = ImageFont.truetype
        self._rutas = {"SemiBold": ruta_fuente("SemiBold"), "Regular": ruta_fuente("Regular")}

    def ancho(self, texto, estilo, tam):
        clave = (estilo, tam)
        if clave not in self._f:
            self._f[clave] = self._cargar(self._rutas[estilo], tam)
        return self._f[clave].getlength(texto)

    def partir(self, texto, estilo, tam, ancho_max):
        lineas, actual = [], ""
        for palabra in texto.split():
            prueba = f"{actual} {palabra}".strip()
            if actual and self.ancho(prueba, estilo, tam) > ancho_max:
                lineas.append(actual)
                actual = palabra
            else:
                actual = prueba
        if actual:
            lineas.append(actual)
        return lineas


def leer_indice(ruta):
    filas = []
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines()[1:]:
        if not linea.strip():
            continue
        _, seg, clip, frase = linea.split("\t")
        filas.append((float(seg), clip, int(frase)))
    return filas


def frases_sincronizadas(transcript, indice):
    """[(inicio, hablante, texto)] en orden. El clip `004nivi.wav` es el bloque 4 del transcript (la fábrica numera
    los clips por posición, desde 1) y la frase k es su k-ésima frase no vacía."""
    bloques = transcript["contenido"]
    salida = []
    for seg, clip, k in indice:
        n = int(clip[:3])
        b = bloques[n - 1]
        frases = [f.strip() for f in b["frases"] if f.strip()]
        salida.append((seg, b["speaker"], frases[k - 1]))
    faltan = sum(len([f for f in b["frases"] if f.strip()]) for b in bloques) - len(salida)
    if faltan:
        print(f"aviso: el índice tiene {faltan} frases menos que el transcript (¿master antiguo?)", file=sys.stderr)
    return salida


def duracion_audio(ruta):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def t_ass(s):
    cs = int(round(s * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    sec, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def t_srt(s):
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def esc(texto):
    return texto.replace("\\", "＼").replace("{", "(").replace("}", ")")


def facilitar(u):
    """Curva de la transición: arranca y frena con suavidad (easeInOutCubic)."""
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def mezclar(c1, c2, e):
    a = [int(c1[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(c2[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x + (y - x) * e):02X}" for x, y in zip(a, b))


def ranura(k):
    """Cómo se ve una frase según su distancia `k` a la que suena (0), como los números de un candado: escala, aplastado
    vertical (la curvatura del tambor), opacidad (0–1), desenfoque y cuánto color de resaltado tiene."""
    k = abs(k)
    if k == 0:
        return dict(escala=1.0, aplaste=1.0, opac=1.0, blur=0.0, luz=1.0)
    if k == 1:
        return dict(escala=ESCALA_VECINA, aplaste=0.86, opac=0.55, blur=0.6, luz=0.0)
    return dict(escala=ESCALA_VECINA * 0.8, aplaste=0.6, opac=0.0, blur=1.5, luz=0.0)


def construir_ass(frases, transcript, fin_audio, medidor, fps):
    """Efecto tambor: las frases están en una columna que gira hacia arriba. La que suena, grande y resaltada en el
    centro; la anterior encima y la siguiente debajo, pequeñas y sombreadas. En cada cambio de frase toda la columna se
    desliza a la vez con una curva suave, calculada fotograma a fotograma (eventos de un fotograma solo durante la
    transición; entre transiciones, un evento fijo)."""
    hablantes, color = [], {}
    for _, h, _ in frases:
        if h not in hablantes:
            hablantes.append(h)
    for h in hablantes:
        otros = [x for x in color if x not in COLORES_HABLANTE]
        color[h] = COLORES_HABLANTE.get(h) or OTROS_COLORES[len(otros) % len(OTROS_COLORES)]

    ancho_txt = ANCHO - 2 * MARGEN
    # cada frase se parte una sola vez, al tamaño grande: al encoger o crecer conserva sus líneas y no salta
    trozos = []
    for _, _, texto in frases:
        tam = T_ACTUAL
        lineas = medidor.partir(texto, "SemiBold", tam, ancho_txt)
        while len(lineas) > MAX_LINEAS_ACTUAL and tam > 40:
            tam -= 4
            lineas = medidor.partir(texto, "SemiBold", tam, ancho_txt)
        trozos.append((tam, "\\N".join(esc(l) for l in lineas), len(lineas) * tam * INTERLINEA))

    def estado(s):
        """{frase: propiedades} con la frase `s` en el centro (s = -1: antes de empezar; la primera espera debajo)."""
        props = {}
        for k in range(-2, 3):
            j = s + k
            if 0 <= j < len(frases):
                props[j] = dict(ranura(k))
        # alturas: cada vecina se apila pegada a la anterior, con su altura ya encogida
        def alto(j):
            return trozos[j][2] * props[j]["escala"] * props[j]["aplaste"] if j in props else 0
        y = {}
        if s in props:
            y[s] = CENTRO_Y
        for paso in (-1, 1):
            borde = CENTRO_Y + paso * (alto(s) / 2 if s in props else 0)
            for k in (1, 2):
                j = s + paso * k
                if j in props:
                    y[j] = borde + paso * (HUECO + alto(j) / 2)
                    borde = y[j] + paso * alto(j) / 2
        for j in props:
            props[j]["y"] = y[j]
        return props

    def lineas_ass(props, t0, t1, capa=2):
        out = []
        a, b = t_ass(t0), t_ass(t1)
        for j, p in props.items():
            if p["opac"] <= 0.01:
                continue
            tam, cuerpo, _ = trozos[j]
            alfa = f"{round(255 * (1 - p['opac'])):02X}"
            col = mezclar(TENUE, TEXTO, p["luz"])
            out.append(f"Dialogue: {capa},{a},{b},Tambor,,0,0,0,,{{\\an5\\pos({ANCHO / 2:.0f},{p['y']:.2f})"
                       f"\\fs{tam}\\fscx{100 * p['escala']:.2f}\\fscy{100 * p['escala'] * p['aplaste']:.2f}"
                       f"\\1c{ass_color(col)}\\alpha&H{alfa}&\\blur{p['blur']:.2f}}}{cuerpo}")
        return out

    def interpolar(pa, pb, e):
        res = {}
        for j in set(pa) | set(pb):
            # lo que entra o sale del tambor lo hace desde/hacia la ranura de más allá, ya invisible
            a = pa.get(j) or dict(pb[j], opac=0.0, y=pb[j]["y"] + (HUECO * 3 if j > max(pa, default=j) else -HUECO * 3))
            b = pb.get(j) or dict(pa[j], opac=0.0, y=pa[j]["y"] + (-HUECO * 3 if j < min(pb, default=j) else HUECO * 3))
            res[j] = {c: a[c] + (b[c] - a[c]) * e for c in ("escala", "aplaste", "opac", "blur", "luz", "y")}
        return res

    cab = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {ANCHO}", f"PlayResY: {ALTO}", "WrapStyle: 2",
        "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        f"Style: Tambor,{FUENTE} SemiBold,{T_ACTUAL},{ass_color(TEXTO)},&H000000FF,&H00000000,&H00000000,0,0,0,0,"
        "100,100,0,0,1,0,0,5,0,0,0,1",
        f"Style: Hablante,{FUENTE} SemiBold,{T_HABLANTE},{ass_color(TEXTO)},&H000000FF,&H00000000,&H00000000,0,0,0,0,"
        "100,100,3,0,1,0,0,2,0,0,0,1",
        f"Style: Cabecera,{FUENTE},28,{ass_color(CABECERA)},&H000000FF,&H00000000,&H00000000,0,0,0,0,"
        "100,100,1,0,1,0,0,7,0,0,0,1",
        f"Style: Titulo,{FUENTE} SemiBold,40,{ass_color(TEXTO)},&H000000FF,&H00000000,&H00000000,0,0,0,0,"
        "100,100,0,0,1,0,0,7,0,0,0,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    ev = []
    numero = transcript.get("numero")
    ev.append(f"Dialogue: 0,0:00:00.00,{t_ass(fin_audio)},Cabecera,,0,0,0,,{{\\pos(120,70)}}"
              f"{esc(PODCAST.upper())}{'  ·  EPISODIO ' + str(numero) if numero else ''}")
    ev.append(f"Dialogue: 0,0:00:00.00,{t_ass(fin_audio)},Titulo,,0,0,0,,{{\\pos(120,112)}}{esc(transcript['titulo'])}")

    # transiciones: la de la frase s empieza ADELANTO s antes de su inicio y dura lo que permita la frase anterior
    paso_t = 1 / fps
    cuadro = lambda t: round(t * fps) / fps                       # todo cae en fotogramas exactos (50 fps = 2 cs)
    trans = []
    for s, (ini, _, _) in enumerate(frases):
        previo = frases[s - 1][0] if s else 0.0
        dur = min(TRANSICION, max(2 * paso_t, 0.6 * (ini - previo))) if s else min(TRANSICION, max(ini, 2 * paso_t))
        t0 = cuadro(max(0.0, ini - ADELANTO * dur / TRANSICION, trans[-1][1] if trans else 0.0))
        trans.append((t0, max(cuadro(t0 + dur), t0 + paso_t)))
    # tramo fijo inicial (la primera frase aún debajo) y luego, por cada frase, transición + tramo fijo
    if trans[0][0] > 0:
        ev += lineas_ass(estado(-1), 0.0, trans[0][0])
    for s in range(len(frases)):
        t0, t1 = trans[s]
        pa, pb = estado(s - 1), estado(s)
        n = max(1, round((t1 - t0) * fps))
        for f in range(n):
            e = facilitar((f + 1) / n)
            ev += lineas_ass(interpolar(pa, pb, e), t0 + f * paso_t, t0 + (f + 1) * paso_t)
        fin_fijo = trans[s + 1][0] if s + 1 < len(frases) else fin_audio
        if fin_fijo > t1:
            ev += lineas_ass(pb, t1, fin_fijo)

    # quién habla: fijo sobre el tambor, cambia con un fundido solo cuando cambia el hablante
    tramos = []
    for s, (_, h, _) in enumerate(frases):
        if tramos and tramos[-1][0] == h:
            continue
        tramos.append([h, trans[s][0] if tramos else 0.0])
    for n_t, (h, t0) in enumerate(tramos):
        t1 = tramos[n_t + 1][1] if n_t + 1 < len(tramos) else fin_audio
        ev.append(f"Dialogue: 1,{t_ass(t0)},{t_ass(t1)},Hablante,,0,0,0,,{{\\an5\\pos({ANCHO // 2},{Y_HABLANTE})"
                  f"\\c{ass_color(color[h])}\\fad(250,250)}}{esc(h.upper())}")

    srt = []
    for i, (ini, _, texto) in enumerate(frases):
        fin = frases[i + 1][0] if i + 1 < len(frases) else fin_audio
        srt.append(f"{i + 1}\n{t_srt(ini)} --> {t_srt(fin)}\n{texto}\n")
    return "\n".join(cab + ev) + "\n", "\n".join(srt)


def renderizar(audio, ass, salida, fin, fps, preset, crf):
    """Fondo liso + barra de progreso (overlay que avanza con t) + ASS + audio del master."""
    alto_barra, y_barra = 6, ALTO - 6
    ass_f = str(ass).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    filtro = (
        f"color=c=0x{FONDO}:s={ANCHO}x{ALTO}:r={fps}:d={fin:.2f}[fondo];"
        f"color=c=0x{BARRA_PISTA}:s={ANCHO}x{alto_barra}:r={fps}:d={fin:.2f}[pista];"
        f"color=c=0x{BARRA}:s={ANCHO}x{alto_barra}:r={fps}:d={fin:.2f}[barra];"
        f"[fondo][pista]overlay=0:{y_barra}[f1];"
        f"[f1][barra]overlay=x='-W+W*t/{fin:.2f}':y={y_barra}:eval=frame[f2];"
        f"[f2]ass='{ass_f}',format=yuv420p[v]"
    )
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", "-i", str(audio), "-filter_complex", filtro,
           "-map", "[v]", "-map", "0:a", "-t", f"{fin:.2f}",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-tune", "stillimage", "-g", str(fps * 10),
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(salida)]
    t0 = time.time()
    subprocess.run(cmd, check=True)
    dt = time.time() - t0
    print(f"renderizado: {salida} ({fin / 60:.1f} min de vídeo en {dt:.0f} s, {fin / dt:.1f}× tiempo real)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episodio", help="año/carpeta del repo, p. ej. 2020/053-philosopher")
    ap.add_argument("--carpeta", help="carpeta de Drive del episodio (con indice_master.tsv y audio/)")
    ap.add_argument("--audio", help="master (por defecto, el .mp3 de <carpeta>/audio sin «descartada»)")
    ap.add_argument("--indice", help="indice_master.tsv (por defecto, el de <carpeta>)")
    ap.add_argument("--salida", help="carpeta de salida (por defecto <carpeta>/video)")
    ap.add_argument("--duracion", type=float, help="renderizar solo los primeros N segundos")
    ap.add_argument("--fps", type=int, default=50, help="50 por defecto: suave y cada fotograma cae en un centisegundo exacto del ASS")
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--solo-ass", action="store_true", help="escribe el .ass y el .srt sin renderizar")
    a = ap.parse_args()

    base = RAIZ / "episodios" / a.episodio
    transcript = json.loads((base / "transcript.es.json").read_text(encoding="utf-8"))
    carpeta = Path(a.carpeta) if a.carpeta else None
    indice = Path(a.indice) if a.indice else carpeta / "indice_master.tsv"
    if a.audio:
        audio = Path(a.audio)
    else:
        candidatos = sorted(p for p in (carpeta / "audio").glob("*.mp3") if "descartada" not in p.name)
        if len(candidatos) != 1:
            sys.exit(f"error: esperaba un master en {carpeta / 'audio'} y hay {len(candidatos)}; usa --audio")
        audio = candidatos[0]
    salida = Path(a.salida) if a.salida else (carpeta / "video")
    salida.mkdir(parents=True, exist_ok=True)

    frases = frases_sincronizadas(transcript, leer_indice(indice))
    fin = duracion_audio(audio)
    if a.duracion:
        fin = min(fin, a.duracion)
        frases = [f for f in frases if f[0] < fin]
    ass, srt = construir_ass(frases, transcript, fin, Medidor(), a.fps)
    nombre = base.name + (f".prueba{int(fin)}s" if a.duracion else "")
    (salida / f"{nombre}.lectura.ass").write_text(ass, encoding="utf-8")
    (salida / f"{base.name}.es.srt").write_text(srt, encoding="utf-8")
    print(f"{len(frases)} frases · {fin / 60:.1f} min · ass y srt en {salida}")
    if not a.solo_ass:
        renderizar(audio, salida / f"{nombre}.lectura.ass", salida / f"{nombre}.lectura.mp4", fin, a.fps,
                   a.preset, a.crf)


if __name__ == "__main__":
    main()
