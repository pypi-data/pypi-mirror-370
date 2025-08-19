import re
import json
from typing import Callable, Dict, Any, List


def parse_response_text(response_text: str) -> dict:
    # Split into lines while preserving empty lines

    cleaned_text = re.sub(r'(\S)(KEY_WORD_TAG::\w+::(?:START|END))', r'\1\n\2', response_text)
    lines = cleaned_text.strip().split("\n")

    # Find tag boundaries and validate structure
    result = {}
    current_tag = None
    content_start = None
    tag_stack = []

    for i, line in enumerate(lines):
        if "KEY_WORD_TAG::" in line:
            match = re.match(r"\s*KEY_WORD_TAG::(\w+)::(START|END)", line)
            if match:
                tag_name, tag_type = match.groups()
                if tag_type == "START":
                    if tag_stack:  # Already have an active tag
                        # Treat the outermost tag as the main tag
                        tag_stack.append(tag_name)
                    else:
                        tag_stack.append(tag_name)
                        current_tag = tag_name
                        content_start = i + 1
                else:  # END tag
                    if not tag_stack:
                        raise ValueError("Unmatched tags found")
                    if tag_stack[-1] != tag_name:
                        raise ValueError("Unmatched tags found")
                    tag_stack.pop()
                    if not tag_stack:
                        # Get the exact content lines without modification
                        content_lines = lines[content_start:i]
                        result[tag_name] = "\n".join(content_lines)
                        current_tag = None
                        content_start = None

    if tag_stack:
        raise ValueError("Unmatched tags found")

    return result

def get_valid_response_json(
    prompt: str,
    inference_func: Callable[[str, float], str],
    logger: Any,
    retries: int = 5,
    temperature: float = 0.5,
    temp_increment: float = 0.1,
    valid_action_list = []
) -> Dict[str, Any]:
    error_feedback = ""
    for attempt in range(retries):
        try:
            current_prompt = f"{prompt}\n{error_feedback}" if error_feedback else prompt
            logger.debug(f"PROMPT (Attempt {attempt + 1}/{retries}): {current_prompt}")

            response_text = inference_func(current_prompt, temperature=temperature)
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3]

            logger.debug(f"RAW RESPONSE: {response_text}")

            # Check if response is valid JSON
            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError as e:
                error_feedback = f"!! Your previous response was not valid JSON:\n{response_text}\nError: {e}\nPlease provide a valid JSON response."
                raise ValueError(error_feedback)

            # Check if the basic structure is correct
            required_keys = ["reasoning", "actions"]
            missing_keys = [key for key in required_keys if key not in parsed_response]
            if missing_keys:
                error_feedback = f"!! Your previous response was missing required keys: {', '.join(missing_keys)}.\nIncorrect response: {response_text}\nPlease include all required keys in your JSON output."
                raise ValueError(error_feedback)

            # Check if actions is a list and contains at least one action
            actions = parsed_response.get("actions", [])
            if len(actions) == 0:
                error_feedback = f"!! Your previous response did not include any actions. Please ensure to include at least one action in your response. Incorrect response: {response_text}"
                raise ValueError(error_feedback)

            # Check if all actions are in the valid_action_list
            valid_action_type_set = set([a.type.lower() for a in valid_action_list])
            called_action_type_set = set([action.get("action_type", "").lower() for action in actions])
            if not called_action_type_set.issubset(valid_action_type_set):
                invalid_actions = called_action_type_set - valid_action_type_set
                error_feedback = f"!! Your previous response included invalid actions: {', '.join(invalid_actions)}. Please ensure to use only the following valid actions: {', '.join(valid_action_type_set)}. Incorrect response: {response_text}"
                raise ValueError(error_feedback)
            
            # Check if there is only one unique action
            unique_action_type_set = set([a.type.lower() for a in valid_action_list if a.unique_action])
            has_unique_action = any([ca in unique_action_type_set for ca in called_action_type_set])
            if has_unique_action and len(actions) > 1:
                error_feedback = f"!! Your previous response included multiple actions while a unique action is included. Please ensure to include only one unique action in your response. Incorrect response: {response_text}"
                raise ValueError(error_feedback)

            parsed_response["est_input_token"] = estimate_token_count(current_prompt)
            parsed_response["est_output_token"] = estimate_token_count(response_text)
            logger.debug(f"Successfully received and parsed valid JSON response: {response_text}")
            return parsed_response

        except ValueError as e:
            logger.warning(f"Validation failed on attempt {attempt + 1}: {e}")
            temperature += temp_increment

    error_message = f"Failed to get a valid response after {retries} retries for prompt:\n{prompt}\nLast error: {error_feedback}"
    raise ValueError(error_message)    


def estimate_token_count(text):
    """
    Estimates the number of tokens in a string using a general-purpose approach.

    This function is not tied to a specific model or provider and offers a rough approximation.

    Args:
        text: The input string.

    Returns:
        An estimated token count (integer).
    """
    # Very simple approximation:
    # 1. Split the text into words by spaces and punctuation.
    # 2. Assume each word is about 1 token, adjust slightly for longer words.

    words = text.split()
    num_words = len(words)

    # Heuristic:
    # - For shorter texts, add a small buffer (e.g., 10% extra).
    # - For very long texts, words might average a little more than 1 token each.
    if num_words < 50:
        token_estimate = int(num_words * 1.1)
    elif num_words < 500:
        token_estimate = int(num_words * 1.15)
    else:
        token_estimate = int(num_words * 1.2)
    return token_estimate