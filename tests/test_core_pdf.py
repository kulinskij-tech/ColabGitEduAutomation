import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PyPDF2 import PdfReader, PdfWriter

from edu_publish.core_pdf import generate_core_pdf_from_notebooks


class CorePdfTests(unittest.TestCase):
    def test_generate_core_pdf_exports_notebooks_merges_pdf_and_rewrites_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            course = Path(tmp) / "course"
            course.mkdir()
            write_notebook(
                course / "demo_toc.ipynb",
                [
                    markdown_cell(
                        "[First](lesson_a.ipynb)\n\n[Second](lesson_b.ipynb)"
                    )
                ],
            )
            write_notebook(
                course / "lesson_a.ipynb",
                [
                    markdown_cell(
                        "# First topic\n\n"
                        "Some **bold** text with $E=h\\nu$.\n\n"
                        '<a href="https://example.com">Example</a>\n\n'
                        '<img src="figs/plot.png" alt="Plot">\n\n'
                        "[Next](lesson_b.ipynb)"
                    ),
                    code_cell("print('hello')\n", outputs=[stream_output("hello\n")]),
                ],
            )
            (course / "figs").mkdir()
            (course / "figs" / "plot.png").write_bytes(b"not a real png")
            write_notebook(
                course / "lesson_b.ipynb",
                [markdown_cell("## Second topic\n\nMore text.")],
            )
            output = course / "core_pdf" / "course_core.pdf"

            with mock.patch(
                "edu_publish.core_pdf.subprocess.run",
                side_effect=fake_export_run,
            ) as run_mock:
                with mock.patch(
                    "edu_publish.core_pdf.ensure_mathjax_assets",
                    return_value="_mathjax/MathJax.js?config=TeX-AMS-MML_HTMLorMML",
                ):
                    result = generate_core_pdf_from_notebooks(
                        course,
                        output,
                        title="Test Course",
                        author="Author Name",
                        subtitle="Notebook edition",
                        github_repo="owner/repo",
                        github_course_dir="Atomic_py",
                        renderer="html",
                    )

            self.assertTrue(result.generated)
            self.assertTrue(result.merged)
            self.assertEqual(result.exported_notebooks, 4)
            self.assertEqual(result.pdf_path, output)
            self.assertTrue(output.exists())

            self.assertEqual(len(PdfReader(str(output)).pages), 4)
            self.assertEqual(run_mock.call_count, 8)

            staged_lesson_a = result.staging_dir / "lesson_a.ipynb"
            lesson_a_text = staged_lesson_a.read_text(encoding="utf-8")
            self.assertIn(
                "https://github.com/owner/repo/blob/main/Atomic_py/lesson_b.ipynb",
                lesson_a_text,
            )
            self.assertIn(
                "https://github.com/owner/repo/blob/main/Atomic_py/lesson_a.ipynb",
                (result.staging_dir / "00_cover.ipynb").read_text(encoding="utf-8"),
            )

            commands = [call.args[0] for call in run_mock.call_args_list]
            command_notebooks = [cmd[-1] for cmd in commands[0::2]]
            self.assertEqual(
                command_notebooks,
                [
                    "00_cover.ipynb",
                    "demo_toc.ipynb",
                    "lesson_a.ipynb",
                    "lesson_b.ipynb",
                ],
            )
            printed_pdfs = [
                Path(next(arg for arg in cmd if arg.startswith("--print-to-pdf="))).name
                for cmd in commands[1::2]
            ]
            self.assertEqual(
                printed_pdfs,
                [
                    "00_cover.pdf",
                    "demo_toc.pdf",
                    "lesson_a.pdf",
                    "lesson_b.pdf",
                ],
            )

    def test_generate_core_pdf_skips_existing_pdf_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            course = Path(tmp) / "course"
            course.mkdir()
            write_notebook(course / "demo_toc.ipynb", [markdown_cell("[First](lesson.ipynb)")])
            write_notebook(course / "lesson.ipynb", [markdown_cell("Text")])
            output = course / "core_pdf" / "course_core.pdf"
            output.parent.mkdir()
            output.write_bytes(b"existing pdf")

            with mock.patch("edu_publish.core_pdf.subprocess.run") as run_mock:
                result = generate_core_pdf_from_notebooks(course, output)

            self.assertFalse(result.generated)
            self.assertEqual(output.read_bytes(), b"existing pdf")
            run_mock.assert_not_called()

    def test_generate_core_pdf_can_use_nbclassic_renderer(self):
        with tempfile.TemporaryDirectory() as tmp:
            course = Path(tmp) / "course"
            course.mkdir()
            write_notebook(course / "demo_toc.ipynb", [markdown_cell("[First](lesson.ipynb)")])
            write_notebook(course / "lesson.ipynb", [markdown_cell("Text")])
            output = course / "core_pdf" / "course_core.pdf"

            with mock.patch("edu_publish.core_pdf.NbclassicServer", FakeNbclassicServer):
                with mock.patch(
                    "edu_publish.core_pdf.subprocess.run",
                    side_effect=fake_nbclassic_print_run,
                ) as run_mock:
                    result = generate_core_pdf_from_notebooks(
                        course,
                        output,
                        renderer="nbclassic",
                    )

            self.assertTrue(result.generated)
            self.assertEqual(result.renderer, "nbclassic")
            self.assertTrue(output.exists())
            printed_urls = [call.args[0][-1] for call in run_mock.call_args_list]
            self.assertEqual(
                printed_urls,
                [
                    "http://nbclassic.local/nbconvert/html/00_cover.ipynb?download=false",
                    "http://nbclassic.local/nbconvert/html/demo_toc.ipynb?download=false",
                    "http://nbclassic.local/nbconvert/html/lesson.ipynb?download=false",
                ],
            )

    def test_generate_core_pdf_reuses_preprinted_notebook_pdfs_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            course = root / "Course_py"
            book = root / "Course_py_book"
            course.mkdir()
            book.mkdir()
            write_notebook(course / "demo_toc.ipynb", [markdown_cell("[First](lesson.ipynb)")])
            write_notebook(course / "lesson.ipynb", [markdown_cell("Text")])
            write_single_page_pdf(book / "lesson - Jupyter Notebook.pdf")
            output = course / "core_pdf" / "course_core.pdf"

            with mock.patch(
                "edu_publish.core_pdf.subprocess.run",
                side_effect=fake_export_run,
            ) as run_mock:
                with mock.patch(
                    "edu_publish.core_pdf.ensure_mathjax_assets",
                    return_value="_mathjax/MathJax.js?config=TeX-AMS-MML_HTMLorMML",
                ):
                    result = generate_core_pdf_from_notebooks(course, output)

            self.assertTrue(result.generated)
            self.assertEqual(result.renderer, "printed")
            self.assertTrue((result.parts_dir / "lesson.pdf").exists())
            exported_notebooks = [call.args[0][-1] for call in run_mock.call_args_list[0::2]]
            self.assertEqual(exported_notebooks, ["00_cover.ipynb", "demo_toc.ipynb"])

    def test_generate_core_pdf_warns_but_reuses_raw_preprinted_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            course = root / "Course_py"
            book = root / "Course_py_book"
            course.mkdir()
            book.mkdir()
            write_notebook(course / "demo_toc.ipynb", [markdown_cell("[First](lesson.ipynb)")])
            write_notebook(
                course / "lesson.ipynb",
                [markdown_cell("### Heading\n\n\\begin{equation}\nE=mc^2\n\\end{equation}")],
            )
            write_single_page_pdf(book / "lesson - Jupyter Notebook.pdf")
            output = course / "core_pdf" / "course_core.pdf"

            with mock.patch(
                "edu_publish.core_pdf.preprinted_notebook_pdf_is_rendered",
                side_effect=lambda notebook, pdf: notebook.name != "lesson.ipynb",
            ) as rendered_mock, mock.patch(
                "edu_publish.core_pdf.sys.stderr"
            ), mock.patch(
                "edu_publish.core_pdf.subprocess.run",
                side_effect=fake_export_run,
            ) as run_mock, mock.patch(
                "edu_publish.core_pdf.ensure_mathjax_assets",
                return_value="_mathjax/MathJax.js?config=TeX-AMS-MML_HTMLorMML",
            ):
                result = generate_core_pdf_from_notebooks(course, output)

            self.assertTrue(result.generated)
            self.assertTrue(rendered_mock.called)
            exported_notebooks = [call.args[0][-1] for call in run_mock.call_args_list[0::2]]
            self.assertEqual(exported_notebooks, ["00_cover.ipynb", "demo_toc.ipynb"])


