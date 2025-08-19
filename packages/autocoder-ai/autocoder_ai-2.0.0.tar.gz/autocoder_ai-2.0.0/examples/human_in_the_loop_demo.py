#!/usr/bin/env python3
"""
Demo script showing Human-in-the-Loop functionality with LangGraph
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from workflow.orchestrator import WorkflowOrchestrator

console = Console()
logger = logging.getLogger(__name__)

def load_demo_config():
    """Load demo configuration"""
    config = {
        'agents': {
            'planner': {
                'model': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'max_tokens': 2048,
                    'temperature': 0
                },
                'description': 'Strategic planner for software development'
            },
            'developer': {
                'model': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'max_tokens': 2048,
                    'temperature': 0
                },
                'description': 'Core development agent'
            },
            'tester': {
                'model': {
                    'model': 'gpt-3.5-turbo',
                    'provider': 'openai',
                    'max_tokens': 2048,
                    'temperature': 0
                },
                'description': 'Quality assurance and testing'
            },
            'devops_expert': {
                'model': {
                    'model': 'gpt-3.5-turbo',
                    'provider': 'openai',
                    'max_tokens': 2048,
                    'temperature': 0
                },
                'description': 'Deployment and infrastructure'
            },
            'ui_ux_expert': {
                'model': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'max_tokens': 2048,
                    'temperature': 0
                },
                'description': 'User interface and experience design'
            },
            'db_expert': {
                'model': {
                    'model': 'gpt-4',
                    'provider': 'openai',
                    'max_tokens': 2048,
                    'temperature': 0
                },
                'description': 'Database design and optimization'
            }
        },
        'workflow': {
            'max_iterations': 5
        },
        'output': {
            'create_summary_report': True
        }
    }
    return config

def human_feedback_handler(review_data):
    """Handle human feedback requests"""
    console.print("\n" + "="*60, style="bold blue")
    console.print(f"🤔 {review_data['title']}", style="bold yellow")
    console.print("="*60, style="bold blue")
    
    # Display content
    console.print("\n📋 Content to Review:", style="bold")
    console.print(review_data.get('content', 'No content available'))
    
    # Display files if available
    if 'files' in review_data:
        console.print("\n📁 Files Generated:", style="bold")
        for file_info in review_data['files']:
            console.print(f"  - {file_info.get('filename', 'unknown')}")
    
    # Display test results if available
    if 'test_results' in review_data:
        console.print("\n🧪 Test Results:", style="bold")
        for test_info in review_data['test_results']:
            console.print(f"  - {test_info.get('filename', 'unknown')}")
    
    # Display summary if available
    if 'summary' in review_data:
        console.print("\n📊 Project Summary:", style="bold")
        summary = review_data['summary']
        console.print(f"  Plan: {summary.get('plan', 'N/A')[:100]}...")
        console.print(f"  Files Created: {summary.get('code_files', 0)}")
        console.print(f"  Agents Used: {', '.join(summary.get('agents_used', []))}")
    
    # Ask questions
    console.print("\n❓ Review Questions:", style="bold")
    for i, question in enumerate(review_data.get('questions', []), 1):
        console.print(f"  {i}. {question}")
    
    # Get user input
    console.print("\n⚡ Available Options:", style="bold green")
    options = review_data.get('options', ['approve', 'reject'])
    for i, option in enumerate(options, 1):
        console.print(f"  {i}. {option.replace('_', ' ').title()}")
    
    while True:
        try:
            choice = console.input(f"\n👉 Your choice (1-{len(options)}): ")
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(options):
                selected_option = options[choice_idx]
                console.print(f"✅ You selected: {selected_option.replace('_', ' ').title()}", style="bold green")
                
                # Get additional feedback if requesting changes
                feedback_comment = ""
                if "request" in selected_option or "changes" in selected_option:
                    feedback_comment = console.input("💬 Please provide specific feedback (optional): ")
                
                return {
                    "type": review_data["type"],
                    "decision": selected_option,
                    "comment": feedback_comment,
                    "timestamp": "2024-01-01T00:00:00Z"  # In real implementation, use actual timestamp
                }
            else:
                console.print("❌ Invalid choice. Please try again.", style="bold red")
        except ValueError:
            console.print("❌ Please enter a valid number.", style="bold red")
        except KeyboardInterrupt:
            console.print("\n\n🚫 Human-in-the-loop cancelled by user.", style="bold red")
            return {
                "type": review_data["type"],
                "decision": "reject",
                "comment": "Cancelled by user",
                "timestamp": "2024-01-01T00:00:00Z"
            }

def demo_human_in_the_loop():
    """Demonstrate human-in-the-loop functionality"""
    console.print("🚀 Human-in-the-Loop LangGraph Demo", style="bold blue")
    console.print("="*60, style="blue")
    
    # Check for API key
    if not os.environ.get('OPENAI_API_KEY'):
        console.print("❌ Please set OPENAI_API_KEY environment variable", style="bold red")
        console.print("For demo purposes, you can use a mock key:", style="yellow")
        console.print("export OPENAI_API_KEY='demo-key-for-testing'", style="green")
        return
    
    # Load configuration
    config = load_demo_config()
    output_dir = "demo_output_hitl"
    
    # Create orchestrator with human approval enabled
    console.print("🔧 Initializing workflow orchestrator with human-in-the-loop...", style="cyan")
    orchestrator = WorkflowOrchestrator(
        config=config,
        output_dir=output_dir,
        dry_run=True,  # Enable dry run for demo
        enable_human_approval=True
    )
    
    # Set human feedback callback
    orchestrator.set_human_feedback_callback(human_feedback_handler)
    
    # Demo task
    task = "Create a simple Python web API with user authentication and rate limiting"
    
    console.print(f"\n📝 Task: {task}", style="bold")
    console.print("\n🔄 This demo will pause at key points for your review:", style="yellow")
    console.print("  1. After planning phase", style="yellow")
    console.print("  2. After code generation", style="yellow") 
    console.print("  3. After testing phase", style="yellow")
    console.print("  4. Before final completion", style="yellow")
    
    # Execute with human approval
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task_id = progress.add_task("Starting human-in-the-loop workflow...", total=None)
        
        try:
            result = orchestrator.execute_with_human_approval(
                task_description=task,
                progress=progress,
                task_id=task_id,
                approval_points=["plan", "code", "tests", "final"]
            )
            
            # Display final results
            console.print("\n" + "="*60, style="bold green")
            console.print("🎉 Human-in-the-Loop Demo Complete!", style="bold green")
            console.print("="*60, style="bold green")
            
            if result['success']:
                console.print("✅ Workflow completed successfully!", style="bold green")
                console.print(f"📁 Files created: {len(result.get('files_created', []))}")
                console.print(f"🤖 Agents executed: {len(result.get('agent_results', {}))}")
                
                # Show human feedback summary
                human_feedback = result.get('human_feedback', {})
                if human_feedback:
                    console.print("\n👤 Human Feedback Summary:", style="bold cyan")
                    for feedback_type, feedback in human_feedback.items():
                        decision = feedback.get('decision', 'unknown')
                        console.print(f"  {feedback_type}: {decision}")
                        if feedback.get('comment'):
                            console.print(f"    Comment: {feedback['comment']}")
            else:
                console.print("❌ Workflow failed!", style="bold red")
                console.print(f"Error: {result.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            console.print("\n🚫 Demo interrupted by user", style="bold red")
        except Exception as e:
            console.print(f"\n❌ Demo failed with error: {str(e)}", style="bold red")
    
    console.print("\n📚 This demo shows how to integrate human review points", style="blue")
    console.print("into LangGraph workflows for better control and quality.", style="blue")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demo
    demo_human_in_the_loop()