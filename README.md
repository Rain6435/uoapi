# Schedulo API

A Python CLI tool for retrieving public data from Canadian universities, including the University of Ottawa and Carleton University.

**This is a fork of [andrewnags/uoapi](https://github.com/andrewnags/uoapi) with added support for Carleton University.**

[![PyPI version](https://badge.fury.io/py/schedulo-api.svg)](https://badge.fury.io/py/schedulo-api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- **University of Ottawa**: Course data, timetables, important dates, Rate My Professor integration
- **NEW: Carleton University**: Complete course catalog, real-time course availability, term information
- Modular CLI with consistent JSON output
- Support for multiple data sources and formats

### Installation

Install from PyPI:
```bash
pip install schedulo-api
```

Or install from source:
```bash
pip install git+https://github.com/Rain6435/uoapi.git@carleton
```

## Usage

### University of Ottawa
```bash
# Get course timetables
uoapi timetable --term winter --year 2020 CSI3104 PHY4 YDD

# Get course information
uoapi course --courses MAT PHY
uoapi course --nosubjects CSI3105 CSI3131

# Get important academic dates
uoapi dates

# Rate My Professor data
uoapi rmp --school "University of Ottawa" --instructor "John Doe"
```

### Carleton University (NEW!)
```bash
# Get available terms
uoapi carleton --available-terms

# List all subjects
uoapi carleton --subjects

# Get courses for specific subjects
uoapi carleton --courses COMP MATH

# Search specific courses with real-time availability
uoapi carleton --courses COMP1405 MATH1007
```

### Output Format
All commands return structured JSON with consistent format:
```json
{
  "data": { ... },
  "messages": [ ... ]
}
```

## Development

### Requirements
- Python 3.10+
- Dependencies: requests, bs4, lxml, pandas, pydantic<2

### Development Setup
```bash
git clone https://github.com/Rain6435/uoapi.git
cd uoapi
pip install -e .[tests]
```

### Testing
```bash
make test    # Run pytest with coverage
make check   # Run type checking with mypy
make lint    # Run code linting with flake8
```

## What's New in This Fork

- **Complete Carleton University integration**
- **Real-time course availability** via Banner ERP system
- **Comprehensive course catalog** from CourseLeaf CMS
- **Term and subject discovery** with full metadata
- **Parallel processing** for efficient data collection
- **Rate limiting and error handling** for robust scraping

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for more.

## Acknowledgments

- Original [uoapi](https://github.com/andrewnags/uoapi) by Andrew Nagarajah
- University of Ottawa and Carleton University for providing public data access

## License

GNU LGPLv3.0

See the `COPYING` and `COPYING.LESSER` files for the exact license.

Generally speaking, LGPL permits use, distribution, and alteration in open source (as long as the licence is propagated),
and permits use and distribution in closed source projects
(this is **not** legal advice, just my best personal summary).
