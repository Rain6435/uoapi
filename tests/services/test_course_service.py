"""Unit tests for DefaultCourseService."""

import pytest
from unittest.mock import Mock, MagicMock, patch

from uoapi.core.models import University, Subject, Course, SearchResult
from uoapi.core.exceptions import (
    UniversityNotSupportedError,
    CourseNotFoundError,
    SubjectNotFoundError,
    ServiceError,
)
from uoapi.services.course_service import DefaultCourseService


@pytest.fixture
def mock_carleton_provider():
    """Create mock Carleton provider."""
    provider = Mock()
    provider.get_subjects.return_value = [
        Subject(name="Computer Science", code="COMP", university=University.CARLETON),
        Subject(name="Mathematics", code="MATH", university=University.CARLETON),
    ]
    provider.get_courses.return_value = [
        Course(
            course_code="COMP1005",
            subject_code="COMP",
            course_number="1005",
            title="Discrete Structures I",
            credits=3,
            university=University.CARLETON,
        ),
        Course(
            course_code="MATH1004",
            subject_code="MATH",
            course_number="1004",
            title="Calculus for Engineering",
            credits=3,
            university=University.CARLETON,
        ),
    ]
    provider.get_subject_by_code.return_value = Subject(
        name="Computer Science", code="COMP", university=University.CARLETON
    )
    provider.get_course_by_code.return_value = Course(
        course_code="COMP1005",
        subject_code="COMP",
        course_number="1005",
        title="Discrete Structures I",
        credits=3,
        university=University.CARLETON,
    )
    provider.search_courses.return_value = SearchResult(
        university=University.CARLETON,
        query="discrete",
        total_found=1,
        courses=[
            Course(
                course_code="COMP1005",
                subject_code="COMP",
                course_number="1005",
                title="Discrete Structures I",
                credits=3,
                university=University.CARLETON,
            )
        ],
    )
    return provider


@pytest.fixture
def mock_uottawa_provider():
    """Create mock UOttawa provider."""
    provider = Mock()
    provider.get_subjects.return_value = [
        Subject(name="Computer Science", code="CSI", university=University.UOTTAWA),
        Subject(name="Mathematics", code="MAT", university=University.UOTTAWA),
    ]
    provider.get_courses.return_value = [
        Course(
            course_code="CSI3140",
            subject_code="CSI",
            course_number="3140",
            title="Advanced Data Structures",
            credits=3,
            university=University.UOTTAWA,
        ),
    ]
    provider.get_subject_by_code.return_value = Subject(
        name="Computer Science", code="CSI", university=University.UOTTAWA
    )
    provider.get_course_by_code.return_value = Course(
        course_code="CSI3140",
        subject_code="CSI",
        course_number="3140",
        title="Advanced Data Structures",
        credits=3,
        university=University.UOTTAWA,
    )
    provider.search_courses.return_value = SearchResult(
        university=University.UOTTAWA,
        query="data",
        total_found=1,
        courses=[],
    )
    return provider


@pytest.fixture
def service_with_mocked_providers(mock_carleton_provider, mock_uottawa_provider):
    """Create service with mocked providers."""
    with (
        patch(
            "uoapi.services.course_service.CarletonProvider",
            return_value=mock_carleton_provider,
        ),
        patch(
            "uoapi.services.course_service.UOttawaProvider",
            return_value=mock_uottawa_provider,
        ),
    ):
        service = DefaultCourseService()
    return service, mock_carleton_provider, mock_uottawa_provider


class TestGetAllUniversities:
    """Tests for get_all_universities method."""

    def test_returns_both_universities(self, service_with_mocked_providers):
        """Test get_all_universities returns all supported universities."""
        service, _, _ = service_with_mocked_providers
        universities = service.get_all_universities()
        assert len(universities) == 2
        assert University.CARLETON in universities
        assert University.UOTTAWA in universities

    def test_returns_university_objects(self, service_with_mocked_providers):
        """Test returns University enum objects."""
        service, _, _ = service_with_mocked_providers
        universities = service.get_all_universities()
        assert all(isinstance(u, University) for u in universities)


class TestGetProvider:
    """Tests for get_provider method."""

    def test_returns_carleton_provider(self, service_with_mocked_providers):
        """Test get_provider returns Carleton provider."""
        service, mock_carleton, _ = service_with_mocked_providers
        provider = service.get_provider(University.CARLETON)
        assert provider == mock_carleton

    def test_returns_uottawa_provider(self, service_with_mocked_providers):
        """Test get_provider returns UOttawa provider."""
        service, _, mock_uottawa = service_with_mocked_providers
        provider = service.get_provider(University.UOTTAWA)
        assert provider == mock_uottawa

    def test_raises_for_unsupported_university(self, service_with_mocked_providers):
        """Test raises UniversityNotSupportedError for invalid university."""
        service, _, _ = service_with_mocked_providers
        # Create a fake enum value for testing
        with pytest.raises(UniversityNotSupportedError):
            service.get_provider(Mock())


