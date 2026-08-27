# Claude Instructions for getting-started

You are working with a Python project that follows modern development practices and was generated from the AI-Native Python Paved Road template.

## Project Information

- **Name**: getting-started
- **Package**: getting_started
- **Description**: A playground for getting started with Zenable
- **Organization**: Zenable Inc (zenable.io)
- **Python Version**: 3.13+

## Technology Stack

- **Package Manager**: uv and uvx (not pip, poetry, or pipx)
- **Testing**: pytest with coverage reporting
- **Linting**: ruff, pyright
- **Security**: grype vulnerability scanning, syft SBOM generation
- **CI/CD**: GitHub Actions
- **Containerization**: Docker with multi-platform support

## Project Structure

```
getting_started/    # Main package code
├── __init__.py                     # Package initialization
├── __main__.py                     # CLI entry point
└── ...                             # Your modules

tests/                              # Test suite
├── unit/                           # Unit tests
├── integration/                    # Integration tests
└── conftest.py                     # pytest fixtures

docker/                             # Docker configuration
docs/                               # Documentation
.github/workflows/                  # CI/CD pipelines
```

## Development Workflow

### Initial Setup

```bash
task init                # Set up development environment
```

### Daily Development

```bash
task build              # Build the project
task test               # Run all tests
task lint               # Check code quality
task format             # Auto-format code
```

### Before Committing

1. Run `task build test` to ensure everything passes
2. Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, etc.
3. Write descriptive commit messages
4. When adding external dependencies, explicitly note them in commit messages

## Code Guidelines

### Style Rules

1. **Imports**: Always use absolute imports
2. **Type Hints**: Required for all function signatures
3. **Docstrings**: Google-style for all public APIs
4. **Line Length**: Maximum 120 characters
5. **Naming**: snake_case for functions/variables, PascalCase for classes
6. **Dependencies**: Prefer built-in packages over external dependencies where reasonable

### Best Practices

- Use built-in types for hints (`list[str]`, `str | None`) — Python 3.10+ syntax; avoid `from typing import List, Optional`
- Use `pathlib.Path` for file operations (not `open("...")` with string paths)
- Use `logging.getLogger(__name__)` per module; never `print()` for diagnostics
- Use context managers (`with`) for all file/resource access
- Raise specific exceptions with descriptive messages; never silently swallow errors

## Testing Requirements

1. Write tests for all new functionality
2. Use pytest fixtures for test setup
3. Maintain >80% code coverage
4. Mark tests appropriately:
   ```python
   @pytest.mark.unit
   def test_calculation():
       ...

   @pytest.mark.integration
   def test_api_call():
       ...
   ```

## Security Guidelines

1. **Never hardcode secrets** - use environment variables
2. **Validate all inputs** - especially from external sources
3. **Use parameterized queries** - prevent SQL injection
4. **Keep dependencies updated** - check with `task security-scan`
5. **Follow OWASP guidelines** - for web-facing code

## Common Patterns
### Configuration Management
- Load YAML config via `yaml.safe_load()` with `pathlib.Path.open()`
- Never use `yaml.load()` (unsafe deserialization)

### Error Handling
- Define a base `GettingStartedError(Exception)` and specific subclasses
- Catch narrow exceptions; re-raise as domain errors with context
- Never use bare `except:` or `except Exception` without logging + re-raise

### CLI Entry Points
- Use `argparse`; support `--verbose`/`-v` to set `logging.DEBUG`
- Catch `KeyboardInterrupt` and unexpected exceptions at top level; call `sys.exit(1)` on failure
- Use `logger.exception()` (not `logger.error()`) for unexpected errors to capture tracebacks

## Task Reference

- `task init`: Initialize development environment
- `task build`: Build the project
- `task test`: Run tests with coverage
- `task lint`: Run all linters
- `task format`: Auto-format code
- `task security-scan`: Check for vulnerabilities
- `task docker-build`: Build Docker image
- `task docker-run`: Run in Docker container
- `task release`: Create a release

## Important Notes

1. Look for `NotImplementedError` markers - these indicate where you need to add business logic
2. All public APIs must have comprehensive docstrings
3. Keep dependencies minimal - justify each addition
4. Follow Zenable Inc coding standards
5. Update tests when modifying functionality
6. Prefer built-in Python packages over external dependencies where reasonable
7. When adding new external dependencies, explicitly mention them in commit messages

## Getting Help

- Check existing code patterns first
- Review test cases for usage examples
- Consult the main README.md for project overview
- Use logging liberally for debugging
