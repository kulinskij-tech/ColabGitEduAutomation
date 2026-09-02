from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re
import socket
import shutil
import subprocess
import sys
import threading
import time
from urllib.parse import quote
from urllib.request import urlopen

from PyPDF2 import PdfMerger, PdfReader

from edu_publish.course import Course
from edu_publish.config import CourseConfig
from edu_publish.github import (
    GitHubRepository,
    RESOURCE_DIRS,
    rewrite_notebook_links_in_data,
)
from edu_publish.notebook import Notebook


DEFAULT_TITLE = "Електронний методичний посібник"
DEFAULT_AUTHOR = "Кулінський В.Л."
DEFAULT_SUBTITLE = "Матеріали курсу, згенеровані з Jupyter notebooks"
DEFAULT_RENDERER = "printed"
CHROME_EXECUTABLES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
)
MATHJAX_CANDIDATES = (
    Path(sys.prefix)
    / "Lib"
    / "site-packages"
    / "nbclassic"
    / "static"
    / "components"
    / "MathJax"
    / "MathJax.js",
    Path(sys.prefix)
    / "share"
    / "jupyter"
    / "nbclassic"
    / "static"
    / "components"
    / "MathJax"
    / "MathJax.js",
)


@dataclass
class CorePdfResult:
    pdf_path: Path
    staging_dir: Path
    parts_dir: Path
    generated: bool
    merged: bool = True
    exported_notebooks: int = 0
    renderer: str = DEFAULT_RENDERER


def run_generate_core_pdf(args: list[str]) -> str:
    options = parse_cli_options(args)
    if len(options.positionals) != 1:
        raise ValueError("generate-core-pdf requires COURSE_DIR")

    course_dir = Path(options.positionals[0]).resolve()
    output = Path(
        options.values.get("--output", course_dir / "core_pdf" / "course_core.pdf")
    ).resolve()
    if output.suffix.lower() == ".tex":
        output = output.with_suffix(".pdf")

    force = "--force" in options.flags
    no_merge = "--no-compile" in options.flags
    renderer = options.values.get("--renderer", DEFAULT_RENDERER)

    result = generate_core_pdf_from_notebooks(
        course_dir=course_dir,
        output_pdf=output,
        title=options.values.get("--title", DEFAULT_TITLE),
        author=options.values.get("--author", DEFAULT_AUTHOR),
        subtitle=options.values.get("--subtitle", DEFAULT_SUBTITLE),
        notebook_pattern=options.values.get("--notebooks", "*.ipynb"),
        github_repo=options.values.get("--repo"),
        github_branch=options.values.get("--branch", "main"),
        github_course_dir=options.values.get("--github-course-dir", course_dir.name),
        force=force,
        merge_pdf=not no_merge,
        renderer=renderer,
    )

    if not result.generated:
        return f"skipped existing core PDF: {result.pdf_path}"
    if result.merged:
        return f"generated core PDF: {result.pdf_path}"
    return f"exported notebook PDFs: {result.parts_dir}"


@dataclass
class ParsedOptions:
    positionals: list[str]
    values: dict[str, str]
    flags: set[str]


def parse_cli_options(args: list[str]) -> ParsedOptions:
    values: dict[str, str] = {}
    flags: set[str] = set()
    positionals: list[str] = []
    flag_names = {"--force", "--no-compile"}

    i = 0
    while i < len(args):
        name = args[i]
        if not name.startswith("--"):
            positionals.append(name)
            i += 1
            continue
        if name in flag_names:
            flags.add(name)
            i += 1
            continue
        if i + 1 >= len(args):
            raise ValueError(f"Missing value for {name}")
        values[name] = args[i + 1]
        i += 2
    return ParsedOptions(positionals=positionals, values=values, flags=flags)


