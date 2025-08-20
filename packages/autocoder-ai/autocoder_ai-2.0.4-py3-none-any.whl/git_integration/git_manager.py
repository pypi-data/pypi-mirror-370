"""
Git operations manager for the AI Coding Agent System
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger()

class GitManager:
    """Manages Git operations for projects"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo_path.mkdir(parents=True, exist_ok=True)
    
    def _run_git_command(self, command: List[str], check_output: bool = True) -> Tuple[bool, str]:
        """Run a git command and return success status and output"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check_output
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(command)}, Error: {e.stderr}")
            return False, e.stderr.strip()
        except Exception as e:
            logger.error(f"Unexpected error running git command: {e}")
            return False, str(e)
    
    def init_repository(self, initial_commit: bool = True) -> bool:
        """Initialize a new Git repository"""
        if self.is_git_repo():
            logger.info("Repository already exists")
            return True
        
        success, output = self._run_git_command(['init'])
        if not success:
            return False
        
        # Set up initial configuration
        self._run_git_command(['config', 'user.name', 'AI Coding Agent'])
        self._run_git_command(['config', 'user.email', 'ai-agent@example.com'])
        
        if initial_commit:
            # Create initial .gitignore
            gitignore_content = """
# AI Agent System
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv/
venv/
*.log
.DS_Store
.idea/
.vscode/
*.swp
*.swo
*~

# Output directories
output/
test_output/
demo_output/

# Temporary files
temp/
tmp/
*.tmp
"""
            gitignore_path = self.repo_path / '.gitignore'
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content.strip())
            
            # Initial commit
            self.add_files(['.gitignore'])
            self.commit('Initial commit - AI Coding Agent System')
        
        logger.info(f"Initialized Git repository at {self.repo_path}")
        return True
    
    def is_git_repo(self) -> bool:
        """Check if the directory is a Git repository"""
        success, _ = self._run_git_command(['rev-parse', '--git-dir'], check_output=False)
        return success
    
    def add_files(self, files: List[str]) -> bool:
        """Add files to the staging area"""
        if not files:
            return True
        
        success, output = self._run_git_command(['add'] + files)
        if success:
            logger.info(f"Added files to staging: {files}")
        return success
    
    def add_all(self) -> bool:
        """Add all changes to the staging area"""
        success, output = self._run_git_command(['add', '.'])
        if success:
            logger.info("Added all changes to staging area")
        return success
    
    def commit(self, message: str, author: str = None) -> bool:
        """Create a commit with the given message"""
        command = ['commit', '-m', message]
        if author:
            command.extend(['--author', author])
        
        success, output = self._run_git_command(command)
        if success:
            logger.info(f"Created commit: {message}")
        return success
    
    def create_branch(self, branch_name: str, switch: bool = True) -> bool:
        """Create a new branch"""
        command = ['checkout', '-b', branch_name] if switch else ['branch', branch_name]
        success, output = self._run_git_command(command)
        if success:
            action = "Created and switched to" if switch else "Created"
            logger.info(f"{action} branch: {branch_name}")
        return success
    
    def switch_branch(self, branch_name: str) -> bool:
        """Switch to an existing branch"""
        success, output = self._run_git_command(['checkout', branch_name])
        if success:
            logger.info(f"Switched to branch: {branch_name}")
        return success
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name"""
        success, output = self._run_git_command(['branch', '--show-current'])
        return output if success else None
    
    def list_branches(self) -> List[str]:
        """List all branches"""
        success, output = self._run_git_command(['branch'])
        if not success:
            return []
        
        branches = []
        for line in output.split('\n'):
            branch = line.strip().lstrip('*').strip()
            if branch:
                branches.append(branch)
        return branches
    
    def get_status(self) -> Dict[str, List[str]]:
        """Get repository status"""
        success, output = self._run_git_command(['status', '--porcelain'])
        if not success:
            return {'modified': [], 'added': [], 'deleted': [], 'untracked': []}
        
        status = {'modified': [], 'added': [], 'deleted': [], 'untracked': []}
        
        for line in output.split('\n'):
            if not line.strip():
                continue
            
            status_code = line[:2]
            filename = line[3:]
            
            if status_code.startswith('M'):
                status['modified'].append(filename)
            elif status_code.startswith('A'):
                status['added'].append(filename)
            elif status_code.startswith('D'):
                status['deleted'].append(filename)
            elif status_code.startswith('??'):
                status['untracked'].append(filename)
        
        return status
    
    def get_commit_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get commit history"""
        success, output = self._run_git_command([
            'log', f'--max-count={limit}', '--pretty=format:%H|%an|%ae|%ad|%s'
        ])
        
        if not success:
            return []
        
        commits = []
        for line in output.split('\n'):
            if not line.strip():
                continue
            
            parts = line.split('|')
            if len(parts) >= 5:
                commits.append({
                    'hash': parts[0],
                    'author_name': parts[1],
                    'author_email': parts[2],
                    'date': parts[3],
                    'message': '|'.join(parts[4:])  # In case message contains |
                })
        
        return commits
    
    def create_agent_commit(self, agent_name: str, task_description: str, 
                          files_created: List[str]) -> bool:
        """Create a commit for AI agent work"""
        if not files_created:
            return True
        
        # Add the generated files
        if not self.add_files(files_created):
            return False
        
        # Create descriptive commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"""[{agent_name}] {task_description}

