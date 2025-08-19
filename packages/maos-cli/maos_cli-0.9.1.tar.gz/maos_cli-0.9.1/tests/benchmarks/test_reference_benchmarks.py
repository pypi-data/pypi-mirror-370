"""
Reference benchmark tests comparing single vs multi-agent performance.
"""

import pytest
import asyncio
import time
from datetime import datetime
from statistics import mean
from typing import List, Dict, Any

from src.maos.core.orchestrator import Orchestrator
from src.maos.models.task import Task, TaskStatus, TaskPriority
from src.maos.models.agent import AgentCapability
from tests.utils.test_helpers import TestDataFactory, PerformanceTimer, AsyncTestRunner


@pytest.mark.benchmark
@pytest.mark.slow
class TestReferenceBenchmarks:
    """Reference benchmarks for single vs multi-agent performance comparison."""

    @pytest.fixture
    async def benchmark_orchestrator(self, mock_persistence):
        """Create orchestrator for benchmarking."""
        config = {
            'agent_manager': {'max_agents': 50},
            'message_bus': {'max_connections': 50},
            'task_planner': {'optimization_enabled': True}
        }
        
        orchestrator = Orchestrator(
            persistence_backend=mock_persistence,
            component_config=config
        )
        await orchestrator.start()
        
        yield orchestrator
        
        await orchestrator.shutdown()

    async def test_single_agent_baseline(self, benchmark_orchestrator):
        """Baseline benchmark: single agent processing sequential tasks."""
        # Reference task: data processing pipeline
        reference_tasks = self._create_reference_task_set()
        
        # Create single agent
        agent = await benchmark_orchestrator.create_agent(
            agent_type="baseline_agent",
            capabilities={
                AgentCapability.TASK_EXECUTION,
                AgentCapability.DATA_PROCESSING,
                AgentCapability.COMPUTATION
            },
            configuration={"max_concurrent_tasks": 1}
        )
        
        print(f"\n=== SINGLE AGENT BASELINE ===")
        print(f"Tasks: {len(reference_tasks)}")
        print(f"Agent: {agent.name} (sequential execution)")
        
        # Execute tasks sequentially
        start_time = time.time()
        
        execution_results = []
        for i, task in enumerate(reference_tasks):
            task_start = time.time()
            
            # Submit and wait for completion
            plan = await benchmark_orchestrator.submit_task(task)
            await benchmark_orchestrator.execute_plan(plan.id)
            
            # Wait for task completion
            await AsyncTestRunner.wait_for_condition(
                lambda: benchmark_orchestrator.get_task(task.id) and 
                       benchmark_orchestrator.get_task(task.id).status in [TaskStatus.COMPLETED, TaskStatus.FAILED],
                timeout=30.0
            )
            
            task_end = time.time()
            task_duration = task_end - task_start
            
            updated_task = await benchmark_orchestrator.get_task(task.id)
            execution_results.append({
                "task_index": i,
                "task_name": task.name,
                "duration": task_duration,
                "status": updated_task.status.value if updated_task else "unknown",
                "success": updated_task.status == TaskStatus.COMPLETED if updated_task else False
            })
            
            print(f"Task {i+1}/{len(reference_tasks)}: {task_duration:.2f}s ({updated_task.status.value if updated_task else 'unknown'})")
        
        total_time = time.time() - start_time
        successful_tasks = [r for r in execution_results if r["success"]]
        
        baseline_metrics = {
            "execution_mode": "single_agent",
            "total_tasks": len(reference_tasks),
            "successful_tasks": len(successful_tasks),
            "success_rate": len(successful_tasks) / len(reference_tasks),
            "total_time": total_time,
            "avg_task_time": mean([r["duration"] for r in execution_results]),
            "throughput": len(successful_tasks) / total_time,
            "agent_count": 1,
            "target_time": 600.0  # 10 minutes baseline target
        }
        
        print(f"\nBaseline Results:")
        print(f"Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        print(f"Success rate: {baseline_metrics['success_rate']:.2%}")
        print(f"Throughput: {baseline_metrics['throughput']:.2f} tasks/sec")
        print(f"Avg task time: {baseline_metrics['avg_task_time']:.2f}s")
        
        # Store baseline for comparison
        self._store_benchmark_result("single_agent_baseline", baseline_metrics)
        
        # Assert baseline performance
        assert baseline_metrics["success_rate"] >= 0.95, "Baseline success rate too low"
        assert total_time <= baseline_metrics["target_time"], f"Baseline too slow: {total_time:.2f}s"
        
        return baseline_metrics

    async def test_multi_agent_parallel_execution(self, benchmark_orchestrator):
        """Multi-agent benchmark: parallel task execution with target 2-3 minute completion."""
        reference_tasks = self._create_reference_task_set()
        agent_count = 5
        target_time_range = (120.0, 180.0)  # 2-3 minutes
        
        # Create multiple agents
        agents = []
        for i in range(agent_count):
            agent = await benchmark_orchestrator.create_agent(
                agent_type=f"parallel_agent_{i}",
                capabilities={
                    AgentCapability.TASK_EXECUTION,
                    AgentCapability.DATA_PROCESSING,
                    AgentCapability.COMPUTATION
                },
                configuration={"max_concurrent_tasks": 2}
            )
            agents.append(agent)
        
        print(f"\n=== MULTI-AGENT PARALLEL EXECUTION ===")
        print(f"Tasks: {len(reference_tasks)}")
        print(f"Agents: {agent_count} (parallel execution)")
        print(f"Target time: {target_time_range[0]:.0f}-{target_time_range[1]:.0f}s")
        
        # Submit all tasks at once
        start_time = time.time()
        execution_plans = []
        
        for task in reference_tasks:
            plan = await benchmark_orchestrator.submit_task(task)
            execution_plans.append(plan)
        
        submission_time = time.time() - start_time
        print(f"Task submission time: {submission_time:.2f}s")
        
        # Execute all plans in parallel
        execution_start = time.time()
        execution_tasks = []
        for plan in execution_plans:
            execution_tasks.append(benchmark_orchestrator.execute_plan(plan.id))
        
        # Start all executions
        await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        # Wait for all tasks to complete
        completed_tasks = []
        timeout = 300.0  # 5 minute timeout
        
        while len(completed_tasks) < len(reference_tasks) and \
              (time.time() - execution_start) < timeout:
            
            for task in reference_tasks:
                if task.id not in [t.id for t in completed_tasks]:
                    updated_task = await benchmark_orchestrator.get_task(task.id)
                    if updated_task and updated_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        completed_tasks.append(updated_task)
            
            await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        execution_time = time.time() - execution_start
        
        # Analyze results
        successful_tasks = [t for t in completed_tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in completed_tasks if t.status == TaskStatus.FAILED]
        
        parallel_metrics = {
            "execution_mode": "multi_agent_parallel",
            "total_tasks": len(reference_tasks),
            "completed_tasks": len(completed_tasks),
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": len(successful_tasks) / len(reference_tasks),
            "completion_rate": len(completed_tasks) / len(reference_tasks),
            "total_time": total_time,
            "execution_time": execution_time,
            "submission_time": submission_time,
            "throughput": len(successful_tasks) / total_time,
            "agent_count": agent_count,
            "target_time_min": target_time_range[0],
            "target_time_max": target_time_range[1]
        }
        
        print(f"\nParallel Execution Results:")
        print(f"Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        print(f"Execution time: {execution_time:.2f}s")
        print(f"Success rate: {parallel_metrics['success_rate']:.2%}")
        print(f"Completion rate: {parallel_metrics['completion_rate']:.2%}")
        print(f"Throughput: {parallel_metrics['throughput']:.2f} tasks/sec")
        print(f"Failed tasks: {len(failed_tasks)}")
        
        # Store results for comparison
        self._store_benchmark_result("multi_agent_parallel", parallel_metrics)
        
        # Assert performance targets
        assert parallel_metrics["success_rate"] >= 0.90, f"Multi-agent success rate too low: {parallel_metrics['success_rate']:.2%}"
        assert parallel_metrics["completion_rate"] >= 0.95, f"Multi-agent completion rate too low: {parallel_metrics['completion_rate']:.2%}"
        assert target_time_range[0] <= total_time <= target_time_range[1], \
            f"Multi-agent time outside target range: {total_time:.2f}s not in [{target_time_range[0]:.0f}, {target_time_range[1]:.0f}]s"
        
        return parallel_metrics

    async def test_speedup_measurement(self, benchmark_orchestrator):
        """Measure and validate speedup between single and multi-agent execution."""
        # Run both benchmarks
        single_agent_metrics = await self.test_single_agent_baseline(benchmark_orchestrator)
        
        # Reset orchestrator state
        await self._reset_orchestrator_state(benchmark_orchestrator)
        
        multi_agent_metrics = await self.test_multi_agent_parallel_execution(benchmark_orchestrator)
        
        # Calculate speedup metrics
        speedup = single_agent_metrics["total_time"] / multi_agent_metrics["total_time"]
        efficiency = speedup / multi_agent_metrics["agent_count"]
        
        throughput_improvement = (
            multi_agent_metrics["throughput"] - single_agent_metrics["throughput"]
        ) / single_agent_metrics["throughput"]
        
        speedup_metrics = {
            "single_agent_time": single_agent_metrics["total_time"],
            "multi_agent_time": multi_agent_metrics["total_time"],
            "speedup": speedup,
            "efficiency": efficiency,
            "agent_count": multi_agent_metrics["agent_count"],
            "throughput_improvement": throughput_improvement,
            "expected_min_speedup": 2.0,  # Minimum 2x speedup expected
            "expected_max_speedup": 4.0   # Maximum theoretical speedup
        }
        
        print(f"\n=== SPEEDUP ANALYSIS ===")
        print(f"Single agent time: {single_agent_metrics['total_time']:.2f}s")
        print(f"Multi-agent time: {multi_agent_metrics['total_time']:.2f}s")
        print(f"Speedup: {speedup:.2f}x")
        print(f"Efficiency: {efficiency:.2f} ({efficiency:.2%})")
        print(f"Throughput improvement: {throughput_improvement:.2%}")
        
        # Performance assertions
        assert speedup >= speedup_metrics["expected_min_speedup"], \
            f"Insufficient speedup: {speedup:.2f}x < {speedup_metrics['expected_min_speedup']:.2f}x"
        
        assert speedup <= speedup_metrics["expected_max_speedup"], \
            f"Unrealistic speedup: {speedup:.2f}x > {speedup_metrics['expected_max_speedup']:.2f}x"
        
        assert efficiency >= 0.4, f"Poor parallel efficiency: {efficiency:.2f}"
        
        assert throughput_improvement >= 1.0, \
            f"Insufficient throughput improvement: {throughput_improvement:.2%}"
        
        self._store_benchmark_result("speedup_analysis", speedup_metrics)
        return speedup_metrics

    async def test_resource_utilization_analysis(self, benchmark_orchestrator):
        """Analyze resource utilization patterns in single vs multi-agent execution."""
        reference_tasks = self._create_reference_task_set()[:10]  # Smaller set for detailed analysis
        
        # Test single agent resource usage
        single_agent = await benchmark_orchestrator.create_agent(
            agent_type="resource_monitor_agent",
            capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.DATA_PROCESSING}
        )
        
        print(f"\n=== RESOURCE UTILIZATION ANALYSIS ===")
        
        # Single agent execution with monitoring
        single_agent_usage = await self._monitor_resource_usage(
            benchmark_orchestrator, reference_tasks, [single_agent]
        )
        
        # Reset and test multi-agent
        await self._reset_orchestrator_state(benchmark_orchestrator)
        
        multi_agents = []
        for i in range(3):
            agent = await benchmark_orchestrator.create_agent(
                agent_type=f"resource_multi_agent_{i}",
                capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.DATA_PROCESSING}
            )
            multi_agents.append(agent)
        
        multi_agent_usage = await self._monitor_resource_usage(
            benchmark_orchestrator, reference_tasks, multi_agents
        )
        
        # Compare resource usage
        usage_comparison = {
            "single_agent": single_agent_usage,
            "multi_agent": multi_agent_usage,
            "cpu_efficiency_improvement": (
                multi_agent_usage["avg_cpu_usage"] - single_agent_usage["avg_cpu_usage"]
            ) / single_agent_usage["avg_cpu_usage"],
            "memory_overhead": (
                multi_agent_usage["peak_memory_mb"] - single_agent_usage["peak_memory_mb"]
            ) / single_agent_usage["peak_memory_mb"],
            "resource_efficiency": multi_agent_usage["tasks_per_cpu_second"] / single_agent_usage["tasks_per_cpu_second"]
        }
        
        print(f"\nResource Usage Comparison:")
        print(f"Single Agent - CPU: {single_agent_usage['avg_cpu_usage']:.1f}%, Memory: {single_agent_usage['peak_memory_mb']:.1f}MB")
        print(f"Multi Agent - CPU: {multi_agent_usage['avg_cpu_usage']:.1f}%, Memory: {multi_agent_usage['peak_memory_mb']:.1f}MB")
        print(f"CPU Efficiency Improvement: {usage_comparison['cpu_efficiency_improvement']:.2%}")
        print(f"Memory Overhead: {usage_comparison['memory_overhead']:.2%}")
        print(f"Resource Efficiency: {usage_comparison['resource_efficiency']:.2f}x")
        
        # Resource usage assertions
        assert usage_comparison["cpu_efficiency_improvement"] >= 0.5, "Insufficient CPU utilization improvement"
        assert usage_comparison["memory_overhead"] <= 2.0, "Excessive memory overhead"
        assert usage_comparison["resource_efficiency"] >= 1.5, "Poor resource efficiency"
        
        self._store_benchmark_result("resource_utilization", usage_comparison)
        return usage_comparison

    async def test_scalability_benchmark(self, benchmark_orchestrator):
        """Test system scalability with increasing agent counts."""
        reference_tasks = self._create_reference_task_set()
        agent_counts = [1, 2, 4, 8, 16]
        scalability_results = {}
        
        print(f"\n=== SCALABILITY BENCHMARK ===")
        print(f"Testing with agent counts: {agent_counts}")
        
        for agent_count in agent_counts:
            print(f"\nTesting with {agent_count} agents...")
            
            # Create agents
            agents = []
            for i in range(agent_count):
                agent = await benchmark_orchestrator.create_agent(
                    agent_type=f"scale_agent_{i}",
                    capabilities={AgentCapability.TASK_EXECUTION, AgentCapability.DATA_PROCESSING}
                )
                agents.append(agent)
            
            # Execute tasks
            start_time = time.time()
            
            for task in reference_tasks:
                await benchmark_orchestrator.submit_task(task)
            
            # Wait for completion
            completed_tasks = []
            timeout = 180.0  # 3 minutes
            
            while len(completed_tasks) < len(reference_tasks) and \
                  (time.time() - start_time) < timeout:
                
                for task in reference_tasks:
                    if task.id not in [t.id for t in completed_tasks]:
                        updated_task = await benchmark_orchestrator.get_task(task.id)
                        if updated_task and updated_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                            completed_tasks.append(updated_task)
                
                await asyncio.sleep(0.1)
            
            total_time = time.time() - start_time
            successful_tasks = [t for t in completed_tasks if t.status == TaskStatus.COMPLETED]
            throughput = len(successful_tasks) / total_time
            
            scalability_results[agent_count] = {
                "agent_count": agent_count,
                "total_time": total_time,
                "successful_tasks": len(successful_tasks),
                "success_rate": len(successful_tasks) / len(reference_tasks),
                "throughput": throughput,
                "efficiency": throughput / agent_count if agent_count > 0 else 0
            }
            
            print(f"  Time: {total_time:.2f}s, Throughput: {throughput:.2f} tasks/sec, Efficiency: {scalability_results[agent_count]['efficiency']:.2f}")
            
            # Cleanup agents
            for agent in agents:
                await benchmark_orchestrator.terminate_agent(agent.id)
            
            await asyncio.sleep(1.0)
        
        # Analyze scalability
        baseline_throughput = scalability_results[1]["throughput"]
        scalability_analysis = {
            "results": scalability_results,
            "linear_scaling_baseline": baseline_throughput,
            "best_throughput": max(result["throughput"] for result in scalability_results.values()),
            "best_agent_count": max(scalability_results.keys(), key=lambda k: scalability_results[k]["throughput"]),
            "scaling_efficiency": {}
        }
        
        for count, result in scalability_results.items():
            expected_throughput = baseline_throughput * count
            actual_throughput = result["throughput"]
            scaling_efficiency = actual_throughput / expected_throughput
            scalability_analysis["scaling_efficiency"][count] = scaling_efficiency
        
        print(f"\nScalability Analysis:")
        print(f"Baseline (1 agent): {baseline_throughput:.2f} tasks/sec")
        print(f"Best performance: {scalability_analysis['best_throughput']:.2f} tasks/sec with {scalability_analysis['best_agent_count']} agents")
        
        for count in agent_counts:
            efficiency = scalability_analysis["scaling_efficiency"][count]
            print(f"{count} agents: {efficiency:.2%} scaling efficiency")
        
        # Scalability assertions
        assert scalability_analysis["scaling_efficiency"][2] >= 0.8, "Poor 2-agent scaling"
        assert scalability_analysis["scaling_efficiency"][4] >= 0.6, "Poor 4-agent scaling"
        assert max(scalability_analysis["scaling_efficiency"].values()) >= 0.8, "No good scaling point found"
        
        self._store_benchmark_result("scalability_analysis", scalability_analysis)
        return scalability_analysis

    # Helper methods
    
    def _create_reference_task_set(self) -> List[Task]:
        """Create standardized reference task set for benchmarking."""
        tasks = []
        
        # Data processing tasks
        for i in range(8):
            task = TestDataFactory.create_task(
                name=f"DataProcess_{i:02d}",
                parameters={
                    "operation": "data_transformation",
                    "dataset_size": 1000,
                    "complexity": "medium"
                },
                timeout_seconds=30
            )
            tasks.append(task)
        
        # Computation tasks
        for i in range(6):
            task = TestDataFactory.create_task(
                name=f"Compute_{i:02d}",
                parameters={
                    "operation": "mathematical_computation",
                    "iterations": 5000,
                    "complexity": "high"
                },
                timeout_seconds=45
            )
            tasks.append(task)
        
        # I/O tasks
        for i in range(4):
            task = TestDataFactory.create_task(
                name=f"IO_{i:02d}",
                parameters={
                    "operation": "file_processing",
                    "file_count": 100,
                    "complexity": "low"
                },
                timeout_seconds=20
            )
            tasks.append(task)
        
        # Mixed workload tasks
        for i in range(2):
            task = TestDataFactory.create_task(
                name=f"Mixed_{i:02d}",
                parameters={
                    "operation": "mixed_workload",
                    "cpu_intensive": True,
                    "io_intensive": True,
                    "complexity": "high"
                },
                timeout_seconds=60
            )
            tasks.append(task)
        
        return tasks

    async def _monitor_resource_usage(self, orchestrator, tasks: List[Task], agents: List) -> Dict[str, Any]:
        """Monitor resource usage during task execution."""
        import psutil
        
        # Initialize monitoring
        cpu_samples = []
        memory_samples = []
        
        start_time = time.time()
        
        # Submit tasks
        for task in tasks:
            await orchestrator.submit_task(task)
        
        # Monitor during execution
        completed_tasks = []
        while len(completed_tasks) < len(tasks) and (time.time() - start_time) < 120.0:
            # Collect resource samples
            cpu_percent = psutil.cpu_percent()
            memory_mb = psutil.virtual_memory().used / 1024 / 1024
            
            cpu_samples.append(cpu_percent)
            memory_samples.append(memory_mb)
            
            # Check task completion
            for task in tasks:
                if task.id not in [t.id for t in completed_tasks]:
                    updated_task = await orchestrator.get_task(task.id)
                    if updated_task and updated_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        completed_tasks.append(updated_task)
            
            await asyncio.sleep(0.5)
        
        execution_time = time.time() - start_time
        successful_tasks = [t for t in completed_tasks if t.status == TaskStatus.COMPLETED]
        
        return {
            "execution_time": execution_time,
            "successful_tasks": len(successful_tasks),
            "avg_cpu_usage": mean(cpu_samples) if cpu_samples else 0,
            "peak_cpu_usage": max(cpu_samples) if cpu_samples else 0,
            "avg_memory_mb": mean(memory_samples) if memory_samples else 0,
            "peak_memory_mb": max(memory_samples) if memory_samples else 0,
            "tasks_per_second": len(successful_tasks) / execution_time,
            "tasks_per_cpu_second": len(successful_tasks) / (execution_time * mean(cpu_samples) / 100) if cpu_samples else 0,
            "agent_count": len(agents)
        }

    async def _reset_orchestrator_state(self, orchestrator):
        """Reset orchestrator state between benchmarks."""
        # Terminate all agents
        system_metrics = await orchestrator.get_system_metrics()
        agent_metrics = system_metrics.get("agent_manager", {})
        
        # Allow brief pause for cleanup
        await asyncio.sleep(2.0)

    def _store_benchmark_result(self, benchmark_name: str, metrics: Dict[str, Any]):
        """Store benchmark results for analysis and reporting."""
        # In a real implementation, this would store to a database or file
        timestamp = datetime.utcnow().isoformat()
        result = {
            "benchmark": benchmark_name,
            "timestamp": timestamp,
            "metrics": metrics
        }
        
        # Store in test artifacts
        print(f"\nStoring benchmark result: {benchmark_name}")
        # Could write to JSON file, database, or metrics system