import pytest
from datetime import datetime
from anges.agents.agent_utils.events import Event, EventSummary, EventStream

def test_event_stream_empty_serialization():
    """Test serialization of an empty event stream"""
    stream = EventStream()
    stream_dict = stream.to_dict()
    reconstructed = EventStream.from_dict(stream_dict)
    assert stream == reconstructed
    assert len(reconstructed.events_list) == 0
    assert len(reconstructed.event_summaries_list) == 0

def test_event_stream_complex_serialization():
    """Test serialization with multiple events and summaries"""
    stream = EventStream(title="Complex Test")
    
    # Add multiple events
    events = [
        Event("type1", "reason1", "content1", "title1"),
        Event("type2", "reason2", "content2", None),
        Event("type3", None, "content3", "title3"),
        Event("type4", "reason4", None, None)
    ]
    for event in events:
        stream.events_list.append(event)
    
    # Add multiple summaries
    summaries = [
        EventSummary("summary1", 0, 1, "First summary"),
        EventSummary("summary2", 2, 3, "Second summary")
    ]
    for summary in summaries:
        stream.event_summaries_list.append(summary)
    
    # Test serialization
    stream_dict = stream.to_dict()
    reconstructed = EventStream.from_dict(stream_dict)
    
    assert stream == reconstructed
    assert len(reconstructed.events_list) == 4
    assert len(reconstructed.event_summaries_list) == 2
    
    # Verify specific fields
    assert reconstructed.events_list[0].title == "title1"
    assert reconstructed.events_list[1].title is None
    assert reconstructed.events_list[2].reasoning is None
    assert reconstructed.events_list[3].content is None

def test_event_stream_datetime_serialization():
    """Test proper datetime handling in serialization"""
    stream = EventStream()
    event = Event("test", "reason", "content")
    specific_time = datetime(2023, 1, 1, 12, 0, 0)
    event.created_at = specific_time
    stream.created_at = specific_time
    stream.events_list.append(event)
    
    stream_dict = stream.to_dict()
    reconstructed = EventStream.from_dict(stream_dict)
    
    assert stream == reconstructed
    assert reconstructed.created_at == specific_time
    assert reconstructed.events_list[0].created_at == specific_time
