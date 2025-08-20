"""
FastAPI web application for the AI Coding Agent System
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json

from web_interface.fastapi_routes import router as api_router
from web_interface.websocket_manager import WebSocketManager

def create_app():
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="AI Coding Agent System API",
        description="Multi-Agent Development Platform with FastAPI",
        version="2.0.0"
    )
    
    # Static files
    app.mount("/static", StaticFiles(directory="web_interface/static"), name="static")
    
    # Templates
    templates = Jinja2Templates(directory="web_interface/templates")
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    # Initialize WebSocket manager
    websocket_manager = WebSocketManager()
    app.state.websocket_manager = websocket_manager
    
    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Main web interface"""
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/project/{project_id}", response_class=HTMLResponse)
    async def project_view(request: Request, project_id: str):
        """Project details view"""
        # Get project data from memory
        from memory.project_memory import ProjectMemory
        memory = ProjectMemory()
        project = memory.get_project(project_id)
        
        if not project:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Project not found",
                "message": f"The project with ID {project_id} was not found."
            }, status_code=404)
        
        # Parse metadata if it's a JSON string
        if project.get('metadata') and isinstance(project['metadata'], str):
            try:
                project['metadata'] = json.loads(project['metadata'])
            except:
                project['metadata'] = {}
        
        return templates.TemplateResponse("project_detail.html", {
            "request": request,
            "project": project
        })
    
    @app.get("/projects", response_class=HTMLResponse)
    async def projects_list(request: Request):
        """Projects list view"""
        return templates.TemplateResponse("projects.html", {"request": request})
    
    @app.get("/new-project", response_class=HTMLResponse)
    async def new_project(request: Request):
        """New project creation view"""
        return templates.TemplateResponse("new_project.html", {"request": request})
    
    @app.get("/task/{session_id}", response_class=HTMLResponse)
    async def task_monitor(request: Request, session_id: str):
        """Task monitoring page for real-time task execution tracking"""
        from memory.project_memory import ProjectMemory
        memory = ProjectMemory()
        
        # Get session data
        session = memory.get_session(session_id)
        if not session:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Session not found",
                "message": f"The session with ID {session_id} was not found."
            }, status_code=404)
        
        # Get project ID from session
        project_id = session.get('project_id')
        
        return templates.TemplateResponse("task_detail.html", {
            "request": request,
            "session": session,
            "project_id": project_id
        })
    
    @app.websocket("/socket.io/")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates"""
        await websocket_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                await websocket_manager.handle_message(websocket, message)
        except WebSocketDisconnect:
            await websocket_manager.disconnect(websocket)
    
    @app.websocket("/ws/task/{session_id}")
    async def task_websocket(websocket: WebSocket, session_id: str):
        """WebSocket endpoint for task monitoring real-time updates"""
        await websocket.accept()
        
        # Add websocket to session room
        await websocket_manager.join_session(websocket, session_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle task-specific messages
                if message.get('type') == 'join_session':
                    # Already joined above
                    await websocket.send_text(json.dumps({
                        'type': 'session_joined',
                        'payload': {'session_id': session_id}
                    }))
                elif message.get('type') == 'chat_message':
                    # Broadcast chat message to session room
                    await websocket_manager.broadcast_to_session(
                        session_id,
                        {
                            'type': 'chat_message',
                            'payload': {
                                'type': 'human',
                                'message': message.get('message'),
                                'timestamp': message.get('timestamp')
                            }
                        }
                    )
                elif message.get('type') == 'human_response':
                    # Handle human input response for agents
                    await websocket_manager.handle_human_response(
                        session_id,
                        message.get('message')
                    )
                elif message.get('type') == 'cancel_task':
                    # Cancel task execution
                    await websocket_manager.cancel_task(session_id)
                    
        except WebSocketDisconnect:
            await websocket_manager.leave_session(websocket, session_id)
    
    @app.exception_handler(404)
    async def not_found(request: Request, exc: HTTPException):
        return templates.TemplateResponse("error.html", 
            {"request": request, "error": "Page not found"}, status_code=404)
    
    @app.exception_handler(500)
    async def internal_error(request: Request, exc: HTTPException):
        return templates.TemplateResponse("error.html", 
            {"request": request, "error": "Internal server error"}, status_code=500)
    
    return app

if __name__ == '__main__':
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description='FastAPI server for AI Coding Agent System')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind to')
    args = parser.parse_args()
    
    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)
