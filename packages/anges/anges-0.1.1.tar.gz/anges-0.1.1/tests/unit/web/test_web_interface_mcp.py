import pytest
import json
import asyncio
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from anges.web_interface.web_interface import init_app
from anges.utils.mcp_manager import McpManager, McpStdioClient


@pytest.fixture(scope='function')
def client():
    """Test client fixture with MCP manager mocked"""
    app = init_app("test_password")
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True
    
    with app.test_client() as client_instance:
        with client_instance.session_transaction() as session:
            session['user_id'] = 'test_user'
        yield client_instance


@pytest.fixture
def mock_event_stream():
    """Mock event stream fixture"""
    mock_stream = MagicMock()
    mock_stream.mcp_config = {
        "dummy_mcp_server": {
            "command": sys.executable,
            "args": ["tests/unit/utils/dummy_mcp_server.py"]
        }
    }
    return mock_stream


class TestMcpRefreshApi:
    """Test cases for MCP refresh API"""

    def test_refresh_mcp_status_success(self, client):
        """Test successfully refreshing MCP status"""
        # Setup mock event stream
        mock_stream = MagicMock()
        mock_stream.mcp_config = {
            "dummy_mcp_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            }
        }
        
        # Setup mock manager
        mock_manager = MagicMock()
        # Create mock tools with proper name attributes
        mock_echo_tool = MagicMock()
        mock_echo_tool.name = 'echo'
        mock_add_tool = MagicMock()
        mock_add_tool.name = 'add_numbers'
        
        mock_client_info = [
            {
                'name': 'dummy_mcp_server',
                'status': True,
                'command': sys.executable,
                'args': ['tests/unit/utils/dummy_mcp_server.py'],
                'tools': [mock_echo_tool, mock_add_tool]
            }
        ]
        mock_manager.list_mcp_clients.return_value = mock_client_info
        
        with patch('anges.web_interface.web_interface.current_event_stream', mock_stream), \
             patch('anges.web_interface.web_interface.McpManager', return_value=mock_manager):
            
            response = client.post('/api/mcp/refresh')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'mcp_clients' in data
            assert len(data['mcp_clients']) == 1
            assert data['mcp_clients'][0]['name'] == 'dummy_mcp_server'
            # Check that tools were processed correctly
            assert 'tools' in data['mcp_clients'][0]
            assert len(data['mcp_clients'][0]['tools']) == 2
            assert data['mcp_clients'][0]['tools'][0]['name'] == 'echo'
            assert data['mcp_clients'][0]['tools'][1]['name'] == 'add_numbers'

    def test_refresh_mcp_status_no_stream(self, client):
        """Test refreshing MCP status when no active event stream"""
        with patch('anges.web_interface.web_interface.current_event_stream', None):
            response = client.post('/api/mcp/refresh')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'No active event stream' in data['message']

    def test_refresh_mcp_status_error(self, client):
        """Test refreshing MCP status with error"""
        # Setup mock event stream
        mock_stream = MagicMock()
        mock_stream.mcp_config = {}
        
        # Setup mock manager to raise exception
        with patch('anges.web_interface.web_interface.current_event_stream', mock_stream), \
             patch('anges.web_interface.web_interface.McpManager', side_effect=Exception("Connection failed")):
            
            response = client.post('/api/mcp/refresh')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'


