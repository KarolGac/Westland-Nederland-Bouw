"""Zet de SQL-dump uit OutSmart/Azure om naar één compact JSON-bestand per project.

Gebruik:
    python src/sql_dump_naar_projecten.py data/ruw/<levering>/WNB_offertes_werkbonnen_taalmodel.sql data/verwerkt/projecten

Per project: alle offertes met hun regels en alle werkbonnen met discipline (TypeOfWork),
datum, duur en omschrijving. Adres, e-mail, telefoon, handtekening, IP en GPS worden
niet overgenomen. Vrije tekst (omschrijvingen, opmerkingen) kan nog namen of
telefoonnummers bevatten: niet zonder anonimiseerstap naar een taalmodel sturen.
"""
import ast
import collections
import json
import re
import sys
from pathlib import Path

INSERT = re.compile(r"INSERT INTO #(\w+) \(([^)]*)\) VALUES \(")
GEEN_UITVOERING = {"Opname", "Service", "Reservering"}


def lees_waarden(s, i):
    """Leest de waarden van één VALUES (...) vanaf positie i; geeft (waarden, eindpositie)."""
    waarden = []
    while True:
        while s[i] in " \r\n\t,":
            i += 1
        if s[i] == ")":
            return waarden, i + 1
        if s.startswith("NULL", i):
            waarden.append(None)
            i += 4
            continue
        if s[i] == "N" and s[i + 1] == "'":
            i += 1
        if s[i] == "'":
            i += 1
            delen = []
            while True:
                j = s.index("'", i)
                delen.append(s[i:j])
                if s[j + 1:j + 2] == "'":
                    delen.append("'")
                    i = j + 2
                else:
                    i = j + 1
                    break
            waarden.append("".join(delen))
            continue
        m = re.match(r"[-\d.]+", s[i:])
        waarden.append(m.group())
        i += m.end()


def lees_dump(pad):
    tekst = Path(pad).read_text(encoding="utf-8-sig")
    tabellen = collections.defaultdict(list)
    for m in INSERT.finditer(tekst):
        kolommen = [k.strip(" []") for k in m.group(2).split(",")]
        waarden, _ = lees_waarden(tekst, m.end())
        tabellen[m.group(1)].append(dict(zip(kolommen, waarden)))
    return tabellen


def zonder_html(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()


def offerte(rij, doelset):
    j = json.loads(rij["raw_json"])
    return {
        "offertenummer": rij["quote_number"],
        "doelset": doelset,
        "status": rij["status"],
        "geaccepteerd": rij["accepted_at"],
        "bedrag_incl": float(j["quo_amount"]),
        "bedrag_excl": float(j["quo_amount_excl"]),
        "bericht_bij_akkoord": j.get("quo_message_accepted"),
        "regels": [
            {
                "volgorde": int(r["qln_order"]),
                "artikelcode": r["qln_material_code"],
                "omschrijving": r["qln_description"].strip(),
                "toelichting": zonder_html(r.get("qln_note")),
                "aantal": float(r["qln_amount"]),
                "eenheid": r["qln_unit"],
                "bedrag_excl": float(r["qln_total_excl"]),
                # 0 bij regels die niet in het offertebedrag zitten: "Opname meerwerk" (verrekend)
                # en "(al in keukenorder)". Die laatste zijn wel werk dat ingepland wordt.
                "gefactureerd": r.get("qln_billable") == "1",
                "sectie": (r.get("section") or "").strip(),
                "verborgen": r.get("qln_hidden") == "1",
            }
            for r in sorted(j.get("qln_lines", []), key=lambda r: int(r["qln_order"]))
        ],
    }


def formulier_antwoorden(form):
    """Alleen ingevulde tekstvelden uit een OutSmart-formulier (bv. opmerkingen van de opname)."""
    try:
        velden = json.loads(form["Data"]).get("fields", [])
    except (TypeError, ValueError):
        return []
    antwoorden = []
    for veld in velden:
        if veld.get("field_type") != "text":
            continue
        try:
            # field_options is een Python-repr ('True', enkele quotes), geen JSON
            waarde = ast.literal_eval(veld.get("field_options") or "{}").get("value", "")
        except (ValueError, SyntaxError):
            continue
        if isinstance(waarde, str) and waarde.strip():
            antwoorden.append({"vraag": veld.get("label", "").strip(), "antwoord": waarde.strip()})
    return antwoorden


def werkbon(rij):
    j = json.loads(rij["raw_json"])
    return {
        "ordernr": j["OrderNr"],
        "discipline": j["TypeOfWork"],
        "uitvoering": j["TypeOfWork"] not in GEEN_UITVOERING,
        "datum": j["WorkDate"],
        "starttijd": j["WorkTime"],
        "duur_minuten": int(j["WorkDuration"] or 0),
        "status": j["status"],
        "omschrijving": (j.get("WorkDescription") or "").replace("\r\n", "\n").strip(),
        "formulieren": [
            {"naam": f["Name"].strip(), "antwoorden": formulier_antwoorden(f)} for f in j.get("Forms", [])
        ],
    }


def main(bron, doelmap):
    t = lees_dump(bron)
    doel = {r["quote_number"] for r in t["target_quotes"]}
    projecten = collections.defaultdict(lambda: {"offertes": [], "werkbonnen": []})
    for r in t["project_quotes"]:
        projecten[r["project_code"]]["offertes"].append(offerte(r, r["quote_number"] in doel))
    for r in t["workorders"]:
        projecten[r["project_code"]]["werkbonnen"].append(werkbon(r))

    uit = Path(doelmap)
    uit.mkdir(parents=True, exist_ok=True)
    for code, p in sorted(projecten.items()):
        p["werkbonnen"].sort(key=lambda w: (w["datum"], w["starttijd"], w["ordernr"]))
        p["offertes"].sort(key=lambda o: o["offertenummer"])
        (uit / f"{code}.json").write_text(
            json.dumps({"projectcode": code, **p}, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"{code}: {len(p['offertes'])} offerte(s), {len(p['werkbonnen'])} werkbonnen")


if __name__ == "__main__":
    main(*sys.argv[1:3])
