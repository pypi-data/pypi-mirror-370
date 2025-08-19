"""
Simple verification tests to check basic functionality without complex imports.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_basic_imports():
    """Test that basic modules can be imported."""
    try:
        from maos.models.task import Task, TaskStatus, TaskPriority
        assert Task is not None
        assert TaskStatus is not None
        assert TaskPriority is not None
        print("✅ Task models import successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import task models: {e}")
    
    try:
        from maos.models.agent import Agent, AgentStatus, AgentCapability
        assert Agent is not None
        assert AgentStatus is not None
        assert AgentCapability is not None
        print("✅ Agent models import successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import agent models: {e}")
    
    try:
        from maos.models.resource import Resource, ResourceType
        assert Resource is not None
        assert ResourceType is not None
        print("✅ Resource models import successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import resource models: {e}")


def test_task_creation():
    """Test creating a task object."""
    from maos.models.task import Task, TaskPriority
    
    task = Task(
        name="Test Task",
        description="A test task",
        priority=TaskPriority.MEDIUM
    )
    
    assert task.name == "Test Task"
    assert task.description == "A test task"
    assert task.priority == TaskPriority.MEDIUM
    assert task.id is not None
    print("✅ Task creation works")


def test_agent_creation():
    """Test creating an agent object."""
    from maos.models.agent import Agent, AgentCapability
    
    agent = Agent(
        name="Test Agent",
        type="worker",
        capabilities={AgentCapability.TASK_EXECUTION}
    )
    
    assert agent.name == "Test Agent"
    assert agent.type == "worker"
    assert AgentCapability.TASK_EXECUTION in agent.capabilities
    assert agent.id is not None
    print("✅ Agent creation works")


def test_resource_creation():
    """Test creating a resource object."""
    from maos.models.resource import Resource, ResourceType
    
    resource = Resource(
        type=ResourceType.CPU,
        capacity=4.0
    )
    
    assert resource.type == ResourceType.CPU
    assert resource.capacity == 4.0
    assert resource.id is not None
    print("✅ Resource creation works")


def test_task_status_transitions():
    """Test task status transitions."""
    from maos.models.task import Task, TaskStatus
    
    task = Task(name="Status Test", description="Test status transitions")
    
    # Initial status
    assert task.status == TaskStatus.PENDING
    
    # Transition to running
    task.update_status(TaskStatus.RUNNING)
    assert task.status == TaskStatus.RUNNING
    
    # Transition to completed
    task.update_status(TaskStatus.COMPLETED)
    assert task.status == TaskStatus.COMPLETED
    assert task.is_terminal()
    
    print("✅ Task status transitions work")


def test_agent_status_and_metrics():
    """Test agent status and metrics."""
    from maos.models.agent import Agent, AgentStatus, AgentCapability
    
    agent = Agent(
        name="Metrics Test",
        type="worker",
        capabilities={AgentCapability.TASK_EXECUTION}
    )
    
    # Initial status
    assert agent.status == AgentStatus.IDLE
    assert agent.is_available()
    
    # Update status
    agent.update_status(AgentStatus.BUSY)
    assert agent.status == AgentStatus.BUSY
    assert not agent.is_available()
    
    # Update metrics
    agent.update_heartbeat(cpu_usage=50.0, memory_usage=1024.0)
    assert agent.metrics.cpu_usage == 50.0
    assert agent.metrics.memory_usage == 1024.0
    
    print("✅ Agent status and metrics work")


def test_resource_allocation():
    """Test resource allocation tracking."""
    from maos.models.resource import Resource, ResourceType
    from uuid import uuid4
    
    resource = Resource(
        type=ResourceType.MEMORY,
        capacity=8.0
    )
    
    # Initial state
    assert resource.available_capacity == 8.0
    assert not resource.is_fully_allocated()
    
    # Allocate some capacity
    requester_id = uuid4()
    success = resource.allocate(requester_id, 4.0)
    assert success
    assert resource.available_capacity == 4.0
    
    # Release allocation
    released = resource.release(requester_id)
    assert released == 4.0
    assert resource.available_capacity == 8.0
    
    print("✅ Resource allocation works")


def test_task_dependencies():
    """Test task dependency management."""
    from maos.models.task import Task
    from uuid import uuid4
    
    parent = Task(name="Parent", description="Parent task")
    child1 = Task(name="Child1", description="First child")
    child2 = Task(name="Child2", description="Second child")
    
    # Add dependencies
    child1.dependencies.add(parent.id)
    child2.dependencies.add(parent.id)
    child2.dependencies.add(child1.id)
    
    assert parent.id in child1.dependencies
    assert parent.id in child2.dependencies
    assert child1.id in child2.dependencies
    
    print("✅ Task dependencies work")


def test_agent_capabilities():
    """Test agent capability checking."""
    from maos.models.agent import Agent, AgentCapability
    
    agent = Agent(
        name="Capability Test",
        type="advanced",
        capabilities={
            AgentCapability.TASK_EXECUTION,
            AgentCapability.MONITORING,
            AgentCapability.OPTIMIZATION
        }
    )
    
    # Check single capability
    assert agent.has_capability(AgentCapability.MONITORING)
    assert not agent.has_capability(AgentCapability.ORCHESTRATION)
    
    # Check multiple capabilities
    required = {AgentCapability.TASK_EXECUTION, AgentCapability.MONITORING}
    assert agent.can_handle_task(required)
    
    required_with_missing = {
        AgentCapability.TASK_EXECUTION,
        AgentCapability.ORCHESTRATION
    }
    assert not agent.can_handle_task(required_with_missing)
    
    print("✅ Agent capabilities work")


def test_message_creation():
    """Test message creation."""
    from maos.models.message import Message, MessageType, MessagePriority
    from uuid import uuid4
    
    message = Message(
        type=MessageType.TASK_ASSIGNMENT,
        sender_id=uuid4(),
        recipient_id=uuid4(),
        payload={'task_id': str(uuid4())},
        priority=MessagePriority.HIGH
    )
    
    assert message.type == MessageType.TASK_ASSIGNMENT
    assert message.priority == MessagePriority.HIGH
    assert 'task_id' in message.payload
    assert message.id is not None
    
    print("✅ Message creation works")


def test_checkpoint_creation():
    """Test checkpoint creation."""
    from maos.models.checkpoint import Checkpoint, CheckpointType
    
    checkpoint = Checkpoint(
        type=CheckpointType.MANUAL,
        name="test-checkpoint",
        state_data={'test': 'data'}
    )
    
    assert checkpoint.type == CheckpointType.MANUAL
    assert checkpoint.name == "test-checkpoint"
    assert checkpoint.state_data == {'test': 'data'}
    assert checkpoint.id is not None
    
    print("✅ Checkpoint creation works")


if __name__ == "__main__":
    # Run tests directly
    print("\n" + "="*60)
    print("Running Simple Verification Tests")
    print("="*60 + "\n")
    
    test_functions = [
        test_basic_imports,
        test_task_creation,
        test_agent_creation,
        test_resource_creation,
        test_task_status_transitions,
        test_agent_status_and_metrics,
        test_resource_allocation,
        test_task_dependencies,
        test_agent_capabilities,
        test_message_creation,
        test_checkpoint_creation
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            print(f"\nRunning {test_func.__name__}...")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")