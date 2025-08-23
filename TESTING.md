# Testing Guide for Schedulo API

This document provides comprehensive information about the testing infrastructure, test suites, and quality assurance processes for the schedulo-api package.

## Test Infrastructure

### Test Framework
- **Primary**: `pytest` with coverage reporting
- **Coverage**: `pytest-cov` for detailed coverage analysis
- **Mocking**: `unittest.mock` and `httmock` for HTTP mocking
- **Markers**: Custom markers for test categorization

### Test Structure
```
tests/
├── carleton/                   # Carleton University functionality
│   ├── test_carleton_simple.py   # Models and basic integration
│   └── __init__.py
├── cli/                        # Command-line interface
│   ├── test_cli.py             # CLI parsing and subcommands
│   └── __init__.py
├── course/                     # University of Ottawa courses
│   ├── test_models.py          # Pydantic data models
│   ├── test_regress.py         # Regression tests
│   └── data/                   # Test data files
└── timetable/                  # Timetable functionality
    ├── test_query_timetable.py # Timetable querying
    └── data/                   # Mock HTTP responses
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
Test individual components in isolation:
- Data model validation
- Utility functions
- Parser logic
- Error handling

### Integration Tests (`@pytest.mark.integration`)
Test component interaction:
- CLI integration
- Module loading
- End-to-end data flow
- Cross-module dependencies

### Regression Tests (`@pytest.mark.regress`)
Prevent regressions in existing functionality:
- Historical data validation
- Known good outputs
- HTML parsing accuracy

### CLI Tests (`@pytest.mark.cli`)
Test command-line interface:
- Argument parsing
- Subcommand discovery
- Error handling
- Output formatting

## Running Tests

### Basic Test Commands
```bash
# Run all tests with coverage
make test

# Run specific test categories
make test-unit
make test-integration
make test-cli

# Run fast tests (no coverage)
make test-fast

# Generate HTML coverage report
make test-coverage
```

### Advanced Test Commands
```bash
# Run tests with specific markers
pytest -m "unit"
pytest -m "integration"
pytest -m "not slow"

# Run tests in parallel (faster)
pytest -n auto

# Run specific test files
pytest tests/course/test_models.py
pytest tests/cli/test_cli.py::TestCliTools

# Verbose output with details
pytest -v --tb=long

# Stop on first failure
pytest -x
```

## Test Coverage

### Coverage Requirements
- **Minimum**: 70% overall coverage
- **Target**: 80%+ for core modules
- **Reports**: HTML, XML, and terminal output

### Coverage Configuration
Located in `pytest.ini`:
```ini
[coverage:run]
source = src/
omit =
    */tests/*
    */test_*
    */__pycache__/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if __name__ == .__main__.:
```

### Viewing Coverage Reports
```bash
# Generate and view HTML report
make test-coverage
# Opens htmlcov/index.html in browser

# Terminal coverage report
pytest --cov=src --cov-report=term-missing

