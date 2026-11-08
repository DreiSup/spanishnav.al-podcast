# Tablero

Dirección: https://spanishnav-tablero.vercel.app/ (vista Kanban: `#kanban`). Proyecto de Vercel
`spanishnav-tablero`, rama de producción `main`: los cambios de la página se suben a `main` (solo esta carpeta).

Página estática (un solo `index.html`, sin build) que muestra en qué etapa está cada episodio.
Lee `tablero.json` de la rama `claude/quirky-dirac-x18c3n` en raw.githubusercontent.com, así que
**no hace falta redesplegarla** cuando cambian los datos: basta con regenerar y subir el JSON.

- Datos: `python3 scripts/tablero.py --web ../spanishnaval-web --r2` (desde la raíz del repo) y push.
- Despliegue: proyecto de Vercel aparte, importado de este repo con *Root Directory* `tablero`,
  *Framework* «Other» y la rama de producción `main`.
- GitHub cachea el JSON 5 minutos: un cambio recién subido puede tardar eso en verse.
