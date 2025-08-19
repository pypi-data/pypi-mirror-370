import os
import pytest
from unittest.mock import patch
import subprocess
import tempfile

def test_cli_interface_with_file_input():
    # Create a temporary test task file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write("What's the python version?")
        task_file_path = temp_file.name

    try:
        # Run the CLI with the test file
        result = subprocess.run(
            ['python', '-m', 'anges.cli_interface.cli_runner', '--input-file', task_file_path],
            capture_output=True,
            text=True
        )

        # Verify the execution was successful
        assert result.returncode == 0
        
        # Verify the output contains task completion message
        assert "Task completed successfully!" in result.stdout

        # Verify the agent received and processed the request
        assert "received a new request" in result.stderr
        assert "python version" in result.stderr
    finally:
        # Cleanup the temporary file
        os.unlink(task_file_path)