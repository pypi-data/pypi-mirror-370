import os
import difflib
from pathlib import Path
from typing import List, Optional # For type hinting

# --- Core Editing Logic (Handlers) ---
# These functions now perform the edit and return a simple success message.

def handle_new_file(file_path: str, text_block: str) -> str:
    """Creates a new file with the given content."""
    if os.path.exists(file_path):
        raise FileExistsError(f"File '{file_path}' already exists.")
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(text_block)
        return f"File created successfully: {file_path}\n" + "\n".join([f"{i+1}\t{line}" for i, line in enumerate(text_block.splitlines())])
    except Exception as e:
        raise OSError(f"Error creating file {file_path}: {e}")

def handle_insert_lines(file_path: str, line_number: int, text_block: str) -> str:
    """Inserts lines at the specified position in the file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    try:
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        raise OSError(f"Error reading file {file_path}: {e}")

    # Ensure each line in text_block ends with a newline
    insert_lines = [line if line.endswith("\n") else line + "\n"
                   for line in text_block.splitlines()]

    if line_number == 0:  # Insert at the start
        lines = insert_lines + lines
    elif line_number == -1:  # Append to the end
        if lines and not lines[-1].endswith("\n"): # Add newline to last line if needed
            lines[-1] = lines[-1].rstrip('\n') + "\n"
        lines.extend(insert_lines)
    else:  # Insert before specific line (1-based index)
        line_index = line_number - 1
        if not (0 <= line_index <= len(lines)):
             raise ValueError(f"Invalid line number {line_number} for insertion. File has {len(lines)} lines.")
        lines = lines[:line_index] + insert_lines + lines[line_index:]

    try:
        with open(file_path, "w", encoding='utf-8') as f:
            f.writelines(lines)
        return f"Lines inserted successfully: {file_path}\n"
    except Exception as e:
        raise OSError(f"Error writing updated file {file_path}: {e}")

def handle_remove_lines(file_path: str, start: int, end: int) -> str:
    """Removes lines within the specified 1-based range [start, end] (inclusive)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    try:
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        raise OSError(f"Error reading file {file_path}: {e}")

    # Convert 1-based inclusive range to 0-based exclusive range for slicing
    start_index = start - 1
    end_index = end # Slice up to, but not including, this index

    if start < 1 or end > len(lines) or start > end or start_index < 0:
        raise ValueError(f"Invalid line range: {start}-{end}.")

    lines = lines[:start_index] + lines[end_index:]

    try:
        with open(file_path, "w", encoding='utf-8') as f:
            f.writelines(lines)
        return f"Lines removed successfully: {file_path}\n"
    except Exception as e:
        raise OSError(f"Error writing updated file {file_path}: {e}")

