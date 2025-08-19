"""
Event Methods Module

This module contains utility functions for event management, including event
formatting, summarization, and stream construction. These functions work with
the Event, EventSummary, and EventStream classes to provide comprehensive
event handling capabilities.
"""
DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS = 30

import logging
from .events import Event, EventSummary, EventStream
from ...config import config

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARNING)

SUMMARIZE_TASK_COMPLETION_EVENTS_REQUEST = """
Now summarize the events for the most recent one new request that was just completed, and all previous events and tasks. including:
- SUMMARY_OF_PREVIOUS_TASKS_AND_RESULTS
- LAST_TASK_REQUEST
- KEY_STEPS_AND_ACTIONS
- FILES_UPDATED
- FINAL_RESULTS_AND_VERIFICATION

Output the plain text only, do not use any START/END key words.
"""

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARNING)

SUMMARIZE_TASK_COMPLETION_EVENTS_REQUEST = """
Now summarize the events for the most recent one new request that was just completed, and all previous events and tasks. including:
- SUMMARY_OF_PREVIOUS_TASKS_AND_RESULTS
- LAST_TASK_REQUEST
- KEY_STEPS_AND_ACTIONS
- FILES_UPDATED
- FINAL_RESULTS_AND_VERIFICATION

Output the plain text only, do not use any START/END key words.
"""

SUMMARIZE_ACTION_EVENTS_REQUEST = """
Now summarize action events from the Event PLACEHOLDER_START_INDEX to the most recent action Event. You should include:
- THE_REQUEST_BEING_ASKED
- GOALS_OF_THE_ACTIONS
- OVERALL_ACTIONS_DONE
- THINGS_THAT_WORKED
- THINGS_THAT_DID_NOT_WORK
- SUGGESTED_NEXT_STEP_ACTIONS (ONLY to finish the current request)

Output the plain text only, do not use any START/END key words.
"""

def construct_events_str(events, start=1):
    """
    Constructs a formatted string representation of events.
    
    Args:
        events (list[Event]): List of events to format
        start (int, optional): Starting index for event numbering. Defaults to 1
    
    Returns:
        str: Formatted string containing all events
    """
    previous_events = ""
    for idx, event in enumerate(events, start=start):
        previous_events += f"\n## Event {idx} TYPE: {event.type.upper()}\n"
        if event.reasoning:
            previous_events += f"REASONING:\n{event.reasoning}\n"
        previous_events += f"CONTENT:\n{event.content}\n"
    return previous_events


def construct_events_str_with_summary(event_stream, start=1, max_content_lines_override=None, recent_content_not_truncating_override=None, agent_config=None):
    """
    Constructs a formatted string representation of events with summaries.
    
    Args:
        event_stream (EventStream): The event stream to format
        start (int, optional): Starting index for event numbering. Defaults to 1
    
    Returns:
        str: Formatted string containing events and their summaries
    """
    return construct_events_str_with_events_and_summary(
        event_stream.events_list, event_stream.event_summaries_list, start, max_content_lines_override, recent_content_not_truncating_override, agent_config
    )

