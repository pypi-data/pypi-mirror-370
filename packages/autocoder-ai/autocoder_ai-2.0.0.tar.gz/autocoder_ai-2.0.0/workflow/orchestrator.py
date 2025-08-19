"""
Workflow Orchestrator using LangGraph for agent coordination
"""

import logging
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from rich.progress import Progress
import asyncio

from .state import WorkflowState
from agents import (
    PlannerAgent, DeveloperAgent, TesterAgent,
    UIUXExpertAgent, DBExpertAgent, DevOpsExpertAgent
)
from agents.base_agent import AgentConfig
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """Orchestrates the multi-agent workflow using LangGraph"""
    
    def __init__(self, config: Dict[str, Any], output_dir: str, dry_run: bool = False, enable_human_approval: bool = False, websocket_manager=None):
        self.config = config
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.enable_human_approval = enable_human_approval
        self.file_handler = FileHandler(output_dir)
        self.progress_callback = None
        self.human_feedback_callback = None
        self.websocket_manager = websocket_manager
        
        # Initialize event emitters for each agent
        self.agent_emitters = {}
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents with their configurations"""
        agents = {}
        
        agent_classes = {
            'planner': PlannerAgent,
            'developer': DeveloperAgent,
            'tester': TesterAgent,
            'ui_ux_expert': UIUXExpertAgent,
            'db_expert': DBExpertAgent,
            'devops_expert': DevOpsExpertAgent
        }
        
        for agent_name, agent_class in agent_classes.items():
            try:
                agent_config_data = self.config['agents'][agent_name]
                agent_config = AgentConfig(
                    name=agent_name,
                    model=agent_config_data['model'],
                    description=agent_config_data['description']
                )
                agents[agent_name] = agent_class(agent_config)
                
                # Create event emitter for this agent if websocket_manager provided
                if self.websocket_manager:
                    # Import here to avoid circular dependency
                    from web_interface.agent_event_emitter import AgentEventEmitter
                    self.agent_emitters[agent_name] = AgentEventEmitter(self.websocket_manager)
                    self.agent_emitters[agent_name].set_agent_name(agent_name)
                
                logger.info(f"Initialized {agent_name} agent")
                
            except Exception as e:
                logger.error(f"Failed to initialize {agent_name} agent: {str(e)}")
                raise
        
        return agents
    
    def set_progress_callback(self, callback):
        """Set progress callback for real-time updates"""
        self.progress_callback = callback
    
    def set_human_feedback_callback(self, callback):
        """Set callback for human feedback requests"""
        self.human_feedback_callback = callback
    
    def _create_workflow(self):
        """Create the LangGraph workflow with human-in-the-loop support"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each agent
        workflow.add_node("planner", self._run_planner)
        workflow.add_node("developer", self._run_developer)
        workflow.add_node("ui_ux_expert", self._run_ui_ux_expert)
        workflow.add_node("db_expert", self._run_db_expert)
        workflow.add_node("tester", self._run_tester)
        workflow.add_node("devops_expert", self._run_devops_expert)
        workflow.add_node("finalize", self._finalize_results)
        
        # Add human-in-the-loop nodes
        workflow.add_node("review_plan", self._request_plan_review)
        workflow.add_node("review_code", self._request_code_review)
        workflow.add_node("review_tests", self._request_test_review)
        workflow.add_node("final_approval", self._request_final_approval)
        
        # Define the workflow edges with human approval points
        workflow.set_entry_point("planner")
        
        # After planner, optionally review plan
        workflow.add_conditional_edges(
            "planner",
            self._check_human_approval_needed,
            {
                "review": "review_plan",
                "continue": "developer"
            }
        )
        workflow.add_edge("review_plan", "developer")
        
        # After developer, route to appropriate next agent
        workflow.add_conditional_edges(
            "developer",
            self._route_after_developer,
            {
                "ui_ux": "ui_ux_expert",
                "db": "db_expert",
                "tester": "tester"
            }
        )
        
        # Note: Standard routing after developer handled above
        
        workflow.add_edge("ui_ux_expert", "tester")
        workflow.add_edge("db_expert", "tester")
        
        # After tester, optionally review tests
        workflow.add_conditional_edges(
            "tester",
            self._check_test_review_needed,
            {
                "review": "review_tests",
                "continue": "devops_expert"
            }
        )
        workflow.add_edge("review_tests", "devops_expert")
        
        workflow.add_edge("devops_expert", "final_approval")
        
        # Final approval before completion
        workflow.add_conditional_edges(
            "final_approval",
            self._check_final_approval_needed,
            {
                "approve": "finalize",
                "continue": "finalize"
            }
        )
        workflow.add_edge("finalize", END)
        
        # Compile with interrupt support for human input
        return workflow.compile(interrupt_before=["review_plan", "review_code", "review_tests", "final_approval"] if self.enable_human_approval else [])
    
    def execute_task(self, task_description: str, progress: Progress, task_id: Any) -> Dict[str, Any]:
        """Execute the multi-agent workflow"""
        try:
            # Initialize workflow state
            initial_state = {
                "task_description": task_description,
                "current_agent": "planner",
                "agent_results": {},
                "context": {},
                "files_created": [],
                "iteration": 0,
                "max_iterations": self.config.get('workflow', {}).get('max_iterations', 5),
                "human_feedback": {},
                "awaiting_human_input": False,
                "human_input_required": None,
                "human_input_data": None,
                "enable_human_approval": self.enable_human_approval,
                "approval_points": ["plan", "code", "tests", "final"]
            }
            
            # Run the workflow
            progress.update(task_id, description="Running multi-agent workflow...")
            final_state = self.workflow.invoke(initial_state)
            
            # Process and save results
            progress.update(task_id, description="Processing results...")
            result = self._process_final_results(final_state)
            
            progress.update(task_id, description="✅ Task completed!")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            progress.update(task_id, description="❌ Task failed!")
            return {
                'success': False,
                'error': str(e),
                'agent_results': {},
                'files_created': []
            }
    
    async def execute_task_async(self, task_description: str, project_id: str = None, 
                                 session_id: str = None, verbose: bool = False) -> Dict[str, Any]:
        """Execute the multi-agent workflow asynchronously (for FastAPI)"""
        try:
            # Initialize workflow state
            initial_state = {
                "task_description": task_description,
                "project_id": project_id,
                "session_id": session_id,
                "current_agent": "planner",
                "agent_results": {},
                "context": {},
                "files_created": [],
                "iteration": 0,
                "max_iterations": self.config.get('workflow', {}).get('max_iterations', 5),
                "human_feedback": {},
                "awaiting_human_input": False,
                "human_input_required": None,
                "human_input_data": None,
                "enable_human_approval": self.enable_human_approval,
                "approval_points": ["plan", "code", "tests", "final"],
                "verbose": verbose
            }
            
            # Run the workflow asynchronously
            import asyncio
            loop = asyncio.get_event_loop()
            final_state = await loop.run_in_executor(None, self.workflow.invoke, initial_state)
            
            # Process and save results
            result = self._process_final_results(final_state)
            
            return result
            
        except Exception as e:
            logger.error(f"Async workflow execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent_results': {},
                'files_created': []
            }
    
    def _run_planner(self, state: WorkflowState) -> WorkflowState:
        """Run the planner agent"""
        logger.info("Running planner agent")
        
        # Run async method synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.agents['planner'].execute(
                task=state["task_description"],
                context=state["context"]
            ))
        finally:
            loop.close()
        
        state["agent_results"]['planner'] = result
        state["context"]['planner'] = result
        state["current_agent"] = 'developer'
        
        return state
    
    def _run_developer(self, state: WorkflowState) -> WorkflowState:
        """Run the developer agent"""
        logger.info("Running developer agent")
        
        # Run async method synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.agents['developer'].execute(
                task=state["task_description"],
                context=state["context"]
            ))
        finally:
            loop.close()
        
        state["agent_results"]['developer'] = result
        state["context"]['developer'] = result
        
        # Save code files if generated
        if result.get('code_files'):
            for file_info in result['code_files']:
                file_path = self.file_handler.save_file(
                    filename=file_info['filename'],
                    content=file_info['content'],
                    dry_run=self.dry_run
                )
                if file_path:
                    state["files_created"].append(file_path)
        
        return state
    
    def _run_ui_ux_expert(self, state: WorkflowState) -> WorkflowState:
        """Run the UI/UX expert agent"""
        logger.info("Running UI/UX expert agent")
        
        # Run async method synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.agents['ui_ux_expert'].execute(
                task=state["task_description"],
                context=state["context"]
            ))
        finally:
            loop.close()
        
        state["agent_results"]['ui_ux_expert'] = result
        state["context"]['ui_ux_expert'] = result
        
        # Save frontend files if generated
        if result.get('frontend_files'):
            for file_info in result['frontend_files']:
                file_path = self.file_handler.save_file(
                    filename=file_info['filename'],
                    content=file_info['content'],
                    dry_run=self.dry_run
                )
                if file_path:
                    state["files_created"].append(file_path)
        
        return state
    
    def _run_db_expert(self, state: WorkflowState) -> WorkflowState:
        """Run the database expert agent"""
        logger.info("Running database expert agent")
        
        # Run async method synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.agents['db_expert'].execute(
                task=state["task_description"],
                context=state["context"]
            ))
        finally:
            loop.close()
        
        state["agent_results"]['db_expert'] = result
        state["context"]['db_expert'] = result
        
        # Save schema files if generated
        if result.get('schema_files'):
            for file_info in result['schema_files']:
                file_path = self.file_handler.save_file(
                    filename=file_info['filename'],
                    content=file_info['content'],
                    dry_run=self.dry_run
                )
                if file_path:
                    state["files_created"].append(file_path)
        
        return state
    
    def _run_tester(self, state: WorkflowState) -> WorkflowState:
        """Run the tester agent"""
        logger.info("Running tester agent")
        
        # Run async method synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.agents['tester'].execute(
                task=state["task_description"],
                context=state["context"]
            ))
        finally:
            loop.close()
        
        state["agent_results"]['tester'] = result
        state["context"]['tester'] = result
        
        # Save test files if generated
        if result.get('test_files'):
            for file_info in result['test_files']:
                file_path = self.file_handler.save_file(
                    filename=file_info['filename'],
                    content=file_info['content'],
                    dry_run=self.dry_run
                )
                if file_path:
                    state["files_created"].append(file_path)
        
        return state
    
    def _run_devops_expert(self, state: WorkflowState) -> WorkflowState:
        """Run the DevOps expert agent"""
        logger.info("Running DevOps expert agent")
        
        # Run async method synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.agents['devops_expert'].execute(
                task=state["task_description"],
                context=state["context"]
            ))
        finally:
            loop.close()
        
        state["agent_results"]['devops_expert'] = result
        state["context"]['devops_expert'] = result
        
        # Save config files if generated
        if result.get('config_files'):
            for file_info in result['config_files']:
                file_path = self.file_handler.save_file(
                    filename=file_info['filename'],
                    content=file_info['content'],
                    dry_run=self.dry_run
                )
                if file_path:
                    state["files_created"].append(file_path)
        
        # Save deployment scripts if generated
        if result.get('deployment_scripts'):
            for file_info in result['deployment_scripts']:
                file_path = self.file_handler.save_file(
                    filename=file_info['filename'],
                    content=file_info['content'],
                    dry_run=self.dry_run
                )
                if file_path:
                    state["files_created"].append(file_path)
        
        return state
    
    def _finalize_results(self, state: WorkflowState) -> WorkflowState:
        """Finalize the workflow results"""
        logger.info("Finalizing workflow results")
        
        # Generate summary report if configured
        if self.config.get('output', {}).get('create_summary_report', True):
            summary_content = self._generate_summary_report(state)
            summary_path = self.file_handler.save_file(
                filename="project_summary.md",
                content=summary_content,
                dry_run=self.dry_run
            )
            if summary_path:
                state["files_created"].append(summary_path)
        
        state["current_agent"] = 'completed'
        return state
    
    def _route_after_developer(self, state: WorkflowState) -> str:
        """Route to the next agent after developer"""
        # Check if UI/UX expert should run based on developer output
        dev_result = state["agent_results"].get('developer', {})
        if dev_result.get('metadata', {}).get('languages_used'):
            languages = dev_result['metadata']['languages_used']
            if any(lang in ['html', 'css', 'javascript'] for lang in languages):
                return "ui_ux"
        
        # Check if database expert should run
        if 'database' in state["task_description"].lower() or 'data' in state["task_description"].lower():
            return "db"
        
        # Default to tester
        return "tester"
    
    def _process_final_results(self, state: WorkflowState) -> Dict[str, Any]:
        """Process the final workflow results"""
        successful_agents = []
        failed_agents = []
        recommendations = []
        
        for agent_name, result in state["agent_results"].items():
            if result.get('success', False):
                successful_agents.append(agent_name)
            else:
                failed_agents.append(agent_name)
        
        # Generate recommendations based on results
        if successful_agents:
            recommendations.append(f"Successfully executed {len(successful_agents)} agents")
        
        if failed_agents:
            recommendations.append(f"Review failed agents: {', '.join(failed_agents)}")
        
        if state["files_created"]:
            recommendations.append(f"Generated {len(state['files_created'])} files - review and test before deployment")
        
        return {
            'success': len(failed_agents) == 0,
            'agent_results': state["agent_results"],
            'files_created': state["files_created"],
            'recommendations': recommendations,
            'summary': {
                'successful_agents': successful_agents,
                'failed_agents': failed_agents,
                'total_files': len(state["files_created"])
            }
        }
    
    def _generate_summary_report(self, state: WorkflowState) -> str:
        """Generate a summary report of the workflow execution"""
        report = f"""# Project Summary Report

## Task Description
{state["task_description"]}

## Agents Executed
"""
        
        for agent_name, result in state["agent_results"].items():
            status = "✅ Success" if result.get('success', False) else "❌ Failed"
            report += f"- **{agent_name.replace('_', ' ').title()}**: {status}\n"
        
        report += f"\n## Files Generated\n"
        for file_path in state["files_created"]:
            report += f"- {file_path}\n"
        
        report += f"\n## Next Steps\n"
        report += "1. Review all generated files\n"
        report += "2. Test the implementation\n"
        report += "3. Deploy according to DevOps recommendations\n"
        report += "4. Monitor performance and iterate as needed\n"
        
        return report
    
    # Human-in-the-loop workflow nodes
    
    def _request_plan_review(self, state: WorkflowState) -> WorkflowState:
        """Request human review of the plan"""
        logger.info("Requesting human review of plan")
        
        plan_result = state["agent_results"].get('planner', {})
        
        # Prepare review data
        review_data = {
            "type": "plan_review",
            "title": "Review Development Plan",
            "content": plan_result.get('plan', ''),
            "questions": [
                "Does this plan cover all requirements?",
                "Are there any missing components?", 
                "Should we proceed with this approach?"
            ],
            "options": ["approve", "request_changes", "reject"]
        }
        
        state["human_input_required"] = "plan_review"
        state["human_input_data"] = review_data
        state["awaiting_human_input"] = True
        
        # Trigger callback if available
        if self.human_feedback_callback:
            self.human_feedback_callback(review_data)
        
        return state
    
    def _request_code_review(self, state: WorkflowState) -> WorkflowState:
        """Request human review of generated code"""
        logger.info("Requesting human review of code")
        
        code_result = state["agent_results"].get('developer', {})
        
        review_data = {
            "type": "code_review",
            "title": "Review Generated Code", 
            "content": code_result.get('summary', ''),
            "files": code_result.get('code_files', []),
            "questions": [
                "Does the code look correct?",
                "Are there any obvious issues?",
                "Should we proceed to testing?"
            ],
            "options": ["approve", "request_changes", "reject"]
        }
        
        state["human_input_required"] = "code_review"
        state["human_input_data"] = review_data
        state["awaiting_human_input"] = True
        
        if self.human_feedback_callback:
            self.human_feedback_callback(review_data)
        
        return state
    
    def _request_test_review(self, state: WorkflowState) -> WorkflowState:
        """Request human review of test results"""
        logger.info("Requesting human review of test results")
        
        test_result = state["agent_results"].get('tester', {})
        
        review_data = {
            "type": "test_review", 
            "title": "Review Test Results",
            "content": test_result.get('test_summary', ''),
            "test_results": test_result.get('test_files', []),
            "questions": [
                "Are the test results satisfactory?",
                "Do we need additional testing?",
                "Should we proceed to deployment?"
            ],
            "options": ["approve", "request_more_tests", "reject"]
        }
        
        state["human_input_required"] = "test_review"
        state["human_input_data"] = review_data
        state["awaiting_human_input"] = True
        
        if self.human_feedback_callback:
            self.human_feedback_callback(review_data)
        
        return state
    
    def _request_final_approval(self, state: WorkflowState) -> WorkflowState:
        """Request final approval before completion"""
        logger.info("Requesting final approval")
        
        # Compile summary of all work done
        summary = {
            "plan": state["agent_results"].get('planner', {}).get('plan', ''),
            "code_files": len(state.get("files_created", [])),
            "agents_used": list(state["agent_results"].keys()),
            "final_output": state["agent_results"].get('devops_expert', {}).get('summary', '')
        }
        
        review_data = {
            "type": "final_approval",
            "title": "Final Project Approval",
            "summary": summary,
            "files_created": state.get("files_created", []),
            "questions": [
                "Are you satisfied with the final result?",
                "Should we deploy/finalize the project?",
                "Any final modifications needed?"
            ],
            "options": ["approve", "request_changes", "reject"]
        }
        
        state["human_input_required"] = "final_approval"
        state["human_input_data"] = review_data
        state["awaiting_human_input"] = True
        
        if self.human_feedback_callback:
            self.human_feedback_callback(review_data)
        
        return state
    
    # Human approval routing functions
    
    def _check_human_approval_needed(self, state: WorkflowState) -> str:
        """Check if human approval is needed after planning"""
        if state.get("enable_human_approval", False) and "plan" in state.get("approval_points", []):
            return "review"
        return "continue"
    
    def _check_code_review_needed(self, state: WorkflowState) -> str:
        """Check if code review is needed"""
        if state.get("enable_human_approval", False) and "code" in state.get("approval_points", []):
            return "review"
        return "continue"
    
    def _check_test_review_needed(self, state: WorkflowState) -> str:
        """Check if test review is needed"""
        if state.get("enable_human_approval", False) and "tests" in state.get("approval_points", []):
            return "review"
        return "continue"
    
    def _check_final_approval_needed(self, state: WorkflowState) -> str:
        """Check if final approval is needed"""
        if state.get("enable_human_approval", False) and "final" in state.get("approval_points", []):
            return "approve"
        return "continue"
    
    def provide_human_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """Provide human feedback to resume workflow"""
        logger.info(f"Received human feedback: {feedback_data}")
        
        # Process feedback and resume workflow
        if hasattr(self.workflow, 'get_state'):
            current_state = self.workflow.get_state()
            current_state["human_feedback"][feedback_data.get("type", "general")] = feedback_data
            current_state["awaiting_human_input"] = False
            current_state["human_input_required"] = None
            
            # Resume workflow with updated state
            self.workflow.invoke(current_state)
    
    def execute_with_human_approval(self, task_description: str, progress: Progress, task_id: Any, approval_points: List[str] = None) -> Dict[str, Any]:
        """Execute workflow with human approval points"""
        self.enable_human_approval = True
        
        # Override approval points if provided
        if approval_points:
            # Recreate workflow with new approval points
            self.workflow = self._create_workflow()
        
        return self.execute_task(task_description, progress, task_id)
