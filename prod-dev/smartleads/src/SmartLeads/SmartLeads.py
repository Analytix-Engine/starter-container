# System imports
import importlib
import multiprocessing
import socket
import time

# Third-party imports
import webview
from streamlit.web.cli import main as streamlit_main

# Local imports
import SmartLeads.streamlit_app.app as app

"""
The main entry point to run the Streamlit UI app.
"""


def get_next_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def is_streamlit_server_running(port: str) -> bool:
    """
    Create a socket and attempt to connect to the Streamlit server

    Args:
        port (str): The port number of the Streamlit server

    Returns:
        bool: True if the Streamlit server is running, False otherwise
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", port))
        return True
    except ConnectionRefusedError:
        return False
    finally:
        sock.close()


def attempt_to_connect_to_streamlit_server(port: str, number_retries: int) -> bool:
    """
    Attempt to connect to the Streamlit server

    Args:
        port (str): The port number of the Streamlit server
        number_retries (str): The number of times to retry connecting to the Streamlit server

    Returns:
        bool: True if the Streamlit server is running, False otherwise
    """
    for _ in range(number_retries):
        if is_streamlit_server_running(port):
            return True
        time.sleep(1)
    return False


def run_streamlit(port):
    streamlit_app = importlib.import_module(app.__name__)

    # Todo: Update streamlit run to use the .streamlit/config.toml settings.
    streamlit_main(
        [
            "run",
            str(streamlit_app.__file__),
            "--server.address=localhost",
            f"--server.port={port}",
            "--server.headless=True",
            "--theme.primaryColor=#38A1FF",
            "--theme.backgroundColor=#FFFFFF",
            "--theme.textColor=#000000",
            "--theme.font=sans serif",
            "--client.toolbarMode=minimal",
            "--global.disableWatchdogWarning=True",
            "--global.developmentMode=False",
        ]
    )


if __name__ == "__main__":
    port = get_next_free_port()
    streamlit_process = multiprocessing.Process(target=run_streamlit, args=(port,))
    streamlit_process.start()
    if attempt_to_connect_to_streamlit_server(port, 10):
        webview.create_window("SmartLeads", f"http://localhost:{port}")
        webview.start()
    streamlit_process.kill()
