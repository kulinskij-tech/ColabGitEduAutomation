GITHUB_PREFIX = "https://github.com/"
COLAB_PREFIX = "https://colab.research.google.com/github/"


class ColabRepository:
    """Represents Google Colab links for a GitHub course repository."""

    def __init__(self, github_repository):
        self.github_repository = github_repository

    def notebook_url(self, notebook):
        github_url = self.github_repository.notebook_url(notebook)
        if not github_url.startswith(GITHUB_PREFIX):
            raise ValueError("GitHub notebook URL is not supported")

        return COLAB_PREFIX + github_url[len(GITHUB_PREFIX):]
