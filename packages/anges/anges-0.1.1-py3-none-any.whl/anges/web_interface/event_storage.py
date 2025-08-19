from ..utils.event_storage_service import event_storage_service
from ..agents.agent_utils.events import EventStream

class EventStorage:
    """Thin wrapper around EventStorageService to maintain API compatibility.
    
    This class delegates all operations to the centralized EventStorageService
    while maintaining the exact same API that existing code expects.
    """
    
    def __init__(self):
        # Delegate to the singleton service instance
        self._service = event_storage_service
    
    @property
    def current_event_stream(self):
        """Get the current event stream from the service."""
        return self._service.current_event_stream
    
    @current_event_stream.setter
    def current_event_stream(self, value):
        """Set the current event stream on the service."""
        self._service.current_event_stream = value
    
    @property
    def _user_streams(self):
        """Get the user streams dictionary from the service."""
        return self._service._user_streams
    
    def __getitem__(self, user_id):
        """Support dictionary-style access for user event streams"""
        return self._service[user_id]
    
    def __setitem__(self, user_id, event_stream):
        """Support dictionary-style assignment for user event streams"""
        self._service[user_id] = event_stream
    
    def save(self, event_stream):
        """Save the event stream"""
        return self._service.save(event_stream)
    
    def load(self, stream_id):
        """Load an event stream by ID"""
        return self._service.load(stream_id)
    
    def list_streams(self):
        """List all available event streams"""
        return self._service.list_streams()
    
    def update_stream_title(self, stream_id, title):
        """Update stream title"""
        return self._service.update_stream_title(stream_id, title)
    
    def delete_stream(self, stream_id, recursive=False):
        """Delete stream"""
        return self._service.delete_stream(stream_id, recursive)

# Create a singleton instance
event_storage = EventStorage()
