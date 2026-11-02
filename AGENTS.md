# Instructies voor agents in deze repo

AI Werklab (De Haagse Hogeschool) voor West Nederland Bouw: een geaccepteerde offerte omzetten in een
voorstel voor werkbonnen. Eindproduct is een skill in ChatGPT Business (geen eigen GPT: OpenAI stopt
daarmee in december 2026); we testen via de OpenAI API.
Huidige prompt: `prompts/v3/README.md`. Vaste uitvoer: `prompts/v2/README.md`.

## Privacy en de openbare repo
- De GitHub-repo is **openbaar**. Commit nooit klantdata: geen offertes, werkbonnen, namen, adressen,
  projectcodes of exports. `data/` en `docs/` staan in `.gitignore`; houd dat zo.
- Klantdata staat alleen in `data/` (lokaal) en in de SharePoint-teammap.
- `data/sharepoint_workspace` is een tweerichtingskoppeling naar de SharePoint-teammap. Wat je daar
  wijzigt, wijzigt in SharePoint. Lees eerst `data/sharepoint_workspace/AGENTS.md`. Nooit iets uit `raw/`
  wijzigen, nooit de map in git zetten.
- API-sleutels alleen in `.env` (staat in `.gitignore`). Voorbeeld: `.env.example`.

## Waar staat wat
| Plek | Inhoud |
|---|---|
| `src/` | Scripts (Python 3.11+, alleen standaardbibliotheek) |
| `prompts/` | Prompts per versie; `v3/` is de huidige |
| `tests/` | Unittests met eigen kleine voorbeelden, geen klantdata |
| `data/ruw/` | Leveringen van de klant (niet wijzigen) |
| `data/verwerkt/` | Gemaakt door scripts: projecten, antwoordblad, kennisbestanden, tekst uit de offerte-PDF's |
| `data/skill/` | De skill om te uploaden (bevat voorbeeldklussen, dus niet in git) |
| `data/resultaten/` | Uitkomsten van API-runs |
| `docs/` | Eigen documenten (privé) |

## Werkwijze
- Kleine, gerichte wijzigingen in de stijl van de bestaande code: Nederlandse namen, korte docstrings.
- Paden als argument, zodat tests niet van de werkmap afhangen.
- Na een wijziging: `python -m unittest discover -s tests` en het betrokken script draaien.
- Teksten voor de klant of school: geen emoji's, gewone zinnen, korte lijstjes alleen waar het helpt.

## Commando's
```
python src/sql_dump_naar_projecten.py data/ruw/<levering>/WNB_offertes_werkbonnen_taalmodel.sql data/verwerkt/projecten
python src/maak_antwoordblad.py data/verwerkt/projecten data/verwerkt
python src/maak_kennisbestanden.py data/verwerkt/projecten data/verwerkt/kennis <projectcodes voorbeeldklussen>
python src/maak_skill.py prompts/v3 data/verwerkt/kennis data/skill
python src/offerte_pdf_naar_tekst.py data/ruw/<levering>/WNB_offertes_werkbonnen_taalmodel.sql data/ruw/<datum>_offerte_pdfs data/verwerkt/pdf_tekst
python src/test_openai.py --droog
python src/evalueer.py data/resultaten/<run-map>
python -m unittest discover -s tests
```
