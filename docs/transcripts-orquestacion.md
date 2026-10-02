# Orquestación del archivo de transcripts

Instrucciones para la sesión principal de Claude Code. Para lanzarlo:

> Lee `docs/transcripts-orquestacion.md` y ejecútalo con `<ruta al .txt del año>`.

## Objetivo

Archivar todos los episodios de un año de nav.al en Google Drive con tres archivos cada uno:
- Formato 99: el `.txt` literal.
- Formato 0: inglés literal en JSON.
- Formato 5: español apto para TTS en JSON.

Los episodios se procesan **de uno en uno y en orden**. No se empieza el siguiente hasta que el anterior está subido y verificado. Así el glosario se hereda de un episodio al siguiente.

## Antes del bucle (una vez por sesión)

1. Pregunta a Ysst qué modelo y qué nivel de esfuerzo estás usando, y guárdalo como `MODELO`. Formato: `Claude Opus 5.5, esfuerzo alto`.
2. Trocea el documento:
   `python3 scripts/transcripts/trocear.py <doc.txt> catalogo.json trabajo/transcripts/troceo`
   Revisa la tabla que imprime:
   - Si sale `NO ESTA EN EL CATALOGO`, `DISTINTO, revisar a mano`, o hay huecos o duplicados, **para y enséñaselo a Ysst**.
   - Los repetidos idénticos se ignoran solos.
3. Consulta qué hay ya en Drive:
   `python3 scripts/transcripts/drive.py hechos <año>`
   Los números que aparezcan se saltan.
4. Dile a Ysst en una línea qué episodios vas a procesar y empieza. No esperes confirmación.

## El bucle, por cada episodio pendiente y en orden de número

1. **Casos que paran el bucle.** Pregunta a Ysst antes de seguir si el episodio es:
   - Un extra sin número.
   - Un episodio muy largo, de más de 150 líneas. En 2019 son el 051, *How to Angel Invest, Part 1*, y el 052, *How to Get Rich*.
   - Un recopilatorio. El 052 lo es: repite toda la serie.
2. **Lanza el subagente `traductor-episodio`** con:
   - `TXT=trabajo/transcripts/troceo/<NNN>_<slug>.txt`
   - `NUMERO=<NNN>`
   - `MODELO`
   - `SALIDA=trabajo/transcripts/<NNN>/`
   Espera a que termine.
3. **Lee su informe.**
   - Si `dudas` no está vacío o la `validacion` no es `OK 0 / OK 5`, **para y pregunta a Ysst**.
   - Vuelve a validar tú también. No te fíes solo del informe.
4. **Sube a Drive:**
   `python3 scripts/transcripts/drive.py subir <año> "<NNN> <Título en inglés tal cual aparece en la página>" trabajo/transcripts/<NNN>/`
   El título va en la segunda línea no vacía del `.txt` y conserva los apóstrofos tipográficos. Si el script sale con error, **para**.
5. **Glosario.** Añade las `decisiones_nuevas` del informe a `GLOSARIO.md`, en la sección `## Decisiones del archivo de transcripts`. Créala si no existe. Formato de cada línea: `- inglés → español (NNN)`. No dupliques términos que ya estén.
6. **Informa a Ysst en dos o tres líneas:** número, título, turnos, frases en/es, tamaños verificados y decisiones nuevas. Pasa al siguiente.

## Lo que este flujo NO hace sin permiso explícito

- Escribir en `episodios/` del repo, ejecutar `normalizar-extraccion.py` o hacer commits. La sincronización con GitHub es una fase aparte. Ojo: el repo ya tiene episodios en estado `revision`, y el normalizador podría pisarlos.
- Sobrescribir o borrar nada en Drive. `drive.py` se niega a duplicar una carpeta existente.
- Inventar convenciones. Ante cualquier caso nuevo, pregunta.

## Estructura en Drive

```
naval-podcast/transcripts originales/<año>/<NNN> <Título en inglés>/
  <YYYY-MM-DD>_<slug-del-título>.txt        Formato 99
  <YYYY-MM-DD>_<slug-del-título>.json       Formato 0
  <YYYY-MM-DD>_<slug-del-título>_es.json    Formato 5
```

- La numeración es global y sigue el feed: `número = orden del catálogo − 4`. Los órdenes 1–4 son extras.
- **No confundir** con `naval-podcast/<año>/`, que es la carpeta de audio que referencia `drive.json`.

## Estado al crear este documento

- Hechos: del 001 al 011 de 2019.
- Siguiente: el 012, *Partner With Rational Optimists*.
