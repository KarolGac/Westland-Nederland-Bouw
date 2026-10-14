"""Kennisbestanden voor de eigen GPT (en de systeemprompt van de API-test).

Gebruik:
    python src/maak_kennisbestanden.py data/verwerkt/projecten data/verwerkt/kennis <projectcode> [<projectcode> ...]

De projectcodes zijn de voorbeeldklussen. Die tellen niet mee in de test (zie src/test_openai.py).
Schrijft in de uitmap:
- artikelcodes.md       elke artikelcode uit de export met omschrijving, eenheid en discipline (geen prijzen)
- voorbeeldklussen.md   per voorbeeld de offerte als invoer en de echte werkbonnen in de vaste uitvoer
- voorbeeldklussen.txt  de gebruikte projectcodes

Optioneel in de uitmap: uitsluiten.txt met per regel "werkbon:<ordernr>" (werkbon weglaten, bijvoorbeeld
schadeherstel dat niet uit de offerte komt) of "tekst:<stukje>" (werkbonregels met dit stukje weglaten,
bijvoorbeeld namen). Dat bestand blijft lokaal en komt niet in git.
"""
import collections
import json
import re
import sys
from pathlib import Path

from werkbonvoorstel import ARTIKELCODE, KOLOMMEN, getal, project_als_invoer, werkbonnen_als_rijen

VAKGEBIED = {
    1: ("Afplakken / beschermen", "Demontage"),
    2: ("Demontage", "Demontage"),
    3: ("Leidingwerk en elektra", "Leidingwerk en elektra voor stuken"),
    4: ("Timmerwerk", "Timmerwerk voor stuken"),
    5: ("Egalisatie", "Egalisatie / vloerafwerking"),
    6: ("Stukwerk", "Stukwerk"),
    7: ("Schakelmateriaal en spots", "Afmonteren schakelmateriaal (zonder stukwerk: bij leidingwerk)"),
    9: ("Schilderwerk", "Latexen / schilderen"),
    10: ("Tegelwerk", "Wand tegelen"),
}

# Vanaf deze regels staat er informatie van de keukenleverancier in de werkbon (leverweek, showroom,
# inmeetdatum). Die komt niet uit de offerte, dus de GPT kan het niet weten.
KNIP = re.compile(r"^\s*(leverweek|showroom|inmeet|werkzaamheden( aangekocht)?\s*:)", re.I)
TELEFOON = re.compile(r"(\+31|0031|\b0)[\s-]?[1-9](?:[\s-]?\d){8}\b")
EMAIL = re.compile(r"\S+@\S+")


def artikelcodes(projecten):
    codes = {}
    for p in projecten:
        for o in p["offertes"]:
            for r in o["regels"]:
                code = r["artikelcode"]
                if code and ARTIKELCODE.match(code) and r["omschrijving"]:
                    codes.setdefault(code, collections.Counter())[(r["omschrijving"].strip(), r["eenheid"])] += 1
    md = ["# Artikelcodes en disciplines", "",
          "Alle artikelcodes uit de OutSmart-export van 2 oktober 2026. Het eerste getal van de code geeft het "
          "vakgebied. Uitzondering: 1.0 Opname meerwerk wordt nooit een werkbon. Nog te bevestigen door West Nederland Bouw.",
          "", "| Vakgebied | Discipline in OutSmart |", "|---|---|"]
    md += [f"| {k}.x {v[0]} | {v[1]} |" for k, v in VAKGEBIED.items()]
    md += ["", "| Code | Omschrijving | Eenheid | Discipline |", "|---|---|---|---|"]
    for code in sorted(codes, key=lambda c: [int(x) for x in c.split(".")]):
        (omschrijving, eenheid), _ = codes[code].most_common(1)[0]
        hoofd = int(code.split(".")[0])
        discipline = "geen werkbon" if code == "1.0" else VAKGEBIED.get(hoofd, ("", "onbekend"))[1]
        md.append(f"| {code} | {omschrijving} | {eenheid} | {discipline} |")
    return "\n".join(md) + "\n", len(codes)


