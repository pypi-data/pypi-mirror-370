import json
import logging

from anges.agents.agent_utils.agent_actions import Action
from anges.agents.agent_utils.event_methods import append_events_summary_if_needed
from anges.agents.agent_utils.events import Event
from anges.utils.data_handler import save_event_stream
from anges.utils.mcp_manager import McpManager

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARNING)


class UseMCPToolAction(Action):
    def __init__(self, mcp_manager: McpManager):
        self.type = "USE_MCP_TOOL"
        self.user_visible = False
        self.unique_action = False
        self.returning_action = False
        self.mcp_manager:McpManager = mcp_manager
        # Will be dynamically generated
        self._guide_prompt = """
### USE_MCP_TOOL:
Use this action to call MCP (Model Context Protocol) tools from connected MCP servers. This action provides access to external tools and services through standardized MCP protocol.

The action object must contain:
- `action_type`: "USE_MCP_TOOL"
- `mcp_server_name` (string, required): The name of the MCP server to use
- `tool_name` (string, required): The name of the tool to call on the MCP server  
- `tool_args` (object, required): The arguments to pass to the tool (must match the tool's input schema)

#### Available MCP Servers and Tools:
{available_tools}

#### Tool Usage Guidelines:
- Choose the appropriate server name from the available servers listed above
- Ensure tool arguments match the required schema exactly  
- Check parameter types and required fields before making the call
- Some tools may depend on previous tool outputs or external resources

#### Example 1: Simple Tool Call
{{
    "analysis": "The user wants to use a specific MCP tool to accomplish their task.",
    "reasoning": "I need to call the appropriate MCP tool with the correct parameters to fulfill the user's request.",
    "actions": [{{
        "action_type": "USE_MCP_TOOL",
        "mcp_server_name": "example_server",
        "tool_name": "example_tool",
        "tool_args": {{
            "param1": "value1",
            "param2": "value2"
        }}
    }}]
}}
"""
        
    @property
    def guide_prompt(self) -> str:
        """Dynamically generate guide_prompt based on available MCP tools"""
        available_tools_formatted = self._format_available_tools()
        if available_tools_formatted is None:
            return ""
        return self._guide_prompt.format(
            available_tools=available_tools_formatted
        )
    
    def _format_available_tools(self) -> str|None:
        """Format available MCP tools into a readable string"""

        if not self.mcp_manager:
            return None
        
        try:
            # Get all tools info from mcp_manager using the actual API
            all_tools_info = {}
            for mcp_name, mcp_client in self.mcp_manager.mcp_clients.items():
                try:
                    tools = self.mcp_manager.list_client_tools(mcp_name)
                    all_tools_info[mcp_name] = tools
                except Exception:
                    pass
            
            if not all_tools_info:
                return None
            
            formatted_sections = []
            
            for server_name, tools_list in all_tools_info.items():
                if not tools_list:
                    continue
                    
                server_section = f"\n**{server_name}** MCP Server:\n"
                
                for tool in tools_list:
                    # Tool is a Tool object from MCP, access its attributes directly
                    tool_name = getattr(tool, 'name', 'Unknown')
                    tool_desc = getattr(tool, 'description', 'No description available')
                    if tool_desc:
                        tool_desc = tool_desc.strip()
                    else:
                        tool_desc = 'No description available'
                    
                    # Format input schema
                    input_schema = getattr(tool, 'inputSchema', {})
                    required_params = input_schema.get('required', []) if input_schema else []
                    properties = input_schema.get('properties', {}) if input_schema else {}
                    
                    params_info = []
                    for param_name, param_info in properties.items():
                        param_type = param_info.get('type', 'unknown')
                        is_required = param_name in required_params
                        param_title = param_info.get('title', param_name)
                        required_marker = " (required)" if is_required else " (optional)"
                        params_info.append(f"    - `{param_name}` ({param_type}){required_marker}: {param_title}")
                    
                    params_str = "\n".join(params_info) if params_info else "    - No parameters required"
                    
                    # Format output schema  
                    output_schema = getattr(tool, 'outputSchema', {})
                    output_title = output_schema.get('title', 'Tool execution result') if output_schema else 'Tool execution result'
                    
                    tool_section = f"""  - **{tool_name}**: {tool_desc}
    - Input parameters:
{params_str}
    - Output: {output_title}"""
                    
                    server_section += tool_section + "\n"
                
                formatted_sections.append(server_section)
            
            return "\n".join(formatted_sections) if formatted_sections else None
            
        except Exception as e:
            logger.error("Error formatting available MCP tools: %s", e)
            return None
    

    def handle_action_in_parsed_response(self, run_config, parsed_response_dict, action_json):
        action = action_json
        mcp_server_name = action.get("mcp_server_name", "")
        tool_name = action.get("tool_name", "")
        tool_args = action.get("tool_args", {})

        reasoning = parsed_response_dict.get("reasoning", "")
        event_stream = run_config["event_stream"]
        inference_func = run_config["inference_func"]
        max_consecutive_actions_to_summarize = run_config["max_consecutive_actions_to_summarize"]
        message = f"{run_config['agent_message_base']} wants to use MCP tool:\n\nServer: {mcp_server_name}\nTool: {tool_name}\nArgs: {tool_args}\n\n{reasoning}"

        
        if not mcp_server_name or not tool_name:
            result_content = "Missing required fields: mcp_server_name and tool_name are required"
        else:
            try:
                # Call the MCP tool using the correct API
                result_content = self.mcp_manager.call_mcp_tool(mcp_server_name, tool_name, tool_args)
                try:
                    result_content = json.dumps(result_content)
                except Exception:
                    result_content = str(result_content)
            except Exception as e:
                result_content = f"Unexpected error calling MCP tool: {str(e)}"
        
                    
        event_stream.events_list.append(
            Event(
                type="mcp_tool_call",
                reasoning=reasoning,
                content=result_content,
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
            f"Event {len(event_stream.events_list)}: MCP Tool Call - Server: {mcp_server_name}, Tool: {tool_name}, Result: {result_content[:100]}..."
        )
        
        return event_stream