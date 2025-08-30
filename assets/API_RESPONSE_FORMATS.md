# Schedulo API Response Formats

This document describes the data structures and response formats for all commands available in the Schedulo API.

## Overview

All API responses follow a consistent structure with JSON output. Most responses include:
- **Data payload**: The main response content
- **Messages**: Status, error, or informational messages
- **Metadata**: Additional context like timestamps, counts, etc.

**Important**: All commands now require a `--university` parameter to specify which university to query:
- `--university uottawa` or `--university "University of Ottawa"` for University of Ottawa
- `--university carleton` or `--university "Carleton University"` for Carleton University

Each module validates that it supports the specified university.

---

## Course Module (`schedulo-api course`)

### Commands

#### List Subjects Only
```bash
schedulo-api --university uottawa course
```

**Response Format:**
```json
{
  "subjects": [
    {
      "subject": "Computer Science",
      "subject_code": "CSI", 
      "link": "https://catalogue.uottawa.ca/en/courses/csi/"
    }
  ]
}
```

#### List Courses for Subjects
```bash
schedulo-api --university uottawa course -c [CSI MAT]
```

**Response Format:**
```json
{
  "courses": {
    "subject_code": "CSI",
    "courses": [
      {
        "course_code": "CSI3140",
        "title": "WWW Structures, Techniques and Standards",
        "credits": 3,
        "description": "Course description text...",
        "components": ["Lecture", "Laboratory"],
        "prerequisites": "Prerequisite text...",
        "dependencies": [["CSI2110"], ["CSI2101"]]
      }
    ]
  }
}
```

### Data Models

#### Subject
- `subject` (string): Full department name
- `subject_code` (string): 3-4 letter department code
- `link` (URL): Link to course catalog

#### Course  
- `course_code` (string): Course identifier (e.g., "CSI3140")
- `title` (string): Human-readable course title
- `credits` (integer): Number of academic credits
- `description` (string): Detailed course description
- `components` (array): Course components (Lecture, Lab, etc.)
- `prerequisites` (string): Prerequisites text
- `dependencies` (array): Parsed prerequisite dependencies as nested arrays

---

## Timetable Module (`schedulo-api timetable`)

### Commands

#### Available Terms
```bash
schedulo-api --university uottawa timetable -a
```

**Response Format:**
```json
{
  "available": [
    {
      "term": "winter",
      "year": 2024,
      "term_code": "1244"
    }
  ],
  "messages": []
}
```

#### Query Course Timetable
```bash
schedulo-api --university uottawa timetable -y 2024 -t winter CSI3140
```

**Response Format:**
```json
{
  "timetables": [
    {
      "subject_code": "CSI",
      "course_code": "3140", 
      "course_name": "WWW Structures, Techniques and Standards",
      "sections": [
        {
          "year": 2024,
          "term": "winter",
          "label": "A",
          "components": [
            {
              "instructor": "Andrew James Henry Forward",
              "day": "TU",
              "start_time": "10:00",
              "end_time": "11:20",
              "start_date": "2024-01-08",
              "end_date": "2024-04-05",
              "label": "A00-LEC",
              "section_id": "A",
              "type": "LEC",
              "session_type": "FULLSESS",
              "status": "OPEN",
              "description": "",
              "room": "FSS 4004"
            }
          ]
        }
      ],
      "messages": []
    }
  ],
  "messages": []
}
```

#### With Rate My Professor Integration
```bash
schedulo-api --university uottawa timetable -y 2024 -t winter --include-ratings CSI3140
```

**Enhanced Response (adds rating fields to components):**
```json
{
  "timetables": [
    {
      "subject_code": "CSI",
      "course_code": "3140",
      "course_name": "WWW Structures, Techniques and Standards", 
      "sections": [
        {
          "year": 2024,
          "term": "winter",
          "label": "A",
          "components": [
            {
              "instructor": "Andrew James Henry Forward",
              "day": "TU",
              "start_time": "10:00",
              "end_time": "11:20",
              "start_date": "2024-01-08",
              "end_date": "2024-04-05",
              "label": "A00-LEC",
              "section_id": "A", 
              "type": "LEC",
              "session_type": "FULLSESS",
              "status": "OPEN",
              "description": "",
              "room": "FSS 4004",
              "rmp_rating": {
                "instructor": "Andrew James Henry Forward",
                "rating": 4.2,
                "num_ratings": 15,
                "department": "Computer Science",
                "rmp_id": 12345,
                "would_take_again_percent": 78.5,
                "avg_difficulty": 3.1
              }
            }
          ]
        }
      ],
      "messages": []
    }
  ],
  "messages": [
    {
      "type": "info",
      "message": "Ratings successfully added for 1 instructors"
    }
  ]
}
```

### Data Models

#### Timetable Course
- `subject_code` (string): Department code
- `course_code` (string): Course number
- `course_name` (string): Course title
- `sections` (array): List of course sections
- `messages` (array): Processing messages

#### Section
- `year` (integer): Academic year
- `term` (string): Term name (winter/summer/fall)  
- `label` (string): Section identifier
- `components` (array): Section components/meetings

