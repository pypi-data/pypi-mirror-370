"""
Tests for the termco CLI module
"""

import pytest
import base64
from io import BytesIO, StringIO
from unittest.mock import patch, mock_open
from src.termcopy.cli import is_terminal_input, read_input, encode_and_format, main


def test_is_terminal_input():
    """Test terminal input detection."""
    # This test depends on the environment, so we just test that it returns a boolean
    result = is_terminal_input()
    assert isinstance(result, bool)


def test_read_input_from_file():
    """Test reading input from a file."""
    test_data = b"Hello, World!"
    with patch("builtins.open", mock_open(read_data=test_data)):
        result = read_input("test.txt")
        assert result == test_data


def test_read_input_from_stdin():
    """Test reading input from stdin."""
    test_data = b"Hello from stdin"
    mock_stdin = BytesIO(test_data)
    with patch("sys.stdin") as mock_sys_stdin:
        mock_sys_stdin.buffer = mock_stdin
        result = read_input()
        assert result == test_data


def test_read_input_file_not_found():
    """Test handling of file not found error."""
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(SystemExit):
            read_input("nonexistent.txt")


def test_read_input_permission_error():
    """Test handling of permission error."""
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(SystemExit):
            read_input("protected.txt")


def test_encode_and_format():
    """Test base64 encoding and OSC 52 formatting."""
    test_data = b"Hello, World!"
    result = encode_and_format(test_data)

    # Base64 encode the test data
    expected_b64 = base64.b64encode(test_data).decode("ascii").replace("\n", "")
    expected_output = f"\033]52;c;{expected_b64}\007"

    assert result == expected_output


def test_encode_and_format_empty():
    """Test encoding empty data."""
    result = encode_and_format(b"")
    expected_output = "\033]52;c;\007"
    assert result == expected_output


@patch("sys.argv", ["termcopy", "--help"])
def test_main_help():
    """Test help output."""
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


@patch("sys.argv", ["termcopy", "--version"])
def test_main_version():
    """Test version output."""
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


@patch("sys.stdin.isatty", return_value=True)
@patch("sys.argv", ["termcopy"])
def test_main_terminal_no_file(mock_isatty):
    """Test main function when terminal input but no file provided."""
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_main_terminal_with_file():
    """Test main function when terminal input with file provided."""
    with patch("sys.stdin.isatty", return_value=True), patch(
        "sys.argv", ["termcopy", "test.txt"]
    ), patch("builtins.open", mock_open(read_data=b"test data")), patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout:
        main()
        output = mock_stdout.getvalue()
        assert output.startswith("\033]52;c;")


def test_main_pipe_input():
    """Test main function when input is from pipe."""
    mock_stdin = BytesIO(b"stdin data")
    with patch("sys.stdin.isatty", return_value=False), patch(
        "sys.argv", ["termcopy"]
    ), patch("sys.stdin") as mock_sys_stdin, patch(
        "sys.stdout", new_callable=StringIO
    ) as mock_stdout:
        mock_sys_stdin.buffer = mock_stdin
        mock_sys_stdin.isatty.return_value = False
        main()
        output = mock_stdout.getvalue()
        assert output.startswith("\033]52;c;")
