import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from offerte_pdf_naar_tekst import schoon  # noqa: E402

PDF = """Jan Voorbeeld
Teststraat 1
1234 AB Testdorp

Omschrijving                 Foto Aantal   Totaal
                                  1        € 1.701,15
Leidingwerk basis keuken
Bel 0612345678 of mail jan@voorbeeld.nl, Jan Voorbeeld is thuis

Let op: diverse werkzaamheden zijn in combinatie en op basis van een totaalafname.

Let op: door ondertekening stemt u in met deze montage-opdracht
Jan Voorbeeld
15-04-2026
"""


class Schoon(unittest.TestCase):
    def setUp(self):
        self.tekst = schoon(PDF, {"Jan Voorbeeld", "Voorbeeld"})

    def test_kop_en_ondertekening_vallen_weg(self):
        self.assertTrue(self.tekst.startswith("Omschrijving"))
        self.assertNotIn("Teststraat", self.tekst)
        self.assertNotIn("ondertekening", self.tekst)
        self.assertNotIn("15-04-2026", self.tekst)

    def test_klantgegevens_uit_de_tekst(self):
        self.assertNotIn("Voorbeeld", self.tekst)
        self.assertNotIn("0612345678", self.tekst)
        self.assertNotIn("voorbeeld.nl", self.tekst)

    def test_regels_en_bedragen_blijven_staan(self):
        self.assertIn("Leidingwerk basis keuken", self.tekst)
        self.assertIn("€ 1.701,15", self.tekst)
        self.assertIn("op basis van een totaalafname", self.tekst)

    def test_zonder_kolomkop_begint_de_tekst_bij_de_eerste_regel(self):
        tekst = schoon("Jan\nTeststraat 1\nLeidingwerk basis keuken 1\n", set())
        self.assertTrue(tekst.startswith("Leidingwerk basis keuken"))


if __name__ == "__main__":
    unittest.main()
