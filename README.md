# Schedulo API

A Python CLI tool and library for retrieving public data from Canadian universities, including the University of Ottawa and Carleton University.

**This package now features a completely refactored, clean architecture with improved maintainability and extensibility.**

[![PyPI version](https://badge.fury.io/py/schedulo-api.svg)](https://badge.fury.io/py/schedulo-api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- **🏫 Multi-University Support**: University of Ottawa and Carleton University
- **📚 Complete Course Data**: Catalogs, timetables, prerequisites, components
- **⚡ Live Timetable Data**: Real-time course availability and scheduling
- **⭐ Rate My Professor Integration**: Professor ratings for both universities
- **🚀 FastAPI REST API**: Complete HTTP API with interactive documentation
- **🔧 Clean Architecture**: Layered design with proper separation of concerns
- **🐍 Python Library**: Comprehensive programmatic access
- **📝 Type Safety**: Full type annotations with Pydantic models
- **🔄 Backward Compatibility**: Existing code continues to work

## 🏗️ New Architecture

The package has been completely refactored with a clean layered architecture:

```
uoapi/
├── core/                    # Domain models & interfaces
├── universities/           # University-specific implementations  
├── services/              # Business logic layer
├── interfaces/            # CLI and API interfaces
└── utils/                # Shared utilities
```

### Key Benefits:
- ✅ **Single Responsibility**: Each module has one clear purpose
- ✅ **Consistent Models**: Unified data structures across universities
- ✅ **Easy Extension**: Add new universities by implementing simple interfaces
- ✅ **Better Testing**: Clear boundaries enable comprehensive testing
- ✅ **Type Safety**: Full type annotations throughout

## 🚀 Quick Start

### Installation

```bash
# From PyPI (Recommended)
pip install schedulo-api

# From Source
pip install git+https://github.com/Rain6435/uoapi.git@dev

# Development Installation
git clone https://github.com/Rain6435/uoapi.git
cd uoapi
pip install -e .[tests]
```

### Basic Usage

#### New Service-Based API (Recommended)
```python
from uoapi.core import University
from uoapi.services import DefaultCourseService, DefaultTimetableService

# Initialize services
course_service = DefaultCourseService()
timetable_service = DefaultTimetableService()

# Get all subjects for a university
subjects = course_service.get_subjects(University.CARLETON)
print(f"Found {len(subjects)} subjects")

# Get courses for a specific subject
courses = course_service.get_courses(University.CARLETON, "COMP")
print(f"Found {len(courses)} COMP courses")

# Search courses
search_result = course_service.search_courses(University.UOTTAWA, "programming")
print(f"Found {search_result.total_found} courses matching 'programming'")

# Get live timetable data (Carleton only)
if University.CARLETON in timetable_service.get_supported_universities():
    live_data = timetable_service.get_live_courses(
        University.CARLETON,
        term_code="202501",
        subjects=["COMP"],
        max_courses_per_subject=10
    )
    print(f"Found {live_data.courses_offered} offered courses")
```

#### Command Line Interface
```bash
# List available terms
schedulo terms carleton

# List available subjects
schedulo subjects carleton

# Get courses for subjects
schedulo courses carleton fall2025 COMP MATH

# Get specific course details
schedulo course carleton COMP1005 fall2025

# Start FastAPI server
schedulo server --port 8000
```

#### FastAPI Server
```bash
# Start the server
schedulo server --port 8000

# Interactive docs available at:
# http://localhost:8000/docs
# http://localhost:8000/redoc
```

## 📖 Complete Usage Guide

### University Data Access

#### Course Service
```python
from uoapi.core import University
from uoapi.services import DefaultCourseService

service = DefaultCourseService()

# Get all supported universities
universities = service.get_all_universities()

# Get subjects
subjects = service.get_subjects(University.UOTTAWA)
for subject in subjects[:5]:
    print(f"{subject.code}: {subject.name}")

# Get courses with filtering
courses = service.get_courses(
    University.CARLETON, 
    subject_code="COMP",
    query="database"
)

# Get specific course
course = service.get_course_by_code(University.UOTTAWA, "CSI3140")
print(f"{course.title}: {course.credits} credits")

# Get course statistics
stats = service.get_course_statistics(University.CARLETON)
print(f"Total courses: {stats['total_courses']}")
```

#### Timetable Service
```python
from uoapi.services import DefaultTimetableService

service = DefaultTimetableService()

# Check which universities support live data
supported = service.get_supported_universities()
print(f"Live data supported by: {[u.value for u in supported]}")

# Get available terms
terms = service.get_available_terms(University.CARLETON)
for code, name in terms:
    print(f"{code}: {name}")

# Get live course data
result = service.get_live_courses(
    university=University.CARLETON,
    term_code="202501",
    subjects=["COMP", "MATH"],
    max_courses_per_subject=20
)

print(f"Processing time: {result.processing_time:.2f}s")
print(f"Offering rate: {result.offering_rate:.1f}%")

for course in result.courses:
    if course.is_offered:
        print(f"\n{course.course_code}: {course.title}")
        for section in course.sections:
            print(f"  {section.section}: {section.instructor} - {section.status}")
            for mt in section.meeting_times:
                print(f"    {mt.days} {mt.start_time}-{mt.end_time}")
```

#### Rating Service
```python
from uoapi.services import DefaultRatingService

service = DefaultRatingService()

# Get individual instructor rating
rating = service.get_instructor_rating("John Smith", University.UOTTAWA)
if rating:
    print(f"Rating: {rating['rating']}/5.0")
    print(f"Difficulty: {rating['avg_difficulty']}/5.0")

# Get batch ratings
instructors = [("Jane", "Doe"), ("John", "Smith")]
ratings = service.get_batch_ratings(instructors, University.CARLETON)

# Enhance courses with ratings
enhanced_courses = service.inject_ratings_into_courses(courses, University.UOTTAWA)
```

### CLI Usage

The clean, unified CLI provides simple commands for accessing university data:

#### Basic Commands
```bash
# List available terms
schedulo terms carleton

# List available subjects
schedulo subjects carleton

# Get courses for specific subjects and term
schedulo courses carleton fall2025 COMP MATH --limit 20

# Get catalog courses (no term required, no live sections)
schedulo courses carleton COMP --catalog --limit 10        # Carleton: 4-letter subjects
schedulo courses uottawa CSI --catalog --limit 10          # UOttawa: 3-letter subjects  
schedulo courses carleton --catalog --limit 20             # All catalog courses

# Get detailed information for a specific course
schedulo course carleton COMP1005 fall2025

# Get professor ratings from Rate My Professor
schedulo professor John Smith carleton
schedulo professor Lucia Moura uottawa

# Start the API server
schedulo server --port 8000
```

#### Catalog Courses Access
Access complete course catalogs without needing term information:

```bash
# Get all catalog courses for a subject (university-specific formats)
schedulo courses carleton COMP --catalog --limit 10        # Carleton: 4-letter codes
schedulo courses uottawa CSI --catalog --limit 10          # UOttawa: 3-letter codes

# Get all catalog courses (with limit for performance)
schedulo courses carleton --catalog --limit 50             # First 50 courses
schedulo courses uottawa --catalog --limit 0               # All courses (no limit)

# Example output:
# Getting catalog courses from carleton...
# Found 10 catalog courses
#
# COMP - 10 courses:
#   COMP1001: Introduction to Computational Thinking for Arts and Social Science Students
#   COMP1005: Introduction to Computer Science I
#   COMP1006: Introduction to Computer Science II
#   COMP1405: Introduction to Computer Science I
#     Credits: 3
#   ...
```

**Key Features:**
- **No term required**: Catalog data is term-independent
- **Subject code validation**: Automatically detects valid subject codes based on university
- **Organized output**: Courses grouped by subject with credit information
- **Performance limits**: Built-in limits to handle large catalogs efficiently

#### Enhanced Section Parsing
The CLI now captures **complete section data** including all lectures, tutorials, and labs:

```bash
# Example: COMP 1005 retrieves all 13 sections (4 lectures + 9 tutorials)
schedulo course carleton COMP1005 fall2025

# Output shows:
#   Sections Summary:
#     Total: 13
#     Lectures: 4  
#     Tutorials: 9
#   
#   All Sections:
#     A (Lecture) - CRN 10001 - Open
#     B (Lecture) - CRN 10002 - Open
#     T01 (Tutorial) - CRN 10101 - Open
#     T02 (Tutorial) - CRN 10102 - Wait List
#     ...
```

#### Professor Rating Lookup
Get comprehensive Rate My Professor data for university instructors:

```bash
# Basic professor lookup
schedulo professor Rami Abielmona uottawa

# Output example:
# 📊 Professor Rating: Rami Abielmona
# ==================================================
# Overall Rating: 4.5/5.0 ⭐
# Number of Ratings: 57
# Department: Engineering
# Would Take Again: 85%
# Average Difficulty: 3.3/5.0
# Rate My Professor ID: 232123
# Profile URL: https://www.ratemyprofessors.com/professor/232123
#
# 📝 Rating Interpretation:
# 🟢 Excellent professor (4.0+ rating)

# Works with both universities
schedulo professor Bo Sun uottawa      # University of Ottawa
schedulo professor John Smith carleton # Carleton University

# Handles various name formats and provides helpful error messages
schedulo professor NonExistent Name uottawa
# No ratings found for NonExistent Name at University of Ottawa
# Tips:
# - Try different name variations (nicknames, middle names)  
# - Check spelling of first and last name
# - Some professors may not be on Rate My Professor
```

### REST API Server

The Schedulo API provides a comprehensive FastAPI-based REST server with interactive documentation, structured responses, and powerful filtering capabilities.

#### Start Server
```bash
# Using CLI (Recommended)
schedulo server --port 8000

# Or programmatically
python -c "
from uoapi.server.app import create_app
import uvicorn
app = create_app()
uvicorn.run(app, host='127.0.0.1', port=8000)
"
```

**Interactive Documentation**: http://localhost:8000/docs  
**ReDoc Documentation**: http://localhost:8000/redoc

#### Core Endpoints

##### University Information
```bash
# List all supported universities
curl http://localhost:8000/universities

# Get university-specific information
curl http://localhost:8000/universities/carleton/info
curl http://localhost:8000/universities/uottawa/info
```

##### Subjects
```bash
# Get subjects (preview - first 20)
curl http://localhost:8000/universities/carleton/subjects
curl http://localhost:8000/universities/uottawa/subjects

# Get all subjects (complete catalog)
curl http://localhost:8000/universities/carleton/subjects/catalog
curl http://localhost:8000/universities/uottawa/subjects/catalog
```

##### Course Catalog (Static Data)
```bash
# Get catalog courses by subject
curl "http://localhost:8000/universities/carleton/courses/catalog?subjects=COMP,MATH&limit=10"
curl "http://localhost:8000/universities/uottawa/courses/catalog?subjects=CSI,MAT&limit=5"

# Get all catalog courses (warning: large response)
curl "http://localhost:8000/universities/carleton/courses/catalog"

# Get single course (catalog data only)
curl http://localhost:8000/universities/carleton/courses/COMP1005
curl http://localhost:8000/universities/uottawa/courses/CSI3140
```

##### Live Timetable Data
```bash
# Get available terms for live data
curl http://localhost:8000/universities/carleton/terms
curl http://localhost:8000/universities/uottawa/terms

# Multiple courses with live sections
curl "http://localhost:8000/universities/carleton/courses/live?term=fall&year=2025&subjects=COMP,MATH&limit=20&include_ratings=true"
curl "http://localhost:8000/universities/uottawa/courses/live?term=winter&year=2025&subjects=CSI,CEG&limit=10"

# Filter by specific course codes
curl "http://localhost:8000/universities/carleton/courses/live?term=fall&year=2025&subjects=COMP&course_codes=COMP1005,COMP1405"

# Single course with structured sections
curl "http://localhost:8000/universities/carleton/courses/COMP1005/live?term=fall&year=2025&include_ratings=true"
```

**New Single Course Response Structure**:
```json
{
  "university": "carleton",
  "term_code": "202530",
  "term_name": "Fall 2025",
  "course": {
    "course_code": "COMP1005",
    "subject_code": "COMP",
    "title": "Programming Concepts",
    "credits": 0.5,
    "is_offered": true,
    "sections_found": 13
  },
  "sections": [
    {
      "section": "A",
      "components": [
        {
          "name": "A",
          "crn": "31108",
          "status": "Open",
          "credits": 0.5,
          "schedule_type": "Lecture",
          "instructor": "Ava McKenney",
          "meeting_times": [
            {
              "start_date": "Sep 03, 2025",
              "end_date": "Dec 05, 2025", 
              "days": "Wed Fri",
              "start_time": "13:05",
              "end_time": "14:25"
            }
          ],
          "notes": ["Also Register in: COMP 1005 A1 or A2 or A3"],
          "rmp_rating": {
            "instructor": "Ava McKenney",
            "rating": 4.2,
            "num_ratings": 15
          }
        },
        {
          "name": "A1",
          "crn": "31109",
          "status": "Open",
          "schedule_type": "Tutorial",
          "instructor": "Ava McKenney"
        },
        {
          "name": "A2", 
          "crn": "31110",
          "status": "Full, No Waitlist",
          "schedule_type": "Tutorial"
        }
      ]
    }
  ]
}
```

##### Professor Ratings
```bash
# Get Rate My Professor ratings
curl "http://localhost:8000/universities/carleton/professors/John/Smith"
curl "http://localhost:8000/universities/uottawa/professors/Lucia/Moura"
```

#### API Features

- **🏗️ Structured Responses**: Properly grouped course sections and components
- **⭐ Professor Integration**: Optional Rate My Professor ratings via `?include_ratings=true`
- **🔍 Smart Filtering**: Filter by subjects, course codes, terms
- **📊 University-Specific**: Handles different term formats and subject code lengths
- **📚 Comprehensive Data**: Course catalogs, live timetables, prerequisites
- **🚀 High Performance**: Direct single-course queries bypass bulk discovery
- **📖 Interactive Docs**: Auto-generated OpenAPI documentation
- **🛡️ Type Safety**: Full Pydantic validation and serialization
- **🎯 RESTful Design**: Clean, predictable endpoint structure

## 🔧 Advanced Usage

### Custom University Provider
```python
from uoapi.core import UniversityProvider, University, Subject, Course
from uoapi.universities import BaseUniversityProvider

class MyUniversityProvider(BaseUniversityProvider):
    @property
    def university(self) -> University:
        return University.MYUNI  # Add to enum first
    
    @property  
    def name(self) -> str:
        return "My University"
    
    def get_subjects(self) -> List[Subject]:
        # Implement subject scraping/loading
        return []
    
    def get_courses(self, subject_code: str = None) -> List[Course]:
        # Implement course scraping/loading
        return []

# Register with service
from uoapi.services import DefaultCourseService
service = DefaultCourseService()
service._providers[University.MYUNI] = MyUniversityProvider()
```

### Custom CLI Command
```python
from uoapi.interfaces.cli.framework import UniversityCommand, registry
import argparse

class MyCommand(UniversityCommand):
    @property
    def name(self) -> str:
        return "mycmd"
    
    @property
    def help(self) -> str:
        return "My custom command"
    
    @property
    def description(self) -> str:
        return "Does something useful"
    
    def configure_command_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("--option", help="My option")
        return parser
    
    def execute_for_university(self, args, university):
        # Implement command logic
        return self.format_output({"result": "success"})

# Register command
registry.register(MyCommand())
```

### Configuration
```python
from uoapi.utils import get_config

config = get_config()

# Adjust cache settings
config.cache.ttl_seconds = 7200  # 2 hours
config.cache.uottawa_ttl = 14400  # 4 hours for UOttawa

# Adjust scraping settings
config.scraping.timeout_seconds = 60
config.scraping.concurrent_workers = 8

# API settings
config.api.port = 9000
config.api.debug = True
```

## 📊 Data Models

### Unified Course Model
```python
from uoapi.core import Course

# All universities use the same model
course = Course(
    course_code="COMP1001",
    subject_code="COMP", 
    course_number="1001",
    title="Introduction to Computing",
    description="Basic computing concepts...",
    credits=3,
    university=University.CARLETON,
    components=["Lecture", "Laboratory"],
    prerequisites="None",
    sections=[...],  # Live sections if available
    is_offered=True
)
```

### Search Results
```python
from uoapi.core import SearchResult

result = SearchResult(
    university=University.UOTTAWA,
    query="programming",
    subject_filter="CSI",
    total_found=25,
    courses=[...],
    metadata={"search_method": "text_search"}
)
```

### Live Course Discovery
```python
from uoapi.core import DiscoveryResult

result = DiscoveryResult(
    term_code="202501",
    term_name="Winter 2025",
    university=University.CARLETON,
    subjects_queried=["COMP", "MATH"],
    total_courses=150,
    courses_offered=142,
    offering_rate=94.7,
    processing_time=25.3,
    courses=[...]
)
```

## 🧪 Development

### Setup
```bash
git clone https://github.com/Rain6435/uoapi.git
cd uoapi
pip install -e .[tests]
```

### Testing
```bash
# Run all tests
make test     # or pytest

# Test specific components
pytest tests/core/
pytest tests/services/
pytest tests/universities/

# Test with coverage
pytest --cov=uoapi tests/

# Type checking
make check    # or mypy src/

# Linting  
make lint     # or flake8

# All checks
make          # test + lint + typecheck
```

### Code Quality
The refactored codebase maintains high code quality with:
- **100% type coverage** with mypy
- **Comprehensive tests** for all components
- **Consistent formatting** with black
- **Clean imports** and modular design
- **Documentation** for all public APIs

## 🔄 Migration Guide

### From Old API
```python
# Old way
from uoapi.course.course_info import scrape_subjects, get_courses
subjects = scrape_subjects()
courses = list(get_courses(subjects[0]['link']))

# New way (recommended)
from uoapi.core import University
from uoapi.services import DefaultCourseService

service = DefaultCourseService()
subjects = service.get_subjects(University.UOTTAWA)
courses = service.get_courses(University.UOTTAWA, subjects[0].code)
```

### Legacy Compatibility
```python
# Old imports still work
from uoapi.course import scrape_subjects, get_courses  # ✅ Still works
from uoapi.carleton.discovery import CarletonDiscovery  # ✅ Still works
from uoapi.server.app import create_app  # ✅ Still works

# But new imports are cleaner
from uoapi.core import *  # ✅ New unified models
from uoapi.services import *  # ✅ Business logic
from uoapi.interfaces.api import create_app  # ✅ Clean API
```

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Ensure Python 3.10+ and proper installation
2. **University not supported**: Check `service.get_all_universities()`
3. **Term validation**: Use `timetable_service.get_available_terms()` first
4. **Rate limiting**: Reduce concurrent workers if getting blocked
5. **Live data not available**: Both Carleton and UOttawa support live timetable data

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via CLI
uoapi --verbose course -u carleton -c COMP
```

### Configuration Issues
```python
from uoapi.utils import get_config, reload_config

# Check current config
config = get_config()
print(config.to_dict())

# Reload with different environment
reload_config("development")
```

## 🎯 What's New in v3.2+

### Major Enhancements
- **🔧 Enhanced Section Parsing**: Complete retrieval of all course sections, lectures, tutorials, and labs
- **🎨 Clean CLI Interface**: Simplified commands with intuitive structure (`schedulo` instead of complex nested commands)
- **⚡ Improved Data Accuracy**: Fixed Banner system parsing to capture all available course sections  
- **🚀 Better User Experience**: Streamlined commands and comprehensive section information
- **👨‍🏫 Professor Ratings**: New `schedulo professor` command with Rate My Professor integration
- **📚 Catalog Access**: New `--catalog` option to browse complete course catalogs without term requirements
- **🎯 Smart Subject Validation**: University-specific subject code validation (4-letter for Carleton, 3-letter for UOttawa)

### Architecture Improvements
- **🏗️ Clean Architecture**: Proper layered design with separation of concerns
- **🔧 Service Layer**: Business logic separated from data access
- **🎯 Single Responsibility**: Each module has one clear purpose  
- **🔄 Dependency Inversion**: High-level modules don't depend on low-level details

### Developer Experience
- **✅ Type Safety**: Complete type annotations with Pydantic
- **🧪 Better Testing**: Clear boundaries enable comprehensive testing
- **📚 Better Documentation**: Comprehensive examples and API docs
- **🔧 Easy Extension**: Add new universities via simple interfaces

### User Experience  
- **🎨 Consistent APIs**: Same patterns across all universities
- **⚡ Better Performance**: Improved caching and parallel processing
- **🔍 Better Error Messages**: Structured exceptions with helpful details
- **📊 Richer Data**: Enhanced models with metadata and validation

## 🤝 Contributing

We welcome contributions! The new architecture makes it much easier to contribute:

1. **Add Universities**: Implement `UniversityProvider` interface
2. **Add Features**: Extend service classes with new functionality  
3. **Add Interfaces**: Create new CLI commands or API endpoints
4. **Fix Bugs**: Clear modular structure makes debugging easier

### Contribution Process
```bash
# 1. Fork and clone
git clone https://github.com/your-username/uoapi.git

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes and test
make test
make lint

# 4. Submit PR
git push origin feature/my-feature
```

## 📜 License

GNU LGPLv3.0 - See the `COPYING` and `COPYING.LESSER` files for details.

## 🙏 Acknowledgments

- Original [uoapi](https://github.com/andrewnags/uoapi) by Andrew Nagarajah
- University of Ottawa and Carleton University for public data access
- Rate My Professor for their API
- The Python community for excellent libraries and tools

---

**Ready to explore university course data with enhanced section parsing and clean CLI?** 
```bash
pip install schedulo-api
schedulo terms carleton  # Get started!
```