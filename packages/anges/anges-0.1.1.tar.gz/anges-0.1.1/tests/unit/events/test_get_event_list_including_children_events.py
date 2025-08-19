import pytest
import json
from unittest.mock import patch, MagicMock
from anges.agents.agent_utils.events import Event, EventStream, RETURN_TO_PARENT_EVENT_TYPES


@pytest.fixture
def parent_stream():
    stream = EventStream(title="ParentStream", uid="parent123")
    return stream


@pytest.fixture
def child_stream():
    stream = EventStream(title="ChildStream", uid="child456")
    # Add a normal event and a return-to-parent event to the child
    child_event_normal = Event(type="child_normal", reasoning="child reasoning", content="child content")
    child_event_return = Event(type="task_completion", reasoning="", content="")
    stream.events_list = [child_event_normal, child_event_return]
    return stream


def test_no_child_events(parent_stream):
    # Just some normal events
    event1 = Event(type="normal", reasoning="reason", content="content")
    event2 = Event(type="normal", reasoning="reason2", content="content2")
    parent_stream.events_list = [event1, event2]

    result = parent_stream.get_event_list_including_children_events(0)
    assert result == [event1, event2]


@patch("anges.agents.agent_utils.events.read_event_stream")
def test_child_events_success(mock_read, parent_stream, child_stream):
    event1 = Event(type="normal", reasoning="reason", content="content")
    event2 = Event(
        type="child_agent_running",
        reasoning=json.dumps({"agent_id": child_stream.uid, "starting_from": 0}),
        content="child event content"
    )
    event3 = Event(type="normal", reasoning="reason3", content="content3")
    parent_stream.events_list = [event1, event2, event3]

    # Mock read_event_stream to return the child_stream
    mock_read.return_value = child_stream

    # Flattened events should include event1, event2, then child's events, then event3
    result = parent_stream.get_event_list_including_children_events(0)
    expected = [event1, event2] + child_stream.events_list[:2] + [event3]  # stops at return-to-parent
    
    # First verify the lists have same length
    assert len(result) == len(expected), f"Lists have different lengths. Result: {len(result)}, Expected: {len(expected)}"

    # Then compare events one by one to give better error messages
    for i, (res, exp) in enumerate(zip(result, expected)):
        assert res == exp, f"Events at position {i} differ:\nResult:   {res}\nExpected: {exp}"


@patch("anges.agents.agent_utils.events.read_event_stream")
def test_child_events_loading_failure(mock_read, parent_stream, caplog):
    # Simulate a child event with invalid reasoning or failing load
    event1 = Event(type="normal", reasoning="reason", content="content")
def test_return_to_parent_event(parent_stream):
    # If we have a return-to-parent event and parent UIDs, we should stop immediately
    parent_stream.parent_event_stream_uids = ["parent123"]  # Add parent UID to trigger return behavior
    event1 = Event(type="normal", reasoning="reason", content="content")
    event2 = Event(type="task_completion", reasoning="", content="")  # return-to-parent event
    event3 = Event(type="normal", reasoning="ignored", content="ignored")
    parent_stream.events_list = [event1, event2, event3]

    result = parent_stream.get_event_list_including_children_events(0)
    # Should stop after event2 since we have a parent UID and a return-to-parent event
    assert result == [event1, event2]
    # Should stop after event2
    assert result == [event1, event2]
    mock_read.side_effect = Exception("Child load failed")

    result = parent_stream.get_event_list_including_children_events(0)
    # Since child failed, we should have event1, event2, then continue normally with event3
    assert result == [event1, event2, event3]

    # Check if an error was logged
    assert "Child load failed" in caplog.text


def test_return_to_parent_event(parent_stream):
    # If we have a return-to-parent event and parent UIDs, we should stop immediately
    parent_stream.parent_event_stream_uids = ["parent123"]  # Add parent UID to trigger return behavior
    event1 = Event(type="normal", reasoning="reason", content="content")
    event2 = Event(type="task_completion", reasoning="", content="")  # return-to-parent event
    event3 = Event(type="normal", reasoning="ignored", content="ignored")
    parent_stream.events_list = [event1, event2, event3]

    result = parent_stream.get_event_list_including_children_events(0)
    # Should stop after event2 since we have a parent UID and a return-to-parent event
    assert result == [event1, event2]
