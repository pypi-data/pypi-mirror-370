"""
Provider validation and model fetching for configuration setup
Validates API keys and fetches available models from different providers
"""

import os
import json
import requests
from typing import Tuple, List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProviderValidator:
    """Validates provider API keys and fetches available models"""
    
    def __init__(self):
        self.cache_dir = Path.home() / ".autocoder" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "models_cache.json"
        self.cache_ttl_hours = 24  # Cache for 24 hours
        
        # Fallback model lists if API calls fail
        self.fallback_models = {
            'openai': [
                'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 
                'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'
            ],
            'anthropic': [
                'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022',
                'claude-3-opus-20240229', 'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307'
            ],
            'google': [
                'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.5-flash-8b',
                'gemini-1.0-pro', 'gemini-pro-vision'
            ],
            'ollama': [
                'llama3.2', 'llama3.1', 'mistral', 'codellama',
                'deepseek-coder-v2', 'qwen2.5-coder'
            ],
            'openai_compatible': []
        }
    
    def validate_and_fetch_models(self, provider: str, api_key: str = None, 
                                 base_url: str = None) -> Tuple[bool, List[str], str]:
        """
        Validate provider credentials and fetch available models
        
        Args:
            provider: Provider name (openai, anthropic, google, ollama, openai_compatible)
            api_key: API key for the provider
            base_url: Base URL for the provider (for ollama and openai_compatible)
            
        Returns:
            Tuple of (is_valid, models_list, error_message)
        """
        validators = {
            'openai': self.validate_openai,
            'anthropic': self.validate_anthropic,
            'google': self.validate_google,
            'ollama': self.validate_ollama,
            'openai_compatible': self.validate_openai_compatible
        }
        
        if provider not in validators:
            return False, [], f"Unknown provider: {provider}"
        
        # Check cache first
        cached_models = self._get_cached_models(provider, api_key or base_url)
        
        # Try to validate and fetch fresh models
        try:
            is_valid, models, error = validators[provider](api_key, base_url)
            
            if is_valid and models:
                # Cache the successful result
                self._cache_models(provider, api_key or base_url, models)
                return is_valid, models, error
            elif is_valid and not models and cached_models:
                # Validation passed but couldn't fetch models, use cache
                return True, cached_models, "Using cached model list"
            else:
                return is_valid, models or self.fallback_models.get(provider, []), error
                
        except Exception as e:
            logger.error(f"Error validating {provider}: {e}")
            if cached_models:
                return True, cached_models, f"Using cached models (API error: {str(e)})"
            else:
                return False, self.fallback_models.get(provider, []), str(e)
    
    def validate_openai(self, api_key: str, base_url: str = None) -> Tuple[bool, List[str], str]:
        """Validate OpenAI API key and fetch available models"""
        if not api_key:
            return False, [], "API key is required"
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=api_key)
            
            # Fetch available models
            models_response = client.models.list()
            
            # Filter for chat models
            chat_models = []
            for model in models_response.data:
                model_id = model.id
                # Filter for GPT models that support chat
                if any(prefix in model_id for prefix in ['gpt-4', 'gpt-3.5']):
                    chat_models.append(model_id)
            
            # Sort models by capability (gpt-4 first, then gpt-3.5)
            chat_models.sort(key=lambda x: (
                0 if 'gpt-4o' in x else
                1 if 'gpt-4-turbo' in x else
                2 if 'gpt-4' in x else
                3
            ))
            
            if not chat_models:
                # If no models found, use fallback but validation passed
                return True, self.fallback_models['openai'], "API key valid, using default model list"
            
            return True, chat_models, ""
            
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return False, [], "Invalid API key"
            elif "connection" in error_msg.lower():
                return False, self.fallback_models['openai'], "Connection error - check your internet"
            else:
                return False, self.fallback_models['openai'], f"Error: {error_msg}"
    
    def validate_anthropic(self, api_key: str, base_url: str = None) -> Tuple[bool, List[str], str]:
        """Validate Anthropic API key and fetch available models"""
        if not api_key:
            return False, [], "API key is required"
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Test the API key with a minimal request
            # Anthropic doesn't have a models.list endpoint, so we test with a completion
            try:
                # Make a minimal test request
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                
                # If successful, return the known Claude models
                models = [
                    'claude-3-5-sonnet-latest',
                    'claude-3-5-sonnet-20241022', 
                    'claude-3-5-haiku-latest',
                    'claude-3-5-haiku-20241022',
                    'claude-3-opus-20240229',
                    'claude-3-sonnet-20240229',
                    'claude-3-haiku-20240307'
                ]
                
                return True, models, ""
                
            except anthropic.AuthenticationError:
                return False, [], "Invalid API key"
            except Exception as e:
                # API key might be valid but other issues
                return True, self.fallback_models['anthropic'], f"API key valid, using default models"
                
        except ImportError:
            return False, self.fallback_models['anthropic'], "Anthropic library not installed"
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return False, [], "Invalid API key"
            else:
                return False, self.fallback_models['anthropic'], f"Error: {error_msg}"
    
    def validate_google(self, api_key: str, base_url: str = None) -> Tuple[bool, List[str], str]:
        """Validate Google Gemini API key and fetch available models"""
        if not api_key:
            return False, [], "API key is required"
        
        try:
            import google.generativeai as genai
            
            # Configure with API key
            genai.configure(api_key=api_key)
            
            # List available models
            models_list = []
            try:
                for model in genai.list_models():
                    # Filter for Gemini models that support generateContent
                    if 'generateContent' in model.supported_generation_methods:
                        model_name = model.name.replace('models/', '')
                        models_list.append(model_name)
                
                if not models_list:
                    models_list = self.fallback_models['google']
                    
                return True, models_list, ""
                
            except Exception as e:
                error_msg = str(e)
                if "api_key" in error_msg.lower() or "invalid" in error_msg.lower():
                    return False, [], "Invalid API key"
                else:
                    # API key might be valid but can't fetch models
                    return True, self.fallback_models['google'], "API key valid, using default models"
                    
        except ImportError:
            return False, self.fallback_models['google'], "Google Generative AI library not installed"
        except Exception as e:
            return False, [], f"Error: {str(e)}"
    
    def validate_ollama(self, api_key: str = None, base_url: str = None) -> Tuple[bool, List[str], str]:
        """Validate Ollama connection and fetch available models"""
        if not base_url:
            base_url = "http://localhost:11434"
        
        try:
            # Try to connect to Ollama API
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                
                if not models:
                    return True, self.fallback_models['ollama'], "Ollama connected but no models found. Pull models with: ollama pull <model>"
                
                return True, models, ""
            else:
                return False, [], f"Ollama server returned status {response.status_code}"
                
        except requests.ConnectionError:
            return False, [], f"Cannot connect to Ollama at {base_url}. Is Ollama running?"
        except requests.Timeout:
            return False, [], f"Connection to Ollama timed out at {base_url}"
        except Exception as e:
            return False, [], f"Error connecting to Ollama: {str(e)}"
    
    def validate_openai_compatible(self, api_key: str, base_url: str) -> Tuple[bool, List[str], str]:
        """Validate OpenAI-compatible API endpoint and fetch available models"""
        if not api_key:
            return False, [], "API key is required"
        if not base_url:
            return False, [], "Base URL is required"
        
        try:
            # Ensure base_url ends with /v1 if not already
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'
            
            # Try to fetch models using OpenAI-compatible endpoint
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for model in data.get('data', []):
                    model_id = model.get('id', '')
                    if model_id:
                        models.append(model_id)
                
                if not models:
                    # No models found, but connection successful
                    return True, ['default'], "Connected successfully, but no models listed"
                
                return True, models, ""
                
            elif response.status_code == 401:
                return False, [], "Invalid API key or unauthorized"
            elif response.status_code == 404:
                # Models endpoint not found, but might still work
                return True, ['default'], "API connected (models endpoint not available)"
            else:
                return False, [], f"API returned status {response.status_code}"
                
        except requests.ConnectionError:
            return False, [], f"Cannot connect to {base_url}"
        except requests.Timeout:
            return False, [], f"Connection timed out"
        except Exception as e:
            return False, [], f"Error: {str(e)}"
    
    def _get_cached_models(self, provider: str, key: str) -> Optional[List[str]]:
        """Get cached models for a provider"""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            cache_key = f"{provider}:{key[:8] if key else 'default'}"
            if cache_key in cache:
                entry = cache[cache_key]
                # Check if cache is still valid
                cached_time = datetime.fromisoformat(entry['timestamp'])
                if datetime.now() - cached_time < timedelta(hours=self.cache_ttl_hours):
                    return entry['models']
            
            return None
            
        except Exception as e:
            logger.debug(f"Error reading cache: {e}")
            return None
    
    def _cache_models(self, provider: str, key: str, models: List[str]):
        """Cache models for a provider"""
        try:
            cache = {}
            if self.cache_file.exists():
                try:
                    with open(self.cache_file, 'r') as f:
                        cache = json.load(f)
                except:
                    pass
            
            cache_key = f"{provider}:{key[:8] if key else 'default'}"
            cache[cache_key] = {
                'models': models,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
                
        except Exception as e:
            logger.debug(f"Error writing cache: {e}")


# Convenience functions for direct usage
def validate_provider(provider: str, api_key: str = None, base_url: str = None) -> Tuple[bool, List[str], str]:
    """
    Validate a provider and fetch available models
    
    Returns:
        Tuple of (is_valid, models_list, error_message)
    """
    validator = ProviderValidator()
    return validator.validate_and_fetch_models(provider, api_key, base_url)
