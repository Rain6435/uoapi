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


class ProgramType(str, Enum):
    """Types of academic programs."""
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    DUAL_LEVEL = "dual_level"


class ProgramDegreeType(str, Enum):
    """Types of degrees/credentials."""
    BACHELOR = "bachelor"
    CERTIFICATE = "certificate"
    DOCTORATE = "doctorate"
    DUAL_DEGREE = "dual_degree"
    GRADUATE_DIPLOMA = "graduate_diploma"
    JURIS_DOCTOR = "juris_doctor"
    LICENTIATE = "licentiate"
    MAJOR = "major"
    MASTER = "master"
    MICROPROGRAM = "microprogram"
    MINOR = "minor"
    ONLINE = "online"
    OPTION = "option"


class Faculty(str, Enum):
    """University faculties."""
    ARTS = "arts"
    EDUCATION = "education"
    ENGINEERING = "engineering"
    HEALTH_SCIENCES = "health_sciences"
    LAW = "law"
    MANAGEMENT = "management"
    MEDICINE = "medicine"
    SCIENCE = "science"
    SOCIAL_SCIENCES = "social_sciences"


class Discipline(str, Enum):
    """Academic disciplines."""
    # Popular disciplines - expand based on full list from programs page
    ACCOUNTING = "accounting"
    ADVANCED_MATERIALS_MANUFACTURING = "advanced_materials_manufacturing"
    AFRICAN_STUDIES = "african_studies"
    ANTHROPOLOGY = "anthropology"
    ART_HISTORY = "art_history"
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    AUDIOLOGY = "audiology"
    BIOCHEMISTRY = "biochemistry"
    BIOINFORMATICS = "bioinformatics"
    BIOLOGY = "biology"
    BIOMEDICAL_ENGINEERING = "biomedical_engineering"
    BIOMEDICAL_SCIENCE = "biomedical_science"
    BIOPHARMACEUTICAL_SCIENCE = "biopharmaceutical_science"
    BIOPHYSICS = "biophysics"
    BIOSTATISTICS = "biostatistics"
    BUSINESS = "business"
    BUSINESS_ANALYTICS = "business_analytics"
    CANADIAN_LAW = "canadian_law"
    CANADIAN_STUDIES = "canadian_studies"
    CELTIC_STUDIES = "celtic_studies"
    CHEMICAL_ENGINEERING = "chemical_engineering"
    CHEMISTRY = "chemistry"
    CINEMA = "cinema"
    CIVIL_ENGINEERING = "civil_engineering"
    CLASSICAL_STUDIES = "classical_studies"
    CLINICAL_SCIENCE_TRANSLATIONAL_MEDICINE = "clinical_science_translational_medicine"
    COMMUNICATION = "communication"
    COMPUTER_ENGINEERING = "computer_engineering"
    COMPUTER_SCIENCE = "computer_science"
    CONFERENCE_INTERPRETING = "conference_interpreting"
    CONFLICT_STUDIES_HUMAN_RIGHTS = "conflict_studies_human_rights"
    EARTH_SCIENCES = "earth_sciences"
    ECONOMICS = "economics"
    ELECTRICAL_ENGINEERING = "electrical_engineering"
    ENGLISH = "english"
    ENGLISH_AS_SECOND_LANGUAGE = "english_as_second_language"
    ENTREPRENEURSHIP = "entrepreneurship"
    ENVIRONMENT = "environment"
    ENVIRONMENTAL_ENGINEERING = "environmental_engineering"
    ENVIRONMENTAL_SCIENCE = "environmental_science"
    ENVIRONMENTAL_SUSTAINABILITY = "environmental_sustainability"
    EPIDEMIOLOGY = "epidemiology"
    ETHICS = "ethics"
    EXPERIMENTAL_MEDICINE = "experimental_medicine"
    FEMINIST_GENDER_STUDIES = "feminist_gender_studies"
    FINANCE = "finance"
    FINE_ARTS = "fine_arts"
    FOOD_NUTRITION = "food_nutrition"
    FRENCH = "french"
    FRENCH_AS_SECOND_LANGUAGE = "french_as_second_language"
    GENETICS = "genetics"
    GEOGRAPHY = "geography"
    GEOLOGY = "geology"
    GEOMATICS_SPATIAL_ANALYSIS = "geomatics_spatial_analysis"
    GERMAN = "german"
    GREEK_ROMAN_STUDIES = "greek_roman_studies"
    HEALTH = "health"
    HEALTH_SYSTEMS = "health_systems"
    HISTORY = "history"
    HUMAN_KINETICS = "human_kinetics"
    HUMAN_RESOURCE_MANAGEMENT = "human_resource_management"
    INDIGENOUS_STUDIES = "indigenous_studies"
    INFORMATION_STUDIES = "information_studies"
    INTERNATIONAL_AFFAIRS = "international_affairs"
    INTERNATIONAL_DEVELOPMENT = "international_development"
    INTERNATIONAL_ECONOMICS_DEVELOPMENT = "international_economics_development"
    INTERNATIONAL_STUDIES = "international_studies"
    ITALIAN = "italian"
    JEWISH_CANADIAN_STUDIES = "jewish_canadian_studies"
    JOURNALISM = "journalism"
    LATIN_AMERICAN_STUDIES = "latin_american_studies"
    LAW = "law"
    LIFE_SCIENCES = "life_sciences"
    LINGUISTICS = "linguistics"
    MANAGEMENT = "management"
    MARKETING = "marketing"
    MATHEMATICS = "mathematics"
    MECHANICAL_ENGINEERING = "mechanical_engineering"
    MEDIA = "media"
    MEDICINE = "medicine"
    MEDIEVAL_RENAISSANCE_STUDIES = "medieval_renaissance_studies"
    MICROBIOLOGY_IMMUNOLOGY = "microbiology_immunology"
    MUSIC = "music"
    NEUROSCIENCE = "neuroscience"
    NURSING = "nursing"
    OCCUPATIONAL_THERAPY = "occupational_therapy"
    OPHTHALMIC_MEDICAL_TECHNOLOGY = "ophthalmic_medical_technology"
    PHILOSOPHY = "philosophy"
    PHYSICS = "physics"
    PHYSIOTHERAPY = "physiotherapy"
    POLITICAL_SCIENCE = "political_science"
    PSYCHOLOGY = "psychology"
    PUBLIC_ADMINISTRATION = "public_administration"
    PUBLIC_HEALTH = "public_health"
    PUBLIC_POLICY = "public_policy"
    RELIGIOUS_STUDIES = "religious_studies"
    RUSSIAN = "russian"
    SECOND_LANGUAGE_TEACHING = "second_language_teaching"
    SOCIAL_IMPACT = "social_impact"
    SOCIAL_WORK = "social_work"
    SOCIOLOGY = "sociology"
    SOFTWARE_ENGINEERING = "software_engineering"
    SPANISH = "spanish"
    SPEECH_LANGUAGE_PATHOLOGY = "speech_language_pathology"
    STATISTICS = "statistics"
    THEATRE = "theatre"
    VISUAL_ARTS = "visual_arts"
    WORLD_CINEMAS = "world_cinemas"
    WRITING = "writing"


