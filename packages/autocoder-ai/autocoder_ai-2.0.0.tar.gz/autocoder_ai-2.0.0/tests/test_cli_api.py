"""
Tests for API-based CLI functionality
"""

import pytest
import subprocess
import json
import time
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.api_client import APIClient
from utils.port_finder import find_available_port, is_port_available, get_next_available_port
from utils.config_loader import ConfigLoader


class TestPortFinder:
    """Test port finding utilities"""
    
    def test_is_port_available(self):
        """Test port availability check"""
        # Find a random available port
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            available_port = s.getsockname()[1]
        
        # Should be available after closing
        assert is_port_available(available_port) == True
        
    def test_find_available_port(self):
        """Test finding available port in range"""
        port = find_available_port(50000, 10)
        assert port is not None
        assert 50000 <= port < 50010
        assert is_port_available(port)
        
    def test_get_next_available_port(self):
        """Test getting next available port with preferences"""
        # Use high ports unlikely to be in use
        preferred = [60001, 60002, 60003]
        port = get_next_available_port(preferred)
        assert port is not None
        assert is_port_available(port)

    def test_port_conflict_handling(self):
        """Test handling when preferred port is busy"""
        import socket
        
        # Block a port
        blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocker.bind(('127.0.0.1', 50100))
        
        try:
            # Should find alternative
            port = get_next_available_port([50100])
            assert port != 50100
            assert port is not None
        finally:
            blocker.close()


