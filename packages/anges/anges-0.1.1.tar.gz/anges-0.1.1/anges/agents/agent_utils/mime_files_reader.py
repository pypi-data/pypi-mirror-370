from mime_files_reader import MimeFilesReader
from anges.config import config
import os
import json

def get_mime_reader_instance(working_directory: str) -> MimeFilesReader:
    """Retrieves or creates the MimeFilesReader instance."""
    # This is a placeholder. Implement how your application accesses
    # the initialized MimeFilesReader (e.g., singleton, dependency injection).
    # Ensure API key and model are configured correctly.
    api_key = os.environ.get("GEMINI_API_KEY")
    model_name = config.action_defaults.mime_reader_model
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set for MimeFilesReader.")
    # Consider efficiency if creating a new instance on every call.
    return MimeFilesReader(google_genai_key=api_key, model_name=model_name, working_dir=working_directory)

def read_mime_files_from_agent_request(action_content: str, working_directory: str) -> str:
    """
    Parses the agent's JSON request, calls MimeFilesReader.read, returns result/error.
    """
    try:
        if isinstance(action_content, str):
            request_data = json.loads(action_content)
        elif isinstance(action_content, dict):
            request_data = action_content
        else:
            raise ValueError("Invalid action content format. Expected JSON string or dictionary.")
        question = request_data.get("question")
        inputs = request_data.get("inputs")
        output_path = request_data.get("output", "") # Optional
        error_msg = None
        output_content = ""

        if not question or not isinstance(question, str):
            error_msg = "Error: Missing or invalid 'question' (string) in READ_MIME_FILES JSON."
        if not inputs or not isinstance(inputs, list) or not all(isinstance(f, str) for f in inputs):
            error_msg = "Error: Missing or invalid 'inputs' (list of strings) in READ_MIME_FILES JSON."

        # IMPORTANT: Ensure file paths are accessible from the execution environment.
        # The 'working_directory' might be used by the reader if paths are relative.
        reader = get_mime_reader_instance(working_directory)

        # Note: reader.read itself is synchronous in the current implementation.
        # If the agent framework is async, consider running this in a thread pool.
        result = reader.read(
            question=question,
            inputs=inputs,
            output=output_path
            # auto_cleanup defaults to True in MimeFilesReader
        )
        output_content = result

    except json.JSONDecodeError:
        error_msg = "Error: Invalid JSON format provided for READ_MIME_FILES."
    except FileNotFoundError as e:
        error_msg = f"Error: File not found - {e}"
    except ValueError as e: # Catches reader's validation errors
        error_msg = f"Error: Invalid input or configuration - {e}"
    except Exception as e:
        error_msg = f"Error: An unexpected error occurred: {e}"

    output = "\n******\n"
    output += f"- READ_MIME_FILES request:\n{action_content}\n"
    if error_msg:
        # If any error occurred, report it clearly
        output += f"\n- ERROR: {error_msg}\n"
    else:
        # If successful, report the operation result and the diff
        output += f"\n- READ_MIME_FILES_OUTPUT_CONTENT:\n{output_content}\n"

    output += "\n******\n"
    return output
