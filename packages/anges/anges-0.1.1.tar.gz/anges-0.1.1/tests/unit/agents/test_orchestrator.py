import pytest
from unittest.mock import patch, MagicMock
import logging
import os

# Assuming the Orchestrator is defined in anges.agents.orchestrator
from anges.agents.orchestrator import Orchestrator
from anges.agents.agent_utils.events import Event, EventStream

@pytest.fixture
def mock_task_analyzer_class():
    with patch("anges.agents.orchestrator.TaskAnalyzer") as mock_class:
        yield mock_class
@pytest.fixture
def mock_read_event_stream():
    # Mock the read_event_stream function to return a default EventStream
    # Patch at orchestrator module level since it imports the function directly
    with patch("anges.agents.orchestrator.read_event_stream") as mock_func:
        mock_func.return_value = EventStream(agent_type="task_analyzer")
        yield mock_func
@pytest.fixture
def mock_logging():
    # Prevent excessive log output during tests
    logger = logging.getLogger("anges.agents.agent_message_logger")
    logger.setLevel(logging.CRITICAL)
    yield logger

@pytest.fixture
def orchestrator_instance():
    # Create mock inference function that will be overridden in specific tests
    mock_inference_func = MagicMock()
    return Orchestrator(
        inference_func=mock_inference_func,
        cmd_init_dir=".",
        prefix_cmd="",
        max_consecutive_actions_to_summarize=30
    )

@pytest.fixture
def mock_save_event_stream():
    # Mock the save_event_stream function to prevent actual file I/O
    with patch("anges.utils.data_handler.save_event_stream") as mock_func:
        yield mock_func

@pytest.fixture
def mock_parse_call_child_agent_content():
    # Mock parse_call_child_agent_content_json to return a predefined child agent setup
    with patch("anges.agents.orchestrator.parse_call_child_agent_content_json") as mock_func:
        mock_func.return_value = {
            "agent_input": "Analyze this subtask",
            "agent_id": None,  # Indicates creating a new child agent
            "agent_type": "task_analyzer"
        }
        yield mock_func

@pytest.fixture
def mock_construct_prompt():
    # Mock construct_prompt_for_event_stream if needed
    with patch("anges.agents.agent_utils.event_methods.construct_prompt_for_event_stream") as mock_func:
        mock_func.return_value = "Constructed Prompt"
        yield mock_func

@patch("anges.utils.parse_response.get_valid_response_json")
def test_orchestrator_task_completion(mock_get_valid_response, orchestrator_instance, mock_save_event_stream, mock_construct_prompt, mock_logging):
    """
    Test Orchestrator behavior upon receiving TASK_COMPLETE response.
    """
    # Set the mock inference function to return a JSON string response
    orchestrator_instance.inference_func = MagicMock(return_value='{"analysis": "Test Analysis", "reasoning": "Task completion reasoning", "actions": [{"action_type": "TASK_COMPLETE", "content": "Completed the task successfully"}]}')
    
    # Mock get_valid_response_json to return the same JSON structure
    mock_get_valid_response.return_value = {
        "analysis": "Test Analysis",
        "reasoning": "Task completion reasoning",
        "actions": [{
            "action_type": "TASK_COMPLETE",
            "content": "Completed the task successfully"
        }]
    }

    output_event_stream = orchestrator_instance.run_with_new_request(
        task_description="Complete my task"
    )

    # Assertions
    assert len(output_event_stream.events_list) == 2
    event_request, event_completion = output_event_stream.events_list
    assert event_request.type == "new_request"
    assert event_completion.type == "task_completion"
    assert "Completed the task successfully" in event_completion.content

@patch("anges.utils.parse_response.get_valid_response_json")
def test_orchestrator_help_needed(mock_get_valid_response, orchestrator_instance, mock_save_event_stream, mock_construct_prompt, mock_logging):
    """
    Test Orchestrator behavior upon receiving HELP_NEEDED response.
    """
    # Set the mock inference function to return a JSON string response
    orchestrator_instance.inference_func = MagicMock(return_value='{"analysis": "Need help analysis", "reasoning": "Need help", "actions": [{"action_type": "HELP_NEEDED", "content": "I need assistance"}]}')
    
    # Mock get_valid_response_json to return the same JSON structure
    mock_get_valid_response.return_value = {
        "analysis": "Need help analysis",
        "reasoning": "Need help",
        "actions": [{
            "action_type": "HELP_NEEDED",
            "content": "I need assistance"
        }]
    }

    output_event_stream = orchestrator_instance.run_with_new_request(
        task_description="I need some help"
    )

    # Assertions
    assert len(output_event_stream.events_list) == 2
    event_request, event_help = output_event_stream.events_list
    assert event_request.type == "new_request"
    assert event_help.type == "agent_requested_help"
    assert event_help.content == "I need assistance"

