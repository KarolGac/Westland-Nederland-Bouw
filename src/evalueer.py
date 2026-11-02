"""Evaluatie: de voorstellen van het taalmodel naast de echte werkbonnen leggen.

Gebruik:
    python src/evalueer.py data/resultaten/<run-map>
    python src/evalueer.py <map> --marge-uren 4 --marge-procent 25

Leest alle antwoorden <projectcode>_<label>.md in de map: uit src/test_openai.py (<code>_run1.md) of met
de hand uit ChatGPT met de skill gekopieerd (bijvoorbeeld <code>_skill1.md). Per antwoord en per discipline:
- ontbrekend: de planner plande deze discipline, het voorstel niet
- extra: het voorstel heeft deze discipline, de planner niet
- buiten marge: allebei, maar de persoonuren wijken meer af dan de marge (standaard 4 uur of 25%)
Aanpassingen = ontbrekend + extra + buiten marge: wat de planner zou moeten corrigeren. Hetzelfde
nog eens per vakgebied, waarbij "voor stuken" en "na stuken" samen tellen.

Schrijft evaluatie.md en evaluatie.csv in dezelfde map.
"""
import argparse
import collections
import csv
import json
import re
import statistics
from pathlib import Path

from werkbonvoorstel import DISCIPLINES, getal, lees_voorstel, werkbonnen_als_rijen

ROOT = Path(__file__).resolve().parent.parent
ANTWOORD = re.compile(r"^(\d+)_(.+)\.md$")


def vakgebied(discipline):
    return discipline.replace(" voor stuken", "").replace(" na stuken", "")


def persoonuren(rijen, sleutel=lambda d: d):
    """{discipline: personen x uren} voor rijen met 'discipline', 'personen' en 'uren'."""
    uren = collections.defaultdict(float)
    for r in rijen:
        uren[sleutel(r["discipline"])] += (r["personen"] or 0) * (r["uren"] or 0)
    return dict(uren)


def vergelijk(voorstel, echt, marge_uren, marge_procent):
    """Vergelijkt {discipline: persoonuren} van voorstel en echt. Geeft een rij per discipline."""
    rijen = []
    for d in sorted(set(voorstel) | set(echt), key=lambda d: (DISCIPLINES.index(d) if d in DISCIPLINES else 99, d)):
        v, e = voorstel.get(d), echt.get(d)
        if v is None:
            status = "ontbrekend"
        elif e is None:
            status = "extra"
        elif abs(v - e) <= max(marge_uren, e * marge_procent / 100):
            status = "goed"
        else:
            status = "te veel uren" if v > e else "te weinig uren"
        rijen.append({"discipline": d, "echt": e or 0.0, "voorstel": v or 0.0, "status": status})
    return rijen


def aanpassingen(vergelijking):
    return sum(r["status"] != "goed" for r in vergelijking)


def tijd_in_uren(tijd):
    uren, minuten = str(tijd).split(":")[:2]
    return int(uren) + int(minuten) / 60


def uren_op_planbord(w):
    """Duur van de bon, of het blok op het planbord als dat langer is: een paar bonnen staan op 2 uur
    terwijl ze van 08:00 tot 16:00 zijn ingepland."""
    duur = w["duur_minuten"] / 60
    if not w.get("starttijd") or not w.get("eindtijd"):
        return duur
    return max(duur, tijd_in_uren(w["eindtijd"]) - tijd_in_uren(w["starttijd"]))


def vooraf_en_eind(werkbonnen):
    """{discipline: uren} vooraf (bon gemaakt vóór de eerste werkdag van de klus) en aan het eind (alle bonnen)."""
    bonnen = [w for w in werkbonnen if w["uitvoering"]]
    start = min(w["datum"][:10] for w in bonnen)
    vooraf, eind = collections.defaultdict(float), collections.defaultdict(float)
    for w in bonnen:
        eind[w["discipline"]] += uren_op_planbord(w)
        if w["aangemaakt"][:10] < start:
            vooraf[w["discipline"]] += w["duur_minuten"] / 60
    return dict(vooraf), dict(eind)


