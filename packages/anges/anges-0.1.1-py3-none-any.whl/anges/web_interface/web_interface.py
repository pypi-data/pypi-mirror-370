from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    send_from_directory,
    Response
)
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os
from datetime import timedelta, datetime
import queue
from concurrent.futures import ThreadPoolExecutor
import logging
import argparse
import asyncio
from collections import defaultdict
import zipfile
import io
from anges.agents.agent_utils.events import Event, EventStream
from anges.utils.event_storage_service import event_storage_service as event_storage
from anges.web_interface.agent_runner import run_agent_task
from anges.config import config
from anges.utils.mcp_manager import McpManager

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Global variables
message_queue_dict = defaultdict(queue.Queue)
login_manager = LoginManager()
current_event_stream: EventStream|None = None  # Will store the single EventStream
interrupt_flags = {}
active_tasks = {}  # Dictionary to track active tasks for each chat ID

# Function to set the web interface password
def set_password(password):
    """
    Set the password for the web interface.

    Args:
        password (str): The password to set for authentication
    """
    global APP_PASSWORD
    APP_PASSWORD = password

# Default password for testing
APP_PASSWORD = "test_password"

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Add a file handler for debugging
debug_file_path = "/tmp/web_interface_debug.log"
os.makedirs(os.path.dirname(debug_file_path), exist_ok=True)
debug_handler = logging.FileHandler(debug_file_path)
debug_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
debug_handler = logging.FileHandler(debug_file_path)
debug_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return str(self.id)

def format_complete_message(events=None):
    logger.debug("Formatting complete message")
    events_dict = [event.to_dict() for event in events] if events else None
    return json.dumps(
        {"type": "complete", "content": "Task completed", "events": events_dict}
    )

def format_agent_message(message):
    """Format regular agent messages for SSE streaming"""
    return json.dumps({"type": "message", "content": message})

