class CourseConfig:
    """Publishing configuration for a course."""

    def __init__(self, github_repo=None, github_branch="main"):
        self.github_repo = github_repo
        self.github_branch = github_branch
