"""
Tests for advanced tools functionality including file loading.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import os

from agent_expert_panel.tools import (
    load_tools_from_file,
    load_tools_from_directory,
)


class TestAdvancedTools:
    """Test cases for advanced tools functionality."""

    def test_load_tools_from_file_success(self):
        """Test successfully loading tools from a file."""
        # Create a mock file content
        mock_file_content = '''
def test_tool_1():
    """Test tool 1"""
    return "tool1"

def test_tool_2(param):
    """Test tool 2"""
    return f"tool2: {param}"

def _private_tool():
    """Private tool - should not be loaded"""
    return "private"

class NotAFunction:
    """Not a function - should not be loaded"""
    pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(mock_file_content)
            temp_file_path = f.name

        try:
            tools = load_tools_from_file(temp_file_path)

            # Should load public functions
            assert "test_tool_1" in tools
            assert "test_tool_2" in tools

            # Should not load private functions or non-functions
            assert "_private_tool" not in tools
            assert "NotAFunction" not in tools

            # Loaded tools should be callable
            assert callable(tools["test_tool_1"])
            assert callable(tools["test_tool_2"])

        finally:
            os.unlink(temp_file_path)

    def test_load_tools_from_file_not_found(self):
        """Test load_tools_from_file with non-existent file."""
        with pytest.raises(FileNotFoundError, match="Tools file not found"):
            load_tools_from_file("/nonexistent/file.py")

    @patch("importlib.util.spec_from_file_location")
    def test_load_tools_from_file_import_error(self, mock_spec_from_file):
        """Test load_tools_from_file when module import fails."""
        # Mock file exists
        with tempfile.NamedTemporaryFile(suffix=".py") as f:
            # Mock spec creation failure
            mock_spec_from_file.return_value = None

            with pytest.raises(ImportError, match="Could not load module"):
                load_tools_from_file(f.name)

    def test_load_tools_from_directory_success(self):
        """Test successfully loading tools from a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create first tool file
            (temp_path / "tools1.py").write_text("""
def dir_tool_1():
    return "dir_tool_1"

def dir_tool_2():
    return "dir_tool_2"
""")

            # Create second tool file
            (temp_path / "tools2.py").write_text("""
def dir_tool_3():
    return "dir_tool_3"
""")

            # Create a non-Python file (should be ignored)
            (temp_path / "readme.txt").write_text("Not a Python file")

            # Create a file starting with underscore (should be ignored)
            (temp_path / "_private_tools.py").write_text("""
def private_tool():
    return "private"
""")

            tools = load_tools_from_directory(temp_dir)

            # Should load tools from Python files
            assert "dir_tool_1" in tools
            assert "dir_tool_2" in tools
            assert "dir_tool_3" in tools

            # Should not load from private files
            assert "private_tool" not in tools

            # All should be callable
            for tool in tools.values():
                assert callable(tool)

    def test_load_tools_from_directory_not_found(self):
        """Test load_tools_from_directory with non-existent directory."""
        with pytest.raises(FileNotFoundError, match="Tools directory not found"):
            load_tools_from_directory("/nonexistent/directory")

    @patch("agent_expert_panel.tools.simple_tools.load_tools_from_file")
    @patch("builtins.print")
    def test_load_tools_from_directory_with_errors(self, mock_print, mock_load_tools):
        """Test load_tools_from_directory handles file loading errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some files
            (temp_path / "good_tools.py").write_text("def good_tool(): pass")
            (temp_path / "bad_tools.py").write_text("def bad_tool(): pass")

            # Mock load_tools_from_file to succeed for one file and fail for another
            def side_effect(file_path):
                if "bad_tools" in str(file_path):
                    raise Exception("File loading error")
                return {"good_tool": lambda: "good"}

            mock_load_tools.side_effect = side_effect

            tools = load_tools_from_directory(temp_dir)

            # Should get tools from successful file
            assert "good_tool" in tools

            # Should print warning for failed file
            mock_print.assert_called()
            warning_call = str(mock_print.call_args[0][0])
            assert "Warning: Could not load tools from" in warning_call
            assert "bad_tools.py" in warning_call

    @patch("agent_expert_panel.tools.load_tools_from_file")
    @patch("builtins.print")
    def test_load_tools_from_directory_duplicate_tools(
        self, mock_print, mock_load_tools
    ):
        """Test load_tools_from_directory handles duplicate tool names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files that would have duplicate tool names
            (temp_path / "tools1.py").write_text("def duplicate_tool(): pass")
            (temp_path / "tools2.py").write_text("def duplicate_tool(): pass")

            # Mock load_tools_from_file to return duplicate names
            mock_load_tools.side_effect = [
                {"duplicate_tool": lambda: "from_tools1"},
                {"duplicate_tool": lambda: "from_tools2"},
            ]

            tools = load_tools_from_directory(temp_dir)

            # Should have the tool (from the last file processed)
            assert "duplicate_tool" in tools

            # Should print warning about duplicate
            mock_print.assert_called()
            warning_calls = [str(call[0][0]) for call in mock_print.call_args_list]
            duplicate_warnings = [
                call for call in warning_calls if "defined in multiple files" in call
            ]
            assert len(duplicate_warnings) > 0

    def test_load_tools_from_file_with_complex_module(self):
        """Test loading tools from a file with imports and complex functions."""
        complex_content = '''
import json
from typing import Dict, Any

def json_processor(data: str) -> Dict[str, Any]:
    """Process JSON data"""
    return json.loads(data)

async def async_tool(value: int) -> int:
    """Async tool function"""
    return value * 2

def tool_with_defaults(name: str = "default", count: int = 1) -> str:
    """Tool with default parameters"""
    return f"{name}_{count}"
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(complex_content)
            temp_file_path = f.name

        try:
            tools = load_tools_from_file(temp_file_path)

            # Should load all public functions
            assert "json_processor" in tools
            assert "async_tool" in tools
            assert "tool_with_defaults" in tools

            # All should be callable
            for tool in tools.values():
                assert callable(tool)

        finally:
            os.unlink(temp_file_path)

    def test_load_tools_from_directory_empty(self):
        """Test loading tools from an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tools = load_tools_from_directory(temp_dir)
            assert tools == {}

    def test_load_tools_from_directory_no_python_files(self):
        """Test loading tools from a directory with no Python files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create non-Python files
            (temp_path / "readme.md").write_text("# README")
            (temp_path / "config.json").write_text('{"key": "value"}')

            tools = load_tools_from_directory(temp_dir)
            assert tools == {}

    @patch("importlib.util.module_from_spec")
    def test_load_tools_from_file_exec_module_error(self, mock_module_from_spec):
        """Test load_tools_from_file when module execution fails."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test_tool(): pass")
            temp_file_path = f.name

        try:
            # Mock module execution to fail
            mock_module = Mock()
            mock_module_from_spec.return_value = mock_module

            with patch("importlib.util.spec_from_file_location") as mock_spec:
                mock_spec_obj = Mock()
                mock_spec_obj.loader = Mock()
                mock_spec_obj.loader.exec_module.side_effect = Exception(
                    "Execution failed"
                )
                mock_spec.return_value = mock_spec_obj

                # Should raise the execution error
                with pytest.raises(Exception, match="Execution failed"):
                    load_tools_from_file(temp_file_path)

        finally:
            os.unlink(temp_file_path)
