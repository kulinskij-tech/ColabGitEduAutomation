# Development Workflow

## Philosophy

Prefer many small commits.

Every commit should preserve existing behavior except for the explicitly
requested feature.

Typical cycle:

1. Explain design.
2. Implement one small change.
3. Test.
4. Commit.
5. Push.

Avoid large rewrites.

---

## Refactoring Rules

Do not change behavior unless explicitly requested.

Keep diffs small.

Do not rename files unnecessarily.

Avoid speculative abstractions.

Objects should represent domain concepts.

Keep URL generation centralized in repository classes.

Never modify source notebooks during export transformations.

---

## Code Style

Use pathlib.

Prefer properties over public attributes when appropriate.

Keep functions short.

Prefer composition over duplicated discovery logic.

Keep export-only notebook transformations small and explicit.

---

## Testing

Useful manual checks:

```powershell
python -m edu_publish analyze COURSE_DIR
python -m edu_publish github-preview COURSE_DIR --repo owner/repository
python -m edu_publish colab-preview COURSE_DIR --repo owner/repository
python -m edu_publish github-export COURSE_DIR DESTINATION
python -m edu_publish github-export COURSE_DIR DESTINATION --repo owner/repository
python -m edu_publish github-export COURSE_DIR DESTINATION --repo owner/repository --external-notebook NOTEBOOK=URL
```

For exporter changes, verify:

- source notebooks are unchanged
- export without `--repo` copies notebooks unchanged
- export with `--repo` applies only exported-notebook transformations
- local `.ipynb` links become Colab URLs
- configured external `.ipynb` links become their mapped published URLs
- absolute URLs and non-notebook links remain unchanged
- fragments such as `notebook.ipynb#section` are preserved
- every exported notebook has exactly one first-cell Open in Colab badge


## Current Manual Publication Notes

Exported course repositories are kept inside this working folder under `published/`, which is ignored by the library repository.

Current AtomicPhys export command:

```powershell
.venv/bin/python -m edu_publish github-export /media/me/Myfiles/localtexmf/Mytex/lectures/quantum/AtomicPhys/Atomic_py published/AtomicPhys --repo kulinskij-tech/AtomicPhys
```

Current QuantumMechanics2 source check:

```powershell
$env:PYTHONPATH='src'; .venv\Scripts\python.exe -m edu_publish analyze "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" --notebooks qm2_*.ipynb
```

Current QuantumMechanics2 export command:

```powershell
$env:PYTHONPATH='src'; .venv\Scripts\python.exe -m edu_publish github-export "C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py" "C:\Users\myself\ColabGitEduAutomation\published\QuantumMechanics2" --repo kulinskij-tech/QuantumMechanics2 --notebooks qm2_*.ipynb
```

Before pushing a course export, audit unresolved local `.ipynb` markdown links in the source course. AtomicPhys currently has unresolved links that need a maintainer decision before publication continues.
