#!/usr/bin/env python3
"""
Autocoder - Unified CLI for the AI Coding Agent System
A professional multi-agent development platform
"""

import click
import os
import sys
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
import json
import uuid

# Import system modules
from workflow.orchestrator import WorkflowOrchestrator
from utils.logger import setup_logger
from utils.config_loader import ConfigLoader
from utils.file_handler import FileHandler
from utils.funny_names import generate_funny_project_name
from memory.project_memory import ProjectMemory
from web_interface.export_manager import export_manager
from cli_websocket_client import CLIWebSocketClient
from utils.config_setup import InteractiveConfigSetup

console = Console()
# Set default logging to WARNING to avoid verbose output
logger = setup_logger(level="WARNING")


@click.group()
@click.version_option(version='2.0.6', prog_name='autocoder')
@click.pass_context
def cli(ctx):
    """
    Autocoder - AI-Powered Multi-Agent Development System
    
    A professional development platform that uses AI agents to write,
    test, and deploy code based on natural language descriptions.
    
    Examples:
    
        # Run a task with monitoring
        autocoder run "Create a REST API" --monitor
        
        # Monitor an existing session
        autocoder monitor abc123def
        
        # List all projects
        autocoder projects
        
        # Start the web interface
        autocoder web
    """
    # Store shared context
    ctx.ensure_object(dict)
    ctx.obj['console'] = console
    ctx.obj['logger'] = logger


