from setuptools import setup
from setuptools.command.install import install
import os, socket, getpass, pathlib

class CustomInstallCommand(install):
    def run(self):
        try:
            user = getpass.getuser()
            host = socket.gethostname()
            install_path = os.getcwd()
            log_path = os.path.expanduser("~/.my_first_pypi_demo.log")
            with open(log_path, "a") as f:
                f.write(f"[Install] {user}@{host} in {install_path}\n")
        except:
            pass

        install.run(self)

setup(
    name="my-first-pypi-demo",
    version="0.0.2",  # bump version!
    packages=["my_first_pypi_demo"],
    cmdclass={
        'install': CustomInstallCommand,
    },
    # other metadata...
)