def construct_events_str_with_events_and_summary(event_list, summary_list, start=1, max_content_lines_override=None, recent_content_not_truncating_override=None, agent_config=None):
    """
    Constructs a formatted string representation of events and summaries.

    Args:
        event_list (list[Event]): List of events
        summary_list (list[EventSummary]): List of event summaries
        start (int, optional): Starting index for event numbering. Defaults to 1

    Returns:
        str: Formatted string containing events and summaries
    """
    previous_events = ""
    summary_indices = set()
    total_events = len(event_list) + start
    
    for summary in summary_list:
        summary_indices.update(
            range(summary.start_event_idx, summary.end_event_idx + 1)
        )

    idx = start
    while idx < total_events:
        if idx in summary_indices:
            for summary in summary_list:
                if summary.start_event_idx <= idx <= summary.end_event_idx:
                    previous_events += f"\n## Summary of Events {summary.start_event_idx} to {summary.end_event_idx}\n{summary.summary}\n"
                    idx = summary.end_event_idx + 1
                    break
        else:
            event = event_list[idx - start]
            previous_events += f"\n## Event {idx} TYPE: {event.type.upper()}\n"
            if event.reasoning:
                previous_events += f"REASONING:\n{event.reasoning}\n"
            # Get content lines
            content_lines = event.content.splitlines()
            try:
                recent_content_not_truncating = agent_config.recent_content_not_truncating
            except:
                recent_content_not_truncating = config.general_config.recent_content_not_truncating
            if recent_content_not_truncating_override:
                recent_content_not_truncating = recent_content_not_truncating_override
            max_content_lines = config.general_config.max_consecutive_content_lines
            if max_content_lines_override:
                max_content_lines = max_content_lines_override

            # For recent recent_content_not_truncating events, show full content
            if idx >= total_events - recent_content_not_truncating:
                previous_events += f"CONTENT:\n{event.content}\n"
            else:
                # For older events, show first max_content_lines lines + omitted count
                if len(content_lines) > max_content_lines:
                    truncated_content = '\n'.join(content_lines[:max_content_lines])
                    omitted_lines = len(content_lines) - max_content_lines
                    previous_events += f"CONTENT:\n{truncated_content}\n...{omitted_lines} lines omitted...\n"
                else:
                    previous_events += f"CONTENT:\n{event.content}\n"
            idx += 1
    return previous_events


def construct_prompt_for_event_stream(event_stream, prompt_template=None, max_content_lines_override=None, recent_content_not_truncating_override=None, agent_config=None):
    """
    Constructs a prompt string from an event stream.
    
    Args:
        event_stream (EventStream): The event stream to create a prompt from
    
    Returns:
        str: Formatted prompt string
    """
    if not prompt_template:
        raise ValueError("Prompt template must be provided")
    event_stream_string = construct_events_str_with_summary(event_stream, max_content_lines_override=max_content_lines_override, recent_content_not_truncating_override=recent_content_not_truncating_override, agent_config=agent_config)
    
    prompt = prompt_template.replace(
        "PLACEHOLDER_EVENT_STREAM", event_stream_string
    )

    if event_stream.events_list and event_stream.events_list[-1].type == "edit_file":
        prompt = prompt + "\n<!!The last event was a file editing operation. So you should start the analysis with double-checking the edited file content in the diff format. Make sure that no lines are removed unexpected, no deplicated lines etc. If the diff content seems wrong, continue to edit the file to fix it.>\n"

    return prompt


def get_task_completion_summary(event_stream, inference_func):
    """
    Generates a summary for completed tasks in the event stream.
    
    Args:
        event_stream (EventStream): The event stream to summarize
        inference_func (callable): Function to use for generating the summary
    
    Returns:
        str: Generated summary text
    """
    events_copy = event_stream.events_list.copy()
    events_copy.append(
        Event(
            type="new_request",
            reasoning="",
            content=SUMMARIZE_TASK_COMPLETION_EVENTS_REQUEST,
        )
    )
    prompt = construct_events_str_with_events_and_summary(
        events_copy, event_stream.event_summaries_list
    )
    try:
        response = inference_func(prompt)
        if not response:
            logger.warning("Empty response from inference function during task completion summary")
            return None
        return response
    except Exception as e:
        logger.debug(f"Error getting task completion summary: {e}")
        # For testing scenarios with limited mock responses, return None
