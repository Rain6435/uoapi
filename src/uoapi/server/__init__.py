"""
FastAPI server module for serving course data via HTTP API.
"""

from .app import create_app
from .cli import cli, main, parser, help, description, epilog

# CLI metadata for main CLI integration
cli_help = help
cli_description = description
cli_epilog = epilog

__all__ = ["create_app", "cli", "main", "parser"]
