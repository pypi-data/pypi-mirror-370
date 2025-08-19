"""
Fixtures and utilities for chaos engineering tests.
"""

import asyncio
import random
from typing import List, Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock

from src.maos.models.agent import Agent, AgentStatus
from src.maos.models.resource import Resource
from src.communication.message_bus.core import MessageBus


class ChaosInjection:
    """Enhanced chaos injection utility with realistic failure scenarios."""
    
    def __init__(self):
        self.active_failures = []
        self.network_partitions = []
        self.resource_constraints = {}
        self.byzantine_agents = []
        self.original_states = {}

    async def inject_agent_failure(self, agent: Agent, failure_type: str = "crash"):
        """Inject various types of agent failures."""
        # Store original state for potential recovery
        self.original_states[agent.id] = {
            "status": agent.status,
            "current_task_id": agent.current_task_id,
            "task_queue": agent.task_queue.copy()
        }
        
        if failure_type == "crash":
            agent.status = AgentStatus.OFFLINE
            agent.current_task_id = None
            agent.task_queue.clear()
            
        elif failure_type == "hang":
            agent.status = AgentStatus.UNHEALTHY
            # Keep task but make it unresponsive
            
        elif failure_type == "overload":
            agent.status = AgentStatus.OVERLOADED
            # Simulate resource exhaustion
            agent.metrics.cpu_usage_percent = 100.0
            agent.metrics.memory_usage_mb = agent.resource_limits.get("memory_mb", 1024)
            
        elif failure_type == "intermittent":
            # Random status changes
            statuses = [AgentStatus.UNHEALTHY, AgentStatus.OFFLINE, AgentStatus.IDLE]
            agent.status = random.choice(statuses)
            
        self.active_failures.append((agent.id, failure_type))

    async def inject_network_partition(self, group1_agents: List[Agent], group2_agents: List[Agent]):
        """Simulate network partition between agent groups."""
        partition_id = f"partition_{len(self.network_partitions)}"
        
        partition = {
            "id": partition_id,
            "group1": [agent.id for agent in group1_agents],
            "group2": [agent.id for agent in group2_agents],
            "active": True
        }
        
        self.network_partitions.append(partition)
        
        # Simulate network isolation effects
        for agent in group1_agents + group2_agents:
            # Increase heartbeat intervals to simulate connectivity issues
            agent.health_check_interval *= 2
            agent.heartbeat_timeout *= 2

    async def heal_network_partition(self, partition_id: Optional[str] = None):
        """Heal network partition (all partitions if none specified)."""
        if partition_id:
            partitions_to_heal = [p for p in self.network_partitions if p["id"] == partition_id]
        else:
            partitions_to_heal = self.network_partitions.copy()
        
        for partition in partitions_to_heal:
            partition["active"] = False
            # Restore normal network parameters
            # In real implementation, would restore connectivity

    async def inject_resource_exhaustion(self, agent: Agent, resource_type: str, severity: float = 0.9):
        """Inject resource exhaustion scenarios."""
        if resource_type == "memory":
            max_memory = agent.resource_limits.get("memory_mb", 1024)
            agent.metrics.memory_usage_mb = max_memory * severity
            
        elif resource_type == "cpu":
            agent.metrics.cpu_usage_percent = 100.0 * severity
            
        elif resource_type == "disk":
            # Simulate disk space exhaustion
            agent.metadata["disk_usage_percent"] = 100.0 * severity
            
        if severity >= 0.9:
            agent.status = AgentStatus.OVERLOADED

    async def inject_resource_scarcity(self, resource_types: List[str], reduction_factor: float = 0.5):
        """Create system-wide resource scarcity."""
        for resource_type in resource_types:
            self.resource_constraints[resource_type] = {
                "original_capacity": 1.0,
                "reduced_capacity": 1.0 - reduction_factor,
                "active": True
            }

    async def restore_resources(self):
        """Restore all resource constraints."""
        for resource_type in self.resource_constraints:
            self.resource_constraints[resource_type]["active"] = False

    async def inject_byzantine_behavior(self, agent: Agent, behavior_type: str):
        """Inject byzantine (malicious) agent behavior."""
        byzantine_config = {
            "agent_id": agent.id,
            "behavior_type": behavior_type,
            "active": True
        }
        
        if behavior_type == "send_conflicting_messages":
            # Agent sends conflicting information
            agent.metadata["byzantine_behavior"] = "conflicting_messages"
            
        elif behavior_type == "ignore_consensus":
            # Agent ignores consensus protocols
            agent.metadata["byzantine_behavior"] = "ignore_consensus"
            
        elif behavior_type == "report_false_results":
            # Agent reports incorrect task results
            agent.metadata["byzantine_behavior"] = "false_results"
            
        elif behavior_type == "delay_responses":
            # Agent introduces delays in responses
            agent.metadata["byzantine_behavior"] = "delayed_responses"
            agent.health_check_interval *= 5
            
        self.byzantine_agents.append(byzantine_config)

    async def inject_cascading_failure(self, initial_agent: Agent, cascade_probability: float = 0.3):
        """Inject failure that may cascade to other agents."""
        await self.inject_agent_failure(initial_agent, "crash")
        
        # Store cascade configuration
        self.active_failures.append({
            "type": "cascading",
            "initial_agent": initial_agent.id,
            "cascade_probability": cascade_probability,
            "active": True
        })

    async def inject_correlated_failures(self, agents: List[Agent], correlation_factor: float = 0.8):
        """Inject correlated failures across multiple agents."""
        if correlation_factor > random.random():
            # All agents fail together (correlated)
            for agent in agents:
                await self.inject_agent_failure(agent, "crash")
        else:
            # Random subset fails
            failure_count = max(1, int(len(agents) * 0.3))
            failing_agents = random.sample(agents, failure_count)
            for agent in failing_agents:
                await self.inject_agent_failure(agent, random.choice(["crash", "hang", "overload"]))

    async def inject_slow_network(self, latency_multiplier: float = 3.0):
        """Simulate slow network conditions."""
        self.resource_constraints["network_latency"] = {
            "multiplier": latency_multiplier,
            "active": True
        }

    async def inject_message_loss(self, loss_rate: float = 0.1):
        """Simulate message loss in communication."""
        self.resource_constraints["message_loss"] = {
            "loss_rate": loss_rate,
            "active": True
        }

    async def inject_clock_skew(self, skew_seconds: float = 30.0):
        """Simulate clock synchronization issues."""
        self.resource_constraints["clock_skew"] = {
            "skew_seconds": skew_seconds,
            "active": True
        }

    async def recover_agent(self, agent_id):
        """Recover a specific agent from failure."""
        if agent_id in self.original_states:
            original_state = self.original_states[agent_id]
            # In real implementation, would restore agent state
            
        # Remove from active failures
        self.active_failures = [
            f for f in self.active_failures 
            if f[0] != agent_id if isinstance(f, tuple) else f.get("initial_agent") != agent_id
        ]

    async def get_failure_summary(self) -> Dict[str, Any]:
        """Get summary of all active chaos conditions."""
        return {
            "agent_failures": len([f for f in self.active_failures if isinstance(f, tuple)]),
            "network_partitions": len([p for p in self.network_partitions if p["active"]]),
            "resource_constraints": len([c for c in self.resource_constraints.values() if c.get("active")]),
            "byzantine_agents": len([b for b in self.byzantine_agents if b["active"]]),
            "total_chaos_conditions": (
                len([f for f in self.active_failures if isinstance(f, tuple)]) +
                len([p for p in self.network_partitions if p["active"]]) +
                len([c for c in self.resource_constraints.values() if c.get("active")]) +
                len([b for b in self.byzantine_agents if b["active"]])
            )
        }

    def clear_all_chaos(self):
        """Clear all chaos conditions."""
        self.active_failures.clear()
        self.network_partitions.clear()
        self.resource_constraints.clear()
        self.byzantine_agents.clear()
        self.original_states.clear()


