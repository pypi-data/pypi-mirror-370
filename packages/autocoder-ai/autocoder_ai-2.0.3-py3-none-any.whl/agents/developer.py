"""
Developer Agent - Code implementation and development
"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig

class DeveloperAgent(BaseAgent):
    """Agent responsible for code implementation and development"""
    
    def _format_task(self, task: str) -> str:
        """Format the task for the developer"""
        return f"""
DEVELOPMENT TASK: {task}

As the Developer, implement the core functionality. Provide:

1. CODE STRUCTURE:
   - Directory structure and file organization
   - Main modules and their responsibilities
   - Entry points and configuration files

2. CORE IMPLEMENTATION:
   - Key functions and classes
   - Data models and schemas
   - Business logic implementation
   - Error handling and validation

3. INTEGRATION POINTS:
   - APIs and interfaces
   - Database connections (if applicable)
   - External service integrations
   - Configuration management

4. CODE QUALITY:
   - Best practices followed
   - Security considerations
   - Performance optimizations
   - Maintainability features

5. TESTING HOOKS:
   - Unit test structure
   - Integration test points
   - Mock/stub requirements
   - Test data considerations

6. DOCUMENTATION:
   - Code comments and docstrings
   - README content
   - API documentation
   - Setup instructions

Provide actual code snippets and specific implementation details.
"""
    
    def _process_response(self, response: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the developer's response"""
        try:
            # Extract code snippets and implementation details
            implementation = self._extract_implementation(response)
            
            return {
                'success': True,
                'agent': self.name,
                'output': response,
                'implementation': implementation,
                'code_files': self._extract_code_files(response),
                'setup_instructions': self._extract_setup_instructions(response),
                'metadata': {
                    'task': task,
                    'development_completed': True,
                    'languages_used': self._detect_languages(response)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'output': response
            }
    
    def _extract_implementation(self, response: str) -> Dict[str, Any]:
        """Extract implementation details from the response"""
        implementation = {
            'structure': '',
            'core_code': [],
            'integrations': '',
            'quality_notes': '',
            'testing_approach': ''
        }
        
        try:
            # Extract code structure
            structure_match = re.search(r'1\.\s*CODE STRUCTURE[:\s]*(.*?)(?=2\.|$)', response, re.DOTALL | re.IGNORECASE)
            if structure_match:
                implementation['structure'] = structure_match.group(1).strip()
            
            # Extract core implementation
            core_match = re.search(r'2\.\s*CORE IMPLEMENTATION[:\s]*(.*?)(?=3\.|$)', response, re.DOTALL | re.IGNORECASE)
            if core_match:
                core_text = core_match.group(1).strip()
                # Extract code blocks
                code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', core_text, re.DOTALL)
                implementation['core_code'] = code_blocks
            
            # Extract integration points
            integration_match = re.search(r'3\.\s*INTEGRATION POINTS[:\s]*(.*?)(?=4\.|$)', response, re.DOTALL | re.IGNORECASE)
            if integration_match:
                implementation['integrations'] = integration_match.group(1).strip()
            
            # Extract testing approach
            testing_match = re.search(r'5\.\s*TESTING HOOKS[:\s]*(.*?)(?=6\.|$)', response, re.DOTALL | re.IGNORECASE)
            if testing_match:
                implementation['testing_approach'] = testing_match.group(1).strip()
            
        except Exception as e:
            implementation['raw_response'] = response
        
        return implementation
    
    def _extract_code_files(self, response: str) -> List[Dict[str, str]]:
        """Extract code files from the response"""
        files = []
        
        # Look for file patterns like "filename.py:" or "# filename.py"
        file_patterns = [
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.py):\s*\n```python\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.js):\s*\n```javascript\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.html):\s*\n```html\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.css):\s*\n```css\n(.*?)\n```',
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
            for filename, content in matches:
                files.append({
                    'filename': filename,
                    'content': content.strip(),
                    'language': filename.split('.')[-1]
                })
        
        return files
    
    def _extract_setup_instructions(self, response: str) -> str:
        """Extract setup instructions from the response"""
        setup_match = re.search(r'(?:setup|installation|getting started)[:\s]*(.*?)(?=\n\n|\n#|$)', response, re.DOTALL | re.IGNORECASE)
        if setup_match:
            return setup_match.group(1).strip()
        return ""
    
    def _detect_languages(self, response: str) -> List[str]:
        """Detect programming languages mentioned in the response"""
        languages = set()
        
        # Common language indicators
        language_patterns = {
            'python': [r'python', r'\.py', r'```python'],
            'javascript': [r'javascript', r'\.js', r'```javascript', r'node\.js'],
            'html': [r'html', r'\.html', r'```html'],
            'css': [r'css', r'\.css', r'```css'],
            'sql': [r'sql', r'\.sql', r'```sql', r'database'],
            'bash': [r'bash', r'shell', r'```bash', r'```sh'],
        }
        
        response_lower = response.lower()
        for lang, patterns in language_patterns.items():
            if any(re.search(pattern, response_lower) for pattern in patterns):
                languages.add(lang)
        
        return list(languages)
