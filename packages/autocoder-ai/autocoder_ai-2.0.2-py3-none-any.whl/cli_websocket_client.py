#!/usr/bin/env python3
"""
CLI WebSocket Client for real-time task monitoring
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import websockets
import argparse
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
import aiohttp

console = Console()


class CLIWebSocketClient:
    """WebSocket client for CLI real-time monitoring"""
    
    def __init__(self, server_url: str = "ws://localhost:5001", token: Optional[str] = None):
        """
        Initialize the CLI WebSocket client
        
        Args:
            server_url: WebSocket server URL
            token: Optional authentication token
        """
        self.server_url = server_url.replace("http://", "ws://").replace("https://", "wss://")
        self.token = token
        self.websocket = None
        self.session_id = None
        self.connected = False
        
        # Agent states
        self.agents = {}
        self.activity_log = []
        self.console_output = []
        self.files_created = []
        self.chat_messages = []
        
        # UI components
        self.layout = Layout()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )
    
    async def get_auth_token(self) -> str:
        """Get authentication token from server"""
        try:
            # Request token from server
            api_url = self.server_url.replace("ws://", "http://").replace("wss://", "https://")
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{api_url}/api/auth/token", 
                                       json={"client_type": "cli"}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("token")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not get auth token: {e}[/yellow]")
        return None
    
    async def connect(self, session_id: str):
        """Connect to WebSocket server"""
        self.session_id = session_id
        
        # Get auth token if not provided
        if not self.token:
            self.token = await self.get_auth_token()
        
        # Build WebSocket URL
        ws_url = f"{self.server_url}/ws/task/{session_id}"
        if self.token:
            ws_url += f"?token={self.token}"
        
        try:
            console.print(f"[cyan]Connecting to {ws_url}...[/cyan]")
            self.websocket = await websockets.connect(ws_url)
            self.connected = True
            console.print("[green]✓ Connected to task monitoring[/green]")
            
            # Send join message
            await self.send_message({
                "type": "join_session",
                "session_id": session_id
            })
            
        except Exception as e:
            console.print(f"[red]Failed to connect: {e}[/red]")
            raise
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            console.print("[yellow]Disconnected from server[/yellow]")
    
    async def send_message(self, message: Dict[str, Any]):
        """Send message to server"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
    
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        msg_type = message.get("type")
        
        if msg_type == "agent_status":
            self.update_agent_status(message)
        elif msg_type == "activity_log":
            self.add_activity_log(message)
        elif msg_type == "console_output":
            self.add_console_output(message)
        elif msg_type == "file_created":
            self.add_file_created(message)
        elif msg_type == "agent_interaction":
            self.handle_agent_interaction(message)
        elif msg_type == "chat_message":
            self.add_chat_message(message)
        elif msg_type == "task_completed":
            self.handle_task_completed(message)
        elif msg_type == "task_failed":
            self.handle_task_failed(message)
        elif msg_type == "human_input_request":
            await self.handle_human_input_request(message)
    
    def update_agent_status(self, message: Dict[str, Any]):
        """Update agent status"""
        agent = message.get("agent", "unknown")
        self.agents[agent] = {
            "status": message.get("status", "idle"),
            "activity": message.get("activity", ""),
            "progress": message.get("progress", 0),
            "metrics": message.get("metrics", {})
        }
    
    def add_activity_log(self, message: Dict[str, Any]):
        """Add activity to log"""
        self.activity_log.append({
            "timestamp": message.get("timestamp", datetime.now().isoformat()),
            "agent": message.get("agent", "unknown"),
            "activity": message.get("activity", ""),
            "level": message.get("level", "info")
        })
        # Keep only last 50 entries
        if len(self.activity_log) > 50:
            self.activity_log = self.activity_log[-50:]
    
    def add_console_output(self, message: Dict[str, Any]):
        """Add console output"""
        self.console_output.append({
            "agent": message.get("agent", "unknown"),
            "output": message.get("output", ""),
            "type": message.get("output_type", "stdout")
        })
        # Keep only last 100 lines
        if len(self.console_output) > 100:
            self.console_output = self.console_output[-100:]
    
    def add_file_created(self, message: Dict[str, Any]):
        """Add file to created list"""
        self.files_created.append({
            "agent": message.get("agent", "unknown"),
            "file_path": message.get("file_path", ""),
            "file_type": message.get("file_type", "unknown")
        })
    
    def add_chat_message(self, message: Dict[str, Any]):
        """Add chat message"""
        self.chat_messages.append({
            "sender": message.get("sender", "unknown"),
            "message": message.get("message", ""),
            "sender_type": message.get("sender_type", "agent"),
            "timestamp": message.get("timestamp", datetime.now().isoformat())
        })
    
    def handle_agent_interaction(self, message: Dict[str, Any]):
        """Handle agent interaction"""
        self.add_activity_log({
            "agent": message.get("from_agent", "unknown"),
            "activity": f"→ {message.get('to_agent', 'unknown')}: {message.get('interaction_type', '')}",
            "level": "info"
        })
    
    def handle_task_completed(self, message: Dict[str, Any]):
        """Handle task completion"""
        console.print("\n[green bold]✅ Task Completed Successfully![/green bold]")
        if message.get("files_created"):
            console.print(f"[cyan]Files created: {len(message['files_created'])}[/cyan]")
    
    def handle_task_failed(self, message: Dict[str, Any]):
        """Handle task failure"""
        console.print(f"\n[red bold]❌ Task Failed: {message.get('error', 'Unknown error')}[/red bold]")
    
    async def handle_human_input_request(self, message: Dict[str, Any]):
        """Handle human input request"""
        agent = message.get("agent", "unknown")
        prompt = message.get("prompt", "Input required")
        input_type = message.get("input_type", "text")
        options = message.get("options", [])
        
        console.print(f"\n[yellow]⚠️ {agent} requests input:[/yellow]")
        console.print(f"[cyan]{prompt}[/cyan]")
        
        if input_type == "choice" and options:
            for i, option in enumerate(options, 1):
                console.print(f"  {i}. {option}")
            response = console.input("[yellow]Enter choice number: [/yellow]")
            try:
                choice_idx = int(response) - 1
                if 0 <= choice_idx < len(options):
                    response = options[choice_idx]
            except:
                pass
        else:
            response = console.input("[yellow]Your response: [/yellow]")
        
        # Send response back
        await self.send_message({
            "type": "human_response",
            "message": response
        })
    
    def create_display(self) -> Table:
        """Create display table for agents"""
        table = Table(title=f"Task Monitor - Session: {self.session_id}")
        table.add_column("Agent", style="cyan", width=15)
        table.add_column("Status", width=10)
        table.add_column("Activity", width=40)
        table.add_column("Progress", width=20)
        
        for agent_name, agent_data in self.agents.items():
            status = agent_data["status"]
            
            # Color code status
            if status == "working":
                status_text = Text(status, style="yellow")
            elif status == "completed":
                status_text = Text(status, style="green")
            elif status == "error":
                status_text = Text(status, style="red")
            elif status == "waiting":
                status_text = Text(status, style="cyan")
            else:
                status_text = Text(status, style="dim")
            
            # Progress bar
            progress = agent_data["progress"]
            progress_bar = f"[{'=' * (progress // 5)}{' ' * (20 - progress // 5)}] {progress}%"
            
            table.add_row(
                agent_name.replace("_", " ").title(),
                status_text,
                agent_data["activity"][:40],
                progress_bar
            )
        
        return table
    
    def create_activity_panel(self) -> Panel:
        """Create activity log panel"""
        activities = []
        for log in self.activity_log[-10:]:  # Show last 10 activities
            timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
            level = log["level"]
            
            # Color code by level
            if level == "error":
                style = "red"
            elif level == "warning":
                style = "yellow"
            elif level == "success":
                style = "green"
            else:
                style = "white"
            
            activities.append(f"[dim]{timestamp}[/dim] [{style}]{log['agent']}[/{style}]: {log['activity']}")
        
        content = "\n".join(activities) if activities else "[dim]No activity yet[/dim]"
        return Panel(content, title="Activity Log", border_style="blue")
    
    def create_files_panel(self) -> Panel:
        """Create files created panel"""
        files = []
        for file in self.files_created[-10:]:  # Show last 10 files
            files.append(f"[cyan]{file['agent']}[/cyan]: {file['file_path']}")
        
        content = "\n".join(files) if files else "[dim]No files created yet[/dim]"
        return Panel(content, title=f"Files Created ({len(self.files_created)})", border_style="green")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        try:
            with Live(console=console, refresh_per_second=2) as live:
                while self.connected:
                    try:
                        # Receive message
                        message_str = await asyncio.wait_for(
                            self.websocket.recv(), 
                            timeout=0.1
                        )
                        message = json.loads(message_str)
                        await self.handle_message(message)
                        
                    except asyncio.TimeoutError:
                        pass  # No message, continue
                    except websockets.exceptions.ConnectionClosed:
                        console.print("[red]Connection closed by server[/red]")
                        self.connected = False
                        break
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                    
                    # Update display
                    display_table = self.create_display()
                    activity_panel = self.create_activity_panel()
                    files_panel = self.create_files_panel()
                    
                    # Create layout
                    layout = Layout()
                    layout.split_column(
                        Layout(display_table, size=len(self.agents) + 4),
                        Layout(activity_panel, size=12),
                        Layout(files_panel, size=12)
                    )
                    
                    live.update(layout)
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring interrupted[/yellow]")
        finally:
            await self.disconnect()
    
    async def run(self, session_id: str):
        """Run the WebSocket client"""
        await self.connect(session_id)
        await self.monitor_loop()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="CLI WebSocket Client for Task Monitoring")
    parser.add_argument("session_id", help="Session ID to monitor")
    parser.add_argument("--server", default="ws://localhost:5001", 
                       help="WebSocket server URL (default: ws://localhost:5001)")
    parser.add_argument("--token", help="Authentication token")
    
    args = parser.parse_args()
    
    client = CLIWebSocketClient(server_url=args.server, token=args.token)
    
    try:
        await client.run(args.session_id)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
