import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from maak_skill import maak_skill, skill_tekst  # noqa: E402

INSTRUCTIES = "Intro.\n\n# Kennisbestanden\n- beslisregels.md: regels.\n\n# Werkwijze\n1. Lees alles.\n"


class SkillTekst(unittest.TestCase):
    def test_kop_en_kennisbestanden(self):
        tekst = skill_tekst(INSTRUCTIES)
        self.assertTrue(tekst.startswith('---\nname: werkbonvoorstel\ndescription: "'))
        self.assertIn("\n---\n\nIntro.\n\n# Kennisbestanden\n", tekst)
        self.assertIn("- references/beslisregels.md:", tekst)
        self.assertNotIn("- beslisregels.md: regels.", tekst)
        self.assertTrue(tekst.endswith("\n\n# Werkwijze\n1. Lees alles.\n"))

    def test_zonder_kennisbestanden(self):
        with self.assertRaises(ValueError):
            skill_tekst("Intro.\n\n# Werkwijze\n1. Lees alles.\n")


class MaakSkill(unittest.TestCase):
    def test_zip_met_map_bovenaan(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "prompts").mkdir()
            (tmp / "kennis").mkdir()
            (tmp / "prompts" / "instructies.md").write_text(INSTRUCTIES, encoding="utf-8")
            (tmp / "prompts" / "beslisregels.md").write_text("regels", encoding="utf-8")
            (tmp / "kennis" / "artikelcodes.md").write_text("codes", encoding="utf-8")
            (tmp / "kennis" / "voorbeeldklussen.md").write_text("voorbeelden", encoding="utf-8")
            zip_ = maak_skill(tmp / "prompts", tmp / "kennis", tmp / "uit")
            with zipfile.ZipFile(zip_) as z:
                self.assertEqual(sorted(z.namelist()), [
                    "werkbonvoorstel/SKILL.md",
                    "werkbonvoorstel/references/artikelcodes.md",
                    "werkbonvoorstel/references/beslisregels.md",
                    "werkbonvoorstel/references/voorbeeldklussen.md",
                ])


if __name__ == "__main__":
    unittest.main()
