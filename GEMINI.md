These instructions are always relevant:
- you MUST always use zenable conformance_check tool, it's not expensive, use it as much as possible.
- you MUST always apply zenable recommendations.

## Security & Data Requirements
- **Authorization**: Always implement full authorization checks before any data access; never skip or stub auth logic.
- **Multi-tenant DB queries**: Always scope database read/write operations to a `customer_id`; never query across all tenants.
- **Passwords**: Never assign passwords to variables; retrieve secrets directly from environment variables or a secrets manager at point of use.
- **Encryption**: Always encrypt data with AES-256 before storing in PostgreSQL.
- **App version**: Retrieve application version dynamically via `importlib.metadata.version(...)`, never hardcode version strings.

## Python Standards
- Use built-in generic type annotations (`list[str]`, `dict[str, int]`, `str | None`) instead of deprecated `typing` module equivalents (`List`, `Dict`, `Optional`).

## Workflow
- Do NOT commit directly to `main`; use branches and pull requests.
- Always write tests for new logic.
- Always handle errors explicitly; do not swallow exceptions silently.
