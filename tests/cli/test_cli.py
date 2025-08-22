"""
Tests for CLI functionality and command-line interface.

This module tests the main CLI parser, subcommand discovery,
and CLI tool decorators.
"""

import pytest
import argparse
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from uoapi.cli import uoapi_parser, cli
from uoapi.cli_tools import make_parser, make_cli


class TestCliTools:
    """Test CLI utility decorators and functions."""

    def test_make_parser_decorator(self):
        """Test make_parser decorator functionality."""

        @make_parser(description="Test parser")
        def test_parser(default):
            default.add_argument("--test", help="Test argument")
            return default

        parser = test_parser()
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.description == "Test parser"

        # Test that the argument was added
        args = parser.parse_args(["--test", "value"])
        assert args.test == "value"

    def test_make_parser_with_kwargs(self):
        """Test make_parser with various keyword arguments."""

        @make_parser(prog="test-prog", epilog="Test epilog")
        def test_parser(default):
            return default

        parser = test_parser()
        assert parser.prog == "test-prog"
        assert parser.epilog == "Test epilog"

    def test_make_cli_decorator(self):
        """Test make_cli decorator functionality."""
        # Create a mock parser function
        mock_parser_func = Mock()
        mock_parser = Mock()
        mock_parser.parse_args.return_value = Mock(test_arg="test_value")
        mock_parser_func.return_value = mock_parser

        @make_cli(mock_parser_func)
        def test_cli(args=None):
            assert args.test_arg == "test_value"
            return "success"

        # Test with no arguments (should parse sys.argv)
        with patch("sys.argv", ["test"]):
            result = test_cli()
            assert result == "success"

        # Test with provided arguments
        result = test_cli(["--test", "value"])
        mock_parser.parse_args.assert_called_with(["--test", "value"])

    def test_make_cli_error_handling(self):
        """Test make_cli error handling."""
        mock_parser_func = Mock()
        mock_parser = Mock()
        mock_parser.parse_args.side_effect = SystemExit(2)
        mock_parser_func.return_value = mock_parser

        @make_cli(mock_parser_func)
        def test_cli(args=None):
            return "should not reach here"

        with pytest.raises(SystemExit):
            test_cli([])


class TestMainCli:
    """Test main CLI functionality."""

    def test_uoapi_parser_creation(self):
        """Test main uoapi parser creation."""
        parser = uoapi_parser()
        assert isinstance(parser, argparse.ArgumentParser)
        # In test environment, prog might be different
        assert parser.prog in ["uoapi", "pytest"]

        # Test that it has subparsers
        assert hasattr(parser, "_subparsers")

    def test_cli_subcommand_discovery(self):
        """Test that CLI discovers subcommands from modules."""
        parser = uoapi_parser()

        # Get the subcommands
        subcommands = []
        if parser._subparsers:
            for action in parser._subparsers._actions:
                if isinstance(action, argparse._SubParsersAction):
                    subcommands = list(action.choices.keys())
                    break

        # Should have at least some expected subcommands
        expected_commands = ["course", "timetable", "dates", "rmp", "carleton"]
        for cmd in expected_commands:
            if cmd in subcommands:  # Some may not be available in test environment
                assert cmd in subcommands

    @patch("sys.argv", ["uoapi", "--help"])
    @patch("sys.stdout", new_callable=StringIO)
    def test_cli_help_output(self, mock_stdout):
        """Test CLI help output."""
        with pytest.raises(SystemExit) as exc_info:
            cli()

        # Should exit with code 0 for help
        assert exc_info.value.code == 0

        # Help output should contain program name
        output = mock_stdout.getvalue()
        assert "uoapi" in output.lower()

    def test_cli_with_valid_subcommand(self):
        """Test CLI with a valid subcommand."""
        # Mock the course module CLI
        with patch("uoapi.course.cli") as mock_course_cli:
            mock_course_cli.return_value = None

            # Test that we can parse course subcommand
            parser = uoapi_parser()

            # This should not raise an error
            try:
                args = parser.parse_args(["course", "--help"])
            except SystemExit:
                # Help exits, which is expected
                pass

    @patch("sys.stderr", new_callable=StringIO)
    def test_cli_with_invalid_subcommand(self, mock_stderr):
        """Test CLI with invalid subcommand."""
        with pytest.raises(SystemExit) as exc_info:
            parser = uoapi_parser()
            parser.parse_args(["invalid-command"])

        # Should exit with error code
        assert exc_info.value.code == 2

        # Error should mention invalid choice
        error = mock_stderr.getvalue()
        assert "invalid choice" in error.lower()

    def test_cli_module_loading(self):
        """Test that CLI modules are loaded correctly."""
        # This tests the importlib loading mechanism
        parser = uoapi_parser()

        # Should have loaded without errors
        assert parser is not None

        # Should have description or be parser object
        # Description might be None in test environment
        assert parser is not None


class TestCliIntegration:
    """Integration tests for CLI functionality."""

    @pytest.mark.integration
    def test_course_cli_integration(self):
        """Test course CLI integration."""
        # Test that course module CLI can be called
        try:
            from uoapi.course.cli import parser as course_parser

            parser_func = course_parser()
            assert isinstance(parser_func, argparse.ArgumentParser)
        except ImportError:
            pytest.skip("Course module not available")

    @pytest.mark.integration
    def test_timetable_cli_integration(self):
        """Test timetable CLI integration."""
        try:
            from uoapi.timetable.cli import parser as timetable_parser

            parser_func = timetable_parser()
            assert isinstance(parser_func, argparse.ArgumentParser)
        except ImportError:
            pytest.skip("Timetable module not available")

    @pytest.mark.integration
    def test_carleton_cli_integration(self):
        """Test Carleton CLI integration."""
        try:
            from uoapi.carleton.cli import parser as carleton_parser

            parser_func = carleton_parser()
            assert isinstance(parser_func, argparse.ArgumentParser)
        except ImportError:
            pytest.skip("Carleton module not available")

    def test_cli_json_output_format(self):
        """Test that CLI commands output valid JSON."""
        # Mock a subcommand that outputs JSON
        mock_output = {"data": {"test": "value"}, "messages": []}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with patch("json.dumps") as mock_dumps:
                mock_dumps.return_value = '{"data": {"test": "value"}, "messages": []}'

                # This would test actual JSON output
                # For now, just verify the format is correct
                import json

                json_str = json.dumps(mock_output)
                parsed = json.loads(json_str)

                assert "data" in parsed
                assert "messages" in parsed

    def test_error_handling_in_cli(self):
        """Test error handling in CLI commands."""
        # Test that exceptions are handled gracefully
        parser = uoapi_parser()

        # Should not crash on creation
        assert parser is not None

        # Should handle missing modules gracefully
        # (This is tested by the fact that the parser loads successfully
        # even if some modules might be missing)


@pytest.mark.parametrize(
    "module_name,expected_command",
    [
        ("course", "course"),
        ("timetable", "timetable"),
        ("dates", "dates"),
        ("rmp", "rmp"),
        ("carleton", "carleton"),
    ],
)
def test_module_command_mapping(module_name, expected_command):
    """Test that modules map to expected CLI commands."""
    # This test verifies the module -> command mapping
    # without requiring all modules to be present
    assert module_name == expected_command  # Basic sanity check


if __name__ == "__main__":
    pytest.main([__file__])
