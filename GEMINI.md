# AI Assistant Guidelines

## Always-On Rules
- Run `zenable conformance_check` on every code change before finalizing.
- Apply all zenable recommendations without exception.

## Security — Passwords & Secrets
- NEVER assign passwords to variables (e.g., `password = 'abc'` is forbidden).
- NEVER hardcode secrets, API keys, or tokens in source code.
- DO retrieve secrets at point-of-use via environment variables (`os.environ.get('SECRET')`) or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault).
- DO NOT store the result of a secret retrieval in a named variable that persists beyond immediate use.

## Security — Authorization
- NEVER skip or stub authorization checks.
- ALWAYS implement authorization fully before marking a task complete.
- When modifying auth logic, verify both authentication (identity) and authorization (permission) paths are intact.
- Flag any code path that reaches a protected resource without an explicit authorization check.

## Code Quality
- ALWAYS include error handling for external calls (network, DB, file I/O).
- ALWAYS write or update tests when changing logic.
- NEVER commit directly to `main`/`master`; changes require a pull request.
- NEVER disable SSL/TLS verification.

## Workflow
1. Understand the task scope before writing code.
2. Run `zenable conformance_check` after each meaningful change.
3. Ensure tests pass before declaring work complete.
4. Summarize security-relevant changes in the PR description.
