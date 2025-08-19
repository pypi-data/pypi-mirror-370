#!/usr/bin/env python3
"""
Custom Agent Example for Anges Framework

This example demonstrates how to create custom agents by extending the BaseAgent class
and implementing specialized behavior, custom actions, and agent-specific logic.
"""

import logging
import json
from anges.agents.agent_utils.base_agent import BaseAgent
from anges.agents.agent_utils.agent_actions import (
    Action, TaskCompleteAction, RunShellCMDAction, 
    EditFileAction, AgentTextResponseAction, AgentHelpNeededAction
)
from anges.agents.agent_utils.events import Event, EventStream
from anges.config import config
from anges.utils.inference_api import INFERENCE_FUNC_DICT
from anges.prompt_templates.common_prompts import DEFAULT_AGENT_PROMPT_TEMPLATE


class CodeAnalyzerAgent(BaseAgent):
    """
    A custom agent specialized for code analysis tasks.
    This agent has enhanced capabilities for analyzing Python code,
    detecting patterns, and providing code quality feedback.
    
    专门用于代码分析任务的自定义代理。
    该代理具有分析Python代码、检测模式和提供代码质量反馈的增强功能。
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set custom agent identification
        # 设置自定义代理标识
        if self.parent_ids:
            self.agent_message_base = f"Agent (Type: CodeAnalyzerAgent, ID: {self.uid}, Parent_Ids: {'-'.join(self.parent_ids)}) "
        else:
            self.agent_message_base = f"Agent (Type: CodeAnalyzerAgent, ID: {self.uid}) "
        
        # Custom prompt template for code analysis
        # 代码分析的自定义提示模板
        self.agent_prompt_template = self._get_custom_prompt_template()
        
        # Register actions (including custom ones)
        # Register actions (including custom ones)
        # 注册动作（包括自定义动作）
        self.registered_actions = [
            TaskCompleteAction(),
            RunShellCMDAction(),
            EditFileAction(),
            AgentTextResponseAction(),
            AgentHelpNeededAction(),
            CodeQualityCheckAction(),  # Custom action | 自定义动作
            PythonLintAction(),        # Custom action | 自定义动作
        ]
        
        # Use task executor config as base
        # 使用任务执行器配置作为基础
        self.agent_config = config.agents.task_executor
        self.max_consecutive_actions_to_summarize = self.agent_config.max_consecutive_actions_to_summarize
        
        # Set inference function
        # 设置推理函数
        if kwargs.get("inference_func"):
            self.inference_func = kwargs.get("inference_func")
        else:
            self.inference_func = INFERENCE_FUNC_DICT[self.agent_config.model_name]
    def _get_custom_prompt_template(self):
        """
        Returns a custom prompt template specialized for code analysis.
        返回专门用于代码分析的自定义提示模板。
        """
        return """
# INSTRUCTION
You are a specialized Code Analyzer Agent. You excel at analyzing Python code, 
detecting code quality issues, suggesting improvements, and performing automated 
code reviews. You have access to custom actions for code quality checking and linting.

Your capabilities include:
- Static code analysis
- Code quality assessment
- Security vulnerability detection

When analyzing code, always consider:
1. Code readability and maintainability
2. Performance implications
3. Security best practices
4. Adherence to Python conventions (PEP 8)
5. Potential bugs or edge cases

{event_stream_prompt}

## Response Format Rules
You need to respond in a *JSON* format with the following keys:
- `analysis`: your chain-of-thought thinking about the code analysis task
- `action`: [] -> List of actions you want to take as the next step
- `reasoning`: your reasoning for the chosen actions

