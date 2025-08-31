"""
University of Ottawa provider implementation.

This module wraps the existing UOttawa scraping functionality
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
)
from uoapi.universities.base import BaseUniversityProvider

# Import existing functionality
from uoapi.course.course_info import scrape_subjects, get_courses
from uoapi.course.models import Subject as OldSubject, Course as OldCourse

# Import for catalog data loading
from uoapi.discovery.discovery_service import get_courses_data

# Import timetable functionality for live data
from uoapi.timetable.query_timetable import (
    TimetableQuery,
    extract_timetable,
    parse_available,
)

logger = logging.getLogger(__name__)


class UOttawaProvider(BaseUniversityProvider):
    """
    University of Ottawa course data provider.

    This provider scrapes course information from the University of Ottawa
    course catalog website and provides live timetable data.
    """

    def __init__(self):
        super().__init__()
        self._base_url = "https://catalogue.uottawa.ca/en/courses/"
        self._timetable_query = None

    @property
    def university(self) -> University:
        return University.UOTTAWA

    @property
    def name(self) -> str:
        return "University of Ottawa"

    def get_subjects(self) -> List[Subject]:
        """
        Retrieve all available subjects from UOttawa catalog.

        Uses cached data if available and valid.
        """
        if self._is_cache_valid() and self._subjects_cache:
            logger.debug("Using cached subjects data")
            return self._subjects_cache

        try:
            logger.info("Scraping subjects from UOttawa catalog")
            raw_subjects = scrape_subjects(self._base_url)

            subjects = []
            for subject_data in raw_subjects:
                # Convert from old Subject model to new unified model
                subjects.append(
                    Subject(
                        name=subject_data["subject"],
                        code=subject_data["subject_code"],
                        university=self.university,
                        url=subject_data.get("link"),
                    )
                )

            # Cache the results
            self._subjects_cache = subjects
            self._update_cache_timestamp()

            logger.info(f"Successfully scraped {len(subjects)} subjects")
            return subjects

        except Exception as e:
            logger.error(f"Failed to scrape subjects: {e}")
            raise DataSourceError(f"Failed to retrieve subjects from UOttawa: {str(e)}")

    def get_courses(self, subject_code: Optional[str] = None) -> List[Course]:
        """
        Retrieve courses from UOttawa catalog.

        Args:
            subject_code: Optional subject code to filter by

        Returns:
            List of Course objects
        """
        if self._is_cache_valid() and self._courses_cache:
            logger.debug("Using cached courses data")
            courses = self._courses_cache
        else:
            logger.info("Loading courses from UOttawa catalog data")
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
        Load courses from the UOttawa catalog data JSON files.

        Returns:
            List of Course objects
        """
        try:
            # Load catalog data using discovery service
            catalog_data = get_courses_data("uottawa")
            departments = catalog_data.get("departments", {})
            
            courses = []
            for dept_name, dept_info in departments.items():
                dept_code = dept_info.get("department_code", "")
                dept_courses = dept_info.get("courses", [])
                
                for course_data in dept_courses:
                    try:
                        course_code = f"{course_data.get('subject_code', dept_code)} {course_data.get('course_code', '')}"
                        
                        # Handle prerequisites - can be list or nested object
                        prereqs = course_data.get("prerequisites", [])
                        prerequisite_courses = []
                        if isinstance(prereqs, list):
                            # Simple format: ["COURSE1", "COURSE2"]
                            prerequisite_courses = prereqs
                        elif isinstance(prereqs, dict) and "prerequisites" in prereqs:
                            # Complex format: {"prerequisites": {"required": [{"course": "..."}]}}
                            nested_prereqs = prereqs.get("prerequisites", {})
                            required = nested_prereqs.get("required", [])
                            prerequisite_courses = [item.get("course", "") for item in required if isinstance(item, dict) and "course" in item]
                        
                        course = Course(
                            course_code=self._normalize_course_code(course_code),
                            subject_code=course_data.get('subject_code', dept_code),
                            course_number=course_data.get('course_code', ''),
                            title=course_data.get("title", ""),
                            description=course_data.get("description", ""),
                            credits=course_data.get("credits", "0"),
                            university=self.university,
                            components=course_data.get("course_components", []),
                            prerequisites="",  # UOttawa doesn't have text prerequisites in catalog
                            prerequisite_courses=prerequisite_courses,
                            sections=[],  # Catalog data doesn't include live sections
                            is_offered=True,  # Assume offered if in catalog
                        )
                        courses.append(course)
                    except Exception as e:
                        logger.warning(f"Failed to create course object for {course_code}: {e}")
                        continue
            
            logger.info(f"Loaded {len(courses)} courses from UOttawa catalog")
            return courses
            
        except Exception as e:
            logger.error(f"Failed to load catalog data: {e}")
            # Fall back to scraping if catalog loading fails
            logger.info("Falling back to scraping courses from UOttawa catalog")
            return self._scrape_all_courses()

    def _scrape_all_courses(self) -> List[Course]:
        """
        Scrape all courses from all subjects.

        Returns:
            List of Course objects
        """
        all_courses = []
        subjects = self.get_subjects()

        for subject in subjects:
            if not subject.url:
                logger.warning(f"No URL available for subject {subject.code}")
                continue

            try:
                logger.debug(f"Scraping courses for subject {subject.code}")
                raw_courses = list(get_courses(subject.url))

                for course_data in raw_courses:
                    try:
                        course = self._convert_old_course_to_new(course_data, subject)
                        all_courses.append(course)
                    except Exception as e:
                        logger.warning(
                            f"Failed to convert course {course_data.get('course_code', 'unknown')}: {e}"
                        )
                        continue

                logger.debug(f"Scraped {len(raw_courses)} courses for {subject.code}")

            except Exception as e:
                logger.error(
                    f"Failed to scrape courses for subject {subject.code}: {e}"
                )
                continue

        logger.info(f"Successfully scraped {len(all_courses)} total courses")
        return all_courses

    def _convert_old_course_to_new(
        self, old_course_data: Dict[str, Any], subject: Subject
    ) -> Course:
        """
        Convert old course data format to new unified Course model.

        Args:
            old_course_data: Course data in old format
            subject: Subject this course belongs to

        Returns:
            Course object in new format
        """
        course_code = self._normalize_course_code(old_course_data["course_code"])

        return Course(
            course_code=course_code,
            subject_code=subject.code,
            course_number=self._extract_course_number(course_code),
            title=old_course_data.get("title", ""),
            description=old_course_data.get("description", ""),
            credits=old_course_data.get("credits", 0),
            university=self.university,
            components=old_course_data.get("course_components", []),
            prerequisites="",  # UOttawa doesn't have text prerequisites in catalog
            prerequisite_courses=old_course_data.get("prerequisites", []),
            sections=[],  # UOttawa provider doesn't have live section data
            is_offered=True,  # Assume offered if in catalog
        )

    def supports_live_data(self) -> bool:
        """UOttawa provider supports live timetable data."""
        return True

    def get_available_terms(self) -> List[Tuple[str, str]]:
        """
        Get available terms for live data from UOttawa.

        Returns:
            List of (term_code, term_name) tuples
        """
        try:
            # Initialize timetable query if not already done
            if self._timetable_query is None:
                self._timetable_query = TimetableQuery()

            with self._timetable_query as messages:
                available_terms = []

                # Parse available terms from the timetable system
                for term_code, term_name in self._timetable_query.available.items():
                    parsed_term = parse_available(term_code)
                    if parsed_term:
                        # Format term code as expected by the system
                        formatted_code = f"{parsed_term['year']}{parsed_term['term']}"
                        available_terms.append((formatted_code, term_name))

                logger.info(f"Found {len(available_terms)} available terms")
                return available_terms

        except Exception as e:
            logger.error(f"Failed to get available terms: {e}")
            raise DataSourceError(
                f"Failed to get available terms from UOttawa: {str(e)}"
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
            term_code: Term identifier (e.g., "2025fall", "2025winter")
            subjects: Optional list of subject codes to query
            course_codes: Optional list of specific course codes
            max_courses_per_subject: Maximum courses to query per subject

        Returns:
            DiscoveryResult with live course information
        """
        start_time = time.time()

        try:
            # Parse term code to extract year and term
            if len(term_code) < 8:  # Should be like "2025fall"
                raise ValueError(f"Invalid term code format: {term_code}")

            year = term_code[:4]
            term = term_code[4:]

            # Validate term
            valid_terms = ["fall", "winter", "summer"]
            if term.lower() not in valid_terms:
                raise ValueError(f"Invalid term: {term}. Must be one of {valid_terms}")

            # Initialize timetable query if not already done
            if self._timetable_query is None:
                self._timetable_query = TimetableQuery()

            # Determine what to query
            if subjects:
                query_subjects = [s.upper() for s in subjects]
            else:
                # Get all available subjects if none specified
                query_subjects = [s.code for s in self.get_subjects()]

            if course_codes:
                # If specific course codes provided, extract subjects from them
                course_subjects = set()
                for code in course_codes:
                    # Extract alphabetic characters as subject code (e.g., "CSI" from "CSI3140")
                    subject = "".join(c for c in code if c.isalpha()).upper()
                    if subject:
                        course_subjects.add(subject)
                if course_subjects:
                    query_subjects = list(course_subjects)

            # Limit subjects to avoid overwhelming the system
            query_subjects = query_subjects[:max_courses_per_subject]

            all_courses = []
            total_courses = 0
            courses_offered = 0
            courses_with_errors = 0
            errors = []

            with self._timetable_query as messages:
                for subject_code in query_subjects:
                    logger.info(
                        f"Querying live data for {subject_code} in {term} {year}"
                    )

                    try:
                        # Query the timetable system
                        response, query_messages = self._timetable_query(
                            year, term, subject_code, ""
                        )

                        if response:
                            # Extract course data from response
                            extracted_courses = list(
                                extract_timetable(response, year, term, log=True)
                            )

                            for course_data in extracted_courses:
                                total_courses += 1

                                try:
                                    # Convert to unified Course model
                                    course = self._convert_timetable_course_to_new(
                                        course_data, year, term
                                    )
                                    all_courses.append(course)

                                    if course.is_offered:
                                        courses_offered += 1

                                except Exception as e:
                                    courses_with_errors += 1
                                    error_msg = f"Failed to convert course {course_data.get('course_code', 'unknown')}: {e}"
                                    logger.warning(error_msg)
                                    errors.append(error_msg)
                        else:
                            logger.warning(f"No response for {subject_code}")

                    except Exception as e:
                        courses_with_errors += 1
                        error_msg = f"Failed to query {subject_code}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)

                # Add any messages from the timetable query
                for msg in messages:
                    if msg.get("type") == "error":
                        errors.append(msg.get("message", "Unknown error"))

            # Calculate offering rate
            offering_rate = (
                (courses_offered / total_courses * 100) if total_courses > 0 else 0.0
            )
            processing_time = time.time() - start_time

            # Get term name
            term_names = {"fall": "Fall", "winter": "Winter", "summer": "Summer"}
            term_name = f"{term_names.get(term.lower(), term.title())} {year}"

            # Filter by specific course codes if requested
            if course_codes:
                requested_codes = set(code.upper() for code in course_codes)
                filtered_courses = []
                for course in all_courses:
                    if course.course_code in requested_codes:
                        filtered_courses.append(course)

                # Update stats for filtered results
                all_courses = filtered_courses
                courses_offered = sum(1 for c in all_courses if c.is_offered)
                total_courses = len(all_courses)
                offering_rate = (
                    (courses_offered / total_courses * 100)
                    if total_courses > 0
                    else 0.0
                )

            logger.info(
                f"Discovery completed: {courses_offered}/{total_courses} courses offered ({offering_rate:.1f}%)"
            )

            return DiscoveryResult(
                term_code=term_code,
                term_name=term_name,
                university=self.university,
                subjects_queried=query_subjects,
                total_courses=total_courses,
                courses_offered=courses_offered,
                courses_with_errors=courses_with_errors,
                offering_rate=offering_rate,
                processing_time=processing_time,
                courses=all_courses,
                errors=errors,
            )

        except Exception as e:
            logger.error(f"Failed to discover courses: {e}")
            raise DataSourceError(f"Failed to discover courses from UOttawa: {str(e)}")

    def _convert_timetable_course_to_new(
        self, timetable_course: Dict[str, Any], year: str, term: str
    ) -> Course:
        """
        Convert timetable course data to unified Course model.

        Args:
            timetable_course: Course data from timetable system
            year: Year of the term
            term: Term name

        Returns:
            Course object in new format
        """
        # Extract course information
        subject_code = timetable_course.get("subject_code", "").upper()
        course_code = timetable_course.get("course_code", "").upper()
        course_name = timetable_course.get("course_name", "")

        # Convert sections - create separate section for each component type
        sections = []
        for section_data in timetable_course.get("sections", []):
            try:
                # Each section_data can contain multiple components (LEC, LAB, TUT)
                # We need to create a separate CourseSection for each component
                component_sections = self._convert_timetable_section_to_new(section_data)
                sections.extend(component_sections)
            except Exception as e:
                logger.warning(
                    f"Failed to convert section {section_data.get('label', 'unknown')}: {e}"
                )
                continue

        # Determine if course is offered
        is_offered = len(sections) > 0

        # Create full course code (subject + number) if not already combined
        full_course_code = course_code
        if subject_code and not course_code.startswith(subject_code):
            full_course_code = f"{subject_code}{course_code}"

        return Course(
            course_code=full_course_code,
            subject_code=subject_code,
            course_number=self._extract_course_number(course_code),
            title=course_name,
            description="",  # Not available in timetable data
            credits=0,  # Not available in timetable data
            university=self.university,
            components=[],  # Not available in timetable data
            prerequisites="",  # Not available in timetable data
            prerequisite_courses=[],  # Not available in timetable data
            sections=sections,
            is_offered=is_offered,
            last_updated=datetime.now(),
        )

    def _convert_timetable_section_to_new(
        self, section_data: Dict[str, Any]
    ) -> List[CourseSection]:
        """
        Convert timetable section data to unified CourseSection models.
        
        Each component (LEC, LAB, TUT) becomes a separate CourseSection.

        Args:
            section_data: Section data from timetable system

        Returns:
            List of CourseSection objects (one per component type)
        """
        # Extract section information
        label = section_data.get("label", "")
        components = section_data.get("components", [])

        sections = []
        
        # Create a separate section for each component
        for component in components:
            try:
                # Extract component information
                component_type = component.get("type", "Lecture")
                section_id = component.get("section_id", "")
                
                # Generate a unique section identifier combining base section and component
                # e.g., "A00" for LEC, "A01" for LAB, etc.
                full_section_id = section_id if section_id else label
                
                # Extract CRN (use component-specific if available)
                crn = component.get("crn", f"{label.replace(' ', '')}")
                
                # Extract status
                status = component.get("status", "Unknown")
                
                # Extract instructor
                instructor = component.get("instructor", "TBA")
                
                # Create single meeting time for this component
                meeting_time = MeetingTime(
                    start_date=component.get("start_date", ""),
                    end_date=component.get("end_date", ""),
                    days=component.get("day", ""),
                    start_time=component.get("start_time", ""),
                    end_time=component.get("end_time", ""),
                )
                
                # Extract notes
                notes = []
                description = component.get("description", "")
                if description:
                    notes.append(description)
                
                section = CourseSection(
                    crn=crn,
                    section=full_section_id,
                    status=status,
                    credits=0.0,  # Not available in timetable data
                    schedule_type=component_type,
                    instructor=instructor,
                    meeting_times=[meeting_time],
                    notes=notes,
                    capacity=None,  # Not available in timetable data
                    enrolled=None,
                    remaining=None,
                )
                sections.append(section)
                
            except Exception as e:
                logger.warning(f"Failed to convert component in {label}: {e}")
                continue
        
        return sections
