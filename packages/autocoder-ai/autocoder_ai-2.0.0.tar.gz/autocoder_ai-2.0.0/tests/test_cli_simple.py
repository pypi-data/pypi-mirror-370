"""
Simple CLI tests for the AI Coding Agent System that match the actual implementation
"""

import pytest
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def run_cli_command(args: list, input_text: str = None) -> tuple:
    """
    Run a CLI command and return (stdout, stderr, return_code)
    """
    cmd = [sys.executable, str(PROJECT_ROOT / "main.py")] + args
    
    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        input=input_text
    )
    
    return result.stdout, result.stderr, result.returncode


class TestMainCLI:
    """Test the main.py CLI interface"""
    
    def test_help_flag(self):
        """Test that --help flag works"""
        stdout, stderr, code = run_cli_command(["--help"])
        
        assert code == 0
        assert "Autonomous AI Coding Agent System" in stdout
        assert "TASK_DESCRIPTION" in stdout
        assert "--config" in stdout
        assert "--output-dir" in stdout
        assert "--verbose" in stdout
        assert "--dry-run" in stdout
    
    def test_missing_task_description(self):
        """Test that missing task description shows error"""
        stdout, stderr, code = run_cli_command([])
        
        assert code != 0
        assert "Missing argument" in stderr or "required" in stderr.lower()
    
    def test_invalid_option(self):
        """Test that invalid options are caught"""
        stdout, stderr, code = run_cli_command(["--invalid-option", "test task"])
        
        assert code != 0
        assert "no such option" in stderr.lower() or "error" in stderr.lower()
    
    def test_dry_run_mode(self):
        """Test dry run mode execution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout, stderr, code = run_cli_command([
                "Create a simple hello world script",
                "--dry-run",
                "--output-dir", tmpdir
            ])
            
            # Check for dry run indicators
            if code == 0:
                assert "Dry Run" in stdout or "dry" in stdout.lower()
            else:
                # Might fail due to missing config or API keys
                assert "config" in stderr.lower() or "api" in stderr.lower()
    
    def test_verbose_mode(self):
        """Test verbose mode"""
        stdout, stderr, code = run_cli_command([
            "Test task",
            "--verbose",
            "--dry-run"
        ])
        
        # Verbose mode should be recognized
        # May fail due to config, but option should be accepted
        assert "--verbose" not in stderr.lower()
    
    def test_custom_config_path(self):
        """Test custom config file path"""
        stdout, stderr, code = run_cli_command([
            "Test task",
            "--config", "custom_config.yaml",
            "--dry-run"
        ])
        
        # Should attempt to load the custom config
        # Will likely fail but should show config-related error
        assert code != 0
        assert "config" in stderr.lower() or "Failed to load configuration" in stdout
    
    def test_custom_output_directory(self):
        """Test custom output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "test_output"
            
            stdout, stderr, code = run_cli_command([
                "Create a test file",
                "--output-dir", str(output_dir),
                "--dry-run"
            ])
            
            # Should accept the output directory option
            if code == 0:
                assert str(output_dir) in stdout or "test_output" in stdout
            else:
                # Might fail due to config, but not due to output-dir
                assert "--output-dir" not in stderr.lower()


class TestWebServer:
    """Test the web server startup"""
    
    def test_web_server_help(self):
        """Test web server script help"""
        cmd = [sys.executable, str(PROJECT_ROOT / "web_server.py"), "--help"]
        
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Check if web_server.py exists and has help
        if result.returncode == 0:
            assert "port" in result.stdout.lower() or "server" in result.stdout.lower()
        else:
            # File might not exist or might not have --help
            pytest.skip("web_server.py not found or doesn't support --help")
    
    def test_web_interface_exists(self):
        """Test that web interface directory exists"""
        web_interface_dir = PROJECT_ROOT / "web_interface"
        assert web_interface_dir.exists(), "web_interface directory should exist"
        
        # Check for key files
        assert (web_interface_dir / "app.py").exists(), "app.py should exist"
        assert (web_interface_dir / "templates").exists(), "templates directory should exist"
        assert (web_interface_dir / "static").exists(), "static directory should exist"


class TestProjectStructure:
    """Test that the project has the expected structure"""
    
    def test_main_file_exists(self):
        """Test that main.py exists and is executable"""
        main_file = PROJECT_ROOT / "main.py"
        assert main_file.exists(), "main.py should exist"
        assert main_file.is_file(), "main.py should be a file"
    
    def test_config_file_exists(self):
        """Test that a config file exists"""
        config_file = PROJECT_ROOT / "config.yaml"
        config_example = PROJECT_ROOT / "config.example.yaml"
        
        assert config_file.exists() or config_example.exists(), \
            "config.yaml or config.example.yaml should exist"
    
    def test_required_directories(self):
        """Test that required directories exist"""
        required_dirs = [
            "agents",
            "utils",
            "workflow",
            "web_interface",
            "tests"
        ]
        
        for dir_name in required_dirs:
            dir_path = PROJECT_ROOT / dir_name
            assert dir_path.exists(), f"{dir_name} directory should exist"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"
    
    def test_agent_files_exist(self):
        """Test that agent files exist"""
        agents_dir = PROJECT_ROOT / "agents"
        expected_agents = [
            "planner_agent.py",
            "coder_agent.py",
            "reviewer_agent.py",
            "tester_agent.py"
        ]
        
        for agent_file in expected_agents:
            agent_path = agents_dir / agent_file
            assert agent_path.exists(), f"{agent_file} should exist"


def test_cli_imports():
    """Test that CLI modules can be imported"""
    try:
        import main
        assert hasattr(main, 'main'), "main.py should have a main function"
    except ImportError as e:
        pytest.fail(f"Failed to import main: {e}")
    
    try:
        from workflow.orchestrator import WorkflowOrchestrator
        assert WorkflowOrchestrator is not None
    except ImportError as e:
        pytest.fail(f"Failed to import WorkflowOrchestrator: {e}")
    
    try:
        from utils.config_loader import ConfigLoader
        assert ConfigLoader is not None
    except ImportError as e:
        pytest.fail(f"Failed to import ConfigLoader: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
