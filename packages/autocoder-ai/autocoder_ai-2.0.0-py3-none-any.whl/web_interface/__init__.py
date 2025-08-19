"""
Web interface for the AI Coding Agent System
Provides a user-friendly web interface for non-CLI users
"""

from .app import create_app

__all__ = ['create_app']