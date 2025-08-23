"""
Data models for University of Ottawa course information.

This module defines Pydantic models for representing course data,
subjects, prerequisites, and components from the University of Ottawa.
"""

from typing import List, Optional, Union
from pydantic import (
    BaseModel,
    HttpUrl,
    Field,
)


class Subject(BaseModel):
    """
    Represents a subject/department at the University of Ottawa.

    Attributes:
        subject: Full name of the subject (e.g., "Computer Science")
        subject_code: Short code for the subject (e.g., "CSI")
        link: URL to the subject's course listing page
    """

    subject: str = Field(..., description="Full name of the subject")
    subject_code: str = Field(..., description="Short code identifier")
    link: HttpUrl = Field(..., description="URL to course listing")


class Course(BaseModel):
    """
    Represents a course at the University of Ottawa.

    Attributes:
        course_code: Unique identifier for the course (e.g., "CSI3140")
        title: Human-readable course title
        credits: Number of academic credits for the course
        description: Detailed course description
        components: List of course components (e.g., ["Lecture", "Laboratory"])
        prerequisites: Text description of prerequisites
        dependencies: Parsed prerequisite dependencies as nested lists
    """

    course_code: str = Field(..., description="Course identifier (e.g., CSI3140)")
    title: str = Field(..., description="Course title")
    credits: int = Field(..., description="Number of credits", ge=0)
    description: str = Field(..., description="Course description")
    components: List[str] = Field(default_factory=list, description="Course components")
    prerequisites: str = Field(default="", description="Prerequisites text")
    dependencies: List[List[str]] = Field(default_factory=list, description="Parsed dependencies")


# TODO: Refactor logic in Prereq into this class
class Prerequisite(BaseModel):
    """
    Represents course prerequisite information.

    This model is used to parse and store prerequisite text from
    course descriptions. Future refactoring should move parsing
    logic from the Prereq module into this class.

    Attributes:
        content: Raw prerequisite text content
    """

    content: str = Field(..., description="Raw prerequisite text")

    @classmethod
    def try_parse(cls, string: str) -> Optional["Prerequisite"]:
        """
        Attempt to parse prerequisite information from a string.

        Args:
            string: Text that might contain prerequisite information

        Returns:
            Prerequisite instance if found, None otherwise
        """
        if "Prerequisite" in string or "Préalable" in string:
            return cls(content=string)
        return None


# TODO: Encapsulate component parsing logic in this class
class Component(BaseModel):
    """
    Represents a course component (e.g., Lecture, Laboratory, Tutorial).

    Future refactoring should move component parsing logic into
    this class to centralize component-related functionality.

    Attributes:
        content: Raw component text content
    """

    content: str = Field(..., description="Raw component text")

    @classmethod
    def try_parse(cls, string: str) -> Optional["Component"]:
        """
        Attempt to parse component information from a string.

        Args:
            string: Text that might contain component information

        Returns:
            Component instance if found, None otherwise
        """
        if "Course Component" in string or "Volet" in string:
            return cls(content=string)
        return None
