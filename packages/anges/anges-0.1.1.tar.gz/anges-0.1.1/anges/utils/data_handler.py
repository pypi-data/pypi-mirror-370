import os
import json
from ..agents.agent_utils.events import EventStream
from .shared_base import DATA_DIR
from .event_storage_service import EventStorageService
import logging

# Create a singleton instance of EventStorageService for internal use
_event_storage_service = EventStorageService()

def get_data_dir():
    """Get the current data directory, respecting any override set by set_data_dir()"""
    return _event_storage_service.get_data_dir()

def set_data_dir(path):
    """Set the data directory path"""
    _event_storage_service.set_data_dir(path)

def ensure_data_dir():
    """Ensure the data directory exists"""
    _event_storage_service.ensure_data_dir()

def save_event_stream(event_stream: EventStream) -> str:
    """Save an EventStream object as a JSON file.

    Args:
        event_stream (EventStream): The event stream to save

    Returns:
        str: The UID of the saved stream if successful, None otherwise
    """
    if event_stream is None or not isinstance(event_stream, EventStream):
        return None
    
    try:
        success = _event_storage_service.save_event_stream(event_stream)
        return event_stream.uid if success else None
    except Exception as e:
        logging.error(f"Error saving event stream: {e}")
        return None

def list_event_streams() -> list[dict]:
    """List all event stream JSON files in the data directory.

    Returns:
        list[dict]: List of dictionaries with 'uid' and 'title' keys
    """
    try:
        streams_data = _event_storage_service.list_event_streams()
        # Convert to expected format if needed
        if streams_data and isinstance(streams_data[0], str):
            # If we get a list of UIDs, convert to dict format
            result = []
            for uid in streams_data:
                stream = _event_storage_service.load_event_stream(uid)
                if stream:
                    result.append({'uid': uid, 'title': stream.title})
            return result
        return streams_data
    except Exception as e:
        logging.error(f"Error listing event streams: {e}")
        return []

def read_event_stream(uid: str):
    """Read an event stream from its JSON file.

    Args:
        uid (str): The UID of the event stream to read

    Returns:
        EventStream | None: The event stream object if successful, None otherwise
    """
    if uid is None:
        return None
    
    try:
        return _event_storage_service.load_event_stream(uid)
    except Exception as e:
        logging.error(f"Error reading event stream {uid}: {e}")
        return None

def _get_child_stream_uids(event_stream: EventStream) -> set[str]:
    """Get all child stream UIDs for an event stream.

    Args:
        event_stream (EventStream): The parent event stream

    Returns:
        set[str]: Set of child stream UIDs
    """
    return _event_storage_service._get_child_stream_uids(event_stream)

def delete_event_stream(uid: str, recursive: bool = False) -> bool:
    """Delete an event stream JSON file and optionally its children.

    Args:
        uid (str): The UID of the event stream to delete
        recursive (bool): If True, delete all child streams first

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    if uid is None:
        return False
    
    try:
        return _event_storage_service.delete_event_stream(uid, recursive)
    except Exception as e:
        logging.error(f"Error deleting event stream {uid}: {e}")
        return False
