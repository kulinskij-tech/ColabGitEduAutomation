from pathlib import Path
import json
import re

TOC_NAME = "atomicphys_toc.ipynb"

link_pattern = re.compile(r"\]\(([^)]+\.ipynb)\)")


def read_notebook_markdown(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    parts = []
    for cell in data.get("cells", []):
        if cell.get("cell_type") == "markdown":
            src = cell.get("source", [])
            parts.append("".join(src))
    return "\n".join(parts)


def analyze_course(course: Path) -> None:
    toc = course / TOC_NAME
    text = read_notebook_markdown(toc)

    links = []
    for match in link_pattern.finditer(text):
        link = match.group(1)
        link = link.split("#")[0]
        link = Path(link).name
        if link not in links:
            links.append(link)

    print(f"TOC: {toc.name}")
    print(f"Found {len(links)} notebook links:\n")

    for i, link in enumerate(links, start=1):
        exists = "OK" if (course / link).exists() else "MISSING"
        print(f"{i:02d}. {link} [{exists}]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python src/edu_publish/discover.py /path/to/course")
        raise SystemExit(1)

    analyze_course(Path(sys.argv[1]))
