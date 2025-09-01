"""
FastAPI application for serving course data.
"""

from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from uoapi.core import University
from uoapi.universities.carleton.provider import CarletonProvider
from uoapi.universities.uottawa.provider import UOttawaProvider
from uoapi.services import DefaultCourseService, DefaultTimetableService


# Initialize providers
_providers = {
    "carleton": CarletonProvider(),
    "uottawa": UOttawaProvider(),
}


def get_provider(university: str):
    """Get the appropriate provider for a university."""
    normalized = university.lower()
    if normalized in ["carleton", "cu"]:
        return _providers["carleton"]
    elif normalized in ["uottawa", "ottawa", "uo"]:
        return _providers["uottawa"]
    else:
        raise ValueError(
            f"University '{university}' not supported. Available: carleton, uottawa"
        )


def get_available_universities():
    """Get list of available universities."""
    return list(_providers.keys())


def normalize_university(university: str) -> str:
    """Normalize university parameter to standard form."""
    normalized_uni = (
        university.lower().replace(" ", "").replace("university", "").replace("of", "")
    )

    if "ottawa" in normalized_uni:
        return "uottawa"
    elif "carleton" in normalized_uni:
        return "carleton"
    else:
        return normalized_uni


def term_code_to_name(term_code: str) -> str:
    """Convert term code to human-readable name."""
    if len(term_code) == 6:
        # Carleton format: YYYYTS (e.g., 202530 = Fall 2025)
        year = term_code[:4]
        term_num = term_code[4:6]
        term_names = {"10": "Winter", "20": "Summer", "30": "Fall"}
        term_name = term_names.get(term_num, "Unknown")
        return f"{term_name} {year}"
    else:
        # UOttawa format: YYYY+term (e.g., 2025fall)
        if term_code.endswith("fall"):
            return f"Fall {term_code[:4]}"
        elif term_code.endswith("winter"):
            return f"Winter {term_code[:4]}"
        elif term_code.endswith("summer"):
            return f"Summer {term_code[:4]}"
        else:
            return term_code


class UniversityInfo(BaseModel):
    university: str
    total_courses: int
    total_subjects: int
    subjects: List[str]
    data_metadata: Optional[Dict[str, Any]] = None
    discovery_metadata: Optional[Dict[str, Any]] = None


class CourseData(BaseModel):
    subject: str
    code: str
    title: str
    credits: str  # Credits can be "3 units", "0.5", etc.
    description: str


