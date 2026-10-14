# Beslisregels: van offerteregel naar werkbon

Versie 2 (14-10-2026). Kennisbestand bij de eigen GPT en onderdeel van de systeemprompt in de API-test.

Bronnen: demo van Daphne en Matthijs (22-09), proef v1 (29-09) en de export van 2 oktober
(15 klussen, 93 werkdagen per discipline). De vuistregels voor personen en uren komen uit die export
en zijn nog niet bevestigd door de planning (vragen uitgezet op 12-10). Waar de planning iets anders
zegt, gaat de planning voor.

## 1. Wat is een werkbon

Een werkbon is één persoon op één dag voor één discipline, met een duur in uren. Twee monteurs die een
dag leidingwerk doen zijn dus twee werkbonnen. In het voorstel staat dat als één rij met
Personen = 2. Werkt de ene persoon 8 uur en de andere 4, dan zijn dat twee rijen.

De duur is bijna altijd 8 uur (hele dag), 4 uur (halve dag) of 2 uur. Andere duren komen voor, maar
weinig.

## 2. Regels die geen werkbon worden

| Regel | Waarom |
|---|---|
| Opname meerwerk (1.0) | Is al gedaan voordat de offerte er was; wordt verrekend met de keukenorder. |
| Algemene kosten (7,5% van de aanneemsom) | Geen werk. |
| Korting | Geen werk. |
| Subtotalen en btw | Geen werk. |
| Negatieve regel (creditering) | Geen eigen werkbon. Het werk van die discipline wordt kleiner of valt weg. |
| Tekstregel zonder aantal en bedrag | Geen werk, wel lezen: soms staat er een aanwijzing in (bijvoorbeeld "afdekken van de hal en lift"). |

Let op: regels met "(al in keukenorder)" zitten niet in het offertebedrag, maar het werk wordt wel
door West Nederland Bouw gedaan. Die regels plan je dus wel in.

## 3. Discipline per artikelcode

Het eerste getal van de artikelcode geeft het vakgebied. De volledige lijst staat in `artikelcodes.md`.

| Code | Vakgebied | Discipline in OutSmart |
|---|---|---|
| 1.x | Afplakken / beschermen | Demontage (afplakken gebeurt op de demontagedag) |
| 2.x | Demontage, afvoeren, sloop | Demontage |
| 3.x | Leidingwerk en elektra | Leidingwerk en elektra voor stuken |
| 4.x | Timmerwerk | Timmerwerk voor stuken |
| 5.x | Egalisatie | Egalisatie / vloerafwerking |
| 6.x | Stukwerk | Stukwerk |
| 7.x | Schakelmateriaal en spots | Afmonteren schakelmateriaal (zie 5.5) |
| 9.x | Schilderwerk | Latexen / schilderen |
| 10.x | Tegelwerk | Wand tegelen |

Regels zonder code: kies op basis van de tekst.
- Wandcontactdoos, thermostaat, kraan, badmeubel inclusief leidingwerk: Leidingwerk en elektra.
- Koof, lijsten, dakplaat, vloer uitvullen, rooster: Timmerwerk.
- Tegelreparatie: Wand tegelen.
- Twijfel je, zet het dan in de kolom Twijfel.

## 4. Volgorde

Demontage, Leidingwerk en elektra voor stuken, Timmerwerk voor stuken, Stukwerk,
Afmonteren schakelmateriaal, Leidingwerk en elektra na stuken, Timmerwerk na stuken,
Egalisatie / vloerafwerking, Wand tegelen, Latexen / schilderen.

## 5. Personen en uren (vuistregels uit de export)

### 5.1 Demontage
- Afplakken en demonteren gebeuren op één dag.
- Standaard 2 personen. Meestal 4 uur; 2 uur als het alleen om demonteren (en afvoeren) van de keuken gaat.
- Met wandtegels, een muur of wanden slopen: 2 à 3 personen, 4 à 8 uur.
- In alle 8 klussen met demontage in de export waren het 2 of 3 personen.

### 5.2 Leidingwerk en elektra voor stuken
- "Leidingwerk basis keuken" alleen: ongeveer 3 personen × 8 uur (in de export 18 tot 24 persoonuren).
- Extra groepen, een groepenkast, aardlekschakelaar, kabels, toeslag boren of kruipruimte: per regel
  ongeveer 4 à 8 persoonuren extra. Meer dan 24 persoonuren: verdeel over 2 dagen.
- Werk in de kruipruimte: minimaal 2 personen.
- Leidingwerk liefst met 2 of meer personen.

### 5.3 Timmerwerk
- Timmerwerk voor stuken (voorzetwanden, interieurbouw, verlaagd plafond, spotvoorbereiding):
  ongeveer 1 persoon × 8 uur per € 1.000 aan timmerwerk (excl. btw), meestal 1 à 3 personen.
- Timmerwerk na stuken: alleen werk dat pas na het stuken of na de montage van de keuken kan
  (koof dichtzetten, rooster plaatsen, lijsten, afwerking). In de offerte staat dan vaak "na montage keuken".

### 5.4 Stukwerk
- "Het stuken van de wand tot 21m2": 1 persoon × 8 uur.
- Stuken van het plafond of meer m²: een extra dag voor 1 persoon.

### 5.5 Afmonteren schakelmateriaal
- Alleen als er stukwerk is: de schakelaars en wandcontactdozen gaan er na het stuken weer op.
  1 à 2 personen × 2 à 4 uur, na het stukwerk. Schakelmateriaal en spots (7.x) horen hierbij.
- Zonder stukwerk: de 7.x-regels gaan mee met Leidingwerk en elektra voor stuken.

### 5.6 Overige disciplines
- Egalisatie (5.x): 1 persoon × 4 uur per ongeveer 10 m².
- Wand tegelen (10.x): 1 persoon × 8 uur voor ongeveer 4 à 6 m².
- Latexen / schilderen (9.x): 1 persoon × 8 uur per ongeveer 20 à 35 m².
- Leidingwerk en elektra na stuken: alleen als de offerte expliciet werk noemt dat na het stuken moet.

### 5.7 Geen vuistregel van toepassing
Reken met ongeveer € 1.000 (excl. btw) per persoon per dag en zet in de kolom Twijfel dat het een schatting is.

## 6. Open vragen aan de planning

1. Klopt "Leidingwerk basis keuken = 3 personen × 1 dag"?
2. Wanneer demontage 2 uur, 4 uur of 8 uur?
3. Wanneer komt er een aparte werkbon Afmonteren schakelmateriaal, en wanneer doet de leidingwerker dat?
4. Wanneer kies je "na stuken" in plaats van "voor stuken"?
5. Wordt een gesloopte muur (2.x) demontage of timmerwerk? In de export deed de timmerman het één keer.
