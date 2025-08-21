import os
import socket
import getpass
import pathlib

def log_installation_info():
    try:
        user = getpass.getuser()
        host = socket.gethostname()
        current_dir = pathlib.Path(__file__).resolve().parent
        log_path = pathlib.Path.home() / ".my_first_pypi_demo.log"
        with open(log_path, "a") as f:
            f.write(f"Installed by: {user}@{host} in {current_dir}\n")
    except Exception as e:
        # Fail silently in PoC
        pass

log_installation_info()

