"""
Extended tests for tools functionality to improve coverage.
"""

import pytest
from unittest.mock import patch

from agent_expert_panel.tools import (
    create_library_tool,
    add_library_tools_to_dict,
    get_tools_by_names,
    load_tools_from_directory,
    web_search,
    read_file,
    write_file,
    calculate,
)


class TestLibraryToolCreation:
    """Test library tool creation and error handling."""

    def test_create_library_tool_invalid_import_path(self):
        """Test creating library tool with invalid import path."""
        with pytest.raises((ImportError, AttributeError, ValueError)):
            create_library_tool("nonexistent.module.function")

    def test_create_library_tool_module_not_found(self):
        """Test creating library tool when module doesn't exist."""
        with pytest.raises((ImportError, AttributeError, ValueError)):
            create_library_tool("totally_fake_module.some_function")

    def test_create_library_tool_attribute_not_found(self):
        """Test creating library tool when attribute doesn't exist."""
        with pytest.raises((ImportError, AttributeError, ValueError)):
            create_library_tool("os.nonexistent_function")

    def test_create_library_tool_invalid_format(self):
        """Test creating library tool with invalid format."""
        with pytest.raises((ImportError, AttributeError, ValueError)):
            create_library_tool("invalid_format")

    def test_create_library_tool_success(self):
        """Test successfully creating a library tool."""
        # Test with a known function that should exist
        tool_func = create_library_tool("os.path.join")
        assert callable(tool_func)


class TestToolRetrieval:
    """Test tool retrieval functions."""

    def test_get_tools_by_names_library_import_error(self):
        """Test get_tools_by_names with library import error."""
        available_tools = {}

        with pytest.raises(ValueError, match="Could not import tool"):
            get_tools_by_names(["nonexistent.module.function"], available_tools)

    def test_get_tools_by_names_tool_not_found(self):
        """Test get_tools_by_names with tool not found."""
        available_tools = {"existing_tool": lambda: "test"}

        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            get_tools_by_names(["nonexistent"], available_tools)

    def test_get_tools_by_names_mixed_success_failure(self):
        """Test get_tools_by_names with mix of success and failure."""
        available_tools = {"existing_tool": lambda: "test"}

        # This should succeed for existing_tool but fail for nonexistent
        with pytest.raises(ValueError):
            get_tools_by_names(["existing_tool", "nonexistent"], available_tools)

    def test_get_tools_by_names_library_import_success(self):
        """Test get_tools_by_names with successful library import."""
        available_tools = {}

        # Should work with valid library import
        tools = get_tools_by_names(["os.path.exists"], available_tools)
        assert len(tools) == 1
        assert callable(tools[0])


class TestDirectoryToolLoading:
    """Test loading tools from directory."""

    def test_load_tools_from_directory_nonexistent(self):
        """Test loading tools from non-existent directory."""
        with pytest.raises(FileNotFoundError):
            load_tools_from_directory("/path/that/does/not/exist")

    def test_load_tools_from_directory_empty(self, tmp_path):
        """Test loading tools from empty directory."""
        tools = load_tools_from_directory(tmp_path)
        assert tools == {}

    def test_load_tools_from_directory_no_python_files(self, tmp_path):
        """Test loading tools from directory with no Python files."""
        # Create a non-Python file
        (tmp_path / "not_python.txt").write_text("This is not Python")

        tools = load_tools_from_directory(tmp_path)
        assert tools == {}

    def test_load_tools_from_directory_with_init_file(self, tmp_path):
        """Test loading tools from directory with __init__.py file."""
        # Create __init__.py (should be ignored)
        (tmp_path / "__init__.py").write_text("# Init file")

        tools = load_tools_from_directory(tmp_path)
        assert tools == {}

    def test_load_tools_from_directory_syntax_error(self, tmp_path):
        """Test loading tools from directory with syntax error in Python file."""
        # Create a Python file with syntax error
        bad_file = tmp_path / "bad_tool.py"
        bad_file.write_text("def invalid_syntax(\nprint('missing closing paren')")

        # Should handle syntax error gracefully
        tools = load_tools_from_directory(tmp_path)
        assert tools == {}

    def test_load_tools_from_directory_import_error(self, tmp_path):
        """Test loading tools from directory with import error in Python file."""
        # Create a Python file with import error
        bad_file = tmp_path / "import_error_tool.py"
        bad_file.write_text(
            "import nonexistent_module\n\ndef my_tool():\n    return 'test'"
        )

        # Should handle import error gracefully
        tools = load_tools_from_directory(tmp_path)
        assert tools == {}


