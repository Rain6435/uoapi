"""
Carleton University module for uoapi

Provides course discovery and timetable information from Carleton University
"""

from uoapi.carleton.discovery import CarletonDiscovery  # noqa: F401
from uoapi.carleton.models import (  # noqa: F401
    Course,
    CourseSection,
    MeetingTime,
    TermResult,
)
from uoapi.carleton.cli import (  # noqa: F401
    parser,
    cli,
    main as py_cli,
    help as cli_help,
    description as cli_description,
    epilog as cli_epilog,
)
