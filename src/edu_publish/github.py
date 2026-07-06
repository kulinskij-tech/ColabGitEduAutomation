from pathlib import Path
import shutil

RESOURCE_DIRS = ("images", "figs", "img", "data")


class GitHubRepository:
    """Represents a GitHub repository associated with a course."""

    def __init__(self, course):
        self.course = course

    def notebook_url(self, notebook):
        repo = self.course.config.github_repo
        if not repo:
            raise ValueError("Course GitHub repository is not configured")

        branch = self.course.config.github_branch
        course_dir = self.course.config.github_course_dir.strip("/")
        path = f"{course_dir}/{notebook.filename}" if course_dir else notebook.filename
        return f"https://github.com/{repo}/blob/{branch}/{path}"

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

    def export(self, destination):
        destination = Path(destination)
        course_dir = self.course.config.github_course_dir.strip("/")
        if not course_dir:
            raise ValueError("Course GitHub directory is not configured")

        destination.mkdir(parents=True, exist_ok=True)
        (destination / "README.md").write_text(
            f"# {self.course.path.name}\n", encoding="utf-8"
        )
        (destination / ".gitignore").write_text(
            ".ipynb_checkpoints/\n__pycache__/\n", encoding="utf-8"
        )

        notebook_dir = destination / course_dir
        notebook_dir.mkdir(parents=True, exist_ok=True)

        for notebook_path in sorted(self.course.path.glob("*.ipynb")):
            shutil.copy2(notebook_path, notebook_dir / notebook_path.name)

        for name in RESOURCE_DIRS:
            resource_dir = self.course.path / name
            if resource_dir.is_dir():
                target_dir = notebook_dir / name
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(
                    resource_dir,
                    target_dir,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".ipynb_checkpoints"),
                )

        return destination
