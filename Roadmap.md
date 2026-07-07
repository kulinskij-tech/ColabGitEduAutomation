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

- `AtomicPhys`: exported locally with Colab badges, not pushed yet
- `QuantumMechanics1`: moved into `published/QuantumMechanics1`

AtomicPhys is paused for source review. The audit found unresolved local notebook links in the source notebooks, including one AtomicPhys TOC link to a missing notebook and several links to QM1/QM2 or other external course notebooks.

## Next

- decide how AtomicPhys should handle unresolved cross-course notebook links
- improve export validation and error messages
- add focused automated tests when a test structure is introduced
- prepare for repository synchronization workflows
- design Google Classroom integration

## Future

- repository synchronization
- Google Classroom API integration
- generated Classroom materials
- richer course metadata
