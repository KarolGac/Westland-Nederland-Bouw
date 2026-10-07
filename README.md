# Westland Nederland Bouw

AI Werklab (De Haagse Hogeschool): prototype dat een geaccepteerde offerte omzet
naar een controleerbaar voorstel voor werkbonnen.

## Mappen

| Map | Inhoud | In GitHub? |
|---|---|---|
| `src/` | Scripts (zonder klantdata) | Ja |
| `prompts/` | Prompts met versienummer | Ja |
| `docs/plan/` | Plan van aanpak, Trello-plan | Nee |
| `docs/klant/` | Intakeverslag, demo-transcript, uitkomsten sprintreviews | Nee |
| `docs/voorbeelden/` | Echte offertes en werkbonnen per project (PDF) | Nee |
| `docs/proef/` | Technische proef en proefverslag | Nee |
| `data/ruw/` | Exports uit Azure SQL / OutSmart zoals ontvangen | Nee |
| `data/verwerkt/` | Door scripts gemaakte bestanden (per project JSON) | Nee |
| `presentatie/` | Sprintreview-slides en demopagina | Nee |

## Data verwerken

```
python src/sql_dump_naar_projecten.py data/ruw/<levering>/WNB_offertes_werkbonnen_taalmodel.sql data/verwerkt/projecten
```

Alles onder `docs/` en `data/` bevat klant- of persoonsgegevens en staat in
`.gitignore`. Deel die bestanden alleen via een besloten map (Teams/OneDrive).
