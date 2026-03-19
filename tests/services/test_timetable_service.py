"""Unit tests for DefaultTimetableService."""

import pytest
from unittest.mock import Mock, patch

from uoapi.core.models import University, DiscoveryResult, Course
from uoapi.core.exceptions import (
    UniversityNotSupportedError,
    TermNotAvailableError,
    LiveDataNotSupportedError,
)
from uoapi.services.timetable_service import DefaultTimetableService
from uoapi.services.course_service import DefaultCourseService


@pytest.fixture
def mock_course_service():
    """Create mock course service."""
    service = Mock(spec=DefaultCourseService)
    return service


@pytest.fixture
def mock_carleton_provider():
    """Create mock Carleton provider with live data support."""
    provider = Mock()
    provider.supports_live_data.return_value = True
    provider.get_available_terms.return_value = [
        ("202530", "Fall 2025"),
        ("202510", "Winter 2025"),
    ]
    return provider


@pytest.fixture
def mock_uottawa_provider():
    """Create mock UOttawa provider with live data support."""
    provider = Mock()
    provider.supports_live_data.return_value = True
    provider.get_available_terms.return_value = [
        ("202530", "Fall 2025"),
        ("202510", "Winter 2025"),
    ]
    return provider


@pytest.fixture
def timetable_service_with_mocks(
    mock_course_service, mock_carleton_provider, mock_uottawa_provider
):
    """Create timetable service with mocked course service."""
    mock_course_service.get_all_universities.return_value = [
        University.CARLETON,
        University.UOTTAWA,
    ]
    mock_course_service.get_provider.side_effect = lambda uni: (
        mock_carleton_provider if uni == University.CARLETON else mock_uottawa_provider
    )

    service = DefaultTimetableService(mock_course_service)
    return service, mock_course_service, mock_carleton_provider, mock_uottawa_provider


class TestGetAvailableTerms:
    """Tests for get_available_terms method."""

    def test_returns_term_list(self, timetable_service_with_mocks):
        """Test get_available_terms returns list of tuples."""
        service, _, _, _ = timetable_service_with_mocks
        terms = service.get_available_terms(University.CARLETON)
        assert len(terms) == 2
        assert isinstance(terms, list)
        assert isinstance(terms[0], tuple)

    def test_term_tuple_format(self, timetable_service_with_mocks):
        """Test term tuple has (code, name) format."""
        service, _, _, _ = timetable_service_with_mocks
        terms = service.get_available_terms(University.CARLETON)
        code, name = terms[0]
        assert isinstance(code, str)
        assert isinstance(name, str)
        assert code == "202530"
        assert name == "Fall 2025"

    def test_raises_for_no_live_data_support(self, timetable_service_with_mocks):
        """Test raises LiveDataNotSupportedError when provider doesn't support live data."""
        service, _, mock_carleton, _ = timetable_service_with_mocks
        mock_carleton.supports_live_data.return_value = False
        with pytest.raises(LiveDataNotSupportedError):
            service.get_available_terms(University.CARLETON)

    def test_raises_for_unsupported_university(self, timetable_service_with_mocks):
        """Test raises for unsupported university."""
        service, mock_course_service, _, _ = timetable_service_with_mocks
        mock_course_service.get_provider.side_effect = UniversityNotSupportedError(
            "invalid"
        )
        with pytest.raises(UniversityNotSupportedError):
            service.get_available_terms(Mock())


class TestGetLiveCourses:
    """Tests for get_live_courses method."""

    def test_returns_discovery_result(self, timetable_service_with_mocks):
        """Test get_live_courses returns DiscoveryResult."""
        service, _, mock_carleton, _ = timetable_service_with_mocks
        mock_carleton.discover_courses.return_value = DiscoveryResult(
            term_code="202530",
            term_name="Fall 2025",
            university=University.CARLETON,
            total_courses=1,
            courses=[
                Course(
                    course_code="COMP1005",
                    subject_code="COMP",
                    course_number="1005",
                    title="Test",
                    credits=3,
                    university=University.CARLETON,
                )
            ],
        )

        result = service.get_live_courses(
            University.CARLETON,
            "202530",
            ["COMP"],
        )

        assert isinstance(result, DiscoveryResult)
        assert result.term_code == "202530"
        assert result.total_courses == 1

    def test_with_course_codes_filter(self, timetable_service_with_mocks):
        """Test get_live_courses with specific course codes."""
        service, _, mock_carleton, _ = timetable_service_with_mocks
        mock_carleton.discover_courses.return_value = DiscoveryResult(
            term_code="202530",
            term_name="Fall 2025",
            university=University.CARLETON,
        )

        result = service.get_live_courses(
            University.CARLETON,
            "202530",
            ["COMP"],
            course_codes=["COMP1005"],
        )

        assert result.term_code == "202530"

    def test_with_max_courses_per_subject(self, timetable_service_with_mocks):
        """Test get_live_courses with max_courses_per_subject."""
        service, _, mock_carleton, _ = timetable_service_with_mocks
        mock_carleton.discover_courses.return_value = DiscoveryResult(
            term_code="202530",
            term_name="Fall 2025",
            university=University.CARLETON,
        )

        result = service.get_live_courses(
            University.CARLETON,
            "202530",
            ["COMP"],
            max_courses_per_subject=100,
        )

        assert result.term_code == "202530"

    def test_raises_for_unsupported_university(self, timetable_service_with_mocks):
        """Test raises for unsupported university."""
        service, mock_course_service, _, _ = timetable_service_with_mocks
        mock_course_service.get_provider.side_effect = UniversityNotSupportedError(
            "invalid"
        )
        with pytest.raises(UniversityNotSupportedError):
            service.get_live_courses(Mock(), "202530", ["COMP"])


class TestLiveDataValidation:
    """Tests for live data validation."""

    def test_raises_when_term_not_available(self, timetable_service_with_mocks):
        """Test raises TermNotAvailableError for unavailable term."""
        service, _, mock_carleton, _ = timetable_service_with_mocks
        # The test setup returns 202530 and 202510
        # Try to get a term that's not available
        mock_carleton.get_available_terms.return_value = [
            ("202530", "Fall 2025"),
            ("202510", "Winter 2025"),
        ]

        # This would raise if term validation is done
        # The actual implementation should handle this
        with pytest.raises(TermNotAvailableError):
            service.get_live_courses(
                University.CARLETON,
                "202540",  # Spring - not available
                ["COMP"],
            )

    def test_accepts_valid_term(self, timetable_service_with_mocks):
        """Test accepts valid term code."""
        service, _, mock_carleton, _ = timetable_service_with_mocks
        mock_carleton.discover_courses.return_value = DiscoveryResult(
            term_code="202530",
            term_name="Fall 2025",
            university=University.CARLETON,
        )

        result = service.get_live_courses(
            University.CARLETON,
            "202530",
            ["COMP"],
        )

        assert result.term_code == "202530"
