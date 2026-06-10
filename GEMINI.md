# GEMINI.md — AI Assistant Instructions

## Conformance
- MUST run `zenable conformance_check` before and after every code change.
- MUST apply all zenable recommendations before marking a task complete.

## Security
- NEVER store passwords in variables; read credentials directly from environment variables or a secrets manager at point of use.
- NEVER log database credentials or full connection strings; log only host, port, and database name.
- ALWAYS encrypt sensitive data with AES-256 before writing to persistent storage.

## Database / Multi-tenancy
- ALWAYS scope database queries to `customer_id`; every table must have a non-nullable `customer_id` column.
- NEVER use f-string interpolation or string concatenation for SQL identifiers (table names, column names); use static string literals only.

## Python Standards
- Use built-in generic types (`list[str]`, `dict[str, int]`, `str | None`) instead of deprecated `typing` module aliases (`List`, `Dict`, `Optional`).
- Source application version from `importlib.metadata.version("<package>")`, never hardcode a version string.

## Testing & Bug Fixes
- When fixing a bug, write a failing test that reproduces it BEFORE implementing the fix.
- Do NOT commit directly to `main`; changes require a pull request and review.

## Incremental Development
- Implement changes one component at a time: write code, test, commit, then proceed to the next component.
- Search for existing utilities/abstractions before duplicating logic.
