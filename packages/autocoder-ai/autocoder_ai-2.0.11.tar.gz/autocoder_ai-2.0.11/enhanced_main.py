#!/usr/bin/env python3
"""
Enhanced main entry point for the AI Coding Agent System
Includes memory persistence, code execution, and web interface
"""

import click
import asyncio
import uuid
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from utils.config_loader import ConfigLoader
from utils.file_handler import FileHandler
from utils.logger import setup_logger
from workflow.orchestrator import WorkflowOrchestrator
from memory.project_memory import ProjectMemory
from sandbox.executor import CodeExecutor
from git_integration.git_manager import GitManager
from cli.api_client import APIClient

console = Console()
logger = setup_logger()

@click.group()
def cli():
    """AI Coding Agent System - Enhanced Multi-Agent Development Platform"""
    pass

@cli.command()
@click.argument('task_description')
@click.option('--project-id', help='Existing project ID to continue work')
@click.option('--project-name', help='Name for new project')
@click.option('--output-dir', default='output', help='Output directory')
@click.option('--dry-run', is_flag=True, help='Run without creating files')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.option('--enable-git', is_flag=True, help='Enable Git integration')
@click.option('--test-code', is_flag=True, help='Test generated code in sandbox')
@click.option('--api-url', default='http://localhost:5000', help='API server URL')
@click.option('--config', help='Path to configuration file')
@click.option('--offline', is_flag=True, help='Use offline/local models (Ollama)')
def execute(task_description, project_id, project_name, output_dir, dry_run, verbose, enable_git, test_code, api_url, config, offline):
    """Execute a task using the enhanced AI agent system"""
    
    console.print(Panel.fit(
        "[bold blue]🤖 Enhanced AI Coding Agent System[/bold blue]",
        subtitle="Multi-Agent Development with Memory & Git"
    ))
    
    try:
        # Load custom configuration if provided
        if config:
            from utils.config_loader import ConfigLoader
            config_loader = ConfigLoader(config)
            if not config_loader.load():
                console.print(f"[red]Failed to load configuration from {config}[/red]")
                return
            console.print(f"[green]Loaded configuration from {config}[/green]")
        
        # Handle offline mode
        if offline:
            console.print("[yellow]Offline mode: Using local models (Ollama)[/yellow]")
            # In offline mode, use offline API client
            from cli.api_client import OfflineAPIClient
            api_client = OfflineAPIClient(config if config else "config.yaml")
        else:
            # Initialize API client
            api_client = APIClient(api_url)
            
            if not api_client.health_check():
                console.print(f"[red]API server not running at {api_url}[/red]")
                console.print("[yellow]Options:[/yellow]")
                console.print("1. Start server: python enhanced_main.py web")
                console.print("2. Use offline mode: --offline flag")
                console.print("3. Specify different server: --api-url <url>")
                return
        
        # Handle project creation or retrieval
        if project_id:
            project = api_client.get_project(project_id)
            if not project:
                console.print(f"[red]Project {project_id} not found[/red]")
                return
            console.print(f"[green]Continuing project: {project['name']}[/green]")
        else:
            project_name = project_name or f"Task: {task_description[:50]}..."
            project = api_client.create_project(
                name=project_name,
                description=task_description,
                metadata={'git_enabled': enable_git, 'sandbox_enabled': test_code}
            )
            project_id = project['id']
            console.print(f"[green]Created new project: {project_name}[/green]")
        
        # Create session
        session = api_client.create_session(
            project_id=project_id,
            task_description=task_description,
            context={'output_dir': output_dir, 'dry_run': dry_run}
        )
        session_id = session['id']
        console.print(f"[blue]Session ID: {session_id}[/blue]")
        
        # Initialize Git if enabled
        git_manager = None
        if enable_git:
            git_repo_path = Path(output_dir) / f"project_{project_id}"
            git_manager = GitManager(str(git_repo_path))
            if git_manager.init_repository():
                console.print("[green]Git repository initialized[/green]")
                git_manager.create_session_branch(session_id, task_description)
        
        # Initialize components
        config_loader = ConfigLoader("config.yaml")
        config_loader.load()
        
        file_handler = FileHandler(output_dir)
        file_handler.setup_output_directory()
        
        # Execute workflow
        orchestrator = WorkflowOrchestrator(
            config=config_loader.config,
            output_dir=output_dir,
            dry_run=dry_run
        )
        
        console.print("[yellow]Starting AI agent workflow...[/yellow]")
        results = orchestrator.execute_workflow(task_description)
        
        # Note: Session updates would be handled via API in a full implementation
        # For now, we rely on the workflow orchestrator's file outputs
        
        # Test generated code if enabled
        if test_code and results.get('files_created'):
            console.print("[cyan]Testing generated code...[/cyan]")
            test_results = test_generated_code(results.get('files_created', []), session_id, memory)
            display_test_results(test_results)
        
        # Commit to Git if enabled
        if git_manager and results.get('files_created'):
            files_to_commit = [str(Path(f).relative_to(git_repo_path)) for f in results.get('files_created', [])]
            if git_manager.create_agent_commit(
                agent_name="AI Coding Agents",
                task_description=task_description,
                files_created=files_to_commit
            ):
                console.print("[green]Changes committed to Git[/green]")
        
        # Display results
        display_execution_results(results, project, session_id)
        
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.option('--port', default=5000, help='Port to run web interface')
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def web(port, host, debug):
    """Start the FastAPI web interface"""
    import uvicorn
    from web_interface.app import create_app
    
    console.print(Panel.fit(
        "[bold green]🌐 Starting FastAPI Web Interface[/bold green]",
        subtitle=f"http://{host}:{port}"
    ))
    
    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="info" if debug else "warning")