class MeetingTime(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class RMPRating(BaseModel):
    instructor: str
    rating: Optional[float] = None
    num_ratings: int = 0
    department: Optional[str] = None
    rmp_id: Optional[int] = None
    would_take_again_percent: Optional[float] = None
    avg_difficulty: Optional[float] = None


class ProfessorRatingResponse(BaseModel):
    first_name: str
    last_name: str
    university: str
    school_name: str
    rating: Optional[float] = None
    num_ratings: int = 0
    department: Optional[str] = None
    rmp_id: Optional[int] = None
    would_take_again_percent: Optional[float] = None
    avg_difficulty: Optional[float] = None
    profile_url: Optional[str] = None
    interpretation: Optional[str] = None


class CatalogCoursesResponse(BaseModel):
    university: str
    subjects_queried: Optional[List[str]] = None
    total_courses: int
    courses_shown: int
    courses_by_subject: Dict[str, List[CourseData]]


class CourseSection(BaseModel):
    crn: str
    section: str
    status: str
    credits: float
    schedule_type: str
    instructor: str
    meeting_times: List[MeetingTime]
    notes: List[str]
    rmp_rating: Optional[RMPRating] = None


class LiveCourseData(BaseModel):
    course_code: str
    subject_code: str
    course_number: str
    catalog_title: str
    catalog_credits: float
    is_offered: bool
    sections_found: int
    banner_title: str
    banner_credits: float
    sections: List[CourseSection]
    error: bool
    error_message: str


class CourseComponent(BaseModel):
    name: str  # A1, A2, B1, B2, etc.
    crn: str
    status: str
    credits: float
    schedule_type: str
    instructor: str
    meeting_times: List[MeetingTime]
    notes: List[str]
    rmp_rating: Optional[RMPRating] = None


class CourseGroup(BaseModel):
    section: str  # A, B, C, D, etc.
    components: List[CourseComponent]  # Lecture, Tutorial, Lab


class SingleCourseResponse(BaseModel):
    university: str
    term_code: str
    term_name: str
    course: Dict[str, Any]  # Basic course info
    sections: List[CourseGroup]  # Grouped by section letter


class CoursesResponse(BaseModel):
    university: str
    subject_filter: Optional[str] = None
    query: Optional[str] = None
    total_courses: int
    courses_shown: int
    courses: List[CourseData]


class LiveCoursesResponse(BaseModel):
    university: str
    term_code: str
    term_name: str
    subjects_queried: List[str]
    total_courses: int
    courses_offered: int
    courses_with_errors: int
    offering_rate_percent: float
    courses: List[LiveCourseData]


class SubjectsResponse(BaseModel):
    university: str
    subjects: List[str]
    total_subjects: int


class HealthResponse(BaseModel):
    status: str
    available_universities: List[str]
    version: str


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Schedulo API Server",
        description="FastAPI server for accessing University of Ottawa and Carleton University course data with catalog browsing and professor ratings",
        version="3.2.4",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        from uoapi.__version__ import __version__

        return HealthResponse(
            status="healthy",
            available_universities=get_available_universities(),
            version=__version__,
        )

    @app.get("/universities")
    async def get_universities():
        """Get list of available universities."""
        return {
            "universities": get_available_universities(),
            "count": len(get_available_universities()),
        }

    @app.get("/universities/{university}/info", response_model=UniversityInfo)
    async def get_university_info(university: str):
        """Get comprehensive information about a university."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        try:
            provider = get_provider(target_uni)
            subjects = provider.get_subjects()
            courses = provider.get_courses()

            info = UniversityInfo(
                university=target_uni,
                total_courses=len(courses),
                total_subjects=len(subjects),
                subjects=sorted([s.code for s in subjects]),
            )

            return info

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get university info: {str(e)}"
            )

    @app.get("/universities/{university}/subjects", response_model=SubjectsResponse)
    async def get_university_subjects(
        university: str,
        limit: int = Query(20, description="Maximum number of subjects to return", ge=1, le=1000),
    ):
        """Get list of available subjects for a university (limited)."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        try:
            provider = get_provider(target_uni)
            subjects = provider.get_subjects()
            subject_codes = sorted([s.code for s in subjects])

            # Apply limit
            limited_subjects = subject_codes[:limit]

            return SubjectsResponse(
                university=target_uni,
                subjects=limited_subjects,
                total_subjects=len(subject_codes),
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get subjects: {str(e)}"
            )

    @app.get("/universities/{university}/subjects/catalog", response_model=SubjectsResponse)
    async def get_all_university_subjects(
        university: str,
    ):
        """Get complete list of all subjects for a university (catalog)."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        try:
            provider = get_provider(target_uni)
            subjects = provider.get_subjects()
            subject_codes = sorted([s.code for s in subjects])

            return SubjectsResponse(
                university=target_uni,
                subjects=subject_codes,
                total_subjects=len(subject_codes),
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get subjects: {str(e)}"
            )

    @app.get("/universities/{university}/terms")
    async def get_university_terms(university: str):
        """Get available terms for a university."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        try:
            provider = get_provider(target_uni)
            terms = provider.get_available_terms()
            
            return {
                "university": target_uni,
                "terms": [{"code": code, "name": name} for code, name in terms],
                "total_terms": len(terms),
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get terms: {str(e)}"
            )

    @app.get("/universities/{university}/courses/catalog", response_model=CatalogCoursesResponse)
    async def get_catalog_courses(
        university: str,
        subjects: Optional[str] = Query(
            None, description="Comma-separated list of subject codes (e.g., COMP,MATH for Carleton or CSI,MAT for UOttawa)"
        ),
        limit: int = Query(
            10, description="Maximum courses per subject (0 for no limit)", ge=0, le=1000
        ),
    ):
        """Get catalog courses (no live sections, no term required)."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        try:
            provider = get_provider(target_uni)
            
            # Parse subjects if provided
            subject_list = None
            if subjects:
                subject_list = [s.strip().upper() for s in subjects.split(",")]
                
                # Validate subject code format based on university
                for subject in subject_list:
                    is_valid = False
                    if target_uni == "carleton" and len(subject) == 4 and subject.isalpha():
                        is_valid = True
                    elif target_uni == "uottawa" and len(subject) == 3 and subject.isalpha():
                        is_valid = True
                    
                    if not is_valid:
                        expected_format = "4-letter" if target_uni == "carleton" else "3-letter"
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid subject code '{subject}' for {target_uni}. Expected {expected_format} format."
                        )

            # Get catalog courses
            if subject_list:
                all_courses = []
                for subject in subject_list:
                    subject_courses = provider.get_courses(subject_code=subject)
                    if limit > 0:
                        subject_courses = subject_courses[:limit]
                    all_courses.extend(subject_courses)
            else:
                all_courses = provider.get_courses()
                if limit > 0:
                    all_courses = all_courses[:limit]

            # Group by subject for response
            courses_by_subject = {}
            for course in all_courses:
                subject = course.subject_code
                if subject not in courses_by_subject:
                    courses_by_subject[subject] = []
                
                courses_by_subject[subject].append(
                    CourseData(
                        subject=course.subject_code,
                        code=course.course_code,
                        title=course.title,
                        credits=str(course.credits),
                        description=course.description,
                    )
                )

            return CatalogCoursesResponse(
                university=target_uni,
                subjects_queried=subject_list,
                total_courses=len(all_courses),
                courses_shown=len(all_courses),
                courses_by_subject=courses_by_subject,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get catalog courses: {str(e)}"
            )

    @app.get("/universities/{university}/professors/{first_name}/{last_name}", response_model=ProfessorRatingResponse)
    async def get_professor_rating(
        university: str,
        first_name: str,
        last_name: str,
    ):
        """Get Rate My Professor ratings for an instructor."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        try:
            from uoapi.rmp.rate_my_prof import get_professor_ratings
            
            # Map university names to school names for RMP
            university_to_school = {
                "carleton": "Carleton University",
                "uottawa": "University of Ottawa",
            }
            
            if target_uni not in university_to_school:
                raise HTTPException(
                    status_code=400,
                    detail=f"Professor ratings not supported for {university}. Supported: carleton, uottawa"
                )
            
            school_name = university_to_school[target_uni]
            
            # Get ratings using RMP API
            ratings = get_professor_ratings([(first_name, last_name)], school_name)
            
            if not ratings or len(ratings) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"No ratings found for {first_name} {last_name} at {school_name}"
                )
            
            professor = ratings[0]
            
            # Generate profile URL if we have an RMP ID
            profile_url = None
            if professor.get('rmp_id'):
                profile_url = f"https://www.ratemyprofessors.com/professor/{professor['rmp_id']}"
            
            # Generate interpretation
            interpretation = None
            rating = professor.get('rating')
            if rating:
                if rating >= 4.0:
                    interpretation = "Excellent professor (4.0+ rating)"
                elif rating >= 3.0:
                    interpretation = "Good professor (3.0+ rating)"
                elif rating >= 2.0:
                    interpretation = "Fair professor (2.0+ rating)"
                else:
                    interpretation = "Below average professor (<2.0 rating)"
            
            return ProfessorRatingResponse(
                first_name=first_name,
                last_name=last_name,
                university=target_uni,
                school_name=school_name,
                rating=professor.get("rating"),
                num_ratings=professor.get("num_ratings", 0),
                department=professor.get("department"),
                rmp_id=professor.get("rmp_id"),
                would_take_again_percent=professor.get("would_take_again_percent"),
                avg_difficulty=professor.get("avg_difficulty"),
                profile_url=profile_url,
                interpretation=interpretation,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get professor rating: {str(e)}"
            )

    @app.get("/universities/{university}/courses/{course_code}")
    async def get_single_course_catalog(
        university: str,
        course_code: str,
    ):
        """Get catalog information for a single course."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        try:
            provider = get_provider(target_uni)
            
            # Extract subject code from course code (e.g., COMP from COMP1005)
            course_code = course_code.upper().replace(" ", "")
            subject = "".join(c for c in course_code if c.isalpha())
            
            # Validate subject code format based on university
            is_valid = False
            if target_uni == "carleton" and len(subject) == 4 and subject.isalpha():
                is_valid = True
            elif target_uni == "uottawa" and len(subject) == 3 and subject.isalpha():
                is_valid = True
            
            if not is_valid:
                expected_format = "4-letter" if target_uni == "carleton" else "3-letter"
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid course code '{course_code}' for {target_uni}. Expected {expected_format} subject format."
                )
            
            # Get courses for this subject
            courses = provider.get_courses(subject_code=subject)
            
            # Find the specific course
            target_course = None
            for course in courses:
                if course.course_code.upper().replace(" ", "") == course_code:
                    target_course = course
                    break
            
            if not target_course:
                raise HTTPException(
                    status_code=404,
                    detail=f"Course '{course_code}' not found in catalog for {target_uni}"
                )
            
            return {
                "university": target_uni,
                "course": {
                    "subject": target_course.subject_code,
                    "code": target_course.course_code,
                    "title": target_course.title,
                    "credits": str(target_course.credits),
                    "description": target_course.description,
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get course: {str(e)}"
            )

    @app.get("/universities/{university}/courses/{course_code}/live", response_model=SingleCourseResponse)
    async def get_single_course_live(
        university: str,
        course_code: str,
        term: str = Query(..., description="Term (winter, summer, fall)"),
        year: int = Query(..., description="Year (e.g., 2025)"),
        include_ratings: bool = Query(
            False, description="Include Rate My Professor ratings for instructors"
        ),
    ):
        """Get live course data with sections for a single course."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        try:
            provider = get_provider(target_uni)
            
            # Convert term and year to term code format
            if target_uni == "carleton":
                term_mapping = {"winter": "10", "summer": "20", "fall": "30"}
                term_code = f"{year}{term_mapping.get(term.lower(), '10')}"
            else:
                term_code = f"{year}{term.lower()}"

            # Extract subject from course code
            course_code = course_code.upper().replace(" ", "")
            subject = "".join(c for c in course_code if c.isalpha())
            
            # Validate subject code format
            is_valid = False
            if target_uni == "carleton" and len(subject) == 4 and subject.isalpha():
                is_valid = True
            elif target_uni == "uottawa" and len(subject) == 3 and subject.isalpha():
                is_valid = True
            
            if not is_valid:
                expected_format = "4-letter" if target_uni == "carleton" else "3-letter"
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid course code '{course_code}' for {target_uni}. Expected {expected_format} subject format."
                )

            # Use the new direct single course discovery method
            course = provider.discover_single_course(
                term_code=term_code,
                course_code=course_code
            )

            if not course:
                raise HTTPException(
                    status_code=404,
                    detail=f"Course '{course_code}' not found for {term} {year} at {target_uni}"
                )
            
            # Get instructor ratings if requested
            instructor_ratings = {}
            if include_ratings:
                from uoapi.rmp.rate_my_prof import get_professor_ratings
                university_to_school = {
                    "carleton": "Carleton University",
                    "uottawa": "University of Ottawa"
                }
                school_name = university_to_school.get(target_uni, "")
                if school_name:
                    instructors = set()
                    for section in course.sections:
                        if section.instructor and section.instructor.strip() and section.instructor != "TBA":
                            name_parts = section.instructor.strip().split()
                            if len(name_parts) >= 2:
                                instructors.add((name_parts[0], name_parts[-1]))
                    
                    if instructors:
                        try:
                            ratings = get_professor_ratings(list(instructors), school_name)
                            for rating in ratings:
                                full_name = f"{rating.get('first_name', '')} {rating.get('last_name', '')}".strip()
                                instructor_ratings[full_name] = rating
                        except Exception:
                            pass
            
            # Group sections by section letter and fix section naming issues
            sections_by_group = {}
            
            for section in course.sections:
                # Fix section naming issues
                section_id = section.section.strip()
                original_section_id = section_id  # Keep original for component name
                
                # Handle common parsing issues
                if section_id in ["Open", "Full", "Waitlist"]:
                    # This is likely a status being misread as section
                    # Try to extract from notes or default to 'A'
                    section_id = "A"
                    original_section_id = "A"
                    
                # Extract the main section letter (A, B, C, D) from section codes like A1, A2, B1, etc.
                main_section = section_id[0] if section_id else "A"
                
                # Use the original section ID as the component name (A, A1, A2, B, B1, B2, etc.)
                component_name = original_section_id if original_section_id else main_section
                
                if main_section not in sections_by_group:
                    sections_by_group[main_section] = []
                
                # Convert meeting times
                meeting_times = []
                for mt in section.meeting_times:
                    meeting_times.append({
                        "start_date": mt.start_date,
                        "end_date": mt.end_date,
                        "days": mt.days,
                        "start_time": mt.start_time,
                        "end_time": mt.end_time,
                    })
                
                # Get RMP rating for this instructor
                rmp_rating = None
                if include_ratings and section.instructor and section.instructor.strip():
                    instructor_name = section.instructor.strip()
                    if instructor_name in instructor_ratings:
                        rating_data = instructor_ratings[instructor_name]
                        rmp_rating = {
                            "instructor": instructor_name,
                            "rating": rating_data.get("rating"),
                            "num_ratings": rating_data.get("num_ratings", 0),
                            "department": rating_data.get("department"),
                            "rmp_id": rating_data.get("rmp_id"),
                            "would_take_again_percent": rating_data.get("would_take_again_percent"),
                            "avg_difficulty": rating_data.get("avg_difficulty"),
                        }
                
                # Fix credits issue - don't use CRN as credits
                actual_credits = section.credits
                if isinstance(actual_credits, (int, float)) and actual_credits > 10:
                    # This is likely the CRN being misread as credits
                    actual_credits = 0.5  # Default for most components
                    if section.schedule_type.lower() == "lecture":
                        actual_credits = course.credits if course.credits > 0 else 0.5
                
                component = {
                    "name": component_name,
                    "crn": section.crn,
                    "status": section.status or "",
                    "credits": actual_credits,
                    "schedule_type": section.schedule_type,
                    "instructor": section.instructor or "TBA",
                    "meeting_times": meeting_times,
                    "notes": section.notes,
                    "rmp_rating": rmp_rating,
                }
                
                sections_by_group[main_section].append(component)
            
            # Create structured response
            structured_sections = []
            for section_letter in sorted(sections_by_group.keys()):
                components = sections_by_group[section_letter]
                structured_sections.append({
                    "section": section_letter,
                    "components": components
                })
            
            return {
                "university": target_uni,
                "term_code": term_code,
                "term_name": f"{term.title()} {year}",
                "course": {
                    "course_code": course.course_code,
                    "subject_code": course.subject_code,
                    "title": course.title or "",
                    "credits": course.credits,
                    "is_offered": course.is_offered,
                    "sections_found": len(course.sections),
                },
                "sections": structured_sections,
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get live course data: {str(e)}"
            )

    @app.get(
        "/universities/{university}/courses/live", response_model=LiveCoursesResponse
    )
    async def get_live_courses(
        university: str,
        term: str = Query(..., description="Term (winter, summer, fall)"),
        year: int = Query(..., description="Year (e.g., 2025)"),
        subjects: str = Query(
            ..., description="Comma-separated list of subject codes (e.g., COMP,MATH)"
        ),
        course_codes: Optional[str] = Query(
            None,
            description="Filter by specific course codes (e.g., COMP1001,MATH1007)",
        ),
        limit: int = Query(10, description="Maximum courses per subject", ge=1, le=50),
        include_ratings: bool = Query(
            False, description="Include Rate My Professor ratings for instructors"
        ),
    ):
        """Get live course schedule data with sections, tutorials, and labs."""
        target_uni = normalize_university(university)

        if target_uni not in get_available_universities():
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {get_available_universities()}",
            )

        # Check if university supports live data
        if target_uni not in ["carleton", "uottawa"]:
            raise HTTPException(
                status_code=400,
                detail="Live course data is currently only available for Carleton University and University of Ottawa",
            )

        try:
            # Use the provider's discover_courses method
            provider = get_provider(target_uni)

            # Convert term and year to term code format
            if target_uni == "carleton":
                # Carleton uses YYYYTS format (T=term: 1=winter, 2=summer, 3=fall, S=0)
                term_mapping = {"winter": "10", "summer": "20", "fall": "30"}
                term_code = f"{year}{term_mapping.get(term.lower(), '10')}"
            else:
                # UOttawa uses YYYY+term format
                term_code = f"{year}{term.lower()}"

            # Parse subjects and course codes
            subject_list = [s.strip().upper() for s in subjects.split(",")]
            course_codes_list = None
            if course_codes:
                course_codes_list = [c.strip().upper() for c in course_codes.split(",")]

            # Get live course data using the provider
            # If specific course codes are requested, use a higher limit to ensure we find them
            effective_limit = max(limit, 100) if course_codes_list else limit
            result = provider.discover_courses(
                term_code=term_code,
                subjects=subject_list,
                course_codes=course_codes_list,
                max_courses_per_subject=effective_limit,
            )

            courses = result.courses

            # Filter by specific course codes if provided
            if course_codes:
                requested_codes = [
                    code.strip().upper().replace(" ", "")
                    for code in course_codes.split(",")
                ]
                filtered_courses = []
                for course in courses:
                    # Normalize course code for comparison (remove spaces)
                    normalized_course_code = course.course_code.upper().replace(" ", "")
                    if normalized_course_code in requested_codes:
                        filtered_courses.append(course)
                courses = filtered_courses

            # Convert to API models
            live_courses = []

            # Get RMP ratings if requested
            instructor_ratings = {}
            if include_ratings:
                try:
                    from uoapi.rmp import get_teachers_ratings_by_school

                    # Collect all unique instructors and convert to tuples
                    all_instructors = []
                    instructor_name_map = {}  # Map tuples back to original names

                    for course in courses:
                        for section in course.sections:
                            if (
                                section.instructor
                                and section.instructor.strip()
                                and section.instructor != "TBA"
                            ):
                                instructor_name = section.instructor.strip()
                                parts = instructor_name.split()
                                if len(parts) >= 2:
                                    first_name = parts[0]
                                    last_name = " ".join(parts[1:])
                                    instructor_tuple = (first_name, last_name)
                                    all_instructors.append(instructor_tuple)
                                    instructor_name_map[f"{first_name} {last_name}"] = (
                                        instructor_name
                                    )

                    # Get RMP data for all instructors
                    if all_instructors:
                        # Use appropriate school name based on university
                        if target_uni == "carleton":
                            school_name = "Carleton University"
                        elif target_uni == "uottawa":
                            school_name = "University of Ottawa"
                        else:
                            school_name = "Unknown"

                        ratings_result = get_teachers_ratings_by_school(
                            school_name, all_instructors
                        )

                        # Create lookup dictionary from ratings result
                        if "ratings" in ratings_result:
                            for rating in ratings_result["ratings"]:
                                full_name = (
                                    f"{rating['first_name']} {rating['last_name']}"
                                )
                                original_name = instructor_name_map.get(
                                    full_name, full_name
                                )
                                instructor_ratings[original_name] = rating

                except Exception as e:
                    # Log error but continue without ratings
                    print(f"Warning: Failed to get RMP ratings: {e}")

            for course in courses:
                # Convert sections
                sections = []
                for section in course.sections:
                    # Convert meeting times
                    meeting_times = []
                    for mt in section.meeting_times:
                        meeting_times.append(
                            MeetingTime(
                                start_date=mt.start_date,
                                end_date=mt.end_date,
                                days=mt.days,
                                start_time=mt.start_time,
                                end_time=mt.end_time,
                            )
                        )

                    # Get RMP rating for this instructor
                    rmp_rating = None
                    if (
                        include_ratings
                        and section.instructor
                        and section.instructor.strip()
                    ):
                        instructor_name = section.instructor.strip()
                        if instructor_name in instructor_ratings:
                            rating_data = instructor_ratings[instructor_name]
                            rmp_rating = RMPRating(
                                instructor=instructor_name,
                                rating=rating_data.get("rating"),
                                num_ratings=rating_data.get("num_ratings", 0),
                                department=rating_data.get("department"),
                                rmp_id=rating_data.get("rmp_id"),
                                would_take_again_percent=rating_data.get(
                                    "would_take_again_percent"
                                ),
                                avg_difficulty=rating_data.get("avg_difficulty"),
                            )

                    sections.append(
                        CourseSection(
                            crn=section.crn,
                            section=section.section,
                            status=section.status,
                            credits=section.credits,
                            schedule_type=section.schedule_type,
                            instructor=section.instructor,
                            meeting_times=meeting_times,
                            notes=section.notes,
                            rmp_rating=rmp_rating,
                        )
                    )

                live_courses.append(
                    LiveCourseData(
                        course_code=course.course_code,
                        subject_code=course.subject_code,
                        course_number=course.course_number,
                        catalog_title=course.title,
                        catalog_credits=course.credits,
                        is_offered=course.is_offered,
                        sections_found=len(course.sections),
                        banner_title=course.title,
                        banner_credits=course.credits,
                        sections=sections,
                        error=False,
                        error_message="",
                    )
                )

            # Calculate statistics
            offered_courses = [c for c in courses if c.is_offered]

            return LiveCoursesResponse(
                university=target_uni,
                term_code=term_code,
                term_name=term_code_to_name(term_code),
                subjects_queried=subject_list,
                total_courses=len(courses),
                courses_offered=len(offered_courses),
                courses_with_errors=0,  # New provider doesn't track errors this way
                offering_rate_percent=len(offered_courses) / max(1, len(courses)) * 100,
                courses=live_courses,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get live courses: {str(e)}"
            )

    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})

    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    return app
