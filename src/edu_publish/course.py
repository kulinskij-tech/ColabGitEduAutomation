from pathlib import Path


class Course:
    """Represents a course directory."""

    def __init__(self, path):
        self.path = Path(path)

        # These will be populated during discovery.
        self.toc = None
        self.notebooks = []
        self.missing = []

    def __repr__(self):
        return f"Course(path={self.path!r})"