#### Component
- `instructor` (string): Instructor name
- `day` (string): Day of week code (MO, TU, WE, TH, FR)
- `start_time` (string): Start time (HH:MM format)
- `end_time` (string): End time (HH:MM format)
- `start_date` (string): Start date (YYYY-MM-DD)
- `end_date` (string): End date (YYYY-MM-DD)
- `label` (string): Component label (A00-LEC)
- `section_id` (string): Section identifier
- `type` (string): Component type (LEC, LAB, TUT, etc.)
- `session_type` (string): Session type (FULLSESS, HALFSESS)
- `status` (string): Enrollment status (OPEN, CLOSED, WAITLIST)
- `description` (string): Additional description
- `room` (string): Room location
- `rmp_rating` (object, optional): Rate My Professor data

---

## RMP Module (`schedulo-api rmp`)

### Commands

#### Query Professor Ratings by School
```bash
schedulo-api --university uottawa rmp -p "John Smith" "Jane Doe"
```

**Response Format:**
```json
{
  "ratings": [
    {
      "rmp_id": 12345,
      "first_name": "John", 
      "last_name": "Smith",
      "rating": 4.2,
      "num_ratings": 15,
      "department": "Computer Science",
      "would_take_again_percent": 78.5,
      "avg_difficulty": 3.1
    },
    {
      "rmp_id": null,
      "first_name": "Jane",
      "last_name": "Doe", 
      "rating": null,
      "num_ratings": 0,
      "department": null,
      "would_take_again_percent": null,
      "avg_difficulty": null
    }
  ],
  "school_id": "U2Nob29sLTE0NTI=",
  "school_name": "University of Ottawa",
  "total_professors": 2,
  "found_professors": 1
}
```

#### Query All Professors for a School
```bash
schedulo-api --university carleton rmp
```

**Response Format:**
```json
{
  "ratings": [],
  "school_id": "U2Nob29sLTE0MjA=", 
  "school_name": "Carleton University",
  "total_professors": 0,
  "found_professors": 0,
  "message": "No specific professors requested - provide -p/--professors to query specific instructors"
}
```

### Data Models

#### Rating Response
- `ratings` (array): List of professor ratings
- `school_id` (string): GraphQL school identifier
- `school_name` (string): Full school name
- `total_professors` (integer): Number of professors queried
- `found_professors` (integer): Number found on RMP

#### Professor Rating
- `rmp_id` (integer|null): Rate My Professor ID
- `first_name` (string): First name
- `last_name` (string): Last name
- `rating` (float|null): Overall rating (1.0-5.0)
- `num_ratings` (integer): Number of student ratings
- `department` (string|null): Department name
- `would_take_again_percent` (float|null): Would take again percentage
- `avg_difficulty` (float|null): Average difficulty (1.0-5.0)
- `error` (string, optional): Error message if lookup failed

---

## Carleton Module (`schedulo-api carleton`)

### Commands

#### Available Terms
```bash
schedulo-api --university carleton carleton --available-terms
```

**Response Format:**
```json
{
  "data": {
    "available_terms": [
      {
        "term_code": "202530",
        "term_name": "Fall 2025 (September-December)",
        "year": 2025,
        "season": "Fall"
      }
    ]
  },
  "messages": [
    {
      "type": "info",
      "message": "Found 3 available terms"
    }
  ]
}
```

#### List Subjects for Term
```bash
schedulo-api --university carleton carleton --term fall --year 2025 --subjects
```

**Response Format:**
```json
{
  "data": {
    "term_code": "202530",
    "term_name": "Fall 2025 (September-December)",
    "session_id": "abc123",
    "subjects": ["COMP", "MATH", "PHYS", "CHEM"],
    "total_subjects": 4
  },
  "messages": [
    {
      "type": "info", 
      "message": "Found 4 subjects for Fall 2025 (September-December)"
    }
  ]
}
```

#### Query Courses
```bash
schedulo-api --university carleton carleton --term fall --year 2025 --courses COMP MATH --limit 5
```

**Response Format:**
```json
{
  "data": {
    "term_code": "202530",
    "term_name": "Fall 2025 (September-December)",
    "subjects_queried": ["COMP", "MATH"],
    "total_courses": 25,
    "courses_offered": 18,
    "courses_with_errors": 2,
    "offering_rate_percent": 72.0,
    "subject_statistics": {
      "COMP": {
        "total": 15,
        "offered": 12,
        "errors": 1
      },
      "MATH": {
        "total": 10,
        "offered": 6, 
        "errors": 1
      }
    },
    "courses": [
      {
        "course_code": "COMP1405",
        "subject_code": "COMP",
        "course_number": "1405", 
        "catalog_title": "Introduction to Object-Oriented Programming",
        "catalog_credits": 0.5,
        "is_offered": true,
        "sections_found": 3,
        "banner_title": "Introduction to Object-Oriented Programming",
        "banner_credits": 0.5,
        "sections": [
          {
            "crn": "12345",
            "section": "A",
            "status": "Open",
            "credits": 0.5,
            "schedule_type": "Lecture",
            "instructor": "John Smith",
            "meeting_times": [
              {
                "start_date": "2025-09-08",
                "end_date": "2025-12-05",
                "days": "MoWe",
                "start_time": "10:05",
                "end_time": "11:25"
              }
            ],
            "notes": []
          }
        ],
        "error": false,
        "error_message": ""
      }
    ]
  },
  "messages": [
    {
      "type": "info",
      "message": "Querying subjects: COMP, MATH"
    },
    {
      "type": "info", 
      "message": "Found 18/25 courses offered (72.0%)"
    },
    {
      "type": "warning",
      "message": "2 courses had errors"
    }
  ]
}
```

