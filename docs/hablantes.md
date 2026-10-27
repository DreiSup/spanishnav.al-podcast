# Hablantes del podcast de Naval y fuentes de audio limpio en inglés

Fecha: 2026-10-27. Fuente de la parte A: los 8 Google Docs anuales («<año> all podcasts»), exportados como
texto plano y analizados con Python. Scripts y datos intermedios en
`/tmp/claude-0/-home-user-spanishnav-al-podcast/3e6ea671-664b-5a1a-88dd-acd78dc2fb27/scratchpad/scripts/`,
`.../scratchpad/eps.json` (episodios segmentados) y `.../scratchpad/hablantes.json` (recuento por hablante y episodio).

## Método (parte A)

- **Segmentación**: cada episodio empieza en el Doc con una línea `Naval`, a veces seguida de `* Archive / * X / …`,
  luego la fecha (`Feb 28 2019`), el título, el subtítulo, la duración y `Get podcast`. El cuerpo se corta en la
  línea `Related`, para no contar el pie de enlaces relacionados. Títulos cruzados con `catalogo.json` por texto
  normalizado: **164 de 168 casan**.
- **Hablantes**: se detectaron todas las líneas `Algo:` (≈150 prefijos distintos). Se descartaron a mano los
  falsos positivos: duraciones (`2:22`), frases con dos puntos («Here's a simple example:», «Part 1:»,
  «Learn more about Constructor Theory here:», «New: Discuss this episode on Airchat»…) y títulos de sección.
  Variantes unificadas: `David`/`David Deutsch`, `Brett`/`Brett Hall`, `Max`/`Max Hodak`,
  `Guillermo`/`Guillermo Rauch`, `Blake`/`Blake Scholl`.
- **Atribución**: las líneas sin prefijo se asignan al último hablante. Se excluyen los títulos de sección
  (línea de ≤15 palabras sin puntuación final; se excluyeron 799 títulos distintos).
- **Duplicados**: el Doc de 2019 trae «Read What You Love…» (orden 20) dos veces, y el de 2021 trae «Is the
  Universe Discrete or Continuous?» (92) dos veces. Se cuentan una sola vez.
- **Recopilatorios** (marcados `[REC]`): 56 *How to Get Rich* (episodios 5–54 más extra), 81 *Happiness* (57–71),
  109 y 134 *The Beginning of Infinity* (clips de 2021) y 167 *The AI Industrial Revolution* (164–166 más una
  parte nueva). Por eso se dan dos cifras: **bruta** (todo) y **sin duplicados** (cada línea de texto se cuenta
  una vez por hablante). Para medir cuánta voz distinta existe, la buena es la de sin duplicados.
- **Minutos** = palabras / 150, como se pidió. **Aviso:** en los episodios de más de 5 minutos, la duración real
  (de la cabecera del Doc) da **~180 palabras/min** (palabras totales de 1.401 min de episodio). Con /150 los
  minutos salen **~20 % altos**; el tiempo real de habla es aproximadamente minutos × 0,83.

## Episodios del catálogo que no están en ningún Doc

| Orden | Título | URL | Nota |
|---|---|---|---|
| 1 | On Meditation | https://nav.al/on-meditation | Diálogo Naval–Kapil Gupta, enero-feb 2019 (extra) |
| 2 | On Humility | https://nav.al/on-humility | ídem |
| 3 | A Founder's Anxiety | https://nav.al/a-founders-anxiety | ídem |
| 4 | The Need for Indifference | https://nav.al/the-need-for-indifference | ídem |

Además:
- **168 *Live in the Future*** (2 jul 2026, 1:07:52) **sí está en el Doc de 2026, pero solo con la cabecera**: no
  hay transcript. La descripción dice: «Naval with three founders who are living in the future: Garry Tan (Y
  Combinator), Daniel Francis (Abel Police), and Farbood Nivi (A-LIST).» Esos tres hablantes no se pueden contar.
