import os
import pytest
from anges.web_interface.event_storage import EventStorage
from anges.agents.agent_utils.events import EventStream
from anges.utils import data_handler

@pytest.fixture
def test_data_dir(tmp_path, monkeypatch):
    """Create a temporary directory for test data"""
    test_dir = tmp_path / "test_event_streams"
    test_dir.mkdir()
    monkeypatch.setattr(data_handler, 'DATA_DIR', str(test_dir))
    return test_dir

@pytest.fixture
def event_storage(test_data_dir):
    return EventStorage()

@pytest.fixture
def sample_event_stream():
    return EventStream(title="Test Stream")

def test_save_and_load(event_storage, sample_event_stream):
    # Test saving
    save_result = event_storage.save(sample_event_stream)
    assert save_result is True
    stream_id = sample_event_stream.uid

    # Test loading
    loaded_stream = event_storage.load(stream_id)
    assert loaded_stream is not None
    assert loaded_stream.title == "Test Stream"
    assert loaded_stream.uid == stream_id

def test_list_streams(event_storage, sample_event_stream):
    # Save a stream first
    event_storage.save(sample_event_stream)
    stream_id = sample_event_stream.uid

    # Test listing
    streams = event_storage.list_streams()
    assert streams is not None
    assert isinstance(streams, list)
    assert stream_id in streams

def test_update_stream_title(event_storage, sample_event_stream):
    # Save a stream first
    event_storage.save(sample_event_stream)
    stream_id = sample_event_stream.uid

    # Update title
    new_title = "Updated Test Stream"
    event_storage.update_stream_title(stream_id, new_title)

    # Verify update
    updated_stream = event_storage.load(stream_id)
    assert updated_stream is not None
    assert updated_stream.title == new_title

def test_delete_stream(event_storage, sample_event_stream):
    # Save a stream first
    event_storage.save(sample_event_stream)
    stream_id = sample_event_stream.uid

    # Delete stream
    delete_result = event_storage.delete_stream(stream_id)
    assert delete_result is True

    # Verify deletion
    streams = event_storage.list_streams()
    assert stream_id not in streams

    # Verify loading deleted stream returns None
    assert event_storage.load(stream_id) is None