def generate_core_pdf_from_notebooks(
    course_dir: Path,
    output_pdf: Path,
    title: str = DEFAULT_TITLE,
    author: str = DEFAULT_AUTHOR,
    subtitle: str = DEFAULT_SUBTITLE,
    notebook_pattern: str = "*.ipynb",
    github_repo: str | None = None,
    github_branch: str = "main",
    github_course_dir: str = "",
    force: bool = False,
    merge_pdf: bool = True,
    renderer: str = DEFAULT_RENDERER,
) -> CorePdfResult:
    output_pdf = Path(output_pdf)
    if output_pdf.suffix.lower() != ".pdf":
        output_pdf = output_pdf.with_suffix(".pdf")

    if output_pdf.exists() and not force:
        parts_dir = output_pdf.parent / f"{output_pdf.stem}_parts"
        staging_dir = output_pdf.parent / f"{output_pdf.stem}_staging"
        return CorePdfResult(
            pdf_path=output_pdf,
            staging_dir=staging_dir,
            parts_dir=parts_dir,
            generated=False,
            merged=output_pdf.exists(),
            exported_notebooks=0,
            renderer=renderer,
        )

    course = Course(
        course_dir,
        CourseConfig(
            github_repo=github_repo,
            github_branch=github_branch,
            github_course_dir=github_course_dir,
            notebook_include_pattern=notebook_pattern,
        ),
    )

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    parts_dir = output_pdf.parent / f"{output_pdf.stem}_parts"
    staging_dir = output_pdf.parent / f"{output_pdf.stem}_staging"

    if force:
        remove_path(parts_dir)
        remove_path(staging_dir)

    staged_notebooks = stage_course_for_pdf(course, staging_dir, title, author, subtitle)

    exported_parts = export_notebooks_to_pdf(staged_notebooks, parts_dir, renderer)

    if merge_pdf:
        merge_pdfs(exported_parts, output_pdf)

    return CorePdfResult(
        pdf_path=output_pdf,
        staging_dir=staging_dir,
        parts_dir=parts_dir,
        generated=True,
        merged=merge_pdf,
        exported_notebooks=len(exported_parts),
        renderer=renderer,
    )


def stage_course_for_pdf(
    course: Course,
    staging_dir: Path,
    title: str,
    author: str,
    subtitle: str,
) -> list[Path]:
    staging_dir.mkdir(parents=True, exist_ok=True)
    notebook_paths = collect_notebook_paths(course)
    copied_paths: list[Path] = []

    for notebook_path in notebook_paths:
        target_path = staging_dir / notebook_path.name
        shutil.copy2(notebook_path, target_path)
        printed_pdf = find_preprinted_notebook_pdf(notebook_path)
        if printed_pdf:
            if not preprinted_notebook_pdf_is_rendered(notebook_path, printed_pdf):
                print(
                    "warning: pre-printed PDF appears to contain raw markdown/TeX "
                    f"and should be reprinted from Jupyter: {printed_pdf}",
                    file=sys.stderr,
                )
            shutil.copy2(printed_pdf, target_path.with_suffix(".pdf"))
        copied_paths.append(target_path)

    copy_resource_directories(course.path, staging_dir)
    rewrite_staged_notebooks(course, copied_paths)

    cover_path = staging_dir / "00_cover.ipynb"
    write_cover_notebook(
        cover_path,
        course=course,
        title=title,
        author=author,
        subtitle=subtitle,
        notebook_paths=notebook_paths,
    )

    return [cover_path, *copied_paths]


def collect_notebook_paths(course: Course) -> list[Path]:
    paths = [course.toc.path, *(notebook.path for notebook in course.notebooks)]
    unique_paths: list[Path] = []
    seen: set[Path] = set()

    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        if not path.exists():
            continue
        seen.add(resolved)
        unique_paths.append(path)

    return unique_paths


def copy_resource_directories(source_dir: Path, staging_dir: Path) -> None:
    for name in RESOURCE_DIRS:
        resource_dir = source_dir / name
        if not resource_dir.is_dir():
            continue
        target_dir = staging_dir / name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(
            resource_dir,
            target_dir,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".ipynb_checkpoints"),
        )


def rewrite_staged_notebooks(course: Course, staged_paths: list[Path]) -> None:
    if not course.config.github_repo:
        for notebook_path in staged_paths:
            data = json.loads(notebook_path.read_text(encoding="utf-8"))
            changed = sanitize_widget_outputs(data)
            if changed:
                notebook_path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8",
                )
        return

    github = GitHubRepository(course)
    notebook_urls = dict(course.config.external_notebook_urls)
    notebook_urls.update(
        {
            path.name: github.notebook_url(Notebook(course, path.name))
            for path in collect_notebook_paths(course)
        }
    )

    for notebook_path in staged_paths:
        data = json.loads(notebook_path.read_text(encoding="utf-8"))
        changed = rewrite_notebook_links_in_data(data, notebook_urls)
        if sanitize_widget_outputs(data):
            changed = True
        if changed:
            notebook_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8",
            )