class TestGetSubjects:
    """Tests for get_subjects method."""

    def test_returns_carleton_subjects(self, service_with_mocked_providers):
        """Test get_subjects returns subjects for Carleton."""
        service, _, _ = service_with_mocked_providers
        subjects = service.get_subjects(University.CARLETON)
        assert len(subjects) == 2
        assert subjects[0].code == "COMP"

    def test_returns_uottawa_subjects(self, service_with_mocked_providers):
        """Test get_subjects returns subjects for UOttawa."""
        service, _, _ = service_with_mocked_providers
        subjects = service.get_subjects(University.UOTTAWA)
        assert len(subjects) == 2
        assert subjects[0].code == "CSI"

    def test_raises_for_unsupported_university(self, service_with_mocked_providers):
        """Test get_subjects raises for unsupported university."""
        service, _, _ = service_with_mocked_providers
        with pytest.raises(UniversityNotSupportedError):
            service.get_subjects(Mock())

    def test_returns_subject_objects(self, service_with_mocked_providers):
        """Test returns Subject objects."""
        service, _, _ = service_with_mocked_providers
        subjects = service.get_subjects(University.CARLETON)
        assert all(isinstance(s, Subject) for s in subjects)


class TestGetSubjectByCode:
    """Tests for get_subject_by_code method."""

    def test_returns_subject_for_valid_code(self, service_with_mocked_providers):
        """Test get_subject_by_code returns subject for valid code."""
        service, _, _ = service_with_mocked_providers
        subject = service.get_subject_by_code(University.CARLETON, "COMP")
        assert subject.code == "COMP"
        assert subject.name == "Computer Science"

    def test_raises_subject_not_found_error(self, service_with_mocked_providers):
        """Test raises SubjectNotFoundError for invalid code."""
        service, mock_carleton, _ = service_with_mocked_providers
        mock_carleton.get_subject_by_code.return_value = None
        with pytest.raises(SubjectNotFoundError):
            service.get_subject_by_code(University.CARLETON, "XX")

    def test_raises_for_unsupported_university(self, service_with_mocked_providers):
        """Test raises UniversityNotSupportedError."""
        service, _, _ = service_with_mocked_providers
        with pytest.raises(UniversityNotSupportedError):
            service.get_subject_by_code(Mock(), "COMP")


class TestGetCourses:
    """Tests for get_courses method."""

    def test_returns_all_courses(self, service_with_mocked_providers):
        """Test get_courses returns all courses."""
        service, _, _ = service_with_mocked_providers
        courses = service.get_courses(University.CARLETON)
        assert len(courses) == 2
        assert all(isinstance(c, Course) for c in courses)

    def test_returns_courses_with_subject_filter(self, service_with_mocked_providers):
        """Test get_courses with subject filter."""
        service, mock_carleton, _ = service_with_mocked_providers
        mock_carleton.get_courses.return_value = [
            Course(
                course_code="COMP1005",
                subject_code="COMP",
                course_number="1005",
                title="Discrete Structures I",
                credits=3,
                university=University.CARLETON,
            )
        ]
        courses = service.get_courses(University.CARLETON, subject_code="COMP")
        assert len(courses) == 1
        assert courses[0].subject_code == "COMP"

    def test_returns_search_results_with_query(self, service_with_mocked_providers):
        """Test get_courses with search query."""
        service, _, _ = service_with_mocked_providers
        courses = service.get_courses(University.CARLETON, query="discrete")
        assert len(courses) == 1
        assert "Discrete" in courses[0].title

    def test_raises_for_unsupported_university(self, service_with_mocked_providers):
        """Test raises UniversityNotSupportedError."""
        service, _, _ = service_with_mocked_providers
        with pytest.raises(UniversityNotSupportedError):
            service.get_courses(Mock())


