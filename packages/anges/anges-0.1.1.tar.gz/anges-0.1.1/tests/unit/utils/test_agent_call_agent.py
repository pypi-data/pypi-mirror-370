import os
import pytest
from anges.utils.agent_call_agent import parse_call_child_agent_content_json

def test_parse_new_task_analyzer():
    content = {
        "directive": "NEW_CHILD_AGENT TASK_ANALYZER",
        "agent_input": "This is a test task for the analyzer."
    }
    parsed = parse_call_child_agent_content_json(content)
    assert parsed["agent_type"] == "TASK_ANALYZER"
    assert parsed["agent_id"] is None
    assert parsed["agent_input"] == "This is a test task for the analyzer."

def test_parse_new_task_executor():
    content = {
        "directive": "NEW_CHILD_AGENT TASK_EXECUTOR",
        "agent_input": "This is a test task for the executor."
    }
    parsed = parse_call_child_agent_content_json(content)
    assert parsed["agent_type"] == "TASK_EXECUTOR"
    assert parsed["agent_id"] is None
    assert parsed["agent_input"] == "This is a test task for the executor."

def test_parse_new_task_executor_with_plan():
    content = {
        "directive": "NEW_CHILD_AGENT TASK_EXECUTOR",
        "agent_input": "Given the original user request:\n\nSome of my unit tests are broken, fix them\n\nAn senior engineer has done analysis and came up with a detailed execution plan. Now you need to follow the plan and execute the task:\n<paste the full execution plan from the Task Analyzer here>"
    }
    parsed = parse_call_child_agent_content_json(content)
    assert parsed["agent_type"] == "TASK_EXECUTOR"
    assert parsed["agent_id"] is None
    assert parsed["agent_input"] == "Given the original user request:\n\nSome of my unit tests are broken, fix them\n\nAn senior engineer has done analysis and came up with a detailed execution plan. Now you need to follow the plan and execute the task:\n<paste the full execution plan from the Task Analyzer here>"

def test_parse_resume_task_executor():
    content = {
        "directive": "RESUME_CHILD_AGENT agent123",
        "agent_input": "This is a follow-up task."
    }
    parsed = parse_call_child_agent_content_json(content)
    assert parsed["agent_type"] is None
    assert parsed["agent_id"] == "agent123"
    assert parsed["agent_input"] == "This is a follow-up task."

def test_parse_empty_input():
    content = {
        "directive": "NEW_CHILD_AGENT TASK_EXECUTOR",
        "agent_input": ""
    }
    parsed = parse_call_child_agent_content_json(content)
    assert parsed["agent_type"] == "TASK_EXECUTOR"
    assert parsed["agent_id"] is None
    assert parsed["agent_input"] == ""

def test_parse_invalid_directive():
    content = {
        "directive": "INVALID_DIRECTIVE",
        "agent_input": "This should not be parsed."
    }
    with pytest.raises(ValueError, match="Failed to parse call child agent action from content, no agent_type or agent_id found"):
        parse_call_child_agent_content_json(content)

def test_parse_resume_without_id():
    content = {
        "directive": "RESUME_CHILD_AGENT",
        "agent_input": "This should also handle missing ID."
    }
    with pytest.raises(ValueError, match="Failed to parse call child agent action from content, no agent_type or agent_id found"):
        parse_call_child_agent_content_json(content)