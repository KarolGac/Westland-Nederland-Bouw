# Prompt v3: regels van de planning, PDF als invoer

Versie 3 (02-11-2026), de huidige. Zelfde uitvoer en bestanden als v2 (zie `../v2/README.md`). Nieuw: de
regels komen uit de controlelijst die de planning heeft ingevuld, en de invoer is meestal een PDF.

## Wat er anders is dan v2

| Onderwerp | v2 | v3 | Bron |
|---|---|---|---|
| Invoer | Geplakte tekst of PDF | Meestal PDF, zonder artikelcodes; meteen een voorstel | Wens klant |
| Leidingwerk | Basis = 3 personen × 8 uur, plus 4 à 8 persoonuren per extra regel | ± € 1.000 per persoon per dag, toeslagen niet of deels meetellen | Planning (R7, afronden) |
| Leidingwerk, personen | Liefst 2 of meer | Bij voorkeur koppels van 2 | Planning (R8) |
| Demontage | 2 personen × 4 uur, met wandtegels 4 à 8 uur | Vaak een halve dag, ook met wandtegels | Planning (R2, R6) |
| Egalisatie | Eigen discipline | Vaak onder timmerwerk | Planning (R5) |
| Timmerwerk | Voorzetwanden, interieurbouw | Ook inbouwkasten, koof, koplatten | Planning (R4) |
| Volgorde | Vast | Vast, met uitzonderingen in de droogtijd van het stukwerk | Planning (R13) |
| Houtrot | Niet genoemd | Uitbesteed aan de schilder | Planning |
| Stukwerk | Plafond of meer m²: een extra dag | Niet op bedrag; plafond, spachtelputz of meer m² samen 1 extra dag | Export |
| Afmonteren | Altijd als er stukwerk is | Alleen met stukwerk én schakelmateriaal; alleen spots gaan mee met leidingwerk | Export |
| Regel van € 0 | Niet genoemd | Geen eigen rij of discipline | Export |

## Nog te bevestigen door de planning

Deze regels komen niet letterlijk van de planning:

- Egalisatie gaat mee met timmerwerk als er timmerwerk met een bedrag in de offerte staat, anders een eigen rij.
- "Leidingwerk basis keuken" is altijd minstens 2 personen × 8 uur, ook als de prijs lager is omdat hij al
  in de keukenorder zit.
- Meer leidingwerk is een extra dag, niet meer personen.
- De drie regels uit de export in de tabel hierboven.

## Testen

```
python src/test_openai.py                                  # tekst uit de export
python src/offerte_pdf_naar_tekst.py <dump.sql> data/ruw/<datum>_offerte_pdfs data/verwerkt/pdf_tekst
python src/test_openai.py --invoer data/verwerkt/pdf_tekst # tekst uit de PDF's, zonder klantgegevens
python src/evalueer.py data/resultaten/<run-map>
```

## Uitslag (02-11-2026, 11 klussen × 3 runs, GPT-6.1 Sol)

| | v2 | v3, tekst | v3, PDF |
|---|---|---|---|
| Precies goed | 18% | 18% | 18% |
| 1 à 2 aanpassingen | 55% | 55% | 55% |
| 3 of meer aanpassingen | 27% | 27% | 27% |
| Aanpassingen in totaal | 72 | 57 | 56 |
| Persoonuren in totaal, t.o.v. de planner | +26% | -6% | -5% |
| Goed of bijna goed, gemeten tegen vooraf tot eind | 73% | 82% | 85% |
| Precies goed, gemeten tegen vooraf tot eind | 18% | 36% | 36% |

"Vooraf tot eind": goed is alles tussen wat vóór de eerste werkdag was ingepland en wat er aan het eind
stond. Dat is een milde maat en een bovengrens, geen eerlijke score. 35% van de geboekte uren is pas tijdens
de klus aangemaakt, maar twee derde van die uren staat op een bon die een offerteregel noemt. Dat werk staat
dus wel in de offerte en is later ingepland of liep uit. Alleen de rest kan werk zijn dat erbij kwam.

## Beperkingen

- De regels uit de export en de planning zijn bekeken op dezelfde klussen als de test, en de regels uit de
  export zijn na de testuitslag van v2 aangescherpt. De uitkomst is dus te positief. Een eerlijke controle
  kan pas op offertes die het model nog niet heeft gezien.
- De PDF-test gebruikt de tekst uit de PDF, zonder kop en ondertekening. Het uploaden van een PDF in ChatGPT
  zelf is daarmee nog niet getest.
- De runs per klus lijken sterk op elkaar: de 33 antwoorden zijn in de praktijk 11 meetpunten.
