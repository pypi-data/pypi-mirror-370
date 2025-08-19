**Languages**: [English](utility-functions.md) | [中文](zh/utility-functions.md)

---
# Utility Functions Documentation

This document covers the utility functions and modules that provide core functionality for the Anges agent system. These utilities handle event management, file processing, and other essential operations.

## Event Methods Module (`event_methods.py`)

The event methods module provides comprehensive utilities for managing events, event streams, and event summarization within the agent system.

### Overview

The event methods module contains functions for:
- Event formatting and display
- Event stream construction and management
- Event summarization and truncation
- Event filtering and processing

### Key Functions

#### Event Stream Construction

##### `construct_event_stream_from_events(events, max_consecutive_actions=None)`

Constructs an EventStream from a list of events with intelligent summarization.

**Parameters:**
- `events` (List[Event]): List of events to include in the stream
- `max_consecutive_actions` (int, optional): Maximum consecutive actions before summarization

**Returns:**
- `EventStream`: Constructed event stream with summarized content

**Example:**
```python
from anges.agents.agent_utils.event_methods import construct_event_stream_from_events
from anges.agents.agent_utils.events import Event

# Create events
events = [
    Event(event_type="user_input", content="Hello"),
    Event(event_type="agent_action", content="Processing...")
]

# Construct stream
stream = construct_event_stream_from_events(events, max_consecutive_actions=5)
```

#### Event Summarization

##### `summarize_consecutive_actions(events, start_index, end_index)`

Summarizes a sequence of consecutive agent actions into a single summary event.

**Parameters:**
- `events` (List[Event]): List of events to summarize
- `start_index` (int): Starting index of events to summarize
- `end_index` (int): Ending index of events to summarize

**Returns:**
- `EventSummary`: Summary object containing condensed information

**Example:**
```python
from anges.agents.agent_utils.event_methods import summarize_consecutive_actions

# Summarize events 2-5
summary = summarize_consecutive_actions(events, 2, 5)
print(f"Summary: {summary.summary_text}")
print(f"Action count: {summary.action_count}")
```

#### Event Formatting

##### `format_event_for_display(event, include_metadata=True)`

Formats an event for human-readable display.

**Parameters:**
- `event` (Event): Event to format
- `include_metadata` (bool): Whether to include timestamp and metadata

**Returns:**
- `str`: Formatted event string

**Example:**
```python
from anges.agents.agent_utils.event_methods import format_event_for_display

formatted = format_event_for_display(event, include_metadata=True)
print(formatted)
```

##### `format_event_stream_for_display(event_stream, max_events=None)`

Formats an entire event stream for display.

**Parameters:**
- `event_stream` (EventStream): Event stream to format
- `max_events` (int, optional): Maximum number of events to display

**Returns:**
- `str`: Formatted event stream string

#### Event Filtering

##### `filter_events_by_type(events, event_types)`

Filters events by their type.

**Parameters:**
- `events` (List[Event]): Events to filter
- `event_types` (List[str]): Event types to include

**Returns:**
- `List[Event]`: Filtered events

**Example:**
```python
from anges.agents.agent_utils.event_methods import filter_events_by_type

# Filter for user inputs and agent actions only
filtered = filter_events_by_type(events, ["user_input", "agent_action"])
```

##### `get_recent_events(events, count=10)`

Retrieves the most recent events from a list.

**Parameters:**
- `events` (List[Event]): Events to filter
- `count` (int): Number of recent events to return

**Returns:**
- `List[Event]`: Most recent events

#### Content Truncation

##### `truncate_event_content(event, max_length=1000)`

Truncates event content to a maximum length while preserving readability.

**Parameters:**
- `event` (Event): Event to truncate
- `max_length` (int): Maximum content length

**Returns:**
- `Event`: Event with truncated content

##### `truncate_consecutive_content_lines(content, max_lines=50)`

Truncates content that exceeds maximum line limits.

**Parameters:**
- `content` (str): Content to truncate
- `max_lines` (int): Maximum number of lines

**Returns:**
- `str`: Truncated content

### Configuration

The module uses the following configuration constants:

- `DEFAULT_MAX_CONSECUTIVE_UNSUMMARIZED_ACTIONS = 30`: Default threshold for action summarization

### Usage Patterns

#### Basic Event Stream Processing

```python
from anges.agents.agent_utils.event_methods import (
    construct_event_stream_from_events,
    format_event_stream_for_display,
    filter_events_by_type
)

# Process and display events
events = get_events_from_somewhere()
filtered_events = filter_events_by_type(events, ["user_input", "agent_response"])
stream = construct_event_stream_from_events(filtered_events)
display_text = format_event_stream_for_display(stream)
print(display_text)
```

#### Event Summarization Workflow

```python
from anges.agents.agent_utils.event_methods import (
    summarize_consecutive_actions,
    construct_event_stream_from_events
)

# Create stream with automatic summarization
stream = construct_event_stream_from_events(
    events, 
    max_consecutive_actions=10
)

# Manual summarization of specific range
summary = summarize_consecutive_actions(events, 5, 15)
```

## MIME Files Reader Module (`mime_files_reader.py`)

The MIME files reader module provides functionality for reading and processing various file types using AI models for content analysis.

### Overview

This module serves as a bridge between the agent system and the external `mime_files_reader` library, providing:
- File content analysis using AI models
- Support for multiple file formats (images, PDFs, documents)
- Integration with the application configuration system
- Working directory management

### Key Functions

#### Core Functions

##### `get_mime_reader_instance(working_directory: str) -> MimeFilesReader`

Retrieves or creates a MimeFilesReader instance configured for the application.

**Parameters:**
- `working_directory` (str): Directory path for file operations

**Returns:**
- `MimeFilesReader`: Configured instance for file processing

