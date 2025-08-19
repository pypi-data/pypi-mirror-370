"""
Unit tests for the main CLI entry point (anges/cli.py).

These tests focus on:
1. Command format parsing
2. Parameter handling
3. Dispatch to the correct functionality
4. Mocking to avoid actual execution
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock, call, mock_open

from anges.cli import main, run_cli_interface, run_web_interface


class TestCLIEntryPoint:
    """Test the main CLI entry point functionality."""

    @patch('anges.cli.run_cli_interface')
    def test_interactive_mode(self, mock_run_cli):
        """Test running in interactive mode with parameters."""
        test_args = [
            'anges',
            '-i',  # Interactive mode flag
            '--cmd_prefix', 'test_prefix',
            '--path', '/test/path',
            '--agent', 'default',
            '--model', 'test_model'  # Fixed: use --model instead of --inference_func
        ]

        # Mock run_cli_interface to prevent SystemExit
        mock_run_cli.return_value = None

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                pass  # Expected due to removed exception handling

        mock_run_cli.assert_called_once_with(
            input_file=None,
            cmd_prefix='test_prefix',
            cmd_init_dir='/test/path',
            agent='default',
            model='test_model',
            logging_level='info',
            existing_stream_id=None,
            notes=None,
            notes_file=None,
            mcp_config_file=None
        )

    @patch('anges.cli.run_cli_interface')
    @patch('os.path.exists', return_value=True)
    def test_file_input_mode(self, mock_exists, mock_run_cli):
        """Test running with a file input."""
        test_args = [
            'anges',
            '-f', 'test_file.txt',
            '--cmd_prefix', 'test_prefix',
            '--path', '/test/path',
            '--agent', 'default',
            '--model', 'test_model'  # Fixed: use --model instead of --inference_func
        ]

        # Mock run_cli_interface to prevent SystemExit
        mock_run_cli.return_value = None

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                pass  # Expected due to removed exception handling

        # Verify run_cli_interface was called with correct parameters
        mock_run_cli.assert_called_once_with(
            input_file='test_file.txt',
            cmd_prefix='test_prefix',
            cmd_init_dir='/test/path',
            agent='default',
            model='test_model',
            logging_level='info',
            existing_stream_id=None,
            notes=None,
            notes_file=None,
            mcp_config_file=None
        )

    @patch('anges.cli.run_cli_interface')
    def test_question_mode(self, mock_run_cli):
        """Test running with a direct question input."""
        test_args = [
            'anges',
            '-q', 'test question',
            '--cmd_prefix', 'test_prefix',
            '--path', '/test/path',
            '--agent', 'default',
            '--model', 'test_model'  # Fixed: use --model instead of --inference_func
        ]

        # Mock run_cli_interface to prevent SystemExit
        mock_run_cli.return_value = None

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                pass  # Expected due to removed exception handling

        # Verify run_cli_interface was called with correct parameters
        # Note: question mode creates a temporary file, so input_file will be a temp path
        import unittest.mock
        mock_run_cli.assert_called_once_with(
            input_file=unittest.mock.ANY,  # Question mode creates a temp file
            cmd_prefix='test_prefix',
            cmd_init_dir='/test/path',
            agent='default',
            model='test_model',
            logging_level='info',
            existing_stream_id=None,
            notes=None,
            notes_file=None,
            mcp_config_file=None
        )

    @patch('anges.cli.run_web_interface')
    def test_web_mode(self, mock_run_web):
        """Test running in web interface mode."""
        test_args = [
            'anges',
            'ui',
            '--port', '8080',
            '--host', '127.0.0.1'
        ]

        # Mock run_web_interface to prevent SystemExit
        mock_run_web.return_value = None

        with patch('sys.argv', test_args):
            try:
                main()
            except SystemExit:
                pass  # Expected due to removed exception handling

        # Verify run_web_interface was called with correct parameters
        mock_run_web.assert_called_once_with(
            host='127.0.0.1',
            password=None,
            port=8080
        )
    def test_no_arguments(self):
        """Test running with no arguments shows help and returns 0."""
        test_args = ['anges']

        with patch('sys.argv', test_args):
            # The actual CLI returns 0 when no arguments are provided, not SystemExit
            result = main()
            assert result == 0

    def test_invalid_arguments(self):
        """Test running with invalid arguments."""
        test_args = ['anges', '--invalid-arg']

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit):
                main()