"""
WebSocket handler for real-time communication with the web interface
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json
import threading
from datetime import datetime
from typing import Dict, Any

from memory.project_memory import ProjectMemory
from workflow.orchestrator import WorkflowOrchestrator
from utils.config_loader import ConfigLoader
from utils.file_handler import FileHandler
from utils.logger import setup_logger

logger = setup_logger()

class SocketIOHandler:
    """Handles WebSocket connections and real-time updates"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.memory = ProjectMemory()
        self.config_loader = ConfigLoader("config.yaml")
        self.config_loader.load()
        self.active_sessions = {}  # session_id -> room_id mapping
    
    def init_handlers(self):
        """Initialize WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client connected: {request.sid}")
            emit('status', {'message': 'Connected to AI Coding Agent System'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('join_session')
        def handle_join_session(data):
            session_id = data.get('session_id')
            if session_id:
                join_room(session_id)
                self.active_sessions[session_id] = request.sid
                logger.info(f"Client {request.sid} joined session {session_id}")
                emit('joined_session', {'session_id': session_id})
        
        @self.socketio.on('leave_session')
        def handle_leave_session(data):
            session_id = data.get('session_id')
            if session_id:
                leave_room(session_id)
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                logger.info(f"Client {request.sid} left session {session_id}")
                emit('left_session', {'session_id': session_id})
        
        @self.socketio.on('execute_task')
        def handle_execute_task(data):
            session_id = data.get('session_id')
            task_description = data.get('task_description')
            
            if not session_id or not task_description:
                emit('error', {'message': 'Session ID and task description required'})
                return
            
            # Start task execution in background thread
            thread = threading.Thread(
                target=self._execute_task_background,
                args=(session_id, task_description)
            )
            thread.daemon = True
            thread.start()
            
            emit('task_started', {'session_id': session_id})
        
        @self.socketio.on('get_session_status')
        def handle_get_session_status(data):
            session_id = data.get('session_id')
            if session_id:
                session = self.memory.get_session(session_id)
                if session:
                    emit('session_status', {
                        'session_id': session_id,
                        'status': session.get('status'),
                        'progress': self._calculate_progress(session)
                    })
        
        @self.socketio.on('cancel_task')
        def handle_cancel_task(data):
            session_id = data.get('session_id')
            # Implementation for canceling tasks
            emit('task_cancelled', {'session_id': session_id})
    
    def _execute_task_background(self, session_id: str, task_description: str):
        """Execute task in background thread with real-time updates"""
        try:
            session = self.memory.get_session(session_id)
            if not session:
                self._emit_to_session(session_id, 'error', {'message': 'Session not found'})
                return
            
            # Initialize file handler
            file_handler = FileHandler("output")
            file_handler.setup_output_directory()
            
            # Create workflow orchestrator
            orchestrator = WorkflowOrchestrator(
                config=self.config_loader.config,
                file_handler=file_handler,
                dry_run=False
            )
            
            # Set up progress callback
            def progress_callback(agent_name: str, status: str, message: str = ""):
                self._emit_to_session(session_id, 'agent_progress', {
                    'agent': agent_name,
                    'status': status,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
            
            orchestrator.set_progress_callback(progress_callback)
            
            # Update session status
            self.memory.update_session(session_id, status='running')
            self._emit_to_session(session_id, 'task_status', {'status': 'running'})
            
            # Execute workflow
            results = orchestrator.execute_workflow(task_description)
            
            # Update session with results
            self.memory.update_session(
                session_id,
                agent_results=results.get('agent_results', {}),
                files_created=results.get('files_created', []),
                status='completed'
            )
            
            # Emit completion
            self._emit_to_session(session_id, 'task_completed', {
                'results': results,
                'files_created': results.get('files_created', []),
                'success': results.get('success', False)
            })
            
        except Exception as e:
            logger.error(f"Error executing task for session {session_id}: {e}")
            self.memory.update_session(session_id, status='failed')
            self._emit_to_session(session_id, 'task_failed', {
                'error': str(e)
            })
    
    def _emit_to_session(self, session_id: str, event: str, data: Dict[str, Any]):
        """Emit event to specific session room"""
        self.socketio.emit(event, data, room=session_id)
    
    def _calculate_progress(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate session progress based on agent results"""
        agent_results = session.get('agent_results', {})
        
        total_agents = 6  # Number of agents in the system
        completed_agents = len([r for r in agent_results.values() if r.get('success')])
        
        return {
            'total_agents': total_agents,
            'completed_agents': completed_agents,
            'percentage': (completed_agents / total_agents) * 100 if total_agents > 0 else 0,
            'current_agent': session.get('current_agent', 'unknown')
        }
    
    def emit_system_status(self, status: Dict[str, Any]):
        """Emit system status to all connected clients"""
        self.socketio.emit('system_status', status)
    
    def emit_agent_update(self, agent_name: str, status: str, message: str = ""):
        """Emit agent status update to all connected clients"""
        self.socketio.emit('agent_update', {
            'agent': agent_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })