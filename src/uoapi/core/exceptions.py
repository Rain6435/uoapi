"""
Common exception classes for the uoapi package.

This module defines exception hierarchies that provide consistent
error handling across all university implementations and services.
"""


class UOAPIError(Exception):
    """Base exception class for all uoapi-related errors."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ProviderError(UOAPIError):
    """Exception raised when a university provider encounters an error."""

    pass


class DataSourceError(ProviderError):
    """Exception raised when there are issues with the underlying data source."""

    pass


class NetworkError(DataSourceError):
    """Exception raised when network requests fail."""

    def __init__(self, message: str, status_code: int = None, url: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.details = {"status_code": status_code, "url": url}


class ParsingError(ProviderError):
    """Exception raised when data parsing fails."""

    def __init__(self, message: str, raw_data: str = None):
        super().__init__(message)
        self.raw_data = raw_data
        self.details = {"raw_data_length": len(raw_data) if raw_data else 0}


class ValidationError(UOAPIError):
    """Exception raised when data validation fails."""

    def __init__(self, message: str, field: str = None, value: str = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.details = {"field": field, "value": value}


class ConfigurationError(UOAPIError):
    """Exception raised when there are configuration issues."""

    pass


class ServiceError(UOAPIError):
    """Exception raised by service layer operations."""

    pass


class UniversityNotSupportedError(ServiceError):
    """Exception raised when an unsupported university is requested."""

    def __init__(self, university: str, supported_universities: list = None):
        message = f"University '{university}' is not supported"
        if supported_universities:
            message += f". Supported universities: {', '.join(supported_universities)}"
        super().__init__(message)
        self.university = university
        self.supported_universities = supported_universities or []
        self.details = {
            "university": university,
            "supported_universities": self.supported_universities,
        }


class CourseNotFoundError(ServiceError):
    """Exception raised when a requested course cannot be found."""

    def __init__(self, course_code: str, university: str = None):
        message = f"Course '{course_code}' not found"
        if university:
            message += f" at {university}"
        super().__init__(message)
        self.course_code = course_code
        self.university = university
        self.details = {"course_code": course_code, "university": university}


class SubjectNotFoundError(ServiceError):
    """Exception raised when a requested subject cannot be found."""

    def __init__(self, subject_code: str, university: str = None):
        message = f"Subject '{subject_code}' not found"
        if university:
            message += f" at {university}"
        super().__init__(message)
        self.subject_code = subject_code
        self.university = university
        self.details = {"subject_code": subject_code, "university": university}


class TermNotAvailableError(ServiceError):
    """Exception raised when a requested term is not available."""

    def __init__(
        self, term_code: str, university: str = None, available_terms: list = None
    ):
        message = f"Term '{term_code}' is not available"
        if university:
            message += f" at {university}"
        if available_terms:
            message += f". Available terms: {', '.join(available_terms)}"
        super().__init__(message)
        self.term_code = term_code
        self.university = university
        self.available_terms = available_terms or []
        self.details = {
            "term_code": term_code,
            "university": university,
            "available_terms": self.available_terms,
        }


class RateLimitError(NetworkError):
    """Exception raised when API rate limits are exceeded."""

    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after
        self.details["retry_after"] = retry_after


class AssetNotFoundError(DataSourceError):
    """Exception raised when required data assets cannot be found."""

    def __init__(self, asset_path: str, searched_paths: list = None):
        message = f"Asset not found: {asset_path}"
        if searched_paths:
            message += f". Searched paths: {', '.join(searched_paths)}"
        super().__init__(message)
        self.asset_path = asset_path
        self.searched_paths = searched_paths or []
        self.details = {"asset_path": asset_path, "searched_paths": self.searched_paths}


class LiveDataNotSupportedError(ServiceError):
    """Exception raised when live data is requested but not supported."""

    def __init__(self, university: str):
        message = f"Live course data is not supported for {university}"
        super().__init__(message)
        self.university = university
        self.details = {"university": university}
