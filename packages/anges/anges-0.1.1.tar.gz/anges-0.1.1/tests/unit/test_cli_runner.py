"""
Unit tests for the CLI runner functionality (anges/cli_interface/cli_runner.py).

These tests focus on:
1. Parameter parsing for all supported parameters
2. Dispatch to the correct functionality
3. Mocking to avoid actual execution
4. Ensuring tests are isolated
"""

import pytest
import sys
import io
import os
import signal
import logging
import argparse
from unittest.mock import patch, MagicMock, call

from anges.cli_interface.cli_runner import (
    run_cli_with_args, create_agent,
    signal_handler, parse_arguments
)
from anges.agents.agent_utils.agent_factory import AgentType

# Reuse the mock_cli_environment context manager from test_cli_interface.py
from tests.unit.test_cli_interface import mock_cli_environment


class TestAgentType:
    """Test the AgentType enum functionality."""

    def test_agent_type_values(self):
        """Test that AgentType enum has the expected values."""
        assert AgentType.TASK_EXECUTOR.value == "task_executor"
        assert AgentType.TASK_ANALYZER.value == "task_analyzer"
        assert AgentType.ORCHESTRATOR.value == "orchestrator"
        assert AgentType.DEFAULT.value == "default"

    def test_agent_type_list(self):
        """Test the list method returns all agent types."""
        agent_types = AgentType.list()
        assert "task_executor" in agent_types
        assert "task_analyzer" in agent_types
        assert "orchestrator" in agent_types
        assert "default" in agent_types
        assert len(agent_types) == 4


