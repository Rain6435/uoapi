"""
CLI utilities and decorators for the uoapi application.

This module provides decorators and utility functions for building
command-line interfaces consistently across all university modules.
"""

import os
import argparse
import functools as ft
from typing import Callable, Any, Optional, Union, List

###############################################################################
#               UTILITIES
###############################################################################


def absolute_path(path: str) -> str:
    """
    Get absolute path relative to this module's directory.

    Args:
        path: Relative path from the module directory

    Returns:
        Absolute path to the specified location
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


def make_parser(**kwargs) -> Callable:
    """
    Decorator to create argument parser configuration functions.

    This decorator allows modules to define their argument parser
    configuration in a standardized way that integrates with the
    main CLI system.

    Args:
        **kwargs: Keyword arguments passed to ArgumentParser constructor

    Returns:
        Decorator function for parser configuration
    """

    def parser_decorator(function: Callable) -> Callable:
        @ft.wraps(function)
        def parser(
            default: Optional[argparse.ArgumentParser] = None,
        ) -> argparse.ArgumentParser:
            if default is None:
                default = argparse.ArgumentParser(**kwargs)
            return function(default)

        return parser

    return parser_decorator


def make_cli(default_parser: Callable) -> Callable:
    """
    Decorator to create CLI command functions.

    This decorator standardizes how CLI commands parse arguments
    and handle different input types (string, list, or parsed args).

    Args:
        default_parser: Function that returns an ArgumentParser

    Returns:
        Decorator function for CLI commands
    """

    def cli_decorator(function: Callable) -> Callable:
        @ft.wraps(function)
        def cli(args: Union[str, List[str], argparse.Namespace, None] = None) -> Any:
            if isinstance(args, str):
                args = args.split()
            if isinstance(args, list):
                args = default_parser().parse_args(args)
            elif args is None:
                args = default_parser().parse_args()
            elif not isinstance(args, argparse.Namespace):
                raise TypeError("Argument is not a str, list, or namespace")
            return function(args)

        return cli

    return cli_decorator


@make_parser()
def default_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Default parser configuration that does nothing.

    This is used as a fallback when modules don't provide
    their own parser configuration.

    Args:
        parser: ArgumentParser to configure

    Returns:
        The same parser unchanged
    """
    return parser


def noop(*args, **kwargs) -> None:
    """
    No-operation function.

    Used as a default function for CLI commands that don't
    provide their own implementation.

    Args:
        *args: Any positional arguments (ignored)
        **kwargs: Any keyword arguments (ignored)
    """
    pass
