"""
Carleton University provider implementation.

This module wraps the existing Carleton discovery functionality
to implement the UniversityProvider interface.
"""

from typing import List, Optional, Tuple, Dict, Any
import logging
import time
from datetime import datetime

from uoapi.core import (
    University,
    Subject,
    Course,
    CourseSection,
    MeetingTime,
    SearchResult,
    DiscoveryResult,
    ProviderError,
    DataSourceError,
    NetworkError,
    LiveDataNotSupportedError,
)
from uoapi.universities.base import BaseUniversityProvider

# Import existing Carleton functionality
from uoapi.carleton.discovery import CarletonDiscovery
from uoapi.carleton.models import (
    Course as OldCourse,
    CourseSection as OldSection,
    MeetingTime as OldMeetingTime,
)

logger = logging.getLogger(__name__)


class CarletonProvider(BaseUniversityProvider):
    """
    Carleton University course data provider.

    This provider uses the existing Carleton discovery system to provide
    both catalog and live timetable data.
    """

    def __init__(self, max_workers: int = 4, cookie_file: Optional[str] = None):
        super().__init__()
        self._discovery = CarletonDiscovery(
            max_workers=max_workers, cookie_file=cookie_file
        )
        self._catalog_data = None
        self._subjects_from_catalog = None

    @property
    def university(self) -> University:
        return University.CARLETON

    @property
    def name(self) -> str:
        return "Carleton University"

    def get_subjects(self) -> List[Subject]:
        """
        Retrieve all available subjects from Carleton catalog.

        Uses the catalog data loaded by CarletonDiscovery.
        """
        if self._is_cache_valid() and self._subjects_cache:
            logger.debug("Using cached subjects data")
            return self._subjects_cache

        try:
            if not self._catalog_data:
                self._catalog_data = self._discovery.catalog_data

            # Extract unique subject codes from catalog
            subject_codes = set()
            for course_code in self._catalog_data.keys():
                # Extract subject code (letters at the start)
                import re

                match = re.match(r"^([A-Z]+)", course_code)
                if match:
                    subject_codes.add(match.group(1))

            # Create Subject objects
            subjects = []
            for code in sorted(subject_codes):
                # Try to get a full name from a course title, otherwise use code
                subject_name = self._get_subject_name_from_catalog(code)
                subjects.append(
                    Subject(
                        name=subject_name,
                        code=code,
                        university=self.university,
                        url=None,  # Carleton doesn't have subject-specific URLs
                    )
                )

            # Cache the results
            self._subjects_cache = subjects
            self._update_cache_timestamp()

            logger.info(f"Retrieved {len(subjects)} subjects from Carleton catalog")
            return subjects

        except Exception as e:
            logger.error(f"Failed to get subjects: {e}")
            raise DataSourceError(
                f"Failed to retrieve subjects from Carleton: {str(e)}"
            )

    def _get_subject_name_from_catalog(self, subject_code: str) -> str:
        """Try to infer subject name from catalog data."""
        # This is a simplified implementation - could be improved with a mapping
        subject_names = {
            "COMP": "Computer Science",
            "MATH": "Mathematics",
            "PHYS": "Physics",
            "CHEM": "Chemistry",
            "BIOL": "Biology",
            "ECON": "Economics",
            "PSYC": "Psychology",
            "HIST": "History",
            "ENGL": "English",
            "PHIL": "Philosophy",
            # Add more mappings as needed
        }
        return subject_names.get(subject_code, subject_code)

    def get_courses(self, subject_code: Optional[str] = None) -> List[Course]:
        """
        Retrieve courses from Carleton catalog.

        Args:
            subject_code: Optional subject code to filter by

        Returns:
            List of Course objects from catalog data (no live sections)
        """
        if self._is_cache_valid() and self._courses_cache:
            logger.debug("Using cached courses data")
            courses = self._courses_cache
        else:
            logger.info("Loading courses from Carleton catalog")
            courses = self._load_catalog_courses()
            self._courses_cache = courses
            self._update_cache_timestamp()

        # Filter by subject code if provided
        if subject_code:
            normalized_code = self._normalize_subject_code(subject_code)
            filtered_courses = [
                course for course in courses if course.subject_code == normalized_code
            ]
            logger.info(
                f"Filtered to {len(filtered_courses)} courses for subject {subject_code}"
            )
            return filtered_courses

        return courses

    def _load_catalog_courses(self) -> List[Course]:
        """
        Load courses from the Carleton catalog data.

        Returns:
            List of Course objects
        """
        if not self._catalog_data:
            self._catalog_data = self._discovery.catalog_data

        courses = []
        for subject_code, subject_courses in self._catalog_data.items():
            for course_data in subject_courses:
                try:
                    course_code = course_data.get("code", "")
                    course = Course(
                        course_code=self._normalize_course_code(course_code),
                        subject_code=self._extract_subject_code(course_code),
                        course_number=self._extract_course_number(course_code),
                        title=course_data.get("title", ""),
                        description=course_data.get("description", ""),
                        credits=course_data.get("credits", 0.0),
                        university=self.university,
                        components=[],  # Catalog data doesn't include components
                        prerequisites="",  # Convert prerequisite list to text if needed
                        prerequisite_courses=course_data.get("prerequisites", []),
                        sections=[],  # Catalog data doesn't include live sections
                        is_offered=True,  # Assume offered if in catalog
                    )
                    courses.append(course)
                except Exception as e:
                    logger.warning(f"Failed to create course object for {course_code}: {e}")
                    continue

        logger.info(f"Loaded {len(courses)} courses from Carleton catalog")
        return courses

    def supports_live_data(self) -> bool:
        """Carleton provider supports live timetable data."""
        return True

    def get_available_terms(self) -> List[Tuple[str, str]]:
        """
        Get available terms for live data from Carleton.

        Returns:
            List of (term_code, term_name) tuples
        """
        try:
            return self._discovery.get_available_terms()
        except Exception as e:
            logger.error(f"Failed to get available terms: {e}")
            raise DataSourceError(
                f"Failed to get available terms from Carleton: {str(e)}"
            )

    def discover_courses(
        self,
        term_code: str,
        subjects: Optional[List[str]] = None,
        course_codes: Optional[List[str]] = None,
        max_courses_per_subject: int = 50,
    ) -> DiscoveryResult:
        """
        Discover live course data for a specific term.

        Args:
            term_code: Term identifier
            subjects: Optional list of subject codes to query
            course_codes: Optional list of specific course codes
            max_courses_per_subject: Maximum courses to query per subject

        Returns:
            DiscoveryResult with live course information
        """
        try:
            start_time = time.time()

            # Use the existing discovery system
            courses = self._discovery.discover_courses(
                term_code,
                subjects=subjects,
                max_courses_per_subject=max_courses_per_subject,
            )

            # Convert old format to new format
            converted_courses = []
            for old_course in courses:
                converted_course = self._convert_old_course_to_new(old_course)
                converted_courses.append(converted_course)

            # Filter by specific course codes if provided
            if course_codes:
                normalized_codes = [
                    self._normalize_course_code(code) for code in course_codes
                ]
                filtered_courses = [
                    course
                    for course in converted_courses
                    if course.course_code in normalized_codes
                ]
                converted_courses = filtered_courses

            processing_time = time.time() - start_time

            # Calculate statistics
            offered_courses = [c for c in converted_courses if c.is_offered]
            error_courses = [
                c
                for c in converted_courses
                if any("error" in str(s.notes).lower() for s in c.sections)
            ]

            # Get term name from available terms
            term_name = term_code
            try:
                available_terms = self.get_available_terms()
                for code, name in available_terms:
                    if code == term_code:
                        term_name = name
                        break
            except Exception:
                pass

            return DiscoveryResult(
                term_code=term_code,
                term_name=term_name,
                university=self.university,
                subjects_queried=subjects or [],
                total_courses=len(converted_courses),
                courses_offered=len(offered_courses),
                courses_with_errors=len(error_courses),
                offering_rate=len(offered_courses)
                / max(1, len(converted_courses))
                * 100,
                processing_time=processing_time,
                courses=converted_courses,
                errors=[],
            )

        except Exception as e:
            logger.error(f"Failed to discover courses: {e}")
            raise DataSourceError(f"Failed to discover courses from Carleton: {str(e)}")

    def discover_single_course(
        self, 
        term_code: str, 
        course_code: str
    ) -> Optional[Course]:
        """
        Discover live data for a single specific course.
        
        This method directly queries Carleton Banner for a specific course
        without going through the bulk discovery process.
        
        Args:
            term_code: Term identifier (e.g., "202530")
            course_code: Full course code (e.g., "COMP1005")
            
        Returns:
            Course object with live sections if found, None otherwise
        """
        try:
            # Extract subject and course number
            subject_code = self._extract_subject_code(course_code)
            course_number = self._extract_course_number(course_code)
            
            logger.info(f"Searching for single course: {course_code} ({subject_code} {course_number})")
            
            # Get available terms to validate session_id
            available_terms = self._discovery.get_available_terms()
            session_id = None
            for code, name in available_terms:
                if code == term_code:
                    # For Carleton, session_id is typically the same as term_code
                    session_id = code
                    break
            
            if not session_id:
                logger.error(f"Term {term_code} not found in available terms")
                return None
            
            # Use the direct search_course method
            old_course = self._discovery.search_course(
                term_code=term_code,
                session_id=session_id,
                subject_code=subject_code,
                course_number=course_number,
                course_title="",  # Let Banner search by code
                course_credits=0.0
            )
            
            if old_course:
                # Convert to new format
                return self._convert_old_course_to_new(old_course)
            
            logger.info(f"Course {course_code} not found for term {term_code}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to discover single course {course_code}: {e}")
            raise DataSourceError(f"Failed to discover course {course_code}: {str(e)}")

    def _convert_old_course_to_new(self, old_course: OldCourse) -> Course:
        """
        Convert old Carleton course format to new unified Course model.

        Args:
            old_course: Course in old format

        Returns:
            Course object in new format
        """
        # Convert sections
        sections = []
        for old_section in old_course.sections:
            # Convert meeting times
            meeting_times = []
            for old_mt in old_section.meeting_times:
                meeting_times.append(
                    MeetingTime(
                        start_date=old_mt.start_date,
                        end_date=old_mt.end_date,
                        days=old_mt.days,
                        start_time=old_mt.start_time,
                        end_time=old_mt.end_time,
                    )
                )

            sections.append(
                CourseSection(
                    crn=old_section.crn,
                    section=old_section.section,
                    status=old_section.status,
                    credits=old_section.credits,
                    schedule_type=old_section.schedule_type,
                    instructor=old_section.instructor,
                    meeting_times=meeting_times,
                    notes=old_section.notes,
                    capacity=None,  # Not available in old format
                    enrolled=None,
                    remaining=None,
                )
            )

        return Course(
            course_code=self._normalize_course_code(old_course.course_code),
            subject_code=old_course.subject_code,
            course_number=old_course.course_number,
            title=old_course.catalog_title,
            description="",  # Not available in discovery data
            credits=old_course.catalog_credits,
            university=self.university,
            components=[],
            prerequisites="",
            prerequisite_courses=[],
            sections=sections,
            is_offered=old_course.is_offered,
            last_updated=datetime.now(),
        )
