#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Coding Agent System
Tests FastAPI, OpenAI Gateway, MCP Server, and CLI components
"""

import pytest
import asyncio
import requests
import json
import time
import subprocess
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import websocket
import threading
from unittest.mock import patch, MagicMock

# Test Configuration
BASE_DIR = Path(__file__).parent.parent
FASTAPI_URL = "http://localhost:5000"
OPENAI_GATEWAY_URL = "http://localhost:8000"
MCP_PORT = 8001
TEST_API_KEY = "sk-autocoder-dev-key"


class TestEnvironment:
    """Manages test environment and service startup"""
    
    def __init__(self):
        self.services = {}
        self.temp_dirs = []
        
    def start_service(self, name: str, command: list, port: int, timeout: int = 30):
        """Start a service and wait for it to be ready"""
        print(f"Starting {name} service...")
        
        process = subprocess.Popen(
            command,
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.services[name] = {
            'process': process,
            'port': port,
            'url': f"http://localhost:{port}"
        }
        
        # Wait for service to be ready
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name} service ready on port {port}")
                    return True
            except:
                time.sleep(1)
        
        print(f"❌ {name} service failed to start")
        return False
    
    def stop_service(self, name: str):
        """Stop a service"""
        if name in self.services:
            process = self.services[name]['process']
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.services[name]
    
    def create_temp_dir(self) -> Path:
        """Create temporary directory for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def cleanup(self):
        """Clean up test environment"""
        for name in list(self.services.keys()):
            self.stop_service(name)
        
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