class TestAgentCreation:
    """Test the agent creation functionality."""

    @patch('anges.agents.agent_utils.agent_factory.AgentFactory.create_agent')
    def test_create_task_executor(self, mock_create_agent):
        """Test creating a TaskExecutor agent."""
        mock_instance = MagicMock()
        mock_create_agent.return_value = mock_instance

        # Create a task executor agent
        agent = create_agent(
            agent_type="task_executor",
            cmd_init_dir="/test/path",
            prefix_cmd="test_prefix",
            interrupt_check=lambda: False,
            logging_level=logging.INFO
        )

        # Verify the agent was created and returned
        assert agent == mock_instance
        mock_create_agent.assert_called_once()
    @patch('anges.agents.agent_utils.agent_factory.AgentFactory.create_agent')
    def test_create_task_analyzer(self, mock_create_agent):
        """Test creating a TaskAnalyzer agent."""
        mock_instance = MagicMock()
        mock_create_agent.return_value = mock_instance

        # Create a task analyzer agent
        agent = create_agent(
            agent_type="task_analyzer",
            cmd_init_dir="/test/path",
            prefix_cmd="test_prefix",
            logging_level=logging.INFO
        )

        # Verify the agent was created and returned
        assert agent == mock_instance
        mock_create_agent.assert_called_once()
    @patch('anges.agents.agent_utils.agent_factory.AgentFactory.create_agent')
    def test_create_orchestrator(self, mock_create_agent):
        """Test creating an Orchestrator agent."""
        mock_instance = MagicMock()
        mock_create_agent.return_value = mock_instance

        # Create an orchestrator agent
        agent = create_agent(
            agent_type="orchestrator",
            cmd_init_dir="/test/path",
            prefix_cmd="test_prefix",
            logging_level=logging.INFO
        )

        # Verify the agent was created and returned
        assert agent == mock_instance
        mock_create_agent.assert_called_once()
    @patch('anges.agents.agent_utils.agent_factory.AgentFactory.create_agent')
    def test_create_default_agent(self, mock_create_agent):
        """Test creating a DefaultAgent agent."""
        mock_instance = MagicMock()
        mock_create_agent.return_value = mock_instance

        # Create a default agent
        agent = create_agent(
            agent_type="default",
            cmd_init_dir="/test/path",
            prefix_cmd="test_prefix",
            logging_level=logging.INFO
        )

        # Verify the agent was created and returned
        assert agent == mock_instance
        mock_create_agent.assert_called_once()

    def test_create_invalid_agent(self):
        """Test creating an invalid agent type raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            create_agent(agent_type="invalid_agent")

        assert "Invalid agent type: invalid_agent" in str(excinfo.value)


class TestCLIRunnerParameters:
    """Test CLI runner parameter parsing and handling."""

    def test_parse_args_defaults(self):
        """Test parsing arguments with default values."""
        test_args = ["anges"]

        with patch('sys.argv', test_args):
            with patch('argparse.ArgumentParser.parse_args') as mock_parse_args:
                # Create a namespace with expected default values
                default_args = argparse.Namespace(
                    model="claude",
                    prefix_cmd="",
                    cmd_init_dir="",
                    agent="default",
                    input_file=None,
                    question=None,
                    existing_stream_id=None,
                    logging="info"
                )
                mock_parse_args.return_value = default_args
                
                args = parse_arguments()

    @patch('sys.exit')
    @patch('builtins.input')
    @patch('anges.cli_interface.cli_runner.create_agent')
    def test_run_cli_with_input(self, mock_create_agent, mock_input, mock_exit):
        """Test running CLI with interactive input."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent

        # Setup mock input to return a task and then empty string to end input
        mock_input.side_effect = ["Test task", "", "", "", ""]

        # Create args namespace with question to avoid interactive mode
        args = argparse.Namespace(
            model="claude",
            prefix_cmd="",
            cmd_init_dir="",
            agent="default",
            input_file=None,
            question="Test task",  # Provide question to avoid interactive mode
            existing_stream_id=None,
            interactive=True
        )

        # Mock sys.stdin.isatty to return True (interactive mode)
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        
        # Run the function with our mocked stdin and suppress output
        with patch('sys.stdin', mock_stdin):
            with patch('sys.stdout'):  # Suppress output during test
                run_cli_with_args(args)
        
        # Verify agent.run_with_new_request was called with the correct input
        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once_with(
            task_description="Test task",
            event_stream=[]
        )
        
        # Verify that sys.exit was not called (execution completed successfully)
        mock_exit.assert_not_called()
        
    @patch('os.path.exists')
    @patch('sys.exit')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('anges.cli_interface.cli_runner.create_agent')
    def test_run_cli_with_file(self, mock_create_agent, mock_open, mock_exit, mock_exists):
        """Test running CLI with a file input."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        mock_exists.return_value = True

        # Setup mock file handle
        mock_file = MagicMock()
        mock_file.read.return_value = "Test task from file"
        mock_open.return_value.__enter__.return_value = mock_file

        # Create args namespace with file input
        args = argparse.Namespace(
            model="claude",
            prefix_cmd="",
            cmd_init_dir="",
            agent="default",
            input_file="test_file.txt",
            question=None,
            existing_stream_id=None,
            interactive=False
        )

        # Mock sys.stdin to avoid reading from actual stdin
        mock_stdin = MagicMock()
        mock_stdin.readline.side_effect = ["", ""]  # Empty input to avoid stdin reading

        # Call run_cli_with_args directly with the namespace
        with patch('sys.stdout'):  # Suppress output during test
            with patch('sys.stdin', mock_stdin):
                run_cli_with_args(args)
        
        # Verify agent was created and run with the file content
        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once_with(
            task_description="Test task from file",
            event_stream=[]
        )

    @patch('anges.cli_interface.cli_runner.create_agent')
    @patch('os.path.exists')
    @patch('sys.exit')
    def test_run_cli_with_file_not_found(self, mock_exit, mock_exists, mock_create_agent):
        """Test running CLI when input file is not found."""
        # Setup mocks
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        mock_exists.return_value = False

        # Create args namespace
        # Create args namespace
        args = argparse.Namespace(
            model="default",
            prefix_cmd="",
            cmd_init_dir="",
            agent="default",  # Changed from 'agent' to 'agent_type'
            input_file="nonexistent_file.txt",
            question="Test fallback question",  # Add a question to avoid stdin reading
            existing_stream_id=None,
            logging="info"
        )

        # Call run_cli_with_args directly with the namespace
        with patch('sys.stderr', new=io.StringIO()):
            with patch('sys.stdout'):  # Suppress output during test
                run_cli_with_args(args)

        # Verify agent was created and run with the fallback question
        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once_with(
            task_description="Test fallback question",
            event_stream=[]
        )

        # Verify that sys.exit was not called (execution continued)
        mock_exit.assert_not_called()

    @patch('anges.utils.data_handler.read_event_stream')
    @patch('anges.cli_interface.cli_runner.create_agent')
    def test_run_cli_with_existing_stream(self, mock_create_agent, mock_read_stream):
        """Test running CLI with an existing stream ID."""
        # Setup mocks
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        mock_stream = {"events": [{"type": "test"}]}
        mock_read_stream.return_value = mock_stream  # Mock successful stream read
        
        # Create args namespace
        args = argparse.Namespace(
            model="default",
            prefix_cmd="",
            cmd_init_dir="",
            agent="default",
            input_file=None,
            existing_stream_id="test_stream",
            question="test question",
            logging="info"
        )

        # Mock sys.stdin to avoid reading from actual stdin
        mock_stdin = MagicMock()
        mock_stdin.readline.side_effect = ["", ""]  # Empty input to avoid stdin reading

        # Call run_cli_with_args directly with the namespace
        with patch('sys.stdout'):  # Suppress output during test
            with patch('sys.stdin', mock_stdin):
                run_cli_with_args(args)
        
        # Verify agent was created and run with the existing stream
        # Verify agent was created and run with new request (not existing stream when question is provided)
        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once_with(
            task_description="test question",
            event_stream=mock_stream
        )

    @patch('anges.cli_interface.cli_runner.create_agent')
    def test_run_cli_with_question(self, mock_create_agent):
        """Test running CLI with a direct question input."""
        # Setup mock agent
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent

        # Create args namespace with a question
        args = argparse.Namespace(
            model="default",
            prefix_cmd="",
            cmd_init_dir="",
            agent="default",
            input_file=None,
            question="Test question?",
            existing_stream_id=None,
            logging="info"
        )

        # Mock sys.stdin to avoid reading from actual stdin
        mock_stdin = MagicMock()
        mock_stdin.readline.side_effect = ["", ""]  # Empty input to avoid stdin reading

        # Call run_cli_with_args directly with the namespace
        with patch('sys.stdout'):  # Suppress output during test
            with patch('sys.stdin', mock_stdin):
                run_cli_with_args(args)

        # Verify agent was created and run with the question
        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once_with(
            task_description="Test question?",
            event_stream=[]
        )


class TestSignalHandling:
    """Test signal handling."""

    @patch('anges.cli_interface.cli_runner.interrupt_requested', False)
    def test_signal_handler(self):
        """Test the signal handler sets the interrupt flag."""
        # Call the signal handler
        signal_handler(signal.SIGINT, None)

        # Import the module to check the global variable
        import anges.cli_interface.cli_runner as cli_runner

        # Verify the interrupt flag was set
        assert cli_runner.interrupt_requested is True

class TestNotesValidation:
    """Test notes validation functionality."""

    def test_validate_note_structure_valid(self):
        """Test validation of a properly structured note."""
        from anges.cli_interface.cli_runner import validate_note_structure
        
        valid_note = {
            "scope": "general",
            "title": "Test Note",
            "content": "This is a test note content"
        }
        
        is_valid, error_msg = validate_note_structure(valid_note, "test")
        assert is_valid is True
        assert error_msg is None

    def test_validate_note_structure_missing_fields(self):
        """Test validation fails when required fields are missing."""
        from anges.cli_interface.cli_runner import validate_note_structure
        
        # Missing 'content' field
        invalid_note = {
            "scope": "general",
            "title": "Test Note"
        }
        
        is_valid, error_msg = validate_note_structure(invalid_note, "test")
        assert is_valid is False
        assert "missing required fields: content" in error_msg
        assert "Required: scope, title, content" in error_msg

    def test_validate_note_structure_wrong_type(self):
        """Test validation fails when note is not a dictionary."""
        from anges.cli_interface.cli_runner import validate_note_structure
        
        invalid_note = "This is a string, not a dict"
        
        is_valid, error_msg = validate_note_structure(invalid_note, "test")
        assert is_valid is False
        assert "must be a dictionary/object, got str" in error_msg

    def test_validate_note_structure_empty_fields(self):
        """Test validation fails when required fields are empty."""
        from anges.cli_interface.cli_runner import validate_note_structure
        
        invalid_note = {
            "scope": "",
            "title": "Test Note",
            "content": "This is a test note content"
        }
        
        is_valid, error_msg = validate_note_structure(invalid_note, "test")
        assert is_valid is False
        assert "field 'scope' cannot be empty" in error_msg

    def test_validate_note_structure_non_string_fields(self):
        """Test validation fails when fields are not strings."""
        from anges.cli_interface.cli_runner import validate_note_structure
        
        invalid_note = {
            "scope": "general",
            "title": 123,  # Should be string
            "content": "This is a test note content"
        }
        
        is_valid, error_msg = validate_note_structure(invalid_note, "test")
        assert is_valid is False
        assert "field 'title' must be a string, got int" in error_msg


class TestNotesParsingFromArgs:
    """Test parsing notes from command line arguments."""

    def test_parse_notes_from_args_valid_json(self):
        """Test parsing valid JSON notes from command line arguments."""
        from anges.cli_interface.cli_runner import parse_notes_from_args
        
        notes_args = [
            '{"scope": "general", "title": "Note 1", "content": "First note"}',
            '{"scope": "project", "title": "Note 2", "content": "Second note"}'
        ]
        
        parsed_notes, errors = parse_notes_from_args(notes_args)
        
        assert len(parsed_notes) == 2
        assert len(errors) == 0
        assert parsed_notes[0]["scope"] == "general"
        assert parsed_notes[0]["title"] == "Note 1"
        assert parsed_notes[1]["scope"] == "project"
        assert parsed_notes[1]["title"] == "Note 2"

    def test_parse_notes_from_args_plain_text(self):
        """Test parsing plain text notes (non-JSON) from command line arguments."""
        from anges.cli_interface.cli_runner import parse_notes_from_args
        
        notes_args = [
            "This is a plain text note",
            "Another plain text note"
        ]
        
        parsed_notes, errors = parse_notes_from_args(notes_args)
        
        assert len(parsed_notes) == 2
        assert len(errors) == 0
        assert parsed_notes[0]["scope"] == "general"
        assert parsed_notes[0]["title"] == "CLI Note 1"
        assert parsed_notes[0]["content"] == "This is a plain text note"
        assert parsed_notes[1]["title"] == "CLI Note 2"
        assert parsed_notes[1]["content"] == "Another plain text note"

    def test_parse_notes_from_args_mixed_format(self):
        """Test parsing mixed JSON and plain text notes."""
        from anges.cli_interface.cli_runner import parse_notes_from_args
        
        notes_args = [
            '{"scope": "project", "title": "JSON Note", "content": "This is JSON"}',
            "This is plain text"
        ]
        
        parsed_notes, errors = parse_notes_from_args(notes_args)
        
        assert len(parsed_notes) == 2
        assert len(errors) == 0
        assert parsed_notes[0]["scope"] == "project"
        assert parsed_notes[0]["title"] == "JSON Note"
        assert parsed_notes[1]["scope"] == "general"
        assert parsed_notes[1]["title"] == "CLI Note 2"

    def test_parse_notes_from_args_invalid_json(self):
        """Test parsing invalid JSON notes from command line arguments."""
        from anges.cli_interface.cli_runner import parse_notes_from_args
        
        notes_args = [
            '{"scope": "general", "title": "Missing Content"}',  # Missing content field
            '{"invalid": "json"}'  # Missing required fields
        ]
        
        parsed_notes, errors = parse_notes_from_args(notes_args)
        
        assert len(parsed_notes) == 0
        assert len(errors) == 2
        assert "missing required fields: content" in errors[0]
        assert "missing required fields: scope, title, content" in errors[1]

    def test_parse_notes_from_args_empty_input(self):
        """Test parsing empty notes arguments."""
        from anges.cli_interface.cli_runner import parse_notes_from_args
        
        parsed_notes, errors = parse_notes_from_args(None)
        assert len(parsed_notes) == 0
        assert len(errors) == 0
        
        parsed_notes, errors = parse_notes_from_args([])
        assert len(parsed_notes) == 0
        assert len(errors) == 0

    def test_parse_notes_from_args_empty_string(self):
        """Test parsing empty string notes."""
        from anges.cli_interface.cli_runner import parse_notes_from_args
        
        notes_args = ["", "   "]
        
        parsed_notes, errors = parse_notes_from_args(notes_args)
        
        assert len(parsed_notes) == 0
        assert len(errors) == 2
        assert "Command line note 1 is empty" in errors[0]
        assert "Command line note 2 is empty" in errors[1]


class TestNotesParsingFromFile:
    """Test parsing notes from JSON files."""

    def test_parse_notes_from_file_valid(self, tmp_path):
        """Test parsing valid notes from a JSON file."""
        from anges.cli_interface.cli_runner import parse_notes_from_file
        
        # Create a temporary JSON file with valid notes
        notes_data = [
            {"scope": "general", "title": "File Note 1", "content": "First note from file"},
            {"scope": "project", "title": "File Note 2", "content": "Second note from file"}
        ]
        
        notes_file = tmp_path / "notes.json"
        with open(notes_file, 'w') as f:
            import json
            json.dump(notes_data, f)
        
        parsed_notes, errors = parse_notes_from_file(str(notes_file))
        
        assert len(parsed_notes) == 2
        assert len(errors) == 0
        assert parsed_notes[0]["scope"] == "general"
        assert parsed_notes[0]["title"] == "File Note 1"
        assert parsed_notes[1]["scope"] == "project"
        assert parsed_notes[1]["title"] == "File Note 2"

    def test_parse_notes_from_file_not_found(self):
        """Test parsing notes from a non-existent file."""
        from anges.cli_interface.cli_runner import parse_notes_from_file
        
        parsed_notes, errors = parse_notes_from_file("nonexistent_file.json")
        
        assert len(parsed_notes) == 0
        assert len(errors) == 1
        assert "Notes file not found: 'nonexistent_file.json'" in errors[0]

    def test_parse_notes_from_file_invalid_json(self, tmp_path):
        """Test parsing notes from a file with invalid JSON."""
        from anges.cli_interface.cli_runner import parse_notes_from_file
        
        # Create a temporary file with invalid JSON
        notes_file = tmp_path / "invalid_notes.json"
        with open(notes_file, 'w') as f:
            f.write('{"invalid": json}')
        
        parsed_notes, errors = parse_notes_from_file(str(notes_file))
        
        assert len(parsed_notes) == 0
        assert len(errors) == 1
        assert "Invalid JSON in notes file" in errors[0]

    def test_parse_notes_from_file_not_array(self, tmp_path):
        """Test parsing notes from a file that doesn't contain an array."""
        from anges.cli_interface.cli_runner import parse_notes_from_file
        
        # Create a temporary file with a single object instead of array
        notes_file = tmp_path / "not_array_notes.json"
        with open(notes_file, 'w') as f:
            import json
            json.dump({"scope": "general", "title": "Note", "content": "Content"}, f)
        
        parsed_notes, errors = parse_notes_from_file(str(notes_file))
        
        assert len(parsed_notes) == 0
        assert len(errors) == 1
        assert "must contain an array of notes, got dict" in errors[0]

    def test_parse_notes_from_file_empty_array(self, tmp_path):
        """Test parsing notes from a file with an empty array."""
        from anges.cli_interface.cli_runner import parse_notes_from_file
        
        # Create a temporary file with empty array
        notes_file = tmp_path / "empty_notes.json"
        with open(notes_file, 'w') as f:
            import json
            json.dump([], f)
        
        parsed_notes, errors = parse_notes_from_file(str(notes_file))
        
        assert len(parsed_notes) == 0
        assert len(errors) == 1
        assert "contains an empty array" in errors[0]

    def test_parse_notes_from_file_invalid_notes(self, tmp_path):
        """Test parsing notes from a file with invalid note structures."""
        from anges.cli_interface.cli_runner import parse_notes_from_file
        
        # Create a temporary file with invalid note structures
        notes_data = [
            {"scope": "general", "title": "Valid Note", "content": "This is valid"},
            {"scope": "general", "title": "Invalid Note"},  # Missing content
            {"invalid": "structure"}  # Missing all required fields
        ]
        
        notes_file = tmp_path / "mixed_notes.json"
        with open(notes_file, 'w') as f:
            import json
            json.dump(notes_data, f)
        
        parsed_notes, errors = parse_notes_from_file(str(notes_file))
        
        assert len(parsed_notes) == 1  # Only the valid note
        assert len(errors) == 2  # Two invalid notes
        assert parsed_notes[0]["title"] == "Valid Note"
        assert "missing required fields: content" in errors[0]
        assert "missing required fields: scope, title, content" in errors[1]

    def test_parse_notes_from_file_empty_path(self):
        """Test parsing notes with empty file path."""
        from anges.cli_interface.cli_runner import parse_notes_from_file
        
        parsed_notes, errors = parse_notes_from_file(None)
        assert len(parsed_notes) == 0
        assert len(errors) == 0
        
        parsed_notes, errors = parse_notes_from_file("")
        assert len(parsed_notes) == 0
        assert len(errors) == 0


