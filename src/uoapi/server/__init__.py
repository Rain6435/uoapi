"""
FastAPI server module for serving course data via HTTP API.
"""

from .app import create_app  # noqa: F401
from .cli import main  # noqa: F401

__all__ = ["create_app", "main"]