class TestGetCourseByCode:
    """Tests for get_course_by_code method."""

    def test_returns_course_for_valid_code(self, service_with_mocked_providers):
        """Test get_course_by_code returns course for valid code."""
        service, _, _ = service_with_mocked_providers
        course = service.get_course_by_code(University.CARLETON, "COMP1005")
        assert course.course_code == "COMP1005"
        assert course.title == "Discrete Structures I"

    def test_raises_course_not_found_error(self, service_with_mocked_providers):
        """Test raises CourseNotFoundError for invalid code."""
        service, mock_carleton, _ = service_with_mocked_providers
        mock_carleton.get_course_by_code.return_value = None
        with pytest.raises(CourseNotFoundError):
            service.get_course_by_code(University.CARLETON, "COMP9999")

    def test_raises_for_unsupported_university(self, service_with_mocked_providers):
        """Test raises UniversityNotSupportedError."""
        service, _, _ = service_with_mocked_providers
        with pytest.raises(UniversityNotSupportedError):
            service.get_course_by_code(Mock(), "COMP1005")


class TestSearchCourses:
    """Tests for search_courses method."""

    def test_returns_search_result(self, service_with_mocked_providers):
        """Test search_courses returns SearchResult."""
        service, _, _ = service_with_mocked_providers
        result = service.search_courses(University.CARLETON, "discrete")
        assert isinstance(result, SearchResult)
        assert result.query == "discrete"
        assert result.university == University.CARLETON

    def test_with_subject_filter(self, service_with_mocked_providers):
        """Test search_courses with subject filter."""
        service, mock_carleton, _ = service_with_mocked_providers
        mock_carleton.search_courses.return_value = SearchResult(
            university=University.CARLETON,
            query="discrete",
            subject_filter="COMP",
            total_found=1,
            courses=[],
        )
        result = service.search_courses(University.CARLETON, "discrete", "COMP")
        assert result.subject_filter == "COMP"

    def test_raises_for_unsupported_university(self, service_with_mocked_providers):
        """Test raises UniversityNotSupportedError."""
        service, _, _ = service_with_mocked_providers
        with pytest.raises(UniversityNotSupportedError):
            service.search_courses(Mock(), "query")


class TestGetCourseStatistics:
    """Tests for get_course_statistics method."""

    def test_returns_statistics_dict(self, service_with_mocked_providers):
        """Test get_course_statistics returns dict with stats."""
        service, _, _ = service_with_mocked_providers
        stats = service.get_course_statistics(University.CARLETON)
        assert isinstance(stats, dict)
        assert "total_subjects" in stats
        assert "total_courses" in stats
        assert stats["university"] == "carleton"

    def test_statistics_contain_expected_keys(self, service_with_mocked_providers):
        """Test statistics dict has all expected keys."""
        service, _, _ = service_with_mocked_providers
        stats = service.get_course_statistics(University.CARLETON)
        expected_keys = [
            "university",
            "total_subjects",
            "total_courses",
            "subjects_with_courses",
            "average_courses_per_subject",
            "credit_distribution",
            "subject_distribution",
        ]
        for key in expected_keys:
            assert key in stats

    def test_statistics_values_are_correct(self, service_with_mocked_providers):
        """Test statistics values are calculated correctly."""
        service, _, _ = service_with_mocked_providers
        stats = service.get_course_statistics(University.CARLETON)
        assert stats["total_subjects"] == 2
        assert stats["total_courses"] == 2


class TestValidateUniversityString:
    """Tests for validate_university_string method."""

    def test_validate_uottawa_variations(self, service_with_mocked_providers):
        """Test validate accepts various UOttawa string formats."""
        service, _, _ = service_with_mocked_providers
        variants = ["uottawa", "ottawa", "University of Ottawa"]
        for variant in variants:
            result = service.validate_university_string(variant)
            assert result == University.UOTTAWA

    def test_validate_carleton_variations(self, service_with_mocked_providers):
        """Test validate accepts various Carleton string formats."""
        service, _, _ = service_with_mocked_providers
        variants = ["carleton", "Carleton University"]
        for variant in variants:
            result = service.validate_university_string(variant)
            assert result == University.CARLETON

    def test_validate_raises_for_invalid(self, service_with_mocked_providers):
        """Test validate raises for invalid university string."""
        service, _, _ = service_with_mocked_providers
        with pytest.raises(UniversityNotSupportedError):
            service.validate_university_string("mcmaster")

    def test_validate_case_insensitive(self, service_with_mocked_providers):
        """Test validate is case insensitive."""
        service, _, _ = service_with_mocked_providers
        result = service.validate_university_string("CARLETON")
        assert result == University.CARLETON

    def test_validate_direct_enum_value(self, service_with_mocked_providers):
        """Test validate accepts direct enum values."""
        service, _, _ = service_with_mocked_providers
        result = service.validate_university_string("carleton")
        assert result == University.CARLETON