class Program(BaseModel):
    """
    Represents an academic program at a university.

    Attributes:
        name: Program name
        code: Optional program code
        url: Optional URL to program details
        university: University offering this program
        level: Program level (undergraduate, graduate, etc.)
        degree_type: Type of degree/credential
        faculty: Faculty offering the program
        discipline: Academic discipline
        description: Program description
        credits_required: Credits required
        duration_years: Typical duration in years
        is_offered: Whether program is currently offered
        last_updated: When information was last updated
    """

    name: str = Field(..., description="Program name")
    code: Optional[str] = Field(None, description="Program code if applicable")
    url: Optional[str] = Field(None, description="URL to program details")
    university: University = Field(..., description="University offering this program")
    level: ProgramType = Field(..., description="Program level")
    degree_type: ProgramDegreeType = Field(..., description="Type of degree/credential")
    faculty: Optional[Faculty] = Field(None, description="Faculty offering the program")
    discipline: Optional[Discipline] = Field(None, description="Academic discipline")
    description: Optional[str] = Field(None, description="Program description")
    credits_required: Optional[Union[int, float]] = Field(None, description="Credits required", ge=0)
    duration_years: Optional[float] = Field(None, description="Typical duration in years", ge=0)
    is_offered: bool = Field(default=True, description="Whether program is currently offered")
    last_updated: Optional[datetime] = Field(None, description="When information was last updated")


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
            return cls(name="Unknown", content=text, hours=None)
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
