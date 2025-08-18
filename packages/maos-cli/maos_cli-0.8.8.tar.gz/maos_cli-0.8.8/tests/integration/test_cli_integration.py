"""
Comprehensive integration tests for MAOS CLI commands.
"""

import pytest
import asyncio
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from click.testing import CliRunner
from uuid import uuid4

from maos.cli.main import cli
from maos.core.orchestrator import Orchestrator
from maos.models.task import Task, TaskStatus, TaskPriority
from maos.models.agent import Agent, AgentStatus


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create necessary subdirectories
        Path(tmpdir, '.maos').mkdir(exist_ok=True)
        Path(tmpdir, 'maos_storage').mkdir(exist_ok=True)
        
        # Create a basic config file
        config = {
            'project_name': 'test_project',
            'storage_directory': str(Path(tmpdir, 'maos_storage')),
            'enable_monitoring': False,
            'claude_integration': {
                'enabled': False
            }
        }
        
        config_path = Path(tmpdir, '.maos', 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        yield tmpdir


class TestInitCommand:
    """Test the init command."""
    
    def test_init_new_project(self, runner, temp_project_dir):
        """Test initializing a new MAOS project."""
        with runner.isolated_filesystem(temp=True) as td:
            result = runner.invoke(cli, ['init', '--name', 'test_project'])
            
            assert result.exit_code == 0
            assert 'Initializing MAOS project' in result.output
            assert Path('.maos').exists()
            assert Path('.maos/config.json').exists()
    
    def test_init_with_options(self, runner):
        """Test init with various options."""
        with runner.isolated_filesystem(temp=True):
            result = runner.invoke(cli, [
                'init',
                '--name', 'advanced_project',
                '--storage-dir', './custom_storage',
                '--enable-monitoring',
                '--enable-claude'
            ])
            
            assert result.exit_code == 0
            
            # Verify config file
            with open('.maos/config.json', 'r') as f:
                config = json.load(f)
            
            assert config['project_name'] == 'advanced_project'
            assert config['storage_directory'] == './custom_storage'
            assert config['enable_monitoring'] is True
            assert config['claude_integration']['enabled'] is True
    
    def test_init_existing_project(self, runner):
        """Test initializing in a directory with existing project."""
        with runner.isolated_filesystem(temp=True):
            # First init
            runner.invoke(cli, ['init', '--name', 'project1'])
            
            # Second init should warn
            result = runner.invoke(cli, ['init', '--name', 'project2'])
            
            assert 'already exists' in result.output.lower()


class TestStatusCommand:
    """Test the status command."""
    
    def test_status_no_project(self, runner):
        """Test status when no project exists."""
        with runner.isolated_filesystem(temp=True):
            result = runner.invoke(cli, ['status'])
            
            assert result.exit_code != 0
            assert 'No MAOS project found' in result.output
    
    @patch('maos.cli.commands.status.load_orchestrator')
    async def test_status_running(self, mock_load, runner, temp_project_dir):
        """Test status with running orchestrator."""
        # Mock orchestrator
        mock_orch = AsyncMock()
        mock_orch.get_system_status.return_value = {
            'running': True,
            'uptime_seconds': 3600,
            'components': {
                'state_manager': 'running',
                'message_bus': 'running',
                'agent_manager': 'running'
            }
        }
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert 'System Status' in result.output
        assert 'Running' in result.output
    
    @patch('maos.cli.commands.status.load_orchestrator')
    async def test_status_verbose(self, mock_load, runner, temp_project_dir):
        """Test verbose status output."""
        mock_orch = AsyncMock()
        mock_orch.get_system_status.return_value = {
            'running': True,
            'uptime_seconds': 1800,
            'components': {}
        }
        mock_orch.get_system_metrics.return_value = {
            'orchestrator': {
                'tasks_submitted': 10,
                'tasks_completed': 8,
                'tasks_failed': 2
            }
        }
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['status', '--verbose'])
        
        assert result.exit_code == 0
        assert 'Metrics' in result.output
        assert 'tasks_submitted' in result.output


