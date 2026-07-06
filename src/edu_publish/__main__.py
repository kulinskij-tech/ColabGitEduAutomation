from pathlib import Path
import sys

from edu_publish.colab import ColabRepository
from edu_publish.course import Course
from edu_publish.github import GitHubRepository


def print_usage():
    print("Usage:")
    print("  python -m edu_publish analyze /path/to/course")
    print("  python -m edu_publish github-preview /path/to/course --repo owner/name")
    print("  python -m edu_publish colab-preview /path/to/course --repo owner/name")
    print("  python -m edu_publish github-export /path/to/course /path/to/destination")


def main():
    if len(sys.argv) < 3:
        print_usage()
        raise SystemExit(1)

    command = sys.argv[1]
    course_path = Path(sys.argv[2])

    if command == "analyze":
        course = Course(course_path)
        print(course.report())
        return

    if command == "github-preview":
        if len(sys.argv) != 5 or sys.argv[3] != "--repo":
            print_usage()
            raise SystemExit(1)

        course = Course(course_path)
        course.config.github_repo = sys.argv[4]
        repo = GitHubRepository(course)
        print(repo.publication_report())
        return

    if command == "colab-preview":
        if len(sys.argv) != 5 or sys.argv[3] != "--repo":
            print_usage()
            raise SystemExit(1)

        course = Course(course_path)
        course.config.github_repo = sys.argv[4]
        course.config.github_course_dir = course.path.name
        github = GitHubRepository(course)
        colab = ColabRepository(github)

        for notebook in course.notebooks:
            print(colab.notebook_url(notebook))
        return

    if command == "github-export":
        if len(sys.argv) != 4:
            print_usage()
            raise SystemExit(1)

        course = Course(course_path)
        course.config.github_course_dir = course.path.name
        repo = GitHubRepository(course)
        repo.export(Path(sys.argv[3]))
        return

    print_usage()
    raise SystemExit(1)


if __name__ == "__main__":
    main()
