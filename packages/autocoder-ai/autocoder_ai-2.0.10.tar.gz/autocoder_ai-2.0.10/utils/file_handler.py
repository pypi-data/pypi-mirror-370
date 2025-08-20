"""
File handling utilities for the agent system
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations for the agent system"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.created_files: List[str] = []
        
    def setup_output_directory(self) -> bool:
        """
        Setup the output directory structure
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create main output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            subdirs = [
                'code',
                'tests',
                'config',
                'docs',
                'scripts',
                'schemas'
            ]
            
            for subdir in subdirs:
                (self.output_dir / subdir).mkdir(exist_ok=True)
            
            logger.info(f"Output directory structure created at: {self.output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup output directory: {e}")
            return False
    
    def save_file(self, filename: str, content: str, subdir: Optional[str] = None, dry_run: bool = False) -> Optional[str]:
        """
        Save content to a file
        
        Args:
            filename: Name of the file
            content: Content to write
            subdir: Optional subdirectory
            dry_run: If True, don't actually create files
            
        Returns:
            File path if successful, None otherwise
        """
        try:
            # Determine file path
            if subdir:
                file_path = self.output_dir / subdir / filename
            else:
                # Auto-determine subdirectory based on file extension
                file_path = self.output_dir / self._get_auto_subdir(filename) / filename
            
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if dry_run:
                logger.info(f"[DRY RUN] Would create file: {file_path}")
                return str(file_path)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.created_files.append(str(file_path))
            logger.info(f"File created: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            return None
    
    def _get_auto_subdir(self, filename: str) -> str:
        """Automatically determine subdirectory based on file extension"""
        ext = filename.split('.')[-1].lower()
        
        extension_map = {
            'py': 'code',
            'js': 'code',
            'html': 'code',
            'css': 'code',
            'vue': 'code',
            'jsx': 'code',
            'tsx': 'code',
            'sql': 'schemas',
            'json': 'config',
            'yaml': 'config',
            'yml': 'config',
            'toml': 'config',
            'conf': 'config',
            'sh': 'scripts',
            'dockerfile': 'config',
            'md': 'docs',
            'txt': 'docs',
            'test.py': 'tests',
            'spec.js': 'tests'
        }
        
        # Check for test files
        if 'test' in filename.lower() or filename.startswith('test_'):
            return 'tests'
        
        return extension_map.get(ext, 'code')
    
    def read_file(self, file_path: str) -> Optional[str]:
        """
        Read content from a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content if successful, None otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def list_created_files(self) -> List[str]:
        """Get list of files created during this session"""
        return self.created_files.copy()
    
    def backup_output_directory(self, backup_name: Optional[str] = None) -> Optional[str]:
        """
        Create a backup of the output directory
        
        Args:
            backup_name: Optional backup name, defaults to timestamp
            
        Returns:
            Backup path if successful, None otherwise
        """
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_path = self.output_dir.parent / f"{self.output_dir.name}_{backup_name}"
            
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            shutil.copytree(self.output_dir, backup_path)
            logger.info(f"Backup created at: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def clean_output_directory(self, confirm: bool = False) -> bool:
        """
        Clean the output directory
        
        Args:
            confirm: If True, actually delete files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not confirm:
                logger.warning("clean_output_directory called without confirmation")
                return False
            
            if self.output_dir.exists():
                shutil.rmtree(self.output_dir)
                logger.info(f"Output directory cleaned: {self.output_dir}")
            
            self.created_files.clear()
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean output directory: {e}")
            return False
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """Get statistics about the output directory"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'subdirs': {}
        }
        
        try:
            if not self.output_dir.exists():
                return stats
            
            for root, dirs, files in os.walk(self.output_dir):
                root_path = Path(root)
                subdir_name = root_path.relative_to(self.output_dir)
                
                if str(subdir_name) not in stats['subdirs']:
                    stats['subdirs'][str(subdir_name)] = 0
                
                for file in files:
                    file_path = root_path / file
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        file_ext = file_path.suffix.lower()
                        
                        stats['total_files'] += 1
                        stats['total_size'] += file_size
                        stats['subdirs'][str(subdir_name)] += 1
                        
                        if file_ext not in stats['file_types']:
                            stats['file_types'][file_ext] = 0
                        stats['file_types'][file_ext] += 1
            
            # Convert size to human readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if stats['total_size'] < 1024.0:
                    stats['total_size_readable'] = f"{stats['total_size']:.1f} {unit}"
                    break
                stats['total_size'] /= 1024.0
            
        except Exception as e:
            logger.error(f"Failed to get directory stats: {e}")
        
        return stats
