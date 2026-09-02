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
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" ` --notebooks qm1_*.ipynb
```

For Quantum Mechanics II:

```powershell
python -m edu_publish analyze `
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" ` --notebooks qm2_*.ipynb
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

Use `--rounding-increment 1` when the report must be rounded upward to whole author sheets instead of half sheets.

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

## 9. Generate a Core PDF from Notebooks

Courses with a hand-written canonical PDF should keep using that PDF. For
courses that do not have a core PDF, generate a notebook-native publication
from the ordered notebook links in the course TOC:

```powershell
python -m edu_publish generate-core-pdf `
  "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" `
  --notebooks qm2_*.ipynb `
  --output "C:\Users\myself\ColabGitEduAutomation\published\QuantumMechanics2\course_core.pdf" `
  --title "МЕТОДИЧНИЙ ПОСІБНИК З КУРСУ" `
  --subtitle "Матеріали курсу, згенеровані з Jupyter notebooks" `
  --renderer printed
```

The command reuses matching pre-printed notebook PDFs such as
`atomicphys_wavevolut - Jupyter Notebook.pdf` from a sibling `*_book` folder
when they exist. This preserves code cells, outputs, figures, links, and
MathJax rendering from the manual notebook print workflow while still merging
the PDFs in TOC order. A small notebook-based cover page is added in front so
the merged PDF still has course metadata without depending on the QM1 LaTeX
template.

Before copying a pre-printed notebook PDF, the generator extracts its text and
compares it with raw markdown markers from the source notebook. If a candidate
PDF appears to contain visible notebook source such as `###` headings or
literal `\begin{equation}` blocks, the generator prints a warning and still
uses the PDF. This is intentional: in the current Windows/Chrome environment,
the automated HTML fallback preserves layout less reliably and does not render
MathJax formulas, so a suspicious manual print should be fixed by reprinting
that notebook from rendered Jupyter view.

The default `printed` renderer is best when manually printed notebook PDFs are
available. If a pre-printed PDF is missing, `printed` falls back to the HTML
export path for that notebook. `--renderer html` exports all notebooks to HTML
and prints those pages to PDF with local Chrome; use it only for diagnostics
until MathJax rendering is verified in the local Chrome print path.
`--renderer nbclassic` can be used to try a closer nbclassic print-preview
workflow, but it depends on headless Chrome successfully printing pages served
by a temporary local nbclassic server.

AtomicPhys status as of the latest QC pass:

- source path:
  `C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\AtomicPhys\Atomic_py`
- printed source PDFs:
  `C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\AtomicPhys\Atomic_py_book`
- output:
  `C:\Users\myself\ColabGitEduAutomation\published\AtomicPhys\atomicphys_core.pdf`
- current generated PDF after the reprint QC pass: 164 pages, about 12.8 MB
- `atomicphys_atomlight - Jupyter Notebook.pdf` and
  `atomicphys_mols - Jupyter Notebook.pdf` were reprinted from rendered
  Jupyter view after earlier source-view/raw-LaTeX defects

### Maintain AtomicPhys experimental sections

The AtomicPhys source notebooks live outside this automation repository. Their
experimental additions are reproducible with the checked-in updater:

```powershell
C:\Users\myself\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  tools\add_atomicphys_experimental_sections.py `
  --atomic-py "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\AtomicPhys\Atomic_py"
```

Use `--notebook atomicphys_dual.ipynb` to update only the wave-particle duality
notebook. Its Ramsauer-Townsend figure is generated from the Ar, Kr, and Xe
momentum-transfer curves in `sources/lxcat_siglo.json`, downloaded from the
LXCat SIGLO database. The notebook caption records the dataset citation,
explains the partial-wave minimum, and treats the Poisson-Arago white spot as a
wave-interference analogy rather than the same scattering geometry.

The core PDF uses manually printed notebook PDFs, so source notebook edits do
not enter `atomicphys_core.pdf` automatically. Reprint each affected notebook
from rendered Jupyter view into `Atomic_py_book`, then rebuild with
`generate-core-pdf --renderer printed --force`.

The student how-to and syllabus are generated separately:

```powershell
C:\Users\myself\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  tools\build_atomicphys_student_docs.py `
  --atomic-root "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\AtomicPhys"
```

