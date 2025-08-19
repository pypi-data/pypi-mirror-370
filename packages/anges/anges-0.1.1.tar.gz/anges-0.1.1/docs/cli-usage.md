**Language**: [English](cli-usage.md) | [中文](zh/cli-usage.md)

---
# Anges CLI Usage Guide

## Overview

The Anges CLI provides a command-line interface for interacting with the AI agent framework. It supports multiple modes of operation including interactive sessions, file-based input, direct questions, and a web interface.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Command Modes](#command-modes)
- [CLI Arguments](#cli-arguments)
- [Notes Feature](#notes-feature)
- [Examples](#examples)

## Basic Usage

```bash
# Show help
anges --help

# Interactive mode
anges -i

# Run with a question
anges -q "What files are in the current directory?"

# Run with input file
anges -f task.txt

# Launch web interface
anges ui
```

## Command Modes

### Interactive Mode
Enter interactive mode for ongoing conversations with the agent:
```bash
anges -i
```

### Direct Question Mode
Ask a single question directly:
```bash
anges -q "Your question here"
```

### File Input Mode
Provide a task description from a file:
```bash
anges -f /path/to/task.txt
```

### Web Interface Mode
Launch the web-based interface:
```bash
anges ui --host 127.0.0.1 --port 5000
```

## CLI Arguments

### General Arguments

- `--cmd_prefix`: Command prefix to prepend to all shell commands
- `--path`, `--cmd_init_dir`: Initial directory for running commands
- `--agent`: Agent type to use (default, task_executor, task_analyzer, orchestrator)
- `--model`: Model to use for inference (default: agent_default)
- `--logging`: Logging level (info, debug, warning, error, critical)
- `--existing_stream_id`: Existing event stream ID to continue from

### Input Arguments

- `-f`, `--input-file`: Path to input file containing task description
- `-q`, `--question`: Direct text input for single question
- `-i`, `--interactive`: Enter interactive mode

### Web Interface Arguments

- `--host`: Host address to bind (default: 127.0.0.1)
- `--port`: Port number to bind (default: 5000)
- `--password`: Web interface password

## Notes Feature

The notes feature allows you to provide contextual information to the agent through structured notes. Notes can be added individually via command line or in bulk from a JSON file.

### Individual Notes (`--notes`)

Add individual notes in JSON format:

```bash
anges -q "Analyze the project" --notes '{"scope": "project", "title": "Current Status", "content": "Working on CLI documentation"}'
```

Multiple notes can be added by using the `--notes` argument multiple times:

```bash
anges -i \
  --notes '{"scope": "general", "title": "Context", "content": "This is a documentation task"}' \
  --notes '{"scope": "project", "title": "Priority", "content": "High priority feature"}'
```

**Alternative Plain Text Format**: You can also provide plain text which will be auto-formatted:
```bash
anges -q "Help me" --notes "Remember to check the logs"
```

### Bulk Notes Import (`--notes-file`)

Import multiple notes from a JSON file:

```bash
anges -f task.txt --notes-file notes.json
```

#### JSON File Format

The notes file should contain an array of note objects:

```json
[
  {
    "scope": "general",
    "title": "Project Overview",
    "content": "This project focuses on improving CLI documentation for better user experience."
  },
  {
    "scope": "technical",
    "title": "Implementation Notes",
    "content": "The CLI uses argparse for argument parsing and supports multiple execution modes."
  },
  {
    "scope": "project",
    "title": "Requirements",
    "content": "Documentation should be simple, concise, and follow existing style patterns."
  }
]
```

#### Required JSON Fields

Each note must contain the following fields as non-empty strings:
- **`scope`**: The context or category of the note (e.g., "general", "project", "technical")
- **`title`**: A brief title describing the note
- **`content`**: The main content of the note

## Examples

### Basic Examples

```bash
# Simple question
anges -q "List all Python files in the current directory"

# Interactive session with custom working directory
anges -i --path /home/user/project

# Run task from file with debug logging
anges -f task.txt --logging debug
```

### Examples with Notes

```bash
# Add context note for a development task
anges -q "Review the code structure" \
  --notes '{"scope": "project", "title": "Current Phase", "content": "In development phase, focus on code quality"}'

# Use notes file for complex context
anges -f complex_task.txt --notes-file project_context.json

# Combine individual notes with file input
anges -f task.txt \
  --notes '{"scope": "urgent", "title": "Deadline", "content": "Must complete by end of week"}' \
  --notes-file background_info.json
```

### Web Interface Examples

```bash
# Launch web interface on default settings
anges ui

# Launch with custom host and port
anges ui --host 0.0.0.0 --port 8080

# Launch with password protection
anges ui --password mypassword
```

### Advanced Examples

```bash
# Continue from existing session with additional context
anges -i --existing_stream_id abc123 \
  --notes '{"scope": "session", "title": "Previous Context", "content": "Continuing from database analysis task"}'

# Use specific agent with custom model
anges -q "Analyze system performance" \
  --agent task_analyzer \
  --model gemini \
  --notes '{"scope": "system", "title": "Focus Area", "content": "Pay attention to memory usage patterns"}'
```