def vergelijk_vooraf(voorstel, vooraf, eind, marge_uren, marge_procent):
    """Als vergelijk, maar goed is alles tussen wat vooraf gepland was en wat er aan het eind stond. Een
    discipline die pas tijdens de klus is bijgekomen hoeft niet in het voorstel te staan."""
    def marge(uren):
        return max(marge_uren, uren * marge_procent / 100)

    rijen = []
    for d in sorted(set(voorstel) | set(eind), key=lambda d: (DISCIPLINES.index(d) if d in DISCIPLINES else 99, d)):
        v, laag, hoog = voorstel.get(d), vooraf.get(d, 0.0), eind.get(d)
        if hoog is None:
            status = "extra"
        elif v is None:
            status = "ontbrekend" if laag else "goed"
        elif v > hoog + marge(hoog):
            status = "te veel uren"
        elif v < laag - marge(laag):
            status = "te weinig uren"
        else:
            status = "goed"
        rijen.append({"discipline": d, "vooraf": laag, "eind": hoog or 0.0, "voorstel": v or 0.0, "status": status})
    return rijen


def lees_antwoorden(map_, projecten):
    antwoorden, onleesbaar = [], []
    for pad in sorted(map_.glob("*.md")):
        m = ANTWOORD.match(pad.name)
        if not m or m.group(1) not in projecten:
            continue
        rijen, problemen = lees_voorstel(pad.read_text(encoding="utf-8"))
        if not rijen:
            onleesbaar.append((pad.name, "; ".join(problemen)))
            continue
        antwoorden.append({
            "project": m.group(1), "label": m.group(2), "problemen": problemen,
            "rijen": [{"discipline": r["discipline"], "personen": r["personen"], "uren": r["uren per persoon"]} for r in rijen],
        })
    return antwoorden, onleesbaar


def procent(deel, geheel):
    return f"{round(100 * deel / geheel)}%" if geheel else "-"


