"""Antwoordblad: per klus wat de planner echt heeft ingepland, in dezelfde vorm als de vaste uitvoer.

Gebruik:
    python src/maak_antwoordblad.py data/verwerkt/projecten data/verwerkt

Schrijft antwoordblad.csv (één rij per dag, discipline en duur) en antwoordblad.md (leesbaar, met
totalen per discipline). Opname, Service en Reservering tellen niet mee; projecten zonder
uitvoeringswerkbonnen vallen af.
"""
import collections
import csv
import json
import sys
from pathlib import Path

from werkbonvoorstel import DISCIPLINES, getal, werkbonnen_als_rijen


def main(projectmap, uitmap):
    uit = Path(uitmap)
    uit.mkdir(parents=True, exist_ok=True)
    csv_rijen, md = [], ["# Antwoordblad: echte werkbonnen per klus", ""]
    md.append("Eén rij = zoveel personen die die dag even lang aan die discipline werkten. "
              "Opname, Service en Reservering tellen niet mee. Gemaakt met `src/maak_antwoordblad.py`.")
    volgorde = {d: i for i, d in enumerate(DISCIPLINES)}
    n = 0
    for pad in sorted(Path(projectmap).glob("*.json")):
        p = json.loads(pad.read_text(encoding="utf-8"))
        rijen = werkbonnen_als_rijen(p["werkbonnen"])
        if not rijen:
            print(f"{p['projectcode']}: geen uitvoeringswerkbonnen, overgeslagen")
            continue
        n += 1
        offertes = ", ".join(o["offertenummer"] for o in p["offertes"])
        md += ["", f"## {p['projectcode']} (offertes {offertes})", "",
               "| Datum | Discipline | Personen | Uren per persoon |", "|---|---|---|---|"]
        totaal = collections.defaultdict(lambda: {"persoonuren": 0.0, "dagen": set(), "max_personen": 0})
        for r in rijen:
            csv_rijen.append({"project": p["projectcode"], "datum": r["datum"], "discipline": r["discipline"],
                              "personen": r["personen"], "uren_per_persoon": r["uren"]})
            md.append(f"| {r['datum']} | {r['discipline']} | {r['personen']} | {getal(r['uren'])} |")
            t = totaal[r["discipline"]]
            t["persoonuren"] += r["personen"] * r["uren"]
            t["dagen"].add(r["datum"])
            t["max_personen"] = max(t["max_personen"], sum(x["personen"] for x in rijen
                                                           if x["datum"] == r["datum"] and x["discipline"] == r["discipline"]))
        md += ["", "| Discipline | Persoonuren | Dagen | Max. personen op een dag |", "|---|---|---|---|"]
        for d, t in sorted(totaal.items(), key=lambda kv: volgorde.get(kv[0], 99)):
            md.append(f"| {d} | {getal(t['persoonuren'])} | {len(t['dagen'])} | {t['max_personen']} |")
        print(f"{p['projectcode']}: {len(rijen)} rijen, {len(totaal)} disciplines")

    with open(uit / "antwoordblad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["project", "datum", "discipline", "personen", "uren_per_persoon"])
        w.writeheader()
        w.writerows(csv_rijen)
    (uit / "antwoordblad.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{n} klussen, {len(csv_rijen)} rijen -> {uit / 'antwoordblad.csv'} en antwoordblad.md")


if __name__ == "__main__":
    main(*sys.argv[1:3])
