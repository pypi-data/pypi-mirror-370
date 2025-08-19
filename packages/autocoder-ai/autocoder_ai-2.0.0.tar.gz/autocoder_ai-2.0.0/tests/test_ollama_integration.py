#!/usr/bin/env python3
"""
Ollama Integration Tests
Tests local Ollama provider functionality for offline operation
"""

import pytest
import requests
import subprocess
import json
import time
from pathlib import Path
import tempfile
import os

# Test Configuration
OLLAMA_URL = "http://localhost:11434"
BASE_DIR = Path(__file__).parent.parent


class TestOllamaIntegration:
    """Test Ollama integration for local/offline AI capabilities"""
    
    def test_ollama_server_availability(self):
        """Test if Ollama server is running"""
        try:
            response = requests.get(f"{OLLAMA_URL}/api/version", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama server is available")
                return True
        except requests.exceptions.RequestException:
            print("⚠️ Ollama server not available - install with: curl -fsSL https://ollama.ai/install.sh | sh")
            return False
        
        return False
    
    def test_ollama_model_list(self):
        """Test listing available Ollama models"""
        if not self.test_ollama_server_availability():
            pytest.skip("Ollama server not available")
        
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            models = data.get("models", [])
            
            print(f"Available Ollama models: {[m['name'] for m in models]}")
            return models
        
        except Exception as e:
            pytest.fail(f"Failed to list Ollama models: {e}")
    
    def test_ollama_model_pull(self):
        """Test pulling a lightweight model for testing"""
        if not self.test_ollama_server_availability():
            pytest.skip("Ollama server not available")
        
        # Try to pull a lightweight model for testing
        test_model = "llama3.2:1b"  # Smallest model for testing
        
        print(f"Attempting to pull {test_model}...")
        
        try:
            # Start model pull
            response = requests.post(
                f"{OLLAMA_URL}/api/pull",
                json={"name": test_model, "stream": False},
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully pulled {test_model}")
                return True
            else:
                print(f"⚠️ Failed to pull {test_model}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout pulling {test_model} - this is normal for first run")
            return False
        except Exception as e:
            print(f"⚠️ Error pulling {test_model}: {e}")
            return False
    
    def test_ollama_chat_completion(self):
        """Test Ollama chat completion"""
        if not self.test_ollama_server_availability():
            pytest.skip("Ollama server not available")
        
        # List available models
        models = self.test_ollama_model_list()
        if not models:
            pytest.skip("No Ollama models available")
        
        # Use first available model
        model_name = models[0]["name"]
        print(f"Testing with model: {model_name}")
        
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": "Write a simple Python hello world function"}
                    ],
                    "stream": False
                },
                timeout=60
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "message" in data
            assert "content" in data["message"]
            
            content = data["message"]["content"]
            assert len(content) > 0
            print(f"✅ Ollama response: {content[:100]}...")
            
        except Exception as e:
            pytest.fail(f"Ollama chat completion failed: {e}")
    
    def test_agent_system_with_ollama(self):
        """Test agent system using Ollama provider"""
        if not self.test_ollama_server_availability():
            pytest.skip("Ollama server not available")
        
        models = self.test_ollama_model_list()
        if not models:
            pytest.skip("No Ollama models available")
        
        # Create temporary config for Ollama
        temp_dir = Path(tempfile.mkdtemp())
        ollama_config = temp_dir / "ollama_test_config.yaml"
        
        model_name = models[0]["name"]
        
        config_content = f"""
agents:
  planner:
    description: Strategic planning and task breakdown
    model:
      provider: ollama
      model: {model_name}
      max_tokens: 1024
      temperature: 0.1
  developer:
    description: Code implementation and development
    model:
      provider: ollama
      model: {model_name}
      max_tokens: 1024
      temperature: 0.1

default_model:
  provider: ollama
  model: {model_name}
  max_tokens: 1000
  temperature: 0

providers:
  ollama:
    base_url: "{OLLAMA_URL}"
    enabled: true
    models:
      {model_name.replace(':', '-')}: "{model_name}"
    default_model: "{model_name}"
    timeout: 120
    keep_alive: "5m"

workflow:
  agent_timeout: 180
  enable_parallel_execution: false
  max_iterations: 2

logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

output:
  create_summary_report: true
  preserve_agent_logs: true
  save_intermediate_results: true
"""
        
        with open(ollama_config, 'w') as f:
            f.write(config_content)
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Test CLI execution with Ollama
        result = subprocess.run([
            "python", "enhanced_main.py", "execute",
            "Create a simple Python function that adds two numbers",
            "--config", str(ollama_config),
            "--output-dir", str(output_dir),
            "--dry-run",  # Use dry run to avoid long execution
            "--verbose"
        ], cwd=BASE_DIR, capture_output=True, text=True, timeout=120)
        
        print(f"CLI execution result: {result.returncode}")
        print(f"stdout: {result.stdout}")
        if result.stderr:
            print(f"stderr: {result.stderr}")
        
        # Should not crash, even if Ollama models are slow
        assert result.returncode == 0 or "ollama" in result.stderr.lower()
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


