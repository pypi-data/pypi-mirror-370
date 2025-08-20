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
        """Extract code files from the response - enhanced to handle various formats"""
        files = []
        files_found = set()  # Track filenames to avoid duplicates
        
        # Method 1: Look for explicit file patterns like "filename.py:" followed by code block
        explicit_patterns = [
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_\./-]*\.py):\s*\n```(?:python)?\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_\./-]*\.js):\s*\n```(?:javascript)?\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_\./-]*\.html):\s*\n```(?:html)?\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_\./-]*\.css):\s*\n```(?:css)?\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_\./-]*\.yaml):\s*\n```(?:yaml)?\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_\./-]*\.json):\s*\n```(?:json)?\n(.*?)\n```',
        ]
        
        for pattern in explicit_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE | re.IGNORECASE)
            for filename, content in matches:
                if filename not in files_found:
                    files.append({
                        'filename': filename.strip(),
                        'content': content.strip(),
                        'language': filename.split('.')[-1]
                    })
                    files_found.add(filename)
        
        # Method 2: Look for code blocks with filename comments inside
        # Pattern: ```language\n# filename.ext\n...code...\n```
        code_block_pattern = r'```(\w+)?\n(?:#|//|--|/\*)\s*([a-zA-Z_][a-zA-Z0-9_\./-]+\.[a-zA-Z]+).*?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, response, re.DOTALL | re.MULTILINE)
        for lang, filename, content in matches:
            if filename not in files_found:
                # Clean up the content to remove the filename comment line
                content_lines = content.split('\n')
                if content_lines and any(filename in content_lines[0] for filename in [filename]):
                    content = '\n'.join(content_lines[1:])
                files.append({
                    'filename': filename.strip(),
                    'content': content.strip(),
                    'language': lang or filename.split('.')[-1]
                })
                files_found.add(filename)
        
        # Method 3: If no files found yet, try to extract any code blocks and generate filenames
        if not files:
            # Look for any code blocks
            generic_pattern = r'```(\w+)?\n(.*?)\n```'
            matches = re.findall(generic_pattern, response, re.DOTALL)
            
            # Also check for language-specific indicators in the response
            task_lower = response.lower()
            
            for i, (lang, content) in enumerate(matches):
                # Skip if content is too short or looks like output
                if len(content.strip()) < 10 or content.startswith('$') or content.startswith('>'):
                    continue
                    
                # Try to determine appropriate filename
                filename = None
                if lang:
                    lang = lang.lower()
                    
                # Check for common file patterns in content or nearby text
                if 'fastapi' in task_lower or 'api' in task_lower:
                    if lang in ['python', 'py'] or 'def ' in content or 'import ' in content:
                        filename = 'main.py' if i == 0 else f'app_{i}.py'
                elif 'hello' in task_lower and 'world' in task_lower:
                    if lang in ['python', 'py'] or 'print' in content:
                        filename = 'hello.py'
                    elif lang in ['javascript', 'js'] or 'console.log' in content:
                        filename = 'hello.js'
                elif lang == 'python' or (not lang and ('def ' in content or 'import ' in content)):
                    filename = 'main.py' if i == 0 else f'script_{i}.py'
                elif lang == 'javascript' or (not lang and ('function ' in content or 'const ' in content)):
                    filename = 'main.js' if i == 0 else f'script_{i}.js'
                elif lang == 'html' or (not lang and '<html' in content):
                    filename = 'index.html' if i == 0 else f'page_{i}.html'
                elif lang == 'css' or (not lang and ('body {' in content or '.class' in content)):
                    filename = 'styles.css' if i == 0 else f'styles_{i}.css'
                elif lang == 'sql':
                    filename = 'schema.sql' if i == 0 else f'query_{i}.sql'
                elif lang in ['yaml', 'yml']:
                    filename = 'config.yaml'
                elif lang == 'json':
                    filename = 'config.json'
                elif lang in ['bash', 'sh', 'shell']:
                    filename = 'script.sh' if i == 0 else f'script_{i}.sh'
                
                if filename and filename not in files_found:
                    files.append({
                        'filename': filename,
                        'content': content.strip(),
                        'language': lang or filename.split('.')[-1]
                    })
                    files_found.add(filename)
        
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
