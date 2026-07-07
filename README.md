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
- optionally add an Open in Colab badge to exported notebooks

Current CLI:

```powershell
python -m edu_publish analyze COURSE_DIR
python -m edu_publish github-preview COURSE_DIR --repo owner/repository
python -m edu_publish colab-preview COURSE_DIR --repo owner/repository
python -m edu_publish github-export COURSE_DIR DESTINATION [--repo owner/repository]
```

Export behavior:

- without `--repo`, notebooks are copied unchanged
- with `--repo`, only exported notebooks are modified
- source notebooks are never modified
- exported local `.ipynb` markdown links are rewritten to Colab URLs
- every exported notebook receives one first-cell Open in Colab badge
- resource directories such as `images`, `figs`, `img`, and `data` are copied
- `.ipynb_checkpoints` are ignored

Future:

- richer export validation
- repository synchronization
- Google Classroom publishing
