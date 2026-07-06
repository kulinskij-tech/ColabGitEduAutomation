class GitHubRepository:
    """Represents a GitHub repository associated with a course."""

    def __init__(self, course):
        self.course = course

    def notebook_url(self, notebook):
        repo = self.course.config.github_repo
        if not repo:
            raise ValueError("Course GitHub repository is not configured")

        branch = self.course.config.github_branch
        return f"https://github.com/{repo}/blob/{branch}/{notebook.filename}"

    def publication_report(self):
        lines = [
            f"TOC: {self.course.toc.name}",
            f"Found {len(self.course.notebooks)} notebooks:",
            "",
        ]

        for i, notebook in enumerate(self.course.notebooks, start=1):
            exists = "OK" if notebook.exists else "MISSING"
            lines.append(
                f"{i:02d}. {notebook.filename} [{exists}] {self.notebook_url(notebook)}"
            )

        return "\n".join(lines)
