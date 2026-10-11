# QuantumMechanics1 handoff

Last updated: 2026-10-11, Europe/Kiev. Verified on Windows with native Python 3.11.
Live QM1 publication was verified with `git ls-remote` after pushing.

On either platform, read [the portable guide](../PORTABLE_START.md) and resolve
the mirrored roots. Recheck pending changes and branch divergence on that machine.

## Identity and paths

- Source: `<LOCALTEXMF_ROOT>/Mytex/lectures/quantum/quantumbook/QM_py`.
- Primary filter: `qm1_*.ipynb`; TOC: `qm1_toc.ipynb`.
- Checkout: `published/QuantumMechanics1`; exported folder: `QM_py`.
- Remote: `git@github.com:kulinskij-tech/QuantumMechanics1.git`; branch: `main`.
- Supplementary source: `<LOCALTEXMF_ROOT>/Mytex/lectures/Phys4Math/Phys4Math_course`.

## Current state

- Published QM1 main: `5fe66cd1770509ef2df0539b6332b578441c4d65` — `Proofread Ukrainian QM1 materials and refresh current sources`.
- Ukrainian proofreading updated 30 source notebooks / 148 Markdown cells out of 32 reviewed notebooks. Corrections cover spelling, agreement, case, punctuation, Russian prose left in Ukrainian exercises, and terminology. Mathematical claims were not reviewed.
- Source edits include the shared `QM_py/qm_technotes.ipynb` helper and `Phys4Math_course/phys4math_qm_qcorr.ipynb`. Future exports of courses using those helpers will inherit their language corrections; no other course was published here.
- The refreshed publication also includes existing source changes to the hydrogen theory formula and exercises/code, plus current output/metadata changes. These predated proofreading; preservation checks compare against the current source export, not the previous GitHub commit.
- The canonical checkout at `published/QuantumMechanics1` was preserved byte-for-byte: HEAD `e66cb73` and its 26 pre-existing modified notebook entries remain. Do not reset or overwrite it to match this publication.
- Publication used a clean linked worktree at `reports/qm1-ua-20261011/publication`, branch `codex/qm1-ua-20261011`, based on the freshly fetched `8c1e270`. Its committed HEAD is `5fe66cd`; no force-push or rewriting of existing history was used.

## User decisions and scope

- Keep chat messages in English; course prose remains Ukrainian.
- The user requested Ukrainian grammar correction, source update, commit, and publication for QM1.
- Preserve formulas, code, outputs, metadata, link destinations, and existing local work during language editing. Source corrections are a separate authoring step; export still never modifies source notebooks.

## Current validation

- 32 exported notebooks parse and pass notebook-schema validation, with a pre-existing missing-cell-ID warning; no IDs were rewritten on disk.
- 93 local/course notebook links resolve with case-sensitive filename checks; zero unresolved notebook targets. All notebooks retain one first-cell Colab badge.
- Formula/code blocks, URLs/HTML attributes, code cells, outputs, and metadata match the pre-proofreading current-source export. 93 resource files are unchanged; 10 existing SVG/HTML checkout differences are only Git CRLF normalization.
- Source/filter/helper inventory matches the publication inventory. QM2 source notebook hashes are unchanged. Re-running the grammar correction finds zero changes. Git whitespace checks pass.
- No notebook execution, full rendered review, scientific accuracy review, or PDF rebuild was performed.
- Local evidence and source backups: `reports/qm1-ua-20261011/`; see `publication-validation.json`, `review/validation.json`, `review/prose.diff`, and `review/source-before/`. These local reports may not be mirrored.

## Workflow and prior validation

Run `tools/refresh_qm1_links.py` after the normal export. It adds excluded helper
notebooks, obtains `qm1_qcorr` from the Phys4Math source, restores section anchors,
and repairs QM1/Phys4Math/QM2 links. See the
[repair details](../QM1_REFRESH_STATUS.md) and the [README example](../../README.md).
Preserve customized repository-level files and perform a complete inventory sync.

Reviewed language corrections are stored in `sources/qm1_ua_corrections.tsv`.
With the native Python runtime, preview them using:

```text
python tools/proofread_qm1_ua.py --localtexmf <LOCALTEXMF_ROOT> --report-dir reports/qm1-ua-review
```

The command backs up changed sources and produces a cell-level diff; `--apply`
applies corrections to the authoritative sources. Source corrections are already
applied for the current publication. The link repair supports both the corrected
and older spelling of the qubit-section anchor marker.

The historical 2026-09-21 report at
`reports/qm1-refresh-2026-09-21-validation.json` records 32 notebooks, 92 links,
93 resources, and no unresolved links; it also lists two obsolete destination
notebooks then retained. The older 2026-09-15 repair report records a different
34-notebook/95-link snapshot. Neither establishes validation of today's dirty
checkout, and the publication statement in the older report is historical.

## Next actions

1. Preserve the older canonical checkout's changes and divergence. For new publication work, fetch main and use a clean checkout until those local changes are deliberately reconciled.
2. Resolve roots again on the next machine; mirror the corrected source notebooks as well as the library. The linked worktree and local backups may not travel in a mirror.
3. Export from current source and run the link repair; revalidate inventory, resources, and links before publication.
4. PDFs remain outside this proofreading update. Regenerate/review them separately if requested.
