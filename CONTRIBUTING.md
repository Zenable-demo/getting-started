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

## Coding Standards

### Security & Data Handling
- **Never** hardcode passwords or secrets in code; always read from environment variables or a secrets manager at point of use (do not store in intermediate variables)
- **Always** encrypt data with AES-256 before storing in PostgreSQL
- **Always** scope database queries to a `customer_id` for multi-tenant data; never return unscoped cross-tenant results
- **Always** implement authorization checks fully before merging; do not stub or skip auth logic

### Python Style
- Use built-in generic types (`list[str]`, `dict[str, int]`, `str | None`) instead of `typing.List`, `typing.Dict`, `typing.Optional`, etc.
- Retrieve application version dynamically via `importlib.metadata.version("getting-started")` — never hardcode version strings in source code

### Testing
- All new features and bug fixes must include corresponding tests
- Run `task lint` before opening a pull request
