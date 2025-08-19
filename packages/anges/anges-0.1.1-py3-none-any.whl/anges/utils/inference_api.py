from openai import OpenAI
from anthropic import AnthropicVertex
import anthropic
import logging
import functools
import time
from anges.config import config
import os


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or config.model_api.openai.api_key or ""
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or config.model_api.deepseek.api_key or ""
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or config.model_api.genai_gemini.api_key or ""
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY") or config.model_api.anthropic.api_key or ""


# Default model versions from configuration
OAI_MODEL = config.model_api.openai.model

CLAUDE_MODEL = config.model_api.anthropic.model

ANTHROPIC_CLAUDE_CLIENT = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

GEMINI_MODEL = config.model_api.gemini.model

DEEPSEEK_MODEL = config.model_api.deepseek.model
VERTEX_CLAUDE_MODEL = config.model_api.vertex_claude.model
VERTEX_GCP_REGION = config.model_api.vertex_claude.gcp_region
VERTEX_GCP_PROJECT = config.model_api.vertex_claude.gcp_project
VERTEX_CLAUDE_CLIENT = AnthropicVertex(region=VERTEX_GCP_REGION, project_id=VERTEX_GCP_PROJECT)


# Setup clients
OAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)


def retry_on_quota_exceeded(max_attempts=30, initial_delay=1.0, backoff_factor=2):
    """A decorator for retrying a function call with exponential backoff on quota errors.

    Retries if the error message contains "Quota exceeded" or "Content has no parts".

    Args:
        max_attempts: Maximum number of attempts.
        initial_delay: Initial delay between retries in seconds.
        backoff_factor: Factor by which the delay increases after each retry.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            delay = initial_delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if (
                        "429" in str(e)
                        or "529" in str(e)
                        or "503" in str(e)
                        or "Quota exceeded" in str(e)
                        or "Content has no parts" in str(e)
                        or "Cannot get the response text" in str(e)
                    ) and attempts < max_attempts:
                        logging.warning(
                            f"Retriable error: {e}, retrying {attempts + 1}/{max_attempts} in {delay:.1f}s"
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                        attempts += 1
                    else:
                        logging.error(f"Final attempt failed or non-quota error: {e}")
                        raise
        return wrapper
    return decorator


def deepseek_inference(prompt, temperature=0.6):
    """Performs inference using Deepseek's API."""
    from openai import OpenAI
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        stream=False
    )
    response_text = response.choices[0].message.content
    if "</think>" in response_text:
        response_text = response_text.split("</think>")[-1]
    return response_text


def openai_inference(prompt, temperature=0.3):
    """Performs inference using OpenAI's API."""
    completion = OAI_CLIENT.chat.completions.create(
        model=OAI_MODEL,
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return completion.choices[0].message.content


def anthropic_claude_inference(prompt, temperature=0.3):
    """Performs inference using Anthropic's API."""
    message = ANTHROPIC_CLAUDE_CLIENT.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8096,
        temperature=temperature,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ]
            }
        ]
    )
    return message.content[0].text


@retry_on_quota_exceeded()
def vertex_claude_inference(prompt, temperature=0.6, enforce_json=False):
    """Performs inference using Anthropic's Claude API via Vertex AI."""
    message = VERTEX_CLAUDE_CLIENT.messages.create(
        max_tokens=8096,
        messages=[{"role": "user", "content": prompt}],
        model=VERTEX_CLAUDE_MODEL,
        temperature=temperature,
    )
    return message.content[0].text


@retry_on_quota_exceeded()
def genai_gemini_model(prompt, temperature: float = 0.3, enforce_json=False):
    from google import genai
    from google.genai import types
    api_key = GEMINI_API_KEY
    client = genai.Client(
        api_key=api_key,
    )
    model = config.model_api.genai_gemini.model
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    mime_type = "application/json" if enforce_json else "text/plain"
    generate_content_config = types.GenerateContentConfig(
        response_mime_type=mime_type,
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    return response.text


@retry_on_quota_exceeded()
def gemini_inference(prompt, temperature: float = 0.3, enforce_json=True):
    from google import genai
    from google.genai import types
    api_key = GEMINI_API_KEY
    if api_key:
        client = genai.Client(
            api_key=api_key,
        )
    else:
        client = genai.Client(
            vertexai=True,
            project=VERTEX_GCP_PROJECT,
            location="global",
        )
    model = config.model_api.gemini.model
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    if enforce_json:
        mime_type = "application/json"
    else:
        mime_type = "text/plain"
    generate_content_config = types.GenerateContentConfig(
        response_mime_type=mime_type,
        temperature=temperature,
        safety_settings = [types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="OFF"
        ),types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="OFF"
        )],
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    return response.text

# Dictionary mapping inference function names to their implementations
INFERENCE_FUNC_DICT = {
    "openai": openai_inference,
    "vertex_claude": vertex_claude_inference,
    "gemini": gemini_inference,
    "genai_gemini": genai_gemini_model,
    "deepseek": deepseek_inference,
    "claude": anthropic_claude_inference,
}
