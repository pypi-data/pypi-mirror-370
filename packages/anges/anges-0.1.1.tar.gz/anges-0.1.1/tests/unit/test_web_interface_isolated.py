import sys
import unittest
from unittest.mock import patch, MagicMock

# Import the function directly
from anges.cli import run_web_interface

class TestWebInterfaceIsolated(unittest.TestCase):
    @patch('importlib.import_module')
    def test_run_web_interface(self, mock_import):
        """Test that run_web_interface correctly imports and runs the web interface."""
        # Create a mock web interface module with a mock app
        mock_web_interface = MagicMock()
        mock_web_interface.app = MagicMock()
        mock_import.return_value = mock_web_interface
        
        # Reset the mock to clear any previous calls
        mock_import.reset_mock()
        
        # Call the function with test parameters
        run_web_interface(
            host='test_host',
            port='8080',
            password='test_password'
        )
        
        # Verify web interface was imported exactly once
        mock_import.assert_called_once_with('anges.web_interface.web_interface')
        
        # Verify password was set if provided
        mock_web_interface.set_password.assert_called_once_with('test_password')
        
        # Verify app was run with correct parameters
        mock_web_interface.run_app.assert_called_once_with(
            mock_web_interface.app,
            host='test_host',
            port=8080,
            debug=False
        )

    @patch('importlib.import_module', side_effect=ImportError("Web interface not available"))
    def test_run_web_interface_import_error(self, mock_import):
        """Test that run_web_interface handles import errors gracefully."""
        with self.assertRaises(SystemExit) as cm:
            run_web_interface(
                host='test_host',
                port='8080',
                password='test_password'
            )
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()