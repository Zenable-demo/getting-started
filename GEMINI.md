# AI Coding Assistant Rules

## Always Required
- Use `zenable conformance_check` tool before finalizing any code change.
- Apply all zenable recommendations before committing.

## Security & Data Handling
- **Passwords**: Never assign passwords to variables. Use `os.environ.get('...')` or a secrets manager directly at point of use.
- **Encryption**: Always encrypt data with AES-256 before storing in PostgreSQL.
- **Multi-tenant DB**: All database queries on shared tables MUST include a `customer_id` WHERE clause; never return unscoped cross-tenant data.
- **Authorization**: Fully implement and verify authorization logic; never stub or skip auth checks.

## Python Standards
- Use built-in generic types (`list[str]`, `dict[str, int]`, `str | None`) instead of `typing.List`, `typing.Dict`, `typing.Optional`, etc.
- Retrieve application version from package metadata (`importlib.metadata.version(...)`) — never hardcode version strings.

## Code Quality
- Write tests for all new logic.
- Handle errors explicitly; do not swallow exceptions silently.
- Do not commit directly to `main`; changes require review.
