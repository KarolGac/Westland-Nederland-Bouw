# Prompt v2: eigen GPT in ChatGPT Business

Versie 2 (14-10-2026). Vervangt v1 (`../offerte_naar_werkbon_v1.md`). Verschil met v1: disciplines zijn
de namen uit OutSmart, uren per persoon in plaats van alleen dagen, artikelcode-indeling, regels voor
"(al in keukenorder)" en afmonteren, en de hele offerte mag erin (besluit 14-10).

## Bestanden

| Bestand | Waar | Rol in de GPT |
|---|---|---|
| `instructies.md` | git | Instructies (± 4.400 tekens, limiet ± 8.000) |
| `beslisregels.md` | git | Kennisbestand |
| `artikelcodes.md` | lokaal, `data/verwerkt/kennis/` | Kennisbestand |
| `voorbeeldklussen.md` | lokaal, `data/verwerkt/kennis/` | Kennisbestand (bevat echte offertes, niet in git) |

De twee lokale bestanden maak je met:

```
python src/maak_kennisbestanden.py data/verwerkt/projecten data/verwerkt/kennis <projectcodes voorbeeldklussen>
```

## Vaste uitvoer

De GPT geeft altijd drie onderdelen: één tabel, "Niet ingepland" en "Vragen voor de planner".
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
ook als die uit de echte GPT is gekopieerd.

## Eigen GPT inrichten (zodra de licentie er is)

1. Instructies: de inhoud van `instructies.md` plakken.
2. Kennis: `beslisregels.md`, `artikelcodes.md` en `voorbeeldklussen.md` uploaden.
3. Model: GPT-6.1 Sol, als de bouwer dat laat kiezen.
4. Functies: webzoeken en afbeeldingen uit; geen acties.
5. Geheugen uit voor het account van de planner, zodat elke offerte los wordt beoordeeld.
6. Delen: alleen binnen de werkruimte van West Nederland Bouw.

## Testen via de API

```
python src/test_openai.py --droog       # klaarzetten zonder key
python src/test_openai.py --modellen    # juiste model-id controleren
python src/test_openai.py               # 11 testklussen x 3 runs
```

De API-test geeft de kennisbestanden helemaal mee in de systeemprompt; de GPT doorzoekt ze. Daarom na
de API-test 4 à 5 klussen met de hand in de echte GPT controleren.

## Beperking van de test

De vier voorbeeldklussen tellen niet mee in de test. De vuistregels in `beslisregels.md` zijn wel
afgeleid uit de hele export, dus ook uit de testklussen. De uitkomst is daardoor iets te positief.
Een eerlijke controle kan op nieuwe offertes (nieuwe export of live bij de planning in sprint 3).
