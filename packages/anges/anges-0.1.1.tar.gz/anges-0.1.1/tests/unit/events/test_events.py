import pytest
from datetime import datetime
import unittest
from anges.agents.agent_utils.events import Event, EventSummary, EventStream

class TestEvent(unittest.TestCase):
    def test_event_initialization(self):
        # Test default initialization
        event = Event(type="test")
        self.assertEqual(event.type, "test")
        self.assertEqual(event.est_input_token, 0)
        self.assertEqual(event.est_output_token, 0)

        # Test initialization with token values
        event = Event(
            type="test",
            reasoning="test reasoning",
            content="test content",
            title="test title",
            message="test message",
            analysis="test analysis",
            est_input_token=100,
            est_output_token=50
        )
        self.assertEqual(event.est_input_token, 100)
        self.assertEqual(event.est_output_token, 50)

    def test_event_serialization(self):
        event = Event(
            type="test",
            reasoning="test reasoning",
            content="test content",
            title="test title",
            est_input_token=100,
            est_output_token=50
        )
        event_dict = event.to_dict()
        
        # Verify token fields are included in serialization
        self.assertEqual(event_dict["est_input_token"], 100)
        self.assertEqual(event_dict["est_output_token"], 50)

    def test_event_deserialization(self):
        # Test deserialization with token fields
        data = {
            "type": "test",
            "reasoning": "test reasoning",
            "content": "test content",
            "title": "test title",
            "message": "test message",
            "analysis": "test analysis",
            "est_input_token": 100,
            "est_output_token": 50,
            "created_at": datetime.now().isoformat()
        }
        event = Event.from_dict(data)
        self.assertEqual(event.est_input_token, 100)
        self.assertEqual(event.est_output_token, 50)

    def test_backward_compatibility(self):
        # Test deserialization of old event format without token fields
        old_data = {
            "type": "test",
            "reasoning": "test reasoning",
            "content": "test content",
            "title": "test title",
            "message": "test message",
            "analysis": "test analysis",
            "created_at": datetime.now().isoformat()
        }
        event = Event.from_dict(old_data)
        
        # Verify default values are used
        self.assertEqual(event.est_input_token, 0)
        self.assertEqual(event.est_output_token, 0)

def test_event_serialization():
    """Test event serialization with new message and analysis fields."""
    # Create an event with all fields including new ones
    event = Event(
        type="test_type",
        reasoning="test reasoning",
        content="test content",
        title="test title",
        message="test message",
        analysis="test analysis"
    )

    # Convert to dictionary
    event_dict = event.to_dict()

    # Verify all fields are present in dictionary
    assert event_dict['type'] == "test_type"
    assert event_dict['reasoning'] == "test reasoning"
    assert event_dict['content'] == "test content"
    assert event_dict['title'] == "test title"
    assert event_dict['message'] == "test message"
    assert event_dict['analysis'] == "test analysis"
    assert 'created_at' in event_dict

    # Test deserialization
    reconstructed_event = Event.from_dict(event_dict)
    assert event == reconstructed_event

    # Test backward compatibility (without new fields)
    old_event_dict = {
        'type': 'old_type',
        'reasoning': 'old reasoning',
        'content': 'old content',
        'title': 'old title',
        'created_at': datetime.now().isoformat()
    }
    old_event = Event.from_dict(old_event_dict)
    assert old_event.message == ''  # Should default to empty string
    assert old_event.analysis == ''  # Should default to empty string

def test_event_summary_serialization():
    """Test event summary serialization."""
    # Create an event summary
    summary = EventSummary(
        type="test_summary",
        start_event_idx=0,
        end_event_idx=5,
        summary="Test summary content"
    )

    # Convert to dict and back
    summary_dict = summary.to_dict()
    reconstructed_summary = EventSummary.from_dict(summary_dict)

    # Verify equality
    assert summary == reconstructed_summary

def test_event_stream_serialization():
    """Test event stream serialization with events containing new fields."""
    # Create an event stream with some events and summaries
    stream = EventStream(
        title="Test Stream",
        uid="test123",
        parent_event_stream_uids=["parent456"]
    )

    # Add an event with new fields
    event = Event(
        type="test_type",
        reasoning="test reasoning",
        content="test content",
        message="test message",
        analysis="test analysis"
    )
    summary = EventSummary("test_summary", 0, 1, "Test summary")

    stream.events_list.append(event)
    stream.event_summaries_list.append(summary)

    # Convert to dict and back
    stream_dict = stream.to_dict()
    reconstructed_stream = EventStream.from_dict(stream_dict)

    # Verify equality
    assert stream == reconstructed_stream

def test_equality_comparison():
    """Test equality comparison for all event-related classes."""
    # Test Event equality with new fields
    event1 = Event("type", "reasoning", "content", "title", "message", "analysis")
    event2 = Event("type", "reasoning", "content", "title", "message", "analysis")
    event3 = Event("different", "reasoning", "content", "title", "message", "analysis")

    assert event1 == event2
    assert event1 != event3
    assert event1 != "not an event"

    # Test EventSummary equality
    summary1 = EventSummary("type", 0, 1, "summary")
    summary2 = EventSummary("type", 0, 1, "summary")
    summary3 = EventSummary("different", 0, 1, "summary")

    assert summary1 == summary2
    assert summary1 != summary3
    assert summary1 != "not a summary"

    # Test EventStream equality
    stream1 = EventStream("title", "uid", "parent")
    stream2 = EventStream("title", "uid", "parent")
    stream3 = EventStream("different", "uid", "parent")

    assert stream1 == stream2
    assert stream1 != stream3
    assert stream1 != "not a stream"
