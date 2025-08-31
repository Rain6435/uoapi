"""
Core domain models and interfaces for the uoapi package.

This module provides the foundational abstractions used across all
university implementations and services.
"""

from .models import (
    University,
    Subject,
    Course,
    CourseSection,
    MeetingTime,
    Prerequisite,
    Component,
    SearchResult,
    DiscoveryResult,
)

from .interfaces import (
    UniversityProvider,
    CourseService,
    TimetableService,
    RatingService,
    DiscoveryService,
)

from .exceptions import (
    UOAPIError,
    ProviderError,
    DataSourceError,
    NetworkError,
    ParsingError,
    ValidationError,
    ConfigurationError,
    ServiceError,
    UniversityNotSupportedError,
    CourseNotFoundError,
    SubjectNotFoundError,
    TermNotAvailableError,
    RateLimitError,
    AssetNotFoundError,
    LiveDataNotSupportedError,
)

__all__ = [
    # Models
    "University",
    "Subject",
    "Course",
    "CourseSection",
    "MeetingTime",
    "Prerequisite",
    "Component",
    "SearchResult",
    "DiscoveryResult",
    # Interfaces
    "UniversityProvider",
    "CourseService",
    "TimetableService",
    "RatingService",
    "DiscoveryService",
    # Exceptions
    "UOAPIError",
    "ProviderError",
    "DataSourceError",
    "NetworkError",
    "ParsingError",
    "ValidationError",
    "ConfigurationError",
    "ServiceError",
    "UniversityNotSupportedError",
    "CourseNotFoundError",
    "SubjectNotFoundError",
    "TermNotAvailableError",
    "RateLimitError",
    "AssetNotFoundError",
    "LiveDataNotSupportedError",
]
