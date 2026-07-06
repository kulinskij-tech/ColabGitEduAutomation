from pathlib import Path
import sys

from edu_publish.discover import analyze_course


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "analyze":
        print("Usage:")
        print("  python -m edu_publish analyze /path/to/course")
        raise SystemExit(1)

    course_path = Path(sys.argv[2])
    analyze_course(course_path)


if __name__ == "__main__":
    main()
