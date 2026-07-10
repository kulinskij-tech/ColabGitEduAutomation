from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import Path
import json
import re

from edu_publish.authorship.deduplicate import (
    duplicate_index,
    normalize_text,
    strip_simple_markdown,
    visible_blocks,
)
from edu_publish.authorship.models import (
    AuthorshipConfig,
    NotebookResult,
    TextBlock,
)


def measure_notebook_dirs(
    dirs: list[Path],
    config: AuthorshipConfig,
    latex_blocks: list[TextBlock],
    exclude_patterns: list[str] | None = None,
) -> NotebookResult:
    result = NotebookResult()
    duplicates = duplicate_index(latex_blocks, config)
    exclude_patterns = exclude_patterns or []

    for directory in dirs:
        if not directory.exists():
            result.warnings.append(f"Missing notebook directory: {directory}")
            continue
        for notebook_path in sorted(directory.rglob("*.ipynb")):
            if is_excluded(notebook_path, exclude_patterns):
                continue
            measure_notebook(notebook_path, config, duplicates, result)


    text_characters = result.markdown_characters
    if config.code_mode == "text":
        text_characters += result.code_characters
    if config.include_outputs:
        text_characters += result.output_characters
    result.author_sheets = text_characters / config.characters_per_sheet
    return result


def measure_notebook(
    notebook_path: Path,
    config: AuthorshipConfig,
    duplicates: set[str],
    result: NotebookResult,
) -> None:
    result.notebooks_read.append(str(notebook_path.resolve()))
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))

    for cell_index, cell in enumerate(notebook.get("cells", [])):
        source = source_text(cell.get("source", ""))
        if cell.get("cell_type") == "markdown":
            result.image_count += markdown_image_count(source)
            visible = markdown_visible_text(source)
            result.markdown_characters += count_markdown_with_duplicates(
                visible,
                notebook_path,
                cell_index,
                duplicates,
                config,
                result,
            )
        elif cell.get("cell_type") == "code":
            if config.code_mode == "text":
                result.code_characters += len(source)
            elif config.code_mode != "exclude":
                result.warnings.append(f"Unsupported code mode: {config.code_mode}")

            if config.include_outputs:
                for output in cell.get("outputs", []):
                    result.output_characters += output_text_length(output)
                    result.image_count += output_image_count(output)


def count_markdown_with_duplicates(
    text: str,
    notebook_path: Path,
    cell_index: int,
    duplicates: set[str],
    config: AuthorshipConfig,
    result: NotebookResult,
) -> int:
    total = 0
    for block in visible_blocks(text):
        normalized = normalize_text(block)
        if (
            config.deduplicate
            and len(normalized) >= config.minimum_duplicate_block_length
            and normalized in duplicates
        ):
            result.duplicates_removed += len(block)
            result.duplicate_blocks.append(
                {
                    "notebook": str(notebook_path),
                    "cell_index": cell_index,
                    "characters": len(block),
                    "preview": block[:120],
                }
            )
        else:
            total += len(block)
    return total


def markdown_visible_text(text: str) -> str:
    paragraphs = []
    current = []
    text = strip_simple_markdown(text)
    for raw_line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if line:
            current.append(line)
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs)


def source_text(source: str | list[str]) -> str:
    if isinstance(source, list):
        return "".join(source)
    return str(source)


def markdown_image_count(text: str) -> int:
    return len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text))


def output_text_length(output: dict) -> int:
    total = 0
    if "text" in output:
        total += len(source_text(output["text"]))
    for mime, value in output.get("data", {}).items():
        if mime.startswith("text/"):
            total += len(source_text(value))
    return total


def output_image_count(output: dict) -> int:
    return sum(1 for mime in output.get("data", {}) if mime.startswith("image/"))


def is_excluded(path: Path, patterns: list[str]) -> bool:
    text = str(path)
    return any(fnmatchcase(path.name, pattern) or pattern in text for pattern in patterns)

