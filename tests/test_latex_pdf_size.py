import tempfile
import unittest
from pathlib import Path

from edu_publish.latex_pdf_size import format_pdf_size_mb, update_pdf_size_text


class LatexPdfSizeTests(unittest.TestCase):
    def test_format_pdf_size_uses_ukrainian_decimal_comma(self):
        self.assertEqual(format_pdf_size_mb(1_049_000), "1,0")
        self.assertEqual(format_pdf_size_mb(1_050_000), "1,1")

    def test_update_pdf_size_text_replaces_first_obsyag_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "shapka.tex"
            target.write_text(
                "before\n Обсяг 1,0 МБ. Зам. № \\\\\n Обсяг 2,0 МБ.\n",
                encoding="utf-8",
            )

            changed = update_pdf_size_text(target, "1,7")

            self.assertTrue(changed)
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                "before\n Обсяг 1,7 МБ. Зам. № \\\\\n Обсяг 2,0 МБ.\n",
            )

    def test_update_pdf_size_text_reports_when_already_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "shapka.tex"
            target.write_text("Обсяг 1,7 МБ. Зам. № \\\\\n", encoding="utf-8")

            changed = update_pdf_size_text(target, "1,7")

            self.assertFalse(changed)

    def test_update_pdf_size_text_requires_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "shapka.tex"
            target.write_text("No size here\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                update_pdf_size_text(target, "1,7")


if __name__ == "__main__":
    unittest.main()
