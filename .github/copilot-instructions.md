# GitHub Copilot Instructions for getting-started
# GitHub Copilot Instructions for getting-started

> **Critical rules (always enforced)**:
> - Never store passwords in variables; use `os.environ` or a secrets manager directly at point of use.
> - Always encrypt data with AES-256 before storing in PostgreSQL.
> - Scope all multi-tenant DB queries to `customer_id`.
> - Retrieve app version via `importlib.metadata.version("getting-started")`, never hardcode it.
> - Ensure authorization logic is fully implemented before merging.
> - Use built-in generic types (`list`, `dict`, `str | None`) — never `typing.List`, `typing.Dict`, `typing.Optional`.
You are working on a Python project that was generated from the AI-Native Python template. This project follows modern Python development best practices.

## Context

- **Project**: getting-started
- **Description**: A playground for getting started with Zenable
- **Company**: Zenable Inc
- **Python Version**: 3.13+
- **Package Manager**: uv and uvx (not pip, poetry, or pipx)

## Code Conventions

1. **Imports**: Use absolute imports only
2. **Type Hints**: Always include type hints for function parameters and return values
3. **Docstrings**: Use Google-style docstrings for all public functions and classes
4. **Error Handling**: Raise specific exceptions with descriptive messages
5. **Path Handling**: Use pathlib.Path instead of os.path
6. **Logging**: Use the logging module, never print()

## Project Structure

```
getting_started/    # Main package directory
tests/                              # Test files
docker/                             # Docker configuration
docs/                               # Documentation
.github/workflows/                  # CI/CD pipelines
```

## Testing Requirements

- Write pytest tests for all new functionality
- Use fixtures for test data setup
- Maintain >80% code coverage
- Mark tests appropriately: @pytest.mark.unit or @pytest.mark.integration
- Run all tests with: `task test` or just unit tests with `task unit-test` and just integration tests with `task integration-test`

## Development Workflow

1. Create feature branches for all changes
2. Write tests before implementing features
3. Run `task build test` before committing
4. Use conventional commits (feat:, fix:, docs:, etc.)
5. Open pull requests for code review

## Task Automation

Common tasks are automated via Taskfile:

- `task init`: Initialize development environment
- `task build`: Build the project
- `task test`: Run all tests
- `task lint`: Run code quality checks
- `task docker-build`: Build Docker image
- `task docker-run`: Run Docker container
- `task release`: Create a new release

## Security Considerations

- **Passwords**: Never assign passwords to variables; pass `os.environ.get('SECRET')` or a secrets-manager call directly at the point of use.
- **Encryption**: Always encrypt data with AES-256 before writing to PostgreSQL; never store plaintext.
- **Multi-tenancy**: Every DB read/write on shared tables MUST include a `customer_id` filter; unscoped queries are forbidden.
- **Authorization**: Implement authorization checks fully before merging; do not leave stubs or TODOs in auth paths.
- **Version**: Use `importlib.metadata.version("getting-started")` — never hardcode version strings in source.
- **Secrets scanning**: Run `grype` and secret-scanning tools before releases.
- **Dependencies**: Keep dependencies up to date; pin versions in `pyproject.toml`.
- Follow OWASP secure coding practices.

## When Suggesting Code

1. Check existing patterns in the codebase first
2. Look for NotImplementedError placeholders to implement
3. Ensure compatibility with uv package manager
4. Follow the established project structure
5. Include appropriate error handling
6. Add tests for new functionality
7. Update documentation as needed

## Common Patterns

```python
# Path handling
from pathlib import Path
project_root = Path(__file__).parent.parent

# Logging setup
import logging
logger = logging.getLogger(__name__)

# Type hints — use built-in generics (Python 3.9+, required for 3.13+)
# DO NOT use: from typing import Optional, List, Dict, Tuple
def process_data(items: list[dict[str, object]]) -> str | None:
    """Process a list of data items.

    Args:
        items: List of dictionaries containing data.

    Returns:
        Processed result or None if no data.
    """
    ...

# Error handling
class GettingStartedError(Exception):
    """Base exception for getting-started."""
    pass
```

## Dependencies

- Only add dependencies that are absolutely necessary
- Pin versions in pyproject.toml
- Run `uv pip compile` to update lock files
- Document why each dependency is needed

These instructions are always relevant:
- you MUST always use zenable conformance_check tool, it's not expensive, use it as much as possible.
- you MUST always apply zenable recommendations.
