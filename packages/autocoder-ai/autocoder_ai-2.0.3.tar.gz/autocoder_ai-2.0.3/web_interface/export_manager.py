"""
Export manager for task logs, metrics, and timeline data
"""

import json
import csv
import io
import zipfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from jinja2 import Template

from memory.project_memory import ProjectMemory
from utils.logger import setup_logger

logger = setup_logger()


class ExportManager:
    """Manages export of task data in various formats"""
    
    def __init__(self):
        self.memory = ProjectMemory()
        
    def export_session_data(self, session_id: str, format: str = "json") -> Optional[bytes]:
        """
        Export session data in specified format
        
        Args:
            session_id: Session ID to export
            format: Export format (json, csv, html, markdown, zip)
            
        Returns:
            Exported data as bytes
        """
        try:
            # Get session data
            session = self.memory.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return None
            
            # Get session logs
            logs = self.memory.get_session_logs(session_id)
            
            # Prepare data
            export_data = {
                "session": session,
                "logs": logs,
                "exported_at": datetime.utcnow().isoformat()
            }
            
            # Export based on format
            if format == "json":
                return self._export_json(export_data)
            elif format == "csv":
                return self._export_csv(export_data)
            elif format == "html":
                return self._export_html(export_data)
            elif format == "markdown":
                return self._export_markdown(export_data)
            elif format == "zip":
                return self._export_zip(export_data)
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to export session data: {e}")
            return None
    
    def _export_json(self, data: Dict[str, Any]) -> bytes:
        """Export data as JSON"""
        return json.dumps(data, indent=2, default=str).encode('utf-8')
    
    def _export_csv(self, data: Dict[str, Any]) -> bytes:
        """Export data as CSV"""
        output = io.StringIO()
        
        # Session info
        session_writer = csv.writer(output)
        session_writer.writerow(["Session Information"])
        session_writer.writerow(["Field", "Value"])
        
        session = data["session"]
        session_writer.writerow(["ID", session.get("id")])
        session_writer.writerow(["Project ID", session.get("project_id")])
        session_writer.writerow(["Task Description", session.get("task_description")])
        session_writer.writerow(["Status", session.get("status")])
        session_writer.writerow(["Started At", session.get("started_at")])
        session_writer.writerow(["Completed At", session.get("completed_at")])
        session_writer.writerow([])
        
        # Logs
        session_writer.writerow(["Session Logs"])
        session_writer.writerow(["Timestamp", "Agent", "Level", "Message"])
        
        for log in data.get("logs", []):
            session_writer.writerow([
                log.get("timestamp"),
                log.get("agent"),
                log.get("level"),
                log.get("message")
            ])
        
        return output.getvalue().encode('utf-8')
    
    def _export_html(self, data: Dict[str, Any]) -> bytes:
        """Export data as HTML report"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Task Report - {{ session.id }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .info-table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        .info-table th, .info-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .info-table th { background-color: #f2f2f2; }
        .log-entry { margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; background: #f9f9f9; }
        .log-time { color: #666; font-size: 0.9em; }
        .log-agent { font-weight: bold; color: #007bff; }
        .status-completed { color: green; }
        .status-failed { color: red; }
        .status-running { color: orange; }
    </style>
</head>
<body>
    <h1>Task Execution Report</h1>
    
    <h2>Session Information</h2>
    <table class="info-table">
        <tr><th>Session ID</th><td>{{ session.id }}</td></tr>
        <tr><th>Project ID</th><td>{{ session.project_id }}</td></tr>
        <tr><th>Task Description</th><td>{{ session.task_description }}</td></tr>
        <tr><th>Status</th><td class="status-{{ session.status }}">{{ session.status }}</td></tr>
        <tr><th>Started At</th><td>{{ session.started_at }}</td></tr>
        <tr><th>Completed At</th><td>{{ session.completed_at or 'N/A' }}</td></tr>
    </table>
    
    <h2>Files Created</h2>
    {% if session.files_created %}
    <ul>
        {% for file in session.files_created %}
        <li>{{ file }}</li>
        {% endfor %}
    </ul>
    {% else %}
    <p>No files created</p>
    {% endif %}
    
    <h2>Execution Timeline</h2>
    {% for log in logs %}
    <div class="log-entry">
        <span class="log-time">{{ log.timestamp }}</span> - 
        <span class="log-agent">{{ log.agent }}</span>: 
        {{ log.message }}
    </div>
    {% endfor %}
    
    <hr>
    <p><small>Report generated at {{ exported_at }}</small></p>
</body>
</html>
"""
        template = Template(html_template)
        html = template.render(**data)
        return html.encode('utf-8')
    
    def _export_markdown(self, data: Dict[str, Any]) -> bytes:
        """Export data as Markdown"""
        md_template = """# Task Execution Report

## Session Information

| Field | Value |
|-------|-------|
| Session ID | {{ session.id }} |
| Project ID | {{ session.project_id }} |
| Task Description | {{ session.task_description }} |
| Status | {{ session.status }} |
| Started At | {{ session.started_at }} |
| Completed At | {{ session.completed_at or 'N/A' }} |

## Files Created

{% if session.files_created %}
{% for file in session.files_created %}
- `{{ file }}`
{% endfor %}
{% else %}
No files created
{% endif %}

## Execution Timeline

{% for log in logs %}
**{{ log.timestamp }}** - *{{ log.agent }}*: {{ log.message }}
{% endfor %}

---

*Report generated at {{ exported_at }}*
"""
        template = Template(md_template)
        markdown = template.render(**data)
        return markdown.encode('utf-8')
    
    def _export_zip(self, data: Dict[str, Any]) -> bytes:
        """Export data as ZIP archive with multiple formats"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add JSON
            zip_file.writestr(
                f"session_{data['session']['id']}.json",
                self._export_json(data)
            )
            
            # Add CSV
            zip_file.writestr(
                f"session_{data['session']['id']}.csv",
                self._export_csv(data)
            )
            
            # Add HTML
            zip_file.writestr(
                f"session_{data['session']['id']}.html",
                self._export_html(data)
            )
            
            # Add Markdown
            zip_file.writestr(
                f"session_{data['session']['id']}.md",
                self._export_markdown(data)
            )
            
            # Add agent results if available
            if data['session'].get('result'):
                zip_file.writestr(
                    "agent_results.json",
                    json.dumps(data['session']['result'], indent=2, default=str)
                )
        
        return zip_buffer.getvalue()
    
    def export_project_metrics(self, project_id: str) -> Dict[str, Any]:
        """
        Export aggregate metrics for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Project metrics dictionary
        """
        try:
            sessions = self.memory.get_project_sessions(project_id)
            
            metrics = {
                "project_id": project_id,
                "total_sessions": len(sessions),
                "completed_sessions": sum(1 for s in sessions if s.get("status") == "completed"),
                "failed_sessions": sum(1 for s in sessions if s.get("status") == "failed"),
                "running_sessions": sum(1 for s in sessions if s.get("status") == "running"),
                "total_files_created": sum(len(s.get("files_created", [])) for s in sessions),
                "average_duration": self._calculate_average_duration(sessions),
                "agents_used": self._get_agents_used(sessions),
                "exported_at": datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to export project metrics: {e}")
            return {}
    
    def _calculate_average_duration(self, sessions: List[Dict]) -> float:
        """Calculate average session duration in seconds"""
        durations = []
        
        for session in sessions:
            if session.get("started_at") and session.get("completed_at"):
                try:
                    start = datetime.fromisoformat(session["started_at"])
                    end = datetime.fromisoformat(session["completed_at"])
                    duration = (end - start).total_seconds()
                    durations.append(duration)
                except:
                    pass
        
        return sum(durations) / len(durations) if durations else 0
    
    def _get_agents_used(self, sessions: List[Dict]) -> Dict[str, int]:
        """Get count of each agent used across sessions"""
        agent_counts = {}
        
        for session in sessions:
            if session.get("result") and session["result"].get("agent_results"):
                for agent in session["result"]["agent_results"].keys():
                    agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        return agent_counts
    
    def generate_analytics_report(self, project_id: str = None) -> Dict[str, Any]:
        """
        Generate analytics report for project or system-wide
        
        Args:
            project_id: Optional project ID (None for system-wide)
            
        Returns:
            Analytics report dictionary
        """
        try:
            if project_id:
                sessions = self.memory.get_project_sessions(project_id)
                projects = [self.memory.get_project(project_id)]
            else:
                # Get all sessions and projects
                projects = self.memory.get_all_projects()
                sessions = []
                for project in projects:
                    sessions.extend(self.memory.get_project_sessions(project["id"]))
            
            report = {
                "summary": {
                    "total_projects": len(projects),
                    "total_sessions": len(sessions),
                    "total_files_created": sum(len(s.get("files_created", [])) for s in sessions),
                },
                "session_stats": {
                    "completed": sum(1 for s in sessions if s.get("status") == "completed"),
                    "failed": sum(1 for s in sessions if s.get("status") == "failed"),
                    "running": sum(1 for s in sessions if s.get("status") == "running"),
                },
                "performance": {
                    "average_duration_seconds": self._calculate_average_duration(sessions),
                    "success_rate": (sum(1 for s in sessions if s.get("status") == "completed") / 
                                   len(sessions) * 100) if sessions else 0,
                },
                "agents": self._get_agents_used(sessions),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {e}")
            return {}


# Global export manager instance
export_manager = ExportManager()
