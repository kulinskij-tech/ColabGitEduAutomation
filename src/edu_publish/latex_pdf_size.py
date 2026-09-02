from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import re
import subprocess


PDF_SIZE_PATTERN = re.compile(r"(Обсяг\s+)(\d+(?:[,.]\d+)?)(\s*МБ\.)")


def run_latex_with_pdf_size(args: list[str]) -> str:
    options = parse_cli_options(args)
    if "--main" not in options:
        raise ValueError("latex-pdf-size requires --main path/to/main.tex")

    main = Path(options["--main"]).resolve()
    target = Path(options.get("--target", main)).resolve()
    engine = options.get("--engine", "xelatex")

    build_pdf(main, engine)
    pdf = main.with_suffix(".pdf")
    if not pdf.exists():
        raise FileNotFoundError(f"LaTeX did not create expected PDF: {pdf}")

    size_text = format_pdf_size_mb(pdf.stat().st_size)
    changed = update_pdf_size_text(target, size_text)
    build_pdf(main, engine)

    status = "updated" if changed else "already current"
    return f"{status}: {target} uses Обсяг {size_text} МБ. from {pdf.name}"


def parse_cli_options(args: list[str]) -> dict[str, str]:
    options: dict[str, str] = {}
    i = 0
    while i < len(args):
        name = args[i]
        if not name.startswith("--"):
            raise ValueError(f"Unexpected argument: {name}")
        if i + 1 >= len(args):
            raise ValueError(f"Missing value for {name}")
        options[name] = args[i + 1]
        i += 2
    return options


def build_pdf(main: Path, engine: str) -> None:
    subprocess.run(
        [
            engine,
            "-synctex=1",
            "-interaction=nonstopmode",
            main.name,
        ],
        cwd=main.parent,
        check=True,
    )


def format_pdf_size_mb(size_bytes: int) -> str:
    mb = Decimal(size_bytes) / Decimal(1_000_000)
    rounded = mb.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"{rounded:.1f}".replace(".", ",")


def update_pdf_size_text(target: Path, size_text: str) -> bool:
    text = target.read_text(encoding="utf-8", errors="replace")
    updated, count = PDF_SIZE_PATTERN.subn(rf"\g<1>{size_text}\g<3>", text, count=1)
    if count == 0:
        raise ValueError(f"Could not find Ukrainian PDF size marker in {target}")
    if updated == text:
        return False
    target.write_text(updated, encoding="utf-8")
    return True
