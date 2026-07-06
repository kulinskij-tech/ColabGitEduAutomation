from pathlib import Path
import sys

from edu_publish.course import Course
from edu_publish.github import GitHubRepository


def print_usage():
    print("Usage:")
    print("  python -m edu_publish analyze /path/to/course")
    print("  python -m edu_publish github-preview /path/to/course --repo owner/name")


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

    print_usage()
    raise SystemExit(1)


if __name__ == "__main__":
    main()
