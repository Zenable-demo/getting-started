# getting-started Development Notes

## Environmental setup

Ensure you have `docker`, `git`, and `uv` installed locally, and the `docker` daemon is running. Then run the following command to finish the repo setup
locally:

```bash
task init
```

## Linting locally

```bash
task lint
```

## Updating the dependencies

```bash
task update
```

## Creating a release

Releases are created automatically by python-semantic-release based on conventional commits. The version bump is determined by your commit messages:

- `fix:` commits bump patch version (0.0.x)
- `feat:` commits bump minor version (0.x.0)
- `BREAKING CHANGE:` in commit body bumps major version (x.0.0)

To create a release, use the release GitHub action:

Example commit messages:

```bash
# Patch release (0.0.1 -> 0.0.2)
git commit -m "fix: resolve user login issue"

# Minor release (0.0.2 -> 0.1.0)
git commit -m "feat: add user profile page"

# Major release (0.1.0 -> 1.0.0)
git commit -m "feat!: redesign authentication system

BREAKING CHANGE: The login API now requires a different payload format"
BREAKING CHANGE: The login API now requires a different payload format"
```

## Development Guidelines

### Security
- **Never assign passwords to variables.** Use `os.environ.get('SECRET')` or a secrets manager directly at the point of use.
- **Never log credentials or full connection strings.** Log only non-sensitive fields (host, port, db name, user).
- **Encrypt sensitive data with AES-256 before writing to persistent storage.**
- **All database queries on multi-tenant data must include a `customer_id` scope.** Every store/retrieve function must accept `customer_id` as a non-nullable parameter and filter by it.

### SQL Safety
- **Never use f-strings or string concatenation for SQL identifiers** (table names, column names, schema names). Use static string literals or identifier-quoting utilities.
- **Always use parameterized queries** for data values (`%s` placeholders, never inline values).

### Python Style
- **Use built-in generic types** for annotations (`list[str]`, `dict[str, int]`, `str | None`). Do **not** import `List`, `Dict`, `Optional`, `Tuple` from `typing` (deprecated in Python 3.9+, removed in 3.13+).
- **Source application version from package metadata**, not hardcoded strings:
  ```python
  from importlib.metadata import version, PackageNotFoundError
  try:
      app_version = version("getting-started")
  except PackageNotFoundError:
      app_version = "unknown"
  ```

### Testing & Bug Fixes
- **Write a failing test before fixing a bug.** Add a test that reproduces the bug, confirm it fails, then implement the fix.
- Do not commit directly to `main`. Open a pull request and ensure CI passes.

### Incremental Changes
- Keep PRs small and focused. Implement one component, test it, commit, then move to the next.
- Search for existing utilities/abstractions before duplicating logic.