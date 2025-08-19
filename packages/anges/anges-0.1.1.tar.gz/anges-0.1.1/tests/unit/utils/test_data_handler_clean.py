import os
import json
import uuid
import shutil
import unittest
import tempfile
from anges.utils.data_handler import (
    save_event_stream,
    list_event_streams,
    read_event_stream,
    delete_event_stream,
    set_data_dir,
    get_data_dir,
)
from anges.agents.agent_utils.events import Event, EventStream


class TestDataHandler(unittest.TestCase):
    """Test suite for data handler functions using EventStorageService."""
    
    @classmethod
    def setUpClass(cls):
        """Create base test directory"""
        cls.base_test_dir = tempfile.mkdtemp(prefix="test_data_handler_")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up base test directory"""
        if os.path.exists(cls.base_test_dir):
            shutil.rmtree(cls.base_test_dir)
    
    def setUp(self):
        """Set up test environment before each test"""
        # Store original data directory
        self._original_data_dir = get_data_dir()
        
        # Create unique test directory for this test
        test_id = str(uuid.uuid4())
        self.test_dir = os.path.join(self.base_test_dir, test_id)
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Set test directory as data directory
        set_data_dir(self.test_dir)
        
        # Create test event stream
        self.test_stream = EventStream(title="Test Stream")
        self.test_stream.add_event(Event("test", "test reasoning", "test content"))
    
    def tearDown(self):
        """Clean up after each test"""
        # Reset data directory to original
        set_data_dir(self._original_data_dir)
        
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_save_event_stream(self):
        """Test saving an event stream"""
        # Test successful save
        uid = save_event_stream(self.test_stream)
        self.assertIsNotNone(uid)
        file_path = os.path.join(self.test_dir, f"{uid}.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Test invalid input
        self.assertIsNone(save_event_stream(None))
        self.assertIsNone(save_event_stream("not an event stream"))
    
    def test_read_event_stream(self):
        """Test reading an event stream"""
        # Save a stream first
        uid = save_event_stream(self.test_stream)
        
        # Test successful read
        loaded_stream = read_event_stream(uid)
        self.assertIsNotNone(loaded_stream)
        self.assertEqual(loaded_stream.title, self.test_stream.title)
        self.assertEqual(len(loaded_stream.events_list), len(self.test_stream.events_list))
        
        # Test reading non-existent stream
        self.assertIsNone(read_event_stream("non_existent_uid"))
        self.assertIsNone(read_event_stream(None))
    
    def test_list_event_streams(self):
        """Test listing event streams"""
        # Test empty directory
        self.assertEqual(list_event_streams(), [])
        
        # Test with one stream
        uid = save_event_stream(self.test_stream)
        streams = list_event_streams()
        self.assertEqual(len(streams), 1)
        self.assertEqual(streams[0]['uid'], uid)
        self.assertEqual(streams[0]['title'], self.test_stream.title)
        
        # Test with multiple streams
        stream2 = EventStream(title="Second Stream")
        uid2 = save_event_stream(stream2)
        streams = list_event_streams()
        self.assertEqual(len(streams), 2)
        uids = [s['uid'] for s in streams]
        self.assertIn(uid, uids)
        self.assertIn(uid2, uids)
    
    def test_delete_event_stream(self):
        """Test deleting event streams"""
        # Save a stream
        uid = save_event_stream(self.test_stream)
        
        # Verify it exists
        self.assertIsNotNone(read_event_stream(uid))
        
        # Delete it
        result = delete_event_stream(uid)
        self.assertTrue(result)
        
        # Verify it's gone
        self.assertIsNone(read_event_stream(uid))
        
        # Test deleting non-existent stream
        self.assertFalse(delete_event_stream("non_existent_uid"))
        self.assertFalse(delete_event_stream(None))
    
    def test_set_and_get_data_dir(self):
        """Test setting and getting data directory"""
        original_dir = get_data_dir()
        new_dir = os.path.join(self.base_test_dir, "new_data_dir")
        os.makedirs(new_dir, exist_ok=True)
        
        # Set new directory
        set_data_dir(new_dir)
        self.assertEqual(get_data_dir(), new_dir)
        
        # Reset to original
        set_data_dir(original_dir)
        self.assertEqual(get_data_dir(), original_dir)
    
    def test_special_characters_in_title(self):
        """Test handling streams with special characters in title"""
        special_stream = EventStream(title="Test/Stream:with*special<chars>")
        uid = save_event_stream(special_stream)
        self.assertIsNotNone(uid)
        
        # Verify it can be read back
        loaded_stream = read_event_stream(uid)
        self.assertIsNotNone(loaded_stream)
        self.assertEqual(loaded_stream.title, special_stream.title)
    
    def test_large_event_stream(self):
        """Test handling large event streams"""
        large_stream = EventStream(title="Large Stream")
        for i in range(100):  # Reduced from 1000 for faster testing
            large_stream.add_event(Event(f"test_{i}", f"reasoning_{i}", f"content_{i}"))
        
        # Test save and read
        uid = save_event_stream(large_stream)
        self.assertIsNotNone(uid)
        
        loaded_stream = read_event_stream(uid)
        self.assertIsNotNone(loaded_stream)
        self.assertEqual(len(loaded_stream.events_list), 100)
        self.assertEqual(loaded_stream.events_list[99].type, "test_99")


if __name__ == '__main__':
    unittest.main()