class NetworkChaosSimulator:
    """Simulate network-level chaos conditions."""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.original_methods = {}
        self.chaos_conditions = {}

    async def inject_latency(self, base_latency_ms: float, jitter_ms: float = 0.0):
        """Add artificial latency to message delivery."""
        self.chaos_conditions["latency"] = {
            "base_ms": base_latency_ms,
            "jitter_ms": jitter_ms,
            "active": True
        }

    async def inject_packet_loss(self, loss_rate: float):
        """Simulate packet loss in message delivery."""
        self.chaos_conditions["packet_loss"] = {
            "rate": loss_rate,
            "active": True
        }

    async def inject_connection_drops(self, drop_probability: float):
        """Simulate random connection drops."""
        self.chaos_conditions["connection_drops"] = {
            "probability": drop_probability,
            "active": True
        }

    async def inject_bandwidth_limit(self, max_messages_per_second: int):
        """Limit message throughput to simulate bandwidth constraints."""
        self.chaos_conditions["bandwidth_limit"] = {
            "max_mps": max_messages_per_second,
            "active": True
        }

    def clear_network_chaos(self):
        """Clear all network chaos conditions."""
        self.chaos_conditions.clear()


class ResourceChaosSimulator:
    """Simulate resource-level chaos conditions."""
    
    def __init__(self):
        self.resource_limits = {}
        self.contention_scenarios = {}

    async def create_resource_contention(self, resource_type: str, contention_factor: float):
        """Create artificial resource contention."""
        self.contention_scenarios[resource_type] = {
            "factor": contention_factor,
            "active": True
        }

    async def limit_resource_capacity(self, resource_type: str, capacity_reduction: float):
        """Reduce available resource capacity."""
        self.resource_limits[resource_type] = {
            "reduction": capacity_reduction,
            "active": True
        }

    async def inject_resource_leaks(self, resource_type: str, leak_rate: float):
        """Simulate gradual resource leaks."""
        self.resource_limits[f"{resource_type}_leak"] = {
            "rate": leak_rate,
            "active": True
        }

    def clear_resource_chaos(self):
        """Clear all resource chaos conditions."""
        self.resource_limits.clear()
        self.contention_scenarios.clear()


