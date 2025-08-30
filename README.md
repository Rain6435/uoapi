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
# Get course information
uoapi course -u carleton -c COMP MATH
uoapi course -u uottawa --search "web programming"

# Get live timetable data
uoapi timetable -u carleton --term 202501 --subjects COMP,MATH
uoapi timetable -u carleton --term 202501 --subjects COMP --ratings

# Start FastAPI server
uoapi server --port 8000 --reload
```

#### FastAPI Server
```bash
# Start the server
uoapi server --host 0.0.0.0 --port 8000

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

#### Course Commands
```bash
# List subjects for a university
uoapi course -u uottawa

# Get courses for specific subjects
uoapi course -u carleton -c COMP MATH PHYS

# Search courses
uoapi course -u uottawa --search "artificial intelligence"

# Get courses without showing subjects table
uoapi course -u carleton -c COMP -s
```

#### Timetable Commands  
```bash
# Show available terms
uoapi timetable -u carleton

# Get live course data
uoapi timetable -u carleton --term 202501 --subjects COMP,MATH

# Include professor ratings
uoapi timetable -u carleton --term 202501 --subjects COMP --ratings

# Filter specific courses
uoapi timetable -u carleton --term 202501 --subjects COMP --courses COMP1001,COMP1002

# Adjust query limits
uoapi timetable -u carleton --term 202501 --subjects COMP --limit 30
```

### REST API Usage

#### Start Server
```python
from uoapi.interfaces.api import create_app
import uvicorn

app = create_app()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# List universities
curl http://localhost:8000/universities

# University info
curl http://localhost:8000/universities/carleton/info

# Get subjects
curl http://localhost:8000/universities/uottawa/subjects

# Search courses
curl "http://localhost:8000/universities/uottawa/courses?subject=CSI&search=web&limit=10"

# Live course data (Carleton only)
curl "http://localhost:8000/universities/carleton/live-courses?term=winter&year=2025&subjects=COMP,MATH&limit=20&include_ratings=true"
```

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
5. **Live data not available**: Only Carleton supports live timetable data currently

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

## 🎯 What's New in v3.0

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

**Ready to explore university course data with a clean, modern API?** 
```bash
pip install schedulo-api
```