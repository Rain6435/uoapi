# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Schedulo API is a Python CLI tool for retrieving public data from Canadian universities including the University of Ottawa and Carleton University. It's a setuptools-based package with modular architecture supporting multiple data sources (timetables, courses, dates, rate my prof).

## Development Commands

### Testing
```bash
make test     # or make t - Run pytest with coverage
pytest        # Direct pytest execution
```

### Code Quality
```bash
make check    # or make c - Run mypy type checking
make lint     # or make l - Run flake8 linting
mypy          # Direct type checking
flake8        # Direct linting
```

### Package Installation
```bash
pip install -e .                    # Install in development mode
pip install -e .[tests]             # Install with test dependencies
```

## Architecture

### Module System
- Core modules defined in `src/uoapi/__modules__` file: example, course, timetable, dates, rmp
- Each module auto-loaded via `__init__.py` using importlib
- CLI auto-discovers subcommands from modules using `cli.py` pattern

### CLI Structure
- Main CLI in `src/uoapi/cli.py` with argparse-based subcommand system
- Each module provides its own CLI via `cli.py`, `parser()`, and module-specific functions
- Entry point: `schedulo-api=uoapi.cli:cli` (console_scripts)

### Key Modules
- `course/`: Course and subject parsing with prerequisite handling
- `timetable/`: Query timetable data with JSON templates
- `dates/`: Important academic dates
- `rmp/`: Rate My Professor integration

### Dependencies
- Core: requests, regex, bs4, lxml, pandas, parsedatetime, pydantic<2
- Testing: pytest, mypy, flake8, black, bandit

### Configuration
- Python >=3.10 required
- Flake8 max line length: 100, max complexity: 10
- pytest with coverage reporting enabled
- mypy configured for src/**/*.py
