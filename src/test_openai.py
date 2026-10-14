"""Test prompt v2 via de OpenAI API: elke klus een paar keer door het model en de tabel uitlezen.

Gebruik:
    python src/test_openai.py --droog                 alles klaarzetten zonder API (geen key nodig)
    python src/test_openai.py --modellen              beschikbare model-id's tonen
    python src/test_openai.py                         alle testklussen, 3 runs per klus
    python src/test_openai.py --runs 1 --projecten <projectcode> ...

De API-key staat in .env in de repo-root (OPENAI_API_KEY=...), nooit in git. Optioneel OPENAI_MODEL.

Systeemprompt = prompts/v2/instructies.md + beslisregels.md + de kennisbestanden uit
data/verwerkt/kennis (artikelcodes.md, voorbeeldklussen.md). In de eigen GPT staan die als losse
kennisbestanden die ChatGPT doorzoekt; hier leest het model ze helemaal. Daarom achteraf een paar
klussen met de hand in de echte GPT controleren.

De voorbeeldklussen (voorbeeldklussen.txt) tellen niet mee in de test. Uitvoer per run in
data/resultaten/<datum>_<model>_<prompt-hash>/: het antwoord (.md), voorstellen.csv met alle
uitgelezen rijen en runs.csv met tokens, duur en problemen.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from werkbonvoorstel import lees_voorstel, project_als_invoer

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.openai.com/v1"
STANDAARD_MODEL = "gpt-6.1-sol"  # controleren met --modellen zodra het account er is


def lees_env(pad):
    if pad.exists():
        for regel in pad.read_text(encoding="utf-8").splitlines():
            sleutel, is_, waarde = regel.partition("=")
            if is_ and not regel.lstrip().startswith("#"):
                os.environ.setdefault(sleutel.strip(), waarde.strip().strip('"'))


def systeemprompt(promptmap, kennismap):
    delen = [(promptmap / "instructies.md").read_text(encoding="utf-8")]
    for pad in [promptmap / "beslisregels.md", kennismap / "artikelcodes.md", kennismap / "voorbeeldklussen.md"]:
        if not pad.exists():
            sys.exit(f"{pad} ontbreekt. Maak de kennisbestanden eerst met src/maak_kennisbestanden.py.")
        delen.append(f"# Kennisbestand: {pad.name}\n\n{pad.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(delen)


def api(pad, sleutel, body=None, timeout=600):
    req = urllib.request.Request(
        f"{API}/{pad}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {sleutel}", "Content-Type": "application/json"},
    )
    for poging in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and poging < 2:
                time.sleep(15 * (poging + 1))
                continue
            sys.exit(f"OpenAI API gaf {e.code}: {e.read().decode(errors='replace')[:500]}")
        except urllib.error.URLError as e:
            if poging < 2:
                time.sleep(15 * (poging + 1))
                continue
            sys.exit(f"Geen verbinding met de OpenAI API: {e.reason}")


def antwoordtekst(data):
    """De tekst uit een Responses-antwoord; redeneerstappen en andere onderdelen vallen weg."""
    return "".join(
        c.get("text", "")
        for item in data.get("output", []) if item.get("type") == "message"
        for c in item.get("content", []) if c.get("type") == "output_text"
    )


def vraag_model(sleutel, model, instructies, invoer):
    # store=False: OpenAI bewaart het antwoord niet om later op te halen
    data = api("responses", sleutel, {"model": model, "instructions": instructies, "input": invoer, "store": False})
    return antwoordtekst(data), data.get("usage", {})


def testklussen(projectmap, voorbeelden, alleen):
    klussen = []
    for pad in sorted(projectmap.glob("*.json")):
        p = json.loads(pad.read_text(encoding="utf-8"))
        if alleen and p["projectcode"] not in alleen:
            continue
        if not alleen and (p["projectcode"] in voorbeelden or not any(w["uitvoering"] for w in p["werkbonnen"])):
            continue
        klussen.append(p)
    return klussen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--droog", action="store_true", help="alleen systeemprompt en invoer wegschrijven, geen API")
    ap.add_argument("--modellen", action="store_true", help="beschikbare model-id's tonen")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model")
    ap.add_argument("--projecten", nargs="*", default=[], help="alleen deze projectcodes (ook voorbeeldklussen)")
    ap.add_argument("--prompts", default=ROOT / "prompts" / "v2", type=Path)
    ap.add_argument("--kennis", default=ROOT / "data" / "verwerkt" / "kennis", type=Path)
    ap.add_argument("--data", default=ROOT / "data" / "verwerkt" / "projecten", type=Path)
    ap.add_argument("--uit", default=ROOT / "data" / "resultaten", type=Path)
    args = ap.parse_args()

    lees_env(ROOT / ".env")
    sleutel = os.environ.get("OPENAI_API_KEY")
    model = args.model or os.environ.get("OPENAI_MODEL") or STANDAARD_MODEL
    if not args.droog and not sleutel:
        sys.exit("OPENAI_API_KEY ontbreekt. Zet hem in .env in de repo-root, of gebruik --droog.")

    if args.modellen:
        for m in sorted(m["id"] for m in api("models", sleutel)["data"]):
            print(m)
        return

    instructies = systeemprompt(args.prompts, args.kennis)
    voorbeelden_pad = args.kennis / "voorbeeldklussen.txt"
    voorbeelden = set(voorbeelden_pad.read_text(encoding="utf-8").split()) if voorbeelden_pad.exists() else set()
    klussen = testklussen(args.data, voorbeelden, set(args.projecten))
    if not klussen:
        sys.exit("Geen klussen gevonden.")

    prompt_hash = hashlib.sha256(instructies.encode()).hexdigest()[:8]
    map_ = args.uit / f"{datetime.date.today()}_{'droog' if args.droog else model}_{prompt_hash}"
    map_.mkdir(parents=True, exist_ok=True)
    (map_ / "systeemprompt.md").write_text(instructies, encoding="utf-8")
    print(f"Systeemprompt: {len(instructies)} tekens (± {len(instructies) // 4} tokens), {len(klussen)} klussen -> {map_}")

    if args.droog:
        for p in klussen:
            invoer = project_als_invoer(p)
            (map_ / f"{p['projectcode']}_invoer.txt").write_text(invoer, encoding="utf-8")
            print(f"  {p['projectcode']}: invoer {len(invoer)} tekens")
        return

    nieuw = not (map_ / "voorstellen.csv").exists()
    with open(map_ / "voorstellen.csv", "a", newline="", encoding="utf-8") as fv, \
         open(map_ / "runs.csv", "a", newline="", encoding="utf-8") as fr:
        kolommen = ["project", "run", "nr", "discipline", "personen", "uren per persoon",
                    "omschrijving werkbon", "offerteregels", "twijfel"]
        wv = csv.DictWriter(fv, fieldnames=kolommen, extrasaction="ignore")
        wr = csv.DictWriter(fr, fieldnames=["project", "run", "model", "seconden", "input_tokens", "output_tokens", "rijen", "problemen"])
        if nieuw:
            wv.writeheader()
            wr.writeheader()
        for p in klussen:
            invoer = project_als_invoer(p)
            for run in range(1, args.runs + 1):
                bestand = map_ / f"{p['projectcode']}_run{run}.md"
                if bestand.exists():
                    print(f"  {p['projectcode']} run {run}: bestaat al, overgeslagen")
                    continue
                start = time.time()
                tekst, gebruik = vraag_model(sleutel, model, instructies, invoer)
                seconden = round(time.time() - start, 1)
                bestand.write_text(tekst, encoding="utf-8")
                rijen, problemen = lees_voorstel(tekst)
                for r in rijen:
                    wv.writerow({"project": p["projectcode"], "run": run, **r})
                wr.writerow({"project": p["projectcode"], "run": run, "model": model, "seconden": seconden,
                             "input_tokens": gebruik.get("input_tokens"), "output_tokens": gebruik.get("output_tokens"),
                             "rijen": len(rijen), "problemen": "; ".join(problemen)})
                fv.flush()
                fr.flush()
                print(f"  {p['projectcode']} run {run}: {len(rijen)} rijen, {seconden}s"
                      f"{', LET OP: ' + '; '.join(problemen) if problemen else ''}")


if __name__ == "__main__":
    main()
