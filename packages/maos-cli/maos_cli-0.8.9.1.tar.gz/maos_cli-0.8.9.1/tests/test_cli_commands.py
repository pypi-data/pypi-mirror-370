"""
Tests for MAOS CLI commands.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock, AsyncMock
import json
import tempfile
import os

from src.maos.cli.main import cli
from src.maos.cli.commands.agent import agent_group
from src.maos.cli.commands.task import task_group
from src.maos.cli.commands.status import status_command
from src.maos.cli.commands.recover import recover_command
from src.maos.models.agent import Agent, AgentStatus


class TestCLIMain:
    """Test main CLI functionality."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Multi-Agent Orchestration System' in result.output
    
    def test_cli_version(self, runner):
        """Test CLI version command."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'version' in result.output.lower()


class TestAgentCommands:
    """Test agent-related CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @patch('src.maos.cli.commands.agent.AgentManager')
    def test_agent_create(self, mock_manager_class, runner):
        """Test creating an agent via CLI."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        mock_agent = Agent(name="TestAgent", type="worker")
        mock_manager.create_agent = AsyncMock(return_value=mock_agent)
        
        result = runner.invoke(cli, [
            'agent', 'create',
            '--name', 'TestAgent',
            '--type', 'worker',
            '--capabilities', 'task_execution,data_processing'
        ])
        
        assert result.exit_code == 0
        assert 'TestAgent' in result.output
        assert 'created successfully' in result.output.lower()
    
    @patch('src.maos.cli.commands.agent.AgentManager')
    def test_agent_list(self, mock_manager_class, runner):
        """Test listing agents via CLI."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        mock_agents = [
            Agent(name="Agent1", type="worker", status=AgentStatus.IDLE),
            Agent(name="Agent2", type="coordinator", status=AgentStatus.BUSY),
            Agent(name="Agent3", type="worker", status=AgentStatus.IDLE)
        ]
        mock_manager.list_agents = AsyncMock(return_value=mock_agents)
        
        result = runner.invoke(cli, ['agent', 'list'])
        
        assert result.exit_code == 0
        assert 'Agent1' in result.output
        assert 'Agent2' in result.output
        assert 'Agent3' in result.output
        assert 'IDLE' in result.output
        assert 'BUSY' in result.output
    
    @patch('src.maos.cli.commands.agent.AgentManager')
    def test_agent_status(self, mock_manager_class, runner):
        """Test getting agent status via CLI."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        mock_agent = Agent(
            name="TestAgent",
            type="worker",
            status=AgentStatus.BUSY,
            current_task_id="task123"
        )
        mock_manager.get_agent = AsyncMock(return_value=mock_agent)
        
        result = runner.invoke(cli, ['agent', 'status', 'agent123'])
        
        assert result.exit_code == 0
        assert 'TestAgent' in result.output
        assert 'BUSY' in result.output
        assert 'task123' in result.output
    
    @patch('src.maos.cli.commands.agent.AgentManager')
    def test_agent_delete(self, mock_manager_class, runner):
        """Test deleting an agent via CLI."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        mock_manager.delete_agent = AsyncMock(return_value=True)
        
        result = runner.invoke(cli, ['agent', 'delete', 'agent123', '--force'])
        
        assert result.exit_code == 0
        assert 'deleted successfully' in result.output.lower()


class TestTaskCommands:
    """Test task-related CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @patch('src.maos.cli.commands.task.Orchestrator')
    def test_task_execute(self, mock_orchestrator_class, runner):
        """Test executing a task via CLI."""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_result = {
            'task_id': 'task123',
            'status': 'completed',
            'result': 'Task completed successfully'
        }
        mock_orchestrator.execute_task = AsyncMock(return_value=mock_result)
        
        result = runner.invoke(cli, [
            'task', 'execute',
            '--name', 'Test Task',
            '--description', 'A test task',
            '--priority', 'high'
        ])
        
        assert result.exit_code == 0
        assert 'task123' in result.output
        assert 'completed' in result.output.lower()
    
    @patch('src.maos.cli.commands.task.Orchestrator')
    def test_task_execute_with_params(self, mock_orchestrator_class, runner):
        """Test executing a task with parameters via CLI."""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_orchestrator.execute_task = AsyncMock(return_value={'task_id': 'task123'})
        
        params = {'key1': 'value1', 'key2': 'value2'}
        result = runner.invoke(cli, [
            'task', 'execute',
            '--name', 'Test Task',
            '--params', json.dumps(params)
        ])
        
        assert result.exit_code == 0
        mock_orchestrator.execute_task.assert_called_once()
        call_args = mock_orchestrator.execute_task.call_args[0][0]
        assert call_args['parameters'] == params
    
    @patch('src.maos.cli.commands.task.TaskPlanner')
    def test_task_list(self, mock_planner_class, runner):
        """Test listing tasks via CLI."""
        mock_planner = MagicMock()
        mock_planner_class.return_value = mock_planner
        
        mock_tasks = [
            {'id': 'task1', 'name': 'Task 1', 'status': 'pending'},
            {'id': 'task2', 'name': 'Task 2', 'status': 'running'},
            {'id': 'task3', 'name': 'Task 3', 'status': 'completed'}
        ]
        mock_planner.list_tasks = AsyncMock(return_value=mock_tasks)
        
        result = runner.invoke(cli, ['task', 'list'])
        
        assert result.exit_code == 0
        assert 'Task 1' in result.output
        assert 'Task 2' in result.output
        assert 'Task 3' in result.output
        assert 'pending' in result.output
        assert 'running' in result.output
        assert 'completed' in result.output
    
    @patch('src.maos.cli.commands.task.TaskPlanner')
    def test_task_cancel(self, mock_planner_class, runner):
        """Test canceling a task via CLI."""
        mock_planner = MagicMock()
        mock_planner_class.return_value = mock_planner
        
        mock_planner.cancel_task = AsyncMock(return_value=True)
        
        result = runner.invoke(cli, ['task', 'cancel', 'task123'])
        
        assert result.exit_code == 0
        assert 'canceled successfully' in result.output.lower()


class TestStatusCommand:
    """Test status command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @patch('src.maos.cli.commands.status.Orchestrator')
    def test_status_command(self, mock_orchestrator_class, runner):
        """Test status command."""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_status = {
            'orchestrator': {'status': 'running', 'uptime': '2h 30m'},
            'agents': {
                'total': 5,
                'idle': 2,
                'busy': 3,
                'offline': 0
            },
            'tasks': {
                'total': 10,
                'pending': 2,
                'running': 3,
                'completed': 5
            },
            'system': {
                'cpu_percent': 45.5,
                'memory_percent': 62.3,
                'disk_usage': 78.9
            }
        }
        mock_orchestrator.get_status = AsyncMock(return_value=mock_status)
        
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert 'Orchestrator Status' in result.output
        assert 'running' in result.output
        assert 'Agents' in result.output
        assert 'Tasks' in result.output
        assert 'System Resources' in result.output


