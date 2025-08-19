import pytest
from unittest.mock import patch, MagicMock
from anges.agents.agent_utils.events import Event, EventStream
from anges.agents.default_agent import DefaultAgent
import logging

# Create a wrapper function to maintain compatibility with tests
def agent_run_task(task_description, input_event_stream=None, model="claude", input_inference_func=None, max_consecutive_actions_to_summarize=15):
    """
    Wrapper function to maintain compatibility with tests after migration from agent_with_shell.py to default_agent.py
    This function adapts the DefaultAgent.run_with_new_request method to match the old agent_run_task signature.
    """
    agent = DefaultAgent(
        inference_func=input_inference_func,
        event_stream=input_event_stream,
        max_consecutive_actions_to_summarize=max_consecutive_actions_to_summarize
    )
    return agent.run_with_new_request(task_description)

def test_agent_run_task_simple():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Reasoning 1", "reasoning": "Task completion", "actions": [{"action_type": "TASK_COMPLETE", "content": "Task complete 1"}]}',
        "Dummy Task Summary",
    ]

    output_event_stream = agent_run_task(task_description="Test new task", input_event_stream=None, model="claude", input_inference_func=mock_inference_func)

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
    assert event_summary.end_event_idx == 2

def test_agent_run_task_agent_response():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Reasoning 1", "reasoning": "Agent response", "actions": [{"action_type": "AGENT_TEXT_RESPONSE", "content": "Fake agent response"}]}',
    ]

    output_event_stream = agent_run_task(task_description="Test new task", input_event_stream=None, model="claude", input_inference_func=mock_inference_func)

    # Assertions
    assert len(output_event_stream.events_list) == 2
    assert len(output_event_stream.event_summaries_list) == 0

    event_1, event_2 = output_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test new task"
    assert event_2.type == "agent_text_response"
    assert event_2.content == "Fake agent response"

def test_agent_run_task_multiple_actions():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Need to run command", "reasoning": "Reasoning 1", "actions": [{"action_type": "RUN_SHELL_CMD", "command": "echo fake command 1", "reasoning": "Running command"}]}',
        '{"analysis": "Need to run another command", "reasoning": "Reasoning 2", "actions": [{"action_type": "RUN_SHELL_CMD", "command": "echo fake command 2", "reasoning": "Running command"}]}',
        '{"analysis": "Reasoning 3", "reasoning": "Task completion", "actions": [{"action_type": "TASK_COMPLETE", "content": "Task complete 1"}]}',
        "Dummy Task Summary",
    ]

    output_event_stream = agent_run_task(task_description="Test new task", input_event_stream=None, model="claude", input_inference_func=mock_inference_func)

    # Assertions
    assert len(output_event_stream.events_list) == 4
    assert len(output_event_stream.event_summaries_list) == 1

    event_1, event_2, event_3, event_4 = output_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test new task"
    assert event_2.type == "action"
    assert event_2.reasoning == "Reasoning 1"
    assert "fake command 1" in event_2.content
    assert event_3.type == "action"
    assert event_3.reasoning == "Reasoning 2"
    assert "fake command 2" in event_3.content
    assert event_4.type == "task_completion"
    assert event_4.content == "Task complete 1"

    event_summary = output_event_stream.event_summaries_list[0]
    assert event_summary.summary == "Dummy Task Summary"
    assert event_summary.type == "task_completion_summary"
    assert event_summary.start_event_idx == 1
    assert event_summary.end_event_idx == 4

def test_agent_run_task_help_needed():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Analyzing the situation", "reasoning": "Need help", "actions": [{"action_type": "HELP_NEEDED", "content": "Need help with permission issue"}]}'
    ]

    # Act
    output_event_stream = agent_run_task(
        task_description="Test help needed",
        input_event_stream=None,
        model="claude",
        input_inference_func=mock_inference_func
    )

    # Assert
    assert len(output_event_stream.events_list) == 2
    assert len(output_event_stream.event_summaries_list) == 0

    event_1, event_2 = output_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_1.content == "Test help needed"
    assert event_2.type == "agent_requested_help"
    assert event_2.content == "Need help with permission issue"

def test_agent_run_task_shell_cmd_execution():
    # Arrange
    mock_inference_func = MagicMock()
    mock_inference_func.side_effect = [
        '{"analysis": "Testing shell command", "reasoning": "Executing test commands", "actions": [{"action_type": "RUN_SHELL_CMD", "command": "echo \'stdout test\' && echo \'stderr test\' >&2 && exit 1", "reasoning": "Running test command"}]}',
        '{"analysis": "Handling command failure", "reasoning": "Task completion", "actions": [{"action_type": "TASK_COMPLETE", "content": "Command execution verified"}]}',
        "Shell command execution summary"
    ]

    # Act
    output_event_stream = agent_run_task(
        task_description="Test shell command execution",
        input_event_stream=None,
        model="claude",
        input_inference_func=mock_inference_func
    )

    # Assert
    assert len(output_event_stream.events_list) == 3
    assert len(output_event_stream.event_summaries_list) == 1

    event_1, event_2, event_3 = output_event_stream.events_list
    assert event_1.type == "new_request"
    assert event_2.type == "action"
    assert event_2.reasoning == "Executing test commands"
    # Verify command output capture
    assert "stdout test" in event_2.content
    assert "stderr test" in event_2.content
    assert "EXIT_CODE: 1" in event_2.content
    assert event_3.type == "task_completion"

    # Verify summary
    summary = output_event_stream.event_summaries_list[0]
    assert summary.summary == "Shell command execution summary"
    assert summary.start_event_idx == 1
    assert summary.end_event_idx == 3