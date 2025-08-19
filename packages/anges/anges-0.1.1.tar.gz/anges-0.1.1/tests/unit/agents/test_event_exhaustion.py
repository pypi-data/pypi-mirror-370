"""
Unit tests for the improved event exhaustion logic.

Tests the new behavior where max_number_of_events_to_exhaust counts events
only from the most recent user input (new_request or follow_up_request).
"""

import pytest
from unittest.mock import MagicMock, patch
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.events import Event, EventStream
from anges.agents.agent_utils.agent_factory import AgentConfig


class TestEventExhaustion:
    """Test class for event exhaustion logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a minimal agent instance for testing
        self.agent = BaseAgent.__new__(BaseAgent)
        
        # Mock agent config
        self.mock_agent_config = MagicMock()
        self.mock_agent_config.max_number_of_events_to_exhaust = 5
        self.agent.agent_config = self.mock_agent_config
        
        # Mock required attributes for testing
        self.agent.message_handlers = []
        
    def test_count_events_since_last_user_input_with_new_request(self):
        """Test counting events from the most recent new_request."""
        events_list = [
            Event(type="system", content="System start"),
            Event(type="new_request", content="First request"),
            Event(type="action", content="Action 1"),
            Event(type="action", content="Action 2"),
            Event(type="new_request", content="Second request"),  # Most recent
            Event(type="action", content="Action 3"),
            Event(type="action", content="Action 4"),
        ]
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        # Should count from the second new_request onwards: new_request + 2 actions = 3
        assert count == 3
        
    def test_count_events_since_last_user_input_with_follow_up_request(self):
        """Test counting events from the most recent follow_up_request."""
        events_list = [
            Event(type="new_request", content="Initial request"),
            Event(type="action", content="Action 1"),
            Event(type="follow_up_request", content="Follow up"),  # Most recent
            Event(type="action", content="Action 2"),
            Event(type="action", content="Action 3"),
        ]
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        # Should count from follow_up_request onwards: follow_up_request + 2 actions = 3
        assert count == 3
        
    def test_count_events_since_last_user_input_mixed_user_inputs(self):
        """Test with mixed new_request and follow_up_request events."""
        events_list = [
            Event(type="new_request", content="First request"),
            Event(type="action", content="Action 1"),
            Event(type="follow_up_request", content="Follow up"),
            Event(type="action", content="Action 2"),
            Event(type="new_request", content="Another request"),  # Most recent
            Event(type="action", content="Action 3"),
        ]
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        # Should count from the last new_request onwards: new_request + 1 action = 2
        assert count == 2
        
    def test_count_events_since_last_user_input_no_user_input(self):
        """Test fallback behavior when no user input events exist."""
        events_list = [
            Event(type="system", content="System event"),
            Event(type="action", content="Action 1"),
            Event(type="action", content="Action 2"),
        ]
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        # Should fall back to counting all events
        assert count == 3
        
    def test_count_events_since_last_user_input_empty_list(self):
        """Test with empty events list."""
        events_list = []
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        assert count == 0
        
    def test_count_events_since_last_user_input_only_user_input(self):
        """Test with only a user input event."""
        events_list = [
            Event(type="new_request", content="Only request"),
        ]
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        # Should count the user input event itself
        assert count == 1
        
    def test_count_events_since_last_user_input_user_input_at_end(self):
        """Test when user input is the last event."""
        events_list = [
            Event(type="action", content="Action 1"),
            Event(type="action", content="Action 2"),
            Event(type="new_request", content="Last request"),  # At the end
        ]
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        # Should count only the last event
        assert count == 1
        
    def test_check_exhausted_not_exhausted(self):
        """Test _check_exhausted when events are below the limit."""
        event_stream = EventStream()
        # Add 4 events (below limit of 5)
        event_stream.events_list = [
            Event(type="new_request", content="Request"),
            Event(type="action", content="Action 1"),
            Event(type="action", content="Action 2"),
            Event(type="action", content="Action 3"),
        ]
        
        run_config = {
            'agent_config': self.mock_agent_config,
            'event_stream': event_stream,
            'inference_func': MagicMock(),
        }
        
        result = self.agent._check_exhausted(run_config)
        
        # Should not be exhausted
        assert result is None
        
    @patch('anges.agents.agent_utils.base_agent.append_events_summary_if_needed')
    @patch('anges.agents.agent_utils.base_agent.save_event_stream')
    def test_check_exhausted_is_exhausted(self, mock_save, mock_summary):
        """Test _check_exhausted when events exceed the limit."""
        # Mock the agent_message_base attribute
        self.agent.agent_message_base = "Test Agent"
        
        event_stream = EventStream()
        # Add 5 events (at the limit of 5)
        event_stream.events_list = [
            Event(type="new_request", content="Request"),
            Event(type="action", content="Action 1"),
            Event(type="action", content="Action 2"),
            Event(type="action", content="Action 3"),
            Event(type="action", content="Action 4"),
        ]
        
        # Mock the summary to avoid dependency on actual summarization
        event_stream.event_summaries_list = [MagicMock(summary="Test summary")]
        
        run_config = {
            'agent_config': self.mock_agent_config,
            'event_stream': event_stream,
            'inference_func': MagicMock(),
        }
        
        result = self.agent._check_exhausted(run_config)
        
        # Should be exhausted and return the event stream
        assert result == event_stream
        
        # Should have added a task_interrupted event
        assert len(event_stream.events_list) == 6  # Original 5 + 1 interruption
        assert event_stream.events_list[-1].type == "task_interrupted"
        
        # Should have called summary and save functions
        mock_summary.assert_called_once()
        assert mock_save.called, "save_event_stream should be called"
        # Check that event_stream was saved (may be called multiple times due to summarization)
        assert any(call[0][0] == event_stream for call in mock_save.call_args_list)
        
    @patch('anges.agents.agent_utils.base_agent.append_events_summary_if_needed')
    @patch('anges.agents.agent_utils.base_agent.save_event_stream')
    def test_check_exhausted_with_multiple_user_inputs(self, mock_save, mock_summary):
        """Test exhaustion counting with multiple user inputs."""
        self.agent.agent_message_base = "Test Agent"
        
        event_stream = EventStream()
        # Add events with multiple user inputs - only count from the last one
        event_stream.events_list = [
            Event(type="new_request", content="First request"),
            Event(type="action", content="Action 1"),
            Event(type="action", content="Action 2"),
            Event(type="action", content="Action 3"),
            Event(type="action", content="Action 4"),
            Event(type="new_request", content="Second request"),  # Reset point
            Event(type="action", content="Action 5"),
            Event(type="action", content="Action 6"),
            Event(type="action", content="Action 7"),
            # Only 4 events since last user input (new_request + 3 actions)
        ]
        
        event_stream.event_summaries_list = [MagicMock(summary="Test summary")]
        
        run_config = {
            'agent_config': self.mock_agent_config,
            'event_stream': event_stream,
            'inference_func': MagicMock(),
        }
        
        result = self.agent._check_exhausted(run_config)
        
        # Should NOT be exhausted because only 4 events since last user input
        assert result is None
        
        # Should not have called summary or save functions
        mock_summary.assert_not_called()
        mock_save.assert_not_called()
        
    def test_exhausted_message_format(self):
        """Test the format of the exhaustion message."""
        self.agent.agent_message_base = "Test Agent"
        
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="new_request", content="Request"),
            Event(type="action", content="Action 1"),
            Event(type="action", content="Action 2"),
            Event(type="action", content="Action 3"),
            Event(type="action", content="Action 4"),
        ]
        
        # Mock the summary
        mock_summary = MagicMock()
        mock_summary.summary = "Mock progress summary"
        event_stream.event_summaries_list = [mock_summary]
        
        run_config = {
            'agent_config': self.mock_agent_config,
            'event_stream': event_stream,
            'inference_func': MagicMock(),
        }
        
        with patch('anges.agents.agent_utils.base_agent.append_events_summary_if_needed'), \
             patch('anges.agents.agent_utils.base_agent.save_event_stream'):
            
            result = self.agent._check_exhausted(run_config)
            
            # Check the interruption event message format
            interruption_event = result.events_list[-1]
            expected_msg_parts = [
                "Test Agent",
                "exhausted the maximum number of events",
                "(5/5)",  # events_since_last_user_input/max_number_of_events_to_exhaust
                "since the last user input",
                "Mock progress summary"
            ]
            
            for part in expected_msg_parts:
                assert part in interruption_event.message
                assert part in interruption_event.content
                
    def test_integration_below_limit(self):
        """Test with events below the limit."""
        self._test_integration_case(limit=3, event_count=2, should_exhaust=False)
        
    def test_integration_at_limit(self):
        """Test with events at the limit."""
        self._test_integration_case(limit=3, event_count=3, should_exhaust=True)
        
    def test_integration_higher_limit_below(self):
        """Test with higher limit, events below."""
        self._test_integration_case(limit=10, event_count=5, should_exhaust=False)
        
    def test_integration_higher_limit_at_limit(self):
        """Test with higher limit, events at limit."""
        self._test_integration_case(limit=10, event_count=10, should_exhaust=True)
        
    def test_count_events_multiple_consecutive_user_inputs(self):
        """Test counting with multiple consecutive user inputs."""
        events_list = [
            Event(type="action", content="Action before"),
            Event(type="new_request", content="First request"),
            Event(type="follow_up_request", content="Immediate follow up"),  # Most recent
            Event(type="action", content="Action after"),
        ]
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        # Should count from the follow_up_request onwards: follow_up + 1 action = 2
        assert count == 2
        
    def test_count_events_large_conversation(self):
        """Test counting in a large conversation with multiple user interactions."""
        events_list = []
        
        # First conversation
        events_list.extend([
            Event(type="new_request", content="First request"),
            *[Event(type="action", content=f"Action {i}") for i in range(1, 21)],  # 20 actions
        ])
        
        # Second conversation  
        events_list.extend([
            Event(type="follow_up_request", content="Follow up"),
            *[Event(type="action", content=f"Follow action {i}") for i in range(1, 16)],  # 15 actions
        ])
        
        # Third conversation (most recent)
        events_list.extend([
            Event(type="new_request", content="Latest request"),
            *[Event(type="action", content=f"Latest action {i}") for i in range(1, 6)],  # 5 actions
        ])
        
        count = self.agent._count_events_since_last_user_input(events_list)
        
        # Total events: 1 + 20 + 1 + 15 + 1 + 5 = 43
        # Events since last user input: 1 + 5 = 6
        assert len(events_list) == 43
        assert count == 6
        
    def test_exhaustion_with_edge_case_limits(self):
        """Test exhaustion behavior with edge case limits."""
        # Test with limit = 1 (should exhaust immediately after user input)
        mock_config = MagicMock()
        mock_config.max_number_of_events_to_exhaust = 1
        self.agent.agent_message_base = "Test Agent"
        
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="new_request", content="Request"),  # This alone should trigger exhaustion
        ]
        event_stream.event_summaries_list = [MagicMock(summary="Summary")]
        
        run_config = {
            'agent_config': mock_config,
            'event_stream': event_stream,
            'inference_func': MagicMock(),
        }
        
        with patch('anges.agents.agent_utils.base_agent.append_events_summary_if_needed'), \
             patch('anges.agents.agent_utils.base_agent.save_event_stream'):
            
            result = self.agent._check_exhausted(run_config)
            
            # Should be exhausted with just the user input event
            assert result is not None
            assert result.events_list[-1].type == "task_interrupted"
        
    def _test_integration_case(self, limit, event_count, should_exhaust):
        """Helper method for integration testing."""
        # Set up fresh agent config for each test
        mock_config = MagicMock()
        mock_config.max_number_of_events_to_exhaust = limit
        
        event_stream = EventStream()
        # Create events: 1 user request + (event_count-1) actions
        event_stream.events_list = [Event(type="new_request", content="Request")]
        for i in range(event_count - 1):
            event_stream.events_list.append(Event(type="action", content=f"Action {i+1}"))
        
        if should_exhaust:
            event_stream.event_summaries_list = [MagicMock(summary="Summary")]
            self.agent.agent_message_base = "Test Agent"
        
        run_config = {
            'agent_config': mock_config,
            'event_stream': event_stream,
            'inference_func': MagicMock(),
        }
        
        with patch('anges.agents.agent_utils.base_agent.append_events_summary_if_needed'), \
             patch('anges.agents.agent_utils.base_agent.save_event_stream'):
            
            result = self.agent._check_exhausted(run_config)
            
            if should_exhaust:
                assert result is not None, f"Should be exhausted with limit={limit}, events={event_count}"
                assert result.events_list[-1].type == "task_interrupted"
            else:
                assert result is None, f"Should not be exhausted with limit={limit}, events={event_count}"
