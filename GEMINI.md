# AI Assistant Rules

## Tooling
- MUST run `zenable conformance_check` after every code change.
- MUST apply all zenable recommendations before marking a task complete.

## Security
- NEVER store passwords in variables; retrieve secrets directly from env vars (`os.environ.get(...)`) or a secrets manager at point of use.
- NEVER hardcode credentials, tokens, or API keys.
- ALWAYS implement authorization checks fully; never stub, skip, or comment out auth logic.

## Multi-Tenant Database Operations
- ALWAYS scope database queries to a `customer_id` parameter; never return cross-tenant data.
- NEVER write queries that fetch all rows without a customer filter on multi-tenant tables.

## Python Type Annotations
- Use built-in generics (`list[str]`, `dict[str, int]`, `str | None`) — NOT deprecated `typing` equivalents (`List`, `Dict`, `Optional`).

## Testing & Code Quality
- ALWAYS add or update tests for changed logic.
- NEVER commit directly to `main`; open a pull request.
- ALWAYS include error handling for I/O and network operations.