def fake_export_run(command, cwd=None, capture_output=None, text=None, timeout=None):
    if len(command) >= 3 and command[:3] == [command[0], "-m", "nbconvert"]:
        output_dir = Path(command[command.index("--output-dir") + 1])
        output_name = command[command.index("--output") + 1]
        output_dir.mkdir(parents=True, exist_ok=True)
        html_path = output_dir / f"{output_name}.html"
        html_path.write_text("<html><body>ok</body></html>", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    if command and (
        command[0].endswith("chrome.exe") or command[0].endswith("msedge.exe")
    ):
        pdf_arg = next(arg for arg in command if arg.startswith("--print-to-pdf="))
        pdf_path = Path(pdf_arg.split("=", 1)[1])
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with pdf_path.open("wb") as handle:
            writer.write(handle)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    raise AssertionError(f"Unexpected command: {command}")


def fake_nbclassic_print_run(command, cwd=None, capture_output=None, text=None, timeout=None):
    if command and (
        command[0].endswith("chrome.exe") or command[0].endswith("msedge.exe")
    ):
        pdf_arg = next(arg for arg in command if arg.startswith("--print-to-pdf="))
        pdf_path = Path(pdf_arg.split("=", 1)[1])
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with pdf_path.open("wb") as handle:
            writer.write(handle)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    raise AssertionError(f"Unexpected command: {command}")


def write_single_page_pdf(path):
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with path.open("wb") as handle:
        writer.write(handle)


class FakeNbclassicServer:
    def __init__(self, root):
        self.root = Path(root)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def url_for_notebook(self, notebook_path):
        return f"http://nbclassic.local/nbconvert/html/{notebook_path.name}?download=false"


def write_notebook(path, cells):
    path.write_text(
        json.dumps(
            {
                "cells": cells,
                "metadata": {},
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


def code_cell(source, outputs=None):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": outputs or [],
        "source": source,
    }


def stream_output(text):
    return {
        "name": "stdout",
        "output_type": "stream",
        "text": text,
    }


if __name__ == "__main__":
    unittest.main()
