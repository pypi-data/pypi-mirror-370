**Languages**: [English](web-interface.md) | [中文](zh/web-interface.md)

---
# Web Interface Documentation

The Anges web interface provides a browser-based user interface for interacting with AI agents. It offers real-time communication, task management, and session handling through a Flask-based web application.

## Overview

The web interface consists of several key components:

- **Flask Web Application**: Main web server with authentication and routing
- **Agent Runner**: Task execution and agent management
- **Event Storage**: Event persistence and retrieval
- **Real-time Communication**: WebSocket-like messaging for live updates
- **Session Management**: User authentication and session handling

## Architecture

### Core Components

#### Web Interface (`web_interface.py`)

The main Flask application that handles:
- HTTP routing and request handling
- User authentication and session management
- Real-time messaging queues
- Agent task coordination
- Static file serving

#### Agent Runner (`agent_runner.py`)

Manages agent execution with features:
- Task execution with configurable parameters
- Logging and message queue integration
- Interrupt handling for task cancellation
- Multi-agent support with different agent types

#### Event Storage (`event_storage.py`)

Provides event persistence through:
- Wrapper around centralized EventStorageService
- Event stream management per user
- Save/load functionality for event streams
- API compatibility layer

## Web Interface Configuration

### Basic Configuration

```yaml
web_interface:
  host: "0.0.0.0"
  port: 5000
  enable_authentication: true
  session_timeout: 3600
  secret_key: "your-secret-key-for-sessions"
```

### Environment Variables

```bash
# Override web interface settings
export ANGES_WEB_INTERFACE_HOST="localhost"
export ANGES_WEB_INTERFACE_PORT=8080
export ANGES_WEB_INTERFACE_ENABLE_AUTHENTICATION=false
```

## Authentication System

### Password-Based Authentication

The web interface uses simple password-based authentication:

```python
from anges.web_interface.web_interface import set_password

# Set custom password
set_password("your-secure-password")
```

### Session Management

- **Session Timeout**: Configurable session duration
- **Secure Sessions**: Flask session encryption with secret key
- **Login Required**: Decorator-based route protection

### Default Credentials

- **Default Password**: `test_password` (for development only)
- **Production**: Always set a secure password in production

## API Endpoints

### Authentication Endpoints

#### `POST /login`
Authenticate user with password.

**Request:**
```json
{
  "password": "your-password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful"
}
```

#### `POST /logout`
Log out current user and clear session.

### Chat Endpoints

#### `GET /`
Main chat interface (requires authentication).

#### `POST /send_message`
Send message to agent for processing.

**Request:**
```json
{
  "message": "Your message to the agent",
  "model": "gpt-4",
  "agent_type": "task_executor",
  "prefix_cmd": "optional-prefix"
}
```

**Response:**
```json
{
  "status": "success",
  "chat_id": "unique-chat-id"
}
```

#### `GET /get_messages/<chat_id>`
Retrieve messages for a specific chat session.

**Response:**
```json
{
  "messages": [
    "Message 1",
    "Message 2"
  ],
  "task_complete": false
}
```

#### `POST /interrupt/<chat_id>`
Interrupt running agent task.

**Response:**
```json
{
  "status": "interrupted"
}
```

### Event Stream Endpoints

#### `GET /list_streams`
List all available event streams.

**Response:**
```json
{
  "streams": [
    {
      "id": "stream-1",
      "title": "Stream Title",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### `GET /load_stream/<stream_id>`
Load specific event stream.

#### `POST /update_stream_title/<stream_id>`
Update event stream title.

**Request:**
```json
{
  "title": "New Stream Title"
}
```

## Agent Runner

### Task Execution

The agent runner handles task execution with the following features:

#### Function Signature

```python
def run_agent_task(
    message,
    event_stream=None,
    message_queue=None,
    interrupt_flags=None,
    chat_id=None,
    cmd_init_dir=None,
    model=None,
    prefix_cmd="",
    agent_type="task_executor",
):
```

#### Parameters

- **message** (str): User message or task description
- **event_stream** (EventStream, optional): Existing event stream to continue
- **message_queue** (Queue, optional): Queue for real-time message updates
- **interrupt_flags** (dict, optional): Flags for task interruption
- **chat_id** (str, optional): Unique identifier for the chat session
- **cmd_init_dir** (str, optional): Initial directory for command execution
- **model** (str, optional): AI model to use for the task
- **prefix_cmd** (str, optional): Command prefix for shell operations
- **agent_type** (str, optional): Type of agent to use

#### Agent Types

- **task_executor**: General task execution agent
- **task_analyzer**: Task analysis and planning agent
- **orchestrator**: Multi-agent coordination
- **default_agent**: Basic agent functionality

### Message Queue Integration

Real-time communication through message queues:

```python
import queue
from collections import defaultdict

# Global message queues per chat
message_queue_dict = defaultdict(queue.Queue)

