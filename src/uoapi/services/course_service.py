"""
Course service implementation.

This module provides business logic for course-related operations,
abstracting the complexity of different university providers.
"""

from typing import List, Optional, Dict, Any
import logging

from uoapi.core import (
    CourseService,
    UniversityProvider,
    University,
    Subject,
    Course,
    SearchResult,
    UniversityNotSupportedError,
    CourseNotFoundError,
    SubjectNotFoundError,
    ServiceError,
)
from uoapi.universities import UOttawaProvider, CarletonProvider

logger = logging.getLogger(__name__)


class DefaultCourseService(CourseService):
    """
    Default implementation of the CourseService interface.

    This service manages university providers and provides a unified
    interface for course-related operations across all universities.
    """

    def __init__(self):
        self._providers: Dict[University, UniversityProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available university providers."""
        try:
            self._providers[University.UOTTAWA] = UOttawaProvider()
            logger.info("Initialized UOttawa provider")
        except Exception as e:
            logger.error(f"Failed to initialize UOttawa provider: {e}")

        try:
            self._providers[University.CARLETON] = CarletonProvider()
            logger.info("Initialized Carleton provider")
        except Exception as e:
            logger.error(f"Failed to initialize Carleton provider: {e}")

        logger.info(f"Initialized {len(self._providers)} university providers")

    def get_all_universities(self) -> List[University]:
        """Get all supported universities."""
        return list(self._providers.keys())

    def get_provider(self, university: University) -> UniversityProvider:
        """
        Get the provider for a specific university.

        Args:
            university: University to get provider for

        Returns:
            UniversityProvider instance

        Raises:
            UniversityNotSupportedError: If university is not supported
        """
        if university not in self._providers:
            supported = [u.value for u in self.get_all_universities()]
            raise UniversityNotSupportedError(university.value, supported)

        return self._providers[university]

    def get_subjects(self, university: University) -> List[Subject]:
        """
        Get all subjects for a university.

        Args:
            university: University to get subjects for

        Returns:
            List of Subject objects

        Raises:
            UniversityNotSupportedError: If university is not supported
        """
        provider = self.get_provider(university)
        try:
            subjects = provider.get_subjects()
            logger.info(f"Retrieved {len(subjects)} subjects for {university.value}")
            return subjects
        except Exception as e:
            logger.error(f"Failed to get subjects for {university.value}: {e}")
            raise ServiceError(
                f"Failed to get subjects for {university.value}: {str(e)}"
            )

    def get_subject_by_code(self, university: University, subject_code: str) -> Subject:
        """
        Get a specific subject by code.

        Args:
            university: University to search in
            subject_code: Subject code to find

        Returns:
            Subject object

        Raises:
            UniversityNotSupportedError: If university is not supported
            SubjectNotFoundError: If subject is not found
        """
        provider = self.get_provider(university)
        try:
            subject = provider.get_subject_by_code(subject_code)
            if subject is None:
                raise SubjectNotFoundError(subject_code, university.value)
            return subject
        except SubjectNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to get subject {subject_code} for {university.value}: {e}"
            )
            raise ServiceError(f"Failed to get subject {subject_code}: {str(e)}")

    def get_courses(
        self,
        university: University,
        subject_code: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[Course]:
        """
        Get courses with optional filtering.

        Args:
            university: University to get courses from
            subject_code: Optional subject code to filter by
            query: Optional search query

        Returns:
            List of Course objects

        Raises:
            UniversityNotSupportedError: If university is not supported
        """
        provider = self.get_provider(university)

        try:
            if query:
                # Use search functionality if query is provided
                search_result = provider.search_courses(query, subject_code)
                courses = search_result.courses
            else:
                # Just get courses by subject
                courses = provider.get_courses(subject_code)

            logger.info(f"Retrieved {len(courses)} courses for {university.value}")
            if subject_code:
                logger.debug(f"Filtered by subject: {subject_code}")
            if query:
                logger.debug(f"Searched with query: {query}")

            return courses

        except Exception as e:
            logger.error(f"Failed to get courses for {university.value}: {e}")
            raise ServiceError(f"Failed to get courses: {str(e)}")

    def get_course_by_code(self, university: University, course_code: str) -> Course:
        """
        Get a specific course by code.

        Args:
            university: University to search in
            course_code: Course code to find

        Returns:
            Course object

        Raises:
            UniversityNotSupportedError: If university is not supported
            CourseNotFoundError: If course is not found
        """
        provider = self.get_provider(university)
        try:
            course = provider.get_course_by_code(course_code)
            if course is None:
                raise CourseNotFoundError(course_code, university.value)
            return course
        except CourseNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to get course {course_code} for {university.value}: {e}"
            )
            raise ServiceError(f"Failed to get course {course_code}: {str(e)}")

    def search_courses(
        self, university: University, query: str, subject_code: Optional[str] = None
    ) -> SearchResult:
        """
        Search for courses.

        Args:
            university: University to search in
            query: Search query
            subject_code: Optional subject filter

        Returns:
            SearchResult with matching courses

        Raises:
            UniversityNotSupportedError: If university is not supported
        """
        provider = self.get_provider(university)
        try:
            result = provider.search_courses(query, subject_code)
            logger.info(
                f"Search for '{query}' in {university.value} found {result.total_found} courses"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to search courses in {university.value}: {e}")
            raise ServiceError(f"Failed to search courses: {str(e)}")

    def get_course_statistics(self, university: University) -> Dict[str, Any]:
        """
        Get statistics about courses for a university.

        Args:
            university: University to get statistics for

        Returns:
            Dictionary with course statistics
        """
        try:
            subjects = self.get_subjects(university)
            courses = self.get_courses(university)

            # Calculate statistics
            stats = {
                "university": university.value,
                "total_subjects": len(subjects),
                "total_courses": len(courses),
                "subjects_with_courses": len(
                    set(course.subject_code for course in courses)
                ),
                "average_courses_per_subject": len(courses) / max(1, len(subjects)),
            }

            # Course credit distribution
            credits_dist = {}
            for course in courses:
                credit_str = str(course.credits)
                credits_dist[credit_str] = credits_dist.get(credit_str, 0) + 1
            stats["credit_distribution"] = credits_dist

            # Subject distribution
            subject_dist = {}
            for course in courses:
                subject_dist[course.subject_code] = (
                    subject_dist.get(course.subject_code, 0) + 1
                )
            stats["subject_distribution"] = dict(
                sorted(subject_dist.items(), key=lambda x: x[1], reverse=True)[:10]
            )

            logger.info(f"Generated statistics for {university.value}")
            return stats

        except Exception as e:
            logger.error(f"Failed to get statistics for {university.value}: {e}")
            raise ServiceError(f"Failed to get course statistics: {str(e)}")

    def validate_university_string(self, university_str: str) -> University:
        """
        Validate and convert a university string to University enum.

        Args:
            university_str: String representation of university

        Returns:
            University enum value

        Raises:
            UniversityNotSupportedError: If university string is not valid
        """
        # Normalize the input
        normalized = (
            university_str.lower()
            .replace(" ", "")
            .replace("university", "")
            .replace("of", "")
        )

        # Map variations to standard values
        university_mapping = {
            "ottawa": University.UOTTAWA,
            "uottawa": University.UOTTAWA,
            "universityofottawa": University.UOTTAWA,
            "carleton": University.CARLETON,
            "carletonuniversity": University.CARLETON,
        }

        if normalized in university_mapping:
            return university_mapping[normalized]

        # Try direct enum value lookup
        try:
            return University(university_str.lower())
        except ValueError:
            pass

        supported = list(university_mapping.keys())
        raise UniversityNotSupportedError(university_str, supported)
