import platform
from anges.utils.shell_wrapper import run_command
from anges.utils.data_handler import save_event_stream
from anges.utils.agent_edit_file import get_agent_file_editing_operation_output
from anges.agents.agent_utils.events import Event
from anges.agents.agent_utils.event_methods import append_events_summary_if_needed


class Action:
    def __init__(self):
        self.type = ""
        self.guide_prompt = ""
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False

    def handle_action_in_parsed_response():
        raise NotImplementedError("Subclasses must implement this method")


class TaskCompleteAction(Action):
    def __init__(self):
        self.type = "TASK_COMPLETE"
        self.user_visible = True
        self.unique_action = True
        self.returning_action = True
        self.guide_prompt = """
### TASK_COMPLETE:
**user visible action**
**unique action**
If you think the current task has been completed, use this action to output the task completion information in JSON format.
Two fields are required:
- `action_type`: Should be set to "TASK_COMPLETE".
- `content`: A string explains the task completion information, including a summary of high steps, actions, and verifications that have been done. If needed, output the content in Markdown style.
{
    "action_type": "TASK_COMPLETE",
    "content": "The task has been completed",
}

#### Example full response. TASK_COMPLETE is used for call completion of the task
{
    "analysis": "some mumbling and chain of thought etc etc ...",
    "reasoning": "Since the files have been cleaned up and the system is in a good state, we can use the task complete action to finish the task.",
    "actions": [{
        "action_type": "TASK_COMPLETE",
        "content": "The task has been completed. The files have been cleaned up and the system is in a good state.",
    }],
}
"""

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        action = action_json
        task_complete_content = action.get("content", "")
        event_stream = run_config["event_stream"]
        inference_func = run_config["inference_func"]
        max_consecutive_actions_to_summarize = run_config["max_consecutive_actions_to_summarize"]
        message = f"{run_config['agent_message_base']} completed the task:\n\n{task_complete_content}"
        event_stream.events_list.append(
            Event(
                type="task_completion",
                reasoning=parsed_response_dict.get("reasoning", ""),
                content=task_complete_content,
                analysis=parsed_response_dict.get("analysis", ""),
                message=message,
                est_input_token=parsed_response_dict.get("est_input_token", 0),
                est_output_token=parsed_response_dict.get("est_output_token", 0),
            )
        )
        run_config["message_handler_func"](message)
        append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, run_config.get('agent_config'))
        save_event_stream(event_stream)
        return event_stream



