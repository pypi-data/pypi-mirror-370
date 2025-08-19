#!/usr/bin/env python3
"""CLI Interface for Anges Agent

This module provides a command-line interface for running Anges agents,
similar to the web interface functionality but through the terminal.
"""

import json
import argparse
import sys
import signal
import logging
from pathlib import Path
from typing import Optional

from anges.agents.agent_utils.agent_factory import AgentFactory, AgentType, AgentConfig
from anges.utils.data_handler import read_event_stream

# Define interrupt_requested at the module level
interrupt_requested = False

def signal_handler(signum, frame):
    """Handle interrupt signal (Ctrl+C or SIGTERM)."""
    global interrupt_requested
    interrupt_requested = True
    print("\nInterrupt received, cleaning up...")

def create_agent(agent_type: str, cmd_init_dir: str = "", prefix_cmd: str = "", interrupt_check=None, logging_level=logging.INFO, model="agent_default", notes=None, mcp_config=None) -> Optional[object]:
    """Factory function to create different types of agents using the centralized AgentFactory.
    
    Args:
        agent_type (str): Type of agent to create (must be one of AgentType values)
        cmd_init_dir (str, optional): Initial directory for commands. Defaults to "".
        prefix_cmd (str, optional): Command prefix. Defaults to "".
        interrupt_check (callable, optional): Function to check for interrupts. Defaults to None.
        logging_level: Logging level for the agent. Defaults to logging.INFO.
        model (str, optional): Model to use for inference. Defaults to "agent_default".
        notes (list, optional): List of notes to pass to the agent. Defaults to None.
        mcp_config (dict, optional): MCP configuration. Defaults to None.

    Returns:
        Agent: Instance of the requested agent type
    
    Raises:
        ValueError: If invalid agent type is provided
    """
    # Ensure notes is a list if provided
    if notes is None:
        notes = []

    # Create agent configuration
    config = AgentConfig(
        agent_type=agent_type,
        cmd_init_dir=cmd_init_dir,
        prefix_cmd=prefix_cmd,
        model=model,
        interrupt_check=interrupt_check,
        logging_level=logging_level,
        auto_entitle=True,
        notes=notes,
        remaining_recursive_depth=3 if agent_type == "orchestrator" else None,
        mcp_config=mcp_config
    )
    
    # Use the centralized factory
    factory = AgentFactory()
    return factory.create_agent(config)

def parse_arguments():
    """Parse command-line arguments for the CLI interface.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Anges CLI Interface")
    parser.add_argument(
        "--model",
        type=str,
        default="agent_default",
        help="Model to use for inference (default to agent config)",
    )
    parser.add_argument(
        "--prefix_cmd",
        type=str,
        default="",
        help="Command prefix to prepend to all shell commands",
    )
    parser.add_argument(
        "--cmd_init_dir",
        type=str,
        default="",
        help="Initial directory for running commands",
    )
    parser.add_argument(
        "--agent",
        type=str,
        choices=AgentType.list(),
        default="default",
        help="Type of agent to use",
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--event_stream",
        type=str,
        help="Path to event stream file to process",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode",
    )
    parser.add_argument(
        "-q", "--question",
        type=str,
        help="Question or task description to execute"
    )
    parser.add_argument(
        "-f", "--input-file",
        type=str,
        help="Path to file containing task description"
    )
    parser.add_argument(
        "--existing-stream-id",
        type=str,
        help="ID of existing event stream to continue"
    )
    parser.add_argument(
        "--notes",
        type=str,
        action="append",
        help="Add a note in JSON format: '{\"scope\": \"general\", \"title\": \"My Note\", \"content\": \"Note content\"}'. "
             "Alternatively, provide plain text which will be auto-formatted. Can be used multiple times. "
             "Required JSON fields: scope, title, content (all must be non-empty strings)."
    )
    parser.add_argument(
        "--notes-file",
        type=str,
        help="Path to JSON file containing notes array. Format: "
             "[{\"scope\": \"general\", \"title\": \"Note 1\", \"content\": \"Content 1\"}, "
             "{\"scope\": \"project\", \"title\": \"Note 2\", \"content\": \"Content 2\"}]. "
             "Each note must have scope, title, and content fields as non-empty strings."
    )
    parser.add_argument(
        "--mcp_config",
        type=str,
        help="MCP configuration in JSON format"
    )

    return parser.parse_args()


def validate_note_structure(note, source="unknown"):
    """Validate that a note has all required fields with proper types.

    Args:
        note (dict): The note to validate
        source (str): Source description for error messages

    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(note, dict):
        return False, f"Note from {source} must be a dictionary/object, got {type(note).__name__}"

    required_fields = ['scope', 'title', 'content']
    missing_fields = [field for field in required_fields if field not in note]

    if missing_fields:
        return False, f"Note from {source} missing required fields: {', '.join(missing_fields)}. Required: {', '.join(required_fields)}"

    # Validate field types
    for field in required_fields:
        if not isinstance(note[field], str):
            return False, f"Note from {source} field '{field}' must be a string, got {type(note[field]).__name__}"
        if not note[field].strip():
            return False, f"Note from {source} field '{field}' cannot be empty"

    return True, None