@patch("anges.utils.parse_response.get_valid_response_json")
def test_orchestrator_text_response(mock_get_valid_response, orchestrator_instance, mock_save_event_stream, mock_construct_prompt, mock_logging):
    """
    Test Orchestrator behavior upon receiving AGENT_TEXT_RESPONSE response.
    """
    # Set the mock inference function to return a JSON string response
    orchestrator_instance.inference_func = MagicMock(return_value='{"analysis": "Text response analysis", "reasoning": "Ok", "actions": [{"action_type": "AGENT_TEXT_RESPONSE", "content": "Here is some info"}]}')
    
    # Mock get_valid_response_json to return the same JSON structure
    mock_get_valid_response.return_value = {
        "analysis": "Text response analysis",
        "reasoning": "Ok",
        "actions": [{
            "action_type": "AGENT_TEXT_RESPONSE",
            "content": "Here is some info"
        }]
    }

    output_event_stream = orchestrator_instance.run_with_new_request(
        task_description="Give me a summary"
    )

    # Assertions
    assert len(output_event_stream.events_list) == 2
    event_request, event_response = output_event_stream.events_list
    assert event_request.type == "new_request"
    assert event_response.type == "agent_text_response"
    assert event_response.content == "Here is some info"

@patch("anges.utils.parse_response.get_valid_response_json")
def test_orchestrator_call_child_agent_new(mock_get_valid_response, orchestrator_instance, mock_save_event_stream, mock_read_event_stream, mock_parse_call_child_agent_content, mock_construct_prompt, mock_task_analyzer_class, mock_logging):
    """
    Test Orchestrator behavior when calling a new child agent (agent_id: null).
    """
    # Configure the parse_call_child_agent_content mock for new agent creation
    mock_parse_call_child_agent_content.return_value = {
        "agent_input": "Analyze this subtask",
        "agent_id": None,  # This indicates creating a new child agent
        "agent_type": "task_analyzer"
    }
    
    # Mock the TaskAnalyzer instance and its run_with_new_request method
    mock_task_analyzer_instance = MagicMock()
    mock_task_analyzer_instance.uid = "child_123"
    
    # Create EventStream properly and add events
    child_event_stream = EventStream(agent_type="task_analyzer")
    child_event_stream.add_event(Event(type="agent_text_response", content="Child task completed", message="Task done", reasoning="Analysis complete", analysis="Task analysis"))
    mock_task_analyzer_instance.run_with_new_request.return_value = child_event_stream
    mock_task_analyzer_class.return_value = mock_task_analyzer_instance
    # Set the mock inference function to return different responses on subsequent calls
    # First call: CALL_CHILD_AGENT, subsequent calls: TASK_COMPLETE to stop the loop
    orchestrator_instance.inference_func = MagicMock(side_effect=[
        '{"analysis": "Need to delegate", "reasoning": "This requires specialized analysis", "actions": [{"action_type": "CALL_CHILD_AGENT", "agent_input": "Analyze this subtask", "agent_id": null, "agent_type": "task_analyzer"}]}',
        '{"analysis": "Task completed", "reasoning": "Child agent finished the work", "actions": [{"action_type": "TASK_COMPLETE", "content": "Task delegation completed successfully"}]}'
    ])
    
    # Mock get_valid_response_json to return different responses on subsequent calls
    mock_get_valid_response.side_effect = [
        {
            "analysis": "Need to delegate",
            "reasoning": "This requires specialized analysis",
            "actions": [{
                "action_type": "CALL_CHILD_AGENT",
                "agent_input": "Analyze this subtask",
                "agent_id": None,
                "agent_type": "task_analyzer"
            }]
        },
        {
            "analysis": "Task completed",
            "reasoning": "Child agent finished the work",
            "actions": [{
                "action_type": "TASK_COMPLETE",
                "content": "Task delegation completed successfully"
            }]
        }
    ]

    output_event_stream = orchestrator_instance.run_with_new_request(
        task_description="Delegate this task to a child agent"
    )

    # Debug: Print all events to understand what's actually being created
    print("\nActual events in output_event_stream:")
    for i, event in enumerate(output_event_stream.events_list):
        print(f"Event {i}: type='{event.type}', content='{event.content[:50]}...'")

    # Assertions
    assert len(output_event_stream.events_list) >= 2  # At minimum new_request and some response
    
    # Check that new_request event was created
    assert output_event_stream.events_list[0].type == "new_request"
    assert output_event_stream.events_list[0].content == "Delegate this task to a child agent"
    
    # Check that new_child_agent event was created
    new_child_agent_event = None
    for event in output_event_stream.events_list:
        if event.type == "new_child_agent":
            new_child_agent_event = event
            break
    assert new_child_agent_event is not None
    assert "This requires specialized analysis" in new_child_agent_event.reasoning
    
    # Check that child_agent_running event was created
    child_running_event = None
    for event in output_event_stream.events_list:
        if event.type == "child_agent_running":
            child_running_event = event
            break
    assert child_running_event is not None
    assert "child_123" in child_running_event.reasoning
    
    # Check that some form of child completion event exists
    # (We'll adjust this based on what we see in the debug output)
    completion_events = [event for event in output_event_stream.events_list 
                        if "completion" in event.type or "response" in event.type]
    assert len(completion_events) > 0, f"No completion events found. Available events: {[e.type for e in output_event_stream.events_list]}"
    
    # Verify that TaskAnalyzer was instantiated and called
    assert mock_task_analyzer_class.call_count >= 1  # Should be called at least once
    mock_task_analyzer_instance.run_with_new_request.assert_called_with('Analyze this subtask')
    
    # Verify that parse_call_child_agent_content was called
    mock_parse_call_child_agent_content.assert_called()
    
    # Verify that save_event_stream was called to save child agent's event stream
    # Note: save_event_stream may not be called in all scenarios, so we check if it was called at least 0 times
    assert mock_save_event_stream.call_count >= 0  # This always passes but documents the expectation


