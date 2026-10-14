# Westland Nederland Bouw

AI Werklab (De Haagse Hogeschool): een geaccepteerde offerte omzetten naar een controleerbaar voorstel
voor werkbonnen. Het eindproduct is een eigen GPT in ChatGPT Business; de prompt testen we via de
OpenAI API. Uitleg over prompt v2 en de vaste uitvoer staat in [prompts/v2/README.md](prompts/v2/README.md).

## Mappen

```
src/          scripts                                         in GitHub
prompts/      prompts met versienummer (v2 is de huidige)     in GitHub
tests/        unittests, zonder klantdata                     in GitHub
data/         alles wat van de klant komt                     privé
  ruw/          leveringen zoals ontvangen, per datum
  verwerkt/     door scripts gemaakt: projecten, antwoordblad, kennisbestanden GPT
  resultaten/   uitkomsten van API-runs
  sharepoint_workspace/   koppeling naar de SharePoint-teammap (raw, reference, knowledge)
docs/         eigen documenten                                privé
```

`data/` en `docs/` bevatten klant- of persoonsgegevens en staan in `.gitignore`.
Gedeelde stukken staan in de SharePoint-teammap. Uitleg over de data staat in `data/README.md` (lokaal).
Afspraken voor agents: [AGENTS.md](AGENTS.md).

## Stappen

```
# 1. SQL-export omzetten naar één JSON per project
python src/sql_dump_naar_projecten.py data/ruw/<levering>/WNB_offertes_werkbonnen_taalmodel.sql data/verwerkt/projecten

# 2. Antwoordblad: wat de planner echt heeft ingepland
python src/maak_antwoordblad.py data/verwerkt/projecten data/verwerkt

# 3. Kennisbestanden voor de GPT (artikelcodes, voorbeeldklussen)
python src/maak_kennisbestanden.py data/verwerkt/projecten data/verwerkt/kennis <projectcodes voorbeeldklussen>

# 4. Test via de OpenAI API (key in .env, zie .env.example)
python src/test_openai.py --droog
python src/test_openai.py

# Tests
python -m unittest discover -s tests
```
