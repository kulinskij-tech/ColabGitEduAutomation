class Notebook:
    """Represents a notebook belonging to a course."""

    def __init__(self, course, filename):
        self.course = course
        self.filename = filename

    @property
    def path(self):
        return self.course.path / self.filename

    @property
    def exists(self):
        return self.path.exists()

    def __repr__(self):
        return f"Notebook({self.filename!r})"