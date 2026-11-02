import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from evalueer import (aanpassingen, lees_antwoorden, persoonuren, uren_op_planbord, vakgebied, vergelijk,  # noqa: E402
                      vergelijk_vooraf, vooraf_en_eind)

KOP = "| Nr | Discipline | Personen | Uren per persoon | Omschrijving werkbon | Offerteregels | Twijfel |\n|---|---|---|---|---|---|---|\n"


def rij(discipline, personen, uren):
    return {"discipline": discipline, "personen": personen, "uren": uren}


class Vergelijk(unittest.TestCase):
    echt = persoonuren([rij("Demontage", 2, 4), rij("Leidingwerk en elektra voor stuken", 3, 8)])

    def test_precies_goed(self):
        voorstel = persoonuren([rij("Demontage", 2, 4), rij("Leidingwerk en elektra voor stuken", 2, 8),
                                rij("Leidingwerk en elektra voor stuken", 1, 8)])
        self.assertEqual(aanpassingen(vergelijk(voorstel, self.echt, 4, 25)), 0)

    def test_ontbrekend_extra_en_marge(self):
        voorstel = persoonuren([rij("Leidingwerk en elektra voor stuken", 2, 8), rij("Stukwerk", 1, 8)])
        status = {r["discipline"]: r["status"] for r in vergelijk(voorstel, self.echt, 4, 25)}
        self.assertEqual(status, {"Demontage": "ontbrekend", "Leidingwerk en elektra voor stuken": "te weinig uren",
                                  "Stukwerk": "extra"})

    def test_marge_is_grootste_van_uren_en_procent(self):
        # echt 8 uur, voorstel 12: 4 uur verschil valt binnen 4 uur, niet binnen 25%
        self.assertEqual(vergelijk({"Stukwerk": 12}, {"Stukwerk": 8}, 4, 25)[0]["status"], "goed")
        self.assertEqual(vergelijk({"Stukwerk": 12}, {"Stukwerk": 8}, 2, 25)[0]["status"], "te veel uren")

    def test_vakgebied_voegt_voor_en_na_stuken_samen(self):
        echt = persoonuren([rij("Leidingwerk en elektra na stuken", 2, 8)], vakgebied)
        voorstel = persoonuren([rij("Leidingwerk en elektra voor stuken", 2, 8)], vakgebied)
        self.assertEqual(aanpassingen(vergelijk(voorstel, echt, 4, 25)), 0)


def bon(discipline, datum, aangemaakt, uren, eindtijd="16:00"):
    return {"uitvoering": True, "discipline": discipline, "datum": datum, "aangemaakt": aangemaakt,
            "duur_minuten": uren * 60, "starttijd": "08:00", "eindtijd": eindtijd}


class VergelijkVooraf(unittest.TestCase):
    def test_vooraf_is_gemaakt_voor_de_eerste_werkdag(self):
        vooraf, eind = vooraf_en_eind([
            bon("Demontage", "2026-06-05", "2026-04-30T10:00:00", 8),
            bon("Demontage", "2026-06-05", "2026-06-04T10:00:00", 8),
            bon("Stukwerk", "2026-06-10", "2026-06-05T10:00:00", 8),
        ])
        self.assertEqual(vooraf, {"Demontage": 16})
        self.assertEqual(eind, {"Demontage": 16, "Stukwerk": 8})

    def test_blok_telt_als_het_langer_is_dan_de_duur(self):
        self.assertEqual(uren_op_planbord(bon("Stukwerk", "2026-06-10", "2026-06-05", 2)), 8)
        self.assertEqual(uren_op_planbord(bon("Stukwerk", "2026-06-10", "2026-06-05", 8, eindtijd="10:00")), 8)

    def test_goed_tussen_vooraf_en_eind(self):
        status = {r["discipline"]: r["status"] for r in vergelijk_vooraf(
            {"Demontage": 24, "Stukwerk": 8, "Wand tegelen": 8, "Latexen / schilderen": 40},
            {"Demontage": 16, "Egalisatie / vloerafwerking": 4},
            {"Demontage": 32, "Stukwerk": 8, "Egalisatie / vloerafwerking": 4, "Afmonteren schakelmateriaal": 4,
             "Latexen / schilderen": 8},
            4, 25)}
        self.assertEqual(status, {"Demontage": "goed", "Stukwerk": "goed", "Wand tegelen": "extra",
                                  "Latexen / schilderen": "te veel uren", "Egalisatie / vloerafwerking": "ontbrekend",
                                  "Afmonteren schakelmateriaal": "goed"})

    def test_te_weinig_onder_wat_vooraf_gepland_was(self):
        [rij] = vergelijk_vooraf({"Demontage": 8}, {"Demontage": 24}, {"Demontage": 24}, 4, 25)
        self.assertEqual(rij["status"], "te weinig uren")


class LeesAntwoorden(unittest.TestCase):
    def test_bestandsnamen_en_onleesbaar(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_ = Path(tmp)
            (map_ / "123_run1.md").write_text(KOP + "| 1 | Stukwerk | 1 | 8 | Stuken | 6.0 | |\n", encoding="utf-8")
            (map_ / "123_gpt1.md").write_text("Geen tabel", encoding="utf-8")
            (map_ / "999_run1.md").write_text(KOP, encoding="utf-8")  # onbekend project
            (map_ / "systeemprompt.md").write_text(KOP, encoding="utf-8")
            antwoorden, onleesbaar = lees_antwoorden(map_, {"123": json.loads("{}")})
        self.assertEqual([(a["project"], a["label"]) for a in antwoorden], [("123", "run1")])
        self.assertEqual(antwoorden[0]["rijen"], [rij("Stukwerk", 1, 8)])
        self.assertEqual([naam for naam, _ in onleesbaar], ["123_gpt1.md"])


if __name__ == "__main__":
    unittest.main()