### Data Models

#### Standard Carleton Response
- `data` (object): Main response data
- `messages` (array): Status and error messages

#### Available Terms
- `term_code` (string): Carleton term code (YYYYST)
- `term_name` (string): Human-readable term name
- `year` (integer): Academic year
- `season` (string): Season name

#### Course Discovery
- `term_code` (string): Term identifier
- `term_name` (string): Human-readable term
- `subjects_queried` (array): Subjects included in query
- `total_courses` (integer): Total courses found
- `courses_offered` (integer): Courses with available sections
- `courses_with_errors` (integer): Courses that failed to parse
- `offering_rate_percent` (float): Percentage of courses offered
- `subject_statistics` (object): Per-subject statistics
- `courses` (array): Detailed course information

#### Course
- `course_code` (string): Full course code (e.g., "COMP1405")
- `subject_code` (string): Subject prefix
- `course_number` (string): Course number
- `catalog_title` (string): Official course title
- `catalog_credits` (float): Credit value
- `is_offered` (boolean): Whether course has sections
- `sections_found` (integer): Number of sections discovered
- `banner_title` (string): Banner system title
- `banner_credits` (float): Banner system credits
- `sections` (array): Course sections
- `error` (boolean): Whether parsing failed
- `error_message` (string): Error details if applicable

#### Section
- `crn` (string): Course Reference Number
- `section` (string): Section identifier  
- `status` (string): Enrollment status
- `credits` (float): Section credit value
- `schedule_type` (string): Type (Lecture, Lab, etc.)
- `instructor` (string): Instructor name
- `meeting_times` (array): Meeting schedule
- `notes` (array): Additional notes

#### Meeting Time
- `start_date` (string): Start date (YYYY-MM-DD)
- `end_date` (string): End date (YYYY-MM-DD)
- `days` (string): Days of week (MoWe, TuTh, etc.)
- `start_time` (string): Start time (HH:MM)
- `end_time` (string): End time (HH:MM)

---

## Discovery Module (`schedulo-api discovery`)

The discovery module provides fast access to pre-scraped course data from locally stored JSON files, eliminating the need for web scraping during queries.

### Commands

#### University Information
```bash
schedulo-api --university uottawa discovery --info
```

**Response Format:**
```json
{
  "action": "info",
  "data": {
    "university": "uottawa",
    "total_courses": 10683,
    "total_subjects": 168,
    "subjects": ["ACP", "ADM", "AFR", "AHL", "..."],
    "data_metadata": {
      "saved_at": "2025-07-14T14:03:39.891024Z",
      "batch_id": "173d82a6-9b78-467c-8b32-af55c4c0ecd6",
      "completed_batches": 28,
      "total_departments": 168,
      "total_courses": 10683,
      "status": "complete"
    },
    "discovery_metadata": {
      "university": "uottawa",
      "file_path": "/path/to/assets/uottawa/courses.json",
      "file_size_bytes": 9444148
    }
  },
  "messages": [
    {
      "type": "info",
      "message": "Found 10683 courses across 168 subjects"
    }
  ]
}
```

#### List All Subjects
```bash
schedulo-api --university carleton discovery --subjects
```

**Response Format:**
```json
{
  "action": "subjects",
  "data": {
    "university": "carleton",
    "subjects": ["AERO", "AFRI", "ANTH", "ARAB", "..."],
    "total_subjects": 100
  },
  "messages": [
    {
      "type": "info",
      "message": "Found 100 subjects"
    }
  ]
}
```

#### List Courses (All or Filtered by Subject)
```bash
schedulo-api --university uottawa discovery --courses --subject CSI --limit 3
```

**Response Format:**
```json
{
  "action": "courses",
  "data": {
    "university": "uottawa",
    "subject_filter": "CSI",
    "total_courses": 174,
    "courses_shown": 3,
    "courses": [
      {
        "subject": "CSI",
        "code": "CSI 4507",
        "title": "Recherche d'information et l'Internet",
        "credits": "3 crédits",
        "description": "Principes de base de la recherche d'information..."
      },
      {
        "subject": "CSI",
        "code": "CSI 4508", 
        "title": "Cryptographie",
        "credits": "3 crédits",
        "description": "La notion de communication sûre..."
      },
      {
        "subject": "CSI",
        "code": "CSI 4509",
        "title": "Introduction au calcul réparti", 
        "credits": "3 crédits",
        "description": "Modèles de calcul. Complexité de communication..."
      }
    ]
  },
  "messages": [
    {
      "type": "info",
      "message": "Found 174 courses for subject CSI"
    },
    {
      "type": "info", 
      "message": "Showing first 3 results (use --limit 0 for all)"
    }
  ]
}
```

#### Search Courses
```bash
schedulo-api --university carleton discovery --search "computer" --limit 2
```

**Response Format:**
```json
{
  "action": "search",
  "data": {
    "university": "carleton",
    "query": "computer",
    "total_matches": 42,
    "courses_shown": 2,
    "courses": [
      {
        "subject": "CIVE",
        "code": "CIVE 4500",
        "title": "Computer Methods in Civil Engineering",
        "credits": 0.5,
        "description": "Advanced software development for Civil Engineering applications..."
      },
      {
        "subject": "COMP",
        "code": "COMP 1005", 
        "title": "Introduction to Computer Science I",
        "credits": 0.5,
        "description": "Introduction to computer science and programming..."
      }
    ]
  },
  "messages": [
    {
      "type": "info",
      "message": "Found 42 courses matching 'computer'"
    },
    {
      "type": "info",
      "message": "Showing first 2 results (use --limit 0 for all)"
    }
  ]
}
```