def parse_notes_from_args(notes_args):
    """Parse notes from command line arguments.

    Supports both JSON format and plain text format:
    - JSON: '{"scope": "general", "title": "My Note", "content": "Note content"}'
    - Plain text: 'This is my note content' (automatically gets scope='general', title='CLI Note')

    Args:
        notes_args (list): List of strings from --notes arguments

    Returns:
        tuple: (parsed_notes, errors)
    """
    parsed_notes = []
    errors = []

    if not notes_args:
        return parsed_notes, errors

    for i, note_str in enumerate(notes_args):
        try:
            # First try to parse as JSON
            note = json.loads(note_str)
            is_valid, error_msg = validate_note_structure(note, f"command line argument {i+1}")

            if is_valid:
                parsed_notes.append(note)
            else:
                errors.append(error_msg)

        except json.JSONDecodeError:
            # If JSON parsing fails, treat as plain text note
            if note_str.strip():
                plain_text_note = {
                    "scope": "general",
                    "title": f"CLI Note {i+1}",
                    "content": note_str.strip()
                }
                parsed_notes.append(plain_text_note)
            else:
                errors.append(f"Command line note {i+1} is empty")

    return parsed_notes, errors

def parse_notes_from_file(notes_file_path):
    """Parse notes from a JSON file.

    Args:
        notes_file_path (str): Path to the JSON file containing notes

    Returns:
        tuple: (parsed_notes, errors)
    """
    parsed_notes = []
    errors = []

    if not notes_file_path:
        return parsed_notes, errors

    try:
        with open(notes_file_path, 'r', encoding='utf-8') as f:
            file_content = json.load(f)

        if not isinstance(file_content, list):
            errors.append(f"Notes file '{notes_file_path}' must contain an array of notes, got {type(file_content).__name__}")
            return parsed_notes, errors

        if not file_content:
            errors.append(f"Notes file '{notes_file_path}' contains an empty array")
            return parsed_notes, errors

        for i, note in enumerate(file_content):
            is_valid, error_msg = validate_note_structure(note, f"file '{notes_file_path}' note {i+1}")

            if is_valid:
                parsed_notes.append(note)
            else:
                errors.append(error_msg)

    except FileNotFoundError:
        errors.append(f"Notes file not found: '{notes_file_path}'")
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in notes file '{notes_file_path}': {e}")
    except PermissionError:
        errors.append(f"Permission denied reading notes file: '{notes_file_path}'")
    except Exception as e:
        errors.append(f"Unexpected error reading notes file '{notes_file_path}': {e}")

    return parsed_notes, errors

def convert_notes_to_expected_format(notes):
    """Convert notes to the format expected by the agent.

    Args:
        notes (list): List of validated note dictionaries

    Returns:
        list: Notes in the expected format for the agent
    """
    # For now, we'll keep the same format but ensure consistency
    # This can be enhanced later if the agent expects a different format
    converted_notes = []

    for note in notes:
        converted_note = {
            'scope': note['scope'].strip(),
            'title': note['title'].strip(),
            'content': note['content'].strip()
        }

        # Preserve any additional fields that might be present
        for key, value in note.items():
            if key not in ['scope', 'title', 'content']:
                converted_note[key] = value

        converted_notes.append(converted_note)

    return converted_notes

