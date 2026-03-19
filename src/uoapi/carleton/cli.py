"""
Carleton University CLI module providing command-line interface for Carleton operations.
"""

import argparse
from typing import List

# CLI metadata
help = "Carleton University course operations"
description = "Query course and timetable data from Carleton University"
epilog = "Use discover to find available courses"


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for Carleton CLI."""
    parser = argparse.ArgumentParser(
        prog="carleton",
        description=description,
        epilog=epilog,
    )
    parser.add_argument(
        "command",
        choices=["discover"],
        help="Carleton command to execute",
    )
    return parser


parser = create_parser()


def main(args: List[str] | None = None) -> int:
    """
    Main entry point for Carleton CLI.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parsed_args = parser.parse_args(args)

    try:
        if parsed_args.command == "discover":
            from .discovery import CarletonDiscovery

            discovery = CarletonDiscovery()
            terms = discovery.get_available_terms()
            print(f"Available terms: {len(terms)}")
            for code, name in terms[:5]:  # Show first 5
                print(f"  {code}: {name}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


# CLI function alias
cli = main
