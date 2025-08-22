# Contributing to Schedulo API

Contributions are more than welcome! We appreciate all forms of contributions, from bug reports and documentation improvements to new features and university integrations.

## Getting Started

If you're looking for ideas, check out the [issues page](https://github.com/Rain6435/uoapi/issues) in the GitHub repository for this project.

### Repository Structure

- **Primary development branch**: `dev`
- **Feature branches**: Create from `dev` and merge back via pull requests
- **Package name**: `schedulo-api` (installable via `pip install schedulo-api`)
- **CLI command**: `uoapi`

## Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/uoapi.git
   cd uoapi
   git checkout dev
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .[tests]
   ```

3. **Run tests to ensure everything works**:
   ```bash
   make test     # or pytest
   ```

## Adding New Features

### University Integration

To add support for a new university, create a new module following the established pattern:

1. **Create module structure**:
   ```
   src/uoapi/your_university/
   ├── __init__.py
   ├── cli.py
   ├── models.py
   ├── discovery.py (or scraper.py)
   └── README.md (optional)
   ```

2. **Add to module list**:
   Add your module name to `src/uoapi/__modules__` file.

3. **CLI Integration**:
   Your module must export these in `__init__.py`:
   - `parser` - CLI argument parser function
   - `cli` - CLI execution function
   - `help` - Short help text
   - `description` - Detailed description
   - `epilog` - Usage examples

   Use the `@make_parser` and `@make_cli` decorators from `cli_tools.py`.

### Data Models

- Use **Pydantic v1** for data validation (requirement: `pydantic<2`)
- Include comprehensive **type annotations**
- Follow existing patterns from `uoapi.course.models` or `uoapi.carleton.models`
- Implement JSON serialization helpers

### Example Module Structure

See `src/uoapi/carleton/` for a complete example of university integration.

## Testing Requirements

### Test Framework
- **Primary**: `pytest` (modern, preferred)
- **Legacy**: `unittest` (for existing tests)
- **Location**: `tests/` directory mirroring `src/uoapi/` structure

### Writing Tests

1. **Create test files**:
   ```bash
   tests/your_module/
   ├── test_models.py
   ├── test_cli.py
   └── test_integration.py
   ```

2. **Test categories**:
   - **Unit tests**: Individual component testing
   - **Integration tests**: Module interaction testing (mark with `@pytest.mark.integration`)
   - **CLI tests**: Command-line interface testing

3. **Coverage requirements**: Aim for >70% test coverage

4. **Running tests**:
   ```bash
   make test           # All tests with coverage
   make test-unit      # Unit tests only
   pytest tests/your_module/  # Specific module
   ```

### Mocking Network Requests

- Use `httmock` for HTTP request mocking
- See `tests/timetable/test_query_timetable.py` for examples
- Mark network-dependent tests with `@pytest.mark.network`

## Code Quality Standards

### Style and Linting

Run quality checks before submitting:

```bash
make check-all      # All quality checks
make lint          # Flake8 linting
make check         # Type checking with mypy
make format        # Code formatting with black
```

### Code Standards

- **Line length**: 100 characters maximum
- **Complexity**: Keep functions under complexity 10
- **Type annotations**: Required for all public functions
- **Docstrings**: Required for all modules, classes, and public functions
- **Import style**: Use absolute imports

### Documentation

- **Docstrings**: Google style docstrings
- **Type hints**: Complete type annotations
- **README updates**: Add usage examples for new features
- **API documentation**: Auto-generated from docstrings

## Pull Request Process

1. **Create feature branch from `dev`**:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow coding standards
   - Add comprehensive tests
   - Update documentation

3. **Run quality checks**:
   ```bash
   make test
   make check-all
   ```

4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add University X integration"
   ```

5. **Push and create pull request**:
   - Target the `dev` branch
   - Include description of changes
   - Reference any related issues

6. **CI/CD Pipeline**:
   - All tests must pass
   - Code coverage must meet threshold
   - Linting and type checking must pass

## Release Process

### Version Numbering

We use semantic versioning (`<major>.<minor>.<patch>`):

- **Major**: Breaking changes or major architecture updates
- **Minor**: New features, backward-compatible
- **Patch**: Bug fixes, backward-compatible

### Creating Releases

1. **Update version** in `src/uoapi/__version__.py`
2. **Create GitHub release** with tag `vX.Y.Z`
3. **Automated publishing**: CI/CD automatically publishes to PyPI

## Current Architecture

### Module System
- **Auto-discovery**: Modules listed in `__modules__` are automatically loaded
- **CLI integration**: Subcommands auto-generated from module `parser()` functions
- **Entry point**: `uoapi=uoapi.cli:cli`

### Supported Universities
- **University of Ottawa**: Course data, timetables, important dates, Rate My Professor
- **Carleton University**: Course discovery, timetable information

### Dependencies
- **Core**: `requests`, `regex`, `bs4`, `lxml`, `pandas`, `parsedatetime`, `pydantic<2`
- **Testing**: `pytest`, `mypy`, `flake8`, `black`, `bandit`, `httmock`
- **Python**: 3.10+ required

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/Rain6435/uoapi/issues)
- **Discussions**: Use GitHub Discussions for questions
- **Examples**: See existing modules for implementation patterns

## Recognition

Contributors will be acknowledged in releases and the project README. Thank you for helping improve Schedulo API!
