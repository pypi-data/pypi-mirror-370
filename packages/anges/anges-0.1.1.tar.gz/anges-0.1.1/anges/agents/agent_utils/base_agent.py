import logging
from anges.utils.inference_api import INFERENCE_FUNC_DICT
from anges.utils.data_handler import save_event_stream
from anges.utils.agent_common import LogColors
from anges.agents.agent_utils.events import Event, EventStream
from anges.agents.agent_utils.event_methods import append_events_summary_if_needed
from anges.config import config
from anges.utils.parse_response import get_valid_response_json
from anges.agents.agent_utils.event_methods import construct_prompt_for_event_stream
from anges.utils.mcp_manager import McpManager

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("anges.agents.agent_message_logger")
logger.setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARNING)

class BaseAgent:
    def __init__(
        self,
        parent_ids = [],
        inference_func=None,
        model=None,
        event_stream=None,
        cmd_init_dir=config.agents.default_agent.cmd_init_dir,
        prefix_cmd="",
        interrupt_check=None,
        max_consecutive_actions_to_summarize=config.agents.default_agent.max_consecutive_actions_to_summarize,
        logging_level=logging.DEBUG,
        auto_entitle = False,
        notes = [],
        mcp_config=None,
    ):
        self.parent_ids = parent_ids
        self.event_stream = event_stream if event_stream else EventStream(parent_event_stream_uids=parent_ids, agent_type="default_agent")
        if mcp_config:
            self.event_stream.mcp_config = mcp_config

        self.mcp_manager = McpManager(self.event_stream.mcp_config)

        # Use the configured inference function from YAML if none is provided
        self.inference_func = inference_func
        self.model = model if model else "agent_default"
        self.cmd_init_dir = cmd_init_dir
        self.prefix_cmd = prefix_cmd
        self.interrupt_check = interrupt_check
        self.status = "new"
        self.uid = self.event_stream.uid
        self.max_consecutive_actions_to_summarize = max_consecutive_actions_to_summarize
        self.message_handlers = []
        self.agent_prompt_template = ""
        self.logger = logger
        self.logging_level = logging_level
        logger.setLevel(logging_level)
        self.auto_entitle = auto_entitle
        self.agent_message_base = ""
        self.notes = notes
        self.agent_config = None
        if inference_func:
            self.inference_func = inference_func
        elif model != "agent_default":
            self.inference_func = INFERENCE_FUNC_DICT[model]
        else:
            self.inference_func = None


    def handle_user_visible_messages(self, message: str):
        """
        Handle user visible messages by calling all registered message handlers.
        This provides a more direct approach for sending messages to the frontend.
        
        Args:
            message: The message to be sent to the frontend
        """
        logger.info(f"{LogColors.YELLOW}{message}{LogColors.RESET}")
        for handler in self.message_handlers:
            handler(message)

    def _build_run_config(self, task_description, event_stream):
        return {
            "event_stream": event_stream,
            "inference_func": self.inference_func,
            "cmd_init_dir": self.cmd_init_dir,
            "prefix_cmd": self.prefix_cmd,
            "interrupt_check": self.interrupt_check,
            "max_consecutive_actions_to_summarize": self.max_consecutive_actions_to_summarize,
            "task_description": task_description,
            "message_handler_func": self.handle_user_visible_messages,
            "logger": self.logger,
            "agent_config": self.agent_config,
            "mcp_manager": self.mcp_manager
        }
    
    # Handle received request - add new request event to event stream
    def _handle_received_new_request(self, run_config) -> None:
        task_description = run_config["task_description"]
        event_stream = run_config["event_stream"]
        inference_func = run_config["inference_func"]
        # Add new request event to event stream
        message = f"{self.agent_message_base} received a new request:\n\n{task_description}"
        event_message = message if self.parent_ids else task_description
        if len(event_stream.events_list) == 0:
            event_stream.events_list.append(Event(type="new_request", reasoning="", content=task_description, message=event_message))
        else:
            event_stream.events_list.append(Event(type="follow_up_request", reasoning="", content=task_description, message=event_message))
        # Log after adding the event
        self.handle_user_visible_messages(message)
        if not self.parent_ids and len(event_stream.events_list) == 1 and self.auto_entitle:
            ask_for_title_prompt = f"Please summarize the following request in several words as the title of the conversation:***\n{task_description}\n*** Only output the summarized title, nothing else. Use the same language as the request."
            title = inference_func(ask_for_title_prompt)
            event_stream.title = title
        save_event_stream(event_stream)
    
    def _check_interruption(self, run_config) -> EventStream:
        interrupt_check = run_config['interrupt_check']
        event_stream = run_config['event_stream']
        max_consecutive_actions_to_summarize = run_config['max_consecutive_actions_to_summarize']
        inference_func = run_config['inference_func']
        if interrupt_check and interrupt_check():
            message = f"{self.agent_message_base} task was interrupted by user request"
            append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, self.agent_config)
            save_event_stream(event_stream)
            event_stream.events_list.append(
                Event(
                    type="task_interrupted",
                    reasoning="Task interrupted by user",
                    content="Task execution was interrupted by user request before completion",
                    analysis="Task interrupted before completion",
                    message=message,
                )
            )
            self.handle_user_visible_messages(message)
            append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, self.agent_config)
            save_event_stream(event_stream)
            return event_stream
        return None

    def _count_events_since_last_user_input(self, events_list):
        """
        Count events from the most recent user input (new_request or follow_up_request).
        
        Args:
            events_list (list): List of events to analyze
            
        Returns:
            int: Number of events since the last user input
        """
        if not events_list:
            return 0
        
        # Find the index of the most recent user input event
        last_user_input_index = -1
        for i in range(len(events_list) - 1, -1, -1):  # Search backwards
            if events_list[i].type in ["new_request", "follow_up_request"]:
                last_user_input_index = i
                break
        
        # If no user input found, count all events (fallback to original behavior)
        if last_user_input_index == -1:
            return len(events_list)
        
        # Count events from the user input onwards (including the user input event)
        return len(events_list) - last_user_input_index

    def _check_exhausted(self, run_config) -> EventStream:
        agent_config = run_config['agent_config']
        max_number_of_events_to_exhaust = agent_config.max_number_of_events_to_exhaust
        event_stream = run_config['event_stream']
        inference_func = run_config['inference_func']
        
        # Count events from the most recent user input (new_request or follow_up_request)
        events_since_last_user_input = self._count_events_since_last_user_input(event_stream.events_list)
        
        if events_since_last_user_input >= max_number_of_events_to_exhaust:
            append_events_summary_if_needed(event_stream, inference_func, 1, self.agent_config)
            save_event_stream(event_stream)
            message = f"{self.agent_message_base} Task execution was stopped because the agent has exhausted the maximum number of events ({events_since_last_user_input}/{max_number_of_events_to_exhaust}) since the last user input. Summary of the progress so far:\n{event_stream.event_summaries_list[-1].summary}"
            event_stream.events_list.append(
                Event(
                    type="task_interrupted",
                    reasoning="Task execution was stopped because the maximum number of events was reached",
                    content=message,
                    analysis="Task execution was stopped because the maximum number of events was reached",
                    message=message,
                )
            )
            self.handle_user_visible_messages(message)
            save_event_stream(event_stream)
            return event_stream
        return None

    def _prompt_and_get_action_from_response(self, event_stream):
        inference_func = self.inference_func
        registered_actions = self.registered_actions
        # Construct prompt given the event stream and parse the response
        action_type_list = [a.type for a in registered_actions]
        action_instruction_list = [a.guide_prompt for a in registered_actions if a.guide_prompt]
        prompt_template = self.agent_prompt_template
        prompt_action_instruction = f"Here are the actionable tags that you can use in the response (note that all any unique action can not be used along with any other actions): {action_type_list}\n" + "\n".join(action_instruction_list)
        prompt_template = prompt_template.replace("PLACEHOLDER_ACTION_INSTRUCTIONS", prompt_action_instruction)
        notes_instruction = ""
        agent_notes = [n for n in self.notes if n.get("scope") == "agent"]
        if agent_notes:
            agent_notes_str = str([{'title': n.get('title', ''), 'content': n.get('content', '')} for n in agent_notes])
            notes_instruction = f"Here IMPORTANT notes provided by the user about this task:\n{agent_notes_str}\n(! Note that these are only available to you, not your child agents)"
        prompt_template = prompt_template.replace("PLACEHOLDER_NOTES_INSTRUCTIONS", notes_instruction)
        prompt = construct_prompt_for_event_stream(event_stream, prompt_template=prompt_template, agent_config=self.agent_config)
        parsed_response_dict = get_valid_response_json(
            prompt=prompt, inference_func=inference_func, logger=self.logger, valid_action_list = registered_actions
        )
        return parsed_response_dict


    def _prefict_next_event_and_handle_actions(self, event_stream, run_config):
        parsed_response_dict = self._prompt_and_get_action_from_response(event_stream)
        registered_actions_dict = {}
        for ra in self.registered_actions:
            registered_actions_dict[ra.type.lower()] = ra
        called_actions_json = parsed_response_dict.get("actions", [])
        first_action = registered_actions_dict[called_actions_json[0].get("action_type").lower()]

        if first_action.returning_action:
            returning_event_stream = first_action.handle_action_in_parsed_response(run_config, parsed_response_dict, called_actions_json[0])
            return returning_event_stream
        
        for action_json in called_actions_json:
            action = registered_actions_dict.get(action_json.get("action_type").lower())
            action.handle_action_in_parsed_response(run_config, parsed_response_dict, action_json)
        
        # Do not return event_stream here, loop will continue
        return None

    def run_with_new_request(
        self,
        task_description,
        event_stream=None,
    ):
        # Use provided parameters or default to instance fields
        event_stream = event_stream if event_stream else self.event_stream

        run_config = self._build_run_config(task_description, event_stream)
        run_config["agent_message_base"] = self.agent_message_base

        # Add new request event to event stream
        self._handle_received_new_request(run_config)

        while True:
            # Check for interrupt if function is provided
            event_stream_if_interrupted = self._check_interruption(run_config)
            if event_stream_if_interrupted:
                return event_stream_if_interrupted

            # Check if the agent is exhausted
            event_stream_if_exhausted = self._check_exhausted(run_config)
            if event_stream_if_exhausted:
                return event_stream_if_exhausted

            event_stream_if_return = self._prefict_next_event_and_handle_actions(event_stream, run_config)
            if event_stream_if_return:
                return event_stream_if_return            
            
            # Do not return event_stream here, loop will continue
