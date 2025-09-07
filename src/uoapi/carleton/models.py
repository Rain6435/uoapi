"""
Data models for Carleton University course discovery
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class MeetingTime:
    """Course meeting time information"""

    start_date: str
    end_date: str
    days: str
    start_time: str
    end_time: str


@dataclass
class ComponentInstance:
    """Individual component instance (e.g., specific tutorial A1, A2)"""
    
    crn: str
    instructor: str
    status: str
    meeting_times: List[MeetingTime]
    notes: List[str] = None
    
    def __post_init__(self):
        if self.notes is None:
            self.notes = []


@dataclass
class CourseComponent:
    """Course component (Lecture or Tutorial with options)"""
    
    component_type: str  # "Lecture" or "Tutorial"
    
    # For Lecture: single instance
    crn: str = ""
    instructor: str = ""
    status: str = ""
    credits: float = 0.0
    meeting_times: List[MeetingTime] = None
    notes: List[str] = None
    
    # For Tutorial: multiple choices
    choices: Dict[str, ComponentInstance] = None
    
    def __post_init__(self):
        if self.meeting_times is None:
            self.meeting_times = []
        if self.notes is None:
            self.notes = []
        if self.choices is None:
            self.choices = {}


@dataclass
class CourseSection:
    """Course section with components structure"""
    
    section: str
    components: Dict[str, CourseComponent]  # "Lecture", "Tutorial", etc.


@dataclass
class Course:
    """Complete course information with new section structure"""

    course_code: str
    subject_code: str
    course_number: str
    catalog_title: str
    catalog_credits: float
    is_offered: bool
    sections_found: int
    banner_title: str
    banner_credits: float
    sections: Dict[str, CourseSection]  # {"A": CourseSection, "B": CourseSection, ...}
    error: bool
    error_message: str


@dataclass
class TermResult:
    """Results for a complete term discovery"""

    term_code: str
    term_name: str
    session_id: str
    total_subjects_available: int
    subjects_tested: int
    total_courses_tested: int
    courses_offered: int
    errors: int
    processing_time_seconds: float
    offering_rate_percent: float
    subject_statistics: Dict[str, Any]
    courses: List[Course]
    processed_at: str


def to_json_serializable(obj):
    """Convert dataclass objects to JSON-serializable format"""
    if hasattr(obj, "__dataclass_fields__"):
        return {
            field.name: to_json_serializable(getattr(obj, field.name))
            for field in obj.__dataclass_fields__.values()
        }
    elif isinstance(obj, list):
        return [to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: to_json_serializable(value) for key, value in obj.items()}
    else:
        return obj


def format_output(data, messages=None):
    """Format output in uoapi standard format"""
    if messages is None:
        messages = []

    return {"data": to_json_serializable(data) if data else [], "messages": messages}
