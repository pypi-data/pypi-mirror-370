"""
WebSocket manager for real-time communication with FastAPI
"""

from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import threading

from memory.project_memory import ProjectMemory
from workflow.orchestrator import WorkflowOrchestrator
from utils.config_loader import ConfigLoader
from utils.file_handler import FileHandler
from utils.logger import setup_logger

logger = setup_logger()

class WebSocketManager:
    """Manages WebSocket connections and real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_connections: Dict[str, List[WebSocket]] = {}  # session_id -> [websockets]
        self.memory = ProjectMemory()
        self.config_loader = ConfigLoader("config.yaml")
        self.config_loader.load()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected: {id(websocket)}")
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "status",
            "message": "Connected to AI Coding Agent System"
        }, websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from session connections
        for session_id, connections in self.session_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                if not connections:  # Clean up empty session lists
                    del self.session_connections[session_id]
                break
        
        logger.info(f"Client disconnected: {id(websocket)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to websocket: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def send_to_session(self, session_id: str, message: Dict[str, Any]):
        """Send a message to all clients connected to a specific session"""
        if session_id not in self.session_connections:
            return
        
        disconnected = []
        for connection in self.session_connections[session_id]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to session {session_id}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.session_connections[session_id].remove(connection)
    
    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type == "join_session":
                await self._handle_join_session(websocket, data)
            elif message_type == "leave_session":
                await self._handle_leave_session(websocket, data)
            elif message_type == "execute_task":
                await self._handle_execute_task(websocket, data)
            elif message_type == "cancel_task":
                await self._handle_cancel_task(websocket, data)
            else:
                await self.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, websocket)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_personal_message({
                "type": "error",
                "message": "Error processing message"
            }, websocket)
    
    async def _handle_join_session(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle joining a session room"""
        session_id = data.get("session_id")
        if not session_id:
            await self.send_personal_message({
                "type": "error",
                "message": "Session ID required"
            }, websocket)
            return
        
        # Add to session connections
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        
        if websocket not in self.session_connections[session_id]:
            self.session_connections[session_id].append(websocket)
        
        logger.info(f"Client {id(websocket)} joined session {session_id}")
        await self.send_personal_message({
            "type": "joined_session",
            "session_id": session_id
        }, websocket)
    
    async def _handle_leave_session(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle leaving a session room"""
        session_id = data.get("session_id")
        if not session_id:
            return
        
        if session_id in self.session_connections and websocket in self.session_connections[session_id]:
            self.session_connections[session_id].remove(websocket)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        logger.info(f"Client {id(websocket)} left session {session_id}")
        await self.send_personal_message({
            "type": "left_session",
            "session_id": session_id
        }, websocket)
    
    async def _handle_execute_task(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle task execution request"""
        session_id = data.get("session_id")
        task_description = data.get("task_description")
        
        if not session_id or not task_description:
            await self.send_personal_message({
                "type": "error",
                "message": "Session ID and task description required"
            }, websocket)
            return
        
        # Send task started event
        await self.send_to_session(session_id, {
            "type": "task_started",
            "session_id": session_id,
            "task_description": task_description,
            "timestamp": datetime.now().isoformat()
        })
        
        # Start task execution in background
        asyncio.create_task(self._execute_task_background(session_id, task_description))
    
    async def _handle_cancel_task(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle task cancellation request"""
        session_id = data.get("session_id")
        if not session_id:
            return
        
        # Send cancellation event
        await self.send_to_session(session_id, {
            "type": "task_cancelled",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_agent_status(self, session_id: str, agent_name: str, status: str, 
                                activity: str = None, progress: int = 0, metrics: Dict = None):
        """Send agent status update to session clients"""
        message = {
            "type": "agent_status",
            "agent": agent_name,
            "status": status,  # 'idle', 'working', 'completed', 'error', 'waiting'
            "activity": activity,
            "progress": progress,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message)
    
    async def send_agent_interaction(self, session_id: str, from_agent: str, 
                                     to_agent: str, interaction_type: str, data: Any = None):
        """Send agent interaction event"""
        message = {
            "type": "agent_interaction",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "interaction_type": interaction_type,  # 'call', 'response', 'delegate', 'request'
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message)
    
    async def send_activity_log(self, session_id: str, agent: str, activity: str, 
                                level: str = "info", details: Dict = None):
        """Send activity log entry"""
        message = {
            "type": "activity_log",
            "agent": agent,
            "activity": activity,
            "level": level,  # 'info', 'warning', 'error', 'success'
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message)
    
    async def send_console_output(self, session_id: str, agent: str, output: str, 
                                  output_type: str = "stdout"):
        """Send console output from agent"""
        message = {
            "type": "console_output",
            "agent": agent,
            "output": output,
            "output_type": output_type,  # 'stdout', 'stderr'
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message)
    
    async def send_file_created(self, session_id: str, agent: str, file_path: str, 
                                file_type: str = None, content_preview: str = None):
        """Send file creation notification"""
        message = {
            "type": "file_created",
            "agent": agent,
            "file_path": file_path,
            "file_type": file_type,
            "content_preview": content_preview,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message)
    
    async def send_error(self, session_id: str, agent: str, error_message: str, 
                        error_type: str = None, stack_trace: str = None):
        """Send error notification"""
        message = {
            "type": "error",
            "agent": agent,
            "error_message": error_message,
            "error_type": error_type,
            "stack_trace": stack_trace,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message)
    
    async def send_human_input_request(self, session_id: str, agent: str, 
                                       prompt: str, input_type: str = "text",
                                       options: List[str] = None):
        """Request human input during task execution"""
        message = {
            "type": "human_input_request",
            "agent": agent,
            "prompt": prompt,
            "input_type": input_type,  # 'text', 'choice', 'confirmation'
            "options": options,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message)
    
    async def send_chat_message(self, session_id: str, sender: str, message: str, 
                                sender_type: str = "agent"):
        """Send chat message to session"""
        message_data = {
            "type": "chat_message",
            "sender": sender,
            "sender_type": sender_type,  # 'agent', 'human', 'system'
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_session(session_id, message_data)
    
    async def _execute_task_background(self, session_id: str, task_description: str):
        """Execute a task in the background and send progress updates"""
        try:
            # Initialize agents
            agents = ["planner", "developer", "tester", "ui_ux_expert", "db_expert", "devops_expert"]
            
            # Send initial status for all agents
            for agent in agents:
                await self.send_agent_status(session_id, agent, "idle", "Waiting to start")
            
            # Simulate planning phase
            await self.send_agent_status(session_id, "planner", "working", "Analyzing requirements", 20)
            await self.send_activity_log(session_id, "planner", "Started task analysis", "info")
            await asyncio.sleep(1)
            
            await self.send_agent_status(session_id, "planner", "working", "Creating task breakdown", 60)
            await self.send_console_output(session_id, "planner", "Breaking down task into subtasks...\n")
            await asyncio.sleep(1)
            
            # Planner delegates to developer
            await self.send_agent_interaction(session_id, "planner", "developer", "delegate", 
                                             {"task": "Implement core functionality"})
            await self.send_agent_status(session_id, "planner", "waiting", "Waiting for developer", 80)
            
            # Developer starts working
            await self.send_agent_status(session_id, "developer", "working", "Writing code", 10)
            await self.send_activity_log(session_id, "developer", "Started implementation", "info")
            await asyncio.sleep(1)
            
            # Developer creates a file
            await self.send_file_created(session_id, "developer", "src/main.py", "python", 
                                        "def main():\n    print('Hello World')")
            await self.send_agent_status(session_id, "developer", "working", "Implementing features", 50)
            await asyncio.sleep(1)
            
            # Developer requests DB expert help
            await self.send_agent_interaction(session_id, "developer", "db_expert", "request", 
                                             {"query": "Need database schema design"})
            
            # DB expert responds
            await self.send_agent_status(session_id, "db_expert", "working", "Designing schema", 30)
            await self.send_agent_interaction(session_id, "db_expert", "developer", "response", 
                                             {"schema": "CREATE TABLE users..."})
            await self.send_agent_status(session_id, "db_expert", "completed", "Schema provided", 100)
            
            # Developer continues
            await self.send_agent_status(session_id, "developer", "working", "Integrating database", 75)
            await asyncio.sleep(1)
            
            # Simulate human input request
            await self.send_human_input_request(session_id, "developer", 
                                               "Should we use PostgreSQL or MySQL?", 
                                               "choice", ["PostgreSQL", "MySQL"])
            await asyncio.sleep(2)  # Wait for response (simulated)
            
            # Developer completes
            await self.send_agent_status(session_id, "developer", "completed", "Code complete", 100)
            await self.send_agent_interaction(session_id, "developer", "tester", "call", 
                                             {"files": ["src/main.py"]})
            
            # Tester starts
            await self.send_agent_status(session_id, "tester", "working", "Running tests", 25)
            await self.send_console_output(session_id, "tester", 
                                          "Running test suite...\n✓ Test 1 passed\n✓ Test 2 passed\n")
            await asyncio.sleep(1)
            
            # UI/UX expert provides feedback
            await self.send_agent_status(session_id, "ui_ux_expert", "working", "Reviewing UI", 50)
            await self.send_activity_log(session_id, "ui_ux_expert", 
                                        "UI review completed - suggestions provided", "success")
            await self.send_agent_status(session_id, "ui_ux_expert", "completed", "Review done", 100)
            
            # DevOps prepares deployment
            await self.send_agent_status(session_id, "devops_expert", "working", "Preparing deployment", 40)
            await self.send_file_created(session_id, "devops_expert", "Dockerfile", "docker")
            await self.send_agent_status(session_id, "devops_expert", "completed", "Deployment ready", 100)
            
            # Tester completes
            await self.send_agent_status(session_id, "tester", "completed", "All tests passed", 100)
            
            # Planner finalizes
            await self.send_agent_status(session_id, "planner", "completed", "Task completed", 100)
            await self.send_activity_log(session_id, "planner", "Task completed successfully", "success")
            
            # Send task completion
            await self.send_to_session(session_id, {
                "type": "task_completed",
                "session_id": session_id,
                "success": True,
                "message": "Task completed successfully",
                "files_created": ["src/main.py", "Dockerfile"],
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in background task execution: {e}")
            await self.send_error(session_id, "system", str(e), "ExecutionError")
            await self.send_to_session(session_id, {
                "type": "task_failed",
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
