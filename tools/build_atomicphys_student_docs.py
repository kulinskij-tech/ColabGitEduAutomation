from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


REPO_URL = "https://github.com/kulinskij-tech/AtomicPhys"
COLAB_TOC_URL = (
    "https://colab.research.google.com/github/kulinskij-tech/"
    "AtomicPhys/blob/main/Atomic_py/atomicphys_toc.ipynb"
)


def register_fonts() -> tuple[str, str, str]:
    fonts = Path(r"C:\Windows\Fonts")
    regular = fonts / "arial.ttf"
    bold = fonts / "arialbd.ttf"
    italic = fonts / "ariali.ttf"
    if regular.exists() and bold.exists() and italic.exists():
        pdfmetrics.registerFont(TTFont("DocSans", str(regular)))
        pdfmetrics.registerFont(TTFont("DocSans-Bold", str(bold)))
        pdfmetrics.registerFont(TTFont("DocSans-Italic", str(italic)))
        return "DocSans", "DocSans-Bold", "DocSans-Italic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


FONT, FONT_BOLD, FONT_ITALIC = register_fonts()


def styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            name="DocTitle",
            fontName=FONT_BOLD,
            fontSize=21,
            leading=25,
            alignment=TA_CENTER,
            spaceAfter=14,
            textColor=colors.HexColor("#17324d"),
        )
    )
    base.add(
        ParagraphStyle(
            name="Subtitle",
            fontName=FONT,
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor("#44546a"),
        )
    )
    base.add(
        ParagraphStyle(
            name="Heading",
            fontName=FONT_BOLD,
            fontSize=13,
            leading=16,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor("#17324d"),
        )
    )
    base.add(
        ParagraphStyle(
            name="BodyDoc",
            fontName=FONT,
            fontSize=10,
            leading=14,
            spaceAfter=6,
            alignment=TA_LEFT,
        )
    )
    base.add(
        ParagraphStyle(
            name="Small",
            fontName=FONT,
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#4d4d4d"),
        )
    )
    base.add(
        ParagraphStyle(
            name="Button",
            fontName=FONT_BOLD,
            fontSize=12,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.white,
        )
    )
    return base


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def link(text: str, url: str) -> str:
    return f'<a href="{url}" color="#0b57d0">{esc(text)}</a>'


def colored_link(text: str, url: str, color: str) -> str:
    return f'<a href="{url}" color="{color}">{esc(text)}</a>'


def extract_toc(atomic_dir: Path) -> tuple[str, list[str], list[str]]:
    toc = atomic_dir / "Atomic_py" / "atomicphys_toc.ipynb"
    nb = json.loads(toc.read_text(encoding="utf-8"))
    markdown = "\n\n".join(
        "".join(cell.get("source", []))
        for cell in nb.get("cells", [])
        if cell.get("cell_type") == "markdown"
    )
    annotation_match = re.search(
        r"Посібник містить.*?практичними заняттями\.", markdown, re.S
    )
    annotation = (
        annotation_match.group(0).replace("\n", " ").strip()
        if annotation_match
        else (
            "Посібник містить теоретичний матеріал, приклади та задачі для "
            "практичних занять з курсу Фізика атома."
        )
    )
    sections: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"\s*-\s+\[([^\]]+)\]\(\./(atomicphys_[^)]+\.ipynb)\)", line)
        if not match:
            continue
        title = re.sub(r"<br\s*/?>", "", match.group(1)).strip()
        if title != "Задачі":
            sections.append(title)
    references = [
        "Irodov I.E. Problems in General Physics, Mir Publishers, 1988.",
        "Yung-Kuo Lim. Problems and Solutions on Mechanics, World Scientific, 2005.",
    ]
    return annotation, sections, references


def bullet_list(items: list[str], style: ParagraphStyle) -> Table:
    return Table(
        [["-", Paragraph(esc(item), style)] for item in items],
        colWidths=[0.35 * cm, None],
        style=TableStyle(
            [
                ("FONT", (0, 0), (0, -1), FONT_BOLD),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        ),
    )


def numbered_list(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=12) for item in items],
        bulletType="1",
        leftIndent=18,
    )


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(1.8 * cm, 1.15 * cm, "Atomic Physics")
    canvas.drawRightString(19.2 * cm, 1.15 * cm, f"{doc.page}")
    canvas.restoreState()


def build_howto(output: Path) -> None:
    s = styles()
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
        title="Atomic Physics - How to Start",
    )
    story = [
        Paragraph("Atomic Physics — How to Start", s["DocTitle"]),
        Paragraph("Student quick guide for the Jupyter notebook course", s["Subtitle"]),
        Spacer(1, 0.2 * cm),
        Table(
            [
                [
                    Paragraph(
                        colored_link("Open Atomic Physics in Google Colab", COLAB_TOC_URL, "white"),
                        s["Button"],
                    )
                ]
            ],
            colWidths=[15.5 * cm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0b57d0")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#0b57d0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            ),
        ),
        Spacer(1, 0.45 * cm),
        Paragraph("What You Need", s["Heading"]),
        bullet_list(
            [
                "A web browser.",
                "A Google account is recommended if you want to save your own notebook copies.",
                "No local Python setup is required for the Colab workflow.",
            ],
            s["BodyDoc"],
        ),
        Paragraph("Start From The Table Of Contents", s["Heading"]),
        Paragraph(
            "Use the course table of contents notebook, "
            + link("Atomic_py/atomicphys_toc.ipynb", COLAB_TOC_URL)
            + ". It links the theory notebooks, practical problem notebooks, figures, and technical notes.",
            s["BodyDoc"],
        ),
        Paragraph("How To Work With A Notebook", s["Heading"]),
        numbered_list(
            [
                "Open the TOC link above and choose a topic notebook.",
                "Read the text, formulas, and figure captions before running code cells.",
                "Run executable cells with the play button on the left of each cell.",
                "If a notebook asks for a package or runtime restart, follow the Colab prompt and rerun the affected cells.",
                "Use the links inside the TOC to move between theory, examples, and problem sets.",
            ],
            s["BodyDoc"],
        ),
        Paragraph("Saving Your Work", s["Heading"]),
        Paragraph(
            "In Colab, use <b>File → Save a copy in Drive</b>. Work in your own copy when solving tasks, adding notes, or changing code.",
            s["BodyDoc"],
        ),
        Paragraph("Repository And Offline PDF", s["Heading"]),
        Paragraph(
            "The source notebooks are in "
            + link("github.com/kulinskij-tech/AtomicPhys", REPO_URL)
            + ". The compiled course PDF is useful for reading and reference, while notebooks remain the working format for code execution.",
            s["BodyDoc"],
        ),
        Paragraph("If Something Does Not Open", s["Heading"]),
        bullet_list(
            [
                "Reload the Colab page.",
                "Open the same notebook from the GitHub repository.",
                "Check whether browser pop-up blocking prevented a new Colab tab.",
                "If formulas look like raw LaTeX in a printed PDF, use the notebook or a freshly rendered notebook print.",
            ],
            s["BodyDoc"],
        ),
    ]
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def build_syllabus(output: Path, atomic_dir: Path) -> None:
    annotation, sections, references = extract_toc(atomic_dir)
    s = styles()
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.6 * cm,
        title="Syllabus - Atomic Physics",
    )

    info = [
        ["Discipline", "Фізика атома / Atomic Physics"],
        ["Course Type", "Навчальна дисципліна для студентів 3 курсу"],
        ["Department", "Кафедра фізики та астрономії"],
        ["School", "Факультет математики, фізики та інформаційних технологій"],
        ["Instructor", "проф., д-р ф.-м.н. Кулінський В.Л."],
        ["Digital Materials", f"{REPO_URL}\n{COLAB_TOC_URL}"],
    ]
    table = Table(
        [[Paragraph(f"<b>{esc(k)}</b>", s["BodyDoc"]), Paragraph(esc(v), s["BodyDoc"])] for k, v in info],
        colWidths=[4.2 * cm, 12.2 * cm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef3f8")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c9d3df")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        ),
    )

    topic_groups = [
        (
            "Module 1. Quantum Phenomena And Foundations",
            [
                "Квантова природа світла: фотони, фото- і Комптон-ефект.",
                "Модель атома Резерфорда-Бора та правила квантування.",
                "Корпускулярно-хвильовий дуалізм і гіпотеза де Бройля.",
                "Ймовірнісний зміст хвильової функції та обчислення середніх.",
                "Рівняння Шредінгера для простих систем.",
            ],
        ),
        (
            "Module 2. Atomic Structure",
            [
                "Оператори фізичних величин, момент імпульсу, спін.",
                "Задача Кеплера у квантовій механіці; спектр атома водню.",
                "Атом гелію, багатоелектронні атоми, терми.",
                "Періодична система з точки зору квантової теорії.",
                "Атом у зовнішньому електричному та магнітному полі.",
            ],
        ),
        (
            "Module 3. Spectra And Applications",
            [
                "Випромінювання світла атомами та спонтанне випромінювання.",
                "Особливості рентгенівських спектрів атомів.",
                "Молекули, адіабатичне наближення, коливальні та обертальні спектри.",
                "Практичні задачі й Jupyter-notebook представлення результатів.",
            ],
        ),
    ]

    story = [
        Paragraph("Syllabus", s["DocTitle"]),
        Paragraph("Фізика атома / Atomic Physics", s["Subtitle"]),
        table,
        Paragraph("Annotation", s["Heading"]),
        Paragraph(esc(annotation), s["BodyDoc"]),
        Paragraph("Course Aim", s["Heading"]),
        Paragraph(
            esc(
                "Вивчення основних положень атомної теорії та методів розв'язків задач; "
                "формування навичок аналізу квантових явищ."
            ),
            s["BodyDoc"],
        ),
        Paragraph("Learning Outcomes", s["Heading"]),
        bullet_list(
            [
                "Пояснювати базові квантові моделі світла, частинок та атомів.",
                "Оцінювати основні фізичні величини в атомній фізиці.",
                "Розв'язувати типові задачі з атомної та квантової фізики.",
                "Працювати з Jupyter notebooks, Python-кодом, графіками і LaTeX-поданням результатів.",
            ],
            s["BodyDoc"],
        ),
        Paragraph("Prerequisites", s["Heading"]),
        Paragraph(
            "General physics, mathematical analysis, linear algebra, differential equations, and basic Python/Jupyter skills.",
            s["BodyDoc"],
        ),
        Paragraph("Course Content", s["Heading"]),
    ]
    for heading, items in topic_groups:
        story.extend(
            [
                KeepTogether([Paragraph(f"<b>{esc(heading)}</b>", s["BodyDoc"]), bullet_list(items, s["BodyDoc"])]),
                Spacer(1, 0.1 * cm),
            ]
        )

    story.extend(
        [
            Paragraph("Notebook Topic List", s["Heading"]),
            bullet_list(sections[:18], s["Small"]),
            PageBreak(),
            Paragraph("Interactive Materials", s["Heading"]),
            Paragraph(
                "The course is organized as Jupyter notebooks with Python, Matplotlib, NumPy, SciPy, SymPy, and LaTeX/MathJax notation. "
                "Start from "
                + link("atomicphys_toc.ipynb", COLAB_TOC_URL)
                + " or browse the repository at "
                + link("kulinskij-tech/AtomicPhys", REPO_URL)
                + ".",
                s["BodyDoc"],
            ),
            Paragraph("Assessment Model", s["Heading"]),
            Table(
                [
                    ["Activity", "Share"],
                    ["Practical notebook/problem work", "40%"],
                    ["Module tests or control tasks", "30%"],
                    ["Independent work and presentation of results", "20%"],
                    ["Participation and current preparation", "10%"],
                ],
                colWidths=[11.0 * cm, 3.0 * cm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324d")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONT", (0, 0), (-1, 0), FONT_BOLD),
                        ("FONT", (0, 1), (-1, -1), FONT),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c9d3df")),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                ),
            ),
            Paragraph("Recommended Literature", s["Heading"]),
            numbered_list([esc(item) for item in references], s["BodyDoc"]),
            Paragraph("Course Policies", s["Heading"]),
            bullet_list(
                [
                    "Work submitted in notebooks should contain executable code, final numerical or symbolic results, and short explanatory comments.",
                    "Copied code or copied solutions must be clearly attributed.",
                    "Late or incomplete work is handled according to the department policy announced by the instructor.",
                ],
                s["BodyDoc"],
            ),
        ]
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def write_markdown(path: Path, title: str, body: str) -> None:
    path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atomic-dir", type=Path, required=True)
    args = parser.parse_args()
    atomic_dir = args.atomic_dir
    atomic_dir.mkdir(parents=True, exist_ok=True)
    syllabus_dir = atomic_dir / "AtomicPhys_syllabus"
    syllabus_dir.mkdir(parents=True, exist_ok=True)

    howto_pdf = atomic_dir / "AtomicPhys_student_howto.pdf"
    syllabus_pdf = syllabus_dir / "AtomicPhys_syllabus.pdf"
    build_howto(howto_pdf)
    build_syllabus(syllabus_pdf, atomic_dir)

    write_markdown(
        atomic_dir / "AtomicPhys_student_howto.md",
        "Atomic Physics — How to Start",
        f"""
Open the course TOC in Colab: {COLAB_TOC_URL}

Use `Atomic_py/atomicphys_toc.ipynb` as the starting point. Read the text and
formulas, run executable cells with the play button, and save your own working
copy with `File -> Save a copy in Drive`.

Repository: {REPO_URL}
""",
    )
    write_markdown(
        syllabus_dir / "AtomicPhys_syllabus.md",
        "Фізика атома / Atomic Physics — Syllabus",
        f"""
Interactive materials are maintained in the AtomicPhys notebook collection:
{REPO_URL}

Start notebook:
{COLAB_TOC_URL}
""",
    )

    print(howto_pdf)
    print(syllabus_pdf)


if __name__ == "__main__":
    main()
