"""
Test configuration and shared fixtures for MAOS test suite.
"""

import asyncio
import os
import pytest
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

# Third-party imports
import redis.asyncio as redis
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# MAOS imports
from src.maos.core.orchestrator import Orchestrator
from src.maos.core.agent_manager import AgentManager
from src.maos.core.task_planner import TaskPlanner
from src.maos.core.resource_allocator import ResourceAllocator
from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.models.agent import Agent, AgentStatus, AgentCapability
from src.maos.models.resource import Resource, ResourceType
from src.maos.interfaces.state_manager import StateManager
from src.maos.interfaces.persistence import FilePersistence
from src.communication.message_bus.core import MessageBus


# Test configuration
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///test_maos.db")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Provide Redis client for testing."""
    client = redis.from_url(TEST_REDIS_URL)
    
    # Test connection
    try:
        await client.ping()
    except redis.ConnectionError:
        pytest.skip("Redis not available for testing")
    
    yield client
    
    # Cleanup
    await client.flushdb()
    await client.close()


@pytest.fixture
async def clean_redis(redis_client: redis.Redis) -> AsyncGenerator[redis.Redis, None]:
    """Provide clean Redis instance for each test."""
    await redis_client.flushdb()
    yield redis_client
    await redis_client.flushdb()


@pytest.fixture
async def mock_persistence() -> AsyncGenerator[FilePersistence, None]:
    """Provide mock persistence backend."""
    temp_dir = f"/tmp/maos_test_{uuid.uuid4().hex[:8]}"
    os.makedirs(temp_dir, exist_ok=True)
    
    persistence = FilePersistence(storage_directory=temp_dir)
    await persistence.initialize()
    
    yield persistence
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def state_manager(mock_persistence: FilePersistence) -> AsyncGenerator[StateManager, None]:
    """Provide StateManager instance for testing."""
    state_mgr = StateManager(persistence_backend=mock_persistence)
    await state_mgr.start()
    
    yield state_mgr
    
    await state_mgr.shutdown()


@pytest.fixture
async def message_bus(clean_redis: redis.Redis) -> AsyncGenerator[MessageBus, None]:
    """Provide MessageBus instance for testing."""
    bus = MessageBus(redis_url=TEST_REDIS_URL)
    await bus.connect()
    
    yield bus
    
    await bus.disconnect()


@pytest.fixture
def task_planner() -> TaskPlanner:
    """Provide TaskPlanner instance for testing."""
    return TaskPlanner()


@pytest.fixture
async def agent_manager(state_manager: StateManager) -> AgentManager:
    """Provide AgentManager instance for testing."""
    return AgentManager()


@pytest.fixture
async def resource_allocator() -> ResourceAllocator:
    """Provide ResourceAllocator instance for testing."""
    return ResourceAllocator()


@pytest.fixture
async def orchestrator(
    mock_persistence: FilePersistence
) -> AsyncGenerator[Orchestrator, None]:
    """Provide full Orchestrator instance for testing."""
    config = {
        'storage_directory': mock_persistence.storage_directory,
        'message_bus': {'redis_url': TEST_REDIS_URL}
    }
    
    orch = Orchestrator(
        persistence_backend=mock_persistence,
        component_config=config
    )
    
    await orch.start()
    
    yield orch
    
    await orch.shutdown()


# Test data factories
@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        name="Test Task",
        description="A test task",
        priority=TaskPriority.MEDIUM,
        parameters={"test_param": "test_value"},
        timeout_seconds=60,
        resource_requirements={"cpu": 1.0, "memory": 512}
    )


@pytest.fixture
def sample_agent() -> Agent:
    """Create a sample agent for testing."""
    return Agent(
        name="Test Agent",
        type="test_agent",
        capabilities={
            AgentCapability.TASK_EXECUTION,
            AgentCapability.DATA_PROCESSING
        },
        max_concurrent_tasks=3,
        resource_limits={
            "cpu_percent": 80,
            "memory_mb": 1024
        }
    )


@pytest.fixture
def sample_resource() -> Resource:
    """Create a sample resource for testing."""
    return Resource(
        name="Test Resource",
        type=ResourceType.CPU,
        capacity=4.0,
        available_capacity=4.0
    )


@pytest.fixture
def multiple_tasks() -> list[Task]:
    """Create multiple related tasks for testing."""
    tasks = []
    
    # Root task
    root_task = Task(
        name="Root Task",
        description="Main task",
        priority=TaskPriority.HIGH
    )
    tasks.append(root_task)
    
    # Dependent tasks
    for i in range(3):
        task = Task(
            name=f"Subtask {i+1}",
            description=f"Subtask {i+1} of root task",
            priority=TaskPriority.MEDIUM,
            parent_task_id=root_task.id
        )
        task.add_dependency(root_task.id, "completion", True)
        tasks.append(task)
    
    return tasks


