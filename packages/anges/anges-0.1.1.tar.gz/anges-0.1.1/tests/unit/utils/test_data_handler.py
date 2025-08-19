import os
import json
import uuid
import shutil
import unittest
import importlib
from anges.utils.data_handler import (
    save_event_stream,
    list_event_streams,
    read_event_stream,
    delete_event_stream,
    set_data_dir,
    get_data_dir,
)
from anges.utils.event_storage_service import event_storage_service
from anges.agents.agent_utils.events import Event, EventStream
class TestDataHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create base test directory"""
        # Get the worker ID from pytest-xdist if running in parallel
        worker_id = os.environ.get('PYTEST_XDIST_WORKER', '')
        
        # Get the original data directory from the event storage service
        original_data_dir = get_data_dir()

        cls.base_test_dir = os.path.join(
            os.path.dirname(original_data_dir),
            'test_data',
            worker_id if worker_id else 'single'
        )

        # Clean up any existing directory and its contents
        if os.path.exists(cls.base_test_dir):
            try:
                shutil.rmtree(cls.base_test_dir)
            except PermissionError:
                # If permission error, try to change permissions first
                for root, dirs, files in os.walk(cls.base_test_dir):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), 0o755)
                    for f in files:
                        os.chmod(os.path.join(root, f), 0o644)
                shutil.rmtree(cls.base_test_dir)
        # Create fresh base directory with proper permissions
        os.makedirs(cls.base_test_dir, mode=0o755, exist_ok=True)

        # Create test-specific directory path and store original data directory
        cls.test_dir = os.path.join(
            cls.base_test_dir,
            f"{worker_id}_{str(uuid.uuid4())}" if worker_id else str(uuid.uuid4())
        )

    def setUp(self):
        """Set up test environment before each test"""
        # Store original data directory
        self._original_data_dir = get_data_dir()

        # Create a unique test directory for this test
        worker_id = os.environ.get('PYTEST_XDIST_WORKER', '')
        test_id = str(uuid.uuid4())
        self.test_dir = os.path.join(
            self.base_test_dir,
            f"{worker_id}_{test_id}" if worker_id else test_id
        )
        
        # Ensure test directory exists
        os.makedirs(self.test_dir, mode=0o755, exist_ok=True)
        
        # Set the data directory for testing
        set_data_dir(self.test_dir)

        # Create test event stream
        self.test_stream = EventStream(title="Test Stream")
        self.test_stream.add_event(Event("test", "test reasoning", "test content"))

    def tearDown(self):
        """Clean up after each test"""
        # Store current test directory path
        current_test_dir = self.test_dir

        # Reset data directory to original
        set_data_dir(self._original_data_dir)

        # Clean up test directory
        if os.path.exists(current_test_dir):
            try:
                shutil.rmtree(current_test_dir)
            except (OSError, PermissionError):
                # If cleanup fails, just continue
                pass

    @classmethod
    def tearDownClass(cls):
        """Clean up base test directory"""
        if os.path.exists(cls.base_test_dir):
            try:
                shutil.rmtree(cls.base_test_dir)
            except (OSError, PermissionError):
                # If cleanup fails, just continue
                pass

    def test_save_and_read_event_stream(self):
        """Test saving and reading event streams"""
        # Save the test stream
        uid = save_event_stream(self.test_stream)
        self.assertIsNotNone(uid)
        
        # Read it back
        loaded_stream = read_event_stream(uid)
        self.assertIsNotNone(loaded_stream)
        self.assertEqual(loaded_stream.title, self.test_stream.title)
        self.assertEqual(len(loaded_stream.events_list), len(self.test_stream.events_list))

    def test_list_event_streams(self):
        """Test listing event streams"""
        # Initially should be empty
        streams = list_event_streams()
        initial_count = len(streams)
        
        # Save a stream
        uid = save_event_stream(self.test_stream)
        
        # Should now have one more stream
        streams = list_event_streams()
        self.assertEqual(len(streams), initial_count + 1)
        self.assertIn(uid, [s['uid'] for s in streams])

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

    def test_set_and_get_data_dir(self):
        """Test setting and getting data directory"""
        original_dir = get_data_dir()
        
        # Test setting new directory
        new_dir = os.path.join(self.test_dir, 'new_data')
        os.makedirs(new_dir, exist_ok=True)
        set_data_dir(new_dir)
        self.assertEqual(get_data_dir(), new_dir)
        
        # Reset to original
        set_data_dir(original_dir)
        self.assertEqual(get_data_dir(), original_dir)

    def test_save_event_stream_with_special_chars(self):
        """Test saving event streams with special characters in title"""
        special_stream = EventStream(title="Test/Stream:with*special<chars>")
        special_stream.add_event(Event("test", "test reasoning", "test content"))
        uid = save_event_stream(special_stream)
        self.assertIsNotNone(uid)

    def test_list_event_streams_format(self):
        """Test listing event streams returns correct format"""
        # Test empty directory
        streams = list_event_streams()
        self.assertIsInstance(streams, list)

        # Test with one file
        uid = save_event_stream(self.test_stream)
        streams = list_event_streams()
        self.assertEqual(len(streams), 1)
        self.assertIn('uid', streams[0])
        self.assertIn('title', streams[0])
        self.assertEqual(streams[0]['uid'], uid)

        # Test with multiple files
        stream2 = EventStream(title="Test Stream 2")
        stream2.add_event(Event("test2", "test reasoning 2", "test content 2"))
        uid2 = save_event_stream(stream2)
        streams = list_event_streams()
        self.assertEqual(len(streams), 2)
        uids = [s['uid'] for s in streams]
        self.assertIn(uid, uids)
        self.assertIn(uid2, uids)

        # Test with non-json files in directory
        with open(os.path.join(get_data_dir(), "not_json.txt"), "w") as f:
            f.write("test")
        self.assertEqual(len(list_event_streams()), 2)

    def test_read_event_stream_detailed(self):
        """Test reading an event stream with detailed validation"""
        # Test reading non-existent file
        self.assertIsNone(read_event_stream("nonexistent"))

        # Test successful read
        uid = save_event_stream(self.test_stream)
        loaded_stream = read_event_stream(uid)
        self.assertIsNotNone(loaded_stream)
        self.assertEqual(loaded_stream.uid, self.test_stream.uid)
        self.assertEqual(loaded_stream.title, self.test_stream.title)
        self.assertEqual(len(loaded_stream.events_list), 1)
        self.assertEqual(loaded_stream.events_list[0].type, "test")

        # Test corrupted file
        corrupted_path = os.path.join(get_data_dir(), "corrupted.json")
        with open(corrupted_path, "w") as f:
            f.write("invalid json")
        self.assertIsNone(read_event_stream("corrupted"))

    def test_delete_event_stream_basic(self):
        """Test basic event stream deletion"""
        # Test deleting non-existent file
        self.assertFalse(delete_event_stream("nonexistent"))

        # Test successful deletion
        uid = save_event_stream(self.test_stream)
        self.assertTrue(delete_event_stream(uid))
        self.assertIsNone(read_event_stream(uid))

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
