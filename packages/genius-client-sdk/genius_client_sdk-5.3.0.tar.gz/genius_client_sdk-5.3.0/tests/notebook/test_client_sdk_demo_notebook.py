import os
import sys
import subprocess
import time
import requests
import threading
import pytest
import nbformat
from pathlib import Path
from nbconvert.preprocessors import ExecutePreprocessor
from requests.exceptions import RequestException
from threading import Thread

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test_fixtures import PATH_TO_REPO_ROOT
from genius_client_sdk.configuration import default_agent_config

NOTEBOOK_DIRECTORY = PATH_TO_REPO_ROOT + "demo/client-sdk/"
max_server_start_time_seconds = 90
max_notebook_run_time_seconds = 30


def get_notebook_files():
    """
    Returns a list of all the Jupyter notebook files in the NOTEBOOK_DIRECTORY.
    """
    notebook_dir = Path(NOTEBOOK_DIRECTORY)
    return [file.name for file in notebook_dir.glob("*.ipynb")]


def is_port_open(port):
    """
    Checks if a given port is open and accepting connections.

    Args:
        port (int): The port number to check.

    Returns:
        bool: True if the port is open, False otherwise.
    """
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}"], capture_output=True, text=True
        )

        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


def test_notebook_files():
    """
    Ensures that there is at least one notebook file in the NOTEBOOK_DIRECTORY.
    """
    assert len(get_notebook_files()) > 0, (
        "No notebook files found in the directory (" + NOTEBOOK_DIRECTORY + ")."
    )


def start_gent_via_docker_compose():
    """
    Starts the agent in a Docker container using Docker Compose.
    """
    command = f"docker compose --project-directory {PATH_TO_REPO_ROOT} up"
    print(f"Running Docker Compose command: {command} from directory {os.getcwd()}")
    try:
        result = subprocess.run(command, shell=True)
        print(f"Docker Compose output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Docker Compose failed to start: {e}")
        print(f"Error output: {e.stderr}")
        raise e


def wait_for_server_to_accept_get(url):
    """
    Waits for a server to accept GET requests at the specified URL, with a maximum wait time.

    This function attempts to make a GET request to the specified URL, and returns True if the request is successful (i.e. the server is accepting requests). If the request fails, it retries the request with an exponentially increasing wait time, up to the maximum wait time.

    Args:
        url (str): The URL to make the GET request to.

    Returns:
        bool: True if the server accepts the GET request within the maximum wait time, False otherwise.
    """
    start_time = time.time()
    wait_time = 0.1  # Start with a 100ms wait time

    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return True  # Return True if the request is successful
        except RequestException:
            elapsed_time = time.time() - start_time
            if elapsed_time + wait_time > max_server_start_time_seconds:
                return False  # Return False if the max wait time is exceeded

            print(f"Request failed. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            wait_time = min(
                wait_time * 2, max_server_start_time_seconds - elapsed_time
            )  # Double the wait time, but don't exceed remaining time


# this one is a bit troublesome as docker image starts on 8080 but raw agent starts on 3000 by default
def start_server_in_thread_wait_for_it_to_come_online() -> Thread:
    assert not (is_port_open(default_agent_config.agent_port)), (
        f"Port {default_agent_config.agent_port} is already in use"
    )

    agent_thread = threading.Thread(target=start_gent_via_docker_compose)
    print("Starting the agent")
    agent_thread.start()
    assert agent_thread.is_alive(), f"Agent thread is not running: {agent_thread}"

    print("Waiting for the agent to come online")
    try:
        wait_for_server_to_accept_get(default_agent_config.agent_url)
    except Exception as e:
        print(f"Error waiting for server to start: {str(e)}")
        try:
            agent_thread.join()
        except Exception as e:
            print(f"Error joining agent thread: {str(e)}")
        raise e

    print("Agent started")
    return agent_thread


@pytest.mark.skip(
    reason="Running agent directly via uv seems to result in different behavior from running in Docker (including different payloads and ports). Fix this up later once we get more of that clarified"
)
@pytest.mark.parametrize("notebook_filename", get_notebook_files())
def test_notebook_execution(notebook_filename):
    """
    Executes a Jupyter notebook file and ensures it runs to completion without errors.

    This function loads the specified notebook file, configures the notebook execution with a timeout of 600 seconds and the 'python3' kernel, and then preprocesses the notebook to execute all the cells. If any exceptions occur during the execution, the test will fail.
    """
    server_thread = start_server_in_thread_wait_for_it_to_come_online()

    try:
        # Load the notebook
        with open(NOTEBOOK_DIRECTORY + notebook_filename) as f:
            nb = nbformat.read(f, as_version=4)

        # Configure the notebook execution
        ep = ExecutePreprocessor(
            timeout=max_notebook_run_time_seconds, kernel_name="python3"
        )
        try:
            # Execute the notebook
            ep.preprocess(nb, {"metadata": {"path": NOTEBOOK_DIRECTORY}})
        except Exception as e:
            pytest.fail(
                f"Error executing the notebook {notebook_filename} in directory {NOTEBOOK_DIRECTORY} (CWD is {os.getcwd()}): {str(e)}"
            )
    finally:
        try:
            server_thread.join()
        except Exception:
            return
