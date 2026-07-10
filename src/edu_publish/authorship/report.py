from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import csv
import json

from edu_publish.authorship.models import MeasurementReport


def report_to_dict(report: MeasurementReport) -> dict:
    return {
        "course": asdict(report.course),
        "main_publication": {
            "characters": report.main_publication.characters,
            "author_sheets": round(report.main_publication.author_sheets, 4),
            "files_read": report.main_publication.files_read,
        },
        "interactive_companion": {
            "markdown_characters": report.interactive_companion.markdown_characters,
            "code_characters": report.interactive_companion.code_characters,
            "output_characters": report.interactive_companion.output_characters,
            "image_count": report.interactive_companion.image_count,
            "duplicates_removed": report.interactive_companion.duplicates_removed,
            "author_sheets": round(report.interactive_companion.author_sheets, 4),
            "notebooks_read": report.interactive_companion.notebooks_read,
            "duplicate_blocks": report.interactive_companion.duplicate_blocks,
        },
        "combined": {
            "author_sheets": round(report.combined_author_sheets, 4),
        },
        "settings": asdict(report.settings),
        "warnings": report.warnings,
    }


def write_json(report: MeasurementReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report_to_dict(report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_markdown(report: MeasurementReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = report_to_dict(report)
    course = data["course"]
    main = data["main_publication"]
    companion = data["interactive_companion"]
    lines = [
        "# Author's Sheet Measurement Report",
        "",
        f"Course: {course.get('name') or 'unspecified'}",
        f"Publication: {course.get('publication_title') or 'unspecified'}",
        f"Author: {course.get('author') or 'unspecified'}",
        f"Semester: {course.get('semester') or 'unspecified'}",
        "",
        "## Main Publication",
        "",
        f"- Characters: {main['characters']:,}",
        f"- Author's sheets: {main['author_sheets']:.2f}",
        "",
        "## Interactive Companion",
        "",
        f"- Markdown characters: {companion['markdown_characters']:,}",
        f"- Code characters: {companion['code_characters']:,}",
        f"- Output characters: {companion['output_characters']:,}",
        f"- Images detected: {companion['image_count']:,}",
        f"- Duplicates removed: {companion['duplicates_removed']:,}",
        f"- Author's sheets: {companion['author_sheets']:.2f}",
        "",
        "## Combined",
        "",
        f"- Total author's sheets: {data['combined']['author_sheets']:.2f}",
        "",
        "## Warnings",
        "",
    ]
    warnings = data["warnings"]
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_csv(report: MeasurementReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = report_to_dict(report)
    rows = [
        ("main_publication", "characters", data["main_publication"]["characters"]),
        ("main_publication", "author_sheets", data["main_publication"]["author_sheets"]),
        ("interactive_companion", "markdown_characters", data["interactive_companion"]["markdown_characters"]),
        ("interactive_companion", "code_characters", data["interactive_companion"]["code_characters"]),
        ("interactive_companion", "output_characters", data["interactive_companion"]["output_characters"]),
        ("interactive_companion", "duplicates_removed", data["interactive_companion"]["duplicates_removed"]),
        ("interactive_companion", "author_sheets", data["interactive_companion"]["author_sheets"]),
        ("combined", "author_sheets", data["combined"]["author_sheets"]),
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["section", "metric", "value"])
        writer.writerows(rows)


def terminal_summary(report: MeasurementReport) -> str:
    return "\n".join(
        [
            "Main publication",
            "",
            "Text characters:",
            str(report.main_publication.characters),
            "",
            "Author's sheets:",
            f"{report.main_publication.author_sheets:.2f}",
            "",
            "Interactive Companion",
            "",
            "Markdown:",
            str(report.interactive_companion.markdown_characters),
            "",
            "Code:",
            str(report.interactive_companion.code_characters),
            "",
            "Duplicates excluded:",
            str(report.interactive_companion.duplicates_removed),
            "",
            "Author's sheets:",
            f"{report.interactive_companion.author_sheets:.2f}",
            "",
            "TOTAL:",
            f"{report.combined_author_sheets:.2f} author's sheets",
        ]
    )

