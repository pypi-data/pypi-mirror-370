"""
DevOps Expert Agent - Deployment and infrastructure
"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig

class DevOpsExpertAgent(BaseAgent):
    """Agent responsible for deployment and infrastructure"""
    
    def _format_task(self, task: str) -> str:
        """Format the task for the DevOps expert"""
        return f"""
DEVOPS DEPLOYMENT TASK: {task}

As the DevOps Expert, design the deployment and infrastructure strategy. Provide:

1. INFRASTRUCTURE DESIGN:
   - Deployment architecture
   - Server/container specifications
   - Network configuration
   - Load balancing strategy

2. CI/CD PIPELINE:
   - Version control workflow
   - Build and test automation
   - Deployment pipeline stages
   - Rollback strategies

3. CONTAINERIZATION:
   - Docker configuration
   - Container orchestration (if needed)
   - Image optimization
   - Security scanning

4. MONITORING & LOGGING:
   - Application monitoring setup
   - Log aggregation strategy
   - Performance metrics
   - Alerting mechanisms

5. SECURITY & COMPLIANCE:
   - Security best practices
   - Access controls
   - SSL/TLS configuration
   - Backup strategies

6. SCALABILITY & PERFORMANCE:
   - Auto-scaling configuration
   - Performance optimization
   - Resource management
   - Cost optimization

Provide specific configuration files and deployment scripts.
"""
    
    def _process_response(self, response: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the DevOps expert's response"""
        try:
            # Extract DevOps components
            devops_plan = self._extract_devops_plan(response)
            
            return {
                'success': True,
                'agent': self.name,
                'output': response,
                'devops_plan': devops_plan,
                'config_files': self._extract_config_files(response),
                'deployment_scripts': self._extract_deployment_scripts(response),
                'metadata': {
                    'task': task,
                    'devops_planned': True,
                    'containerization': self._check_containerization(response),
                    'ci_cd_configured': self._check_ci_cd(response)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'output': response
            }
    
    def _extract_devops_plan(self, response: str) -> Dict[str, Any]:
        """Extract DevOps plan from the response"""
        plan = {
            'infrastructure': '',
            'ci_cd': '',
            'containerization': '',
            'monitoring': '',
            'security': '',
            'scalability': ''
        }
        
        try:
            # Extract infrastructure design
            infra_match = re.search(r'1\.\s*INFRASTRUCTURE DESIGN[:\s]*(.*?)(?=2\.|$)', response, re.DOTALL | re.IGNORECASE)
            if infra_match:
                plan['infrastructure'] = infra_match.group(1).strip()
            
            # Extract CI/CD pipeline
            cicd_match = re.search(r'2\.\s*CI/CD PIPELINE[:\s]*(.*?)(?=3\.|$)', response, re.DOTALL | re.IGNORECASE)
            if cicd_match:
                plan['ci_cd'] = cicd_match.group(1).strip()
            
            # Extract containerization
            container_match = re.search(r'3\.\s*CONTAINERIZATION[:\s]*(.*?)(?=4\.|$)', response, re.DOTALL | re.IGNORECASE)
            if container_match:
                plan['containerization'] = container_match.group(1).strip()
            
            # Extract monitoring & logging
            monitor_match = re.search(r'4\.\s*MONITORING & LOGGING[:\s]*(.*?)(?=5\.|$)', response, re.DOTALL | re.IGNORECASE)
            if monitor_match:
                plan['monitoring'] = monitor_match.group(1).strip()
            
            # Extract security & compliance
            security_match = re.search(r'5\.\s*SECURITY & COMPLIANCE[:\s]*(.*?)(?=6\.|$)', response, re.DOTALL | re.IGNORECASE)
            if security_match:
                plan['security'] = security_match.group(1).strip()
            
            # Extract scalability & performance
            scale_match = re.search(r'6\.\s*SCALABILITY & PERFORMANCE[:\s]*(.*?)(?=\Z)', response, re.DOTALL | re.IGNORECASE)
            if scale_match:
                plan['scalability'] = scale_match.group(1).strip()
            
        except Exception as e:
            plan['raw_response'] = response
        
        return plan
    
    def _extract_config_files(self, response: str) -> List[Dict[str, str]]:
        """Extract configuration files from the response"""
        files = []
        
        # Look for configuration file patterns
        config_patterns = [
            r'(?:^|\n)(Dockerfile):\s*\n```(?:dockerfile)?\n(.*?)\n```',
            r'(?:^|\n)(docker-compose\.ya?ml):\s*\n```ya?ml\n(.*?)\n```',
            r'(?:^|\n)(\.github/workflows/[a-zA-Z0-9_-]+\.ya?ml):\s*\n```ya?ml\n(.*?)\n```',
            r'(?:^|\n)(nginx\.conf):\s*\n```(?:nginx|conf)?\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z0-9_-]+\.ya?ml):\s*\n```ya?ml\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z0-9_-]+\.json):\s*\n```json\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z0-9_-]+\.toml):\s*\n```toml\n(.*?)\n```',
        ]
        
        for pattern in config_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
            for filename, content in matches:
                files.append({
                    'filename': filename,
                    'content': content.strip(),
                    'type': 'config',
                    'language': self._get_file_language(filename)
                })
        
        return files
    
    def _extract_deployment_scripts(self, response: str) -> List[Dict[str, str]]:
        """Extract deployment scripts from the response"""
        scripts = []
        
        # Look for script patterns
        script_patterns = [
            r'(?:^|\n)(deploy\.sh):\s*\n```(?:bash|sh)?\n(.*?)\n```',
            r'(?:^|\n)(build\.sh):\s*\n```(?:bash|sh)?\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z0-9_-]+\.sh):\s*\n```(?:bash|sh)?\n(.*?)\n```',
            r'(?:^|\n)(Makefile):\s*\n```(?:make|makefile)?\n(.*?)\n```',
        ]
        
        for pattern in script_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
            for filename, content in matches:
                scripts.append({
                    'filename': filename,
                    'content': content.strip(),
                    'type': 'script',
                    'language': self._get_file_language(filename)
                })
        
        return scripts
    
    def _get_file_language(self, filename: str) -> str:
        """Get the language/type of a file based on its extension"""
        ext = filename.split('.')[-1].lower()
        
        language_map = {
            'yml': 'yaml',
            'yaml': 'yaml',
            'json': 'json',
            'sh': 'bash',
            'py': 'python',
            'js': 'javascript',
            'toml': 'toml',
            'conf': 'config',
            'dockerfile': 'dockerfile'
        }
        
        return language_map.get(ext, 'text')
    
    def _check_containerization(self, response: str) -> bool:
        """Check if containerization is mentioned"""
        container_indicators = [
            'docker', 'dockerfile', 'container', 'kubernetes',
            'k8s', 'docker-compose', 'podman', 'containerd'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in container_indicators)
    
    def _check_ci_cd(self, response: str) -> bool:
        """Check if CI/CD is configured"""
        cicd_indicators = [
            'ci/cd', 'continuous integration', 'continuous deployment',
            'github actions', 'gitlab ci', 'jenkins', 'travis',
            'circleci', 'azure devops', 'pipeline'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in cicd_indicators)
