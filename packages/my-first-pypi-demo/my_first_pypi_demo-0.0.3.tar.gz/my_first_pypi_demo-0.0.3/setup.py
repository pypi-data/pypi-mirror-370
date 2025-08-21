from setuptools import setup, find_packages

setup(
    name='my-first-pypi-demo',
    version='0.0.3',  # Change version to 0.0.3
    author='Your Name',
    author_email='you@example.com',
    description='A demo package to learn PyPI publishing',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my-first-pypi-demo',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)

