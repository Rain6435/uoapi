"""
Abstract interfaces for university data providers.

This module defines the contracts that all university implementations
must follow, ensuring consistent behavior across different institutions.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from .models import Course, Subject, SearchResult, DiscoveryResult, University


class UniversityProvider(ABC):
    """
    Abstract base class for university data providers.

    This interface defines the methods that all university implementations
    must implement to provide course and subject information.
    """

    @property
    @abstractmethod
    def university(self) -> University:
        """Return the university this provider represents."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable name of the university."""
        pass

    @abstractmethod
    def get_subjects(self) -> List[Subject]:
        """
        Retrieve all available subjects/departments.

        Returns:
            List of Subject objects representing all available departments

        Raises:
            ProviderError: If subjects cannot be retrieved
        """
        pass

    @abstractmethod
    def get_subject_by_code(self, code: str) -> Optional[Subject]:
        """
        Retrieve a specific subject by its code.

        Args:
            code: Subject code (e.g., "CSI", "COMP")

        Returns:
            Subject object if found, None otherwise

        Raises:
            ProviderError: If subject lookup fails
        """
        pass

    @abstractmethod
    def get_courses(self, subject_code: Optional[str] = None) -> List[Course]:
        """
        Retrieve courses, optionally filtered by subject.

        Args:
            subject_code: Optional subject code to filter by

        Returns:
            List of Course objects

        Raises:
            ProviderError: If courses cannot be retrieved
        """
        pass

    @abstractmethod
    def get_course_by_code(self, course_code: str) -> Optional[Course]:
        """
        Retrieve a specific course by its code.

        Args:
            course_code: Course code (e.g., "CSI3140", "COMP 1005")

        Returns:
            Course object if found, None otherwise

        Raises:
            ProviderError: If course lookup fails
        """
        pass

    @abstractmethod
    def search_courses(
        self, query: str, subject_code: Optional[str] = None
    ) -> SearchResult:
        """
        Search for courses by title, description, or code.

        Args:
            query: Search query string
            subject_code: Optional subject code to limit search

        Returns:
            SearchResult containing matching courses

        Raises:
            ProviderError: If search fails
        """
        pass

    def supports_live_data(self) -> bool:
        """
        Check if this provider supports live timetable data.

        Returns:
            True if live data is supported, False otherwise
        """
        return False

    def get_available_terms(self) -> List[Tuple[str, str]]:
        """
        Get available terms for live data.

        Returns:
            List of (term_code, term_name) tuples

        Raises:
            NotImplementedError: If live data is not supported
        """
        raise NotImplementedError("Live data not supported by this provider")

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

        Raises:
            NotImplementedError: If live data is not supported
        """
        raise NotImplementedError("Live data discovery not supported by this provider")


class CourseService(ABC):
    """
    Abstract interface for course-related business operations.

    This service layer abstracts business logic from data access,
    allowing different implementations and easier testing.
    """

    @abstractmethod
    def get_all_universities(self) -> List[University]:
        """Get all supported universities."""
        pass

    @abstractmethod
    def get_provider(self, university: University) -> UniversityProvider:
        """Get the provider for a specific university."""
        pass

    @abstractmethod
    def get_subjects(self, university: University) -> List[Subject]:
        """Get all subjects for a university."""
        pass

    @abstractmethod
    def get_courses(
        self,
        university: University,
        subject_code: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[Course]:
        """Get courses with optional filtering."""
        pass

    @abstractmethod
    def search_courses(
        self, university: University, query: str, subject_code: Optional[str] = None
    ) -> SearchResult:
        """Search for courses."""
        pass


class TimetableService(ABC):
    """
    Abstract interface for timetable-related operations.
    """

    @abstractmethod
    def get_available_terms(self, university: University) -> List[Tuple[str, str]]:
        """Get available terms for a university."""
        pass

    @abstractmethod
    def get_live_courses(
        self,
        university: University,
        term_code: str,
        subjects: List[str],
        course_codes: Optional[List[str]] = None,
        max_courses_per_subject: int = 50,
    ) -> DiscoveryResult:
        """Get live course data for a term."""
        pass


class RatingService(ABC):
    """
    Abstract interface for professor rating operations.
    """

    @abstractmethod
    def get_instructor_rating(
        self, instructor_name: str, university: University
    ) -> Optional[Dict[str, Any]]:
        """Get rating for a specific instructor."""
        pass

    @abstractmethod
    def get_batch_ratings(
        self,
        instructors: List[Tuple[str, str]],  # (first_name, last_name)
        university: University,
    ) -> Dict[str, Dict[str, Any]]:
        """Get ratings for multiple instructors."""
        pass

    @abstractmethod
    def inject_ratings_into_courses(
        self, courses: List[Course], university: University
    ) -> List[Course]:
        """Add rating information to course sections."""
        pass


class DiscoveryService(ABC):
    """
    Abstract interface for data discovery and asset management.
    """

    @abstractmethod
    def get_available_universities(self) -> List[str]:
        """Get list of universities with available data."""
        pass

    @abstractmethod
    def get_course_data(self, university: str) -> Dict[str, Any]:
        """Get course data for a university."""
        pass

    @abstractmethod
    def get_course_count(self, university: str) -> int:
        """Get total course count for a university."""
        pass

    @abstractmethod
    def get_subjects_list(self, university: str) -> List[str]:
        """Get list of subject codes for a university."""
        pass

    @abstractmethod
    def search_courses(
        self,
        university: str,
        subject_code: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search courses in stored data."""
        pass