- El Doc de 2020 contiene un post que **no está en `catalogo.json`**: *Finding Time to Invest in Yourself*
  (13 ene 2020, Naval + Nivi; es el material extra del final de *How to Get Rich*). En las tablas aparece como
  episodio «0».

## Tabla 1 — Hablante → episodios → minutos → prioridad

Episodios por número de orden del catálogo. «Interv.» = turnos con prefijo de hablante.

| Hablante | Episodios (orden del catálogo) | Nº ep. | Interv. | Palabras (brutas) | Min. brutos (/150) | Palabras sin dup. | Min. sin dup. (/150) | Prioridad |
|---|---|---|---|---|---|---|---|---|
| **Naval Ravikant** | 0, 5–82, 84–87, 89–90, 92–93, 95–96, 98, 100–110, 112, 114, 116–118, 122–127, 129–149, 151–167 | 150 | 832 | 200.053 | 1.334 | 140.721 | **938** | **Máxima**: voz principal en casi todo |
| **David Deutsch** | 137–142 | 6 | 221 | 39.039 | 260 | 39.035 | **260** | **Alta**: el invitado con más tiempo, en 6 episodios largos |
| **Brett Hall** | 78–80, 82–84, 87–109, 111–113, 115, 117–123, 125–126, 128–129, 132–134, 138–142 | 52 | 178 | 28.389 | 189 | 17.033 | **114** | **Alta**: toda la serie BoI de 2021 y los Deutsch Files |
| **Nivi** (Babak Nivi, cofundador de AngelList) | 0, 5, 7–28, 30–31, 33–51, 53–57, 73, 81, 143–144, 147, 150, 152–155, 157–165, 167 | 70 | 273 | 13.117 | 87 | 9.000 | **60** | **Alta**: poco tiempo pero en 70 episodios, y es la otra voz fija |
| **Vitalik Buterin** | 135–136 | 2 | 53 | 7.591 | 51 | 7.591 | **51** | Media |
| **Max Hodak** | 164–167 | 4 | 44 | 5.051 | 34 | 4.016 | **27** | Media-baja (164–166 son extras) |
| **Matt Ridley** | 74–75 | 2 | 30 | 4.267 | 28 | 4.267 | **28** | Media |
| **Guillermo Rauch** | 164–167 | 4 | 43 | 4.152 | 28 | 3.162 | **21** | Media-baja |
| **Kapil Gupta** | 72 (+ 1–4 sin transcript en los Docs) | 1 (+4) | 48 | 3.801 | 25 | 3.801 | **25** (+ lo de 1–4) | Media: con los 4 extras sube bastante |
| **Blake Scholl** | 164–167 | 4 | 21 | 2.266 | 15 | 1.784 | **12** | Baja |
| **Haseeb Qureshi** | 135–136 | 2 | 20 | 1.808 | 12 | 1.808 | **12** | Baja |
| Garry Tan | 168 (sin transcript) | 1 | — | — | — | — | — | Pendiente: no hay texto |
| Daniel Francis | 168 (sin transcript) | 1 | — | — | — | — | — | Pendiente |
| Farbood Nivi | 168 (sin transcript) | 1 | — | — | — | — | — | Pendiente; ver nota |

Notas:
- Episodios donde Naval no tiene prefijo: 83, 88, 91, 94, 97, 99, 111, 113, 115, 119–121, 128 y 150. Son clips
  de la serie BoI de 2021 en los que solo habla Brett, y el 150, en el que solo habla Nivi. Puede que en el audio
  Naval diga algo que el transcript no recoge (suposición).
- **Nivi**: el transcript de 2019 dice «I'm Nivi, the co-founder of AngelList with Naval. And I co-authored the
  Venture Hacks blog with him»: es **Babak Nivi**. **Farbood Nivi**, del episodio 168, es según Crunchbase y
  Wikipedia el fundador de Grockit. Parece **otra persona**, aunque no he verificado la relación entre ambos.
  Conviene no mezclar sus voces.
