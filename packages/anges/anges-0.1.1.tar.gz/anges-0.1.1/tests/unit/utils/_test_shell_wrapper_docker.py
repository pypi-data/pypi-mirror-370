#!/usr/bin/env python3

import unittest
import os
import re
from anges.utils.shell_wrapper import run_command, run_command_in_docker

class TestRunCommandInDocker(unittest.TestCase):
    def setUp(self):
        # Check if the required container is running
        output = run_command("docker ps --filter name=python_dev --format '{{.Names}}'")
        if 'python_dev' not in output:
            self.fail("Required container 'python_dev' is not running")

    def test_echo_in_container(self):
        cmd = 'echo "Hello from Docker!"'
        output = run_command_in_docker(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('STDOUT:\nHello from Docker!\n', output)

    def test_command_timeout(self):
        cmd = 'sleep 3'
        output = run_command_in_docker(cmd, timeout=1)
        self.assertIn('EXIT_CODE: -1', output)
        self.assertIn('Command timed out after 1 seconds', output)
        time_match = re.search(r'TIME_SPENT: ([0-9.]+) seconds', output)
        self.assertIsNotNone(time_match)
        time_spent = float(time_match.group(1))
        self.assertLess(time_spent, 2.0)

    def test_nonexistent_container(self):
        cmd = 'echo "test"'
        output = run_command_in_docker(cmd, container='nonexistent_container')
        self.assertNotIn('EXIT_CODE: 0', output)
        self.assertIn('ERROR', output.upper())

    def test_file_operations(self):
        # Create a test file
        create_cmd = 'echo "Test content" > /tmp/test.txt'
        output = run_command_in_docker(create_cmd)
        self.assertIn('EXIT_CODE: 0', output)

        # Read the file content
        read_cmd = 'cat /tmp/test.txt'
        output = run_command_in_docker(read_cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('Test content', output)

        # Clean up
        cleanup_cmd = 'rm /tmp/test.txt'
        output = run_command_in_docker(cleanup_cmd)
        self.assertIn('EXIT_CODE: 0', output)

    def test_working_directory(self):
        cmd = 'pwd'
        output = run_command_in_docker(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('/\n', output)  # Default should be root directory

    def test_environment_variables(self):
        # Test setting and reading environment variables
        cmd = 'export TEST_VAR="test_value" && echo $TEST_VAR'
        output = run_command_in_docker(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('test_value', output)

    def test_command_chaining(self):
        # Test multiple commands with different operators
        cmd = 'mkdir -p /tmp/test && cd /tmp/test && pwd && touch test.txt && ls'
        output = run_command_in_docker(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('/tmp/test', output)
        self.assertIn('test.txt', output)

    def test_unicode_output(self):
        cmd = 'echo "こんにちは世界"'  # "Hello World" in Japanese
        output = run_command_in_docker(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('こんにちは世界', output)

if __name__ == '__main__':
    unittest.main()
