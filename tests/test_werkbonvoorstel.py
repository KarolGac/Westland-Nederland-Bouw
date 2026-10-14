import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from maak_kennisbestanden import schone_omschrijving  # noqa: E402
from test_openai import antwoordtekst  # noqa: E402
from werkbonvoorstel import bedrag, lees_voorstel, offerte_als_tekst, werkbonnen_als_rijen  # noqa: E402

ANTWOORD = """| Nr | Discipline | Personen | Uren per persoon | Omschrijving werkbon | Offerteregels | Twijfel |
|---|---|---|---|---|---|---|
| 1 | Demontage | 2 | 4 | Afplakken; Demonteren oude keuken | 1.1, 2.2 | |
| 2 | Leidingwerk en elektra voor stuken | 3 | hele dag | Leidingwerk basis keuken | 3.1.1 | |
| 3 | Stukwerk | 1 | 8,0 | Het stuken van de wand tot 21m2 | 6.0 | |

**Niet ingepland:**
- Opname meerwerk: al gedaan
"""


def werkbon(datum, discipline, minuten, uitvoering=True):
    return {"datum": datum, "discipline": discipline, "duur_minuten": minuten, "uitvoering": uitvoering}


class LeesVoorstel(unittest.TestCase):
    def test_tabel_wordt_gelezen(self):
        rijen, problemen = lees_voorstel(ANTWOORD)
        self.assertEqual(problemen, [])
        self.assertEqual([r["discipline"] for r in rijen], ["Demontage", "Leidingwerk en elektra voor stuken", "Stukwerk"])
        self.assertEqual([(r["personen"], r["uren per persoon"]) for r in rijen], [(2, 4), (3, 8), (1, 8)])
        self.assertEqual(rijen[0]["offerteregels"], "1.1, 2.2")

    def test_onbekende_discipline_en_lege_cel(self):
        rijen, problemen = lees_voorstel(ANTWOORD.replace("| Stukwerk | 1 |", "| Stucwerk | ? |"))
        self.assertEqual(len(rijen), 3)
        self.assertEqual(len(problemen), 2)

    def test_geen_tabel(self):
        self.assertEqual(lees_voorstel("Ik weet het niet.")[0], [])

    def test_tekst_uit_api_antwoord(self):
        data = {"output": [
            {"type": "reasoning", "summary": []},
            {"type": "message", "content": [{"type": "output_text", "text": ANTWOORD}]},
        ]}
        self.assertEqual(len(lees_voorstel(antwoordtekst(data))[0]), 3)


class Werkbonnen(unittest.TestCase):
    def test_groeperen_per_dag_discipline_en_duur(self):
        rijen = werkbonnen_als_rijen([
            werkbon("2026-05-28", "Leidingwerk en elektra voor stuken", 480),
            werkbon("2026-05-28", "Leidingwerk en elektra voor stuken", 480),
            werkbon("2026-05-28", "Leidingwerk en elektra voor stuken", 240),
            werkbon("2026-05-26", "Demontage", 240),
            werkbon("2026-05-05", "Opname", 120, uitvoering=False),
        ])
        self.assertEqual([(r["discipline"], r["personen"], r["uren"]) for r in rijen], [
            ("Demontage", 1, 4),
            ("Leidingwerk en elektra voor stuken", 2, 8),
            ("Leidingwerk en elektra voor stuken", 1, 4),
        ])


class OfferteAlsTekst(unittest.TestCase):
    def test_verborgen_regel_en_bedrag(self):
        regel = {"artikelcode": "3.1.1", "omschrijving": "Leidingwerk basis keuken", "toelichting": "",
                 "aantal": 1.0, "eenheid": "Eenheidsprijs", "bedrag_excl": 1701.15, "verborgen": False}
        tekst = offerte_als_tekst({"offertenummer": "2026-00001", "geaccepteerd": "2026-05-11T08:54:18",
                                   "bedrag_excl": 1701.15,
                                   "regels": [regel, {**regel, "omschrijving": "Geheim", "verborgen": True}]})
        self.assertIn("[3.1.1] Leidingwerk basis keuken | 1 Eenheidsprijs | € 1.701,15", tekst)
        self.assertIn("geaccepteerd 11-05-2026", tekst)
        self.assertNotIn("Geheim", tekst)
        self.assertEqual(bedrag(-765.31), "€ -765,31")


class SchoneOmschrijving(unittest.TestCase):
    def test_leveranciersblok_en_telefoon_weg(self):
        tekst = "Bellen 0612345678 bij aankomst\n\nLeidingwerk basis keuken\n\nLeverweek 26\nShowroom X\nInmeetdatum: 1/4"
        self.assertEqual(schone_omschrijving(tekst, []), "Bellen  bij aankomst; Leidingwerk basis keuken")

    def test_weglaten(self):
        self.assertEqual(schone_omschrijving("Naam meenemen\nStukwerk", ["naam"]), "Stukwerk")


if __name__ == "__main__":
    unittest.main()
