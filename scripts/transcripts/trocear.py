#!/usr/bin/env python3
"""Trocea un .txt con varias paginas de nav.al pegadas una tras otra.

Limites: cada pagina empieza en una linea "Naval" seguida de "* Archive"
(o "Archive") y termina en la linea "Related". El cuerpo es lo que hay entre
"* Subscribe" y "Related", sin las lineas en blanco de los bordes.
Normaliza BOM y CRLF a LF. Cruza fecha y titulo con catalogo.json.

Uso: python trocear.py documento.txt catalogo.json salida_dir
"""
import json, re, sys, unicodedata
from datetime import datetime
from pathlib import Path


def norm(t):
    t = unicodedata.normalize("NFKC", t).replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", t).strip().lower()


def numero(orden):
    if 1 <= orden <= 4 or 164 <= orden <= 166:
        return None
    return orden - 4 if orden <= 163 else orden - 7


doc, cat, salida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
salida.mkdir(parents=True, exist_ok=True)
texto = doc.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
lineas = texto.split("\n")
catalogo = json.load(open(cat, encoding="utf-8"))["episodios"]
por_titulo = {norm(e["titulo"]): e for e in catalogo}

FECHA = re.compile(r"^[A-Z][a-z]{2} \d{1,2} \d{4}$")
NAV = {"Archive", "X", "Instagram", "Subscribe"}


def es_nav(l):
    return l.strip().lstrip("*").strip() in NAV or not l.strip()


def linea_fecha(i):
    """Si la linea i es la cabecera "Naval", devuelve el indice de la fecha que la sigue."""
    if lineas[i].strip() != "Naval":
        return None
    j = i + 1
    while j < len(lineas) and es_nav(lineas[j]):
        j += 1
    return j if j < len(lineas) and FECHA.match(lineas[j].strip()) else None


inicios = [i for i in range(len(lineas)) if linea_fecha(i) is not None]

filas = []
for k, ini in enumerate(inicios):
    fin_bloque = inicios[k + 1] if k + 1 < len(inicios) else len(lineas)
    sub = linea_fecha(ini)
    rel = next((j for j in range(sub, fin_bloque) if lineas[j].strip() == "Related"), None)
    cuerpo = lineas[sub: rel if rel is not None else fin_bloque]
    while cuerpo and not cuerpo[0].strip():
        cuerpo.pop(0)
    while cuerpo and not cuerpo[-1].strip():
        cuerpo.pop()
    no_vacias = [l for l in cuerpo if l.strip()]
    fecha, titulo = no_vacias[0].strip(), no_vacias[1].strip()
    e = por_titulo.get(norm(titulo))
    try:
        iso = datetime.strptime(fecha, "%b %d %Y").strftime("%Y-%m-%d")
    except ValueError:
        iso = "?"
    num = numero(e["orden"]) if e else None
    slug_url = e["url"].rstrip("/").split("/")[-1] if e else "?"
    nombre = f"{num:03d}" if num else (f"extra" if e else f"pos{k + 1:03d}")
    archivo = salida / f"{nombre}_{slug_url}.txt"
    contenido_txt = "\n".join(cuerpo) + "\n"
    if archivo.exists():
        igual = archivo.read_text(encoding="utf-8") == contenido_txt
        print(f"AVISO  {archivo.name} repetido en el documento ({'identico, se ignora' if igual else 'DISTINTO, revisar a mano'})")
        if igual:
            continue
        archivo = salida / f"{nombre}_{slug_url}_dup{k + 1}.txt"
    archivo.write_text(contenido_txt, encoding="utf-8")
    filas.append({
        "pos": k + 1, "lineas": f"{ini + 1}-{(rel or fin_bloque) + 1}", "fecha": iso,
        "titulo": titulo, "orden": e["orden"] if e else None, "numero": num,
        "slug": slug_url, "related": rel is not None, "txt": str(archivo),
    })

json.dump(filas, open(salida / "indice.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f in filas:
    n = f"{f['numero']:03d}" if f["numero"] else ("extra" if f["orden"] else "???")
    aviso = "" if f["orden"] else "  <- NO ESTA EN EL CATALOGO"
    aviso += "" if f["related"] else "  <- SIN Related"
    print(f"{f['pos']:>2}  {n}  {f['fecha']}  orden {f['orden']}  {f['slug']:<28} {f['titulo']}  [{f['lineas']}]{aviso}")
nums = [f["numero"] for f in filas if f["numero"]]
dup = sorted({n for n in nums if nums.count(n) > 1})
huecos = sorted(set(range(min(nums), max(nums) + 1)) - set(nums)) if nums else []
print("duplicados:", dup or "ninguno", "| huecos:", huecos or "ninguno")
