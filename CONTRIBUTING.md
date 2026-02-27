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

## Security guidelines

- **Never hardcode secrets, passwords, or API keys** in source code or commit them to the repository.
- Use environment variables or a secrets manager (e.g., `os.environ.get('SECRET')`) at the point of use — do not assign secrets to intermediate variables.
- Do not disable SSL/TLS verification in any code.
- Authorization and authentication logic must be fully implemented before merging — do not merge placeholder or stub auth code.
