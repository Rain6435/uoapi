"""
Discovery module for serving course data from assets.

This module provides access to pre-scraped course data for both
University of Ottawa and Carleton University.
"""

from .discovery_service import get_courses_data, get_available_universities
from .cli import (
    parser,
    cli,
    main as py_cli,
    help as cli_help,
    description as cli_description,
    epilog as cli_epilog,
)

__all__ = [
    "get_courses_data",
    "get_available_universities",
    "parser",
    "cli",
    "py_cli",
    "cli_help",
    "cli_description",
    "cli_epilog",
]
