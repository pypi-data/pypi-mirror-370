import pytest

from unittest import mock

from kaya_module_sdk.src.utils.shell import shell_cmd


@mock.patch("subprocess.Popen")
def test_shell_cmd_without_user(mock_popen):
    """Test the function without a user argument"""
    # NOTE: Mock the Popen object to simulate process output
    mock_process = mock.Mock()
    mock_process.communicate.return_value = ("hello\n", "")
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    command = ["echo", "hello"]
    output, error, return_code = shell_cmd(command)
    assert "hello" in output
    assert error.strip("b''") == ""
    assert return_code == 0


@mock.patch("subprocess.Popen")
def test_shell_cmd_with_error(mock_popen):
    """Test error handling in the function"""
    # NOTE: Mock the Popen object to simulate process output with error
    mock_process = mock.Mock()
    mock_process.communicate.return_value = ("", "Error: command not found\n")
    mock_process.returncode = 1
    mock_popen.return_value = mock_process
    command = ["nonexistent_command"]
    output, error, return_code = shell_cmd(command)
    assert output.strip("b''") == ""
    assert "not found" in error
    assert return_code == 127


@mock.patch("subprocess.Popen")
def test_shell_cmd_empty_command(mock_popen):
    """Test that the function handles empty commands gracefully"""
    command = []
    # Test empty command should not fail
    with pytest.raises(ValueError):
        shell_cmd(command)