class TestAgentCommands:
    """Test agent-related commands."""
    
    @patch('maos.cli.commands.agent.load_orchestrator')
    async def test_agent_list(self, mock_load, runner, temp_project_dir):
        """Test listing agents."""
        mock_orch = AsyncMock()
        mock_orch.get_available_agents.return_value = [
            Agent(name="Agent1", type="worker"),
            Agent(name="Agent2", type="monitor")
        ]
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['agent', 'list'])
        
        assert result.exit_code == 0
        assert 'Agent1' in result.output
        assert 'Agent2' in result.output
        assert 'worker' in result.output
        assert 'monitor' in result.output
    
    @patch('maos.cli.commands.agent.load_orchestrator')
    async def test_agent_spawn(self, mock_load, runner, temp_project_dir):
        """Test spawning a new agent."""
        mock_orch = AsyncMock()
        mock_agent = Agent(name="NewAgent", type="worker")
        mock_orch.create_agent.return_value = mock_agent
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'agent', 'spawn',
            '--type', 'worker',
            '--name', 'NewAgent'
        ])
        
        assert result.exit_code == 0
        assert 'Agent spawned successfully' in result.output
        assert 'NewAgent' in result.output
    
    @patch('maos.cli.commands.agent.load_orchestrator')
    async def test_agent_terminate(self, mock_load, runner, temp_project_dir):
        """Test terminating an agent."""
        mock_orch = AsyncMock()
        mock_orch.terminate_agent.return_value = True
        mock_load.return_value = mock_orch
        
        agent_id = str(uuid4())
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'agent', 'terminate',
            agent_id,
            '--reason', 'Test termination'
        ])
        
        assert result.exit_code == 0
        assert 'terminated successfully' in result.output
    
    @patch('maos.cli.commands.agent.load_orchestrator')
    async def test_agent_info(self, mock_load, runner, temp_project_dir):
        """Test getting agent info."""
        mock_orch = AsyncMock()
        agent_id = uuid4()
        mock_orch.get_agent.return_value = Agent(
            id=agent_id,
            name="TestAgent",
            type="worker",
            status=AgentStatus.IDLE
        )
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['agent', 'info', str(agent_id)])
        
        assert result.exit_code == 0
        assert 'TestAgent' in result.output
        assert 'IDLE' in result.output


class TestTaskCommands:
    """Test task-related commands."""
    
    @patch('maos.cli.commands.task.load_orchestrator')
    async def test_task_submit(self, mock_load, runner, temp_project_dir):
        """Test submitting a task."""
        mock_orch = AsyncMock()
        mock_plan = Mock(id=uuid4())
        mock_orch.submit_task.return_value = mock_plan
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'task', 'submit',
            '--name', 'TestTask',
            '--description', 'A test task',
            '--priority', 'high'
        ])
        
        assert result.exit_code == 0
        assert 'Task submitted successfully' in result.output
    
    @patch('maos.cli.commands.task.load_orchestrator')
    async def test_task_list(self, mock_load, runner, temp_project_dir):
        """Test listing tasks."""
        mock_orch = AsyncMock()
        mock_orch.state_manager.get_objects.return_value = [
            Task(name="Task1", description="First task", status=TaskStatus.PENDING),
            Task(name="Task2", description="Second task", status=TaskStatus.RUNNING)
        ]
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['task', 'list'])
        
        assert result.exit_code == 0
        assert 'Task1' in result.output
        assert 'Task2' in result.output
        assert 'PENDING' in result.output
        assert 'RUNNING' in result.output
    
    @patch('maos.cli.commands.task.load_orchestrator')
    async def test_task_status(self, mock_load, runner, temp_project_dir):
        """Test getting task status."""
        mock_orch = AsyncMock()
        task_id = uuid4()
        mock_orch.get_task.return_value = Task(
            id=task_id,
            name="TestTask",
            status=TaskStatus.COMPLETED,
            result={'success': True}
        )
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['task', 'status', str(task_id)])
        
        assert result.exit_code == 0
        assert 'TestTask' in result.output
        assert 'COMPLETED' in result.output
    
    @patch('maos.cli.commands.task.load_orchestrator')
    async def test_task_cancel(self, mock_load, runner, temp_project_dir):
        """Test canceling a task."""
        mock_orch = AsyncMock()
        mock_orch.cancel_task.return_value = True
        mock_load.return_value = mock_orch
        
        task_id = str(uuid4())
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'task', 'cancel',
            task_id,
            '--reason', 'Test cancellation'
        ])
        
        assert result.exit_code == 0
        assert 'cancelled successfully' in result.output
    
    @patch('maos.cli.commands.task.load_orchestrator')
    async def test_task_retry(self, mock_load, runner, temp_project_dir):
        """Test retrying a failed task."""
        mock_orch = AsyncMock()
        mock_orch.retry_task.return_value = True
        mock_load.return_value = mock_orch
        
        task_id = str(uuid4())
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['task', 'retry', task_id])
        
        assert result.exit_code == 0
        assert 'retry initiated' in result.output


