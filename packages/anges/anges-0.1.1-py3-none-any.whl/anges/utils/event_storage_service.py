import os
import json
import logging
from typing import Optional, List, Dict, Set
from ..agents.agent_utils.events import EventStream
from .shared_base import DATA_DIR

class EventStorageService:
    """Enhanced event storage service that consolidates all event stream functionality.
    
    This service provides:
    - Event stream CRUD operations
    - User session management
    - Title updating functionality
    - Proper error handling
    - Directory management
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the event storage service.
        
        Args:
            data_dir (Optional[str]): Custom data directory path. If None, uses default.
        """
        self._data_dir = os.path.expanduser(data_dir or DATA_DIR)
        self._user_streams: Dict[str, EventStream] = {}  # Dictionary to store per-user event streams
        self.current_event_stream: Optional[EventStream] = None
        self.logger = logging.getLogger(__name__)
    
    # Directory management methods
    def get_data_dir(self) -> str:
        """Get the current data directory.
        
        Returns:
            str: The data directory path
        """
        return self._data_dir
    
    def set_data_dir(self, path: str) -> None:
        """Set the data directory path.
        
        Args:
            path (str): New data directory path
        """
        self._data_dir = os.path.expanduser(path)
    
    def ensure_data_dir(self) -> None:
        """Ensure the data directory exists.
        
        Raises:
            OSError: If directory creation fails
        """
        try:
            os.makedirs(self.get_data_dir(), exist_ok=True)
        except OSError as e:
            self.logger.error(f"Failed to create data directory {self.get_data_dir()}: {e}")
            raise
    
    # User session management methods
    def __getitem__(self, user_id: str) -> Optional[EventStream]:
        """Support dictionary-style access for user event streams.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Optional[EventStream]: The user's event stream or None
        """
        return self._user_streams.get(user_id)
    
    def __setitem__(self, user_id: str, event_stream: EventStream) -> None:
        """Support dictionary-style assignment for user event streams.
        
        Args:
            user_id (str): User identifier
            event_stream (EventStream): Event stream to assign
            
        Raises:
            ValueError: If event_stream is not an EventStream instance
            RuntimeError: If save operation fails
        """
        if not isinstance(event_stream, EventStream):
            raise ValueError("event_stream must be an EventStream instance")
        
        self._user_streams[user_id] = event_stream
        if not self.save_event_stream(event_stream):
            raise RuntimeError(f"Failed to persist event stream for user {user_id}")
    
    def get_user_stream(self, user_id: str) -> Optional[EventStream]:
        """Get event stream for a specific user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Optional[EventStream]: The user's event stream or None
        """
        return self._user_streams.get(user_id)
    
    def set_user_stream(self, user_id: str, event_stream: EventStream) -> bool:
        """Set event stream for a specific user.
        
        Args:
            user_id (str): User identifier
            event_stream (EventStream): Event stream to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self[user_id] = event_stream
            return True
        except (ValueError, RuntimeError) as e:
            self.logger.error(f"Failed to set user stream for {user_id}: {e}")
            return False
    
    def remove_user_stream(self, user_id: str) -> bool:
        """Remove user stream from session management.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if removed, False if user not found
        """
        if user_id in self._user_streams:
            del self._user_streams[user_id]
            return True
        return False
    
    # Core event stream operations
    def save_event_stream(self, event_stream: EventStream) -> bool:
        """Save an EventStream object as a JSON file.
        
        Args:
            event_stream (EventStream): The event stream to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not isinstance(event_stream, EventStream):
            self.logger.error("Invalid event stream type provided for saving")
            return False
        
        try:
            self.ensure_data_dir()
            file_path = os.path.join(self.get_data_dir(), f"{event_stream.uid}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(event_stream.to_json())
            self.logger.debug(f"Successfully saved event stream {event_stream.uid}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save event stream {event_stream.uid}: {e}")
            return False
    
    def load_event_stream(self, uid: str) -> Optional[EventStream]:
        """Load an event stream by UID.
        
        Args:
            uid (str): The UID of the event stream to load
            
        Returns:
            Optional[EventStream]: The event stream object if successful, None otherwise
        """
        if not uid or not isinstance(uid, str):
            self.logger.error("Invalid UID provided for loading")
            return None
        
        try:
            self.ensure_data_dir()
            file_path = os.path.join(self.get_data_dir(), f"{uid}.json")
            
            if not os.path.exists(file_path):
                self.logger.debug(f"Event stream file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
                event_stream = EventStream.from_dict(data)
                self.logger.debug(f"Successfully loaded event stream {uid}")
                return event_stream
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in event stream file {uid}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load event stream {uid}: {e}")
            return None
    
    def list_event_streams(self) -> List[str]:
        """List all event stream UIDs.
        
        Returns:
            List[str]: List of event stream UIDs (filenames without .json extension)
        """
        try:
            self.ensure_data_dir()
            files = os.listdir(self.get_data_dir())
            stream_uids = [f[:-5] for f in files if f.endswith('.json')]
            self.logger.debug(f"Found {len(stream_uids)} event streams")
            return stream_uids
        except Exception as e:
            self.logger.error(f"Failed to list event streams: {e}")
            return []
    
    def update_stream_title(self, stream_id: str, title: str) -> bool:
        """Update the title of an event stream.
        
        Args:
            stream_id (str): The UID of the event stream
            title (str): New title for the stream
            
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            ValueError: If stream not found or title is invalid
        """
        if not stream_id or not isinstance(stream_id, str):
            raise ValueError("Stream ID must be a non-empty string")
        
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
        
        event_stream = self.load_event_stream(stream_id)
        if event_stream is None:
            raise ValueError(f"Stream with ID {stream_id} not found")
        
        try:
            event_stream.title = title.strip()
            success = self.save_event_stream(event_stream)
            if success:
                self.logger.info(f"Updated title for stream {stream_id} to '{title.strip()}'")
            return success
        except Exception as e:
            self.logger.error(f"Failed to update title for stream {stream_id}: {e}")
            return False
    
    def _get_child_stream_uids(self, event_stream: EventStream) -> Set[str]:
        """Get all child stream UIDs for an event stream.
        
        Args:
            event_stream (EventStream): The parent event stream
            
        Returns:
            Set[str]: Set of child stream UIDs
        """
        child_uids = set()
        
        try:
            # Get children from events
            for event in event_stream.events_list:
                if event.type == "child_agent_running":
                    try:
                        child_info = json.loads(event.reasoning)
                        child_uids.add(child_info["agent_id"])
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            # Get any streams that list this as parent
            all_streams = self.list_event_streams()
            for uid in all_streams:
                try:
                    stream = self.load_event_stream(uid)
                    if stream and event_stream.uid in stream.parent_event_stream_uids:
                        child_uids.add(uid)
                except Exception:
                    continue
        except Exception as e:
            self.logger.error(f"Error finding child streams for {event_stream.uid}: {e}")
        
        return child_uids
    
    def delete_event_stream(self, uid: str, recursive: bool = False) -> bool:
        """Delete an event stream and optionally its children.
        
        Args:
            uid (str): The UID of the event stream to delete
            recursive (bool): If True, delete all child streams first
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not uid or not isinstance(uid, str):
            self.logger.error("Invalid UID provided for deletion")
            return False
        
        try:
            # Read the stream first
            stream = self.load_event_stream(uid)
            if not stream:
                self.logger.warning(f"Stream {uid} not found for deletion")
                return False
            
            if recursive:
                # Delete all children first
                child_uids = self._get_child_stream_uids(stream)
                for child_uid in child_uids:
                    if not self.delete_event_stream(child_uid, recursive=True):
                        self.logger.warning(f"Failed to delete child stream {child_uid}")
            
            # Delete the stream file
            file_path = os.path.join(self.get_data_dir(), f"{uid}.json")
            if not os.path.exists(file_path):
                self.logger.warning(f"Stream file {file_path} does not exist")
                return False
            
            os.remove(file_path)
            
            # Remove from user sessions if present
            users_to_remove = [user_id for user_id, stream in self._user_streams.items() 
                             if stream and stream.uid == uid]
            for user_id in users_to_remove:
                self.remove_user_stream(user_id)
            
            self.logger.info(f"Successfully deleted event stream {uid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete event stream {uid}: {e}")
            return False
    
    # Legacy method aliases for backward compatibility
    def save(self, event_stream: EventStream) -> bool:
        """Legacy alias for save_event_stream."""
        return self.save_event_stream(event_stream)
    
    def load(self, stream_id: str) -> Optional[EventStream]:
        """Legacy alias for load_event_stream."""
        return self.load_event_stream(stream_id)
    
    def list_streams(self) -> List[str]:
        """Legacy alias for list_event_streams."""
        return self.list_event_streams()
    
    def delete_stream(self, stream_id: str, recursive: bool = False) -> bool:
        """Legacy alias for delete_event_stream."""
        return self.delete_event_stream(stream_id, recursive)


# Create a singleton instance for backward compatibility
event_storage_service = EventStorageService()

# Legacy function exports for backward compatibility
def save_event_stream(event_stream: EventStream) -> bool:
    """Legacy function wrapper for save_event_stream."""
    return event_storage_service.save_event_stream(event_stream)

def read_event_stream(uid: str) -> Optional[EventStream]:
    """Legacy function wrapper for load_event_stream."""
    return event_storage_service.load_event_stream(uid)

def list_event_streams() -> List[str]:
    """Legacy function wrapper for list_event_streams."""
    return event_storage_service.list_event_streams()

def delete_event_stream(uid: str, recursive: bool = False) -> bool:
    """Legacy function wrapper for delete_event_stream."""
    return event_storage_service.delete_event_stream(uid, recursive)

def get_data_dir() -> str:
    """Legacy function wrapper for get_data_dir."""
    return event_storage_service.get_data_dir()

def set_data_dir(path: str) -> None:
    """Legacy function wrapper for set_data_dir."""
    event_storage_service.set_data_dir(path)

def ensure_data_dir() -> None:
    """Legacy function wrapper for ensure_data_dir."""
    event_storage_service.ensure_data_dir()