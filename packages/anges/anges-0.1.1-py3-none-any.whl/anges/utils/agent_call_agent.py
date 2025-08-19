import re

def parse_call_child_agent_content_json(call_child_agent_content_json):
  """
  TODO: Just use native JSON
  """

  # lines = call_child_agent_content_json.strip().split('\n')
  directive_line = call_child_agent_content_json['directive']
  # agent_input = '\n'.join(lines[1:]).strip()
  agent_input = call_child_agent_content_json.get('agent_input', '')

  agent_type = None
  agent_id = None

  if directive_line.startswith("NEW_CHILD_AGENT"):
    match = re.match(r"NEW_CHILD_AGENT\s+(\w+)", directive_line)
    if match:
      agent_type = match.group(1)
  elif directive_line.startswith("RESUME_CHILD_AGENT"):
    match = re.match(r"RESUME_CHILD_AGENT\s+(\w+)", directive_line)
    if match:
      agent_id = match.group(1)

  # Validate that we have at least one of agent_type and agent_id set
  if agent_type is None and agent_id is None:
    raise ValueError("Failed to parse call child agent action from content, no agent_type or agent_id found")

  # Validate that we don't have both agent_type and agent_id set
  if agent_type is not None and agent_id is not None:
    raise ValueError("Failed to parse call child agent action from content, both agent_type and agent_id exist")

  # Return the parsed values, with None for invalid cases
  return {
      "agent_type": agent_type,
      "agent_id": agent_id,
      "agent_input": agent_input
  }
