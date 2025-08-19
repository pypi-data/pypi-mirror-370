import os
import unittest
from unittest.mock import patch
from anges.utils.shared_base import get_data_dir, DATA_DIR


class TestSharedBase(unittest.TestCase):
    """Test cases for shared_base.py path expansion functionality"""

    def test_default_data_dir_expansion(self):
        """Test that the default DATA_DIR with tilde is properly expanded"""
        # Clear any environment variable override
        with patch.dict(os.environ, {}, clear=True):
            data_dir = get_data_dir()
            # Should expand ~ to actual home directory
            self.assertTrue(data_dir.startswith('/home/') or data_dir.startswith('/Users/'))
            self.assertNotIn('~', data_dir)
            self.assertTrue(data_dir.endswith('/.anges/data/event_streams'))

    def test_env_var_override_with_absolute_path(self):
        """Test environment variable override with absolute path"""
        custom_path = '/tmp/custom_anges_data'
        with patch.dict(os.environ, {'ANGES_EVENT_STREAM_DATA_DIR': custom_path}):
            data_dir = get_data_dir()
            self.assertEqual(data_dir, custom_path)

    def test_env_var_override_with_tilde(self):
        """Test environment variable override with tilde expansion"""
        custom_path = '~/custom_anges_data'
        with patch.dict(os.environ, {'ANGES_EVENT_STREAM_DATA_DIR': custom_path}):
            data_dir = get_data_dir()
            # Should expand ~ to actual home directory
            self.assertTrue(data_dir.startswith('/home/') or data_dir.startswith('/Users/'))
            self.assertNotIn('~', data_dir)
            self.assertTrue(data_dir.endswith('/custom_anges_data'))

    def test_env_var_override_with_relative_path(self):
        """Test environment variable override with relative path"""
        custom_path = 'relative/path/data'
        with patch.dict(os.environ, {'ANGES_EVENT_STREAM_DATA_DIR': custom_path}):
            data_dir = get_data_dir()
            # Relative paths should remain relative (expanduser doesn't change them)
            self.assertEqual(data_dir, custom_path)

    def test_data_dir_constant_unchanged(self):
        """Test that the DATA_DIR constant itself is unchanged"""
        self.assertTrue(DATA_DIR.endswith('/data/event_streams'))


if __name__ == '__main__':
    unittest.main()