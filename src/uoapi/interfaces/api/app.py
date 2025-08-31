"""
Refactored FastAPI application using the service layer.

This module provides the REST API interface using the new service-based
architecture for better separation of concerns and maintainability.
"""

from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

from uoapi.core import (
    University,
    UniversityNotSupportedError,
    ServiceError,
    LiveDataNotSupportedError,
    TermNotAvailableError,
)
from uoapi.services import (
    DefaultCourseService,
    DefaultTimetableService,
    DefaultRatingService,
    DefaultDiscoveryService,
)

logger = logging.getLogger(__name__)


# API Response Models
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


class APIServices:
    """Container for all API services."""

    def __init__(self):
        self.course_service = DefaultCourseService()
        self.timetable_service = DefaultTimetableService()
        self.rating_service = DefaultRatingService()
        self.discovery_service = DefaultDiscoveryService()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Schedulo API Server",
        description="FastAPI server for accessing University of Ottawa and Carleton University course data",
        version="3.0.0",  # Updated version for new architecture
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Initialize services
    services = APIServices()

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        from uoapi import __version__

        try:
            available_unis = services.discovery_service.get_available_universities()
        except Exception as e:
            logger.error(f"Failed to get available universities: {e}")
            available_unis = []

        return HealthResponse(
            status="healthy", available_universities=available_unis, version=__version__
        )

    @app.get("/universities")
    async def get_universities():
        """Get list of available universities."""
        try:
            available_unis = services.discovery_service.get_available_universities()
            return {"universities": available_unis, "count": len(available_unis)}
        except ServiceError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/universities/{university}/info", response_model=UniversityInfo)
    async def get_university_info(university: str):
        """Get comprehensive information about a university."""
        try:
            # Normalize university name
            normalized_uni = services.discovery_service.normalize_university_name(
                university
            )
            if not normalized_uni:
                available = services.discovery_service.get_available_universities()
                raise HTTPException(
                    status_code=404,
                    detail=f"University '{university}' not found. Available: {available}",
                )

            # Get university info
            info_data = services.discovery_service.get_university_info(normalized_uni)

            return UniversityInfo(
                university=info_data["university"],
                total_courses=info_data["total_courses"],
                total_subjects=info_data["total_subjects"],
                subjects=info_data["subjects"],
                data_metadata=info_data.get("data_metadata"),
                discovery_metadata=info_data.get("discovery_metadata"),
            )

        except HTTPException:
            raise
        except ServiceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting university info: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/universities/{university}/subjects", response_model=SubjectsResponse)
    async def get_university_subjects(university: str):
        """Get list of available subjects for a university."""
        try:
            # Validate and normalize university
            uni_enum = services.course_service.validate_university_string(university)

            # Get subjects
            subjects = services.course_service.get_subjects(uni_enum)
            subject_codes = sorted([s.code for s in subjects])

            return SubjectsResponse(
                university=uni_enum.value,
                subjects=subject_codes,
                total_subjects=len(subject_codes),
            )

        except UniversityNotSupportedError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ServiceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting subjects: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/universities/{university}/courses", response_model=CoursesResponse)
    async def get_university_courses(
        university: str,
        subject: Optional[str] = Query(None, description="Filter by subject code"),
        search: Optional[str] = Query(
            None, description="Search in course titles and descriptions"
        ),
        limit: int = Query(
            50, description="Maximum number of results to return", ge=0, le=1000
        ),
    ):
        """Get courses for a university with optional filtering."""
        try:
            # Validate and normalize university
            uni_enum = services.course_service.validate_university_string(university)

            # Get courses
            if search:
                # Use search functionality
                search_result = services.course_service.search_courses(
                    uni_enum, search, subject
                )
                courses = search_result.courses
                total_found = search_result.total_found
            else:
                # Get courses by subject
                courses = services.course_service.get_courses(uni_enum, subject)
                total_found = len(courses)

            # Apply limit
            limited_courses = courses[:limit] if limit > 0 else courses

            # Convert to API format
            course_data = []
            for course in limited_courses:
                course_data.append(
                    CourseData(
                        subject=course.subject_code,
                        code=course.course_code,
                        title=course.title,
                        credits=str(course.credits),
                        description=course.description,
                    )
                )

            return CoursesResponse(
                university=uni_enum.value,
                subject_filter=subject,
                query=search,
                total_courses=total_found,
                courses_shown=len(limited_courses),
                courses=course_data,
            )

        except UniversityNotSupportedError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ServiceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting courses: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get(
        "/universities/{university}/live-courses", response_model=LiveCoursesResponse
    )
    async def get_live_university_courses(
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
        try:
            # Validate and normalize university
            uni_enum = services.course_service.validate_university_string(university)

            # Check if university supports live data
            if uni_enum not in services.timetable_service.get_supported_universities():
                raise HTTPException(
                    status_code=400,
                    detail=f"Live course data is not supported for {university}",
                )

            # Convert term and year to term code (simplified - may need university-specific logic)
            term_mapping = {"winter": "01", "summer": "05", "fall": "09"}
            term_code = f"{year}{term_mapping.get(term.lower(), '01')}"

            # Parse subjects and course codes
            subject_list = [s.strip().upper() for s in subjects.split(",")]
            course_codes_list = None
            if course_codes:
                course_codes_list = [c.strip().upper() for c in course_codes.split(",")]

            # Get live course data
            result = services.timetable_service.get_live_courses(
                university=uni_enum,
                term_code=term_code,
                subjects=subject_list,
                course_codes=course_codes_list,
                max_courses_per_subject=limit,
            )

            # Enhance with ratings if requested
            if include_ratings:
                try:
                    result.courses = (
                        services.rating_service.inject_ratings_into_courses(
                            result.courses, uni_enum
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to inject ratings: {e}")

            # Convert to API format
            live_courses = []
            for course in result.courses:
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

                    # TODO: Extract RMP rating if available (would need to be added to CourseSection model)
                    rmp_rating = None

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
                        catalog_credits=(
                            float(course.credits) if course.credits else 0.0
                        ),
                        is_offered=course.is_offered,
                        sections_found=len(course.sections),
                        banner_title=course.title,  # Same as catalog for now
                        banner_credits=float(course.credits) if course.credits else 0.0,
                        sections=sections,
                        error=False,  # TODO: Add error tracking to core models
                        error_message="",
                    )
                )

            return LiveCoursesResponse(
                university=uni_enum.value,
                term_code=result.term_code,
                term_name=result.term_name,
                subjects_queried=result.subjects_queried,
                total_courses=result.total_courses,
                courses_offered=result.courses_offered,
                courses_with_errors=result.courses_with_errors,
                offering_rate_percent=result.offering_rate,
                courses=live_courses,
            )

        except HTTPException:
            raise
        except UniversityNotSupportedError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except LiveDataNotSupportedError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except TermNotAvailableError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ServiceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting live courses: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})

    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    return app
