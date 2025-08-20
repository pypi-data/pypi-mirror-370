"""
MCP Server Configuration Management for Web Interface
"""

import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from agents.mcp_client import MCPServerConfig, MCPToolRegistry, mcp_client_manager
import yaml

logger = logging.getLogger(__name__)

class MCPConfigManager:
    """Manages MCP server configurations"""
    
    def __init__(self, config_file: str = "mcp_servers.yaml"):
        self.config_file = Path(config_file)
        self.servers_config = {}
        self.load_config()
    
    def load_config(self):
        """Load MCP server configurations from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.servers_config = yaml.safe_load(f) or {}
                logger.info(f"Loaded MCP server config from {self.config_file}")
            else:
                # Create default config with common servers
                self.servers_config = self._create_default_config()
                self.save_config()
                logger.info("Created default MCP server configuration")
                
        except Exception as e:
            logger.error(f"Error loading MCP config: {e}")
            self.servers_config = {}
    
    def save_config(self):
        """Save MCP server configurations to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.servers_config, f, default_flow_style=False)
            logger.info(f"Saved MCP server config to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving MCP config: {e}")
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default MCP server configuration"""
        return {
            'servers': {
                'filesystem': {
                    'enabled': False,
                    'description': 'File system operations (read, write, search files)',
                    'command': 'npx',
                    'args': ['-y', '@modelcontextprotocol/server-filesystem', '/tmp'],
                    'timeout': 30,
                    'tools': ['read_file', 'write_file', 'create_directory', 'list_directory', 'search_files']
                },
                'web_search': {
                    'enabled': False,
                    'description': 'Web search and content retrieval',
                    'command': 'npx',
                    'args': ['-y', '@modelcontextprotocol/server-brave-search'],
                    'env': {'BRAVE_API_KEY': '${BRAVE_API_KEY}'},
                    'timeout': 60,
                    'tools': ['web_search', 'get_webpage_content']
                },
                'git': {
                    'enabled': False,
                    'description': 'Git repository operations',
                    'command': 'npx',
                    'args': ['-y', '@modelcontextprotocol/server-git'],
                    'timeout': 30,
                    'tools': ['git_status', 'git_log', 'git_diff', 'git_commit', 'git_branch']
                }
            },
            'agent_tools': {
                'developer': ['filesystem', 'git', 'web_search'],
                'tester': ['filesystem', 'git'],
                'planner': ['web_search'],
                'ui_ux_expert': ['web_search', 'filesystem'],
                'db_expert': ['filesystem'],
                'devops_expert': ['filesystem', 'git']
            }
        }
    
    def get_servers(self) -> Dict[str, Any]:
        """Get all server configurations"""
        return self.servers_config.get('servers', {})
    
    def get_server(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific server configuration"""
        return self.servers_config.get('servers', {}).get(server_name)
    
    def add_server(self, server_name: str, config: Dict[str, Any]):
        """Add or update a server configuration"""
        if 'servers' not in self.servers_config:
            self.servers_config['servers'] = {}
        
        self.servers_config['servers'][server_name] = config
        self.save_config()
        
        # Update the MCP client manager
        mcp_config = MCPServerConfig(
            name=server_name,
            description=config.get('description', ''),
            command=config['command'],
            args=config.get('args', []),
            env=config.get('env', {}),
            timeout=config.get('timeout', 30),
            enabled=config.get('enabled', True)
        )
        mcp_client_manager.add_server(mcp_config)
        
        logger.info(f"Added MCP server: {server_name}")
    
    def remove_server(self, server_name: str):
        """Remove a server configuration"""
        if 'servers' in self.servers_config and server_name in self.servers_config['servers']:
            del self.servers_config['servers'][server_name]
            self.save_config()
            
            # Update the MCP client manager
            mcp_client_manager.remove_server(server_name)
            
            logger.info(f"Removed MCP server: {server_name}")
    
    def update_server(self, server_name: str, config: Dict[str, Any]):
        """Update a server configuration"""
        if 'servers' in self.servers_config and server_name in self.servers_config['servers']:
            self.servers_config['servers'][server_name].update(config)
            self.save_config()
            
            # Update the MCP client manager
            mcp_config = MCPServerConfig(
                name=server_name,
                description=config.get('description', ''),
                command=config['command'],
                args=config.get('args', []),
                env=config.get('env', {}),
                timeout=config.get('timeout', 30),
                enabled=config.get('enabled', True)
            )
            mcp_client_manager.add_server(mcp_config)
            
            logger.info(f"Updated MCP server: {server_name}")
    
    def get_agent_tools(self, agent_name: str) -> List[str]:
        """Get tools configured for a specific agent"""
        return self.servers_config.get('agent_tools', {}).get(agent_name, [])
    
    def set_agent_tools(self, agent_name: str, tools: List[str]):
        """Set tools for a specific agent"""
        if 'agent_tools' not in self.servers_config:
            self.servers_config['agent_tools'] = {}
        
        self.servers_config['agent_tools'][agent_name] = tools
        self.save_config()
        logger.info(f"Updated tools for agent {agent_name}: {tools}")
    
    def get_available_tools(self) -> Dict[str, List[str]]:
        """Get all available tools from all servers"""
        tools = {}
        for server_name, server_config in self.get_servers().items():
            if server_config.get('enabled', False):
                server_tools = server_config.get('tools', [])
                tools[server_name] = server_tools
        return tools
    
    def get_common_servers(self) -> List[Dict[str, Any]]:
        """Get list of common server configurations"""
        return MCPToolRegistry.list_common_servers()
    
    def add_common_server(self, server_type: str, custom_config: Dict[str, Any] = None):
        """Add a common server configuration"""
        config_template = MCPToolRegistry.get_common_server_config(server_type)
        if not config_template:
            raise ValueError(f"Unknown server type: {server_type}")
        
        config = dict(config_template)
        if custom_config:
            config.update(custom_config)
        
        # Set default enabled state
        if 'enabled' not in config:
            config['enabled'] = True
        
        self.add_server(server_type, config)
    
    async def initialize_servers(self):
        """Initialize all enabled MCP servers"""
        for server_name, config in self.get_servers().items():
            if config.get('enabled', False):
                mcp_config = MCPServerConfig(
                    name=server_name,
                    description=config.get('description', ''),
                    command=config['command'],
                    args=config.get('args', []),
                    env=config.get('env', {}),
                    timeout=config.get('timeout', 30),
                    enabled=True
                )
                mcp_client_manager.add_server(mcp_config)
                
                # Try to connect
                try:
                    connected = await mcp_client_manager.connect_to_server(server_name)
                    if connected:
                        logger.info(f"Successfully initialized MCP server: {server_name}")
                    else:
                        logger.warning(f"Failed to connect to MCP server: {server_name}")
                except Exception as e:
                    logger.error(f"Error initializing MCP server {server_name}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        servers = self.get_servers()
        active_sessions = mcp_client_manager.active_sessions
        available_tools = mcp_client_manager.available_tools
        
        status = {
            'total_servers': len(servers),
            'enabled_servers': sum(1 for cfg in servers.values() if cfg.get('enabled', False)),
            'connected_servers': len(active_sessions),
            'total_tools': sum(len(tools) for tools in available_tools.values()),
            'servers': {}
        }
        
        for server_name, config in servers.items():
            status['servers'][server_name] = {
                'enabled': config.get('enabled', False),
                'connected': server_name in active_sessions,
                'tools_count': len(available_tools.get(server_name, {})),
                'description': config.get('description', ''),
                'command': config.get('command', '')
            }
        
        return status

# Global MCP configuration manager
mcp_config_manager = MCPConfigManager()