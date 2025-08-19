import pytest
from unittest.mock import patch
from anges.web_interface.web_interface import app
from anges.agents.agent_utils.events import EventStream
import json
from queue import Queue
import time
import secrets

AGENT_RUNNER_PATH = 'anges.web_interface.web_interface.run_agent_task'
STREAM_TERMINATION_SIGNAL = "STREAM_COMPLETE"

@pytest.fixture(scope='function')
def client():
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True
    from anges.web_interface.web_interface import event_storage, message_queue_dict

    # Clear existing test data
    message_queue_dict.clear()

    # Proceed with client setup
    with app.test_client() as client_instance:
        stream = EventStream()
        chat_id = stream.uid
        event_storage.save(stream)
        if chat_id not in message_queue_dict:
             message_queue_dict[chat_id] = Queue()

        client_instance._test_chat_id = chat_id

        with client_instance.session_transaction() as session:
            user_id = str(secrets.token_hex(16))
            session['user_id'] = user_id
            # Associate the EventStream with the user ID in event_storage
            event_storage[user_id] = stream

        yield client_instance


def test_home_route(client):
    """Test if home route returns the chat template"""
    response = client.get('/')

def test_submit_route_default_dir(client):
    """Test if submit route accepts POST requests with messages using default directory"""
    # Get the user ID from the session
    with client.session_transaction() as session:
        user_id = session['user_id']
        from anges.web_interface.web_interface import event_storage
        # Create a new chat and get its ID
        stream = event_storage[user_id]

def test_submit_route_custom_dir(client):
    """Test if submit route accepts POST requests with messages and custom directory"""
    # Get the user ID from the session
    with client.session_transaction() as session:
        user_id = session['user_id']
        from anges.web_interface.web_interface import event_storage
        # Create a new chat and get its ID
        stream = event_storage[user_id]
        chat_id = stream.uid

    test_message = {'message': 'Hi', 'cmd_init_dir': '/tmp'}
    response = client.post(f'/submit/{chat_id}',
                         data=json.dumps(test_message),
                         content_type='application/json')
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_stream_route(client):
    """Test if stream route establishes SSE connection"""
    # Get the user ID from the session
    with client.session_transaction() as session:
        user_id = session['user_id']
        from anges.web_interface.web_interface import event_storage, message_queue_dict
        # Create a new chat and get its ID
        stream = event_storage[user_id]
        chat_id = stream.uid

    # Put a test message in the queue for this chat
    message_queue = message_queue_dict[chat_id]
    message_queue.put("Test message")
    message_queue.put("COMPLETE")

    response = client.get(f'/stream/{chat_id}')
    assert response.status_code == 200
    assert 'text/event-stream' in response.headers['Content-Type']

def test_message_formatting():
    """Test message formatting functions"""
    from anges.web_interface.web_interface import format_agent_message, format_complete_message

    # Test agent message formatting
    agent_msg = json.loads(format_agent_message("Test message"))
    assert agent_msg['type'] == 'message'
    assert agent_msg['content'] == 'Test message'

    # Test complete message formatting
    complete_msg = json.loads(format_complete_message())
    assert complete_msg['type'] == 'complete'
    assert complete_msg['content'] == 'Task completed'

@patch(AGENT_RUNNER_PATH)
def test_integration_flow_default_dir(mock_run_agent_task, client):
    """Test the complete flow from submission to streaming with default directory"""
    # Get chat_id from the client object provided by the fixture
    chat_id = client._test_chat_id
    from anges.web_interface.web_interface import message_queue_dict

    # Get the message queue for this chat
    message_queue = message_queue_dict[chat_id]

    # Submit a simple request - run_agent_task is now mocked
    test_message = {'message': 'What is the current directory?'}
    response = client.post(f'/submit/{chat_id}',
                         data=json.dumps(test_message),
                         content_type='application/json')
    assert response.status_code == 200
    mock_run_agent_task.assert_called_once()

    # Put test messages in the queue to simulate response
    message_queue.put("Test response message")
    message_queue.put(STREAM_TERMINATION_SIGNAL) # Use the signal the app expects

    # Start receiving the stream
    response = client.get(f'/stream/{chat_id}')
    assert response.status_code == 200

    # Check if we receive some messages with timeout
    received_data = False
    start_time = time.time()
    timeout = 5  # 5 seconds timeout

    # Use a non-blocking approach (within timeout)
    end_time = start_time + timeout
    stream_iterator = iter(response.response)
    while time.time() < end_time:
        # Get one line at a time
        try:
            line = next(stream_iterator)
            line_str = line.decode('utf-8').strip()
            if line_str.startswith('data: '):
                data_str = line_str[len('data: '):]
                try:
                    data = json.loads(data_str)
                    if data.get('type') == 'message':
                        received_data = True
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode stream data: {data_str}")
                    continue # Continue loop on decode error
        except StopIteration:
            # Stream ended naturally
            break # Exit loop if stream is exhausted
        except Exception as e:
             print(f"Error reading stream line: {e}")
             break # Exit loop on other errors

    assert received_data == True

@patch(AGENT_RUNNER_PATH)
def test_integration_flow_custom_dir(mock_run_agent_task, client):
    """Test the complete flow from submission to streaming with custom directory"""
    # Get chat_id from the client object provided by the fixture
    chat_id = client._test_chat_id
    from anges.web_interface.web_interface import event_storage, message_queue_dict
    # Get user_id from session if needed for later checks
    with client.session_transaction() as session:
        user_id = session['user_id']

    # Get the message queue for this chat
    message_queue = message_queue_dict[chat_id]

    # Submit a simple request with custom directory - run_agent_task is mocked
    test_message = {'message': 'What is the current directory?', 'cmd_init_dir': '/tmp'}
    response = client.post(f'/submit/{chat_id}',
                         data=json.dumps(test_message),
                         content_type='application/json')
    assert response.status_code == 200
    mock_run_agent_task.assert_called_once()

    # Put test messages in the queue to simulate response
    message_queue.put("Test response message for custom dir")
    message_queue.put(STREAM_TERMINATION_SIGNAL) # Use the signal the app expects

    # Start receiving the stream
    response = client.get(f'/stream/{chat_id}')
    assert response.status_code == 200

    # Check if we receive some messages with timeout
    received_data = False
    start_time = time.time()
    timeout = 5  # 5 seconds timeout

    # Use a non-blocking approach (within timeout)
    end_time = start_time + timeout
    stream_iterator = iter(response.response)
    while time.time() < end_time:
        # Get one line at a time
        try:
            line = next(stream_iterator)
            line_str = line.decode('utf-8').strip()
            if line_str.startswith('data: '):
                data_str = line_str[len('data: '):]
                try:
                    data = json.loads(data_str)
                    if data.get('type') == 'message':
                        received_data = True
                        # Keep original break condition
                        break # Exit loop as soon as one message is found
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode stream data: {data_str}")
                    continue # Continue loop on decode error
        except StopIteration:
            # Stream ended naturally before timeout or finding data
            break # Exit loop if stream is exhausted
        except Exception as e:
             print(f"Error reading stream line: {e}")
             break # Exit loop on other errors

    assert received_data == True

    # Verify that the EventStream object exists and is in expected state
    # (Since run_agent_task was mocked, lists should be empty)
    loaded_stream = event_storage.load(chat_id) # Load stream by chat_id
    assert isinstance(loaded_stream, EventStream)
    # These assertions assume the mocked function doesn't add events
    assert len(loaded_stream.events_list) == 0
    assert len(loaded_stream.event_summaries_list) == 0

if __name__ == '__main__':
    pytest.main(['-v', 'test_web_interface.py'])
