#!/usr/bin/env python3
"""
API-Only CLI for Autonomous AI Coding Agent System
Always uses the API server (embedded or external) for consistency
"""

import click
import os
import sys
import time
import subprocess
import signal
import atexit
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
import json

from cli.api_client import APIClient
from utils.funny_names import generate_funny_project_name
from utils.port_finder import get_next_available_port, is_port_available

console = Console()

# Global server process for cleanup
_server_process = None

def cleanup_server():
    """Clean up the embedded server on exit"""
    global _server_process
    if _server_process:
        console.print("[dim]Stopping embedded API server...[/dim]")
        _server_process.terminate()
        try:
            _server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _server_process.kill()

# Register cleanup
atexit.register(cleanup_server)

class EmbeddedAPIServer:
    """Manages embedded API server lifecycle"""
    
    def __init__(self, port: int = None, host: str = "127.0.0.1"):
        # Auto-detect available port if not specified
        if port is None or not is_port_available(port, host):
            self.port = get_next_available_port([port] if port else None)
            if port and not is_port_available(port, host):
                console.print(f"[yellow]Port {port} is not available, using port {self.port} instead[/yellow]")
        else:
            self.port = port
        
        self.host = host
        self.url = f"http://{host}:{self.port}"
        self.process = None
        self.client = APIClient(self.url)
        
    def is_running(self) -> bool:
        """Check if API server is running"""
        return self.client.health_check()
        
    def start(self, verbose: bool = False) -> bool:
        """Start the embedded API server"""
        global _server_process
        
        if self.is_running():
            console.print(f"[green]✓ API server already running at {self.url}[/green]")
            return True
            
        console.print(f"[yellow]Starting embedded API server on port {self.port}...[/yellow]")
        
        # Double-check port is available before starting
        if not is_port_available(self.port, self.host):
            console.print(f"[red]Port {self.port} is no longer available[/red]")
            # Try to find another port
            self.port = get_next_available_port()
            self.url = f"http://{self.host}:{self.port}"
            self.client = APIClient(self.url)
            console.print(f"[yellow]Using alternative port {self.port}[/yellow]")
        
        # Prepare environment
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        # Start the server
        try:
            if verbose:
                self.process = subprocess.Popen(
                    [sys.executable, "web_interface/app.py", "--port", str(self.port), "--host", self.host],
                    env=env
                )
            else:
                self.process = subprocess.Popen(
                    [sys.executable, "web_interface/app.py", "--port", str(self.port), "--host", self.host],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            _server_process = self.process
            
            # Wait for server to be ready
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Waiting for API server...", total=None)
                
                for i in range(30):  # 30 second timeout
                    if self.is_running():
                        progress.update(task, description="[green]✓ API server ready![/green]")
                        time.sleep(0.5)  # Brief pause for visual feedback
                        return True
                    time.sleep(1)
                    progress.update(task, description=f"Waiting for API server... ({i+1}s)")
            
            # If we get here, server didn't start
            console.print("[red]❌ API server failed to start[/red]")
            if self.process:
                self.process.terminate()
            return False
            
        except Exception as e:
            console.print(f"[red]❌ Failed to start API server: {e}[/red]")
            return False
            
    def stop(self):
        """Stop the embedded server"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

class APIExecutor:
    """Handles task execution through API with real-time monitoring"""
    
    def __init__(self, client: APIClient):
        self.client = client
        
    def create_project(self, task_description: str) -> Optional[Dict[str, Any]]:
        """Create a new project for the task"""
        project_name = generate_funny_project_name()
        
        console.print(f"[cyan]🎲 Creating project: {project_name}[/cyan]")
        
        result = self.client.create_project(
            name=project_name,
            description=f"CLI Task: {task_description[:200]}",
            metadata={
                "source": "cli",
                "api_mode": True,
                "auto_generated": True
            }
        )
        
        if result.get("success"):
            return result.get("project")
        else:
            console.print(f"[red]Failed to create project: {result.get('error')}[/red]")
            return None
            
    def execute_task(self, task_description: str, project_id: str = None, 
                    dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """Execute task through API with monitoring"""
        
        # Create project if not provided
        if not project_id:
            project = self.create_project(task_description)
            if not project:
                return {"success": False, "error": "Failed to create project"}
            project_id = project["id"]
            project_name = project["name"]
        else:
            # Get existing project
            project = self.client.get_project(project_id)
            if not project:
                return {"success": False, "error": f"Project {project_id} not found"}
            project_name = project["name"]
        
        # Display task info
        console.print("\n" + "="*60)
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Field", style="cyan")
        info_table.add_column("Value", style="white")
        info_table.add_row("📋 Task", task_description)
        info_table.add_row("🗂️ Project", project_name)
        info_table.add_row("🔍 Mode", "Dry Run (API)" if dry_run else "Full Execution (API)")
        info_table.add_row("🌐 Server", self.client.base_url)
        console.print(info_table)
        console.print("="*60 + "\n")
        
        # Execute through API
        console.print("[bold]Starting task execution through API...[/bold]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task_progress = progress.add_task("Executing task...", total=None)
            
            # Start execution
            result = self.client.execute_task(
                task_description=task_description,
                project_id=project_id,
                config={
                    "dry_run": dry_run,
                    "verbose": verbose
                }
            )
            
            if result.get("success"):
                progress.update(task_progress, description="[green]✅ Task completed![/green]")
            else:
                progress.update(task_progress, description="[red]❌ Task failed![/red]")
        
        return result
        
    def display_results(self, result: Dict[str, Any]):
        """Display execution results"""
        console.print("\n" + "="*60)
        
        if result.get("success"):
            console.print(Panel("[bold green]✅ Task Execution Complete[/bold green]", expand=False))
        else:
            console.print(Panel(f"[bold red]❌ Task Failed: {result.get('error', 'Unknown error')}[/bold red]", expand=False))
            return
        
        # Agent results summary
        if result.get("agent_results"):
            summary_table = Table(title="Agent Execution Summary")
            summary_table.add_column("Agent", style="cyan")
            summary_table.add_column("Status", style="magenta")
            summary_table.add_column("Output Preview", style="green", width=50)
            
            for agent_name, agent_result in result.get("agent_results", {}).items():
                status = "✅ Success" if agent_result.get("success") else "❌ Failed"
                output = agent_result.get("output", "No output")
                if len(output) > 100:
                    output = output[:97] + "..."
                summary_table.add_row(
                    agent_name.replace("_", " ").title(),
                    status,
                    output
                )
            
            console.print(summary_table)
        
        # Files created
        if result.get("files_created"):
            console.print("\n[bold blue]📁 Files Created:[/bold blue]")
            for file_path in result["files_created"]:
                console.print(f"  • {file_path}")
        
        # Session info
        if result.get("session_id"):
            console.print(f"\n[dim]Session ID: {result['session_id']}[/dim]")
            console.print(f"[dim]View in Web UI: {self.client.base_url}/project/{result.get('project_id')}[/dim]")

@click.command()
@click.argument('task_description', required=True)
@click.option('--api-url', '-a', help='External API server URL (default: embedded server)')
@click.option('--port', '-p', default=5001, help='Port for embedded server (default: 5001)')
@click.option('--dry-run', is_flag=True, help='Simulate execution without creating files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--save-logs', is_flag=True, help='Save detailed logs to file')
@click.option('--project', help='Use existing project ID')
@click.option('--no-embedded', is_flag=True, help='Don\'t start embedded server, fail if no external API')
@click.option('--keep-server', is_flag=True, help='Keep embedded server running after completion')
def main(task_description: str, api_url: str, port: int, dry_run: bool, 
         verbose: bool, save_logs: bool, project: str, no_embedded: bool, keep_server: bool):
    """
    Autonomous AI Coding Agent System - API Mode
    
    This CLI always uses the API server for consistency and centralization.
    By default, it starts an embedded server if none is specified.
    
    Examples:
        # Use embedded server (auto-starts)
        python main_api.py "Create a FastAPI TODO app"
        
        # Use external API server
        python main_api.py "Create a REST API" --api-url http://localhost:5001
        
        # Use specific port for embedded server
        python main_api.py "Build a web scraper" --port 8080
        
        # Dry run mode
        python main_api.py "Create an app" --dry-run
    """
    
    console.print(Panel.fit(
        "[bold blue]🤖 Autonomous AI Coding Agent System[/bold blue]\n"
        "[dim]API-Only Mode with Centralized Execution[/dim]",
        subtitle="Unified Architecture"
    ))
    
    # Determine API server
    if api_url:
        # Use external API
        console.print(f"[cyan]Using external API server: {api_url}[/cyan]")
        client = APIClient(api_url)
        
        if not client.health_check():
            console.print(f"[red]❌ Cannot connect to API server at {api_url}[/red]")
            console.print("[yellow]Hint: Make sure the server is running or omit --api-url to use embedded server[/yellow]")
            sys.exit(1)
    else:
        if no_embedded:
            # Must use external but none specified
            console.print("[red]❌ No API URL specified and embedded server disabled[/red]")
            sys.exit(1)
        
        # Start embedded server
        server = EmbeddedAPIServer(port=port)
        
        if not server.start(verbose=verbose):
            console.print("[red]❌ Failed to start embedded API server[/red]")
            console.print("[yellow]Hint: Check if port {port} is already in use[/yellow]")
            sys.exit(1)
        
        client = server.client
        
        if not keep_server:
            # Server will be stopped on exit via atexit
            console.print("[dim]Note: Embedded server will stop after task completion[/dim]")
        else:
            console.print(f"[dim]Note: Server will keep running at {server.url}[/dim]")
            global _server_process
            _server_process = None  # Don't cleanup if keeping
    
    # Setup logging if requested
    log_file = None
    if save_logs:
        from datetime import datetime
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"agent_run_{timestamp}.log"
        console.print(f"[cyan]📝 Saving logs to: {log_file}[/cyan]")
        
        # Configure file logging
        import logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Execute task
    try:
        executor = APIExecutor(client)
        
        result = executor.execute_task(
            task_description=task_description,
            project_id=project,
            dry_run=dry_run,
            verbose=verbose
        )
        
        executor.display_results(result)
        
        # Show how to access results
        if result.get("success"):
            console.print("\n" + "="*60)
            console.print("[bold green]✨ Success![/bold green] Your task has been completed.")
            
            if result.get("files_created") and not dry_run:
                console.print(f"\n📁 Files saved to: {result.get('output_dir', 'output/')}")
                console.print("View generated files with: ls -la output/")
            
            if result.get("project_id"):
                console.print(f"\n🌐 View in Web UI: {client.base_url}/project/{result['project_id']}")
            
            if log_file and log_file.exists():
                console.print(f"\n📝 Detailed logs saved to: {log_file}")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Task interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        if verbose:
            import traceback
            console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)

if __name__ == '__main__':
    main()