## Available Action Tags
{action_guide_prompt}
"""


class CodeQualityCheckAction(Action):
    """
    Custom action for performing comprehensive code quality checks.
    """
    
    def __init__(self):
        self.type = "CODE_QUALITY_CHECK"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### CODE_QUALITY_CHECK:
**non-visible action**
Use this action to perform comprehensive code quality analysis on Python files.

Required fields:
- `action_type`: Must be "CODE_QUALITY_CHECK".
- `file_path`: Path to the Python file to analyze.
- `checks`: List of checks to perform (e.g., ["complexity", "security", "performance"]).

Optional fields:
- `output_format`: "json" or "text" (default: "text").
- `severity_level`: "low", "medium", "high" (default: "medium").

Example:
{
  "action_type": "CODE_QUALITY_CHECK",
  "file_path": "src/main.py",
  "checks": ["complexity", "security", "performance"],
  "output_format": "json"
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        """
        Handle the code quality check action.
        """
        file_path = action_json.get("file_path", "")
        checks = action_json.get("checks", ["complexity", "security"])
        output_format = action_json.get("output_format", "text")
        severity_level = action_json.get("severity_level", "medium")
        
        event_stream = run_config["event_stream"]
        
        try:
            # Simulate code quality analysis (in real implementation, this would use tools like pylint, bandit, etc.)
            analysis_result = self._perform_quality_analysis(file_path, checks, severity_level)
            
            if output_format == "json":
                content = json.dumps(analysis_result, indent=2)
            else:
                content = self._format_analysis_text(analysis_result)
            
            message = f"{run_config['agent_message_base']} performed code quality check on {file_path}"
            
            event_stream.events_list.append(
                Event(
                    type="action",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=content,
                    analysis=parsed_response_dict.get("analysis", ""),
                    message=message,
                    est_input_token=parsed_response_dict.get("est_input_token", 0),
                    est_output_token=parsed_response_dict.get("est_output_token", 0),
                )
            )
            
            run_config["message_handler_func"](message)
            
        except Exception as e:
            error_message = f"Error performing code quality check: {str(e)}"
            event_stream.events_list.append(
                Event(
                    type="error",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=error_message,
                    message=f"{run_config['agent_message_base']} {error_message}",
                )
            )
        
        return event_stream
    
    def _perform_quality_analysis(self, file_path, checks, severity_level):
        """
        Simulate code quality analysis (placeholder implementation).
        """
        return {
            "file": file_path,
            "checks_performed": checks,
            "severity_level": severity_level,
            "issues_found": [
                {
                    "type": "complexity",
                    "line": 42,
                    "message": "Function has high cyclomatic complexity",
                    "severity": "medium"
                },
                {
                    "type": "security",
                    "line": 15,
                    "message": "Potential SQL injection vulnerability",
                    "severity": "high"
                }
            ],
            "score": 7.5,
            "recommendations": [
                "Consider breaking down complex functions",
                "Use parameterized queries for database operations"
            ]
        }
    
    def _format_analysis_text(self, analysis_result):
        """
        Format analysis results as readable text.
        """
        text = f"Code Quality Analysis for {analysis_result['file']}\n"
        text += f"Score: {analysis_result['score']}/10\n\n"
        text += "Issues Found:\n"
        for issue in analysis_result['issues_found']:
            text += f"- Line {issue['line']}: {issue['message']} ({issue['severity']})\n"
        text += "\nRecommendations:\n"
        for rec in analysis_result['recommendations']:
            text += f"- {rec}\n"
        return text


class PythonLintAction(Action):
    """
    Custom action for running Python linting tools.
    """
    
    def __init__(self):
        self.type = "PYTHON_LINT"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### PYTHON_LINT:
**non-visible action**
Use this action to run Python linting tools on code files.

Required fields:
- `action_type`: Must be "PYTHON_LINT".
- `file_path`: Path to the Python file to lint.

Optional fields:
- `linter`: "pylint", "flake8", "pycodestyle" (default: "pylint").
- `config_file`: Path to linter configuration file.
- `ignore_errors`: List of error codes to ignore.

Example:
{
  "action_type": "PYTHON_LINT",
  "file_path": "src/main.py",
  "linter": "pylint",
  "ignore_errors": ["C0103", "R0903"]
}
"""
    
    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        """
        Handle the Python lint action.
        """
        file_path = action_json.get("file_path", "")
        linter = action_json.get("linter", "pylint")
        config_file = action_json.get("config_file", "")
        ignore_errors = action_json.get("ignore_errors", [])
        
        event_stream = run_config["event_stream"]
        
        # Build linting command
        if linter == "pylint":
            cmd = f"pylint {file_path}"
            if config_file:
                cmd += f" --rcfile={config_file}"
            if ignore_errors:
                cmd += f" --disable={','.join(ignore_errors)}"
        elif linter == "flake8":
            cmd = f"flake8 {file_path}"
            if ignore_errors:
                cmd += f" --ignore={','.join(ignore_errors)}"
        else:
            cmd = f"pycodestyle {file_path}"
        
        try:
            # Use the existing shell command infrastructure
            from anges.utils.shell_wrapper import run_command
            
            result = run_command(
                cmd,
                cwd=run_config.get("cmd_init_dir", "./"),
                timeout=60
            )
            
            content = f"Linting Results ({linter}):\n"
            content += f"Command: {cmd}\n"
            content += f"Exit Code: {result['exit_code']}\n"
            content += f"Output:\n{result['stdout']}\n"
            if result['stderr']:
                content += f"Errors:\n{result['stderr']}\n"
            
            message = f"{run_config['agent_message_base']} ran {linter} on {file_path}"
            
            event_stream.events_list.append(
                Event(
                    type="action",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=content,
                    analysis=parsed_response_dict.get("analysis", ""),
                    message=message,
                    est_input_token=parsed_response_dict.get("est_input_token", 0),
                    est_output_token=parsed_response_dict.get("est_output_token", 0),
                )
            )
            
            run_config["message_handler_func"](message)
            
        except Exception as e:
            error_message = f"Error running {linter}: {str(e)}"
            event_stream.events_list.append(
                Event(
                    type="error",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=error_message,
                    message=f"{run_config['agent_message_base']} {error_message}",
                )
            )
        
        return event_stream


