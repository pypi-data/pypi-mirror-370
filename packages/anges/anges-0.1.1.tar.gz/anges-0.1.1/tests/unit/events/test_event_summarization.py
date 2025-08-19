import unittest
from unittest.mock import Mock
from anges.agents.agent_utils.event_methods import (
    DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS,
    get_task_completion_summary,
    get_aggregated_actions_summary,
    append_events_summary_if_needed,
)
from anges.agents.agent_utils.events import Event, EventSummary, EventStream

class TestEventSummarization(unittest.TestCase):
    def setUp(self):
        """Initialize mock inference function used across tests"""
        self.mock_inference = Mock()
        self.mock_inference.return_value = "Mock summary response"

    def test_get_task_completion_summary_empty_events(self):
        """Test that task completion summary handles empty event list gracefully"""
        event_stream = EventStream()
        summary = get_task_completion_summary(event_stream, self.mock_inference)
        self.assertEqual(summary, "Mock summary response")
        self.mock_inference.assert_called_once()

    def test_get_task_completion_summary(self):
        """Test task completion summary generation with typical event sequence"""
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="new_request", reasoning="", content="Initial request"),
            Event(type="action", reasoning="Some reason", content="Action content"),
            Event(type="task_completion", reasoning="Done", content="Task completed")
        ]
        summary = get_task_completion_summary(event_stream, self.mock_inference)
        self.assertEqual(summary, "Mock summary response")
        self.mock_inference.assert_called_once()

    def test_get_aggregated_actions_summary_empty_events(self):
        """Test that action aggregation handles empty event list gracefully"""
        event_stream = EventStream()
        summary = get_aggregated_actions_summary(event_stream, 1, self.mock_inference)
        self.assertEqual(summary, "Mock summary response")
        self.mock_inference.assert_called_once()

    def test_get_aggregated_actions_summary(self):
        """Test action aggregation summary for multiple actions"""
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="action", reasoning="R1", content="C1"),
            Event(type="action", reasoning="R2", content="C2")
        ]
        summary = get_aggregated_actions_summary(event_stream, 1, self.mock_inference)
        self.assertEqual(summary, "Mock summary response")
        self.mock_inference.assert_called_once()

    def test_append_events_summary_if_needed_task_completion(self):
        """Test summary generation triggered by task completion event"""
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="new_request", reasoning="", content="Request"),
            Event(type="action", reasoning="R1", content="C1"),
            Event(type="task_completion", reasoning="Done", content="Complete")
        ]
        
        append_events_summary_if_needed(event_stream, self.mock_inference, DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS, None)
        
        self.assertEqual(len(event_stream.event_summaries_list), 1)
        self.assertEqual(event_stream.event_summaries_list[0].type, "task_completion_summary")
        self.assertEqual(event_stream.event_summaries_list[0].start_event_idx, 1)
        self.assertEqual(event_stream.event_summaries_list[0].end_event_idx, 3)

    def test_append_events_summary_if_needed_many_actions(self):
        """Test summary generation triggered by exceeding action threshold"""
        event_stream = EventStream()
        # Create DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS + recent_content_not_truncating action events
        # recent_content_not_truncating defaults to 5 in config
        event_stream.events_list = [Event(type="action", reasoning=f"R{i}", content=f"C{i}") for i in range(DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS + 5)]
        
        append_events_summary_if_needed(event_stream, self.mock_inference, DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS, None)
        
        self.assertEqual(len(event_stream.event_summaries_list), 1)
        self.assertEqual(event_stream.event_summaries_list[0].type, "actions_aggregation")
        self.assertEqual(event_stream.event_summaries_list[0].start_event_idx, 1)
        self.assertEqual(event_stream.event_summaries_list[0].end_event_idx, DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS)

    def test_append_events_summary_if_needed_no_summary_needed(self):
        """Test that no summary is generated when conditions aren't met"""
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="action", reasoning="R1", content="C1"),
            Event(type="action", reasoning="R2", content="C2")
        ]
        
        append_events_summary_if_needed(event_stream, self.mock_inference, DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS, None)
        
        self.assertEqual(len(event_stream.event_summaries_list), 0)

    def test_invalid_event_type(self):
        """Test handling of invalid event types in event stream"""
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="invalid_type", reasoning="R1", content="C1"),
            Event(type="another_invalid", reasoning="R2", content="C2")
        ]
        
        append_events_summary_if_needed(event_stream, self.mock_inference, DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS, None)
        self.assertEqual(len(event_stream.event_summaries_list), 0)

    def test_multiple_summaries_generation(self):
        """Test generation of multiple summaries in same event stream"""
        event_stream = EventStream()
        # First set of events leading to action summary
        # Need DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS + recent_content_not_truncating events
        event_stream.events_list = [Event(type="action", reasoning=f"R{i}", content=f"C{i}") for i in range(DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS + 5)]
        append_events_summary_if_needed(event_stream, self.mock_inference, DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS, None)
        
        # Add task completion events
        event_stream.events_list.extend([
            Event(type="action", reasoning="Final", content="Last action"),
            Event(type="task_completion", reasoning="Done", content="Complete")
        ])
        append_events_summary_if_needed(event_stream, self.mock_inference, DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS, None)
        
        self.assertEqual(len(event_stream.event_summaries_list), 2)
        self.assertEqual(event_stream.event_summaries_list[0].type, "actions_aggregation")
        self.assertEqual(event_stream.event_summaries_list[1].type, "task_completion_summary")

    def test_mixed_event_types(self):
        """Test handling of mixed event types in sequence"""
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="new_request", reasoning="", content="Start"),
            Event(type="action", reasoning="R1", content="C1"),
            Event(type="invalid_type", reasoning="X", content="Invalid"),
            Event(type="action", reasoning="R2", content="C2"),
            Event(type="task_completion", reasoning="Done", content="Complete")
        ]
        
        append_events_summary_if_needed(event_stream, self.mock_inference, DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS, None)
        self.assertEqual(len(event_stream.event_summaries_list), 1)
        self.assertEqual(event_stream.event_summaries_list[0].type, "task_completion_summary")

if __name__ == '__main__':
    unittest.main()
