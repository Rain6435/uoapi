"""
Simplified tests for Carleton University functionality.

This module tests the basic data models and CLI integration
without requiring complex mocking of the discovery system.
"""

import pytest
import json
from dataclasses import asdict

from uoapi.carleton.models import (
    Course,
    CourseSection,
    MeetingTime,
    TermResult,
    to_json_serializable,
    format_output,
)


class TestCarletonModels:
    """Test Carleton data models and serialization."""

    def test_meeting_time_creation(self):
        """Test MeetingTime dataclass creation."""
        meeting = MeetingTime(
            start_date="2024-01-08",
            end_date="2024-04-05",
            days="MWF",
            start_time="10:05",
            end_time="11:25",
        )
        assert meeting.start_date == "2024-01-08"
        assert meeting.days == "MWF"
        assert meeting.start_time == "10:05"

    def test_course_section_creation(self):
        """Test CourseSection dataclass creation."""
        meeting = MeetingTime(
            start_date="2024-01-08",
            end_date="2024-04-05",
            days="MWF",
            start_time="10:05",
            end_time="11:25",
        )
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=0.5,
            schedule_type="Lecture",
            instructor="Dr. Smith",
            meeting_times=[meeting],
            notes=["Additional requirements"],
        )
        assert section.crn == "12345"
        assert section.status == "Open"
        assert len(section.meeting_times) == 1
        assert section.meeting_times[0].days == "MWF"

    def test_course_creation(self):
        """Test Course dataclass creation."""
        course = Course(
            course_code="COMP1405",
            subject_code="COMP",
            course_number="1405",
            catalog_title="Introduction to Computer Programming",
            catalog_credits=0.5,
            is_offered=True,
            sections_found=3,
            banner_title="Intro Computer Programming",
            banner_credits=0.5,
            sections=[],
            error=False,
            error_message="",
        )
        assert course.course_code == "COMP1405"
        assert course.is_offered is True
        assert course.sections_found == 3

    def test_term_result_creation(self):
        """Test TermResult dataclass creation."""
        term = TermResult(
            term_code="202401",
            term_name="Winter 2024",
            session_id="abc123",
            total_subjects_available=45,
            subjects_tested=45,
            total_courses_tested=2847,
            courses_offered=1923,
            errors=12,
            processing_time_seconds=324.5,
            offering_rate_percent=67.5,
            subject_statistics={},
            courses=[],
            processed_at="2024-01-15T10:30:00Z",
        )
        assert term.term_code == "202401"
        assert term.offering_rate_percent == 67.5
        assert term.errors == 12

    def test_to_json_serializable(self):
        """Test JSON serialization of dataclass objects."""
        meeting = MeetingTime(
            start_date="2024-01-08",
            end_date="2024-04-05",
            days="MWF",
            start_time="10:05",
            end_time="11:25",
        )

        result = to_json_serializable(meeting)
        expected = {
            "start_date": "2024-01-08",
            "end_date": "2024-04-05",
            "days": "MWF",
            "start_time": "10:05",
            "end_time": "11:25",
        }
        assert result == expected

    def test_to_json_serializable_with_list(self):
        """Test JSON serialization with lists."""
        meetings = [
            MeetingTime("2024-01-08", "2024-04-05", "MWF", "10:05", "11:25"),
            MeetingTime("2024-01-08", "2024-04-05", "TR", "14:05", "15:25"),
        ]

        result = to_json_serializable(meetings)
        assert len(result) == 2
        assert result[0]["days"] == "MWF"
        assert result[1]["days"] == "TR"

    def test_format_output(self):
        """Test standard output formatting."""
        data = {"test": "value"}
        messages = ["Success"]

        result = format_output(data, messages)
        expected = {"data": {"test": "value"}, "messages": ["Success"]}
        assert result == expected

    def test_format_output_empty(self):
        """Test output formatting with empty data."""
        result = format_output(None)
        expected = {"data": [], "messages": []}
        assert result == expected


class TestCarletonIntegration:
    """Integration tests for Carleton functionality."""

    @pytest.mark.integration
    def test_cli_integration(self):
        """Test CLI integration with Carleton module."""
        # Test that CLI functions can be imported from carleton package
        from uoapi.carleton import cli, parser

        # Check that functions exist and are callable
        assert callable(cli)
        assert callable(parser)

    @pytest.mark.integration
    def test_discovery_class_exists(self):
        """Test that discovery class can be imported."""
        from uoapi.carleton.discovery import CarletonDiscovery

        # Should be able to create instance
        discovery = CarletonDiscovery()
        assert discovery is not None

        # Should have expected methods
        assert hasattr(discovery, "get_available_terms")
        assert hasattr(discovery, "get_subjects_for_term")
        assert hasattr(discovery, "search_course")

    def test_data_flow_serialization(self):
        """Test complete data flow from models to JSON."""
        # Create a complete course with sections
        meeting = MeetingTime(
            start_date="2024-01-08",
            end_date="2024-04-05",
            days="MWF",
            start_time="10:05",
            end_time="11:25",
        )

        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=0.5,
            schedule_type="Lecture",
            instructor="Dr. Smith",
            meeting_times=[meeting],
            notes=[],
        )

        course = Course(
            course_code="COMP1405",
            subject_code="COMP",
            course_number="1405",
            catalog_title="Introduction to Computer Programming",
            catalog_credits=0.5,
            is_offered=True,
            sections_found=1,
            banner_title="Intro Computer Programming",
            banner_credits=0.5,
            sections=[section],
            error=False,
            error_message="",
        )

        # Test serialization
        serialized = to_json_serializable(course)
        json_str = json.dumps(serialized)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["course_code"] == "COMP1405"
        assert len(parsed["sections"]) == 1
        assert parsed["sections"][0]["crn"] == "12345"

    @pytest.mark.parametrize(
        "course_code,subject,number",
        [
            ("COMP1405", "COMP", "1405"),
            ("MATH1007", "MATH", "1007"),
            ("PHYS1007", "PHYS", "1007"),
        ],
    )
    def test_course_code_parsing(self, course_code, subject, number):
        """Test course code parsing patterns."""
        course = Course(
            course_code=course_code,
            subject_code=subject,
            course_number=number,
            catalog_title="Test Course",
            catalog_credits=0.5,
            is_offered=True,
            sections_found=0,
            banner_title="Test",
            banner_credits=0.5,
            sections=[],
            error=False,
            error_message="",
        )

        assert course.course_code == course_code
        assert course.subject_code == subject
        assert course.course_number == number


if __name__ == "__main__":
    pytest.main([__file__])