class RunShellCMDAction(Action):
    def __init__(self):
        self.type = "RUN_SHELL_CMD"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        
        # Get current platform information
        current_platform = platform.system()
        if current_platform == "Windows":
            platform_info = "Windows"
            script_types = "cmd/powershell"
        elif current_platform == "Darwin":
            platform_info = "macOS"
            script_types = "bash/zsh"
        else:  # Linux and other Unix-like
            platform_info = "Linux/Unix"
            script_types = "bash/sh"
        
        self.guide_prompt = f"""
### RUN_SHELL_CMD:
**non-visible action**
Use this action to execute a shell command.

Required fields:
- `action_type`: Must be "RUN_SHELL_CMD".
- `command`: The shell command to be executed as string.
- `reasoning`: Why this command should be executed.
Optional fields:
- `run_in_background`: boolean, default false. Set true if the command should run in background.
- `shell_cmd_timeout`: integer, max 1800 (30 minutes). Specify a timeout in seconds. Defaults to system config.

**Current Platform & Script Type**: Running on {platform_info}, recommended script types: {script_types}. Consider cross-platform compatibility when possible.

#### Example full response:
{{
        "analysis": "some analysis...",
  "reasoning": "We need to list current directory to check the files.",
  "actions": [
    {{
        "action_type": "RUN_SHELL_CMD",
      "command": "ls -la",
      "shell_cmd_timeout": 60
    }}
  ]
}}

#### Another example full response of running a web server in background:
{{
        "analysis": "To verify if the web server starts correctly, we need to launch it in the background so it remains running while we perform follow-up tests.",
  "reasoning": "Running the server in background allows us to test endpoints afterward without blocking the agent. Then kill the running process.",
  "actions": [
    {{
        "action_type": "RUN_SHELL_CMD",
      "command": "python3 -m http.server 8000 & echo $! > webserver.pid",
      "run_in_background": true
    }},
    {{
        "action_type": "RUN_SHELL_CMD",
      "command": "curl localhost:8000",
    }}
  ]
}}
"""

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        action = action_json
        command = action.get("command", "")
        if not command:
            return None
        reasoning = parsed_response_dict.get("reasoning", "")
        truncated_command = command[:200] + "..." if len(command) > 100 else command
        cmd_init_dir = run_config["cmd_init_dir"]
        prefix_cmd = run_config["prefix_cmd"]
        event_stream = run_config["event_stream"]
        inference_func = run_config["inference_func"]
        shell_cmd_timeout = min(
            action.get("shell_cmd_timeout", run_config["agent_config"].shell_cmd_timeout), 1800
        )
        run_in_background = action.get("run_in_background", False)
        max_consecutive_actions_to_summarize = run_config["max_consecutive_actions_to_summarize"]

        message = f"{run_config['agent_message_base']} wants to run shell:\n\n```{truncated_command}```\n\n{reasoning}"
        cmd_output = run_command(
            command,
            timeout=shell_cmd_timeout,
            cmd_init_dir=cmd_init_dir,
            prefix_cmd=prefix_cmd,
            run_in_background=run_in_background,
        )

        event_stream.events_list.append(
            Event(
                type="action",
                reasoning=reasoning,
                content=cmd_output,
                analysis=parsed_response_dict.get("analysis", ""),
                message=message,
                est_input_token=parsed_response_dict.get("est_input_token", 0),
                est_output_token=parsed_response_dict.get("est_output_token", 0),
            )
        )
        run_config["message_handler_func"](message)
        append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, run_config.get('agent_config'))
        save_event_stream(event_stream)
        run_config["logger"].debug(
            f"Event {len(event_stream.events_list)}: Reasoning: {reasoning}, Command Executed: {command}, Command Output: {cmd_output}"
        )


class AgentHelpNeededAction(Action):
    def __init__(self):
        self.type = "HELP_NEEDED"
        self.user_visible = True
        self.unique_action = True # Asking for help should be the only action in a turn
        self.returning_action = True
        self.guide_prompt = """
### HELP_NEEDED:
**user visible action**
**unique action**
If you get stuck and are unable to proceed with the task, use this action to call for human help. This is a last resort to be used only after you have tried all viable autonomous solutions. This should be the only action in your response.

The action requires a `content` field, which should be a detailed, Markdown-formatted string explaining the issue. It must include:
- **Blocker**: A clear description of what is preventing you from proceeding.
- **Attempts**: A list of the commands or methods you have already tried.
- **Suggestion**: What you believe is needed to unblock you.

{
    "action_type": "HELP_NEEDED",
    "content": "### Blocker\\nI am unable to install the required Python package 'scikit-learn' due to a permission error.\\n\\n### Attempts\\n1. `pip install scikit-learn` - Failed with 'Permission denied'.\\n2. `sudo pip install scikit-learn` - Failed with 'sudo: command not found' or a password prompt I cannot answer.\\n\\n### Suggestion\\nTo unblock this task, please install the 'scikit-learn' package in the execution environment manually and then restart the task."
}

#### Example full response. HELP_NEEDED is used when the agent is stuck.
{
    "analysis": "My primary goal is to run a data analysis script, which requires the 'scikit-learn' library. My attempt to install this library via `pip` failed due to permissions. I then attempted to use `sudo`, which also failed. I have no other methods to install packages.",
    "reasoning": "Since I have exhausted all autonomous options for installing the dependency, I cannot proceed with the task. It is now necessary to ask for human intervention. I will use the HELP_NEEDED action to clearly state the problem and my attempted solutions.",
    "actions": [{
        "action_type": "HELP_NEEDED",
        "content": "### Blocker\\nI am unable to install the required Python package 'scikit-learn' due to a permission error.\\n\\n### Attempts\\n1. `pip install scikit-learn` - Failed with 'Permission denied'.\\n2. `sudo pip install scikit-learn` - Failed with a password prompt I cannot answer.\\n\\n### Suggestion\\nTo unblock this task, please install the 'scikit-learn' library in the execution environment manually and then restart the task."
    }],
}
"""

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        action = action_json
        agent_help_needed_content = action.get("content", "")

        if agent_help_needed_content:
            event_stream = run_config["event_stream"]
            inference_func = run_config["inference_func"]
            max_consecutive_actions_to_summarize = run_config["max_consecutive_actions_to_summarize"]

            message = f"{run_config['agent_message_base']} needed help:\n\n{agent_help_needed_content}"
            
            event_stream.events_list.append(
                Event(
                    # Note: The event type is kept from your original code
                    type="agent_requested_help",
                    reasoning=parsed_response_dict.get("reasoning", ""),
                    content=agent_help_needed_content,
                    analysis=parsed_response_dict.get("analysis", ""),
                    message=message,
                    est_input_token=parsed_response_dict.get("est_input_token", 0),
                    est_output_token=parsed_response_dict.get("est_output_token", 0),
                )
            )
            
            run_config["message_handler_func"](message)
            append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, run_config.get('agent_config'))
            save_event_stream(event_stream)
            
            # Return the stream to signal that a terminal, user-visible action occurred.
            return event_stream


