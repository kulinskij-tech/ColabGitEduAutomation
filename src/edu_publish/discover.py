from pathlib import Path
import json
import re

COURSE = Path(
    r"C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\AtomicPhys\Atomic_py"
)

TOC = COURSE / "atomicphys_toc.ipynb"

link_pattern = re.compile(r"\]\(([^)]+\.ipynb)\)")

def read_notebook_markdown(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    parts = []
    for cell in data.get("cells", []):
        if cell.get("cell_type") == "markdown":
            src = cell.get("source", [])
            parts.append("".join(src))
    return "\n".join(parts)

text = read_notebook_markdown(TOC)

links = []
for match in link_pattern.finditer(text):
    link = match.group(1)
    link = link.split("#")[0]
    link = Path(link).name
    if link not in links:
        links.append(link)

print(f"TOC: {TOC.name}")
print(f"Found {len(links)} notebook links:\n")

for i, link in enumerate(links, start=1):
    exists = "OK" if (COURSE / link).exists() else "MISSING"
    print(f"{i:02d}. {link} [{exists}]")