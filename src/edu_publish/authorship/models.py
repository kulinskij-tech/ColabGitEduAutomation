from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CourseMetadata:
    name: str = ""
    author: str = ""
    semester: str = ""
    publication_title: str = ""


@dataclass
class AuthorshipConfig:
    characters_per_sheet: int = 40000
    illustration_cm2_per_sheet: int = 3000
    code_mode: str = "text"
    include_outputs: bool = False
    deduplicate: bool = True
    minimum_duplicate_block_length: int = 200


@dataclass
class SourceConfig:
    latex_roots: list[Path] = field(default_factory=list)
    notebook_dirs: list[Path] = field(default_factory=list)
    exclude_latex: list[str] = field(default_factory=list)
    exclude_notebooks: list[str] = field(default_factory=list)


@dataclass
class OutputConfig:
    json: Path | None = None
    markdown: Path | None = None
    csv: Path | None = None


@dataclass
class ToolConfig:
    course: CourseMetadata = field(default_factory=CourseMetadata)
    authorship: AuthorshipConfig = field(default_factory=AuthorshipConfig)
    sources: SourceConfig = field(default_factory=SourceConfig)
    outputs: OutputConfig = field(default_factory=OutputConfig)


@dataclass
class TextBlock:
    source: str
    kind: str
    text: str
    normalized: str


@dataclass
class LatexResult:
    characters: int = 0
    author_sheets: float = 0.0
    files_read: list[str] = field(default_factory=list)
    blocks: list[TextBlock] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class NotebookResult:
    markdown_characters: int = 0
    code_characters: int = 0
    output_characters: int = 0
    image_count: int = 0
    duplicates_removed: int = 0
    author_sheets: float = 0.0
    notebooks_read: list[str] = field(default_factory=list)
    duplicate_blocks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class MeasurementReport:
    course: CourseMetadata
    main_publication: LatexResult
    interactive_companion: NotebookResult
    combined_author_sheets: float
    settings: AuthorshipConfig
    warnings: list[str]
