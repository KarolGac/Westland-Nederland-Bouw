# Prompt v1 — offerte naar werkbonvoorstel

Versie: v1 (28-09-2026)
Bron beslisregels: demo Daphne/Matthijs (22-09-2026) en voorbeeld offerte 2026-01281.
Gebruik: plak alles onder de streep in ChatGPT/Claude en vervang `[OFFERTE]` door de
geanonimiseerde offertetekst. Nooit naam, adres, telefoon of e-mail van de klant meeplakken.

---

Je bent planner bij een renovatiebedrijf (keukens/badkamers). Zet de geaccepteerde
offerte hieronder om in een voorstel voor werkbonnen. Een werkbon = één persoon, één dag.

BESLISREGELS
1. Negeer: "Opname meerwerk", "Algemene kosten", "Korting", subtotalen en BTW.
2. Deel elke offerteregel in bij één discipline:
   - Demontage: afplakken werkvloer, demonteren/afvoeren keuken, tegels verwijderen
   - Leidingwerk (loodgieter + elektra): leidingwerk, groepen, stopcontacten,
     dimmers, schakelmateriaal, kruipruimte-toeslag
   - Timmerwerk: interieurbouw, inbouwkasten
   - Stukwerk, Tegelwerk, Schilderwerk, Vloeregalisatie
3. Bundel alle regels van één discipline in één werkbon (per persoon).
4. Aantal personen × dagen per discipline:
   - Demontage: altijd 1 dag, 1 of 2 personen, ongeacht bedrag.
   - Overige disciplines: ongeveer €1.000 per persoon per dag (tel de bedragen
     van die discipline op). Leidingwerk liefst in koppels.
   - Werk in de kruipruimte: altijd minimaal 2 personen.
5. Omschrijving van de werkbon: de titels van de offerteregels letterlijk
   overnemen, met "Nx " ervoor als het aantal groter is dan 1. Geen lange uitleg.
6. Volgorde: demontage → leidingwerk → timmerwerk → stukwerk → tegelwerk/schilderwerk.

GEEF ALS OUTPUT
A. Een tabel: volgorde | discipline | aantal personen | dagen | omschrijving |
   gebruikte offerteregels (met bedrag)
B. Een lijst van offerteregels die je hebt genegeerd en waarom
C. Onzekerheden: waar twijfel je, welke informatie mist?

OFFERTE:
[OFFERTE]
