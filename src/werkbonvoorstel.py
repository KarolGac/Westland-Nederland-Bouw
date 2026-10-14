"""Gedeelde onderdelen voor prompt v2: vaste disciplines, offerte als tekst, werkbonnen als rijen
en het inlezen van de tabel die het taalmodel teruggeeft (de vaste uitvoer, zie prompts/v2/README.md).
"""
import collections
import html
import re

# TypeOfWork in OutSmart, in de volgorde waarin het werk meestal gebeurt.
# Opname, Service en Reservering komen niet uit de offerte en tellen niet mee.
DISCIPLINES = [
    "Demontage",
    "Leidingwerk en elektra voor stuken",
    "Timmerwerk voor stuken",
    "Stukwerk",
    "Afmonteren schakelmateriaal",
    "Leidingwerk en elektra na stuken",
    "Timmerwerk na stuken",
    "Egalisatie / vloerafwerking",
    "Wand tegelen",
    "Latexen / schilderen",
]

KOLOMMEN = ["Nr", "Discipline", "Personen", "Uren per persoon", "Omschrijving werkbon", "Offerteregels", "Twijfel"]

ARTIKELCODE = re.compile(r"^\d+(\.\d+)*$")


def bedrag(x):
    """1701.15 -> '€ 1.701,15'"""
    tekst = f"{abs(x):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"€ {'-' if x < 0 else ''}{tekst}"


def getal(x):
    """15.0 -> '15', 1.5 -> '1,5'"""
    return str(int(x)) if float(x).is_integer() else str(x).replace(".", ",")


def schoon(tekst):
    return " ".join(html.unescape(tekst or "").replace("﻿", " ").replace("​", "").split())


def regel_als_tekst(r):
    code = r["artikelcode"] if r["artikelcode"] and ARTIKELCODE.match(r["artikelcode"]) else None
    omschrijving = schoon(r["omschrijving"])
    toelichting = schoon(r["toelichting"])
    if not omschrijving and not r["bedrag_excl"]:
        return f"  {toelichting}" if toelichting else None
    kop = f"- {'[' + code + '] ' if code else ''}{omschrijving or '(geen omschrijving)'}"
    eenheid = f" {r['eenheid']}" if r["eenheid"] else ""
    tekst = f"{kop} | {getal(r['aantal'])}{eenheid} | {bedrag(r['bedrag_excl'])}"
    if toelichting:
        tekst += f"\n  Toelichting: {toelichting}"
    return tekst


def offerte_als_tekst(o):
    """De offerte zoals de planner hem uit OutSmart haalt: regels met code, aantal, bedrag en toelichting.
    Verborgen regels staan niet op de offerte voor de klant en worden overgeslagen."""
    regels = [regel_als_tekst(r) for r in o["regels"] if not r.get("verborgen")]
    datum = "-".join(reversed((o.get("geaccepteerd") or "")[:10].split("-")))
    return "\n".join(
        [f"Offerte {o['offertenummer']} (geaccepteerd {datum})", f"Totaal excl. btw: {bedrag(o['bedrag_excl'])}", ""]
        + [r for r in regels if r]
    )


def project_als_invoer(project):
    """Alle offertes van een project als één invoer (de werkbonnen zijn alleen per project te koppelen)."""
    offertes = sorted(project["offertes"], key=lambda o: o.get("geaccepteerd") or "")
    delen = [offerte_als_tekst(o) for o in offertes]
    if len(delen) > 1:
        delen.insert(0, f"Dit project heeft {len(delen)} geaccepteerde offertes. Maak één voorstel voor alle offertes samen.")
    return "\n\n".join(delen)


def werkbonnen_als_rijen(werkbonnen):
    """Echte werkbonnen (zonder opname, service en reservering) gegroepeerd per dag, discipline en duur.
    Eén rij = zoveel personen die die dag even lang aan die discipline werkten."""
    groepen = collections.defaultdict(list)
    for w in werkbonnen:
        if w["uitvoering"]:
            groepen[(w["datum"], w["discipline"], w["duur_minuten"])].append(w)
    volgorde = {d: i for i, d in enumerate(DISCIPLINES)}
    rijen = []
    for (datum, discipline, minuten), ws in sorted(groepen.items(), key=lambda kv: (kv[0][0], volgorde.get(kv[0][1], 99), -kv[0][2])):
        rijen.append({
            "datum": datum,
            "discipline": discipline,
            "personen": len(ws),
            "uren": minuten / 60,
            "werkbonnen": ws,
        })
    return rijen


def _cel_getal(tekst):
    t = tekst.lower()
    if "hele dag" in t:
        return 8.0
    if "halve dag" in t:
        return 4.0
    m = re.search(r"\d+(?:[.,]\d+)?", t)
    return float(m.group().replace(",", ".")) if m else None


def _cellen(regel):
    return [c.strip() for c in regel.strip().strip("|").split("|")]


def lees_voorstel(tekst):
    """Leest de werkbontabel uit het antwoord van het taalmodel.
    Geeft (rijen, problemen); rijen hebben de sleutels van KOLOMMEN in kleine letters."""
    regels = tekst.splitlines()
    for i, regel in enumerate(regels):
        if regel.strip().startswith("|") and "discipline" in regel.lower():
            kop = [k.lower() for k in _cellen(regel)]
            break
    else:
        return [], ["geen tabel met een kolom Discipline gevonden"]

    ontbrekend = [k for k in ("discipline", "personen", "uren per persoon") if k not in kop]
    if ontbrekend:
        return [], [f"kolom ontbreekt: {', '.join(ontbrekend)}"]

    rijen, problemen = [], []
    for regel in regels[i + 1:]:
        if not regel.strip().startswith("|"):
            break
        cellen = _cellen(regel)
        if all(set(c) <= set("-: ") for c in cellen):
            continue  # scheidingsregel |---|---|
        rij = dict(zip(kop, cellen + [""] * (len(kop) - len(cellen))))
        rij["personen"] = _cel_getal(rij["personen"])
        rij["uren per persoon"] = _cel_getal(rij["uren per persoon"])
        if rij["discipline"] not in DISCIPLINES:
            problemen.append(f"onbekende discipline: {rij['discipline']!r}")
        if rij["personen"] is None or rij["uren per persoon"] is None:
            problemen.append(f"personen of uren niet te lezen in: {regel.strip()}")
        rijen.append(rij)
    if not rijen:
        problemen.append("tabel is leeg")
    return rijen, problemen
