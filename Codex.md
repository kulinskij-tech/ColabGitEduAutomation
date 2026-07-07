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


Current project state:

- library repo publishes to `git@github.com:kulinskij-tech/ColabGitEduAutomation.git`
- exported course repos live under ignored `published/`
- AtomicPhys export target is `published/AtomicPhys`
- QuantumMechanics1 repo is located at `published/QuantumMechanics1`
- AtomicPhys remote is `git@github.com:kulinskij-tech/AtomicPhys.git`
- AtomicPhys export is paused pending maintainer review of unresolved source notebook links

Do not commit or push course exports when validation reports unresolved local notebook links unless the maintainer explicitly decides how those links should be handled.
