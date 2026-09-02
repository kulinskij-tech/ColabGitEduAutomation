# Roadmap

## Completed

- Course class
- TOC class
- Notebook class
- CourseConfig
- GitHubRepository
- ColabRepository
- course analysis CLI
- GitHub preview CLI
- Colab preview CLI
- GitHub export CLI
- resource directory copying during export
- export without modifying source notebooks
- Colab link rewriting during repo-aware export
- Open in Colab badge insertion during repo-aware export
- `published/` ignored in the library repository for exported course repos
- GitHub SSH publishing configured for the maintainer account

## Current Stage

The first GitHub and Colab-oriented export workflow is working.

Repo-aware GitHub export now prepares notebooks for the intended user path:

```text
GitHub course page
click notebook or badge
Google Colab opens the notebook
```

Published course repositories are kept under:

```text
published/
```

Current course publication status:

- `AtomicPhys`: exported locally with Colab badges, not pushed yet; notebook-native `atomicphys_core.pdf` builds from manually printed notebook PDFs and passes the current 164-page QC after the `atomicphys_atomlight` and `atomicphys_mols` reprints
- `QuantumMechanics1`: moved into `published/QuantumMechanics1`
- `QuantumMechanics2`: exported into `published/QuantumMechanics2` from `QM_py` with `qm2_*.ipynb`

AtomicPhys source review is complete for TOC-linked notebooks. The previously missing `atomicphys_intsymom_probs.ipynb` source notebook exists, the AtomicPhys analysis passes, and the local export has been regenerated from source. The core PDF workflow is usable and the two previously flagged notebook PDFs have been reprinted. Experimental additions now cover the main historical experiments; the Ramsauer-Townsend section uses an Ar/Kr/Xe comparison generated from LXCat SIGLO data and explains the limited analogy with the Poisson-Arago spot.

## Next

- improve export validation and error messages
- add focused automated tests when a test structure is introduced
- prepare for repository synchronization workflows
- design Google Classroom integration

## Future

- repository synchronization
- Google Classroom API integration
- generated Classroom materials
- richer course metadata
