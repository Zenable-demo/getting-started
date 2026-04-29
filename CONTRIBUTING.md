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
```
```

## Development Guidelines

### Testing
- **Bug fixes require a failing test first**: Before fixing any bug, write a test that reproduces and fails on the bug, then implement the fix. This ensures regression coverage and confirms the fix addresses the root cause.
- Do not merge bug fixes without a corresponding new or updated test.

### Security
- **Never assign passwords to variables**. Read credentials directly from environment variables or a secrets manager at the point of use (e.g., `os.environ.get('DB_PASSWORD')`).
- **Encrypt sensitive data with AES-256 before writing to persistent storage**. Use `cryptography.hazmat.primitives.ciphers.aead.AESGCM` with a 256-bit key.
- **Never use string interpolation or concatenation for SQL identifiers** (table names, column names). Use static string literals or identifier-quoting utilities.

### Multi-tenancy
- All database read/write functions on multi-tenant data **must** accept a `customer_id` parameter and scope every query to that customer. Omitting `customer_id` from a query function is a data-isolation violation.

### Python style
- Use built-in generic types for annotations (`list[str]`, `dict[str, int]`, `str | None`) instead of deprecated `typing` equivalents (`List`, `Dict`, `Optional`). The project targets Python 3.9+.
- Source the application version from package metadata, not hardcoded strings:
  ```python
  from importlib.metadata import version, PackageNotFoundError
  try:
      app_version = version("getting-started")
  except PackageNotFoundError:
      app_version = "unknown"
  ```
