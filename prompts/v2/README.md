# Prompt v2: skill in ChatGPT Business

Versie 2 (14-10-2026). Vervangt v1 (`../offerte_naar_werkbon_v1.md`). Verschil met v1: disciplines zijn
de namen uit OutSmart, uren per persoon in plaats van alleen dagen, artikelcode-indeling, regels voor
"(al in keukenorder)" en afmonteren, en de hele offerte mag erin (besluit 14-10).

Eerst gemaakt voor een eigen GPT. Sinds 29-10 wordt het een skill, omdat OpenAI in december 2026 stopt
met eigen GPT's. De tekst van de prompt is daarvoor niet veranderd.

## Bestanden

| Bestand | Waar | Rol in de skill |
|---|---|---|
| `instructies.md` | git | `SKILL.md`, met naam en beschrijving erboven |
| `beslisregels.md` | git | `references/` |
| `artikelcodes.md` | lokaal, `data/verwerkt/kennis/` | `references/` |
| `voorbeeldklussen.md` | lokaal, `data/verwerkt/kennis/` | `references/` (bevat echte offertes, niet in git) |

De twee lokale bestanden maak je met:

```
python src/maak_kennisbestanden.py data/verwerkt/projecten data/verwerkt/kennis <projectcodes voorbeeldklussen>
```

## Vaste uitvoer

Het model geeft altijd drie onderdelen: één tabel, "Niet ingepland" en "Vragen voor de planner".
De tabel heeft precies deze kolommen:

| Kolom | Inhoud |
|---|---|
| Nr | Volgorde van uitvoering: 1, 2, 3 |
| Discipline | Exact een van de tien TypeOfWork-namen uit OutSmart (lijst in `instructies.md`) |
| Personen | Aantal personen, alleen een getal |
| Uren per persoon | 8 (hele dag), 4 (halve dag) of 2; ander heel getal alleen als nodig |
| Omschrijving werkbon | Titels van de offerteregels, met "Nx " bij aantallen, gescheiden door "; " |
| Offerteregels | Artikelcodes, gescheiden door komma's |
| Twijfel | Leeg, of kort waarom het model twijfelt |

Eén rij is één discipline op één werkdag. Werk dat twee dagen duurt staat op twee rijen. Personen die
op dezelfde dag verschillend lang werken staan op aparte rijen.

Waarom uren per persoon in plaats van "dagen": in OutSmart heeft elke werkbon een duur (WorkDuration).
In de export is 480 minuten (hele dag) het vaakst, dan 240 (halve dag) en 120 (2 uur). Zo kan de planner
de werkbon direct overnemen en kunnen we het voorstel één op één naast het antwoordblad leggen
(`src/maak_antwoordblad.py`, zelfde vorm). `src/werkbonvoorstel.py` leest de tabel in (`lees_voorstel`),
ook als die uit ChatGPT is gekopieerd.

## Skill in ChatGPT Business

1. Zip maken: `python src/maak_skill.py prompts/v2 data/verwerkt/kennis data/skill` geeft
   `data/skill/werkbonvoorstel.zip`. In `SKILL.md` is het stuk "Kennisbestanden" vervangen door een
   verwijzing naar `references/`, omdat een skill die bestanden pas opent als de instructies dat zeggen.
   De rest is gelijk aan `instructies.md`.
2. Uploaden: in ChatGPT bij Skills, Create, Upload from your computer, de zip kiezen.
3. Model: GPT-6.1 Sol kiezen in de chat. Het model zit niet in de skill.
4. Geheugen uit voor het account van de planner, zodat elke offerte los wordt beoordeeld.
5. Delen: in de bibliotheek van de werkruimte van West Nederland Bouw, niet daarbuiten.

ChatGPT gebruikt de skill als de vraag past bij de beschrijving bovenaan `SKILL.md`.

## Testen via de API

```
python src/test_openai.py --droog       # klaarzetten zonder key
python src/test_openai.py --modellen    # juiste model-id controleren
python src/test_openai.py               # 11 testklussen x 3 runs
python src/evalueer.py data/resultaten/<run-map>
```

De API-test geeft de kennisbestanden helemaal mee in de systeemprompt; in ChatGPT opent het model ze via
de skill. Daarom na de API-test 4 à 5 klussen met de hand in ChatGPT met de skill controleren: plak het
antwoord in `<projectcode>_skill1.md` in een map en draai `evalueer.py` op die map.

## Evaluatie

`src/evalueer.py` vergelijkt per antwoord en per discipline de persoonuren met het antwoordblad en telt
wat de planner zou moeten aanpassen: een vergeten discipline, een extra discipline of persoonuren buiten
de marge (standaard 4 uur of 25%, in te stellen met `--marge-uren` en `--marge-procent`). De verdeling
"precies goed / 1 à 2 aanpassingen / 3 of meer" sluit aan op de vraag uit de nulmeting wanneer een
voorstel goed genoeg is. Hetzelfde staat er nog eens met voor en na stuken samengenomen, omdat dat
onderscheid voor de planner een kleine correctie is.

## Beperking van de test

De vier voorbeeldklussen tellen niet mee in de test. De vuistregels in `beslisregels.md` zijn wel
afgeleid uit de hele export, dus ook uit de testklussen. De uitkomst is daardoor iets te positief.
Een eerlijke controle kan op nieuwe offertes (nieuwe export of live bij de planning in sprint 3).