#### Raw Data Access
```bash
schedulo-api --university carleton discovery --raw
```

**Response Format:**
Returns the complete JSON structure from the courses.json file, which varies by university:

**Carleton Format:**
```json
{
  "metadata": {
    "university": "Carleton University",
    "source_url": "https://calendar.carleton.ca/undergrad/courses/",
    "total_subjects": 100,
    "total_courses": 3580,
    "scraped_at": "2025-07-26 15:40:44"
  },
  "subjects": {
    "AERO": [
      {
        "code": "AERO 2001",
        "title": "Aerospace Engineering Graphical Design",
        "credits": 0.5,
        "description": "Engineering drawing techniques...",
        "experiential_learning": true,
        "prerequisites": [],
        "corequisites": [],
        "preclusions": [],
        "cross_listed": []
      }
    ]
  },
  "discovery_metadata": {
    "university": "carleton",
    "file_path": "/path/to/assets/carleton/courses.json",
    "file_size_bytes": 2847291
  }
}
```

**University of Ottawa Format:**
```json
{
  "metadata": {
    "saved_at": "2025-07-14T14:03:39.891024Z",
    "batch_id": "173d82a6-9b78-467c-8b32-af55c4c0ecd6", 
    "completed_batches": 28,
    "total_departments": 168,
    "total_courses": 10683,
    "status": "complete"
  },
  "departments": {
    "Computer Science (CSI)": {
      "department_code": "CSI",
      "title": "Computer Science (CSI)",
      "courses": [
        {
          "subject_code": "CSI",
          "course_code": "4507",
          "title": "Recherche d'information et l'Internet",
          "credits": "3 crédits",
          "description": "Principes de base de la recherche d'information..."
        }
      ]
    }
  },
  "discovery_metadata": {
    "university": "uottawa",
    "file_path": "/path/to/assets/uottawa/courses.json", 
    "file_size_bytes": 9444148
  }
}
```

### Data Models

#### Discovery Info Response
- `action` (string): Action performed ("info")
- `data` (object): University information
  - `university` (string): University identifier
  - `total_courses` (integer): Total number of courses
  - `total_subjects` (integer): Total number of subjects
  - `subjects` (array): List of subject codes
  - `data_metadata` (object): Original scraping metadata
  - `discovery_metadata` (object): File access metadata
- `messages` (array): Status messages

#### Discovery Subjects Response
- `action` (string): Action performed ("subjects")
- `data` (object): Subjects information
  - `university` (string): University identifier
  - `subjects` (array): Sorted list of subject codes
  - `total_subjects` (integer): Number of subjects
- `messages` (array): Status messages

#### Discovery Courses Response
- `action` (string): Action performed ("courses")
- `data` (object): Courses information
  - `university` (string): University identifier
  - `subject_filter` (string|null): Applied subject filter
  - `total_courses` (integer): Total matching courses
  - `courses_shown` (integer): Number of courses in response
  - `courses` (array): Course objects
- `messages` (array): Status and limit messages

#### Discovery Search Response
- `action` (string): Action performed ("search")
- `data` (object): Search results
  - `university` (string): University identifier
  - `query` (string): Search query used
  - `total_matches` (integer): Total matching courses
  - `courses_shown` (integer): Number of courses in response
  - `courses` (array): Matching course objects
- `messages` (array): Status and limit messages

#### Course Object
- `subject` (string): Subject code (e.g., "CSI", "COMP")
- `code` (string): Full course code (e.g., "CSI 4507", "COMP 1005")
- `title` (string): Course title
- `credits` (string|number): Credit value (format varies by university)
- `description` (string): Course description

#### Discovery Metadata
- `university` (string): Normalized university name
- `file_path` (string): Path to source JSON file
- `file_size_bytes` (integer): File size in bytes

### Command Options

#### Common Parameters
- `--limit LIMIT` (integer): Limit number of results (default: 50, 0 for all)
- `--subject CODE` (string): Filter by subject code (use with --courses)

#### Actions (mutually exclusive)
- `--info`: Show university statistics and metadata
- `--subjects`: List all available subject codes  
- `--courses`: List courses (optionally filtered by subject)
- `--search QUERY`: Search courses by title or description
- `--raw`: Output complete raw JSON data

### Performance Benefits

The discovery module provides several advantages:
- **No Network Requests**: All data served from local files
- **Fast Response Times**: No web scraping delays
- **Comprehensive Data**: Complete course catalogs pre-loaded
- **Offline Capability**: Works without internet connection
- **Consistent Availability**: No dependency on university website uptime

### Data Sources

- **University of Ottawa**: 10,683 courses across 168 subjects
- **Carleton University**: 3,580 courses across 100 subjects

Both datasets include course codes, titles, credits, descriptions, and additional metadata specific to each university's catalog structure.

---

## FastAPI Server Module

The FastAPI server provides HTTP REST API endpoints for accessing course data. All endpoints return JSON responses and support OpenAPI documentation.

### Server Startup

```bash
# Start server on default port 8000
schedulo-api --university carleton server

# Custom configuration
schedulo-api --university carleton server --host 0.0.0.0 --port 8080 --reload
```

### Base URL

