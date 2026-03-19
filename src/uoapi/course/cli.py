"""
Course CLI module providing command-line interface for course operations.
"""

import argparse
from typing import List

# CLI metadata
help = "Query course information"
description = "Retrieve course catalog and information"
epilog = "Use subjects to list available subjects"


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for course CLI."""
    parser = argparse.ArgumentParser(
        prog="course",
        description=description,
        epilog=epilog,
    )
    parser.add_argument(
        "command",
        choices=["subjects"],
        help="Course command to execute",
    )
    return parser


parser = create_parser()


def main(args: List[str] | None = None) -> int:
    """
    Main entry point for course CLI.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parsed_args = parser.parse_args(args)

    try:
        if parsed_args.command == "subjects":
            from uoapi.course.course_info import scrape_subjects

            subjects = scrape_subjects("https://catalogue.uottawa.ca/en/courses/")
            print(f"Found {len(subjects)} subjects")
            for subject in subjects[:10]:  # Show first 10
                print(f"  {subject['subject_code']}: {subject['subject']}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


# CLI function alias
cli = main
