"""
Simple comprehensive tests for MAOS core components.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
import tempfile
import os

from src.maos.core.orchestrator import Orchestrator
from src.maos.core.agent_manager import AgentManager
from src.maos.models.agent import Agent, AgentStatus
from src.maos.core.claude_cli_manager import ClaudeCliManager
from src.maos.core.session_manager import SessionManager
from src.maos.interfaces.sqlite_persistence import SQLitePersistence


class TestOrchestrator:
    """Test the main Orchestrator component."""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create an orchestrator with test configuration."""
        config = {
            'state_manager': {
                'auto_checkpoint_interval': 300,
                'max_snapshots': 50
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = SQLitePersistence(f"{tmpdir}/test.db")
            orch = Orchestrator(
                persistence_backend=persistence,
                component_config=config
            )
            yield orch
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.state_manager is not None
        assert orchestrator.agent_manager is not None
        assert orchestrator.task_planner is not None
    
    @pytest.mark.asyncio
    async def test_orchestrator_start_shutdown(self, orchestrator):
        """Test orchestrator can start and shutdown."""
        await orchestrator.start()
        assert orchestrator._running == True
        
        await orchestrator.shutdown()
        assert orchestrator._running == False
    
    @pytest.mark.asyncio
    async def test_orchestrator_execute_task(self, orchestrator):
        """Test orchestrator can execute a task."""
        await orchestrator.start()
        
        task_request = {
            'name': 'Test Task',
            'description': 'A test task',
            'priority': 'medium'
        }
        
        result = await orchestrator.execute_task(task_request)
        assert result is not None
        
        await orchestrator.shutdown()


class TestAgentManager:
    """Test the AgentManager component."""
    
    @pytest.fixture
    def agent_manager(self):
        """Create an agent manager for testing."""
        return AgentManager()
    
    @pytest.mark.asyncio
    async def test_create_agent(self, agent_manager):
        """Test creating an agent."""
        agent_config = {
            'name': 'TestAgent',
            'type': 'test',
            'capabilities': ['task_execution']
        }
        
        agent = await agent_manager.create_agent(agent_config)
        assert agent is not None
        assert agent.name == 'TestAgent'
        assert agent.type == 'test'
    
    @pytest.mark.asyncio
    async def test_register_agent(self, agent_manager):
        """Test registering an agent."""
        agent = Agent(
            name="TestAgent",
            type="test",
            capabilities=['task_execution']
        )
        
        registered = await agent_manager.register_agent(agent)
        assert registered == True
        assert agent.id in agent_manager.agents
    
    @pytest.mark.asyncio
    async def test_get_available_agents(self, agent_manager):
        """Test getting available agents."""
        agent1 = Agent(name="Agent1", type="test", status=AgentStatus.IDLE)
        agent2 = Agent(name="Agent2", type="test", status=AgentStatus.BUSY)
        agent3 = Agent(name="Agent3", type="test", status=AgentStatus.IDLE)
        
        await agent_manager.register_agent(agent1)
        await agent_manager.register_agent(agent2)
        await agent_manager.register_agent(agent3)
        
        available = await agent_manager.get_available_agents()
        assert len(available) == 2
        assert agent1 in available
        assert agent3 in available
        assert agent2 not in available
    
    @pytest.mark.asyncio
    async def test_assign_task_to_agent(self, agent_manager):
        """Test assigning a task to an agent."""
        agent = Agent(name="TestAgent", type="test", status=AgentStatus.IDLE)
        await agent_manager.register_agent(agent)
        
        task = MagicMock()
        task.id = "task123"
        task.name = "Test Task"
        
        assigned = await agent_manager.assign_task(agent.id, task)
        assert assigned == True
        assert agent.status == AgentStatus.BUSY
        assert agent.current_task_id == task.id


class TestClaudeCliManager:
    """Test the Claude CLI Manager component."""
    
    @pytest.fixture
    def claude_manager(self):
        """Create a Claude CLI manager for testing."""
        return ClaudeCliManager()
    
    @pytest.mark.asyncio
    async def test_initialize_claude_session(self, claude_manager):
        """Test initializing a Claude session."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Claude CLI ready"
            
            result = await claude_manager.initialize_session()
            assert result == True
            mock_run.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_claude_command(self, claude_manager):
        """Test executing a Claude command."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Command executed"
            
            result = await claude_manager.execute_command("test command")
            assert result is not None
            assert "Command executed" in result
    
    @pytest.mark.asyncio
    async def test_claude_error_handling(self, claude_manager):
        """Test Claude CLI error handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Error occurred"
            
            with pytest.raises(Exception):
                await claude_manager.execute_command("bad command")


class TestSessionManager:
    """Test the Session Manager component."""
    
    @pytest.fixture
    async def session_manager(self):
        """Create a session manager for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = SQLitePersistence(f"{tmpdir}/test.db")
            manager = SessionManager(persistence_backend=persistence)
            await manager.initialize()
            yield manager
    
    @pytest.mark.asyncio
    async def test_create_session(self, session_manager):
        """Test creating a new session."""
        session = await session_manager.create_session(
            name="Test Session",
            type="test"
        )
        
        assert session is not None
        assert session.name == "Test Session"
        assert session.type == "test"
        assert session.status == "active"
    
    @pytest.mark.asyncio
    async def test_get_session(self, session_manager):
        """Test retrieving a session."""
        session = await session_manager.create_session(
            name="Test Session",
            type="test"
        )
        
        retrieved = await session_manager.get_session(session.id)
        assert retrieved is not None
        assert retrieved.id == session.id
        assert retrieved.name == session.name
    
    @pytest.mark.asyncio
    async def test_update_session(self, session_manager):
        """Test updating a session."""
        session = await session_manager.create_session(
            name="Test Session",
            type="test"
        )
        
        updated = await session_manager.update_session(
            session.id,
            status="completed"
        )
        
        assert updated.status == "completed"
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, session_manager):
        """Test listing all sessions."""
        session1 = await session_manager.create_session(name="Session 1")
        session2 = await session_manager.create_session(name="Session 2")
        session3 = await session_manager.create_session(name="Session 3")
        
        sessions = await session_manager.list_sessions()
        assert len(sessions) >= 3
        
        session_ids = [s.id for s in sessions]
        assert session1.id in session_ids
        assert session2.id in session_ids
        assert session3.id in session_ids


class TestSQLitePersistence:
    """Test the SQLite persistence layer."""
    
    @pytest.fixture
    async def persistence(self):
        """Create a SQLite persistence instance."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        persistence = SQLitePersistence(db_path)
        await persistence.initialize()
        yield persistence
        
        os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_save_and_load_agent(self, persistence):
        """Test saving and loading an agent."""
        agent = Agent(
            name="TestAgent",
            type="test",
            capabilities=['task_execution']
        )
        
        await persistence.save_agent(agent)
        
        loaded = await persistence.load_agent(agent.id)
        assert loaded is not None
        assert loaded.id == agent.id
        assert loaded.name == agent.name
        assert loaded.type == agent.type
    
    @pytest.mark.asyncio
    async def test_save_and_load_session(self, persistence):
        """Test saving and loading a session."""
        session_data = {
            'id': 'session123',
            'name': 'Test Session',
            'type': 'test',
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
        await persistence.save_session(session_data)
        
        loaded = await persistence.load_session('session123')
        assert loaded is not None
        assert loaded['id'] == 'session123'
        assert loaded['name'] == 'Test Session'
    
    @pytest.mark.asyncio
    async def test_list_agents(self, persistence):
        """Test listing all agents."""
        agent1 = Agent(name="Agent1", type="test")
        agent2 = Agent(name="Agent2", type="test")
        agent3 = Agent(name="Agent3", type="test")
        
        await persistence.save_agent(agent1)
        await persistence.save_agent(agent2)
        await persistence.save_agent(agent3)
        
        agents = await persistence.list_agents()
        assert len(agents) >= 3
        
        agent_ids = [a.id for a in agents]
        assert agent1.id in agent_ids
        assert agent2.id in agent_ids
        assert agent3.id in agent_ids
    
    @pytest.mark.asyncio
    async def test_delete_agent(self, persistence):
        """Test deleting an agent."""
        agent = Agent(name="TestAgent", type="test")
        await persistence.save_agent(agent)
        
        deleted = await persistence.delete_agent(agent.id)
        assert deleted == True
        
        loaded = await persistence.load_agent(agent.id)
        assert loaded is None


class TestIntegration:
    """Integration tests for MAOS components."""
    
    @pytest.mark.asyncio
    async def test_full_task_execution_flow(self):
        """Test complete task execution flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = SQLitePersistence(f"{tmpdir}/test.db")
            await persistence.initialize()
            
            orchestrator = Orchestrator(
                persistence_backend=persistence,
                component_config={'state_manager': {'auto_checkpoint_interval': 300}}
            )
            
            await orchestrator.start()
            
            # Create and register an agent
            agent_config = {
                'name': 'TestAgent',
                'type': 'test',
                'capabilities': ['task_execution']
            }
            agent = await orchestrator.agent_manager.create_agent(agent_config)
            
            # Execute a task
            task_request = {
                'name': 'Integration Test Task',
                'description': 'Test the full flow',
                'priority': 'high'
            }
            
            result = await orchestrator.execute_task(task_request)
            assert result is not None
            
            await orchestrator.shutdown()
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self):
        """Test multiple agents working together."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = SQLitePersistence(f"{tmpdir}/test.db")
            await persistence.initialize()
            
            orchestrator = Orchestrator(
                persistence_backend=persistence,
                component_config={'state_manager': {'auto_checkpoint_interval': 300}}
            )
            
            await orchestrator.start()
            
            # Create multiple agents
            agents = []
            for i in range(3):
                agent_config = {
                    'name': f'Agent{i}',
                    'type': 'worker',
                    'capabilities': ['task_execution']
                }
                agent = await orchestrator.agent_manager.create_agent(agent_config)
                agents.append(agent)
            
            # Execute multiple tasks
            tasks = []
            for i in range(5):
                task_request = {
                    'name': f'Task {i}',
                    'description': f'Test task {i}',
                    'priority': 'medium'
                }
                result = await orchestrator.execute_task(task_request)
                tasks.append(result)
            
            # Verify all tasks were handled
            assert len(tasks) == 5
            
            await orchestrator.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])