When server is running on localhost:8000, all endpoints are available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Endpoints

#### Health Check
```bash
GET /health
```

**Response Format:**
```json
{
  "status": "healthy",
  "available_universities": ["uottawa", "carleton"],
  "version": "2.4.4"
}
```

#### List Universities
```bash
GET /universities
```

**Response Format:**
```json
{
  "universities": ["uottawa", "carleton"],
  "count": 2
}
```

#### University Information
```bash
GET /universities/{university}/info
```

**Response Format:**
```json
{
  "university": "carleton",
  "total_courses": 3580,
  "total_subjects": 100,
  "subjects": ["AERO", "AFRI", "ANTH", "..."],
  "data_metadata": {
    "university": "Carleton University",
    "total_subjects": 100,
    "total_courses": 3580,
    "scraped_at": "2025-07-26 15:40:44"
  },
  "discovery_metadata": {
    "university": "carleton",
    "file_path": "/path/to/assets/carleton/courses.json",
    "file_size_bytes": 2847291
  }
}
```

#### University Subjects
```bash
GET /universities/{university}/subjects
```

**Response Format:**
```json
{
  "university": "carleton",
  "subjects": ["AERO", "AFRI", "ANTH", "ARAB", "..."],
  "total_subjects": 100
}
```

#### Static Course Data (Catalog)
```bash
GET /universities/{university}/courses?subject=COMP&search=1001&limit=10
```

**Response Format:**
```json
{
  "university": "carleton",
  "subject_filter": "COMP",
  "query": "1001",
  "total_courses": 1,
  "courses_shown": 1,
  "courses": [
    {
      "subject": "COMP",
      "code": "COMP 1001",
      "title": "Introduction to Computational Thinking for Arts and Social Science Students",
      "credits": "0.5",
      "description": "An introduction to computational thinking and its applications..."
    }
  ]
}
```

#### Live Course Data with Sections
```bash
GET /universities/{university}/live-courses?term=fall&year=2025&subjects=COMP&limit=5&include_ratings=false
```

**Parameters:**
- `term` (required): Term name (fall, winter, summer)
- `year` (required): Academic year (e.g., 2025)
- `subjects` (required): Comma-separated list of subject codes (e.g., COMP,MATH)
- `course_codes` (optional): Comma-separated list of specific course codes to filter for (e.g., COMP1001,COMP1005)
- `limit` (optional): Maximum courses per subject (default: 10, max: 50)
- `include_ratings` (optional): Include Rate My Professor ratings (default: false)

**Response Format:**
```json
{
  "university": "carleton",
  "term_code": "202530",
  "term_name": "Fall 2025 (September-December)",
  "subjects_queried": ["COMP"],
  "total_courses": 5,
  "courses_offered": 5,
  "courses_with_errors": 0,
  "offering_rate_percent": 100.0,
  "courses": [
    {
      "course_code": "COMP 1001",
      "subject_code": "COMP",
      "course_number": "1001",
      "catalog_title": "Introduction to Computational Thinking for Arts and Social Science Students",
      "catalog_credits": 0.5,
      "is_offered": true,
      "sections_found": 1,
      "banner_title": "Computing for Arts Students",
      "banner_credits": 0.5,
      "sections": [
        {
          "crn": "31107",
          "section": "A",
          "status": "Open",
          "credits": 0.5,
          "schedule_type": "Lecture",
          "instructor": "Andrew Runka",
          "meeting_times": [],
          "notes": [],
          "rmp_rating": null
        }
      ],
      "error": false,
      "error_message": ""
    }
  ]
}
```

#### Live Course Data with Rate My Professor Integration
```bash
GET /universities/{university}/live-courses?term=fall&year=2025&subjects=COMP&limit=3&include_ratings=true
```

**Enhanced Response (adds rmp_rating to sections):**
```json
{
  "university": "carleton",
  "term_code": "202530",
  "term_name": "Fall 2025 (September-December)",
  "subjects_queried": ["COMP"],
  "total_courses": 3,
  "courses_offered": 3,
  "courses_with_errors": 0,
  "offering_rate_percent": 100.0,
  "courses": [
    {
      "course_code": "COMP 1001",
      "subject_code": "COMP",
      "course_number": "1001",
      "catalog_title": "Introduction to Computational Thinking for Arts and Social Science Students",
      "catalog_credits": 0.5,
      "is_offered": true,
      "sections_found": 1,
      "banner_title": "Computing for Arts Students",
      "banner_credits": 0.5,
      "sections": [
        {
          "crn": "31107",
          "section": "A",
          "status": "Open",
          "credits": 0.5,
          "schedule_type": "Lecture",
          "instructor": "Andrew Runka",
          "meeting_times": [],
          "notes": [],
          "rmp_rating": {
            "instructor": "Andrew Runka",
            "rating": 3.5,
            "num_ratings": 52,
            "department": "Computer Science",
            "rmp_id": 1902143,
            "would_take_again_percent": 63.8298,
            "avg_difficulty": 3.4
          }
        }
      ],
      "error": false,
      "error_message": ""
    }
  ]
}
```

#### Live Course Data with Specific Course Filtering
```bash
GET /universities/{university}/live-courses?term=fall&year=2025&subjects=COMP&course_codes=COMP1001&include_ratings=true
```

**Parameters:**
- `course_codes` (optional): Comma-separated list of specific course codes to filter for
  - Examples: `COMP1001`, `COMP1001,COMP1005`, `COMP 1001` (spaces are normalized)
  - Case insensitive and flexible formatting
  - When omitted, returns all courses in the specified subjects

