"""
Enhanced agent configuration with support for multiple providers and MCP servers
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ModelProvider(str, Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GENAI = "google_genai"
    AZURE_OPENAI = "azure_openai"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    OPENAI_COMPATIBLE = "openai_compatible"

class ToolType(str, Enum):
    """Types of tools available"""
    MCP_SERVER = "mcp_server"
    LANGCHAIN_TOOL = "langchain_tool"
    CUSTOM_FUNCTION = "custom_function"

class MCPServerConfig(BaseModel):
    """Configuration for an MCP server"""
    name: str
    type: str = "stdio"  # stdio, http, websocket
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    enabled: bool = True
    tools: Optional[List[str]] = None  # List of specific tools to enable
    
class ProviderConfig(BaseModel):
    """Configuration for a model provider"""
    provider: ModelProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    organization: Optional[str] = None
    project: Optional[str] = None
    region: Optional[str] = None  # For Azure
    deployment_name: Optional[str] = None  # For Azure
    api_version: Optional[str] = None  # For Azure
    model_path: Optional[str] = None  # For local models
    extra_params: Dict[str, Any] = Field(default_factory=dict)

class ModelConfig(BaseModel):
    """Configuration for a specific model"""
    provider: ModelProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    stream: bool = False
    reasoning: Optional[Dict[str, Any]] = None  # For models with reasoning capabilities
    
class ToolConfig(BaseModel):
    """Configuration for tool usage"""
    enabled: bool = True
    max_calls_per_response: int = 5
    tools: List[str] = Field(default_factory=list)  # List of tool names
    tool_types: List[ToolType] = Field(default_factory=lambda: [ToolType.MCP_SERVER, ToolType.LANGCHAIN_TOOL])
    mcp_servers: List[MCPServerConfig] = Field(default_factory=list)  # Agent-specific MCP servers
    
class EnhancedAgentConfig(BaseModel):
    """Enhanced configuration for agents with full customization"""
    model_config = ConfigDict(protected_namespaces=())
    
    # Basic information
    name: str
    description: str
    role: str = ""
    
    # System prompt configuration
    system_prompt: str = ""
    custom_instructions: Optional[str] = None
    
    # Model configuration
    model: ModelConfig
    fallback_models: Optional[List[ModelConfig]] = None  # Fallback models if primary fails
    
    # Tool configuration
    tools: ToolConfig = Field(default_factory=ToolConfig)
    
    # Advanced settings
    memory_enabled: bool = True
    max_memory_entries: int = 100
    conversation_timeout: int = 3600  # seconds
    retry_strategy: Dict[str, Any] = Field(default_factory=lambda: {
        "max_retries": 3,
        "backoff_factor": 2,
        "max_wait": 60
    })
    
    # Provider-specific settings
    provider_configs: Dict[ModelProvider, ProviderConfig] = Field(default_factory=dict)
    
    @classmethod
    def from_simple_config(cls, config: Dict[str, Any]) -> "EnhancedAgentConfig":
        """Create from simple configuration format for backward compatibility"""
        model_config = config.get('model', {})
        provider = model_config.get('provider', 'openai')
        model_name = model_config.get('model', 'gpt-4')
        
        # Map old provider names to enum
        provider_map = {
            'openai': ModelProvider.OPENAI,
            'anthropic': ModelProvider.ANTHROPIC,
            'google': ModelProvider.GOOGLE_GENAI,
            'gemini': ModelProvider.GOOGLE_GENAI,
            'azure': ModelProvider.AZURE_OPENAI,
            'openai_compatible': ModelProvider.OPENAI_COMPATIBLE
        }
        
        provider_enum = provider_map.get(provider, ModelProvider.OPENAI)
        
        # Create model config
        model = ModelConfig(
            provider=provider_enum,
            model_name=model_name,
            temperature=model_config.get('temperature', 0.7),
            max_tokens=model_config.get('max_tokens', 2000),
            reasoning=model_config.get('reasoning')
        )
        
        # Create tool config
        tools = ToolConfig(
            enabled=config.get('tools_enabled', False),
            tools=config.get('available_tools', []),
            max_calls_per_response=config.get('max_tool_calls', 5)
        )
        
        return cls(
            name=config.get('name', 'Agent'),
            description=config.get('description', ''),
            system_prompt=config.get('system_prompt', ''),
            model=model,
            tools=tools
        )
    
    def to_langchain_config(self) -> Dict[str, Any]:
        """Convert to LangChain-compatible configuration"""
        # Map providers to LangChain format
        provider_map = {
            ModelProvider.OPENAI: "openai",
            ModelProvider.ANTHROPIC: "anthropic",
            ModelProvider.GOOGLE_GENAI: "google_genai",
            ModelProvider.AZURE_OPENAI: "azure_openai",
            ModelProvider.HUGGINGFACE: "huggingface",
            ModelProvider.OLLAMA: "ollama",
            ModelProvider.LLAMACPP: "llamacpp",
            ModelProvider.OPENAI_COMPATIBLE: "openai"
        }
        
        config = {
            "model": self.model.model_name,
            "model_provider": provider_map.get(self.model.provider, "openai"),
            "temperature": self.model.temperature,
            "max_tokens": self.model.max_tokens,
            "top_p": self.model.top_p,
            "frequency_penalty": self.model.frequency_penalty,
            "presence_penalty": self.model.presence_penalty,
            "max_retries": self.retry_strategy.get("max_retries", 3)
        }
        
        # Add provider-specific configuration
        if self.model.provider in self.provider_configs:
            provider_config = self.provider_configs[self.model.provider]
            if provider_config.api_key:
                config["api_key"] = provider_config.api_key
            if provider_config.base_url:
                config["base_url"] = provider_config.base_url
            if provider_config.organization:
                config["organization"] = provider_config.organization
                
            # Azure-specific
            if self.model.provider == ModelProvider.AZURE_OPENAI:
                if provider_config.deployment_name:
                    config["deployment_name"] = provider_config.deployment_name
                if provider_config.api_version:
                    config["api_version"] = provider_config.api_version
                    
            # Local model specific
            if self.model.provider in [ModelProvider.OLLAMA, ModelProvider.LLAMACPP]:
                if provider_config.model_path:
                    config["model_path"] = provider_config.model_path
        
        if self.model.stop_sequences:
            config["stop"] = self.model.stop_sequences
            
        return config
    
    def get_mcp_servers(self, include_global: bool = True) -> List[MCPServerConfig]:
        """Get all MCP servers for this agent"""
        servers = list(self.tools.mcp_servers)
        
        if include_global:
            # TODO: Add global MCP servers from config
            pass
            
        return servers
    
    def add_mcp_server(self, server: MCPServerConfig) -> None:
        """Add an MCP server to this agent"""
        if server not in self.tools.mcp_servers:
            self.tools.mcp_servers.append(server)
            logger.info(f"Added MCP server '{server.name}' to agent '{self.name}'")
    
    def remove_mcp_server(self, server_name: str) -> bool:
        """Remove an MCP server from this agent"""
        for i, server in enumerate(self.tools.mcp_servers):
            if server.name == server_name:
                self.tools.mcp_servers.pop(i)
                logger.info(f"Removed MCP server '{server_name}' from agent '{self.name}'")
                return True
        return False
    
    def update_system_prompt(self, new_prompt: str) -> None:
        """Update the system prompt for this agent"""
        self.system_prompt = new_prompt
        logger.info(f"Updated system prompt for agent '{self.name}'")
    
    def set_provider_config(self, provider: ModelProvider, config: ProviderConfig) -> None:
        """Set provider-specific configuration"""
        self.provider_configs[provider] = config
        logger.info(f"Updated {provider} configuration for agent '{self.name}'")

class AgentConfigManager:
    """Manager for agent configurations"""
    
    def __init__(self):
        self.configs: Dict[str, EnhancedAgentConfig] = {}
        
    def load_config(self, agent_id: str, config_dict: Dict[str, Any]) -> EnhancedAgentConfig:
        """Load an agent configuration from dictionary"""
        if "model_config" in config_dict:
            # New enhanced format
            config = EnhancedAgentConfig(**config_dict)
        else:
            # Old simple format
            config = EnhancedAgentConfig.from_simple_config(config_dict)
        
        self.configs[agent_id] = config
        return config
    
    def get_config(self, agent_id: str) -> Optional[EnhancedAgentConfig]:
        """Get an agent configuration"""
        return self.configs.get(agent_id)
    
    def save_config(self, agent_id: str, config: EnhancedAgentConfig) -> Dict[str, Any]:
        """Save an agent configuration to dictionary"""
        self.configs[agent_id] = config
        return config.model_dump()
    
    def list_agents(self) -> List[str]:
        """List all configured agents"""
        return list(self.configs.keys())
