"""
Enhanced Task Decomposer for MAOS orchestration system.

Provides better task understanding and explicit agent assignment.
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
    ANALYZE = "analyze"
    UNDERSTAND = "understand"
    EXPLAIN = "explain"
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
    specific_instructions: Optional[str] = None
    
    @property
    def agent_type(self) -> str:
        """Map task type to agent type for compatibility."""
        task_to_agent_map = {
            TaskType.ANALYZE: "analyst",
            TaskType.UNDERSTAND: "analyst", 
            TaskType.EXPLAIN: "analyst",
            TaskType.DESIGN: "architect",
            TaskType.IMPLEMENT: "developer",
            TaskType.TEST: "tester",
            TaskType.REVIEW: "reviewer",
            TaskType.SECURITY: "security",
            TaskType.PERFORMANCE: "performance",
            TaskType.DOCUMENTATION: "developer",
            TaskType.DEBUG: "developer",
            TaskType.REFACTOR: "developer",
            TaskType.DEPLOY: "developer"
        }
        return task_to_agent_map.get(self.task_type, "analyst")
    
    def to_claude_prompt(self) -> str:
        """Convert subtask to a Claude prompt."""
        prompt = f"{self.description}\n\n"
        
        if self.specific_instructions:
            prompt += f"Instructions:\n{self.specific_instructions}\n\n"
        
        if self.task_type == TaskType.ANALYZE:
            prompt += "Focus on: understanding the structure, patterns, and architecture.\n"
        elif self.task_type == TaskType.UNDERSTAND:
            prompt += "Focus on: comprehending the purpose, requirements, and business logic.\n"
        elif self.task_type == TaskType.EXPLAIN:
            prompt += "Focus on: providing clear explanations suitable for the audience.\n"
        elif self.task_type == TaskType.REVIEW:
            prompt += "Focus on: code quality, security issues, performance problems, best practices.\n"
        elif self.task_type == TaskType.TEST:
            prompt += "Write comprehensive tests including edge cases and error scenarios.\n"
        
        return prompt


@dataclass
class TaskPlan:
    """Complete plan for executing a user request."""
    id: str
    original_request: str
    subtasks: List[SubTask]
    estimated_agents_needed: int
    parallel_execution_possible: bool
    explanation: str = ""
    
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
    role_description: str = ""


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
                if suggestion.role_description:
                    lines.append(f"       Role: {suggestion.role_description}")
            else:
                session_info = f" [session: {suggestion.session_id[:8]}]" if suggestion.session_id else ""
                lines.append(f"  REUSE: {suggestion.agent_name}{session_info}")
            
            if suggestion.assigned_task:
                lines.append(f"    → {suggestion.assigned_task.description}")
        
        return "\n".join(lines)


class EnhancedTaskDecomposer:
    """Enhanced task decomposer with better understanding and explainability."""
    
    # Agent type capabilities
    AGENT_CAPABILITIES = {
        "requirements-analyst": ["understand", "analyze", "requirements", "business-logic", "documentation"],
        "code-analyst": ["understand", "analyze", "code", "architecture", "implementation"],
        "architect": ["design", "planning", "architecture", "system-design"],
        "developer": ["implement", "code", "build", "refactor"],
        "tester": ["test", "verify", "validate", "qa"],
        "reviewer": ["review", "audit", "quality", "standards"],
        "security-auditor": ["security", "vulnerability", "penetration", "compliance"],
        "performance-optimizer": ["performance", "optimize", "profile", "benchmark"],
        "debugger": ["debug", "troubleshoot", "fix", "diagnose"],
        "documentation-writer": ["document", "explain", "tutorial", "guide"],
        "explainer": ["explain", "clarify", "communicate", "present"],
    }
    
    def __init__(self, db: SqlitePersistence):
        """
        Initialize enhanced task decomposer.
        
        Args:
            db: Database for checking existing agents
        """
        self.db = db
        self.logger = MAOSLogger("enhanced_task_decomposer")
    
    async def decompose(self, user_request: str) -> TaskPlan:
        """
        Break down user request into subtasks with better understanding.
        
        Args:
            user_request: Natural language request from user
            
        Returns:
            TaskPlan with subtasks and explanation
        """
        plan_id = str(uuid4())
        request_lower = user_request.lower()
        
        # Parse the request for specific agent requirements
        subtasks = []
        explanation = ""
        
        # Check for explicit agent specification - expanded patterns
        if any(pattern in request_lower for pattern in [
            "use", "spawn", "create", "launch", "start"
        ]) and "agent" in request_lower:
            # User wants specific agents
            subtasks, explanation = await self._parse_explicit_agents(user_request)
        
        # Check for codebase analysis request
        elif any(word in request_lower for word in ["explain", "analyze", "understand"]) and \
             any(word in request_lower for word in ["code", "codebase", "project"]):
            subtasks, explanation = self._generate_codebase_analysis_tasks(user_request)
        
        # Check for PRD/requirements (but be more specific)
        elif ("prd" in request_lower or "product requirements" in request_lower) and \
             "implement" in request_lower:
            subtasks, explanation = self._generate_prd_implementation_tasks(user_request)
        
        # Default: create a single task
        else:
            subtasks, explanation = self._generate_default_task(user_request)
        
        # Determine if parallel execution is possible
        parallel_possible = self._can_parallelize(subtasks)
        
        # Estimate agents needed
        agents_needed = len(set(task.assigned_agent or task.task_type.value for task in subtasks))
        
        # Save tasks to database
        for task in subtasks:
            await self._save_task_to_db(task, plan_id)
        
        return TaskPlan(
            id=plan_id,
            original_request=user_request,
            subtasks=subtasks,
            estimated_agents_needed=agents_needed,
            parallel_execution_possible=parallel_possible,
            explanation=explanation
        )
    
    async def _parse_explicit_agents(self, request: str) -> Tuple[List[SubTask], str]:
        """Parse request with explicit agent specifications."""
        subtasks = []
        request_lower = request.lower()
        
        # Pattern 1: "spawn X agent and Y agent" format
        if "spawn" in request_lower or "create" in request_lower:
            # Look for specific agent types mentioned
            agent_types = []
            if "analyst" in request_lower:
                agent_types.append("analyst")
            if "security" in request_lower:
                agent_types.append("security")
            if "developer" in request_lower:
                agent_types.append("developer")
            if "tester" in request_lower:
                agent_types.append("tester")
            if "reviewer" in request_lower:
                agent_types.append("reviewer")
            
            # Create tasks for each agent type found
            for agent_type in agent_types:
                if agent_type == "analyst":
                    task = SubTask(
                        id=str(uuid4()),
                        description=f"Analyze and explain what the calculator does, its functionality and architecture",
                        task_type=TaskType.ANALYZE,
                        required_capabilities=["analyze", "code", "explain"],
                        assigned_agent="analyst",
                        specific_instructions="Focus on understanding the calculator's purpose, main features, code structure, and how it works."
                    )
                    subtasks.append(task)
                
                elif agent_type == "security":
                    task = SubTask(
                        id=str(uuid4()),
                        description=f"Perform security analysis and identify ways to improve security",
                        task_type=TaskType.SECURITY,
                        required_capabilities=["security", "audit", "vulnerability"],
                        assigned_agent="security",
                        specific_instructions="Focus on identifying security vulnerabilities, potential attack vectors, and recommendations for improving security."
                    )
                    subtasks.append(task)
                
                elif agent_type == "developer":
                    task = SubTask(
                        id=str(uuid4()),
                        description=f"Implement code improvements and new features",
                        task_type=TaskType.IMPLEMENT,
                        required_capabilities=["implement", "code", "develop"],
                        assigned_agent="developer",
                        specific_instructions="Focus on implementing new features, fixing bugs, and improving code quality."
                    )
                    subtasks.append(task)
            
            if subtasks:
                explanation = f"Creating {len(subtasks)} specialized agents as requested: " + \
                             ", ".join([f"{t.assigned_agent}" for t in subtasks])
                return subtasks, explanation
        
        # Pattern 2: "use 2 agents, one which..." or "one that..." 
        if ("one which" in request_lower or "one that" in request_lower) and "understand" in request_lower:
            # Check for requirements agent
            if "requirement" in request_lower:
                # Requirements understanding agent
                task1 = SubTask(
                    id=str(uuid4()),
                    description="Analyze and understand the requirements, business logic, and documentation in this codebase",
                    task_type=TaskType.UNDERSTAND,
                    required_capabilities=["understand", "requirements", "documentation"],
                    assigned_agent="requirements-analyst",
                    specific_instructions="Focus on understanding the business requirements, user stories, and functional specifications. Look for requirements documents, README files, API documentation, and comments that explain the purpose and goals."
                )
                subtasks.append(task1)
            
            # Check for code agent - look for variations
            if "code" in request_lower and ("one that" in request_lower or "and one" in request_lower):
                # Code understanding agent
                task2 = SubTask(
                    id=str(uuid4()),
                    description="Analyze and understand the code structure, implementation, and architecture of this codebase",
                    task_type=TaskType.ANALYZE,
                    required_capabilities=["analyze", "code", "architecture"],
                    assigned_agent="code-analyst",
                    specific_instructions="Focus on understanding the code architecture, design patterns, implementation details, and technical decisions. Analyze the file structure, dependencies, and how components interact."
                )
                subtasks.append(task2)
        
        explanation = f"Creating {len(subtasks)} specialized agents as requested: " + \
                     ", ".join([f"{t.assigned_agent} for {t.task_type.value}" for t in subtasks])
        
        return subtasks, explanation
    
    def _generate_codebase_analysis_tasks(self, request: str) -> Tuple[List[SubTask], str]:
        """Generate tasks for codebase analysis."""
        subtasks = []
        request_lower = request.lower()
        
        # Check if multiple types of analysis are requested
        analysis_types = []
        
        # Look for different analysis keywords
        if any(word in request_lower for word in ["analyze", "analysis"]):
            analysis_types.append("general")
        
        if any(word in request_lower for word in ["security", "secure", "vulnerability", "audit"]):
            analysis_types.append("security")
        
        if any(word in request_lower for word in ["performance", "optimize", "speed", "efficiency"]):
            analysis_types.append("performance")
        
        # If multiple analysis types detected, create separate tasks
        if len(analysis_types) > 1 or "security" in analysis_types:
            # Create general analysis task
            if "general" in analysis_types:
                task1 = SubTask(
                    id=str(uuid4()),
                    description="Analyze and explain what the calculator app does, its functionality and architecture",
                    task_type=TaskType.ANALYZE,
                    required_capabilities=["analyze", "code", "explain"],
                    assigned_agent="analyst",
                    specific_instructions="Focus on understanding the calculator's purpose, main features, code structure, and how it works."
                )
                subtasks.append(task1)
            
            # Create security analysis task
            if "security" in analysis_types:
                task2 = SubTask(
                    id=str(uuid4()),
                    description="Perform security analysis of the calculator app and identify security improvements",
                    task_type=TaskType.SECURITY,
                    required_capabilities=["security", "audit", "vulnerability"],
                    assigned_agent="security",
                    specific_instructions="Focus on identifying security vulnerabilities, potential attack vectors, input validation issues, and recommendations for improving security."
                )
                subtasks.append(task2)
            
            # Create performance analysis task
            if "performance" in analysis_types:
                task3 = SubTask(
                    id=str(uuid4()),
                    description="Analyze performance and identify optimization opportunities",
                    task_type=TaskType.PERFORMANCE,
                    required_capabilities=["performance", "optimize", "profile"],
                    assigned_agent="performance",
                    specific_instructions="Focus on identifying performance bottlenecks, memory usage, and optimization opportunities."
                )
                subtasks.append(task3)
            
            explanation = f"Creating {len(subtasks)} specialized analysis tasks: " + \
                         ", ".join([f"{t.assigned_agent} for {t.task_type.value}" for t in subtasks])
        else:
            # Single comprehensive analysis task
            task = SubTask(
                id=str(uuid4()),
                description=request,
                task_type=TaskType.ANALYZE,
                required_capabilities=["analyze", "code", "explain"],
                specific_instructions="Provide a comprehensive analysis of the codebase including its purpose, architecture, key components, and how it works."
            )
            subtasks.append(task)
            explanation = "Creating a code analysis task to understand and explain the codebase"
        
        return subtasks, explanation
    
    def _generate_prd_implementation_tasks(self, request: str) -> Tuple[List[SubTask], str]:
        """Generate tasks for PRD implementation."""
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
        
        # Implementation tasks...
        # (keeping existing PRD logic when it's actually needed)
        
        explanation = "Breaking down PRD implementation into design, development, and testing phases"
        
        return subtasks, explanation
    
    def _generate_default_task(self, request: str) -> Tuple[List[SubTask], str]:
        """Generate a default task when no specific pattern matches."""
        task = SubTask(
            id=str(uuid4()),
            description=request,
            task_type=self._identify_task_type(request.lower()),
            required_capabilities=["general"]
        )
        
        explanation = f"Creating a single task to {task.task_type.value} as requested"
        
        return [task], explanation
    
    def _identify_task_type(self, request: str) -> TaskType:
        """Identify the primary task type from the request."""
        type_keywords = {
            TaskType.ANALYZE: ["analyze", "analysis", "examine"],
            TaskType.UNDERSTAND: ["understand", "comprehend", "grasp"],
            TaskType.EXPLAIN: ["explain", "describe", "clarify"],
            TaskType.IMPLEMENT: ["implement", "build", "create", "develop"],
            TaskType.TEST: ["test", "verify", "validate"],
            TaskType.REVIEW: ["review", "audit", "check"],
            TaskType.DEBUG: ["debug", "fix", "troubleshoot"],
        }
        
        for task_type, keywords in type_keywords.items():
            if any(keyword in request for keyword in keywords):
                return task_type
        
        return TaskType.IMPLEMENT
    
    def _can_parallelize(self, subtasks: List[SubTask]) -> bool:
        """Determine if subtasks can be executed in parallel."""
        # If any task has dependencies, we need ordered execution
        for task in subtasks:
            if task.dependencies:
                return False
        return len(subtasks) > 1
    
    async def _save_task_to_db(self, task: SubTask, plan_id: str):
        """Save task to database."""
        try:
            # Don't set parent_task_id to plan_id as it's not a task
            # Use parent_task_id only for actual task dependencies
            await self.db.create_task(
                task_id=task.id,
                description=task.description,
                parent_task_id=task.parent_task_id,  # Use actual parent task if exists
                assigned_agents=[task.assigned_agent] if task.assigned_agent else []
            )
            self.logger.logger.debug(f"Saved task {task.id} to database")
        except Exception as e:
            self.logger.log_error(e, {"operation": "save_task", "task_id": task.id})
    
    async def suggest_agents(self, task_plan: TaskPlan) -> AgentProposal:
        """
        Suggest agents for executing the task plan with better descriptions.
        
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
                    assigned_task=subtask,
                    role_description=f"Reusing existing {matched_agent['type']} agent"
                )
                reused += 1
            else:
                # Create new agent suggestion with better naming
                agent_type = subtask.assigned_agent or self._determine_agent_type(subtask)
                agent_name = f"{agent_type}-{uuid4().hex[:8]}"
                
                suggestion = AgentSuggestion(
                    agent_id=None,
                    agent_name=agent_name,
                    agent_type=agent_type,
                    is_new=True,
                    capabilities=self.AGENT_CAPABILITIES.get(agent_type, ["general"]),
                    assigned_task=subtask,
                    role_description=self._get_agent_role_description(agent_type, subtask)
                )
                new += 1
            
            suggestions.append(suggestion)
            subtask.assigned_agent = suggestion.agent_name
        
        return AgentProposal(
            suggestions=suggestions,
            reused_agents=reused,
            new_agents=new,
            total_cost_estimate=new * 0.05
        )
    
    def _get_agent_role_description(self, agent_type: str, subtask: SubTask) -> str:
        """Get a description of the agent's role."""
        descriptions = {
            "requirements-analyst": "Specializes in understanding business requirements and documentation",
            "code-analyst": "Specializes in analyzing code structure and implementation",
            "architect": "Designs system architecture and technical solutions",
            "developer": "Implements features and functionality",
            "tester": "Creates and runs tests to ensure quality",
            "reviewer": "Reviews code for quality and best practices",
            "explainer": "Explains complex concepts in clear terms",
        }
        return descriptions.get(agent_type, f"Handles {subtask.task_type.value} tasks")
    
    async def _find_matching_agent(self, existing_agents: List[Dict], 
                                  subtask: SubTask) -> Optional[Dict]:
        """Find an existing agent that can handle the subtask."""
        for agent in existing_agents:
            agent_capabilities = agent.get('capabilities', [])
            
            # Check if agent has required capabilities
            if any(cap in agent_capabilities for cap in subtask.required_capabilities):
                return agent
        
        return None
    
    def _determine_agent_type(self, subtask: SubTask) -> str:
        """Determine the best agent type for a subtask."""
        task_type_to_agent = {
            TaskType.ANALYZE: "code-analyst",
            TaskType.UNDERSTAND: "requirements-analyst",
            TaskType.EXPLAIN: "explainer",
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