from fnmatch import fnmatchcase
from pathlib import Path
import json
import re
import shutil

from edu_publish.colab import ColabRepository
from edu_publish.notebook import Notebook

RESOURCE_DIRS = ("images", "figs", "img", "data")
NOTEBOOK_LINK_PATTERN = re.compile(r"(\]\()([^)]+?\.ipynb(?:#[^)]+)?)(\))")
COLAB_BADGE_IMAGE_URL = "https://colab.research.google.com/assets/colab-badge.svg"


class GitHubRepository:
    """Represents a GitHub repository associated with a course."""

    def __init__(self, course):
        self.course = course

    def notebook_url(self, notebook):
        repo = self.course.config.github_repo
        if not repo:
            raise ValueError("Course GitHub repository is not configured")

        branch = self.course.config.github_branch
        course_dir = self.course.config.github_course_dir.strip("/")
        path = f"{course_dir}/{notebook.filename}" if course_dir else notebook.filename
        return f"https://github.com/{repo}/blob/{branch}/{path}"

    def publication_report(self):
        lines = [
            f"TOC: {self.course.toc.name}",
            f"Found {len(self.course.notebooks)} notebooks:",
            "",
        ]

        for i, notebook in enumerate(self.course.notebooks, start=1):
            exists = "OK" if notebook.exists else "MISSING"
            lines.append(
                f"{i:02d}. {notebook.filename} [{exists}] {self.notebook_url(notebook)}"
            )

        return "\n".join(lines)

    def export(self, destination):
        destination = Path(destination)
        course_dir = self.course.config.github_course_dir.strip("/")
        if not course_dir:
            raise ValueError("Course GitHub directory is not configured")

        destination.mkdir(parents=True, exist_ok=True)
        (destination / "README.md").write_text(
            f"# {self.course.path.name}\n", encoding="utf-8"
        )
        (destination / ".gitignore").write_text(
            ".ipynb_checkpoints/\n__pycache__/\n", encoding="utf-8"
        )

        notebook_dir = destination / course_dir
        notebook_dir.mkdir(parents=True, exist_ok=True)

        for notebook_path in self._notebook_paths_for_export():
            target_path = notebook_dir / notebook_path.name
            shutil.copy2(notebook_path, target_path)

        if self.course.config.github_repo:
            self._update_exported_notebooks_for_colab(notebook_dir)

        for name in RESOURCE_DIRS:
            resource_dir = self.course.path / name
            if resource_dir.is_dir():
                target_dir = notebook_dir / name
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(
                    resource_dir,
                    target_dir,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".ipynb_checkpoints"),
                )

        return destination

    def _notebook_paths_for_export(self):
        pattern = self.course.config.notebook_include_pattern
        return sorted(
            path
            for path in self.course.path.glob("*.ipynb")
            if fnmatchcase(path.name, pattern)
        )

    def _update_exported_notebooks_for_colab(self, notebook_dir):
        colab = ColabRepository(self)
        notebook_urls = {
            path.name: colab.notebook_url(Notebook(self.course, path.name))
            for path in sorted(notebook_dir.glob("*.ipynb"))
        }

        for notebook_path in sorted(notebook_dir.glob("*.ipynb")):
            apply_colab_export_transformations(
                notebook_path,
                notebook_urls,
                notebook_urls[notebook_path.name],
            )


def apply_colab_export_transformations(notebook_path, notebook_urls, colab_url):
    notebook_path = Path(notebook_path)
    data = json.loads(notebook_path.read_text(encoding="utf-8"))
    changed = rewrite_notebook_links_in_data(data, notebook_urls)

    if insert_colab_badge_cell(data, colab_url):
        changed = True

    if changed:
        notebook_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )

    return changed


def insert_colab_badge_cell(data, colab_url):
    badge = colab_badge_markdown(colab_url)
    cells = data.setdefault("cells", [])

    if cells and cells[0].get("cell_type") == "markdown":
        source = cells[0].get("source", [])
        if source_text(source).strip() == badge:
            return False

    cells.insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [badge + "\n"],
        },
    )
    return True


def colab_badge_markdown(colab_url):
    return f"[![Open In Colab]({COLAB_BADGE_IMAGE_URL})]({colab_url})"


def source_text(source):
    if isinstance(source, list):
        return "".join(source)
    if isinstance(source, str):
        return source
    return ""


def rewrite_notebook_links(notebook_path, notebook_urls):
    notebook_path = Path(notebook_path)
    data = json.loads(notebook_path.read_text(encoding="utf-8"))
    changed = rewrite_notebook_links_in_data(data, notebook_urls)

    if changed:
        notebook_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )

    return changed


def rewrite_notebook_links_in_data(data, notebook_urls):
    changed = False

    for cell in data.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue

        source = cell.get("source", [])
        if isinstance(source, list):
            rewritten = [
                rewrite_markdown_notebook_links(part, notebook_urls)
                for part in source
            ]
            if rewritten != source:
                cell["source"] = rewritten
                changed = True
        elif isinstance(source, str):
            rewritten = rewrite_markdown_notebook_links(source, notebook_urls)
            if rewritten != source:
                cell["source"] = rewritten
                changed = True

    return changed


def rewrite_markdown_notebook_links(text, notebook_urls):
    def replace(match):
        link = match.group(2)
        target, separator, fragment = link.partition("#")

        if "://" in target:
            return match.group(0)

        filename = Path(target).name
        url = notebook_urls.get(filename)
        if not url:
            return match.group(0)

        if separator:
            url = f"{url}#{fragment}"

        return f"{match.group(1)}{url}{match.group(3)}"

    return NOTEBOOK_LINK_PATTERN.sub(replace, text)