class TestNotesProcessing:
    """Test the complete notes processing functionality."""

    def test_process_notes_from_args_only(self):
        """Test processing notes from command line arguments only."""
        from anges.cli_interface.cli_runner import process_notes
        import argparse
        
        args = argparse.Namespace(
            notes=['{"scope": "general", "title": "Test", "content": "Test content"}'],
            notes_file=None
        )
        
        with patch('sys.stderr', new=io.StringIO()):
            processed_notes, has_errors = process_notes(args)
        
        assert len(processed_notes) == 1
        assert has_errors is False
        assert processed_notes[0]["scope"] == "general"
        assert processed_notes[0]["title"] == "Test"

    def test_process_notes_from_file_only(self, tmp_path):
        """Test processing notes from file only."""
        from anges.cli_interface.cli_runner import process_notes
        import argparse
        import json
        
        # Create test file
        notes_data = [{"scope": "project", "title": "File Note", "content": "From file"}]
        notes_file = tmp_path / "test_notes.json"
        with open(notes_file, 'w') as f:
            json.dump(notes_data, f)
        
        args = argparse.Namespace(
            notes=None,
            notes_file=str(notes_file)
        )
        
        with patch('sys.stderr', new=io.StringIO()):
            processed_notes, has_errors = process_notes(args)
        
        assert len(processed_notes) == 1
        assert has_errors is False
        assert processed_notes[0]["scope"] == "project"
        assert processed_notes[0]["title"] == "File Note"

    def test_process_notes_from_both_sources(self, tmp_path):
        """Test processing notes from both command line and file."""
        from anges.cli_interface.cli_runner import process_notes
        import argparse
        import json
        
        # Create test file
        notes_data = [{"scope": "project", "title": "File Note", "content": "From file"}]
        notes_file = tmp_path / "test_notes.json"
        with open(notes_file, 'w') as f:
            json.dump(notes_data, f)
        
        args = argparse.Namespace(
            notes=['{"scope": "general", "title": "CLI Note", "content": "From CLI"}'],
            notes_file=str(notes_file)
        )
        
        with patch('sys.stderr', new=io.StringIO()):
            processed_notes, has_errors = process_notes(args)
        
        assert len(processed_notes) == 2
        assert has_errors is False
        # CLI notes come first, then file notes
        assert processed_notes[0]["title"] == "CLI Note"
        assert processed_notes[1]["title"] == "File Note"

    def test_process_notes_with_errors(self):
        """Test processing notes with some errors but valid notes too."""
        from anges.cli_interface.cli_runner import process_notes
        import argparse
        
        args = argparse.Namespace(
            notes=[
                '{"scope": "general", "title": "Valid", "content": "Valid note"}',
                '{"invalid": "note"}',  # Missing required fields
                'Plain text note'  # This should work as plain text
            ],
            notes_file=None
        )
        
        with patch('sys.stderr', new=io.StringIO()):
            processed_notes, has_errors = process_notes(args)
        
        assert len(processed_notes) == 2  # Valid JSON note + plain text note
        assert has_errors is True  # Because of the invalid JSON note
        assert processed_notes[0]["title"] == "Valid"
        assert processed_notes[1]["title"] == "CLI Note 3"  # Plain text gets auto title

    def test_process_notes_no_notes(self):
        """Test processing when no notes are provided."""
        from anges.cli_interface.cli_runner import process_notes
        import argparse
        
        args = argparse.Namespace(
            notes=None,
            notes_file=None
        )
        
        with patch('sys.stderr', new=io.StringIO()):
            processed_notes, has_errors = process_notes(args)
        
        assert len(processed_notes) == 0
        assert has_errors is False