class TestAPIClient:
    """Test API client functionality"""
    
    @pytest.fixture
    def client(self):
        """Create API client instance"""
        return APIClient("http://localhost:5000")
    
    def test_client_initialization(self, client):
        """Test API client initialization"""
        assert client.base_url == "http://localhost:5000"
        assert client.session is not None
        
    @patch('requests.Session.get')
    def test_health_check_success(self, mock_get, client):
        """Test successful health check"""
        mock_get.return_value.status_code = 200
        assert client.health_check() == True
        mock_get.assert_called_with(
            "http://localhost:5000/api/health",
            timeout=5
        )
        
    @patch('requests.Session.get')
    def test_health_check_failure(self, mock_get, client):
        """Test failed health check"""
        mock_get.return_value.status_code = 500
        assert client.health_check() == False
        
    @patch('requests.Session.get')
    def test_health_check_exception(self, mock_get, client):
        """Test health check with exception"""
        mock_get.side_effect = Exception("Connection error")
        assert client.health_check() == False
        
    @patch('requests.Session.post')
    def test_create_project_success(self, mock_post, client):
        """Test successful project creation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "project": {
                "id": "proj-123",
                "name": "Test Project"
            }
        }
        mock_post.return_value = mock_response
        
        result = client.create_project("Test Project", "Description")
        assert result["success"] == True
        assert result["project"]["id"] == "proj-123"
        
    @patch('requests.Session.post')
    def test_create_project_error(self, mock_post, client):
        """Test project creation error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid project name"
        mock_post.return_value = mock_response
        
        result = client.create_project("", "Description")
        assert result["success"] == False
        assert "400" in result["error"]
        
    @patch('requests.Session.post')
    def test_execute_task(self, mock_post, client):
        """Test task execution"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "session_id": "sess-456",
            "project_id": "proj-123",
            "files_created": ["app.py", "test.py"]
        }
        mock_post.return_value = mock_response
        
        result = client.execute_task(
            "Create app",
            project_id="proj-123",
            config={"dry_run": True}
        )
        
        assert result["success"] == True
        assert result["session_id"] == "sess-456"
        assert len(result["files_created"]) == 2


class TestCLICommands:
    """Test CLI command execution"""
    
    def test_help_command(self):
        """Test help output"""
        result = subprocess.run(
            ["python", "main_api.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        
        assert result.returncode == 0
        assert "Autonomous AI Coding Agent System" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--verbose" in result.stdout
        assert "--save-logs" in result.stdout
        
    def test_missing_task_description(self):
        """Test error when task description is missing"""
        result = subprocess.run(
            ["python", "main_api.py"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        
        assert result.returncode == 2
        assert "Error" in result.stderr or "Usage" in result.stderr


class TestEmbeddedServer:
    """Test embedded API server functionality"""
    
    @patch('subprocess.Popen')
    @patch('cli.api_client.APIClient.health_check')
    def test_server_startup(self, mock_health, mock_popen):
        """Test embedded server startup"""
        from main_api import EmbeddedAPIServer
        
        # Mock successful server start
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc
        mock_health.side_effect = [False, False, True]  # Server starts on 3rd check
        
        server = EmbeddedAPIServer(port=5555)
        result = server.start()
        
        assert result == True
        assert mock_popen.called
        assert server.port == 5555
        
    def test_port_auto_detection(self):
        """Test automatic port detection"""
        from main_api import EmbeddedAPIServer
        
        server = EmbeddedAPIServer()
        assert server.port is not None
        assert is_port_available(server.port) or server.port in [5001, 5000, 5002]
        
    @patch('subprocess.Popen')
    def test_server_cleanup(self, mock_popen):
        """Test server cleanup on exit"""
        from main_api import EmbeddedAPIServer
        
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc
        
        server = EmbeddedAPIServer()
        server.process = mock_proc
        server.stop()
        
        mock_proc.terminate.assert_called_once()


class TestConfigIntegration:
    """Test configuration integration"""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config file"""
        import yaml
        
        config = {
            "api_keys": {
                "openai_api_key": "sk-test-key",
                "google_api_key": "test-google"
            },
            "agents": {
                "planner": {
                    "model": {"provider": "openai", "model": "gpt-3.5-turbo"},
                    "description": "Test planner"
                },
                "developer": {
                    "model": {"provider": "openai", "model": "gpt-3.5-turbo"},
                    "description": "Test developer"
                },
                "tester": {
                    "model": {"provider": "openai", "model": "gpt-3.5-turbo"},
                    "description": "Test tester"
                },
                "ui_ux_expert": {
                    "model": {"provider": "openai", "model": "gpt-3.5-turbo"},
                    "description": "Test UI/UX"
                },
                "db_expert": {
                    "model": {"provider": "openai", "model": "gpt-3.5-turbo"},
                    "description": "Test DB"
                },
                "devops_expert": {
                    "model": {"provider": "openai", "model": "gpt-3.5-turbo"},
                    "description": "Test DevOps"
                }
            },
            "default_model": {"provider": "openai", "model": "gpt-3.5-turbo"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            yield f.name
        
        os.unlink(f.name)
        
    def test_config_loading(self, temp_config):
        """Test configuration loading"""
        loader = ConfigLoader(temp_config)
        assert loader.load() == True
        
        # Check API keys loaded
        assert "openai_api_key" in loader.config["api_keys"]
        assert loader.config["api_keys"]["openai_api_key"] == "sk-test-key"
        
        # Check agents loaded
        assert "planner" in loader.config["agents"]
        assert "developer" in loader.config["agents"]
        
    def test_config_validation(self, temp_config):
        """Test configuration validation"""
        loader = ConfigLoader(temp_config)
        assert loader.load() == True
        
        # All required agents should be present
        required_agents = ["planner", "developer", "tester", 
                          "ui_ux_expert", "db_expert", "devops_expert"]
        for agent in required_agents:
            assert agent in loader.config["agents"]


class TestDryRunMode:
    """Test dry run functionality"""
    
    @patch('main_api.EmbeddedAPIServer.start')
    @patch('cli.api_client.APIClient.health_check')
    @patch('cli.api_client.APIClient.create_project')
    @patch('cli.api_client.APIClient.execute_task')
    def test_dry_run_execution(self, mock_execute, mock_create, mock_health, mock_start):
        """Test dry run mode execution"""
        from main_api import main
        from click.testing import CliRunner
        
        # Setup mocks
        mock_start.return_value = True
        mock_health.return_value = True
        mock_create.return_value = {
            "success": True,
            "project": {"id": "test-id", "name": "Test"}
        }
        mock_execute.return_value = {
            "success": True,
            "dry_run": True,
            "files_created": []
        }
        
        runner = CliRunner()
        result = runner.invoke(main, ["Test task", "--dry-run"])
        
        # Verify dry run was executed
        assert mock_execute.called
        config = mock_execute.call_args[1]["config"]
        assert config["dry_run"] == True


class TestLogging:
    """Test logging functionality"""
    
    @patch('main_api.EmbeddedAPIServer.start')
    @patch('cli.api_client.APIClient.health_check')
    @patch('cli.api_client.APIClient.create_project')
    @patch('cli.api_client.APIClient.execute_task')
    def test_save_logs_option(self, mock_execute, mock_create, mock_health, mock_start):
        """Test --save-logs option"""
        from main_api import main
        from click.testing import CliRunner
        
        # Setup mocks
        mock_start.return_value = True
        mock_health.return_value = True
        mock_create.return_value = {
            "success": True,
            "project": {"id": "test-id", "name": "Test"}
        }
        mock_execute.return_value = {
            "success": True,
            "files_created": []
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=tmpdir):
                result = runner.invoke(main, ["Test", "--save-logs"])
                
                # Check logs directory would be created
                assert "logs" in result.output or result.exit_code == 0


class TestErrorHandling:
    """Test error handling"""
    
    @patch('cli.api_client.APIClient.health_check')
    def test_connection_error(self, mock_health):
        """Test handling connection errors"""
        from main_api import main
        from click.testing import CliRunner
        
        mock_health.return_value = False
        
        runner = CliRunner()
        result = runner.invoke(main, [
            "Test", 
            "--api-url", "http://localhost:9999",
            "--no-embedded"
        ])
        
        assert result.exit_code != 0
        assert "Cannot connect" in result.output
        
    @patch('main_api.EmbeddedAPIServer.start')
    def test_server_start_failure(self, mock_start):
        """Test handling server start failure"""
        from main_api import main
        from click.testing import CliRunner
        
        mock_start.return_value = False
        
        runner = CliRunner()
        result = runner.invoke(main, ["Test task"])
        
        assert result.exit_code != 0
        assert "Failed to start" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
