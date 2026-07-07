class CourseConfig:
    """Publishing configuration for a course."""

    def __init__(
        self,
        github_repo=None,
        github_branch="main",
        github_course_dir="",
        notebook_include_pattern="*.ipynb",
        external_notebook_urls=None,
    ):
        self.github_repo = github_repo
        self.github_branch = github_branch
        self.github_course_dir = github_course_dir
        self.notebook_include_pattern = notebook_include_pattern
        self.external_notebook_urls = dict(external_notebook_urls or {})
