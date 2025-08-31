"""
Schedulo API (uoapi) - University course data access API.

This package provides a command-line interface and Python API for accessing
course information from the University of Ottawa and Carleton University.

The package now features a clean layered architecture with:
- Core domain models and interfaces
- University-specific implementations
- Business logic services
- CLI and API interfaces
- Shared utilities

For backward compatibility, the old module structure is still available.
New code should use the new architecture via the core, services, and interfaces modules.
"""

import importlib
import os
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

# Legacy CLI tools for backward compatibility
from . import cli_tools

# Backward compatibility: dynamically load old modules
try:
    with open(cli_tools.absolute_path("__modules__"), "r") as f:
        legacy_modules: List[str] = [x.strip() for x in f.readlines()]

    # Load legacy modules for backward compatibility
    for mod in legacy_modules:
        try:
            globals()[mod] = importlib.import_module("uoapi." + mod)
        except ImportError as e:
            # Skip modules that can't be imported (may have been refactored)
            pass

    from . import cli

except Exception:
    # If legacy loading fails, continue with just new architecture
    legacy_modules = []

# Export new architecture
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
    # Legacy compatibility
    "cli_tools",
    "cli",
] + legacy_modules