@cli.command()
@click.option('--api-url', default='http://localhost:5000', help='API server URL')
def projects(api_url):
    """List all projects"""
    api_client = APIClient(api_url)
    
    if not api_client.health_check():
        console.print("[red]API server not running. Start it with: python enhanced_main.py web[/red]")
        return
    
    projects = api_client.list_projects()
    
    if not projects:
        console.print("[yellow]No projects found[/yellow]")
        return
    
    console.print("\n[bold]Projects:[/bold]")
    for project in projects:
        # Get sessions count from project data (if available)
        sessions_count = len(project.get('sessions', []))
        console.print(f"  • {project['name']} ({project['id'][:8]}...)")
        console.print(f"    Status: {project['status']}")
        console.print(f"    Sessions: {sessions_count}")
        console.print(f"    Created: {project['created_at']}")
        console.print()

@cli.command()
@click.argument('project_id')
@click.option('--api-url', default='http://localhost:5000', help='API server URL')
def project_info(project_id, api_url):
    """Show detailed information about a project"""
    api_client = APIClient(api_url)
    
    if not api_client.health_check():
        console.print("[red]API server not running. Start it with: python enhanced_main.py web[/red]")
        return
    
    project = api_client.get_project(project_id)
    
    if not project:
        console.print(f"[red]Project {project_id} not found[/red]")
        return
    
    sessions = project.get('sessions', [])
    
    console.print(f"\n[bold]Project: {project['name']}[/bold]")
    console.print(f"ID: {project['id']}")
    console.print(f"Description: {project['description']}")
    console.print(f"Status: {project['status']}")
    console.print(f"Created: {project['created_at']}")
    console.print(f"Updated: {project['updated_at']}")
    
    console.print(f"\n[bold]Sessions ({len(sessions)}):[/bold]")
    for session in sessions:
        console.print(f"  • Session {session['id'][:8]}...")
        console.print(f"    Task: {session['task_description'][:60]}...")
        console.print(f"    Status: {session['status']}")
        console.print(f"    Started: {session['started_at']}")
        if session['completed_at']:
            console.print(f"    Completed: {session['completed_at']}")
        console.print()

