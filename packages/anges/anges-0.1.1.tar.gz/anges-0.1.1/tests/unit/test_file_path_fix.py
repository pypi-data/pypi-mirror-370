#!/usr/bin/env python3
"""Test script to verify the file path fix works end-to-end"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, '.')

from anges.utils.data_handler import save_event_stream, get_data_dir, ensure_data_dir
from anges.agents.agent_utils.events import EventStream, Event

def test_file_path_fix():
    """Test that files are saved to the correct expanded path"""
    print("Testing file path fix...")
    
    # Check the data directory path
    data_dir = get_data_dir()
    print(f"Data directory: {data_dir}")
    
    # Verify it's properly expanded (not containing ~)
    # Verify it's properly expanded (not containing ~ and is absolute)
    assert '~' not in data_dir, f"Path still contains tilde: {data_dir}"
    assert os.path.isabs(data_dir), f'Path is not absolute: {data_dir}'
    
    # Ensure directory exists
    ensure_data_dir()
    assert os.path.exists(data_dir), f"Directory was not created: {data_dir}"
    
    # Create a test EventStream with an actual event
    # Create a test EventStream with an actual event
    event_stream = EventStream(title="Test Stream")
    test_event = Event(
        type="test_event",
        reasoning="Testing path functionality", 
        content="Test event content",
        message="Test event for path verification"
    )
    event_stream.add_event(test_event)
    
    # Save the event stream
    success = save_event_stream(event_stream)
    assert success, "Failed to save event stream"
    
    # List files in the directory to verify file was created
    files_in_dir = os.listdir(data_dir)
    json_files = [f for f in files_in_dir if f.endswith('.json')]
    assert len(json_files) > 0, f"No JSON files found in {data_dir}"
    
    # Verify we can read the saved file - use the specific UID instead of assuming latest
    expected_filename = f"{event_stream.uid}.json"
    expected_file_path = os.path.join(data_dir, expected_filename)
    assert os.path.exists(expected_file_path), f"Expected file {expected_filename} not found in {data_dir}"
    
    with open(expected_file_path, 'r') as f:
        saved_data = json.load(f)
    
    # Verify the file contains the expected data
    print(f"DEBUG: Saved data keys: {list(saved_data.keys())}")
    print(f"DEBUG: Events list length: {len(saved_data.get('events_list', []))}")
    print(f"DEBUG: First few chars of file: {str(saved_data)[:200]}...")
    
    assert 'events_list' in saved_data, "Saved file doesn't contain events_list"
    assert len(saved_data['events_list']) > 0, "No events in saved file"
    print(f"✅ SUCCESS: File saved correctly to {expected_file_path}")
    
    print(f"✅ Directory exists at: {data_dir}")
    
    # Test passed - no return value needed for pytest

if __name__ == "__main__":
    try:
        test_file_path_fix()
        print("\n🎉 All tests passed! File path fix is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)