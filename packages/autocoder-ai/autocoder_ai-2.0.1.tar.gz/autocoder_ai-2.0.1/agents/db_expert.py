"""
DB Expert Agent - Database design and optimization
"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig

class DBExpertAgent(BaseAgent):
    """Agent responsible for database design and optimization"""
    
    def _format_task(self, task: str) -> str:
        """Format the task for the database expert"""
        return f"""
DATABASE DESIGN TASK: {task}

As the Database Expert, design the data architecture and storage solution. Provide:

1. DATA ARCHITECTURE:
   - Data modeling approach (relational, NoSQL, hybrid)
   - Entity relationship design
   - Data flow and relationships
   - Normalization strategy

2. DATABASE SCHEMA:
   - Table/collection structures
   - Primary and foreign keys
   - Indexes and constraints
   - Data types and validation rules

3. PERFORMANCE OPTIMIZATION:
   - Query optimization strategies
   - Indexing recommendations
   - Caching mechanisms
   - Partitioning considerations

4. SCALABILITY DESIGN:
   - Horizontal vs vertical scaling
   - Sharding strategies
   - Replication setup
   - Load balancing approaches

5. DATA SECURITY:
   - Access control and permissions
   - Data encryption strategies
   - Backup and recovery plans
   - Audit logging requirements

6. IMPLEMENTATION:
   - Database setup scripts
   - Migration strategies
   - Connection pooling
   - ORM/ODM recommendations

Provide specific SQL/NoSQL schemas and implementation code.
"""
    
    def _process_response(self, response: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the database expert's response"""
        try:
            # Extract database components
            db_design = self._extract_db_design(response)
            
            return {
                'success': True,
                'agent': self.name,
                'output': response,
                'db_design': db_design,
                'schema_files': self._extract_schema_files(response),
                'migration_scripts': self._extract_migration_scripts(response),
                'metadata': {
                    'task': task,
                    'database_designed': True,
                    'db_type': self._detect_database_type(response),
                    'scalability_considered': self._check_scalability(response)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'output': response
            }
    
    def _extract_db_design(self, response: str) -> Dict[str, Any]:
        """Extract database design from the response"""
        design = {
            'architecture': '',
            'schema': '',
            'performance': '',
            'scalability': '',
            'security': '',
            'implementation': ''
        }
        
        try:
            # Extract data architecture
            arch_match = re.search(r'1\.\s*DATA ARCHITECTURE[:\s]*(.*?)(?=2\.|$)', response, re.DOTALL | re.IGNORECASE)
            if arch_match:
                design['architecture'] = arch_match.group(1).strip()
            
            # Extract database schema
            schema_match = re.search(r'2\.\s*DATABASE SCHEMA[:\s]*(.*?)(?=3\.|$)', response, re.DOTALL | re.IGNORECASE)
            if schema_match:
                design['schema'] = schema_match.group(1).strip()
            
            # Extract performance optimization
            perf_match = re.search(r'3\.\s*PERFORMANCE OPTIMIZATION[:\s]*(.*?)(?=4\.|$)', response, re.DOTALL | re.IGNORECASE)
            if perf_match:
                design['performance'] = perf_match.group(1).strip()
            
            # Extract scalability design
            scale_match = re.search(r'4\.\s*SCALABILITY DESIGN[:\s]*(.*?)(?=5\.|$)', response, re.DOTALL | re.IGNORECASE)
            if scale_match:
                design['scalability'] = scale_match.group(1).strip()
            
            # Extract data security
            security_match = re.search(r'5\.\s*DATA SECURITY[:\s]*(.*?)(?=6\.|$)', response, re.DOTALL | re.IGNORECASE)
            if security_match:
                design['security'] = security_match.group(1).strip()
            
            # Extract implementation
            impl_match = re.search(r'6\.\s*IMPLEMENTATION[:\s]*(.*?)(?=\Z)', response, re.DOTALL | re.IGNORECASE)
            if impl_match:
                design['implementation'] = impl_match.group(1).strip()
            
        except Exception as e:
            design['raw_response'] = response
        
        return design
    
    def _extract_schema_files(self, response: str) -> List[Dict[str, str]]:
        """Extract database schema files from the response"""
        files = []
        
        # Look for SQL and schema file patterns
        schema_patterns = [
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.sql):\s*\n```sql\n(.*?)\n```',
            r'(?:^|\n)(schema\.sql):\s*\n```sql\n(.*?)\n```',
            r'(?:^|\n)(migrations?/[a-zA-Z0-9_]+\.sql):\s*\n```sql\n(.*?)\n```',
            r'(?:^|\n)([a-zA-Z_][a-zA-Z0-9_]*\.json):\s*\n```json\n(.*?)\n```',  # NoSQL schemas
        ]
        
        for pattern in schema_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
            for filename, content in matches:
                files.append({
                    'filename': filename,
                    'content': content.strip(),
                    'type': 'schema',
                    'language': filename.split('.')[-1]
                })
        
        return files
    
    def _extract_migration_scripts(self, response: str) -> List[Dict[str, str]]:
        """Extract migration scripts from the response"""
        scripts = []
        
        # Look for migration patterns
        migration_patterns = [
            r'(?:migration|migrate)[^\n]*:\s*\n```sql\n(.*?)\n```',
            r'(?:^|\n)((?:up|down)_migration[a-zA-Z0-9_]*\.sql):\s*\n```sql\n(.*?)\n```',
            r'CREATE TABLE[^;]+;',
            r'ALTER TABLE[^;]+;',
            r'DROP TABLE[^;]+;'
        ]
        
        for pattern in migration_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE | re.IGNORECASE)
            for i, match in enumerate(matches):
                if isinstance(match, tuple):
                    filename, content = match
                else:
                    filename = f"migration_{i+1}.sql"
                    content = match
                
                scripts.append({
                    'filename': filename,
                    'content': content.strip(),
                    'type': 'migration'
                })
        
        return scripts
    
    def _detect_database_type(self, response: str) -> str:
        """Detect the type of database being used"""
        response_lower = response.lower()
        
        # SQL databases
        if any(db in response_lower for db in ['mysql', 'postgresql', 'postgres', 'sqlite', 'oracle', 'sql server']):
            return 'sql'
        
        # NoSQL databases
        elif any(db in response_lower for db in ['mongodb', 'cassandra', 'redis', 'dynamodb', 'couchdb']):
            return 'nosql'
        
        # Graph databases
        elif any(db in response_lower for db in ['neo4j', 'amazon neptune', 'arangodb']):
            return 'graph'
        
        # Default to SQL if not specified
        return 'sql'
    
    def _check_scalability(self, response: str) -> bool:
        """Check if scalability is considered in the design"""
        scalability_indicators = [
            'scaling', 'scalability', 'sharding', 'partitioning',
            'replication', 'clustering', 'load balancing',
            'horizontal scaling', 'vertical scaling'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in scalability_indicators)