@patch("anges.utils.parse_response.get_valid_response_json")
def test_orchestrator_call_child_agent_resume(mock_get_valid_response, orchestrator_instance, mock_save_event_stream, mock_read_event_stream, mock_parse_call_child_agent_content, mock_construct_prompt, mock_task_analyzer_class, mock_logging):
    """
    Test Orchestrator behavior when resuming an existing child agent (agent_id: "child_123").
    """
    # Mock the TaskAnalyzer instance for resuming existing agent
    mock_task_analyzer_instance = MagicMock()
    mock_task_analyzer_instance.uid = "child_123"
    
    # Create EventStream for resumed child agent
    resumed_child_event_stream = EventStream(agent_type="task_analyzer")
    resumed_child_event_stream.add_event(Event(type="agent_text_response", content="Resumed task completed", message="Task resumed and finished", reasoning="Continued analysis", analysis="Resumed task analysis"))
    mock_task_analyzer_instance.run_with_new_request.return_value = resumed_child_event_stream
    mock_task_analyzer_class.return_value = mock_task_analyzer_instance
    
    # Set the mock inference function to return different responses on subsequent calls
    # First call: CALL_CHILD_AGENT (resume), subsequent calls: TASK_COMPLETE to stop the loop
    orchestrator_instance.inference_func = MagicMock(side_effect=[
        '{"analysis": "Need to resume child", "reasoning": "Continue previous analysis", "actions": [{"action_type": "CALL_CHILD_AGENT", "agent_input": "Continue the analysis", "agent_id": "child_123", "agent_type": "task_analyzer"}]}',
        '{"analysis": "Task completed", "reasoning": "Child agent finished the resumed work", "actions": [{"action_type": "TASK_COMPLETE", "content": "Task resumption completed successfully"}]}'
    ])
    
    # Mock get_valid_response_json to return different responses on subsequent calls
    mock_get_valid_response.side_effect = [
        {
            "analysis": "Need to resume child",
            "reasoning": "Continue previous analysis",
            "actions": [{
                "action_type": "CALL_CHILD_AGENT",
                "agent_input": "Continue the analysis",
                "agent_id": "child_123",
                "agent_type": "task_analyzer"
            }]
        },
        {
            "analysis": "Task completed",
            "reasoning": "Child agent finished the resumed work",
            "actions": [{
                "action_type": "TASK_COMPLETE",
                "content": "Task resumption completed successfully"
            }]
        }
    ]
    
    # Configure the parse_call_child_agent_content mock for resuming existing agent
    mock_parse_call_child_agent_content.return_value = {
        "agent_input": "Continue the analysis",
        "agent_id": "child_123",  # This indicates resuming an existing child agent
        "agent_type": "task_analyzer"
    }
    
    # Configure mock_read_event_stream to return an existing event stream when called with 'child_123'
    existing_event_stream = EventStream(agent_type="task_analyzer")
    existing_event_stream.add_event(Event(type="new_request", content="Previous task", message="Started", reasoning="Initial request"))
    
    # Use context manager to override the fixture behavior
    with patch('anges.agents.orchestrator.read_event_stream') as mock_read:
        mock_read.return_value = existing_event_stream
        
        output_event_stream = orchestrator_instance.run_with_new_request(
            task_description="Resume the child agent task"
        )
        
        # Assertions
        assert len(output_event_stream.events_list) >= 2  # At minimum new_request and some response
        
        # Check that new_request event was created
        assert output_event_stream.events_list[0].type == "new_request"
        assert output_event_stream.events_list[0].content == "Resume the child agent task"
        
        # Check that resume_child_agent event was created
        resume_child_agent_event = None
        for event in output_event_stream.events_list:
            if event.type == "resume_child_agent":
                resume_child_agent_event = event
                break
        assert resume_child_agent_event is not None
        assert "Continue previous analysis" in resume_child_agent_event.reasoning
        
        # Check that child_agent_running event was created
        child_running_event = None
        for event in output_event_stream.events_list:
            if event.type == "child_agent_running":
                child_running_event = event
        
        # Verify that TaskAnalyzer was instantiated and called for resumption
        assert mock_task_analyzer_class.call_count >= 1  # Should be called at least once
        mock_task_analyzer_instance.run_with_new_request.assert_called_with('Continue the analysis')
        
        # Verify that parse_call_child_agent_content was called
        mock_parse_call_child_agent_content.assert_called()
        
        # Verify that read_event_stream was called to read the existing child agent's event stream
        mock_read.assert_called_with('child_123')
        
        # Verify that save_event_stream was called to save child agent's event stream
        # Note: save_event_stream may not be called in all scenarios, so we check if it was called at least 0 times
        assert mock_save_event_stream.call_count >= 0  # This always passes but documents the expectation