**Single Course Response:**
```json
{
  "university": "carleton",
  "term_code": "202530", 
  "term_name": "Fall 2025 (September-December)",
  "subjects_queried": ["COMP"],
  "total_courses": 1,
  "courses_offered": 1,
  "courses_with_errors": 0,
  "offering_rate_percent": 100.0,
  "courses": [
    {
      "course_code": "COMP 1001",
      "subject_code": "COMP",
      "course_number": "1001",
      "catalog_title": "Introduction to Computational Thinking for Arts and Social Science Students",
      "catalog_credits": 0.5,
      "is_offered": true,
      "sections_found": 1,
      "banner_title": "Computing for Arts Students",
      "banner_credits": 0.5,
      "sections": [
        {
          "crn": "31107",
          "section": "A",
          "status": "Open",
          "credits": 0.5,
          "schedule_type": "Lecture",
          "instructor": "Andrew Runka",
          "meeting_times": [],
          "notes": [],
          "rmp_rating": {
            "instructor": "Andrew Runka",
            "rating": 3.5,
            "num_ratings": 52,
            "department": "Computer Science",
            "rmp_id": 1902143,
            "would_take_again_percent": 63.8298,
            "avg_difficulty": 3.4
          }
        }
      ],
      "error": false,
      "error_message": ""
    }
  ]
}
```

**Multiple Courses Example:**
```bash
GET /universities/{university}/live-courses?term=fall&year=2025&subjects=COMP&course_codes=COMP1001,COMP1005&include_ratings=true
```

This returns an array with both COMP 1001 and COMP 1005, each with their complete section and rating data.

### Usage Examples

#### Common Use Cases

1. **Get all COMP courses for a term:**
   ```bash
   GET /universities/carleton/live-courses?term=fall&year=2025&subjects=COMP&limit=20
   ```

2. **Get specific course (COMP 1001) only:**
   ```bash
   GET /universities/carleton/live-courses?term=fall&year=2025&subjects=COMP&course_codes=COMP1001&include_ratings=true
   ```

3. **Compare multiple specific courses:**
   ```bash
   GET /universities/carleton/live-courses?term=fall&year=2025&subjects=COMP,MATH&course_codes=COMP1001,COMP1005,MATH1007&include_ratings=true
   ```

4. **Get all courses from multiple subjects:**
   ```bash
   GET /universities/carleton/live-courses?term=fall&year=2025&subjects=COMP,MATH,PHYS&limit=10
   ```

### Data Models

#### Health Response
- `status` (string): Service status
- `available_universities` (array): List of supported universities
- `version` (string): API version

#### University Info Response
- `university` (string): University identifier
- `total_courses` (integer): Total number of courses
- `total_subjects` (integer): Total number of subjects
- `subjects` (array): List of subject codes
- `data_metadata` (object): Source data metadata
- `discovery_metadata` (object): Discovery system metadata

#### Static Course Data
- `subject` (string): Subject code
- `code` (string): Full course code
- `title` (string): Course title
- `credits` (string): Credit value
- `description` (string): Course description

#### Live Course Data
- `course_code` (string): Full course code
- `subject_code` (string): Subject prefix
- `course_number` (string): Course number
- `catalog_title` (string): Official catalog title
- `catalog_credits` (float): Credit value from catalog
- `is_offered` (boolean): Whether course has sections
- `sections_found` (integer): Number of sections discovered
- `banner_title` (string): Title from registration system
- `banner_credits` (float): Credits from registration system
- `sections` (array): Live course sections
- `error` (boolean): Whether parsing failed
- `error_message` (string): Error details if applicable

#### Course Section
- `crn` (string): Course Reference Number
- `section` (string): Section identifier
- `status` (string): Enrollment status (Open, Full, Closed, etc.)
- `credits` (float): Section credit value
- `schedule_type` (string): Type (Lecture, Lab, Tutorial, etc.)
- `instructor` (string): Instructor name
- `meeting_times` (array): Meeting schedule details
- `notes` (array): Additional notes
- `rmp_rating` (object, optional): Rate My Professor data

#### Meeting Time
- `start_date` (string): Start date (MMM DD, YYYY)
- `end_date` (string): End date (MMM DD, YYYY)
- `days` (string): Days of week (e.g., "Wed Fri", "MoWe")
- `start_time` (string): Start time (HH:MM)
- `end_time` (string): End time (HH:MM)

#### RMP Rating
- `instructor` (string): Instructor name
- `rating` (float|null): Overall rating (1.0-5.0)
- `num_ratings` (integer): Number of student ratings
- `department` (string|null): Department name
- `rmp_id` (integer|null): Rate My Professor ID
- `would_take_again_percent` (float|null): Would take again percentage
- `avg_difficulty` (float|null): Average difficulty (1.0-5.0)

### Query Parameters

#### Live Courses Endpoint
- `term` (required): Term name (winter, summer, fall)
- `year` (required): Academic year (integer)
- `subjects` (required): Comma-separated subject codes
- `limit` (optional): Maximum courses per subject (1-50, default: 10)
- `include_ratings` (optional): Include Rate My Professor data (boolean, default: false)

#### Static Courses Endpoint
- `subject` (optional): Filter by subject code
- `search` (optional): Search in titles, codes, and descriptions
- `limit` (optional): Maximum results (0-1000, default: 50)