@pytest.fixture
def multiple_agents() -> list[Agent]:
    """Create multiple agents with different capabilities."""
    agents = []
    
    # CPU-intensive agent
    cpu_agent = Agent(
        name="CPU Agent",
        type="cpu_worker",
        capabilities={AgentCapability.COMPUTATION, AgentCapability.TASK_EXECUTION},
        max_concurrent_tasks=1,
        resource_limits={"cpu_percent": 100, "memory_mb": 512}
    )
    agents.append(cpu_agent)
    
    # I/O agent
    io_agent = Agent(
        name="I/O Agent",
        type="io_worker",
        capabilities={AgentCapability.FILE_OPERATIONS, AgentCapability.API_INTEGRATION},
        max_concurrent_tasks=5,
        resource_limits={"cpu_percent": 50, "memory_mb": 256}
    )
    agents.append(io_agent)
    
    # General purpose agent
    general_agent = Agent(
        name="General Agent",
        type="general_worker",
        capabilities={
            AgentCapability.TASK_EXECUTION,
            AgentCapability.DATA_PROCESSING,
            AgentCapability.COMMUNICATION
        },
        max_concurrent_tasks=3,
        resource_limits={"cpu_percent": 80, "memory_mb": 1024}
    )
    agents.append(general_agent)
    
    return agents


# Mock utilities
@pytest.fixture
def mock_claude_api():
    """Mock Claude API for testing."""
    mock = AsyncMock()
    mock.create_message.return_value = {
        "id": "msg_test123",
        "content": [{"text": "Test response"}],
        "usage": {"input_tokens": 10, "output_tokens": 20}
    }
    return mock


# Performance test utilities
@pytest.fixture
def performance_metrics():
    """Utility for collecting performance metrics."""
    class PerformanceMetrics:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.metrics = {}
        
        def start_timer(self):
            self.start_time = datetime.utcnow()
        
        def stop_timer(self):
            self.end_time = datetime.utcnow()
            return (self.end_time - self.start_time).total_seconds()
        
        def record_metric(self, name: str, value: Any):
            self.metrics[name] = value
        
        def get_duration(self) -> float:
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time).total_seconds()
            return 0.0
        
        def reset(self):
            self.start_time = None
            self.end_time = None
            self.metrics = {}
    
    return PerformanceMetrics()


# Chaos testing utilities
@pytest.fixture
def chaos_injection():
    """Utility for injecting chaos into tests."""
    class ChaosInjection:
        def __init__(self):
            self.active_failures = []
        
        async def inject_agent_failure(self, agent: Agent, failure_type: str = "crash"):
            """Simulate agent failure."""
            if failure_type == "crash":
                agent.status = AgentStatus.OFFLINE
            elif failure_type == "hang":
                agent.status = AgentStatus.UNHEALTHY
            elif failure_type == "overload":
                agent.status = AgentStatus.OVERLOADED
            
            self.active_failures.append((agent.id, failure_type))
        
        async def inject_network_partition(self, message_bus: MessageBus):
            """Simulate network partition."""
            # Mock Redis connection failure
            original_redis = message_bus.pub_redis
            message_bus.pub_redis = None
            message_bus.is_connected = False
            return original_redis
        
        async def restore_network(self, message_bus: MessageBus, original_redis):
            """Restore network connectivity."""
            message_bus.pub_redis = original_redis
            message_bus.is_connected = True
        
        def clear_failures(self):
            """Clear all injected failures."""
            self.active_failures = []
    
    return ChaosInjection()


# Database fixtures (if using SQL storage)
@pytest.fixture
async def database_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session for testing."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with Session() as session:
        yield session
        await session.rollback()


# Load testing utilities
@pytest.fixture
def load_generator():
    """Utility for generating load in tests."""
    class LoadGenerator:
        def __init__(self):
            self.tasks = []
            self.agents = []
        
        def generate_tasks(self, count: int) -> list[Task]:
            """Generate multiple tasks for load testing."""
            tasks = []
            for i in range(count):
                task = Task(
                    name=f"Load Test Task {i}",
                    description=f"Task {i} for load testing",
                    priority=TaskPriority.MEDIUM,
                    parameters={"task_index": i},
                    timeout_seconds=30
                )
                tasks.append(task)
            return tasks
        
        def generate_agents(self, count: int) -> list[Agent]:
            """Generate multiple agents for load testing."""
            agents = []
            for i in range(count):
                agent = Agent(
                    name=f"Load Test Agent {i}",
                    type="load_test_agent",
                    capabilities={AgentCapability.TASK_EXECUTION},
                    max_concurrent_tasks=2
                )
                agents.append(agent)
            return agents
    
    return LoadGenerator()


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "chaos: mark test as a chaos engineering test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (may be skipped)"
    )
    config.addinivalue_line(
        "markers", "redis_required: mark test as requiring Redis"
    )
    config.addinivalue_line(
        "markers", "postgresql_required: mark test as requiring PostgreSQL"
    )


# Skip tests if dependencies not available
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle skipped tests."""
    # Skip Redis tests if Redis not available
    try:
        import redis
        redis_client = redis.Redis.from_url(TEST_REDIS_URL)
        redis_client.ping()
        redis_available = True
    except:
        redis_available = False
    
    if not redis_available:
        skip_redis = pytest.mark.skip(reason="Redis not available")
        for item in items:
            if "redis_required" in item.keywords:
                item.add_marker(skip_redis)