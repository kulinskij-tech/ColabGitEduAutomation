# Author's Sheet Measurement

This feature estimates the author's-sheet volume of a hybrid educational
publication:

- a stable LaTeX/PDF textbook;
- an Interactive Companion made from Jupyter notebooks.

The estimate is intended to be auditable support for university publishing
documentation. It is not a substitute for the final interpretation of a
university publishing office.

## Definition

The calculation uses the standard approximation:

- 1 author's sheet = 40,000 characters, including spaces;
- 1 author's sheet = 3,000 cm2 of illustrative material.

The current implementation focuses on deterministic text volume. Raw values are calculated first, then reported author-sheet totals are rounded upward using `rounding_increment` (default `0.5`; use `1` for whole-sheet reporting):

```text
author_sheets = text_characters / 40000
```

The report keeps image counts and configuration fields so illustration-area
measurement can be added without changing the report shape.

## Counted Content

For LaTeX sources, the tool follows `\input{...}` and `\include{...}` recursively
and counts visible text after removing comments, labels, references,
bibliography metadata, and common formatting syntax. A file included more than
once is counted only once.

For notebooks, Markdown cells are counted as visible text. Code cells are
controlled by `--code-mode`:

- `text`: count code as ordinary text;
- `exclude`: ignore code.

Notebook outputs and metadata are tracked but excluded from the author's-sheet
calculation in this initial implementation.

## Duplicate Handling

By default, notebook Markdown is compared with LaTeX text blocks to avoid obvious
double counting. The duplicate detector is conservative:

- normalizes whitespace;
- removes simple Markdown formatting;
- removes simple LaTeX markup;
- compares only blocks above a configurable minimum length;
- excludes exact normalized matches.

Use `--no-deduplicate` to disable this behavior.

## Configuration

YAML configuration is supported for the `authorship` section:

```yaml
authorship:
  characters_per_sheet: 40000
  illustration_cm2_per_sheet: 3000
  code_mode: text
  deduplicate: true
  minimum_duplicate_block_length: 200
  rounding_increment: 0.5
```

CLI options override configuration values.

## Limitations

The estimate is intentionally conservative. It does not perform semantic
deduplication, does not fully parse arbitrary TeX macro definitions, and does
not yet convert image dimensions into illustration-area sheets. Generated
notebook outputs are excluded from the author's-sheet total in the current
version.

For official reporting, treat the output as an auditable estimate and confirm
the final method with the university publishing office.