def write_cover_notebook(
    cover_path: Path,
    course: Course,
    title: str,
    author: str,
    subtitle: str,
    notebook_paths: list[Path],
) -> None:
    course_label = course.path.name
    notebook_lines = []
    if course.config.github_repo:
        github = GitHubRepository(course)
        for notebook_path in notebook_paths:
            notebook = Notebook(course, notebook_path.name)
            notebook_lines.append(f"- [{notebook_path.name}]({github.notebook_url(notebook)})")
    else:
        for notebook_path in notebook_paths:
            notebook_lines.append(f"- {notebook_path.name}")

    cover = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "<div align=\"center\">\n",
                    f"\n# {title}\n",
                    f"\n**{author}**\n",
                    f"\n{subtitle}\n",
                    f"\n{course_label}\n",
                    f"\n{date.today().isoformat()}\n",
                    "\n</div>\n",
                ],
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Notebook order\n", *[line + "\n" for line in notebook_lines]],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    cover_path.write_text(
        json.dumps(cover, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )


def sanitize_widget_outputs(data: dict) -> bool:
    changed = False

    metadata = data.get("metadata")
    if isinstance(metadata, dict) and "widgets" in metadata:
        metadata.pop("widgets", None)
        changed = True

    for cell in data.get("cells", []):
        if remove_visible_mathjax_setup(cell):
            changed = True
            continue

        if cell.get("cell_type") != "code":
            continue

        metadata = cell.get("metadata")
        if isinstance(metadata, dict) and "widgets" in metadata:
            metadata.pop("widgets", None)
            changed = True
            if not metadata:
                cell.pop("metadata", None)

        outputs = cell.get("outputs", [])
        for output in outputs:
            if not isinstance(output, dict):
                continue

            output_metadata = output.get("metadata")
            if isinstance(output_metadata, dict) and "widgets" in output_metadata:
                output_metadata.pop("widgets", None)
                changed = True
                if not output_metadata:
                    output.pop("metadata", None)

            output_data = output.get("data")
            if isinstance(output_data, dict):
                widget_keys = [
                    key
                    for key in output_data
                    if key.startswith("application/vnd.jupyter.widget")
                ]
                if widget_keys:
                    for key in widget_keys:
                        output_data.pop(key, None)
                    changed = True
                    if not output_data:
                        output.pop("data", None)

            if output.get("output_type") == "display_data" and not output.get("data"):
                output["data"] = {"text/plain": "[widget output omitted]"}
                changed = True

    return changed