# Get messages for a chat
chat_queue = message_queue_dict[chat_id]
messages = []
while not chat_queue.empty():
    messages.append(chat_queue.get())
```

### Interrupt Handling

Task interruption mechanism:

```python
# Set interrupt flag
interrupt_flags[chat_id] = True

# Check for interruption in agent
def check_interrupt():
    if interrupt_flags and chat_id in interrupt_flags:
        return interrupt_flags[chat_id]
    return False
```

## Event Storage

### Event Stream Management

The event storage system provides:

#### Core Operations

```python
from anges.web_interface.event_storage import EventStorage

# Initialize storage
storage = EventStorage()

# Save event stream
storage.save(event_stream)

# Load event stream
loaded_stream = storage.load(stream_id)

# List all streams
streams = storage.list_streams()

# Update stream title
storage.update_stream_title(stream_id, "New Title")
```

#### User-Specific Streams

```python
# Access user-specific event streams
user_stream = storage[user_id]
storage[user_id] = new_event_stream
```

### Integration with EventStorageService

The EventStorage class serves as a compatibility wrapper:

```python
class EventStorage:
    def __init__(self):
        # Delegate to singleton service
        self._service = event_storage_service
    
    def save(self, event_stream):
        return self._service.save(event_stream)
    
    def load(self, stream_id):
        return self._service.load(stream_id)
```

## Frontend Integration

### HTML Templates

The web interface uses Flask templates for rendering:

- **Base template**: Common layout and styling
- **Login page**: Authentication form
- **Chat interface**: Main conversation interface
- **Error pages**: Error handling and display

### JavaScript Integration

```javascript
// Send message to agent
function sendMessage(message, model, agentType) {
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            model: model,
            agent_type: agentType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            pollForMessages(data.chat_id);
        }
    });
}

// Poll for new messages
function pollForMessages(chatId) {
    setInterval(() => {
        fetch(`/get_messages/${chatId}`)
            .then(response => response.json())
            .then(data => {
                updateChatDisplay(data.messages);
                if (data.task_complete) {
                    stopPolling();
                }
            });
    }, 1000);
}
```

## Deployment

### Development Setup

```python
from anges.web_interface.web_interface import app

# Run development server
if __name__ == '__main__':
    app.run(
        host='localhost',
        port=5000,
        debug=True
    )
```

### Production Deployment

#### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 anges.web_interface.web_interface:app
```

#### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "anges.web_interface.web_interface:app"]
```

#### Environment Configuration

```bash
# Production environment variables
export ANGES_WEB_INTERFACE_HOST="0.0.0.0"
export ANGES_WEB_INTERFACE_PORT=80
export ANGES_WEB_INTERFACE_ENABLE_AUTHENTICATION=true
export ANGES_WEB_INTERFACE_SECRET_KEY="$(openssl rand -hex 32)"
```

### Reverse Proxy Setup

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

### Authentication Security

1. **Strong Passwords**: Use complex passwords in production
2. **HTTPS**: Always use HTTPS in production environments
3. **Session Security**: Configure secure session cookies
4. **Rate Limiting**: Implement rate limiting for login attempts

### Input Validation

```python
from flask import request
import re

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    
    # Validate message length
    message = data.get('message', '')
    if len(message) > 10000:
        return jsonify({'error': 'Message too long'}), 400
    
    # Validate model name
    model = data.get('model', '')
    if not re.match(r'^[a-zA-Z0-9-_]+$', model):
        return jsonify({'error': 'Invalid model name'}), 400
```

### File Upload Security

```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'success': True})
```

## Monitoring and Logging

### Application Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/anges_web.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Performance Monitoring

```python
from flask import g
import time

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    total_time = time.time() - g.start_time
    app.logger.info(f'Request completed in {total_time:.3f}s')
    return response
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>
```

#### Session Issues
```python
# Clear Flask sessions
from flask import session
session.clear()

# Check session configuration
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
```

#### Message Queue Problems
```python
# Clear message queues
message_queue_dict.clear()

# Check queue status
for chat_id, queue in message_queue_dict.items():
    print(f"Chat {chat_id}: {queue.qsize()} messages")
```

### Debug Mode

```python
# Enable debug mode
app.run(debug=True)

# Debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference Summary

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/login` | POST | User authentication | No |
| `/logout` | POST | User logout | Yes |
| `/` | GET | Main chat interface | Yes |
| `/send_message` | POST | Send message to agent | Yes |
| `/get_messages/<chat_id>` | GET | Get chat messages | Yes |
| `/interrupt/<chat_id>` | POST | Interrupt agent task | Yes |
| `/list_streams` | GET | List event streams | Yes |
| `/load_stream/<stream_id>` | GET | Load event stream | Yes |
| `/update_stream_title/<stream_id>` | POST | Update stream title | Yes |

The web interface provides a comprehensive platform for interacting with Anges agents through a user-friendly browser interface, complete with real-time messaging, task management, and secure session handling.