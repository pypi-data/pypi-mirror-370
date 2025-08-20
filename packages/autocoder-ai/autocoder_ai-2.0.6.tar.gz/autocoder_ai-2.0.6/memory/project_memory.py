"""
Project memory management for persistent context across sessions
"""

import json
import uuid
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from utils.logger import setup_logger
import logging

# Use module logger to respect global logging configuration
logger = logging.getLogger(__name__)

class ProjectMemory:
    """Manages project memory and context persistence using SQLite"""
    
    def __init__(self, db_path: str = "ai_agent_system.db"):
        self.db_path = Path(db_path)
        self._initialize_tables()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _dict_factory(self, cursor, row):
        """Convert sqlite3.Row to dict"""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    
    def _initialize_tables(self):
        """Initialize database tables for memory persistence"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    task_description TEXT NOT NULL,
                    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT,
                    status TEXT DEFAULT 'running',
                    agent_results TEXT DEFAULT '{}',
                    files_created TEXT DEFAULT '[]',
                    context TEXT DEFAULT '{}',
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            # Context history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_history (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    context_type TEXT NOT NULL,
                    context_data TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Code execution results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_results (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    code_snippet TEXT NOT NULL,
                    execution_output TEXT,
                    execution_error TEXT,
                    success INTEGER DEFAULT 0,
                    executed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            logger.debug("SQLite memory persistence tables initialized")  # Changed from info to debug
    
    def create_project(self, name: str, description: str = "", metadata: Dict = None) -> Dict:
        """Create a new project and return its data"""
        project_id = str(uuid.uuid4())
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (id, name, description, metadata)
                VALUES (?, ?, ?, ?)
            """, (project_id, name, description, json.dumps(metadata or {})))
            conn.commit()
        
        logger.info(f"Created project: {name} (ID: {project_id})")
        return {
            'id': project_id,
            'name': name,
            'description': description,
            'metadata': metadata or {},
            'status': 'active'
        }
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        with self._get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM projects WHERE id = ?
            """, (project_id,))
            result = cursor.fetchone()
            if result and result.get('metadata'):
                try:
                    result['metadata'] = json.loads(result['metadata'])
                except:
                    result['metadata'] = {}
            return result
    
    def update_project(self, project_id: str, name: str = None, description: str = None, 
                      status: str = None, metadata: Dict = None):
        """Update project details"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(json.dumps(metadata))
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(project_id)
                cursor.execute(f"""
                    UPDATE projects SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
                conn.commit()
                logger.info(f"Updated project: {project_id}")
    
    def list_projects(self, status: str = None) -> List[Dict]:
        """List all projects, optionally filtered by status"""
        with self._get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT * FROM projects WHERE status = ? 
                    ORDER BY updated_at DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT * FROM projects ORDER BY updated_at DESC
                """)
            results = cursor.fetchall()
            for result in results:
                if result.get('metadata'):
                    try:
                        result['metadata'] = json.loads(result['metadata'])
                    except:
                        result['metadata'] = {}
            return results
    
    def get_all_projects(self) -> List[Dict]:
        """Alias for list_projects() for compatibility"""
        return self.list_projects()
    
    def create_session(self, project_id: str, task_description: str, context: Dict = None) -> Dict:
        """Create a new session for a project"""
        session_id = str(uuid.uuid4())
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (id, project_id, task_description, context)
                VALUES (?, ?, ?, ?)
            """, (session_id, project_id, task_description, json.dumps(context or {})))
            
            # Update project's updated_at timestamp
            cursor.execute("""
                UPDATE projects SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (project_id,))
            
            conn.commit()
        
        logger.info(f"Created session: {session_id} for project: {project_id}")
        return {
            'id': session_id,
            'project_id': project_id,
            'task_description': task_description,
            'context': context or {},
            'status': 'running'
        }
    
    def update_session(self, session_id: str, agent_results: Dict = None, 
                      files_created: List = None, context: Dict = None, 
                      status: str = None):
        """Update session with results and context"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if agent_results is not None:
                updates.append("agent_results = ?")
                params.append(json.dumps(agent_results))
            
            if files_created is not None:
                updates.append("files_created = ?")
                params.append(json.dumps(files_created))
            
            if context is not None:
                updates.append("context = ?")
                params.append(json.dumps(context))
            
            if status:
                updates.append("status = ?")
                params.append(status)
                if status == 'completed':
                    updates.append("completed_at = CURRENT_TIMESTAMP")
            
            if updates:
                params.append(session_id)
                cursor.execute(f"""
                    UPDATE sessions SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
                conn.commit()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID with full context"""
        with self._get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, p.name as project_name, p.description as project_description
                FROM sessions s
                JOIN projects p ON s.project_id = p.id
                WHERE s.id = ?
            """, (session_id,))
            result = cursor.fetchone()
            if result:
                # Parse JSON fields
                for field in ['agent_results', 'files_created', 'context']:
                    if result.get(field):
                        try:
                            result[field] = json.loads(result[field])
                        except:
                            result[field] = {} if field != 'files_created' else []
            return result
    
    def get_project_sessions(self, project_id: str) -> List[Dict]:
        """Get all sessions for a project"""
        with self._get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE project_id = ? 
                ORDER BY started_at DESC
            """, (project_id,))
            results = cursor.fetchall()
            for result in results:
                # Parse JSON fields
                for field in ['agent_results', 'files_created', 'context']:
                    if result.get(field):
                        try:
                            result[field] = json.loads(result[field])
                        except:
                            result[field] = {} if field != 'files_created' else []
            return results
    
    def store_context(self, project_id: str, session_id: str, 
                     context_type: str, context_data: Dict):
        """Store context information for later retrieval"""
        context_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO context_history 
                (id, project_id, session_id, context_type, context_data)
                VALUES (?, ?, ?, ?, ?)
            """, (context_id, project_id, session_id, context_type, json.dumps(context_data)))
            conn.commit()
    
    def get_project_context(self, project_id: str, context_type: str = None) -> List[Dict]:
        """Get project context history"""
        with self._get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            if context_type:
                cursor.execute("""
                    SELECT * FROM context_history 
                    WHERE project_id = ? AND context_type = ?
                    ORDER BY created_at DESC
                """, (project_id, context_type))
            else:
                cursor.execute("""
                    SELECT * FROM context_history 
                    WHERE project_id = ?
                    ORDER BY created_at DESC
                """, (project_id,))
            results = cursor.fetchall()
            for result in results:
                if result.get('context_data'):
                    try:
                        result['context_data'] = json.loads(result['context_data'])
                    except:
                        result['context_data'] = {}
            return results
    
    def store_execution_result(self, session_id: str, code_snippet: str, 
                             output: str = None, error: str = None, success: bool = False):
        """Store code execution results"""
        result_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_results 
                (id, session_id, code_snippet, execution_output, execution_error, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (result_id, session_id, code_snippet, output, error, 1 if success else 0))
            conn.commit()
    
    def get_execution_history(self, session_id: str) -> List[Dict]:
        """Get execution history for a session"""
        with self._get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM execution_results 
                WHERE session_id = ?
                ORDER BY executed_at DESC
            """, (session_id,))
            results = cursor.fetchall()
            for result in results:
                # Convert SQLite integer back to boolean
                if 'success' in result:
                    result['success'] = bool(result['success'])
            return results
    
    def get_session_logs(self, session_id: str) -> List[Dict]:
        """Get all logs for a session"""
        # This is a placeholder for a real logging implementation
        # In a production system, this would query actual log entries from a logs table
        from datetime import datetime
        return [
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": f"Session {session_id} started"},
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": f"Agents executed for session {session_id}"},
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": f"Session {session_id} completed"}
        ]
