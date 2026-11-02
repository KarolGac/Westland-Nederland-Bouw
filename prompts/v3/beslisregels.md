# Beslisregels: van offerteregel naar werkbon

Versie 3 (02-11-2026). Kennisbestand bij de skill en onderdeel van de systeemprompt in de API-test.

Bronnen: demo van Daphne en Matthijs (22-09), proef v1 (29-09), de export van 2 oktober (15 klussen,
93 werkdagen per discipline) en de controlelijst die de planning heeft ingevuld (oktober 2026). Waar de
planning iets anders zegt dan de export, gaat de planning voor.

## 1. Wat is een werkbon

Een werkbon is één persoon op één dag voor één discipline, met een duur in uren. Twee monteurs die een
dag leidingwerk doen zijn dus twee werkbonnen. In het voorstel staat dat als één rij met
Personen = 2. Werkt de ene persoon 8 uur en de andere 4, dan zijn dat twee rijen.

Bij werk van meerdere dagen krijgt elke dag een nieuwe werkbon, zodat per dag duidelijk is wat er is
gedaan.

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
door West Nederland Bouw gedaan. Die regels plan je dus wel in, ook als er in de PDF geen bedrag bij staat.

Een andere regel van € 0 of zonder bedrag (bijvoorbeeld "Gat afzuigkap dichten") krijgt geen eigen rij en
geen eigen discipline. Neem hem op in de omschrijving van de discipline waar hij bij hoort.

## 3. Discipline per artikelcode

Het eerste getal van de artikelcode geeft het vakgebied. De volledige lijst staat in `artikelcodes.md`.
In een PDF staan geen artikelcodes: zoek daar de titel van de regel op.

| Code | Vakgebied | Discipline in OutSmart |
|---|---|---|
| 1.x | Afplakken / beschermen | Demontage (afplakken gebeurt op de demontagedag) |
| 2.x | Demontage, afvoeren, sloop | Demontage |
| 3.x | Leidingwerk en elektra | Leidingwerk en elektra voor stuken |
| 4.x | Timmerwerk | Timmerwerk voor stuken |
| 5.x | Egalisatie | Vaak mee met Timmerwerk voor stuken, anders Egalisatie / vloerafwerking (zie 5.6) |
| 6.x | Stukwerk | Stukwerk |
| 7.x | Schakelmateriaal en spots | Afmonteren schakelmateriaal (zie 5.5) |
| 9.x | Schilderwerk | Latexen / schilderen |
| 10.x | Tegelwerk | Wand tegelen |

Leidingwerk is al het loodgieters- én elektrawerk: groepen, stopcontacten, schakelmateriaal. Meestal doet
dezelfde monteur beide.

Regels zonder code: kies op basis van de tekst.
- Wandcontactdoos, thermostaat, kraan, badmeubel inclusief leidingwerk, gat afzuigkap dichten: Leidingwerk en elektra.
- Maatwerk interieurbouw, inbouwkast, koof, koplatten, lijsten, dakplaat, vloer uitvullen, rooster: Timmerwerk.
- Vensterbank of andere onderdelen demonteren en afvoeren: Demontage.
- Tegelreparatie: Wand tegelen.
- Houtrot: wordt uitbesteed aan de schilder. Zet het bij Latexen / schilderen en meld het bij Twijfel.
- Twijfel je, zet het dan in de kolom Twijfel.

## 4. Volgorde

Demontage, Leidingwerk en elektra voor stuken, Timmerwerk voor stuken, Stukwerk,
Afmonteren schakelmateriaal, Leidingwerk en elektra na stuken, Timmerwerk na stuken,
Egalisatie / vloerafwerking, Wand tegelen, Latexen / schilderen.

Er zijn uitzonderingen. In de droogtijd van het stukwerk kan er wel worden geëgaliseerd, de vloer
getegeld en schakelmateriaal afgemonteerd.

## 5. Personen en uren

De algemene regel van de planning is ongeveer € 1.000 per persoon per dag, met de bedragen per discipline
opgeteld. Dat klopt meestal, en de planner kijkt daarbij ook naar het werk zelf. Voor demontage geldt die
regel niet, en voor stukwerk, tegelwerk en schilderwerk staan hieronder de vuistregels uit de export.

### 5.1 Demontage
- Afplakken en demonteren gebeuren op één dag, ongeacht het bedrag.
- Vaak een halve dag: standaard 2 personen × 4 uur, ook als er wandtegels worden verwijderd.
- 2 uur kan als het alleen om demonteren en afvoeren van de keuken gaat.
- Een muur of wanden slopen: 2 à 3 personen, 4 à 8 uur.