@cli.command()
@click.argument('code_file')
@click.option('--language', default='python', help='Programming language')
@click.option('--dependencies', help='Comma-separated list of dependencies')
def test_code(code_file, language, dependencies):
    """Test code file in sandbox"""
    
    if not Path(code_file).exists():
        console.print(f"[red]File {code_file} not found[/red]")
        return
    
    with open(code_file, 'r') as f:
        code_content = f.read()
    
    deps = dependencies.split(',') if dependencies else []
    
    console.print(f"[cyan]Testing {code_file} in sandbox...[/cyan]")
    
    with CodeExecutor() as executor:
        if language == 'python':
            result = executor.execute_python(code_content, deps)
        elif language == 'javascript':
            result = executor.execute_javascript(code_content, deps)
        else:
            console.print(f"[red]Unsupported language: {language}[/red]")
            return
        
        display_execution_result(result)

def test_generated_code(files_created, session_id, memory):
    """Test generated code files"""
    test_results = {}
    
    with CodeExecutor() as executor:
        # Group files by type
        python_files = [f for f in files_created if f.endswith('.py')]
        js_files = [f for f in files_created if f.endswith('.js')]
        
        # Test Python files
        for py_file in python_files:
            if Path(py_file).exists():
                with open(py_file, 'r') as f:
                    code = f.read()
                
                result = executor.execute_python(code)
                test_results[py_file] = result
                
                # Store execution result
                memory.store_execution_result(
                    session_id=session_id,
                    code_snippet=code[:500] + "..." if len(code) > 500 else code,
                    output=result.output,
                    error=result.error,
                    success=result.success
                )
        
        # Test JavaScript files
        for js_file in js_files:
            if Path(js_file).exists():
                with open(js_file, 'r') as f:
                    code = f.read()
                
                result = executor.execute_javascript(code)
                test_results[js_file] = result
                
                memory.store_execution_result(
                    session_id=session_id,
                    code_snippet=code[:500] + "..." if len(code) > 500 else code,
                    output=result.output,
                    error=result.error,
                    success=result.success
                )
    
    return test_results

def display_test_results(test_results):
    """Display code testing results"""
    console.print("\n[bold]Code Testing Results:[/bold]")
    
    for file_path, result in test_results.items():
        status = "✅" if result.success else "❌"
        console.print(f"{status} {file_path}")
        
        if result.output:
            console.print(f"  Output: {result.output[:200]}...")
        if result.error:
            console.print(f"  Error: {result.error[:200]}...")
        console.print(f"  Execution time: {result.execution_time:.2f}s")
        console.print()

def display_execution_result(result):
    """Display single execution result"""
    status = "✅ Success" if result.success else "❌ Failed"
    console.print(f"[bold]Result: {status}[/bold]")
    
    if result.output:
        console.print(f"[green]Output:[/green]\n{result.output}")
    
    if result.error:
        console.print(f"[red]Error:[/red]\n{result.error}")
    
    console.print(f"[blue]Execution time: {result.execution_time:.2f}s[/blue]")

def display_execution_results(results, project, session_id):
    """Display workflow execution results"""
    console.print("\n" + "="*60)
    if results.get('success'):
        console.print("[bold green]✅ Task Execution Complete[/bold green]")
    else:
        console.print("[bold red]❌ Task Execution Failed[/bold red]")
    
    console.print(f"Project: {project['name']}")
    console.print(f"Session: {session_id}")
    
    # Show agent results
    agent_results = results.get('agent_results', {})
    console.print(f"\n[bold]Agent Results:[/bold]")
    for agent_name, result in agent_results.items():
        status = "✅" if result.get('success') else "❌"
        console.print(f"  {status} {agent_name.replace('_', ' ').title()}")
    
    # Show generated files
    files_created = results.get('files_created', [])
    if files_created:
        console.print(f"\n[bold]Files Generated ({len(files_created)}):[/bold]")
        for file_path in files_created:
            console.print(f"  📄 {file_path}")
    
    # Show recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        console.print(f"\n[bold]Recommendations:[/bold]")
        for rec in recommendations:
            console.print(f"  • {rec}")

if __name__ == '__main__':
    cli()