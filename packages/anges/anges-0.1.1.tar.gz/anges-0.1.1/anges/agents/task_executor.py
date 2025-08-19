from anges.agents.agent_utils.mcp_actions import UseMCPToolAction
from anges.prompt_templates.common_prompts import DEFAULT_AGENT_PROMPT_TEMPLATE
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.agent_actions import RunShellCMDAction, TaskCompleteAction, EditFileAction, AgentHelpNeededAction, ReadMIMEFilesAction
from anges.config import config
from anges.utils.inference_api import INFERENCE_FUNC_DICT


"""
Task Executor
"""
class TaskExecutor(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.parent_ids:
            self.agent_message_base = f"Agent (Type: TaskExecutor, ID: {self.uid}, Parent_Ids: {'-'.join(self.parent_ids)}) "
        else:
            self.agent_message_base = f"Agent (Type: TaskExecutor, ID: {self.uid}) "
        self.agent_prompt_template = DEFAULT_AGENT_PROMPT_TEMPLATE
        # 2 actions are loop termination actions: task_complete, agent_help_needed
        # 2 actions are loop continuation actions: run_shell_cmd, edit_file_content
        self.registered_actions = [
            TaskCompleteAction(),
            AgentHelpNeededAction(),
            RunShellCMDAction(),
            EditFileAction(),
            ReadMIMEFilesAction(),
            UseMCPToolAction(self.mcp_manager)
        ]
        self.agent_config = config.agents.task_executor
        self.max_consecutive_actions_to_summarize = self.agent_config.max_consecutive_actions_to_summarize
        if not self.inference_func:
            self.inference_func = INFERENCE_FUNC_DICT[self.agent_config.model_name]