def find_preprinted_notebook_pdf(notebook_path: Path) -> Path | None:
    stem = notebook_path.stem
    course_dir = notebook_path.parent
    sibling_book_dir = course_dir.parent / f"{course_dir.name}_book"
    candidates = [
        course_dir / f"{stem} - Jupyter Notebook.pdf",
        course_dir / f"{stem}_Jupyter Notebook.pdf",
        sibling_book_dir / f"{stem} - Jupyter Notebook.pdf",
        sibling_book_dir / f"{stem}_Jupyter Notebook.pdf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def preprinted_notebook_pdf_is_rendered(notebook_path: Path, pdf_path: Path) -> bool:
    raw_markers = raw_markdown_markers_for_notebook(notebook_path)
    if not raw_markers:
        return True

    try:
        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return False

    return not any(marker in text for marker in raw_markers)


def raw_markdown_markers_for_notebook(notebook_path: Path) -> set[str]:
    try:
        data = json.loads(notebook_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return set()

    markers: set[str] = set()
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", [])
        text = "".join(source) if isinstance(source, list) else str(source)
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                markers.add(stripped)
                if len(stripped) > 40:
                    markers.add(stripped[:40])
    return markers


def remove_visible_mathjax_setup(cell: dict) -> bool:
    source = cell.get("source", [])
    if isinstance(source, list):
        text = "".join(source)
    elif isinstance(source, str):
        text = source
    else:
        return False

    if "MathJax.Hub.Config" not in text:
        return False

    cell["cell_type"] = "raw"
    cell["source"] = []
    cell["metadata"] = {"edu_publish": {"removed": "mathjax setup cell"}}
    return True


def export_notebooks_to_pdf(
    notebook_paths: list[Path],
    parts_dir: Path,
    renderer: str,
) -> list[Path]:
    if renderer == "printed":
        return [
            export_preprinted_or_html_notebook_to_pdf(notebook_path, parts_dir)
            for notebook_path in notebook_paths
        ]
    if renderer == "html":
        return [export_notebook_to_pdf(notebook_path, parts_dir) for notebook_path in notebook_paths]
    if renderer != "nbclassic":
        raise ValueError("renderer must be 'printed', 'html', or 'nbclassic'")

    with NbclassicServer(notebook_paths[0].parent) as server:
        return [
            print_nbclassic_notebook_to_pdf(server.url_for_notebook(notebook_path), notebook_path, parts_dir)
            for notebook_path in notebook_paths
        ]


def export_preprinted_or_html_notebook_to_pdf(notebook_path: Path, parts_dir: Path) -> Path:
    preprinted = notebook_path.with_suffix(".pdf")
    target = parts_dir / f"{notebook_path.stem}.pdf"
    parts_dir.mkdir(parents=True, exist_ok=True)
    if preprinted.exists():
        shutil.copy2(preprinted, target)
        return target
    return export_notebook_to_pdf(notebook_path, parts_dir)


class NbclassicServer:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.port = find_free_port()
        self.token = "edu-publish"
        self.process: subprocess.Popen | None = None

    def __enter__(self) -> "NbclassicServer":
        command = [
            sys.executable,
            "-m",
            "jupyter",
            "nbclassic",
            "--no-browser",
            "--ip=127.0.0.1",
            f"--port={self.port}",
            f"--ServerApp.token={self.token}",
            "--ServerApp.password=",
            "--ServerApp.disable_check_xsrf=True",
        ]
        self.process = subprocess.Popen(
            command,
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self._wait_until_ready()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.process is None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=10)

    def url_for_notebook(self, notebook_path: Path) -> str:
        relative = notebook_path.relative_to(self.root).as_posix()
        encoded = quote(relative)
        return (
            f"http://127.0.0.1:{self.port}/nbconvert/html/{encoded}"
            f"?download=false&token={self.token}"
        )

    def _wait_until_ready(self) -> None:
        url = f"http://127.0.0.1:{self.port}/tree?token={self.token}"
        deadline = time.time() + 30
        last_output = ""
        while time.time() < deadline:
            if self.process is not None and self.process.poll() is not None:
                if self.process.stdout is not None:
                    last_output = self.process.stdout.read() or ""
                raise RuntimeError(f"nbclassic exited before it was ready:\n{last_output}")
            try:
                with urlopen(url, timeout=1):
                    return
            except OSError:
                time.sleep(0.5)
        raise TimeoutError(f"Timed out waiting for nbclassic at {url}")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return server.getsockname()[1]


def print_nbclassic_notebook_to_pdf(url: str, notebook_path: Path, parts_dir: Path) -> Path:
    parts_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = parts_dir / f"{notebook_path.stem}.pdf"
    chrome = find_browser_executable()
    command = [
        str(chrome),
        "--headless",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-extensions",
        "--hide-scrollbars",
        "--no-first-run",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",
        f"--print-to-pdf={pdf_path}",
        "--print-to-pdf-no-header",
        url,
    ]
    try:
        result = subprocess.run(
            command,
            cwd=notebook_path.parent,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"Timed out printing {notebook_path.name} from nbclassic"
        ) from exc
    if result.returncode != 0 and not pdf_path.exists():
        raise RuntimeError(
            f"Failed to print {notebook_path.name} from nbclassic:\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return pdf_path


def export_notebook_to_pdf(notebook_path: Path, parts_dir: Path) -> Path:
    parts_dir.mkdir(parents=True, exist_ok=True)
    html_path = parts_dir / f"{notebook_path.stem}.html"
    pdf_path = parts_dir / f"{notebook_path.stem}.pdf"
    export_notebook_to_html(notebook_path, parts_dir, html_path)
    copy_resource_directories(notebook_path.parent, parts_dir)
    print_html_to_pdf(html_path, pdf_path)

    return pdf_path


def export_notebook_to_html(notebook_path: Path, parts_dir: Path, html_path: Path) -> None:
    mathjax_url = ensure_mathjax_assets(parts_dir)
    command = [
        sys.executable,
        "-m",
        "nbconvert",
        "--to",
        "html",
        "--output-dir",
        str(parts_dir),
        "--output",
        notebook_path.stem,
        f"--HTMLExporter.mathjax_url={mathjax_url}",
        notebook_path.name,
    ]
    result = subprocess.run(
        command,
        cwd=notebook_path.parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and not html_path.exists():
        raise RuntimeError(
            f"Failed to export {notebook_path.name} to HTML:\n"
            f"{result.stdout}\n{result.stderr}"
        )
    prepare_html_for_pdf_math(html_path)


def prepare_html_for_pdf_math(html_path: Path) -> None:
    text = html_path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(
        r"<script[^>]+src=[\"']https?://[^\"']+[\"'][^>]*>\s*</script>\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    mathjax_config = r"""
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  tex2jax: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true
  },
  TeX: { equationNumbers: { autoNumber: "AMS" } },
  messageStyle: "none"
});
</script>
<style>
body { visibility: hidden; }
body.mathjax-ready { visibility: visible; }
@media print {
  .jp-InputPrompt, .jp-OutputPrompt { color: transparent !important; }
}
</style>
<script>
(function () {
  function reveal() {
    document.body.classList.add("mathjax-ready");
  }
  function typesetWhenReady() {
    if (window.MathJax && MathJax.Hub) {
      MathJax.Hub.Queue(["Typeset", MathJax.Hub], reveal);
      return;
    }
    window.setTimeout(typesetWhenReady, 50);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", typesetWhenReady);
  } else {
    typesetWhenReady();
  }
  window.setTimeout(reveal, 15000);
})();
</script>
"""
    text = re.sub(
        r"<script\s+type=[\"']text/x-mathjax-config[\"']>.*?</script>\s*",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    mathjax_script = re.search(
        r"<script[^>]+src=[\"'][^\"']*MathJax\.js[^\"']*[\"'][^>]*>\s*</script>",
        text,
        flags=re.IGNORECASE,
    )
    if mathjax_script:
        text = text[: mathjax_script.start()] + mathjax_config + text[mathjax_script.start() :]
    elif "</head>" in text:
        text = text.replace("</head>", mathjax_config + "\n</head>", 1)
    else:
        text = mathjax_config + text
    html_path.write_text(text, encoding="utf-8")


def print_html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = find_browser_executable()
    with StaticHttpServer(html_path.parent) as server:
        command = [
            str(chrome),
            "--headless",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-extensions",
            "--disable-web-security",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=20000",
            "--no-first-run",
            "--hide-scrollbars",
            f"--print-to-pdf={pdf_path}",
            "--print-to-pdf-no-header",
            "--no-pdf-header-footer",
            server.url_for(html_path.name),
        ]
        try:
            result = subprocess.run(
                command,
                cwd=html_path.parent,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"Timed out printing {html_path.name} to PDF") from exc
    if result.returncode != 0 and not pdf_path.exists():
        raise RuntimeError(
            f"Failed to print {html_path.name} to PDF:\n"
            f"{result.stdout}\n{result.stderr}"
        )


def find_browser_executable() -> Path:
    for candidate in CHROME_EXECUTABLES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find Chrome or Edge executable for PDF export")


class StaticHttpServer:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.port = find_free_port()
        self.httpd: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def __enter__(self) -> "StaticHttpServer":
        root = self.root

        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(root), **kwargs)

            def log_message(self, format, *args):
                return

        self.httpd = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.thread is not None:
            self.thread.join(timeout=5)

    def url_for(self, filename: str) -> str:
        return f"http://127.0.0.1:{self.port}/{quote(filename)}"


def ensure_mathjax_assets(parts_dir: Path) -> str:
    source = find_local_mathjax_path()
    target_dir = parts_dir / "_mathjax"
    if not target_dir.exists():
        shutil.copytree(source.parent, target_dir, dirs_exist_ok=True)
    return "_mathjax/MathJax.js?config=TeX-AMS-MML_HTMLorMML"


def find_local_mathjax_path() -> Path:
    for candidate in MATHJAX_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find a local MathJax.js for notebook export")


def merge_pdfs(pdf_paths: list[Path], output_pdf: Path) -> None:
    merger = PdfMerger()
    try:
        for pdf_path in pdf_paths:
            merger.append(str(pdf_path))
        with output_pdf.open("wb") as handle:
            merger.write(handle)
    finally:
        merger.close()


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