class TestRecoverCommand:
    """Test the recover command."""
    
    @patch('maos.cli.commands.recover.load_orchestrator')
    async def test_recover_list_checkpoints(self, mock_load, runner, temp_project_dir):
        """Test listing checkpoints."""
        mock_orch = AsyncMock()
        mock_orch.list_checkpoints.return_value = [
            {
                'id': str(uuid4()),
                'name': 'checkpoint1',
                'created_at': '2024-01-01T00:00:00',
                'size_bytes': 1024
            },
            {
                'id': str(uuid4()),
                'name': 'checkpoint2',
                'created_at': '2024-01-02T00:00:00',
                'size_bytes': 2048
            }
        ]
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['recover', 'list'])
        
        assert result.exit_code == 0
        assert 'checkpoint1' in result.output
        assert 'checkpoint2' in result.output
    
    @patch('maos.cli.commands.recover.load_orchestrator')
    async def test_recover_create_checkpoint(self, mock_load, runner, temp_project_dir):
        """Test creating a checkpoint."""
        mock_orch = AsyncMock()
        checkpoint_id = uuid4()
        mock_orch.create_checkpoint.return_value = checkpoint_id
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'recover', 'checkpoint',
            '--name', 'test-checkpoint'
        ])
        
        assert result.exit_code == 0
        assert 'Checkpoint created' in result.output
        assert str(checkpoint_id) in result.output
    
    @patch('maos.cli.commands.recover.load_orchestrator')
    async def test_recover_restore(self, mock_load, runner, temp_project_dir):
        """Test restoring from checkpoint."""
        mock_orch = AsyncMock()
        mock_orch.restore_checkpoint.return_value = True
        mock_load.return_value = mock_orch
        
        checkpoint_id = str(uuid4())
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'recover', 'restore',
            checkpoint_id
        ])
        
        assert result.exit_code == 0
        assert 'restored successfully' in result.output


class TestNaturalLanguageInterface:
    """Test natural language command interface."""
    
    @patch('maos.cli.natural_language.NaturalLanguageProcessor')
    @patch('maos.cli.commands.task.load_orchestrator')
    async def test_nl_task_submission(self, mock_load, mock_nlp, runner, temp_project_dir):
        """Test submitting task via natural language."""
        mock_orch = AsyncMock()
        mock_plan = Mock(id=uuid4())
        mock_orch.submit_task.return_value = mock_plan
        mock_load.return_value = mock_orch
        
        # Mock NLP processor
        nlp_instance = Mock()
        nlp_instance.parse_command.return_value = {
            'command': 'task_submit',
            'parameters': {
                'name': 'Process data',
                'description': 'Process the user data',
                'priority': 'high'
            }
        }
        mock_nlp.return_value = nlp_instance
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'nl',
            'Create a high priority task to process user data'
        ])
        
        assert result.exit_code == 0
        assert 'Task submitted' in result.output or 'task' in result.output.lower()


class TestChatMode:
    """Test interactive chat mode."""
    
    @patch('maos.cli.commands.chat.ChatSession')
    def test_chat_mode_start(self, mock_session, runner, temp_project_dir):
        """Test starting chat mode."""
        session_instance = Mock()
        session_instance.start = AsyncMock()
        mock_session.return_value = session_instance
        
        os.chdir(temp_project_dir)
        
        # Use input to simulate user interaction
        with patch('click.prompt', side_effect=['exit']):
            result = runner.invoke(cli, ['chat'])
        
        assert result.exit_code == 0
        assert 'Chat mode' in result.output or 'chat' in result.output.lower()


class TestMonitoringCommands:
    """Test monitoring-related commands."""
    
    @patch('maos.cli.commands.monitor.load_orchestrator')
    async def test_monitor_metrics(self, mock_load, runner, temp_project_dir):
        """Test viewing system metrics."""
        mock_orch = AsyncMock()
        mock_orch.get_system_metrics.return_value = {
            'orchestrator': {
                'tasks_submitted': 100,
                'tasks_completed': 85,
                'tasks_failed': 15,
                'agents_created': 10
            },
            'agent_manager': {
                'total_agents': 10,
                'available_agents': 7
            }
        }
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['monitor', 'metrics'])
        
        assert result.exit_code == 0
        assert 'tasks_submitted' in result.output
        assert '100' in result.output
    
    @patch('maos.cli.commands.monitor.load_orchestrator')
    async def test_monitor_health(self, mock_load, runner, temp_project_dir):
        """Test health check command."""
        mock_orch = AsyncMock()
        mock_orch.get_component_health.return_value = {
            'orchestrator': 'healthy',
            'state_manager': 'healthy',
            'message_bus': 'healthy',
            'agent_manager': 'unhealthy'
        }
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['monitor', 'health'])
        
        assert result.exit_code == 0
        assert 'healthy' in result.output
        assert 'unhealthy' in result.output


