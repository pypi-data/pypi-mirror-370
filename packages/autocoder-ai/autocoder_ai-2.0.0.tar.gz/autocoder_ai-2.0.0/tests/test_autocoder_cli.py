"""
Comprehensive test suite for the Autocoder CLI
"""

import pytest
import click.testing
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Import the CLI
import sys
sys.path.append(str(Path(__file__).parent.parent))
from autocoder import cli


@pytest.fixture
def runner():
    """Create a Click test runner"""
    return click.testing.CliRunner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_memory():
    """Mock ProjectMemory"""
    with patch('autocoder.ProjectMemory') as mock:
        memory_instance = Mock()
        mock.return_value = memory_instance
        
        # Mock project data
        memory_instance.get_project.return_value = {
            'id': 'test-project-123',
            'name': 'Test Project',
            'status': 'active',
            'created_at': '2024-01-01T00:00:00'
        }
        
        memory_instance.create_project.return_value = {
            'id': 'new-project-456',
            'name': 'New Project',
            'status': 'active'
        }
        
        memory_instance.create_session.return_value = {
            'id': 'session-789',
            'project_id': 'test-project-123',
            'task_description': 'Test task',
            'status': 'running'
        }
        
        memory_instance.get_all_projects.return_value = [
            {'id': 'proj1', 'name': 'Project 1', 'status': 'active', 'created_at': '2024-01-01T00:00:00'},
            {'id': 'proj2', 'name': 'Project 2', 'status': 'completed', 'created_at': '2024-01-02T00:00:00'}
        ]
        
        memory_instance.get_project_sessions.return_value = [
            {
                'id': 'sess1',
                'task_description': 'Task 1',
                'status': 'completed',
                'files_created': ['file1.py'],
                'started_at': '2024-01-01T00:00:00'
            }
        ]
        
        yield memory_instance


@pytest.fixture
def mock_orchestrator():
    """Mock WorkflowOrchestrator"""
    with patch('autocoder.WorkflowOrchestrator') as mock:
        orchestrator_instance = Mock()
        mock.return_value = orchestrator_instance
        
        orchestrator_instance.execute_task.return_value = {
            'success': True,
            'agent_results': {
                'planner': {'success': True},
                'developer': {'success': True},
                'tester': {'success': True}
            },
            'files_created': ['output/main.py', 'output/test.py']
        }
        
        orchestrator_instance.agent_emitters = {}
        
        yield orchestrator_instance


@pytest.fixture
def mock_config_loader():
    """Mock ConfigLoader"""
    with patch('autocoder.ConfigLoader') as mock:
        config_instance = Mock()
        mock.return_value = config_instance
        config_instance.load.return_value = True
        config_instance.config = {'agents': {}, 'workflow': {}}
        yield config_instance


@pytest.fixture
def mock_websocket_client():
    """Mock CLIWebSocketClient"""
    with patch('autocoder.CLIWebSocketClient') as mock:
        client_instance = Mock()
        mock.return_value = client_instance
        
        # Mock async run method
        async def mock_run(session_id):
            await asyncio.sleep(0.1)
        
        client_instance.run = Mock(side_effect=mock_run)
        yield client_instance