class TestNotesIntegrationWithAgentCreation:
    """Test integration of notes with agent creation."""

    @patch('anges.agents.agent_utils.agent_factory.AgentFactory.create_agent')
    def test_create_agent_with_notes(self, mock_create_agent):
        """Test that notes are properly passed to agent creation."""
        from anges.cli_interface.cli_runner import create_agent
        
        mock_instance = MagicMock()
        mock_create_agent.return_value = mock_instance
        
        test_notes = [
            {"scope": "general", "title": "Test Note", "content": "Test content"}
        ]
        
        agent = create_agent(
            agent_type="default",
            notes=test_notes
        )
        
        # Verify agent was created with notes
        assert agent == mock_instance
        mock_create_agent.assert_called_once()
        
        # Get the AgentConfig that was passed to create_agent
        call_args = mock_create_agent.call_args[0][0]  # First positional argument
        assert hasattr(call_args, 'notes')
        assert call_args.notes == test_notes

    @patch('anges.agents.agent_utils.agent_factory.AgentFactory.create_agent')
    def test_create_agent_without_notes(self, mock_create_agent):
        """Test that agent creation works when no notes are provided."""
        from anges.cli_interface.cli_runner import create_agent
        
        mock_instance = MagicMock()
        mock_create_agent.return_value = mock_instance
        
        agent = create_agent(agent_type="default")
        
        # Verify agent was created with empty notes list
        assert agent == mock_instance
        mock_create_agent.assert_called_once()
        
        # Get the AgentConfig that was passed to create_agent
        call_args = mock_create_agent.call_args[0][0]  # First positional argument
        assert hasattr(call_args, 'notes')
        assert call_args.notes == []

    @patch('anges.cli_interface.cli_runner.create_agent')
    def test_run_cli_with_notes_integration(self, mock_create_agent, tmp_path):
        """Test end-to-end notes processing in run_cli_with_args."""
        from anges.cli_interface.cli_runner import run_cli_with_args
        import argparse
        import json
        
        # Setup mock agent
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        # Create test notes file
        notes_data = [{"scope": "project", "title": "File Note", "content": "From file"}]
        notes_file = tmp_path / "test_notes.json"
        with open(notes_file, 'w') as f:
            json.dump(notes_data, f)
        
        # Create args with both CLI notes and notes file
        args = argparse.Namespace(
            model="default",
            prefix_cmd="",
            cmd_init_dir="",
            agent="default",
            input_file=None,
            question="Test question with notes",
            existing_stream_id=None,
            logging="info",
            notes=['{"scope": "general", "title": "CLI Note", "content": "From CLI"}'],
            notes_file=str(notes_file)
        )
        
        # Mock sys.stdin to avoid reading from actual stdin
        mock_stdin = MagicMock()
        mock_stdin.readline.side_effect = ["", ""]
        
        with patch('sys.stdout'):
            with patch('sys.stderr', new=io.StringIO()):
                with patch('sys.stdin', mock_stdin):
                    run_cli_with_args(args)
        
        # Verify agent was created with the processed notes
        mock_create_agent.assert_called_once()
        create_call_args = mock_create_agent.call_args[1]  # keyword arguments
        
        assert 'notes' in create_call_args
        notes_passed = create_call_args['notes']
        assert len(notes_passed) == 2
        
        # CLI notes should come first
        assert notes_passed[0]['title'] == 'CLI Note'
        assert notes_passed[1]['title'] == 'File Note'
        
        # Verify agent.run_with_new_request was called
        mock_agent.run_with_new_request.assert_called_once()


