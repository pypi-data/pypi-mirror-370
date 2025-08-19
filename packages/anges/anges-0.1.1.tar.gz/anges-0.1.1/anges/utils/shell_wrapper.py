#!/usr/bin/env python3

import subprocess
import time
import os
import platform
import signal
import shlex
from anges.config import config

def truncate_stdout(stdout):
    """Truncate stdout if it exceeds some lines or characters."""
    max_lines = 5000
    max_chars = config.general_config.max_char_in_single_content_to_truncate

    if len(stdout) > max_chars:
        stdout = (
            stdout[: max_chars // 2]
            + f"<... {len(stdout) - max_chars} chars truncated ...>"
            + stdout[len(stdout) - max_chars // 2 :]
        )

    lines = stdout.splitlines()
    if len(lines) > max_lines:
        return "\n".join(
            lines[: max_lines // 2]
            + [f"... {len(lines)-max_lines} lines truncated ..."]
            + lines[-max_lines // 2 :]
        )

    if len(stdout) > max_chars:
        return (
            stdout[: max_chars // 2]
            + f"... {len(stdout) - max_chars} chars truncated ..."
            + stdout[max_chars // 2 :]
        )

    return stdout


def run_command(cmd, timeout=300, cmd_init_dir=".", prefix_cmd="", use_bash=True, run_in_background=False):
    """Execute a shell command locally and return formatted output."""
    if cmd is None:
        raise ValueError("Command cannot be None")

    start_time = time.perf_counter()
    if prefix_cmd:
        full_cmd = f"cd {cmd_init_dir} && {prefix_cmd} && {cmd}"
    else:
        full_cmd = f"cd {cmd_init_dir} && {cmd}"

    if use_bash:
        full_cmd = f"bash -c {shlex.quote(full_cmd)}"

    # Check if the command should run in the background or use nohup
    run_in_background = (cmd.strip().endswith("&") or cmd.startswith("nohup") or "#RUN_IN_BACKGROUND" in cmd) or run_in_background

    preexec_fn = None if platform.system() == "Windows" else os.setsid
    process = subprocess.Popen(
        full_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,  # Prevent interactive input
        preexec_fn=preexec_fn,  # Create a new process group
    )
    if run_in_background:
        # Get the actual PID of the background process by using process group id
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            stdout = "".encode()
            stderr = "".encode()
        output = "******\n"
        output += f"- BACKGROUND_COMMAND_EXECUTED: {cmd}\n"
        output += f"\n- MAX_TIME_WAITED: 5 seconds\n"
        output += f"\n- STDERR: {stderr.decode()}\n"
        output += f"\n- STDOUT:\n{truncate_stdout(stdout.decode())}\n"
        output += "******\n"
        return output

    try:
        stdout, stderr = process.communicate(timeout=timeout)
        exit_code = process.returncode
    except subprocess.TimeoutExpired:
        # Kill the entire process group
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        stdout, stderr = process.communicate()
        exit_code = -1
        stderr = f"Command timed out after {timeout} seconds".encode()

    end_time = time.perf_counter()
    time_spent = end_time - start_time

    output = "******\n"
    output += f"- COMMAND_EXECUTED: {cmd}\n"
    output += f"\n- EXIT_CODE: {exit_code}\n"
    output += f"\n- TIME_SPENT: {time_spent:.4f} seconds\n"
    output += f"\n- STDERR: {stderr.decode()}\n"
    output += f"\n- STDOUT:\n{truncate_stdout(stdout.decode())}\n"
    output += "******\n"
    return output


def run_command_remote(cmd, hostname, username=None, key_filename=None):
    """Execute a shell command on a remote machine via SSH and return formatted output."""
    ssh_cmd = ["ssh"]
    if key_filename:
        ssh_cmd += ["-i", key_filename]
    if username:
        ssh_cmd.append(f"{username}@{hostname}")
    else:
        ssh_cmd.append(hostname)
    ssh_cmd.append(cmd)

    start_time = time.perf_counter()
    process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    end_time = time.perf_counter()
    exit_code = process.returncode
    time_spent = end_time - start_time

    output = "******\n"
    output += f"- COMMAND_EXECUTED: {' '.join(ssh_cmd)}\n"
    output += f"\n- EXIT_CODE: {exit_code}\n"
    output += f"\n- TIME_SPENT: {time_spent:.4f} seconds\n"
    output += f"\n- STDERR: {stderr.decode()}\n"
    output += f"\n- STDOUT:\n{truncate_stdout(stdout.decode())}\n"
    output += "******\n"
    return output


def run_command_in_docker(cmd, container="python_dev", timeout=60):
    """Execute a shell command inside a Docker container and return formatted output."""
    if cmd is None:
        raise ValueError("Command cannot be None")

    docker_cmd = ["docker", "exec", container, "bash", "-c", cmd]

    start_time = time.perf_counter()

    preexec_fn = None if platform.system() == "Windows" else os.setsid
    process = subprocess.Popen(
        docker_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,  # Prevent interactive input
        preexec_fn=preexec_fn,  # Create a new process group
    )

    try:
        stdout, stderr = process.communicate(timeout=timeout)
        exit_code = process.returncode
    except subprocess.TimeoutExpired:
        # Kill the entire process group
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        stdout, stderr = process.communicate()
        exit_code = -1
        stderr = f"Command timed out after {timeout} seconds".encode()

    end_time = time.perf_counter()
    time_spent = end_time - start_time

    output = "******\n"
    output += f"- COMMAND_EXECUTED: {' '.join(docker_cmd)}\n"
    output += f"\n- EXIT_CODE: {exit_code}\n"
    output += f"\n- TIME_SPENT: {time_spent:.4f} seconds\n"
    output += f"\n- STDERR: {stderr.decode()}\n"
    output += f"\n- STDOUT:\n{truncate_stdout(stdout.decode())}\n"
    output += "******\n"
    return output


# Example usage
if __name__ == "__main__":
    cmd = 'echo "Hello, World!"'
    print(run_command(cmd, use_bash=True))
