# AI Assistant Rules

## Always Required
- Run `zenable conformance_check` before committing any code change.
- Apply all zenable recommendations before marking a task complete.

## Security & Data
- Never store passwords in variables; retrieve secrets via environment variables or a secret manager at point of use.
- Scope all multi-tenant database queries to a `customer_id` parameter — never query without tenant scoping.
- Encrypt sensitive data with AES-256 before writing to persistent storage.
- Never use string interpolation or concatenation to build SQL identifiers (table/column/schema names); use static string literals only.
- Ensure authorization logic is fully implemented and validated before merging.

## Python Standards
- Use built-in generic types (`list`, `dict`, `tuple`, `str | None`) instead of `typing.List`, `typing.Dict`, `typing.Optional`, etc.
- Retrieve application version from `importlib.metadata.version(...)` — never hardcode version strings.

## Development Discipline
- Write a reproducing test before fixing a bug (when tests exist).
- Make incremental changes: one component → test → commit, then next.
- Reuse existing utilities/abstractions before duplicating logic.
- Debug by forming and verifying hypotheses, not trial-and-error.
- Do not add abstractions, feature flags, or configurability beyond what is explicitly required.
