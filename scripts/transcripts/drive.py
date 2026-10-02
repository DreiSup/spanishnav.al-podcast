#!/usr/bin/env python3
"""Drive de transcripts via rclone. Los bytes nunca pasan por el contexto del agente.

  python drive.py hechos  <anio>
      Lista los numeros de episodio que ya tienen carpeta en Drive (p. ej. 001 002 ...).

  python drive.py subir   <anio> "<NNN> <Titulo en ingles>" <dir_local>
      Crea la carpeta si no existe, sube .txt y .json tal cual (sin convertir a
      Google Docs) y verifica que el tamano en Drive coincide byte a byte con el
      local. Sale con codigo 1 si algo no cuadra.

Raiz: gdrive:naval-podcast/transcripts originales  (remoto "gdrive", ver docs/almacenamiento.md)
"""
import json, re, subprocess, sys
from pathlib import Path

RAIZ = "gdrive:naval-podcast/transcripts originales"


def rclone(*args):
    r = subprocess.run(["rclone", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FALTA  rclone {' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout


def hechos(anio):
    salida = subprocess.run(["rclone", "lsf", "--dirs-only", f"{RAIZ}/{anio}"],
                            capture_output=True, text=True)
    if salida.returncode:  # la carpeta del anio todavia no existe
        return []
    return sorted(m.group(1) for l in salida.stdout.splitlines()
                  if (m := re.match(r"^(\d{3}) ", l)))


def subir(anio, carpeta, local):
    local = Path(local)
    archivos = sorted(p for p in local.iterdir() if p.suffix in {".txt", ".json"})
    if len(archivos) != 3:
        sys.exit(f"FALTA  se esperaban 3 archivos en {local}, hay {len(archivos)}")
    numero = carpeta[:3]
    if numero in hechos(anio):
        sys.exit(f"FALTA  ya existe una carpeta {numero} en {anio}; no se duplica")
    destino = f"{RAIZ}/{anio}/{carpeta}"
    rclone("mkdir", destino)
    for a in archivos:
        rclone("copyto", str(a), f"{destino}/{a.name}")
    remoto = {e["Name"]: e["Size"] for e in json.loads(rclone("lsjson", destino))}
    ok = True
    for a in archivos:
        tam = a.stat().st_size
        estado = "OK" if remoto.get(a.name) == tam else "FALTA"
        ok &= estado == "OK"
        print(f"{estado}  {a.name}  local {tam} B  drive {remoto.get(a.name)} B")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "hechos":
        print(" ".join(hechos(sys.argv[2])))
    elif len(sys.argv) == 5 and sys.argv[1] == "subir":
        subir(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        sys.exit(__doc__)
