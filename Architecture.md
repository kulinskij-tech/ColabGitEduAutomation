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

The project follows small, incremental object-oriented design.

Objects represent real domain concepts and keep platform-specific behavior in
platform-specific classes.

Current domain objects:

- Course
- TOC
- Notebook
- CourseConfig
- GitHubRepository
- ColabRepository

Planned domain objects:

- Google Classroom publishing object

---

## Course

Represents one course directory.

Responsibilities:

- discover the TOC notebook
- discover notebooks linked from the TOC
- hold publication configuration

Course should not generate platform-specific URLs.

---

## Notebook

Represents one notebook.

Responsibilities:

- filename
- filesystem path
- existence check

Notebook objects do not generate URLs.

---

## TOC

Represents the course TOC notebook.

Responsibilities:

- read notebook markdown
- discover linked notebooks

---

## CourseConfig

Stores publication configuration.

Current fields:

- `github_repo`
- `github_branch`
- `github_course_dir`

---

## GitHubRepository

Represents a GitHub repository associated with a course.

Responsibilities:

- generate GitHub notebook URLs
- generate GitHub preview reports
- export a GitHub-ready course directory
- copy notebooks and supported resource directories
- apply export-only notebook transformations when repository information is configured

The export-only Colab transformations currently are:

- rewrite exported local notebook links to Colab URLs
- insert one first-cell Open in Colab badge in each exported notebook

GitHubRepository does not call GitHub APIs, execute git commands, or access the
network.

---

## ColabRepository

Represents Google Colab links for notebooks hosted in a GitHub repository.

Responsibilities:

- convert GitHub notebook URLs into Google Colab URLs

ColabRepository reuses GitHubRepository for GitHub URL generation so URL logic
stays centralized.

---

## Export Flow

`github-export` creates a GitHub-ready directory containing:

```text
DESTINATION/
    README.md
    .gitignore
    COURSE_DIR_NAME/
        *.ipynb
        images/
        figs/
        img/
        data/
```

When `--repo` is not supplied, exported notebooks are copied unchanged.

When `--repo` is supplied, only exported notebooks are transformed:

```text
copy notebook
rewrite local notebook links to Colab URLs
insert Open in Colab badge
write exported notebook if changed
```

Source notebooks are never modified.