@cli.command()
@click.argument('task_description')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--output-dir', '-o', default='output', help='Output directory for generated files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--debug', is_flag=True, help='Enable debug logging (shows all messages)')
@click.option('--dry-run', is_flag=True, help='Simulate execution without creating files')
@click.option('--project', '-p', default=None, help='Project ID or name to use')
@click.option('--monitor', '-m', is_flag=True, help='Enable real-time monitoring')
@click.option('--server-url', default='http://localhost:5001', help='Server URL for WebSocket')
@click.option('--test-code', is_flag=True, help='Test generated code in sandbox')
@click.option('--enable-git', is_flag=True, help='Enable Git integration')
@click.pass_context
def run(ctx, task_description, config, output_dir, verbose, debug, dry_run, project, 
        monitor, server_url, test_code, enable_git):
    """
    Run a new task using AI agents
    
    Examples:
    
        # Simple task
        autocoder run "Create a Python calculator"
        
        # With monitoring and Git
        autocoder run "Build a web API" --monitor --enable-git
        
        # Continue existing project
        autocoder run "Add authentication" --project my_project
    """
    console = ctx.obj['console']
    
    # Configure logging based on flags
    if debug:
        # Debug mode - show everything
        import logging
        logging.basicConfig(level=logging.DEBUG, force=True)
        logger.setLevel('DEBUG')
    elif verbose:
        # Verbose mode - show INFO and above
        logger.setLevel('INFO')
    # Otherwise keep default WARNING level
    
    console.print(Panel.fit(
        "[bold blue]🤖 Autocoder - AI Coding Agent System[/bold blue]",
        subtitle="Running Task"
    ))
    
    # Initialize project memory
    memory = ProjectMemory()
    
    try:
        # Load configuration
        config_loader = ConfigLoader(config)
        if not config_loader.load():
            # Check if config file exists
            config_path = Path(config)
            if not config_path.exists():
                console.print(f"[yellow]⚠️ Configuration file not found: {config}[/yellow]")
                console.print("[cyan]Let's create a configuration file with the minimum required settings.[/cyan]\n")
                
                # Run interactive setup
                setup = InteractiveConfigSetup(console)
                if setup.run(str(config_path)):
                    console.print(f"\n[green]✅ Configuration saved to {config_path}[/green]")
                    console.print("[cyan]Loading new configuration...[/cyan]\n")
                    
                    # Try loading again
                    config_loader = ConfigLoader(config)
                    if not config_loader.load():
                        console.print("[red]❌ Failed to load newly created configuration[/red]")
                        sys.exit(1)
                else:
                    console.print("[red]❌ Configuration setup cancelled[/red]")
                    sys.exit(1)
            else:
                console.print("[red]❌ Failed to load configuration - invalid format[/red]")
                sys.exit(1)
        
        # Setup output directory
        file_handler = FileHandler(output_dir)
        file_handler.setup_output_directory()
        
        # Handle project
        if project:
            project_data = memory.get_project(project)
            if not project_data:
                console.print(f"[red]❌ Project '{project}' not found[/red]")
                sys.exit(1)
            project_id = project_data['id']
            project_name = project_data['name']
        else:
            project_name = generate_funny_project_name()
            project_description = f"Task: {task_description[:100]}..."
            metadata = {
                "auto_generated": True,
                "enable_git": enable_git,
                "test_code": test_code,
                "cli_generated": True
            }
            project_data = memory.create_project(project_name, project_description, metadata)
            project_id = project_data['id']
            console.print(f"[bold cyan]📁 Created project: {project_name}[/bold cyan]")
        
        # Create session
        session = memory.create_session(project_id, task_description)
        session_id = session['id']
        console.print(f"[dim]Session ID: {session_id}[/dim]")
        
        # Start WebSocket monitoring if requested
        websocket_thread = None
        if monitor:
            console.print(f"[bold cyan]📡 Starting real-time monitoring...[/bold cyan]")
            websocket_thread = start_websocket_monitor(session_id, server_url)
        
        # Display task information
        console.print(f"\n[bold green]📋 Task:[/bold green] {task_description}")
        console.print(f"[bold cyan]🗂️ Project:[/bold cyan] {project_name}")
        console.print(f"[bold blue]📁 Output:[/bold blue] {output_dir}")
        
        # Initialize Git if enabled
        if enable_git:
            from git_integration.git_manager import GitManager
            git_repo_path = Path(output_dir) / f"project_{project_id}"
            git_manager = GitManager(str(git_repo_path))
            if git_manager.init_repository():
                console.print("[green]✓ Git repository initialized[/green]")
        
        # Initialize orchestrator with WebSocket support
        websocket_manager = None
        if monitor:
            try:
                from web_interface.websocket_manager import WebSocketManager
                websocket_manager = WebSocketManager()
            except Exception as e:
                console.print(f"[yellow]Warning: WebSocket monitoring limited: {e}[/yellow]")
        
        
        orchestrator = WorkflowOrchestrator(
            config=config_loader.config,
            output_dir=output_dir,
            dry_run=dry_run,
            websocket_manager=websocket_manager
        )
        
        # Set session for all agent emitters if they exist
        if monitor and websocket_manager and hasattr(orchestrator, 'agent_emitters'):
            for emitter in orchestrator.agent_emitters.values():
                emitter.set_session(session_id)
        
        # Execute workflow
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running agents...", total=None)
            result = orchestrator.execute_task(task_description, progress, task)
        
        # Update session with results
        memory.update_session(session_id, status='completed', agent_results=result)
        
        # Display results
        display_results(result)
        
        # Test code if requested
        if test_code and result.get('files_created'):
            console.print("\n[cyan]🧪 Testing generated code...[/cyan]")
            test_generated_code(result.get('files_created', []), session_id, memory)
        
        console.print(f"\n[green]✅ Task completed successfully![/green]")
        console.print(f"[dim]Session ID: {session_id}[/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Task interrupted[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Task failed: {e}")
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('session_id')
@click.option('--server-url', default='ws://localhost:5001', help='WebSocket server URL')
@click.option('--token', help='Authentication token')
@click.pass_context
def monitor(ctx, session_id, server_url, token):
    """
    Monitor an existing task session in real-time
    
    Examples:
    
        # Monitor a session
        autocoder monitor abc123def
        
        # Monitor on different server
        autocoder monitor abc123 --server-url ws://remote:5001
    """
    console = ctx.obj['console']
    
    console.print(Panel.fit(
        "[bold green]📡 Task Monitor[/bold green]",
        subtitle=f"Session: {session_id}"
    ))
    
    try:
        # Create and run WebSocket client
        client = CLIWebSocketClient(server_url=server_url, token=token)
        asyncio.run(client.run(session_id))
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--limit', default=10, help='Number of projects to display')
@click.option('--status', help='Filter by status (active/completed/failed)')
@click.pass_context
def projects(ctx, limit, status):
    """
    List all projects
    
    Examples:
    
        # List all projects
        autocoder projects
        
        # Show only active projects
        autocoder projects --status active
    """
    console = ctx.obj['console']
    memory = ProjectMemory()
    
    all_projects = memory.get_all_projects()
    
    # Filter by status if specified
    if status:
        all_projects = [p for p in all_projects if p.get('status') == status]
    
    if not all_projects:
        console.print("[yellow]No projects found[/yellow]")
        return
    
    # Create table
    table = Table(title="Projects")
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Name", style="green")
    table.add_column("Status", width=10)
    table.add_column("Sessions", justify="right", width=8)
    table.add_column("Created", style="dim")
    
    for project in all_projects[:limit]:
        # Get sessions count
        sessions = memory.get_project_sessions(project['id'])
        sessions_count = len(sessions)
        
        # Format created date
        created = project.get('created_at', '')
        if created:
            try:
                created_dt = datetime.fromisoformat(created)
                created = created_dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        # Status color
        status_val = project.get('status', 'unknown')
        if status_val == 'active':
            status_text = Text(status_val, style="green")
        elif status_val == 'completed':
            status_text = Text(status_val, style="blue")
        else:
            status_text = Text(status_val, style="yellow")
        
        table.add_row(
            project['id'][:12],
            project['name'],
            status_text,
            str(sessions_count),
            created
        )
    
    console.print(table)
    
    if len(all_projects) > limit:
        console.print(f"\n[dim]Showing {limit} of {len(all_projects)} projects[/dim]")


