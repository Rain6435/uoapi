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
pip install git+https://github.com/Rain6435/uoapi.git@dev
```

## Usage

### University of Ottawa
```bash
# Get course timetables
schedulo-api timetable --term winter --year 2020 CSI3104 PHY4 YDD

# Get course information
schedulo-api course --courses MAT PHY
schedulo-api course --nosubjects CSI3105 CSI3131

# Get important academic dates
schedulo-api dates

# Rate My Professor data
schedulo-api rmp --school "University of Ottawa" --instructor "John Doe"
```

### Carleton University (NEW!)
```bash
# Get available terms
schedulo-api carleton --available-terms

# List all subjects
schedulo-api carleton --subjects

# Get courses for specific subjects
schedulo-api carleton --courses COMP MATH

# Search specific courses with real-time availability
schedulo-api carleton --courses COMP1405 MATH1007
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

## Data Structures and Entities

### University of Ottawa Models

#### Subject
Represents academic departments/subjects:
```python
{
    "subject": "Computer Science",           # Full department name
    "subject_code": "CSI",                 # Short identifier
    "link": "https://catalogue.uottawa.ca/en/courses/csi/"
}
```

#### Course
Complete course information:
```python
{
    "course_code": "CSI3140",              # Course identifier
    "title": "World Wide Web Programming", # Course title
    "credits": 3,                          # Academic credits
    "description": "Introduction to...",   # Full description
    "components": ["LECTURE", "LAB"],      # Course delivery methods
    "prerequisites": "CSI2520, CSI2101",  # Raw prerequisite text
    "dependencies": [["CSI2520"], ["CSI2101"]]  # Parsed dependencies
}
```

### Carleton University Models

#### Course Section
Individual course section with scheduling:
```python
{
    "crn": "12345",                        # Course reference number
    "section": "A",                        # Section identifier
    "status": "Open",                      # Enrollment status
    "credits": 0.5,                        # Course credits
    "schedule_type": "Lecture",            # Delivery method
    "instructor": "Dr. Smith",             # Instructor name
    "meeting_times": [                     # Schedule information
        {
            "start_date": "2024-01-08",
            "end_date": "2024-04-05",
            "days": "MWF",
            "start_time": "10:05",
            "end_time": "11:25"
        }
    ],
    "notes": ["Additional requirements"]
}
```

#### Complete Course
Full course with all sections:
```python
{
    "course_code": "COMP1405",             # Full course code
    "subject_code": "COMP",               # Subject prefix
    "course_number": "1405",              # Course number
    "catalog_title": "Introduction to...", # Official title
    "catalog_credits": 0.5,               # Credit value
    "is_offered": true,                   # Availability status
    "sections_found": 3,                  # Number of sections
    "banner_title": "Intro Computer Programming",
    "banner_credits": 0.5,
    "sections": [...],                    # Array of CourseSection objects
    "error": false,
    "error_message": ""
}
```

#### Term Result
Complete term discovery results:
```python
{
    "term_code": "202401",                # Term identifier
    "term_name": "Winter 2024",          # Human-readable term
    "session_id": "abc123",              # Session identifier
    "total_subjects_available": 45,       # Total subjects
    "subjects_tested": 45,               # Subjects processed
    "total_courses_tested": 2847,        # Courses checked
    "courses_offered": 1923,             # Available courses
    "errors": 12,                        # Processing errors
    "processing_time_seconds": 324.5,    # Execution time
    "offering_rate_percent": 67.5,       # Availability rate
    "subject_statistics": {...},         # Per-subject stats
    "courses": [...],                    # Array of Course objects
    "processed_at": "2024-01-15T10:30:00Z"
}
```

### Common Output Format

All commands return structured JSON:
```python
{
    "data": {                            # Main response data
        "subjects": [...],               # or "courses", "dates", etc.
    },
    "messages": [                        # Status/error messages
        "Successfully retrieved 45 subjects"
    ]
}
```

### Prerequisites and Dependencies

#### Raw Prerequisites
Text as scraped from university catalogs:
- University of Ottawa: `"Prerequisite: CSI2520, CSI2101"`
- Carleton: Usually embedded in course descriptions

#### Parsed Dependencies
Structured prerequisite relationships:
```python
{
    "dependencies": [
        ["CSI2520"],                     # Required course
        ["CSI2101", "CSI2110"]          # Alternative courses (OR relationship)
    ]
}
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
