"""
UI/UX Expert Agent - User interface and experience design
"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig

class UIUXExpertAgent(BaseAgent):
    """Agent responsible for user interface and experience design"""
    
    def _format_task(self, task: str) -> str:
        """Format the task for the UI/UX expert"""
        return f"""
UI/UX DESIGN TASK: {task}

As the UI/UX Expert, design the user experience and interface. Provide:

1. USER EXPERIENCE DESIGN:
   - User personas and use cases
   - User journey mapping
   - Information architecture
   - Interaction design principles

2. INTERFACE DESIGN:
   - Wireframes and layouts
   - Visual design system
   - Color palette and typography
   - Component specifications

3. RESPONSIVE DESIGN:
   - Mobile-first approach
   - Breakpoint considerations
   - Responsive layouts
   - Touch interaction design

4. ACCESSIBILITY:
   - WCAG compliance guidelines
   - Screen reader compatibility
   - Keyboard navigation
   - Color contrast requirements

5. FRONTEND IMPLEMENTATION:
   - HTML structure recommendations
   - CSS framework suggestions
   - JavaScript interactions
   - Performance optimizations

6. USABILITY TESTING:
   - Testing scenarios
   - User feedback collection
   - A/B testing recommendations
   - Metrics and analytics

Provide specific design specifications and code examples for frontend implementation.
"""
    
    def _process_response(self, response: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the UI/UX expert's response"""
        try:
            # Extract design components
            design_plan = self._extract_design_plan(response)
            
            return {
                'success': True,
                'agent': self.name,
                'output': response,
                'design_plan': design_plan,
                'frontend_files': self._extract_frontend_files(response),
                'design_assets': self._extract_design_assets(response),
                'metadata': {
                    'task': task,
                    'design_completed': True,
                    'responsive_design': self._check_responsive_design(response),
                    'accessibility_considered': self._check_accessibility(response)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'output': response
            }
    
    def _extract_design_plan(self, response: str) -> Dict[str, Any]:
        """Extract design plan from the response"""
        plan = {
            'user_experience': '',
            'interface_design': '',
            'responsive_design': '',
            'accessibility': '',
            'implementation': '',
            'usability_testing': ''
        }
        
        try:
            # Extract user experience design
            ux_match = re.search(r'1\.\s*USER EXPERIENCE DESIGN[:\s]*(.*?)(?=2\.|$)', response, re.DOTALL | re.IGNORECASE)
            if ux_match:
                plan['user_experience'] = ux_match.group(1).strip()
            
            # Extract interface design
            ui_match = re.search(r'2\.\s*INTERFACE DESIGN[:\s]*(.*?)(?=3\.|$)', response, re.DOTALL | re.IGNORECASE)
            if ui_match:
                plan['interface_design'] = ui_match.group(1).strip()
            
            # Extract responsive design
            responsive_match = re.search(r'3\.\s*RESPONSIVE DESIGN[:\s]*(.*?)(?=4\.|$)', response, re.DOTALL | re.IGNORECASE)
            if responsive_match:
                plan['responsive_design'] = responsive_match.group(1).strip()
            
            # Extract accessibility
            a11y_match = re.search(r'4\.\s*ACCESSIBILITY[:\s]*(.*?)(?=5\.|$)', response, re.DOTALL | re.IGNORECASE)
            if a11y_match:
                plan['accessibility'] = a11y_match.group(1).strip()
            
            # Extract frontend implementation
            impl_match = re.search(r'5\.\s*FRONTEND IMPLEMENTATION[:\s]*(.*?)(?=6\.|$)', response, re.DOTALL | re.IGNORECASE)
            if impl_match:
                plan['implementation'] = impl_match.group(1).strip()
            
        except Exception as e:
            plan['raw_response'] = response
        
        return plan
    
    def _extract_frontend_files(self, response: str) -> List[Dict[str, str]]:
        """Extract frontend files from the response"""
        files = []
        
        # Look for frontend file patterns
        frontend_patterns = [
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.html):\s*\n```html\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.css):\s*\n```css\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.js):\s*\n```javascript\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.vue):\s*\n```vue\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.jsx):\s*\n```jsx\n(.*?)\n```',
        ]
        
        for pattern in frontend_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
            for filename, content in matches:
                files.append({
                    'filename': filename,
                    'content': content.strip(),
                    'type': 'frontend',
                    'language': filename.split('.')[-1]
                })
        
        return files
    
    def _extract_design_assets(self, response: str) -> Dict[str, Any]:
        """Extract design assets and specifications"""
        assets = {
            'color_palette': [],
            'typography': {},
            'components': [],
            'breakpoints': {}
        }
        
        # Extract color palette
        color_patterns = [
            r'(?:primary|secondary|accent|background|text)[\s\-_]*color[:\s]*([#\w]+)',
            r'color[:\s]*([#\w]+)',
            r'([#][0-9a-fA-F]{3,6})'
        ]
        
        colors = set()
        for pattern in color_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    colors.update(match)
                else:
                    colors.add(match)
        
        assets['color_palette'] = list(colors)
        
        # Extract typography information
        font_match = re.search(r'font[-\s]*family[:\s]*([^\n;]+)', response, re.IGNORECASE)
        if font_match:
            assets['typography']['font_family'] = font_match.group(1).strip()
        
        size_matches = re.findall(r'font[-\s]*size[:\s]*(\d+(?:\.\d+)?(?:px|em|rem))', response, re.IGNORECASE)
        if size_matches:
            assets['typography']['font_sizes'] = size_matches
        
        # Extract breakpoints
        breakpoint_patterns = [
            r'mobile[:\s]*(\d+px)',
            r'tablet[:\s]*(\d+px)',
            r'desktop[:\s]*(\d+px)',
            r'@media[^{]*?(\d+px)'
        ]
        
        for pattern in breakpoint_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                assets['breakpoints'][pattern.split('[')[0]] = matches
        
        return assets
    
    def _check_responsive_design(self, response: str) -> bool:
        """Check if responsive design is considered"""
        responsive_indicators = [
            'responsive', 'mobile-first', 'breakpoint', '@media',
            'mobile', 'tablet', 'desktop', 'viewport'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in responsive_indicators)
    
    def _check_accessibility(self, response: str) -> bool:
        """Check if accessibility is considered"""
        a11y_indicators = [
            'accessibility', 'a11y', 'wcag', 'aria',
            'screen reader', 'keyboard navigation', 'contrast',
            'alt text', 'semantic html'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in a11y_indicators)
