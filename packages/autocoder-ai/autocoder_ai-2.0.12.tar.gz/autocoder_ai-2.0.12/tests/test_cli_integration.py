#!/usr/bin/env python3
"""
CLI Integration Tests
Tests CLI functionality with different configurations
"""

import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path
import json

BASE_DIR = Path(__file__).parent.parent


class TestCLIIntegration:
    """Test CLI integration with various configurations"""
    
    def test_cli_help_command(self):
        """Test CLI help command"""
        result = subprocess.run([
            "python", "enhanced_main.py", "--help"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
        assert "AI Coding Agent System" in result.stdout
        assert "execute" in result.stdout
        assert "web" in result.stdout
    
    def test_cli_with_custom_config(self):
        """Test CLI with custom configuration file"""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create test config
            config_content = """
agents:
  planner:
    description: Strategic planning and task breakdown
    model:
      provider: openai
      model: gpt-4
      max_tokens: 1024
      temperature: 0

default_model:
  provider: openai
  model: gpt-4
  max_tokens: 1000
  temperature: 0

providers:
  openai:
    api_key: test-key
    enabled: true
    models:
      gpt-4: "gpt-4"

workflow:
  agent_timeout: 120
  max_iterations: 2

logging:
  level: INFO
"""
            
            config_file = temp_dir / "test_config.yaml"
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            # Test with custom config
            result = subprocess.run([
                "python", "enhanced_main.py", "execute",
                "Test task with custom config",
                "--config", str(config_file),
                "--dry-run",
                "--output-dir", str(temp_dir)
            ], cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
            
            # Should not crash and should mention config
            assert result.returncode == 0 or "config" in result.stdout.lower()
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_cli_offline_mode(self):
        """Test CLI offline mode functionality"""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            result = subprocess.run([
                "python", "enhanced_main.py", "execute",
                "Test offline mode execution",
                "--offline",
                "--dry-run",
                "--output-dir", str(temp_dir)
            ], cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0
            assert "offline" in result.stdout.lower() or "local" in result.stdout.lower()
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_cli_with_api_url(self):
        """Test CLI with custom API URL"""
        result = subprocess.run([
            "python", "enhanced_main.py", "execute",
            "Test with custom API URL",
            "--api-url", "http://localhost:5000",
            "--dry-run"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
        
        # Should attempt to connect or gracefully handle connection failure
        assert result.returncode == 0 or "API server" in result.stdout or "connection" in result.stdout.lower()
    
    def test_cli_projects_command(self):
        """Test CLI projects listing"""
        result = subprocess.run([
            "python", "enhanced_main.py", "projects"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=15)
        
        # Should not crash, even if no projects exist
        assert result.returncode == 0 or "projects" in result.stdout.lower()
    
    def test_cli_models_command(self):
        """Test CLI models listing"""
        result = subprocess.run([
            "python", "enhanced_main.py", "models"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=15)
        
        # Should not crash and should mention models
        assert result.returncode == 0 or "model" in result.stdout.lower()
    
    def test_cli_with_ollama_config(self):
        """Test CLI with Ollama configuration"""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create Ollama config
            ollama_config = """
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
    models:
      llama3-2-3b: "llama3.2:3b"
    default_model: "llama3.2:3b"
    timeout: 120

workflow:
  agent_timeout: 180
  max_iterations: 2

logging:
  level: INFO
"""
            
            config_file = temp_dir / "ollama_config.yaml"
            with open(config_file, 'w') as f:
                f.write(ollama_config)
            
            result = subprocess.run([
                "python", "enhanced_main.py", "execute",
                "Test with Ollama configuration", 
                "--config", str(config_file),
                "--offline",
                "--dry-run",
                "--output-dir", str(temp_dir)
            ], cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
            
            # Should handle Ollama config without crashing
            assert result.returncode == 0 or "ollama" in result.stdout.lower() or "llama" in result.stdout.lower()
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_cli_error_handling(self):
        """Test CLI error handling with invalid options"""
        # Test with non-existent config
        result = subprocess.run([
            "python", "enhanced_main.py", "execute",
            "Test error handling",
            "--config", "/nonexistent/config.yaml",
            "--dry-run"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=15)
        
        # Should fail gracefully
        assert result.returncode != 0
        assert "config" in result.stdout.lower() or "file" in result.stdout.lower()
    
    def test_cli_verbose_mode(self):
        """Test CLI verbose mode"""
        result = subprocess.run([
            "python", "enhanced_main.py", "execute",
            "Test verbose mode",
            "--verbose",
            "--dry-run", 
            "--offline"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
        
        assert result.returncode == 0
        # Verbose mode should produce more output
        assert len(result.stdout) > 100 or len(result.stderr) > 50


class TestAPIClient:
    """Test API client functionality"""
    
    def test_api_client_import(self):
        """Test that API client can be imported"""
        from cli.api_client import APIClient, OfflineAPIClient
        
        client = APIClient("http://localhost:5000")
        offline_client = OfflineAPIClient()
        
        assert client.base_url == "http://localhost:5000"
        assert offline_client.config_path == "config.yaml"
    
    def test_offline_api_client(self):
        """Test offline API client functionality"""
        from cli.api_client import OfflineAPIClient
        
        client = OfflineAPIClient()
        
        # Test basic functionality
        health = client.health_check()
        assert isinstance(health, bool)
        
        models = client.get_models()
        assert isinstance(models, dict)
        assert "success" in models
    
    def test_api_client_with_mock_server(self):
        """Test API client with mock responses"""
        from cli.api_client import APIClient
        
        client = APIClient("http://localhost:9999")  # Non-existent server
        
        # Should handle connection failures gracefully
        health = client.health_check()
        assert health is False
        
        models = client.get_models()
        assert models["success"] is False


if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])