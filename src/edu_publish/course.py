from pathlib import Path

from edu_publish.toc import read_notebook_markdown, extract_notebook_links

from edu_publish.notebook import Notebook

class Course:
    """Represents a course directory."""

    def __init__(self, path):
        self.path = Path(path)
        self.toc = self._find_toc()
        self.notebooks = []
        self.missing = []

        self._discover()

    def _find_toc(self):
        toc_files = sorted(self.path.glob("*_toc.ipynb"))

        if not toc_files:
            raise FileNotFoundError(
                f"No TOC notebook matching '*_toc.ipynb' found in {self.path}"
            )

        if len(toc_files) > 1:
            names = ", ".join(path.name for path in toc_files)
            raise ValueError(
                f"Multiple TOC notebooks found in {self.path}: {names}"
            )

        return toc_files[0]

    def _discover(self):
        text = read_notebook_markdown(self.toc)

        links = extract_notebook_links(text)

        self.notebooks = [
        Notebook(self, filename)
        for filename in links
        ]

    def report(self):
        lines = [
            f"TOC: {self.toc.name}",
            f"Found {len(self.notebooks)} notebook links:",
            "",
        ]

        for i, notebook in enumerate(self.notebooks, start=1):
            exists = "OK" if notebook.exists else "MISSING"
            lines.append(
            f"{i:02d}. {notebook.filename} [{exists}]"
            )

        return "\n".join(lines)

    def __repr__(self):
        return f"Course({self.path!r})"