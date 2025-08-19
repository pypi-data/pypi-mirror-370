import pytest
from unittest.mock import patch
from anges.web_interface.web_interface import app, active_tasks
from anges.agents.agent_utils.events import EventStream
import json
import secrets

AGENT_RUNNER_PATH = 'anges.web_interface.web_interface.run_agent_task'
STREAM_TERMINATION_SIGNAL = "STREAM_COMPLETE"

@pytest.fixture(scope='function')
def client():
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True
    from anges.web_interface.web_interface import event_storage, message_queue_dict, active_tasks

    # Clear existing test data
    message_queue_dict.clear()
    active_tasks.clear()

    # Proceed with client setup
    with app.test_client() as client_instance:
        stream = EventStream()
        chat_id = stream.uid
        event_storage.save(stream)
        if chat_id not in message_queue_dict:
             message_queue_dict[chat_id] = pytest.importorskip("queue").Queue()

        client_instance._test_chat_id = chat_id

        with client_instance.session_transaction() as session:
            user_id = str(secrets.token_hex(16))
            session['user_id'] = user_id
            # Associate the EventStream with the user ID in event_storage
            event_storage[user_id] = stream

        yield client_instance

def test_check_stream_no_active_task(client):
    """Test if check_stream endpoint correctly reports when no active task exists"""
    # Get the chat_id from the client fixture
    chat_id = client._test_chat_id
    
    # Make request to check_stream endpoint
    response = client.get(f'/check_stream/{chat_id}')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['has_active_task'] is False

def test_check_stream_with_active_task(client):
    """Test if check_stream endpoint correctly reports when an active task exists"""
    # Get the chat_id from the client fixture
    chat_id = client._test_chat_id
    
    # Manually set the active task flag
    active_tasks[chat_id] = True
    
    # Make request to check_stream endpoint
    response = client.get(f'/check_stream/{chat_id}')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['has_active_task'] is True

def test_check_stream_nonexistent_chat(client):
    """Test if check_stream endpoint returns 404 for nonexistent chat"""
    # Use a non-existent chat ID
    nonexistent_chat_id = "nonexistent_chat_id"
    
    # Make request to check_stream endpoint
    response = client.get(f'/check_stream/{nonexistent_chat_id}')
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'message' in data

@patch(AGENT_RUNNER_PATH)
def test_active_task_tracking(mock_run_agent_task, client):
    """Test if active task tracking is correctly updated when submitting a task"""
    # Get the chat_id from the client fixture
    chat_id = client._test_chat_id
    
    # Verify no active task initially
    response = client.get(f'/check_stream/{chat_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['has_active_task'] is False
    
    # Submit a task
    test_message = {'message': 'Test message'}
    response = client.post(f'/submit/{chat_id}',
                         data=json.dumps(test_message),
                         content_type='application/json')
    assert response.status_code == 200
    
    # Verify active task is set
    response = client.get(f'/check_stream/{chat_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['has_active_task'] is True
    
    # Simulate task completion by directly updating active_tasks
    active_tasks[chat_id] = False
    
    # Verify active task is cleared
    response = client.get(f'/check_stream/{chat_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['has_active_task'] is False

@patch(AGENT_RUNNER_PATH)
def test_integration_with_agent_runner(mock_run_agent_task, client):
    """Test integration between submit endpoint, active task tracking, and check_stream endpoint"""
    # Get the chat_id from the client fixture
    chat_id = client._test_chat_id
    
    # Submit a task without a side effect first to test active task setting
    test_message = {'message': 'Test message'}
    response = client.post(f'/submit/{chat_id}',
                         data=json.dumps(test_message),
                         content_type='application/json')
    assert response.status_code == 200
    
    # Verify active task is set
    response = client.get(f'/check_stream/{chat_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['has_active_task'] is True
    
    # Now define a side effect for the mock that simulates task completion
    def mock_run_agent_side_effect(message, event_stream, message_queue, interrupt_flags, chat_id, *args, **kwargs):
        # Simulate task execution
        message_queue.put("Task is running")
        message_queue.put(STREAM_TERMINATION_SIGNAL)
        # Mark task as complete
        active_tasks[chat_id] = False
        
    # Manually simulate task completion
    active_tasks[chat_id] = False
    
    # Verify active task is cleared
    response = client.get(f'/check_stream/{chat_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['has_active_task'] is False

if __name__ == '__main__':
    pytest.main(['-v', 'test_stream_check.py'])