class TestRecoverCommand:
    """Test recover command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @patch('src.maos.cli.commands.recover.Orchestrator')
    def test_recover_from_checkpoint(self, mock_orchestrator_class, runner):
        """Test recovering from checkpoint."""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_orchestrator.recover_from_checkpoint = AsyncMock(return_value=True)
        
        result = runner.invoke(cli, ['recover', '--checkpoint', 'checkpoint123'])
        
        assert result.exit_code == 0
        assert 'Recovery successful' in result.output
    
    @patch('src.maos.cli.commands.recover.Orchestrator')
    def test_recover_latest(self, mock_orchestrator_class, runner):
        """Test recovering from latest checkpoint."""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_orchestrator.recover_latest = AsyncMock(return_value=True)
        
        result = runner.invoke(cli, ['recover', '--latest'])
        
        assert result.exit_code == 0
        assert 'Recovery successful' in result.output


class TestNaturalLanguage:
    """Test natural language command processing."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @patch('src.maos.cli.natural_language.NaturalLanguageProcessor')
    def test_chat_command(self, mock_nlp_class, runner):
        """Test chat/natural language command."""
        mock_nlp = MagicMock()
        mock_nlp_class.return_value = mock_nlp
        
        mock_nlp.process = AsyncMock(return_value={
            'command': 'task execute',
            'parameters': {'name': 'Test Task'},
            'confidence': 0.95
        })
        
        with patch('src.maos.cli.main.Orchestrator') as mock_orch:
            mock_orch.return_value.execute_task = AsyncMock(
                return_value={'task_id': 'task123'}
            )
            
            result = runner.invoke(cli, ['chat', 'create a test task'])
            
            assert result.exit_code == 0
            assert 'task123' in result.output or 'Task' in result.output


class TestConfigCommands:
    """Test configuration-related commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    def test_config_show(self, runner):
        """Test showing configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                'orchestrator': {'max_agents': 10},
                'storage': {'type': 'sqlite'}
            }
            json.dump(config, f)
            config_file = f.name
        
        try:
            with patch.dict(os.environ, {'MAOS_CONFIG': config_file}):
                result = runner.invoke(cli, ['config', 'show'])
                assert result.exit_code == 0
                assert 'max_agents' in result.output
                assert 'sqlite' in result.output
        finally:
            os.unlink(config_file)
    
    def test_config_set(self, runner):
        """Test setting configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            config_file = f.name
        
        try:
            with patch.dict(os.environ, {'MAOS_CONFIG': config_file}):
                result = runner.invoke(cli, [
                    'config', 'set',
                    'orchestrator.max_agents', '20'
                ])
                assert result.exit_code == 0
                
                with open(config_file) as f:
                    config = json.load(f)
                    assert config['orchestrator']['max_agents'] == 20
        finally:
            os.unlink(config_file)


class TestErrorHandling:
    """Test CLI error handling."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    def test_invalid_command(self, runner):
        """Test handling of invalid command."""
        result = runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0
        assert 'Error' in result.output or 'No such command' in result.output
    
    @patch('src.maos.cli.commands.agent.AgentManager')
    def test_agent_not_found(self, mock_manager_class, runner):
        """Test handling of agent not found."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        mock_manager.get_agent = AsyncMock(return_value=None)
        
        result = runner.invoke(cli, ['agent', 'status', 'nonexistent'])
        assert result.exit_code != 0
        assert 'not found' in result.output.lower()
    
    @patch('src.maos.cli.commands.task.Orchestrator')
    def test_task_execution_failure(self, mock_orchestrator_class, runner):
        """Test handling of task execution failure."""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_orchestrator.execute_task = AsyncMock(
            side_effect=Exception("Task execution failed")
        )
        
        result = runner.invoke(cli, [
            'task', 'execute',
            '--name', 'Failing Task'
        ])
        
        assert result.exit_code != 0
        assert 'failed' in result.output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])