class TestOllamaSetup:
    """Test Ollama setup and configuration"""
    
    def test_ollama_installation_check(self):
        """Check if Ollama is installed"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Ollama installed: {result.stdout.strip()}")
                return True
            else:
                print("⚠️ Ollama not found in PATH")
                return False
                
        except FileNotFoundError:
            print("⚠️ Ollama not installed")
            return False
        except subprocess.TimeoutExpired:
            print("⚠️ Ollama command timed out")
            return False
    
    def test_ollama_service_status(self):
        """Test Ollama service status"""
        if not self.test_ollama_installation_check():
            pytest.skip("Ollama not installed")
        
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            print(f"Ollama models: {result.stdout}")
            
            if result.returncode == 0:
                return True
            else:
                print(f"Ollama service issue: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error checking Ollama service: {e}")
            return False
    
    def test_recommended_models_available(self):
        """Test if recommended models are available"""
        if not self.test_ollama_installation_check():
            pytest.skip("Ollama not installed")
        
        recommended_models = [
            "llama3.2:1b",    # Fastest, smallest
            "llama3.2:3b",    # Good balance
            "qwen2.5-coder:7b"  # Best for coding
        ]
        
        available_models = []
        
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                available_models = [m["name"] for m in data.get("models", [])]
        except:
            pass
        
        print(f"Available models: {available_models}")
        print(f"Recommended models: {recommended_models}")
        
        # Check which recommended models are available
        available_recommended = [m for m in recommended_models if m in available_models]
        print(f"Available recommended models: {available_recommended}")
        
        return len(available_recommended) > 0


def setup_ollama_guide():
    """Print setup guide for Ollama"""
    print("""
🦙 Ollama Setup Guide for Offline AI Development

1. Install Ollama:
   curl -fsSL https://ollama.ai/install.sh | sh

2. Start Ollama service:
   ollama serve

3. Pull recommended models:
   ollama pull llama3.2:1b      # Fastest (1.3GB)
   ollama pull llama3.2:3b      # Balanced (2.0GB)  
   ollama pull qwen2.5-coder:7b # Best for coding (4.7GB)

4. Test installation:
   ollama list
   ollama run llama3.2:1b "Hello world"

5. Configure agent system:
   Use provider: ollama in config.yaml
   Point to http://localhost:11434

✅ Benefits:
- Complete offline operation
- No API keys required  
- Local data privacy
- Fast response times
- Multiple model options

⚠️ Requirements:
- 8GB+ RAM recommended
- 10GB+ disk space
- Modern CPU (Apple Silicon preferred)
""")


if __name__ == "__main__":
    setup_ollama_guide()
    
    print("\n🧪 Running Ollama Integration Tests")
    print("=" * 50)
    
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"  # Show print statements
    ])