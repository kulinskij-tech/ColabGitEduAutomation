# ColabGitEduAutomation

Python library for publishing educational Jupyter notebook courses.

Current functionality:

- discover a course TOC notebook
- discover linked notebooks
- analyze course structure
- generate GitHub notebook preview URLs
- generate Google Colab notebook preview URLs
- export a GitHub-ready course directory
- generate a notebook-native core PDF from course notebooks when no hand-written core PDF exists
- copy notebook resource directories during export
- optionally rewrite exported notebook links to Google Colab URLs
- optionally map known external notebook links to published URLs
- optionally add an Open in Colab badge to exported notebooks
- keep exported course repositories outside library Git tracking under `published/`

Current CLI:

```powershell
python -m edu_publish analyze COURSE_DIR
python -m edu_publish github-preview COURSE_DIR --repo owner/repository
python -m edu_publish colab-preview COURSE_DIR --repo owner/repository
python -m edu_publish github-export COURSE_DIR DESTINATION [--repo owner/repository] [--external-notebook NOTEBOOK=URL]
python -m edu_publish generate-core-pdf COURSE_DIR [--output COURSE_CORE.pdf] [--title TITLE] [--renderer printed|html|nbclassic] [--force]
```

Export behavior:

- without `--repo`, notebooks are copied unchanged
- with `--repo`, only exported notebooks are modified
- source notebooks are never modified
- `generate-core-pdf` skips an existing target PDF unless `--force` is passed
- `generate-core-pdf` defaults to reusing pre-printed notebook PDFs when available
- suspicious pre-printed notebook PDFs are reported for manual reprint; missing pre-prints fall back to HTML rendering
- exported local `.ipynb` markdown links are rewritten to Colab URLs
- mapped external `.ipynb` markdown links are rewritten to their configured URLs
- every exported notebook receives one first-cell Open in Colab badge
- resource directories such as `images`, `figs`, `img`, and `data` are copied
- `.ipynb_checkpoints` are ignored

Current publication stage:

- library repository is clean and pushed to `kulinskij-tech/ColabGitEduAutomation`
- SSH publishing is configured for GitHub
- exported course repositories are intended to live under `published/`
- `published/AtomicPhys` export was generated for `kulinskij-tech/AtomicPhys`
- `published/QuantumMechanics1` contains the moved QuantumMechanics1 course repository
- `published/QuantumMechanics2` contains the generated QuantumMechanics2 course repository
- AtomicPhys source TOC links resolve and the local export has been regenerated from source
- AtomicPhys core PDF generation uses pre-printed PDFs from `Atomic_py_book`; the latest core PDF QC passes after reprinting `atomicphys_atomlight` and `atomicphys_mols` from rendered Jupyter view
- AtomicPhys experimental sections are reproducible with `tools/add_atomicphys_experimental_sections.py`; the Ramsauer-Townsend comparison uses Ar/Kr/Xe momentum-transfer data from the LXCat SIGLO database
- AtomicPhys student guidance and syllabus artifacts are reproducible with `tools/build_atomicphys_student_docs.py`

## Example: update QM1 materials

Run from the ColabGitEduAutomation repository root. Use a Python environment
with `PyPDF2` installed (the CLI imports it even for notebook export).
This Linux example uses the source materials on `/media/me/Myfiles`:

```bash
set -e
export PYTHONPATH=src
qm1_source='/media/me/Myfiles/localtexmf/Mytex/lectures/quantum/quantumbook/QM_py'
phys4math_source='/media/me/Myfiles/localtexmf/Mytex/lectures/Phys4Math/Phys4Math_course'
qm1_destination='published/QuantumMechanics1'

.venv/bin/python -m edu_publish analyze "$qm1_source" --notebooks 'qm1_*.ipynb'
.venv/bin/python -m edu_publish github-export "$qm1_source" "$qm1_destination" \
  --repo kulinskij-tech/QuantumMechanics1 --notebooks 'qm1_*.ipynb'
.venv/bin/python tools/refresh_qm1_links.py \
  --source "$qm1_source" --phys4math "$phys4math_source" \
  --destination "$qm1_destination"

git -C "$qm1_destination" diff --check
git -C "$qm1_destination" diff --stat
```

Always run the repair after export: it includes `qm_technotes`, `sinc_wolfram`,
`rectwv_fresnel`, and `qm1_qcorr`, restores the required section anchors, and
repairs QM1/Phys4Math/QM2 notebook links. Source notebooks remain unchanged.
The `qm1_*.ipynb` filter excludes QM2 notebooks from the shared source folder.

For an existing repository with local edits, export and repair into a fresh
preview directory first, validate it, then copy the course files into the
published repository. The exporter overwrites destination `README.md` and
`.gitignore`; preserve customized repository-level files. Export updates
selected notebooks and resource directories but does not remove obsolete
notebooks. Review the diff and validate notebook links before committing or
pushing. These commands update local materials only.

The 2026-09-21 run used `reports/qm1-refresh-2026-09-21` as its preview;
validation results are in `reports/qm1-refresh-2026-09-21-validation.json`.
It refreshed six notebooks and validated 32 exported notebooks, 92 notebook
links, and 93 resource files. Two older destination notebooks absent from the
current source (`qm1_atomh_conluent` and `qm1_atomh_hyeprgeom`) were retained.
The subsequent publication preserves the remote removal of those two obsolete
notebooks. Notebook code was not executed.
See [QM1 link-repair details](docs/QM1_REFRESH_STATUS.md) and the
[publishing guide](docs/PUBLISHING_HOWTO.md) for the Windows source paths
and PowerShell examples.

Future:

- richer export validation
- repository synchronization
- Google Classroom publishing