- **Kapil Gupta**: en el 72 habla 3.801 palabras frente a 3.963 de Naval. En los diálogos 1–4, por el formato,
  es de esperar que hable aún más (suposición: no hay texto en los Docs).
- **Advertencia de calidad sacada del propio transcript**: en el 160 *A Motorcycle for the Mind*, Nivi dice
  «we are not at the same location… I am actually walking around town… there might be some ambient noise».
  Ese episodio, y quizá otros de 2026, no es buen material de referencia para la voz.
- Sugerencia: para Blake Scholl, Haseeb Qureshi y los tres del 168 (≤12 min cada uno), quizá no compense un
  fine-tune propio. Bastaría con clonar en zero-shot desde una referencia corta, o usar una voz genérica.

## Tabla 2 — Fuentes de audio limpio por hablante

**Verificación.** «Doc» = duración leída de la cabecera del episodio en los Google Docs, verificada. «Listado» =
dato de un agregador o de la página de la plataforma tal como lo devolvió la búsqueda web. **No he podido abrir
ninguna página**: WebFetch falló por DNS en todos los dominios, así que las duraciones web no están comprobadas
de primera mano. Las notas de calidad son suposiciones razonadas salvo que se diga otra cosa.

### Naval Ravikant
Tono: calmado y didáctico en los monólogos; más enérgico y rápido en entrevistas largas (Rogan, Modern Wisdom).

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| Naval Podcast: *How to Get Rich* (episodio completo, orden 56) | https://nav.al/rich | 3:35:35 (Doc) | Estudio, 2019. Naval ≈ 91 % del texto (37.261 de ~40.750 palabras). Lo mejor por cantidad | Calmado, expositivo |
| Naval Podcast, serie de clips de 2025 (143–157; p. ej. *Blame Yourself for Everything…* 4:39, *Find the Simplest Thing That Works* 6:18) | https://nav.al/agency · https://nav.al/simplest | 1–6 min cada uno (Doc) | Casi monólogo; Nivi solo lee el tweet. Naval más reciente (2025) | Reflexivo, pausado |
| Naval Podcast: *In the Arena* (158) / *Curate People* (159) | https://nav.al/in-the-arena · https://nav.al/curate-people | 41:45 / 52:03 (Doc) | Naval ≈ 93 % y 88 % del texto (8.181 y 8.763 palabras) | Conversacional, más enérgico |
| The Joe Rogan Experience #1309 – Naval Ravikant (jun 2019) | https://www.youtube.com/watch?v=3qHkcs3kG44 | ~150 min (Listado: TheTVDB) | Estudio de JRE, buena calidad; Naval habla mucho, Rogan interrumpe algo | Conversacional, relajado-enérgico |
| Modern Wisdom #922 – Naval Ravikant – 44 Harsh Truths About Human Nature (31 mar 2025) | https://podcasts.apple.com/gb/podcast/922-naval-ravikant-44-harsh-truths-about-human-nature/id1347973549?i=1000701535098 | 3h16m (Listado: Apple) | Estudio; formato de «verdades» que Naval desarrolla, así que habla la mayor parte | Variado: serio, enfático |
| The Tim Ferriss Show #473 – Naval Ravikant on Happiness, Reducing Anxiety, Crypto Stablecoins, and Crypto Strategy (15 oct 2020) | https://tim.blog/2020/10/15/naval-transcript/ | 2h01m (Listado: Podwise) | Buena calidad; reparto equilibrado entre los dos | Conversacional |
| The Knowledge Project #18 – Naval Ravikant: The Angel Philosopher (2017) | https://fs.blog/knowledge-project-podcast/naval-ravikant-171 | «más de 2 h» (Listado: Shane Parrish) | Naval de 2017, la voz más joven; útil para variar | Calmado, filosófico |

**Audiolibro**: *The Almanack of Naval Ravikant* **no lo lee Naval**. El narrador es Vikas Adam (Listado:
Audiobooks Now). Solo la edición con «bonus audio» trae una conversación con Naval. No sirve como fuente
principal.

