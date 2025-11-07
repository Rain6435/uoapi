"""
Schedulo API (uoapi) - University course data access API.

This package provides a REST API server for accessing course information
from the University of Ottawa and Carleton University.

The package features a clean layered architecture with:
- Core domain models and interfaces
- University-specific implementations
- Business logic services
- REST API interface
- Shared utilities

Usage:
    Start the server using the command-line:
        schedulo-server --port 8000

    Or programmatically:
        from uoapi.server.app import create_app
        import uvicorn

        app = create_app()
        uvicorn.run(app, host="127.0.0.1", port=8000)
"""

import importlib
from typing import List

# Import new architecture components
from . import core
from . import universities
from . import services
from . import interfaces
from . import utils

# Import version
from .__version__ import __version__

# Import logging configuration
from . import log_config

# Backward compatibility: dynamically load old modules (non-CLI modules only)
legacy_modules: List[str] = []
legacy_module_names = ["course", "carleton", "timetable", "rmp", "discovery"]

for mod in legacy_module_names:
    try:
        globals()[mod] = importlib.import_module("uoapi." + mod)
        legacy_modules.append(mod)
    except ImportError:
        # Skip modules that can't be imported
        pass

# Export public API
__all__ = [
    # New architecture
    "core",
    "universities",
    "services",
    "interfaces",
    "utils",
    # Version and config
    "__version__",
    "log_config",
] + legacy_modules
