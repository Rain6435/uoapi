"""
CLI interface for discovery module - serves course data from assets.
"""

import sys
import json
import argparse
from typing import Dict, Any

from uoapi.cli_tools import make_parser, make_cli
from .discovery_service import (
    get_courses_data,
    get_available_universities,
    get_course_count,
    get_subjects_list,
    search_courses,
)

# CLI metadata
help = "Discover and serve course data from pre-loaded assets"
description = (
    "Access pre-scraped course data for University of Ottawa and Carleton University. "
    "This command serves course information from locally stored JSON files, providing "
    "fast access to comprehensive course catalogs without needing to scrape university websites."
)
epilog = (
    "Examples:\n"
    "  schedulo-api --university uottawa discovery --info\n"
    "  schedulo-api --university carleton discovery --subjects\n"
    "  schedulo-api --university uottawa discovery --courses --subject CSI\n"
    "  schedulo-api --university carleton discovery --search 'computer science'"
)


@make_parser(description=description, epilog=epilog)
def parser(default: argparse.ArgumentParser):
    """Configure command line arguments for discovery module."""

    # Action selection (mutually exclusive)
    action_group = default.add_mutually_exclusive_group(required=True)

    action_group.add_argument(
        "--info",
        action="store_true",
        help="Show university course data information and statistics",
    )

    action_group.add_argument(
        "--subjects", action="store_true", help="List all available subject codes"
    )

    action_group.add_argument(
        "--courses",
        action="store_true",
        help="List courses (optionally filtered by subject)",
    )

    action_group.add_argument(
        "--search", metavar="QUERY", help="Search courses by title or description"
    )

    action_group.add_argument(
        "--raw", action="store_true", help="Output raw JSON data file contents"
    )

    # Options for filtering
    default.add_argument(
        "--subject",
        "-s",
        metavar="CODE",
        help="Filter courses by subject code (use with --courses)",
    )

    default.add_argument(
        "--limit",
        "-l",
        type=int,
        default=50,
        help="Limit number of results (default: 50, 0 for all)",
    )

    return default


@make_cli(parser)
def cli(args=None):
    """Main CLI function for discovery module."""
    if args is None:
        print("Did not receive any arguments", file=sys.stderr)
        sys.exit(1)

    # Check university parameter
    university = getattr(args, "university", None)
    if not university:
        output = {"error": "University parameter is required"}
        print(json.dumps(output))
        sys.exit(1)

    # Check if university data is available
    available_unis = get_available_universities()
    normalized_uni = (
        university.lower().replace(" ", "").replace("university", "").replace("of", "")
    )

    if "ottawa" in normalized_uni:
        target_uni = "uottawa"
    elif "carleton" in normalized_uni:
        target_uni = "carleton"
    else:
        target_uni = normalized_uni

    if target_uni not in available_unis:
        output = {
            "error": f"No course data available for {university}",
            "available_universities": available_unis,
        }
        print(json.dumps(output))
        sys.exit(1)

    try:
        # Execute the requested action
        if args.info:
            output = get_info_output(target_uni)
        elif args.subjects:
            output = get_subjects_output(target_uni)
        elif args.courses:
            output = get_courses_output(target_uni, args.subject, args.limit)
        elif args.search:
            output = get_search_output(target_uni, args.search, args.limit)
        elif args.raw:
            output = get_courses_data(target_uni)
        else:
            output = {"error": "No valid action specified"}

        print(json.dumps(output, indent=2))

    except Exception as e:
        output = {"error": f"Failed to process request: {str(e)}"}
        print(json.dumps(output))
        sys.exit(1)


def get_info_output(university: str) -> Dict[str, Any]:
    """Get information and statistics about university course data."""
    try:
        data = get_courses_data(university)
        course_count = get_course_count(university)
        subjects = get_subjects_list(university)

        info = {
            "university": university,
            "total_courses": course_count,
            "total_subjects": len(subjects),
            "subjects": sorted(subjects),
        }

        # Add metadata if available
        if "metadata" in data:
            info["data_metadata"] = data["metadata"]

        if "discovery_metadata" in data:
            info["discovery_metadata"] = data["discovery_metadata"]

        return {
            "action": "info",
            "data": info,
            "messages": [
                {
                    "type": "info",
                    "message": f"Found {course_count} courses across {len(subjects)} subjects",
                }
            ],
        }

    except Exception as e:
        return {
            "action": "info",
            "error": str(e),
            "messages": [{"type": "error", "message": f"Failed to get info: {str(e)}"}],
        }


def get_subjects_output(university: str) -> Dict[str, Any]:
    """Get list of available subjects."""
    try:
        subjects = get_subjects_list(university)

        return {
            "action": "subjects",
            "data": {
                "university": university,
                "subjects": sorted(subjects),
                "total_subjects": len(subjects),
            },
            "messages": [
                {"type": "info", "message": f"Found {len(subjects)} subjects"}
            ],
        }

    except Exception as e:
        return {
            "action": "subjects",
            "error": str(e),
            "messages": [
                {"type": "error", "message": f"Failed to get subjects: {str(e)}"}
            ],
        }


def get_courses_output(
    university: str, subject_filter: str = None, limit: int = 50
) -> Dict[str, Any]:
    """Get courses, optionally filtered by subject."""
    try:
        courses = search_courses(university, subject_code=subject_filter)

        # Apply limit
        if limit > 0:
            limited_courses = courses[:limit]
        else:
            limited_courses = courses

        messages = [
            {
                "type": "info",
                "message": f"Found {len(courses)} courses"
                + (f" for subject {subject_filter}" if subject_filter else ""),
            }
        ]

        if limit > 0 and len(courses) > limit:
            messages.append(
                {
                    "type": "info",
                    "message": f"Showing first {limit} results (use --limit 0 for all)",
                }
            )

        return {
            "action": "courses",
            "data": {
                "university": university,
                "subject_filter": subject_filter,
                "total_courses": len(courses),
                "courses_shown": len(limited_courses),
                "courses": limited_courses,
            },
            "messages": messages,
        }

    except Exception as e:
        return {
            "action": "courses",
            "error": str(e),
            "messages": [
                {"type": "error", "message": f"Failed to get courses: {str(e)}"}
            ],
        }


def get_search_output(university: str, query: str, limit: int = 50) -> Dict[str, Any]:
    """Search courses by title or description."""
    try:
        courses = search_courses(university, query=query)

        # Apply limit
        if limit > 0:
            limited_courses = courses[:limit]
        else:
            limited_courses = courses

        messages = [
            {
                "type": "info",
                "message": f"Found {len(courses)} courses matching '{query}'",
            }
        ]

        if limit > 0 and len(courses) > limit:
            messages.append(
                {
                    "type": "info",
                    "message": f"Showing first {limit} results (use --limit 0 for all)",
                }
            )

        return {
            "action": "search",
            "data": {
                "university": university,
                "query": query,
                "total_matches": len(courses),
                "courses_shown": len(limited_courses),
                "courses": limited_courses,
            },
            "messages": messages,
        }

    except Exception as e:
        return {
            "action": "search",
            "error": str(e),
            "messages": [
                {"type": "error", "message": f"Failed to search courses: {str(e)}"}
            ],
        }


def main(args):
    """Alternative entry point for direct usage."""
    return cli(args)


if __name__ == "__main__":
    cli()
