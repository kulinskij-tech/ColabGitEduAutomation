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
- QuantumMechanics1 was refreshed and its supplementary links repaired on 2026-09-15: all 34 exported notebooks and 95 notebook links validate. Run `tools/refresh_qm1_links.py` after export to preserve the repairs; see `docs/QM1_REFRESH_STATUS.md`.
- QuantumMechanics2 source uses `C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py` with `--notebooks qm2_*.ipynb`
- QuantumMechanics2 repo is located at `published/QuantumMechanics2`
- QuantumMechanics2 remote is `git@github.com:kulinskij-tech/QuantumMechanics2.git`
- AtomicPhys remote is `git@github.com:kulinskij-tech/AtomicPhys.git`
- AtomicPhys source TOC links resolve and the local export has been regenerated from source
- AtomicPhys notebook-native core PDF is generated from pre-printed PDFs in the sibling `Atomic_py_book` folder
- Current AtomicPhys core PDF QC passes after reprinting `atomicphys_atomlight` and `atomicphys_mols`; the merged PDF has 164 pages and is about 12.8 MB
- AtomicPhys experimental notebook sections are maintained by `tools/add_atomicphys_experimental_sections.py`; their source figures and citations must be checked before the affected notebooks are manually reprinted

Do not commit or push course exports when validation reports unresolved local notebook links unless the maintainer explicitly decides how those links should be handled.