class AgentTextResponseAction(Action):
    def __init__(self):
        self.type = "AGENT_TEXT_RESPONSE"
        self.user_visible = True
        self.unique_action = True
        self.returning_action = True
        self.guide_prompt = """
### AGENT_TEXT_RESPONSE
**user visible action**
**unique action**

Use this action to provide a markdown-formatted **textual response** when the user's request is **question-like**, expects **information**, or **intermediate results**. Do **not** use this for final task completion summaries — for that, use `TASK_COMPLETE`.

---

Use this when:
- The user asked a question and expects a factual or informative answer.
- You need to present the output of a command, table, or formatted text to the user.
- You want to respond with a markdown explanation or update.

Do **not** use this when:
- The goal is to summarize and declare a full task as completed — instead, use `TASK_COMPLETE`.

---

Required fields:
- `action_type`: Must be `"AGENT_TEXT_RESPONSE"`
- `content`: Markdown-formatted response text to be shown to the user.

Optional fields:
- `analysis`: Analysis of what the user asked or why this response is appropriate.
- `reasoning`: Explanation of how this response was derived.

---

Example 1: Returning command output
{
  "analysis": "The user asked to list the files. We ran `ls -la`, and the output should be shown.",
  "reasoning": "This is the expected output and answers the user's question.",
  "actions": [
    {
      "action_type": "AGENT_TEXT_RESPONSE",
      "content": "Here is the result of `ls -la`:\n```\ntotal 24\ndrwxr-xr-x  3 user user 4096 Dec  5 07:33 .\ndrwxr-xr-x 29 user user 4096 Dec  5 07:46 ..\n-rw-r--r--  1 user user 1627 Dec  5 07:32 chat_app.py\n-rw-r--r--  1 user user 1262 Dec  5 07:33 complex_test.txt\n-rw-r--r--  1 user user 1001 Dec  5 07:26 sample.txt\ndrwxr-xr-x  2 user user 4096 Dec  5 07:25 templates\n```"
    }
  ]
}

Example 2: Responding to a user question
{
  "reasoning": "The user asked how to restart the server, and this is a direct response to that.",
  "actions": [
    {
      "action_type": "AGENT_TEXT_RESPONSE",
      "content": "You can restart the server using:\n```\nsystemctl restart webserver.service\n```"
    }
  ]
}

❗If you’re ready to conclude and summarize a complete multi-step task (e.g. setup, fix, pipeline run), use `TASK_COMPLETE` instead.
"""

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        action = action_json
        text_response = action.get("content", "")
        event_stream = run_config["event_stream"]
        inference_func = run_config["inference_func"]
        max_consecutive_actions_to_summarize = run_config["max_consecutive_actions_to_summarize"]

        message = f"{run_config['agent_message_base']} provided response:\n\n{text_response}"
        event_stream.events_list.append(
            Event(
                type="agent_text_response",
                reasoning=parsed_response_dict.get("reasoning", ""),
                content=text_response,
                analysis=parsed_response_dict.get("analysis", ""),
                message=message,
                est_input_token=parsed_response_dict.get("est_input_token", 0),
                est_output_token=parsed_response_dict.get("est_output_token", 0),
            )
        )
        run_config["message_handler_func"](message)
        append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, run_config.get('agent_config'))
        save_event_stream(event_stream)
        run_config["logger"].debug(
            f"Event {len(event_stream.events_list)}: Agent Text Response: {text_response}"
        )
        return event_stream