def init_app(password=None):
    global APP_PASSWORD, app
    
    # Add custom unauthorized handler for API requests
    def unauthorized_handler():
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        return redirect(url_for('login'))

    login_manager.unauthorized_handler(unauthorized_handler)

    # Create custom API login required decorator
    def api_login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if app.config.get('LOGIN_DISABLED', False):
                return f(*args, **kwargs)
            if not current_user.is_authenticated:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required'
                }), 401
            return f(*args, **kwargs)
        return decorated_function

    if password:
        APP_PASSWORD = password

    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Set session lifetime to 7 days
    app.config['SESSION_PERMANENT'] = True
    app.secret_key = config.web_interface.secret_key

    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    @app.route("/api/auth", methods=["POST"])
    def api_auth():
        try:
            data = request.get_json()
            password = data.get("password")
            if password == APP_PASSWORD:
                user = User(1)
                login_user(user)
                session["user_id"] = "testuser"
                return jsonify({"status": "success", "token": session["user_id"]})
            return jsonify({"status": "error", "message": "Invalid password"}), 401
        except Exception as e:
            logger.error(f"API auth error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/login", methods=["GET", "POST"])
    def login():
        global current_event_stream
        if request.method == "POST":
            password = request.form.get("password")
            if password == APP_PASSWORD:
                user = User(1)
                login_user(user)
                session["user_id"] = "testuser"
                
                # Initialize or load event stream from storage
                if current_event_stream is None:
                    # Try to load existing event stream
                    stream_ids = event_storage.list_streams()
                    if stream_ids:
                        # Load the first available event stream
                        current_event_stream = event_storage.load(stream_ids[0])
                    
                    # If no existing stream or loading failed, create new one
                    if current_event_stream is None:
                        current_event_stream = EventStream()
                        event_storage.save(current_event_stream)
                
                logger.debug(f"New session created: {session['user_id']}")
                return redirect(url_for("home"))
            return render_template("login.html", error="Invalid password")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        session.clear()
        logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    # @login_required
    def home():
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        return render_template("chat.html")

    @app.route("/submit/<chat_id>", methods=["POST"])
    @api_login_required
    def submit(chat_id):
        # global current_event_stream
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid session"}), 400

        current_event_stream = event_storage.load(chat_id)
        data = request.json
        message = data.get("message")
        cmd_init_dir = data.get("cmd_init_dir", ".")
        model = data.get("model", "agent_default")  # Default to agent config
        prefix_cmd = data.get("prefix_cmd", "")  # Default to empty string if not specified
        agent_type = data.get("agent_type", "default")  # Default to original agent if not specified
        notes = data.get("notes", [])  # Default to empty list if not specified

        logger.debug(f"Received submit request with message: {message} and agent_type: {agent_type}")

        # Store agent settings in the event stream
        if current_event_stream:
            current_event_stream.agent_settings = {
                "cmd_init_dir": cmd_init_dir,
                "model": model,
                "prefix_cmd": prefix_cmd,
                "agent_type": agent_type,
                "notes": notes
            }
            event_storage.save(current_event_stream)
        
        message_queue = message_queue_dict[current_event_stream.uid]
        # Clear the queue for new messages
        while not message_queue.empty():
            message_queue.get()

        # Mark this chat as having an active task
        active_tasks[chat_id] = True
        logger.debug(f"Marked chat {chat_id} as having an active task")

        # Use ThreadPoolExecutor for better thread management
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(run_agent_task,
                      message,
                      current_event_stream,
                      message_queue,
                      interrupt_flags,
                      chat_id,
                      cmd_init_dir,
                      model,
                      prefix_cmd,
                      agent_type,
                      notes)
        return jsonify({"status": "success"}), 200

    @app.route("/new-chat")
    @api_login_required
    def new_chat():
        global current_event_stream
        # Create new empty event stream
        current_event_stream = EventStream()
        # Save to persistent storage
        event_storage.save(current_event_stream)
        logger.debug("Created new chat")
        return jsonify({"status": "success", "chat_id": current_event_stream.uid})

    @app.route("/list-chats")
    # @login_required
    def list_chats():
        try:
            stream_ids = event_storage.list_streams()
            chats = {}
            for stream_id in stream_ids:
                stream = event_storage.load(stream_id)
                if stream:
                    title = stream.title if hasattr(stream, 'title') and stream.title else "<no title>"
                    created_at = stream.created_at if hasattr(stream, 'created_at') else None
                    chats[stream_id] = {
                        "stream_id": stream_id,
                        "title": title,
                        "created_at": created_at
                    }
            return jsonify({"status": "success", "chats": chats})
        except Exception as e:
            logger.error(f"Error listing chats: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/load-chat/<chat_id>")
    # @login_required
    def load_chat(chat_id):
        global current_event_stream
        try:
            current_event_stream = event_storage.load(chat_id)
            if current_event_stream is None:
                return jsonify({"status": "error", "message": "Chat not found"}), 404
            all_events = current_event_stream.get_event_list_including_children_events()
            total_est_token_input = 0
            total_est_token_output = 0
            for e in all_events:
                total_est_token_input += e.est_input_token
                total_est_token_output += e.est_output_token
            # Get MCP configuration and status
            mcp_config = current_event_stream.mcp_config
            mcp_clients = []
            try:
                if mcp_config:
                    event_stream_mcp_manager = McpManager(mcp_config)
                    clients_info = event_stream_mcp_manager.list_mcp_clients()
                    for client_info in clients_info:
                        client_info["tools"] = [
                            {"name": tool.name} for tool in client_info["tools"]
                        ]
                    mcp_clients = clients_info
            except Exception as e:
                logger.warning(f"Error loading MCP clients for chat {chat_id}: {e}")
            
            return jsonify({
                "status": "success",
                "est_input_token": total_est_token_input,
                "est_output_token": total_est_token_output,
                "agent_settings": current_event_stream.agent_settings,
                "mcp_config": mcp_config,
                "mcp_clients": mcp_clients,
                "parent_event_stream_uids": current_event_stream.parent_event_stream_uids,
                "events": [{"type": event.type, "message": event.message } for event in all_events]
            })
        except Exception as e:
            logger.error(f"Error loading chat {chat_id}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/interrupt/<chat_id>", methods=["POST"])
    @api_login_required
    def interrupt(chat_id):
        interrupt_flags[chat_id] = True
        logger.debug(f"Set interrupt flag for chat {chat_id}")
        return jsonify({"status": "success"})

    @app.route("/edit-chat/<chat_id>", methods=["POST"])
    @login_required
    def edit_chat(chat_id):
        try:
            data = request.json
            new_title = data.get("title")
            if not new_title:
                return jsonify({"status": "error", "message": "Title is required"}), 400
            event_storage.update_stream_title(chat_id, new_title)
            return jsonify({"status": "success"})
        except Exception as e:
            logger.error(f"Error editing chat {chat_id}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/stream/<chat_id>")
    @api_login_required
    def stream(chat_id):
        # global current_event_stream
        current_event_stream = event_storage.load(chat_id)
        message_queue = message_queue_dict[current_event_stream.uid]
        user_id = session.get("user_id")
        logger.debug(f"Started streaming for user {user_id}")
        
        def generate():
            while True:
                message = message_queue.get()  # This will block until a message is available
                if message == "STREAM_COMPLETE":
                    break
                yield f"data: {format_agent_message(message)}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    @app.route("/delete-chat/<chat_id>", methods=["POST"])
    @api_login_required
    def delete_chat(chat_id):
        try:
            event_storage.delete_stream(chat_id, recursive=True)
            return jsonify({"status": "success"})
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/favicon.ico")
    def favicon():
        try:
            return send_from_directory("static", "favicon.ico")
        except Exception as e:
            logger.error(f"Error serving favicon: {str(e)}")
            return str(e), 500
            
    @app.route("/check_stream/<chat_id>")
    @api_login_required
    def check_stream(chat_id):
        """
        Check if a chat has an active task.
        
        Args:
            chat_id (str): The ID of the chat to check
            
        Returns:
            JSON response with the status of the task
        """
        try:
            # Check if the chat exists
            stream = event_storage.load(chat_id)
            if stream is None:
                return jsonify({"status": "error", "message": "Chat not found"}), 404
                
            # Check if the chat has an active task
            is_active = active_tasks.get(chat_id, False)
            logger.debug(f"Checking if chat {chat_id} has an active task: {is_active}")
            
            return jsonify({
                "status": "success",
                "has_active_task": is_active
            })
        except Exception as e:
            logger.error(f"Error checking stream status for chat {chat_id}: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    # MCP management routes
    @app.route("/api/mcp/refresh", methods=["POST"])
    @api_login_required
    def refresh_mcp_status():
        """Refresh MCP client status"""
        try:
            global current_event_stream
            
            if current_event_stream is None:
                return jsonify({"status": "error", "message": "No active event stream"}), 400
            
            # Get current configuration
            mcp_config = current_event_stream.mcp_config
            
            # Initialize MCP manager with current configuration
            event_stream_mcp_manager = McpManager(mcp_config)
            
            # Get client status and tools
            clients_info = event_stream_mcp_manager.list_mcp_clients()
            for client_info in clients_info:
                client_info["tools"] = [
                    {"name": tool.name} for tool in client_info["tools"]
                ]
            
            return jsonify({
                "status": "success", 
                "mcp_clients": clients_info
            })
        except Exception as e:
            logger.error(f"Error refreshing MCP status: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/mcp/config", methods=["PUT"])
    @api_login_required
    def update_mcp_config():
        """Update entire MCP configuration from JSON"""
        try:
            global current_event_stream

            if current_event_stream is None:
                return jsonify({"status": "error", "message": "No active event stream"}), 400

            data = request.get_json()
            mcp_config = data.get("mcp_config")

            if mcp_config is None:
                return jsonify({"status": "error", "message": "mcp_config is required"}), 400

            if not isinstance(mcp_config, dict):
                return jsonify({"status": "error", "message": "mcp_config must be a valid JSON object"}), 400

            # Validate configuration format
            for name, config in mcp_config.items():
                if not isinstance(config, dict):
                    return jsonify({"status": "error", "message": f"Invalid configuration for '{name}': must be an object"}), 400
                if "command" not in config or "args" not in config:
                    return jsonify({"status": "error", "message": f"Invalid configuration for '{name}': missing 'command' or 'args'"}), 400
                if not isinstance(config["args"], list):
                    return jsonify({"status": "error", "message": f"Invalid configuration for '{name}': 'args' must be an array"}), 400

            # Update the event stream's MCP configuration
            current_event_stream.mcp_config = mcp_config

            # Save the event stream
            event_storage.save_event_stream(current_event_stream)

            return jsonify({"status": "success", "message": "MCP configuration updated successfully"})
        except json.JSONDecodeError:
            return jsonify({"status": "error", "message": "Invalid JSON format"}), 400

    @app.route('/export-chat/<chat_id>', methods=['GET'])
    @api_login_required
    def export_chat(chat_id):
        """
        Export a chat and all its related event streams as a zip file.
        
        Args:
            chat_id (str): The ID of the chat to export
            
        Returns:
            ZIP file containing all related event streams as event_stream_id.json files
        """
        try:
            # Load the main event stream
            main_stream = event_storage.load(chat_id)
            if main_stream is None:
                return jsonify({"status": "error", "message": "Chat not found"}), 404
            
            # Get all related event stream IDs using the new recursive method
            try:
                children_stream_ids = main_stream.get_all_children_event_stream_ids()
                # Convert list to set and include the main stream ID as well
                if isinstance(children_stream_ids, list):
                    all_stream_ids = set(children_stream_ids)
                else:
                    all_stream_ids = children_stream_ids
                all_stream_ids.add(chat_id)
                logger.info(f"Found {len(all_stream_ids)} related streams for chat {chat_id}")
            except AttributeError:
                # Fallback if the method doesn't exist yet
                logger.warning(f"get_all_children_event_stream_ids method not found, exporting only main stream {chat_id}")
                all_stream_ids = {chat_id}
            except Exception as e:
                logger.error(f"Error getting children event stream IDs for {chat_id}: {e}")
                return jsonify({"status": "error", "message": f"Error collecting related streams: {str(e)}"}), 500
            
            # Create a zip file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Process each event stream
                for stream_id in all_stream_ids:
                    try:
                        stream = event_storage.load(stream_id)
                        if stream is None:
                            logger.warning(f"Could not load stream {stream_id}, skipping")
                            continue
                        
                        # Get all events for this stream
                        all_events = stream.get_event_list_including_children_events()
                        
                        # Convert events to the expected format
                        events_data = {
                            "stream_id": stream_id,
                            "title": getattr(stream, 'title', '<no title>'),
                            "created_at": getattr(stream, 'created_at', None),
                            "agent_settings": getattr(stream, 'agent_settings', {}),
                            "parent_event_stream_uids": getattr(stream, 'parent_event_stream_uids', []),
                            "events": [event.to_dict() for event in all_events]
                        }
                        
                        # Add to zip file with the expected structure: event_stream_id.json
                        file_path = f"{stream_id}.json"
                        zip_file.writestr(file_path, json.dumps(events_data, indent=2, cls=DateTimeEncoder))
                        
                    except Exception as e:
                        logger.error(f"Error processing stream {stream_id}: {e}")
                        # Add more detailed error information
                        logger.error(f"Stream {stream_id} error details: {type(e).__name__}: {str(e)}")
                        # Continue with other streams even if one fails
                        continue
            
            # Prepare the zip file for download
            zip_buffer.seek(0)
            
            # Create response with proper headers
            response = Response(
                zip_buffer.getvalue(),
                mimetype='application/zip',
                headers={
                    'Content-Disposition': f'attachment; filename="chat_{chat_id}_export.zip"',
                    'Content-Length': str(len(zip_buffer.getvalue()))
                }
            )
            
            logger.info(f"Successfully exported chat {chat_id} with {len(all_stream_ids)} streams")
            return response
            
        except Exception as e:
            logger.error(f"Unexpected error during chat export for {chat_id}: {e}")
            logger.error(f"Export error details: {type(e).__name__}: {str(e)}")
            return jsonify({"status": "error", "message": f"Export failed: {str(e)}"}), 500

    return app


def main():
    """
    Parse command-line arguments and run the web interface.

    This function is the entry point when running the web interface directly.
    """
    parser = argparse.ArgumentParser(description="Run the AI Agent Web Interface")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for accessing the interface",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the server on (127.0.0.1 or 0.0.0.0)",
    )

    args = parser.parse_args()

    # Initialize the app with the provided password
    app = init_app(args.password)

    # Run the app
    run_app(app, host=args.host, port=args.port)


def run_app(app, host="127.0.0.1", port=5000, debug=True):
    """
    Run the Flask application with the specified parameters.

    This function can be called programmatically to run the web interface.

    Args:
        app: The Flask application instance
        host: Host address to bind (default: "127.0.0.1")
        port: Port number to listen on (default: 5000)
        debug: Whether to run in debug mode (default: True)
    """
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    main()

# Initialize the app with default settings for testing
app = init_app()
