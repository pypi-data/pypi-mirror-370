"""
FastAPI routes for the AI Coding Agent System
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
from utils.funny_names import generate_funny_project_name

from memory.project_memory import ProjectMemory
from workflow.orchestrator import WorkflowOrchestrator
from utils.config_loader import ConfigLoader
from utils.file_handler import FileHandler
from utils.logger import setup_logger
from web_interface.object_storage import get_storage_service

# Import MCP components
try:
    from web_interface.mcp_config import mcp_config_manager
    from agents.mcp_client import mcp_client_manager
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = setup_logger()

# Pydantic models for request/response
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = {}

class SessionCreate(BaseModel):
    task_description: str
    context: Optional[Dict[str, Any]] = {}

class QuickTaskCreate(BaseModel):
    task_description: str
    execute_immediately: Optional[bool] = False

class TaskExecution(BaseModel):
    execution_options: Optional[Dict[str, Any]] = {}

class DirectTaskExecution(BaseModel):
    task_description: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}

class ConfigUpdate(BaseModel):
    global_settings: Optional[Dict[str, Any]] = None
    reasoning: Optional[Dict[str, Any]] = None
    providers: Optional[Dict[str, Any]] = None
    agents: Optional[Dict[str, Dict[str, Any]]] = None

class MCPServerConfig(BaseModel):
    name: str
    command: str
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    timeout: int = 30
    enabled: bool = True
    description: str = ""

class AgentToolsConfig(BaseModel):
    agent_name: str
    tools: List[str]

class AgentConfigUpdate(BaseModel):
    """Model for updating agent configuration"""
    name: str
    system_prompt: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tools_enabled: Optional[bool] = None
    available_tools: Optional[List[str]] = None
    mcp_servers: Optional[List[Dict[str, Any]]] = None

class AgentMCPServerAdd(BaseModel):
    """Model for adding MCP server to agent"""
    name: str
    type: str = "stdio"
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    api_key: Optional[str] = None
    enabled: bool = True

# Router
router = APIRouter()

# Initialize components
memory = ProjectMemory()
config_loader = ConfigLoader("config.yaml")
config_loader.load()

@router.get("/projects")
async def list_projects():
    """List all projects"""
    try:
        projects = memory.list_projects()
        return {"success": True, "projects": projects}
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects")
async def create_project(project: ProjectCreate):
    """Create a new project"""
    try:
        if not project.name:
            raise HTTPException(status_code=400, detail="Project name is required")
        
        project_id = memory.create_project(project.name, project.description, project.metadata)
        project_data = memory.get_project(project_id)
        
        logger.info(f"Created project: {project.name} (ID: {project_id})")
        return {"success": True, "project": project_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    try:
        project = memory.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        sessions = memory.get_project_sessions(project_id)
        project['sessions'] = sessions
        
        return {"success": True, "project": project}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/sessions")
async def get_project_sessions(project_id: str):
    """Get all sessions for a project"""
    try:
        project = memory.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        sessions = memory.get_project_sessions(project_id)
        return {"success": True, "sessions": sessions}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/sessions")
async def create_session(project_id: str, session: SessionCreate):
    """Create a new session for a project"""
    try:
        if not session.task_description:
            raise HTTPException(status_code=400, detail="Task description is required")
        
        # Check if project exists
        project = memory.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        session_id = memory.create_session(project_id, session.task_description, session.context)
        session_data = memory.get_session(session_id)
        
        logger.info(f"Created session: {session_id} for project: {project_id}")
        return {"success": True, "session": session_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/quick")
async def create_quick_task(task: QuickTaskCreate):
    """Create a task without specifying a project (creates default project)"""
    try:
        if not task.task_description:
            raise HTTPException(status_code=400, detail="Task description is required")
        
        # Create a default project with a funny name
        project_name = generate_funny_project_name()
        project_description = f"Auto-generated project for: {task.task_description[:100]}..."
        metadata = {
            "auto_generated": True,
            "enable_git": False,
            "create_readme": False
        }
        
        # Create the project
        project_id = memory.create_project(project_name, project_description, metadata)
        
        # Create a session for the task
        session_id = memory.create_session(project_id, task.task_description)
        session = memory.get_session(session_id)
        
        logger.info(f"Created quick task in project '{project_name}' (ID: {project_id})")
        
        return {
            "success": True,
            "project_id": project_id,
            "project_name": project_name,
            "session": session,
            "message": f"Task created in project '{project_name}'"
        }
    except Exception as e:
        logger.error(f"Error creating quick task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_direct_task(task: DirectTaskExecution):
    """Execute a task directly (CLI endpoint)"""
    try:
        # If no project_id, create a new project
        if not task.project_id:
            project_name = generate_funny_project_name()
            project_description = f"CLI Task: {task.task_description[:100]}..."
            metadata = {
                "source": "cli",
                "auto_generated": True
            }
            task.project_id = memory.create_project(project_name, project_description, metadata)
            logger.info(f"Created project {project_name} for CLI task")
        
        # Create a session if not provided
        if not task.session_id:
            task.session_id = memory.create_session(task.project_id, task.task_description)
            logger.info(f"Created session {task.session_id} for task")
        
        # Get configuration
        config = task.config or {}
        dry_run = config.get("dry_run", False)
        verbose = config.get("verbose", False)
        
        if dry_run:
            # Dry run - don't execute, just return success
            return {
                "success": True,
                "message": "Dry run completed successfully",
                "session_id": task.session_id,
                "project_id": task.project_id,
                "dry_run": True,
                "files_created": [],
                "agent_results": {
                    "planner": {"success": True, "output": "Planning phase (dry run)"},
                    "developer": {"success": True, "output": "Development phase (dry run)"},
                    "tester": {"success": True, "output": "Testing phase (dry run)"}
                }
            }
        
        # Execute the workflow
        output_dir = config_loader.config.get('output', {}).get('directory', 'output')
        orchestrator = WorkflowOrchestrator(
            config=config_loader.config,
            output_dir=output_dir,
            dry_run=False,
            enable_human_approval=False
        )
        result = await orchestrator.execute_task_async(
            task_description=task.task_description,
            project_id=task.project_id,
            session_id=task.session_id,
            verbose=verbose
        )
        
        # Update session with results
        memory.update_session(task.session_id, {
            "status": "completed" if result.get("success") else "failed",
            "result": result
        })
        
        return {
            "success": result.get("success", False),
            "session_id": task.session_id,
            "project_id": task.project_id,
            "files_created": result.get("files_created", []),
            "output_dir": result.get("output_dir", "output"),
            "agent_results": result.get("agent_results", {}),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error executing direct task: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": task.session_id if hasattr(task, 'session_id') else None,
            "project_id": task.project_id if hasattr(task, 'project_id') else None
        }

@router.post("/sessions/{session_id}/execute")
async def execute_task(session_id: str, task: TaskExecution):
    """Execute a task using the agent system"""
    try:
        session = memory.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # In a full implementation, this would start the workflow orchestrator
        # For now, we return a success response indicating task execution started
        return {
            "success": True, 
            "message": "Task execution started",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    try:
        session = memory.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "session": session}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/download")
async def download_session_files(session_id: str):
    """Download files generated by a session"""
    try:
        session = memory.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        files_created = session.get('files_created', [])
        if not files_created:
            raise HTTPException(status_code=404, detail="No files to download")
        
        # In a real implementation, this would create a zip file
        # For now, return the file list
        return {
            "success": True,
            "session_id": session_id,
            "files": files_created,
            "message": "File download endpoint - implementation pending"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading session files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config():
    """Get system configuration"""
    try:
        return {
            "success": True,
            "config": {
                "agents": list(config_loader.config.get('agents', {}).keys()),
                "output_directory": config_loader.config.get('output', {}).get('directory', 'output'),
                "supported_providers": ['openai', 'anthropic', 'google', 'azure', 'deepseek', 'xai', 'mistral', 'perplexity'],
                "reasoning_models": ['anthropic/claude-3-7-sonnet-20250219', 'deepseek/deepseek-chat', 'xai/grok-beta', 'perplexity/llama-3.1-sonar-large-128k-online'],
                "current_settings": config_loader.config
            }
        }
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config")
async def update_config(config_data: Dict[str, Any]):
    """Update system configuration"""
    try:
        logger.info(f"Updating configuration: {config_data}")
        
        # Update the config - merge with existing config
        updated_config = dict(config_loader.config)
        
        # Update global settings
        if 'global' in config_data:
            updated_config.setdefault('global_settings', {}).update(config_data['global'])
        
        # Update reasoning settings  
        if 'reasoning' in config_data:
            updated_config.setdefault('reasoning_settings', {}).update(config_data['reasoning'])
        
        # Update provider settings
        if 'providers' in config_data:
            updated_config.setdefault('providers', {}).update(config_data['providers'])
        
        # Update agent configurations
        if 'agents' in config_data:
            for agent_key, agent_config in config_data['agents'].items():
                if agent_key in updated_config.get('agents', {}):
                    # Parse model string (e.g., "openai/gpt-4" -> provider="openai", model="gpt-4")
                    model_string = agent_config.get('model', '')
                    if model_string:
                        model_parts = model_string.split('/', 1)
                        provider = model_parts[0] if len(model_parts) > 1 else 'openai'
                        model = model_parts[1] if len(model_parts) > 1 else model_string
                        
                        # Update agent model configuration
                        agent_settings = updated_config['agents'][agent_key]
                        agent_settings['model'] = {
                            'provider': provider,
                            'model': model,
                            'temperature': agent_config.get('temperature', 0),
                            'max_tokens': agent_config.get('max_tokens', 2048)
                        }
                        
                        # Update reasoning settings
                        if 'reasoning' in agent_config:
                            agent_settings['reasoning'] = agent_config['reasoning']
        
        # Save configuration
        config_loader.config = updated_config
        config_loader.save()
        
        logger.info("Configuration saved to config.yaml")
        logger.info("Configuration updated successfully")
        
        return {"success": True, "message": "Configuration updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints
@router.get("/sessions/{session_id}/files")
async def get_session_files(session_id: str):
    """Get files generated by a session"""
    try:
        session = memory.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        files = session.get('files_created', [])
        return {"success": True, "files": files}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        project = memory.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # In a full implementation, this would delete the project
        return {"success": True, "message": "Project deletion initiated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Heatmap proxy endpoints to avoid CORS issues
@router.get("/heatmap/data")
async def get_heatmap_data(hours_back: int = 24):
    """Get heatmap data from OpenAI Gateway"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/v1/heatmap/data?hours_back={hours_back}",
                headers={"Authorization": "Bearer sk-autocoder-dev-key"},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"heatmap_data": [], "hours_back": hours_back, "error": "Gateway not available"}
    except Exception as e:
        logger.warning(f"Heatmap data unavailable: {e}")
        return {"heatmap_data": [], "hours_back": hours_back, "error": str(e)}