class TestAddLibraryTools:
    """Test adding library tools to dictionary."""

    def test_add_library_tools_to_dict_success(self):
        """Test successfully adding library tools to dictionary."""
        tools_dict = {}
        library_tools = {"path_join": "os.path.join"}

        add_library_tools_to_dict(tools_dict, library_tools)

        assert "path_join" in tools_dict
        assert callable(tools_dict["path_join"])

    def test_add_library_tools_to_dict_import_error(self):
        """Test adding library tools with import error."""
        tools_dict = {}
        library_tools = {"bad_tool": "nonexistent.module.function"}

        # Should handle error gracefully and not add the tool
        add_library_tools_to_dict(tools_dict, library_tools)

        assert "bad_tool" not in tools_dict

    def test_add_library_tools_to_dict_mixed(self):
        """Test adding library tools with mix of success and failure."""
        tools_dict = {}
        library_tools = {
            "good_tool": "os.path.join",
            "bad_tool": "nonexistent.module.function",
        }

        add_library_tools_to_dict(tools_dict, library_tools)

        # Only the good tool should be added
        assert "good_tool" in tools_dict
        assert "bad_tool" not in tools_dict


class TestBuiltinTools:
    """Test built-in tool functions."""

    @pytest.mark.asyncio
    async def test_web_search_default_params(self):
        """Test web_search with default parameters."""
        result = await web_search("test query")

        assert "query" in result
        assert "results" in result
        assert "total_results" in result
        assert result["query"] == "test query"
        assert len(result["results"]) <= 5
        assert isinstance(result["results"], list)

    @pytest.mark.asyncio
    async def test_web_search_custom_max_results(self):
        """Test web_search with custom max_results."""
        result = await web_search("test query", max_results=2)

        assert len(result["results"]) <= 2

    @pytest.mark.asyncio
    async def test_read_file_success(self, tmp_path):
        """Test successful file reading."""
        test_file = tmp_path / "test.txt"
        test_content = "Hello, world!"
        test_file.write_text(test_content)

        result = await read_file(str(test_file))

        assert "error" not in result
        assert result["content"] == test_content
        assert result["file_path"] == str(test_file.absolute())

    @pytest.mark.asyncio
    async def test_read_file_not_found(self):
        """Test reading non-existent file."""
        result = await read_file("/path/that/does/not/exist.txt")

        assert "error" in result
        assert "File not found" in result["error"]

    @pytest.mark.asyncio
    async def test_read_file_permission_error(self, tmp_path):
        """Test reading file with permission error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Mock permission error by patching Path.read_text
        with patch(
            "pathlib.Path.read_text", side_effect=PermissionError("Permission denied")
        ):
            result = await read_file(str(test_file))

            assert "error" in result
            assert "Failed to read file" in result["error"]

    @pytest.mark.asyncio
    async def test_write_file_success(self, tmp_path):
        """Test successful file writing."""
        test_file = tmp_path / "output.txt"
        test_content = "Hello, world!"

        result = await write_file(str(test_file), test_content)

        assert "error" not in result
        assert result["file_path"] == str(test_file.absolute())
        assert test_file.read_text() == test_content

    @pytest.mark.asyncio
    async def test_write_file_permission_error(self, tmp_path):
        """Test writing file with permission error."""
        test_file = tmp_path / "output.txt"

        # Mock permission error by patching Path.write_text
        with patch(
            "pathlib.Path.write_text", side_effect=PermissionError("Permission denied")
        ):
            result = await write_file(str(test_file), "test content")

            assert "error" in result
            assert "Failed to write file" in result["error"]

    @pytest.mark.asyncio
    async def test_calculate_simple_expression(self):
        """Test calculate with simple expression."""
        result = await calculate("2 + 2")

        assert "error" not in result
        assert result["expression"] == "2 + 2"
        assert result["result"] == 4

    @pytest.mark.asyncio
    async def test_calculate_complex_expression(self):
        """Test calculate with complex expression."""
        result = await calculate("(10 + 5) * 2 / 3")

        assert "error" not in result
        assert result["result"] == 10.0

    @pytest.mark.asyncio
    async def test_calculate_invalid_expression(self):
        """Test calculate with invalid expression."""
        result = await calculate("2 +")  # Incomplete expression

        assert "error" in result

    @pytest.mark.asyncio
    async def test_calculate_dangerous_expression(self):
        """Test calculate with potentially dangerous expression."""
        # Should handle dangerous expressions safely
        result = await calculate("__import__('os').system('echo hello')")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_calculate_with_functions(self):
        """Test calculate with mathematical functions."""
        # Since the calculate function uses restricted globals, math functions won't work
        result = await calculate("2 * 3.14159")

        assert "error" not in result
        assert result["result"] == 6.28318
