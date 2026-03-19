"""Pytest configuration and fixtures for Schedulo API tests."""

import sys
from unittest.mock import MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock problematic legacy modules BEFORE importing anything from uoapi
# These modules don't exist in the REST API architecture but are needed by legacy tests
removed_modules = [
    'uoapi.course.cli',
    'uoapi.carleton.cli',
    'uoapi.discovery.cli',
    'uoapi.server.cli',
    'uoapi.timetable.cli',
]

for module in removed_modules:
    sys.modules[module] = MagicMock()

import pytest


@pytest.fixture
def mock_carleton_provider():
    """Create mock Carleton provider."""
    from unittest.mock import Mock
    from uoapi.core.models import University, Subject, Course, SearchResult

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
    ]
    return provider


@pytest.fixture
def mock_uottawa_provider():
    """Create mock UOttawa provider."""
    from unittest.mock import Mock
    from uoapi.core.models import University, Subject, Course

    provider = Mock()
    provider.get_subjects.return_value = [
        Subject(name="Computer Science", code="CSI", university=University.UOTTAWA),
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
    return provider
