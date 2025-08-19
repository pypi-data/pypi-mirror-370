from anges.agents.agent_utils.mcp_actions import UseMCPToolAction
from anges.prompt_templates.task_analyzer_prompts import TASK_ANALYZER_PROMPT_TEMPLATE
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.agent_actions import RunShellCMDAction, TaskCompleteAction, AgentHelpNeededAction, ReadMIMEFilesAction
from anges.config import config
from anges.utils.inference_api import INFERENCE_FUNC_DICT

"""
Task Analyzer
"""
class TaskAnalyzer(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.parent_ids:
            self.agent_message_base = f"Agent (Type: TaskAnalyzer, ID: {self.uid}, Parent_Ids: {'-'.join(self.parent_ids)}) "
        else:
            self.agent_message_base = f"Agent (Type: TaskAnalyzer, ID: {self.uid}) "
        self.agent_prompt_template = TASK_ANALYZER_PROMPT_TEMPLATE
        # 2 actions are loop termination actions: task_complete, agent_help_needed
        # 1 actions are loop continuation actions: run_shell_cmd
        self.registered_actions = [
            TaskCompleteAction(),
            AgentHelpNeededAction(),
            RunShellCMDAction(),
            ReadMIMEFilesAction(),
            UseMCPToolAction(self.mcp_manager)
        ]
        self.agent_config = config.agents.task_analyzer
        self.max_consecutive_actions_to_summarize = self.agent_config.max_consecutive_actions_to_summarize
        if not self.inference_func:
            self.inference_func = INFERENCE_FUNC_DICT[self.agent_config.model_name]