**Example:**
```python
from anges.agents.agent_utils.mime_files_reader import get_mime_reader_instance

# Get reader instance
reader = get_mime_reader_instance("/path/to/working/directory")
```

##### `read_mime_files(question: str, inputs: List[str], output: str = None, working_directory: str = None) -> str`

Reads and analyzes files using AI models to answer questions about their content.

**Parameters:**
- `question` (str): Question to ask about the file content
- `inputs` (List[str]): List of file paths or URLs to analyze
- `output` (str, optional): Path to save the analysis result
- `working_directory` (str, optional): Working directory for file operations

**Returns:**
- `str`: Analysis result or confirmation message if output file is specified

**Example:**
```python
from anges.agents.agent_utils.mime_files_reader import read_mime_files

# Analyze an image
result = read_mime_files(
    question="What objects are visible in this image?",
    inputs=["/path/to/image.jpg"],
    working_directory="/tmp"
)
print(result)

# Analyze multiple files and save result
read_mime_files(
    question="Summarize the content of these documents",
    inputs=["/path/to/doc1.pdf", "/path/to/doc2.pdf"],
    output="/path/to/summary.txt",
    working_directory="/tmp"
)
```

### Supported File Types

The MIME files reader supports various file formats:

- **Images**: JPEG, PNG, GIF, WebP, SVG
- **Documents**: PDF, Word documents, text files
- **Web Content**: URLs, YouTube links
- **Other**: Various MIME types supported by the underlying library

### Configuration Integration

The module integrates with the application configuration system:

```python
from anges.config import config

# Configuration is automatically used for:
# - API keys for AI models
# - Model selection for analysis
# - Working directory defaults
```

### Usage Patterns

#### Image Analysis

```python
from anges.agents.agent_utils.mime_files_reader import read_mime_files

# Analyze image content
result = read_mime_files(
    question="Describe the main elements in this screenshot",
    inputs=["screenshot.png"],
    working_directory="./temp"
)
```

#### Document Processing

```python
# Extract information from PDF
result = read_mime_files(
    question="What are the key findings in this research paper?",
    inputs=["research_paper.pdf"],
    output="findings_summary.txt"
)
```

#### Multi-file Analysis

```python
# Compare multiple documents
result = read_mime_files(
    question="Compare the approaches described in these documents",
    inputs=["approach_a.pdf", "approach_b.pdf", "approach_c.pdf"],
    working_directory="./analysis"
)
```

#### Web Content Analysis

```python
# Analyze YouTube video content
result = read_mime_files(
    question="What is the main topic of this video?",
    inputs=["https://www.youtube.com/watch?v=example"],
    working_directory="./temp"
)
```

### Error Handling

The module provides error handling for common scenarios:

- **File not found**: Clear error messages for missing files
- **Unsupported formats**: Graceful handling of unsupported file types
- **API errors**: Proper error propagation from AI model APIs
- **Network issues**: Timeout and retry handling for web content

### Best Practices

#### 1. Working Directory Management

```python
# Use absolute paths for working directories
working_dir = os.path.abspath("./temp")
os.makedirs(working_dir, exist_ok=True)

result = read_mime_files(
    question="Analyze this file",
    inputs=["data.pdf"],
    working_directory=working_dir
)
```

#### 2. Question Formulation

```python
# Be specific in questions for better results
specific_question = "List the main technical requirements mentioned in section 3 of this document"
general_question = "What is this document about?"

# Specific questions yield more useful results
result = read_mime_files(specific_question, ["requirements.pdf"])
```

#### 3. Output File Management

```python
# Use output files for large analyses
output_path = "./results/analysis_result.txt"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

read_mime_files(
    question="Provide detailed analysis",
    inputs=["large_document.pdf"],
    output=output_path
)

# Read the result
with open(output_path, 'r') as f:
    analysis = f.read()
```

#### 4. Batch Processing

```python
# Process multiple files efficiently
files_to_analyze = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

for i, file_path in enumerate(files_to_analyze):
    result = read_mime_files(
        question=f"Summarize document {i+1}",
        inputs=[file_path],
        output=f"summary_{i+1}.txt"
    )
```

## Integration with Agent System

Both utility modules integrate seamlessly with the broader agent system:

### Event Methods Integration

```python
# Used by agents for event processing
from anges.agents.agent_utils.event_methods import construct_event_stream_from_events
from anges.agents.agent_utils.events import EventStream

class CustomAgent:
    def process_events(self, events):
        # Use event methods for processing
        stream = construct_event_stream_from_events(events)
        return stream
```

### MIME Reader Integration

```python
# Used by agents for file analysis
from anges.agents.agent_utils.mime_files_reader import read_mime_files

class FileAnalysisAgent:
    def analyze_file(self, file_path, question):
        # Use MIME reader for analysis
        result = read_mime_files(question, [file_path])
        return result
```

## Testing and Debugging

### Event Methods Testing

```python
# Test event stream construction
from anges.agents.agent_utils.events import Event
from anges.agents.agent_utils.event_methods import construct_event_stream_from_events

# Create test events
test_events = [
    Event(event_type="user_input", content="Test input"),
    Event(event_type="agent_action", content="Test action")
]

# Test stream construction
stream = construct_event_stream_from_events(test_events)
assert len(stream.events) > 0
```

### MIME Reader Testing

```python
# Test file reading
from anges.agents.agent_utils.mime_files_reader import read_mime_files

# Test with a simple text file
result = read_mime_files(
    question="What is the content of this file?",
    inputs=["test.txt"],
    working_directory="./test_data"
)
assert result is not None
```

These utility functions form the foundation of the Anges agent system's file processing and event management capabilities, providing robust and flexible tools for building intelligent agent workflows.