import string
import random
import json
from datetime import datetime
import re
import logging
from anges.utils.shared_base import get_data_dir
import os

RETURN_TO_PARENT_EVENT_TYPES = ["task_interrupted", "task_completion", "agent_requested_help", "agent_text_response"]
def read_event_stream(uid: str):
    try:
        file_path = os.path.join(get_data_dir(), f"{uid}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            data = json.loads(f.read())
            return EventStream.from_dict(data)
    except Exception as e:
        logging.error(f"Failed to read_event_stream {e} ")
        return None

def remove_ansi_escape_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class Event:
    """Represents a single event in the agent's execution history.
    type: *required* The type of event (e.g. "new_request", "task_completion", "task_interrupted", "action", "edit_file", "call_child_agent"). This is needed to determine how to process the event.
    message: *required* This will be shown to the user in the chat history. The **user visible** action tags (task_complete, help_needed, agent_text_response) will be stored to this.
    reasoning: *required* The content in the reasoning tag from the agent response will be stored here. This will be shown in the constructed event history. Also this is shown to the web UI like "thinking path"
    content: The content in the content tag from the agent response will be stored here. This will be shown in the constructed event history.
    analysis: The content in the analysis tag from the agent response will be stored here. This will not be shown in the constructed event history nor shown to the user.
    """
    
    def __init__(self, type, reasoning="", content="", title=None, message="", analysis="", est_input_token=0, est_output_token=0):
        self.type = type    
        self.reasoning = reasoning
        self.content = content
        self.title = title
        self.message = remove_ansi_escape_codes(message)
        self.analysis = analysis
        self.est_input_token = est_input_token
        self.est_output_token = est_output_token
        self.created_at = datetime.now()
    
    def __str__(self):
        parts = []
        parts.append(f"Type: {self.type}")
        if self.title:
            parts.append(f"Title: {self.title}")
        if self.reasoning:
            parts.append(f"Reasoning: {self.reasoning}")
        if self.content:
            parts.append(f"Content: {self.content}")
        if self.message:
            parts.append(f"Message: {self.message}")
        if self.analysis:
            parts.append(f"Analysis: {self.analysis}")
        parts.append(f"Created: {self.created_at}")
        return " | ".join(parts)
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Event):
            return False
        return (self.type == other.type and
                self.reasoning == other.reasoning and
                self.content == other.content and
                self.title == other.title and
                self.message == other.message and
                self.analysis == other.analysis and
                self.est_input_token == other.est_input_token and
                self.est_output_token == other.est_output_token)
    
    def to_dict(self):
        return {
            'type': self.type,
            'reasoning': self.reasoning,
            'content': self.content,
            'title': self.title,
            'message': self.message,
            'analysis': self.analysis,
            'est_input_token': self.est_input_token,
            'est_output_token': self.est_output_token,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        event = cls(
            type=data['type'],
            reasoning=data['reasoning'],
            content=data['content'],
            title=data['title'],
            message=data.get('message', ''),
            analysis=data.get('analysis', ''),
            est_input_token=data.get('est_input_token', 0),
            est_output_token=data.get('est_output_token', 0)
        )
        event.created_at = datetime.fromisoformat(data['created_at'])
        return event

class EventSummary:
    """Represents a summary of multiple events."""
    
    def __init__(self, type, start_event_idx, end_event_idx, summary):
        self.type = type
        self.start_event_idx = start_event_idx
        self.end_event_idx = end_event_idx
        self.summary = summary
        self.created_at = datetime.now()
    
    def __eq__(self, other):
        if not isinstance(other, EventSummary):
            return False
        return (self.type == other.type and
                self.start_event_idx == other.start_event_idx and
                self.end_event_idx == other.end_event_idx and
                self.summary == other.summary)
    
    def to_dict(self):
        return {
            'type': self.type,
            'start_event_idx': self.start_event_idx,
            'end_event_idx': self.end_event_idx,
            'summary': self.summary,
            'created_at': self.created_at.isoformat()
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data):
        summary = cls(
            type=data['type'],
            start_event_idx=data['start_event_idx'],
            end_event_idx=data['end_event_idx'],
            summary=data['summary']
        )
        summary.created_at = datetime.fromisoformat(data['created_at'])
        return summary

class EventStream:
    """Manages a sequence of events and their summaries."""
    
    def __init__(self, title=None, uid=None, parent_event_stream_uids=None, agent_type="", mcp_config=None):
        self.events_list = []
        self.event_summaries_list = []
        self.created_at = datetime.now()
        self.uid = uid if uid else "".join(random.choices(string.ascii_letters + string.digits, k=8))
        self.title = title if title else self.uid
        self.parent_event_stream_uids = parent_event_stream_uids if parent_event_stream_uids is not None else []
        self.agent_type = agent_type
        self.agent_settings = {}
        self.mcp_config = mcp_config or {}

    def update_settings(self, settings):
        """Update agent settings with new values"""
        self.agent_settings.update({
            k: v for k, v in settings.items()
            if k in ['cmd_init_dir', 'model', 'prefix_cmd', 'agent_type', 'notes']
        })

    def get_settings(self):
        """Return current agent settings"""
        return self.agent_settings.copy()

    def get_event_list_including_children_events(self, starting_from=0):
        final_flatten_event_list = []
        for i in range(starting_from, len(self.events_list)):
            event = self.events_list[i]
            final_flatten_event_list.append(event)
            if event.type in RETURN_TO_PARENT_EVENT_TYPES and self.parent_event_stream_uids:
                return final_flatten_event_list
            if event.type == "child_agent_running":
                try:
                    child_info = json.loads(event.reasoning)
                    child_agent_event_stream = read_event_stream(child_info["agent_id"])
                    child_events = child_agent_event_stream.get_event_list_including_children_events(child_info["starting_from"])
                    child_events_with_updated_type = []
                    for e in child_events:
                        if e.type in ["new_request", "follow_up_request"]:
                            e.type += "_from_parent"
                        child_events_with_updated_type.append(e)
                    final_flatten_event_list.extend(child_events_with_updated_type)
                except Exception as e:
                    logging.error("Error loading child event stream: %s", e)
        return final_flatten_event_list

    def get_all_children_event_stream_ids(self, starting_from=0):
        """Recursively collect all event stream IDs including children.
        
        Returns a list of unique event stream IDs, starting with the current stream ID
        and including all child event stream IDs found recursively.
        
        Args:
            starting_from (int): Index to start searching from in the events list
            
        Returns:
            list: List of unique event stream IDs
        """
        collected_ids = [self.uid]  # Start with current stream ID
        
        for i in range(starting_from, len(self.events_list)):
            event = self.events_list[i]
            
            # If we hit a return-to-parent event and we have parent streams, stop here
            if event.type in RETURN_TO_PARENT_EVENT_TYPES and self.parent_event_stream_uids:
                break
                
            # Look for child agent events
            if event.type == "child_agent_running":
                try:
                    child_info = json.loads(event.reasoning)
                    child_agent_event_stream = read_event_stream(child_info["agent_id"])
                    
                    if child_agent_event_stream:
                        # Recursively collect IDs from child stream
                        child_ids = child_agent_event_stream.get_all_children_event_stream_ids(child_info["starting_from"])
                        
                        # Add child IDs to our collection (avoiding duplicates)
                        for child_id in child_ids:
                            if child_id not in collected_ids:
                                collected_ids.append(child_id)
                                
                except Exception as e:
                    logging.error("Error loading child event stream for ID collection: %s", e)
                    # Continue processing other events even if one child fails
                    
        return collected_ids
    def add_event(self, event):
        self.events_list.append(event)
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def __str__(self):
        parts = []
        parts.append(f"Stream UID: {self.uid}")
        if self.parent_event_stream_uids:
            parts.append(f"Parent Stream UIDs: {', '.join(self.parent_event_stream_uids)}")
        if self.title:
            parts.append(f"Stream Title: {self.title}")
        if self.agent_type:
            parts.append(f"Agent Type: {self.agent_type}")
        parts.append(f"Created: {self.created_at}")
        parts.extend(str(event) for event in self.events_list)
        return "\n".join(parts)
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, EventStream):
            return False
        # Compare all fields except uid and created_at
        return (self.title == other.title and
                self.parent_event_stream_uids == other.parent_event_stream_uids and
                self.events_list == other.events_list and
                self.event_summaries_list == other.event_summaries_list and
                self.agent_type == other.agent_type and
                self.agent_settings == other.agent_settings)
    
    def to_dict(self):
        return {
            'events_list': [event.to_dict() for event in self.events_list],
            'event_summaries_list': [summary.to_dict() for summary in self.event_summaries_list],
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'uid': self.uid,
            'parent_event_stream_uids': self.parent_event_stream_uids,
            'agent_type': self.agent_type,
            'agent_settings': self.agent_settings,
            'mcp_config': self.mcp_config or {}
        }
    
    @classmethod
    def from_dict(cls, data):
        stream = cls(
            title=data['title'],
            uid=data['uid'],
            parent_event_stream_uids=data.get('parent_event_stream_uids', []),
            agent_type=data.get('agent_type', ''),
            mcp_config=data.get("mcp_config", {})
        )
        stream.created_at = datetime.fromisoformat(data['created_at'])
        stream.events_list = [Event.from_dict(event_data) for event_data in data['events_list']]
        stream.event_summaries_list = [EventSummary.from_dict(summary_data) for summary_data in data['event_summaries_list']]
        # Handle backwards compatibility for agent_settings
        if 'agent_settings' in data:
            stream.agent_settings = data['agent_settings']
        return stream
