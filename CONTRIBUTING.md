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

## Running tests

```bash
task test
```

Run tests before opening a pull request. All tests must pass.

## Security requirements

- **Never** assign passwords or secrets to variables; retrieve them via `os.environ.get('SECRET')` or a secrets manager at the point of use.
- **Never** hardcode credentials, API keys, or tokens in source files.
- All database queries on multi-tenant data **must** be scoped to a `customer_id`.
- Authorization logic must be fully implemented before merging — do not merge stubs or TODOs in auth paths.

## Pull request process

1. Branch from `main`; do **not** commit directly to `main`.
2. Ensure `task lint` and `task test` pass locally.
3. Use conventional commit messages (see [Creating a release](#creating-a-release)).
4. Request at least one reviewer before merging.