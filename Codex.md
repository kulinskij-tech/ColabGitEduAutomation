# Instructions for Codex

This project is developed incrementally.

Important rules:

- Preserve existing behavior.
- Make the smallest possible change.
- Avoid rewriting working code.
- Do not introduce unnecessary abstractions.
- Objects should represent real domain concepts.
- Keep diffs easy to review.
- Do not modify unrelated files.
- Never modify source notebooks during export.
- Keep URL generation centralized in repository classes.
- Keep export-only transformations limited to exported notebooks.

Architecture decisions are made by the maintainer.

If a requested change requires a larger redesign, explain why before implementing it.

Always prefer behavior-preserving refactoring.

Current exporter behavior to preserve:

- `github-export COURSE_DIR DESTINATION` copies notebooks unchanged
- `github-export COURSE_DIR DESTINATION --repo owner/repository` may transform only exported notebooks
- repo-aware export rewrites local notebook links to Colab URLs
- repo-aware export inserts one first-cell Open in Colab badge per exported notebook
- source notebooks are never modified