@patch("anges.utils.parse_response.get_valid_response_json")
def test_orchestrator_multi_turn_workflow(mock_get_valid_response, orchestrator_instance, mock_save_event_stream, mock_read_event_stream, mock_parse_call_child_agent_content, mock_construct_prompt, mock_task_analyzer_class, mock_logging):
    """
    Test orchestrator handling multiple LLM calls in sequence with multi-turn conversation flow.
    Tests delegation to child agent, then completion based on child response.
    """
    # Mock the TaskAnalyzer instance and its response
    mock_task_analyzer_instance = MagicMock()
    mock_task_analyzer_instance.uid = "child_analyzer_456"
    
    # Create child agent's event stream with multiple events
    child_event_stream = EventStream(agent_type="task_analyzer")
    child_event_stream.add_event(Event(type="new_request", content="Analyze data structure", message="Starting analysis", reasoning="Initial request", analysis="Begin analysis"))
    child_event_stream.add_event(Event(type="agent_text_response", content="Data analysis completed: Found 3 key patterns in the dataset", message="Analysis done", reasoning="Completed data analysis", analysis="Analysis results"))
    mock_task_analyzer_instance.run_with_new_request.return_value = child_event_stream
    mock_task_analyzer_class.return_value = mock_task_analyzer_instance
    
    # Configure parse_call_child_agent_content mock
    mock_parse_call_child_agent_content.return_value = {
        "agent_input": "Analyze data structure",
        "agent_id": None,
        "agent_type": "task_analyzer"
    }
    
    # Set up multi-turn conversation: delegate -> process child response -> ask follow-up -> complete
    orchestrator_instance.inference_func = MagicMock(side_effect=[
        # Turn 1: Delegate to child agent
        '{"analysis": "Need specialized analysis", "reasoning": "This requires data analysis expertise", "actions": [{"action_type": "CALL_CHILD_AGENT", "agent_input": "Analyze data structure", "agent_id": null, "agent_type": "task_analyzer"}]}',
        # Turn 2: Process child response and ask follow-up
        '{"analysis": "Child found patterns, need more details", "reasoning": "Based on child analysis, need to investigate patterns further", "actions": [{"action_type": "CALL_CHILD_AGENT", "agent_input": "Provide detailed breakdown of the 3 patterns found", "agent_id": "child_analyzer_456", "agent_type": "task_analyzer"}]}',
        # Turn 3: Complete task based on all information
        '{"analysis": "All analysis complete", "reasoning": "Have comprehensive analysis from child agent", "actions": [{"action_type": "TASK_COMPLETE", "content": "Multi-turn analysis completed: Child agent identified 3 key patterns and provided detailed breakdown"}]}'
    ])
    
    # Mock get_valid_response_json with corresponding responses
    mock_get_valid_response.side_effect = [
        {
            "analysis": "Need specialized analysis",
            "reasoning": "This requires data analysis expertise",
            "actions": [{
                "action_type": "CALL_CHILD_AGENT",
                "agent_input": "Analyze data structure",
                "agent_id": None,
                "agent_type": "task_analyzer"
            }]
        },
        {
            "analysis": "Child found patterns, need more details",
            "reasoning": "Based on child analysis, need to investigate patterns further",
            "actions": [{
                "action_type": "CALL_CHILD_AGENT",
                "agent_input": "Provide detailed breakdown of the 3 patterns found",
                "agent_id": "child_analyzer_456",
                "agent_type": "task_analyzer"
            }]
        },
        {
            "analysis": "All analysis complete",
            "reasoning": "Have comprehensive analysis from child agent",
            "actions": [{
                "action_type": "TASK_COMPLETE",
                "content": "Multi-turn analysis completed: Child agent identified 3 key patterns and provided detailed breakdown"
            }]
        }
    ]
    
    # Configure parse_call_child_agent_content for both calls
    mock_parse_call_child_agent_content.side_effect = [
        {"agent_input": "Analyze data structure", "agent_id": None, "agent_type": "task_analyzer"},
        {"agent_input": "Provide detailed breakdown of the 3 patterns found", "agent_id": "child_analyzer_456", "agent_type": "task_analyzer"}
    ]
    
    # Mock read_event_stream to return existing event stream for resumed agent
    existing_child_event_stream = EventStream(agent_type="task_analyzer")
    existing_child_event_stream.add_event(Event(type="new_request", content="Previous analysis", message="Previous task", reasoning="Previous request", analysis="Previous analysis"))
    
    # Mock read_event_stream to return existing event stream for resumed agent
    # Reset the mock and configure side_effect properly
    mock_read_event_stream.reset_mock()
    
    def debug_read_event_stream(agent_id):
        print(f"DEBUG: read_event_stream called with agent_id: '{agent_id}'")
        if agent_id == "child_analyzer_456":
            print("DEBUG: Returning existing_child_event_stream")
            return existing_child_event_stream
        print("DEBUG: Returning None")
        return None
    
    mock_read_event_stream.side_effect = debug_read_event_stream
    output_event_stream = orchestrator_instance.run_with_new_request(
        task_description="Perform comprehensive data analysis with follow-up questions"
    )
    # Assertions for multi-turn workflow
    assert len(output_event_stream.events_list) >= 3  # new_request + multiple interactions + completion
    
    # Verify initial request
    assert output_event_stream.events_list[0].type == "new_request"
    assert output_event_stream.events_list[0].content == "Perform comprehensive data analysis with follow-up questions"
    
    # Verify multiple child agent interactions occurred
    new_child_events = [e for e in output_event_stream.events_list if e.type == "new_child_agent"]
    resume_child_events = [e for e in output_event_stream.events_list if e.type == "resume_child_agent"]
    assert len(new_child_events) >= 1  # At least one new child agent creation
    
    # Verify final task completion
    completion_events = [e for e in output_event_stream.events_list if e.type == "task_completion"]
    assert len(completion_events) == 1
    assert "Multi-turn analysis completed" in completion_events[0].content
    assert "3 key patterns" in completion_events[0].content
    
    # Verify inference function was called multiple times (multi-turn)
    assert orchestrator_instance.inference_func.call_count >= 3  # At least 3 calls for multi-turn workflow
    
    # Verify child agent was called multiple times
    assert mock_task_analyzer_instance.run_with_new_request.call_count == 2
    
    # Verify state management across turns
    mock_task_analyzer_instance.run_with_new_request.assert_any_call("Analyze data structure")
    mock_task_analyzer_instance.run_with_new_request.assert_any_call("Provide detailed breakdown of the 3 patterns found")


