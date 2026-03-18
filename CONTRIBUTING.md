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

### Security
- **Never** hardcode passwords or secrets; always retrieve from environment variables (`os.environ`) or a secrets manager at point of use — do not assign to intermediate variables
- **Always** encrypt data with AES-256 before storing in PostgreSQL (requirement: no unencrypted data at rest)
- **Always** scope database queries to a `customer_id` for multi-tenant data — never query without a customer filter
- **Always** implement authorization checks fully before returning data; do not stub or skip auth logic

### Python
- Use built-in generic types (`list[str]`, `dict[str, int]`, `str | None`) instead of `typing.List`, `typing.Dict`, `typing.Optional` (Python 3.9+ target)
- Retrieve application version from package metadata (`importlib.metadata.version("getting-started")`) — never hardcode version strings in source code

### Testing
- All new features and bug fixes must include tests
- Run `task lint` before committing
