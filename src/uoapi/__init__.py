"""
Schedulo API (uoapi) - University course data access API.

This package provides a command-line interface and Python API for accessing
course information from the University of Ottawa and Carleton University.

The package automatically loads all available university modules and makes
them available for import and CLI usage.
"""

import importlib
import os
from typing import List

from . import cli_tools
from . import log_config
from .__version__ import __version__

# Dynamically load all university modules listed in __modules__
with open(cli_tools.absolute_path("__modules__"), "r") as f:
    modules: List[str] = [x.strip() for x in f.readlines()]

for mod in modules:
    globals()[mod] = importlib.import_module("uoapi." + mod)

from . import cli

__all__ = modules
