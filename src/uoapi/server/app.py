"""
FastAPI application for serving course data.
"""

from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from uoapi.discovery.discovery_service import (
    get_available_universities,
    get_courses_data,
    get_course_count,
    get_subjects_list,
    search_courses
)


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
        description="FastAPI server for accessing University of Ottawa and Carleton University course data",
        version="2.4.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        from uoapi import __version__
        return HealthResponse(
            status="healthy",
            available_universities=get_available_universities(),
            version=__version__
        )

    @app.get("/universities")
    async def get_universities():
        """Get list of available universities."""
        return {
            "universities": get_available_universities(),
            "count": len(get_available_universities())
        }

    @app.get("/universities/{university}/info", response_model=UniversityInfo)
    async def get_university_info(university: str):
        """Get comprehensive information about a university."""
        available_unis = get_available_universities()
        
        # Normalize university parameter
        normalized_uni = university.lower().replace(' ', '').replace('university', '').replace('of', '')
        
        if 'ottawa' in normalized_uni:
            target_uni = 'uottawa'
        elif 'carleton' in normalized_uni:
            target_uni = 'carleton'
        else:
            target_uni = normalized_uni
            
        if target_uni not in available_unis:
            raise HTTPException(
                status_code=404, 
                detail=f"University '{university}' not found. Available: {available_unis}"
            )
        
        try:
            data = get_courses_data(target_uni)
            course_count = get_course_count(target_uni)
            subjects = get_subjects_list(target_uni)
            
            info = UniversityInfo(
                university=target_uni,
                total_courses=course_count,
                total_subjects=len(subjects),
                subjects=sorted(subjects)
            )
            
            # Add metadata if available
            if 'metadata' in data:
                info.data_metadata = data['metadata']
            
            if 'discovery_metadata' in data:
                info.discovery_metadata = data['discovery_metadata']
                
            return info
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get university info: {str(e)}")

    @app.get("/universities/{university}/subjects", response_model=SubjectsResponse)
    async def get_university_subjects(university: str):
        """Get list of available subjects for a university."""
        available_unis = get_available_universities()
        
        # Normalize university parameter
        normalized_uni = university.lower().replace(' ', '').replace('university', '').replace('of', '')
        
        if 'ottawa' in normalized_uni:
            target_uni = 'uottawa'
        elif 'carleton' in normalized_uni:
            target_uni = 'carleton'
        else:
            target_uni = normalized_uni
            
        if target_uni not in available_unis:
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {available_unis}"
            )
        
        try:
            subjects = get_subjects_list(target_uni)
            return SubjectsResponse(
                university=target_uni,
                subjects=sorted(subjects),
                total_subjects=len(subjects)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get subjects: {str(e)}")

    @app.get("/universities/{university}/courses", response_model=CoursesResponse)
    async def get_university_courses(
        university: str,
        subject: Optional[str] = Query(None, description="Filter by subject code"),
        search: Optional[str] = Query(None, description="Search in course titles and descriptions"),
        limit: int = Query(50, description="Maximum number of results to return", ge=0, le=1000)
    ):
        """Get courses for a university with optional filtering."""
        available_unis = get_available_universities()
        
        # Normalize university parameter
        normalized_uni = university.lower().replace(' ', '').replace('university', '').replace('of', '')
        
        if 'ottawa' in normalized_uni:
            target_uni = 'uottawa'
        elif 'carleton' in normalized_uni:
            target_uni = 'carleton'
        else:
            target_uni = normalized_uni
            
        if target_uni not in available_unis:
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {available_unis}"
            )
        
        try:
            courses = search_courses(target_uni, subject_code=subject, query=search)
            
            # Apply limit
            if limit > 0:
                limited_courses = courses[:limit]
            else:
                limited_courses = courses
            
            # Convert to CourseData models
            course_data = []
            for course in limited_courses:
                course_data.append(CourseData(
                    subject=course["subject"],
                    code=course["code"],
                    title=course["title"],
                    credits=course["credits"],
                    description=course["description"]
                ))
            
            return CoursesResponse(
                university=target_uni,
                subject_filter=subject,
                query=search,
                total_courses=len(courses),
                courses_shown=len(limited_courses),
                courses=course_data
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get courses: {str(e)}")

    @app.get("/universities/{university}/live-courses", response_model=LiveCoursesResponse)
    async def get_live_university_courses(
        university: str,
        term: str = Query(..., description="Term (winter, summer, fall)"),
        year: int = Query(..., description="Year (e.g., 2025)"),
        subjects: str = Query(..., description="Comma-separated list of subject codes (e.g., COMP,MATH)"),
        course_codes: Optional[str] = Query(None, description="Filter by specific course codes (e.g., COMP1001,MATH1007)"),
        limit: int = Query(10, description="Maximum courses per subject", ge=1, le=50),
        include_ratings: bool = Query(False, description="Include Rate My Professor ratings for instructors")
    ):
        """Get live course schedule data with sections, tutorials, and labs."""
        available_unis = get_available_universities()
        
        # Normalize university parameter
        normalized_uni = university.lower().replace(' ', '').replace('university', '').replace('of', '')
        
        if 'ottawa' in normalized_uni:
            target_uni = 'uottawa'
        elif 'carleton' in normalized_uni:
            target_uni = 'carleton'
        else:
            target_uni = normalized_uni
            
        if target_uni not in available_unis:
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {available_unis}"
            )
            
        # Currently only support Carleton for live data
        if target_uni != 'carleton':
            raise HTTPException(
                status_code=400,
                detail="Live course data is currently only available for Carleton University"
            )
        
        try:
            from uoapi.carleton.discovery import CarletonDiscovery
            from uoapi.carleton.cli import term_name_to_code, term_code_to_name
            
            # Initialize discovery system
            discovery = CarletonDiscovery()
            
            # Convert term and year to term code
            term_code = term_name_to_code(term, year)
            if not term_code:
                raise HTTPException(status_code=400, detail=f"Invalid term: {term}")
            
            # Validate term is available
            available_terms = discovery.get_available_terms()
            available_term_codes = [t[0] for t in available_terms]
            if term_code not in available_term_codes:
                available_term_names = [t[1] for t in available_terms]
                raise HTTPException(
                    status_code=400, 
                    detail=f"Term {term} {year} is not available. Available terms: {', '.join(available_term_names)}"
                )
            
            # Parse subjects
            subject_list = [s.strip().upper() for s in subjects.split(',')]
            
            # Discover courses
            courses = discovery.discover_courses(
                term_code, subjects=subject_list, max_courses_per_subject=limit
            )
            
            # Filter by specific course codes if provided
            if course_codes:
                requested_codes = [code.strip().upper().replace(' ', '') for code in course_codes.split(',')]
                filtered_courses = []
                for course in courses:
                    # Normalize course code for comparison (remove spaces)
                    normalized_course_code = course.course_code.upper().replace(' ', '')
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
                            if section.instructor and section.instructor.strip() and section.instructor != "TBA":
                                instructor_name = section.instructor.strip()
                                parts = instructor_name.split()
                                if len(parts) >= 2:
                                    first_name = parts[0]
                                    last_name = " ".join(parts[1:])
                                    instructor_tuple = (first_name, last_name)
                                    all_instructors.append(instructor_tuple)
                                    instructor_name_map[f"{first_name} {last_name}"] = instructor_name
                    
                    # Get RMP data for all instructors
                    if all_instructors:
                        school_name = "Carleton University"  # Only Carleton supported for live data
                        ratings_result = get_teachers_ratings_by_school(school_name, all_instructors)
                        
                        # Create lookup dictionary from ratings result
                        if 'ratings' in ratings_result:
                            for rating in ratings_result['ratings']:
                                full_name = f"{rating['first_name']} {rating['last_name']}"
                                original_name = instructor_name_map.get(full_name, full_name)
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
                        meeting_times.append(MeetingTime(
                            start_date=mt.start_date,
                            end_date=mt.end_date,
                            days=mt.days,
                            start_time=mt.start_time,
                            end_time=mt.end_time
                        ))
                    
                    # Get RMP rating for this instructor
                    rmp_rating = None
                    if include_ratings and section.instructor and section.instructor.strip():
                        instructor_name = section.instructor.strip()
                        if instructor_name in instructor_ratings:
                            rating_data = instructor_ratings[instructor_name]
                            rmp_rating = RMPRating(
                                instructor=instructor_name,
                                rating=rating_data.get('rating'),
                                num_ratings=rating_data.get('num_ratings', 0),
                                department=rating_data.get('department'),
                                rmp_id=rating_data.get('rmp_id'),
                                would_take_again_percent=rating_data.get('would_take_again_percent'),
                                avg_difficulty=rating_data.get('avg_difficulty')
                            )
                    
                    sections.append(CourseSection(
                        crn=section.crn,
                        section=section.section,
                        status=section.status,
                        credits=section.credits,
                        schedule_type=section.schedule_type,
                        instructor=section.instructor,
                        meeting_times=meeting_times,
                        notes=section.notes,
                        rmp_rating=rmp_rating
                    ))
                
                live_courses.append(LiveCourseData(
                    course_code=course.course_code,
                    subject_code=course.subject_code,
                    course_number=course.course_number,
                    catalog_title=course.catalog_title,
                    catalog_credits=course.catalog_credits,
                    is_offered=course.is_offered,
                    sections_found=course.sections_found,
                    banner_title=course.banner_title,
                    banner_credits=course.banner_credits,
                    sections=sections,
                    error=course.error,
                    error_message=course.error_message
                ))
            
            # Calculate statistics
            offered_courses = [c for c in courses if c.is_offered]
            error_courses = [c for c in courses if c.error]
            
            return LiveCoursesResponse(
                university=target_uni,
                term_code=term_code,
                term_name=term_code_to_name(term_code),
                subjects_queried=subject_list,
                total_courses=len(courses),
                courses_offered=len(offered_courses),
                courses_with_errors=len(error_courses),
                offering_rate_percent=len(offered_courses) / max(1, len(courses)) * 100,
                courses=live_courses
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get live courses: {str(e)}")

    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Endpoint not found"}
        )

    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app