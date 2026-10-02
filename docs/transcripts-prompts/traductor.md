Trabajas en el repo /home/user/spanishnav.al-podcast (usa rutas relativas a esa raíz; haz `cd /home/user/spanishnav.al-podcast` en cada comando Bash).

Tu rol y tus instrucciones completas están en `.claude/agents/traductor-episodio.md`. Léelo entero primero y síguelo al pie de la letra (incluido leer `GLOSARIO.md` antes de traducir, sobre todo la sección "Decisiones del archivo de transcripts", y mantener esos términos). No subas nada a Drive, no toques git, no escribas en `episodios/`, no edites GLOSARIO.md.

Criterio ya fijado: el "you" impersonal de los consejos se traduce con tú genérico (como en 011–015); vosotros solo si el inglés se dirige a un plural.

MODELO=Claude Opus 5.5, esfuerzo alto
SALIDA=trabajo/transcripts/<NUMERO>/  (créala si no existe; debe acabar con exactamente 3 archivos: .txt, .json y _es.json)

En `decisiones_nuevas` incluye solo términos que NO estén ya en GLOSARIO.md. Si una decisión tuya contradice algo del glosario, o algo no está cubierto por las reglas, ponlo en `dudas`.

Devuelve solo el informe JSON que describe el fichero de instrucciones.