def get_aggregated_actions_summary(event_stream, start_event_idx, inference_func):
    """
    Generates a summary for a sequence of action events.

    Args:
        event_stream (EventStream): The event stream to summarize
        start_event_idx (int): Starting event index for the summary
        inference_func (callable): Function to use for generating the summary

    Returns:
        str: Generated summary text
    """
    events_copy = event_stream.events_list.copy()
    summarizing_request = SUMMARIZE_ACTION_EVENTS_REQUEST.replace(
        "PLACEHOLDER_START_INDEX", str(start_event_idx)
    )
    events_copy.append(
        Event(type="new_request", reasoning="", content=summarizing_request)
    )
    prompt = construct_events_str_with_events_and_summary(
        events_copy, event_stream.event_summaries_list
    )
    logger.debug(f"Actions Summary Prompt: {prompt}")
    try:
        response = inference_func(prompt)
        if not response:
            logger.warning("Empty response from inference function during action summary")
            return None
        logger.debug(f"Actions Summary Response: {response}")
        return response
    except Exception as e:
        logger.debug(f"Error getting action summary: {e}")
        return None


def append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, agent_config=None):
    """
    Checks and appends summaries to the event stream if needed.

    This function determines if new summaries should be generated based on
    certain conditions (task completion or number of consecutive actions)
    and appends them to the event stream.

    Args:
        event_stream (EventStream): The event stream to check and update
        inference_func (callable): Function to use for generating summaries
        max_consecutive_actions_to_summarize (int): Maximum number of consecutive actions before summarization
        agent_config (optional): Agent configuration containing recent_content_not_truncating
    """
    if not max_consecutive_actions_to_summarize:
        max_consecutive_actions_to_summarize = DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS
    
    # Get recent_content_not_truncating value
    try:
        recent_content_not_truncating = agent_config.recent_content_not_truncating if agent_config else config.general_config.recent_content_not_truncating
    except:
        recent_content_not_truncating = config.general_config.recent_content_not_truncating
    
    logger.debug("Checking if summarization is needed ...")
    events = event_stream.events_list
    if not events:
        return

    # Append a Task Completion summary if the latest event is task_completion
    if events[-1].type == "task_completion":
        logger.debug("Summarization is needed for task completion ...")
        start_event_idx = (
            max(
                [idx for idx, e in enumerate(events) if e.type == "new_request"],
                default=-1,
            )
            + 1
        )
        end_event_idx = len(events)
        task_completion_summary = get_task_completion_summary(
            event_stream, inference_func
        )
        if task_completion_summary:  # Only append if we got a valid summary
            event_stream.event_summaries_list.append(
                EventSummary(
                    "task_completion_summary",
                    start_event_idx,
                    end_event_idx,
                    task_completion_summary,
                )
            )
        return

    # Append an actions aggregation summary if there are too many consecutive unsummarized actions
    consecutive_action_events = []
    for idx, event in enumerate(events):
        if event.type not in ["new_request", "task_completion"] and not any(
            summary.start_event_idx <= idx + 1 <= summary.end_event_idx
            for summary in event_stream.event_summaries_list
        ):
            consecutive_action_events.append(idx)
        else:
            consecutive_action_events = []

        # Check if we have enough events to trigger summarization considering recent_content_not_truncating
        if len(consecutive_action_events) >= max_consecutive_actions_to_summarize + recent_content_not_truncating:
            logger.debug("Summarization is needed for action aggregation ...")
            start_event_idx = max(consecutive_action_events[0] + 1, 0)
            # End at the point that leaves recent_content_not_truncating events unsummarized
            # Original logic: consecutive_action_events[-1] + 1 (summarize all)
            # New logic: consecutive_action_events[-(recent_content_not_truncating+1)] + 1 (leave recent events)
            end_event_idx = min(consecutive_action_events[-(recent_content_not_truncating+1)] + 1, len(events))
            actions_aggregation_summary = get_aggregated_actions_summary(
                event_stream, start_event_idx, inference_func
            )
            if actions_aggregation_summary:  # Only append if we got a valid summary
                event_stream.event_summaries_list.append(
                    EventSummary(
                        "actions_aggregation",
                        start_event_idx,
                        end_event_idx,
                        actions_aggregation_summary,
                    )
                )
            return
    logger.debug(f"No summarization is needed. len(consecutive_action_events): {len(consecutive_action_events)} max_consecutive_actions_to_summarize: {max_consecutive_actions_to_summarize}")
