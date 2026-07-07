from pathlib import Path
import sys

from edu_publish.colab import ColabRepository
from edu_publish.config import CourseConfig
from edu_publish.course import Course
from edu_publish.github import GitHubRepository


def print_usage():
    print("Usage:")
    print("  python -m edu_publish analyze /path/to/course [--notebooks PATTERN]")
    print("  python -m edu_publish github-preview /path/to/course --repo owner/name [--notebooks PATTERN]")
    print("  python -m edu_publish colab-preview /path/to/course --repo owner/name [--notebooks PATTERN]")
    print("  python -m edu_publish github-export /path/to/course /path/to/destination [--repo owner/name] [--notebooks PATTERN] [--external-notebook NOTEBOOK=URL]")


def parse_options(args):
    options = {}
    i = 0
    while i < len(args):
        name = args[i]
        if not name.startswith("--") or i + 1 >= len(args):
            print_usage()
            raise SystemExit(1)
        if name == "--external-notebook":
            options.setdefault(name, []).append(args[i + 1])
        else:
            options[name] = args[i + 1]
        i += 2
    return options


def course_config(options):
    return CourseConfig(
        github_repo=options.get("--repo"),
        notebook_include_pattern=options.get("--notebooks", "*.ipynb"),
        external_notebook_urls=parse_external_notebook_urls(
            options.get("--external-notebook", [])
        ),
    )


def parse_external_notebook_urls(values):
    notebook_urls = {}

    for value in values:
        if "=" not in value:
            raise ValueError(
                "--external-notebook must use NOTEBOOK=URL format"
            )

        notebook, url = value.split("=", 1)
        notebook = Path(notebook).name
        if not notebook or not url:
            raise ValueError(
                "--external-notebook must use NOTEBOOK=URL format"
            )

        notebook_urls[notebook] = url

    return notebook_urls


def main():
    if len(sys.argv) < 3:
        print_usage()
        raise SystemExit(1)

    command = sys.argv[1]
    course_path = Path(sys.argv[2])

    if command == "analyze":
        options = parse_options(sys.argv[3:])
        if set(options) - {"--notebooks"}:
            print_usage()
            raise SystemExit(1)

        course = Course(course_path, course_config(options))
        print(course.report())
        return

    if command == "github-preview":
        options = parse_options(sys.argv[3:])
        if "--repo" not in options or set(options) - {"--repo", "--notebooks"}:
            print_usage()
            raise SystemExit(1)

        course = Course(course_path, course_config(options))
        repo = GitHubRepository(course)
        print(repo.publication_report())
        return

    if command == "colab-preview":
        options = parse_options(sys.argv[3:])
        if "--repo" not in options or set(options) - {"--repo", "--notebooks"}:
            print_usage()
            raise SystemExit(1)

        config = course_config(options)
        config.github_course_dir = course_path.name
        course = Course(course_path, config)
        github = GitHubRepository(course)
        colab = ColabRepository(github)

        for notebook in course.notebooks:
            print(colab.notebook_url(notebook))
        return

    if command == "github-export":
        if len(sys.argv) < 4:
            print_usage()
            raise SystemExit(1)

        destination = Path(sys.argv[3])
        options = parse_options(sys.argv[4:])
        if set(options) - {"--repo", "--notebooks", "--external-notebook"}:
            print_usage()
            raise SystemExit(1)

        config = course_config(options)
        config.github_course_dir = course_path.name
        course = Course(course_path, config)
        repo = GitHubRepository(course)
        repo.export(destination)
        return

    print_usage()
    raise SystemExit(1)


if __name__ == "__main__":
    main()
