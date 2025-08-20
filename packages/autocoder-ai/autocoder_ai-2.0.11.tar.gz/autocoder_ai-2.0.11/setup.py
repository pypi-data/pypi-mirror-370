#!/usr/bin/env python
"""Setup script for AutoCoder AI"""

import os
import sys
import stat
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
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


def create_wrapper_script():
    """Create a wrapper script for autocoder command."""
    wrapper_content = '''#!/bin/sh
# Auto-generated wrapper script for autocoder
exec python3 -m autocoder "$@"
'''
    
    # List of potential locations to try
    locations = [
        '/usr/local/bin/autocoder',  # Global location (requires root)
        os.path.expanduser('~/bin/autocoder'),  # User's bin directory
        os.path.expanduser('~/.local/bin/autocoder'),  # User's local bin
    ]
    
    for location in locations:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(location), exist_ok=True)
            
            # Write the wrapper script
            with open(location, 'w') as f:
                f.write(wrapper_content)
            
            # Make it executable
            st = os.stat(location)
            os.chmod(location, st.st_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            print(f"✓ Created autocoder wrapper at: {location}")
            
            # Check if location is in PATH
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            if os.path.dirname(location) not in path_dirs:
                print(f"  Note: {os.path.dirname(location)} is not in your PATH")
                print(f"  Add it with: export PATH='{os.path.dirname(location)}:$PATH'")
            
            return True
            
        except (OSError, PermissionError) as e:
            # Try next location
            continue
    
    # If we couldn't create a wrapper anywhere, provide instructions
    print("⚠ Could not create autocoder wrapper script automatically.")
    print("  You can still use: python3 -m autocoder")
    return False


class CustomInstallCommand(install):
    """Custom installation command that creates wrapper script."""
    
    def run(self):
        # Run the standard installation
        install.run(self)
        
        # Create the wrapper script
        print("\nSetting up autocoder command...")
        create_wrapper_script()


class CustomDevelopCommand(develop):
    """Custom develop command that creates wrapper script."""
    
    def run(self):
        # Run the standard develop installation
        develop.run(self)
        
        # Create the wrapper script
        print("\nSetting up autocoder command...")
        create_wrapper_script()


class CustomEggInfoCommand(egg_info):
    """Custom egg_info command to ensure version is correct."""
    
    def run(self):
        # Run the standard egg_info
        egg_info.run(self)

# Minimal setup.py since we're using pyproject.toml
setup(
    version=read_version(),
    packages=find_packages(where='.', include=['agents*', 'utils*', 'workflow*', 'memory*', 'web_interface*', 'git_integration*', 'sandbox*']),
    py_modules=['autocoder', 'main', 'main_api', 'enhanced_main', 'cli_websocket_client'],
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
)
