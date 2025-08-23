# Schedulo API

A Python CLI tool and library for retrieving public data from Canadian universities, including the University of Ottawa and Carleton University.

**This is a fork of [andrewnags/uoapi](https://github.com/andrewnags/uoapi) with added support for Carleton University and Rate My Professor integration.**

[![PyPI version](https://badge.fury.io/py/schedulo-api.svg)](https://badge.fury.io/py/schedulo-api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- **University of Ottawa**: Course data, timetables, Rate My Professor integration
- **Carleton University**: Complete course catalog, real-time course availability, term information
- **Rate My Professor**: Professor ratings integration for both universities
- Modular CLI with consistent JSON output
- Python library for programmatic access
- Support for multiple data sources and formats

## Installation

### From PyPI (Recommended)
```bash
pip install schedulo-api
```

### From Source
```bash
pip install git+https://github.com/Rain6435/uoapi.git@dev
```

### Development Installation
```bash
git clone https://github.com/Rain6435/uoapi.git
cd uoapi
pip install -e .[tests]
```

## Quick Start

### Terminal Usage
```bash
# Get available terms for Carleton
schedulo-api carleton --available-terms

# Get AERO courses for Fall 2025
schedulo-api carleton --term fall --year 2025 --courses AERO

# Get University of Ottawa course information
schedulo-api course --courses CSI --limit 5

# Get Rate My Professor data
schedulo-api rmp --school "University of Ottawa" --instructor "John Smith"
```

### Python Code Usage
```python
from uoapi.carleton.cli import main as carleton_main
from uoapi.course.cli import main as course_main
from uoapi.rmp import get_instructor_rating

# Get Carleton course data
import argparse
args = argparse.Namespace(
    term='fall', year=2025, courses=['AERO'], 
    subjects=False, available_terms=False,
    limit=10, workers=4, cookie_file=None
)
results = list(carleton_main(args))

# Get instructor rating
rating = get_instructor_rating("John Smith", "University of Ottawa")
print(f"Rating: {rating['rating']}/5.0")
```

## Complete Usage Guide

### University of Ottawa

#### Course Information
```bash
# List all subjects
schedulo-api course

# Get courses for specific subjects  
schedulo-api course --courses CSI MAT

# Get specific courses only (no subject list)
schedulo-api course --courses --nosubjects CSI

# Control request timing
schedulo-api course --courses CSI --waittime 1.0
```

#### Timetable Queries
```bash
# Get timetables for specific courses
schedulo-api timetable --year 2024 --term fall CSI3140

# Include Rate My Professor ratings
schedulo-api timetable --year 2024 --term fall --school "University of Ottawa" --include-ratings CSI3140
```

### Carleton University

#### Available Terms
```bash
# Get all available terms for course queries
schedulo-api carleton --available-terms
```
*Output:*
```json
{
  "data": {
    "available_terms": [
      {"term_code": "202520", "term_name": "Summer 2025 (May-August)", "year": 2025, "season": "Summer"},
      {"term_code": "202530", "term_name": "Fall 2025 (September-December)", "year": 2025, "season": "Fall"},
      {"term_code": "202610", "term_name": "Winter 2026 (January-April)", "year": 2026, "season": "Winter"}
    ]
  },
  "messages": [{"type": "info", "message": "Found 3 available terms"}]
}
```

#### Subject Discovery
```bash
# List all subjects for a term
schedulo-api carleton --term fall --year 2025 --subjects
```

#### Course Queries
```bash
# Get courses for specific subjects
schedulo-api carleton --term fall --year 2025 --courses COMP MATH

# Get all courses for a subject (limited to 10 per subject by default)
schedulo-api carleton --term fall --year 2025 --courses AERO

# Increase course limit per subject
schedulo-api carleton --term fall --year 2025 --courses COMP --limit 20

# Use more parallel workers for faster processing
schedulo-api carleton --term fall --year 2025 --courses COMP MATH --workers 8
```

**Important:** Always check available terms first! The system will validate that the requested term is available and show helpful error messages:

```bash
# This will fail with helpful message
schedulo-api carleton --term fall --year 2024 --courses AERO
```
*Output:*
```json
{
  "data": null,
  "messages": [
    {"type": "error", "message": "Term fall 2024 (code: 202430) is not available for query"},
    {"type": "info", "message": "Available terms: Summer 2025 (May-August), Fall 2025 (September-December), Winter 2026 (January-April)"}
  ]
}
```

### Rate My Professor

#### Individual Instructor Lookup
```bash
# Get rating for specific instructor
schedulo-api rmp --school "University of Ottawa" --instructor "John Smith" "Jane Doe"

# Get rating for Carleton instructor  
schedulo-api rmp --school "Carleton University" --instructor "John Smith"

# Alternative school names are supported
schedulo-api rmp --school "uottawa" --instructor "John Smith"
schedulo-api rmp --school "carleton" --instructor "Jane Doe"
```

## Python Library Usage

### Carleton University Integration

```python
from uoapi.carleton.discovery import CarletonDiscovery
from uoapi.carleton.cli import main as carleton_main
import argparse

# Direct discovery system usage
discovery = CarletonDiscovery(max_workers=4)

# Get available terms
terms = discovery.get_available_terms()
for term_code, term_name in terms:
    print(f"{term_code}: {term_name}")

# Get subjects for a term
subjects, session_id = discovery.discover_subjects("202530")  # Fall 2025
print(f"Found {len(subjects)} subjects")

# Get courses for specific subjects
courses = discovery.discover_courses("202530", subjects=["AERO"], max_courses_per_subject=10)
for course in courses:
    if course.is_offered:
        print(f"{course.course_code}: {course.catalog_title}")
        for section in course.sections:
            print(f"  Section {section.section}: {section.instructor} - {section.status}")

# Using CLI interface programmatically
args = argparse.Namespace(
    available_terms=False,
    subjects=False, 
    courses=['AERO'],
    term='fall',
    year=2025,
    limit=10,
    workers=4,
    cookie_file=None
)

# This returns a generator of results
for result in carleton_main(args):
    import json
    print(json.dumps(result, indent=2))
```

### University of Ottawa Integration

```python
from uoapi.course import scrape_subjects, get_courses
from uoapi.course.cli import main as course_main

# Direct course system usage
subjects = scrape_subjects()
print(f"Found {len(subjects)} subjects")

# Get courses for a specific subject
csi_subject = next(s for s in subjects if s['subject_code'] == 'CSI')
courses = list(get_courses(csi_subject['link']))
for course in courses[:5]:  # First 5 courses
    print(f"{course['course_code']}: {course['title']}")

# Using CLI interface programmatically
results = list(course_main(subjects=True, courses=True, subject_list=['CSI'], waittime=0.5))
for result in results:
    if 'courses' in result:
        print(f"Subject: {result['courses']['subject_code']}")
        print(f"Number of courses: {len(result['courses']['courses'])}")
```

### Rate My Professor Integration

```python
from uoapi.rmp import (
    get_instructor_rating, 
    get_professor_ratings, 
    inject_ratings_into_timetable,
    get_school_by_name
)

# Check supported schools
school = get_school_by_name("University of Ottawa")
if school:
    print(f"School ID: {school['id']}, Name: {school['name']}")

# Get single instructor rating
rating = get_instructor_rating("John Smith", "University of Ottawa")
print(f"Instructor: {rating['instructor']}")
print(f"Rating: {rating['rating']}/5.0")
print(f"Number of ratings: {rating['num_ratings']}")
print(f"Department: {rating['department']}")

# Get multiple professor ratings
professors = [("John", "Smith"), ("Jane", "Doe")]
ratings = get_professor_ratings(professors, "University of Ottawa")
for rating in ratings:
    print(f"{rating['first_name']} {rating['last_name']}: {rating['rating']}/5.0")

# Inject ratings into timetable data
timetable_data = {
    "timetables": [
        {
            "course_code": "CSI3140",
            "sections": [
                {
                    "components": [
                        {"instructor": "John Smith"}
                    ]
                }
            ]
        }
    ]
}

enhanced_data = inject_ratings_into_timetable(timetable_data, "University of Ottawa")
# Now enhanced_data includes instructor ratings for each component
```

### Error Handling

```python
from uoapi.carleton.discovery import CarletonDiscovery

try:
    discovery = CarletonDiscovery()
    
    # This might fail if term is invalid or network issues occur
    courses = discovery.discover_courses("invalid_term", subjects=["COMP"])
    
except Exception as e:
    print(f"Discovery failed: {e}")
    
# For individual course errors, check the course.error field
courses = discovery.discover_courses("202530", subjects=["COMP"])
for course in courses:
    if course.error:
        print(f"Error for {course.course_code}: {course.error_message}")
    elif course.is_offered:
        print(f"{course.course_code} is available with {course.sections_found} sections")
```

## Data Structures

### Carleton University Models

#### Course Object
```python
{
    "course_code": "AERO 2001",
    "subject_code": "AERO",
    "course_number": "2001", 
    "catalog_title": "Aerospace Engineering Graphical Design",
    "catalog_credits": 0.5,
    "is_offered": True,
    "sections_found": 1,
    "banner_title": "Aerospace Graphical Design",
    "banner_credits": 0.5,
    "sections": [
        {
            "crn": "30045",
            "section": "A", 
            "status": "Full, No Waitlist",
            "credits": 0.5,
            "schedule_type": "Lecture",
            "instructor": "Pakeeza Hafeez",
            "meeting_times": [
                {
                    "start_date": "Sep 03, 2025",
                    "end_date": "Dec 05, 2025", 
                    "days": "Mon Wed",
                    "start_time": "13:05",
                    "end_time": "14:25"
                }
            ],
            "notes": []
        }
    ],
    "error": False,
    "error_message": ""
}
```

### University of Ottawa Models

#### Course Object
```python
{
    "course_code": "CSI3140",
    "title": "World Wide Web Programming",
    "credits": 3,
    "description": "Introduction to web programming...",
    "components": ["LECTURE", "LAB"],
    "prerequisites": "CSI2520, CSI2101",
    "dependencies": [["CSI2520"], ["CSI2101"]]
}
```

### Rate My Professor Models

#### Instructor Rating Object
```python
{
    "instructor": "John Smith",
    "rating": 4.2,
    "num_ratings": 15,
    "department": "Computer Science",
    "rmp_id": 123456,
    "would_take_again_percent": 85.0,
    "avg_difficulty": 3.1
}
```

## Output Format

All CLI commands return structured JSON with this format:

```python
{
    "data": {
        # Main response data - varies by command
        "courses": [...],        # or "subjects", "available_terms", etc.
        "term_code": "202530",
        "total_courses": 10,
        "courses_offered": 5,
        # ... command-specific fields
    },
    "messages": [
        # Status, info, warning, and error messages
        {"type": "info", "message": "Found 5/10 courses offered (50.0%)"},
        {"type": "warning", "message": "2 courses had errors"}
    ]
}
```

## Development

### Requirements
- Python 3.10+
- Dependencies: requests, bs4, lxml, pandas, pydantic<2, parsedatetime

### Development Commands
```bash
# Run tests
make test     # or make t - Run pytest with coverage
pytest        # Direct pytest execution

# Code quality
make check    # or make c - Run mypy type checking  
make lint     # or make l - Run flake8 linting
make          # Run all checks (test + lint + typecheck)

# Manual checks
mypy src/     # Direct type checking
flake8        # Direct linting
black .       # Code formatting
```

### Testing Individual Modules
```bash
# Test specific module
PYTHONPATH=src python3.10 -m pytest tests/carleton/ -v

# Test CLI functionality
PYTHONPATH=src python3.10 -c "from uoapi.cli import cli; cli(['--help'])"

# Test Carleton integration
PYTHONPATH=src python3.10 -c "from uoapi.cli import cli; cli(['carleton', '--available-terms'])"
```

## Troubleshooting

### Common Issues

1. **"Term not available" error**: Always check available terms first using `schedulo-api carleton --available-terms`

2. **Rate My Professor not working**: Make sure you're using the exact school names: "University of Ottawa", "Carleton University", "uottawa", or "carleton"

3. **Import errors**: Make sure you installed the package correctly and are using Python 3.10+

4. **Network timeouts**: Carleton queries can be slow; try reducing the number of workers or subjects queried at once

### Debug Mode
```bash
# Enable verbose logging
schedulo-api --verbose carleton --available-terms

# For Python usage
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Run linting: `make lint`  
6. Submit a pull request

### Adding New Universities

To add support for a new university:

1. Create a new module in `src/uoapi/new_university/`
2. Add the module name to `src/uoapi/__modules__`
3. Implement CLI interface with `parser()` and `cli()` functions
4. Follow the existing patterns for JSON output format
5. Add comprehensive tests

## What's New in This Fork

- **Complete Carleton University integration** with real-time course data
- **Rate My Professor GraphQL API integration** for both universities  
- **Term validation** - automatically checks if requested terms are available
- **Enhanced error handling** with helpful error messages
- **Comprehensive Python library interface** for programmatic usage
- **Parallel processing** for efficient data collection
- **Improved CLI with consistent JSON output format**

## Acknowledgments

- Original [uoapi](https://github.com/andrewnags/uoapi) by Andrew Nagarajah
- University of Ottawa and Carleton University for providing public data access
- Rate My Professor for their GraphQL API

## License

GNU LGPLv3.0 - See the `COPYING` and `COPYING.LESSER` files for details.

This license permits use, distribution, and modification in open source projects (with license propagation), and permits use and distribution in closed source projects.