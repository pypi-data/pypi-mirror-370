"""
Workflow State management for LangGraph
"""

from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict

class WorkflowState(TypedDict, total=False):
    """State object for the multi-agent workflow"""
    
    # Core task information
    task_description: str
    current_agent: str
    
    # Agent execution results
    agent_results: Dict[str, Any]
    
    # Shared context between agents
    context: Dict[str, Any]
    
    # Generated files
    files_created: List[str]
    
    # Workflow control
    iteration: int
    max_iterations: int
    
    # Human-in-the-loop support
    human_feedback: Dict[str, Any]
    awaiting_human_input: bool
    human_input_required: Optional[str]
    human_input_data: Optional[Dict[str, Any]]
    
    # Configuration
    enable_human_approval: bool
    approval_points: List[str]
    
    # Optional metadata
    metadata: Optional[Dict[str, Any]]
