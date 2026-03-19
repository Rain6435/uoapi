"""Unit tests for uoapi.core models."""

import pytest
from datetime import datetime

from uoapi.core.models import (
    University,
    Subject,
    Course,
    CourseSection,
    MeetingTime,
    SearchResult,
    DiscoveryResult,
    Program,
    ProgramType,
    ProgramDegreeType,
    Faculty,
    Discipline,
)




class TestUniversityEnum:
    """Tests for University enum."""

    def test_university_members(self):
        """Test University enum has expected members."""
        assert University.UOTTAWA.value == "uottawa"
        assert University.CARLETON.value == "carleton"

    def test_university_count(self):
        """Test Universe enum has exactly 2 members."""
        assert len(list(University)) == 2

    def test_university_from_string(self):
        """Test creating University from string value."""
        assert University("uottawa") == University.UOTTAWA
        assert University("carleton") == University.CARLETON

    def test_university_string_repr(self):
        """Test University string representation."""
        assert str(University.UOTTAWA) == "University.UOTTAWA"


class TestSubject:
    """Tests for Subject model."""

    def test_subject_creation(self):
        """Test creating a Subject."""
        subject = Subject(
            name="Computer Science",
            code="COMP",
            university=University.CARLETON,
        )
        assert subject.name == "Computer Science"
        assert subject.code == "COMP"
        assert subject.university == University.CARLETON

    def test_subject_with_url(self):
        """Test Subject with optional URL."""
        subject = Subject(
            name="Mathematics",
            code="MATH",
            university=University.CARLETON,
            url="https://example.com/math",
        )
        assert subject.url == "https://example.com/math"

    def test_subject_url_none_by_default(self):
        """Test Subject URL defaults to None."""
        subject = Subject(
            name="Physics",
            code="PHYS",
            university=University.UOTTAWA,
        )
        assert subject.url is None

    def test_subject_required_fields(self):
        """Test Subject requires name, code, and university."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            Subject(name="CS", code="CS")  # Missing university


class TestCourse:
    """Tests for Course model."""

    def test_course_creation(self):
        """Test creating a basic Course."""
        course = Course(
            course_code="COMP1005",
            subject_code="COMP",
            course_number="1005",
            title="Discrete Structures I",
            credits=3,
            university=University.CARLETON,
        )
        assert course.course_code == "COMP1005"
        assert course.subject_code == "COMP"
        assert course.course_number == "1005"
        assert course.title == "Discrete Structures I"
        assert course.credits == 3
        assert course.university == University.CARLETON

    def test_course_code_normalization_uppercase(self):
        """Test course code is uppercased."""
        course = Course(
            course_code="comp1005",
            subject_code="comp",
            course_number="1005",
            title="Test",
            credits=3,
            university=University.CARLETON,
        )
        assert course.course_code == "COMP1005"

    def test_course_code_normalization_spaces(self):
        """Test course code spaces are removed."""
        course = Course(
            course_code="COMP 1005",
            subject_code="COMP",
            course_number="1005",
            title="Test",
            credits=3,
            university=University.CARLETON,
        )
        assert course.course_code == "COMP1005"

    def test_subject_code_normalization(self):
        """Test subject code is uppercased."""
        course = Course(
            course_code="COMP1005",
            subject_code="comp",
            course_number="1005",
            title="Test",
            credits=3,
            university=University.CARLETON,
        )
        assert course.subject_code == "COMP"

    def test_course_with_sections(self):
        """Test Course with course sections."""
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=3,
            schedule_type="Lecture",
        )
        course = Course(
            course_code="COMP1005",
            subject_code="COMP",
            course_number="1005",
            title="Test",
            credits=3,
            university=University.CARLETON,
            sections=[section],
        )
        assert len(course.sections) == 1
        assert course.sections[0].crn == "12345"

    def test_course_with_meeting_times(self):
        """Test CourseSection with meeting times."""
        meeting = MeetingTime(
            start_date="2025-01-06",
            end_date="2025-04-15",
            days="MWF",
            start_time="08:30",
            end_time="10:00",
        )
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=3,
            schedule_type="Lecture",
            meeting_times=[meeting],
        )
        assert len(section.meeting_times) == 1
        assert section.meeting_times[0].days == "MWF"

    def test_course_credits_string(self):
        """Test Course credits can be stored as string."""
        course = Course(
            course_code="COMP1005",
            subject_code="COMP",
            course_number="1005",
            title="Test",
            credits="3 units",
            university=University.CARLETON,
        )
        assert course.credits == "3 units"

    def test_course_with_description(self):
        """Test Course with description."""
        course = Course(
            course_code="COMP1005",
            subject_code="COMP",
            course_number="1005",
            title="Test",
            credits=3,
            description="A test course",
            university=University.CARLETON,
        )
        assert course.description == "A test course"

    def test_course_with_prerequisites(self):
        """Test Course with prerequisite information."""
        course = Course(
            course_code="COMP1005",
            subject_code="COMP",
            course_number="1005",
            title="Test",
            credits=3,
            prerequisites="COMP1004",
            prerequisite_courses=["COMP1004"],
            university=University.CARLETON,
        )
        assert course.prerequisites == "COMP1004"
        assert "COMP1004" in course.prerequisite_courses


class TestCourseSection:
    """Tests for CourseSection model."""

    def test_section_creation(self):
        """Test creating a CourseSection."""
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=3,
            schedule_type="Lecture",
        )
        assert section.crn == "12345"
        assert section.section == "A"
        assert section.status == "Open"
        assert section.credits == 3

    def test_section_credits_validation_ge_zero(self):
        """Test CourseSection credits must be >= 0."""
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=0,
            schedule_type="Lecture",
        )
        assert section.credits == 0

    def test_section_capacity_validation(self):
        """Test CourseSection capacity validation."""
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=3,
            schedule_type="Lecture",
            capacity=30,
        )
        assert section.capacity == 30

    def test_section_capacity_ge_zero(self):
        """Test CourseSection capacity must be >= 0."""
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=3,
            schedule_type="Lecture",
            capacity=0,
        )
        assert section.capacity == 0

    def test_section_with_instructor(self):
        """Test CourseSection with instructor."""
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=3,
            schedule_type="Lecture",
            instructor="Dr. Smith",
        )
        assert section.instructor == "Dr. Smith"

    def test_section_instructor_default_tba(self):
        """Test CourseSection instructor defaults to TBA."""
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=3,
            schedule_type="Lecture",
        )
        assert section.instructor == "TBA"

    def test_section_with_enrollment(self):
        """Test CourseSection with enrollment info."""
        section = CourseSection(
            crn="12345",
            section="A",
            status="Open",
            credits=3,
            schedule_type="Lecture",
            capacity=30,
            enrolled=25,
            remaining=5,
        )
        assert section.capacity == 30
        assert section.enrolled == 25
        assert section.remaining == 5


class TestMeetingTime:
    """Tests for MeetingTime model."""

    def test_meeting_time_creation(self):
        """Test creating a MeetingTime."""
        meeting = MeetingTime(
            start_date="2025-01-06",
            end_date="2025-04-15",
            days="MWF",
            start_time="08:30",
            end_time="10:00",
        )
        assert meeting.start_date == "2025-01-06"
        assert meeting.days == "MWF"
        assert meeting.start_time == "08:30"

    def test_meeting_time_all_optional(self):
        """Test MeetingTime fields are all optional."""
        meeting = MeetingTime()
        assert meeting.start_date is None
        assert meeting.days is None


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_search_result_creation(self):
        """Test creating a SearchResult."""
        result = SearchResult(
            university=University.CARLETON,
            total_found=5,
        )
        assert result.university == University.CARLETON
        assert result.total_found == 5
        assert len(result.courses) == 0

    def test_search_result_with_query(self):
        """Test SearchResult with query."""
        result = SearchResult(
            university=University.CARLETON,
            query="data",
            total_found=3,
        )
        assert result.query == "data"

    def test_search_result_with_courses(self):
        """Test SearchResult with courses."""
        course = Course(
            course_code="COMP1005",
            subject_code="COMP",
            course_number="1005",
            title="Test",
            credits=3,
            university=University.CARLETON,
        )
        result = SearchResult(
            university=University.CARLETON,
            total_found=1,
            courses=[course],
        )
        assert len(result.courses) == 1
        assert result.courses[0].course_code == "COMP1005"


class TestDiscoveryResult:
    """Tests for DiscoveryResult model."""

    def test_discovery_result_creation(self):
        """Test creating a DiscoveryResult."""
        result = DiscoveryResult(
            term_code="202530",
            term_name="Fall 2025",
            university=University.CARLETON,
        )
        assert result.term_code == "202530"
        assert result.term_name == "Fall 2025"
        assert result.university == University.CARLETON

    def test_discovery_result_with_courses(self):
        """Test DiscoveryResult with courses."""
        course = Course(
            course_code="COMP1005",
            subject_code="COMP",
            course_number="1005",
            title="Test",
            credits=3,
            university=University.CARLETON,
        )
        result = DiscoveryResult(
            term_code="202530",
            term_name="Fall 2025",
            university=University.CARLETON,
            total_courses=1,
            courses=[course],
        )
        assert len(result.courses) == 1

    def test_discovery_result_offering_rate(self):
        """Test DiscoveryResult offering rate."""
        result = DiscoveryResult(
            term_code="202530",
            term_name="Fall 2025",
            university=University.CARLETON,
            total_courses=10,
            courses_offered=7,
            offering_rate=70.0,
        )
        assert result.offering_rate == 70.0

    def test_discovery_result_with_errors(self):
        """Test DiscoveryResult with errors."""
        result = DiscoveryResult(
            term_code="202530",
            term_name="Fall 2025",
            university=University.CARLETON,
            total_courses=10,
            courses_with_errors=2,
            errors=["Error 1", "Error 2"],
        )
        assert result.courses_with_errors == 2
        assert len(result.errors) == 2


class TestProgram:
    """Tests for Program model."""

    def test_program_creation(self):
        """Test creating a Program."""
        program = Program(
            name="Bachelor of Computer Science",
            university=University.CARLETON,
            level=ProgramType.UNDERGRADUATE,
            degree_type=ProgramDegreeType.BACHELOR,
        )
        assert program.name == "Bachelor of Computer Science"
        assert program.level == ProgramType.UNDERGRADUATE

    def test_program_with_code(self):
        """Test Program with code."""
        program = Program(
            name="Bachelor of Computer Science",
            code="BCS",
            university=University.CARLETON,
            level=ProgramType.UNDERGRADUATE,
            degree_type=ProgramDegreeType.BACHELOR,
        )
        assert program.code == "BCS"

    def test_program_with_faculty(self):
        """Test Program with faculty."""
        program = Program(
            name="Bachelor of Computer Science",
            university=University.CARLETON,
            level=ProgramType.UNDERGRADUATE,
            degree_type=ProgramDegreeType.BACHELOR,
            faculty=Faculty.ENGINEERING,
        )
        assert program.faculty == Faculty.ENGINEERING

    def test_program_with_discipline(self):
        """Test Program with discipline."""
        program = Program(
            name="Bachelor of Computer Science",
            university=University.CARLETON,
            level=ProgramType.UNDERGRADUATE,
            degree_type=ProgramDegreeType.BACHELOR,
            discipline=Discipline.COMPUTER_SCIENCE,
        )
        assert program.discipline == Discipline.COMPUTER_SCIENCE

    def test_program_credits_required(self):
        """Test Program with credits_required."""
        program = Program(
            name="Bachelor of Computer Science",
            university=University.CARLETON,
            level=ProgramType.UNDERGRADUATE,
            degree_type=ProgramDegreeType.BACHELOR,
            credits_required=120,
        )
        assert program.credits_required == 120

    def test_program_duration(self):
        """Test Program with duration_years."""
        program = Program(
            name="Bachelor of Computer Science",
            university=University.CARLETON,
            level=ProgramType.UNDERGRADUATE,
            degree_type=ProgramDegreeType.BACHELOR,
            duration_years=4.0,
        )
        assert program.duration_years == 4.0

    def test_program_is_offered_default(self):
        """Test Program is_offered defaults to True."""
        program = Program(
            name="Bachelor of Computer Science",
            university=University.CARLETON,
            level=ProgramType.UNDERGRADUATE,
            degree_type=ProgramDegreeType.BACHELOR,
        )
        assert program.is_offered is True

    def test_program_with_last_updated(self):
        """Test Program with last_updated timestamp."""
        now = datetime.now()
        program = Program(
            name="Bachelor of Computer Science",
            university=University.CARLETON,
            level=ProgramType.UNDERGRADUATE,
            degree_type=ProgramDegreeType.BACHELOR,
            last_updated=now,
        )
        assert program.last_updated == now
