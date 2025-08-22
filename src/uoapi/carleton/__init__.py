"""
Carleton University module for uoapi

Provides course discovery and timetable information from Carleton University
"""

from uoapi.carleton.discovery import CarletonDiscovery
from uoapi.carleton.models import Course, CourseSection, MeetingTime, TermResult
from uoapi.carleton.cli import (
    parser,
    cli,
    main as py_cli,
    help as cli_help,
    description as cli_description,
    epilog as cli_epilog,
)