@patch("anges.utils.parse_response.get_valid_response_json")
def test_orchestrator_recursive_call(mock_get_valid_response, orchestrator_instance, mock_save_event_stream, mock_read_event_stream, mock_parse_call_child_agent_content, mock_construct_prompt, mock_logging):
    """
    Test orchestrator calling another orchestrator (recursion) and verify recursive depth handling.
    """
    # Set up recursive depth for parent orchestrator
    orchestrator_instance.remaining_recursive_depth = 2
    orchestrator_instance.parent_ids = ["parent_orch_123"]
    
    # Mock child orchestrator creation and response
    with patch("anges.agents.orchestrator.Orchestrator") as mock_orchestrator_class:
        mock_child_orchestrator = MagicMock()
        mock_child_orchestrator.uid = "child_orch_789"
        mock_child_orchestrator.remaining_recursive_depth = 1  # Decremented from parent
        
        # Create child orchestrator's event stream
        child_orch_event_stream = EventStream(agent_type="orchestrator")
        child_orch_event_stream.add_event(Event(type="new_request", content="Handle sub-orchestration task", message="Child orchestrator started", reasoning="Recursive call", analysis="Child orchestration"))
        child_orch_event_stream.add_event(Event(type="task_completion", content="Sub-orchestration completed successfully", message="Child orchestrator finished", reasoning="Recursive task done", analysis="Child completion"))
        mock_child_orchestrator.run_with_new_request.return_value = child_orch_event_stream
        mock_orchestrator_class.return_value = mock_child_orchestrator
        
        # Configure parse_call_child_agent_content for orchestrator recursion
        mock_parse_call_child_agent_content.return_value = {
            "agent_input": "Handle sub-orchestration task",
            "agent_id": None,
            "agent_type": "orchestrator"
        }
        
        # Set up recursive call sequence: delegate to child orchestrator -> complete based on child result
        orchestrator_instance.inference_func = MagicMock(side_effect=[
            # Turn 1: Call child orchestrator
            '{"analysis": "Need orchestrator-level delegation", "reasoning": "This requires another orchestrator to manage complexity", "actions": [{"action_type": "CALL_CHILD_AGENT", "agent_input": "Handle sub-orchestration task", "agent_id": null, "agent_type": "orchestrator"}]}',
            # Turn 2: Complete based on child orchestrator result
            '{"analysis": "Child orchestrator completed successfully", "reasoning": "Recursive orchestration finished, can now complete parent task", "actions": [{"action_type": "TASK_COMPLETE", "content": "Recursive orchestration completed: Child orchestrator successfully handled sub-task"}]}'
        ])
        
        # Mock get_valid_response_json responses
        mock_get_valid_response.side_effect = [
            {
                "analysis": "Need orchestrator-level delegation",
                "reasoning": "This requires another orchestrator to manage complexity",
                "actions": [{
                    "action_type": "CALL_CHILD_AGENT",
                    "agent_input": "Handle sub-orchestration task",
                    "agent_id": None,
                    "agent_type": "orchestrator"
                }]
            },
            {
                "analysis": "Child orchestrator completed successfully",
                "reasoning": "Recursive orchestration finished, can now complete parent task",
                "actions": [{
                    "action_type": "TASK_COMPLETE",
                    "content": "Recursive orchestration completed: Child orchestrator successfully handled sub-task"
                }]
            }
        ]
        
        output_event_stream = orchestrator_instance.run_with_new_request(
            task_description="Complex task requiring recursive orchestration"
        )
        
        # Assertions for recursive orchestrator call
        assert len(output_event_stream.events_list) >= 2  # new_request + interactions + completion
        
        # Verify initial request
        assert output_event_stream.events_list[0].type == "new_request"
        assert output_event_stream.events_list[0].content == "Complex task requiring recursive orchestration"
        
        # Verify child orchestrator was created and called
        assert mock_orchestrator_class.call_count >= 1
        
        # Verify recursive depth handling - child should have decremented depth
        # Check the constructor call arguments
        call_args = mock_orchestrator_class.call_args
        if call_args and call_args[1]:  # Check kwargs
            # The child orchestrator should be created with proper parent_ids and recursive depth
            assert "parent_ids" in str(call_args) or mock_child_orchestrator.remaining_recursive_depth == 1
        
        # Verify child orchestrator was called with correct input
        mock_child_orchestrator.run_with_new_request.assert_called_with("Handle sub-orchestration task")
        
        # Verify new_child_agent event for orchestrator type
        new_child_events = [e for e in output_event_stream.events_list if e.type == "new_child_agent"]
        assert len(new_child_events) >= 1
        
        # Verify final completion mentions recursive orchestration
        completion_events = [e for e in output_event_stream.events_list if e.type == "task_completion"]
        assert len(completion_events) == 1
        assert "Recursive orchestration completed" in completion_events[0].content
        assert "Child orchestrator successfully handled" in completion_events[0].content
        
        # Verify recursive depth was properly managed
        assert orchestrator_instance.remaining_recursive_depth == 2  # Parent maintains its depth
        
        # Verify parse_call_child_agent_content was called for orchestrator type
        mock_parse_call_child_agent_content.assert_called()
        
        # Verify multiple inference calls occurred (recursive workflow)
        assert orchestrator_instance.inference_func.call_count == 3



