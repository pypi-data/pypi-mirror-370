#!/usr/bin/env python3
"""
CLI-based Autonomous AI Coding Agent System
Main entry point for the multi-agent coding system
"""

import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import asyncio
import threading

from workflow.orchestrator import WorkflowOrchestrator
from utils.logger import setup_logger
from utils.config_loader import ConfigLoader
from utils.file_handler import FileHandler
from utils.funny_names import generate_funny_project_name
from memory.project_memory import ProjectMemory

console = Console()
logger = setup_logger()

def start_websocket_monitor(session_id: str, server_url: str):
    """Start WebSocket monitoring in a separate thread"""
    def run_monitor():
        try:
            from cli_websocket_client import CLIWebSocketClient
            
            # Convert HTTP URL to WebSocket URL
            ws_url = server_url.replace('http://', 'ws://').replace('https://', 'wss://')
            
            # Create and run the WebSocket client
            client = CLIWebSocketClient(server_url=ws_url)
            
            # Run the async monitor
            asyncio.run(client.run(session_id))
            
        except Exception as e:
            console.print(f"[red]WebSocket monitoring error: {e}[/red]")
    
    # Start monitoring in a separate thread
    thread = threading.Thread(target=run_monitor, daemon=True)
    thread.start()
    return thread

@click.command()
@click.argument('task_description', required=True)
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--output-dir', '-o', default='output', help='Output directory for generated files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--dry-run', is_flag=True, help='Simulate execution without making actual changes')
@click.option('--project', '-p', default=None, help='Project ID or name to use for the task')
@click.option('--monitor', '-m', is_flag=True, help='Enable real-time WebSocket monitoring')
@click.option('--server-url', default='http://localhost:5001', help='Server URL for WebSocket monitoring')
def main(task_description: str, config: str, output_dir: str, verbose: bool, dry_run: bool, project: str, monitor: bool, server_url: str):
    """
    Autonomous AI Coding Agent System
    
    Describe your coding task in natural language and let the AI agents handle it.
    
    Example:
        python main.py "Create a Flask web application with user authentication and a dashboard"
    """
    
    # Setup
    if verbose:
        logger.setLevel('DEBUG')
    
    console.print(Panel.fit(
        "[bold blue]🤖 Autonomous AI Coding Agent System[/bold blue]",
        subtitle="Multi-Agent Development Team"
    ))
    
    # Initialize project memory
    memory = ProjectMemory()
    
    try:
        # Load configuration
        config_loader = ConfigLoader(config)
        if not config_loader.load():
            console.print("[red]❌ Failed to load configuration[/red]")
            sys.exit(1)
        
        # Setup output directory
        file_handler = FileHandler(output_dir)
        file_handler.setup_output_directory()
        
        # Handle project creation or selection
        if project:
            # Use existing project
            project_data = memory.get_project(project)
            if not project_data:
                console.print(f"[red]❌ Project '{project}' not found[/red]")
                sys.exit(1)
            project_id = project_data['id']
            project_name = project_data['name']
        else:
            # Create a new project with a funny name
            project_name = generate_funny_project_name()
            project_description = f"CLI task: {task_description[:100]}..."
            metadata = {
                "auto_generated": True,
                "enable_git": False,
                "create_readme": False,
                "cli_generated": True
            }
            project_id = memory.create_project(project_name, project_description, metadata)
            console.print(f"[bold cyan]🎲 Created project: {project_name}[/bold cyan]")
        
        # Create a session for this task
        session_id = memory.create_session(project_id, task_description)
    
        # Start WebSocket monitoring if requested
        websocket_thread = None
        if monitor:
            console.print(f"[bold cyan]📡 Starting real-time monitoring...[/bold cyan]")
            websocket_thread = start_websocket_monitor(session_id, server_url)
        
        # Display task information
        console.print(f"\n[bold green]📋 Task:[/bold green] {task_description}")
        console.print(f"[bold cyan]🗂️ Project:[/bold cyan] {project_name}")
        console.print(f"[bold blue]📁 Output Directory:[/bold blue] {output_dir}")
        if dry_run:
            console.print("[bold yellow]🔍 Dry Run Mode - No files will be created[/bold yellow]")
        
        # Initialize workflow orchestrator with WebSocket support
        websocket_manager = None
        if monitor:
            try:
                from web_interface.websocket_manager import WebSocketManager
                websocket_manager = WebSocketManager()
            except Exception as e:
                console.print(f"[yellow]Warning: Could not initialize WebSocket manager: {e}[/yellow]")
        
        orchestrator = WorkflowOrchestrator(
            config=config_loader.config,
            output_dir=output_dir,
            dry_run=dry_run,
            websocket_manager=websocket_manager
        )
        
        # Set session ID for all agent emitters
        if websocket_manager:
            for emitter in orchestrator.agent_emitters.values():
                emitter.set_session(session_id)
        
        # Execute the workflow
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing agents...", total=None)
            
            # Run the multi-agent workflow
            result = orchestrator.execute_task(task_description, progress, task)
        
        # Display results
        display_results(result, file_handler)
        
        # Stop WebSocket monitoring if it was started
        if websocket_thread:
            console.print("\n[yellow]Press Ctrl+C to stop monitoring...[/yellow]")
            try:
                websocket_thread.join(timeout=2)
            except:
                pass
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Task interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)

def display_results(result: dict, file_handler: FileHandler):
    """Display the execution results in a formatted table"""
    
    console.print("\n" + "="*60)
    console.print("[bold green]✅ Task Execution Complete[/bold green]")
    
    # Summary table
    table = Table(title="Execution Summary")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Output", style="green")
    
    for agent_name, agent_result in result.get('agent_results', {}).items():
        status = "✅ Success" if agent_result.get('success') else "❌ Failed"
        output = agent_result.get('output', 'No output')[:50] + "..." if len(agent_result.get('output', '')) > 50 else agent_result.get('output', 'No output')
        table.add_row(agent_name, status, output)
    
    console.print(table)
    
    # Files created
    if result.get('files_created'):
        console.print("\n[bold blue]📁 Files Created:[/bold blue]")
        for file_path in result.get('files_created', []):
            console.print(f"  • {file_path}")
    
    # Final recommendations
    if result.get('recommendations'):
        console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]")
        for rec in result.get('recommendations', []):
            console.print(f"  • {rec}")

if __name__ == '__main__':
    main()