### Features

#### Live Schedule Data
- **Real-time enrollment status**: Open, Full, Waitlist, etc.
- **Complete section information**: Lectures, labs, tutorials
- **Meeting times**: Days, times, and date ranges
- **Instructor information**: Current teaching assignments
- **Course Reference Numbers (CRNs)**: For registration

#### Rate My Professor Integration
- **Instructor ratings**: Overall rating and number of reviews
- **Department information**: Professor's department
- **Student feedback metrics**: Would take again percentage, difficulty ratings
- **Direct RMP links**: Via RMP ID for detailed profiles

#### Performance
- **Cached RMP lookups**: Efficient batch processing of instructor ratings
- **Comprehensive error handling**: Continues operation even if RMP is unavailable
- **Term validation**: Checks available terms before querying

### Usage Examples

#### Get COMP 1001 with instructor ratings
```bash
curl "http://localhost:8000/universities/carleton/live-courses?term=fall&year=2025&subjects=COMP&include_ratings=true" \
  | jq '.courses[] | select(.course_code == "COMP 1001")'
```

#### Get all Computer Science courses for Winter 2026
```bash
curl "http://localhost:8000/universities/carleton/live-courses?term=winter&year=2026&subjects=COMP&limit=50"
```

#### Search for courses with "programming" in the title
```bash
curl "http://localhost:8000/universities/carleton/courses?search=programming&limit=10"
```

### Error Handling

The server returns appropriate HTTP status codes:
- **200**: Success
- **400**: Bad request (invalid parameters)
- **404**: University or resource not found
- **500**: Internal server error

Error responses include detail messages:
```json
{
  "detail": "University 'invalid' not found. Available: ['uottawa', 'carleton']"
}
```

---

## Common Message Types

### Message Structure
All modules can include messages with:
- `type` (string): Message category
- `message` (string): Human-readable text  
- Additional context fields as needed

### Message Types
- `"info"`: Informational messages
- `"warning"`: Non-fatal warnings
- `"error"`: Error conditions
- `"success"`: Successful operations

### Examples
```json
{
  "type": "info",
  "message": "Found 25 courses"
}
```

```json
{
  "type": "error", 
  "message": "Failed to connect to server",
  "details": "Connection timeout after 30 seconds"
}
```

```json
{
  "type": "warning",
  "message": "Some instructors not found on Rate My Professor"
}
```

---

## Error Handling

### Network Errors
When network requests fail, responses include error messages:

```json
{
  "timetables": [],
  "messages": [
    {
      "type": "error",
      "message": "Query failure"
    }
  ]
}
```

### Parsing Errors  
When data parsing fails:

```json
{
  "timetables": [],
  "messages": [
    {
      "type": "error", 
      "message": "Parser failure"
    }
  ]
}
```

### Rate My Professor Integration Errors
When ratings cannot be added:

```json
{
  "timetables": [...],
  "messages": [
    {
      "type": "warning",
      "message": "Failed to add instructor ratings: School not found"
    }
  ]
}
```

---

## Python Library Usage

All CLI commands can be replicated using the Python library directly. Below are Python code examples for each command.

### Course Module Examples

#### Get Subjects
```python
from uoapi.course import scrape_subjects

# Get all subjects from University of Ottawa
subjects = scrape_subjects()
result = {"subjects": list(subjects)}
```

#### Get Courses for Subjects
```python
from uoapi.course import scrape_subjects, get_courses

# Get subjects first
subjects = scrape_subjects()
subject_map = {s["subject_code"]: s["link"] for s in subjects}

# Get courses for specific subjects
target_subjects = ["CSI", "MAT"]
for subject_code in target_subjects:
    if subject_code in subject_map:
        courses = list(get_courses(subject_map[subject_code]))
        result = {
            "courses": {
                "subject_code": subject_code,
                "courses": courses
            }
        }
```

### Timetable Module Examples

#### Get Available Terms
```python
from uoapi.timetable.query_timetable import get_terms

# Get available terms
terms = get_terms()
result = {
    "available": [
        {
            "term": term["term"],
            "year": term["year"], 
            "term_code": term["term_code"]
        } for term in terms
    ],
    "messages": []
}
```

#### Query Course Timetable
```python
from uoapi.timetable.query_timetable import query_timetable

# Query specific course
courses = ["CSI3140"]
year = 2024
term = "winter"

results = []
for course_code in courses:
    timetable_data = query_timetable(course_code, year, term)
    results.append(timetable_data)

result = {
    "timetables": results,
    "messages": []
}
```

#### Query with Rate My Professor Integration
```python
from uoapi.timetable.query_timetable import query_timetable
from uoapi.rmp import inject_ratings_into_timetable

# Query course timetable
course_code = "CSI3140"
year = 2024
term = "winter"
university = "University of Ottawa"

# Get timetable data
timetable_data = query_timetable(course_code, year, term)
base_result = {
    "timetables": [timetable_data] if timetable_data else [],
    "messages": []
}

# Inject ratings
enhanced_result = inject_ratings_into_timetable(base_result, university)
```

### RMP Module Examples

#### Query Professor Ratings
```python
from uoapi.rmp import get_teachers_ratings_by_school

# Query specific professors
school = "University of Ottawa"
professors = ["John Smith", "Jane Doe"]

ratings = get_teachers_ratings_by_school(school, professors)
result = {
    "ratings": ratings,
    "school_name": school,
    "total_professors": len(professors),
    "found_professors": len([r for r in ratings if r.get("rmp_id")])
}
```

