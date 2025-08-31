"""
Unified data models for university course information.

This module defines common Pydantic models used across all university
implementations, providing a consistent interface for course data.
"""

from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class University(str, Enum):
    """Supported universities."""

    UOTTAWA = "uottawa"
    CARLETON = "carleton"


class Subject(BaseModel):
    """
    Represents a subject/department at a university.

    Attributes:
        name: Full name of the subject (e.g., "Computer Science")
        code: Short code for the subject (e.g., "CSI", "COMP")
        university: Which university this subject belongs to
        url: Optional URL to the subject's course listing page
    """

    name: str = Field(..., description="Full name of the subject")
    code: str = Field(..., description="Short code identifier")
    university: University = Field(
        ..., description="University this subject belongs to"
    )
    url: Optional[str] = Field(None, description="URL to course listing")


class MeetingTime(BaseModel):
    """
    Represents when a course section meets.

    Attributes:
        start_date: Start date of the meeting period
        end_date: End date of the meeting period
        days: Days of the week (e.g., "MWF", "TTh")
        start_time: Start time (e.g., "08:30")
        end_time: End time (e.g., "10:00")
    """

    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    days: Optional[str] = Field(None, description="Days of the week")
    start_time: Optional[str] = Field(None, description="Start time (HH:MM)")
    end_time: Optional[str] = Field(None, description="End time (HH:MM)")


class CourseSection(BaseModel):
    """
    Represents a specific section of a course.

    Attributes:
        crn: Course Reference Number (unique identifier)
        section: Section identifier (e.g., "A", "001")
        status: Enrollment status (e.g., "Open", "Closed", "Wait List")
        credits: Number of credits for this section
        schedule_type: Type of schedule (e.g., "Lecture", "Laboratory", "Tutorial")
        instructor: Name of the instructor
        meeting_times: List of meeting times for this section
        notes: Additional notes about the section
        capacity: Maximum enrollment capacity
        enrolled: Currently enrolled students
        remaining: Remaining spots available
    """

    crn: str = Field(..., description="Course Reference Number")
    section: str = Field(..., description="Section identifier")
    status: str = Field(..., description="Enrollment status")
    credits: float = Field(..., description="Number of credits", ge=0)
    schedule_type: str = Field(..., description="Type of schedule")
    instructor: str = Field(default="TBA", description="Instructor name")
    meeting_times: List[MeetingTime] = Field(
        default_factory=list, description="Meeting times"
    )
    notes: List[str] = Field(default_factory=list, description="Section notes")
    capacity: Optional[int] = Field(None, description="Maximum enrollment", ge=0)
    enrolled: Optional[int] = Field(None, description="Currently enrolled", ge=0)
    remaining: Optional[int] = Field(None, description="Remaining spots", ge=0)


class Course(BaseModel):
    """
    Represents a university course.

    This unified model combines information from course catalogs and
    live timetable data to provide a complete picture of a course.

    Attributes:
        course_code: Full course code (e.g., "CSI3140", "COMP 1005")
        subject_code: Subject code portion (e.g., "CSI", "COMP")
        course_number: Course number portion (e.g., "3140", "1005")
        title: Human-readable course title
        description: Detailed course description
        credits: Number of academic credits
        university: Which university offers this course
        components: List of course components (e.g., ["Lecture", "Laboratory"])
        prerequisites: Text description of prerequisites
        prerequisite_courses: Parsed list of prerequisite course codes
        sections: List of course sections (for live data)
        is_offered: Whether the course is currently being offered
        last_updated: When this information was last updated
    """

    course_code: str = Field(..., description="Full course identifier")
    subject_code: str = Field(..., description="Subject code")
    course_number: str = Field(..., description="Course number")
    title: str = Field(..., description="Course title")
    description: str = Field(default="", description="Course description")
    credits: Union[int, float, str] = Field(..., description="Number of credits")
    university: University = Field(..., description="University offering this course")

    # Catalog information
    components: List[str] = Field(default_factory=list, description="Course components")
    prerequisites: str = Field(default="", description="Prerequisites text")
    prerequisite_courses: List[str] = Field(
        default_factory=list, description="Required course codes"
    )

    # Live timetable information
    sections: List[CourseSection] = Field(
        default_factory=list, description="Course sections"
    )
    is_offered: bool = Field(default=True, description="Currently offered")

    # Metadata
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")

    @validator("course_code")
    def normalize_course_code(cls, v):
        """Normalize course code format."""
        return v.upper().replace(" ", "")

    @validator("subject_code")
    def normalize_subject_code(cls, v):
        """Normalize subject code format."""
        return v.upper()


