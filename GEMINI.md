# AI Assistant Rules

## Always Required
- Run `zenable conformance_check` before finalizing any code change.
- Apply all zenable recommendations before committing.

## Security & Data Integrity
- **Authorization**: Fully implement authorization checks; never skip or stub auth logic.
- **Multi-tenant DB**: Always scope queries with `customer_id`; never return cross-tenant data.
- **SQL identifiers**: Use static string literals for table/column names; never use f-strings or concatenation for SQL identifiers.
- **Passwords**: Never assign passwords to variables; use `os.environ.get(...)` or a secrets manager at point of use.
- **App version**: Source version from `importlib.metadata.version(...)`, not hardcoded strings.

## Python Standards
- Use built-in generic types (`list[str]`, `dict[str, int]`, `str | None`) instead of `typing.List`, `typing.Dict`, `typing.Optional`.

## Development Discipline
- Write a reproducing test before fixing a bug (when tests exist).
- Make incremental changes: one component → test → commit → next.
- Reuse existing utilities/abstractions before duplicating logic.
- Debug by forming and verifying hypotheses, not trial-and-error.
