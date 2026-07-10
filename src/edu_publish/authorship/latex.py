from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import Path
import re

from edu_publish.authorship.deduplicate import normalize_text, visible_blocks
from edu_publish.authorship.models import AuthorshipConfig, LatexResult, TextBlock


def measure_latex_roots(
    roots: list[Path],
    config: AuthorshipConfig,
    exclude_patterns: list[str] | None = None,
) -> LatexResult:
    result = LatexResult()
    seen: set[Path] = set()
    exclude_patterns = exclude_patterns or []

    for root in roots:
        source = collect_latex(root, seen, result.files_read, result.warnings, exclude_patterns)
        source = document_body(source)
        visible = latex_visible_text(strip_comments(source))
        for block in visible_blocks(visible):
            result.blocks.append(
                TextBlock(
                    source=str(root),
                    kind="latex",
                    text=block,
                    normalized=normalize_text(block),
                )
            )

    result.characters = sum(len(block.text) for block in result.blocks)
    result.author_sheets = result.characters / config.characters_per_sheet
    return result


def collect_latex(
    path: Path,
    seen: set[Path],
    files_read: list[str],
    warnings: list[str],
    exclude_patterns: list[str],
) -> str:
    resolved = path.resolve()
    if is_excluded(resolved, exclude_patterns):
        return ""
    if resolved in seen:
        return ""
    seen.add(resolved)
    if not resolved.exists():
        warnings.append(f"Missing LaTeX file: {path}")
        return ""

    files_read.append(str(resolved))
    text = resolved.read_text(encoding="utf-8", errors="replace")
    base = resolved.parent

    def replace_include(match: re.Match[str]) -> str:
        child = resolve_latex_path(base, match.group(2).strip())
        return collect_latex(child, seen, files_read, warnings, exclude_patterns)

    return re.sub(r"\\(input|include)\s*\{([^}]+)\}", replace_include, text)



def document_body(text: str) -> str:
    begin = re.search(r"\\begin\{document\}", text)
    if not begin:
        return text
    text = text[begin.end():]
    end = re.search(r"\\end\{document\}", text)
    if end:
        text = text[:end.start()]
    return text


def resolve_latex_path(base: Path, name: str) -> Path:
    candidate = base / name
    if candidate.suffix:
        return candidate
    return candidate.with_suffix(".tex")


def is_excluded(path: Path, patterns: list[str]) -> bool:
    text = str(path)
    return any(fnmatchcase(path.name, pattern) or pattern in text for pattern in patterns)


def strip_comments(text: str) -> str:
    return "\n".join(strip_comment_line(line) for line in text.splitlines())


def strip_comment_line(line: str) -> str:
    escaped = False
    for index, char in enumerate(line):
        if char == "\\":
            escaped = not escaped
            continue
        if char == "%" and not escaped:
            return line[:index]
        escaped = False
    return line


def latex_visible_text(text: str) -> str:
    for environment in ("thebibliography", "bibliography", "comment", "verbatim"):
        text = re.sub(
            rf"\\begin\{{{environment}\}}.*?\\end\{{{environment}\}}",
            " ",
            text,
            flags=re.S,
        )
    text = re.sub(r"\\(label|ref|eqref|pageref|cite[a-zA-Z]*|bibliography|bibliographystyle)\s*\{[^}]*\}", " ", text)
    text = re.sub(r"\\includegraphics(?:\[[^\]]*\])?\s*\{[^}]*\}", " ", text)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = re.sub(r"\$([^$]*)\$", r"\1", text)
    text = re.sub(
        r"\\(section|subsection|subsubsection|paragraph|caption|title|author)\*?(?:\[[^\]]*\])?\s*\{([^{}]*)\}",
        r"\2\n\n",
        text,
    )
    text = re.sub(r"\\begin\{[^}]+\}|\\end\{[^}]+\}", " ", text)
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", lambda m: m.group(1) or " ", text)
    text = re.sub(r"\\.", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"[~^_&#]", " ", text)
    return normalize_spacing(text)


def normalize_spacing(text: str) -> str:
    paragraphs = []
    current = []
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