def handle_replace_lines(file_path: str, start: int, end: int, text_block: str) -> str:
    """Replaces lines within the 1-based range [start, end] (inclusive) with new content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    try:
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        raise OSError(f"Error reading file {file_path}: {e}")

    # Convert 1-based inclusive range to 0-based exclusive range for slicing
    start_index = max(0, start - 1) # Clamp start_index at 0
    end_index = min(len(lines), end) # Clamp end_index at file length

    # Validate range *after* clamping (allows replacing beyond last line slightly)
    if start < 1 or end > len(lines) or start > end or start_index > end_index:
        raise ValueError(f"Invalid line range: {start}-{end}.")
    replace_lines_content = [line if line.endswith("\n") else line + "\n"
                           for line in text_block.splitlines()]

    lines = lines[:start_index] + replace_lines_content + lines[end_index:]

    try:
        with open(file_path, "w", encoding='utf-8') as f:
            f.writelines(lines)
        return f"Lines replaced successfully: {file_path}\n"
    except Exception as e:
        raise OSError(f"Error writing updated file {file_path}: {e}")


# --- Diff Generation Helper ---

def _generate_diff_output(file_path_str: str, content_before_lines: Optional[List[str]], command: str) -> str:
    """
    Generates a unified diff string comparing file content before and after an operation.
    """
    diff_text = ""
    content_after_lines = []
    file_path = Path(file_path_str)
    file_name_for_diff = file_path.name # Use just the filename in diff headers

    try:
        # Read content after the edit
        file_exists_after = file_path.exists()
        if file_exists_after:
            with open(file_path, "r", encoding='utf-8') as f:
                content_after_lines = f.readlines()

        # --- Calculate Diff ---
        from_file_label = f"a/{file_name_for_diff}"
        to_file_label = f"b/{file_name_for_diff}"
        context_lines = 10

        if content_before_lines is None and file_exists_after: # New file created
            return None # No diff needed for new file creation

        elif content_before_lines is not None and file_exists_after: # File modified
             if content_before_lines == content_after_lines:
                 diff_text = "No changes detected."
             else:
                 diff_lines = difflib.unified_diff(
                     content_before_lines, content_after_lines,
                     fromfile=from_file_label, tofile=to_file_label, n=context_lines, lineterm=''
                 )
                 diff_text = "".join(diff_lines)

        elif content_before_lines is not None and not file_exists_after: # File deleted
             to_file_label = "/dev/null" # Standard convention for deleted files
             diff_lines = difflib.unified_diff(
                 content_before_lines, [],
                 fromfile=from_file_label, tofile=to_file_label, n=context_lines, lineterm=''
             )
             diff_text = "".join(diff_lines)
             if not diff_text.strip(): # Check if the original file was empty
                 diff_text = f"File '{file_name_for_diff}' deleted (was empty)."
             # else: diff_text contains the content that was deleted

        # else: File did not exist before and does not exist now.
        # This could be a failed NEW_FILE or an operation on a non-existent file.
        # The error should be caught elsewhere, diff_text remains empty.

    except Exception as e:
        return f"Error generating diff for {file_path_str}: {e}"

    # Return the diff text, stripping leading/trailing whitespace for cleaner presentation
    return diff_text.strip()


# --- Dispatcher Function ---
# Receives the raw content, parses, dispatches to handlers, but uses resolved path.

def agent_file_editing_operation(content: str, cmd_init_dir: str = ".", resolved_file_path: Optional[str] = None) -> str:
    """
    Parses the directive and content, then calls the appropriate file editing handler.
    Uses pre-resolved absolute path if provided.
    """
    # Parse the directive line and validate the operation
    lines = content.strip().split("\n")
    directive = lines[0].split()
    if len(directive) < 2:
        raise ValueError("Invalid directive line format.")
    command = directive[0]
    file_path_rel_or_abs = directive[1] # Original path from directive

    # Use resolved path if provided, otherwise resolve it now
    if resolved_file_path:
        file_path = resolved_file_path
    else:
         # Resolve relative path based on cmd_init_dir
         if not file_path_rel_or_abs.startswith("/"):
             file_path = os.path.abspath(os.path.join(cmd_init_dir, file_path_rel_or_abs))
         else:
             file_path = file_path_rel_or_abs # It's already absolute

    operation_args = directive[2:] if len(directive) > 2 else []
    text_block = "\n".join(lines[1:]) if len(lines) > 1 else ""

    # Dispatch to the appropriate operation using the resolved file_path
    if command == "NEW_FILE":
        return handle_new_file(file_path, text_block)
    elif command == "INSERT_LINES":
        if not operation_args:
            raise ValueError("INSERT_LINES requires a line number.")
        try:
            line_num = int(operation_args[0])
        except ValueError:
            raise ValueError("INSERT_LINES requires an integer line number.")
        return handle_insert_lines(file_path, line_num, text_block)
    elif command == "REMOVE_LINES":
        if not operation_args or "-" not in operation_args[0]:
            raise ValueError("REMOVE_LINES requires a valid line range (e.g., x-y).")
        try:
            start, end = map(int, operation_args[0].split("-"))
        except ValueError:
             raise ValueError("REMOVE_LINES requires integer line numbers in x-y format.")
        return handle_remove_lines(file_path, start, end)
    elif command == "REPLACE_LINES":
        if not operation_args or "-" not in operation_args[0]:
            raise ValueError("REPLACE_LINES requires a valid line range (e.g., x-y).")
        try:
            start, end = map(int, operation_args[0].split("-"))
        except ValueError:
             raise ValueError("REPLACE_LINES requires integer line numbers in x-y format.")
        return handle_replace_lines(file_path, start, end, text_block)
    else:
        raise ValueError(f"Unsupported command: {command}")


# --- Top-Level Wrapper Function ---
# Orchestrates reading state, calling edit, generating diff, and formatting output.

def get_agent_file_editing_operation_output(content: str, cmd_init_dir: str = ".") -> str:
    """
    Main entry point. Handles an edit request string, performs the operation,
    generates a diff, and returns a formatted result string.
    """
    lines = content.strip().split("\n")
    if not lines:
        return "\n******\n- ERROR: Empty input.\n******\n"
    directive_line = lines[0]
    output = ""
    error_msg = ""
    operation_result_msg = "" # Stores simple success message from handler
    diff_output_text = ""   # Stores the generated diff or related messages
    file_path_str = ""
    content_before_lines: Optional[List[str]] = None
    command = ""

    try:
        # --- 1. Parse directive and resolve path ---
        directive_parts = directive_line.split()
        if len(directive_parts) < 2:
            raise ValueError("Invalid directive line format.")
        command = directive_parts[0]
        file_path_rel_or_abs = directive_parts[1]

        # Resolve path robustly using pathlib
        base_dir = Path(cmd_init_dir).resolve()
        file_path = Path(file_path_rel_or_abs)
        if not file_path.is_absolute():
            # Ensure joining works correctly even if cmd_init_dir is '.'
            file_path = (base_dir / file_path).resolve()
        file_path_str = str(file_path) # Use string path for os.path functions if needed

        # --- 2. Capture state before edit ---
        file_existed_before = file_path.exists()
        if command != "NEW_FILE" and file_existed_before:
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    content_before_lines = f.readlines()
            except Exception as e:
                # If reading fails, treat as if file didn't exist for diffing
                content_before_lines = None
                file_existed_before = False
                # Optionally log this warning
                print(f"Warning: Failed to read file '{file_path_str}' before edit: {e}")

        # --- 3. Perform the edit ---
        # Pass the resolved absolute path to the dispatcher
        operation_result_msg = agent_file_editing_operation(
            content, cmd_init_dir, resolved_file_path=file_path_str
        )

        # --- 4. Generate the diff ---
        # This is called even if the edit operation itself raised an error earlier,
        # but it will likely just report an error or no change if the file state is unexpected.
        diff_output_text = _generate_diff_output(
            file_path_str, content_before_lines, command
        )

    except Exception as e:
        # Catch errors from parsing, path resolution, or the edit operation itself
        error_msg = str(e)

    # --- 5. Format the final output ---
    output = "\n******\n"
    output += f"- FILE_EDITING_DIRECTIVE: {directive_line}\n"
    if error_msg:
        # If any error occurred, report it clearly
        output += f"\n- ERROR: {error_msg}\n"
    else:
        # If successful, report the operation result and the diff
        output += f"\n- RESULT: {operation_result_msg}\n"
        if diff_output_text:
            output += f"\n- CHANGES (diff format):\n```diff\n{diff_output_text}\n```\n"
        else:
            # Handle cases where diff is empty (e.g., no change, empty file)
            output += "\n- CHANGES: No textual changes detected or diff not applicable.\n"

    output += "\n******\n"
    return output
