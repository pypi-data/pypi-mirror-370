"""
Configuration merging utilities for handling external agent configurations
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)


class ConfigMerger:
    """Handles merging of configurations with proper precedence rules"""
    
    @staticmethod
    def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries with override taking precedence.
        
        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
            
        Returns:
            Merged configuration with override values taking precedence
        """
        result = deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = ConfigMerger.deep_merge(result[key], value)
            else:
                # Override value
                result[key] = deepcopy(value)
        
        return result
    
    @staticmethod
    def merge_lists(base_list: List[Any], override_list: List[Any], 
                   merge_strategy: str = "replace") -> List[Any]:
        """
        Merge two lists based on specified strategy.
        
        Args:
            base_list: Base list
            override_list: Override list
            merge_strategy: Strategy for merging ('replace', 'append', 'prepend', 'unique')
            
        Returns:
            Merged list based on strategy
        """
        if merge_strategy == "replace":
            return override_list
        elif merge_strategy == "append":
            return base_list + override_list
        elif merge_strategy == "prepend":
            return override_list + base_list
        elif merge_strategy == "unique":
            # Combine and remove duplicates while preserving order
            seen = set()
            result = []
            for item in override_list + base_list:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result
        else:
            logger.warning(f"Unknown merge strategy: {merge_strategy}, using 'replace'")
            return override_list
    
    @staticmethod
    def load_external_config(config_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load an external configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Loaded configuration dictionary or None if failed
        """
        try:
            path = Path(config_path)
            
            # Try to resolve relative paths
            if not path.is_absolute():
                # Try relative to current directory
                if not path.exists():
                    # Try relative to config directory
                    config_dir = Path("configs")
                    if config_dir.exists():
                        alt_path = config_dir / path
                        if alt_path.exists():
                            path = alt_path
            
            if not path.exists():
                logger.error(f"External configuration file not found: {config_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Loaded external configuration from {path}")
                return config
                
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {config_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load external configuration {config_path}: {e}")
            return None
    
    @staticmethod
    def process_mcp_server_config(mcp_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate MCP server configuration.
        
        Args:
            mcp_config: Raw MCP server configuration
            
        Returns:
            Processed MCP server configuration
        """
        processed = {
            "name": mcp_config.get("name", "unnamed_server"),
            "command": mcp_config.get("command"),
            "args": mcp_config.get("args", []),
            "env": mcp_config.get("env", {}),
            "alwaysAllow": mcp_config.get("alwaysAllow", mcp_config.get("autoApprove", [])),
            "disabled": mcp_config.get("disabled", False),
            "timeout": mcp_config.get("timeout", 60000),  # Default 60 seconds
            "type": mcp_config.get("type", "stdio")  # stdio, http, websocket
        }
        
        # Process environment variables
        env_vars = processed["env"]
        for key, value in env_vars.items():
            if isinstance(value, str) and value.startswith("env:"):
                env_name = value[4:]
                env_value = os.getenv(env_name)
                if env_value:
                    env_vars[key] = env_value
                else:
                    logger.warning(f"Environment variable {env_name} not found for MCP server")
        
        return processed
    
    @staticmethod
    def merge_agent_configs(base_agent: Dict[str, Any], 
                           external_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge agent configuration with external configuration file.
        
        Args:
            base_agent: Base agent configuration from main config
            external_config: External agent configuration
            
        Returns:
            Merged agent configuration
        """
        # Start with base configuration
        merged = deepcopy(base_agent)
        
        # Handle system prompt
        if "system_prompt" in external_config:
            merged["system_prompt"] = external_config["system_prompt"]
        
        # Handle custom instructions (append by default)
        if "custom_instructions" in external_config:
            base_instructions = merged.get("custom_instructions", "")
            new_instructions = external_config["custom_instructions"]
            if base_instructions:
                merged["custom_instructions"] = f"{base_instructions}\n\n{new_instructions}"
            else:
                merged["custom_instructions"] = new_instructions
        
        # Handle available tools (unique merge by default)
        if "available_tools" in external_config:
            base_tools = merged.get("available_tools", [])
            new_tools = external_config["available_tools"]
            merged["available_tools"] = ConfigMerger.merge_lists(
                base_tools, new_tools, "unique"
            )
        
        # Handle MCP servers
        if "mcpServers" in external_config:
            mcp_servers = []
            for server_name, server_config in external_config["mcpServers"].items():
                server_config["name"] = server_name
                processed_server = ConfigMerger.process_mcp_server_config(server_config)
                if not processed_server.get("disabled", False):
                    mcp_servers.append(processed_server)
            merged["mcp_servers"] = mcp_servers
        
        # Handle development options
        if "dev" in external_config:
            merged["dev"] = external_config["dev"]
        
        # Handle model configuration
        if "model" in external_config:
            if "model" not in merged:
                merged["model"] = {}
            merged["model"] = ConfigMerger.deep_merge(
                merged.get("model", {}), 
                external_config["model"]
            )
        
        # Handle tool configuration
        if "tools" in external_config:
            merged["tools"] = ConfigMerger.deep_merge(
                merged.get("tools", {}),
                external_config["tools"]
            )
        
        # Handle any other top-level keys
        for key in external_config:
            if key not in ["system_prompt", "custom_instructions", "available_tools", 
                          "mcpServers", "dev", "model", "tools"]:
                merged[key] = external_config[key]
        
        return merged


class ExternalConfigLoader:
    """Handles loading and processing external agent configuration files"""
    
    def __init__(self, base_config: Dict[str, Any]):
        """
        Initialize with base configuration.
        
        Args:
            base_config: Base configuration dictionary
        """
        self.base_config = base_config
        self.merger = ConfigMerger()
    
    def process_agent_configs(self) -> Dict[str, Any]:
        """
        Process all agent configurations, loading external files if specified.
        
        Returns:
            Updated configuration with external agent configs merged
        """
        if "agents" not in self.base_config:
            return self.base_config
        
        updated_config = deepcopy(self.base_config)
        agents = updated_config["agents"]
        
        for agent_name, agent_config in agents.items():
            if "agentConfigFile" in agent_config:
                config_file = agent_config["agentConfigFile"]
                logger.info(f"Loading external config for agent {agent_name}: {config_file}")
                
                # Load external configuration
                external_config = self.merger.load_external_config(config_file)
                
                if external_config:
                    # Merge with base agent configuration
                    merged_config = self.merger.merge_agent_configs(
                        agent_config, external_config
                    )
                    
                    # Update the agent configuration
                    agents[agent_name] = merged_config
                    logger.info(f"Successfully merged external config for agent {agent_name}")
                else:
                    logger.warning(f"Failed to load external config for agent {agent_name}")
        
        return updated_config
    
    def validate_mcp_servers(self, agent_config: Dict[str, Any]) -> bool:
        """
        Validate MCP server configurations for an agent.
        
        Args:
            agent_config: Agent configuration with MCP servers
            
        Returns:
            True if valid, False otherwise
        """
        if "mcp_servers" not in agent_config:
            return True
        
        for server in agent_config["mcp_servers"]:
            if not server.get("command") and server.get("type") == "stdio":
                logger.error(f"MCP server {server.get('name')} missing required 'command' field")
                return False
            
            if server.get("type") == "http" and not server.get("url"):
                logger.error(f"HTTP MCP server {server.get('name')} missing required 'url' field")
                return False
        
        return True
