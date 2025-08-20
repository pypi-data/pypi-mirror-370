"""
Unit tests for the process utilities in tools/benchmark/utils.py.

This test suite focuses on two main utilities:

1. find_server_pid: Function for locating the PID of the FastAPI/uvicorn server process
   using multiple fallback methods:
   - Process command line matching for uvicorn server processes
   - Port binding detection for processes listening on port 3000
   - Log pattern matching for "Started server process [PID]" messages

2. perform_repeated: Function for executing operations multiple times and measuring performance:
   - Handles immediate responses and calculates time differences
   - Supports long-running tasks with task IDs and status polling
   - Provides error handling for failed operations and status checks

The tests use extensive mocking of system utilities (psutil, subprocess, requests) to simulate
different scenarios without interacting with actual system processes or making real HTTP calls,
ensuring tests are deterministic and environment-independent.

Test cases for find_server_pid:
- test_find_server_pid_by_cmdline: Tests PID detection via command line inspection
- test_find_server_pid_by_port: Tests PID detection via port binding
- test_find_server_pid_by_log: Tests PID detection via log pattern matching
- test_find_server_pid_not_found: Tests proper handling when no server is found

Test cases for perform_repeated:
- test_perform_repeated_basic: Tests basic operation with direct responses
- test_perform_repeated_with_task_id: Tests long-running operations with task IDs
- test_perform_repeated_error_response: Tests error handling for operation failures
- test_perform_repeated_status_error: Tests error handling for status check failures
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
import sys
import os
import importlib
from datetime import timedelta
import pytest

# Add the root directory to the Python path to find the tools package
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, root_dir)

# Import the module after path manipulation
tools_utils = importlib.import_module("tools.benchmark.utils")
find_server_pid = tools_utils.find_server_pid
perform_repeated = tools_utils.perform_repeated


class TestBenchmarkUtils(unittest.TestCase):
    @patch("psutil.process_iter")
    def test_find_server_pid_by_cmdline(self, mock_process_iter):
        # Setup mock processes with specific command lines
        mock_process1 = MagicMock()
        mock_process1.info = {
            "pid": 1234,
            "name": "python",
            "cmdline": ["python", "-m", "uvicorn", "app.py"],
        }

        mock_process2 = MagicMock()
        mock_process2.info = {
            "pid": 5678,
            "name": "python",
            "cmdline": ["python", "something_else.py"],
        }

        # Return the mock processes when process_iter is called
        mock_process_iter.return_value = [mock_process1, mock_process2]

        # Test the function
        pid = find_server_pid()

        # Verify the correct PID was found
        self.assertEqual(pid, 1234)

    @patch("psutil.process_iter")
    @patch("subprocess.check_output")
    @patch("psutil.Process")
    def test_find_server_pid_by_port(
        self, mock_process, mock_check_output, mock_process_iter
    ):
        # Make first method fail by returning processes without uvicorn
        mock_process1 = MagicMock()
        mock_process1.info = {
            "pid": 1234,
            "name": "python",
            "cmdline": ["python", "something_else.py"],
        }
        mock_process_iter.return_value = [mock_process1]

        # Make second method succeed by mocking port check
        mock_check_output.return_value = b"5678\n"

        # Mock the process object returned by psutil.Process
        process_instance = MagicMock()
        process_instance.name.return_value = "python"
        mock_process.return_value = process_instance

        # Test the function
        pid = find_server_pid()

        # Verify the correct PID was found
        self.assertEqual(pid, 5678)
        # Verify subprocess was called with the right command
        mock_check_output.assert_called_with("lsof -i :3000 -t", shell=True)

    @patch("psutil.process_iter")
    @patch("subprocess.check_output")
    def test_find_server_pid_by_log(self, mock_check_output, mock_process_iter):
        # Make first method fail
        mock_process1 = MagicMock()
        mock_process1.info = {
            "pid": 1234,
            "name": "python",
            "cmdline": ["python", "something_else.py"],
        }
        mock_process_iter.return_value = [mock_process1]

        # Make second method fail with CalledProcessError
        def side_effect_func(cmd, shell):
            if "lsof" in cmd:
                raise subprocess.CalledProcessError(1, cmd)
            elif "grep" in cmd:
                return b"user 9999 1111  0 12:00 ?  00:00:00 /bin/python Started server process [9876]"
            return b""

        mock_check_output.side_effect = side_effect_func

        # Test the function
        pid = find_server_pid()

        # Verify the correct PID was found
        self.assertEqual(pid, 9876)

    @patch("psutil.process_iter")
    @patch("subprocess.check_output")
    def test_find_server_pid_not_found(self, mock_check_output, mock_process_iter):
        # Make all methods fail
        mock_process_iter.return_value = []

        def side_effect_func(cmd, shell):
            raise subprocess.CalledProcessError(1, cmd)

        mock_check_output.side_effect = side_effect_func

        # Test the function
        pid = find_server_pid()

        # Verify no PID was found
        self.assertIsNone(pid)

    # tests for perform_repeated function

    @patch("requests.get")
    def test_perform_repeated_basic(self, mock_get):
        # Setup mock operation and response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "created_at": "2023-01-01T12:00:00.000",
            "completed_at": "2023-01-01T12:00:01.000",
        }

        mock_get.return_value = mock_get_response

        operation = MagicMock(return_value=mock_response)
        operation.__name__ = "test_operation"

        # Call the function
        with patch("time.sleep"):
            result = perform_repeated("http://test-server", operation, 2, 0.1)

        # Check that operation was called twice
        self.assertEqual(operation.call_count, 2)
        # Check that we got 2 elapsed times
        self.assertEqual(len(result), 2)

    @patch("requests.get")
    def test_perform_repeated_with_task_id(self, mock_get):
        # Setup mock operation and response with task ID
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task-123"}

        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "status": "completed",
            "result": {},
            "created_at": "2023-01-01T12:00:00.000",
            "completed_at": "2023-01-01T12:00:01.000",
        }

        mock_get.return_value = mock_get_response

        operation = MagicMock(return_value=mock_response)
        operation.__name__ = "test_operation"

        # Call the function
        with patch("time.sleep"):
            result = perform_repeated("http://test-server", operation, 1, 0.1)

        # Check that get was called with the correct URL
        mock_get.assert_called_with("http://test-server/status/task-123")
        # Check timing extraction
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], timedelta(seconds=1))

    def test_perform_repeated_error_response(self):
        # Setup mock operation with error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad request"}

        operation = MagicMock(return_value=mock_response)
        operation.__name__ = "test_operation"

        # Call the function and expect SystemExit with code 1
        with pytest.raises(SystemExit) as excinfo:
            perform_repeated("http://test-server", operation, 1, 0.1)

        # Verify exit code was 1
        assert excinfo.value.code == 1

    @patch("requests.get")
    def test_perform_repeated_status_error(self, mock_get):
        # Setup mock operation with task ID
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task-123"}

        # But status check fails
        mock_get_response = MagicMock()
        mock_get_response.status_code = 500
        mock_get_response.json.return_value = {"error": "Server error"}

        mock_get.return_value = mock_get_response

        operation = MagicMock(return_value=mock_response)
        operation.__name__ = "test_operation"

        # Call the function and expect SystemExit with code 2
        with patch("time.sleep"):
            with pytest.raises(SystemExit) as excinfo:
                perform_repeated("http://test-server", operation, 1, 0.1)

        # Verify exit code was 2
        assert excinfo.value.code == 2


if __name__ == "__main__":
    unittest.main()
