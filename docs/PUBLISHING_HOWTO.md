# Publishing System HOWTO

This guide shows the common ColabGitEduAutomation workflows for publishing
course notebooks as GitHub/Colab companion repositories.

Run commands from the repository root:

```powershell
cd C:\Users\myself\ColabGitEduAutomation
$env:PYTHONPATH = "src"
```

If the package is installed in an environment, the `PYTHONPATH` line is not
needed.

## 1. Inspect a Course

Use `analyze` to find the course TOC notebook and check which notebooks it
links.

```powershell
python -m edu_publish analyze `
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" `
  --notebooks qm1_*.ipynb
```

For Quantum Mechanics II:

```powershell
python -m edu_publish analyze `
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" `
  --notebooks qm2_*.ipynb
```

## 2. Preview GitHub Links

Use `github-preview` before export to verify the repository URL pattern.

```powershell
python -m edu_publish github-preview `
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" `
  --repo kulinskij-tech/QuantumMechanics1 `
  --notebooks qm1_*.ipynb
```

This does not modify files. It prints the GitHub URLs that exported notebooks
will use.

## 3. Preview Colab Links

Use `colab-preview` to see the corresponding Google Colab URLs.

```powershell
python -m edu_publish colab-preview `
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" `
  --repo kulinskij-tech/QuantumMechanics1 `
  --notebooks qm1_*.ipynb
```

## 4. Export a Course Repository

Export copies notebooks and resource directories into a GitHub-ready directory.
When `--repo` is supplied, exported notebook links are rewritten to Colab URLs
and an "Open in Colab" badge is added to each exported notebook.

```powershell
python -m edu_publish github-export `
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" `
  "C:\Users\myself\ColabGitEduAutomation\published\QuantumMechanics1" `
  --repo kulinskij-tech/QuantumMechanics1 `
  --notebooks qm1_*.ipynb
```

For Quantum Mechanics II:

```powershell
python -m edu_publish github-export `
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" `
  "C:\Users\myself\ColabGitEduAutomation\published\QuantumMechanics2" `
  --repo kulinskij-tech/QuantumMechanics2 `
  --notebooks qm2_*.ipynb
```

## 5. Map External Notebook Links

If an exported notebook links to another notebook outside the exported set, map
that notebook explicitly.

```powershell
python -m edu_publish github-export `
  "C:\path\to\Course_py" `
  "C:\Users\myself\ColabGitEduAutomation\published\CourseRepo" `
  --repo owner/CourseRepo `
  --external-notebook helper.ipynb=https://colab.research.google.com/github/owner/OtherRepo/blob/main/helper.ipynb
```

## 6. Commit an Exported Course

Exported course repositories live under `published/` and are separate Git
repositories when initialized that way.

```powershell
cd C:\Users\myself\ColabGitEduAutomation\published\QuantumMechanics1
git status --short
git add README.md .gitignore QM_py
git commit -m "Update Quantum Mechanics I notebooks"
git push origin main
```

Before committing, inspect the diff:

```powershell
git diff --stat
git diff --name-status
```

## 7. Measure Author's Sheets

The author's-sheet calculator is course-independent. Course-specific source
paths and report destinations belong in YAML configuration files.

Example:

```powershell
python -m edu_publish measure-authorship `
  --defaults config\authorship-defaults.yml `
  --config courses\qm1-authorship.yml
```

Override report destinations from the command line:

```powershell
python -m edu_publish measure-authorship `
  --defaults config\authorship-defaults.yml `
  --config courses\qm1-authorship.yml `
  --json reports\qm1-authorship.json `
  --markdown reports\qm1-authorship.md `
  --csv reports\qm1-authorship.csv
```

For a new course, copy `courses\qm1-authorship.yml`, change the course metadata,
LaTeX roots, notebook directories, exclusions, and outputs. The measurement
engine does not need course-specific code changes.

## 8. Recommended Publication Checklist

1. Run `analyze` and confirm all linked notebooks exist.
2. Run `github-preview` and `colab-preview`.
3. Export into `published/<CourseRepo>`.
4. Inspect `git diff --stat` and `git diff --name-status`.
5. Open a few exported notebooks and verify the Colab badge/link behavior.
6. Commit and push the exported course repository.
7. Run `measure-authorship` if a publishing-volume report is needed.

## Notes

- Source notebooks are never modified by `github-export`.
- Only exported notebooks are rewritten.
- Resource directories named `images`, `figs`, `img`, and `data` are copied.
- `.ipynb_checkpoints` are ignored during export.
- Keep course-specific paths in configuration files where possible.