class Prerequisite(BaseModel):
    """
    Represents course prerequisite information.

    Attributes:
        content: Raw prerequisite text content
        parsed_courses: List of course codes extracted from the text
        conditions: Structured representation of prerequisite logic
    """

    content: str = Field(..., description="Raw prerequisite text")
    parsed_courses: List[str] = Field(
        default_factory=list, description="Extracted course codes"
    )
    conditions: Dict[str, Any] = Field(
        default_factory=dict, description="Structured conditions"
    )

    @classmethod
    def try_parse(cls, text: str) -> Optional["Prerequisite"]:
        """
        Attempt to parse prerequisite information from text.

        Args:
            text: Text that might contain prerequisite information

        Returns:
            Prerequisite instance if found, None otherwise
        """
        if any(
            keyword in text
            for keyword in ["Prerequisite", "Préalable", "prereq", "Prereq"]
        ):
            return cls(content=text)
        return None


class Component(BaseModel):
    """
    Represents a course component (e.g., Lecture, Laboratory, Tutorial).

    Attributes:
        name: Component name (e.g., "Lecture", "Laboratory")
        content: Raw component text content
        hours: Number of hours per week
        required: Whether this component is required
    """

    name: str = Field(..., description="Component name")
    content: str = Field(..., description="Raw component text")
    hours: Optional[float] = Field(None, description="Hours per week", ge=0)
    required: bool = Field(default=True, description="Whether required")

    @classmethod
    def try_parse(cls, text: str) -> Optional["Component"]:
        """
        Attempt to parse component information from text.

        Args:
            text: Text that might contain component information

        Returns:
            Component instance if found, None otherwise
        """
        if any(
            keyword in text for keyword in ["Course Component", "Volet", "component"]
        ):
            return cls(name="Unknown", content=text)
        return None


class SearchResult(BaseModel):
    """
    Represents search results for courses.

    Attributes:
        university: University searched
        query: Search query used
        subject_filter: Subject code filter applied
        total_found: Total number of courses found
        courses: List of matching courses
        metadata: Additional search metadata
    """

    university: University = Field(..., description="University searched")
    query: Optional[str] = Field(None, description="Search query")
    subject_filter: Optional[str] = Field(None, description="Subject filter")
    total_found: int = Field(..., description="Total courses found", ge=0)
    courses: List[Course] = Field(default_factory=list, description="Matching courses")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Search metadata"
    )


class DiscoveryResult(BaseModel):
    """
    Represents results from course discovery operations.

    Attributes:
        term_code: Term code for the discovery
        term_name: Human-readable term name
        university: University discovered
        subjects_queried: List of subject codes queried
        total_courses: Total number of courses processed
        courses_offered: Number of courses currently offered
        courses_with_errors: Number of courses with processing errors
        offering_rate: Percentage of courses being offered
        processing_time: Time taken for discovery
        courses: List of discovered courses
        errors: List of error messages
    """

    term_code: str = Field(..., description="Term identifier")
    term_name: str = Field(..., description="Human-readable term")
    university: University = Field(..., description="University")
    subjects_queried: List[str] = Field(
        default_factory=list, description="Subject codes queried"
    )
    total_courses: int = Field(default=0, description="Total courses", ge=0)
    courses_offered: int = Field(default=0, description="Courses offered", ge=0)
    courses_with_errors: int = Field(default=0, description="Courses with errors", ge=0)
    offering_rate: float = Field(
        default=0.0, description="Offering rate percentage", ge=0, le=100
    )
    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds", ge=0
    )
    courses: List[Course] = Field(
        default_factory=list, description="Discovered courses"
    )
    errors: List[str] = Field(default_factory=list, description="Error messages")