# Chaos test scenarios
class ChaosScenarios:
    """Pre-defined chaos engineering scenarios."""
    
    @staticmethod
    async def disaster_recovery_scenario(orchestrator, chaos_injection):
        """Complete system failure and recovery scenario."""
        # Phase 1: Multiple agent failures
        agents = await orchestrator.get_available_agents()
        failing_agents = agents[:len(agents)//2]  # Fail half the agents
        
        for agent in failing_agents:
            await chaos_injection.inject_agent_failure(agent, "crash")
        
        # Phase 2: Network partition
        remaining_agents = agents[len(agents)//2:]
        if len(remaining_agents) >= 2:
            mid = len(remaining_agents) // 2
            await chaos_injection.inject_network_partition(
                remaining_agents[:mid], 
                remaining_agents[mid:]
            )
        
        # Phase 3: Resource exhaustion
        await chaos_injection.inject_resource_scarcity(["cpu", "memory"], 0.8)
        
        return {
            "failed_agents": len(failing_agents),
            "partitioned_agents": len(remaining_agents),
            "resource_constraints": ["cpu", "memory"]
        }

    @staticmethod
    async def gradual_degradation_scenario(orchestrator, chaos_injection):
        """Simulate gradual system degradation."""
        agents = await orchestrator.get_available_agents()
        
        # Gradually introduce failures over time
        failure_schedule = [
            (2, "slow_network", {}),
            (5, "agent_failure", {"count": 1}),
            (8, "resource_pressure", {"factor": 0.3}),
            (12, "agent_failure", {"count": 2}),
            (15, "network_partition", {"split": 0.5}),
            (20, "byzantine_behavior", {"count": 1})
        ]
        
        return failure_schedule

    @staticmethod
    async def stress_test_scenario(orchestrator, chaos_injection):
        """High-stress scenario with multiple concurrent failures."""
        agents = await orchestrator.get_available_agents()
        
        # Inject multiple failures simultaneously
        tasks = []
        
        # Random agent failures
        failing_agents = random.sample(agents, min(3, len(agents)))
        for agent in failing_agents:
            failure_type = random.choice(["crash", "hang", "overload"])
            tasks.append(chaos_injection.inject_agent_failure(agent, failure_type))
        
        # Network issues
        tasks.append(chaos_injection.inject_slow_network(5.0))
        tasks.append(chaos_injection.inject_message_loss(0.2))
        
        # Resource constraints
        tasks.append(chaos_injection.inject_resource_scarcity(["cpu", "memory", "disk"], 0.7))
        
        await asyncio.gather(*tasks)
        
        return {
            "concurrent_failures": len(tasks),
            "stress_level": "extreme"
        }