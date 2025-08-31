"""
Timetable service implementation.

This module provides business logic for timetable and live course
data operations across different universities.
"""

from typing import List, Optional, Tuple
import logging

from uoapi.core import (
    TimetableService,
    University,
    DiscoveryResult,
    UniversityNotSupportedError,
    TermNotAvailableError,
    LiveDataNotSupportedError,
    ServiceError,
)
from uoapi.services.course_service import DefaultCourseService

logger = logging.getLogger(__name__)


class DefaultTimetableService(TimetableService):
    """
    Default implementation of the TimetableService interface.

    This service provides access to live timetable data from universities
    that support it, with appropriate error handling for those that don't.
    """

    def __init__(self, course_service: Optional[DefaultCourseService] = None):
        self._course_service = course_service or DefaultCourseService()

    def get_available_terms(self, university: University) -> List[Tuple[str, str]]:
        """
        Get available terms for a university.

        Args:
            university: University to get terms for

        Returns:
            List of (term_code, term_name) tuples

        Raises:
            UniversityNotSupportedError: If university is not supported
            LiveDataNotSupportedError: If university doesn't support live data
        """
        provider = self._course_service.get_provider(university)

        if not provider.supports_live_data():
            raise LiveDataNotSupportedError(university.value)

        try:
            terms = provider.get_available_terms()
            logger.info(
                f"Retrieved {len(terms)} available terms for {university.value}"
            )
            return terms
        except Exception as e:
            logger.error(f"Failed to get available terms for {university.value}: {e}")
            raise ServiceError(f"Failed to get available terms: {str(e)}")

    def get_live_courses(
        self,
        university: University,
        term_code: str,
        subjects: List[str],
        course_codes: Optional[List[str]] = None,
        max_courses_per_subject: int = 50,
    ) -> DiscoveryResult:
        """
        Get live course data for a term.

        Args:
            university: University to get data from
            term_code: Term identifier
            subjects: List of subject codes to query
            course_codes: Optional list of specific course codes
            max_courses_per_subject: Maximum courses per subject

        Returns:
            DiscoveryResult with live course information

        Raises:
            UniversityNotSupportedError: If university is not supported
            LiveDataNotSupportedError: If university doesn't support live data
            TermNotAvailableError: If term is not available
        """
        provider = self._course_service.get_provider(university)

        if not provider.supports_live_data():
            raise LiveDataNotSupportedError(university.value)

        # Validate term is available
        try:
            available_terms = provider.get_available_terms()
            available_codes = [code for code, name in available_terms]
            if term_code not in available_codes:
                available_names = [name for code, name in available_terms]
                raise TermNotAvailableError(
                    term_code, university.value, available_names
                )
        except TermNotAvailableError:
            raise
        except Exception as e:
            logger.warning(f"Could not validate term availability: {e}")

        try:
            result = provider.discover_courses(
                term_code=term_code,
                subjects=subjects,
                course_codes=course_codes,
                max_courses_per_subject=max_courses_per_subject,
            )

            logger.info(
                f"Discovered {result.total_courses} courses for {university.value} {term_code}"
            )
            logger.info(f"Offering rate: {result.offering_rate:.1f}%")

            return result

        except Exception as e:
            logger.error(
                f"Failed to discover courses for {university.value} {term_code}: {e}"
            )
            raise ServiceError(f"Failed to discover courses: {str(e)}")

    def get_supported_universities(self) -> List[University]:
        """
        Get list of universities that support live timetable data.

        Returns:
            List of University enums that support live data
        """
        supported = []
        for university in self._course_service.get_all_universities():
            try:
                provider = self._course_service.get_provider(university)
                if provider.supports_live_data():
                    supported.append(university)
            except Exception as e:
                logger.warning(
                    f"Error checking live data support for {university}: {e}"
                )

        return supported

    def validate_term_format(self, term_code: str) -> bool:
        """
        Validate term code format.

        Args:
            term_code: Term code to validate

        Returns:
            True if format is valid, False otherwise
        """
        # Basic validation - term codes are typically 6 digits (YYYYMM)
        import re

        return bool(re.match(r"^\d{6}$", term_code))

    def parse_term_info(self, term_code: str) -> Tuple[int, str]:
        """
        Parse year and semester from term code.

        Args:
            term_code: Term code to parse (format: YYYYMM)

        Returns:
            Tuple of (year, semester_name)

        Raises:
            ValueError: If term code format is invalid
        """
        if not self.validate_term_format(term_code):
            raise ValueError(f"Invalid term code format: {term_code}")

        year = int(term_code[:4])
        month = int(term_code[4:6])

        # Map month to semester name (this may need adjustment per university)
        semester_map = {
            1: "Winter",
            2: "Winter",
            3: "Winter",
            4: "Summer",
            5: "Summer",
            6: "Summer",
            7: "Summer",
            8: "Summer",
            9: "Fall",
            10: "Fall",
            11: "Fall",
            12: "Fall",
        }

        semester = semester_map.get(month, "Unknown")
        return year, semester

    def format_term_name(self, term_code: str) -> str:
        """
        Format a human-readable term name from term code.

        Args:
            term_code: Term code to format

        Returns:
            Formatted term name (e.g., "Fall 2025")
        """
        try:
            year, semester = self.parse_term_info(term_code)
            return f"{semester} {year}"
        except ValueError:
            return term_code  # Return as-is if parsing fails
