"""
Base implementation for university providers.

This module provides a base class that implements common functionality
shared across all university providers.
"""

from abc import ABC
from typing import List, Optional, Dict, Any
from datetime import datetime

from uoapi.core import (
    UniversityProvider,
    University,
    Course,
    Subject,
    SearchResult,
    DiscoveryResult,
    ProviderError,
)


class BaseUniversityProvider(UniversityProvider, ABC):
    """
    Base implementation of UniversityProvider interface.

    This class provides common functionality that can be shared
    across different university implementations.
    """

    def __init__(self):
        self._subjects_cache: Optional[List[Subject]] = None
        self._courses_cache: Optional[List[Course]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 3600  # 1 hour default cache TTL

    def _is_cache_valid(self) -> bool:
        """Check if the current cache is still valid."""
        if self._cache_timestamp is None:
            return False

        elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
        return elapsed < self._cache_ttl_seconds

    def _clear_cache(self):
        """Clear all cached data."""
        self._subjects_cache = None
        self._courses_cache = None
        self._cache_timestamp = None

    def _update_cache_timestamp(self):
        """Update the cache timestamp to now."""
        self._cache_timestamp = datetime.now()

    def get_subject_by_code(self, code: str) -> Optional[Subject]:
        """
        Default implementation that searches through all subjects.

        Subclasses can override this for more efficient lookups.
        """
        subjects = self.get_subjects()
        for subject in subjects:
            if subject.code.upper() == code.upper():
                return subject
        return None

    def get_course_by_code(self, course_code: str) -> Optional[Course]:
        """
        Default implementation that searches through all courses.

        Subclasses can override this for more efficient lookups.
        """
        courses = self.get_courses()
        normalized_code = course_code.upper().replace(" ", "")

        for course in courses:
            if course.course_code.upper().replace(" ", "") == normalized_code:
                return course
        return None

    def search_courses(
        self, query: str, subject_code: Optional[str] = None
    ) -> SearchResult:
        """
        Default implementation of course search.

        Searches through course codes, titles, and descriptions.
        Subclasses can override for more sophisticated search.
        """
        query_lower = query.lower()
        courses = self.get_courses(subject_code)

        matching_courses = []
        for course in courses:
            # Search in course code, title, and description
            searchable_text = (
                f"{course.course_code} {course.title} {course.description}".lower()
            )
            if query_lower in searchable_text:
                matching_courses.append(course)

        return SearchResult(
            university=self.university,
            query=query,
            subject_filter=subject_code,
            total_found=len(matching_courses),
            courses=matching_courses,
            metadata={
                "search_method": "default_text_search",
                "searched_fields": ["course_code", "title", "description"],
            },
        )

    def _normalize_course_code(self, code: str) -> str:
        """Normalize course code format for consistency."""
        return code.upper().replace(" ", "")

    def _normalize_subject_code(self, code: str) -> str:
        """Normalize subject code format for consistency."""
        return code.upper()

    def _extract_subject_code(self, course_code: str) -> str:
        """Extract subject code from a full course code."""
        # Default implementation assumes format like "CSI3140" or "COMP 1005"
        import re

        match = re.match(r"^([A-Z]+)", course_code.replace(" ", ""))
        if match:
            return match.group(1)
        return course_code  # Fallback

    def _extract_course_number(self, course_code: str) -> str:
        """Extract course number from a full course code."""
        # Default implementation assumes format like "CSI3140" or "COMP 1005"
        import re

        match = re.search(r"([0-9]+[A-Z]*)$", course_code.replace(" ", ""))
        if match:
            return match.group(1)
        return course_code  # Fallback

    def _validate_course_data(self, course_dict: Dict[str, Any]) -> bool:
        """Validate that course data has required fields."""
        required_fields = ["course_code", "title"]
        return all(
            field in course_dict and course_dict[field] for field in required_fields
        )

    def _create_course_from_dict(self, data: Dict[str, Any]) -> Course:
        """Create a Course object from dictionary data."""
        if not self._validate_course_data(data):
            raise ProviderError(f"Invalid course data: {data}")

        course_code = self._normalize_course_code(data["course_code"])

        return Course(
            course_code=course_code,
            subject_code=self._extract_subject_code(course_code),
            course_number=self._extract_course_number(course_code),
            title=data.get("title", ""),
            description=data.get("description", ""),
            credits=data.get("credits", 0),
            university=self.university,
            components=data.get("components", []),
            prerequisites=data.get("prerequisites", ""),
            prerequisite_courses=data.get("prerequisite_courses", []),
            is_offered=data.get("is_offered", True),
            last_updated=datetime.now(),
        )

    def discover_single_course(
        self, 
        term_code: str, 
        course_code: str
    ) -> Optional[Course]:
        """
        Discover live data for a single specific course.
        
        This method should be implemented by providers that support
        more efficient single-course queries. Base implementation
        falls back to using discover_courses with filtering.
        
        Args:
            term_code: Term identifier
            course_code: Full course code
            
        Returns:
            Course object with live sections if found, None otherwise
        """
        # Default implementation: use discover_courses as fallback
        subject_code = self._extract_subject_code(course_code)
        result = self.discover_courses(
            term_code=term_code,
            subjects=[subject_code],
            course_codes=[course_code],
            max_courses_per_subject=100
        )
        
        return result.courses[0] if result.courses else None
