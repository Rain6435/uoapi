"""
Main CLI entry point for the uoapi (Schedulo API) application.

This module provides the main command-line interface for accessing
University of Ottawa and Carleton University course data. It dynamically
loads and configures subcommands from various university modules.
"""

import argparse
from importlib import import_module

from uoapi.cli_tools import absolute_path, default_parser, noop, make_cli
from uoapi.log_config import configure_parser, configure_logging


###############################################################################
#               CONFIGURATION
###############################################################################

# modules = [
#    "example",
# ]
with open(absolute_path("__modules__"), "r") as f:
    modules = [x.strip() for x in f.readlines()]

###############################################################################
#               GLOBAL PARSER AND CLI
###############################################################################


def uoapi_parser() -> argparse.ArgumentParser:
    """
    Create and configure the main argument parser for uoapi.

    This function dynamically loads all available university modules
    and creates subcommands for each one. Each module should provide
    a parser function and cli function for integration.

    Returns:
        argparse.ArgumentParser: Configured parser with all subcommands

    Raises:
        ImportError: If a module listed in __modules__ cannot be imported
    """
    parser = argparse.ArgumentParser()

    # Global arguments
    parser = configure_parser(parser)
    parser.set_defaults(func=noop)

    # Add subparsers
    subparsers = parser.add_subparsers(title="actions")
    for name in modules:
        mod = import_module("uoapi." + name)
        sp = getattr(mod, "parser", default_parser)(
            subparsers.add_parser(
                name,
                description=getattr(mod, "cli_description", ""),
                help=getattr(mod, "cli_help", ""),
                epilog=getattr(mod, "cli_epilog", None),
            )
        )
        sp.set_defaults(func=getattr(mod, "cli", noop))
    return parser


@make_cli(uoapi_parser)
def cli(args=None) -> None:
    """
    Main CLI entry point for the schedulo-api application.

    This function is called when the user runs the `uoapi` command.
    It configures logging and delegates to the appropriate subcommand.

    Args:
        args: Command line arguments (defaults to sys.argv if None)
    """
    configure_logging(args)
    args.func(args)


if __name__ == "__main__":
    cli()
