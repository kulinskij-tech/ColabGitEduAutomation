from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from edu_publish.authorship.latex import measure_latex_roots
from edu_publish.authorship.models import (
    AuthorshipConfig,
    CourseMetadata,
    MeasurementReport,
    OutputConfig,
    SourceConfig,
    ToolConfig,
)
from edu_publish.authorship.notebooks import measure_notebook_dirs
from edu_publish.authorship.report import (
    terminal_summary,
    write_csv,
    write_json,
    write_markdown,
)


def run_measure_authorship(args: list[str]) -> str:
    options = parse_cli_options(args)
    if "--config" not in options:
        raise ValueError("measure-authorship requires --config path/to/course.yml")

    config = load_tool_config(
        Path(options["--config"]),
        Path(options["--defaults"]) if "--defaults" in options else None,
    )
    apply_cli_overrides(config, options)
    report = measure_from_config(config)
    write_configured_reports(config, report, options)
    return terminal_summary(report)


def parse_cli_options(args: list[str]) -> dict[str, Any]:
    options: dict[str, Any] = {}
    flags = {"--deduplicate", "--no-deduplicate", "--include-outputs", "--no-include-outputs"}
    i = 0
    while i < len(args):
        name = args[i]
        if not name.startswith("--"):
            raise ValueError(f"Unexpected argument: {name}")
        if name in flags:
            options[name] = True
            i += 1
            continue
        if i + 1 >= len(args):
            raise ValueError(f"Missing value for {name}")
        options[name] = args[i + 1]
        i += 2
    return options


def apply_cli_overrides(config: ToolConfig, options: dict[str, Any]) -> None:
    if "--code-mode" in options:
        config.authorship.code_mode = options["--code-mode"]
    if config.authorship.code_mode not in {"text", "exclude"}:
        raise ValueError("code_mode must be text or exclude")
    if "--deduplicate" in options:
        config.authorship.deduplicate = True
    if "--no-deduplicate" in options:
        config.authorship.deduplicate = False
    if "--include-outputs" in options:
        config.authorship.include_outputs = True
    if "--no-include-outputs" in options:
        config.authorship.include_outputs = False
    if "--json" in options:
        config.outputs.json = Path(options["--json"])
    if "--markdown" in options:
        config.outputs.markdown = Path(options["--markdown"])
    if "--csv" in options:
        config.outputs.csv = Path(options["--csv"])


def measure_from_config(config: ToolConfig) -> MeasurementReport:
    main = measure_latex_roots(
        config.sources.latex_roots,
        config.authorship,
        config.sources.exclude_latex,
    )
    companion = measure_notebook_dirs(
        config.sources.notebook_dirs,
        config.authorship,
        main.blocks,
        config.sources.exclude_notebooks,
    )
    warnings = main.warnings + companion.warnings
    return MeasurementReport(
        course=config.course,
        main_publication=main,
        interactive_companion=companion,
        combined_author_sheets=main.author_sheets + companion.author_sheets,
        settings=config.authorship,
        warnings=warnings,
    )


def write_configured_reports(config: ToolConfig, report: MeasurementReport, options: dict[str, Any]) -> None:
    json_path = config.outputs.json or (Path(options["--output"]) if "--output" in options else None)
    markdown_path = config.outputs.markdown
    csv_path = config.outputs.csv

    if json_path:
        write_json(report, json_path)
        if markdown_path is None:
            markdown_path = json_path.with_suffix(".md")
    if markdown_path:
        write_markdown(report, markdown_path)
    if csv_path:
        write_csv(report, csv_path)


def load_tool_config(course_path: Path, defaults_path: Path | None = None) -> ToolConfig:
    data: dict[str, Any] = {}
    if defaults_path and defaults_path.exists():
        data = deep_merge(data, parse_simple_yaml(defaults_path))
    data = deep_merge(data, parse_simple_yaml(course_path))
    base = course_path.parent
    return config_from_dict(data, base)


def config_from_dict(data: dict[str, Any], base: Path) -> ToolConfig:
    course_data = data.get("course", {})
    source_data = data.get("sources", {})
    authorship_data = data.get("authorship", {})
    exclude_data = data.get("exclude", {})
    output_data = data.get("outputs", {})

    return ToolConfig(
        course=CourseMetadata(
            name=str(course_data.get("name", "")),
            author=str(course_data.get("author", "")),
            semester=str(course_data.get("semester", "")),
            publication_title=str(course_data.get("publication_title", "")),
        ),
        authorship=AuthorshipConfig(
            characters_per_sheet=int(authorship_data.get("characters_per_sheet", 40000)),
            illustration_cm2_per_sheet=int(authorship_data.get("illustration_cm2_per_sheet", 3000)),
            code_mode=str(authorship_data.get("code_mode", "text")),
            include_outputs=bool(authorship_data.get("include_outputs", False)),
            deduplicate=bool(authorship_data.get("deduplicate", True)),
            minimum_duplicate_block_length=int(authorship_data.get("minimum_duplicate_block_length", 200)),
        ),
        sources=SourceConfig(
            latex_roots=[resolve_config_path(base, value) for value in as_list(source_data.get("latex_roots", source_data.get("latex_main", [])))],
            notebook_dirs=[resolve_config_path(base, value) for value in as_list(source_data.get("notebooks", []))],
            exclude_latex=as_list(exclude_data.get("latex", [])),
            exclude_notebooks=as_list(exclude_data.get("notebooks", [])),
        ),
        outputs=OutputConfig(
            json=optional_path(base, output_data.get("json")),
            markdown=optional_path(base, output_data.get("markdown")),
            csv=optional_path(base, output_data.get("csv")),
        ),
    )


def as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def optional_path(base: Path, value: Any) -> Path | None:
    if not value:
        return None
    return resolve_config_path(base, str(value))


def resolve_config_path(base: Path, value: str) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return (base / path).resolve()


def deep_merge(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(left)
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    pending_key: tuple[int, dict, str] | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if line.startswith("- "):
            value = parse_scalar(line[2:].strip())
            if pending_key and pending_key[0] == indent:
                pending_key[1][pending_key[2]] = []
                stack.append((indent - 1, pending_key[1][pending_key[2]]))
                parent = stack[-1][1]
                pending_key = None
            if isinstance(parent, list):
                parent.append(value)
            continue

        if ":" in line:
            key, raw_value = line.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            if raw_value:
                parent[key] = parse_scalar(raw_value)
                pending_key = None
            else:
                parent[key] = {}
                pending_key = (indent + 2, parent, key)
                stack.append((indent, parent[key]))
    return root


def parse_scalar(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value
