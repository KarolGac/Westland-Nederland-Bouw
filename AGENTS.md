# Instructies voor agents in deze repo

AI Werklab (De Haagse Hogeschool) voor West Nederland Bouw: een geaccepteerde offerte omzetten in een
voorstel voor werkbonnen. Eindproduct is een eigen GPT in ChatGPT Business; we testen via de OpenAI API.
Uitleg over prompt v2 en de vaste uitvoer: `prompts/v2/README.md`.

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
| `prompts/` | Prompts per versie; `v2/` is de huidige |
| `tests/` | Unittests met eigen kleine voorbeelden, geen klantdata |
| `data/ruw/` | Leveringen van de klant (niet wijzigen) |
| `data/verwerkt/` | Gemaakt door scripts: projecten, antwoordblad, kennisbestanden |
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
python src/test_openai.py --droog
python -m unittest discover -s tests
```
