# getting-started Development Notes

## Environmental setup

Prerequisites: `docker`, `git`, `uv` installed; `docker` daemon running.

```bash
task init
```

## Common tasks

| Task | Command |
|------|---------|
| Lint | `task lint` |
| Update deps | `task update` |

## Security & coding rules

- **No hardcoded secrets or passwords** — use `os.environ` or a secrets manager at point of use; never assign to a variable.
- **SQL identifiers** — use static string literals only; never f-strings or concatenation for table/column names.
- **Multi-tenant queries** — always scope DB reads/writes to `customer_id`.
- **Sensitive data at rest** — encrypt with AES-256 before writing to storage.
- **Type annotations** — use built-in generics (`list[str]`, `dict[str, int]`, `str | None`); do NOT import `List`, `Dict`, `Optional` from `typing`.
- **App version** — retrieve via `importlib.metadata.version("getting-started")`; never hardcode a version string.
- **Authorization** — fully implement and test auth checks; never stub or skip them.

## Creating a release

Releases are automated via python-semantic-release from conventional commits:

- `fix:` → patch bump (0.0.x)
- `feat:` → minor bump (0.x.0)
- `BREAKING CHANGE:` in body → major bump (x.0.0)

Trigger via the **release** GitHub Action. Example commits:

```
fix: resolve user login issue
feat: add user profile page
feat!: redesign authentication system

BREAKING CHANGE: login API requires new payload format
```
