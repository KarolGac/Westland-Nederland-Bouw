"""Skill voor ChatGPT Business: de prompt en de kennisbestanden als map en als zip om te uploaden.

Gebruik:
    python src/maak_skill.py prompts/v3 data/verwerkt/kennis data/skill

Schrijft in de uitmap:
- werkbonvoorstel/SKILL.md       naam en beschrijving, daaronder instructies.md
- werkbonvoorstel/references/    beslisregels.md, artikelcodes.md en voorbeeldklussen.md
- werkbonvoorstel.zip            dezelfde map, om te uploaden in ChatGPT (Skills > Create > Upload)

De voorbeeldklussen bevatten echte offertes: de uitmap hoort in data/ (niet in git). instructies.md en
beslisregels.md blijven zoals getest. Alleen het stuk "# Kennisbestanden" wordt vervangen, omdat een skill
de bestanden pas leest als de instructies dat zeggen. In de API-test staan ze helemaal in de systeemprompt.
"""
import json
import re
import sys
import zipfile
from pathlib import Path

NAAM = "werkbonvoorstel"
BESCHRIJVING = (
    "Maakt van een geaccepteerde offerte van West Nederland Bouw (een PDF uit OutSmart of geplakte tekst) een "
    "voorstel voor de werkbonnen als tabel, met discipline, personen, uren per persoon en omschrijving. Gebruik "
    "deze skill altijd als de planner een offerte-PDF geeft, ook zonder verdere vraag, of om een werkbonvoorstel vraagt."
)
KENNIS = """# Kennisbestanden
Lees bij elke offerte eerst deze drie bestanden helemaal. Ze gaan voor je eigen inschatting.
- references/beslisregels.md: alle regels met uitleg.
- references/artikelcodes.md: welke artikelcode bij welke discipline hoort.
- references/voorbeeldklussen.md: echte offertes met de werkbonnen die de planner maakte. Gebruik ze als maatstaf voor personen en uren.

"""
BESTANDEN = [("prompts", "beslisregels.md"), ("kennis", "artikelcodes.md"), ("kennis", "voorbeeldklussen.md")]


def skill_tekst(instructies):
    """instructies.md met naam en beschrijving erboven en het stuk over kennisbestanden voor een skill."""
    delen = re.split(r"(?m)^(?=# )", instructies)
    if not any(d.startswith("# Kennisbestanden") for d in delen):
        raise ValueError("instructies.md heeft geen kop '# Kennisbestanden'")
    delen = [KENNIS if d.startswith("# Kennisbestanden") else d for d in delen]
    kop = f"---\nname: {NAAM}\ndescription: {json.dumps(BESCHRIJVING, ensure_ascii=False)}\n---\n\n"
    return kop + "".join(delen)


def maak_skill(promptmap, kennismap, uitmap):
    bron = {"prompts": Path(promptmap), "kennis": Path(kennismap)}
    uitmap = Path(uitmap)
    map_ = uitmap / NAAM
    (map_ / "references").mkdir(parents=True, exist_ok=True)
    instructies = (bron["prompts"] / "instructies.md").read_text(encoding="utf-8")
    (map_ / "SKILL.md").write_text(skill_tekst(instructies), encoding="utf-8")
    for waar, naam in BESTANDEN:
        pad = bron[waar] / naam
        if not pad.exists():
            sys.exit(f"{pad} ontbreekt. Maak de kennisbestanden eerst met src/maak_kennisbestanden.py.")
        (map_ / "references" / naam).write_text(pad.read_text(encoding="utf-8"), encoding="utf-8")
    zip_ = uitmap / f"{NAAM}.zip"
    with zipfile.ZipFile(zip_, "w", zipfile.ZIP_DEFLATED) as z:
        for pad in sorted(map_.rglob("*")):
            if pad.is_file():
                z.write(pad, pad.relative_to(uitmap).as_posix())
    return zip_


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    print(f"Skill -> {maak_skill(*sys.argv[1:])}")
