"""
Base agent class for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import asyncio
import json
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel
from .mcp_client import mcp_client_manager, use_mcp_tool
import os

logger = logging.getLogger(__name__)

class AgentConfig(BaseModel):
    """Configuration model for agents"""
    name: str
    model: Dict[str, Any]
    description: str
    system_prompt: str = ""
    reasoning: Optional[Dict[str, Any]] = None
    tools_enabled: bool = False
    available_tools: List[str] = []
    max_tool_calls: int = 5

class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.llm = self._initialize_llm()
        self.conversation_history = []
        self.tools_enabled = config.tools_enabled
        self.available_tools = config.available_tools
        self.max_tool_calls = config.max_tool_calls
        
    def _initialize_llm(self) -> BaseChatModel:
        """Initialize the LLM for this agent"""
        try:
            model_config = self.config.model
            
            # Get provider and model name
            provider = model_config['provider']
            model_name = model_config['model']
            
            # Set API keys in environment if available
            self._set_api_keys_in_env()
            
            # Map provider names to LangChain provider names
            langchain_provider_map = {
                'openai': 'openai',
                'anthropic': 'anthropic',
                'google': 'google_genai',
                'gemini': 'google_genai',
                'openai_compatible': 'openai'  # Will handle with custom params
            }
            
            provider_name = langchain_provider_map.get(provider, provider)
            
            # Build model initialization parameters
            init_params = {
                "model": model_name,
                "model_provider": provider_name,
                "temperature": model_config.get('temperature', 0.7),
                "max_tokens": model_config.get('max_tokens', 2000),
                "max_retries": 3
            }
            
            # Handle OpenAI compatible provider configuration
            if provider == 'openai_compatible' and hasattr(self, 'config_loader'):
                provider_config = self.config_loader.get_provider_config('openai_compatible')
                if provider_config:
                    # Use custom base URL and API key for OpenAI-compatible endpoints
                    if provider_config.get('base_url'):
                        init_params['base_url'] = provider_config.get('base_url')
                    if provider_config.get('api_key'):
                        init_params['api_key'] = provider_config.get('api_key')
                    
                    # Apply model-specific overrides if available
                    model_overrides = provider_config.get('model_overrides', {})
                    if model_name in model_overrides:
                        overrides = model_overrides[model_name]
                        init_params.update({
                            'max_tokens': overrides.get('max_tokens', init_params['max_tokens']),
                            'temperature': overrides.get('temperature', init_params['temperature'])
                        })
                    
                    # Custom headers might need special handling per provider
            
            # Note: Reasoning parameters would need to be handled per-provider if supported
            # For now, we'll pass standard parameters that most providers support
            
            # Initialize the chat model using LangChain's init_chat_model
            llm = init_chat_model(**init_params)
            
            logger.info(f"Initialized LLM for {self.name}: {provider}/{model_name}")
            return llm
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM for {self.name}: {str(e)}")
            raise
    
    def _set_api_keys_in_env(self):
        """Set API keys in environment variables from config"""
        try:
            # Try to get config from parent context if available
            if hasattr(self, 'config_loader'):
                config = self.config_loader.config
            else:
                # Try to load config directly
                from utils.config_loader import ConfigLoader
                config_loader = ConfigLoader()
                if config_loader.load():
                    config = config_loader.config
                else:
                    config = {}
            
            # Set API keys from config into environment variables
            if 'api_keys' in config:
                if 'openai_api_key' in config['api_keys']:
                    api_key = config['api_keys']['openai_api_key']
                    if api_key and not api_key.startswith('env:'):
                        os.environ['OPENAI_API_KEY'] = api_key
                        logger.debug("Set OpenAI API key from config")
                
                if 'anthropic_api_key' in config['api_keys']:
                    api_key = config['api_keys']['anthropic_api_key']
                    if api_key and not api_key.startswith('env:'):
                        os.environ['ANTHROPIC_API_KEY'] = api_key
                        logger.debug("Set Anthropic API key from config")
                
                if 'google_api_key' in config['api_keys']:
                    api_key = config['api_keys']['google_api_key']
                    if api_key and not api_key.startswith('env:'):
                        # Set Google API key for google-generativeai
                        os.environ['GOOGLE_API_KEY'] = api_key
                        logger.debug("Set Google API key from config")
            
            # Also check providers section
            if 'providers' in config:
                if 'openai' in config['providers'] and 'api_key' in config['providers']['openai']:
                    api_key = config['providers']['openai']['api_key']
                    if api_key and not api_key.startswith('env:'):
                        os.environ['OPENAI_API_KEY'] = api_key
                        logger.debug("Set OpenAI API key from provider config")
                
                if 'anthropic' in config['providers'] and 'api_key' in config['providers']['anthropic']:
                    api_key = config['providers']['anthropic']['api_key']
                    if api_key and not api_key.startswith('env:'):
                        os.environ['ANTHROPIC_API_KEY'] = api_key
                        logger.debug("Set Anthropic API key from provider config")
                
                if 'google' in config['providers'] and 'api_key' in config['providers']['google']:
                    api_key = config['providers']['google']['api_key']
                    if api_key and not api_key.startswith('env:'):
                        os.environ['GOOGLE_API_KEY'] = api_key
                        logger.debug("Set Google API key from provider config")
            
        except Exception as e:
            logger.warning(f"Could not set API keys from config: {e}")
    
    def _create_system_message(self) -> SystemMessage:
        """Create the system message for this agent"""
        base_prompt = f"""You are a {self.name} in an autonomous AI coding team. 
        Your role: {self.config.description}
        
        Guidelines:
        - Provide detailed, actionable responses
        - Consider the full context of the project
        - Collaborate effectively with other agents
        - Focus on your area of expertise
        - Be specific and practical in your recommendations
        """
        
        # Add tool usage instructions if tools are enabled
        if self.tools_enabled and self.available_tools:
            base_prompt += f"""
        
        AVAILABLE TOOLS:
        You have access to the following tools that can help you complete tasks:
        {', '.join(self.available_tools)}
        
        TOOL USAGE:
        - Use tools when they can help accomplish the task more effectively
        - Call tools by using the format: [TOOL_CALL: tool_name | arguments_as_json]
        - You can make multiple tool calls, but limit to {self.max_tool_calls} calls per response
        - Always explain what you're doing with each tool call
        - Integrate tool results into your final response
        
        Example tool call: [TOOL_CALL: web_search | {{"query": "Python FastAPI tutorial"}}]
        """
        
        if self.config.system_prompt:
            base_prompt += f"\n\nSpecific instructions:\n{self.config.system_prompt}"
        
        return SystemMessage(content=base_prompt)
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the agent's task
        
        Args:
            task: The task description
            context: Additional context from other agents
            
        Returns:
            Dict containing the agent's response and metadata
        """
        try:
            logger.info(f"{self.name} starting task execution")
            
            # Prepare messages
            messages = [self._create_system_message()]
            
            # Add context if available
            if context:
                context_msg = self._format_context(context)
                if context_msg:
                    messages.append(HumanMessage(content=context_msg))
            
            # Add the main task
            task_message = self._format_task(task)
            messages.append(HumanMessage(content=task_message))
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Check if response contains tool calls and execute them
            if self.tools_enabled:
                enhanced_response = await self._process_tool_calls(response.content)
            else:
                enhanced_response = response.content
            
            # Process the response
            result = self._process_response(enhanced_response, task, context or {})
            
            # Store in conversation history
            self.conversation_history.extend(messages + [response])
            
            logger.info(f"{self.name} completed task execution")
            return result
            
        except Exception as e:
            logger.error(f"{self.name} failed to execute task: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': self.name,
                'output': None
            }
    
    async def _process_tool_calls(self, response_content: str) -> str:
        """Process tool calls found in the response"""
        if not response_content or not self.tools_enabled:
            return response_content
        
        import re
        
        # Pattern to match tool calls: [TOOL_CALL: tool_name | arguments_json]
        tool_call_pattern = r'\[TOOL_CALL:\s*([^|]+)\s*\|\s*({[^}]*}|\{.*?\})\s*\]'
        tool_calls = re.finditer(tool_call_pattern, response_content)
        
        enhanced_response = response_content
        tool_call_count = 0
        
        for match in tool_calls:
            if tool_call_count >= self.max_tool_calls:
                logger.warning(f"{self.name} exceeded max tool calls limit ({self.max_tool_calls})")
                break
                
            tool_name = match.group(1).strip()
            try:
                arguments_str = match.group(2).strip()
                arguments = json.loads(arguments_str) if arguments_str else {}
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in tool call arguments: {arguments_str}")
                continue
            
            # Check if tool is available
            if tool_name not in self.available_tools and not any(tool.endswith(f'.{tool_name}') for tool in self.available_tools):
                logger.warning(f"{self.name} tried to use unavailable tool: {tool_name}")
                continue
            
            # Execute the tool call
            try:
                logger.info(f"{self.name} calling tool: {tool_name} with args: {arguments}")
                tool_result = await use_mcp_tool(tool_name, arguments)
                
                if tool_result['success']:
                    result_text = f"\n[TOOL_RESULT: {tool_name}]\n{tool_result['result']}\n[/TOOL_RESULT]\n"
                else:
                    result_text = f"\n[TOOL_ERROR: {tool_name}]\n{tool_result['error']}\n[/TOOL_ERROR]\n"
                
                # Replace the tool call with the result
                enhanced_response = enhanced_response.replace(match.group(0), result_text)
                tool_call_count += 1
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                error_text = f"\n[TOOL_ERROR: {tool_name}]\n{str(e)}\n[/TOOL_ERROR]\n"
                enhanced_response = enhanced_response.replace(match.group(0), error_text)
        
        return enhanced_response
    
    def get_available_tools_info(self) -> Dict[str, Any]:
        """Get information about available tools"""
        if not self.tools_enabled:
            return {'enabled': False, 'tools': []}
        
        all_tools = mcp_client_manager.get_available_tools()
        agent_tools = []
        
        for tool_name in self.available_tools:
            # Check both prefixed and non-prefixed tool names
            tool_info = None
            if tool_name in all_tools:
                tool_info = all_tools[tool_name]
            else:
                # Look for the tool by suffix
                matching_tools = [info for name, info in all_tools.items() if name.endswith(f'.{tool_name}')]
                if matching_tools:
                    tool_info = matching_tools[0]
            
            if tool_info:
                agent_tools.append({
                    'name': tool_name,
                    'description': tool_info.get('description', ''),
                    'server': tool_info.get('server', ''),
                    'schema': tool_info.get('input_schema', {})
                })
        
        return {
            'enabled': True,
            'tools': agent_tools,
            'max_calls': self.max_tool_calls
        }
    
    def _format_context(self, context: Dict[str, Any]) -> Optional[str]:
        """Format context from other agents"""
        if not context:
            return None
            
        context_parts = []
        for agent_name, agent_output in context.items():
            if agent_output and agent_output.get('output'):
                context_parts.append(f"--- {agent_name.upper()} OUTPUT ---\n{agent_output['output']}\n")
        
        if context_parts:
            return "CONTEXT FROM OTHER AGENTS:\n\n" + "\n".join(context_parts)
        return None
    
    @abstractmethod
    def _format_task(self, task: str) -> str:
        """Format the task for this specific agent"""
        pass
    
    @abstractmethod
    def _process_response(self, response: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the LLM response and return structured result"""
        pass
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the agent's conversation history"""
        if not self.conversation_history:
            return f"{self.name} has not processed any tasks yet."
        
        return f"{self.name} has processed {len(self.conversation_history)//2} tasks."
