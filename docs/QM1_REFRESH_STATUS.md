# QuantumMechanics1 refresh — 2026-09-15

## Project context

The automation library exports source notebooks without modifying them, rewrites
exported notebook links to Colab, and copies supporting resources. Course Git
repositories live under the ignored `published/` directory.

The library is at `cad8641`. Existing untracked authorship reports and
`docs/EDUCATIONAL_ARCHITECTURE.md` were left intact.

QuantumMechanics1 was clean at `2934aad` before this refresh. Fetching origin
confirmed that its local main branch matched origin/main.

## Materials refreshed

Source: `C:\Users\myself\Documents\localtexmf\Mytex\lectures\quantum\quantumbook\QM_py`

Destination: `published/QuantumMechanics1`, using `--notebooks qm1_*.ipynb`
and `--repo kulinskij-tech/QuantumMechanics1`.

Six exported notebooks changed: `qm1_QinfoTheory`, `qm1_intsymom_theor`,
`qm1_spinpauli_theor`, `qm1_spinpauli_zad`, `qm1_stac_zad`, and `qm1_toc`.
These incorporate source edits to quantum information, symmetry, spin,
stationary-state exercises, and TOC metadata. Re-export also repairs invalid
JSON escaping in the previously published symmetry notebook.

Validation passed for all 22 TOC targets and all 30 exported notebooks. Each
notebook parses as JSON, matches its source after the standard export
transformations, and contains exactly one first-cell Colab badge. All 93
resource files match the preview export. Git whitespace checks pass.
Notebook code execution and rendered equations were not reviewed in this refresh.

## Link issues found during initial refresh

Nine local notebook links remain unresolved in the exported course:

| Referring notebook | Target |
| --- | --- |
| qm1_atomh_theor | qm2_quasiclass.ipynb |
| qm1_ermitop_theor | phys4math_qm_axioms2.ipynb#postpro |
| qm1_ermitop_theor | phys4math_qm_axioms1.ipynb#ortho |
| qm1_qbitspace | qm1_qcorr.ipynb |
| qm1_QinfoTheory | phys4math_qm_axioms1.ipynb |
| qm1_QinfoTheory | phys4math_toc.ipynb |
| qm1_toc | qm_technotes.ipynb |
| qm1_wavepack_zad | sinc_wolfram.ipynb |
| qm1_wavepack_zadevolut | rectwv_fresnel.ipynb |

The three helper notebooks `qm_technotes`, `sinc_wolfram`, and `rectwv_fresnel`
exist in the source directory but are excluded by the QM1 filename filter.
The `phys4math_*` targets and `qm1_qcorr` are absent from that source directory.
The QM2 reference needs an explicit cross-course mapping.

## Repairs completed

All nine links are repaired. The three helper notebooks are included in the
export. `qm1_qcorr.ipynb` is copied from the author's
`Phys4Math/Phys4Math_course/phys4math_qm_qcorr.ipynb`; its qubit reference now
points to QM1. The old Phys4Math axioms links point to the corresponding
existing QM1 qubit and measurement sections, with explicit `qbit`, `ortho`,
and `postpro` anchors. The back-to-TOC link points to QM1. The semiclassical
link points to QM2's `qm2_quasiclass.ipynb`, whose presence was checked in the
local QM2 origin/main tree.

After the normal QM1 export, run this course-specific repair:

```powershell
$env:PYTHONPATH = 'src'
python tools/refresh_qm1_links.py `
  --source 'C:/Users/myself/Documents/localtexmf/Mytex/lectures/quantum/quantumbook/QM_py' `
  --phys4math 'C:/Users/myself/Documents/localtexmf/Mytex/lectures/Phys4Math/Phys4Math_course'
```

The repair only modifies exported notebooks. Repeating it produces identical
files. Final validation checks 34 notebooks, exactly one first-cell Colab badge
per notebook, 95 local or course Colab notebook links, the newly added anchors,
and supplementary resource references. No unresolved notebook links remain.
Detailed validation is saved in `reports/qm1-refresh-validation.json`.

The course refresh and fixes are committed locally as `ea1a3c3`
(`Refresh QM1 materials and repair supplementary notebook links`).
The commit has not been pushed.