### Nivi (Babak Nivi)
Tono: calmado y medido; lee tweets y hace preguntas. Hay poco material suyo fuera del podcast.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| Su propio podcast «Nivi», episodio *Are LLMs Creative?* (3 mar 2024) | https://podcasts.apple.com/us/podcast/are-llms-creative/id1734104587?i=1000647835694 · https://nivi.com/ | No confirmada | Charla en solitario (según el listado). **La mejor fuente si es solo él** | Expositivo |
| «Nivi», *The Totalitarianism of Knowledge* (9 abr 2024) | https://www.podengine.ai/podcasts/nivi | No confirmada | Charla más preguntas del público, según la descripción; puede haber reverberación de sala (suposición) | Expositivo, técnico |
| Naval Podcast: *How to Get Rich* (56) | https://nav.al/rich | 3:35:35 (Doc) | Nivi 3.493 palabras (~20–23 min), repartidas en 78 turnos, con calidad de estudio | Lector de tweets, preguntas |
| Naval Podcast: *Curate People* (159) / *Sell the Truth* (163) | https://nav.al/curate-people · https://nav.al/sell | 52:03 / 27:40 (Doc) | Nivi 1.142 y 584 palabras. Evitar el 160 (grabado andando, con ruido) | Conversacional |

### David Deutsch
Tono: pausado, preciso, con muchos silencios; acento británico. Casi todas sus entrevistas son en remoto, así
que la calidad varía (suposición).

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| Naval: *The Deutsch Files I–IV* (139–142) | https://nav.al/deutsch-files-i · …-ii · …-iii · https://nav.al/deutsch-files-iv | 54:52 · 1:14:27 · 59:17 · 1:25:05 (Doc) | Deutsch habla 6.075 / 9.154 / 6.383 / 9.787 palabras: la mayor parte de cada episodio | Pausado, argumentativo |
| Sean Carroll's Mindscape #253 – David Deutsch on Science, Complexity, and Explanation (16 oct 2023) | https://www.preposterousuniverse.com/podcast/2023/10/16/253-david-deutsch-on-science-complexity-and-explanation/ | ~1h42m (Listado: Podwise) | Carroll cuida el audio; Deutsch habla mucho (suposición) | Técnico, calmado |
| EconTalk – David Deutsch on the Pattern (22 dic 2025) | https://podcasts.apple.com/us/podcast/david-deutsch-on-the-pattern/id135066958?i=1000742308410 | 1h26m (Listado) | Buena calidad habitual en EconTalk; tema grave (antisemitismo), así que aporta un registro distinto | Serio, grave |
| The TED Interview – David Deutsch on the infinite reach of knowledge (2019) | https://www.ted.com/talks/the_ted_interview_david_deutsch_on_the_infinite_reach_of_knowledge | No confirmada | Producción de TED, solo audio | Divulgativo |
| Making Sense #52 – Finding Our Way in the Cosmos (2016) / #414 – Strange Truths (2025) | https://samharris.substack.com/p/52-finding-our-way-in-the-cosmos-cf7 | ~45 min (#52, reproductor; puede ser la parte gratuita) | Sam Harris tiene parte de los episodios tras muro de pago (suposición) | Conversacional |

**Audiolibro**: *The Beginning of Infinity* lo narra **Walter Dixon**, no Deutsch (Listado: Audible). No sirve.