# XML report for CI/CD
pytest --cov=src --cov-report=xml
```

## Test Data Management

### Mock Data
- **HTTP Responses**: Stored in `tests/*/data/` directories
- **Course Data**: Historical course information for regression testing
- **Timetable Responses**: Mock university server responses

### Test Fixtures
- **Temporary Files**: Automatic cleanup after tests
- **Mock Objects**: Consistent mock configurations
- **Database State**: Isolated test environments

## Continuous Integration

### GitHub Actions Workflow
Located in `.github/workflows/ci.yml`:

#### Test Matrix
- **Python Versions**: 3.10, 3.11, 3.12
- **Operating System**: Ubuntu Latest
- **Dependencies**: Latest stable versions

#### Quality Gates
1. **Security Scan**: Bandit security analysis
2. **Code Formatting**: Black formatting check
3. **Linting**: Flake8 code analysis
4. **Type Checking**: mypy static analysis
5. **Unit Tests**: pytest with coverage
6. **Integration Tests**: Full workflow testing
7. **Package Build**: Successful package creation

#### Artifacts
- Coverage reports
- Test results
- Security scan reports
- Built packages

### Branch Protection
Tests are enforced via GitHub branch protection rules:
- All CI checks must pass before merge
- Minimum coverage thresholds enforced
- Code review required for changes

## Writing New Tests

### Test Organization
```python
class TestModuleName:
    """Test suite for ModuleName functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        pass

    def test_basic_functionality(self):
        """Test basic functionality works correctly."""
        pass

    @pytest.mark.integration
    def test_integration_scenario(self):
        """Test integration with other components."""
        pass

    @pytest.mark.parametrize("input,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
    ])
    def test_parameterized_cases(self, input, expected):
        """Test multiple scenarios with parameters."""
        assert function(input) == expected
```

### Best Practices

#### Test Naming
- Use descriptive names: `test_course_parsing_with_prerequisites`
- Follow pattern: `test_<what>_<when>_<expected>`
- Group related tests in classes

#### Assertions
- Use specific assertions: `assert result.status == "success"`
- Include helpful messages: `assert x == y, f"Expected {y}, got {x}"`
- Test both positive and negative cases

#### Mocking
```python
from unittest.mock import Mock, patch

@patch('module.external_service')
def test_with_mock(mock_service):
    mock_service.return_value = {"data": "test"}
    result = function_that_calls_service()
    assert result == expected_result
    mock_service.assert_called_once_with(expected_args)
```

#### Fixtures
```python
@pytest.fixture
def sample_course():
    """Provide a sample course for testing."""
    return Course(
        course_code="TEST101",
        title="Test Course",
        credits=3,
        description="A test course"
    )

def test_course_serialization(sample_course):
    data = sample_course.dict()
    assert data["course_code"] == "TEST101"
```

## Performance Testing

### Slow Test Marking
```python
@pytest.mark.slow
def test_large_dataset_processing():
    """Test processing of large datasets."""
    # This test takes > 5 seconds
    pass
```

### Running Performance Tests
```bash
# Include slow tests
pytest -m "slow"

# Exclude slow tests (default)
pytest -m "not slow"

# Time individual tests
pytest --durations=10
```

## Testing Guidelines

### What to Test
- ✅ **Public APIs**: All public methods and functions
- ✅ **Edge Cases**: Empty inputs, null values, boundary conditions
- ✅ **Error Conditions**: Exception handling and error messages
- ✅ **Integration Points**: Module boundaries and external dependencies
- ✅ **Data Validation**: Model validation and serialization

### What Not to Test
- ❌ **Private Methods**: Internal implementation details
- ❌ **Third-party Libraries**: External library functionality
- ❌ **Simple Property Access**: Basic getters/setters
- ❌ **Configuration**: Static configuration values

### Test Independence
- Each test should be independent and isolated
- Tests should not depend on execution order
- Clean up resources after each test
- Use fixtures for shared setup

## Debugging Tests

### Common Issues
```bash
# Test discovery problems
pytest --collect-only

# Import errors
pytest --tb=long

# Coverage not working
pytest --cov-config=pytest.ini

# Verbose debugging
pytest -vvv --tb=long --capture=no
```

### Interactive Debugging
```python
def test_with_debugging():
    import pdb; pdb.set_trace()  # Breakpoint
    result = function_under_test()
    assert result == expected
```

## Quality Metrics

### Current Test Statistics
- **Total Tests**: 71 tests
- **Test Files**: 6 test modules
- **Coverage**: 70%+ target
- **Categories**: Unit, Integration, CLI, Regression

### Quality Trends
Track these metrics over time:
- Test count growth
- Coverage percentage
- Test execution time
- Failure rates

This comprehensive testing infrastructure ensures the reliability, maintainability, and quality of the schedulo-api package across all supported environments and use cases.
