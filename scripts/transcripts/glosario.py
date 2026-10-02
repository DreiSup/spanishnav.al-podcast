#!/usr/bin/env python3
"""uso (desde la raiz del repo): python3 scripts/transcripts/glosario.py NNN '<json lista de [en, es]>'  -> añade a GLOSARIO.md sin duplicar el término inglés"""
import json, sys, re
n, pares = sys.argv[1], json.loads(sys.argv[2])
p = "GLOSARIO.md"
txt = open(p, encoding="utf-8").read()
sec = "## Decisiones del archivo de transcripts"
assert sec in txt
ya = {re.split(r" → ", l[2:])[0].strip().lower() for l in txt.split(sec)[1].splitlines() if l.startswith("- ")}
nuevas = [f"- {en} → {es} ({n})" for en, es in pares if en.strip().lower() not in ya]
saltadas = [en for en, es in pares if en.strip().lower() in ya]
if nuevas:
    open(p, "w", encoding="utf-8").write(txt.rstrip("\n") + "\n" + "\n".join(nuevas) + "\n")
print(f"{len(nuevas)} añadidas", "| ya estaban:", saltadas or "ninguna")
