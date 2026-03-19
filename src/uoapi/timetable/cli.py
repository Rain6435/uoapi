"""
Timetable CLI module providing command-line interface for timetable operations.
"""

import argparse
from typing import Dict, List, Any

from .query_timetable import TimetableQuery, parse_available

# CLI metadata
help = "Query timetable availability and schedule information"
description = "Retrieve timetable data for universities"
epilog = "Use available to list available terms for courses"


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for timetable CLI."""
    parser = argparse.ArgumentParser(
        prog="timetable",
        description=description,
        epilog=epilog,
    )
    parser.add_argument(
        "command",
        choices=["available"],
        help="Timetable command to execute",
    )
    return parser


parser = create_parser()


def available() -> Dict[str, Any]:
    """
    Get available terms for timetable queries.

    Returns:
        Dictionary with available terms information
    """
    try:
        timetable_query = TimetableQuery()
        available_terms = []

        # Parse available terms from the timetable system
        for term_code, term_name in timetable_query.available.items():
            parsed_term = parse_available(term_code)
            if parsed_term:
                available_terms.append(
                    {
                        "year": parsed_term["year"],
                        "term": parsed_term["term"],
                        "code": term_code,
                        "name": term_name,
                    }
                )

        return {"available": available_terms}
    except Exception as e:
        return {"error": str(e), "available": []}


def main(args: List[str] | None = None) -> int:
    """
    Main entry point for timetable CLI.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parsed_args = parser.parse_args(args)

    try:
        if parsed_args.command == "available":
            result = available()
            if "error" in result:
                print(f"Error: {result['error']}")
                return 1
            print(f"Available terms: {len(result.get('available', []))}")
            for term_info in result.get("available", []):
                print(f"  {term_info['code']}: {term_info['name']}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


# CLI function alias
cli = main