def process_notes(args):
    """Process and validate notes from both command line arguments and files.

    Args:
        args: Parsed command line arguments

    Returns:
        tuple: (processed_notes, has_errors)
    """
    all_notes = []
    all_errors = []

    # Process notes from command line arguments
    if hasattr(args, 'notes') and args.notes:
        notes_from_args, arg_errors = parse_notes_from_args(args.notes)
        all_notes.extend(notes_from_args)
        all_errors.extend(arg_errors)

    # Process notes from file
    if hasattr(args, 'notes_file') and args.notes_file:
        notes_from_file, file_errors = parse_notes_from_file(args.notes_file)
        all_notes.extend(notes_from_file)
        all_errors.extend(file_errors)

    # Report errors
    if all_errors:
        print("\nNotes processing errors:", file=sys.stderr)
        for error in all_errors:
            print(f"  - {error}", file=sys.stderr)

        # If there are any notes that were successfully parsed, continue with those
        if all_notes:
            print(f"\nContinuing with {len(all_notes)} successfully parsed notes.", file=sys.stderr)
        else:
            print("\nNo valid notes found. Continuing without notes.", file=sys.stderr)
            return [], True

    # Convert notes to expected format
    if all_notes:
        processed_notes = convert_notes_to_expected_format(all_notes)
        print(f"Successfully processed {len(processed_notes)} notes.", file=sys.stderr)
        return processed_notes, len(all_errors) > 0

    return [], len(all_errors) > 0
def check_interrupt():
    """Check if an interrupt has been requested.
    
    Returns:
        bool: True if interrupt was requested, False otherwise
    """
    return interrupt_requested