class EditFileAction(Action):
    def __init__(self):
        self.type = "EDIT_FILE"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.guide_prompt = """
### EDIT_FILE:
**non-visible action**

Use this action to create or edit files in a structured, declarative way.

Required fields:
- `action_type`: Must be "EDIT_FILE"
- `directive_line`: A string that specifies the file operation. Must be one of:
  - `NEW_FILE <file_path>` — Create a new file with content.
  - `INSERT_LINES <file_path> <N>` — Insert lines before line N. Use 0 for start of file, -1 for end of file.
  - `REMOVE_LINES <file_path> <x>-<y>` — Remove lines x to y, inclusive.
  - `REPLACE_LINES <file_path> <x>-<y>` — Replace lines x to y, inclusive, with the given content.
- `content`: The content block used by NEW_FILE, INSERT_LINES, and REPLACE_LINES. Optional for REMOVE_LINES.

IMPORTANT RULES:
- Before editing a file, always read it using `nl -b a` (not `cat`) to include line numbers.
- Edited file content will be shown in **diff** format. Double-check your changes are correct.
- You can use mutliple EDIT_FILE actions, or EDIT_FILE and RUN_SHELL_CMD together in a single response, but ensure they are logically ordered.

---

Example 1: Create a new file
{
  "reasoning": "Create a config file needed by the logging system.",
  "actions": [
    {
      "action_type": "EDIT_FILE",
      "directive_line": "NEW_FILE configs/logging.yaml",
      "content": "level: INFO\nhandlers: [console]"
    }
  ]
}

Example 2: Insert a dependency at line 5
{
  "reasoning": "Add missing dependency to the requirements file.",
  "actions": [
    {
      "action_type": "EDIT_FILE",
      "directive_line": "INSERT_LINES requirements.txt 5",
      "content": "fastapi==0.110.0"
    }
  ]
}

Example 3: Remove deprecated lines 10 through 20 (inclusive)
{
  "reasoning": "Remove deprecated code from main.py.",
  "actions": [
    {
      "action_type": "EDIT_FILE",
      "directive_line": "REMOVE_LINES main.py 10-20",
      "content": ""
    }
  ]
}

Example 4: Replace lines 22 through 25 (inclusive)
{
  "reasoning": "Refactor logic inside the function to fix a bug.",
  "actions": [
    {
      "action_type": "EDIT_FILE",
      "directive_line": "REPLACE_LINES app/logic.py 22-25",
      "content": "def updated_function():\n    return True"
    }
  ]
}
"""

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        action = action_json
        directive = action.get("directive_line", "")
        content = action.get("content", "")
        if not directive:
            return
        reasoning = parsed_response_dict.get("reasoning", "")
        cmd_init_dir = run_config["cmd_init_dir"]
        event_stream = run_config["event_stream"]
        inference_func = run_config["inference_func"]
        max_consecutive_actions_to_summarize = run_config["max_consecutive_actions_to_summarize"]

        edit_file_input = f"{directive}\n{content}".strip()
        message = f"{run_config['agent_message_base']} wants to edit file::\n\n{reasoning}"
        edit_file_output = get_agent_file_editing_operation_output(edit_file_input, cmd_init_dir)

        event_stream.events_list.append(
            Event(
                type="edit_file",
                reasoning=reasoning,
                content=edit_file_output,
                analysis=parsed_response_dict.get("analysis", ""),
                message=message,
                est_input_token=parsed_response_dict.get("est_input_token", 0),
                est_output_token=parsed_response_dict.get("est_output_token", 0),
            )
        )
        run_config["message_handler_func"](message)
        append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, run_config.get('agent_config'))
        save_event_stream(event_stream)
        run_config["logger"].debug(
            f"Event {len(event_stream.events_list)}: Reasoning: {reasoning}, Edit File Input: {edit_file_input}, Output: {edit_file_output}"
        )


