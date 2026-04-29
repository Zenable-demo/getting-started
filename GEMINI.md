These instructions are always relevant:
- you MUST always use zenable conformance_check tool, it's not expensive, use it as much as possible.
- you MUST always apply zenable recommendations.

## Security
- DO NOT assign passwords to variables; use `os.environ.get('SECRET')` or a secrets manager at point of use.
- Encrypt sensitive data with AES-256 before writing to persistent storage.
- Ensure all authorization logic is fully implemented; never skip or stub auth checks.
- All database queries on multi-tenant data MUST include a `customer_id` scope parameter.

## SQL Safety
- DO NOT use f-strings or string concatenation for SQL identifiers (table/column names); use static string literals.
- Use parameterized queries for all data values.

## Python Standards
- Use built-in generic types (`list[str]`, `dict[str, int]`, `str | None`) instead of deprecated `typing.List`, `typing.Dict`, `typing.Optional`.
- Source application version from `importlib.metadata.version("package-name")`, not hardcoded string literals.

## Testing & Bug Fixes
- When fixing a bug, first write a failing test that reproduces it, then implement the fix.
- Do not commit directly to main; changes require review.

## Development Discipline
- Make incremental changes: one component, test, commit, then next.
- Search for existing utilities/abstractions before duplicating logic.
- Debug by forming and verifying hypotheses, not trial-and-error.
