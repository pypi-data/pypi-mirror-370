"""
Chaos engineering tests for agent failure scenarios.
"""

import pytest
import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4

from src.maos.core.orchestrator import Orchestrator
from src.maos.models.task import Task, TaskStatus
from src.maos.models.agent import Agent, AgentStatus, AgentCapability
from tests.utils.test_helpers import TestDataFactory, AsyncTestRunner, StateVerifier


@pytest.mark.chaos
@pytest.mark.slow
class TestAgentFailures:
    """Chaos engineering tests for agent failure scenarios."""

    async def test_random_agent_crashes(self, orchestrator, load_generator, chaos_injection):
        """Test system resilience to random agent crashes."""
        num_agents = 10
        num_tasks = 50
        failure_rate = 0.3  # 30% of agents will crash
        
        # Create agents
        agents = []
        for i in range(num_agents):
            agent = await orchestrator.create_agent(
                agent_type=f"crash_test_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION}
            )
            agents.append(agent)
        
        # Generate tasks
        tasks = load_generator.generate_tasks(num_tasks)
        
        # Submit all tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Randomly crash agents during execution
        num_failures = int(num_agents * failure_rate)
        failing_agents = random.sample(agents, num_failures)
        
        # Introduce failures at random intervals
        failure_tasks = []
        for agent in failing_agents:
            delay = random.uniform(1.0, 10.0)  # Random delay between 1-10 seconds
            failure_tasks.append(
                self._delayed_agent_failure(chaos_injection, agent, delay)
            )
        
        # Start failure injection
        await asyncio.gather(*failure_tasks, return_exceptions=True)
        
        # Wait for system recovery and task completion
        completed_tasks = []
        timeout = 120.0  # Longer timeout due to failures
        start_time = datetime.utcnow()
        
        while len(completed_tasks) < len(tasks) * 0.7 and \
              (datetime.utcnow() - start_time).total_seconds() < timeout:
            
            for task in tasks:
                if task.id not in [t.id for t in completed_tasks]:
                    updated_task = await orchestrator.get_task(task.id)
                    if updated_task and updated_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        completed_tasks.append(updated_task)
            
            await asyncio.sleep(0.5)
        
        # Analyze results
        successful_tasks = [t for t in completed_tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in completed_tasks if t.status == TaskStatus.FAILED]
        
        print(f"\nChaos Test Results:")
        print(f"Agents crashed: {len(failing_agents)}/{num_agents}")
        print(f"Tasks completed: {len(successful_tasks)}/{num_tasks}")
        print(f"Tasks failed: {len(failed_tasks)}/{num_tasks}")
        print(f"Tasks pending: {num_tasks - len(completed_tasks)}")
        
        # Assertions for resilience
        success_rate = len(successful_tasks) / num_tasks
        assert success_rate >= 0.6, f"Too many tasks failed: {success_rate:.2f} success rate"
        
        # Verify system is still operational
        system_status = await orchestrator.get_system_status()
        assert system_status["running"], "System not running after failures"

    async def test_cascading_agent_failures(self, orchestrator, chaos_injection):
        """Test system behavior under cascading agent failures."""
        num_agents = 8
        num_tasks = 30
        
        # Create agents with interdependencies
        agents = []
        for i in range(num_agents):
            agent = await orchestrator.create_agent(
                agent_type=f"cascade_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION},
                configuration={"failure_probability": 0.1}  # Each agent has 10% failure chance
            )
            agents.append(agent)
        
        # Create tasks with dependencies that could trigger cascades
        tasks = []
        for i in range(num_tasks):
            task = TestDataFactory.create_task(
                name=f"Cascade Task {i}",
                timeout_seconds=30
            )
            tasks.append(task)
        
        # Submit tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Let tasks start executing
        await asyncio.sleep(2.0)
        
        # Trigger initial failure
        initial_failure = agents[0]
        await chaos_injection.inject_agent_failure(initial_failure, "crash")
        
        # Monitor for cascading failures
        failure_times = []
        failed_agents = [initial_failure]
        
        # Check for additional failures over time
        for check_round in range(10):  # Check for 10 seconds
            await asyncio.sleep(1.0)
            
            current_failed = []
            for agent in agents:
                updated_agent = await orchestrator.get_agent(agent.id)
                if updated_agent and updated_agent.status in [AgentStatus.OFFLINE, AgentStatus.TERMINATED]:
                    if agent not in failed_agents:
                        current_failed.append(agent)
                        failure_times.append(datetime.utcnow())
            
            failed_agents.extend(current_failed)
            
            if len(current_failed) > 0:
                print(f"Round {check_round}: {len(current_failed)} additional failures detected")
        
        # Wait for system stabilization
        await asyncio.sleep(10.0)
        
        # Analyze cascade pattern
        cascade_count = len(failed_agents) - 1  # Exclude initial failure
        cascade_percentage = len(failed_agents) / num_agents
        
        print(f"\nCascading Failure Analysis:")
        print(f"Initial failures: 1")
        print(f"Cascaded failures: {cascade_count}")
        print(f"Total failed agents: {len(failed_agents)}/{num_agents}")
        print(f"Cascade percentage: {cascade_percentage:.2%}")
        
        # System should contain cascading failures
        assert cascade_percentage < 0.8, f"Too much cascade damage: {cascade_percentage:.2%}"
        
        # Some agents should remain operational
        operational_agents = num_agents - len(failed_agents)
        assert operational_agents >= 2, f"Too few operational agents: {operational_agents}"

    async def test_agent_memory_exhaustion(self, orchestrator, chaos_injection):
        """Test system behavior when agents run out of memory."""
        num_agents = 5
        memory_intensive_tasks = 20
        
        # Create agents with limited memory
        agents = []
        for i in range(num_agents):
            agent = await orchestrator.create_agent(
                agent_type=f"memory_limited_agent_{i}",
                capabilities={AgentCapability.DATA_PROCESSING},
                configuration={
                    "memory_limit_mb": 256,  # Limited memory
                    "max_concurrent_tasks": 1
                }
            )
            agents.append(agent)
        
        # Create memory-intensive tasks
        tasks = []
        for i in range(memory_intensive_tasks):
            task = TestDataFactory.create_task(
                name=f"Memory Heavy Task {i}",
                parameters={
                    "data_size_mb": 100,  # Each task uses 100MB
                    "processing_type": "memory_intensive"
                }
            )
            tasks.append(task)
        
        # Submit tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Simulate memory pressure after some tasks start
        await asyncio.sleep(3.0)
        
        # Inject memory exhaustion on some agents
        memory_exhausted_agents = agents[:2]  # Exhaust 2 agents
        for agent in memory_exhausted_agents:
            await chaos_injection.inject_resource_exhaustion(
                agent, resource_type="memory", severity=0.95
            )
        
        # Monitor system response
        await asyncio.sleep(5.0)
        
        # Check agent status
        healthy_agents = []
        exhausted_agents = []
        
        for agent in agents:
            updated_agent = await orchestrator.get_agent(agent.id)
            if updated_agent:
                if updated_agent.status == AgentStatus.OVERLOADED:
                    exhausted_agents.append(agent)
                elif updated_agent.status in [AgentStatus.IDLE, AgentStatus.BUSY]:
                    healthy_agents.append(agent)
        
        # Wait for task completion with remaining agents
        completed_tasks = []
        timeout = 60.0
        start_time = datetime.utcnow()
        
        while len(completed_tasks) < len(tasks) * 0.5 and \
              (datetime.utcnow() - start_time).total_seconds() < timeout:
            
            for task in tasks:
                if task.id not in [t.id for t in completed_tasks]:
                    updated_task = await orchestrator.get_task(task.id)
                    if updated_task and updated_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        completed_tasks.append(updated_task)
            
            await asyncio.sleep(1.0)
        
        print(f"\nMemory Exhaustion Test Results:")
        print(f"Healthy agents: {len(healthy_agents)}")
        print(f"Exhausted agents: {len(exhausted_agents)}")
        print(f"Completed tasks: {len(completed_tasks)}/{len(tasks)}")
        
        # System should handle memory pressure gracefully
        assert len(healthy_agents) >= 1, "No healthy agents remaining"
        completion_rate = len(completed_tasks) / len(tasks)
        assert completion_rate >= 0.4, f"Too few tasks completed under memory pressure: {completion_rate:.2%}"

    async def test_agent_network_partition(self, orchestrator, chaos_injection):
        """Test agent behavior during network partitions."""
        num_agents = 6
        num_tasks = 20
        
        # Create agents
        agents = []
        for i in range(num_agents):
            agent = await orchestrator.create_agent(
                agent_type=f"network_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.COMMUNICATION}
            )
            agents.append(agent)
        
        # Create tasks that require inter-agent communication
        tasks = []
        for i in range(num_tasks):
            task = TestDataFactory.create_task(
                name=f"Network Task {i}",
                parameters={
                    "requires_communication": True,
                    "coordination_needed": True
                }
            )
            tasks.append(task)
        
        # Submit tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Let some tasks start
        await asyncio.sleep(2.0)
        
        # Partition agents into two groups
        group1 = agents[:3]
        group2 = agents[3:]
        
        # Create network partition between groups
        partition_start = datetime.utcnow()
        await chaos_injection.inject_network_partition(
            group1_agents=group1,
            group2_agents=group2
        )
        
        print(f"Network partition created between {len(group1)} and {len(group2)} agents")
        
        # Monitor system behavior during partition
        partition_duration = 15.0  # 15 seconds
        await asyncio.sleep(partition_duration)
        
        # Heal partition
        await chaos_injection.heal_network_partition()
        partition_end = datetime.utcnow()
        
        print(f"Network partition healed after {(partition_end - partition_start).total_seconds():.1f}s")
        
        # Wait for system recovery and task completion
        await asyncio.sleep(10.0)
        
        completed_tasks = []
        for task in tasks:
            updated_task = await orchestrator.get_task(task.id)
            if updated_task and updated_task.status == TaskStatus.COMPLETED:
                completed_tasks.append(updated_task)
        
        # Check agent connectivity post-partition
        connected_agents = []
        for agent in agents:
            updated_agent = await orchestrator.get_agent(agent.id)
            if updated_agent and updated_agent.status in [AgentStatus.IDLE, AgentStatus.BUSY]:
                connected_agents.append(agent)
        
        print(f"\nNetwork Partition Test Results:")
        print(f"Connected agents post-partition: {len(connected_agents)}/{num_agents}")
        print(f"Completed tasks: {len(completed_tasks)}/{num_tasks}")
        
        # Most agents should reconnect after partition healing
        assert len(connected_agents) >= num_agents * 0.8, "Too many agents disconnected post-partition"
        
        # System should continue operating despite partition
        completion_rate = len(completed_tasks) / num_tasks
        assert completion_rate >= 0.3, f"Too few tasks completed during network issues: {completion_rate:.2%}"

    async def test_byzantine_agent_behavior(self, orchestrator, chaos_injection):
        """Test system resilience to byzantine (malicious) agent behavior."""
        num_agents = 9  # Need odd number for byzantine fault tolerance
        num_tasks = 15
        byzantine_count = 2  # Up to f=(n-1)/3 byzantine agents for n=9
        
        # Create agents
        agents = []
        for i in range(num_agents):
            agent = await orchestrator.create_agent(
                agent_type=f"consensus_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.COORDINATION}
            )
            agents.append(agent)
        
        # Create tasks requiring consensus
        tasks = []
        for i in range(num_tasks):
            task = TestDataFactory.create_task(
                name=f"Consensus Task {i}",
                parameters={
                    "requires_consensus": True,
                    "consensus_threshold": 0.67  # 2/3 majority
                }
            )
            tasks.append(task)
        
        # Submit tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Let system start processing
        await asyncio.sleep(3.0)
        
        # Make some agents byzantine
        byzantine_agents = agents[:byzantine_count]
        for agent in byzantine_agents:
            await chaos_injection.inject_byzantine_behavior(
                agent,
                behavior_type=random.choice([
                    "send_conflicting_messages",
                    "ignore_consensus",
                    "report_false_results",
                    "delay_responses"
                ])
            )
        
        print(f"Injected byzantine behavior in {len(byzantine_agents)} agents")
        
        # Monitor consensus and task completion
        consensus_failures = 0
        completed_tasks = []
        timeout = 45.0
        start_time = datetime.utcnow()
        
        while len(completed_tasks) < len(tasks) * 0.8 and \
              (datetime.utcnow() - start_time).total_seconds() < timeout:
            
            for task in tasks:
                if task.id not in [t.id for t in completed_tasks]:
                    updated_task = await orchestrator.get_task(task.id)
                    if updated_task and updated_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        completed_tasks.append(updated_task)
                        
                        # Check if failure was due to consensus issues
                        if updated_task.status == TaskStatus.FAILED and \
                           updated_task.error and "consensus" in updated_task.error.lower():
                            consensus_failures += 1
            
            await asyncio.sleep(1.0)
        
        # Analyze byzantine fault tolerance
        successful_tasks = [t for t in completed_tasks if t.status == TaskStatus.COMPLETED]
        honest_agents = num_agents - byzantine_count
        
        print(f"\nByzantine Fault Tolerance Test Results:")
        print(f"Byzantine agents: {byzantine_count}/{num_agents}")
        print(f"Honest agents: {honest_agents}/{num_agents}")
        print(f"Successful tasks: {len(successful_tasks)}/{num_tasks}")
        print(f"Consensus failures: {consensus_failures}")
        
        # System should tolerate up to f byzantine agents where f < n/3
        expected_tolerance = (num_agents - 1) // 3
        assert byzantine_count <= expected_tolerance, "Too many byzantine agents for test validity"
        
        # Most tasks should still complete successfully
        success_rate = len(successful_tasks) / num_tasks
        assert success_rate >= 0.6, f"Byzantine agents caused too many failures: {success_rate:.2%}"

    async def test_agent_resource_starvation(self, orchestrator, chaos_injection):
        """Test system behavior under resource starvation conditions."""
        num_agents = 4
        num_tasks = 16
        
        # Create agents with varying resource limits
        agents = []
        for i in range(num_agents):
            agent = await orchestrator.create_agent(
                agent_type=f"resource_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION},
                configuration={
                    "cpu_limit": 1.0,
                    "memory_limit_mb": 512,
                    "max_concurrent_tasks": 2
                }
            )
            agents.append(agent)
        
        # Create resource-intensive tasks
        tasks = []
        for i in range(num_tasks):
            task = TestDataFactory.create_task(
                name=f"Resource Task {i}",
                resource_requirements={
                    "cpu": random.uniform(0.5, 2.0),
                    "memory": random.randint(128, 768),
                    "io_operations": random.randint(100, 1000)
                }
            )
            tasks.append(task)
        
        # Submit tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Create artificial resource scarcity
        await asyncio.sleep(2.0)
        
        # Reduce available resources system-wide
        await chaos_injection.inject_resource_scarcity(
            resource_types=["cpu", "memory"],
            reduction_factor=0.6  # Reduce by 60%
        )
        
        # Monitor resource allocation and task progress
        starved_agents = []
        resource_conflicts = 0
        completed_tasks = []
        
        timeout = 60.0
        start_time = datetime.utcnow()
        
        while len(completed_tasks) < len(tasks) * 0.5 and \
              (datetime.utcnow() - start_time).total_seconds() < timeout:
            
            # Check agent resource status
            for agent in agents:
                updated_agent = await orchestrator.get_agent(agent.id)
                if updated_agent and updated_agent.status == AgentStatus.OVERLOADED:
                    if agent not in starved_agents:
                        starved_agents.append(agent)
            
            # Check task progress
            for task in tasks:
                if task.id not in [t.id for t in completed_tasks]:
                    updated_task = await orchestrator.get_task(task.id)
                    if updated_task and updated_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        completed_tasks.append(updated_task)
                        
                        if updated_task.status == TaskStatus.FAILED and \
                           updated_task.error and "resource" in updated_task.error.lower():
                            resource_conflicts += 1
            
            await asyncio.sleep(1.0)
        
        # Restore resources
        await chaos_injection.restore_resources()
        
        print(f"\nResource Starvation Test Results:")
        print(f"Starved agents: {len(starved_agents)}/{num_agents}")
        print(f"Resource conflicts: {resource_conflicts}")
        print(f"Completed tasks: {len(completed_tasks)}/{num_tasks}")
        
        # System should handle resource starvation gracefully
        starvation_rate = len(starved_agents) / num_agents
        assert starvation_rate < 1.0, "All agents starved - system failed"
        
        completion_rate = len(completed_tasks) / num_tasks
        assert completion_rate >= 0.3, f"Too few tasks completed under resource starvation: {completion_rate:.2%}"

    # Helper methods
    
    async def _delayed_agent_failure(self, chaos_injection, agent, delay):
        """Inject agent failure after specified delay."""
        await asyncio.sleep(delay)
        await chaos_injection.inject_agent_failure(agent, "crash")