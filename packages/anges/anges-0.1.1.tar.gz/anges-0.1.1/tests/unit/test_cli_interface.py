import pytest
import sys
import io
import contextlib
from unittest.mock import patch, MagicMock, call
from builtins import exit

from anges.cli_interface.cli_runner import run_cli_with_args, create_agent, check_interrupt, parse_arguments
from anges.cli import main
from anges.agents.agent_utils.agent_factory import AgentType
@contextlib.contextmanager
def mock_cli_environment():
    with patch('sys.exit') as mock_sys_exit, \
         patch('builtins.exit') as mock_exit, \
         patch('signal.signal') as mock_signal, \
         patch('sys.stdout', new_callable=io.StringIO) as mock_stdout, \
         patch('sys.stdin.isatty', return_value=True) as mock_isatty:
        yield mock_signal, mock_exit, mock_sys_exit, mock_stdout, mock_isatty

@patch('anges.cli_interface.cli_runner.create_agent')
def test_basic_cli_execution(mock_create_agent):
    """Test basic CLI execution with default parameters"""
    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent
    test_input = "echo 'Hello World'\n\n"

    with mock_cli_environment() as (mock_signal, mock_exit, mock_sys_exit, mock_stdout, mock_isatty):
        with patch('sys.stdin', io.StringIO(test_input)):
            with patch('sys.argv', ['cli_runner.py', '--question', "echo 'Hello World'"]):
                args = parse_arguments()
                run_cli_with_args(args)

        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once()
        args, kwargs = mock_agent.run_with_new_request.call_args
        assert 'task_description' in kwargs
        assert kwargs['task_description'].strip() == "echo 'Hello World'"
        # Check if either the function returned normally or called exit
        exit_calls = mock_sys_exit.call_args_list + mock_exit.call_args_list
        if exit_calls:
            assert len(exit_calls) == 1
            assert exit_calls[0] == call(0)

@patch('anges.cli_interface.cli_runner.create_agent')
def test_cli_with_task_executor(mock_create_agent):
    """Test CLI execution with task executor agent"""
    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent
    test_input = "echo 'Test'\n\n"

    with mock_cli_environment() as (mock_signal, mock_exit, mock_sys_exit, mock_stdout, mock_isatty):
        with patch('sys.argv', ['cli_runner.py', '--agent', 'task_executor', '--question', "echo 'Test'"]):
            args = parse_arguments()
            run_cli_with_args(args)

        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once()
        args, kwargs = mock_agent.run_with_new_request.call_args
        assert 'task_description' in kwargs
        assert kwargs['task_description'].strip() == "echo 'Test'"
        
        # Check if either the function returned normally or called exit
        exit_calls = mock_sys_exit.call_args_list + mock_exit.call_args_list
        if exit_calls:
            assert len(exit_calls) == 1
            assert exit_calls[0] == call(0)

@patch('anges.cli_interface.cli_runner.create_agent')
def test_cli_with_prefix_cmd(mock_create_agent):
    """Test CLI execution with command prefix"""
    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent
    test_input = "ls\n\n"
    prefix = 'docker exec test_container'

    with mock_cli_environment() as (mock_signal, mock_exit, mock_sys_exit, mock_stdout, mock_isatty):
        with patch('sys.argv', ['cli_runner.py', '--prefix_cmd', prefix, '--question', 'ls']):
            args = parse_arguments()
            run_cli_with_args(args)

        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once()
        args, kwargs = mock_agent.run_with_new_request.call_args
        assert 'task_description' in kwargs
        assert kwargs['task_description'].strip() == 'ls'

def test_cli_empty_input():
    """Test CLI behavior with empty input"""
    test_input = "\n"

    with mock_cli_environment() as (mock_signal, mock_exit, mock_sys_exit, mock_stdout, mock_isatty):
        with patch('sys.argv', ['cli_runner.py', '--interactive']):
            with patch('sys.stdin', io.StringIO(test_input)):
                args = parse_arguments()
                run_cli_with_args(args)

        assert "Error: No question (-q) or input file (-f) provided" in mock_stdout.getvalue()
        
        # Check if either the function returned normally or called exit
        exit_calls = mock_sys_exit.call_args_list + mock_exit.call_args_list
        if exit_calls:
            assert len(exit_calls) == 1
            assert exit_calls[0] == call(1)
def test_cli_empty_input():
    """Test CLI behavior with empty input - should show help when no arguments provided"""
    with mock_cli_environment() as (mock_signal, mock_exit, mock_sys_exit, mock_stdout, mock_isatty):
        with patch('sys.argv', ['anges']):
            # Mock the parser.print_help() method to capture help output
            with patch('argparse.ArgumentParser.print_help') as mock_print_help:
                main()
                
                # Verify that help was printed when no arguments provided
                mock_print_help.assert_called_once()
                
        # Check if either the function returned normally or called exit
        exit_calls = mock_sys_exit.call_args_list + mock_exit.call_args_list
        if exit_calls:
            assert len(exit_calls) == 1
            assert exit_calls[0] == call(0)

@patch('anges.utils.data_handler.read_event_stream')
@patch('anges.cli_interface.cli_runner.create_agent')
def test_cli_with_existing_stream(mock_create_agent, mock_read_stream):
    """Test CLI continuation from existing event stream"""
    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent
    mock_stream = MagicMock()
    mock_read_stream.return_value = mock_stream
    test_input = "echo 'Continue'\n\n"

    with mock_cli_environment() as (mock_signal, mock_exit, mock_sys_exit, mock_stdout, mock_isatty):
        with patch('sys.argv', ['cli_runner.py', '--existing-stream-id', 'test_id', '--question', "echo 'Continue'"]):
            args = parse_arguments()
            run_cli_with_args(args)

        mock_create_agent.assert_called_once()
        mock_agent.run_with_new_request.assert_called_once()
        mock_read_stream.assert_called_once_with('test_id')
        
        # Check if either the function returned normally or called exit
        exit_calls = mock_sys_exit.call_args_list + mock_exit.call_args_list
        if exit_calls:
            assert len(exit_calls) == 1
            assert exit_calls[0] == call(0)
