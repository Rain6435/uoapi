"""Unit tests for uoapi.core exceptions."""

import pytest
from uoapi.core.exceptions import (
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


class TestUOAPIError:
    """Tests for base UOAPIError exception."""

    def test_basic_instantiation(self):
        """Test creating UOAPIError with message."""
        exc = UOAPIError("Test error")
        assert exc.message == "Test error"
        assert str(exc) == "Test error"

    def test_with_details(self):
        """Test UOAPIError with details dict."""
        details = {"key": "value"}
        exc = UOAPIError("Test error", details)
        assert exc.details == details

    def test_details_default_empty(self):
        """Test details defaults to empty dict."""
        exc = UOAPIError("Test error")
        assert exc.details == {}


class TestProviderError:
    """Tests for ProviderError exception."""

    def test_inheritance(self):
        """Test ProviderError inherits from UOAPIError."""
        exc = ProviderError("Test error")
        assert isinstance(exc, UOAPIError)

    def test_instantiation(self):
        """Test creating ProviderError."""
        exc = ProviderError("Provider failed")
        assert exc.message == "Provider failed"


class TestDataSourceError:
    """Tests for DataSourceError exception."""

    def test_inheritance(self):
        """Test DataSourceError inherits from ProviderError."""
        exc = DataSourceError("Data source error")
        assert isinstance(exc, ProviderError)
        assert isinstance(exc, UOAPIError)


class TestNetworkError:
    """Tests for NetworkError exception."""

    def test_basic_instantiation(self):
        """Test creating NetworkError with message."""
        exc = NetworkError("Connection failed")
        assert exc.message == "Connection failed"

    def test_with_status_code(self):
        """Test NetworkError with status code."""
        exc = NetworkError("Server error", status_code=500)
        assert exc.status_code == 500
        assert exc.details["status_code"] == 500

    def test_with_url(self):
        """Test NetworkError with URL."""
        exc = NetworkError("Request failed", url="https://example.com")
        assert exc.url == "https://example.com"
        assert exc.details["url"] == "https://example.com"

    def test_with_status_and_url(self):
        """Test NetworkError with both status code and URL."""
        exc = NetworkError(
            "Request failed",
            status_code=404,
            url="https://example.com/api",
        )
        assert exc.status_code == 404
        assert exc.url == "https://example.com/api"
        assert exc.details["status_code"] == 404
        assert exc.details["url"] == "https://example.com/api"

    def test_inheritance(self):
        """Test NetworkError inherits from DataSourceError."""
        exc = NetworkError("Network error")
        assert isinstance(exc, DataSourceError)


class TestParsingError:
    """Tests for ParsingError exception."""

    def test_basic_instantiation(self):
        """Test creating ParsingError."""
        exc = ParsingError("Failed to parse")
        assert exc.message == "Failed to parse"

    def test_with_raw_data(self):
        """Test ParsingError with raw data."""
        data = "<html>invalid</html>"
        exc = ParsingError("Parse failed", raw_data=data)
        assert exc.raw_data == data
        assert exc.details["raw_data_length"] == len(data)

    def test_raw_data_length_zero_when_none(self):
        """Test raw_data_length is 0 when raw_data is None."""
        exc = ParsingError("Parse failed", raw_data=None)
        assert exc.details["raw_data_length"] == 0

    def test_inheritance(self):
        """Test ParsingError inherits from ProviderError."""
        exc = ParsingError("Parse error")
        assert isinstance(exc, ProviderError)


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_basic_instantiation(self):
        """Test creating ValidationError."""
        exc = ValidationError("Invalid input")
        assert exc.message == "Invalid input"

    def test_with_field(self):
        """Test ValidationError with field name."""
        exc = ValidationError("Invalid course code", field="course_code")
        assert exc.field == "course_code"
        assert exc.details["field"] == "course_code"

    def test_with_field_and_value(self):
        """Test ValidationError with field and value."""
        exc = ValidationError(
            "Invalid subject code",
            field="subject_code",
            value="XX",
        )
        assert exc.field == "subject_code"
        assert exc.value == "XX"
        assert exc.details["value"] == "XX"

    def test_inheritance(self):
        """Test ValidationError inherits from UOAPIError."""
        exc = ValidationError("Validation failed")
        assert isinstance(exc, UOAPIError)


class TestConfigurationError:
    """Tests for ConfigurationError exception."""

    def test_instantiation(self):
        """Test creating ConfigurationError."""
        exc = ConfigurationError("Configuration invalid")
        assert exc.message == "Configuration invalid"

    def test_inheritance(self):
        """Test ConfigurationError inherits from UOAPIError."""
        exc = ConfigurationError("Config error")
        assert isinstance(exc, UOAPIError)


class TestServiceError:
    """Tests for ServiceError exception."""

    def test_instantiation(self):
        """Test creating ServiceError."""
        exc = ServiceError("Service operation failed")
        assert exc.message == "Service operation failed"

    def test_inheritance(self):
        """Test ServiceError inherits from UOAPIError."""
        exc = ServiceError("Service error")
        assert isinstance(exc, UOAPIError)


class TestUniversityNotSupportedError:
    """Tests for UniversityNotSupportedError exception."""

    def test_basic_instantiation(self):
        """Test creating UniversityNotSupportedError."""
        exc = UniversityNotSupportedError("mcmaster")
        assert exc.university == "mcmaster"
        assert "mcmaster" in exc.message
        assert "not supported" in exc.message

    def test_with_supported_universities(self):
        """Test UniversityNotSupportedError with supported list."""
        supported = ["carleton", "uottawa"]
        exc = UniversityNotSupportedError("mcmaster", supported)
        assert exc.supported_universities == supported
        assert "carleton" in exc.message
        assert "uottawa" in exc.message

    def test_details_dict(self):
        """Test details dict contains university info."""
        supported = ["carleton", "uottawa"]
        exc = UniversityNotSupportedError("mcmaster", supported)
        assert exc.details["university"] == "mcmaster"
        assert exc.details["supported_universities"] == supported

    def test_inheritance(self):
        """Test UniversityNotSupportedError inherits from ServiceError."""
        exc = UniversityNotSupportedError("invalid")
        assert isinstance(exc, ServiceError)


class TestCourseNotFoundError:
    """Tests for CourseNotFoundError exception."""

    def test_basic_instantiation(self):
        """Test creating CourseNotFoundError."""
        exc = CourseNotFoundError("COMP9999")
        assert exc.course_code == "COMP9999"
        assert "COMP9999" in exc.message

    def test_with_university(self):
        """Test CourseNotFoundError with university."""
        exc = CourseNotFoundError("COMP9999", "carleton")
        assert exc.university == "carleton"
        assert "carleton" in exc.message

    def test_details_dict(self):
        """Test details dict contains course info."""
        exc = CourseNotFoundError("COMP9999", "carleton")
        assert exc.details["course_code"] == "COMP9999"
        assert exc.details["university"] == "carleton"

    def test_inheritance(self):
        """Test CourseNotFoundError inherits from ServiceError."""
        exc = CourseNotFoundError("COMP9999")
        assert isinstance(exc, ServiceError)


class TestSubjectNotFoundError:
    """Tests for SubjectNotFoundError exception."""

    def test_basic_instantiation(self):
        """Test creating SubjectNotFoundError."""
        exc = SubjectNotFoundError("XX")
        assert exc.subject_code == "XX"
        assert "XX" in exc.message

    def test_with_university(self):
        """Test SubjectNotFoundError with university."""
        exc = SubjectNotFoundError("XX", "carleton")
        assert exc.university == "carleton"

    def test_details_dict(self):
        """Test details dict contains subject info."""
        exc = SubjectNotFoundError("XX", "carleton")
        assert exc.details["subject_code"] == "XX"
        assert exc.details["university"] == "carleton"

    def test_inheritance(self):
        """Test SubjectNotFoundError inherits from ServiceError."""
        exc = SubjectNotFoundError("XX")
        assert isinstance(exc, ServiceError)


class TestTermNotAvailableError:
    """Tests for TermNotAvailableError exception."""

    def test_basic_instantiation(self):
        """Test creating TermNotAvailableError."""
        exc = TermNotAvailableError("202540")
        assert exc.term_code == "202540"
        assert "202540" in exc.message

    def test_with_university(self):
        """Test TermNotAvailableError with university."""
        exc = TermNotAvailableError("202540", "carleton")
        assert exc.university == "carleton"

    def test_with_available_terms(self):
        """Test TermNotAvailableError with available terms."""
        available = ["202530", "202510"]
        exc = TermNotAvailableError("202540", "carleton", available)
        assert exc.available_terms == available
        assert "202530" in exc.message
        assert "202510" in exc.message

    def test_details_dict(self):
        """Test details dict contains term info."""
        available = ["202530", "202510"]
        exc = TermNotAvailableError("202540", "carleton", available)
        assert exc.details["term_code"] == "202540"
        assert exc.details["university"] == "carleton"
        assert exc.details["available_terms"] == available

    def test_inheritance(self):
        """Test TermNotAvailableError inherits from ServiceError."""
        exc = TermNotAvailableError("202540")
        assert isinstance(exc, ServiceError)


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_basic_instantiation(self):
        """Test creating RateLimitError."""
        exc = RateLimitError("Rate limited")
        assert exc.message == "Rate limited"

    def test_with_retry_after(self):
        """Test RateLimitError with retry_after."""
        exc = RateLimitError("Rate limited", retry_after=60)
        assert exc.retry_after == 60
        assert exc.details["retry_after"] == 60

    def test_inheritance(self):
        """Test RateLimitError inherits from NetworkError."""
        exc = RateLimitError("Rate limited")
        assert isinstance(exc, NetworkError)


class TestAssetNotFoundError:
    """Tests for AssetNotFoundError exception."""

    def test_basic_instantiation(self):
        """Test creating AssetNotFoundError."""
        exc = AssetNotFoundError("assets/courses.json")
        assert exc.asset_path == "assets/courses.json"
        assert "assets/courses.json" in exc.message

    def test_with_searched_paths(self):
        """Test AssetNotFoundError with searched paths."""
        searched = ["/path1/courses.json", "/path2/courses.json"]
        exc = AssetNotFoundError("courses.json", searched)
        assert exc.searched_paths == searched
        assert "/path1/courses.json" in exc.message

    def test_details_dict(self):
        """Test details dict contains asset info."""
        searched = ["/path1"]
        exc = AssetNotFoundError("courses.json", searched)
        assert exc.details["asset_path"] == "courses.json"
        assert exc.details["searched_paths"] == searched

    def test_inheritance(self):
        """Test AssetNotFoundError inherits from DataSourceError."""
        exc = AssetNotFoundError("courses.json")
        assert isinstance(exc, DataSourceError)


class TestLiveDataNotSupportedError:
    """Tests for LiveDataNotSupportedError exception."""

    def test_instantiation(self):
        """Test creating LiveDataNotSupportedError."""
        exc = LiveDataNotSupportedError("mcmaster")
        assert exc.university == "mcmaster"
        assert "mcmaster" in exc.message
        assert "Live" in exc.message

    def test_details_dict(self):
        """Test details dict contains university."""
        exc = LiveDataNotSupportedError("mcmaster")
        assert exc.details["university"] == "mcmaster"

    def test_inheritance(self):
        """Test LiveDataNotSupportedError inherits from ServiceError."""
        exc = LiveDataNotSupportedError("mcmaster")
        assert isinstance(exc, ServiceError)


class TestExceptionHierarchy:
    """Tests for exception inheritance hierarchy."""

    def test_network_error_is_data_source_error(self):
        """Test NetworkError is a DataSourceError."""
        exc = NetworkError("test")
        assert isinstance(exc, DataSourceError)
        assert isinstance(exc, ProviderError)
        assert isinstance(exc, UOAPIError)

    def test_parsing_error_is_provider_error(self):
        """Test ParsingError is a ProviderError."""
        exc = ParsingError("test")
        assert isinstance(exc, ProviderError)
        assert isinstance(exc, UOAPIError)

    def test_service_errors_are_uoapi_error(self):
        """Test all service errors inherit from UOAPIError."""
        exc = ServiceError("test")
        assert isinstance(exc, UOAPIError)

    def test_course_not_found_is_service_error(self):
        """Test CourseNotFoundError is ServiceError."""
        exc = CourseNotFoundError("COMP1005")
        assert isinstance(exc, ServiceError)
