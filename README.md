# Westland Nederland Bouw

AI Werklab (De Haagse Hogeschool): een geaccepteerde offerte omzetten naar een controleerbaar voorstel
voor werkbonnen. Het eindproduct is een skill in ChatGPT Business (geen eigen GPT: OpenAI stopt daarmee
in december 2026); de prompt testen we via de OpenAI API. De huidige prompt staat in
[prompts/v3/README.md](prompts/v3/README.md), de vaste uitvoer in [prompts/v2/README.md](prompts/v2/README.md).

## Mappen

```
src/          scripts                                         in GitHub
prompts/      prompts met versienummer (v3 is de huidige)     in GitHub
tests/        unittests, zonder klantdata                     in GitHub
data/         alles wat van de klant komt                     privé
  ruw/          leveringen zoals ontvangen, per datum
  verwerkt/     door scripts gemaakt: projecten, antwoordblad, kennisbestanden
  skill/        de skill om te uploaden (bevat voorbeeldklussen)
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

# 3. Kennisbestanden (artikelcodes, voorbeeldklussen) en de skill als zip
python src/maak_kennisbestanden.py data/verwerkt/projecten data/verwerkt/kennis <projectcodes voorbeeldklussen>
python src/maak_skill.py prompts/v3 data/verwerkt/kennis data/skill

# 4. Test via de OpenAI API (key in .env, zie .env.example), op de export of op de tekst uit de PDF's
python src/test_openai.py --droog
python src/test_openai.py
python src/offerte_pdf_naar_tekst.py data/ruw/<levering>/WNB_offertes_werkbonnen_taalmodel.sql data/ruw/<datum>_offerte_pdfs data/verwerkt/pdf_tekst
python src/test_openai.py --invoer data/verwerkt/pdf_tekst

# 5. Evaluatie: voorstellen naast de echte werkbonnen leggen
python src/evalueer.py data/resultaten/<run-map>

# Tests
python -m unittest discover -s tests
```
