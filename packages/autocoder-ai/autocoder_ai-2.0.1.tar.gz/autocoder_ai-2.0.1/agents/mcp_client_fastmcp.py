"""
MCP Client for AI Agents using FastMCP 2.0
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
from fastmcp import Client

logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str  # Can be a Python script path, HTTP URL, or server instance
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None
    timeout: int = 30
    enabled: bool = True
    description: str = ""
    server_type: str = "script"  # "script", "http", or "instance"

class MCPClientManager:
    """Manages connections to multiple MCP servers using FastMCP 2.0"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.clients: Dict[str, Client] = {}
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        
    def add_server(self, config: MCPServerConfig):
        """Add an MCP server configuration"""
        self.servers[config.name] = config
        logger.info(f"Added MCP server config: {config.name}")
        
    def remove_server(self, server_name: str):
        """Remove an MCP server configuration"""
        if server_name in self.servers:
            del self.servers[server_name]
            if server_name in self.clients:
                # Note: FastMCP Client uses context manager, so cleanup happens automatically
                del self.clients[server_name]
            logger.info(f"Removed MCP server config: {server_name}")
    
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
            # Create client based on server type
            if config.server_type == "http":
                # HTTP server
                client = Client(config.command)
            elif config.server_type == "script":
                # Local Python script
                client = Client(config.command)
            else:
                # For future: in-memory server instances
                logger.error(f"Unsupported server type: {config.server_type}")
                return False
            
            # Store the client
            self.clients[server_name] = client
            
            # Connect and list available tools
            async with client:
                # Ping to verify connection
                await client.ping()
                
                # List available tools
                tools = await client.list_tools()
                
                # Store tools information
                server_tools = {}
                for tool in tools:
                    server_tools[tool.name] = {
                        'name': tool.name,
                        'description': tool.description or '',
                        'input_schema': tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                        'server': server_name
                    }
                
                self.available_tools[server_name] = server_tools
                
                logger.info(f"Connected to MCP server '{server_name}' with {len(tools)} tools")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{server_name}': {e}")
            return False
    
    async def disconnect_from_server(self, server_name: str):
        """Disconnect from an MCP server"""
        if server_name in self.clients:
            del self.clients[server_name]
        if server_name in self.available_tools:
            del self.available_tools[server_name]
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool from a specific MCP server"""
        if server_name not in self.servers:
            return {
                'success': False,
                'error': f'MCP server not configured: {server_name}'
            }
        
        # Get or create client
        if server_name not in self.clients:
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
            client = self.clients[server_name]
            
            # Use the client to call the tool
            async with client:
                result = await client.call_tool(tool_name, arguments or {})
                
                # Process the result
                if isinstance(result, dict) and result.get('error'):
                    return {
                        'success': False,
                        'error': result.get('error')
                    }
                else:
                    return {
                        'success': True,
                        'result': result,
                        'content': result
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
    
    async def list_all_server_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """List all capabilities (tools, resources, prompts) from all servers"""
        capabilities = {}
        
        for server_name, client in self.clients.items():
            try:
                async with client:
                    server_caps = {
                        'tools': await client.list_tools(),
                        'resources': await client.list_resources(),
                        'prompts': await client.list_prompts(),
                    }
                    capabilities[server_name] = server_caps
            except Exception as e:
                logger.error(f"Error listing capabilities for {server_name}: {e}")
                capabilities[server_name] = {'error': str(e)}
        
        return capabilities
    
    async def load_from_config(self, config_path: str):
        """Load MCP server configurations from a YAML file"""
        import yaml
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            servers_config = config.get('mcp_servers', {})
            for server_name, server_data in servers_config.items():
                if server_data.get('enabled', True):
                    config = MCPServerConfig(
                        name=server_name,
                        command=server_data.get('command', ''),
                        args=server_data.get('args', []),
                        env=server_data.get('env', {}),
                        working_directory=server_data.get('working_directory'),
                        timeout=server_data.get('timeout', 30),
                        enabled=True,
                        description=server_data.get('description', ''),
                        server_type=server_data.get('type', 'script')
                    )
                    self.add_server(config)
            
            logger.info(f"Loaded {len(self.servers)} MCP server configurations")
            
        except Exception as e:
            logger.error(f"Error loading MCP config from {config_path}: {e}")
            raise


# Example usage for testing
async def test_fastmcp_client():
    """Test the FastMCP client implementation"""
    manager = MCPClientManager()
    
    # Add a test server (you would need an actual MCP server for this)
    test_config = MCPServerConfig(
        name="test_server",
        command="test_mcp_server.py",  # Path to a Python MCP server script
        description="Test MCP server",
        server_type="script"
    )
    
    manager.add_server(test_config)
    
    # Try to connect
    connected = await manager.connect_to_server("test_server")
    if connected:
        print("Successfully connected to test server")
        
        # List available tools
        tools = manager.get_available_tools()
        print(f"Available tools: {list(tools.keys())}")
        
        # Call a tool (example)
        if tools:
            tool_name = list(tools.keys())[0]
            result = await manager.call_tool("test_server", tool_name.split('.')[-1], {"test": "value"})
            print(f"Tool result: {result}")
    else:
        print("Failed to connect to test server")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_fastmcp_client())
