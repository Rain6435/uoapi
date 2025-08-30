"""
New main CLI entry point using the service-based architecture.

This module provides the main CLI interface that uses the new
framework and service layer.
"""

import sys
from typing import Optional

from uoapi.interfaces.cli.framework import registry
from uoapi.interfaces.cli.commands.course_command import CourseCommand
from uoapi.interfaces.cli.commands.timetable_command import TimetableCommand
from uoapi.log_config import configure_logging


def register_commands():
    """Register all available CLI commands."""
    # Register core commands
    registry.register(CourseCommand())
    registry.register(TimetableCommand())
    
    # TODO: Add more commands as they're implemented
    # registry.register(DiscoveryCommand())
    # registry.register(RatingCommand())
    # registry.register(ServerCommand())


def create_parser():
    """Create the main argument parser with all commands."""
    register_commands()
    return registry.create_parser()


def main(args: Optional[list] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        args: Command line arguments (uses sys.argv if None)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        parser = create_parser()
        parsed_args = parser.parse_args(args)
        
        # Configure logging
        configure_logging(parsed_args)
        
        # Execute the command
        if hasattr(parsed_args, 'func'):
            parsed_args.func(parsed_args)
            return 0
        else:
            # No command specified, show help
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except SystemExit as e:
        return e.code
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def cli_entry_point():
    """Entry point for the CLI script."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry_point()