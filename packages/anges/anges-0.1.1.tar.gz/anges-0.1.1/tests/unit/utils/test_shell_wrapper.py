#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import os
import subprocess
import shutil
import re
from anges.utils.shell_wrapper import run_command, run_command_remote, run_command_in_docker

class TestRunCommand(unittest.TestCase):
    def setUp(self):
        # Create a unique temp directory for each test
        self.test_id = self.id().split('.')[-1]
        self.temp_dir = f'.temp_{self.test_id}'
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_interactive_command(self):
        """Test that commands requiring interactive input fail appropriately"""
        # Using read with a timeout, which requires input and will fail if it can't get it
        cmd = '/bin/bash -c "read -t 1 input && echo $input"'
        output = run_command(cmd, timeout=5)
        self.assertIn('EXIT_CODE: 1', output)  # Should fail with exit code 1
        self.assertNotIn('EXIT_CODE: 0', output)  # Should definitely not succeed

    def test_echo_hello_world(self):
        cmd = 'echo "Hello, World!"'
        output = run_command(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('STDOUT:\nHello, World!\n', output)

    def test_list_directory(self):
        cmd = 'ls -a'
        output = run_command(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn(self.temp_dir, output)

    def test_pwd(self):
        cmd = 'pwd'
        output = run_command(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        current_dir = os.getcwd()
        self.assertIn(f'STDOUT:\n{current_dir}\n', output)

    def test_create_temp_file(self):
        temp_file = os.path.join(self.temp_dir, 'test_file.txt')
        cmd_create = f'echo "Test Content" > {temp_file}'
        cmd_read = f'cat {temp_file}'

        output_create = run_command(cmd_create)
        self.assertIn('EXIT_CODE: 0', output_create)

        output_read = run_command(cmd_read)
        self.assertIn('EXIT_CODE: 0', output_read)
        self.assertIn('STDOUT:\nTest Content\n', output_read)

    def test_nonexistent_command(self):
        cmd = 'nonexistentcommand'
        output = run_command(cmd)
        self.assertNotIn('EXIT_CODE: 0', output)
        self.assertIn('EXIT_CODE:', output)
        self.assertRegex(output, r'STDERR:.*(not found|No such file or directory)')

    def test_cat_nonexistent_file(self):
        temp_file = os.path.join(self.temp_dir, 'nonexistent.txt')
        cmd = f'cat {temp_file}'
        output = run_command(cmd)
        self.assertNotIn('EXIT_CODE: 0', output)
        self.assertIn('No such file or directory', output)

    def test_permission_denied(self):
        temp_file = os.path.join(self.temp_dir, 'restricted.txt')
        with open(temp_file, 'w') as f:
            f.write('Restricted Content')
        os.chmod(temp_file, 0o000)
        cmd = f'cat {temp_file}'
        output = run_command(cmd)
        self.assertNotIn('EXIT_CODE: 0', output)
        self.assertIn('Permission denied', output)
        os.chmod(temp_file, 0o644)

    def test_invalid_syntax(self):
        cmd = 'echo "Missing quote'
        output = run_command(cmd)
        self.assertNotIn('EXIT_CODE: 0', output)
        self.assertIn('STDERR:', output)

    def test_time_spent_in_output(self):
        cmd = 'sleep 1'
        output = run_command(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertRegex(output, r'TIME_SPENT: [0-9.]+ seconds')
        match = re.search(r'TIME_SPENT: ([0-9.]+) seconds', output)
        self.assertIsNotNone(match)
        time_spent = float(match.group(1))
        self.assertGreaterEqual(time_spent, 1.0)

    def test_command_timeout(self):
        cmd = 'sleep 3'
        output = run_command(cmd, timeout=1)
        self.assertIn('EXIT_CODE: -1', output)
        self.assertIn('Command timed out after 1 seconds', output)
        time_match = re.search(r'TIME_SPENT: ([0-9.]+) seconds', output)
        self.assertIsNotNone(time_match)
        time_spent = float(time_match.group(1))
        self.assertLess(time_spent, 2.0)

    def test_empty_command(self):
        cmd = ''
        output = run_command(cmd)
        self.assertNotIn('EXIT_CODE: 0', output)  # Empty command should fail
        self.assertIn('STDERR:', output)

    def test_none_command(self):
        cmd = None
        with self.assertRaises(ValueError):
            run_command(cmd)

    def test_command_with_special_characters(self):
        cmd = 'echo "Special & Characters"'
        output = run_command(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('STDOUT:\nSpecial & Characters\n', output)

    def test_command_with_large_output(self):
        cmd = 'yes "Line" | head -n 10000'
        output = run_command(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertTrue('STDOUT:' in output)
        self.assertTrue(len(output.splitlines()) > 30)

    def test_unicode_output(self):
        cmd = 'echo "こんにちは世界"'  # "Hello World" in Japanese
        output = run_command(cmd)
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('STDOUT:\nこんにちは世界\n', output)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_background_detection_ampersand(self, mock_popen):
        """Test background process detection with & suffix"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'background output', b'')
        mock_popen.return_value = mock_process
        
        cmd = 'sleep 10 &'
        output = run_command(cmd)
        
        # Verify background process was detected and handled
        self.assertIn('BACKGROUND_COMMAND_EXECUTED: sleep 10 &', output)
        self.assertIn('MAX_TIME_WAITED: 5 seconds', output)
        self.assertIn('STDOUT:\nbackground output', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        # Verify communicate was called with 5-second timeout
        mock_process.communicate.assert_called_once_with(timeout=5)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_background_detection_nohup(self, mock_popen):
        """Test background process detection with nohup prefix"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'nohup output', b'nohup: ignoring input')
        mock_popen.return_value = mock_process
        
        cmd = 'nohup python script.py'
        output = run_command(cmd)
        
        # Verify background process was detected and handled
        self.assertIn('BACKGROUND_COMMAND_EXECUTED: nohup python script.py', output)
        self.assertIn('MAX_TIME_WAITED: 5 seconds', output)
        self.assertIn('STDOUT:\nnohup output', output)
        self.assertIn('STDERR: nohup: ignoring input', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        # Verify communicate was called with 5-second timeout
        mock_process.communicate.assert_called_once_with(timeout=5)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_background_detection_comment(self, mock_popen):
        """Test background process detection with #RUN_IN_BACKGROUND comment"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'comment background output', b'')
        mock_popen.return_value = mock_process
        
        cmd = 'python long_running_script.py #RUN_IN_BACKGROUND'
        output = run_command(cmd)
        
        # Verify background process was detected and handled
        self.assertIn('BACKGROUND_COMMAND_EXECUTED: python long_running_script.py #RUN_IN_BACKGROUND', output)
        self.assertIn('MAX_TIME_WAITED: 5 seconds', output)
        self.assertIn('STDOUT:\ncomment background output', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        # Verify communicate was called with 5-second timeout
        mock_process.communicate.assert_called_once_with(timeout=5)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_background_parameter(self, mock_popen):
        """Test background process with explicit run_in_background=True"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'explicit background output', b'')
        mock_popen.return_value = mock_process
        
        cmd = 'python normal_script.py'
        output = run_command(cmd, run_in_background=True)
        
        # Verify background process was detected and handled
        self.assertIn('BACKGROUND_COMMAND_EXECUTED: python normal_script.py', output)
        self.assertIn('MAX_TIME_WAITED: 5 seconds', output)
        self.assertIn('STDOUT:\nexplicit background output', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        # Verify communicate was called with 5-second timeout
        mock_process.communicate.assert_called_once_with(timeout=5)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_background_timeout_handling(self, mock_popen):
        """Test that background processes handle TimeoutExpired correctly"""
        # Setup mock to raise TimeoutExpired
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired('cmd', 5)
        mock_popen.return_value = mock_process
        
        cmd = 'sleep 10 &'
        output = run_command(cmd)
        
        # Verify background process timeout was handled
        self.assertIn('BACKGROUND_COMMAND_EXECUTED: sleep 10 &', output)
        self.assertIn('MAX_TIME_WAITED: 5 seconds', output)
        self.assertIn('STDOUT:\n', output)  # Should be empty due to timeout
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        # Verify communicate was called with 5-second timeout
        mock_process.communicate.assert_called_once_with(timeout=5)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_background_no_wait_for_completion(self, mock_popen):
        """Test that background processes don't wait for completion beyond timeout"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'quick output', b'')
        mock_popen.return_value = mock_process
        
        cmd = 'nohup long_running_process &'
        
        import time
        start_time = time.time()
        output = run_command(cmd)
        end_time = time.time()
        
        # Verify the function returned quickly (within reasonable time)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 1.0)  # Should be much faster than any real background process
        
        # Verify background process was detected and handled
        self.assertIn('BACKGROUND_COMMAND_EXECUTED: nohup long_running_process &', output)
        self.assertIn('MAX_TIME_WAITED: 5 seconds', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        # Verify communicate was called with 5-second timeout
        mock_process.communicate.assert_called_once_with(timeout=5)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_background_five_second_timeout(self, mock_popen):
        """Test that 5-second timeout is applied for background processes"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'timeout test output', b'timeout test error')
        mock_popen.return_value = mock_process
        
        cmd = 'python script.py #RUN_IN_BACKGROUND'
        output = run_command(cmd, timeout=300)  # Regular timeout should be ignored for background
        
        # Verify background process was detected and handled
        self.assertIn('BACKGROUND_COMMAND_EXECUTED: python script.py #RUN_IN_BACKGROUND', output)
        self.assertIn('MAX_TIME_WAITED: 5 seconds', output)
        self.assertIn('STDOUT:\ntimeout test output', output)
        self.assertIn('STDERR: timeout test error', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        # Verify communicate was called with 5-second timeout, not the 300-second timeout
        mock_process.communicate.assert_called_once_with(timeout=5)

    @patch('anges.utils.shell_wrapper.os.killpg')
    @patch('anges.utils.shell_wrapper.os.getpgid')
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_timeout_handling(self, mock_popen, mock_getpgid, mock_killpg):
        """Test timeout mechanism kills process and returns correct error"""
        # Setup mocks
        mock_process = MagicMock()
        mock_process.pid = 12345
        # First call raises TimeoutExpired, second call returns values after kill
        mock_process.communicate.side_effect = [
            subprocess.TimeoutExpired('test_cmd', 2),
            (b'partial output', b'Command timed out after 2 seconds')
        ]
        mock_popen.return_value = mock_process
        mock_getpgid.return_value = 12345
        
        cmd = 'sleep 10'
        output = run_command(cmd, timeout=2)
        
        # Verify timeout handling
        self.assertIn('EXIT_CODE: -1', output)
        self.assertIn('Command timed out after 2 seconds', output)
        self.assertIn('COMMAND_EXECUTED: sleep 10', output)
        
        # Verify process group was killed
        mock_getpgid.assert_called_once_with(12345)
        mock_killpg.assert_called_once_with(12345, 9)  # SIGKILL = 9
        
        # Verify communicate was called twice (once with timeout, once after kill)
        self.assertEqual(mock_process.communicate.call_count, 2)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_process_group_creation(self, mock_popen):
        """Test that commands are run in new process group for proper cleanup"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'test output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        cmd = 'echo "test"'
        output = run_command(cmd)
        
        # Verify subprocess.Popen was called with preexec_fn=os.setsid
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        self.assertEqual(call_args[1]['preexec_fn'], os.setsid)
        self.assertEqual(call_args[1]['stdin'], subprocess.DEVNULL)
        self.assertEqual(call_args[1]['stdout'], subprocess.PIPE)
        self.assertEqual(call_args[1]['stderr'], subprocess.PIPE)
        
        # Verify successful execution
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('STDOUT:\ntest output', output)

    @patch('anges.utils.shell_wrapper.shlex.quote')
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_special_characters_escaping(self, mock_popen, mock_shlex_quote):
        """Test command construction with special characters using shlex.quote"""
        # Setup mocks
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'escaped output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_shlex_quote.return_value = "'cd . && echo \"test & special; chars\"'"
        
        cmd = 'echo "test & special; chars"'
        output = run_command(cmd, use_bash=True)
        
        # Verify shlex.quote was called to escape the full command
        mock_shlex_quote.assert_called_once_with('cd . && echo "test & special; chars"')
        
        # Verify the escaped command was used in subprocess.Popen
        expected_cmd = "bash -c 'cd . && echo \"test & special; chars\"'"
        mock_popen.assert_called_once_with(
            expected_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )
        
        # Verify successful execution
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('STDOUT:\nescaped output', output)

    @patch('anges.utils.shell_wrapper.config')
    def test_truncate_stdout_character_limit(self, mock_config):
        """Test stdout truncation by character count"""
        from anges.utils.shell_wrapper import truncate_stdout
        
        # Mock config to set character limit
        mock_config.general_config.max_char_in_single_content_to_truncate = 100
        
        # Create a string longer than the limit
        long_output = 'A' * 150  # 150 characters
        
        result = truncate_stdout(long_output)
        
        # Verify truncation occurred
        self.assertIn('chars truncated', result)
        self.assertLess(len(result), len(long_output))
        # Should contain first and last parts
        self.assertTrue(result.startswith('A' * 50))  # First half of limit
        self.assertTrue(result.endswith('A' * 50))    # Last half of limit
        self.assertIn('<... 50 chars truncated ...>', result)

    @patch('anges.utils.shell_wrapper.config')
    def test_truncate_stdout_line_limit(self, mock_config):
        """Test stdout truncation by line count"""
        from anges.utils.shell_wrapper import truncate_stdout
        
        # Mock config to set high character limit so line limit is tested
        mock_config.general_config.max_char_in_single_content_to_truncate = 100000
        
        # Create output with many lines (more than 5000)
        lines = [f'Line {i}' for i in range(6000)]
        long_output = '\n'.join(lines)
        
        result = truncate_stdout(long_output)
        
        # Verify line truncation occurred
        self.assertIn('lines truncated', result)
        result_lines = result.splitlines()
        self.assertLess(len(result_lines), 6000)
        
        # Should contain first and last parts (2500 lines each)
        self.assertIn('Line 0', result)
        self.assertIn('Line 2499', result)  # Last line of first half
        self.assertIn('Line 3500', result)  # First line of second half
        self.assertIn('Line 5999', result)  # Last line
        self.assertIn('... 1000 lines truncated ...', result)

    @patch('anges.utils.shell_wrapper.shlex.quote')
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_special_characters_escaping(self, mock_popen, mock_shlex_quote):
        """Test command construction with special characters using shlex.quote"""
        # Setup mocks
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'escaped output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_shlex_quote.return_value = "'cd . && echo \"test & special; chars\"'"
        
        cmd = 'echo "test & special; chars"'
        output = run_command(cmd, use_bash=True)
        
        # Verify shlex.quote was called to escape the full command
        mock_shlex_quote.assert_called_once_with('cd . && echo "test & special; chars"')
        
        # Verify the escaped command was used in subprocess.Popen
        expected_cmd = "bash -c 'cd . && echo \"test & special; chars\"'"
        mock_popen.assert_called_once_with(
            expected_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )
        
        # Verify successful execution
        self.assertIn('EXIT_CODE: 0', output)
        self.assertIn('STDOUT:\nescaped output', output)

    @patch('anges.utils.shell_wrapper.config')
    def test_truncate_stdout_character_limit(self, mock_config):
        """Test stdout truncation by character count"""
        from anges.utils.shell_wrapper import truncate_stdout
        
        # Mock config to set character limit
        mock_config.general_config.max_char_in_single_content_to_truncate = 100
        
        # Create a string longer than the limit
        long_output = 'A' * 150  # 150 characters
        
        result = truncate_stdout(long_output)
        
        # Verify truncation occurred
        self.assertIn('chars truncated', result)
        # The result contains first 50 chars + truncation message + last 50 chars
        # So it should contain the truncation message
        self.assertIn('<... 50 chars truncated ...>', result)
        # Should contain first and last parts
        self.assertTrue(result.startswith('A' * 50))  # First half of limit
        self.assertTrue(result.endswith('A' * 50))    # Last half of limit

    @patch('anges.utils.shell_wrapper.config')
    def test_truncate_stdout_line_limit(self, mock_config):
        """Test stdout truncation by line count"""
        from anges.utils.shell_wrapper import truncate_stdout
        
        # Mock config to set high character limit so line limit is tested
        mock_config.general_config.max_char_in_single_content_to_truncate = 100000
        
        # Create output with many lines (more than 5000)
        lines = [f'Line {i}' for i in range(6000)]
        long_output = '\n'.join(lines)
        
        result = truncate_stdout(long_output)
        
        # Verify line truncation occurred
        self.assertIn('lines truncated', result)
        result_lines = result.splitlines()
        self.assertLess(len(result_lines), 6000)
        
        # Should contain first and last parts (2500 lines each)
        self.assertIn('Line 0', result)
        self.assertIn('Line 2499', result)  # Last line of first half
        self.assertIn('Line 3500', result)  # First line of second half
        self.assertIn('Line 5999', result)  # Last line
        self.assertIn('... 1000 lines truncated ...', result)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_in_docker_container_not_found(self, mock_popen):
        """Test docker execution with non-existent container"""
        # Setup mock to simulate container not found error
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'Error: No such container: nonexistent_container')
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        cmd = 'docker exec nonexistent_container echo "test"'
        output = run_command(cmd)
        
        # Verify error handling
        self.assertIn('EXIT_CODE: 1', output)
        self.assertIn('COMMAND_EXECUTED: docker exec nonexistent_container echo "test"', output)
        self.assertIn('STDERR: Error: No such container: nonexistent_container', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        mock_process.communicate.assert_called_once()

    @patch('anges.utils.shell_wrapper.os.killpg')
    @patch('anges.utils.shell_wrapper.os.getpgid')
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_in_docker_timeout(self, mock_popen, mock_getpgid, mock_killpg):
        """Test docker execution with timeout"""
        # Setup mocks
        mock_process = MagicMock()
        mock_process.pid = 54321
        # First call raises TimeoutExpired, second call returns values after kill
        mock_process.communicate.side_effect = [
            subprocess.TimeoutExpired('docker exec test_container sleep 10', 3),
            (b'', b'Command timed out after 3 seconds')
        ]
        mock_popen.return_value = mock_process
        mock_getpgid.return_value = 54321
        
        cmd = 'docker exec test_container sleep 10'
        output = run_command(cmd, timeout=3)
        
        # Verify timeout handling
        self.assertIn('EXIT_CODE: -1', output)
        self.assertIn('Command timed out after 3 seconds', output)
        self.assertIn('COMMAND_EXECUTED: docker exec test_container sleep 10', output)
        
        # Verify process group was killed
        mock_getpgid.assert_called_once_with(54321)
        mock_killpg.assert_called_once_with(54321, 9)  # SIGKILL = 9
        
        # Verify communicate was called twice (once with timeout, once after kill)
        self.assertEqual(mock_process.communicate.call_count, 2)

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_connection_failure(self, mock_popen):
        """Test remote execution with connection failure"""
        # Setup mock to simulate SSH connection failure
        mock_process = MagicMock()
        mock_process.communicate.return_value = (
            b'', 
            b'ssh: connect to host remote.server.com port 22: Connection refused'
        )
        mock_process.returncode = 255  # SSH connection failure exit code
        mock_popen.return_value = mock_process
        
        cmd = 'ssh user@remote.server.com "echo test"'
        output = run_command(cmd)
        
        # Verify connection failure handling
        self.assertIn('EXIT_CODE: 255', output)
        self.assertIn('COMMAND_EXECUTED: ssh user@remote.server.com "echo test"', output)
        self.assertIn('STDERR: ssh: connect to host remote.server.com port 22: Connection refused', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        mock_process.communicate.assert_called_once()

    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_authentication_failure(self, mock_popen):
        """Test remote execution with authentication failure"""
        # Setup mock to simulate SSH authentication failure
        mock_process = MagicMock()
        mock_process.communicate.return_value = (
            b'', 
            b'Permission denied (publickey,password).'
        )
        mock_process.returncode = 255  # SSH authentication failure exit code
        mock_popen.return_value = mock_process
        
        cmd = 'ssh user@remote.server.com "ls -la"'
        output = run_command(cmd)
        
        # Verify authentication failure handling
        self.assertIn('EXIT_CODE: 255', output)
        self.assertIn('COMMAND_EXECUTED: ssh user@remote.server.com "ls -la"', output)
        self.assertIn('STDERR: Permission denied (publickey,password).', output)
        
        # Verify subprocess.Popen was called correctly
        mock_popen.assert_called_once()
        mock_process.communicate.assert_called_once()


class TestRunCommandRemote(unittest.TestCase):
    """Test cases for run_command_remote function"""
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_basic(self, mock_popen):
        """Test basic remote command execution"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'remote output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command_remote('echo "hello"', 'test.example.com')
        
        # Verify SSH command construction
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertEqual(call_args, ['ssh', 'test.example.com', 'echo "hello"'])
        
        # Verify output format
        self.assertIn('COMMAND_EXECUTED: ssh test.example.com echo "hello"', result)
        self.assertIn('EXIT_CODE: 0', result)
        self.assertIn('STDOUT:\nremote output', result)
        self.assertIn('TIME_SPENT:', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_with_username(self, mock_popen):
        """Test remote command with username"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'user output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command_remote('ls -la', 'server.com', username='testuser')
        
        # Verify SSH command construction with username
        call_args = mock_popen.call_args[0][0]
        self.assertEqual(call_args, ['ssh', 'testuser@server.com', 'ls -la'])
        
        # Verify output
        self.assertIn('COMMAND_EXECUTED: ssh testuser@server.com ls -la', result)
        self.assertIn('EXIT_CODE: 0', result)
        self.assertIn('STDOUT:\nuser output', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_with_key_file(self, mock_popen):
        """Test remote command with SSH key file"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'key auth output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command_remote('pwd', 'remote.host', key_filename='/path/to/key.pem')
        
        # Verify SSH command construction with key file
        call_args = mock_popen.call_args[0][0]
        self.assertEqual(call_args, ['ssh', '-i', '/path/to/key.pem', 'remote.host', 'pwd'])
        
        # Verify output
        self.assertIn('COMMAND_EXECUTED: ssh -i /path/to/key.pem remote.host pwd', result)
        self.assertIn('EXIT_CODE: 0', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_with_all_params(self, mock_popen):
        """Test remote command with username and key file"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'full params output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command_remote(
            'whoami', 
            'prod.server.com', 
            username='admin', 
            key_filename='/home/user/.ssh/id_rsa'
        )
        
        # Verify SSH command construction with all parameters
        call_args = mock_popen.call_args[0][0]
        expected_cmd = ['ssh', '-i', '/home/user/.ssh/id_rsa', 'admin@prod.server.com', 'whoami']
        self.assertEqual(call_args, expected_cmd)
        
        # Verify output
        self.assertIn('COMMAND_EXECUTED: ssh -i /home/user/.ssh/id_rsa admin@prod.server.com whoami', result)
        self.assertIn('EXIT_CODE: 0', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_connection_error(self, mock_popen):
        """Test remote command with connection failure"""
        # Setup mock for connection failure
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'ssh: connect to host badhost port 22: Connection refused')
        mock_process.returncode = 255
        mock_popen.return_value = mock_process
        
        result = run_command_remote('echo test', 'badhost')
        
        # Verify error handling
        self.assertIn('EXIT_CODE: 255', result)
        self.assertIn('STDERR: ssh: connect to host badhost port 22: Connection refused', result)
        self.assertIn('COMMAND_EXECUTED: ssh badhost echo test', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_auth_error(self, mock_popen):
        """Test remote command with authentication failure"""
        # Setup mock for auth failure
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'Permission denied (publickey,password).')
        mock_process.returncode = 255
        mock_popen.return_value = mock_process
        
        result = run_command_remote('ls', 'secure.host', username='wronguser')
        
        # Verify auth error handling
        self.assertIn('EXIT_CODE: 255', result)
        self.assertIn('STDERR: Permission denied (publickey,password).', result)
        self.assertIn('COMMAND_EXECUTED: ssh wronguser@secure.host ls', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_remote_command_error(self, mock_popen):
        """Test remote command that fails on remote host"""
        # Setup mock for command failure on remote host
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'bash: badcommand: command not found')
        mock_process.returncode = 127
        mock_popen.return_value = mock_process
        
        result = run_command_remote('badcommand', 'goodhost')
        
        # Verify command error handling
        self.assertIn('EXIT_CODE: 127', result)
        self.assertIn('STDERR: bash: badcommand: command not found', result)
        self.assertIn('COMMAND_EXECUTED: ssh goodhost badcommand', result)


class TestRunCommandInDocker(unittest.TestCase):
    """Test cases for run_command_in_docker function"""
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_in_docker_basic(self, mock_popen):
        """Test basic docker command execution"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'docker output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command_in_docker('echo "hello docker"', 'test_container')
        
        # Verify docker command construction
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        expected_cmd = ['docker', 'exec', 'test_container', 'bash', '-c', 'echo "hello docker"']
        self.assertEqual(call_args[0][0], expected_cmd)
        
        # Verify subprocess options
        self.assertEqual(call_args[1]['stdout'], subprocess.PIPE)
        self.assertEqual(call_args[1]['stderr'], subprocess.PIPE)
        self.assertEqual(call_args[1]['stdin'], subprocess.DEVNULL)
        self.assertEqual(call_args[1]['preexec_fn'], os.setsid)
        
        # Verify output format
        self.assertIn('COMMAND_EXECUTED: docker exec test_container bash -c echo "hello docker"', result)
        self.assertIn('EXIT_CODE: 0', result)
        self.assertIn('STDOUT:\ndocker output', result)
        self.assertIn('TIME_SPENT:', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_in_docker_with_timeout(self, mock_popen):
        """Test docker command with custom timeout"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'quick output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command_in_docker('ls -la', 'my_container', timeout=30)
        
        # Verify communicate was called with correct timeout
        mock_process.communicate.assert_called_once_with(timeout=30)
        
        # Verify output
        self.assertIn('COMMAND_EXECUTED: docker exec my_container bash -c ls -la', result)
        self.assertIn('EXIT_CODE: 0', result)
        self.assertIn('STDOUT:\nquick output', result)
    
    def test_run_command_in_docker_none_command(self):
        """Test docker command with None command raises ValueError"""
        with self.assertRaises(ValueError) as context:
            run_command_in_docker(None, 'test_container')
        
        self.assertEqual(str(context.exception), "Command cannot be None")
    
    @patch('anges.utils.shell_wrapper.os.killpg')
    @patch('anges.utils.shell_wrapper.os.getpgid')
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_in_docker_timeout_handling(self, mock_popen, mock_getpgid, mock_killpg):
        """Test docker command timeout with process group killing"""
        # Setup mocks
        mock_process = MagicMock()
        mock_process.pid = 98765
        # First call raises TimeoutExpired, second call returns values after kill
        mock_process.communicate.side_effect = [
            subprocess.TimeoutExpired('docker exec test_container sleep 10', 5),
            (b'', b'Command timed out after 5 seconds')
        ]
        mock_popen.return_value = mock_process
        mock_getpgid.return_value = 98765
        
        result = run_command_in_docker('sleep 10', 'test_container', timeout=5)
        
        # Verify timeout handling
        self.assertIn('EXIT_CODE: -1', result)
        self.assertIn('Command timed out after 5 seconds', result)
        self.assertIn('COMMAND_EXECUTED: docker exec test_container bash -c sleep 10', result)
        
        # Verify process group was killed
        mock_getpgid.assert_called_once_with(98765)
        mock_killpg.assert_called_once_with(98765, 9)  # SIGKILL = 9
        
        # Verify communicate was called twice (once with timeout, once after kill)
        self.assertEqual(mock_process.communicate.call_count, 2)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_in_docker_container_not_found(self, mock_popen):
        """Test docker command with non-existent container"""
        # Setup mock for container not found error
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'Error: No such container: nonexistent')
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        result = run_command_in_docker('echo test', 'nonexistent')
        
        # Verify error handling
        self.assertIn('EXIT_CODE: 1', result)
        self.assertIn('STDERR: Error: No such container: nonexistent', result)
        self.assertIn('COMMAND_EXECUTED: docker exec nonexistent bash -c echo test', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_in_docker_command_failure(self, mock_popen):
        """Test docker command that fails inside container"""
        # Setup mock for command failure inside container
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'bash: invalidcommand: command not found')
        mock_process.returncode = 127
        mock_popen.return_value = mock_process
        
        result = run_command_in_docker('invalidcommand', 'valid_container')
        
        # Verify command failure handling
        self.assertIn('EXIT_CODE: 127', result)
        self.assertIn('STDERR: bash: invalidcommand: command not found', result)
        self.assertIn('COMMAND_EXECUTED: docker exec valid_container bash -c invalidcommand', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_in_docker_complex_command(self, mock_popen):
        """Test docker command with complex shell operations"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'file1\nfile2\nfile3', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        complex_cmd = 'find /app -name "*.py" | head -3'
        result = run_command_in_docker(complex_cmd, 'python_container')
        
        # Verify complex command handling
        expected_docker_cmd = ['docker', 'exec', 'python_container', 'bash', '-c', complex_cmd]
        call_args = mock_popen.call_args[0][0]
        self.assertEqual(call_args, expected_docker_cmd)
        
        # Verify output
        self.assertIn('EXIT_CODE: 0', result)
        self.assertIn('STDOUT:\nfile1\nfile2\nfile3', result)


class TestRunCommandAdditionalCoverage(unittest.TestCase):
    """Additional tests to improve coverage of run_command function"""
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_with_prefix_cmd(self, mock_popen):
        """Test run_command with prefix_cmd parameter"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'prefixed output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command('echo test', prefix_cmd='export VAR=value')
        
        # Verify command construction with prefix
        call_args = mock_popen.call_args[0][0]
        # The command should include the prefix
        self.assertIn('export VAR=value', call_args)
        self.assertIn('echo test', call_args)
        
        # Verify output
        self.assertIn('EXIT_CODE: 0', result)
        self.assertIn('STDOUT:\nprefixed output', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_with_cmd_init_dir(self, mock_popen):
        """Test run_command with cmd_init_dir parameter"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'/custom/dir', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command('pwd', cmd_init_dir='/custom/dir')
        
        # Verify command construction with directory change
        call_args = mock_popen.call_args[0][0]
        self.assertIn('cd /custom/dir', call_args)
        self.assertIn('pwd', call_args)
        
        # Verify output
        self.assertIn('EXIT_CODE: 0', result)
        self.assertIn('STDOUT:\n/custom/dir', result)
    
    @patch('anges.utils.shell_wrapper.subprocess.Popen')
    def test_run_command_with_prefix_and_init_dir(self, mock_popen):
        """Test run_command with both prefix_cmd and cmd_init_dir"""
        # Setup mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'combined output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = run_command(
            'echo $TEST_VAR', 
            prefix_cmd='export TEST_VAR=hello', 
            cmd_init_dir='/tmp'
        )
        
        # Verify command construction with both prefix and directory
        call_args = mock_popen.call_args[0][0]
        self.assertIn('cd /tmp', call_args)
        self.assertIn('export TEST_VAR=hello', call_args)
        self.assertIn('echo $TEST_VAR', call_args)
        
        # Verify output
        self.assertIn('EXIT_CODE: 0', result)
        self.assertIn('STDOUT:\ncombined output', result)
if __name__ == '__main__':
    unittest.main()
