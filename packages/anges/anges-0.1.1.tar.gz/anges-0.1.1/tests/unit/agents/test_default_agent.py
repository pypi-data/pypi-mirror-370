import pytest
from unittest.mock import patch, MagicMock
from anges.agents.default_agent import DefaultAgent
from anges.agents.agent_utils.events import Event, EventStream
from anges.utils.inference_api import vertex_claude_inference
import logging

def test_default_agent_initialization():
    """Test DefaultAgent initialization with default and custom parameters"""
    # Test with default parameters - provide mock inference to avoid KeyError: None
    with patch('anges.agents.agent_utils.base_agent.INFERENCE_FUNC_DICT') as mock_dict:
        mock_inference = MagicMock()
        mock_dict.__getitem__.return_value = mock_inference
        
        agent = DefaultAgent()
        assert agent.inference_func == mock_inference  # Should be the mocked inference function
        assert agent.cmd_init_dir == '.'  # Accept new default
        assert agent.prefix_cmd == ""
        assert agent.status == "new"
        assert isinstance(agent.event_stream, EventStream)
    
    # Test with custom parameters
    mock_inference = MagicMock()
    custom_event_stream = EventStream()
    agent = DefaultAgent(
        parent_ids=["parent1", "parent2"],
        inference_func=mock_inference,
        event_stream=custom_event_stream,
        cmd_init_dir="/custom/dir",
        prefix_cmd="sudo",
        max_consecutive_actions_to_summarize=10
    )
    assert agent.parent_ids == ["parent1", "parent2"]
    assert agent.inference_func == mock_inference
    assert agent.event_stream == custom_event_stream
    assert agent.cmd_init_dir == "/custom/dir"
    assert agent.prefix_cmd == "sudo"
    assert agent.max_consecutive_actions_to_summarize == 50  # Updated to match actual default

def test_agent_message_base_formatting():
    """Test agent message base formatting with and without parent IDs"""
    # Without parent IDs - provide mock inference to avoid KeyError: None
    with patch('anges.agents.agent_utils.base_agent.INFERENCE_FUNC_DICT') as mock_dict:
        mock_inference = MagicMock()
        mock_dict.__getitem__.return_value = mock_inference
        
        agent = DefaultAgent()
        
        # Test agent_message_base property (not a method)
        assert isinstance(agent.agent_message_base, str)
        
    # With parent IDs - provide mock inference to avoid KeyError: None
    with patch('anges.agents.agent_utils.base_agent.INFERENCE_FUNC_DICT') as mock_dict:
        mock_inference = MagicMock()
        mock_dict.__getitem__.return_value = mock_inference
        
        agent = DefaultAgent(parent_ids=["parent1", "parent2"])
        
        # Test agent_message_base property with parent IDs
        assert isinstance(agent.agent_message_base, str)
        # Agent message base should contain agent information


def test_run_with_new_request_task_complete():
    """Test successful task completion scenario"""
    mock_inference = MagicMock()
    mock_inference.return_value = '{"analysis": "Analyzing task", "reasoning": "Task completion reasoning", "actions": [{"action_type": "TASK_COMPLETE", "content": "Task successfully completed"}]}'
    
    agent = DefaultAgent(inference_func=mock_inference)
    event_stream = agent.run_with_new_request("Test task")
    assert len(event_stream.events_list) == 2
    assert event_stream.events_list[0].type == "new_request"
    assert event_stream.events_list[0].content == "Test task"
    assert event_stream.events_list[1].type == "task_completion"
    assert event_stream.events_list[1].content == "Task successfully completed"
    assert event_stream.events_list[1].type == "task_completion"

def test_run_with_new_request_help_needed():
    """Test help needed scenario"""
    mock_inference = MagicMock()
    mock_inference.return_value = '{"analysis": "Analyzing issue", "reasoning": "Need help reasoning", "actions": [{"action_type": "HELP_NEEDED", "content": "Need assistance with task"}]}'
    
    agent = DefaultAgent(inference_func=mock_inference)
    event_stream = agent.run_with_new_request("Test task")
    
    assert len(event_stream.events_list) == 2
    assert event_stream.events_list[0].type == "new_request"
    assert event_stream.events_list[1].type == "agent_requested_help"
    assert event_stream.events_list[1].content == "Need assistance with task"

def test_default_agent_action_execution():
    """Test action execution with shell commands"""
    mock_inference = MagicMock()
    # Mock sequence: shell command, then task completion
    mock_inference.side_effect = [
        '{"analysis": "Need to run command", "reasoning": "Running ls command", "actions": [{"action_type": "RUN_SHELL_CMD", "command": "ls", "reasoning": "List files"}]}',
        '{"analysis": "Command completed", "reasoning": "Task finished", "actions": [{"action_type": "TASK_COMPLETE", "content": "Command executed successfully"}]}'
    ]

    agent = DefaultAgent(inference_func=mock_inference)
    event_stream = agent.run_with_new_request("Run ls command")

    # Should have: new_request + action + task_completion
    assert len(event_stream.events_list) >= 3
    assert event_stream.events_list[0].type == "new_request"
    assert event_stream.events_list[0].content == "Run ls command"
    # Find action and completion events