class TestMcpConfigApi:
    """Test cases for MCP config API"""

    def test_update_mcp_config_success(self, client):
        """Test successfully updating MCP configuration"""
        # Setup mock event stream
        mock_stream = MagicMock()
        mock_stream.mcp_config = {}
        
        request_data = {
            'mcp_config': {
                'filesystem_server': {
                    'command': 'npx',
                    'args': ['-g', '@modelcontextprotocol/server-filesystem', '/tmp']
                },
                'dummy_server': {
                    'command': sys.executable,
                    'args': ['tests/unit/utils/dummy_mcp_server.py']
                }
            }
        }
        
        with patch('anges.web_interface.web_interface.current_event_stream', mock_stream), \
             patch('anges.web_interface.web_interface.event_storage') as mock_event_storage:
            
            response = client.put('/api/mcp/config',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'updated successfully' in data['message']
            
            # Verify the configuration was updated
            assert mock_stream.mcp_config == request_data['mcp_config']
            mock_event_storage.save_event_stream.assert_called_once()

    def test_update_mcp_config_no_stream(self, client):
        """Test updating MCP config when no active event stream"""
        request_data = {
            'mcp_config': {
                'test_server': {
                    'command': sys.executable,
                    'args': ['tests/unit/utils/dummy_mcp_server.py']
                }
            }
        }
        
        with patch('anges.web_interface.web_interface.current_event_stream', None):
            response = client.put('/api/mcp/config',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'No active event stream' in data['message']

    def test_update_mcp_config_missing_config(self, client):
        """Test updating MCP config with missing mcp_config field"""
        mock_stream = MagicMock()
        
        request_data = {
            'other_field': 'value'
            # Missing 'mcp_config' field
        }
        
        with patch('anges.web_interface.web_interface.current_event_stream', mock_stream):
            response = client.put('/api/mcp/config',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'mcp_config is required' in data['message']

    def test_update_mcp_config_invalid_format(self, client):
        """Test updating MCP config with invalid format"""
        mock_stream = MagicMock()
        
        request_data = {
            'mcp_config': 'invalid_format'  # Should be a dict
        }
        
        with patch('anges.web_interface.web_interface.current_event_stream', mock_stream):
            response = client.put('/api/mcp/config',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'must be a valid JSON object' in data['message']

    def test_update_mcp_config_invalid_client_config(self, client):
        """Test updating MCP config with invalid client configuration"""
        mock_stream = MagicMock()
        
        request_data = {
            'mcp_config': {
                'invalid_server': {
                    'command': 'python'
                    # Missing 'args' field
                }
            }
        }
        
        with patch('anges.web_interface.web_interface.current_event_stream', mock_stream):
            response = client.put('/api/mcp/config',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert "missing 'command' or 'args'" in data['message']

    def test_update_mcp_config_invalid_args_type(self, client):
        """Test updating MCP config with invalid args type"""
        mock_stream = MagicMock()
        
        request_data = {
            'mcp_config': {
                'invalid_server': {
                    'command': 'python',
                    'args': 'should_be_array'  # Should be a list
                }
            }
        }
        
        with patch('anges.web_interface.web_interface.current_event_stream', mock_stream):
            response = client.put('/api/mcp/config',
                                data=json.dumps(request_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert "'args' must be an array" in data['message']

    def test_update_mcp_config_invalid_json(self, client):
        """Test updating MCP config with invalid JSON"""
        # Flask will return 400 for invalid JSON automatically, 
        # so we don't need to mock current_event_stream
        response = client.put('/api/mcp/config',
                            data='invalid json',
                            content_type='application/json')
        
        assert response.status_code == 400
        # Flask returns a default error message for bad JSON


class TestMcpApiAuthentication:
    """Test cases for MCP API authentication"""

    def test_mcp_api_requires_authentication(self):
        """Test that MCP APIs require authentication when login is enabled"""
        app = init_app("test_password")
        app.config['TESTING'] = True
        # Don't disable login to test authentication
        
        with app.test_client() as client:
            # Test without authentication
            response = client.post('/api/mcp/refresh')
            assert response.status_code == 401
            
            response = client.put('/api/mcp/config',
                                data=json.dumps({'mcp_config': {}}),
                                content_type='application/json')
            assert response.status_code == 401


class TestLoadChatMcpIntegration:
    """Test cases for MCP integration in load chat functionality"""

    def test_load_chat_with_mcp_config(self, client):
        """Test loading chat with MCP configuration"""
        # Setup mock event stream
        mock_stream = MagicMock()
        mock_stream.mcp_config = {
            "dummy_mcp_server": {
                "command": sys.executable,
                "args": ["tests/unit/utils/dummy_mcp_server.py"]
            }
        }
        mock_stream.agent_settings = {}
        mock_stream.parent_event_stream_uids = []
        mock_stream.get_event_list_including_children_events.return_value = []
        
        # Mock events to have required attributes
        mock_event = MagicMock()
        mock_event.est_input_token = 10
        mock_event.est_output_token = 20
        mock_event.type = "user"
        mock_event.message = "test message"
        mock_stream.get_event_list_including_children_events.return_value = [mock_event]
        
        # Setup mock manager
        mock_manager = MagicMock()
        mock_tool = MagicMock()
        mock_tool.name = 'echo'
        mock_client_info = [
            {
                'name': 'dummy_mcp_server',
                'status': True,
                'command': sys.executable,
                'args': ['tests/unit/utils/dummy_mcp_server.py'],
                'tools': [mock_tool]
            }
        ]
        mock_manager.list_mcp_clients.return_value = mock_client_info
        
        with patch('anges.web_interface.web_interface.event_storage') as mock_event_storage, \
             patch('anges.web_interface.web_interface.McpManager', return_value=mock_manager):
            
            mock_event_storage.load.return_value = mock_stream
            
            response = client.get('/load-chat/test_chat_id')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'mcp_config' in data
            assert 'mcp_clients' in data
            assert len(data['mcp_clients']) == 1

    def test_load_chat_no_mcp_config(self, client):
        """Test loading chat without MCP configuration"""
        # Setup mock event stream without MCP config
        mock_stream = MagicMock()
        mock_stream.mcp_config = None
        mock_stream.agent_settings = {}
        mock_stream.parent_event_stream_uids = []
        
        # Mock events to have required attributes
        mock_event = MagicMock()
        mock_event.est_input_token = 10
        mock_event.est_output_token = 20
        mock_event.type = "user"
        mock_event.message = "test message"
        mock_stream.get_event_list_including_children_events.return_value = [mock_event]
        
        with patch('anges.web_interface.web_interface.event_storage') as mock_event_storage:
            mock_event_storage.load.return_value = mock_stream
            
            response = client.get('/load-chat/test_chat_id')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert data['mcp_config'] is None
            assert data['mcp_clients'] == []


if __name__ == '__main__':
    pytest.main([__file__]) 