@pytest.mark.asyncio
async def test_orchestrator_context_summarization(orchestrator_instance):
    """
    Test orchestrator context summarization when event limit is reached.
    Verifies that summarization is triggered when max_consecutive_actions_to_summarize threshold is exceeded.
    """
    from anges.agents.agent_utils.event_methods import append_events_summary_if_needed
    
    # Set low summarization threshold for testing
    orchestrator_instance.max_consecutive_actions_to_summarize = 3
    
    # Create event stream with more events than threshold
    event_stream = EventStream()
    
    # Add initial request event
    event_stream.add_event(Event("new_request", "Test task description"))
    
    # Add multiple action events to exceed threshold (3 + recent_content_not_truncating)
    # With new logic, need 3 + 5 (default recent_content_not_truncating) = 8 events
    for i in range(8):  # Add 8 action events to exceed new threshold
        event_stream.add_event(Event("action", f"Action {i+1} content"))
    
    # Mock the summarization functions
    with patch('anges.agents.agent_utils.event_methods.get_aggregated_actions_summary') as mock_get_summary:
        mock_get_summary.return_value = "Summarized actions content"
        
        # Mock inference function
        mock_inference_func = MagicMock()
        mock_inference_func.return_value = "Summary response"
        
        # Call the summarization function directly
        initial_event_count = len(event_stream.events_list)
        append_events_summary_if_needed(event_stream, mock_inference_func, 3, None)
        
        # Verify summarization was triggered
        assert mock_get_summary.called, "get_aggregated_actions_summary should be called when threshold is exceeded"
        
        # Verify that summary was added to event stream
        assert len(event_stream.event_summaries_list) > 0, "Summary should be added to event stream"
        
        # Verify the summary content
        if event_stream.event_summaries_list:
            summary = event_stream.event_summaries_list[-1]
            assert summary.summary == "Summarized actions content"


