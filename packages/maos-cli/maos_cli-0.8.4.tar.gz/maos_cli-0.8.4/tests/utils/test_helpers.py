"""
Test helper utilities and shared testing functions.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.models.agent import Agent, AgentStatus, AgentCapability
from src.maos.models.resource import Resource, ResourceType
from src.maos.models.message import Message, MessageType, MessagePriority


class TestDataFactory:
    """Factory for creating test data objects."""
    
    @staticmethod
    def create_task(
        name: str = "Test Task",
        priority: TaskPriority = TaskPriority.MEDIUM,
        **kwargs
    ) -> Task:
        """Create a test task with sensible defaults."""
        defaults = {
            "description": f"Test task: {name}",
            "parameters": {"test": True},
            "timeout_seconds": 300,
            "resource_requirements": {"cpu": 1.0, "memory": 256}
        }
        defaults.update(kwargs)
        
        return Task(name=name, priority=priority, **defaults)
    
    @staticmethod
    def create_agent(
        name: str = "Test Agent",
        agent_type: str = "test_agent",
        capabilities: Optional[set] = None,
        **kwargs
    ) -> Agent:
        """Create a test agent with sensible defaults."""
        if capabilities is None:
            capabilities = {AgentCapability.TASK_EXECUTION}
        
        defaults = {
            "max_concurrent_tasks": 2,
            "resource_limits": {"cpu_percent": 80, "memory_mb": 1024}
        }
        defaults.update(kwargs)
        
        return Agent(
            name=name,
            type=agent_type,
            capabilities=capabilities,
            **defaults
        )
    
    @staticmethod
    def create_resource(
        name: str = "Test Resource",
        resource_type: ResourceType = ResourceType.CPU,
        capacity: float = 4.0,
        **kwargs
    ) -> Resource:
        """Create a test resource with sensible defaults."""
        defaults = {
            "available_capacity": capacity,
            "metadata": {"test": True}
        }
        defaults.update(kwargs)
        
        return Resource(
            name=name,
            type=resource_type,
            capacity=capacity,
            **defaults
        )
    
    @staticmethod
    def create_message(
        message_type: MessageType = MessageType.TASK_ASSIGNMENT,
        topic: str = "test_topic",
        payload: Optional[Dict] = None,
        **kwargs
    ) -> Message:
        """Create a test message with sensible defaults."""
        if payload is None:
            payload = {"test": True}
        
        defaults = {
            "priority": MessagePriority.MEDIUM,
            "sender": "test_sender"
        }
        defaults.update(kwargs)
        
        return Message(
            type=message_type,
            topic=topic,
            payload=payload,
            **defaults
        )


class MockManager:
    """Utility for managing mocks in tests."""
    
    def __init__(self):
        self.mocks = {}
        self.patches = {}
    
    def create_mock(self, name: str, spec=None) -> MagicMock:
        """Create and store a mock."""
        mock = MagicMock(spec=spec)
        self.mocks[name] = mock
        return mock
    
    def create_async_mock(self, name: str, spec=None) -> AsyncMock:
        """Create and store an async mock."""
        mock = AsyncMock(spec=spec)
        self.mocks[name] = mock
        return mock
    
    def patch_object(self, target: str, attribute: str, new=None):
        """Create and start a patch."""
        if new is None:
            new = AsyncMock() if attribute.startswith('async_') else MagicMock()
        
        patcher = patch.object(target, attribute, new)
        self.patches[f"{target}.{attribute}"] = patcher
        return patcher.start()
    
    def patch(self, target: str, new=None):
        """Create and start a patch."""
        if new is None:
            new = AsyncMock() if 'async' in target else MagicMock()
        
        patcher = patch(target, new)
        self.patches[target] = patcher
        return patcher.start()
    
    def stop_all(self):
        """Stop all patches."""
        for patcher in self.patches.values():
            patcher.stop()
        self.patches.clear()


class PerformanceTimer:
    """Utility for timing operations in tests."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.durations = []
    
    def start(self):
        """Start timing."""
        self.start_time = datetime.utcnow()
    
    def stop(self) -> float:
        """Stop timing and return duration."""
        self.end_time = datetime.utcnow()
        duration = (self.end_time - self.start_time).total_seconds()
        self.durations.append(duration)
        return duration
    
    def get_average(self) -> float:
        """Get average duration across all measurements."""
        return sum(self.durations) / len(self.durations) if self.durations else 0.0
    
    def get_min(self) -> float:
        """Get minimum duration."""
        return min(self.durations) if self.durations else 0.0
    
    def get_max(self) -> float:
        """Get maximum duration."""
        return max(self.durations) if self.durations else 0.0
    
    def reset(self):
        """Reset all measurements."""
        self.durations.clear()
        self.start_time = None
        self.end_time = None


