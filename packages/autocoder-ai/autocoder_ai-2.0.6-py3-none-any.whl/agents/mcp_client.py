"""
MCP Client for AI Agents to use tools from MCP servers
"""

import asyncio
import json
import logging
import subprocess
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import httpx
from fastmcp import Client as ClientSession, StdioServerParameters
from fastmcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None
    timeout: int = 30
    enabled: bool = True
    description: str = ""

class MCPClientManager:
    """Manages connections to multiple MCP servers and tool access"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.active_sessions: Dict[str, ClientSession] = {}
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        
    def add_server(self, config: MCPServerConfig):
        """Add an MCP server configuration"""
        self.servers[config.name] = config
        logger.info(f"Added MCP server config: {config.name}")
        
    def remove_server(self, server_name: str):
        """Remove an MCP server configuration"""
        if server_name in self.servers:
            del self.servers[server_name]
            if server_name in self.active_sessions:
                # Close the session
                asyncio.create_task(self._close_session(server_name))
            logger.info(f"Removed MCP server config: {server_name}")
    
    async def _close_session(self, server_name: str):
        """Close an active session"""
        if server_name in self.active_sessions:
            try:
                session = self.active_sessions[server_name]
                # MCP ClientSession doesn't have close method, just remove from tracking
                del self.active_sessions[server_name]
                logger.info(f"Closed MCP session: {server_name}")
            except Exception as e:
                logger.error(f"Error closing MCP session {server_name}: {e}")
    
    async def connect_to_server(self, server_name: str) -> bool:
        """Connect to an MCP server and establish a session"""
        if server_name not in self.servers:
            logger.error(f"MCP server config not found: {server_name}")
            return False
            
        config = self.servers[server_name]
        if not config.enabled:
            logger.info(f"MCP server disabled: {server_name}")
            return False
            
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args or [],
                env=config.env or {}
            )
            
            # Connect to the server
            async with stdio_client(server_params) as (read, write):
                # Create client session
                session = ClientSession(read, write)
                
                # Initialize the session
                await session.initialize()
                
                # List available tools
                tools_result = await session.list_tools()
                tools = tools_result.tools if tools_result else []
                
                # Store tools information
                server_tools = {}
                for tool in tools:
                    server_tools[tool.name] = {
                        'name': tool.name,
                        'description': tool.description or '',
                        'input_schema': tool.inputSchema,
                        'server': server_name
                    }
                
                self.available_tools[server_name] = server_tools
                self.active_sessions[server_name] = session
                
                logger.info(f"Connected to MCP server '{server_name}' with {len(tools)} tools")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{server_name}': {e}")
            return False
    
    async def disconnect_from_server(self, server_name: str):
        """Disconnect from an MCP server"""
        await self._close_session(server_name)
        if server_name in self.available_tools:
            del self.available_tools[server_name]
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool from a specific MCP server"""
        if server_name not in self.active_sessions:
            # Try to connect if not already connected
            connected = await self.connect_to_server(server_name)
            if not connected:
                return {
                    'success': False,
                    'error': f'Unable to connect to MCP server: {server_name}'
                }
        
        if server_name not in self.available_tools:
            return {
                'success': False,
                'error': f'No tools available from server: {server_name}'
            }
        
        if tool_name not in self.available_tools[server_name]:
            return {
                'success': False,
                'error': f'Tool not found: {tool_name} in server {server_name}'
            }
        
        try:
            session = self.active_sessions[server_name]
            
            # Call the tool
            result = await session.call_tool(tool_name, arguments or {})
            
            if result.isError:
                # Handle error result
                error_text = 'Unknown error'
                if result.content:
                    for item in result.content:
                        if hasattr(item, 'text') and item.text:
                            error_text = item.text
                            break
                
                return {
                    'success': False,
                    'error': error_text
                }
            else:
                # Process successful result
                content = []
                for item in result.content:
                    if hasattr(item, 'text') and item.text:
                        content.append(item.text)
                    elif hasattr(item, 'data') and item.data:
                        content.append(str(item.data))
                    else:
                        content.append(str(item))
                
                return {
                    'success': True,
                    'result': '\n'.join(content),
                    'content': result.content
                }
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on server {server_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all available tools from all connected servers"""
        all_tools = {}
        for server_name, tools in self.available_tools.items():
            for tool_name, tool_info in tools.items():
                # Prefix tool name with server name to avoid conflicts
                prefixed_name = f"{server_name}.{tool_name}"
                all_tools[prefixed_name] = tool_info
        return all_tools
    
    def get_server_tools(self, server_name: str) -> Dict[str, Any]:
        """Get tools for a specific server"""
        return self.available_tools.get(server_name, {})
    
    async def refresh_tools(self, server_name: Optional[str] = None):
        """Refresh tool list from servers"""
        if server_name:
            # Refresh specific server
            if server_name in self.active_sessions:
                await self.disconnect_from_server(server_name)
            await self.connect_to_server(server_name)
        else:
            # Refresh all servers
            for name in list(self.servers.keys()):
                if name in self.active_sessions:
                    await self.disconnect_from_server(name)
                await self.connect_to_server(name)
    
    async def shutdown(self):
        """Shutdown all MCP connections"""
        for server_name in list(self.active_sessions.keys()):
            await self._close_session(server_name)
        logger.info("MCP Client Manager shutdown complete")

# Global MCP client manager instance
mcp_client_manager = MCPClientManager()

class MCPToolRegistry:
    """Registry of common MCP server configurations"""
    
    COMMON_SERVERS = {
        'filesystem': {
            'name': 'filesystem',
            'description': 'File system operations (read, write, search files)',
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
            'tools': ['read_file', 'write_file', 'create_directory', 'list_directory', 'search_files']
        },
        'web_search': {
            'name': 'web_search',
            'description': 'Web search and content retrieval',
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-brave-search'],
            'env': {'BRAVE_API_KEY': '${BRAVE_API_KEY}'},
            'tools': ['web_search', 'get_webpage_content']
        },
        'git': {
            'name': 'git',
            'description': 'Git repository operations',
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-git'],
            'tools': ['git_status', 'git_log', 'git_diff', 'git_commit', 'git_branch']
        },
        'sqlite': {
            'name': 'sqlite',
            'description': 'SQLite database operations',
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-sqlite'],
            'tools': ['query', 'execute', 'describe_table', 'list_tables']
        },
        'github': {
            'name': 'github',
            'description': 'GitHub API integration',
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-github'],
            'env': {'GITHUB_PERSONAL_ACCESS_TOKEN': '${GITHUB_TOKEN}'},
            'tools': ['create_repository', 'get_repository', 'create_issue', 'get_user']
        }
    }
    
    @classmethod
    def get_common_server_config(cls, server_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a common MCP server type"""
        return cls.COMMON_SERVERS.get(server_type)
    
    @classmethod
    def list_common_servers(cls) -> List[Dict[str, Any]]:
        """List all available common server configurations"""
        return list(cls.COMMON_SERVERS.values())
    
    @classmethod
    def create_server_config(cls, server_type: str, custom_args: Optional[Dict[str, Any]] = None) -> Optional[MCPServerConfig]:
        """Create a server configuration from a common server type"""
        common_config = cls.get_common_server_config(server_type)
        if not common_config:
            return None
        
        config = MCPServerConfig(
            name=common_config['name'],
            description=common_config['description'],
            command=common_config['command'],
            args=common_config['args'],
            env=common_config.get('env', {}),
            enabled=True
        )
        
        # Apply custom arguments if provided
        if custom_args:
            for key, value in custom_args.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        return config

# Async initialization function
async def initialize_mcp_client():
    """Initialize MCP client with default configurations"""
    logger.info("Initializing MCP Client Manager")
    # This can be called when the system starts
    return mcp_client_manager

# Convenience function for agents to use tools
async def use_mcp_tool(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function for agents to use MCP tools"""
    # Parse tool name (format: server_name.tool_name)
    if '.' in tool_name:
        server_name, actual_tool_name = tool_name.rsplit('.', 1)
    else:
        # If no server prefix, try to find the tool in any server
        all_tools = mcp_client_manager.get_available_tools()
        matching_servers = [name for name, info in all_tools.items() if name.endswith(f'.{tool_name}')]
        
        if not matching_servers:
            return {
                'success': False,
                'error': f'Tool not found: {tool_name}'
            }
        
        # Use the first matching server
        server_tool = matching_servers[0]
        server_name, actual_tool_name = server_tool.rsplit('.', 1)
    
    return await mcp_client_manager.call_tool(server_name, actual_tool_name, arguments)