"""
Task Decomposer for MAOS orchestration system.

Breaks down user requests into parallel subtasks and suggests appropriate agents.
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from ..utils.logging_config import MAOSLogger
from ..interfaces.sqlite_persistence import SqlitePersistence


class TaskType(Enum):
    """Types of tasks that can be assigned to agents."""
    DESIGN = "design"
    IMPLEMENT = "implement"
    TEST = "test"
    REVIEW = "review"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    DEBUG = "debug"
    REFACTOR = "refactor"
    DEPLOY = "deploy"


@dataclass
class SubTask:
    """Represents a subtask that can be assigned to an agent."""
    id: str
    description: str
    task_type: TaskType
    required_capabilities: List[str]
    parent_task_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_complexity: int = 1  # 1-5 scale
    assigned_agent: Optional[str] = None
    
    def to_claude_prompt(self) -> str:
        """Convert subtask to a Claude prompt."""
        prompt = f"{self.description}\n\n"
        
        if self.task_type == TaskType.REVIEW:
            prompt += "Focus on: code quality, security issues, performance problems, best practices.\n"
        elif self.task_type == TaskType.TEST:
            prompt += "Write comprehensive tests including edge cases and error scenarios.\n"
        elif self.task_type == TaskType.SECURITY:
            prompt += "Check for: injection vulnerabilities, authentication issues, data exposure.\n"
        elif self.task_type == TaskType.PERFORMANCE:
            prompt += "Analyze: bottlenecks, memory usage, query optimization, caching opportunities.\n"
        
        return prompt


@dataclass
class TaskPlan:
    """Complete plan for executing a user request."""
    id: str
    original_request: str
    subtasks: List[SubTask]
    estimated_agents_needed: int
    parallel_execution_possible: bool
    
    def get_execution_order(self) -> List[List[SubTask]]:
        """Get subtasks grouped by execution order (parallel batches)."""
        # Group tasks that can run in parallel
        batches = []
        processed = set()
        
        while len(processed) < len(self.subtasks):
            batch = []
            for task in self.subtasks:
                if task.id in processed:
                    continue
                # Check if all dependencies are processed
                if all(dep in processed for dep in task.dependencies):
                    batch.append(task)
            
            if not batch:
                # Circular dependency or error
                remaining = [t for t in self.subtasks if t.id not in processed]
                batch = remaining[:1]  # Force progress
            
            batches.append(batch)
            for task in batch:
                processed.add(task.id)
        
        return batches


@dataclass
class AgentSuggestion:
    """Suggestion for which agent to use for a task."""
    agent_id: Optional[str]  # None if new agent needed
    agent_name: str
    agent_type: str
    is_new: bool
    session_id: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    assigned_task: Optional[SubTask] = None


@dataclass
class AgentProposal:
    """Complete proposal for agent allocation."""
    suggestions: List[AgentSuggestion]
    reused_agents: int
    new_agents: int
    total_cost_estimate: float = 0.0
    
    def get_summary(self) -> str:
        """Get human-readable summary of the proposal."""
        lines = []
        lines.append(f"Agent allocation proposal:")
        lines.append(f"  • Reusing {self.reused_agents} existing agents")
        lines.append(f"  • Creating {self.new_agents} new agents")
        lines.append("")
        
        for suggestion in self.suggestions:
            if suggestion.is_new:
                lines.append(f"  NEW: {suggestion.agent_name} ({suggestion.agent_type})")
            else:
                session_info = f" [session: {suggestion.session_id[:8]}]" if suggestion.session_id else ""
                lines.append(f"  REUSE: {suggestion.agent_name}{session_info}")
            
            if suggestion.assigned_task:
                lines.append(f"    → {suggestion.assigned_task.description}")
        
        return "\n".join(lines)


class TaskDecomposer:
    """Breaks down user requests into parallel subtasks and suggests agents."""
    
    # Patterns for identifying task types
    TASK_PATTERNS = {
        TaskType.IMPLEMENT: [
            r"implement\s+(.+)",
            r"build\s+(.+)",
            r"create\s+(.+)",
            r"develop\s+(.+)",
            r"code\s+(.+)",
            r"write\s+(.+)",
        ],
        TaskType.REVIEW: [
            r"review\s+(.+)",
            r"check\s+(.+)",
            r"audit\s+(.+)",
            r"inspect\s+(.+)",
        ],
        TaskType.TEST: [
            r"test\s+(.+)",
            r"verify\s+(.+)",
            r"validate\s+(.+)",
        ],
        TaskType.SECURITY: [
            r"secure\s+(.+)",
            r".*security\s+.*",
            r".*vulnerabilit.*",
        ],
        TaskType.PERFORMANCE: [
            r"optimize\s+(.+)",
            r".*performance.*",
            r"speed\s+up\s+(.+)",
        ],
        TaskType.DEBUG: [
            r"debug\s+(.+)",
            r"fix\s+(.+)",
            r"resolve\s+(.+)",
            r"troubleshoot\s+(.+)",
        ],
    }
    
    # Agent type capabilities
    AGENT_CAPABILITIES = {
        "architect": ["design", "planning", "architecture", "system-design"],
        "developer": ["implement", "code", "build", "refactor"],
        "tester": ["test", "verify", "validate", "qa"],
        "reviewer": ["review", "audit", "quality", "standards"],
        "security-auditor": ["security", "vulnerability", "penetration", "compliance"],
        "performance-optimizer": ["performance", "optimize", "profile", "benchmark"],
        "debugger": ["debug", "troubleshoot", "fix", "diagnose"],
        "documentation-writer": ["document", "explain", "tutorial", "guide"],
    }
    
    def __init__(self, db: SqlitePersistence):
        """
        Initialize task decomposer.
        
        Args:
            db: Database for checking existing agents
        """
        self.db = db
        self.logger = MAOSLogger("task_decomposer")
    
    async def decompose(self, user_request: str) -> TaskPlan:
        """
        Break down user request into parallel subtasks.
        
        Args:
            user_request: Natural language request from user
            
        Returns:
            TaskPlan with subtasks that can be executed in parallel
        """
        plan_id = str(uuid4())
        request_lower = user_request.lower()
        
        # Identify the main task type
        main_task_type = self._identify_task_type(request_lower)
        
        # Generate subtasks based on request
        subtasks = await self._generate_subtasks(user_request, main_task_type)
        
        # Determine if parallel execution is possible
        parallel_possible = self._can_parallelize(subtasks)
        
        # Estimate agents needed
        agents_needed = len(set(task.task_type for task in subtasks))
        
        return TaskPlan(
            id=plan_id,
            original_request=user_request,
            subtasks=subtasks,
            estimated_agents_needed=agents_needed,
            parallel_execution_possible=parallel_possible
        )
    
    def _identify_task_type(self, request: str) -> TaskType:
        """Identify the primary task type from the request."""
        for task_type, patterns in self.TASK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, request):
                    return task_type
        
        # Default to implementation if no specific pattern matches
        return TaskType.IMPLEMENT
    
    async def _generate_subtasks(self, request: str, main_type: TaskType) -> List[SubTask]:
        """Generate subtasks based on the request."""
        subtasks = []
        request_lower = request.lower()
        
        # Check for specific keywords that indicate comprehensive work
        comprehensive = any(word in request_lower for word in 
                          ["everything", "complete", "full", "entire", "all"])
        
        # PRD/Requirements implementation
        if "prd" in request_lower or "requirement" in request_lower:
            subtasks.extend(self._generate_prd_subtasks(request))
        
        # Code review request
        elif "review" in request_lower or "audit" in request_lower:
            subtasks.extend(self._generate_review_subtasks(request))
        
        # Testing request
        elif "test" in request_lower:
            subtasks.extend(self._generate_test_subtasks(request))
        
        # Security analysis
        elif "security" in request_lower or "vulnerabilit" in request_lower:
            subtasks.extend(self._generate_security_subtasks(request))
        
        # Performance optimization
        elif "performance" in request_lower or "optimize" in request_lower:
            subtasks.extend(self._generate_performance_subtasks(request))
        
        # General implementation
        elif main_type == TaskType.IMPLEMENT:
            subtasks.extend(self._generate_implementation_subtasks(request, comprehensive))
        
        # Debugging
        elif main_type == TaskType.DEBUG:
            subtasks.extend(self._generate_debug_subtasks(request))
        
        # Default: Create a single task
        if not subtasks:
            subtasks.append(SubTask(
                id=str(uuid4()),
                description=request,
                task_type=main_type,
                required_capabilities=self._get_required_capabilities(main_type)
            ))
        
        return subtasks
    
    def _generate_prd_subtasks(self, request: str) -> List[SubTask]:
        """Generate subtasks for PRD implementation."""
        subtasks = []
        base_id = str(uuid4())
        
        # Architecture design
        design_task = SubTask(
            id=f"{base_id}_design",
            description="Design system architecture based on PRD requirements",
            task_type=TaskType.DESIGN,
            required_capabilities=["design", "architecture", "planning"]
        )
        subtasks.append(design_task)
        
        # Backend implementation
        backend_task = SubTask(
            id=f"{base_id}_backend",
            description="Implement backend services and APIs according to PRD",
            task_type=TaskType.IMPLEMENT,
            required_capabilities=["implement", "backend", "api"],
            dependencies=[design_task.id]
        )
        subtasks.append(backend_task)
        
        # Frontend implementation
        frontend_task = SubTask(
            id=f"{base_id}_frontend",
            description="Implement frontend components and UI according to PRD",
            task_type=TaskType.IMPLEMENT,
            required_capabilities=["implement", "frontend", "ui"],
            dependencies=[design_task.id]
        )
        subtasks.append(frontend_task)
        
        # Testing
        test_task = SubTask(
            id=f"{base_id}_test",
            description="Write comprehensive tests for all PRD features",
            task_type=TaskType.TEST,
            required_capabilities=["test", "verify"],
            dependencies=[backend_task.id, frontend_task.id]
        )
        subtasks.append(test_task)
        
        # Security review
        security_task = SubTask(
            id=f"{base_id}_security",
            description="Review implementation for security vulnerabilities",
            task_type=TaskType.SECURITY,
            required_capabilities=["security", "audit"],
            dependencies=[backend_task.id, frontend_task.id]
        )
        subtasks.append(security_task)
        
        return subtasks
    
    def _generate_review_subtasks(self, request: str) -> List[SubTask]:
        """Generate subtasks for code review."""
        subtasks = []
        base_id = str(uuid4())
        
        # Code quality review
        subtasks.append(SubTask(
            id=f"{base_id}_quality",
            description="Review code for quality, readability, and best practices",
            task_type=TaskType.REVIEW,
            required_capabilities=["review", "quality"]
        ))
        
        # Security review
        subtasks.append(SubTask(
            id=f"{base_id}_security",
            description="Review code for security vulnerabilities and issues",
            task_type=TaskType.SECURITY,
            required_capabilities=["security", "vulnerability"]
        ))
        
        # Performance review
        subtasks.append(SubTask(
            id=f"{base_id}_performance",
            description="Review code for performance issues and optimization opportunities",
            task_type=TaskType.PERFORMANCE,
            required_capabilities=["performance", "optimize"]
        ))
        
        return subtasks
    
    def _generate_test_subtasks(self, request: str) -> List[SubTask]:
        """Generate subtasks for testing."""
        subtasks = []
        base_id = str(uuid4())
        
        # Unit tests
        subtasks.append(SubTask(
            id=f"{base_id}_unit",
            description="Write unit tests for individual components",
            task_type=TaskType.TEST,
            required_capabilities=["test", "unit-test"]
        ))
        
        # Integration tests
        subtasks.append(SubTask(
            id=f"{base_id}_integration",
            description="Write integration tests for component interactions",
            task_type=TaskType.TEST,
            required_capabilities=["test", "integration-test"]
        ))
        
        # End-to-end tests
        if "e2e" in request.lower() or "end" in request.lower():
            subtasks.append(SubTask(
                id=f"{base_id}_e2e",
                description="Write end-to-end tests for complete workflows",
                task_type=TaskType.TEST,
                required_capabilities=["test", "e2e-test"]
            ))
        
        return subtasks
    
    def _generate_security_subtasks(self, request: str) -> List[SubTask]:
        """Generate subtasks for security analysis."""
        subtasks = []
        base_id = str(uuid4())
        
        # Vulnerability scan
        subtasks.append(SubTask(
            id=f"{base_id}_scan",
            description="Scan codebase for known vulnerabilities",
            task_type=TaskType.SECURITY,
            required_capabilities=["security", "scan"]
        ))
        
        # Authentication review
        subtasks.append(SubTask(
            id=f"{base_id}_auth",
            description="Review authentication and authorization implementation",
            task_type=TaskType.SECURITY,
            required_capabilities=["security", "authentication"]
        ))
        
        # Data security
        subtasks.append(SubTask(
            id=f"{base_id}_data",
            description="Review data handling and encryption practices",
            task_type=TaskType.SECURITY,
            required_capabilities=["security", "encryption"]
        ))
        
        return subtasks
    
    def _generate_performance_subtasks(self, request: str) -> List[SubTask]:
        """Generate subtasks for performance optimization."""
        subtasks = []
        base_id = str(uuid4())
        
        # Performance profiling
        subtasks.append(SubTask(
            id=f"{base_id}_profile",
            description="Profile application to identify performance bottlenecks",
            task_type=TaskType.PERFORMANCE,
            required_capabilities=["performance", "profile"]
        ))
        
        # Query optimization
        subtasks.append(SubTask(
            id=f"{base_id}_queries",
            description="Optimize database queries and data access patterns",
            task_type=TaskType.PERFORMANCE,
            required_capabilities=["performance", "database"]
        ))
        
        # Caching implementation
        subtasks.append(SubTask(
            id=f"{base_id}_cache",
            description="Implement caching strategies for improved performance",
            task_type=TaskType.PERFORMANCE,
            required_capabilities=["performance", "cache"]
        ))
        
        return subtasks
    
    def _generate_implementation_subtasks(self, request: str, comprehensive: bool) -> List[SubTask]:
        """Generate subtasks for general implementation."""
        subtasks = []
        base_id = str(uuid4())
        
        # Main implementation
        impl_task = SubTask(
            id=f"{base_id}_impl",
            description=f"Implement {request}",
            task_type=TaskType.IMPLEMENT,
            required_capabilities=["implement", "code"]
        )
        subtasks.append(impl_task)
        
        if comprehensive:
            # Add testing
            subtasks.append(SubTask(
                id=f"{base_id}_test",
                description=f"Write tests for {request}",
                task_type=TaskType.TEST,
                required_capabilities=["test"],
                dependencies=[impl_task.id]
            ))
            
            # Add review
            subtasks.append(SubTask(
                id=f"{base_id}_review",
                description=f"Review implementation of {request}",
                task_type=TaskType.REVIEW,
                required_capabilities=["review"],
                dependencies=[impl_task.id]
            ))
        
        return subtasks
    
    def _generate_debug_subtasks(self, request: str) -> List[SubTask]:
        """Generate subtasks for debugging."""
        subtasks = []
        base_id = str(uuid4())
        
        # Diagnose issue
        diagnose_task = SubTask(
            id=f"{base_id}_diagnose",
            description="Diagnose and identify root cause of the issue",
            task_type=TaskType.DEBUG,
            required_capabilities=["debug", "diagnose"]
        )
        subtasks.append(diagnose_task)
        
        # Fix issue
        fix_task = SubTask(
            id=f"{base_id}_fix",
            description="Implement fix for the identified issue",
            task_type=TaskType.DEBUG,
            required_capabilities=["debug", "fix"],
            dependencies=[diagnose_task.id]
        )
        subtasks.append(fix_task)
        
        # Verify fix
        verify_task = SubTask(
            id=f"{base_id}_verify",
            description="Verify that the fix resolves the issue",
            task_type=TaskType.TEST,
            required_capabilities=["test", "verify"],
            dependencies=[fix_task.id]
        )
        subtasks.append(verify_task)
        
        return subtasks
    
    def _get_required_capabilities(self, task_type: TaskType) -> List[str]:
        """Get required capabilities for a task type."""
        capability_map = {
            TaskType.DESIGN: ["design", "architecture", "planning"],
            TaskType.IMPLEMENT: ["implement", "code", "build"],
            TaskType.TEST: ["test", "verify", "validate"],
            TaskType.REVIEW: ["review", "audit", "quality"],
            TaskType.SECURITY: ["security", "vulnerability", "audit"],
            TaskType.PERFORMANCE: ["performance", "optimize", "profile"],
            TaskType.DOCUMENTATION: ["document", "explain", "write"],
            TaskType.DEBUG: ["debug", "troubleshoot", "fix"],
            TaskType.REFACTOR: ["refactor", "improve", "clean"],
            TaskType.DEPLOY: ["deploy", "release", "ci-cd"],
        }
        return capability_map.get(task_type, ["general"])
    
    def _can_parallelize(self, subtasks: List[SubTask]) -> bool:
        """Determine if subtasks can be executed in parallel."""
        # If any task has dependencies, we need ordered execution
        for task in subtasks:
            if task.dependencies:
                return False
        return len(subtasks) > 1
    
    async def suggest_agents(self, task_plan: TaskPlan) -> AgentProposal:
        """
        Suggest agents for executing the task plan.
        
        Args:
            task_plan: The task plan to assign agents to
            
        Returns:
            AgentProposal with suggested agent allocations
        """
        suggestions = []
        reused = 0
        new = 0
        
        # Get existing active agents
        existing_agents = await self.db.get_active_agents()
        
        # Match subtasks to agents
        for subtask in task_plan.subtasks:
            # Try to find matching existing agent
            matched_agent = await self._find_matching_agent(existing_agents, subtask)
            
            if matched_agent:
                suggestion = AgentSuggestion(
                    agent_id=matched_agent['id'],
                    agent_name=matched_agent['name'],
                    agent_type=matched_agent['type'],
                    is_new=False,
                    session_id=matched_agent.get('session_id'),
                    capabilities=matched_agent.get('capabilities', []),
                    assigned_task=subtask
                )
                reused += 1
            else:
                # Create new agent suggestion
                agent_type = self._determine_agent_type(subtask)
                suggestion = AgentSuggestion(
                    agent_id=None,
                    agent_name=f"{agent_type}-{uuid4().hex[:8]}",
                    agent_type=agent_type,
                    is_new=True,
                    capabilities=self.AGENT_CAPABILITIES.get(agent_type, []),
                    assigned_task=subtask
                )
                new += 1
            
            suggestions.append(suggestion)
            subtask.assigned_agent = suggestion.agent_name
        
        return AgentProposal(
            suggestions=suggestions,
            reused_agents=reused,
            new_agents=new,
            total_cost_estimate=new * 0.05  # Estimate $0.05 per new agent session
        )
    
    async def _find_matching_agent(self, existing_agents: List[Dict], 
                                  subtask: SubTask) -> Optional[Dict]:
        """Find an existing agent that can handle the subtask."""
        for agent in existing_agents:
            agent_capabilities = agent.get('capabilities', [])
            
            # Check if agent has required capabilities
            if any(cap in agent_capabilities for cap in subtask.required_capabilities):
                # Check if agent is not busy (could check current task load)
                return agent
        
        return None
    
    def _determine_agent_type(self, subtask: SubTask) -> str:
        """Determine the best agent type for a subtask."""
        task_type_to_agent = {
            TaskType.DESIGN: "architect",
            TaskType.IMPLEMENT: "developer",
            TaskType.TEST: "tester",
            TaskType.REVIEW: "reviewer",
            TaskType.SECURITY: "security-auditor",
            TaskType.PERFORMANCE: "performance-optimizer",
            TaskType.DOCUMENTATION: "documentation-writer",
            TaskType.DEBUG: "debugger",
            TaskType.REFACTOR: "developer",
            TaskType.DEPLOY: "developer",
        }
        return task_type_to_agent.get(subtask.task_type, "developer")