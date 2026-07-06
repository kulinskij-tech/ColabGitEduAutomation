# ColabGitEduAutomation Architecture

## Goal

Provide a reusable Python library for publishing educational Jupyter notebook
courses to multiple platforms:

- GitHub
- Google Colab
- Google Classroom

The same codebase should work on Linux and Windows.

---

## Design Principles

The project follows object-oriented design.

Objects represent real domain concepts.

Current domain objects:

- Course
- Notebook

Planned objects:

- TOC
- GitHubPublisher
- ColabPublisher
- ClassroomPublisher

---

## Course

Represents one course directory.

Responsibilities:

- discover TOC notebook
- discover notebooks
- coordinate publishers

Course should NOT know platform-specific publishing details.

---

## Notebook

Represents one notebook.

Responsibilities:

- filename
- filesystem path
- existence check

Later responsibilities:

- GitHub URL
- Colab URL
- Classroom attachment

---

## TOC

Represents the course TOC notebook.

Responsibilities:

- read notebook markdown
- discover linked notebooks

---

## Publishers

Publishers consume Course objects.

They never rediscover notebooks themselves.

Course
    ├── TOC
    ├── Notebook[]
    ├── GitHubPublisher
    ├── ColabPublisher
    └── ClassroomPublisher

Publishing should reuse the already discovered Course model.