### Brett Hall
Tono: calmado, de profesor; acento australiano. En ToKCast hay muchas horas en solitario: es el caso ideal.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| ToKCast – Episode 2: Chapter 1 "The Reach of Explanations" (y siguientes capítulos de BoI) | https://brettroberthall.podbean.com/e/the-beginning-of-infinity-chapter-1-commentary/ | No confirmada (media del show ~57 min, Listado) | **En solitario**: lee y comenta. Habla el 100 % | Didáctico, calmado |
| ToKCast – Ep 99: David Deutsch's "The Beginning of Infinity" – a retrospective in 99 minutes | https://brettroberthall.podbean.com/e/ep-99-david-deutsch-s-the-beginning-of-infinity-a-retrospective-in-99-minutes/ | ~99 min (por el título) | En solitario | Resumen, ritmo sostenido |
| Do Explain (Christofer Lövgren) – The Nature of Knowledge, with Brett Hall (1/2 y 2/2) | https://metacast.app/podcast/do-explain-with-christofer-lovgren/9HHQ9Wgw/the-nature-of-knowledge-with-brett-hall-2-2/jwiMH47t | No confirmada | Entrevista: Brett habla mucho y en un registro más dialogado | Conversacional |
| Naval: *The Beginning of Infinity, Part 1 / Part 2* (109, 134) | https://nav.al/infinity · https://nav.al/infinity-2 | 66:09 / 52:51 (Doc) | Brett 6.789 y 4.719 palabras, más que Naval | Divulgativo |
| Two for Tea – Ep 135 Brett Hall | https://it.player.fm/series/two-for-tea-podcast/ep-135-brett-hall | No confirmada | Entrevista | Conversacional |

### Vitalik Buterin
Tono: rápido, técnico y bastante monótono, con pausas para pensar. Es el registro más difícil de variar.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| Lex Fridman Podcast #80 – Vitalik Buterin: Ethereum, Cryptocurrency, and the Future of Money (mar 2020) | https://lexfridman.com/vitalik-buterin/ | ~95 min (Listado) | Presencial, buen micro; Vitalik habla la mayor parte | Técnico, calmado |
| Lex Fridman Podcast #188 – Vitalik Buterin: Ethereum 2.0 (3 jun 2021) | https://lexfridman.com/vitalik-buterin-2 | 3h08m (Listado: Anghami, TheTVDB) | Igual que el anterior; mucho material | Técnico |
| Bankless – Vitalik Buterin: How Ethereum Becomes The World Ledger (ago 2025) | https://www.bankless.com/read/vitalik-talks-ethereum-vision-value-on-bankless.md | ~2h03m (Listado: Podwise) | Vitalik reciente; dos presentadores | Conversacional |
| Naval: *Vitalik: Ethereum, Part 1/2* (135–136) | https://nav.al/vitalik · https://nav.al/vitalik-2 | 46:06 / 24:59 (Doc) | Vitalik 4.757 + 2.834 palabras | Técnico |

### Matt Ridley
Tono: británico, narrativo y claro.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| Audiolibro *How Innovation Works*, **leído por Matt Ridley** (Harper Audio, 2020) | https://www.audible.com/pd/0063007312 | ~12h30m (Listado: Audible y otros) | **La mejor fuente de todo el informe**: audio de estudio, una sola voz, horas de material | Narrativo, pausado |
| EconTalk – Matt Ridley on the Evolution of Everything (22 feb 2016) | https://app.podwise.ai/dashboard/episodes/5385552 | 1h09m (Listado) | Calidad EconTalk; da registro de conversación | Conversacional |
| Uncommon Knowledge (Hoover) – How Innovation Works with Matt Ridley (grabado el 6 may 2020) | https://www.hoover.org/node/78430 | No confirmada | Entrevista en vídeo, quizá en remoto por la fecha (suposición) | Conversacional |
| Naval: *Matt Ridley: How Innovation Works, Part 1/2* (74–75) | https://nav.al/matt-ridley · https://nav.al/matt-ridley-2 | 29:49 / 30:31 (Doc) | Ridley 2.020 + 2.247 palabras; el transcript dice «who is on the line», así que probablemente es remoto | Conversacional |

