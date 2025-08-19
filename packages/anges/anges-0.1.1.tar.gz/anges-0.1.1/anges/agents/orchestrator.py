from anges.utils.agent_call_agent import parse_call_child_agent_content_json
from anges.agents.agent_utils.events import Event, EventStream
from anges.prompt_templates.orchestrator_prompts import ORCHESTRATOR_PROMPT_TEMPLATE, CALL_CHILD_ACTION_GUIDE_PROMPT, CALL_CHILD_ACTION_RECURSION_GUIDE_PROMPT
from anges.agents.task_analyzer import TaskAnalyzer
from anges.agents.task_executor import TaskExecutor
from anges.utils.data_handler import save_event_stream, read_event_stream
from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.agent_actions import TaskCompleteAction, AgentHelpNeededAction, AgentTextResponseAction
from anges.config import config
from anges.utils.inference_api import INFERENCE_FUNC_DICT
import json

"""
Orchestrator is an agent, that interacts with user and orchestrate other agents.
"""
class Orchestrator(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.parent_ids:
            self.agent_message_base = f"Agent (Type: Orchestrator, ID: {self.uid}, Parent_Ids: {'-'.join(self.parent_ids)}) "
        else:
            self.agent_message_base = f"Agent (Type: Orchestrator, ID: {self.uid}) "
        self.remaining_recursive_depth = 0
        self.agent_prompt_template = ORCHESTRATOR_PROMPT_TEMPLATE
        # 3 actions are loop termination actions: task_complete, agent_help_needed, agent_text_response.
        # 1 actions are loop continuation actions: call_child_agent. This will be appended to the list at runtime.
        self.registered_actions = [
            TaskCompleteAction(),
            AgentHelpNeededAction(),
            AgentTextResponseAction(),
        ]
        self.agent_config = config.agents.orchestrator
        self.max_consecutive_actions_to_summarize = self.agent_config.max_consecutive_actions_to_summarize
        if not self.inference_func:
            self.inference_func = INFERENCE_FUNC_DICT[self.agent_config.model_name]

    def run_with_new_request(
        self,
        task_description,
        event_stream=None,
    ):
        # Use provided parameters or default to instance fields
        event_stream = event_stream if event_stream else self.event_stream

        run_config = self._build_run_config(task_description, event_stream)
        run_config["agent_message_base"] = self.agent_message_base
        run_config["remaining_recursive_depth"] = self.remaining_recursive_depth
        run_config["parent_ids"] = self.parent_ids
        run_config["uid"] = self.uid
        run_config["message_handlers"] = self.message_handlers
        run_config["logging_level"] = self.logging_level
        call_child_agent_action = CallChildAgentAction()
        if self.remaining_recursive_depth != 0:
            self.agent_prompt_template = ORCHESTRATOR_PROMPT_TEMPLATE
            call_child_agent_action.guide_prompt = CALL_CHILD_ACTION_RECURSION_GUIDE_PROMPT
        self.registered_actions.append(call_child_agent_action)

        # Add new request event to event stream
        self._handle_received_new_request(run_config)

        while True:
            # Check for interrupt if function is provided
            event_stream_if_interrupted = self._check_interruption(run_config)
            if event_stream_if_interrupted:
                return event_stream_if_interrupted

            event_stream_if_exhausted = self._check_exhausted(run_config)
            if event_stream_if_exhausted:
                return event_stream_if_exhausted

            # found_action, parsed_response_dict = self._prompt_and_get_action_from_response(event_stream)
            # event_stream_if_exit = found_action.handle_action_in_parsed_response(run_config, parsed_response_dict)
            # if event_stream_if_exit:
            #     return event_stream_if_exit
            event_stream_if_return = self._prefict_next_event_and_handle_actions(event_stream, run_config)
            if event_stream_if_return:
                return event_stream_if_return

            # Do not return event_stream here, loop will continue


class CallChildAgentAction(Action):
    def __init__(self):
        self.type = "CALL_CHILD_AGENT"
        self.user_visible = False
        self.unique_action = True
        self.returning_action = False
        self.guide_prompt = CALL_CHILD_ACTION_GUIDE_PROMPT

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        logger = run_config["logger"]
        event_stream = run_config["event_stream"]
        inference_func = run_config["inference_func"]
        cmd_init_dir = run_config["cmd_init_dir"]
        prefix_cmd = run_config["prefix_cmd"]
        interrupt_check = run_config["interrupt_check"]
        max_consecutive_actions_to_summarize = run_config["max_consecutive_actions_to_summarize"]
        remaining_recursive_depth = run_config["remaining_recursive_depth"]
        parent_ids = run_config["parent_ids"]
        uid = run_config["uid"]
        agent_message_base = run_config["agent_message_base"]
        message_handlers = run_config["message_handlers"]
        reasoning = parsed_response_dict.get("reasoning", "")
        call_child_agent_content = json.dumps(action_json, indent=2)
        try:
            parsed_call_child_agent_content = parse_call_child_agent_content_json(action_json)
        except Exception as e:
            logger.error(e)
            return event_stream

        child_agent_input = parsed_call_child_agent_content["agent_input"]
        child_agent_id = parsed_call_child_agent_content["agent_id"]
        
        # If resume existing agent
        if child_agent_id:
            child_agent_event_stream = read_event_stream(child_agent_id)
            child_agent_type = child_agent_event_stream.agent_type
            message = f"{agent_message_base} wants to resume a child agent {child_agent_id}:\n\n{reasoning}"
            new_child_agent_event = Event(type="resume_child_agent", reasoning=reasoning, content=call_child_agent_content, message=message)

        # If create a new agent
        else:
            child_agent_type = parsed_call_child_agent_content["agent_type"].lower()
            title = f"{'-'.join(parent_ids + [uid])} Child Agent {child_agent_type}"
            child_agent_event_stream = EventStream(parent_event_stream_uids=parent_ids + [uid], title=title)
            message = f"{agent_message_base} wants to call a new child agent {child_agent_type}:\n\n{reasoning}"
            new_child_agent_event = Event(type="new_child_agent", reasoning=reasoning, content=call_child_agent_content, message=message)
        
        run_config["message_handler_func"](message)
        event_stream.add_event(new_child_agent_event)

        # Constructing the agent instance
        if child_agent_type == "task_analyzer":
            child_agent_event_stream.agent_type = "task_analyzer"
            child_agent = TaskAnalyzer(
                parent_ids=parent_ids + [uid],
                inference_func=inference_func,
                event_stream=child_agent_event_stream,
                logging_level=run_config["logging_level"],
                cmd_init_dir=cmd_init_dir,
                prefix_cmd=prefix_cmd,
                interrupt_check=interrupt_check,
                max_consecutive_actions_to_summarize=max_consecutive_actions_to_summarize,
            )

        elif child_agent_type == "task_executor":
            child_agent_event_stream.agent_type = "task_executor"
            child_agent = TaskExecutor(
                parent_ids=parent_ids + [uid],
                inference_func=inference_func,
                event_stream=child_agent_event_stream,
                logging_level=run_config["logging_level"],
                cmd_init_dir=cmd_init_dir,
                prefix_cmd=prefix_cmd,
                interrupt_check=interrupt_check,
                max_consecutive_actions_to_summarize=max_consecutive_actions_to_summarize,
            )
        
        elif child_agent_type == "orchestrator":
            child_agent_event_stream.agent_type = "orchestrator"
            child_agent = Orchestrator(
                parent_ids=parent_ids + [uid],
                inference_func=inference_func,
                event_stream=child_agent_event_stream,
                logging_level=run_config["logging_level"],
                cmd_init_dir=cmd_init_dir,
                prefix_cmd=prefix_cmd,
                interrupt_check=interrupt_check,
                max_consecutive_actions_to_summarize=max_consecutive_actions_to_summarize,
            )
            child_agent.remaining_recursive_depth = remaining_recursive_depth - 1

        else:
            logger.error(f"Unknown child_agent_type: {child_agent_type}")
            return event_stream

        child_agent.message_handlers = message_handlers
        child_agent_message_base = f"Child Agent (Type: {child_agent_type}, ID: {child_agent.uid})"
        message = f"{agent_message_base} child is running:\n\n{child_agent_message_base}"
        child_agent_ack_event = Event(
            type="child_agent_running",
            reasoning=f"""{{"agent_id": "{child_agent.uid}", "starting_from": {len(child_agent_event_stream.events_list)}}}""",
            content=message, message=message)
        run_config["message_handler_func"](message)
        event_stream.add_event(child_agent_ack_event)
        save_event_stream(event_stream)

        # Running the child agent
        child_agent_event_stream = child_agent.run_with_new_request(child_agent_input)

        # Based on the child agent exit result, update the event_stream and go back to the main loop
        child_agent_exit_event = child_agent_event_stream.events_list[-1]
        message = f"{agent_message_base} child agent {child_agent_message_base} exited with message:\n\n{child_agent_exit_event.message}"
        new_child_agent_exit_event = Event(
            type=f"child_agent_{child_agent_exit_event.type}",
            reasoning=f"{child_agent_message_base} exited with reasoning:\n{child_agent_exit_event.reasoning}",
            content=f"{child_agent_message_base} exited with content:\n{child_agent_exit_event.content}",
            message=message,
            analysis=f"{child_agent_message_base} exited with analysis:\n{child_agent_exit_event.analysis}",
        )
        
        run_config["message_handler_func"](message)
        event_stream.add_event(new_child_agent_exit_event)
        save_event_stream(event_stream)
