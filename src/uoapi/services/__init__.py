"""
Business logic services for the uoapi package.

This package contains service classes that implement business logic
and coordinate between university providers and external interfaces.
"""

from .course_service import DefaultCourseService
from .timetable_service import DefaultTimetableService
from .rating_service import DefaultRatingService
from .discovery_service import DefaultDiscoveryService

__all__ = [
    "DefaultCourseService",
    "DefaultTimetableService",
    "DefaultRatingService",
    "DefaultDiscoveryService",
]
