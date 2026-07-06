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
