# ColabGitEduAutomation

Python library for publishing educational Jupyter notebook courses.

Current functionality:

- discover a course TOC notebook
- discover linked notebooks
- analyze course structure
- generate GitHub notebook preview URLs
- generate Google Colab notebook preview URLs
- export a GitHub-ready course directory
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
```

Export behavior:

- without `--repo`, notebooks are copied unchanged
- with `--repo`, only exported notebooks are modified
- source notebooks are never modified
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
- AtomicPhys publication is paused while unresolved local notebook links in the source course are reviewed

Future:

- richer export validation
- repository synchronization
- Google Classroom publishing
