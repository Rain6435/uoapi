# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Schedulo API** is a FastAPI-based REST API for retrieving public data from Canadian universities (University of Ottawa and Carleton University). The codebase features a clean, layered architecture with clear separation of concerns and full type safety.

- **Package Name**: `schedulo-api`
- **Python Version**: 3.10+
- **Main Entry Point**: `schedulo-server` CLI command or `uoapi.server.app.create_app()`
- **Key Technologies**: FastAPI, Uvicorn, Pydantic, BeautifulSoup, Requests

## Architecture Overview

The codebase follows a **layered clean architecture** pattern:

```
src/uoapi/
├── core/                    # Domain models and interfaces (Pydantic models, abstract base classes)
├── universities/            # University-specific implementations
│   ├── base.py             # BaseUniversityProvider abstract class
│   ├── carleton/           # Carleton University scraper/data provider
│   └── uottawa/            # University of Ottawa scraper/data provider
├── services/               # Business logic (DefaultCourseService, DefaultTimetableService, etc.)
├── server/                 # FastAPI REST API (CLI, app factory, routes)
├── interfaces/             # Legacy compatibility (old API endpoints)
├── timetable/              # Timetable querying logic (Banner system)
├── rmp/                    # Rate My Professor integration
├── course/                 # Legacy course parsing utilities
└── utils/                  # Configuration, patterns, utilities
```

### Key Architecture Patterns

1. **Service Layer**: Business logic is in `services/` (CourseService, TimetableService, RatingService). Services use UniversityProvider implementations to get data.

2. **University Provider Pattern**: Each university implements `UniversityProvider` interface. Services are agnostic to which university is being used.

3. **Pydantic Models**: All data is typed with Pydantic models in `core/models.py` (University, Subject, Course, CourseSection, SearchResult, DiscoveryResult).

4. **Unified API**: Despite different data sources (Carleton vs UOttawa have different systems), the API presents unified models to clients.

## Common Development Tasks

### Building and Running

```bash
# Install in development mode with test dependencies
pip install -e .[tests]

# Start the REST API server
schedulo-server --port 8000

# Start with auto-reload (development)
schedulo-server --reload --log-level debug

# Programmatically (in Python)
from uoapi.server.app import create_app
import uvicorn
app = create_app()
uvicorn.run(app, host="127.0.0.1", port=8000)
```

### Testing

```bash
# Run all tests with coverage (default)
make test                    # or pytest

# Run specific test categories
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make test-cli               # CLI tests only

# Run tests faster (no coverage)
make test-fast              # or pytest --no-cov

# Run specific test file/test
pytest tests/course/test_models.py
pytest tests/course/test_models.py::TestCourseModel::test_some_scenario

# Generate HTML coverage report
make test-coverage

# Check which tests exist
pytest --collect-only
```

Test markers are defined in `pytest.ini`: `unit`, `integration`, `cli`, `regress`, `slow`, `network`

### Code Quality

```bash
# Type checking with mypy
make check                  # or mypy src/

# Linting with flake8
make lint                   # or flake8 src/ tests/

# Code formatting with black
make format                 # Format code
make format-check           # Check formatting without changes

# All checks together
make check-all              # type + lint + format + security

# Security scan with bandit
make security               # or bandit -r src/ -ll
```

### Building and Releasing

```bash
# Clean build artifacts
make clean

# Build the package
make build

# Full CI pipeline locally
make ci

# Quick local checks (no full install/build)
make ci-local
```

## Data Flow and Key Classes

### Course Discovery Flow

1. **User/Client** → calls `DefaultCourseService` methods
2. **Service Layer** → delegates to appropriate `UniversityProvider` (CarletonProvider, UOttawaProvider)
3. **Provider** → scrapes/loads data, returns raw data
4. **Service** → normalizes to Pydantic models (Course, Subject, SearchResult, etc.)
5. **API** → serializes to JSON via FastAPI

### Key Services

- **DefaultCourseService**: Manages course catalogs, subjects, searching across all universities
- **DefaultTimetableService**: Handles live timetable data (currently Carleton and UOttawa Banner systems)
- **DefaultRatingService**: Integrates Rate My Professor data
- **DefaultDiscoveryService**: Batch discovery of courses across subjects

### University Providers

Both implement `BaseUniversityProvider`:
- **CarletonProvider** (`src/uoapi/universities/carleton/provider.py`): Scrapes Carleton's Banner system
- **UOttawaProvider** (`src/uoapi/universities/uottawa/provider.py`): Scrapes UOttawa's Banner system

Providers load courses from JSON assets: `assets/carleton/courses.json`, `assets/uottawa/courses.json`

## REST API Structure

