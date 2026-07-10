from __future__ import annotations

import re

from edu_publish.authorship.models import AuthorshipConfig, TextBlock


def normalize_text(text: str) -> str:
    text = strip_simple_latex(text)
    text = strip_simple_markdown(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().casefold()


def strip_simple_latex(text: str) -> str:
    text = re.sub(r"\\(label|ref|eqref|pageref|cite[a-zA-Z]*)\s*\{[^}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", lambda m: m.group(1) or " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"[$~^_&#]", " ", text)
    return text


def strip_simple_markdown(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_>#`~\-]+", " ", text)
    return text


def duplicate_index(blocks: list[TextBlock], config: AuthorshipConfig) -> set[str]:
    return {
        block.normalized
        for block in blocks
        if len(block.normalized) >= config.minimum_duplicate_block_length
    }


def visible_blocks(text: str) -> list[str]:
    return [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
