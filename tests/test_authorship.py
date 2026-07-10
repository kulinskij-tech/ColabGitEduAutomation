import json
import tempfile
import unittest
from pathlib import Path

from edu_publish.authorship.cli import measure_from_config
from edu_publish.authorship.latex import measure_latex_roots
from edu_publish.authorship.models import AuthorshipConfig, SourceConfig, ToolConfig
from edu_publish.authorship.notebooks import measure_notebook_dirs


class AuthorshipTests(unittest.TestCase):
    def test_simple_latex_ignores_commands_comments_and_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / "main.tex"
            main.write_text(
                r"""
\section{Intro}
Visible text here. % hidden comment
\label{sec:intro}
See \ref{sec:other}.
\textbf{Bold text}
""",
                encoding="utf-8",
            )

            result = measure_latex_roots([main], AuthorshipConfig())
            joined = " ".join(block.text for block in result.blocks)

            self.assertIn("Intro", joined)
            self.assertIn("Visible text here.", joined)
            self.assertIn("Bold text", joined)
            self.assertNotIn("hidden comment", joined)
            self.assertNotIn("sec:intro", joined)

    def test_nested_inputs_are_followed_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "child.tex").write_text("Child text.", encoding="utf-8")
            (root / "main.tex").write_text(
                r"Main text. \input{child} \input{child}",
                encoding="utf-8",
            )

            result = measure_latex_roots([root / "main.tex"], AuthorshipConfig())
            joined = " ".join(block.text for block in result.blocks)

            self.assertIn("Main text.", joined)
            self.assertEqual(joined.count("Child text."), 1)
            self.assertEqual(len(result.files_read), 2)

    def test_markdown_notebook_counts_visible_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            notebook_dir = Path(tmp)
            write_notebook(
                notebook_dir / "lesson.ipynb",
                [markdown_cell("# Heading\n\nSome **markdown** [link](x).")],
            )

            result = measure_notebook_dirs([notebook_dir], AuthorshipConfig(), [])

            self.assertEqual(result.code_characters, 0)
            self.assertGreater(result.markdown_characters, 0)

    def test_code_mode_text_and_exclude(self):
        with tempfile.TemporaryDirectory() as tmp:
            notebook_dir = Path(tmp)
            write_notebook(notebook_dir / "lesson.ipynb", [code_cell("print('hello')\n")])

            text_result = measure_notebook_dirs(
                [notebook_dir],
                AuthorshipConfig(code_mode="text"),
                [],
            )
            exclude_result = measure_notebook_dirs(
                [notebook_dir],
                AuthorshipConfig(code_mode="exclude"),
                [],
            )

            self.assertEqual(text_result.code_characters, len("print('hello')\n"))
            self.assertEqual(exclude_result.code_characters, 0)

    def test_duplicate_removal(self):
        duplicate = "This paragraph is deliberately long enough to trigger duplicate detection. " * 4
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            latex = root / "main.tex"
            notebooks = root / "nbs"
            notebooks.mkdir()
            latex.write_text(duplicate, encoding="utf-8")
            write_notebook(notebooks / "lesson.ipynb", [markdown_cell(duplicate)])

            main = measure_latex_roots(
                [latex],
                AuthorshipConfig(minimum_duplicate_block_length=50),
            )
            companion = measure_notebook_dirs(
                [notebooks],
                AuthorshipConfig(minimum_duplicate_block_length=50),
                main.blocks,
            )

            self.assertEqual(companion.markdown_characters, 0)
            self.assertGreater(companion.duplicates_removed, 0)

    def test_author_sheets_round_up_to_half_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            latex = root / "main.tex"
            latex.write_text("a" * 40001, encoding="utf-8")

            report = measure_from_config(
                ToolConfig(
                    sources=SourceConfig(latex_roots=[latex]),
                    authorship=AuthorshipConfig(rounding_increment=0.5),
                )
            )

            self.assertAlmostEqual(report.main_publication.raw_author_sheets, 1.000025)
            self.assertEqual(report.main_publication.author_sheets, 1.5)
            self.assertEqual(report.combined_author_sheets, 1.5)
    def test_combined_calculation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            latex = root / "main.tex"
            notebooks = root / "nbs"
            notebooks.mkdir()
            latex.write_text("a" * 40000, encoding="utf-8")
            write_notebook(notebooks / "lesson.ipynb", [markdown_cell("b" * 40000)])

            report = measure_from_config(
                ToolConfig(
                    sources=SourceConfig(
                        latex_roots=[latex],
                        notebook_dirs=[notebooks],
                    ),
                    authorship=AuthorshipConfig(deduplicate=False),
                )
            )

            self.assertEqual(report.main_publication.author_sheets, 1.0)
            self.assertEqual(report.interactive_companion.author_sheets, 1.0)
            self.assertEqual(report.combined_author_sheets, 2.0)


def write_notebook(path, cells):
    path.write_text(
        json.dumps(
            {
                "cells": cells,
                "metadata": {"ignored": True},
                "nbformat": 4,
                "nbformat_minor": 5,
            }
        ),
        encoding="utf-8",
    )


def markdown_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source,
    }


def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [
            {
                "output_type": "stream",
                "name": "stdout",
                "text": "generated output",
            }
        ],
        "source": source,
    }


if __name__ == "__main__":
    unittest.main()

