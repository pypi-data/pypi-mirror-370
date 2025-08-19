"""
Planner Agent - Strategic planning and task breakdown
"""

import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent, AgentConfig

class PlannerAgent(BaseAgent):
    """Agent responsible for strategic planning and task breakdown"""
    
    def _format_task(self, task: str) -> str:
        """Format the task for the planner"""
        return f"""
TASK: {task}

As the Planner, break down this task into a comprehensive development plan. Provide:

1. PROJECT OVERVIEW:
   - Brief description of what needs to be built
   - Key requirements and objectives
   - Target users/stakeholders

2. TECHNICAL ARCHITECTURE:
   - Recommended technology stack
   - System architecture overview
   - Key components and their relationships

3. DEVELOPMENT PHASES:
   - Phase breakdown with priorities
   - Dependencies between phases
   - Estimated effort for each phase

4. TEAM COORDINATION:
   - Which agents should be involved in each phase
   - Specific tasks for each specialist agent
   - Coordination points and handoffs

5. RISK ASSESSMENT:
   - Potential challenges and risks
   - Mitigation strategies
   - Alternative approaches

6. SUCCESS CRITERIA:
   - How to measure success
   - Key deliverables
   - Testing and validation requirements

Provide your response in a structured format that other agents can easily follow.
"""
    
    def _process_response(self, response: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the planner's response"""
        try:
            # Extract structured information from the response
            plan = self._extract_plan_structure(response)
            
            return {
                'success': True,
                'agent': self.name,
                'output': response,
                'structured_plan': plan,
                'next_agents': self._determine_next_agents(plan),
                'metadata': {
                    'task': task,
                    'planning_completed': True
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'output': response
            }
    
    def _extract_plan_structure(self, response: str) -> Dict[str, Any]:
        """Extract structured plan from the response"""
        plan = {
            'overview': '',
            'architecture': '',
            'phases': [],
            'team_coordination': {},
            'risks': [],
            'success_criteria': []
        }
        
        try:
            # Extract project overview
            overview_match = re.search(r'1\.\s*PROJECT OVERVIEW[:\s]*(.*?)(?=2\.|$)', response, re.DOTALL | re.IGNORECASE)
            if overview_match:
                plan['overview'] = overview_match.group(1).strip()
            
            # Extract technical architecture
            arch_match = re.search(r'2\.\s*TECHNICAL ARCHITECTURE[:\s]*(.*?)(?=3\.|$)', response, re.DOTALL | re.IGNORECASE)
            if arch_match:
                plan['architecture'] = arch_match.group(1).strip()
            
            # Extract development phases
            phases_match = re.search(r'3\.\s*DEVELOPMENT PHASES[:\s]*(.*?)(?=4\.|$)', response, re.DOTALL | re.IGNORECASE)
            if phases_match:
                phases_text = phases_match.group(1).strip()
                # Simple phase extraction - can be enhanced
                plan['phases'] = [phase.strip() for phase in phases_text.split('\n') if phase.strip() and not phase.strip().startswith('-')]
            
            # Extract team coordination
            team_match = re.search(r'4\.\s*TEAM COORDINATION[:\s]*(.*?)(?=5\.|$)', response, re.DOTALL | re.IGNORECASE)
            if team_match:
                team_text = team_match.group(1).strip()
                plan['team_coordination'] = {'raw': team_text}
            
        except Exception as e:
            # If parsing fails, store the raw response
            plan['raw_response'] = response
        
        return plan
    
    def _determine_next_agents(self, plan: Dict[str, Any]) -> list:
        """Determine which agents should be involved next based on the plan"""
        next_agents = []
        
        # Always start with developer for code structure
        next_agents.append('developer')
        
        # Check if UI/UX is needed
        response_lower = plan.get('raw_response', '').lower()
        if any(term in response_lower for term in ['ui', 'interface', 'frontend', 'web', 'user experience']):
            next_agents.append('ui_ux_expert')
        
        # Check if database is needed
        if any(term in response_lower for term in ['database', 'data', 'storage', 'sql', 'nosql']):
            next_agents.append('db_expert')
        
        # Tester is usually needed
        next_agents.append('tester')
        
        # DevOps for deployment considerations
        next_agents.append('devops_expert')
        
        return next_agents