API routes are defined in `src/uoapi/server/app.py`. Main endpoint patterns:

- `/universities` - List supported universities
- `/universities/{university}/subjects` - Course subjects
- `/universities/{university}/courses/catalog` - Static course catalog
- `/universities/{university}/courses/live` - Live timetable data
- `/universities/{university}/courses/{course_code}/live` - Single course with sections
- `/universities/{university}/professors/{first}/{last}` - Rate My Professor ratings
- `/universities/{university}/programs` - Academic programs (with search/filter/export)

## Testing Strategy

- **Unit Tests**: Individual components (models, parsers, utilities) in isolation
- **Integration Tests**: Component interactions and end-to-end data flow
- **Regression Tests**: Known good outputs (historical data validation)
- **Mock Data**: HTTP responses stored in `tests/*/data/` directories

Minimum coverage: 70% (enforced by `pytest.ini: cov-fail-under`)

## Configuration

Configuration is managed in `src/uoapi/utils/config.py`. Key config sections:
- **cache**: TTL settings for different universities
- **scraping**: Timeout and concurrent worker settings
- **api**: Server host/port/debug settings

Configuration can be accessed via `get_config()` from utils.

## Important Implementation Notes

### University-Specific Considerations

- **Carleton**: Uses 4-letter subject codes (COMP, MATH), Banner system
- **University of Ottawa**: Uses 3-letter subject codes (CSI, MAT), Banner system
- **Term codes**: Format varies (202501 = January 2025 for both, but API accepts "fall", "winter", "spring", "summer" + year)

### Data Sources

- **Course Catalog**: Loaded from pre-scraped JSON assets (not live scraped)
- **Live Timetable**: Scraped from Banner systems on demand
- **Programs**: Loaded from JSON in universities/*/programs.py
- **Ratings**: Fetched from Rate My Professor API on demand

### Error Handling

Custom exception hierarchy in `core/exceptions.py`:
- `UOAPIError` (base)
  - `ProviderError`, `DataSourceError`, `NetworkError`
  - `ParsingError`, `ValidationError`
  - `UniversityNotSupportedError`, `CourseNotFoundError`, etc.

Services should raise appropriate exceptions; the API layer handles serialization to JSON error responses.

## Legacy Compatibility

Old imports still work for backwards compatibility:
- `from uoapi.course import scrape_subjects, get_courses`
- `from uoapi.carleton.discovery import CarletonDiscovery`
- `from uoapi.server.app import create_app`

New code should use the clean architecture:
- Import from `uoapi.core` for models
- Import from `uoapi.services` for business logic
- Use service interfaces, not university providers directly

## When Making Changes

### Adding a New Feature

1. Define the domain model in `core/models.py` (Pydantic)
2. Add the interface method to appropriate service interface in `core/interfaces.py`
3. Implement in the service class (`services/*.py`)
4. Add API endpoint in `server/app.py`
5. Add tests in `tests/` with appropriate markers
6. Update README.md if user-facing

### Fixing a Bug

1. Write a regression test first (use `@pytest.mark.regress`)
2. Fix the bug in the implementation
3. Verify test passes

### Adding a University

1. Extend `University` enum in `core/models.py`
2. Create provider class extending `BaseUniversityProvider` in `universities/{uni}/provider.py`
3. Implement required methods: `get_subjects()`, `get_courses()`, etc.
4. Add to services' provider registry
5. Update README documentation

## CI/CD and Quality Gates

Enforced by GitHub Actions (`.github/workflows/ci.yml`):
1. Bandit security scan
2. Black formatting check
3. Flake8 linting
4. mypy type checking
5. pytest with coverage (≥70%)
6. Package build validation

All checks must pass before merge. Branch protection rules are in `.github/BRANCH_PROTECTION.md`.

## Common Gotchas

- **Term Code Validation**: Always validate term codes with `timetable_service.get_available_terms()` first
- **Subject Code Length**: Carleton = 4 chars (COMP), UOttawa = 3 chars (CSI)
- **Live Data Availability**: Not all terms/subjects have live timetable data
- **Rate Limiting**: RMP integration may hit rate limits; implement retry logic if needed
- **Asset Loading**: Course JSON assets must exist at build time; they're baked into the wheel

## Key Files to Know

- `src/uoapi/core/models.py` - All Pydantic data models
- `src/uoapi/services/*.py` - Main business logic
- `src/uoapi/universities/*/provider.py` - University-specific scrapers
- `src/uoapi/server/app.py` - FastAPI app factory and routes
- `src/uoapi/server/cli.py` - CLI entry point
- `pyproject.toml` - Package metadata, dependencies, scripts
- `pytest.ini` - Test configuration, markers, coverage settings
- `Makefile` - Development commands
