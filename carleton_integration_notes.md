# Carleton University Integration Notes

## Initial Analysis - Term Selection Page

**URL**: https://central.carleton.ca/prod/bwysched.p_select_term?wsea_code=EXT

### System Type
- Banner ERP system (similar to many universities)
- Uses traditional HTML forms with POST methods

### Form Structure
- **Action**: `bwysched.p_search_fields`
- **Method**: POST
- **Hidden Parameters**:
  - `wsea_code`: "EXT"
  - `session_id`: "23953502" (likely dynamic)

### Available Terms (as of current scrape)
- Summer 2025: `202520` (May-August)
- Fall 2025: `202530` (September-December) 
- Winter 2026: `202610` (January-April)

### Term Code Format
- Appears to follow `YYYYST` format
- YYYY = year
- S = season (2=Summer, 3=Fall, 1=Winter following year)
- T = term number within year

## Course Search Form Analysis

**URL**: https://central.carleton.ca/prod/bwysched.p_search_fields (POST)

### Form Structure
- **Action**: `bwysched.p_course_search`
- **Method**: POST
- **Key Fields**:
  - `sel_levl`: Course level (UG/GR/All)
  - `sel_subj`: Subject codes (multiple select)
  - `sel_number`: Course number (partial search supported)
  - `sel_crn`: Course Reference Number (5 digits)
  - `sel_special`: Special criteria (Open/Online/All)

### Available Subjects (Sample)
- COMP: Computer Science
- MATH: Mathematics  
- PHYS: Physics
- CHEM: Chemistry
- BIOL: Biology
- ECON: Economics
- PSYC: Psychology
- ENGL: English
- [100+ total subjects available]

### Search Capabilities
- Course level filtering (Undergraduate/Graduate)
- Subject-based search with multi-select
- Partial course number matching (e.g., "1" for all 1st year)
- CRN direct lookup
- Special filters (open registration, online courses)
- Advanced options: session type, schedule type, instructor

### Session Types
- Day, Evening, Web, Algonquin, U of O, Unscheduled

### Schedule Types
- Lecture, Lab, Tutorial, Seminar, Workshop, etc.

## Banner Registration System Progress

### Course Search Process
1. **Term Selection**: POST to `bwysched.p_search_fields` with term code
2. **Course Search Form**: Comprehensive search interface with filters
3. **Search Execution**: POST to `bwysched.p_course_search` with criteria

### Available Search Parameters
- **Course Level**: UG (Undergraduate), GR (Graduate), All
- **Subject**: AERO, COMP, MATH, etc. (100+ subjects available)
- **Course Number**: Full or partial (e.g., "2001" or "1" for all 1st year)
- **CRN**: 5-digit Course Reference Number for direct lookup
- **Special Criteria**: Show All, Open for Registration, Online courses

### Advanced Search Options
- **Session Type**: Day, Evening, Web, Algonquin, U of O, Unscheduled
- **Schedule Type**: Lecture, Lab, Tutorial, Seminar, Workshop, etc.
- **Instructor**: Searchable instructor list
- **Time Filters**: Days of week, start/end times

### Current Implementation Challenges
- **Server Errors**: Banner system returns 500 Internal Server Error on search
- **Session Management**: Complex session/cookie requirements
- **Validation**: Strict parameter validation may be required
- **Rate Limiting**: Possible anti-automation measures

### Integration Strategy Notes
- **Two-System Approach**: Course catalog (static) + Registration system (dynamic)
- **Data Complementarity**: Catalog provides descriptions, registration provides schedules
- **Access Method**: May require browser automation instead of direct HTTP requests

### Next Steps for Integration
1. ~~POST to `bwysched.p_course_search` with search parameters~~ (Blocked by server errors)
2. Investigate browser automation approach (Selenium/Playwright)
3. Analyze course results format when accessible
4. Compare with existing uOttawa integration patterns

## Course Catalog Analysis

**URL**: https://calendar.carleton.ca/undergrad/courses/

### System Type
- Modern CourseLeaf calendar system (different from registration system)
- Static HTML pages with organized course information
- Uses responsive design with jQuery UI components

### Structure
- Comprehensive course catalog for undergraduate programs
- Course listings organized by subject code
- Detailed course descriptions with prerequisites, corequisites
- Credit hours and academic level information

### Technical Implementation
- CourseLeaf CMS (courseleaf.js, courseleaf.css)
- jQuery UI for interface interactions
- Font Awesome icons
- Responsive CSS framework

### Data Access Potential
- Static course catalog data (descriptions, prerequisites)
- Different from dynamic timetable system
- Could be scraped for comprehensive course information
- Complements the registration system data

### Integration Strategy
Two complementary data sources:
1. **Registration System** (`central.carleton.ca`): Real-time course offerings, schedules, availability
2. **Course Catalog** (`calendar.carleton.ca`): Static course descriptions, prerequisites, academic information

## Course Data Structure Analysis

**URL Pattern**: https://calendar.carleton.ca/undergrad/courses/{SUBJECT}/

### Course Block Structure
Each course is contained in a `<div class="courseblock">` with:

1. **Course Header**:
   - `<span class="courseblockcode">`: Course code (e.g., AERO 2001)
   - Credit value: [0.5 credit] or [1.0 credit]
   - Course title

2. **Course Description**: Plain text paragraph

3. **Additional Details** (`<div class="coursedescadditional">`):
   - Experiential Learning Activity indicators
   - Cross-listed courses ("Also listed as...")
   - Prerequisites with clickable course links
   - Preclusions ("Precludes additional credit for...")
   - Lecture/lab schedule information

### Extractable Data Fields
- **Course Code**: AERO 2001, COMP 1405, etc.
- **Credits**: 0.5 or 1.0 (occasionally other values)
- **Title**: Course name
- **Description**: Full course description
- **Prerequisites**: Parsed from prerequisite text with course links
- **Cross-listings**: Alternative course codes
- **Preclusions**: Courses that can't be taken for additional credit
- **Schedule**: Lecture/tutorial/lab hours
- **Special Indicators**: Experiential Learning, etc.

### URL Pattern for All Subjects
- Individual subject pages: `/undergrad/courses/{SUBJECT}/`
- Available subjects can be scraped from main courses page
- Each subject page contains all courses for that department

### Technical Notes
- Registration system: Legacy Banner ERP with session management
- Course catalog: Modern CourseLeaf CMS with static content
- Different authentication and session requirements
- Uses jQuery for dynamic subject loading based on level selection
- Course links use JavaScript `showCourse()` function for dynamic loading
- Structured HTML makes parsing straightforward with CSS selectors