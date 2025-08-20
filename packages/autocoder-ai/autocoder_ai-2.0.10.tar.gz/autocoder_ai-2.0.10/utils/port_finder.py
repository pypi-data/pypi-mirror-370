"""
Utility to find available ports for the API server
"""

import socket
from typing import Optional


def find_available_port(start_port: int = 5000, max_tries: int = 100) -> Optional[int]:
    """
    Find an available port starting from start_port
    
    Args:
        start_port: Port to start searching from
        max_tries: Maximum number of ports to try
        
    Returns:
        Available port number or None if none found
    """
    for port in range(start_port, start_port + max_tries):
        if is_port_available(port):
            return port
    return None


def is_port_available(port: int, host: str = '127.0.0.1') -> bool:
    """
    Check if a port is available for binding
    
    Args:
        port: Port number to check
        host: Host to check on
        
    Returns:
        True if port is available, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def get_next_available_port(preferred_ports: list = None) -> int:
    """
    Get the next available port from a list of preferred ports or find one
    
    Args:
        preferred_ports: List of preferred ports to try first
        
    Returns:
        Available port number
    """
    # Default preferred ports
    if preferred_ports is None:
        preferred_ports = [5001, 5000, 5002, 5003, 8000, 8001, 8080]
    
    # Try preferred ports first
    for port in preferred_ports:
        if is_port_available(port):
            return port
    
    # If none available, find one starting from 5000
    port = find_available_port(5000)
    if port:
        return port
    
    # Last resort - let the OS assign one
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]