class ReadMIMEFilesAction(Action):
    def __init__(self):
        self.type = "READ_MIME_FILES"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False # This action does not terminate the turn
        self.guide_prompt = """
### READ_MIME_FILES:
Use this action to analyze the content of local files (e.g., images, PDFs) and YouTube links using a multi-modal AI model.

The action object must contain:
- `action_type`: "READ_MIME_FILES"
- `question` (string, required): The query about the content of the specified files.
- `inputs` (list of strings, required): One or more paths to local files or a YouTube link. Ensure paths are accessible.
- `output` (string, optional): If provided, the AI's full response is saved to this file, and the action's result is a confirmation message. Otherwise, the result is the full text response itself.

#### Example 1: Analyzing an Image
{
    "analysis": "The user wants to know the colors in a logo. I have the logo file locally.",
    "reasoning": "I need to use a multimodal model to 'see' the image. The READ_MIME_FILES action is the correct tool. I will ask about the colors and provide the path to the image.",
    "actions": [{
        "action_type": "READ_MIME_FILES",
        "question": "What are the main colors visible in this logo?",
        "inputs": ["/home/agent/workspace/downloads/company_logo.png"]
    }]
}

#### Example 2: Summarizing a PDF and Saving Output
{
    "analysis": "The user wants a summary of a PDF report and wants it saved to a file.",
    "reasoning": "I will use READ_MIME_FILES to process the PDF. By providing the 'output' field, the tool will automatically handle saving the result, and I will just get a confirmation.",
    "actions": [{
        "action_type": "READ_MIME_FILES",
        "question": "Provide a concise summary of the executive summary section in this report.",
        "inputs": ["/home/agent/workspace/reports/quarterly_report_q3.pdf"],
        "output": "/home/agent/workspace/summaries/q3_exec_summary.txt"
    }]
}

#### Example 3: Understanding a YouTube video
{
    "analysis": "The user provided a YouTube link and asked what the video is about.",
    "reasoning": "The READ_MIME_FILES action can directly process YouTube links to analyze their content. I will pass the link directly in the 'inputs' field.",
    "actions": [{
        "action_type": "READ_MIME_FILES",
        "question": "What is this video about?",
        "inputs": ["https://www.youtube.com/watch?v=86y0gZnxuWE"]
    }]
}

#### When and How to use READ_MIME_FILES
One strategy for using READ_MIME_FILES is to apply it after performing headless browsing with tools like puppeteer. For instance, when developing frontend code, you might use headless browsing for testing.
Sometimes, your headless browsing script might only output text (e.g., writing to console logs). In these scenarios, READ_MIME_FILES isn't necessary. However, for tasks that involve capturing screenshots via headless browsing, READ_MIME_FILES can be used to analyze those images.
Additionally, the READ_MIME_FILES action is required when you need to analyze the content of specific file types, such as PDFs or images. This can be useful, for example, when performing web searches and needing to analyze files found in the search results.

Advanced scenario example: Web Browsing Workflow Example: Product Research Task

This example demonstrates the proper sequence of actions for web browsing tasks using edit_file, run_shell (with Playwright), and read_mime actions.

Scenario
A user requests: "Please visit the Tesla Model 3 product page, capture a screenshot of the main features section, and analyze what key features are highlighted."

Complete Agent Response Example:

{
    "analysis": "The user wants me to research Tesla Model 3 features by visiting their website. I need to: 1) Create a Playwright script to navigate and capture screenshots, 2) Execute the script, 3) Analyze the captured images to identify key features. This requires a multi-step approach using edit_file, run_shell, and read_mime actions.",
    "reasoning": "I'll start by creating a Playwright script to automate the web browsing task. The script will navigate to Tesla's Model 3 page, wait for content to load, and capture screenshots of the features section. Then I'll execute it and analyze the results.",
    "actions": [
        {
            "action_type": "EDIT_FILE",
            "directive_line": "NEW_FILE tesla_research.js",
            "content": "const { chromium } = require('playwright');\n\n(async () => {\n  const browser = await chromium.launch({ headless: true });\n  const context = await browser.newContext({\n    viewport: { width: 1920, height: 1080 },\n    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'\n  });\n  \n  const page = await context.newPage();\n  \n  try {\n    console.log('Navigating to Tesla Model 3 page...');\n    await page.goto('https://www.tesla.com/model3', { waitUntil: 'networkidle' });\n    \n    // Wait for page to fully load\n    await page.waitForTimeout(3000);\n    \n    // Capture full page screenshot\n    await page.screenshot({ \n      path: 'tesla_model3_full_page.png', \n      fullPage: true \n    });\n    console.log('Full page screenshot captured: tesla_model3_full_page.png');\n    \n    // Try to find and capture features section specifically\n    const featuresSection = await page.locator('[data-section=\"features\"], .features, #features, [class*=\"feature\"]').first();\n    if (await featuresSection.isVisible()) {\n      await featuresSection.screenshot({ path: 'tesla_features_section.png' });\n      console.log('Features section screenshot captured: tesla_features_section.png');\n    } else {\n      console.log('Specific features section not found, using full page screenshot');\n    }\n    \n    // Scroll down to capture more content\n    await page.evaluate(() => window.scrollTo(0, window.innerHeight));\n    await page.waitForTimeout(2000);\n    await page.screenshot({ \n      path: 'tesla_model3_scrolled.png'\n    });\n    console.log('Scrolled view screenshot captured: tesla_model3_scrolled.png');\n    \n    // Extract text content for analysis\n    const pageTitle = await page.title();\n    const headings = await page.locator('h1, h2, h3').allTextContents();\n    \n    console.log('Page Title:', pageTitle);\n    console.log('Main Headings:', headings.slice(0, 5));\n    \n  } catch (error) {\n    console.error('Error during browsing:', error);\n  } finally {\n    await browser.close();\n    console.log('Browser closed successfully');\n  }\n})();"
        },
        {
            "action_type": "RUN_SHELL_CMD",
            "command": "npm init -y && npm install playwright",
            "shell_cmd_timeout": 120
        },
        {
            "action_type": "RUN_SHELL_CMD",
            "command": "npx playwright install chromium",
            "shell_cmd_timeout": 180
        },
        {
            "action_type": "RUN_SHELL_CMD",
            "command": "node tesla_research.js",
            "shell_cmd_timeout": 60
        },
        {
            "action_type": "RUN_SHELL_CMD",
            "command": "ls -la *.png",
            "shell_cmd_timeout": 10
        },
        {
            "action_type": "READ_MIME_FILES",
            "question": "What are the key features of the Tesla Model 3 highlighted on this webpage? Please identify and list the main selling points, specifications, or features that are prominently displayed.",
            "inputs": ["tesla_model3_full_page.png", "tesla_model3_scrolled.png"],
            "output": "tesla_features_analysis.txt"
        },
        {
            "action_type": "RUN_SHELL_CMD",
            "command": "cat tesla_features_analysis.txt",
            "shell_cmd_timeout": 10
        }
    ]
}


"""

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        from anges.agents.agent_utils.mime_files_reader import read_mime_files_from_agent_request
        action_content = action_json
        reasoning = parsed_response_dict.get("reasoning", "")

        # Retrieve necessary context from run_config
        # Adjust these keys based on your actual run_config structure
        cmd_init_dir = run_config["cmd_init_dir"]
        event_stream = run_config["event_stream"]
        inference_func = run_config["inference_func"]
        message_handler_func = run_config["message_handler_func"]
        agent_message_base = run_config.get('agent_message_base', "")
        max_consecutive_actions_to_summarize = run_config["max_consecutive_actions_to_summarize"]

        action_logger = run_config.get("logger")

        message = f"{agent_message_base} wants to read mime files::\n\n{reasoning}"
        message_handler_func(message)

        # Execute the action
        action_output = read_mime_files_from_agent_request(action_content, cmd_init_dir)

        # Add event to the stream
        event_stream.events_list.append(
            Event(
                type=self.type,
                reasoning=reasoning,
                content=action_output, # Result or error message from the function
                analysis=parsed_response_dict.get("ANALYSIS", ""),
                message=message,
                # Placeholder token estimates
                est_input_token=parsed_response_dict.get("est_input_token", 0),
                est_output_token=parsed_response_dict.get("est_output_token", 0),
            )
        )

        append_events_summary_if_needed(event_stream, inference_func, max_consecutive_actions_to_summarize, run_config.get('agent_config'))
        save_event_stream(event_stream)
        action_logger.debug(
            f"Event {len(event_stream.events_list)}: Type={self.type}, Reasoning='{reasoning[:50]}...', Output='{action_output[:100]}...'"
        )

        return None # No need to return the event stream, it's already updated
