import pytest
from unittest.mock import patch, MagicMock
from anges.agents.task_executor import TaskExecutor
from anges.agents.agent_utils.events import Event, EventStream
import logging
import os

def test_task_executor_simple():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Reasoning 1", "reasoning": "Task completion reasoning", "actions": [{"action_type": "TASK_COMPLETE", "content": "Task complete 1"}]}',
        "Dummy Task Summary",
    ]
    executor = TaskExecutor(inference_func=mock_inference_func)
    output_event_stream = executor.run_with_new_request(task_description="Test new task")

    # Assertions
    assert len(output_event_stream.events_list) == 2
    assert len(output_event_stream.event_summaries_list) == 1

    event_1, event_2 = output_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test new task"
    assert event_2.type == "task_completion"
    assert event_2.content == "Task complete 1"

    event_summary = output_event_stream.event_summaries_list[0]
    assert event_summary.summary == "Dummy Task Summary"
    assert event_summary.type == "task_completion_summary"
    assert event_summary.start_event_idx == 1

def test_task_executor_multiple_actions():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        # First request responses
        '{"analysis": "Need to run command", "reasoning": "Reasoning 1", "actions": [{"action_type": "RUN_SHELL_CMD", "command": "echo fake command 1", "reasoning": "Running command"}]}',
        '{"analysis": "Reasoning 2", "reasoning": "Task completion", "actions": [{"action_type": "TASK_COMPLETE", "content": "Task complete 1"}]}',
        "First Task Summary",
        # Second request responses
        '{"analysis": "Need to run command", "reasoning": "Reasoning 3", "actions": [{"action_type": "RUN_SHELL_CMD", "command": "echo fake command 2", "reasoning": "Running command"}]}',
        '{"analysis": "Need to run another command", "reasoning": "Reasoning 4", "actions": [{"action_type": "RUN_SHELL_CMD", "command": "echo fake command 3", "reasoning": "Running command"}]}',
        '{"analysis": "Final reasoning", "reasoning": "Task completion", "actions": [{"action_type": "TASK_COMPLETE", "content": "Task complete 2"}]}',
        "Second Task Summary"
    ]

    # Act - First request
    executor = TaskExecutor(inference_func=mock_inference_func)
    first_event_stream = executor.run_with_new_request(task_description="Test new task 1")

    # Assert first request
    assert len(first_event_stream.events_list) == 3  # request + action + completion
    assert len(first_event_stream.event_summaries_list) == 1

    event_1, event_2, event_3 = first_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test new task 1"
    assert event_2.type == "action"
    assert event_2.reasoning == "Reasoning 1"
    assert "fake command 1" in event_2.content
    assert event_3.type == "task_completion"
    assert event_3.content == "Task complete 1"

    # Act - Second request with fresh event stream
    second_event_stream = executor.run_with_new_request(
        task_description="Test new task 2",
        event_stream=EventStream()  # Pass empty event stream to avoid inheriting previous events
    )

    # Assert second request
    assert len(second_event_stream.events_list) == 4  # request + 2 actions + completion
    assert len(second_event_stream.event_summaries_list) == 1

    event_1, event_2, event_3, event_4 = second_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test new task 2"
    assert event_2.type == "action"
    assert event_2.reasoning == "Reasoning 3"
    assert "fake command 2" in event_2.content
    assert event_3.type == "action"
    assert event_3.reasoning == "Reasoning 4"
    assert "fake command 3" in event_3.content
    assert event_4.type == "task_completion"
    assert event_4.content == "Task complete 2"

    summary = second_event_stream.event_summaries_list[0]
    assert summary.summary == "Second Task Summary"
    assert summary.type == "task_completion_summary"
    assert summary.start_event_idx == 1
    assert summary.end_event_idx == 4

def test_task_executor_help_needed():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Analyzing the situation", "reasoning": "Need help", "actions": [{"action_type": "HELP_NEEDED", "content": "Need help with permission issue"}]}'
    ]

    # Act
    executor = TaskExecutor(inference_func=mock_inference_func)
    output_event_stream = executor.run_with_new_request(
        task_description="Test help needed"
    )

    # Assert
    assert len(output_event_stream.events_list) == 2
    assert len(output_event_stream.event_summaries_list) == 0

    event_1, event_2 = output_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test help needed"
    assert event_2.type == "agent_requested_help"
    assert event_2.content == "Need help with permission issue"

def test_task_executor_shell_cmd_execution():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Testing shell command", "reasoning": "Executing test commands", "actions": [{"action_type": "RUN_SHELL_CMD", "command": "echo \'stdout test\' && echo \'stderr test\' >&2 && exit 1", "reasoning": "Running test command"}]}',
        '{"analysis": "Handling command failure", "reasoning": "Task completion", "actions": [{"action_type": "TASK_COMPLETE", "content": "Command execution verified"}]}',
        "Shell command execution summary"
    ]

    # Act
    executor = TaskExecutor(inference_func=mock_inference_func)
    output_event_stream = executor.run_with_new_request(
        task_description="Test shell command execution"
    )

    # Assert
    assert len(output_event_stream.events_list) == 3  # request + command + completion
    assert len(output_event_stream.event_summaries_list) == 1

    event_1, event_2, event_3 = output_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test shell command execution"
    assert event_2.type == "action"
    assert event_2.reasoning == "Executing test commands"
    assert "stdout test" in event_2.content
    assert "stderr test" in event_2.content
    assert "EXIT_CODE: 1" in event_2.content
    assert event_3.type == "task_completion"
    assert event_3.content == "Command execution verified"

def test_task_executor_file_editing():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Testing file editing", "reasoning": "Creating new file", "actions": [{"action_type": "EDIT_FILE", "directive_line": "NEW_FILE test_task_executor_test.txt", "content": "Hello World"}]}',
        '{"analysis": "Modifying file", "reasoning": "Appending content", "actions": [{"action_type": "EDIT_FILE", "directive_line": "INSERT_LINES test_task_executor_test.txt -1", "content": "Goodbye World"}]}',
        '{"analysis": "Task complete", "reasoning": "File operations done", "actions": [{"action_type": "TASK_COMPLETE", "content": "File editing operations verified"}]}',
        "File editing test summary"
    ]

    # Act
    executor = TaskExecutor(inference_func=mock_inference_func)
    output_event_stream = executor.run_with_new_request(
        task_description="Test file editing operations"
    )

    # Assert
    assert len(output_event_stream.events_list) == 4  # request + 2 edits + completion
    assert len(output_event_stream.event_summaries_list) == 1

    event_1, event_2, event_3, event_4 = output_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test file editing operations"
    assert event_2.type == "edit_file"
    assert event_2.reasoning == "Creating new file"
    assert "NEW_FILE test_task_executor_test.txt" in event_2.content
    assert event_3.type == "edit_file"
    assert event_3.reasoning == "Appending content"
    assert "INSERT_LINES test_task_executor_test.txt" in event_3.content
    assert event_4.type == "task_completion"
    assert event_4.content == "File editing operations verified"

    # Verify summary
    summary = output_event_stream.event_summaries_list[0]
    assert summary.summary == "File editing test summary"
    assert summary.start_event_idx == 1
    assert summary.end_event_idx == 4

    # Clean up test file
    try:
        os.remove("test_task_executor_test.txt")
    except:
        pass