class TestAutocoderCLI:
    """Test suite for Autocoder CLI"""
    
    def test_cli_help(self, runner):
        """Test CLI help command"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Autocoder' in result.output
        assert 'AI-Powered Multi-Agent Development System' in result.output
    
    def test_cli_version(self, runner):
        """Test CLI version command"""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '2.0.0' in result.output
    
    def test_run_command_basic(self, runner, temp_dir, mock_memory, 
                               mock_orchestrator, mock_config_loader):
        """Test basic run command"""
        with patch('autocoder.FileHandler'):
            result = runner.invoke(cli, [
                'run', 'Create a calculator',
                '--output-dir', temp_dir
            ])
            
            assert result.exit_code == 0
            assert 'Task completed successfully' in result.output
            mock_memory.create_session.assert_called_once()
            mock_orchestrator.execute_task.assert_called_once()
    
    def test_run_command_with_project(self, runner, temp_dir, mock_memory,
                                     mock_orchestrator, mock_config_loader):
        """Test run command with existing project"""
        with patch('autocoder.FileHandler'):
            result = runner.invoke(cli, [
                'run', 'Add feature',
                '--project', 'test-project-123',
                '--output-dir', temp_dir
            ])
            
            assert result.exit_code == 0
            mock_memory.get_project.assert_called_with('test-project-123')
    
    def test_run_command_with_monitor(self, runner, temp_dir, mock_memory,
                                     mock_orchestrator, mock_config_loader,
                                     mock_websocket_client):
        """Test run command with monitoring enabled"""
        with patch('autocoder.FileHandler'), \
             patch('autocoder.start_websocket_monitor') as mock_monitor, \
             patch('autocoder.WebSocketManager'):
            
            result = runner.invoke(cli, [
                'run', 'Create API',
                '--monitor',
                '--output-dir', temp_dir
            ])
            
            assert result.exit_code == 0
            mock_monitor.assert_called_once()
    
    def test_run_command_with_git(self, runner, temp_dir, mock_memory,
                                 mock_orchestrator, mock_config_loader):
        """Test run command with Git integration"""
        with patch('autocoder.FileHandler'), \
             patch('autocoder.GitManager') as mock_git:
            
            git_instance = Mock()
            mock_git.return_value = git_instance
            git_instance.init_repository.return_value = True
            
            result = runner.invoke(cli, [
                'run', 'Create app',
                '--enable-git',
                '--output-dir', temp_dir
            ])
            
            assert result.exit_code == 0
            assert 'Git repository initialized' in result.output
            git_instance.init_repository.assert_called_once()
    
    def test_run_command_dry_run(self, runner, temp_dir, mock_memory,
                                mock_orchestrator, mock_config_loader):
        """Test run command in dry-run mode"""
        with patch('autocoder.FileHandler'):
            result = runner.invoke(cli, [
                'run', 'Test task',
                '--dry-run',
                '--output-dir', temp_dir
            ])
            
            assert result.exit_code == 0
            # Verify dry_run was passed to orchestrator
            call_kwargs = mock_orchestrator.call_args[1]
            assert call_kwargs['dry_run'] == True
    
    def test_monitor_command(self, runner, mock_websocket_client):
        """Test monitor command"""
        with patch('asyncio.run'):
            result = runner.invoke(cli, ['monitor', 'session-123'])
            
            assert result.exit_code == 0
            assert 'Task Monitor' in result.output
            mock_websocket_client.run.assert_called()
    
    def test_projects_command(self, runner, mock_memory):
        """Test projects list command"""
        result = runner.invoke(cli, ['projects'])
        
        assert result.exit_code == 0
        assert 'Project 1' in result.output
        assert 'Project 2' in result.output
        mock_memory.get_all_projects.assert_called_once()
    
    def test_projects_command_with_filter(self, runner, mock_memory):
        """Test projects command with status filter"""
        result = runner.invoke(cli, ['projects', '--status', 'active'])
        
        assert result.exit_code == 0
        mock_memory.get_all_projects.assert_called_once()
    
    def test_projects_command_empty(self, runner, mock_memory):
        """Test projects command with no projects"""
        mock_memory.get_all_projects.return_value = []
        
        result = runner.invoke(cli, ['projects'])
        
        assert result.exit_code == 0
        assert 'No projects found' in result.output
    
    def test_sessions_command(self, runner, mock_memory):
        """Test sessions list command"""
        result = runner.invoke(cli, ['sessions', 'test-project-123'])
        
        assert result.exit_code == 0
        assert 'Task 1' in result.output
        mock_memory.get_project.assert_called_with('test-project-123')
        mock_memory.get_project_sessions.assert_called_with('test-project-123')
    
    def test_sessions_command_invalid_project(self, runner, mock_memory):
        """Test sessions command with invalid project"""
        mock_memory.get_project.return_value = None
        
        result = runner.invoke(cli, ['sessions', 'invalid-id'])
        
        assert result.exit_code == 1
        assert 'not found' in result.output
    
    def test_export_command_json(self, runner, temp_dir):
        """Test export command with JSON format"""
        with patch('autocoder.export_manager') as mock_export:
            mock_export.export_session_data.return_value = b'{"test": "data"}'
            
            output_file = os.path.join(temp_dir, 'export.json')
            result = runner.invoke(cli, [
                'export', 'session-123',
                '-f', 'json',
                '-o', output_file
            ])
            
            assert result.exit_code == 0
            assert 'Exported to' in result.output
            assert os.path.exists(output_file)
    
    def test_export_command_html(self, runner, temp_dir):
        """Test export command with HTML format"""
        with patch('autocoder.export_manager') as mock_export:
            mock_export.export_session_data.return_value = b'<html>Report</html>'
            
            output_file = os.path.join(temp_dir, 'export.html')
            result = runner.invoke(cli, [
                'export', 'session-123',
                '-f', 'html',
                '-o', output_file
            ])
            
            assert result.exit_code == 0
            assert os.path.exists(output_file)
    
    def test_export_command_zip(self, runner, temp_dir):
        """Test export command with ZIP format"""
        with patch('autocoder.export_manager') as mock_export:
            mock_export.export_session_data.return_value = b'ZIP_DATA'
            
            result = runner.invoke(cli, [
                'export', 'session-123',
                '-f', 'zip'
            ])
            
            assert result.exit_code == 0
            mock_export.export_session_data.assert_called_with('session-123', 'zip')
    
    def test_web_command(self, runner):
        """Test web server command"""
        with patch('uvicorn.run') as mock_uvicorn, \
             patch('autocoder.create_app') as mock_app:
            
            mock_app.return_value = MagicMock()
            
            # Simulate KeyboardInterrupt to stop server
            mock_uvicorn.side_effect = KeyboardInterrupt()
            
            result = runner.invoke(cli, ['web'])
            
            assert result.exit_code == 0
            assert 'Starting Web Interface' in result.output
            mock_uvicorn.assert_called_once()
    
    def test_web_command_custom_port(self, runner):
        """Test web command with custom port"""
        with patch('uvicorn.run') as mock_uvicorn, \
             patch('autocoder.create_app'):
            
            mock_uvicorn.side_effect = KeyboardInterrupt()
            
            result = runner.invoke(cli, ['web', '--port', '8080'])
            
            assert result.exit_code == 0
            call_kwargs = mock_uvicorn.call_args[1]
            assert call_kwargs['port'] == 8080
    
    def test_stats_command(self, runner):
        """Test stats command"""
        with patch('autocoder.export_manager') as mock_export:
            mock_export.generate_analytics_report.return_value = {
                'summary': {
                    'total_projects': 5,
                    'total_sessions': 10,
                    'total_files_created': 25
                },
                'session_stats': {
                    'completed': 8,
                    'failed': 1,
                    'running': 1
                },
                'performance': {
                    'average_duration_seconds': 120.5,
                    'success_rate': 80.0
                },
                'agents': {
                    'planner': 10,
                    'developer': 10,
                    'tester': 8
                }
            }
            
            result = runner.invoke(cli, ['stats'])
            
            assert result.exit_code == 0
            assert 'System Statistics' in result.output
            assert 'Projects: 5' in result.output
            assert 'Success Rate: 80.0%' in result.output
    
    def test_stats_command_project_specific(self, runner):
        """Test stats command for specific project"""
        with patch('autocoder.export_manager') as mock_export:
            mock_export.generate_analytics_report.return_value = {
                'summary': {'total_sessions': 3}
            }
            
            result = runner.invoke(cli, ['stats', '--project-id', 'proj-123'])
            
            assert result.exit_code == 0
            mock_export.generate_analytics_report.assert_called_with('proj-123')
    
    def test_error_handling_config_load_failure(self, runner, mock_memory):
        """Test error handling when config fails to load"""
        with patch('autocoder.ConfigLoader') as mock_config:
            config_instance = Mock()
            mock_config.return_value = config_instance
            config_instance.load.return_value = False
            
            result = runner.invoke(cli, ['run', 'Test task'])
            
            assert result.exit_code == 1
            assert 'Failed to load configuration' in result.output
    
    def test_error_handling_invalid_project(self, runner, mock_memory, mock_config_loader):
        """Test error handling with invalid project ID"""
        mock_memory.get_project.return_value = None
        
        with patch('autocoder.FileHandler'):
            result = runner.invoke(cli, [
                'run', 'Test task',
                '--project', 'invalid-id'
            ])
            
            assert result.exit_code == 1
            assert 'not found' in result.output
    
    def test_keyboard_interrupt_handling(self, runner, mock_memory, 
                                        mock_config_loader):
        """Test KeyboardInterrupt handling"""
        with patch('autocoder.FileHandler'), \
             patch('autocoder.WorkflowOrchestrator') as mock_orch:
            
            mock_orch.return_value.execute_task.side_effect = KeyboardInterrupt()
            
            result = runner.invoke(cli, ['run', 'Test task'])
            
            assert result.exit_code == 1
            assert 'Task interrupted' in result.output


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_display_results(self, capsys):
        """Test display_results function"""
        from autocoder import display_results
        
        result = {
            'agent_results': {
                'planner': {'success': True},
                'developer': {'success': False}
            },
            'files_created': ['file1.py', 'file2.py']
        }
        
        display_results(result)
        
        captured = capsys.readouterr()
        assert 'Execution Summary' in captured.out
        assert 'file1.py' in captured.out
    
    @pytest.mark.asyncio
    async def test_websocket_monitor_thread(self):
        """Test WebSocket monitor thread creation"""
        from autocoder import start_websocket_monitor
        
        with patch('autocoder.CLIWebSocketClient') as mock_client:
            client_instance = Mock()
            mock_client.return_value = client_instance
            
            # Mock async run
            async def mock_run(session_id):
                await asyncio.sleep(0.01)
            
            client_instance.run = Mock(side_effect=mock_run)
            
            thread = start_websocket_monitor('session-123', 'http://localhost:5001')
            
            assert thread is not None
            assert thread.daemon == True
            
            # Give thread time to start
            await asyncio.sleep(0.1)
            
            mock_client.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
