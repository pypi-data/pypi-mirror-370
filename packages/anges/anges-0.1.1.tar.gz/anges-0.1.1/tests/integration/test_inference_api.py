import pytest
import os
from anges.utils.inference_api import INFERENCE_FUNC_DICT
# from anges.utils.panel_discussion import build_agent_panel

# assert os.environ.get("OPENAI_API_KEY") is not None
# assert os.environ.get("DEEPSEEK_API_KEY") is not None
# assert os.environ.get("ANTHROPIC_API_KEY") is not None

simple_test_cases = [
    (
        "What is the capital of France? One word answer only.",
        "Paris",
    ),
    (
        "Translate 'hello' to Spanish. One word answer only.",
        "Hola",
    ),
    (
        "What is 2 + 2? Answer with the one digit only.",
        "4",
    ),
    (
        "What is the greatest common divisor of 30 and 36? Answer with the digit only without anything other words.",
        "6",
    ),
    (
        "Is the Earth flat? Answer with only 'yes' or 'no' in lowercase.",
        "no",
    ),
]

inference_func_names = [
    # "oai",
    "vertex_claude",
    "gemini",
    # "deepseek",
    # "anthropic_claude", 
]

@pytest.mark.parametrize("prompt, expected_response", simple_test_cases)
@pytest.mark.parametrize("func_name", inference_func_names)
def test_inference_func_dict(prompt, expected_response, func_name):
    inference_func = INFERENCE_FUNC_DICT[func_name]
    response = inference_func(prompt, temperature=0.5, enforce_json=False).strip().lower().replace(".", "")
    assert response == expected_response.lower()


# Example individual tests
# @pytest.mark.parametrize("prompt, expected_response", simple_test_cases)
# def test_claude_inference(prompt, expected_response):
#     response = claude_inference(prompt, temperature=0.5).strip().lower().replace(".", "")
#     assert response == expected_response.lower()

# Panel discussion is currently not in use
# @pytest.mark.parametrize("prompt, expected_response", simple_test_cases)
# def test_panel_inference(prompt, expected_response):
#     agent_panel = build_agent_panel()
#     response = agent_panel.panel_inference(prompt).strip().lower().replace(".", "")
#     assert response == expected_response.lower()