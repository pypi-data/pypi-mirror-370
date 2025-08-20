"""
Configuration loader for the agent system
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Configuration loader and validator"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
    def load(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.config_path.exists():
                logger.error(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            
            # Validate configuration
            if not self._validate_config():
                return False
            
            # Load environment variables for API keys
            self._load_environment_variables()
            
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return True
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate the loaded configuration"""
        required_sections = ['agents', 'default_model']
        
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required configuration section: {section}")
                return False
        
        # Validate agent configurations
        required_agents = ['planner', 'developer', 'tester', 'ui_ux_expert', 'db_expert', 'devops_expert']
        
        if 'agents' not in self.config:
            logger.error("Missing 'agents' section in configuration")
            return False
        
        for agent in required_agents:
            if agent not in self.config['agents']:
                logger.error(f"Missing configuration for agent: {agent}")
                return False
            
            agent_config = self.config['agents'][agent]
            if 'model' not in agent_config:
                logger.error(f"Missing model configuration for agent: {agent}")
                return False
            
            model_config = agent_config['model']
            required_model_fields = ['provider', 'model']
            
            for field in required_model_fields:
                if field not in model_config:
                    logger.error(f"Missing {field} in model configuration for agent: {agent}")
                    return False
        
        logger.info("Configuration validation successful")
        return True
    
    def _load_environment_variables(self):
        """Load API keys and other sensitive data from environment variables"""
        # Process api_keys section for env: prefix
        if 'api_keys' in self.config:
            for key, value in self.config['api_keys'].items():
                if isinstance(value, str) and value.startswith('env:'):
                    env_var = value[4:]  # Remove 'env:' prefix
                    env_value = os.getenv(env_var)
                    if env_value:
                        self.config['api_keys'][key] = env_value
                        logger.info(f"Loaded {env_var} from environment for {key}")
                    else:
                        logger.warning(f"Environment variable {env_var} not found for {key}")
        
        # Process providers section for env: prefix
        if 'providers' in self.config:
            for provider_name, provider_config in self.config['providers'].items():
                if isinstance(provider_config, dict) and 'api_key' in provider_config:
                    api_key_value = provider_config['api_key']
                    if isinstance(api_key_value, str) and api_key_value.startswith('env:'):
                        env_var = api_key_value[4:]  # Remove 'env:' prefix
                        env_value = os.getenv(env_var)
                        if env_value:
                            self.config['providers'][provider_name]['api_key'] = env_value
                            logger.info(f"Loaded {env_var} from environment for provider {provider_name}")
                        else:
                            logger.warning(f"Environment variable {env_var} not found for provider {provider_name}")
        
        # Common API key environment variables (fallback)
        env_vars = {
            'OPENAI_API_KEY': 'openai_api_key',
            'ANTHROPIC_API_KEY': 'anthropic_api_key',
            'GOOGLE_API_KEY': 'google_api_key',
            'AZURE_API_KEY': 'azure_api_key',
            'COHERE_API_KEY': 'cohere_api_key',
            'HUGGINGFACE_API_KEY': 'huggingface_api_key',
            'OPENAI_COMPATIBLE_API_KEY': 'openai_compatible_api_key',
            'OPENAI_COMPATIBLE_BASE_URL': 'openai_compatible_base_url'
        }
        
        api_keys = {}
        for env_var, config_key in env_vars.items():
            value = os.getenv(env_var)
            if value:
                api_keys[config_key] = value
                logger.debug(f"Loaded {env_var} from environment (fallback)")
        
        # Add API keys to configuration if not already present
        if api_keys:
            if 'api_keys' not in self.config:
                self.config['api_keys'] = {}
            for key, value in api_keys.items():
                if key not in self.config['api_keys'] or not self.config['api_keys'][key]:
                    self.config['api_keys'][key] = value
        
        # Update provider configurations with environment variables
        self._update_provider_configs_from_env(api_keys)
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent"""
        return self.config.get('agents', {}).get(agent_name)
    
    def get_model_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get model configuration for a specific agent"""
        agent_config = self.get_agent_config(agent_name)
        if agent_config:
            return agent_config.get('model')
        return None
    
    def get_default_model_config(self) -> Dict[str, Any]:
        """Get default model configuration"""
        return self.config.get('default_model', {})
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """Get workflow configuration"""
        return self.config.get('workflow', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration"""
        return self.config.get('output', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get('logging', {})
    
    def _update_provider_configs_from_env(self, api_keys: Dict[str, str]):
        """Update provider configurations with environment variables"""
        providers = self.config.get('providers', {})
        
        # Update OpenAI compatible provider with environment variables
        if 'openai_compatible' in providers:
            openai_compat = providers['openai_compatible']
            
            # Update API key from environment
            if 'openai_compatible_api_key' in api_keys:
                openai_compat['api_key'] = api_keys['openai_compatible_api_key']
                logger.info("Updated OpenAI compatible API key from environment")
            
            # Update base URL from environment
            if 'openai_compatible_base_url' in api_keys:
                openai_compat['base_url'] = api_keys['openai_compatible_base_url']
                logger.info("Updated OpenAI compatible base URL from environment")
        
        # Update standard OpenAI provider
        if 'openai' in providers and 'openai_api_key' in api_keys:
            providers['openai']['api_key'] = api_keys['openai_api_key']
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific provider"""
        return self.config.get('providers', {}).get(provider_name)
    
    def get_enabled_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled providers"""
        providers = self.config.get('providers', {})
        return {name: config for name, config in providers.items() 
                if config.get('enabled', False)}
    
    def save(self, output_path: Optional[str] = None) -> bool:
        """
        Save current configuration to file
        
        Args:
            output_path: Optional output path, defaults to original config path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            save_path = Path(output_path) if output_path else self.config_path
            
            with open(save_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