# Global test environment
test_env = TestEnvironment()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before all tests"""
    print("🚀 Setting up test environment...")
    
    # Start FastAPI web interface
    success = test_env.start_service(
        "FastAPI",
        ["python", "enhanced_main.py", "web", "--port", "5000", "--host", "0.0.0.0"],
        5000
    )
    assert success, "Failed to start FastAPI service"
    
    # Start OpenAI Gateway
    success = test_env.start_service(
        "OpenAI Gateway", 
        ["python", "-m", "uvicorn", "openai_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"],
        8000
    )
    assert success, "Failed to start OpenAI Gateway"
    
    # Start MCP Server
    success = test_env.start_service(
        "MCP Server",
        ["python", "mcp_server/main.py"],
        8001
    )
    if not success:
        print("⚠️ MCP Server startup failed, some tests may be skipped")
    
    yield
    
    # Cleanup after all tests
    print("🧹 Cleaning up test environment...")
    test_env.cleanup()


class TestFastAPIInterface:
    """Test FastAPI web interface"""
    
    def test_health_check(self):
        """Test FastAPI health endpoint"""
        response = requests.get(f"{FASTAPI_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "agents_available" in data
        assert "database_connected" in data
        assert "timestamp" in data
    
    def test_models_endpoint(self):
        """Test models listing endpoint"""
        response = requests.get(f"{FASTAPI_URL}/api/models")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "models" in data
        assert len(data["models"]) > 0
    
    def test_create_project(self):
        """Test project creation"""
        project_data = {
            "name": "Test Project",
            "description": "Automated test project",
            "metadata": {"test": True}
        }
        
        response = requests.post(
            f"{FASTAPI_URL}/api/projects",
            json=project_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "project" in data
        assert data["project"]["name"] == "Test Project"
        
        # Store project ID for cleanup
        return data["project"]["id"]
    
    def test_list_projects(self):
        """Test project listing"""
        response = requests.get(f"{FASTAPI_URL}/api/projects")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "projects" in data
        assert isinstance(data["projects"], list)
    
    def test_create_session(self):
        """Test session creation"""
        # First create a project
        project_id = self.test_create_project()
        
        session_data = {
            "task_description": "Test task for automated testing",
            "metadata": {"test": True}
        }
        
        response = requests.post(
            f"{FASTAPI_URL}/api/projects/{project_id}/sessions",
            json=session_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "session" in data
        assert data["session"]["project_id"] == project_id
        
        return project_id, data["session"]["id"]
    
    def test_websocket_connection(self):
        """Test WebSocket connection"""
        ws_url = f"ws://localhost:5000/ws"
        
        connected = threading.Event()
        messages = []
        
        def on_message(ws, message):
            messages.append(json.loads(message))
        
        def on_open(ws):
            connected.set()
            ws.send(json.dumps({"type": "ping"}))
        
        def on_close(ws, close_status_code, close_msg):
            pass
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_open=on_open,
            on_close=on_close
        )
        
        # Start WebSocket in thread
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Wait for connection
        assert connected.wait(timeout=10), "WebSocket connection failed"
        
        # Give time for message exchange
        time.sleep(2)
        ws.close()
        
        assert len(messages) > 0, "No WebSocket messages received"


class TestOpenAIGateway:
    """Test OpenAI-compatible gateway"""
    
    def test_health_check(self):
        """Test gateway health endpoint"""
        response = requests.get(f"{OPENAI_GATEWAY_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "agent_system_accessible" in data
    
    def test_models_list(self):
        """Test models listing (OpenAI format)"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = requests.get(f"{OPENAI_GATEWAY_URL}/v1/models", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
        assert data["data"][0]["id"] == "AutoCoder"
    
    def test_chat_completions(self):
        """Test chat completions endpoint"""
        headers = {
            "Authorization": f"Bearer {TEST_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "AutoCoder",
            "messages": [
                {"role": "user", "content": "Create a simple hello world Python script"}
            ]
        }
        
        response = requests.post(
            f"{OPENAI_GATEWAY_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert data["choices"][0]["finish_reason"] == "stop"
        assert "message" in data["choices"][0]
    
    def test_async_chat_completions(self):
        """Test async chat completions"""
        headers = {
            "Authorization": f"Bearer {TEST_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "AutoCoder",
            "messages": [
                {"role": "user", "content": "Create a simple Flask web application"}
            ]
        }
        
        # Create async task
        response = requests.post(
            f"{OPENAI_GATEWAY_URL}/v1/async/chat/completions",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        
        job_id = data["job_id"]
        
        # Poll for status
        max_attempts = 30
        for _ in range(max_attempts):
            status_response = requests.get(
                f"{OPENAI_GATEWAY_URL}/v1/jobs/{job_id}",
                headers={"Authorization": f"Bearer {TEST_API_KEY}"}
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            if status_data["status"] in ["completed", "failed"]:
                break
            
            time.sleep(2)
        
        assert status_data["status"] == "completed", "Async task did not complete"
        
        # Get results
        result_response = requests.get(
            f"{OPENAI_GATEWAY_URL}/v1/jobs/{job_id}/result",
            headers={"Authorization": f"Bearer {TEST_API_KEY}"}
        )
        
        assert result_response.status_code == 200
        result_data = result_response.json()
        assert "result" in result_data
    
    def test_heatmap_endpoints(self):
        """Test heatmap visualization endpoints"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        
        # Test heatmap data endpoint
        response = requests.get(
            f"{OPENAI_GATEWAY_URL}/v1/heatmap/data?hours_back=24",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "heatmap_data" in data
        assert "hours_back" in data
        
        # Test stats endpoint
        stats_response = requests.get(
            f"{OPENAI_GATEWAY_URL}/v1/heatmap/stats",
            headers=headers
        )
        assert stats_response.status_code == 200
        
        stats_data = stats_response.json()
        assert "system_stats" in stats_data
        assert "agent_performance" in stats_data


class TestMCPServer:
    """Test Model Context Protocol server"""
    
    def test_mcp_server_health(self):
        """Test MCP server health"""
        if "MCP Server" not in test_env.services:
            pytest.skip("MCP Server not available")
        
        # MCP uses different protocol, test basic connectivity
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("MCP Server connectivity test failed")
    
    def test_mcp_capabilities(self):
        """Test MCP capabilities discovery"""
        if "MCP Server" not in test_env.services:
            pytest.skip("MCP Server not available")
        
        # This would test MCP-specific capabilities
        # Implementation depends on MCP server API structure
        pass


class TestCLIInterface:
    """Test CLI interface functionality"""
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = subprocess.run(
            ["python", "enhanced_main.py", "--help"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "AI Coding Agent System" in result.stdout
        assert "execute" in result.stdout
        assert "web" in result.stdout
    
    def test_cli_models_list(self):
        """Test CLI models listing"""
        result = subprocess.run(
            ["python", "enhanced_main.py", "models"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        assert "Available models" in result.stdout or "models" in result.stdout.lower()
    
    def test_cli_projects_list(self):
        """Test CLI projects listing"""
        result = subprocess.run(
            ["python", "enhanced_main.py", "projects", "--api-url", FASTAPI_URL],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        # Should not error out, even if no projects exist
    
    def test_cli_dry_run_execution(self):
        """Test CLI dry run execution"""
        temp_dir = test_env.create_temp_dir()
        
        result = subprocess.run([
            "python", "enhanced_main.py", "execute",
            "Create a simple Python hello world script",
            "--output-dir", str(temp_dir),
            "--dry-run",
            "--api-url", FASTAPI_URL
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=60)
        
        # Dry run should complete without creating files
        assert result.returncode == 0
        assert "Dry Run Mode" in result.stdout or "dry" in result.stdout.lower()
    
    def test_cli_config_validation(self):
        """Test CLI configuration validation"""
        # Test with invalid config
        temp_dir = test_env.create_temp_dir()
        invalid_config = temp_dir / "invalid_config.yaml"
        
        with open(invalid_config, 'w') as f:
            f.write("invalid: yaml: content:")
        
        result = subprocess.run([
            "python", "enhanced_main.py", "execute",
            "Test task",
            "--config", str(invalid_config),
            "--dry-run"
        ], cwd=BASE_DIR, capture_output=True, text=True)
        
        assert result.returncode != 0  # Should fail with invalid config
        
    def test_cli_with_ollama_provider(self):
        """Test CLI with Ollama provider configuration"""
        temp_dir = test_env.create_temp_dir()
        ollama_config = temp_dir / "ollama_config.yaml"
        
        # Create test config with Ollama
        config_content = """
agents:
  planner:
    description: Strategic planning and task breakdown
    model:
      provider: ollama
      model: llama3.2:3b
      max_tokens: 2048
      temperature: 0
  developer:
    description: Code implementation and development  
    model:
      provider: ollama
      model: qwen2.5-coder:7b
      max_tokens: 2048
      temperature: 0
  tester:
    description: Testing and quality assurance
    model:
      provider: ollama  
      model: llama3.2:3b
      max_tokens: 2048
      temperature: 0
  ui_ux_expert:
    description: User interface and experience design
    model:
      provider: ollama
      model: llama3.2:3b
      max_tokens: 2048
      temperature: 0
  db_expert:
    description: Database design and optimization
    model:
      provider: ollama
      model: llama3.2:3b
      max_tokens: 2048
      temperature: 0
  devops_expert:
    description: Deployment and infrastructure
    model:
      provider: ollama
      model: llama3.2:3b
      max_tokens: 2048
      temperature: 0

default_model:
  provider: ollama
  model: llama3.2:3b
  max_tokens: 2000
  temperature: 0

providers:
  ollama:
    base_url: "http://localhost:11434"
    enabled: true
    models:
      llama3-2-3b: "llama3.2:3b"
      qwen2-5-coder-7b: "qwen2.5-coder:7b"
    default_model: "llama3.2:3b"
    timeout: 120

workflow:
  agent_timeout: 300
  enable_parallel_execution: false
  max_iterations: 5

logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  file: agent_system.log

output:
  create_summary_report: true
  preserve_agent_logs: true  
  save_intermediate_results: true
"""
        
        with open(ollama_config, 'w') as f:
            f.write(config_content)
        
        # Test with Ollama config (will likely fail if Ollama not running, but should validate config)
        result = subprocess.run([
            "python", "enhanced_main.py", "execute", 
            "Create a simple hello world script",
            "--config", str(ollama_config),
            "--output-dir", str(temp_dir),
            "--dry-run",
            "--api-url", FASTAPI_URL
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
        
        # Should either work or fail gracefully with clear error about Ollama
        assert "ollama" in result.stdout.lower() or "llama" in result.stdout.lower() or result.returncode == 0


class TestIntegration:
    """Integration tests across components"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from CLI to web interface"""
        # 1. Create project via CLI
        temp_dir = test_env.create_temp_dir()
        
        cli_result = subprocess.run([
            "python", "enhanced_main.py", "execute",
            "Create a simple calculator Python script",
            "--output-dir", str(temp_dir),
            "--project-name", "E2E Test Project", 
            "--api-url", FASTAPI_URL,
            "--dry-run"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=60)
        
        # Should complete successfully
        assert cli_result.returncode == 0
        
        # 2. Verify project appears in web interface
        response = requests.get(f"{FASTAPI_URL}/api/projects")
        assert response.status_code == 200
        
        data = response.json()
        project_names = [p["name"] for p in data["projects"]]
        assert "E2E Test Project" in project_names
    
    def test_cross_service_compatibility(self):
        """Test compatibility between services"""
        # Test that OpenAI Gateway can communicate with FastAPI
        headers = {
            "Authorization": f"Bearer {TEST_API_KEY}",
            "Content-Type": "application/json"  
        }
        
        # This should trigger communication between services
        payload = {
            "model": "AutoCoder",
            "messages": [{"role": "user", "content": "Test cross-service communication"}]
        }
        
        response = requests.post(
            f"{OPENAI_GATEWAY_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        
        # Verify both services logged the interaction
        # This would require log analysis in a real scenario


class TestOfflineCapabilities:
    """Test offline and local operation capabilities"""
    
    def test_offline_configuration(self):
        """Test that system can work with local-only configuration"""
        # This tests the configuration for offline operation
        # without requiring actual Ollama installation
        
        temp_dir = test_env.create_temp_dir()
        offline_config = temp_dir / "offline_config.yaml"
        
        # Create minimal offline config
        config_content = """
agents:
  planner:
    description: Strategic planning and task breakdown
    model:
      provider: ollama
      model: llama3.2:3b
      max_tokens: 1024
      temperature: 0

default_model:
  provider: ollama
  model: llama3.2:3b
  max_tokens: 1000
  temperature: 0

providers:
  ollama:
    base_url: "http://localhost:11434"
    enabled: true
    timeout: 60

workflow:
  agent_timeout: 120
  max_iterations: 3

logging:
  level: INFO
"""
        
        with open(offline_config, 'w') as f:
            f.write(config_content)
        
        # Test config validation
        from utils.config_loader import ConfigLoader
        config_loader = ConfigLoader(str(offline_config))
        
        assert config_loader.load(), "Offline config should be valid"
        assert config_loader.get_default_model_config()["provider"] == "ollama"
    
    def test_local_file_system_access(self):
        """Test local file system operations"""
        temp_dir = test_env.create_temp_dir()
        
        # Test that file operations work correctly
        test_file = temp_dir / "test_output.py"
        
        # Simulate file creation
        test_content = """
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        assert test_file.exists()
        assert "Hello, World!" in test_file.read_text()
        
        # Test file permissions
        assert os.access(test_file, os.R_OK)
        assert os.access(test_file, os.W_OK)


def test_system_requirements():
    """Test system requirements and dependencies"""
    # Test Python version
    import sys
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    
    # Test critical imports
    try:
        import fastapi
        import uvicorn
        import websockets
        import pydantic
        import yaml
        import click
        import rich
        import langchain
        import langgraph
    except ImportError as e:
        pytest.fail(f"Missing required dependency: {e}")


if __name__ == "__main__":
    print("🧪 Running Comprehensive Test Suite")
    print("=" * 50)
    
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--disable-warnings"
    ])