class TestConfigCommands:
    """Test configuration commands."""
    
    def test_config_show(self, runner, temp_project_dir):
        """Test showing configuration."""
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['config', 'show'])
        
        assert result.exit_code == 0
        assert 'test_project' in result.output
        assert 'storage_directory' in result.output
    
    def test_config_set(self, runner, temp_project_dir):
        """Test setting configuration values."""
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'config', 'set',
            'enable_monitoring', 'true'
        ])
        
        assert result.exit_code == 0
        assert 'Configuration updated' in result.output
        
        # Verify the change
        with open('.maos/config.json', 'r') as f:
            config = json.load(f)
        assert config['enable_monitoring'] is True
    
    def test_config_get(self, runner, temp_project_dir):
        """Test getting configuration value."""
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'config', 'get',
            'project_name'
        ])
        
        assert result.exit_code == 0
        assert 'test_project' in result.output


class TestSwarmCommands:
    """Test swarm coordination commands."""
    
    @patch('maos.cli.commands.swarm.load_orchestrator')
    async def test_swarm_create(self, mock_load, runner, temp_project_dir):
        """Test creating a swarm."""
        mock_orch = AsyncMock()
        swarm_id = uuid4()
        mock_orch.create_agent_swarm.return_value = swarm_id
        mock_load.return_value = mock_orch
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, [
            'swarm', 'create',
            '--name', 'test-swarm',
            '--pattern', 'star',
            '--min-agents', '2',
            '--max-agents', '5'
        ])
        
        assert result.exit_code == 0
        assert 'Swarm created' in result.output
        assert str(swarm_id) in result.output
    
    @patch('maos.cli.commands.swarm.load_orchestrator')
    async def test_swarm_status(self, mock_load, runner, temp_project_dir):
        """Test getting swarm status."""
        mock_orch = AsyncMock()
        mock_orch.get_swarm_status.return_value = {
            'id': str(uuid4()),
            'name': 'test-swarm',
            'active': True,
            'agent_count': 3
        }
        mock_load.return_value = mock_orch
        
        swarm_id = str(uuid4())
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['swarm', 'status', swarm_id])
        
        assert result.exit_code == 0
        assert 'test-swarm' in result.output
        assert 'active' in result.output.lower()


class TestErrorHandling:
    """Test error handling in CLI commands."""
    
    def test_command_not_found(self, runner):
        """Test handling of unknown command."""
        result = runner.invoke(cli, ['nonexistent'])
        
        assert result.exit_code != 0
        assert 'No such command' in result.output or 'Error' in result.output
    
    @patch('maos.cli.commands.status.load_orchestrator')
    def test_orchestrator_load_error(self, mock_load, runner, temp_project_dir):
        """Test handling orchestrator load errors."""
        mock_load.side_effect = Exception("Failed to load orchestrator")
        
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code != 0
        assert 'Error' in result.output or 'Failed' in result.output
    
    def test_missing_required_argument(self, runner, temp_project_dir):
        """Test handling missing required arguments."""
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['agent', 'spawn'])
        
        assert result.exit_code != 0
        assert 'Missing' in result.output or 'required' in result.output.lower()


@pytest.mark.asyncio
async def test_full_cli_workflow(runner):
    """Test a complete workflow using CLI commands."""
    with runner.isolated_filesystem(temp=True):
        # Initialize project
        result = runner.invoke(cli, [
            'init',
            '--name', 'workflow_test',
            '--enable-monitoring'
        ])
        assert result.exit_code == 0
        
        # Mock orchestrator for subsequent commands
        with patch('maos.cli.commands.status.load_orchestrator') as mock_load:
            mock_orch = AsyncMock()
            mock_orch.get_system_status.return_value = {
                'running': True,
                'uptime_seconds': 0,
                'components': {}
            }
            mock_load.return_value = mock_orch
            
            # Check status
            result = runner.invoke(cli, ['status'])
            assert result.exit_code == 0
        
        # Verify project structure
        assert Path('.maos').exists()
        assert Path('.maos/config.json').exists()
        
        # Load and verify config
        with open('.maos/config.json', 'r') as f:
            config = json.load(f)
        
        assert config['project_name'] == 'workflow_test'
        assert config['enable_monitoring'] is True