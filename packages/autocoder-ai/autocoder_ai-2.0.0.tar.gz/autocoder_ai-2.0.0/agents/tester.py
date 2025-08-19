"""
Tester Agent - Testing and quality assurance
"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig

class TesterAgent(BaseAgent):
    """Agent responsible for testing and quality assurance"""
    
    def _format_task(self, task: str) -> str:
        """Format the task for the tester"""
        return f"""
TESTING TASK: {task}

As the Tester, create a comprehensive testing strategy. Provide:

1. TEST STRATEGY:
   - Testing approach and methodology
   - Test levels (unit, integration, system, acceptance)
   - Test types (functional, performance, security, usability)
   - Risk-based testing priorities

2. TEST CASES:
   - Detailed test scenarios
   - Positive and negative test cases
   - Edge cases and boundary conditions
   - Data validation tests

3. AUTOMATED TESTING:
   - Unit test implementations
   - Integration test setup
   - Test automation framework recommendations
   - Continuous testing pipeline

4. QUALITY ASSURANCE:
   - Code quality checks
   - Security testing approach
   - Performance testing strategy
   - Accessibility testing (if applicable)

5. TEST DATA:
   - Test data requirements
   - Data setup and teardown
   - Mock/stub configurations
   - Environment considerations

6. DEFECT MANAGEMENT:
   - Bug reporting process
   - Severity and priority classification
   - Testing metrics and KPIs
   - Quality gates and criteria

Provide specific test code examples and testing procedures.
"""
    
    def _process_response(self, response: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the tester's response"""
        try:
            # Extract testing components
            testing_plan = self._extract_testing_plan(response)
            
            return {
                'success': True,
                'agent': self.name,
                'output': response,
                'testing_plan': testing_plan,
                'test_files': self._extract_test_files(response),
                'quality_metrics': self._extract_quality_metrics(response),
                'metadata': {
                    'task': task,
                    'testing_completed': True,
                    'test_coverage_target': self._extract_coverage_target(response)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'output': response
            }
    
    def _extract_testing_plan(self, response: str) -> Dict[str, Any]:
        """Extract testing plan from the response"""
        plan = {
            'strategy': '',
            'test_cases': [],
            'automation': '',
            'quality_assurance': '',
            'test_data': '',
            'defect_management': ''
        }
        
        try:
            # Extract test strategy
            strategy_match = re.search(r'1\.\s*TEST STRATEGY[:\s]*(.*?)(?=2\.|$)', response, re.DOTALL | re.IGNORECASE)
            if strategy_match:
                plan['strategy'] = strategy_match.group(1).strip()
            
            # Extract test cases
            cases_match = re.search(r'2\.\s*TEST CASES[:\s]*(.*?)(?=3\.|$)', response, re.DOTALL | re.IGNORECASE)
            if cases_match:
                cases_text = cases_match.group(1).strip()
                # Extract individual test cases
                plan['test_cases'] = self._parse_test_cases(cases_text)
            
            # Extract automation approach
            automation_match = re.search(r'3\.\s*AUTOMATED TESTING[:\s]*(.*?)(?=4\.|$)', response, re.DOTALL | re.IGNORECASE)
            if automation_match:
                plan['automation'] = automation_match.group(1).strip()
            
            # Extract quality assurance
            qa_match = re.search(r'4\.\s*QUALITY ASSURANCE[:\s]*(.*?)(?=5\.|$)', response, re.DOTALL | re.IGNORECASE)
            if qa_match:
                plan['quality_assurance'] = qa_match.group(1).strip()
            
            # Extract test data requirements
            data_match = re.search(r'5\.\s*TEST DATA[:\s]*(.*?)(?=6\.|$)', response, re.DOTALL | re.IGNORECASE)
            if data_match:
                plan['test_data'] = data_match.group(1).strip()
            
        except Exception as e:
            plan['raw_response'] = response
        
        return plan
    
    def _parse_test_cases(self, cases_text: str) -> List[Dict[str, str]]:
        """Parse individual test cases from text"""
        test_cases = []
        
        # Look for test case patterns
        case_patterns = [
            r'Test Case \d+[:\-\s]*([^\n]+)\n([^T]*?)(?=Test Case|\Z)',
            r'TC\d+[:\-\s]*([^\n]+)\n([^T]*?)(?=TC|\Z)',
            r'(?:^|\n)\d+\.\s*([^\n]+)\n([^0-9]*?)(?=\n\d+\.|\Z)'
        ]
        
        for pattern in case_patterns:
            matches = re.findall(pattern, cases_text, re.DOTALL | re.MULTILINE)
            for title, description in matches:
                test_cases.append({
                    'title': title.strip(),
                    'description': description.strip()
                })
        
        return test_cases
    
    def _extract_test_files(self, response: str) -> List[Dict[str, str]]:
        """Extract test files from the response"""
        files = []
        
        # Look for test file patterns
        test_file_patterns = [
            r'(?:^|\n)(test_[a-zA-Z_][a-zA-Z0-9_]*\.py):\s*\n```python\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*_test\.py):\s*\n```python\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.test\.js):\s*\n```javascript\n(.*?)\n```',
        ]
        
        for pattern in test_file_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
            for filename, content in matches:
                files.append({
                    'filename': filename,
                    'content': content.strip(),
                    'type': 'test_file'
                })
        
        return files
    
    def _extract_quality_metrics(self, response: str) -> Dict[str, Any]:
        """Extract quality metrics from the response"""
        metrics = {}
        
        # Look for coverage targets
        coverage_match = re.search(r'coverage[:\s]*(\d+)%', response, re.IGNORECASE)
        if coverage_match:
            metrics['coverage_target'] = int(coverage_match.group(1))
        
        # Look for performance targets
        perf_patterns = [
            r'response time[:\s]*(?:less than\s*)?(\d+(?:\.\d+)?)\s*(ms|seconds?)',
            r'latency[:\s]*(?:under\s*)?(\d+(?:\.\d+)?)\s*(ms|seconds?)'
        ]
        
        for pattern in perf_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2)
                metrics['performance_target'] = {'value': value, 'unit': unit}
                break
        
        return metrics
    
    def _extract_coverage_target(self, response: str) -> int:
        """Extract test coverage target from response"""
        coverage_match = re.search(r'coverage[:\s]*(\d+)%', response, re.IGNORECASE)
        if coverage_match:
            return int(coverage_match.group(1))
        return 80  # Default target
