"""
CLI framework providing common patterns and utilities.

This module extracts the common CLI patterns from the existing
cli_tools module and provides a more structured approach.
"""

import os
import sys
import json
import argparse
import functools as ft
from typing import Callable, Any, Optional, Union, List, Dict
from abc import ABC, abstractmethod

from uoapi.core import University, ServiceError, UniversityNotSupportedError
from uoapi.services import (
    DefaultCourseService,
    DefaultTimetableService,
    DefaultRatingService,
    DefaultDiscoveryService,
)


def absolute_path(path: str) -> str:
    """
    Get absolute path relative to this module's directory.
    
    Args:
        path: Relative path from the module directory
        
    Returns:
        Absolute path to the specified location
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


def noop(args):
    """No-operation function for default parser behavior."""
    pass


class CLICommand(ABC):
    """
    Abstract base class for CLI commands.
    
    This class provides a structured way to implement CLI commands
    with consistent argument parsing and execution patterns.
    """
    
    def __init__(self):
        self.course_service = DefaultCourseService()
        self.timetable_service = DefaultTimetableService()
        self.rating_service = DefaultRatingService()
        self.discovery_service = DefaultDiscoveryService()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name."""
        pass
    
    @property
    @abstractmethod
    def help(self) -> str:
        """Short help text."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description."""
        pass
    
    @property
    def epilog(self) -> Optional[str]:
        """Optional epilog text."""
        return None
    
    @abstractmethod
    def configure_parser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Configure the argument parser for this command.
        
        Args:
            parser: Argument parser to configure
            
        Returns:
            Configured parser
        """
        pass
    
    @abstractmethod
    def execute(self, args: argparse.Namespace) -> Any:
        """
        Execute the command with parsed arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Command result (will be JSON-serialized for output)
        """
        pass
    
    def validate_university(self, university_str: str) -> University:
        """
        Validate and convert university string to University enum.
        
        Args:
            university_str: String representation of university
            
        Returns:
            University enum value
            
        Raises:
            UniversityNotSupportedError: If university is not valid
        """
        return self.course_service.validate_university_string(university_str)
    
    def format_output(self, data: Any, messages: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Format output in standard uoapi format.
        
        Args:
            data: Data to output
            messages: Optional status messages
            
        Returns:
            Formatted output dictionary
        """
        return {
            "data": data if data is not None else [],
            "messages": messages or []
        }
    
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle and format errors consistently.
        
        Args:
            error: Exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            Formatted error response
        """
        error_message = str(error)
        if context:
            error_message = f"{context}: {error_message}"
        
        return self.format_output(
            data=None,
            messages=[f"Error: {error_message}"]
        )


class UniversityCommand(CLICommand):
    """
    Base class for commands that operate on a specific university.
    
    This class adds common university-related argument parsing
    and validation functionality.
    """
    
    def configure_parser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """Add university argument to the parser."""
        parser.add_argument(
            "--university",
            "-u",
            choices=["uottawa", "carleton", "University of Ottawa", "Carleton University"],
            required=True,
            help="University to query (required)"
        )
        return self.configure_command_parser(parser)
    
    @abstractmethod
    def configure_command_parser(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Configure command-specific arguments.
        
        Args:
            parser: Parser with university argument already added
            
        Returns:
            Configured parser
        """
        pass
    
    def execute(self, args: argparse.Namespace) -> Any:
        """Execute with university validation."""
        try:
            university = self.validate_university(args.university)
            return self.execute_for_university(args, university)
        except UniversityNotSupportedError as e:
            return self.handle_error(e, "University validation")
        except Exception as e:
            return self.handle_error(e, "Command execution")
    
    @abstractmethod
    def execute_for_university(self, args: argparse.Namespace, university: University) -> Any:
        """
        Execute the command for a specific university.
        
        Args:
            args: Parsed arguments
            university: Validated university enum
            
        Returns:
            Command result
        """
        pass


def make_parser(**kwargs) -> Callable:
    """
    Decorator to create argument parser configuration functions.
    
    This decorator provides backward compatibility with the existing
    CLI system while using the new framework.
    """
    def parser_decorator(function: Callable) -> Callable:
        @ft.wraps(function)
        def parser(default: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
            if default is None:
                default = argparse.ArgumentParser(**kwargs)
            return function(default)
        return parser
    return parser_decorator


def make_cli(parser_func: Callable) -> Callable:
    """
    Decorator to create CLI entry points.
    
    This decorator provides backward compatibility with the existing
    CLI system.
    """
    def cli_decorator(function: Callable) -> Callable:
        @ft.wraps(function)
        def cli(args=None):
            parser = parser_func()
            parsed_args = parser.parse_args(args)
            return function(parsed_args)
        return cli
    return cli_decorator


def default_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Default parser configuration that does nothing."""
    return parser


def output_json(data: Any, indent: Optional[int] = 2):
    """
    Output data as JSON to stdout.
    
    Args:
        data: Data to output
        indent: JSON indentation level
    """
    try:
        json.dump(data, sys.stdout, indent=indent, default=str)
        print()  # Add newline
    except Exception as e:
        print(f"Error formatting output: {e}", file=sys.stderr)
        sys.exit(1)


def output_table(data: List[Dict[str, Any]], columns: List[str], title: Optional[str] = None):
    """
    Output data as a formatted table.
    
    Args:
        data: List of dictionaries to display
        columns: Column names to include
        title: Optional table title
    """
    if not data:
        print("No data to display")
        return
    
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    
    # Calculate column widths
    col_widths = {}
    for col in columns:
        col_widths[col] = len(col)
        for row in data:
            value = str(row.get(col, ""))
            col_widths[col] = max(col_widths[col], len(value))
    
    # Print header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in data:
        row_str = " | ".join(str(row.get(col, "")).ljust(col_widths[col]) for col in columns)
        print(row_str)
    
    print(f"\nTotal: {len(data)} rows")


class CommandRegistry:
    """
    Registry for CLI commands that provides dynamic command loading.
    """
    
    def __init__(self):
        self._commands: Dict[str, CLICommand] = {}
    
    def register(self, command: CLICommand):
        """Register a CLI command."""
        self._commands[command.name] = command
    
    def get_command(self, name: str) -> Optional[CLICommand]:
        """Get a registered command by name."""
        return self._commands.get(name)
    
    def get_all_commands(self) -> Dict[str, CLICommand]:
        """Get all registered commands."""
        return self._commands.copy()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser with all registered commands."""
        parser = argparse.ArgumentParser(
            description="Schedulo API - University course data access"
        )
        
        # Add global arguments
        from uoapi.log_config import configure_parser
        parser = configure_parser(parser)
        
        parser.set_defaults(func=noop)
        
        # Add subparsers for commands
        if self._commands:
            subparsers = parser.add_subparsers(title="commands", dest="command")
            
            for name, command in self._commands.items():
                subparser = subparsers.add_parser(
                    name,
                    help=command.help,
                    description=command.description,
                    epilog=command.epilog
                )
                command.configure_parser(subparser)
                subparser.set_defaults(func=self._execute_command, command_obj=command)
        
        return parser
    
    def _execute_command(self, args: argparse.Namespace):
        """Execute a registered command."""
        try:
            result = args.command_obj.execute(args)
            output_json(result)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user", file=sys.stderr)
            sys.exit(130)
        except Exception as e:
            error_result = {
                "data": None,
                "messages": [f"Unexpected error: {str(e)}"]
            }
            output_json(error_result)
            sys.exit(1)


# Global command registry
registry = CommandRegistry()