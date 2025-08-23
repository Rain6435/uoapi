import json
import sys
from uoapi.rmp import get_teachers_ratings_by_school
from uoapi.cli_tools import make_parser, make_cli

description = "A tool for querying Rate My Professor ratings"
help = (
    "Provide --school (-s) with school name and optionally "
    "--professors (-p) with professor names."
)
epilog = "Supported schools: University of Ottawa, Carleton University"


@make_parser(description=description, epilog=epilog)
def parser(default):
    default.add_argument(
        "-s",
        "--school",
        action="store",
        required=True,
        help=(
            "School name (University of Ottawa, Carleton University, "
            "uottawa, carleton)"
        ),
    )
    default.add_argument(
        "-p",
        "--professors",
        action="store",
        nargs="*",
        help="Professor names in format 'FirstName LastName' (optional)",
    )
    return default


@make_cli(parser)
def cli(args=None):
    if args is None:
        print("Did not receive any arguments", file=sys.stderr)
        sys.exit(1)
    for out in main(args.school, args.professors):
        print(json.dumps(out, indent=2))


def main(school=None, professors=None):
    if not school:
        return

    professor_tuples = []
    if professors:
        for prof in professors:
            parts = prof.split()
            if len(parts) >= 2:
                first_name = parts[0]
                last_name = " ".join(parts[1:])
                professor_tuples.append((first_name, last_name))

    yield get_teachers_ratings_by_school(school, professor_tuples)


if __name__ == "__main__":
    cli()
