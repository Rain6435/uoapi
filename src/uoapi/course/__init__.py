from uoapi.course import patterns  # noqa: F401
from uoapi.course.prereq import Prereq  # noqa: F401
from uoapi.course.course_info import scrape_subjects, get_courses  # noqa: F401
from uoapi.course.cli import (  # noqa: F401
    parser,
    cli,
    main as py_cli,
    help as cli_help,
    description as cli_description,
    epilog as cli_epilog,
)