#### Query All Professors for School
```python
from uoapi.rmp import get_school_by_name

# Get school information
school_name = "Carleton University"
school = get_school_by_name(school_name)

result = {
    "ratings": [],
    "school_id": school.id if school else None,
    "school_name": school_name,
    "total_professors": 0,
    "found_professors": 0,
    "message": "No specific professors requested - provide professors list to query"
}
```

### Carleton Module Examples

#### Get Available Terms
```python
from uoapi.carleton.discovery import CarletonDiscovery

# Initialize discovery system
discovery = CarletonDiscovery()

# Get available terms
terms = discovery.get_available_terms()
result = {
    "data": {
        "available_terms": [
            {
                "term_code": term.term_code,
                "term_name": term.term_name,
                "year": term.year,
                "season": term.season
            } for term in terms
        ]
    },
    "messages": [
        {
            "type": "info",
            "message": f"Found {len(terms)} available terms"
        }
    ]
}
```

#### Query Courses
```python
from uoapi.carleton.discovery import CarletonDiscovery

# Initialize and query courses
discovery = CarletonDiscovery()
term_code = "202530"  # Fall 2025
subjects = ["COMP", "MATH"]
limit = 5

# Query courses for subjects
courses = []
for subject in subjects:
    subject_courses = discovery.get_courses_for_subject(term_code, subject, limit)
    courses.extend(subject_courses)

result = {
    "data": {
        "term_code": term_code,
        "subjects_queried": subjects,
        "total_courses": len(courses),
        "courses": courses
    },
    "messages": [
        {
            "type": "info",
            "message": f"Found {len(courses)} courses"
        }
    ]
}
```

### Discovery Module Examples

#### Get University Info
```python
from uoapi.discovery.discovery_service import get_courses_data, get_course_count, get_subjects_list

# Get university information
university = "uottawa"
data = get_courses_data(university)
course_count = get_course_count(university)
subjects = get_subjects_list(university)

result = {
    "action": "info",
    "data": {
        "university": university,
        "total_courses": course_count,
        "total_subjects": len(subjects),
        "subjects": sorted(subjects),
        "data_metadata": data.get("metadata", {}),
        "discovery_metadata": data.get("discovery_metadata", {})
    },
    "messages": [
        {
            "type": "info",
            "message": f"Found {course_count} courses across {len(subjects)} subjects"
        }
    ]
}
```

#### Search Courses
```python
from uoapi.discovery.discovery_service import search_courses

# Search for courses
university = "carleton"
query = "computer science"
limit = 2

courses = search_courses(university, query=query)
limited_courses = courses[:limit] if limit > 0 else courses

result = {
    "action": "search",
    "data": {
        "university": university,
        "query": query,
        "total_matches": len(courses),
        "courses_shown": len(limited_courses),
        "courses": limited_courses
    },
    "messages": [
        {
            "type": "info",
            "message": f"Found {len(courses)} courses matching '{query}'"
        }
    ]
}
```

#### Get Courses by Subject
```python
from uoapi.discovery.discovery_service import search_courses

# Get courses for specific subject
university = "uottawa"
subject_code = "CSI"
limit = 3

courses = search_courses(university, subject_code=subject_code)
limited_courses = courses[:limit] if limit > 0 else courses

result = {
    "action": "courses",
    "data": {
        "university": university,
        "subject_filter": subject_code,
        "total_courses": len(courses),
        "courses_shown": len(limited_courses),
        "courses": limited_courses
    },
    "messages": [
        {
            "type": "info",
            "message": f"Found {len(courses)} courses for subject {subject_code}"
        }
    ]
}
```

### Installation and Setup

#### Install the Package
```python
# Via pip
# pip install schedulo-api

# Verify installation
import uoapi
print(f"Schedulo API version: {uoapi.__version__}")
```

#### Import Modules
```python
# Import specific modules
from uoapi import course, timetable, rmp, carleton, discovery

# Import specific functions
from uoapi.course import scrape_subjects, get_courses
from uoapi.timetable.query_timetable import query_timetable, get_terms
from uoapi.rmp import get_teachers_ratings_by_school, inject_ratings_into_timetable
from uoapi.carleton.discovery import CarletonDiscovery
from uoapi.discovery.discovery_service import (
    get_courses_data, 
    search_courses, 
    get_available_universities
)
```

#### Error Handling
```python
import json
from uoapi.discovery.discovery_service import get_courses_data

try:
    # Attempt to get course data
    data = get_courses_data("uottawa")
    print(f"Successfully loaded {data['metadata']['total_courses']} courses")
    
except FileNotFoundError as e:
    print(f"Course data not found: {e}")
    
except ValueError as e:
    print(f"Invalid university or data: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Notes

1. **Timestamps**: Dates use ISO 8601 format (YYYY-MM-DD)
2. **Times**: 24-hour format (HH:MM) 
3. **Encoding**: All responses are UTF-8 encoded JSON
4. **Null Values**: Missing data represented as `null` or empty arrays/strings
5. **Consistency**: All modules follow similar message structure patterns
6. **Extensibility**: Response structures may include additional fields in future versions
7. **Python Library**: All CLI functionality available as importable Python functions
8. **Error Handling**: Python functions raise appropriate exceptions for error conditions