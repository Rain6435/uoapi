"""
Discovery service implementation.

This module wraps the existing discovery service functionality
to provide a clean interface for data asset management.
"""

from typing import List, Dict, Any, Optional
import logging

from uoapi.core import (
    DiscoveryService,
    ServiceError,
)

logger = logging.getLogger(__name__)


class DefaultDiscoveryService(DiscoveryService):
    """
    Default implementation of the DiscoveryService interface.

    This service wraps the existing discovery functionality to provide
    access to stored course data assets.
    """

    def __init__(self):
        # Import the existing discovery service
        from uoapi.discovery import discovery_service

        self._discovery_service = discovery_service

    def get_available_universities(self) -> List[str]:
        """
        Get list of universities with available data.

        Returns:
            List of university identifiers
        """
        try:
            return self._discovery_service.get_available_universities()
        except Exception as e:
            logger.error(f"Failed to get available universities: {e}")
            raise ServiceError(f"Failed to get available universities: {str(e)}")

    def get_course_data(self, university: str) -> Dict[str, Any]:
        """
        Get course data for a university.

        Args:
            university: University identifier

        Returns:
            Dictionary containing course data
        """
        try:
            return self._discovery_service.get_courses_data(university)
        except Exception as e:
            logger.error(f"Failed to get course data for {university}: {e}")
            raise ServiceError(f"Failed to get course data for {university}: {str(e)}")

    def get_course_count(self, university: str) -> int:
        """
        Get total course count for a university.

        Args:
            university: University identifier

        Returns:
            Total number of courses
        """
        try:
            return self._discovery_service.get_course_count(university)
        except Exception as e:
            logger.error(f"Failed to get course count for {university}: {e}")
            raise ServiceError(f"Failed to get course count for {university}: {str(e)}")

    def get_subjects_list(self, university: str) -> List[str]:
        """
        Get list of subject codes for a university.

        Args:
            university: University identifier

        Returns:
            List of subject codes
        """
        try:
            return self._discovery_service.get_subjects_list(university)
        except Exception as e:
            logger.error(f"Failed to get subjects list for {university}: {e}")
            raise ServiceError(
                f"Failed to get subjects list for {university}: {str(e)}"
            )

    def search_courses(
        self,
        university: str,
        subject_code: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search courses in stored data.

        Args:
            university: University identifier
            subject_code: Optional subject code filter
            query: Optional search query

        Returns:
            List of course dictionaries
        """
        try:
            return self._discovery_service.search_courses(
                university, subject_code=subject_code, query=query
            )
        except Exception as e:
            logger.error(f"Failed to search courses for {university}: {e}")
            raise ServiceError(f"Failed to search courses: {str(e)}")

    def get_university_info(self, university: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a university.

        Args:
            university: University identifier

        Returns:
            Dictionary with university information
        """
        try:
            # Collect information from various sources
            course_count = self.get_course_count(university)
            subjects = self.get_subjects_list(university)
            course_data = self.get_course_data(university)

            info = {
                "university": university,
                "total_courses": course_count,
                "total_subjects": len(subjects),
                "subjects": sorted(subjects),
            }

            # Add metadata if available in course data
            if isinstance(course_data, dict):
                if "metadata" in course_data:
                    info["data_metadata"] = course_data["metadata"]
                if "discovery_metadata" in course_data:
                    info["discovery_metadata"] = course_data["discovery_metadata"]

            logger.info(f"Retrieved university info for {university}")
            return info

        except Exception as e:
            logger.error(f"Failed to get university info for {university}: {e}")
            raise ServiceError(f"Failed to get university info: {str(e)}")

    def validate_university(self, university: str) -> bool:
        """
        Check if a university identifier is valid.

        Args:
            university: University identifier to validate

        Returns:
            True if university is valid, False otherwise
        """
        try:
            available = self.get_available_universities()
            return university in available
        except Exception as e:
            logger.warning(f"Failed to validate university {university}: {e}")
            return False

    def normalize_university_name(self, university_input: str) -> Optional[str]:
        """
        Normalize university name variations to standard identifier.

        Args:
            university_input: User-provided university string

        Returns:
            Normalized university identifier if found, None otherwise
        """
        # Normalize the input
        normalized = (
            university_input.lower()
            .replace(" ", "")
            .replace("university", "")
            .replace("of", "")
        )

        # Check available universities
        try:
            available = self.get_available_universities()

            # Direct match
            if university_input in available:
                return university_input

            # Map common variations
            if "ottawa" in normalized:
                if "uottawa" in available:
                    return "uottawa"
            elif "carleton" in normalized:
                if "carleton" in available:
                    return "carleton"

            # Try each available university
            for uni in available:
                if normalized == uni.lower().replace(" ", "").replace(
                    "university", ""
                ).replace("of", ""):
                    return uni

        except Exception as e:
            logger.warning(f"Failed to normalize university name: {e}")

        return None

    def get_data_freshness(self, university: str) -> Dict[str, Any]:
        """
        Get information about data freshness and last update times.

        Args:
            university: University identifier

        Returns:
            Dictionary with data freshness information
        """
        try:
            course_data = self.get_course_data(university)

            freshness_info = {
                "university": university,
                "has_metadata": False,
                "last_updated": None,
                "data_source": "unknown",
            }

            # Extract metadata if available
            if isinstance(course_data, dict):
                if "metadata" in course_data:
                    metadata = course_data["metadata"]
                    freshness_info.update(
                        {
                            "has_metadata": True,
                            "last_updated": metadata.get("last_updated"),
                            "data_source": metadata.get("source", "unknown"),
                            "total_records": metadata.get("total_courses"),
                            "generation_time": metadata.get("generation_time_seconds"),
                        }
                    )

                if "discovery_metadata" in course_data:
                    discovery_meta = course_data["discovery_metadata"]
                    freshness_info["discovery_metadata"] = discovery_meta

            return freshness_info

        except Exception as e:
            logger.error(f"Failed to get data freshness for {university}: {e}")
            return {"error": str(e)}
