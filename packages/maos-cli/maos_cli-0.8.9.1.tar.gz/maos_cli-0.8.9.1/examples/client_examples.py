#!/usr/bin/env python3
"""
MAOS Backend API Client Examples

This module provides examples of how to interact with the MAOS backend API
from client applications, including various task orchestration patterns,
agent management, and monitoring capabilities.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from uuid import UUID

import aiohttp
import httpx


@dataclass
class MAOSClient:
    """Async client for MAOS Backend API."""
    
    base_url: str = "http://localhost:8000"
    api_prefix: str = "/api/v1"
    timeout: int = 30
    
    def __post_init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _url(self, endpoint: str) -> str:
        """Construct full URL for endpoint."""
        return f"{self.base_url}{self.api_prefix}{endpoint}"
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request."""
        if not self.session:
            raise RuntimeError("Client not initialized - use async context manager")
        
        url = self._url(endpoint)
        
        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    # Task management methods
    async def submit_task(
        self,
        name: str,
        description: Optional[str] = None,
        priority: str = "medium",
        parameters: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 300,
        max_retries: int = 3,
        resource_requirements: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        decomposition_strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit a new task."""
        
        payload = {
            "name": name,
            "description": description,
            "priority": priority,
            "parameters": parameters or {},
            "timeout_seconds": timeout_seconds,
            "max_retries": max_retries,
            "resource_requirements": resource_requirements or {},
            "tags": set(tags or []),
            "metadata": metadata or {},
            "decomposition_strategy": decomposition_strategy
        }
        
        return await self._request("POST", "/tasks", json=payload)
    
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task by ID."""
        return await self._request("GET", f"/tasks/{task_id}")
    
    async def cancel_task(self, task_id: str, reason: str = "Cancelled by client") -> Dict[str, Any]:
        """Cancel a task."""
        return await self._request("DELETE", f"/tasks/{task_id}", params={"reason": reason})
    
    async def create_agent(
        self,
        agent_type: str,
        capabilities: List[str],
        configuration: Optional[Dict[str, Any]] = None,
        max_concurrent_tasks: int = 1,
        resource_limits: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new agent."""
        
        payload = {
            "agent_type": agent_type,
            "capabilities": set(capabilities),
            "configuration": configuration or {},
            "max_concurrent_tasks": max_concurrent_tasks,
            "resource_limits": resource_limits or {},
            "tags": set(tags or [])
        }
        
        return await self._request("POST", "/agents", json=payload)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        return await self._request("GET", "/system/status")
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        return await self._request("GET", "/system/metrics")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform basic health check."""
        url = f"{self.base_url}/health"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    
    async def detailed_health_check(self) -> Dict[str, Any]:
        """Perform detailed health check."""
        url = f"{self.base_url}/health/detailed"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    
    # Claude Code integration methods
    async def submit_claude_task(
        self,
        task_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit a Claude Code task."""
        return await self._request("POST", "/claude/tasks", json=task_spec)
    
    async def get_claude_task_status(self, claude_task_id: str) -> Dict[str, Any]:
        """Get Claude task status."""
        return await self._request("GET", f"/claude/tasks/{claude_task_id}")
    
    async def get_claude_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status for Claude Code."""
        return await self._request("GET", "/claude/orchestrator/status")


class TaskOrchestrationPatterns:
    """Examples of common task orchestration patterns."""
    
    def __init__(self, client: MAOSClient):
        self.client = client
    
    async def simple_task_execution(self) -> str:
        """Example: Simple single task execution."""
        print("\n=== Simple Task Execution ===")
        
        # Submit a simple data processing task
        response = await self.client.submit_task(
            name="Data Analysis Task",
            description="Analyze customer data and generate report",
            priority="high",
            parameters={
                "dataset": "customer_data_2024",
                "analysis_type": "behavioral_patterns",
                "output_format": "json"
            },
            resource_requirements={
                "cpu_cores": 2.0,
                "memory_mb": 4096
            },
            tags=["data_analysis", "customer_data"],
            timeout_seconds=600
        )
        
        task_id = response["task"]["id"]
        print(f"Task submitted: {task_id}")
        
        # Monitor task progress
        while True:
            task_status = await self.client.get_task(task_id)
            status = task_status["task"]["status"]
            
            print(f"Task status: {status}")
            
            if status in ["completed", "failed", "cancelled"]:
                break
            
            await asyncio.sleep(2)
        
        return task_id
    
    async def parallel_task_workflow(self) -> List[str]:
        """Example: Parallel task execution workflow."""
        print("\n=== Parallel Task Workflow ===")
        
        # Submit multiple parallel tasks
        tasks = [
            {
                "name": "Data Extraction Task 1",
                "description": "Extract data from database partition 1",
                "parameters": {"partition": 1, "table": "users"},
                "decomposition_strategy": "parallel"
            },
            {
                "name": "Data Extraction Task 2", 
                "description": "Extract data from database partition 2",
                "parameters": {"partition": 2, "table": "users"},
                "decomposition_strategy": "parallel"
            },
            {
                "name": "Data Extraction Task 3",
                "description": "Extract data from database partition 3",
                "parameters": {"partition": 3, "table": "users"},
                "decomposition_strategy": "parallel"
            }
        ]
        
        task_ids = []
        for task in tasks:
            response = await self.client.submit_task(**task)
            task_ids.append(response["task"]["id"])
            print(f"Submitted parallel task: {response['task']['id']}")
        
        # Wait for all tasks to complete
        completed_tasks = 0
        while completed_tasks < len(task_ids):
            completed_tasks = 0
            for task_id in task_ids:
                task_status = await self.client.get_task(task_id)
                status = task_status["task"]["status"]
                
                if status in ["completed", "failed", "cancelled"]:
                    completed_tasks += 1
            
            print(f"Completed tasks: {completed_tasks}/{len(task_ids)}")
            
            if completed_tasks < len(task_ids):
                await asyncio.sleep(3)
        
        print("All parallel tasks completed")
        return task_ids
    
    async def hierarchical_task_decomposition(self) -> str:
        """Example: Hierarchical task decomposition."""
        print("\n=== Hierarchical Task Decomposition ===")
        
        # Submit a complex task that will be decomposed hierarchically
        response = await self.client.submit_task(
            name="Machine Learning Pipeline",
            description="Complete ML pipeline: data preprocessing, training, validation, deployment",
            priority="high",
            parameters={
                "model_type": "random_forest",
                "dataset": "customer_churn",
                "features": ["age", "tenure", "monthly_charges", "total_charges"],
                "validation_split": 0.2,
                "deploy_model": True
            },
            resource_requirements={
                "cpu_cores": 4.0,
                "memory_mb": 8192,
                "gpu_memory_mb": 2048
            },
            decomposition_strategy="hierarchical",
            timeout_seconds=1800,
            tags=["ml", "pipeline", "production"]
        )
        
        task_id = response["task"]["id"]
        execution_plan_id = response["execution_plan_id"]
        
        print(f"ML Pipeline task submitted: {task_id}")
        print(f"Execution plan ID: {execution_plan_id}")
        
        # Monitor the hierarchical execution
        previous_status = None
        while True:
            task_status = await self.client.get_task(task_id)
            status = task_status["task"]["status"]
            
            if status != previous_status:
                print(f"Pipeline status: {status}")
                if task_status["task"]["subtasks"]:
                    print(f"Subtasks: {len(task_status['task']['subtasks'])}")
                previous_status = status
            
            if status in ["completed", "failed", "cancelled"]:
                break
            
            await asyncio.sleep(5)
        
        return task_id
    
    async def resource_intensive_workflow(self) -> str:
        """Example: Resource-intensive workflow with custom resource requirements."""
        print("\n=== Resource-Intensive Workflow ===")
        
        # Submit a resource-intensive computational task
        response = await self.client.submit_task(
            name="Large-Scale Data Processing",
            description="Process 100GB dataset with complex transformations",
            priority="critical",
            parameters={
                "input_path": "/data/large_dataset.parquet",
                "output_path": "/results/processed_data",
                "operations": [
                    "deduplication",
                    "normalization", 
                    "feature_engineering",
                    "aggregation"
                ],
                "chunk_size": "1GB",
                "parallel_workers": 8
            },
            resource_requirements={
                "cpu_cores": 16.0,
                "memory_mb": 32768,
                "disk_mb": 102400,
                "network_mbps": 1000.0
            },
            decomposition_strategy="pipeline",
            timeout_seconds=3600,
            max_retries=2,
            tags=["big_data", "etl", "critical"]
        )
        
        task_id = response["task"]["id"]
        print(f"Resource-intensive task submitted: {task_id}")
        
        # Monitor with progress updates
        start_time = datetime.utcnow()
        while True:
            task_status = await self.client.get_task(task_id)
            status = task_status["task"]["status"]
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            print(f"[{elapsed:.1f}s] Task status: {status}")
            
            if status in ["completed", "failed", "cancelled"]:
                if status == "completed":
                    print(f"Task completed successfully after {elapsed:.1f}s")
                else:
                    print(f"Task {status} after {elapsed:.1f}s")
                    if task_status["task"]["error"]:
                        print(f"Error: {task_status['task']['error']}")
                break
            
            await asyncio.sleep(10)
        
        return task_id


class AgentManagementExamples:
    """Examples of agent management and coordination."""
    
    def __init__(self, client: MAOSClient):
        self.client = client
    
    async def create_specialized_agents(self) -> List[str]:
        """Example: Create specialized agents for different task types."""
        print("\n=== Creating Specialized Agents ===")
        
        agent_specs = [
            {
                "agent_type": "data_scientist_agent",
                "capabilities": ["data_processing", "computation"],
                "configuration": {
                    "python_version": "3.9",
                    "ml_libraries": ["sklearn", "pandas", "numpy"],
                    "specialization": "statistical_analysis"
                },
                "max_concurrent_tasks": 2,
                "resource_limits": {
                    "cpu_cores": 4.0,
                    "memory_mb": 8192
                }
            },
            {
                "agent_type": "api_integration_agent",
                "capabilities": ["api_integration", "communication"],
                "configuration": {
                    "supported_protocols": ["REST", "GraphQL", "gRPC"],
                    "auth_methods": ["OAuth2", "JWT", "API_KEY"],
                    "rate_limit_aware": True
                },
                "max_concurrent_tasks": 5
            },
            {
                "agent_type": "file_processor_agent",
                "capabilities": ["file_operations"],
                "configuration": {
                    "supported_formats": ["csv", "json", "parquet", "xlsx"],
                    "max_file_size_mb": 1024,
                    "streaming_capable": True
                },
                "max_concurrent_tasks": 3
            }
        ]
        
        agent_ids = []
        for spec in agent_specs:
            response = await self.client.create_agent(**spec)
            agent_id = response["agent"]["id"]
            agent_ids.append(agent_id)
            print(f"Created {spec['agent_type']}: {agent_id}")
        
        return agent_ids
    
    async def monitor_system_health(self) -> Dict[str, Any]:
        """Example: Monitor system health and performance."""
        print("\n=== System Health Monitoring ===")
        
        # Basic health check
        health = await self.client.health_check()
        print(f"Basic health: {health['status']}")
        
        # Detailed health check
        detailed_health = await self.client.detailed_health_check()
        print(f"Detailed health: {detailed_health['status']}")
        print(f"Uptime: {detailed_health['uptime_seconds']}s")
        print(f"Active executions: {detailed_health['active_executions']}")
        
        # Component health
        for component, status in detailed_health['components'].items():
            print(f"  {component}: {status['status']} (healthy: {status['healthy']})")
        
        # System status
        status = await self.client.get_system_status()
        print(f"\nSystem Status:")
        print(f"  Running: {status['running']}")
        print(f"  Total tasks: {status['total_tasks']}")
        print(f"  Total agents: {status['total_agents']}")
        print(f"  Total resources: {status['total_resources']}")
        
        # System metrics
        metrics = await self.client.get_system_metrics()
        print(f"\nSystem Metrics:")
        for component, component_metrics in metrics.items():
            if component == "timestamp":
                continue
            print(f"  {component}:")
            for metric, value in component_metrics.items():
                print(f"    {metric}: {value}")
        
        return detailed_health


class ClaudeIntegrationExamples:
    """Examples of Claude Code integration."""
    
    def __init__(self, client: MAOSClient):
        self.client = client
    
    async def claude_task_submission(self) -> str:
        """Example: Submit and monitor a Claude Code task."""
        print("\n=== Claude Code Task Integration ===")
        
        # Claude Code task specification
        claude_task_spec = {
            "name": "Code Generation Task",
            "description": "Generate Python code for data analysis",
            "type": "computation",
            "priority": "high",
            "parameters": {
                "language": "python",
                "task_type": "data_analysis",
                "requirements": [
                    "Load CSV data",
                    "Perform statistical analysis",
                    "Generate visualizations",
                    "Export results"
                ],
                "libraries": ["pandas", "matplotlib", "seaborn", "numpy"]
            },
            "resource_requirements": {
                "cpu_cores": 2.0,
                "memory_mb": 4096
            },
            "timeout_seconds": 600,
            "max_retries": 2,
            "tags": ["claude_code", "code_generation", "python"],
            "metadata": {
                "source": "claude_code_integration_example",
                "user_id": "example_user",
                "session_id": "session_123"
            },
            "decomposition_strategy": "hierarchical"
        }
        
        # Submit Claude task
        response = await self.client.submit_claude_task(claude_task_spec)
        claude_task_id = response["claude_task_id"]
        
        print(f"Claude task submitted: {claude_task_id}")
        print(f"Submitted at: {response['submitted_at']}")
        
        # Monitor Claude task progress
        while True:
            status = await self.client.get_claude_task_status(claude_task_id)
            
            print(f"Claude task status: {status['status']}")
            print(f"Updated at: {status['updated_at']}")
            
            if status['agent_id']:
                print(f"Assigned to agent: {status['agent_id']}")
            
            if status['status'] in ["completed", "failed", "cancelled"]:
                if status['status'] == "completed":
                    print("Task completed successfully!")
                    if status['result']:
                        print(f"Result: {status['result']}")
                else:
                    print(f"Task {status['status']}")
                    if status['error']:
                        print(f"Error: {status['error']}")
                break
            
            await asyncio.sleep(3)
        
        return claude_task_id
    
    async def claude_orchestrator_status(self) -> Dict[str, Any]:
        """Example: Get orchestrator status from Claude perspective."""
        print("\n=== Claude Orchestrator Status ===")
        
        status = await self.client.get_claude_orchestrator_status()
        
        print(f"Orchestrator status: {status['status']}")
        print(f"Uptime: {status['uptime_seconds']}s")
        print(f"Active executions: {status['active_executions']}")
        print(f"Total Claude tasks: {status['total_claude_tasks']}")
        
        print("\nComponent Health:")
        for component, health in status['health'].items():
            print(f"  {component}: {'✓' if health['healthy'] else '✗'} ({health['status']})")
        
        print("\nMetrics:")
        for metric, value in status['metrics'].items():
            print(f"  {metric}: {value}")
        
        return status


async def run_comprehensive_example():
    """Run comprehensive example demonstrating all features."""
    print("MAOS Backend API - Comprehensive Example")
    print("="*50)
    
    async with MAOSClient() as client:
        # Initialize examples
        task_patterns = TaskOrchestrationPatterns(client)
        agent_mgmt = AgentManagementExamples(client)
        claude_examples = ClaudeIntegrationExamples(client)
        
        try:
            # 1. System health check
            await agent_mgmt.monitor_system_health()
            
            # 2. Create specialized agents
            await agent_mgmt.create_specialized_agents()
            
            # 3. Task orchestration patterns
            await task_patterns.simple_task_execution()
            await task_patterns.parallel_task_workflow()
            await task_patterns.hierarchical_task_decomposition()
            await task_patterns.resource_intensive_workflow()
            
            # 4. Claude Code integration
            await claude_examples.claude_task_submission()
            await claude_examples.claude_orchestrator_status()
            
            # 5. Final system status
            print("\n=== Final System Status ===")
            final_status = await client.get_system_status()
            print(f"Total tasks processed: {final_status['total_tasks']}")
            print(f"Total agents created: {final_status['total_agents']}")
            
        except Exception as e:
            print(f"Error during example execution: {e}")
            raise


async def run_specific_example(example_type: str):
    """Run a specific example type."""
    async with MAOSClient() as client:
        if example_type == "tasks":
            patterns = TaskOrchestrationPatterns(client)
            await patterns.simple_task_execution()
            await patterns.parallel_task_workflow()
            
        elif example_type == "agents":
            agent_mgmt = AgentManagementExamples(client)
            await agent_mgmt.create_specialized_agents()
            await agent_mgmt.monitor_system_health()
            
        elif example_type == "claude":
            claude_examples = ClaudeIntegrationExamples(client)
            await claude_examples.claude_task_submission()
            await claude_examples.claude_orchestrator_status()
            
        else:
            print(f"Unknown example type: {example_type}")
            print("Available types: tasks, agents, claude")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MAOS Client Examples")
    parser.add_argument(
        "--example", 
        choices=["all", "tasks", "agents", "claude"],
        default="all",
        help="Which example to run"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="MAOS API base URL"
    )
    args = parser.parse_args()
    
    # Update client configuration
    MAOSClient.base_url = args.base_url
    
    # Run examples
    if args.example == "all":
        asyncio.run(run_comprehensive_example())
    else:
        asyncio.run(run_specific_example(args.example))
