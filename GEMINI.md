# AI Assistant Rules

## Always Required
- Run `zenable conformance_check` on every code change before finalizing.
- Apply all zenable recommendations without exception.

## Security: Passwords
- NEVER assign passwords to variables.
- Use `os.environ.get('...')`, a secrets manager, or `keyring` directly at the point of use.
- Reject any code that stores a password in a named variable (even temporarily).

## Security: Authorization
- Ensure authorization logic is fully implemented before marking a task complete.
- Do NOT stub, skip, or TODO-defer authorization checks.

## Security: Multi-Tenant Database Queries
- ALL database read/write operations on shared tables MUST be scoped to a `customer_id`.
- Never query multi-tenant tables without a `WHERE customer_id = <value>` clause.
- Reject any query that returns rows across multiple customers.

## Testing
- Write tests for every new function or changed behavior.
- Do NOT commit code with no test coverage for security-sensitive paths.

## Version Control
- Do NOT commit directly to `main`/`master`.
- All changes require a pull/merge request.
