"""
Agent Event Emitter for real-time monitoring integration
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from enum import Enum

from utils.logger import setup_logger

logger = setup_logger()


class AgentStatus(Enum):
    """Agent status enum"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


class InteractionType(Enum):
    """Agent interaction types"""
    CALL = "call"
    RESPONSE = "response"
    DELEGATE = "delegate"
    REQUEST = "request"


class AgentEventEmitter:
    """Emits real-time events for agent activities and monitoring"""
    
    def __init__(self, websocket_manager=None):
        """
        Initialize the event emitter
        
        Args:
            websocket_manager: Instance of WebSocketManager for real-time updates
        """
        self.websocket_manager = websocket_manager
        self.session_id: Optional[str] = None
        self.agent_name: str = "unknown"
        self.agent_metrics: Dict[str, Any] = {
            "tasks_completed": 0,
            "files_processed": 0,
            "errors_count": 0,
            "start_time": None,
            "elapsed_time": 0
        }
        self.current_activity: Optional[str] = None
        self.current_progress: int = 0
        
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to the WebSocket manager
        
        Args:
            event_type: Type of event to emit
            data: Event data
        """
        if not self.websocket_manager or not self.session_id:
            logger.debug(f"Event not emitted (no websocket or session): {event_type}")
            return
        
        try:
            # Add timestamp if not present
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()
            
            # Route to appropriate WebSocket method based on event type
            if event_type == "agent_status":
                await self.websocket_manager.send_agent_status(
                    self.session_id,
                    data.get("agent", self.agent_name),
                    data.get("status", "idle"),
                    data.get("activity"),
                    data.get("progress", 0),
                    data.get("metrics")
                )
            elif event_type == "agent_interaction":
                await self.websocket_manager.send_agent_interaction(
                    self.session_id,
                    data.get("from_agent"),
                    data.get("to_agent"),
                    data.get("interaction_type"),
                    data.get("data")
                )
            elif event_type == "activity_log":
                await self.websocket_manager.send_activity_log(
                    self.session_id,
                    data.get("agent", self.agent_name),
                    data.get("activity"),
                    data.get("level", "info"),
                    data.get("details")
                )
            elif event_type == "console_output":
                await self.websocket_manager.send_console_output(
                    self.session_id,
                    data.get("agent", self.agent_name),
                    data.get("output"),
                    data.get("output_type", "stdout")
                )
            elif event_type == "file_created":
                await self.websocket_manager.send_file_created(
                    self.session_id,
                    data.get("agent", self.agent_name),
                    data.get("file_path"),
                    data.get("file_type"),
                    data.get("content_preview")
                )
            elif event_type == "error":
                await self.websocket_manager.send_error(
                    self.session_id,
                    data.get("agent", self.agent_name),
                    data.get("error_message"),
                    data.get("error_type"),
                    data.get("stack_trace")
                )
            elif event_type == "human_input_request":
                await self.websocket_manager.send_human_input_request(
                    self.session_id,
                    data.get("agent", self.agent_name),
                    data.get("prompt"),
                    data.get("input_type", "text"),
                    data.get("options")
                )
            elif event_type == "chat_message":
                await self.websocket_manager.send_chat_message(
                    self.session_id,
                    data.get("sender", self.agent_name),
                    data.get("message"),
                    data.get("sender_type", "agent")
                )
            else:
                # Generic event broadcast
                await self.websocket_manager.send_to_session(
                    self.session_id,
                    {"type": event_type, **data}
                )
                
        except Exception as e:
            logger.error(f"Error emitting event {event_type}: {e}")
    
    def set_session(self, session_id: str):
        """Set the current session ID"""
        self.session_id = session_id
        
    def set_agent_name(self, agent_name: str):
        """Set the agent name"""
        self.agent_name = agent_name
        
    async def start_task(self, activity: str, initial_progress: int = 0):
        """
        Emit task start event
        
        Args:
            activity: Description of the activity
            initial_progress: Initial progress percentage
        """
        self.current_activity = activity
        self.current_progress = initial_progress
        self.agent_metrics["start_time"] = datetime.now()
        
        await self.emit_event("agent_status", {
            "agent": self.agent_name,
            "status": AgentStatus.WORKING.value,
            "activity": activity,
            "progress": initial_progress,
            "metrics": self.agent_metrics
        })
        
        await self.emit_event("activity_log", {
            "agent": self.agent_name,
            "activity": f"Started: {activity}",
            "level": "info"
        })
    
    async def update_progress(self, progress: int, activity: Optional[str] = None):
        """
        Update task progress
        
        Args:
            progress: Progress percentage (0-100)
            activity: Optional updated activity description
        """
        self.current_progress = progress
        if activity:
            self.current_activity = activity
        
        # Update elapsed time
        if self.agent_metrics["start_time"]:
            elapsed = (datetime.now() - self.agent_metrics["start_time"]).total_seconds()
            self.agent_metrics["elapsed_time"] = elapsed
        
        await self.emit_event("agent_status", {
            "agent": self.agent_name,
            "status": AgentStatus.WORKING.value,
            "activity": self.current_activity,
            "progress": progress,
            "metrics": self.agent_metrics
        })
    
    async def complete_task(self, message: Optional[str] = None):
        """
        Emit task completion event
        
        Args:
            message: Optional completion message
        """
        self.agent_metrics["tasks_completed"] += 1
        
        await self.emit_event("agent_status", {
            "agent": self.agent_name,
            "status": AgentStatus.COMPLETED.value,
            "activity": message or "Task completed",
            "progress": 100,
            "metrics": self.agent_metrics
        })
        
        await self.emit_event("activity_log", {
            "agent": self.agent_name,
            "activity": message or "Task completed successfully",
            "level": "success"
        })
    
    async def report_error(self, error_message: str, error_type: Optional[str] = None,
                          stack_trace: Optional[str] = None):
        """
        Report an error
        
        Args:
            error_message: Error message
            error_type: Type of error
            stack_trace: Optional stack trace
        """
        self.agent_metrics["errors_count"] += 1
        
        await self.emit_event("agent_status", {
            "agent": self.agent_name,
            "status": AgentStatus.ERROR.value,
            "activity": f"Error: {error_message}",
            "progress": self.current_progress,
            "metrics": self.agent_metrics
        })
        
        await self.emit_event("error", {
            "agent": self.agent_name,
            "error_message": error_message,
            "error_type": error_type,
            "stack_trace": stack_trace
        })
    
    async def log_activity(self, activity: str, level: str = "info", details: Optional[Dict] = None):
        """
        Log an activity
        
        Args:
            activity: Activity description
            level: Log level (info, warning, error, success)
            details: Optional additional details
        """
        await self.emit_event("activity_log", {
            "agent": self.agent_name,
            "activity": activity,
            "level": level,
            "details": details or {}
        })
    
    async def log_console(self, output: str, output_type: str = "stdout"):
        """
        Log console output
        
        Args:
            output: Console output text
            output_type: Type of output (stdout, stderr)
        """
        await self.emit_event("console_output", {
            "agent": self.agent_name,
            "output": output,
            "output_type": output_type
        })
    
    async def file_created(self, file_path: str, file_type: Optional[str] = None,
                          content_preview: Optional[str] = None):
        """
        Notify about file creation
        
        Args:
            file_path: Path to the created file
            file_type: Type of file
            content_preview: Optional preview of file content
        """
        self.agent_metrics["files_processed"] += 1
        
        await self.emit_event("file_created", {
            "agent": self.agent_name,
            "file_path": file_path,
            "file_type": file_type,
            "content_preview": content_preview
        })
    
    async def interact_with_agent(self, target_agent: str, interaction_type: InteractionType,
                                  data: Optional[Any] = None):
        """
        Emit agent interaction event
        
        Args:
            target_agent: Name of the target agent
            interaction_type: Type of interaction
            data: Optional interaction data
        """
        await self.emit_event("agent_interaction", {
            "from_agent": self.agent_name,
            "to_agent": target_agent,
            "interaction_type": interaction_type.value,
            "data": data
        })
    
    async def request_human_input(self, prompt: str, input_type: str = "text",
                                  options: Optional[List[str]] = None) -> Optional[str]:
        """
        Request human input
        
        Args:
            prompt: Input prompt
            input_type: Type of input (text, choice, confirmation)
            options: Optional list of choices
            
        Returns:
            Human input response (if available)
        """
        await self.emit_event("human_input_request", {
            "agent": self.agent_name,
            "prompt": prompt,
            "input_type": input_type,
            "options": options
        })
        
        # TODO: Implement waiting for human response through WebSocket
        # This would require a response channel implementation
        return None
    
    async def send_chat_message(self, message: str):
        """
        Send a chat message
        
        Args:
            message: Chat message content
        """
        await self.emit_event("chat_message", {
            "sender": self.agent_name,
            "message": message,
            "sender_type": "agent"
        })
    
    async def set_waiting(self, waiting_for: str):
        """
        Set agent to waiting status
        
        Args:
            waiting_for: Description of what the agent is waiting for
        """
        await self.emit_event("agent_status", {
            "agent": self.agent_name,
            "status": AgentStatus.WAITING.value,
            "activity": f"Waiting for {waiting_for}",
            "progress": self.current_progress,
            "metrics": self.agent_metrics
        })
    
    async def set_idle(self):
        """Set agent to idle status"""
        await self.emit_event("agent_status", {
            "agent": self.agent_name,
            "status": AgentStatus.IDLE.value,
            "activity": "Idle",
            "progress": 0,
            "metrics": self.agent_metrics
        })


class AgentEventContext:
    """Context manager for agent events"""
    
    def __init__(self, emitter: AgentEventEmitter, activity: str, initial_progress: int = 0):
        self.emitter = emitter
        self.activity = activity
        self.initial_progress = initial_progress
        
    async def __aenter__(self):
        await self.emitter.start_task(self.activity, self.initial_progress)
        return self.emitter
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.emitter.report_error(str(exc_val), exc_type.__name__)
        else:
            await self.emitter.complete_task()
        return False
