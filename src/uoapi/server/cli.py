"""
CLI interface for the FastAPI server module.
"""

import sys
import json
import argparse
from typing import Any

from uoapi.cli_tools import make_parser, make_cli


# CLI metadata
help = "Start FastAPI server to serve course data via HTTP API"
description = (
    "Launch a FastAPI web server that provides HTTP endpoints for accessing "
    "University of Ottawa and Carleton University course data. The server "
    "provides RESTful API endpoints for querying courses, subjects, and university information."
)
epilog = (
    "Examples:\n"
    "  schedulo-api --university uottawa server --port 8000\n"
    "  schedulo-api --university carleton server --host 0.0.0.0 --port 8080\n"
    "  schedulo-api --university uottawa server --reload --log-level debug\n\n"
    "API Endpoints:\n"
    "  GET /health - Health check\n"
    "  GET /universities - List available universities\n"
    "  GET /universities/{university}/info - University information\n"
    "  GET /universities/{university}/subjects - Available subjects\n"
    "  GET /universities/{university}/courses - Course data with filtering\n\n"
    "Documentation available at /docs and /redoc when server is running"
)


@make_parser(description=description, epilog=epilog)
def parser(default: argparse.ArgumentParser):
    """Configure command line arguments for server module."""

    default.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )

    default.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )

    default.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development mode)",
    )

    default.add_argument(
        "--log-level",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        default="info",
        help="Set the logging level (default: info)",
    )

    default.add_argument(
        "--workers", type=int, default=1, help="Number of worker processes (default: 1)"
    )

    return default


@make_cli(parser)
def cli(args=None):
    """Main CLI function for server module."""
    if args is None:
        print("Did not receive any arguments", file=sys.stderr)
        sys.exit(1)

    try:
        # Import uvicorn here to avoid import errors if not installed
        import uvicorn
    except ImportError:
        print("Error: uvicorn is required to run the server", file=sys.stderr)
        print(
            "Install with: pip install 'schedulo-api[server]' or pip install uvicorn",
            file=sys.stderr,
        )
        sys.exit(1)

    # Check if university data is available
    from uoapi.discovery.discovery_service import get_available_universities

    available_unis = get_available_universities()

    if not available_unis:
        print("Warning: No university data available", file=sys.stderr)
        print(
            "The server will start but some endpoints may not work properly",
            file=sys.stderr,
        )

    print(f"Starting Schedulo API server...")
    print(f"Available universities: {available_unis}")
    print(f"Server will be available at: http://{args.host}:{args.port}")
    print(f"API documentation: http://{args.host}:{args.port}/docs")

    # Configure uvicorn
    config = {
        "app": "uoapi.server.app:create_app",
        "factory": True,
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
        "reload": args.reload,
    }

    # Only add workers if not in reload mode (uvicorn limitation)
    if not args.reload and args.workers > 1:
        config["workers"] = args.workers

    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


def main(args):
    """Alternative entry point for direct usage."""
    return cli(args)


if __name__ == "__main__":
    cli()
