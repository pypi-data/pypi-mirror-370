"""
Secure code execution environment for testing generated code
"""

import subprocess
import tempfile
import os
import signal
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import threading
import shutil

from utils.logger import setup_logger

logger = setup_logger()

class ExecutionResult:
    """Result of code execution"""
    def __init__(self, success: bool, output: str = "", error: str = "", 
                 execution_time: float = 0.0, timeout: bool = False):
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.timeout = timeout
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'output': self.output,
            'error': self.error,
            'execution_time': self.execution_time,
            'timeout': self.timeout
        }

class CodeExecutor:
    """Secure code executor with sandboxing capabilities"""
    
    def __init__(self, timeout: int = 30, max_memory_mb: int = 512):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        self.temp_dir = None
        self._setup_sandbox()
    
    def _setup_sandbox(self):
        """Set up temporary sandbox directory"""
        self.temp_dir = tempfile.mkdtemp(prefix="ai_agent_sandbox_")
        logger.info(f"Created sandbox directory: {self.temp_dir}")
    
    def cleanup(self):
        """Clean up sandbox directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up sandbox directory: {self.temp_dir}")
    
    def execute_python(self, code: str, dependencies: List[str] = None) -> ExecutionResult:
        """Execute Python code in a sandboxed environment"""
        return self._execute_with_language(code, 'python', dependencies or [])
    
    def execute_javascript(self, code: str, dependencies: List[str] = None) -> ExecutionResult:
        """Execute JavaScript code using Node.js"""
        return self._execute_with_language(code, 'javascript', dependencies or [])
    
    def execute_shell(self, commands: List[str]) -> ExecutionResult:
        """Execute shell commands safely"""
        # Join commands with && for sequential execution
        command_str = " && ".join(commands)
        return self._execute_command(['bash', '-c', command_str])
    
    def _execute_with_language(self, code: str, language: str, dependencies: List[str]) -> ExecutionResult:
        """Execute code for a specific language"""
        if language == 'python':
            return self._execute_python_code(code, dependencies)
        elif language == 'javascript':
            return self._execute_javascript_code(code, dependencies)
        else:
            return ExecutionResult(False, "", f"Unsupported language: {language}")
    
    def _execute_python_code(self, code: str, dependencies: List[str]) -> ExecutionResult:
        """Execute Python code with dependency management"""
        start_time = time.time()
        
        try:
            # Create a temporary Python file
            python_file = os.path.join(self.temp_dir, "temp_script.py")
            
            # Prepare the code with safety measures
            safe_code = self._prepare_safe_python_code(code, dependencies)
            
            with open(python_file, 'w') as f:
                f.write(safe_code)
            
            # Install dependencies if needed
            if dependencies:
                dep_result = self._install_python_dependencies(dependencies)
                if not dep_result.success:
                    return dep_result
            
            # Execute the Python script
            result = self._execute_command(['python3', python_file])
            result.execution_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(False, "", str(e), execution_time)
    
    def _execute_javascript_code(self, code: str, dependencies: List[str]) -> ExecutionResult:
        """Execute JavaScript code with Node.js"""
        start_time = time.time()
        
        try:
            # Create package.json if dependencies are needed
            if dependencies:
                package_json = {
                    "name": "temp-sandbox",
                    "version": "1.0.0",
                    "dependencies": {dep: "latest" for dep in dependencies}
                }
                
                import json
                with open(os.path.join(self.temp_dir, "package.json"), 'w') as f:
                    json.dump(package_json, f)
                
                # Install dependencies
                npm_result = self._execute_command(['npm', 'install'], cwd=self.temp_dir)
                if not npm_result.success:
                    return npm_result
            
            # Create JavaScript file
            js_file = os.path.join(self.temp_dir, "temp_script.js")
            with open(js_file, 'w') as f:
                f.write(code)
            
            # Execute the JavaScript file
            result = self._execute_command(['node', js_file], cwd=self.temp_dir)
            result.execution_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(False, "", str(e), execution_time)
    
    def _prepare_safe_python_code(self, code: str, dependencies: List[str]) -> str:
        """Prepare Python code with safety measures"""
        safe_imports = []
        
        # Add imports for dependencies
        for dep in dependencies:
            safe_imports.append(f"import {dep}")
        
        # Add basic safety measures
        safety_code = """
import sys
import os

# Limit execution time and resources
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
"""
        
        # Indent the original code
        indented_code = "\n".join(f"    {line}" for line in code.split("\n"))
        
        safety_code += indented_code + """
except TimeoutError as e:
    print(f"TIMEOUT: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
finally:
    signal.alarm(0)  # Disable the alarm
"""
        
        return "\n".join(safe_imports) + "\n" + safety_code
    
    def _install_python_dependencies(self, dependencies: List[str]) -> ExecutionResult:
        """Install Python dependencies using pip"""
        try:
            # Create requirements.txt
            req_file = os.path.join(self.temp_dir, "requirements.txt")
            with open(req_file, 'w') as f:
                f.write("\n".join(dependencies))
            
            # Install dependencies
            return self._execute_command([
                'pip3', 'install', '-r', req_file, '--user', '--quiet'
            ])
            
        except Exception as e:
            return ExecutionResult(False, "", f"Failed to install dependencies: {e}")
    
    def _execute_command(self, command: List[str], cwd: str = None) -> ExecutionResult:
        """Execute a command with timeout and resource limits"""
        start_time = time.time()
        
        try:
            # Use the sandbox directory as working directory if not specified
            if cwd is None:
                cwd = self.temp_dir
            
            # Execute with timeout
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                preexec_fn=os.setsid  # Create new process group for clean termination
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                execution_time = time.time() - start_time
                
                success = process.returncode == 0
                return ExecutionResult(
                    success=success,
                    output=stdout,
                    error=stderr,
                    execution_time=execution_time
                )
                
            except subprocess.TimeoutExpired:
                # Kill the process group to ensure all child processes are terminated
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait()
                
                execution_time = time.time() - start_time
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Execution timed out",
                    execution_time=execution_time,
                    timeout=True
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time
            )
    
    def test_generated_code(self, code_files: Dict[str, str], test_files: Dict[str, str]) -> Dict[str, ExecutionResult]:
        """Test generated code with test files"""
        results = {}
        
        try:
            # Write code files to sandbox
            for filename, content in code_files.items():
                file_path = os.path.join(self.temp_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Write and execute test files
            for test_name, test_content in test_files.items():
                test_path = os.path.join(self.temp_dir, test_name)
                with open(test_path, 'w') as f:
                    f.write(test_content)
                
                # Determine execution method based on file extension
                if test_name.endswith('.py'):
                    result = self._execute_command(['python3', test_path])
                elif test_name.endswith('.js'):
                    result = self._execute_command(['node', test_path])
                else:
                    result = ExecutionResult(False, "", f"Unsupported test file type: {test_name}")
                
                results[test_name] = result
                
        except Exception as e:
            results['error'] = ExecutionResult(False, "", str(e))
        
        return results
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()