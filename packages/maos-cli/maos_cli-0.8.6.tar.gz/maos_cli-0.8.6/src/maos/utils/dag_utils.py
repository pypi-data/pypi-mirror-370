"""
Directed Acyclic Graph (DAG) utilities for task orchestration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any, Iterator
from uuid import UUID
from collections import defaultdict, deque

from .exceptions import DAGError, CircularDependencyError


@dataclass
class TaskNode:
    """Represents a task node in the DAG."""
    
    task_id: UUID
    dependencies: Set[UUID] = field(default_factory=set)
    dependents: Set[UUID] = field(default_factory=set)
    priority: int = 0
    estimated_duration: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_dependency(self, dependency_id: UUID) -> None:
        """Add a dependency to this node."""
        self.dependencies.add(dependency_id)
    
    def remove_dependency(self, dependency_id: UUID) -> None:
        """Remove a dependency from this node."""
        self.dependencies.discard(dependency_id)
    
    def add_dependent(self, dependent_id: UUID) -> None:
        """Add a dependent to this node."""
        self.dependents.add(dependent_id)
    
    def remove_dependent(self, dependent_id: UUID) -> None:
        """Remove a dependent from this node."""
        self.dependents.discard(dependent_id)
    
    def is_ready(self, completed_tasks: Set[UUID]) -> bool:
        """Check if this task is ready to execute (all dependencies completed)."""
        return self.dependencies.issubset(completed_tasks)
    
    def has_dependencies(self) -> bool:
        """Check if this task has any dependencies."""
        return len(self.dependencies) > 0
    
    def has_dependents(self) -> bool:
        """Check if this task has any dependents."""
        return len(self.dependents) > 0


class DAGBuilder:
    """Builder class for constructing task DAGs."""
    
    def __init__(self):
        self.nodes: Dict[UUID, TaskNode] = {}
        self._validated = False
    
    def add_task(
        self, 
        task_id: UUID, 
        dependencies: Optional[Set[UUID]] = None,
        priority: int = 0,
        estimated_duration: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'DAGBuilder':
        """Add a task to the DAG."""
        
        if task_id in self.nodes:
            raise DAGError(f"Task {task_id} already exists in DAG")
        
        node = TaskNode(
            task_id=task_id,
            dependencies=dependencies or set(),
            priority=priority,
            estimated_duration=estimated_duration,
            metadata=metadata or {}
        )
        
        self.nodes[task_id] = node
        
        # Update dependent relationships
        for dep_id in node.dependencies:
            if dep_id in self.nodes:
                self.nodes[dep_id].add_dependent(task_id)
        
        self._validated = False
        return self
    
    def add_dependency(self, task_id: UUID, dependency_id: UUID) -> 'DAGBuilder':
        """Add a dependency relationship between tasks."""
        
        if task_id not in self.nodes:
            raise DAGError(f"Task {task_id} not found in DAG")
        if dependency_id not in self.nodes:
            raise DAGError(f"Dependency task {dependency_id} not found in DAG")
        if task_id == dependency_id:
            raise DAGError("Task cannot depend on itself")
        
        self.nodes[task_id].add_dependency(dependency_id)
        self.nodes[dependency_id].add_dependent(task_id)
        
        self._validated = False
        return self
    
    def remove_dependency(self, task_id: UUID, dependency_id: UUID) -> 'DAGBuilder':
        """Remove a dependency relationship between tasks."""
        
        if task_id in self.nodes and dependency_id in self.nodes:
            self.nodes[task_id].remove_dependency(dependency_id)
            self.nodes[dependency_id].remove_dependent(task_id)
            self._validated = False
        
        return self
    
    def remove_task(self, task_id: UUID) -> 'DAGBuilder':
        """Remove a task from the DAG."""
        
        if task_id not in self.nodes:
            return self
        
        node = self.nodes[task_id]
        
        # Remove all dependency relationships
        for dep_id in node.dependencies:
            if dep_id in self.nodes:
                self.nodes[dep_id].remove_dependent(task_id)
        
        for dependent_id in node.dependents:
            if dependent_id in self.nodes:
                self.nodes[dependent_id].remove_dependency(task_id)
        
        del self.nodes[task_id]
        self._validated = False
        return self
    
    def build(self) -> Dict[UUID, TaskNode]:
        """Build and validate the DAG."""
        self.validate()
        return self.nodes.copy()
    
    def validate(self) -> None:
        """Validate the DAG structure."""
        if self._validated:
            return
        
        # Check for circular dependencies
        self._check_circular_dependencies()
        
        # Validate all dependencies exist
        for task_id, node in self.nodes.items():
            for dep_id in node.dependencies:
                if dep_id not in self.nodes:
                    raise DAGError(f"Task {task_id} depends on non-existent task {dep_id}")
        
        self._validated = True
    
    def _check_circular_dependencies(self) -> None:
        """Check for circular dependencies using DFS."""
        
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {task_id: WHITE for task_id in self.nodes}
        
        def dfs(task_id: UUID, path: List[UUID]) -> None:
            if colors[task_id] == GRAY:
                # Found a cycle
                cycle_start = path.index(task_id)
                cycle = path[cycle_start:] + [task_id]
                raise CircularDependencyError(cycle)
            
            if colors[task_id] == BLACK:
                return
            
            colors[task_id] = GRAY
            path.append(task_id)
            
            for dep_id in self.nodes[task_id].dependencies:
                if dep_id in self.nodes:
                    dfs(dep_id, path)
            
            path.pop()
            colors[task_id] = BLACK
        
        for task_id in self.nodes:
            if colors[task_id] == WHITE:
                dfs(task_id, [])


class DAGValidator:
    """Validator for DAG structures and properties."""
    
    @staticmethod
    def validate_dag(nodes: Dict[UUID, TaskNode]) -> List[str]:
        """Validate DAG and return list of issues found."""
        issues = []
        
        # Check for orphaned nodes (no dependencies and no dependents)
        orphaned = [
            task_id for task_id, node in nodes.items()
            if not node.has_dependencies() and not node.has_dependents()
        ]
        if orphaned:
            issues.append(f"Found {len(orphaned)} orphaned tasks: {orphaned}")
        
        # Check for missing dependencies
        for task_id, node in nodes.items():
            missing_deps = node.dependencies - set(nodes.keys())
            if missing_deps:
                issues.append(f"Task {task_id} has missing dependencies: {missing_deps}")
        
        # Check for inconsistent relationships
        for task_id, node in nodes.items():
            for dep_id in node.dependencies:
                if dep_id in nodes and task_id not in nodes[dep_id].dependents:
                    issues.append(f"Inconsistent dependency: {task_id} -> {dep_id}")
            
            for dependent_id in node.dependents:
                if dependent_id in nodes and task_id not in nodes[dependent_id].dependencies:
                    issues.append(f"Inconsistent dependent: {task_id} <- {dependent_id}")
        
        return issues
    
    @staticmethod
    def get_ready_tasks(nodes: Dict[UUID, TaskNode], completed_tasks: Set[UUID]) -> List[UUID]:
        """Get list of tasks that are ready to execute."""
        ready_tasks = []
        
        for task_id, node in nodes.items():
            if task_id not in completed_tasks and node.is_ready(completed_tasks):
                ready_tasks.append(task_id)
        
        # Sort by priority (higher priority first)
        ready_tasks.sort(key=lambda tid: nodes[tid].priority, reverse=True)
        
        return ready_tasks
    
    @staticmethod
    def topological_sort(nodes: Dict[UUID, TaskNode]) -> List[UUID]:
        """Perform topological sort on the DAG using Kahn's algorithm."""
        
        # Calculate in-degrees
        in_degrees = {task_id: len(node.dependencies) for task_id, node in nodes.items()}
        
        # Initialize queue with nodes that have no dependencies
        queue = deque([task_id for task_id, degree in in_degrees.items() if degree == 0])
        result = []
        
        while queue:
            # Process nodes with same in-degree by priority
            current_batch = []
            for _ in range(len(queue)):
                current_batch.append(queue.popleft())
            
            # Sort by priority (higher priority first)
            current_batch.sort(key=lambda tid: nodes[tid].priority, reverse=True)
            
            for task_id in current_batch:
                result.append(task_id)
                
                # Decrease in-degree of dependents
                for dependent_id in nodes[task_id].dependents:
                    in_degrees[dependent_id] -= 1
                    if in_degrees[dependent_id] == 0:
                        queue.append(dependent_id)
        
        if len(result) != len(nodes):
            raise CircularDependencyError([])
        
        return result
    
    @staticmethod
    def find_critical_path(nodes: Dict[UUID, TaskNode]) -> Tuple[List[UUID], int]:
        """Find the critical path (longest path) through the DAG."""
        
        # Topological sort to process nodes in dependency order
        sorted_tasks = DAGValidator.topological_sort(nodes)
        
        # Calculate earliest start times and longest paths
        earliest_start = {task_id: 0 for task_id in nodes}
        longest_path = {task_id: [] for task_id in nodes}
        
        for task_id in sorted_tasks:
            node = nodes[task_id]
            
            # Find the maximum earliest start time from dependencies
            max_finish_time = 0
            best_predecessor = None
            
            for dep_id in node.dependencies:
                finish_time = earliest_start[dep_id] + nodes[dep_id].estimated_duration
                if finish_time > max_finish_time:
                    max_finish_time = finish_time
                    best_predecessor = dep_id
            
            earliest_start[task_id] = max_finish_time
            
            # Build longest path
            if best_predecessor:
                longest_path[task_id] = longest_path[best_predecessor] + [best_predecessor]
        
        # Find the task with maximum finish time
        max_finish_time = 0
        critical_end_task = None
        
        for task_id, node in nodes.items():
            finish_time = earliest_start[task_id] + node.estimated_duration
            if finish_time > max_finish_time:
                max_finish_time = finish_time
                critical_end_task = task_id
        
        if critical_end_task:
            critical_path = longest_path[critical_end_task] + [critical_end_task]
            return critical_path, max_finish_time
        
        return [], 0
    
    @staticmethod
    def calculate_slack(nodes: Dict[UUID, TaskNode]) -> Dict[UUID, int]:
        """Calculate slack time for each task."""
        
        # Get critical path
        critical_path, total_duration = DAGValidator.find_critical_path(nodes)
        
        # Calculate latest start times (backward pass)
        latest_start = {task_id: total_duration for task_id in nodes}
        
        # Reverse topological order
        sorted_tasks = list(reversed(DAGValidator.topological_sort(nodes)))
        
        for task_id in sorted_tasks:
            node = nodes[task_id]
            
            # For leaf nodes (no dependents), latest start = total_duration - duration
            if not node.dependents:
                latest_start[task_id] = total_duration - node.estimated_duration
            else:
                # Find minimum latest start time from dependents
                min_dependent_start = float('inf')
                for dependent_id in node.dependents:
                    min_dependent_start = min(min_dependent_start, latest_start[dependent_id])
                latest_start[task_id] = min_dependent_start - node.estimated_duration
        
        # Calculate earliest start times (forward pass)
        earliest_start = {task_id: 0 for task_id in nodes}
        sorted_tasks = DAGValidator.topological_sort(nodes)
        
        for task_id in sorted_tasks:
            node = nodes[task_id]
            
            max_finish_time = 0
            for dep_id in node.dependencies:
                finish_time = earliest_start[dep_id] + nodes[dep_id].estimated_duration
                max_finish_time = max(max_finish_time, finish_time)
            
            earliest_start[task_id] = max_finish_time
        
        # Calculate slack = latest_start - earliest_start
        slack = {}
        for task_id in nodes:
            slack[task_id] = max(0, latest_start[task_id] - earliest_start[task_id])
        
        return slack
    
    @staticmethod
    def get_parallel_groups(nodes: Dict[UUID, TaskNode]) -> List[List[UUID]]:
        """Get groups of tasks that can be executed in parallel."""
        
        completed_tasks = set()
        parallel_groups = []
        
        while len(completed_tasks) < len(nodes):
            ready_tasks = DAGValidator.get_ready_tasks(nodes, completed_tasks)
            
            if not ready_tasks:
                # This should not happen in a valid DAG
                remaining_tasks = set(nodes.keys()) - completed_tasks
                raise DAGError(f"Cannot find ready tasks. Remaining: {remaining_tasks}")
            
            parallel_groups.append(ready_tasks)
            completed_tasks.update(ready_tasks)
        
        return parallel_groups