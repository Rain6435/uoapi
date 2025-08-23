"""
CLI interface for Carleton University course discovery
"""

import sys
import json
import argparse
import logging
from typing import Optional

from uoapi.cli_tools import make_parser, make_cli
from .discovery import CarletonDiscovery
from .models import format_output

logger = logging.getLogger(__name__)

# CLI metadata
help = "Query course information from Carleton University"
description = (
    "Discover course offerings, subjects, and detailed timetable information "
    "from Carleton University's course registration system. "
    "You can query available terms, subjects for a term, or specific courses."
)
epilog = (
    "Examples:\n"
    "  uoapi carleton --available-terms\n"
    "  uoapi carleton --term fall --year 2025 --subjects\n"
    "  uoapi carleton --term fall --year 2025 --courses COMP MATH\n"
    "  uoapi carleton --term fall --year 2025 --courses COMP --limit 5"
)


@make_parser(description=description, epilog=epilog)
def parser(default: argparse.ArgumentParser):
    """Configure command line arguments"""

    # Action selection (mutually exclusive)
    action_group = default.add_mutually_exclusive_group(required=True)

    action_group.add_argument(
        "-a", "--available-terms", action="store_true", help="List all available terms"
    )

    action_group.add_argument(
        "-s",
        "--subjects",
        action="store_true",
        help="List available subjects for the specified term",
    )

    action_group.add_argument(
        "-c",
        "--courses",
        nargs="*",
        metavar="SUBJ",
        help="Query courses for specified subjects (or all subjects if none given)",
    )

    # Term specification
    default.add_argument(
        "--term",
        "-t",
        choices=["winter", "summer", "fall"],
        help="Term to query (required for --subjects and --courses)",
    )

    default.add_argument(
        "--year", "-y", type=int, help="Year to query (required for --subjects and --courses)"
    )

    # Options
    default.add_argument(
        "--limit",
        "-l",
        type=int,
        default=10,
        help="Maximum courses per subject to query (default: 10)",
    )

    default.add_argument(
        "--workers", "-w", type=int, default=4, help="Number of parallel workers (default: 4)"
    )

    default.add_argument("--cookie-file", help="Path to cookie file for Banner authentication")

    return default


def term_name_to_code(term: str, year: int) -> Optional[str]:
    """Convert term name and year to Carleton term code"""
    # Carleton uses format: YYYYST where S=season, T=term
    # Summer: 20, Fall: 30, Winter: 10 (next year)

    term_lower = term.lower()
    if term_lower == "summer":
        return f"{year}20"
    elif term_lower == "fall":
        return f"{year}30"
    elif term_lower == "winter":
        return f"{year}10"
    else:
        return None


def term_code_to_name(term_code: str) -> str:
    """Convert Carleton term code to readable name"""
    if not term_code or len(term_code) < 6:
        return term_code

    year = term_code[:4]
    season_code = term_code[4:6]

    if season_code == "20":
        return f"Summer {year} (May-August)"
    elif season_code == "30":
        return f"Fall {year} (September-December)"
    elif season_code == "10":
        return f"Winter {year} (January-April)"
    else:
        return f"Term {term_code}"


