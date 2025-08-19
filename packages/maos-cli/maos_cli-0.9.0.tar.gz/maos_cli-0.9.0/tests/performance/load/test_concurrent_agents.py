"""
Load testing for concurrent agent operations.
"""

import pytest
import asyncio
import time
from datetime import datetime
from statistics import mean, median
from uuid import uuid4

from src.maos.core.orchestrator import Orchestrator
from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.models.agent import AgentCapability
from tests.utils.test_helpers import TestDataFactory, PerformanceTimer, AsyncTestRunner


@pytest.mark.performance
@pytest.mark.slow
class TestConcurrentAgentLoad:
    """Performance tests for concurrent agent operations."""

    @pytest.fixture
    async def performance_orchestrator(self, mock_persistence):
        """Create orchestrator optimized for performance testing."""
        config = {
            'agent_manager': {'max_agents': 50},
            'message_bus': {'max_connections': 100},
            'task_planner': {'parallel_optimization': True}
        }
        
        orchestrator = Orchestrator(
            persistence_backend=mock_persistence,
            component_config=config
        )
        await orchestrator.start()
        
        yield orchestrator
        
        await orchestrator.shutdown()

    async def test_20_concurrent_agents_baseline(self, performance_orchestrator, performance_metrics):
        """Test baseline performance with 20 concurrent agents."""
        num_agents = 20
        num_tasks = 100
        
        performance_metrics.start_timer()
        
        # Create agents
        agents = []
        for i in range(num_agents):
            agent = await performance_orchestrator.create_agent(
                agent_type=f"perf_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION},
                configuration={"max_concurrent_tasks": 3}
            )
            agents.append(agent)
        
        agent_creation_time = performance_metrics.stop_timer()
        performance_metrics.record_metric("agent_creation_time", agent_creation_time)
        
        # Create tasks
        tasks = []
        for i in range(num_tasks):
            task = TestDataFactory.create_task(
                name=f"Load Test Task {i}",
                priority=TaskPriority.MEDIUM,
                timeout_seconds=10
            )
            tasks.append(task)
        
        # Submit tasks and measure throughput
        performance_metrics.start_timer()
        
        submission_times = []
        for task in tasks:
            start = time.time()
            await performance_orchestrator.submit_task(task)
            submission_times.append(time.time() - start)
        
        task_submission_time = performance_metrics.stop_timer()
        
        # Wait for completion
        completion_start = time.time()
        completed_tasks = await self._wait_for_task_completion(
            performance_orchestrator, tasks, timeout=120.0
        )
        total_completion_time = time.time() - completion_start
        
        # Collect metrics
        performance_metrics.record_metric("total_agents", num_agents)
        performance_metrics.record_metric("total_tasks", num_tasks)
        performance_metrics.record_metric("tasks_completed", len(completed_tasks))
        performance_metrics.record_metric("completion_rate", len(completed_tasks) / num_tasks)
        performance_metrics.record_metric("task_submission_time", task_submission_time)
        performance_metrics.record_metric("total_completion_time", total_completion_time)
        performance_metrics.record_metric("avg_submission_time", mean(submission_times))
        performance_metrics.record_metric("tasks_per_second", num_tasks / task_submission_time)
        performance_metrics.record_metric("throughput", len(completed_tasks) / total_completion_time)
        
        # Assertions for baseline performance
        assert len(completed_tasks) >= num_tasks * 0.95, "Too many tasks failed"
        assert task_submission_time < 30.0, f"Task submission too slow: {task_submission_time}s"
        assert total_completion_time < 90.0, f"Task completion too slow: {total_completion_time}s"
        assert performance_metrics.metrics["tasks_per_second"] > 5.0, "Task submission throughput too low"
        
        # Agent utilization check
        agent_metrics = await performance_orchestrator.get_system_metrics()
        active_agents = agent_metrics.get("agent_manager", {}).get("active_agents", 0)
        assert active_agents >= num_agents * 0.9, "Too many agents inactive"

    async def test_agent_scaling_performance(self, performance_orchestrator, performance_metrics):
        """Test performance with different agent counts (1, 5, 10, 20 agents)."""
        agent_counts = [1, 5, 10, 20]
        tasks_per_agent = 10
        results = {}
        
        for agent_count in agent_counts:
            performance_metrics.reset()
            performance_metrics.start_timer()
            
            # Create agents for this test
            agents = []
            for i in range(agent_count):
                agent = await performance_orchestrator.create_agent(
                    agent_type=f"scale_agent_{i}",
                    capabilities={AgentCapability.TASK_EXECUTION}
                )
                agents.append(agent)
            
            # Create tasks
            num_tasks = agent_count * tasks_per_agent
            tasks = []
            for i in range(num_tasks):
                task = TestDataFactory.create_task(f"Scale Task {i}")
                tasks.append(task)
            
            # Submit and execute
            start_time = time.time()
            for task in tasks:
                await performance_orchestrator.submit_task(task)
            
            completed_tasks = await self._wait_for_task_completion(
                performance_orchestrator, tasks, timeout=60.0
            )
            end_time = time.time()
            
            total_time = end_time - start_time
            throughput = len(completed_tasks) / total_time
            
            results[agent_count] = {
                "total_time": total_time,
                "completed_tasks": len(completed_tasks),
                "throughput": throughput,
                "efficiency": throughput / agent_count
            }
            
            # Cleanup agents
            for agent in agents:
                await performance_orchestrator.terminate_agent(agent.id)
            
            await asyncio.sleep(1.0)  # Brief pause between tests
        
        # Analyze scaling efficiency
        single_agent_throughput = results[1]["throughput"]
        
        for agent_count in agent_counts[1:]:
            result = results[agent_count]
            speedup = result["throughput"] / single_agent_throughput
            expected_speedup = min(agent_count, tasks_per_agent)  # Theoretical max
            efficiency = speedup / agent_count
            
            performance_metrics.record_metric(f"speedup_{agent_count}agents", speedup)
            performance_metrics.record_metric(f"efficiency_{agent_count}agents", efficiency)
            
            # Assert reasonable scaling
            assert speedup > 1.0, f"No speedup with {agent_count} agents"
            assert efficiency > 0.3, f"Poor efficiency with {agent_count} agents: {efficiency}"
        
        # Log results for analysis
        print("\nScaling Performance Results:")
        for agent_count, result in results.items():
            print(f"{agent_count} agents: {result['throughput']:.2f} tasks/sec "
                  f"(efficiency: {result['efficiency']:.2f})")

    async def test_message_throughput_1000_per_second(self, performance_orchestrator):
        """Test achieving target message throughput of 1000 messages/second."""
        target_throughput = 1000  # messages per second
        test_duration = 10.0  # seconds
        
        # Create agents for message exchange
        num_agents = 10
        agents = []
        for i in range(num_agents):
            agent = await performance_orchestrator.create_agent(
                agent_type=f"message_agent_{i}",
                capabilities={AgentCapability.COMMUNICATION}
            )
            agents.append(agent)
        
        message_count = 0
        start_time = time.time()
        
        # Generate messages continuously for test duration
        while time.time() - start_time < test_duration:
            # Send messages between agents
            for i in range(10):  # Burst of 10 messages
                sender = agents[i % len(agents)]
                recipient = agents[(i + 1) % len(agents)]
                
                message_payload = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "message_id": message_count,
                    "sender": str(sender.id),
                    "recipient": str(recipient.id)
                }
                
                # Simulate message sending through orchestrator
                await performance_orchestrator.message_bus.publish(
                    TestDataFactory.create_message(
                        topic="throughput_test",
                        payload=message_payload,
                        sender=str(sender.id),
                        recipient=str(recipient.id)
                    )
                )
                
                message_count += 1
            
            # Brief pause to prevent overwhelming
            await asyncio.sleep(0.001)
        
        actual_duration = time.time() - start_time
        actual_throughput = message_count / actual_duration
        
        print(f"\nMessage Throughput Test Results:")
        print(f"Messages sent: {message_count}")
        print(f"Duration: {actual_duration:.2f}s")
        print(f"Actual throughput: {actual_throughput:.2f} messages/sec")
        print(f"Target throughput: {target_throughput} messages/sec")
        
        # Assert throughput target
        assert actual_throughput >= target_throughput * 0.8, \
            f"Throughput too low: {actual_throughput} < {target_throughput * 0.8}"

    async def test_state_operation_latency(self, performance_orchestrator, performance_metrics):
        """Test state operations meet latency target of <100ms p99."""
        num_operations = 1000
        latencies = []
        
        # Test different state operations
        operations = [
            ("store_task", self._benchmark_store_task),
            ("retrieve_task", self._benchmark_retrieve_task),
            ("update_task", self._benchmark_update_task),
            ("store_agent", self._benchmark_store_agent),
            ("retrieve_agent", self._benchmark_retrieve_agent)
        ]
        
        for operation_name, operation_func in operations:
            operation_latencies = []
            
            for i in range(num_operations // len(operations)):
                start_time = time.time()
                await operation_func(performance_orchestrator)
                latency = (time.time() - start_time) * 1000  # Convert to ms
                operation_latencies.append(latency)
            
            latencies.extend(operation_latencies)
            
            # Calculate percentiles for this operation
            operation_latencies.sort()
            p50 = operation_latencies[len(operation_latencies) // 2]
            p95 = operation_latencies[int(len(operation_latencies) * 0.95)]
            p99 = operation_latencies[int(len(operation_latencies) * 0.99)]
            
            performance_metrics.record_metric(f"{operation_name}_p50_ms", p50)
            performance_metrics.record_metric(f"{operation_name}_p95_ms", p95)
            performance_metrics.record_metric(f"{operation_name}_p99_ms", p99)
            
            print(f"{operation_name}: p50={p50:.2f}ms, p95={p95:.2f}ms, p99={p99:.2f}ms")
        
        # Overall latency analysis
        latencies.sort()
        overall_p99 = latencies[int(len(latencies) * 0.99)]
        performance_metrics.record_metric("overall_p99_latency_ms", overall_p99)
        
        # Assert latency target
        assert overall_p99 < 100.0, f"p99 latency too high: {overall_p99:.2f}ms"

    async def test_checkpoint_save_time(self, performance_orchestrator, performance_metrics):
        """Test checkpoint save time meets target of <5 seconds."""
        # Create significant system state
        num_agents = 20
        num_tasks = 100
        
        # Create agents
        for i in range(num_agents):
            await performance_orchestrator.create_agent(
                agent_type=f"checkpoint_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
        
        # Create and submit tasks
        for i in range(num_tasks):
            task = TestDataFactory.create_task(f"Checkpoint Task {i}")
            await performance_orchestrator.submit_task(task)
        
        # Measure checkpoint creation time
        checkpoint_times = []
        for i in range(5):  # Multiple checkpoint samples
            start_time = time.time()
            checkpoint_id = await performance_orchestrator.create_checkpoint(f"perf_test_{i}")
            checkpoint_time = time.time() - start_time
            checkpoint_times.append(checkpoint_time)
            
            # Verify checkpoint was created
            assert checkpoint_id is not None
        
        avg_checkpoint_time = mean(checkpoint_times)
        max_checkpoint_time = max(checkpoint_times)
        
        performance_metrics.record_metric("avg_checkpoint_time", avg_checkpoint_time)
        performance_metrics.record_metric("max_checkpoint_time", max_checkpoint_time)
        
        print(f"Checkpoint Performance:")
        print(f"Average time: {avg_checkpoint_time:.2f}s")
        print(f"Maximum time: {max_checkpoint_time:.2f}s")
        
        # Assert checkpoint time target
        assert avg_checkpoint_time < 5.0, f"Average checkpoint time too slow: {avg_checkpoint_time:.2f}s"
        assert max_checkpoint_time < 10.0, f"Maximum checkpoint time too slow: {max_checkpoint_time:.2f}s"

    async def test_recovery_time_target(self, performance_orchestrator, performance_metrics):
        """Test recovery time meets target of <60 seconds."""
        # Create system state
        num_agents = 15
        num_tasks = 50
        
        agents = []
        tasks = []
        
        # Create agents and tasks
        for i in range(num_agents):
            agent = await performance_orchestrator.create_agent(
                agent_type=f"recovery_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        for i in range(num_tasks):
            task = TestDataFactory.create_task(f"Recovery Task {i}")
            await performance_orchestrator.submit_task(task)
            tasks.append(task)
        
        # Create checkpoint
        checkpoint_id = await performance_orchestrator.create_checkpoint("pre_recovery")
        
        # Simulate system failure and recovery
        await performance_orchestrator.shutdown()
        
        # Measure recovery time
        recovery_start = time.time()
        
        # Restart orchestrator
        await performance_orchestrator.start()
        
        # Restore from checkpoint
        restore_success = await performance_orchestrator.restore_checkpoint(checkpoint_id)
        assert restore_success, "Failed to restore from checkpoint"
        
        # Wait for system to become fully operational
        await AsyncTestRunner.wait_for_condition(
            lambda: performance_orchestrator._running,
            timeout=30.0
        )
        
        recovery_time = time.time() - recovery_start
        
        # Verify system state after recovery
        system_status = await performance_orchestrator.get_system_status()
        assert system_status["running"], "System not running after recovery"
        
        performance_metrics.record_metric("recovery_time", recovery_time)
        
        print(f"Recovery Performance:")
        print(f"Recovery time: {recovery_time:.2f}s")
        
        # Assert recovery time target
        assert recovery_time < 60.0, f"Recovery time too slow: {recovery_time:.2f}s"

    # Helper methods
    
    async def _wait_for_task_completion(self, orchestrator, tasks, timeout=60.0):
        """Wait for tasks to complete and return completed tasks."""
        completed_tasks = []
        start_time = time.time()
        
        while len(completed_tasks) < len(tasks) and (time.time() - start_time) < timeout:
            for task in tasks:
                if task.id not in [t.id for t in completed_tasks]:
                    updated_task = await orchestrator.get_task(task.id)
                    if updated_task and updated_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        completed_tasks.append(updated_task)
            
            await asyncio.sleep(0.1)
        
        return completed_tasks

    async def _benchmark_store_task(self, orchestrator):
        """Benchmark task storage operation."""
        task = TestDataFactory.create_task()
        await orchestrator.state_manager.store_object('tasks', task)

    async def _benchmark_retrieve_task(self, orchestrator):
        """Benchmark task retrieval operation."""
        # First store a task
        task = TestDataFactory.create_task()
        await orchestrator.state_manager.store_object('tasks', task)
        # Then retrieve it
        await orchestrator.state_manager.get_object('tasks', task.id)

    async def _benchmark_update_task(self, orchestrator):
        """Benchmark task update operation."""
        task = TestDataFactory.create_task()
        await orchestrator.state_manager.store_object('tasks', task)
        task.status = TaskStatus.RUNNING
        await orchestrator.state_manager.store_object('tasks', task)

    async def _benchmark_store_agent(self, orchestrator):
        """Benchmark agent storage operation."""
        agent = TestDataFactory.create_agent()
        await orchestrator.state_manager.store_object('agents', agent)

    async def _benchmark_retrieve_agent(self, orchestrator):
        """Benchmark agent retrieval operation."""
        agent = TestDataFactory.create_agent()
        await orchestrator.state_manager.store_object('agents', agent)
        await orchestrator.state_manager.get_object('agents', agent.id)