Generated files:
{chr(10).join(f'- {file}' for file in files_created)}

Timestamp: {timestamp}
Agent: {agent_name}"""
        
        return self.commit(commit_message, f"AI Agent <ai-agent@system.local>")
    
    def create_session_branch(self, session_id: str, task_description: str) -> bool:
        """Create a branch for a specific session"""
        # Clean task description for branch name
        clean_task = "".join(c if c.isalnum() or c in '-_' else '-' for c in task_description.lower())
        clean_task = clean_task[:50]  # Limit length
        
        branch_name = f"session-{session_id[:8]}-{clean_task}"
        return self.create_branch(branch_name)
    
    def merge_session_work(self, session_branch: str, target_branch: str = 'main') -> bool:
        """Merge session work back to target branch"""
        # Switch to target branch
        if not self.switch_branch(target_branch):
            return False
        
        # Merge the session branch
        success, output = self._run_git_command(['merge', session_branch, '--no-ff'])
        if success:
            logger.info(f"Merged {session_branch} into {target_branch}")
        
        return success
    
    def get_file_diff(self, file_path: str, commit1: str = None, commit2: str = None) -> str:
        """Get diff for a specific file"""
        command = ['diff']
        if commit1 and commit2:
            command.extend([commit1, commit2, '--', file_path])
        elif commit1:
            command.extend([commit1, '--', file_path])
        else:
            command.extend(['--', file_path])
        
        success, output = self._run_git_command(command)
        return output if success else ""
    
    def tag_release(self, tag_name: str, message: str = None) -> bool:
        """Create a release tag"""
        command = ['tag']
        if message:
            command.extend(['-a', tag_name, '-m', message])
        else:
            command.append(tag_name)
        
        success, output = self._run_git_command(command)
        if success:
            logger.info(f"Created tag: {tag_name}")
        return success
    
    def setup_remote(self, remote_url: str, name: str = 'origin') -> bool:
        """Add a remote repository"""
        success, output = self._run_git_command(['remote', 'add', name, remote_url])
        if success:
            logger.info(f"Added remote {name}: {remote_url}")
        return success
    
    def push_to_remote(self, remote: str = 'origin', branch: str = None) -> bool:
        """Push to remote repository"""
        if not branch:
            branch = self.get_current_branch()
        
        if not branch:
            return False
        
        success, output = self._run_git_command(['push', remote, branch])
        if success:
            logger.info(f"Pushed {branch} to {remote}")
        return success