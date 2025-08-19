import os
import json
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from anges.utils.event_storage_service import EventStorageService, event_storage_service
from anges.agents.agent_utils.events import EventStream, Event


class TestEventStorageService(unittest.TestCase):
    """Comprehensive test suite for EventStorageService."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.service = EventStorageService(data_dir=self.test_dir)
        
        # Create sample event stream for testing
        self.sample_stream = EventStream()
        self.sample_stream.uid = "test_stream_123"
        self.sample_stream.title = "Test Stream"
        self.sample_stream.add_event(
            Event(type="test_event", content="Test content", reasoning="Test reasoning")
        )
        
        # Create another sample stream for relationship testing
        self.child_stream = EventStream()
        self.child_stream.uid = "child_stream_456"
        self.child_stream.title = "Child Stream"
        self.child_stream.parent_event_stream_uids = ["test_stream_123"]
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    # Directory management tests
    def test_get_data_dir(self):
        """Test getting data directory."""
        self.assertEqual(self.service.get_data_dir(), self.test_dir)
    
    def test_set_data_dir(self):
        """Test setting data directory."""
        new_dir = tempfile.mkdtemp()
        try:
            self.service.set_data_dir(new_dir)
            self.assertEqual(self.service.get_data_dir(), new_dir)
        finally:
            shutil.rmtree(new_dir)
    
    def test_set_data_dir_with_tilde(self):
        """Test setting data directory with tilde expansion."""
        with patch('os.path.expanduser') as mock_expand:
            mock_expand.return_value = '/expanded/path'
            self.service.set_data_dir('~/test')
            mock_expand.assert_called_once_with('~/test')
            self.assertEqual(self.service.get_data_dir(), '/expanded/path')
    
    def test_ensure_data_dir_creates_directory(self):
        """Test that ensure_data_dir creates the directory."""
        new_dir = os.path.join(self.test_dir, 'new_subdir')
        self.service.set_data_dir(new_dir)
        self.assertFalse(os.path.exists(new_dir))
        
        self.service.ensure_data_dir()
        self.assertTrue(os.path.exists(new_dir))
    
    def test_ensure_data_dir_handles_existing_directory(self):
        """Test that ensure_data_dir handles existing directories gracefully."""
        # Directory already exists
        self.assertTrue(os.path.exists(self.test_dir))
        self.service.ensure_data_dir()  # Should not raise exception
    
    def test_ensure_data_dir_handles_permission_error(self):
        """Test that ensure_data_dir handles permission errors."""
        with patch('os.makedirs', side_effect=OSError("Permission denied")):
            with self.assertRaises(OSError):
                self.service.ensure_data_dir()
    
    # User session management tests
    def test_user_stream_dictionary_access(self):
        """Test dictionary-style access for user streams."""
        user_id = "test_user"
        
        # Test getting non-existent user
        self.assertIsNone(self.service[user_id])
        
        # Test setting user stream
        self.service[user_id] = self.sample_stream
        self.assertEqual(self.service[user_id], self.sample_stream)
    
    def test_user_stream_setitem_validation(self):
        """Test validation in __setitem__."""
        user_id = "test_user"
        
        # Test invalid type
        with self.assertRaises(ValueError):
            self.service[user_id] = "not_an_event_stream"
        
        # Test save failure
        with patch.object(self.service, 'save_event_stream', return_value=False):
            with self.assertRaises(RuntimeError):
                self.service[user_id] = self.sample_stream
    
    def test_get_user_stream(self):
        """Test getting user stream."""
        user_id = "test_user"
        
        # Test non-existent user
        self.assertIsNone(self.service.get_user_stream(user_id))
        
        # Test existing user
        self.service._user_streams[user_id] = self.sample_stream
        self.assertEqual(self.service.get_user_stream(user_id), self.sample_stream)
    
    def test_set_user_stream_success(self):
        """Test successful user stream setting."""
        user_id = "test_user"
        
        # Mock save_event_stream to return True
        with patch.object(self.service, 'save_event_stream', return_value=True):
            result = self.service.set_user_stream(user_id, self.sample_stream)
            self.assertTrue(result)
            # Verify the stream was added to user streams
            self.assertEqual(self.service.get_user_stream(user_id), self.sample_stream)
    
    def test_set_user_stream_failure(self):
        """Test user stream setting failure handling."""
        user_id = "test_user"
        
        # Mock save_event_stream to return False, which should cause RuntimeError
        with patch.object(self.service, 'save_event_stream', return_value=False):
            result = self.service.set_user_stream(user_id, self.sample_stream)
            self.assertFalse(result)
    def test_remove_user_stream(self):
        """Test removing user stream."""
        user_id = "test_user"
        
        # Test removing non-existent user
        self.assertFalse(self.service.remove_user_stream(user_id))
        
        # Test removing existing user
        self.service._user_streams[user_id] = self.sample_stream
        self.assertTrue(self.service.remove_user_stream(user_id))
        self.assertNotIn(user_id, self.service._user_streams)
    
    # Core event stream operations tests
    def test_save_event_stream_success(self):
        """Test successful event stream saving."""
        result = self.service.save_event_stream(self.sample_stream)
        self.assertTrue(result)
        
        # Verify file was created
        expected_path = os.path.join(self.test_dir, f"{self.sample_stream.uid}.json")
        self.assertTrue(os.path.exists(expected_path))
        
        # Verify content
        with open(expected_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data['uid'], self.sample_stream.uid)
            self.assertEqual(saved_data['title'], self.sample_stream.title)
    
    def test_save_event_stream_invalid_type(self):
        """Test saving with invalid event stream type."""
        result = self.service.save_event_stream("not_an_event_stream")
        self.assertFalse(result)
    
    def test_save_event_stream_io_error(self):
        """Test saving with IO error."""
        with patch('builtins.open', side_effect=IOError("Disk full")):
            result = self.service.save_event_stream(self.sample_stream)
            self.assertFalse(result)
    
    def test_load_event_stream_success(self):
        """Test successful event stream loading."""
        # First save the stream
        self.service.save_event_stream(self.sample_stream)
        
        # Then load it
        loaded_stream = self.service.load_event_stream(self.sample_stream.uid)
        self.assertIsNotNone(loaded_stream)
        self.assertEqual(loaded_stream.uid, self.sample_stream.uid)
        self.assertEqual(loaded_stream.title, self.sample_stream.title)
    
    def test_load_event_stream_invalid_uid(self):
        """Test loading with invalid UID."""
        # Test empty UID
        self.assertIsNone(self.service.load_event_stream(""))
        
        # Test None UID
        self.assertIsNone(self.service.load_event_stream(None))
        
        # Test non-string UID
        self.assertIsNone(self.service.load_event_stream(123))
    
    def test_load_event_stream_file_not_found(self):
        """Test loading non-existent stream."""
        result = self.service.load_event_stream("non_existent_uid")
        self.assertIsNone(result)
    
    def test_load_event_stream_invalid_json(self):
        """Test loading stream with invalid JSON."""
        # Create invalid JSON file
        file_path = os.path.join(self.test_dir, "invalid.json")
        with open(file_path, 'w') as f:
            f.write("invalid json content")
        
        result = self.service.load_event_stream("invalid")
        self.assertIsNone(result)
    
    def test_load_event_stream_io_error(self):
        """Test loading with IO error."""
        # First save the stream
        self.service.save_event_stream(self.sample_stream)
        
        # Mock IO error during read
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            result = self.service.load_event_stream(self.sample_stream.uid)
            self.assertIsNone(result)
    
    def test_list_event_streams_empty(self):
        """Test listing when no streams exist."""
        streams = self.service.list_event_streams()
        self.assertEqual(streams, [])
    
    def test_list_event_streams_with_data(self):
        """Test listing with existing streams."""
        # Save multiple streams
        self.service.save_event_stream(self.sample_stream)
        self.service.save_event_stream(self.child_stream)
        
        streams = self.service.list_event_streams()
        self.assertIn(self.sample_stream.uid, streams)
        self.assertIn(self.child_stream.uid, streams)
        self.assertEqual(len(streams), 2)
    
    def test_list_event_streams_filters_non_json(self):
        """Test that listing filters out non-JSON files."""
        # Create JSON and non-JSON files
        self.service.save_event_stream(self.sample_stream)
        
        # Create non-JSON file
        with open(os.path.join(self.test_dir, "not_json.txt"), 'w') as f:
            f.write("not json")
        
        streams = self.service.list_event_streams()
        self.assertEqual(len(streams), 1)
        self.assertEqual(streams[0], self.sample_stream.uid)
    
    def test_list_event_streams_io_error(self):
        """Test listing with IO error."""
        with patch('os.listdir', side_effect=OSError("Permission denied")):
            streams = self.service.list_event_streams()
            self.assertEqual(streams, [])
    
    def test_update_stream_title_success(self):
        """Test successful title update."""
        # Save stream first
        self.service.save_event_stream(self.sample_stream)
        
        new_title = "Updated Title"
        result = self.service.update_stream_title(self.sample_stream.uid, new_title)
        self.assertTrue(result)
        
        # Verify title was updated
        loaded_stream = self.service.load_event_stream(self.sample_stream.uid)
        self.assertEqual(loaded_stream.title, new_title)
    
    def test_update_stream_title_invalid_stream_id(self):
        """Test title update with invalid stream ID."""
        with self.assertRaises(ValueError):
            self.service.update_stream_title("", "New Title")
        
        with self.assertRaises(ValueError):
            self.service.update_stream_title(None, "New Title")
        
        with self.assertRaises(ValueError):
            self.service.update_stream_title(123, "New Title")
    
    def test_update_stream_title_invalid_title(self):
        """Test title update with invalid title."""
        with self.assertRaises(ValueError):
            self.service.update_stream_title("stream_id", "")
        
        with self.assertRaises(ValueError):
            self.service.update_stream_title("stream_id", None)
        
        with self.assertRaises(ValueError):
            self.service.update_stream_title("stream_id", 123)
    
    def test_update_stream_title_stream_not_found(self):
        """Test title update for non-existent stream."""
        with self.assertRaises(ValueError):
            self.service.update_stream_title("non_existent", "New Title")
    
    def test_update_stream_title_save_failure(self):
        """Test title update with save failure."""
        # Save stream first
        self.service.save_event_stream(self.sample_stream)
        
        with patch.object(self.service, 'save_event_stream', return_value=False):
            result = self.service.update_stream_title(self.sample_stream.uid, "New Title")
            self.assertFalse(result)
    
    def test_update_stream_title_strips_whitespace(self):
        """Test that title update strips whitespace."""
        # Save stream first
        self.service.save_event_stream(self.sample_stream)
        
        title_with_whitespace = "  New Title  "
        result = self.service.update_stream_title(self.sample_stream.uid, title_with_whitespace)
        self.assertTrue(result)
        
        # Verify title was stripped
        loaded_stream = self.service.load_event_stream(self.sample_stream.uid)
        self.assertEqual(loaded_stream.title, "New Title")
    
    def test_get_child_stream_uids_from_events(self):
        """Test finding child UIDs from events."""
        # Create parent stream with child_agent_running event
        parent_stream = EventStream()
        parent_stream.uid = "parent_123"
        
        child_info = {"agent_id": "child_456"}
        child_event = Event(
            type="child_agent_running",
            content="Child agent started",
            reasoning=json.dumps(child_info)
        )
        parent_stream.add_event(child_event)
        
        child_uids = self.service._get_child_stream_uids(parent_stream)
        self.assertIn("child_456", child_uids)
    
    def test_get_child_stream_uids_from_parent_references(self):
        """Test finding child UIDs from parent references."""
        # Save both streams
        self.service.save_event_stream(self.sample_stream)
        self.service.save_event_stream(self.child_stream)
        
        child_uids = self.service._get_child_stream_uids(self.sample_stream)
        self.assertIn(self.child_stream.uid, child_uids)
    
    def test_get_child_stream_uids_handles_invalid_json(self):
        """Test that child UID finding handles invalid JSON gracefully."""
        parent_stream = EventStream()
        parent_stream.uid = "parent_123"
        
        # Add event with invalid JSON
        invalid_event = Event(
            type="child_agent_running",
            content="Child agent started",
            reasoning="invalid json"
        )
        parent_stream.add_event(invalid_event)
        
        # Should not raise exception
        child_uids = self.service._get_child_stream_uids(parent_stream)
        self.assertEqual(len(child_uids), 0)
    
    def test_delete_event_stream_success(self):
        """Test successful event stream deletion."""
        # Save stream first
        self.service.save_event_stream(self.sample_stream)
        
        result = self.service.delete_event_stream(self.sample_stream.uid)
        self.assertTrue(result)
        
        # Verify file was deleted
        expected_path = os.path.join(self.test_dir, f"{self.sample_stream.uid}.json")
        self.assertFalse(os.path.exists(expected_path))
    
    def test_delete_event_stream_invalid_uid(self):
        """Test deletion with invalid UID."""
        self.assertFalse(self.service.delete_event_stream(""))
        self.assertFalse(self.service.delete_event_stream(None))
        self.assertFalse(self.service.delete_event_stream(123))
    
    def test_delete_event_stream_not_found(self):
        """Test deletion of non-existent stream."""
        result = self.service.delete_event_stream("non_existent")
        self.assertFalse(result)
    
    def test_delete_event_stream_removes_from_user_sessions(self):
        """Test that deletion removes stream from user sessions."""
        user_id = "test_user"
        
        # Save stream and add to user session
        self.service.save_event_stream(self.sample_stream)
        self.service._user_streams[user_id] = self.sample_stream
        
        # Delete stream
        result = self.service.delete_event_stream(self.sample_stream.uid)
        self.assertTrue(result)
        
        # Verify removed from user sessions
        self.assertNotIn(user_id, self.service._user_streams)
    
    def test_delete_event_stream_recursive(self):
        """Test recursive deletion of streams."""
        # Save parent and child streams
        self.service.save_event_stream(self.sample_stream)
        self.service.save_event_stream(self.child_stream)
        
        # Delete parent recursively
        result = self.service.delete_event_stream(self.sample_stream.uid, recursive=True)
        self.assertTrue(result)
        
        # Verify both streams are deleted
        parent_path = os.path.join(self.test_dir, f"{self.sample_stream.uid}.json")
        child_path = os.path.join(self.test_dir, f"{self.child_stream.uid}.json")
        self.assertFalse(os.path.exists(parent_path))
        self.assertFalse(os.path.exists(child_path))
    
    def test_delete_event_stream_io_error(self):
        """Test deletion with IO error."""
        # Save stream first
        self.service.save_event_stream(self.sample_stream)
        
        with patch('os.remove', side_effect=OSError("Permission denied")):
            result = self.service.delete_event_stream(self.sample_stream.uid)
            self.assertFalse(result)
    
    # Legacy method tests
    def test_legacy_save_method(self):
        """Test legacy save method alias."""
        result = self.service.save(self.sample_stream)
        self.assertTrue(result)
        
        # Verify file was created
        expected_path = os.path.join(self.test_dir, f"{self.sample_stream.uid}.json")
        self.assertTrue(os.path.exists(expected_path))
    
    def test_legacy_load_method(self):
        """Test legacy load method alias."""
        self.service.save_event_stream(self.sample_stream)
        
        loaded_stream = self.service.load(self.sample_stream.uid)
        self.assertIsNotNone(loaded_stream)
        self.assertEqual(loaded_stream.uid, self.sample_stream.uid)
    
    def test_legacy_list_streams_method(self):
        """Test legacy list_streams method alias."""
        self.service.save_event_stream(self.sample_stream)
        
        streams = self.service.list_streams()
        self.assertIn(self.sample_stream.uid, streams)
    
    def test_legacy_delete_stream_method(self):
        """Test legacy delete_stream method alias."""
        self.service.save_event_stream(self.sample_stream)
        
        result = self.service.delete_stream(self.sample_stream.uid)
        self.assertTrue(result)
        
        expected_path = os.path.join(self.test_dir, f"{self.sample_stream.uid}.json")
        self.assertFalse(os.path.exists(expected_path))


class TestEventStorageServiceLegacyFunctions(unittest.TestCase):
    """Test suite for legacy function wrappers."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_data_dir = event_storage_service.get_data_dir()
        event_storage_service.set_data_dir(self.test_dir)
        
        # Create sample event stream
        self.sample_stream = EventStream()
        self.sample_stream.uid = "legacy_test_123"
        self.sample_stream.title = "Legacy Test Stream"
    
    def tearDown(self):
        """Clean up test environment."""
        event_storage_service.set_data_dir(self.original_data_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_legacy_save_event_stream_function(self):
        """Test legacy save_event_stream function."""
        from anges.utils.event_storage_service import save_event_stream
        
        result = save_event_stream(self.sample_stream)
        self.assertTrue(result)
    
    def test_legacy_read_event_stream_function(self):
        """Test legacy read_event_stream function."""
        from anges.utils.event_storage_service import read_event_stream, save_event_stream
        
        save_event_stream(self.sample_stream)
        loaded_stream = read_event_stream(self.sample_stream.uid)
        self.assertIsNotNone(loaded_stream)
        self.assertEqual(loaded_stream.uid, self.sample_stream.uid)
    
    def test_legacy_list_event_streams_function(self):
        """Test legacy list_event_streams function."""
        from anges.utils.event_storage_service import list_event_streams, save_event_stream
        
        save_event_stream(self.sample_stream)
        streams = list_event_streams()
        self.assertIn(self.sample_stream.uid, streams)
    
    def test_legacy_delete_event_stream_function(self):
        """Test legacy delete_event_stream function."""
        from anges.utils.event_storage_service import delete_event_stream, save_event_stream
        
        save_event_stream(self.sample_stream)
        result = delete_event_stream(self.sample_stream.uid)
        self.assertTrue(result)
    
    def test_legacy_get_data_dir_function(self):
        """Test legacy get_data_dir function."""
        from anges.utils.event_storage_service import get_data_dir
        
        data_dir = get_data_dir()
        self.assertEqual(data_dir, self.test_dir)
    
    def test_legacy_set_data_dir_function(self):
        """Test legacy set_data_dir function."""
        from anges.utils.event_storage_service import set_data_dir, get_data_dir
        
        new_dir = tempfile.mkdtemp()
        try:
            set_data_dir(new_dir)
            self.assertEqual(get_data_dir(), new_dir)
        finally:
            shutil.rmtree(new_dir)
    
    def test_legacy_ensure_data_dir_function(self):
        """Test legacy ensure_data_dir function."""
        from anges.utils.event_storage_service import ensure_data_dir, set_data_dir
        
        new_dir = os.path.join(self.test_dir, 'new_subdir')
        set_data_dir(new_dir)
        self.assertFalse(os.path.exists(new_dir))
        
        ensure_data_dir()
        self.assertTrue(os.path.exists(new_dir))


if __name__ == '__main__':
    unittest.main()