### 5.2 Leidingwerk en elektra voor stuken
- Tel de bedragen van de leidingwerkregels op en reken ongeveer € 1.000 per persoon per dag.
  Voorbeeld uit de demo: € 2.309 is 2 personen × 1 dag.
- Toeslagen (kruipruimte, boren of frezen in beton) tel je niet helemaal mee: het is een toeslag op het
  werk, geen extra werk.
- "Leidingwerk basis keuken" is altijd minstens 2 personen × 8 uur. Staat hij "(al in keukenorder)", dan
  is de prijs lager maar het werk hetzelfde.
- Leidingwerk gaat bij voorkeur in koppels van 2 personen. Sommige monteurs werken ook alleen.
- Meer werk is een extra dag, niet meer personen.
- Kruipruimte: altijd minimaal 2 personen, vanwege de veiligheid.

### 5.3 Timmerwerk
- Timmerwerk voor stuken (maatwerk interieurbouw, inbouwkasten, koof, koplatten, voorzetwanden, verlaagd
  plafond, spotvoorbereiding): ongeveer 1 persoon × 8 uur per € 1.000 aan timmerwerk (excl. btw), meestal
  1 à 3 personen. Voorbeeld uit de demo: € 1.130 is 1 dag.
- Timmerwerk na stuken: alleen werk dat pas na het stuken of na de montage van de keuken kan
  (koof dichtzetten, rooster plaatsen, lijsten, afwerking). In de offerte staat dan vaak "na montage keuken".

### 5.4 Stukwerk
- Niet op bedrag rekenen: stukwerk is duur per dag. Eén persoon, 8 uur per dag.
- De wand: 1 dag.
- Komt er plafond, spachtelputz of meer m² bij: samen 1 extra dag.
- Meer dan 2 dagen alleen bij veel grotere oppervlakken. Meld dat dan bij Twijfel.

### 5.5 Afmonteren schakelmateriaal
- Alleen als er stukwerk is én schakelmateriaal in de offerte staat (raam, wandcontactdoos, dimmer,
  schakelaar): die gaan er na het stuken weer op. 1 à 2 personen × 2 à 4 uur, na het stukwerk.
- Staan er alleen spots, of is er geen stukwerk: die regels gaan mee met Leidingwerk en elektra voor stuken.

### 5.6 Overige disciplines
- Egalisatie (5.x) valt vaak onder timmerwerk. Staat er timmerwerk met een bedrag in de offerte, zet de
  regel dan bij Timmerwerk voor stuken en tel het bedrag mee. Anders: een eigen rij Egalisatie /
  vloerafwerking, 1 persoon × 4 uur per ongeveer 10 m².
- Wand tegelen (10.x): 1 persoon × 8 uur voor ongeveer 4 à 6 m².
- Latexen / schilderen (9.x): 1 persoon × 8 uur per ongeveer 20 à 35 m².
- Leidingwerk en elektra na stuken: alleen als de offerte expliciet werk noemt dat na het stuken moet.

### 5.7 Geen vuistregel van toepassing
Reken met ongeveer € 1.000 (excl. btw) per persoon per dag en zet in de kolom Twijfel dat het een schatting is.
Staat er geen bedrag bij een regel uit de keukenorder, schat de tijd dan op basis van gelijksoortige regels.

### 5.8 Afronden
Rond af op hele of halve dagen en kijk daarbij naar het werk, niet alleen naar het bedrag.

## 6. Niet in het voorstel

- Starttijd: standaard 08:00, soms in overleg met de klant eerder.
- Filiaal en adviseur horen in de omschrijving van de werkbon, maar staan niet in de offerte. Die vult de
  planner zelf aan.
- Offertes via de keukenwinkel (80 à 90%) volgen deze regels. Particuliere klussen gaan op dezelfde manier,
  maar zijn rommeliger en moeten altijd worden nagekeken.

## 7. Open vragen aan de planning

1. Wanneer komt er een aparte werkbon Afmonteren schakelmateriaal, en wanneer doet de leidingwerker dat?
2. Wanneer kies je "na stuken" in plaats van "voor stuken", ook als er geen stukwerk in de klus zit?
3. Wordt een gesloopte muur (2.x) demontage of timmerwerk? In de export deed de timmerman het één keer.
4. Hoeveel dagen stukwerk bij plafond of spachtelputz, en doet de stukadoor dan ook het sausen?
