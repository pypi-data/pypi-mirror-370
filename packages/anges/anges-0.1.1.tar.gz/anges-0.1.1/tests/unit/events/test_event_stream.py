import unittest
from anges.agents.agent_utils.events import Event, EventSummary, EventStream
from anges.agents.agent_utils.event_methods import construct_events_str_with_summary
from datetime import datetime

class TestEventSummaryCode(unittest.TestCase):
    def test_event_initialization(self):
        event = Event(type="test_type", reasoning="Test reason", content="Event content")
        self.assertEqual(event.type, "test_type")
        self.assertEqual(event.reasoning, "Test reason")
        self.assertEqual(event.content, "Event content")
        self.assertIsNone(event.title)
        self.assertIsInstance(event.created_at, datetime)

    def test_event_initialization_with_title(self):
        event = Event(type="test_type", reasoning="Test reason", content="Event content", title="Test Title")
        self.assertEqual(event.title, "Test Title")
        self.assertIsInstance(event.created_at, datetime)

    def test_event_stream_initialization(self):
        event_stream = EventStream()
        self.assertEqual(len(event_stream.events_list), 0)
        self.assertEqual(len(event_stream.event_summaries_list), 0)
        self.assertEqual(event_stream.title, event_stream.uid)  # Title should be set to uid when not provided
        self.assertIsInstance(event_stream.created_at, datetime)
        self.assertIsNotNone(event_stream.uid)
        self.assertEqual(len(event_stream.uid), 8)
        self.assertEqual(event_stream.parent_event_stream_uids, [])
        self.assertIsNotNone(event_stream.uid)
        self.assertEqual(len(event_stream.uid), 8)
        self.assertEqual(event_stream.parent_event_stream_uids, [])

    def test_event_stream_initialization_with_title(self):
        event_stream = EventStream(title="Test Stream")
        self.assertEqual(event_stream.title, "Test Stream")
        self.assertIsInstance(event_stream.created_at, datetime)
        self.assertIsNotNone(event_stream.uid)
        self.assertEqual(len(event_stream.uid), 8)
    def test_event_stream_initialization_with_custom_uid(self):
        custom_uid = "CUSTOM123"
        event_stream = EventStream(uid=custom_uid)
        self.assertEqual(event_stream.uid, custom_uid)
        self.assertEqual(event_stream.parent_event_stream_uids, [])

    def test_event_stream_initialization_with_agent_type(self):
        event_stream = EventStream(agent_type="test_agent")
        self.assertEqual(event_stream.agent_type, "test_agent")
        self.assertEqual(len(event_stream.events_list), 0)
        self.assertEqual(len(event_stream.event_summaries_list), 0)

    def test_event_stream_string_representation_with_agent_type(self):
        event_stream = EventStream(
            title="Test Stream",
            uid="TEST1234",
            agent_type="test_agent"
        )
        str_rep = str(event_stream)
        self.assertIn("Agent Type: test_agent", str_rep)

    def test_agent_settings_initialization(self):
        """Test that agent settings are initialized as empty dictionary"""
        event_stream = EventStream()
        expected_settings = {}
        self.assertEqual(event_stream.agent_settings, expected_settings)

    def test_update_settings(self):
        """Test that settings can be updated with valid keys"""
        event_stream = EventStream()
        new_settings = {
            'cmd_init_dir': '/tmp',
            'model': 'gpt4',
            'prefix_cmd': 'sudo',
            'agent_type': 'custom',
            'invalid_key': 'should_not_be_added'
        }
        event_stream.update_settings(new_settings)
        
    def test_get_settings(self):
        """Test that settings can be retrieved and are properly copied"""
        event_stream = EventStream()
        
        # First set a test setting
        event_stream.agent_settings['test_key'] = 'test_value'
        
        # Get settings copy
        settings = event_stream.get_settings()
        
        # Verify it's a copy by modifying the returned dict
        settings['test_key'] = 'modified'
        self.assertEqual(event_stream.agent_settings['test_key'], 'test_value')
        self.assertEqual(settings['test_key'], 'modified')


    def test_settings_persistence(self):
        """Test that settings are properly serialized and deserialized"""
        event_stream = EventStream()
        new_settings = {
            'cmd_init_dir': '/custom',
            'model': 'custom_model'
        }
        event_stream.update_settings(new_settings)
        
        # Serialize and deserialize
        serialized = event_stream.to_dict()
        deserialized = EventStream.from_dict(serialized)
        
        # Verify settings were preserved
        self.assertEqual(deserialized.agent_settings['cmd_init_dir'], '/custom')
        self.assertEqual(deserialized.agent_settings['model'], 'custom_model')
        # Create streams with fixed UIDs to avoid random generation
        stream1 = EventStream(agent_type="test_agent", uid="TEST123", title="TestStream")
        stream2 = EventStream(agent_type="test_agent", uid="TEST456", title="TestStream")  # Different UID shouldn't affect equality
        stream3 = EventStream(agent_type="different_agent", uid="TEST789", title="TestStream")

        # Test equality based on agent_type and other attributes, not UID
        self.assertEqual(stream1, stream2)  # Should be equal despite different UIDs
        self.assertNotEqual(stream1, stream3)  # Different agent_type should make them unequal
        self.assertIsNotNone(event_stream.uid)

    def test_event_stream_string_representation(self):
        event_stream = EventStream(
            title="Test Stream",
            uid="TEST1234",
            parent_event_stream_uids=["PARENT99", "PARENT88"]
        )
        str_rep = str(event_stream)
        self.assertIn("Stream UID: TEST1234", str_rep)
        self.assertIn("Parent Stream UIDs: PARENT99, PARENT88", str_rep)
        self.assertIn("Stream Title: Test Stream", str_rep)
        self.assertIn("Created:", str_rep)

    def test_construct_events_str_with_summary_no_summary(self):
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="action", reasoning="Reason 1", content="Content 1"),
            Event(type="action", reasoning="Reason 2", content="Content 2"),
        ]
        result = construct_events_str_with_summary(event_stream)
        expected = (
            "\n## Event 1 TYPE: ACTION\n"
            "REASONING:\nReason 1\n"
            "CONTENT:\nContent 1\n"
            "\n## Event 2 TYPE: ACTION\n"
            "REASONING:\nReason 2\n"
            "CONTENT:\nContent 2\n"
        )
        self.assertEqual(result, expected)

    def test_construct_events_str_with_summary_with_summary(self):
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="action", reasoning="Reason 1", content="Content 1"),
            Event(type="action", reasoning="Reason 2", content="Content 2"),
            Event(type="action", reasoning="Reason 3", content="Content 3"),
            Event(type="action", reasoning="Reason 4", content="Content 4"),
        ]
        event_stream.event_summaries_list = [
            EventSummary("action_summary", start_event_idx=2, end_event_idx=3, summary="Summary of events 2 to 3."),
        ]
        result = construct_events_str_with_summary(event_stream)
        expected = (
            "\n## Event 1 TYPE: ACTION\n"
            "REASONING:\nReason 1\n"
            "CONTENT:\nContent 1\n"
            "\n## Summary of Events 2 to 3\n"
            "Summary of events 2 to 3.\n"
            "\n## Event 4 TYPE: ACTION\n"
            "REASONING:\nReason 4\n"
            "CONTENT:\nContent 4\n"
        )
        self.assertEqual(result, expected)

    def test_construct_events_str_with_multiple_summaries(self):
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="action", reasoning="Reason 1", content="Content 1"),
            Event(type="action", reasoning="Reason 2", content="Content 2"),
            Event(type="action", reasoning="Reason 3", content="Content 3"),
            Event(type="action", reasoning="Reason 4", content="Content 4"),
            Event(type="action", reasoning="Reason 5", content="Content 5"),
        ]
        event_stream.event_summaries_list = [
            EventSummary("action_summary", start_event_idx=2, end_event_idx=3, summary="Summary of events 2 to 3."),
            EventSummary("action_summary", start_event_idx=4, end_event_idx=5, summary="Summary of events 4 to 5."),
        ]
        result = construct_events_str_with_summary(event_stream)
        expected = (
            "\n## Event 1 TYPE: ACTION\n"
            "REASONING:\nReason 1\n"
            "CONTENT:\nContent 1\n"
            "\n## Summary of Events 2 to 3\n"
            "Summary of events 2 to 3.\n"
            "\n## Summary of Events 4 to 5\n"
            "Summary of events 4 to 5.\n"
        )
        self.assertEqual(result, expected)

    def test_construct_events_str_with_more_than_ten_events(self):
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="action", reasoning=f"Reason {i}", content=f"Content {i}") for i in range(1, 12)
        ]
        result = construct_events_str_with_summary(event_stream)
        expected = ""
        for i in range(1, 12):
            expected += (
                f"\n## Event {i} TYPE: ACTION\n"
                f"REASONING:\nReason {i}\n"
                f"CONTENT:\nContent {i}\n"
            )
        self.assertEqual(result, expected)

    def test_construct_events_str_with_summary_covering_all_events(self):
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="action", reasoning=f"Reason {i}", content=f"Content {i}") for i in range(1, 6)
        ]
        event_stream.event_summaries_list = [
            EventSummary("action_summary", start_event_idx=1, end_event_idx=5, summary="Summary of all events."),
        ]
        result = construct_events_str_with_summary(event_stream)
        expected = (
            "\n## Summary of Events 1 to 5\n"
            "Summary of all events.\n"
        )
        self.assertEqual(result, expected)

    def test_construct_events_str_with_varied_summary_lengths(self):
        event_stream = EventStream()
        event_stream.events_list = [
            Event(type="action", reasoning=f"Reason {i}", content=f"Content {i}") for i in range(1, 11)
        ]
        event_stream.event_summaries_list = [
            EventSummary("action_summary", start_event_idx=2, end_event_idx=4, summary="Summary of events 2 to 4."),
            EventSummary("action_summary", start_event_idx=7, end_event_idx=8, summary="Summary of events 7 to 8."),
        ]
        result = construct_events_str_with_summary(event_stream)
        expected = (
            "\n## Event 1 TYPE: ACTION\n"
            "REASONING:\nReason 1\n"
            "CONTENT:\nContent 1\n"
            "\n## Summary of Events 2 to 4\n"
            "Summary of events 2 to 4.\n"
            "\n## Event 5 TYPE: ACTION\n"
            "REASONING:\nReason 5\n"
            "CONTENT:\nContent 5\n"
            "\n## Event 6 TYPE: ACTION\n"
            "REASONING:\nReason 6\n"
            "CONTENT:\nContent 6\n"
            "\n## Summary of Events 7 to 8\n"
            "Summary of events 7 to 8.\n"
            "\n## Event 9 TYPE: ACTION\n"
            "REASONING:\nReason 9\n"
            "CONTENT:\nContent 9\n"
            "\n## Event 10 TYPE: ACTION\n"
            "REASONING:\nReason 10\n"
            "CONTENT:\nContent 10\n"
        )
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
