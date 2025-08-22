from uoapi.rmp.rate_my_prof import (  # noqa: F401
    get_teachers_ratings_by_school,
    get_professor_ratings,
    get_school_by_name,
    inject_ratings_into_timetable,
    get_instructor_rating,
    parse_instructor_name,
)
from uoapi.rmp.cli import (  # noqa: F401
    parser,
    cli,
    main as py_cli,
    help as cli_help,
    description as cli_description,
    epilog as cli_epilog,
)