@router.get("/heatmap/stats") 
async def get_heatmap_stats():
    """Get heatmap stats from OpenAI Gateway"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/v1/heatmap/stats",
                headers={"Authorization": "Bearer sk-autocoder-dev-key"},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"system_stats": {}, "agent_performance": {}, "error": "Gateway not available"}
    except Exception as e:
        logger.warning(f"Heatmap stats unavailable: {e}")
        return {"system_stats": {}, "agent_performance": {}, "error": str(e)}

@router.post("/providers/{provider_name}/test")
async def test_provider_api_key(provider_name: str, request: dict):
    """Test API key and fetch available models for a provider"""
    try:
        api_key = request.get('api_key')
        base_url = request.get('base_url', None)
        
        if not api_key:
            return {"success": False, "error": "API key is required"}
        
        # Test the API key and fetch models
        models = await _fetch_models_for_provider(provider_name, api_key, base_url)
        
        return {
            "success": True,
            "models": models,
            "message": f"Successfully fetched {len(models)} models"
        }
        
    except Exception as e:
        logger.error(f"Error testing {provider_name} API key: {e}")
        return {"success": False, "error": str(e)}

async def _fetch_models_for_provider(provider_name: str, api_key: str, base_url: str = None):
    """Fetch available models for a specific provider"""
    import httpx
    models = []
    
    try:
        if provider_name == "openai":
            # OpenAI models endpoint
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        # Check if model supports reasoning (o1 models)
                        supports_reasoning = "o1" in model_id or "o3" in model_id or "gpt-5" in model_id
                        # Check if model supports vision/images
                        supports_vision = "gpt-4" in model_id and "vision" in model_id or "gpt-4o" in model_id or "gpt-5" in model_id
                        models.append({
                            "id": model_id,
                            "name": model_id,
                            "supports_reasoning": supports_reasoning,
                            "supports_vision": supports_vision,
                            "created": model.get("created"),
                            "owned_by": model.get("owned_by")
                        })
                        
        elif provider_name == "openai_compatible":
            # OpenAI compatible endpoint
            if not base_url:
                return []
                
            url = f"{base_url.rstrip('/')}/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        # Most OpenAI compatible don't support reasoning yet
                        supports_reasoning = False
                        # Check for vision support in custom models
                        supports_vision = "vision" in model_id.lower() or "multimodal" in model_id.lower()
                        models.append({
                            "id": model_id,
                            "name": model_id,
                            "supports_reasoning": supports_reasoning,
                            "supports_vision": supports_vision,
                            "created": model.get("created"),
                            "owned_by": model.get("owned_by", "custom")
                        })
                        
        elif provider_name == "anthropic":
            # Anthropic doesn't have a models endpoint, return known models
            anthropic_models = [
                {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "supports_reasoning": True, "supports_vision": True},
                {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "supports_reasoning": False, "supports_vision": True},
                {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "supports_reasoning": False, "supports_vision": True},
                {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "supports_reasoning": False, "supports_vision": True},
                {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "supports_reasoning": False, "supports_vision": True},
            ]
            # Test key validity with a simple request
            import httpx
            headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01"}
            test_url = "https://api.anthropic.com/v1/messages"
            async with httpx.AsyncClient() as client:
                test_response = await client.post(
                    test_url, 
                    headers=headers,
                    json={"model": "claude-3-haiku-20240307", "max_tokens": 1, "messages": [{"role": "user", "content": "test"}]},
                    timeout=10.0
                )
                if test_response.status_code in [200, 400]:  # 400 is OK, means API key works
                    models = anthropic_models
                else:
                    raise Exception("Invalid API key")
            
        elif provider_name == "google":
            # Google Gemini API models endpoint
            url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("models", []):
                        model_name = model.get("name", "")
                        model_id = model_name.replace("models/", "") if model_name.startswith("models/") else model_name
                        display_name = model.get("displayName", model_id)
                        
                        # Check if model supports reasoning (thinking/flash-thinking models)
                        supports_reasoning = "thinking" in model_id.lower() or "deep-think" in model_id.lower()
                        
                        # Check if model supports vision (most Gemini models are multimodal)
                        supports_vision = "vision" not in model.get("supportedGenerationMethods", [])
                        # Actually, let's check properly - Gemini Pro Vision and newer models support images
                        supports_vision = "gemini-pro-vision" in model_id or "gemini-1.5" in model_id or "gemini-2" in model_id
                        
                        # Only include models that support generateContent (text generation)
                        if "generateContent" in model.get("supportedGenerationMethods", []):
                            models.append({
                                "id": model_id,
                                "name": display_name,
                                "supports_reasoning": supports_reasoning,
                                "supports_vision": supports_vision,
                                "description": model.get("description", ""),
                                "input_token_limit": model.get("inputTokenLimit"),
                                "output_token_limit": model.get("outputTokenLimit")
                            })
                else:
                    # Log the error for debugging
                    logger.error(f"Google API error: {response.status_code} - {response.text}")
                    if response.status_code == 400:
                        raise Exception("Invalid API key or API not enabled. Please check your Google Cloud Console.")
                    elif response.status_code == 403:
                        raise Exception("API key lacks permission. Enable Generative Language API in Google Cloud Console.")
                    else:
                        raise Exception(f"Failed to fetch models: {response.status_code}")
                        
        elif provider_name == "deepseek":
            # DeepSeek models - they use OpenAI-compatible API
            url = "https://api.deepseek.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        # DeepSeek R1 supports reasoning
                        supports_reasoning = "r1" in model_id.lower() or "reasoner" in model_id.lower()
                        # DeepSeek doesn't have vision models yet
                        supports_vision = False
                        models.append({
                            "id": model_id,
                            "name": model_id,
                            "supports_reasoning": supports_reasoning,
                            "supports_vision": supports_vision,
                            "created": model.get("created"),
                            "owned_by": model.get("owned_by", "deepseek")
                        })
                else:
                    raise Exception(f"Failed to fetch DeepSeek models: {response.status_code}")
                    
        elif provider_name == "xai":
            # XAI (Grok) - they use OpenAI-compatible API  
            url = "https://api.x.ai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        # Grok 3 and beta support reasoning
                        supports_reasoning = "grok-3" in model_id or "grok-beta" in model_id
                        # Check for vision support
                        supports_vision = "vision" in model_id.lower()
                        models.append({
                            "id": model_id,
                            "name": model_id,
                            "supports_reasoning": supports_reasoning,
                            "supports_vision": supports_vision,
                            "created": model.get("created"),
                            "owned_by": model.get("owned_by", "xai")
                        })
                else:
                    raise Exception(f"Failed to fetch XAI models: {response.status_code}")
                    
        elif provider_name == "mistral":
            # Mistral AI API
            url = "https://api.mistral.ai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        # Mistral doesn't have reasoning models yet
                        supports_reasoning = False
                        # Pixtral is Mistral's vision model
                        supports_vision = "pixtral" in model_id.lower() or "vision" in model_id.lower()
                        models.append({
                            "id": model_id,
                            "name": model_id,
                            "supports_reasoning": supports_reasoning,
                            "supports_vision": supports_vision,
                            "created": model.get("created"),
                            "owned_by": model.get("owned_by", "mistralai")
                        })
                else:
                    raise Exception(f"Failed to fetch Mistral models: {response.status_code}")
                    
        elif provider_name == "ollama":
            # Ollama local models endpoint
            ollama_url = base_url or "http://localhost:11434"
            url = f"{ollama_url}/api/tags"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("models", []):
                        model_name = model.get("name", "")
                        # Most Ollama models don't support reasoning yet
                        supports_reasoning = False
                        # Check for vision support in Ollama models (llava, bakllava, etc.)
                        supports_vision = "llava" in model_name.lower() or "vision" in model_name.lower() or "multimodal" in model_name.lower()
                        models.append({
                            "id": model_name,
                            "name": model_name,
                            "supports_reasoning": supports_reasoning,
                            "supports_vision": supports_vision,
                            "size": model.get("size"),
                            "modified_at": model.get("modified_at")
                        })
        
        # Sort models by name
        models.sort(key=lambda x: x.get("name", ""))
        
    except httpx.TimeoutException:
        raise Exception("Request timed out - check your network connection")
    except httpx.ConnectError:
        raise Exception("Could not connect to API endpoint")
    except Exception as e:
        raise Exception(f"Error fetching models: {str(e)}")
    
    return models

# Image upload endpoints

@router.post("/local-upload/{filename}")
async def handle_local_upload(filename: str, file: UploadFile = File(...)):
    """Handle local file uploads when running without cloud storage"""
    try:
        storage_service = get_storage_service()
        
        # Only handle local uploads if we're not on Replit
        if hasattr(storage_service, 'is_replit') and storage_service.is_replit:
            raise HTTPException(status_code=400, detail="Use cloud upload endpoint")
        
        # Read file data
        file_data = await file.read()
        
        # Save to local storage
        if hasattr(storage_service, 'local_storage'):
            file_path = await storage_service.local_storage.save_uploaded_file(filename, file_data)
            return {"success": True, "file_path": file_path, "filename": filename}
        else:
            raise HTTPException(status_code=500, detail="Local storage not available")
            
    except Exception as e:
        logger.error(f"Local upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/local-files/{filename}")
async def serve_local_file(filename: str):
    """Serve local files when running without cloud storage"""
    try:
        storage_service = get_storage_service()
        
        # Only serve local files if we're not on Replit
        if hasattr(storage_service, 'is_replit') and storage_service.is_replit:
            raise HTTPException(status_code=404, detail="File not found")
        
        if hasattr(storage_service, 'local_storage'):
            file_path = storage_service.local_storage.private_dir / filename
            
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            from fastapi.responses import FileResponse
            return FileResponse(file_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except Exception as e:
        logger.error(f"Local file serve error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Image upload endpoints

class ImageUploadRequest(BaseModel):
    filename: str

@router.post("/images/upload-url")
async def get_image_upload_url(request: ImageUploadRequest):
    """Get presigned URL for image upload"""
    try:
        storage_service = get_storage_service()
        upload_url = await storage_service.get_upload_url(request.filename)
        
        return {
            "success": True,
            "upload_url": upload_url,
            "filename": request.filename
        }
    except Exception as e:
        logger.error(f"Error getting upload URL: {e}")
        return {"success": False, "error": str(e)}

class ImageMetadata(BaseModel):
    filename: str
    upload_url: str
    content_type: str
    session_id: Optional[str] = None
    task_description: Optional[str] = None

@router.post("/images/metadata")
async def store_image_metadata(image_data: ImageMetadata):
    """Store metadata for uploaded image"""
    try:
        # Store image metadata in session/project memory if needed
        # For now, just return success - can be expanded later
        
        return {
            "success": True,
            "message": "Image metadata stored",
            "image_id": image_data.filename
        }
    except Exception as e:
        logger.error(f"Error storing image metadata: {e}")
        return {"success": False, "error": str(e)}

@router.get("/images/session/{session_id}")
async def get_session_images(session_id: str):
    """Get images for a specific session"""
    try:
        # This would query the memory system for images
        # For now, return empty list - can be expanded later
        
        return {
            "success": True,
            "images": [],
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error getting session images: {e}")
        return {"success": False, "error": str(e)}

# ===== MCP SERVER CONFIGURATION ENDPOINTS =====

@router.get("/mcp/servers")
async def list_mcp_servers():
    """List all MCP server configurations"""
    if not MCP_AVAILABLE:
        raise HTTPException(status_code=501, detail="MCP support not available")
    
    try:
        servers = mcp_config_manager.get_servers()
        status = mcp_config_manager.get_status()
        return {
            "success": True,
            "servers": servers,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error listing MCP servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/servers")
async def add_mcp_server(config: MCPServerConfig):
    """Add a new MCP server configuration"""
    if not MCP_AVAILABLE:
        raise HTTPException(status_code=501, detail="MCP support not available")
    
    try:
        server_config = {
            'command': config.command,
            'args': config.args or [],
            'env': config.env or {},
            'timeout': config.timeout,
            'enabled': config.enabled,
            'description': config.description
        }
        
        mcp_config_manager.add_server(config.name, server_config)
        
        return {
            "success": True,
            "message": f"MCP server '{config.name}' added successfully",
            "server": config.dict()
        }
    except Exception as e:
        logger.error(f"Error adding MCP server: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mcp/tools")
async def list_available_tools():
    """List all available tools from all connected MCP servers"""
    if not MCP_AVAILABLE:
        raise HTTPException(status_code=501, detail="MCP support not available")
    
    try:
        all_tools = mcp_client_manager.get_available_tools()
        tools_by_server = {}
        
        for tool_name, tool_info in all_tools.items():
            server_name = tool_info.get('server', 'unknown')
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            tools_by_server[server_name].append({
                'name': tool_name,
                'description': tool_info.get('description', ''),
                'schema': tool_info.get('input_schema', {})
            })
        
        return {
            "success": True,
            "tools_by_server": tools_by_server,
            "total_tools": len(all_tools)
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mcp/status")
async def get_mcp_status():
    """Get MCP system status"""
    if not MCP_AVAILABLE:
        return {
            "success": False,
            "available": False,
            "message": "MCP support not available"
        }
    
    try:
        status = mcp_config_manager.get_status()
        return {
            "success": True,
            "available": True,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error getting MCP status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== AGENT CONFIGURATION ENDPOINTS =====

@router.get("/agents")
async def list_agents():
    """List all configured agents"""
    try:
        agents = config_loader.config.get('agents', {})
        agent_list = []
        
        for agent_id, agent_config in agents.items():
            agent_info = {
                'id': agent_id,
                'name': agent_config.get('name', agent_id),
                'description': agent_config.get('description', ''),
                'model': agent_config.get('model', {}),
                'tools_enabled': agent_config.get('tools_enabled', False),
                'available_tools': agent_config.get('available_tools', [])
            }
            agent_list.append(agent_info)
        
        return {"success": True, "agents": agent_list}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/config")
async def get_agent_config(agent_id: str):
    """Get detailed configuration for a specific agent"""
    try:
        agents = config_loader.config.get('agents', {})
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_config = agents[agent_id]
        
        # Try to load enhanced config if available
        try:
            from agents.agent_config import EnhancedAgentConfig, AgentConfigManager
            manager = AgentConfigManager()
            enhanced_config = manager.load_config(agent_id, agent_config)
            return {
                "success": True,
                "agent_id": agent_id,
                "config": enhanced_config.model_dump(),
                "enhanced": True
            }
        except:
            # Fall back to basic config
            return {
                "success": True,
                "agent_id": agent_id,
                "config": agent_config,
                "enhanced": False
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/agents/{agent_id}/config")
async def update_agent_config(agent_id: str, config_update: AgentConfigUpdate):
    """Update configuration for a specific agent"""
    try:
        agents = config_loader.config.get('agents', {})
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_config = agents[agent_id]
        
        # Update system prompt
        if config_update.system_prompt is not None:
            agent_config['system_prompt'] = config_update.system_prompt
        
        # Update model configuration
        if config_update.model_provider or config_update.model_name:
            if 'model' not in agent_config:
                agent_config['model'] = {}
            if config_update.model_provider:
                agent_config['model']['provider'] = config_update.model_provider
            if config_update.model_name:
                agent_config['model']['model'] = config_update.model_name
        
        if config_update.temperature is not None:
            if 'model' not in agent_config:
                agent_config['model'] = {}
            agent_config['model']['temperature'] = config_update.temperature
        
        if config_update.max_tokens is not None:
            if 'model' not in agent_config:
                agent_config['model'] = {}
            agent_config['model']['max_tokens'] = config_update.max_tokens
        
        # Update tools configuration
        if config_update.tools_enabled is not None:
            agent_config['tools_enabled'] = config_update.tools_enabled
        
        if config_update.available_tools is not None:
            agent_config['available_tools'] = config_update.available_tools
        
        # Save configuration
        config_loader.save()
        
        logger.info(f"Updated configuration for agent '{agent_id}'")
        return {
            "success": True,
            "message": f"Agent '{agent_id}' configuration updated",
            "config": agent_config
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/mcp-servers")
async def add_agent_mcp_server(agent_id: str, server: AgentMCPServerAdd):
    """Add an MCP server to a specific agent"""
    try:
        from agents.agent_config import (
            EnhancedAgentConfig, AgentConfigManager, 
            MCPServerConfig as AgentMCPConfig
        )
        
        agents = config_loader.config.get('agents', {})
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Load agent config
        manager = AgentConfigManager()
        agent_config = manager.load_config(agent_id, agents[agent_id])
        
        # Create MCP server config
        mcp_server = AgentMCPConfig(
            name=server.name,
            type=server.type,
            command=server.command,
            args=server.args,
            url=server.url,
            api_key=server.api_key,
            enabled=server.enabled
        )
        
        # Add to agent
        agent_config.add_mcp_server(mcp_server)
        
        # Save back to config
        agents[agent_id] = manager.save_config(agent_id, agent_config)
        config_loader.save()
        
        logger.info(f"Added MCP server '{server.name}' to agent '{agent_id}'")
        return {
            "success": True,
            "message": f"MCP server '{server.name}' added to agent '{agent_id}'",
            "server": server.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding MCP server to agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agents/{agent_id}/mcp-servers/{server_name}")
async def remove_agent_mcp_server(agent_id: str, server_name: str):
    """Remove an MCP server from a specific agent"""
    try:
        from agents.agent_config import EnhancedAgentConfig, AgentConfigManager
        
        agents = config_loader.config.get('agents', {})
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Load agent config
        manager = AgentConfigManager()
        agent_config = manager.load_config(agent_id, agents[agent_id])
        
        # Remove MCP server
        if not agent_config.remove_mcp_server(server_name):
            raise HTTPException(status_code=404, detail="MCP server not found")
        
        # Save back to config
        agents[agent_id] = manager.save_config(agent_id, agent_config)
        config_loader.save()
        
        logger.info(f"Removed MCP server '{server_name}' from agent '{agent_id}'")
        return {
            "success": True,
            "message": f"MCP server '{server_name}' removed from agent '{agent_id}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing MCP server from agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/tools")
async def get_agent_tools(agent_id: str):
    """Get all available tools for a specific agent"""
    try:
        agents = config_loader.config.get('agents', {})
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_config = agents[agent_id]
        tools = {
            "builtin": agent_config.get('available_tools', []),
            "mcp_servers": [],
            "total": 0
        }
        
        # Try to get MCP server tools if enhanced config is available
        try:
            from agents.agent_config import EnhancedAgentConfig, AgentConfigManager
            manager = AgentConfigManager()
            enhanced_config = manager.load_config(agent_id, agent_config)
            
            for mcp_server in enhanced_config.get_mcp_servers():
                tools["mcp_servers"].append({
                    "name": mcp_server.name,
                    "enabled": mcp_server.enabled,
                    "tools": mcp_server.tools or []
                })
        except:
            pass
        
        tools["total"] = len(tools["builtin"]) + sum(
            len(s.get("tools", [])) for s in tools["mcp_servers"]
        )
        
        return {"success": True, "agent_id": agent_id, "tools": tools}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))
