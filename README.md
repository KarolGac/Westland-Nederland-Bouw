# Westland Nederland Bouw

AI Werklab (De Haagse Hogeschool): prototype dat een geaccepteerde offerte omzet
naar een controleerbaar voorstel voor werkbonnen.

## Mappen

```
src/          scripts                                         in GitHub
prompts/      prompts met versienummer                        in GitHub
data/         alles wat van de klant komt                     privé
  ruw/          leveringen zoals ontvangen, per datum
  verwerkt/     door scripts gemaakt (één JSON per project)
docs/         eigen documenten                                privé
  plan/         plan van aanpak, Trello-plan, kostenoverzicht
  klant/        verslagen van gesprekken met de klant, per datum
  proeven/      proeven met het taalmodel, per datum
  presentaties/ slides per sprintreview
  archief/      oude versies
```

`data/` en `docs/` bevatten klant- of persoonsgegevens en staan in `.gitignore`.
Deel die bestanden alleen via een besloten map (Teams/OneDrive). Uitleg over de data
staat in `data/README.md` (lokaal).

## Data verwerken

```
python src/sql_dump_naar_projecten.py data/ruw/<levering>/WNB_offertes_werkbonnen_taalmodel.sql data/verwerkt/projecten
```