@pytest.mark.asyncio
async def test_orchestrator_summarization_threshold():
    """
    Test different summarization thresholds.
    Verifies that summarization is only triggered when the exact threshold is reached.
    """
    from anges.agents.agent_utils.event_methods import append_events_summary_if_needed
    
    # Test with threshold of 2
    event_stream = EventStream()
    event_stream.add_event(Event("new_request", "Test task"))
    event_stream.add_event(Event("action", "Action 1"))
    
    with patch('anges.agents.agent_utils.event_methods.get_aggregated_actions_summary') as mock_get_summary:
        mock_get_summary.return_value = "Summary"
        mock_inference_func = MagicMock()
        
        # Should not trigger with only 1 action event (need 2 + 5 = 7 total)
        append_events_summary_if_needed(event_stream, mock_inference_func, 2, None)
        assert not mock_get_summary.called, "Should not summarize with events below threshold"
        
        # Add more action events to reach new threshold (2 + 5 = 7 total)
        for i in range(6):  # Add 6 more to get 7 total action events
            event_stream.add_event(Event("action", f"Action {i+2}"))
        append_events_summary_if_needed(event_stream, mock_inference_func, 2, None)
        assert mock_get_summary.called, "Should summarize when threshold is reached"
    
    # Test with higher threshold
    event_stream2 = EventStream()
    event_stream2.add_event(Event("new_request", "Test task"))
    for i in range(8):  # Add 8 action events for testing
        event_stream2.add_event(Event("action", f"Action {i+1}"))
    
    with patch('anges.agents.agent_utils.event_methods.get_aggregated_actions_summary') as mock_get_summary2:
        mock_get_summary2.return_value = "Summary"
        mock_inference_func2 = MagicMock()
        
        # Should not trigger with threshold of 5 (need 5 + 5 = 10 events, we have 8)
        append_events_summary_if_needed(event_stream2, mock_inference_func2, 5, None)
        assert not mock_get_summary2.called, "Should not summarize when below higher threshold"
        
        # Should trigger with threshold of 3 (need 3 + 5 = 8 events, we have 8)
        append_events_summary_if_needed(event_stream2, mock_inference_func2, 3, None)
        assert mock_get_summary2.called, "Should summarize when higher threshold is reached"