class DataScienceAgent(BaseAgent):
    """
    Another example of a custom agent specialized for data science tasks.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.parent_ids:
            self.agent_message_base = f"Agent (Type: DataScienceAgent, ID: {self.uid}, Parent_Ids: {'-'.join(self.parent_ids)}) "
        else:
            self.agent_message_base = f"Agent (Type: DataScienceAgent, ID: {self.uid}) "
        
        # Specialized prompt for data science tasks
        self.agent_prompt_template = DEFAULT_AGENT_PROMPT_TEMPLATE  # Could be customized further
        
        # Standard actions plus data science specific ones
        self.registered_actions = [
            TaskCompleteAction(),
            RunShellCMDAction(),
            EditFileAction(),
            AgentTextResponseAction(),
            AgentHelpNeededAction(),
            # Could add custom actions like DataAnalysisAction, PlotGenerationAction, etc.
        ]
        
        self.agent_config = config.agents.task_executor
        self.max_consecutive_actions_to_summarize = self.agent_config.max_consecutive_actions_to_summarize
        
        if kwargs.get("inference_func"):
            self.inference_func = kwargs.get("inference_func")
        else:
            self.inference_func = INFERENCE_FUNC_DICT[self.agent_config.model_name]
    
    def analyze_dataset(self, dataset_path):
        """
        Custom method for dataset analysis.
        This demonstrates how to add specialized methods to custom agents.
        """
        task = f"""
        Analyze the dataset at {dataset_path}. Please:
        1. Load the dataset and examine its structure
        2. Check for missing values and data types
        3. Generate basic statistical summaries
        4. Identify potential data quality issues
        5. Suggest preprocessing steps if needed
        """
        
        return self.run_with_new_request(task)


def demonstrate_custom_agents():
    """
    Demonstrate the usage of custom agents.
    """
    print("=== Custom Agent Examples ===\n")
    
    # Example 1: Code Analyzer Agent
    print("--- Code Analyzer Agent ---")
    code_agent = CodeAnalyzerAgent(
        cmd_init_dir="./",
        logging_level=logging.INFO,
        auto_entitle=True
    )
    
    print(f"Created CodeAnalyzerAgent with ID: {code_agent.uid}")
    print(f"Available actions: {[action.type for action in code_agent.registered_actions]}")
    
    # Create a sample Python file to analyze
    sample_code = '''
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                result = x * y * z
                for i in range(100):
                    result += i
                return result
            else:
                return 0
        else:
            return -1
    else:
        return None

# Potential security issue
def unsafe_query(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query
'''
    
    with open("sample_code.py", "w") as f:
        f.write(sample_code)
    
    task = """
    Analyze the Python file 'sample_code.py' for code quality issues.
    Check for complexity, security vulnerabilities, and provide recommendations.
    """
    
    try:
        result = code_agent.run_with_new_request(task)
        print(f"Code analysis completed with {len(result.events_list)} events.")
    except Exception as e:
        print(f"Error in code analysis: {e}")
    
    # Example 2: Data Science Agent
    print("\n--- Data Science Agent ---")
    data_agent = DataScienceAgent(
        cmd_init_dir="./",
        logging_level=logging.INFO
    )
    
    print(f"Created DataScienceAgent with ID: {data_agent.uid}")
    
    # Create sample dataset
    import csv
    sample_data = [
        ["Name", "Age", "Salary", "Department"],
        ["Alice", "25", "50000", "Engineering"],
        ["Bob", "30", "60000", "Marketing"],
        ["Charlie", "35", "", "Engineering"],  # Missing salary
        ["Diana", "28", "55000", "Sales"]
    ]
    
    with open("sample_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)
    
    try:
        result = data_agent.analyze_dataset("sample_data.csv")
        print(f"Dataset analysis completed with {len(result.events_list)} events.")
    except Exception as e:
        print(f"Error in dataset analysis: {e}")


def demonstrate_agent_inheritance():
    """
    Demonstrate different approaches to creating custom agents.
    """
    print("\n=== Agent Inheritance Patterns ===\n")
    
    # Pattern 1: Minimal customization (just change behavior)
    class SimpleCustomAgent(BaseAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.agent_message_base = f"Agent (Type: SimpleCustomAgent, ID: {self.uid}) "
            # Use default everything else
            from anges.agents.default_agent import DefaultAgent
            default_agent = DefaultAgent()
            self.agent_prompt_template = default_agent.agent_prompt_template
            self.registered_actions = default_agent.registered_actions
            self.agent_config = default_agent.agent_config
            self.max_consecutive_actions_to_summarize = default_agent.max_consecutive_actions_to_summarize
            self.inference_func = default_agent.inference_func
    
    # Pattern 2: Composition over inheritance
    class CompositeAgent:
        def __init__(self):
            self.base_agent = BaseAgent()
            self.specialized_tools = {
                'code_analyzer': CodeAnalyzerAgent(),
                'data_scientist': DataScienceAgent()
            }
        
        def delegate_task(self, task_type, task_description):
            if task_type in self.specialized_tools:
                return self.specialized_tools[task_type].run_with_new_request(task_description)
            else:
                return self.base_agent.run_with_new_request(task_description)
    
    print("Demonstrated different patterns for creating custom agents:")
    print("1. Full customization (CodeAnalyzerAgent, DataScienceAgent)")
    print("2. Minimal customization (SimpleCustomAgent)")
    print("3. Composition pattern (CompositeAgent)")


if __name__ == "__main__":
    print("Anges Framework Custom Agent Examples")
    print("====================================\n")
    
    try:
        demonstrate_custom_agents()
        demonstrate_agent_inheritance()
        
        print("\n=== Custom Agent Examples Completed ===\n")
        print("Key takeaways:")
        print("1. Extend BaseAgent to create specialized agents")
        print("2. Override __init__ to customize behavior and actions")
        print("3. Create custom actions by extending the Action class")
        print("4. Use custom prompt templates for specialized domains")
        print("5. Consider composition patterns for complex scenarios")
        
        # Cleanup
        import os
        for file in ["sample_code.py", "sample_data.csv"]:
            if os.path.exists(file):
                os.remove(file)
        
    except Exception as e:
        print(f"Error running custom agent examples: {e}")
        print("Make sure you have the Anges framework properly installed and configured.")