class AsyncTestRunner:
    """Utility for running async operations in tests."""
    
    @staticmethod
    async def wait_for_condition(
        condition: Callable[[], bool],
        timeout: float = 5.0,
        poll_interval: float = 0.1
    ) -> bool:
        """Wait for a condition to become true."""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if condition():
                return True
            await asyncio.sleep(poll_interval)
        
        return False
    
    @staticmethod
    async def run_concurrent(operations: List[Callable], max_concurrent: int = 10):
        """Run multiple async operations concurrently with limited concurrency."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_operation(op):
            async with semaphore:
                return await op()
        
        tasks = [bounded_operation(op) for op in operations]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    @staticmethod
    async def measure_throughput(
        operation: Callable,
        duration_seconds: float = 10.0,
        max_concurrent: int = 100
    ) -> Dict[str, Any]:
        """Measure throughput of an operation."""
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + duration_seconds
        
        completed_operations = 0
        failed_operations = 0
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def timed_operation():
            nonlocal completed_operations, failed_operations
            
            async with semaphore:
                try:
                    await operation()
                    completed_operations += 1
                except Exception:
                    failed_operations += 1
        
        # Keep launching operations until time expires
        tasks = []
        while asyncio.get_event_loop().time() < end_time:
            task = asyncio.create_task(timed_operation())
            tasks.append(task)
            
            # Brief pause to prevent overwhelming
            await asyncio.sleep(0.001)
        
        # Wait for all operations to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        total_operations = completed_operations + failed_operations
        throughput = total_operations / duration_seconds
        
        return {
            "total_operations": total_operations,
            "completed_operations": completed_operations,
            "failed_operations": failed_operations,
            "success_rate": completed_operations / total_operations if total_operations > 0 else 0,
            "throughput_per_second": throughput,
            "duration_seconds": duration_seconds
        }


class StateVerifier:
    """Utility for verifying system state in tests."""
    
    @staticmethod
    def verify_task_state(task: Task, expected_status: TaskStatus, **expected_attributes):
        """Verify task is in expected state."""
        assert task.status == expected_status, f"Expected status {expected_status}, got {task.status}"
        
        for attr, value in expected_attributes.items():
            actual_value = getattr(task, attr)
            assert actual_value == value, f"Expected {attr}={value}, got {actual_value}"
    
    @staticmethod
    def verify_agent_state(agent: Agent, expected_status: AgentStatus, **expected_attributes):
        """Verify agent is in expected state."""
        assert agent.status == expected_status, f"Expected status {expected_status}, got {agent.status}"
        
        for attr, value in expected_attributes.items():
            actual_value = getattr(agent, attr)
            assert actual_value == value, f"Expected {attr}={value}, got {actual_value}"
    
    @staticmethod
    def verify_metrics_within_bounds(
        metrics: Dict[str, Any],
        bounds: Dict[str, tuple]
    ):
        """Verify metrics are within expected bounds."""
        for metric_name, (min_val, max_val) in bounds.items():
            if metric_name in metrics:
                actual_val = metrics[metric_name]
                assert min_val <= actual_val <= max_val, \
                    f"Metric {metric_name}={actual_val} not in bounds [{min_val}, {max_val}]"


class LogCapture:
    """Utility for capturing and verifying log messages."""
    
    def __init__(self):
        self.captured_logs = []
    
    def capture_log(self, level: str, message: str, **kwargs):
        """Capture a log message."""
        self.captured_logs.append({
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow(),
            **kwargs
        })
    
    def assert_log_contains(self, level: str, substring: str):
        """Assert that logs contain a specific message."""
        matching_logs = [
            log for log in self.captured_logs
            if log["level"] == level and substring in log["message"]
        ]
        assert matching_logs, f"No {level} log containing '{substring}' found"
    
    def get_log_count(self, level: str) -> int:
        """Get count of logs at specific level."""
        return len([log for log in self.captured_logs if log["level"] == level])
    
    def clear(self):
        """Clear captured logs."""
        self.captured_logs.clear()


class ResourceMonitor:
    """Utility for monitoring resource usage during tests."""
    
    def __init__(self):
        self.samples = []
    
    async def start_monitoring(self, interval: float = 1.0):
        """Start monitoring system resources."""
        import psutil
        
        while True:
            sample = {
                "timestamp": datetime.utcnow(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_io": psutil.disk_io_counters()._asdict(),
                "network_io": psutil.net_io_counters()._asdict()
            }
            self.samples.append(sample)
            await asyncio.sleep(interval)
    
    def get_peak_usage(self) -> Dict[str, Any]:
        """Get peak resource usage during monitoring."""
        if not self.samples:
            return {}
        
        return {
            "peak_cpu": max(s["cpu_percent"] for s in self.samples),
            "peak_memory": max(s["memory_percent"] for s in self.samples),
            "avg_cpu": sum(s["cpu_percent"] for s in self.samples) / len(self.samples),
            "avg_memory": sum(s["memory_percent"] for s in self.samples) / len(self.samples)
        }


class TestScenarioBuilder:
    """Builder for complex test scenarios."""
    
    def __init__(self):
        self.tasks = []
        self.agents = []
        self.resources = []
        self.dependencies = []
    
    def add_task(self, task: Task) -> 'TestScenarioBuilder':
        """Add task to scenario."""
        self.tasks.append(task)
        return self
    
    def add_agent(self, agent: Agent) -> 'TestScenarioBuilder':
        """Add agent to scenario."""
        self.agents.append(agent)
        return self
    
    def add_resource(self, resource: Resource) -> 'TestScenarioBuilder':
        """Add resource to scenario."""
        self.resources.append(resource)
        return self
    
    def add_dependency(self, task_id: uuid.UUID, depends_on: uuid.UUID) -> 'TestScenarioBuilder':
        """Add task dependency."""
        self.dependencies.append((task_id, depends_on))
        return self
    
    def build_parallel_workflow(self, num_tasks: int = 5) -> 'TestScenarioBuilder':
        """Build a parallel workflow scenario."""
        for i in range(num_tasks):
            task = TestDataFactory.create_task(
                name=f"Parallel Task {i}",
                priority=TaskPriority.MEDIUM
            )
            self.add_task(task)
        
        return self
    
    def build_sequential_workflow(self, num_tasks: int = 5) -> 'TestScenarioBuilder':
        """Build a sequential workflow scenario."""
        previous_task = None
        
        for i in range(num_tasks):
            task = TestDataFactory.create_task(
                name=f"Sequential Task {i}",
                priority=TaskPriority.MEDIUM
            )
            self.add_task(task)
            
            if previous_task:
                self.add_dependency(task.id, previous_task.id)
            
            previous_task = task
        
        return self
    
    def build_diamond_workflow(self) -> 'TestScenarioBuilder':
        """Build a diamond-shaped dependency workflow."""
        # Start task
        start_task = TestDataFactory.create_task("Start Task")
        self.add_task(start_task)
        
        # Parallel middle tasks
        middle_tasks = []
        for i in range(2):
            task = TestDataFactory.create_task(f"Middle Task {i}")
            self.add_task(task)
            self.add_dependency(task.id, start_task.id)
            middle_tasks.append(task)
        
        # End task (depends on both middle tasks)
        end_task = TestDataFactory.create_task("End Task")
        self.add_task(end_task)
        
        for middle_task in middle_tasks:
            self.add_dependency(end_task.id, middle_task.id)
        
        return self


# Export commonly used utilities
__all__ = [
    'TestDataFactory',
    'MockManager',
    'PerformanceTimer',
    'AsyncTestRunner',
    'StateVerifier',
    'LogCapture',
    'ResourceMonitor',
    'TestScenarioBuilder'
]