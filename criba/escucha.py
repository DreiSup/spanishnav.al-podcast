"""Página de escucha a ciegas de la criba.

Monta un HTML autocontenido (audios en MP3 dentro) en outputs/criba/escucha/ con las
versiones de cada item barajadas bajo letras, y guarda aparte la clave para descifrarlas.
Solo necesita ffmpeg: se puede generar en un entorno de Colab sin GPU.
"""
import base64
import html
import json
import random
import subprocess
import tempfile

import comun

CRITERIOS = [("parecido", "Parecido"), ("acento", "Acento nativo"), ("naturalidad", "Naturalidad"),
             ("alucinaciones", "Sin alucinaciones")]
NOTAS = ["", "1", "2", "3", "4", "5"]


def _mp3_b64(ruta):
    with tempfile.NamedTemporaryFile(suffix=".mp3") as t:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ruta), "-ac", "1", "-b:a", "64k", t.name],
                       check=True)
        return base64.b64encode(open(t.name, "rb").read()).decode()


def _audio(ruta):
    return f'<audio controls preload="none" src="data:audio/mpeg;base64,{_mp3_b64(ruta)}"></audio>'


def _select(item, letra, criterio):
    opciones = "".join(f"<option>{x}</option>" for x in NOTAS)
    return f'<select data-item="{item}" data-letra="{letra}" data-criterio="{criterio}">{opciones}</select>'


def construir_pagina(items_escucha, variantes, nombre="escucha", semilla=2026):
    """Escribe <nombre>.html y clave_<nombre>.json en outputs/criba/escucha/."""
    items, _ = comun.cargar_items()
    por_id = {it["id"]: it for it in items}
    rnd = random.Random(semilla)
    clave, bloques, n_audios = {}, [], 0
    for i in items_escucha:
        it = por_id[i]
        vs = [v for v in variantes if (comun.SALIDA / v / f"{i}.wav").exists()]
        rnd.shuffle(vs)
        letras = {chr(65 + n): v for n, v in enumerate(vs)}
        clave[i] = letras
        filas = []
        for letra, v in letras.items():
            selects = "".join(f"<label>{nom} {_select(i, letra, c)}</label>" for c, nom in CRITERIOS)
            extra = ""
            if it["ref"] == "naval_kapil":
                gemelo = comun.SALIDA / v / f"{it['mismo_texto_que']}.wav"
                if gemelo.exists():
                    extra = (f'<div class="gemelo">La misma versión con la referencia normal: {_audio(gemelo)}'
                             f'<label>Tono: ¿se nota el cambio hacia la referencia de Kapil? '
                             f'{_select(i, letra, "tono")}</label></div>')
                    n_audios += 1
            filas.append(f'<div class="version"><b>{letra}</b> {_audio(comun.SALIDA / v / f"{i}.wav")}'
                         f'<div class="notas">{selects}</div>{extra}</div>')
            n_audios += 1
        ref = comun.REFS / it["ref"] / f"{it['ref']}_ref02.wav"
        ancla = f'<div class="ancla">Referencia original ({it["ref"]}): {_audio(ref)}</div>' if ref.exists() else ""
        texto = html.escape(" ".join(it["frases"]))
        bloques.append(f'<section><h2>{i} · {it["voz"]}</h2><p class="texto">{texto}</p>{ancla}'
                       f'{"".join(filas)}</section>')

    pagina = _PLANTILLA.replace("{{BLOQUES}}", "".join(bloques)).replace("{{CLAVE_LS}}", f"criba_{nombre}_v1")
    pagina = pagina.replace("{{CSV}}", f"puntuaciones_{nombre}.csv")
    destino = comun.SALIDA / "escucha"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / f"{nombre}.html").write_text(pagina, encoding="utf-8")
    (destino / f"clave_{nombre}.json").write_text(json.dumps(clave, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Página: {destino / (nombre + '.html')} ({len(pagina) / 1e6:.1f} MB, {n_audios} audios a puntuar). "
          f"La clave está aparte, en clave_{nombre}.json: no la abras antes de puntuar.")


_PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Escucha a ciegas</title>
<style>
body{font-family:system-ui,sans-serif;max-width:900px;margin:0 auto;padding:16px;background:#fafafa;color:#222}
section{background:#fff;border:1px solid #ddd;border-radius:8px;padding:12px 16px;margin:16px 0}
.texto{font-style:italic} .ancla{color:#555;margin-bottom:8px}
.version{border-top:1px solid #eee;padding:8px 0} .notas label{margin-right:12px;white-space:nowrap}
.gemelo{margin-top:6px;padding-left:12px;border-left:3px solid #ccc} audio{vertical-align:middle;max-width:100%}
#barra{position:sticky;top:0;background:#222;color:#fff;padding:8px 12px;border-radius:6px}
button{font-size:15px;padding:4px 12px}
</style></head><body>
<div id="barra">Puntúa de 1 (mal) a 5 (perfecto). Tus notas se guardan en este navegador.
<button onclick="descargar()">Descargar puntuaciones (CSV)</button> <span id="cuenta"></span></div>
<p>Cada versión es un motor distinto, con letras al azar en cada frase. Escucha primero la referencia original.
<b>Sin alucinaciones</b>: 5 = dice exactamente el texto; 1 = repite, se salta o inventa palabras.</p>
{{BLOQUES}}
<script>
const K = "{{CLAVE_LS}}";
let notas = {};
try { notas = JSON.parse(localStorage.getItem(K) || "{}"); } catch (e) {}
const sels = document.querySelectorAll("select");
function id(s) { return s.dataset.item + "|" + s.dataset.letra + "|" + s.dataset.criterio; }
function contar() { document.getElementById("cuenta").textContent =
  Object.values(notas).filter(Boolean).length + " / " + sels.length + " notas"; }
sels.forEach(s => { if (notas[id(s)]) s.value = notas[id(s)];
  s.addEventListener("change", () => { notas[id(s)] = s.value;
    try { localStorage.setItem(K, JSON.stringify(notas)); } catch (e) {} contar(); }); });
contar();
function descargar() {
  let csv = "item,letra,criterio,nota\\n";
  sels.forEach(s => { if (s.value) csv += [s.dataset.item, s.dataset.letra, s.dataset.criterio, s.value].join(",") + "\\n"; });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], {type: "text/csv"}));
  a.download = "{{CSV}}"; a.click();
}
</script></body></html>"""