def lees_uitsluiten(pad):
    werkbonnen, teksten = set(), []
    if pad.exists():
        for regel in pad.read_text(encoding="utf-8").splitlines():
            soort, _, waarde = regel.partition(":")
            if soort.strip() == "werkbon":
                werkbonnen.add(waarde.strip())
            elif soort.strip() == "tekst" and waarde.strip():
                teksten.append(waarde.strip().lower())
    return werkbonnen, teksten


def schone_omschrijving(tekst, weglaten):
    regels = []
    for regel in tekst.splitlines():
        if KNIP.match(regel):
            break
        if any(w in regel.lower() for w in weglaten):
            continue
        regel = EMAIL.sub("", TELEFOON.sub("", regel)).strip()
        if regel:
            regels.append(regel)
    return "; ".join(regels).replace("|", "/")


def woorden(tekst):
    return {w for w in re.findall(r"[a-z0-9]+", tekst.lower()) if len(w) > 3}


def gebruikte_regels(werkbontekst, project):
    """Artikelcodes van offerteregels die (grotendeels) in de werkbontekst terugkomen."""
    in_werkbon = woorden(werkbontekst)
    gevonden = []
    for o in project["offertes"]:
        for r in o["regels"]:
            titel = woorden(r["omschrijving"])
            if titel and len(titel & in_werkbon) / len(titel) >= 0.6:
                code = r["artikelcode"] if r["artikelcode"] and ARTIKELCODE.match(r["artikelcode"]) else r["omschrijving"][:30]
                if code not in gevonden:
                    gevonden.append(code)
    return ", ".join(gevonden)


def voorbeeldklus(nr, project, werkbonnen_weg, weglaten):
    werkbonnen = [w for w in project["werkbonnen"] if w["ordernr"] not in werkbonnen_weg]
    md = [f"## Voorbeeld {nr}", "", "### Offerte (invoer)", "", "```", project_als_invoer(project), "```", "",
          "### Werkbonnen zoals de planner ze maakte", "",
          "| " + " | ".join(KOLOMMEN) + " |", "|" + "---|" * len(KOLOMMEN)]
    for i, r in enumerate(werkbonnen_als_rijen(werkbonnen), 1):
        omschrijving = schone_omschrijving(r["werkbonnen"][0]["omschrijving"], weglaten)
        md.append(f"| {i} | {r['discipline']} | {r['personen']} | {getal(r['uren'])} | {omschrijving} | "
                  f"{gebruikte_regels(omschrijving, project)} |  |")
    return "\n".join(md)


def main(projectmap, uitmap, *voorbeelden):
    uit = Path(uitmap)
    uit.mkdir(parents=True, exist_ok=True)
    projecten = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(projectmap).glob("*.json"))]

    tekst, n = artikelcodes(projecten)
    (uit / "artikelcodes.md").write_text(tekst, encoding="utf-8")
    print(f"artikelcodes.md: {n} codes")

    if not voorbeelden:
        sys.exit("Geef de projectcodes van de voorbeeldklussen mee.")
    per_code = {p["projectcode"]: p for p in projecten}
    onbekend = [c for c in voorbeelden if c not in per_code]
    if onbekend:
        sys.exit(f"Onbekende projectcode(s): {', '.join(onbekend)}")
    werkbonnen_weg, weglaten = lees_uitsluiten(uit / "uitsluiten.txt")
    md = ["# Voorbeeldklussen", "",
          "Echte offertes van West Nederland Bouw met de werkbonnen die de planner ervoor maakte. "
          "Klantgegevens staan er niet in. De tabel staat in de vaste uitvoer: één rij per discipline per werkdag. "
          "Werk dat niet uit de offerte komt (bijvoorbeeld schadeherstel) is weggelaten."]
    for i, code in enumerate(voorbeelden, 1):
        md += ["", voorbeeldklus(i, per_code[code], werkbonnen_weg, weglaten)]
    (uit / "voorbeeldklussen.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (uit / "voorbeeldklussen.txt").write_text("\n".join(voorbeelden) + "\n", encoding="utf-8")
    print(f"voorbeeldklussen.md: {len(voorbeelden)} klussen ({len(werkbonnen_weg)} werkbonnen en {len(weglaten)} tekststukjes uitgesloten)")


if __name__ == "__main__":
    main(*sys.argv[1:])
