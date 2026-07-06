from pathlib import Path
import json
import re


link_pattern = re.compile(r"\]\(([^)]+\.ipynb)\)")


def read_notebook_markdown(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))

    parts = []
    for cell in data.get("cells", []):
        if cell.get("cell_type") == "markdown":
            src = cell.get("source", [])
            parts.append("".join(src))

    return "\n".join(parts)


def extract_notebook_links(text: str) -> list[str]:
    links = []

    for match in link_pattern.finditer(text):
        link = match.group(1)
        link = link.split("#")[0]
        link = Path(link).name

        if link not in links:
            links.append(link)

    return links