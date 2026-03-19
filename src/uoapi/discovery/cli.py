"""
Discovery CLI module providing command-line interface for discovery operations.
"""

import argparse
from typing import List

# CLI metadata
help = "Discover courses from asset data"
description = "Query course discovery data from pre-scraped assets"
epilog = "Use list to display available universities"


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for discovery CLI."""
    parser = argparse.ArgumentParser(
        prog="discovery",
        description=description,
        epilog=epilog,
    )
    parser.add_argument(
        "command",
        choices=["list"],
        help="Discovery command to execute",
    )
    return parser


parser = create_parser()


def main(args: List[str] | None = None) -> int:
    """
    Main entry point for discovery CLI.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parsed_args = parser.parse_args(args)

    try:
        if parsed_args.command == "list":
            from .discovery_service import get_available_universities

            universities = get_available_universities()
            print(f"Available universities: {', '.join(universities)}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


# CLI function alias
cli = main
