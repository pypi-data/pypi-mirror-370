import os
import pytest
from anges.utils.agent_edit_file import agent_file_editing_operation, get_agent_file_editing_operation_output


@pytest.fixture
def temp_file(tmp_path):
    """Creates a temporary file path for each test."""
    file_path = tmp_path / "test_file.txt"
    return file_path


def test_new_file_creation(temp_file):
    content = f"""NEW_FILE {temp_file}
First line of the file.
Second line of the file."""
    result = get_agent_file_editing_operation_output(content)
    assert os.path.exists(temp_file)
    assert "File created successfully:" in result
    assert "1\tFirst line of the file." in result
    assert "2\tSecond line of the file." in result


def test_new_file_creation_existing_file(temp_file):
    temp_file.write_text("Existing content.")
    content = f"""NEW_FILE {temp_file}
First line of the file."""
    with pytest.raises(FileExistsError) as excinfo:
        agent_file_editing_operation(content)
    assert f"File '{temp_file}' already exists." in str(excinfo.value)


def test_insert_lines_at_start(temp_file):
    temp_file.write_text("Line 1\nLine 2\nLine 3")
    content = f"""INSERT_LINES {temp_file} 0
Inserted at the start."""
    result = get_agent_file_editing_operation_output(content)
    assert "Lines inserted successfully:" in result
    assert "+Inserted at the start." in result
    assert " Line 1" in result


def test_insert_lines_at_middle(temp_file):
    temp_file.write_text("Line 1\nLine 2\nLine 3")
    content = f"""INSERT_LINES {temp_file} 2
Inserted before Line 2."""
    result = get_agent_file_editing_operation_output(content)
    assert "Lines inserted successfully:" in result
    assert "+Inserted before Line 2." in result
    assert " Line 2" in result


def test_insert_lines_at_end(temp_file):
    temp_file.write_text("Line 1\nLine 2\nLine 3")
    content = f"""INSERT_LINES {temp_file} -1
Inserted at the end."""
    result = get_agent_file_editing_operation_output(content)
    assert "Lines inserted successfully:" in result
    assert "+Inserted at the end." in result


def test_insert_lines_file_not_found(tmp_path):
    non_existent_file = tmp_path / "non_existent_file.txt"
    content = f"""INSERT_LINES {non_existent_file} 1
Some content"""
    with pytest.raises(FileNotFoundError) as excinfo:
        agent_file_editing_operation(content)
    assert f"File '{non_existent_file}' does not exist." in str(excinfo.value)


def test_remove_lines(temp_file):
    temp_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    content = f"REMOVE_LINES {temp_file} 2-4"
    result = get_agent_file_editing_operation_output(content)
    assert "Lines removed successfully:" in result
    assert "-Line 2" in result
    assert "-Line 3" in result
    assert "-Line 4" in result


def test_remove_lines_invalid_range(temp_file):
    temp_file.write_text("Line 1\nLine 2\nLine 3")
    content = f"REMOVE_LINES {temp_file} 5-10"
    with pytest.raises(ValueError) as excinfo:
        agent_file_editing_operation(content)
    assert "Invalid line range: 5-10." in str(excinfo.value)


def test_remove_lines_file_not_found(tmp_path):
    non_existent_file = tmp_path / "non_existent_file.txt"
    content = f"REMOVE_LINES {non_existent_file} 1-2"
    with pytest.raises(FileNotFoundError) as excinfo:
        agent_file_editing_operation(content)
    assert f"File '{non_existent_file}' does not exist." in str(excinfo.value)


def test_replace_lines(temp_file):
    temp_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    content = f"""REPLACE_LINES {temp_file} 2-4
Replacement Line 1.
Replacement Line 2.
Replacement Line 3."""
    result = get_agent_file_editing_operation_output(content)
    assert "Lines replaced successfully:" in result
    assert "-Line 2" in result
    assert "+Replacement Line 1." in result
    assert "+Replacement Line 2." in result
    assert "+Replacement Line 3." in result


def test_replace_lines_more_content(temp_file):
    """Test replacing lines with more content than original range."""
    temp_file.write_text("Line 1\nLine 2\nLine 3\nLine 4")
    content = f"""REPLACE_LINES {temp_file} 2-3
Replacement Line 1.
Replacement Line 2.
Replacement Line 3.
Replacement Line 4."""
    result = get_agent_file_editing_operation_output(content)
    assert "Lines replaced successfully:" in result
    assert "-Line 2" in result
    assert "+Replacement Line 3." in result
    assert "+Replacement Line 4." in result


def test_replace_lines_less_content(temp_file):
    """Test replacing lines with less content than original range."""
    temp_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")
    content = f"""REPLACE_LINES {temp_file} 2-4
Single replacement line."""
    result = get_agent_file_editing_operation_output(content)
    assert "-Line 2" in result
    assert "+Single replacement line." in result


def test_replace_lines_edge_range(temp_file):
    """Test replacing lines at file boundaries."""
    temp_file.write_text("Line 1\nLine 2\nLine 3")
    content = f"""REPLACE_LINES {temp_file} 1-3
Complete replacement."""
    result = get_agent_file_editing_operation_output(content)
    assert "Lines replaced successfully:" in result
    assert "+Complete replacement." in result
    with open(temp_file, "r") as f:
        assert len(f.readlines()) == 1


def test_replace_lines_invalid_range(temp_file):
    """Test replacing lines with invalid range."""
    temp_file.write_text("Line 1\nLine 2\nLine 3")
    content = f"""REPLACE_LINES {temp_file} 4-5
This should fail."""
    with pytest.raises(ValueError) as excinfo:
        agent_file_editing_operation(content)
    assert "Invalid line range" in str(excinfo.value)


def test_invalid_format():
    content = "NEW_FILE"
    with pytest.raises(ValueError) as excinfo:
        agent_file_editing_operation(content)
    assert "Invalid directive line format." in str(excinfo.value)


def test_empty_content():
    content = ""
    with pytest.raises(ValueError) as excinfo:
        agent_file_editing_operation(content)
    assert "Invalid directive line format." in str(excinfo.value)


def test_get_agent_file_editing_operation_output_success(temp_file):
    """Test successful operation output formatting."""
    content = f"""NEW_FILE {temp_file}
First line
Second line"""
    result = get_agent_file_editing_operation_output(content)
    assert "- FILE_EDITING_DIRECTIVE: NEW_FILE" in result
    assert "1\tFirst line" in result
    assert "2\tSecond line" in result
    assert result.startswith("\n******\n")
    assert result.endswith("\n******\n")


def test_get_agent_file_editing_operation_output_error():
    """Test error operation output formatting."""
    content = "INVALID_DIRECTIVE"
    result = get_agent_file_editing_operation_output(content)
    assert "- FILE_EDITING_DIRECTIVE: INVALID_DIRECTIVE" in result
    assert "- ERROR: Invalid directive line format." in result
    assert result.startswith("\n******\n")
    assert result.endswith("\n******\n")


def test_get_agent_file_editing_operation_output_with_custom_dir(temp_file):
    """Test operation with custom initial directory."""
    parent_dir = os.path.dirname(temp_file)
    file_name = os.path.basename(temp_file)
    content = f"NEW_FILE {file_name}\nTest content"
    result = get_agent_file_editing_operation_output(content, parent_dir)
    assert "- FILE_EDITING_DIRECTIVE: NEW_FILE" in result
    assert "- RESULT:" in result
    assert "1\tTest content" in result