@cli.command()
@click.argument('project_id')
@click.option('--limit', default=10, help='Number of sessions to display')
@click.pass_context
def sessions(ctx, project_id, limit):
    """
    List sessions for a project
    
    Examples:
    
        # List project sessions
        autocoder sessions abc123
        
        # Show more sessions
        autocoder sessions abc123 --limit 20
    """
    console = ctx.obj['console']
    memory = ProjectMemory()
    
    project = memory.get_project(project_id)
    if not project:
        console.print(f"[red]Project {project_id} not found[/red]")
        sys.exit(1)
    
    sessions = memory.get_project_sessions(project_id)
    
    if not sessions:
        console.print(f"[yellow]No sessions found for project {project['name']}[/yellow]")
        return
    
    # Create table
    table = Table(title=f"Sessions for {project['name']}")
    table.add_column("Session ID", style="cyan", width=12)
    table.add_column("Task", style="green")
    table.add_column("Status", width=10)
    table.add_column("Files", justify="right", width=5)
    table.add_column("Started", style="dim")
    
    for session in sessions[:limit]:
        # Format started date
        started = session.get('started_at', '')
        if started:
            try:
                started_dt = datetime.fromisoformat(started)
                started = started_dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        # Status color
        status_val = session.get('status', 'unknown')
        if status_val == 'completed':
            status_text = Text(status_val, style="green")
        elif status_val == 'running':
            status_text = Text(status_val, style="yellow")
        else:
            status_text = Text(status_val, style="red")
        
        # Files count
        files_count = len(session.get('files_created', []))
        
        # Truncate task description
        task = session.get('task_description', '')[:50]
        if len(session.get('task_description', '')) > 50:
            task += "..."
        
        table.add_row(
            session['id'][:12],
            task,
            status_text,
            str(files_count),
            started
        )
    
    console.print(table)
    
    if len(sessions) > limit:
        console.print(f"\n[dim]Showing {limit} of {len(sessions)} sessions[/dim]")


@cli.command()
@click.argument('session_id')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'csv', 'html', 'markdown', 'zip']),
              default='json', help='Export format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def export(ctx, session_id, format, output):
    """
    Export session data and logs
    
    Examples:
    
        # Export as JSON
        autocoder export abc123 -f json -o report.json
        
        # Export as HTML report
        autocoder export abc123 -f html -o report.html
        
        # Export everything as ZIP
        autocoder export abc123 -f zip -o report.zip
    """
    console = ctx.obj['console']
    
    console.print(f"[cyan]Exporting session {session_id} as {format}...[/cyan]")
    
    try:
        # Export data
        data = export_manager.export_session_data(session_id, format)
        
        if not data:
            console.print(f"[red]Failed to export session {session_id}[/red]")
            sys.exit(1)
        
        # Determine output file
        if not output:
            ext_map = {
                'json': 'json',
                'csv': 'csv',
                'html': 'html',
                'markdown': 'md',
                'zip': 'zip'
            }
            output = f"session_{session_id[:8]}.{ext_map[format]}"
        
        # Write to file
        with open(output, 'wb') as f:
            f.write(data)
        
        console.print(f"[green]✓ Exported to {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Export failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--port', '-p', default=5001, help='Port to run server on')
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def web(ctx, port, host, debug):
    """
    Start the web interface server
    
    Examples:
    
        # Start on default port
        autocoder web
        
        # Start on custom port with debug
        autocoder web --port 8080 --debug
    """
    console = ctx.obj['console']
    
    console.print(Panel.fit(
        "[bold green]🌐 Starting Web Interface[/bold green]",
        subtitle=f"http://{host}:{port}"
    ))
    
    try:
        import uvicorn
        from web_interface.app import create_app
        
        app = create_app()
        
        console.print(f"[green]Server starting at http://{host}:{port}[/green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="debug" if debug else "info"
        )
        
    except ImportError:
        console.print("[red]Web interface dependencies not installed[/red]")
        console.print("Run: pip install uvicorn fastapi")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]Server error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--project-id', '-p', help='Analyze specific project')
