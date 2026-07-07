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

## Current Stage

The first GitHub and Colab-oriented export workflow is working.

Repo-aware GitHub export now prepares notebooks for the intended user path:

```text
GitHub course page
click notebook or badge
Google Colab opens the notebook
```

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