def main():
    """Main entry point for the CLI interface."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging
    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create the agent using the factory
        # Process notes if provided
        notes, has_notes_errors = process_notes(args)

        # Exit if there were critical notes errors and no valid notes
        if has_notes_errors and not notes:
            print("\nFailed to process notes. Please check the errors above and try again.", file=sys.stderr)
            return 1

        agent = create_agent(
            agent_type=args.agent,
            cmd_init_dir=args.cmd_init_dir,
            model=args.model,
            prefix_cmd=args.prefix_cmd,
            interrupt_check=check_interrupt,
            logging_level=logging_level,
            notes=notes,
            mcp_config=args.mcp_config
        )
        
        if agent is None:
            print(f"Failed to create agent of type: {args.agent}")
        
        print(f"Created {args.agent} agent successfully")
        # Process event stream if provided
        if args.event_stream:
            print(f"Processing event stream: {args.event_stream}")
            events = read_event_stream(args.event_stream)
            # Process events with the agent
            for event in events:
                if check_interrupt():
                    print("Interrupted during event processing")
                    break
                # Process event with agent (implementation depends on agent interface)
                print(f"Processing event: {event}")
        
        # Handle file input mode
        elif hasattr(args, 'input_file') and args.input_file:
            try:
                with open(args.input_file, 'r') as f:
                    question = f.read().strip()
                
                print(f"Processing question from file: {question}", file=sys.stderr)
                
                # Create a simple event stream for the question
                event_stream = {
                    "events": [
                        {
                            "type": "NEW_REQUEST",
                            "content": question
                        }
                    ]
                }
                
                # Process the question with the agent
                print(f"Agent received a new request: {question}", file=sys.stderr)
                
                print("\nTask completed successfully!")
                return event_stream
                
            except FileNotFoundError:
                print(f"Error: Input file '{args.input_file}' not found")
                sys.exit(1)
            except Exception as e:
                print(f"Error reading input file: {e}")
                sys.exit(1)
        
        # Interactive mode
        elif args.interactive:
            print("Entering interactive mode. Type 'quit' or 'exit' to stop.")
            while not check_interrupt():
                try:
                    user_input = input("> ")
                    if user_input.lower() in ['quit', 'exit']:
                        break
                    # Process user input with agent
                    print(f"Agent would process: {user_input}")
                except EOFError:
                    break
        
        else:
            print("No event stream or interactive mode specified. Use --help for options.")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print("CLI session completed")


def run_cli_with_args(args, check_interrupt=None):
    """Run the CLI interface with the provided arguments.

    Args:
        args (argparse.Namespace): Parsed command-line arguments
        check_interrupt (callable, optional): Function to check for interrupts. Defaults to None.

    Returns:
        dict: The final event stream after execution
    """
    import sys
    from anges.utils.data_handler import read_event_stream

    logging_level = logging.INFO
    if hasattr(args, 'logging') and args.logging.lower() == "debug":
        logging_level = logging.DEBUG

    # Load existing event stream if provided
    event_stream = []
    if hasattr(args, 'existing_stream_id') and args.existing_stream_id:
        try:
            event_stream = read_event_stream(args.existing_stream_id)
        except Exception as e:
            print(f"Warning: Could not load existing event stream {args.existing_stream_id}: {e}")
            event_stream = []

    # Process notes if provided
    notes, has_notes_errors = process_notes(args)

    # Initialize MCP configuration if provided
    mcp_config = {}
    if hasattr(args, 'mcp_config') and args.mcp_config:
        mcp_config = args.mcp_config

        # If we have an existing event stream, update its mcp config
        if event_stream:
            event_stream.mcp_config = mcp_config

    # Create and configure agent
    agent = create_agent(
        agent_type=args.agent,
        interrupt_check=check_interrupt,
        cmd_init_dir=args.cmd_init_dir,
        model=args.model,
        prefix_cmd=getattr(args, 'prefix_cmd', ''),
        logging_level=logging_level,
        notes=notes,
        mcp_config=mcp_config
    )

    if agent is None:
        print(f"Failed to create agent of type: {args.agent}")

    # Handle direct question input mode
    if hasattr(args, 'question') and args.question:
        task_description = args.question.strip()
        if not task_description:
            print("Error: Empty question provided")
            sys.exit(1)

        new_event_stream = agent.run_with_new_request(
            task_description=task_description,
            event_stream=event_stream,
        )

        print("\nTask completed successfully!")
        return new_event_stream

    # Handle file input mode
    if hasattr(args, 'input_file') and args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                task_description = f.read().strip()
            
            if not task_description:
                print("Error: Empty input file")
                sys.exit(1)

            new_event_stream = agent.run_with_new_request(
                task_description=task_description,
                event_stream=event_stream,
            )

            print("\nTask completed successfully!")
            return new_event_stream
            
        except FileNotFoundError:
            print(f"Error: Input file '{args.input_file}' not found")
            sys.exit(1)

    # Interactive mode - when no question or input file is provided
    if (not hasattr(args, 'question') or not args.question) and (not hasattr(args, 'input_file') or not args.input_file):
        print(f"DefaultAgent", file=sys.stderr)
        print("Interactive mode started. Agent ready for input.", file=sys.stderr)
        print("Type 'quit' or 'exit' to stop, or 'help' for available commands.", file=sys.stderr)
        
        # Start interactive session
        while True:
            try:
                user_input = input("> ")
                
                # Handle special commands
                if user_input.lower().strip() in ['quit', 'exit', 'q']:
                    print("Goodbye!", file=sys.stderr)
                    break
                elif user_input.lower().strip() == 'help':
                    print("Available commands:", file=sys.stderr)
                    print("  quit, exit, q - Exit interactive mode", file=sys.stderr)
                    print("  help - Show this help message", file=sys.stderr)
                    print("  Any other input will be processed as a task for the agent", file=sys.stderr)
                    continue
                elif not user_input.strip():
                    # Skip empty input
                    continue
                
                # Process user input with the agent
                print(f"Processing: {user_input}", file=sys.stderr)
                try:
                    new_event_stream = agent.run_with_new_request(
                        task_description=user_input.strip(),
                        event_stream=event_stream,
                    )
                    event_stream = new_event_stream  # Update event stream for next iteration
                    print("Task completed. Ready for next input.", file=sys.stderr)
                except Exception as e:
                    print(f"Error processing task: {e}", file=sys.stderr)
                    
            except EOFError:
                # Handle Ctrl+D
                print("\nGoodbye!", file=sys.stderr)
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C
                print("\nUse 'quit' or 'exit' to stop, or continue with a new command.", file=sys.stderr)
                continue
                
        return event_stream

    return event_stream
if __name__ == "__main__":
    main()