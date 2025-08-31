"""
Rating service implementation.

This module provides business logic for professor rating operations,
integrating with Rate My Professor data.
"""

from typing import List, Optional, Dict, Any, Tuple
import logging

from uoapi.core import (
    RatingService,
    University,
    Course,
    ServiceError,
)

logger = logging.getLogger(__name__)


class DefaultRatingService(RatingService):
    """
    Default implementation of the RatingService interface.

    This service integrates with the existing RMP functionality
    to provide professor rating information.
    """

    def __init__(self):
        self._university_name_mapping = {
            University.UOTTAWA: "University of Ottawa",
            University.CARLETON: "Carleton University",
        }
        self._rating_cache: Dict[str, Dict[str, Any]] = {}

    def get_instructor_rating(
        self, instructor_name: str, university: University
    ) -> Optional[Dict[str, Any]]:
        """
        Get rating for a specific instructor.

        Args:
            instructor_name: Name of the instructor
            university: University the instructor teaches at

        Returns:
            Rating dictionary if found, None otherwise
        """
        cache_key = f"{university.value}:{instructor_name.lower()}"

        if cache_key in self._rating_cache:
            logger.debug(f"Using cached rating for {instructor_name}")
            return self._rating_cache[cache_key]

        try:
            # Parse instructor name
            first_name, last_name = self._parse_instructor_name(instructor_name)
            if not first_name or not last_name:
                logger.warning(f"Could not parse instructor name: {instructor_name}")
                return None

            # Get rating using existing RMP functionality
            from uoapi.rmp import get_instructor_rating

            school_name = self._university_name_mapping.get(university)
            if not school_name:
                logger.error(f"No school mapping for university: {university}")
                return None

            rating_data = get_instructor_rating(first_name, last_name, school_name)

            # Cache the result (even if None)
            self._rating_cache[cache_key] = rating_data

            if rating_data:
                logger.info(
                    f"Found rating for {instructor_name}: {rating_data.get('rating', 'N/A')}"
                )
            else:
                logger.debug(f"No rating found for {instructor_name}")

            return rating_data

        except Exception as e:
            logger.error(f"Failed to get rating for {instructor_name}: {e}")
            return None

    def get_batch_ratings(
        self,
        instructors: List[Tuple[str, str]],  # (first_name, last_name)
        university: University,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get ratings for multiple instructors.

        Args:
            instructors: List of (first_name, last_name) tuples
            university: University the instructors teach at

        Returns:
            Dictionary mapping full names to rating data
        """
        try:
            from uoapi.rmp import get_teachers_ratings_by_school

            school_name = self._university_name_mapping.get(university)
            if not school_name:
                logger.error(f"No school mapping for university: {university}")
                return {}

            result = get_teachers_ratings_by_school(school_name, instructors)

            if "ratings" not in result:
                logger.warning("No ratings data in result")
                return {}

            # Convert to dictionary keyed by full name
            ratings_dict = {}
            for rating in result["ratings"]:
                full_name = f"{rating['first_name']} {rating['last_name']}"
                ratings_dict[full_name] = rating

                # Cache individual ratings
                cache_key = f"{university.value}:{full_name.lower()}"
                self._rating_cache[cache_key] = rating

            logger.info(f"Retrieved ratings for {len(ratings_dict)} instructors")
            return ratings_dict

        except Exception as e:
            logger.error(f"Failed to get batch ratings: {e}")
            return {}

    def inject_ratings_into_courses(
        self, courses: List[Course], university: University
    ) -> List[Course]:
        """
        Add rating information to course sections.

        Args:
            courses: List of courses to enhance with ratings
            university: University the courses are from

        Returns:
            List of courses with rating information added
        """
        if not courses:
            return courses

        try:
            # Collect all unique instructors
            instructors_set = set()
            instructor_name_map = {}  # Map normalized names back to original

            for course in courses:
                for section in course.sections:
                    if (
                        section.instructor
                        and section.instructor.strip()
                        and section.instructor != "TBA"
                    ):
                        instructor_name = section.instructor.strip()
                        first_name, last_name = self._parse_instructor_name(
                            instructor_name
                        )

                        if first_name and last_name:
                            instructors_set.add((first_name, last_name))
                            full_name = f"{first_name} {last_name}"
                            instructor_name_map[full_name] = instructor_name

            if not instructors_set:
                logger.info("No instructors found in courses")
                return courses

            # Get ratings for all instructors
            instructors_list = list(instructors_set)
            ratings = self.get_batch_ratings(instructors_list, university)

            # Inject ratings into courses
            enhanced_courses = []
            for course in courses:
                enhanced_sections = []
                for section in course.sections:
                    # This is where we would add rating data to sections
                    # For now, we'll just note that ratings are available
                    if section.instructor and section.instructor.strip():
                        first_name, last_name = self._parse_instructor_name(
                            section.instructor
                        )
                        if first_name and last_name:
                            full_name = f"{first_name} {last_name}"
                            if full_name in ratings:
                                logger.debug(
                                    f"Rating available for {section.instructor}"
                                )

                    enhanced_sections.append(section)

                # Create new course with potentially enhanced sections
                enhanced_course = Course(
                    course_code=course.course_code,
                    subject_code=course.subject_code,
                    course_number=course.course_number,
                    title=course.title,
                    description=course.description,
                    credits=course.credits,
                    university=course.university,
                    components=course.components,
                    prerequisites=course.prerequisites,
                    prerequisite_courses=course.prerequisite_courses,
                    sections=enhanced_sections,
                    is_offered=course.is_offered,
                    last_updated=course.last_updated,
                )
                enhanced_courses.append(enhanced_course)

            logger.info(f"Enhanced {len(enhanced_courses)} courses with rating data")
            return enhanced_courses

        except Exception as e:
            logger.error(f"Failed to inject ratings into courses: {e}")
            return courses  # Return original courses on error

    def _parse_instructor_name(self, full_name: str) -> Tuple[str, str]:
        """
        Parse instructor name into first and last components.

        Args:
            full_name: Full instructor name

        Returns:
            Tuple of (first_name, last_name)
        """
        try:
            from uoapi.rmp import parse_instructor_name

            return parse_instructor_name(full_name)
        except Exception as e:
            logger.warning(f"Failed to parse instructor name '{full_name}': {e}")

            # Fallback parsing
            parts = full_name.strip().split()
            if len(parts) >= 2:
                return parts[0], " ".join(parts[1:])
            elif len(parts) == 1:
                return parts[0], ""
            else:
                return "", ""

    def get_rating_statistics(self, university: University) -> Dict[str, Any]:
        """
        Get statistics about available ratings for a university.

        Args:
            university: University to get statistics for

        Returns:
            Dictionary with rating statistics
        """
        try:
            # This would require access to all instructors, which might be expensive
            # For now, return basic cache statistics
            university_cache_keys = [
                k
                for k in self._rating_cache.keys()
                if k.startswith(f"{university.value}:")
            ]
            cached_ratings = [
                v
                for k, v in self._rating_cache.items()
                if k.startswith(f"{university.value}:") and v
            ]

            if cached_ratings:
                ratings_values = [
                    r.get("rating", 0) for r in cached_ratings if r.get("rating")
                ]
                avg_rating = (
                    sum(ratings_values) / len(ratings_values) if ratings_values else 0
                )

                stats = {
                    "university": university.value,
                    "instructors_cached": len(university_cache_keys),
                    "instructors_with_ratings": len(cached_ratings),
                    "average_rating": round(avg_rating, 2) if avg_rating else None,
                    "rating_coverage": len(cached_ratings)
                    / max(1, len(university_cache_keys))
                    * 100,
                }
            else:
                stats = {
                    "university": university.value,
                    "instructors_cached": 0,
                    "instructors_with_ratings": 0,
                    "average_rating": None,
                    "rating_coverage": 0,
                }

            return stats

        except Exception as e:
            logger.error(f"Failed to get rating statistics for {university.value}: {e}")
            return {"error": str(e)}

    def clear_cache(self):
        """Clear the rating cache."""
        self._rating_cache.clear()
        logger.info("Rating cache cleared")