@make_cli(parser)
def cli(args=None):
    """Main CLI function"""
    if args is None:
        logger.error("No arguments received")
        sys.exit(1)

    # Initialize discovery system
    try:
        discovery = CarletonDiscovery(max_workers=args.workers, cookie_file=args.cookie_file)
    except Exception as e:
        output = format_output(None, [{"type": "error", "message": f"Failed to initialize: {e}"}])
        print(json.dumps(output))
        sys.exit(1)

    # Handle available terms
    if args.available_terms:
        try:
            terms = discovery.get_available_terms()

            # Format terms for output
            formatted_terms = []
            for term_code, term_name in terms:
                formatted_terms.append(
                    {
                        "term_code": term_code,
                        "term_name": term_name,
                        "year": int(term_code[:4]) if len(term_code) >= 4 else None,
                        "season": term_name.split()[0] if term_name else None,
                    }
                )

            output = format_output(
                {"available_terms": formatted_terms},
                [{"type": "info", "message": f"Found {len(terms)} available terms"}],
            )
            print(json.dumps(output))
            return

        except Exception as e:
            output = format_output(
                None, [{"type": "error", "message": f"Failed to get available terms: {e}"}]
            )
            print(json.dumps(output))
            sys.exit(1)

    # Validate term and year for other actions
    if not args.term or not args.year:
        output = format_output(
            None, [{"type": "error", "message": "Term and year are required for this action"}]
        )
        print(json.dumps(output))
        sys.exit(1)

    # Convert term and year to term code
    term_code = term_name_to_code(args.term, args.year)
    if not term_code:
        output = format_output(None, [{"type": "error", "message": f"Invalid term: {args.term}"}])
        print(json.dumps(output))
        sys.exit(1)

    # Handle subjects listing
    if args.subjects:
        try:
            subjects, session_id = discovery.discover_subjects(term_code)

            output = format_output(
                {
                    "term_code": term_code,
                    "term_name": term_code_to_name(term_code),
                    "session_id": session_id,
                    "subjects": sorted(subjects),
                    "total_subjects": len(subjects),
                },
                [
                    {
                        "type": "info",
                        "message": f"Found {len(subjects)} subjects for {term_code_to_name(term_code)}",
                    }
                ],
            )
            print(json.dumps(output))
            return

        except Exception as e:
            output = format_output(
                None, [{"type": "error", "message": f"Failed to get subjects: {e}"}]
            )
            print(json.dumps(output))
            sys.exit(1)

    # Handle courses query
    if args.courses is not None:
        try:
            # If no subjects specified, query all available subjects
            if not args.courses:
                subjects, _ = discovery.discover_subjects(term_code)
                query_subjects = list(subjects)
                messages = [{"type": "info", "message": f"Querying all {len(subjects)} subjects"}]
            else:
                query_subjects = [s.upper() for s in args.courses]
                messages = [
                    {"type": "info", "message": f"Querying subjects: {', '.join(query_subjects)}"}
                ]

            # Discover courses
            courses = discovery.discover_courses(
                term_code, subjects=query_subjects, max_courses_per_subject=args.limit
            )

            # Calculate statistics
            offered_courses = [c for c in courses if c.is_offered]
            error_courses = [c for c in courses if c.error]

            # Group by subject for statistics
            subject_stats = {}
            for course in courses:
                subject = course.subject_code
                if subject not in subject_stats:
                    subject_stats[subject] = {"total": 0, "offered": 0, "errors": 0}
                subject_stats[subject]["total"] += 1
                if course.is_offered:
                    subject_stats[subject]["offered"] += 1
                if course.error:
                    subject_stats[subject]["errors"] += 1

            messages.append(
                {
                    "type": "info",
                    "message": (
                        f"Found {len(offered_courses)}/{len(courses)} courses offered "
                        f"({len(offered_courses) / max(1, len(courses)) * 100:.1f}%)"
                    ),
                }
            )

            if error_courses:
                messages.append(
                    {"type": "warning", "message": f"{len(error_courses)} courses had errors"}
                )

            output = format_output(
                {
                    "term_code": term_code,
                    "term_name": term_code_to_name(term_code),
                    "subjects_queried": query_subjects,
                    "total_courses": len(courses),
                    "courses_offered": len(offered_courses),
                    "courses_with_errors": len(error_courses),
                    "offering_rate_percent": len(offered_courses) / max(1, len(courses)) * 100,
                    "subject_statistics": subject_stats,
                    "courses": courses,
                },
                messages,
            )
            print(json.dumps(output))
            return

        except Exception as e:
            output = format_output(
                None, [{"type": "error", "message": f"Failed to discover courses: {e}"}]
            )
            print(json.dumps(output))
            sys.exit(1)


def main(args):
    """Alternative entry point for direct usage"""
    return cli(args)


if __name__ == "__main__":
    cli()
