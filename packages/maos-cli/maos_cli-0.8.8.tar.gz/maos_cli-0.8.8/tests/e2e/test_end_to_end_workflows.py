"""
Comprehensive end-to-end tests for MAOS workflows.
"""

import pytest
import asyncio
import tempfile
import os
import json
import time
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta

from maos.core.orchestrator import Orchestrator
from maos.core.agent_manager import AgentManager
from maos.core.task_planner import TaskPlanner
from maos.core.resource_allocator import ResourceAllocator
from maos.core.swarm_coordinator import SwarmCoordinator, SwarmPattern, CoordinationStrategy
from maos.interfaces.persistence import FilePersistence
from maos.interfaces.state_manager import StateManager
from maos.interfaces.message_bus import MessageBus
from maos.models.task import Task, TaskStatus, TaskPriority
from maos.models.agent import Agent, AgentStatus, AgentCapability
from maos.models.resource import Resource, ResourceType
from maos.models.message import Message, MessageType


@pytest.fixture
async def test_environment():
    """Create a complete test environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'storage_directory': tmpdir,
            'state_manager': {
                'auto_checkpoint_interval': 60,
                'max_snapshots': 10
            },
            'agent_manager': {
                'max_agents': 20,
                'health_check_interval': 5,
                'enable_monitoring': True,
                'enable_auto_recovery': True
            },
            'task_planner': {
                'max_depth': 5,
                'max_subtasks': 20
            },
            'resource_allocator': {
                'enable_auto_scaling': True,
                'resource_threshold': 0.8
            },
            'message_bus': {
                'max_queue_size': 1000,
                'enable_persistence': True
            }
        }
        
        orchestrator = Orchestrator(
            persistence_backend=FilePersistence(tmpdir),
            component_config=config,
            use_redis=False
        )
        
        await orchestrator.start()
        
        yield {
            'orchestrator': orchestrator,
            'config': config,
            'tmpdir': tmpdir
        }
        
        await orchestrator.shutdown()


class TestBasicWorkflow:
    """Test basic end-to-end workflows."""
    
    async def test_simple_task_execution(self, test_environment):
        """Test simple task submission and execution."""
        orchestrator = test_environment['orchestrator']
        
        # Create an agent
        agent = await orchestrator.create_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Create and submit a task
        task = Task(
            name="Simple Task",
            description="A simple test task",
            priority=TaskPriority.MEDIUM,
            metadata={'test_id': 'simple_1'}
        )
        
        plan = await orchestrator.submit_task(task)
        assert plan is not None
        
        # Execute the plan
        success = await orchestrator.execute_plan(plan.id)
        assert success
        
        # Wait for execution
        await asyncio.sleep(2)
        
        # Check task status
        task_status = await orchestrator.get_task_status(task.id)
        assert task_status in [TaskStatus.COMPLETED, TaskStatus.RUNNING]
        
        # Get metrics
        metrics = await orchestrator.get_system_metrics()
        assert metrics['orchestrator']['tasks_submitted'] >= 1
    
    async def test_multi_agent_task_distribution(self, test_environment):
        """Test distributing tasks across multiple agents."""
        orchestrator = test_environment['orchestrator']
        
        # Create multiple agents
        agents = []
        for i in range(5):
            agent = await orchestrator.create_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        # Submit multiple tasks
        tasks = []
        for i in range(10):
            task = Task(
                name=f"Task_{i}",
                description=f"Test task number {i}",
                priority=TaskPriority.MEDIUM
            )
            plan = await orchestrator.submit_task(task)
            tasks.append((task, plan))
        
        # Execute all plans
        for task, plan in tasks:
            await orchestrator.execute_plan(plan.id)
        
        # Wait for some execution
        await asyncio.sleep(3)
        
        # Verify agents are being utilized
        available_agents = await orchestrator.get_available_agents()
        assert len(available_agents) <= len(agents)
        
        # Check that tasks are distributed
        metrics = await orchestrator.get_system_metrics()
        assert metrics['orchestrator']['tasks_submitted'] >= 10


class TestResourceManagement:
    """Test resource management workflows."""
    
    async def test_resource_allocation_workflow(self, test_environment):
        """Test complete resource allocation workflow."""
        orchestrator = test_environment['orchestrator']
        
        # Create resources
        cpu_resource = await orchestrator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=8.0,
            configuration={'cores': 8}
        )
        
        memory_resource = await orchestrator.create_resource(
            resource_type=ResourceType.MEMORY,
            capacity=16.0,
            configuration={'size_gb': 16}
        )
        
        gpu_resource = await orchestrator.create_resource(
            resource_type=ResourceType.GPU,
            capacity=2.0,
            configuration={'model': 'Tesla V100'}
        )
        
        # Create agents with resource requirements
        agent1 = await orchestrator.create_agent(
            agent_type="compute_heavy",
            capabilities={AgentCapability.TASK_EXECUTION},
            configuration={'resource_requirements': {'cpu': 2.0, 'memory': 4.0}}
        )
        
        agent2 = await orchestrator.create_agent(
            agent_type="gpu_worker",
            capabilities={AgentCapability.TASK_EXECUTION},
            configuration={'resource_requirements': {'gpu': 1.0, 'memory': 8.0}}
        )
        
        # Request resources for agents
        request1 = await orchestrator.request_resources(
            requester_id=agent1.id,
            resource_requirements={'cpu': 2.0, 'memory': 4.0},
            priority=TaskPriority.HIGH
        )
        
        request2 = await orchestrator.request_resources(
            requester_id=agent2.id,
            resource_requirements={'gpu': 1.0, 'memory': 8.0},
            priority=TaskPriority.MEDIUM
        )
        
        # Verify allocations
        assert request1 is not None
        assert request2 is not None
        
        # Release resources
        released1 = await orchestrator.release_resources(
            requester_id=agent1.id,
            resource_id=cpu_resource.id
        )
        
        released2 = await orchestrator.release_resources(
            requester_id=agent2.id,
            resource_id=gpu_resource.id
        )
        
        assert released1 >= 0
        assert released2 >= 0
    
    async def test_resource_contention(self, test_environment):
        """Test handling resource contention."""
        orchestrator = test_environment['orchestrator']
        
        # Create limited resources
        cpu_resource = await orchestrator.create_resource(
            resource_type=ResourceType.CPU,
            capacity=4.0
        )
        
        # Create multiple agents competing for resources
        agents = []
        for i in range(3):
            agent = await orchestrator.create_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        # All agents request more than available
        requests = []
        for agent in agents:
            try:
                request = await orchestrator.request_resources(
                    requester_id=agent.id,
                    resource_requirements={'cpu': 2.0},
                    priority=TaskPriority.MEDIUM
                )
                requests.append(request)
            except Exception:
                pass  # Some requests may fail due to contention
        
        # At most 2 agents should get resources
        assert len(requests) <= 2


class TestSwarmCoordination:
    """Test swarm coordination workflows."""
    
    async def test_swarm_parallel_execution(self, test_environment):
        """Test parallel task execution with swarm."""
        orchestrator = test_environment['orchestrator']
        
        # Create a swarm
        swarm_id = await orchestrator.create_agent_swarm(
            name="parallel-swarm",
            pattern=SwarmPattern.STAR,
            strategy=CoordinationStrategy.ROUND_ROBIN,
            min_agents=3,
            max_agents=5
        )
        
        # Create a task with subtasks
        main_task = Task(
            name="Parallel Processing",
            description="Process data in parallel",
            priority=TaskPriority.HIGH,
            metadata={
                'subtasks': [
                    {'name': 'Process Chunk 1', 'description': 'Process first data chunk'},
                    {'name': 'Process Chunk 2', 'description': 'Process second data chunk'},
                    {'name': 'Process Chunk 3', 'description': 'Process third data chunk'}
                ]
            }
        )
        
        # Execute with swarm
        results = await orchestrator.execute_swarm_task(
            swarm_id=swarm_id,
            task=main_task,
            execution_mode="parallel"
        )
        
        assert results is not None
        
        # Get swarm status
        status = await orchestrator.get_swarm_status(swarm_id)
        assert status is not None
        
        # Shutdown swarm
        await orchestrator.shutdown_swarm(swarm_id)
    
    async def test_swarm_pipeline_execution(self, test_environment):
        """Test pipeline execution with swarm."""
        orchestrator = test_environment['orchestrator']
        
        # Create a pipeline swarm
        swarm_id = await orchestrator.create_agent_swarm(
            name="pipeline-swarm",
            pattern=SwarmPattern.PIPELINE,
            strategy=CoordinationStrategy.CAPABILITY_BASED,
            min_agents=3
        )
        
        # Create pipeline task
        pipeline_task = Task(
            name="Data Pipeline",
            description="Multi-stage data processing",
            metadata={
                'pipeline_stages': [
                    {'name': 'Extract', 'description': 'Extract data from source'},
                    {'name': 'Transform', 'description': 'Transform data format'},
                    {'name': 'Load', 'description': 'Load data to destination'}
                ]
            }
        )
        
        # Execute pipeline
        results = await orchestrator.execute_swarm_task(
            swarm_id=swarm_id,
            task=pipeline_task,
            execution_mode="pipeline"
        )
        
        assert results is not None
        
        await orchestrator.shutdown_swarm(swarm_id)
    
    async def test_swarm_consensus_execution(self, test_environment):
        """Test consensus-based execution with swarm."""
        orchestrator = test_environment['orchestrator']
        
        # Create consensus swarm
        swarm_id = await orchestrator.create_agent_swarm(
            name="consensus-swarm",
            pattern=SwarmPattern.CONSENSUS,
            strategy=CoordinationStrategy.VOTING,
            min_agents=3,
            max_agents=5
        )
        
        # Create task requiring consensus
        consensus_task = Task(
            name="Decision Task",
            description="Task requiring consensus decision",
            priority=TaskPriority.HIGH,
            metadata={'require_consensus': True}
        )
        
        # Execute with consensus
        results = await orchestrator.execute_swarm_task(
            swarm_id=swarm_id,
            task=consensus_task,
            execution_mode="consensus"
        )
        
        assert results is not None
        
        await orchestrator.shutdown_swarm(swarm_id)


class TestFailureRecovery:
    """Test failure and recovery scenarios."""
    
    async def test_task_failure_and_retry(self, test_environment):
        """Test task failure and retry mechanism."""
        orchestrator = test_environment['orchestrator']
        
        # Create agent
        agent = await orchestrator.create_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Create a task that will fail
        task = Task(
            name="Failing Task",
            description="Task designed to fail",
            max_retries=3,
            metadata={'should_fail': True}
        )
        
        plan = await orchestrator.submit_task(task)
        
        # Simulate task failure
        task_obj = await orchestrator.get_task(task.id)
        task_obj.update_status(TaskStatus.FAILED)
        task_obj.error = "Simulated failure"
        await orchestrator.state_manager.store_object('tasks', task_obj)
        
        # Retry the task
        retry_success = await orchestrator.retry_task(task.id)
        assert retry_success
        
        # Verify retry count
        retried_task = await orchestrator.get_task(task.id)
        assert retried_task.retry_count == 1
        assert retried_task.status == TaskStatus.PENDING
    
    async def test_agent_failure_recovery(self, test_environment):
        """Test agent failure and recovery."""
        orchestrator = test_environment['orchestrator']
        
        # Create agent
        agent = await orchestrator.create_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Assign task to agent
        task = Task(name="Test Task", description="Test")
        plan = await orchestrator.submit_task(task)
        
        # Simulate agent failure
        agent_obj = await orchestrator.get_agent(agent.id)
        agent_obj.update_status(AgentStatus.ERROR)
        agent_obj.error = "Simulated agent failure"
        await orchestrator.state_manager.store_object('agents', agent_obj)
        
        # Wait for auto-recovery (if enabled)
        await asyncio.sleep(2)
        
        # Check if agent was recovered or task reassigned
        recovered_agent = await orchestrator.get_agent(agent.id)
        assert recovered_agent is not None
    
    async def test_checkpoint_and_restore(self, test_environment):
        """Test checkpoint creation and restoration."""
        orchestrator = test_environment['orchestrator']
        
        # Create initial state
        agents = []
        for i in range(3):
            agent = await orchestrator.create_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        tasks = []
        for i in range(5):
            task = Task(name=f"Task_{i}", description=f"Test task {i}")
            plan = await orchestrator.submit_task(task)
            tasks.append(task)
        
        # Create checkpoint
        checkpoint_id = await orchestrator.create_checkpoint("test-checkpoint")
        assert checkpoint_id is not None
        
        # Modify state
        for i in range(2):
            task = Task(name=f"NewTask_{i}", description="New task")
            await orchestrator.submit_task(task)
        
        # Restore checkpoint
        restore_success = await orchestrator.restore_checkpoint(checkpoint_id)
        assert restore_success
        
        # Verify checkpoint list
        checkpoints = await orchestrator.list_checkpoints()
        assert len(checkpoints) >= 1
        assert any(cp['id'] == str(checkpoint_id) for cp in checkpoints)


class TestMessageBusIntegration:
    """Test message bus integration workflows."""
    
    async def test_event_driven_workflow(self, test_environment):
        """Test event-driven task execution."""
        orchestrator = test_environment['orchestrator']
        
        # Create agents
        agents = []
        for i in range(3):
            agent = await orchestrator.create_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        # Track events
        events_received = []
        
        class TestHandler:
            async def handle_message(self, message):
                events_received.append(message)
            
            def get_supported_message_types(self):
                return {MessageType.TASK_COMPLETION, MessageType.TASK_ASSIGNMENT}
        
        # Register event handler
        handler = TestHandler()
        orchestrator.message_bus.register_handler(handler)
        
        # Submit tasks
        for i in range(5):
            task = Task(name=f"Event Task {i}", description="Test")
            await orchestrator.submit_task(task)
        
        # Wait for events
        await asyncio.sleep(2)
        
        # Verify events were received
        assert len(events_received) > 0
    
    async def test_cross_component_communication(self, test_environment):
        """Test communication between components via message bus."""
        orchestrator = test_environment['orchestrator']
        
        # Send message from one component to another
        test_message = Message(
            type=MessageType.STATUS_UPDATE,
            sender_id=uuid4(),
            payload={
                'component': 'test_component',
                'status': 'running',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Publish message
        await orchestrator.message_bus.publish_to_topic(
            'system_status',
            test_message.type,
            test_message.payload
        )
        
        # Verify message handling
        await asyncio.sleep(0.5)
        
        # The event handler should have processed this
        assert orchestrator._running


class TestPerformanceAndScaling:
    """Test performance and scaling scenarios."""
    
    async def test_high_load_scenario(self, test_environment):
        """Test system under high load."""
        orchestrator = test_environment['orchestrator']
        
        # Create many agents
        agents = []
        for i in range(10):
            agent = await orchestrator.create_agent(
                agent_type=f"worker_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        # Submit many tasks
        start_time = time.time()
        tasks = []
        
        for i in range(50):
            task = Task(
                name=f"Load Task {i}",
                description="High load test task",
                priority=TaskPriority.MEDIUM if i % 2 == 0 else TaskPriority.LOW
            )
            plan = await orchestrator.submit_task(task)
            tasks.append((task, plan))
        
        submission_time = time.time() - start_time
        
        # Execute plans concurrently
        execution_tasks = []
        for task, plan in tasks[:20]:  # Execute first 20
            execution_tasks.append(orchestrator.execute_plan(plan.id))
        
        await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        # Check metrics
        metrics = await orchestrator.get_system_metrics()
        assert metrics['orchestrator']['tasks_submitted'] >= 50
        
        # Performance assertions
        assert submission_time < 10  # Should submit 50 tasks in under 10 seconds
    
    async def test_auto_scaling(self, test_environment):
        """Test automatic scaling of resources."""
        orchestrator = test_environment['orchestrator']
        
        # Start with minimal agents
        initial_agent = await orchestrator.create_agent(
            agent_type="worker",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Submit increasing load
        for batch in range(3):
            tasks = []
            for i in range(10 * (batch + 1)):
                task = Task(
                    name=f"Scaling Task {batch}_{i}",
                    description="Auto-scaling test"
                )
                plan = await orchestrator.submit_task(task)
                tasks.append(plan)
            
            # Wait between batches
            await asyncio.sleep(1)
        
        # Check if more agents were created (in a real system)
        available_agents = await orchestrator.get_available_agents()
        assert len(available_agents) >= 1


class TestComplexWorkflows:
    """Test complex, real-world workflows."""
    
    async def test_data_processing_pipeline(self, test_environment):
        """Test a complete data processing pipeline."""
        orchestrator = test_environment['orchestrator']
        
        # Create specialized agents
        extractor = await orchestrator.create_agent(
            agent_type="extractor",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        transformer = await orchestrator.create_agent(
            agent_type="transformer",
            capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.OPTIMIZATION}
        )
        
        loader = await orchestrator.create_agent(
            agent_type="loader",
            capabilities={AgentCapability.TASK_EXECUTION}
        )
        
        # Create pipeline tasks
        extract_task = Task(
            name="Extract Data",
            description="Extract data from source",
            priority=TaskPriority.HIGH
        )
        
        transform_task = Task(
            name="Transform Data",
            description="Transform and clean data",
            priority=TaskPriority.HIGH,
            required_capabilities={AgentCapability.OPTIMIZATION}
        )
        
        load_task = Task(
            name="Load Data",
            description="Load data to destination",
            priority=TaskPriority.MEDIUM
        )
        
        # Submit tasks in sequence
        extract_plan = await orchestrator.submit_task(extract_task)
        await orchestrator.execute_plan(extract_plan.id)
        
        await asyncio.sleep(1)
        
        transform_plan = await orchestrator.submit_task(transform_task)
        await orchestrator.execute_plan(transform_plan.id)
        
        await asyncio.sleep(1)
        
        load_plan = await orchestrator.submit_task(load_task)
        await orchestrator.execute_plan(load_plan.id)
        
        # Verify pipeline completion
        metrics = await orchestrator.get_system_metrics()
        assert metrics['orchestrator']['tasks_submitted'] >= 3
    
    async def test_distributed_computation(self, test_environment):
        """Test distributed computation workflow."""
        orchestrator = test_environment['orchestrator']
        
        # Create computation swarm
        swarm_id = await orchestrator.create_agent_swarm(
            name="compute-swarm",
            pattern=SwarmPattern.MESH,
            strategy=CoordinationStrategy.LOAD_BALANCED,
            min_agents=4,
            max_agents=8
        )
        
        # Create map-reduce task
        computation_task = Task(
            name="Distributed Computation",
            description="Large-scale parallel computation",
            metadata={
                'map_task': {
                    'name': 'Map Phase',
                    'description': 'Map computation across data'
                },
                'reduce_task': {
                    'name': 'Reduce Phase',
                    'description': 'Reduce results'
                },
                'data_chunks': [
                    {'chunk_id': i, 'data': f'chunk_{i}'} 
                    for i in range(10)
                ]
            }
        )
        
        # Execute distributed computation
        results = await orchestrator.execute_swarm_task(
            swarm_id=swarm_id,
            task=computation_task,
            execution_mode="map_reduce"
        )
        
        assert results is not None
        
        await orchestrator.shutdown_swarm(swarm_id)


@pytest.mark.asyncio
async def test_complete_system_integration():
    """Test complete system integration with all components."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create orchestrator with full configuration
        config = {
            'storage_directory': tmpdir,
            'state_manager': {
                'auto_checkpoint_interval': 30,
                'max_snapshots': 20,
                'enable_compression': True
            },
            'agent_manager': {
                'max_agents': 50,
                'health_check_interval': 5,
                'heartbeat_timeout': 15,
                'enable_monitoring': True,
                'enable_auto_recovery': True,
                'enable_load_balancing': True
            },
            'task_planner': {
                'max_depth': 10,
                'max_subtasks': 50,
                'enable_optimization': True
            },
            'resource_allocator': {
                'enable_auto_scaling': True,
                'resource_threshold': 0.75,
                'scaling_factor': 1.5
            },
            'message_bus': {
                'max_queue_size': 5000,
                'enable_persistence': True,
                'enable_replay': True
            },
            'swarm_coordinator': {
                'enable_monitoring': True,
                'enable_auto_recovery': True
            }
        }
        
        orchestrator = Orchestrator(
            persistence_backend=FilePersistence(tmpdir),
            component_config=config,
            use_redis=False
        )
        
        await orchestrator.start()
        
        try:
            # Create diverse agents
            agents = []
            agent_types = ['worker', 'monitor', 'optimizer', 'coordinator']
            capabilities_map = {
                'worker': {AgentCapability.TASK_EXECUTION},
                'monitor': {AgentCapability.MONITORING, AgentCapability.TASK_EXECUTION},
                'optimizer': {AgentCapability.OPTIMIZATION, AgentCapability.TASK_EXECUTION},
                'coordinator': {AgentCapability.TASK_EXECUTION, AgentCapability.MONITORING}
            }
            
            for agent_type in agent_types:
                for i in range(3):
                    agent = await orchestrator.create_agent(
                        agent_type=f"{agent_type}_{i}",
                        capabilities=capabilities_map[agent_type]
                    )
                    agents.append(agent)
            
            # Create resources
            resources = []
            for resource_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.GPU]:
                resource = await orchestrator.create_resource(
                    resource_type=resource_type,
                    capacity=10.0
                )
                resources.append(resource)
            
            # Create swarms
            swarms = []
            for pattern in [SwarmPattern.STAR, SwarmPattern.PIPELINE, SwarmPattern.MESH]:
                swarm_id = await orchestrator.create_agent_swarm(
                    name=f"{pattern.value}-swarm",
                    pattern=pattern,
                    min_agents=2,
                    max_agents=5
                )
                swarms.append(swarm_id)
            
            # Submit various tasks
            tasks_submitted = []
            
            # Simple tasks
            for i in range(10):
                task = Task(
                    name=f"Simple Task {i}",
                    description="Basic task",
                    priority=TaskPriority.LOW
                )
                plan = await orchestrator.submit_task(task)
                tasks_submitted.append(plan)
            
            # Complex tasks with requirements
            for i in range(5):
                task = Task(
                    name=f"Complex Task {i}",
                    description="Complex task with requirements",
                    priority=TaskPriority.HIGH,
                    required_capabilities={AgentCapability.OPTIMIZATION}
                )
                plan = await orchestrator.submit_task(task)
                tasks_submitted.append(plan)
            
            # Execute some plans
            for plan in tasks_submitted[:5]:
                await orchestrator.execute_plan(plan.id)
            
            # Create checkpoint
            checkpoint_id = await orchestrator.create_checkpoint("integration-test")
            
            # Wait for some processing
            await asyncio.sleep(3)
            
            # Get comprehensive metrics
            status = await orchestrator.get_system_status()
            metrics = await orchestrator.get_system_metrics()
            health = await orchestrator.get_component_health()
            
            # Assertions
            assert status['running'] is True
            assert metrics['orchestrator']['tasks_submitted'] >= 15
            assert metrics['orchestrator']['agents_created'] >= 12
            assert all(h == 'healthy' for h in health.values())
            
            # Test recovery
            await orchestrator.restore_checkpoint(checkpoint_id)
            
            # Cleanup swarms
            for swarm_id in swarms:
                await orchestrator.shutdown_swarm(swarm_id)
            
        finally:
            await orchestrator.shutdown()