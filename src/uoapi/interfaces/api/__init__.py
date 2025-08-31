"""
API interface for the uoapi package.

This module provides the FastAPI-based REST API interface
using the service layer architecture.
"""

from .app import create_app

__all__ = ["create_app"]
