# Development Workflow

## Philosophy

Prefer many small commits.

Every commit should preserve behavior.

Typical cycle:

1. Explain design.
2. Implement one small change.
3. Test.
4. Commit.
5. Push.

Avoid large rewrites.

---

## Refactoring Rules

Do not change behavior unless explicitly requested.

Keep diffs small.

Do not rename files unnecessarily.

Avoid speculative abstractions.

Objects should represent domain concepts.

---

## Code Style

Use pathlib.

Prefer properties over public attributes when appropriate.

Keep functions short.

Prefer composition over duplicated discovery logic.

---

## Testing

Primary test:

python -m edu_publish analyze COURSE_DIRECTORY

Expected output should remain identical after refactoring.