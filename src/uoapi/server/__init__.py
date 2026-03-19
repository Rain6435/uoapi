"""
FastAPI server module for serving course data via HTTP API.
"""

from .app import create_app  # noqa: F401
from .cli import cli, main, parser, help, description, epilog  # noqa: F401

# CLI metadata for main CLI integration
cli_help = help
cli_description = description
cli_epilog = epilog

__all__ = ["create_app", "cli", "main", "parser"]