This keeps `AtomicPhys_student_howto.md/.pdf` in the AtomicPhys root and writes
`AtomicPhys_syllabus.md/.pdf` under `AtomicPhys_syllabus`.

If the target PDF already exists, the command skips generation. Use `--force`
only when you intentionally want to replace it. Use `--no-compile` if you want
to export the notebook PDFs without merging them yet.

## 10. Fill the PDF File Size

After the PDF is generated, the `latex-pdf-size` command can update the
`Обсяг ... МБ.` line and run XeLaTeX one more time for LaTeX-based source
documents that still use that pattern.

```powershell
python -m edu_publish latex-pdf-size `
  --main "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\practicemethod\qru1prob_xelatex_ua.tex" `
  --target "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\practicemethod\qru1prob_shapkafin.tex" `
  --engine xelatex
```

## 11. Reusable PowerShell Script Examples

The commands above can be saved in `.ps1` files when the same workflow is run
regularly. Run these scripts from the ColabGitEduAutomation repository root so
that the relative `src` and `published` paths resolve correctly.

### Preview and export one course

Save the following as `publish-course.ps1`:

```powershell
param(
  [Parameter(Mandatory = $true)]
  [string]$CourseDir,

  [Parameter(Mandatory = $true)]
  [string]$Repository,

  [string]$NotebookPattern = "*.ipynb"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "src"
$repoName = $Repository.Split("/")[-1]
$destination = Join-Path "published" $repoName

python -m edu_publish analyze $CourseDir `
  --notebooks $NotebookPattern

python -m edu_publish github-preview $CourseDir `
  --repo $Repository `
  --notebooks $NotebookPattern

python -m edu_publish colab-preview $CourseDir `
  --repo $Repository `
  --notebooks $NotebookPattern

python -m edu_publish github-export $CourseDir $destination `
  --repo $Repository `
  --notebooks $NotebookPattern

Write-Host "Exported $Repository to $destination"
```

Run it for Quantum Mechanics I:

```powershell
.\publish-course.ps1 `
  -CourseDir "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" `
  -Repository "kulinskij-tech/QuantumMechanics1" `
  -NotebookPattern "qm1_*.ipynb"
```

With PowerShell 7.3 or newer, make native command failures stop the script:

```powershell
$PSNativeCommandUseErrorActionPreference = $true
```

### Generate a core PDF and inspect it

Save the following as `build-core-pdf.ps1`:

```powershell
param(
  [Parameter(Mandatory = $true)]
  [string]$CourseDir,

  [Parameter(Mandatory = $true)]
  [string]$Output,

  [string]$NotebookPattern = "*.ipynb",
  [string]$Title = "Course materials",
  [switch]$Force
)

$env:PYTHONPATH = "src"
$arguments = @(
  "-m", "edu_publish", "generate-core-pdf", $CourseDir,
  "--notebooks", $NotebookPattern,
  "--output", $Output,
  "--title", $Title,
  "--renderer", "printed"
)

if ($Force) {
  $arguments += "--force"
}

python @arguments

if ($LASTEXITCODE -ne 0) {
  throw "Core PDF generation failed with exit code $LASTEXITCODE"
}

Get-Item $Output | Select-Object FullName, Length, LastWriteTime
```

Run it normally to keep an existing PDF, or add `-Force` to rebuild it:

```powershell
.\build-core-pdf.ps1 `
  -CourseDir "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\AtomicPhys\Atomic_py" `
  -Output ".\published\AtomicPhys\atomicphys_core.pdf" `
  -NotebookPattern "atomicphys_*.ipynb" `
  -Title "Atomic Physics" `
  -Force
```

### Measure several courses

A short loop can run the same authorship measurement for every course
configuration:

```powershell
$env:PYTHONPATH = "src"

Get-ChildItem "courses\*-authorship.yml" | ForEach-Object {
  Write-Host "Measuring $($_.BaseName)"
  python -m edu_publish measure-authorship `
    --defaults "config\authorship-defaults.yml" `
    --config $_.FullName

  if ($LASTEXITCODE -ne 0) {
    throw "Measurement failed for $($_.FullName)"
  }
}
```

## Notes

- Source notebooks are never modified by `github-export`.
- Only exported notebooks are rewritten.
- Resource directories named `images`, `figs`, `img`, and `data` are copied.
- `.ipynb_checkpoints` are ignored during export.
- Keep course-specific paths in configuration files where possible.


