#!/usr/bin/env python
"""Setup script for AutoCoder AI"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from __version__.py or use default
def read_version():
    """Read version from __version__.py file."""
    version_file = Path(__file__).parent / '__version__.py'
    if version_file.exists():
        version_dict = {}
        with open(version_file) as f:
            exec(f.read(), version_dict)
            return version_dict.get('__version__', '2.0.0')
    return '2.0.0'  # Default version

# Minimal setup.py since we're using pyproject.toml
setup(
    version=read_version(),
    packages=find_packages(where='.', include=['agents*', 'utils*', 'workflow*', 'memory*', 'web_interface*', 'git_integration*', 'sandbox*']),
    py_modules=['autocoder', 'main', 'main_api', 'enhanced_main', 'cli_websocket_client'],
)