### Kapil Gupta
Tono: lento, deliberado, sentencioso, casi hipnótico; registro muy particular.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| Naval: diálogos con Kapil, órdenes 1–4 (*On Meditation*, *On Humility*, *A Founder's Anxiety*, *The Need for Indifference*) | https://nav.al/on-meditation · https://nav.al/on-humility · https://nav.al/a-founders-anxiety · https://nav.al/the-need-for-indifference | No confirmada (no están en los Docs) | Mismo entorno que el resto del podcast; es material del propio proyecto | Sentencioso |
| Naval: *Kapil Gupta: Conquering the Mind* (72) | https://nav.al/kapil | 40:46 (Doc) | Kapil 3.801 palabras (~mitad) | Sentencioso |
| «Kapil Gupta Podcasts» (en solitario, 2019; Podcast Notes lista p. ej. *What Is Life*, *The Limitless Human*, *Wild Freedom*) | https://www.listennotes.com/podcasts/kapil-gupta-podcasts-kapil-gupta-YCqmRdWGO8P/ | No confirmada | **En solitario**. Listen Notes avisa de que algunos audios pueden estar rotos | Monólogo intenso |
| Becoming an Epic Being – Nothing but The Truth with Kapil Gupta (may 2024) | https://podcasters.spotify.com/pod/show/epicbeings/episodes/Nothing-but-The-Truth-with-Kapil-Gupta-e2jsncj | No confirmada | Entrevista reciente; calidad desconocida | Conversacional |

(Hay también un Q&A de Clubhouse del 8 mar 2021, https://www.youtube.com/watch?v=GfY2YlHphJM. Por ser Clubhouse,
el audio será comprimido: no lo recomiendo.)

### Max Hodak
Tono: rápido, técnico y seguro; registro de fundador.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| Core Memory (Ashlee Vance) EP 09 – Engineering Brains / «Max Hodak Loves Brains» (13 mar 2025) | https://www.mypodcastdata.com/podcast/show/core-memory-ashlee-vance-xr1/episodes | ~1h10m (Listado) | Grabado presencialmente en la sede de Science; entrevista larga | Conversacional |
| StrictlyVC Download (TechCrunch) – Max Hodak is more worried about Twitter than brain-computer interface hacking | https://techcrunch.com/podcast/max-hodak-is-more-worried-about-twitter-than-brain-computer-interface-hacking/ | No confirmada | Podcast de TechCrunch | Conversacional |
| No Priors (Sarah Guo) – From Restoring Sight to Reimagining the Brain | (en No Priors; enlace no verificado) | No confirmada | — | Técnico |

(Core Memory EP 77 es en directo y con público: peor para clonar.)

### Guillermo Rauch
Tono: muy rápido y enérgico; acento argentino en inglés.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| ACQ2 by Acquired – Building Web Apps with Just English and AI (feb 2025) | https://podcastaddict.com/acq2-by-acquired/episode/201308861 | ~57 min (Listado) | Producción de Acquired, buena | Enérgico |
| Every «AI & I» Ep. 47 – Vercel's Guillermo Rauch on What Comes After Coding (Dan Shipper, feb 2025) | https://every.to/podcast/best-of-the-pod-vercel-s-guillermo-rauch-on-what-comes-after-coding | ~56 min (Listado) | Entrevista 1:1 | Conversacional |
| The Eric Ries Show – Inside Vercel (ago 2025) | https://podbay.fm/p/the-eric-ries-show/e/1754580675 | ~79 min (Listado) | Entrevista larga 1:1 | Conversacional, narrativo |

### Blake Scholl
Tono: entusiasta y directo; registro de fundador vendiendo una visión.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| Conversations with Tyler Ep. 261 – Blake Scholl on Supersonic Flight and Fixing Broken Infrastructure – Live at the Progress Conference (pub. 19 nov 2025) | https://conversationswithtyler.com/episodes/blake-scholl/ | No confirmada | **En directo con público** (posibles risas o sala) | Enérgico, provocador |
| How I Invest (David Weisburd) – The Next Elon Musk? Boom's CEO on Disrupting Air Travel | https://boomsupersonic.com/flyby/how-i-invest-podcast-the-next-elon-musk-booms-ceo-on-disrupting-air-travel | No confirmada | Entrevista 1:1 | Conversacional |
| ARK Invest FYI – Supersonic Travel with Blake Scholl | https://boomsupersonic.com/press-release/ark-invest-podcast | No confirmada | Entrevista | Explicativo |
| Payload – The Future of Supersonic, with Blake Scholl | https://payloadspace.com/podcast/the-future-of-supersonic-with-blake-scholl-ceo-of-boom-supersonic/ | No confirmada | Entrevista | Explicativo |

### Haseeb Qureshi
Tono: claro y analítico; rápido.

| Fuente | Enlace | Duración | Calidad / cuánto habla | Tono |
|---|---|---|---|---|
| When Shift Happens E104 – Dragonfly Managing Partner: How to get Rich by mastering crypto investing (without getting lucky) | https://open.spotify.com/episode/1o5RaplHOj5nSOlSFhbcVd · https://www.youtube.com/watch?v=61B175Ckm2o | No confirmada | Entrevista larga 1:1 (formato del show) | Conversacional |
| Trailblazers – Haseeb Qureshi: Managing Partner at Dragonfly | https://open.spotify.com/episode/47TeTcToDkPUBBIPBE5zqO | No confirmada | Entrevista 1:1 | Biográfico |
| The Chopping Block (copresentador, con Tom Schmidt, Tarun Chitra y Robert Leshner) | https://unchainedcrypto.com/the-chopping-block-will-modular-blockchains-win/ | Cientos de episodios | Cuatro voces y solapes: **peor** para clonar, pero hay mucha cantidad | Debate rápido |

### Hablantes del 168 (sin transcript)
- **Garry Tan**: su canal de YouTube (https://youtube.com/garrytan) tiene vídeos en solitario hablando a cámara,
  y hay una entrevista en CNBC del 14 mar 2025 de ~33 min (Listado). No investigado a fondo.
- **Daniel Francis** (Abel): no he encontrado ningún podcast; solo prensa (TechCrunch, 17 oct 2024).
- **Farbood Nivi**: entrevista antigua en Mixergy sobre Grockit
  (https://mixergy.com/interviews/farbood-nivi-grockit-interview/). Es una persona distinta del Nivi del podcast
  (no verificado).

## Enlaces usados

- https://podcasts.apple.com/us/podcast/live-in-the-future/id1454097755?i=1000775254284 · https://nav.al/future · https://naval.substack.com/p/live-in-the-future
- https://www.audiobooksnow.com/audiobook/9781668136041 · https://www.overdrive.com/media/11939461/the-almanack-of-naval-ravikant
- https://thetvdb.com/series/joe-rogan-experience/episodes/7224970 · https://www.youtube.com/watch?v=3qHkcs3kG44
- https://podcasts.apple.com/gb/podcast/922-naval-ravikant-44-harsh-truths-about-human-nature/id1347973549?i=1000701535098 · https://www.shortform.com/podcast/episode/modern-wisdom-2025-03-31-episode-summary-922-naval-ravikant-44-harsh-truths-about-human-nature
- https://tim.blog/2020/10/15/naval-transcript/ · https://podwise.ai/episodes/116099 · https://podwise.ai/episodes/116478
- https://fs.blog/knowledge-project-podcast/naval-ravikant-171 · https://apple.co/2ySxrz7
- https://podcastnotes.org/naval-periscope-sessions/naval-ravikant-finding-time-to-invest-in-yourself/ · https://analogue.com/podcast/how-to-get-rich-every-episode-6d0htq
- https://podcasts.apple.com/us/podcast/are-llms-creative/id1734104587?i=1000647835694 · https://nivi.com/ · https://www.podengine.ai/podcasts/nivi
- https://spearhead.co/angel · https://podwise.ai/episodes/77088
- https://crunchbase.com/person/farbood-nivi · https://en.wikipedia.org/wiki/Grockit · https://mixergy.com/interviews/farbood-nivi-grockit-interview/
- https://podwise.ai/episodes/168156 · https://www.preposterousuniverse.com/podcast/2023/10/16/253-david-deutsch-on-science-complexity-and-explanation/
- https://podcasts.apple.com/us/podcast/david-deutsch-on-the-pattern/id135066958?i=1000742308410 · https://podcast.feedspot.com/david_deutsch_podcasts/
- https://www.ted.com/talks/the_ted_interview_david_deutsch_on_the_infinite_reach_of_knowledge
- https://samharris.substack.com/p/52-finding-our-way-in-the-cosmos-cf7 · https://samharris.substack.com/p/making-sense-414-strange-truths
- https://www.audible.com/pd/B005HR40BG
- https://brettroberthall.podbean.com/e/the-beginning-of-infinity-chapter-1-commentary/ · https://brettroberthall.podbean.com/e/ep-99-david-deutsch-s-the-beginning-of-infinity-a-retrospective-in-99-minutes/ · https://www.listennotes.com/podcasts/tokcast-brett-hall-J3YkzjetRuN/ · https://www.bretthall.org/speaking.html
- https://metacast.app/podcast/do-explain-with-christofer-lovgren/9HHQ9Wgw/the-nature-of-knowledge-with-brett-hall-2-2/jwiMH47t · https://it.player.fm/series/two-for-tea-podcast/ep-135-brett-hall
- https://lexfridman.com/vitalik-buterin/ · https://lexfridman.com/vitalik-buterin-2 · https://thetvdb.com/series/lex-fridman-podcast/episodes/9174905
- https://www.bankless.com/read/vitalik-talks-ethereum-vision-value-on-bankless.md · https://app.podwise.ai/dashboard/episodes/5538137
- https://www.audible.com/pd/0063007312 · https://www.learnoutloud.com/Catalog/Technology/-/How-Innovation-Works/131567 · https://app.podwise.ai/dashboard/episodes/5385552 · https://www.hoover.org/node/78430
- https://www.listennotes.com/podcasts/kapil-gupta-podcasts-kapil-gupta-YCqmRdWGO8P/ · https://podcastnotes.org/category/kapil-guptas-solo-podcast/ · https://podcasters.spotify.com/pod/show/epicbeings/episodes/Nothing-but-The-Truth-with-Kapil-Gupta-e2jsncj · https://www.youtube.com/watch?v=GfY2YlHphJM
- https://www.mypodcastdata.com/podcast/show/core-memory-ashlee-vance-xr1/episodes · https://techcrunch.com/podcast/max-hodak-is-more-worried-about-twitter-than-brain-computer-interface-hacking/ · https://en.wikipedia.org/wiki/Max_Hodak
- https://podcastaddict.com/acq2-by-acquired/episode/201308861 · https://every.to/podcast/best-of-the-pod-vercel-s-guillermo-rauch-on-what-comes-after-coding · https://podbay.fm/p/the-eric-ries-show/e/1754580675
- https://conversationswithtyler.com/episodes/blake-scholl/ · https://cowenconvos.libsyn.com/blake-scholl-on-supersonic-flight-and-fixing-broken-infrastructure-live-at-the-progress-conference · https://boomsupersonic.com/flyby/how-i-invest-podcast-the-next-elon-musk-booms-ceo-on-disrupting-air-travel · https://boomsupersonic.com/press-release/ark-invest-podcast · https://payloadspace.com/podcast/the-future-of-supersonic-with-blake-scholl-ceo-of-boom-supersonic/
- https://open.spotify.com/episode/1o5RaplHOj5nSOlSFhbcVd · https://www.youtube.com/watch?v=61B175Ckm2o · https://open.spotify.com/episode/47TeTcToDkPUBBIPBE5zqO · https://unchainedcrypto.com/the-chopping-block-will-modular-blockchains-win/
- https://podwise.ai/episodes/3428631 · https://techcrunch.com/2024/10/17/from-elon-musk-to-cop-car-chases-how-a-software-engineer-launched-a-police-ai-startup