def verdeling(aantallen):
    n = len(aantallen)
    nul = sum(a == 0 for a in aantallen)
    een_twee = sum(1 <= a <= 2 for a in aantallen)
    return [f"| Precies goed (0 aanpassingen) | {nul} | {procent(nul, n)} |",
            f"| Goed met 1 à 2 aanpassingen | {een_twee} | {procent(een_twee, n)} |",
            f"| 3 of meer aanpassingen | {n - nul - een_twee} | {procent(n - nul - een_twee, n)} |"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("map", type=Path)
    ap.add_argument("--data", default=ROOT / "data" / "verwerkt" / "projecten", type=Path)
    ap.add_argument("--marge-uren", type=float, default=4)
    ap.add_argument("--marge-procent", type=float, default=25)
    args = ap.parse_args()

    projecten = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in args.data.glob("*.json")}
    antwoorden, onleesbaar = lees_antwoorden(args.map, projecten)
    if not antwoorden:
        raise SystemExit(f"Geen leesbare antwoorden (<projectcode>_<label>.md) gevonden in {args.map}")

    echt_rijen = {code: werkbonnen_als_rijen(p["werkbonnen"]) for code, p in projecten.items()}
    csv_rijen, per_klus = [], collections.defaultdict(list)
    for a in antwoorden:
        echt = echt_rijen[a["project"]]
        streng = vergelijk(persoonuren(a["rijen"]), persoonuren(echt), args.marge_uren, args.marge_procent)
        grof = vergelijk(persoonuren(a["rijen"], vakgebied), persoonuren(echt, vakgebied), args.marge_uren, args.marge_procent)
        vooraf, eind = vooraf_en_eind(projecten[a["project"]]["werkbonnen"])
        a.update(streng=streng, grof=grof,
                 band=vergelijk_vooraf(persoonuren(a["rijen"]), vooraf, eind, args.marge_uren, args.marge_procent))
        per_klus[a["project"]].append(a)
        for r in streng:
            csv_rijen.append({"project": a["project"], "label": a["label"], **r})

    with open(args.map / "evaluatie.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["project", "label", "discipline", "echt", "voorstel", "status"])
        w.writeheader()
        w.writerows(csv_rijen)

    alle = [r for a in antwoorden for r in a["streng"]]
    telling = collections.Counter(r["status"] for r in alle)
    juist = sum(r["status"] not in ("ontbrekend", "extra") for r in alle)
    md = [f"# Evaluatie {args.map.name}", "",
          f"{len(antwoorden)} antwoorden op {len(per_klus)} klussen"
          f"{f', {len(onleesbaar)} niet leesbaar' if onleesbaar else ''}. "
          f"Marge persoonuren: {getal(args.marge_uren)} uur of {getal(args.marge_procent)}%, de grootste van de twee.", "",
          "## Hoeveel moet de planner aanpassen", "",
          "| Per antwoord | Aantal | Aandeel |", "|---|---|---|", *verdeling([aanpassingen(a["streng"]) for a in antwoorden]), "",
          "Zelfde, met voor en na stuken samengenomen:", "",
          "| Per antwoord | Aantal | Aandeel |", "|---|---|---|", *verdeling([aanpassingen(a["grof"]) for a in antwoorden]), "",
          "Zelfde, maar goed is alles tussen wat vóór de start van de klus was ingepland en wat er aan het eind stond "
          "(milde maat: ook later ingepland werk uit de offerte hoeft niet in het voorstel te staan):", "",
          "| Per antwoord | Aantal | Aandeel |", "|---|---|---|", *verdeling([aanpassingen(a["band"]) for a in antwoorden]), "",
          "## Wat gaat er mis", "",
          "| | Aantal |", "|---|---|",
          f"| Disciplines goed gevonden | {juist} van {juist + telling['ontbrekend']} ({procent(juist, juist + telling['ontbrekend'])}) |",
          f"| Ontbrekende discipline (werk vergeten) | {telling['ontbrekend']} |",
          f"| Extra discipline (werk dat de planner niet plande) | {telling['extra']} |",
          f"| Te veel persoonuren | {telling['te veel uren']} |",
          f"| Te weinig persoonuren | {telling['te weinig uren']} |",
          f"| Persoonuren binnen de marge | {telling['goed']} |", "",
          "## Per klus", "",
          "| Klus | Antwoorden | Aanpassingen per antwoord | Persoonuren echt | Persoonuren voorstel (min–max) | Vaakst ontbrekend of extra |",
          "|---|---|---|---|---|---|"]
    for code, lijst in sorted(per_klus.items()):
        echt_totaal = sum(persoonuren(echt_rijen[code]).values())
        totalen = [sum(r["voorstel"] for r in a["streng"]) for a in lijst]
        fouten = collections.Counter(f"{r['discipline']} ({r['status']})" for a in lijst for r in a["streng"]
                                     if r["status"] in ("ontbrekend", "extra"))
        md.append(f"| {code} | {len(lijst)} | {', '.join(str(aanpassingen(a['streng'])) for a in lijst)} | "
                  f"{getal(echt_totaal)} | {getal(min(totalen))}–{getal(max(totalen))} | "
                  f"{'; '.join(f for f, _ in fouten.most_common(2)) or '-'} |")

    md += ["", "## Per discipline", "",
           "| Discipline | Klussen bij de planner | Gevonden in voorstel | Gem. persoonuren echt | Gem. persoonuren voorstel |",
           "|---|---|---|---|---|"]
    for d in DISCIPLINES:
        rijen = [r for r in alle if r["discipline"] == d]
        bij_planner = [r for r in rijen if r["status"] != "extra"]
        gevonden = [r for r in bij_planner if r["status"] != "ontbrekend"]
        if rijen:
            md.append(f"| {d} | {len(bij_planner)} | {len(gevonden)} | "
                      f"{getal(round(statistics.mean(r['echt'] for r in bij_planner), 1)) if bij_planner else '-'} | "
                      f"{getal(round(statistics.mean(r['voorstel'] for r in gevonden), 1)) if gevonden else '-'} |")

    meldingen = [(f"{a['project']}_{a['label']}", p) for a in antwoorden for p in a["problemen"]] + onleesbaar
    if meldingen:
        md += ["", "## Meldingen bij het inlezen", ""] + [f"- {naam}: {p}" for naam, p in meldingen]
    md += ["", "Klussen bij de planner en het gemiddelde tellen per antwoord: bij 3 runs telt een klus 3 keer."]

    (args.map / "evaluatie.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:md.index("## Per klus")]))
    print(f"\n-> {args.map / 'evaluatie.md'} en evaluatie.csv")


if __name__ == "__main__":
    main()