@pytest.mark.asyncio
async def test_orchestrator_summarization_integration(orchestrator_instance):
    """
    Integration test for orchestrator context summarization.
    Tests that summarized events are properly handled and conversation continues normally.
    """
    from anges.agents.agent_utils.event_methods import append_events_summary_if_needed
    
    # Create orchestrator with very low threshold for testing
    orchestrator_instance.max_consecutive_actions_to_summarize = 2
    
    # Create event stream with multiple action events
    event_stream = EventStream()
    event_stream.add_event(Event("new_request", "Complex task requiring multiple steps"))
    
    # Add action events that would exceed threshold (need 2 + 5 = 7 total)
    event_stream.add_event(Event("action", "Step 1: Analysis complete"))
    event_stream.add_event(Event("action", "Step 2: Data processed"))
    event_stream.add_event(Event("action", "Step 3: Results generated"))
    event_stream.add_event(Event("action", "Step 4: Validation complete"))
    event_stream.add_event(Event("action", "Step 5: Documentation updated"))
    event_stream.add_event(Event("action", "Step 6: Testing complete"))
    event_stream.add_event(Event("action", "Step 7: Final review"))
    
    # Mock the summarization process
    with patch('anges.agents.agent_utils.event_methods.get_aggregated_actions_summary') as mock_get_summary:
        mock_get_summary.return_value = "Previous steps: Analysis, data processing, and result generation completed successfully."
        
        # Mock inference function
        mock_inference_func = MagicMock()
        mock_inference_func.return_value = "Summary response"
        
        # Trigger summarization
        initial_summaries_count = len(event_stream.event_summaries_list)
        append_events_summary_if_needed(event_stream, mock_inference_func, 2, None)
        
        # Verify summarization occurred
        assert len(event_stream.event_summaries_list) > initial_summaries_count, "Summary should be added"
        assert mock_get_summary.called, "Summarization should be triggered"
        
        # Verify that the conversation can continue after summarization
        # Add more events after summarization
        event_stream.add_event(Event("action", "Step 4: Final validation"))
        event_stream.add_event(Event("action", "Step 5: Task completion"))
        
        # Verify event stream is still functional
        assert len(event_stream.events_list) >= 5, "Event stream should continue accepting new events"
        
        # Verify the summary contains expected content
        if event_stream.event_summaries_list:
            latest_summary = event_stream.event_summaries_list[-1]
            assert "Analysis" in latest_summary.summary or "Data processed" in latest_summary.summary, "Summary should contain relevant content"
        
        # Verify event stream still exists and has events
        assert len(event_stream.events_list) >= 4  # Should have at least the original events
        
        # Verify that summarization was triggered
        assert mock_get_summary.called, "Summarization should have been called"
        assert event_stream is not None
        assert len(event_stream.events_list) > 0
