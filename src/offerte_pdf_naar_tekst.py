"""Offerte-PDF's uit OutSmart ophalen en als tekst zonder klantgegevens wegschrijven.

Gebruik:
    python src/offerte_pdf_naar_tekst.py <dump.sql> data/ruw/<datum>_offerte_pdfs data/verwerkt/pdf_tekst [--projecten data/verwerkt/projecten]

De planner geeft straks een PDF aan de skill. Daar staan andere dingen in dan in de export: geen
artikelcodes en geen bedrag bij regels "(al in keukenorder)". Met deze tekst testen we dat via de API:
    python src/test_openai.py --prompts prompts/v3 --invoer data/verwerkt/pdf_tekst

Per project één <projectcode>.txt met alle offertes. Een PDF die al in de pdf-map staat wordt niet opnieuw
opgehaald. De kop van de offerte (klant en adres) valt weg. Namen, adressen, telefoon en e-mail uit de export
worden ook in de rest van de tekst weggehaald, zodat ze niet naar het taalmodel gaan.
Nodig: pdftotext (poppler). PDF's en tekst bevatten klantdata: alleen in data/, nooit in git.
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

from sql_dump_naar_projecten import lees_dump

WEG = "[weg]"
PATRONEN = [
    re.compile(r"\S+@\S+"),
    re.compile(r"\b\d{4}\s?[A-Z]{2}\b"),
    re.compile(r"(\+31|0031|\b0)[\s-]?[1-9](?:[\s-]?\d){8}\b"),
    re.compile(r"\bNL\d{2}[A-Z]{4}\d{10}\b"),
]
KLANTVELDEN = ["Name", "Street", "City", "ZIP", "Email", "ContactPerson", "Phone"]
# De regels beginnen onder de kolomkop van de offerte; daarboven staan klant en adres.
KOLOMKOP = re.compile(r"(?i)^\s*(omschrijving|activiteit|artikel|product)\b.*\b(aantal|bedrag|prijs|totaal)\b")
EERSTE_REGEL = re.compile(r"(?i)opname meerwerk|afplakken van|demonteren oude|leidingwerk basis|het stuken van|maatwerk interieurbouw")


def klantgegevens(tabellen):
    """{projectcode: tekstjes die uit de offerte weg moeten}"""
    per_project = {}

    def voeg_toe(code, waarde):
        if not isinstance(waarde, str):
            return
        waarde = " ".join(waarde.split())
        if len(waarde) < 3:
            return
        per_project.setdefault(code, set()).add(waarde)
        for woord in waarde.split():
            # losse achternaam of plaats; korte woorden als "de" en "van" blijven staan
            if len(woord) >= 4 and woord[0].isupper():
                per_project[code].add(woord.strip(".,"))

    for w in tabellen["workorders"]:
        j = json.loads(w["raw_json"])
        code = w["project_code"] or w["target_project_code"]
        for veld in KLANTVELDEN:
            voeg_toe(code, j.get(f"Customer{veld}"))
            voeg_toe(code, j.get(f"Customer{veld}Invoice"))
    for q in tabellen["project_quotes"]:
        j = json.loads(q["raw_json"])
        voeg_toe(q["project_code"], q.get("end_customer"))
        voeg_toe(q["project_code"], q.get("city"))
        voeg_toe(q["project_code"], j.get("quo_quotation_debtor_name"))
        voeg_toe(q["project_code"], j.get("quo_quotation_debtor_email"))
        voeg_toe(q["project_code"], j.get("quo_accepted_by"))
    return per_project


def schoon(tekst, weg):
    """Knipt de kop weg en haalt klantgegevens uit de rest."""
    regels = tekst.splitlines()
    start = next((i for i, r in enumerate(regels) if KOLOMKOP.search(r)), None)
    if start is None:
        start = next((i for i, r in enumerate(regels) if EERSTE_REGEL.search(r)), 0)
    uit = "\n".join(regels[start:])
    # Na deze zin volgt alleen nog de ondertekening met de naam van de klant.
    einde = re.search(r"(?i)let op: door ondertekening", uit)
    if einde:
        uit = uit[:einde.start()]
    for w in sorted(weg, key=len, reverse=True):
        uit = re.sub(rf"(?i)(?<!\w){re.escape(w)}(?!\w)", WEG, uit)
    for patroon in PATRONEN:
        uit = patroon.sub(WEG, uit)
    return re.sub(r"\n\s*\n+", "\n\n", uit).strip()


def haal_op(url, pad):
    if pad.exists():
        return
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"Geen PDF voor {pad.name}: is de link verlopen of is inloggen nodig?")
    pad.write_bytes(data)


def pdf_als_tekst(pad):
    return subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(pad), "-"], check=True, capture_output=True).stdout.decode("utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dump")
    ap.add_argument("pdfmap", type=Path)
    ap.add_argument("uitmap", type=Path)
    ap.add_argument("--projecten", default=Path("data/verwerkt/projecten"), type=Path)
    args = ap.parse_args()

    tabellen = lees_dump(args.dump)
    links = {q["quote_number"]: json.loads(q["raw_json"]).get("pdf") for q in tabellen["project_quotes"]}
    weg = klantgegevens(tabellen)
    args.pdfmap.mkdir(parents=True, exist_ok=True)
    args.uitmap.mkdir(parents=True, exist_ok=True)
    for pad in sorted(args.projecten.glob("*.json")):
        project = json.loads(pad.read_text(encoding="utf-8"))
        offertes = sorted(project["offertes"], key=lambda o: o.get("geaccepteerd") or "")
        delen = []
        for o in offertes:
            nummer = o["offertenummer"]
            if not links.get(nummer):
                sys.exit(f"Geen PDF-link voor offerte {nummer}")
            pdf = args.pdfmap / f"{nummer}.pdf"
            haal_op(links[nummer], pdf)
            delen.append(f"Offerte {nummer}\n\n{schoon(pdf_als_tekst(pdf), weg.get(project['projectcode'], set()))}")
        if len(delen) > 1:
            delen.insert(0, f"Dit project heeft {len(delen)} geaccepteerde offertes. Maak één voorstel voor alle offertes samen.")
        (args.uitmap / f"{project['projectcode']}.txt").write_text("\n\n".join(delen) + "\n", encoding="utf-8")
        print(f"{project['projectcode']}: {len(offertes)} PDF")


if __name__ == "__main__":
    main()