@click.pass_context
def stats(ctx, project_id):
    """
    Show system statistics and analytics
    
    Examples:
    
        # System-wide stats
        autocoder stats
        
        # Project-specific stats
        autocoder stats --project-id abc123
    """
    console = ctx.obj['console']
    
    # Generate analytics report
    report = export_manager.generate_analytics_report(project_id)
    
    if not report:
        console.print("[yellow]No statistics available[/yellow]")
        return
    
    # Display summary
    summary = report.get('summary', {})
    console.print(Panel.fit(
        f"[bold]System Statistics[/bold]\n\n"
        f"Projects: {summary.get('total_projects', 0)}\n"
        f"Sessions: {summary.get('total_sessions', 0)}\n"
        f"Files Created: {summary.get('total_files_created', 0)}",
        title="📊 Overview"
    ))
    
    # Session stats
    session_stats = report.get('session_stats', {})
    if session_stats:
        table = Table(title="Session Status")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right")
        
        table.add_row("Completed", str(session_stats.get('completed', 0)))
        table.add_row("Failed", str(session_stats.get('failed', 0)))
        table.add_row("Running", str(session_stats.get('running', 0)))
        
        console.print(table)
    
    # Performance metrics
    perf = report.get('performance', {})
    if perf:
        console.print(f"\n[bold]Performance[/bold]")
        console.print(f"Average Duration: {perf.get('average_duration_seconds', 0):.1f}s")
        console.print(f"Success Rate: {perf.get('success_rate', 0):.1f}%")
    
    # Agent usage
    agents = report.get('agents', {})
    if agents:
        console.print(f"\n[bold]Agent Usage[/bold]")
        for agent, count in agents.items():
            console.print(f"  {agent}: {count} sessions")


# Helper functions

def start_websocket_monitor(session_id: str, server_url: str):
    """Start WebSocket monitoring in a separate thread"""
    def run_monitor():
        try:
            ws_url = server_url.replace('http://', 'ws://').replace('https://', 'wss://')
            client = CLIWebSocketClient(server_url=ws_url)
            asyncio.run(client.run(session_id))
        except Exception as e:
            console.print(f"[red]WebSocket monitoring error: {e}[/red]")
    
    thread = threading.Thread(target=run_monitor, daemon=True)
    thread.start()
    return thread


def display_results(result: dict):
    """Display execution results"""
    table = Table(title="Execution Summary")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="magenta")
    
    for agent_name, agent_result in result.get('agent_results', {}).items():
        status = "✅" if agent_result.get('success') else "❌"
        table.add_row(agent_name.replace('_', ' ').title(), status)
    
    console.print(table)
    
    # Files created
    files = result.get('files_created', [])
    if files:
        console.print(f"\n[bold]Files Created ({len(files)}):[/bold]")
        for file_path in files[:5]:  # Show first 5
            console.print(f"  📄 {file_path}")
        if len(files) > 5:
            console.print(f"  [dim]... and {len(files) - 5} more[/dim]")


def test_generated_code(files_created, session_id, memory):
    """Test generated code files"""
    from sandbox.executor import CodeExecutor
    
    with CodeExecutor() as executor:
        for file_path in files_created:
            if file_path.endswith('.py'):
                console.print(f"  Testing {file_path}...")
                with open(file_path, 'r') as f:
                    code = f.read()
                result = executor.execute_python(code)
                if result.success:
                    console.print(f"    [green]✓ Passed[/green]")
                else:
                    console.print(f"    [red]✗ Failed: {result.error}[/red]")


if __name__ == '__main__':
    cli()
