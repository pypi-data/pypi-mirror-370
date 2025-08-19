"""
Coordinator Agent - Special agent that orchestrates and coordinates other agents.

This agent manages execution phases, monitors progress, and synthesizes results.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .agent_message_bus import AgentMessageBus, MessageType
from .orchestrated_agent import OrchestratedAgent
from ..utils.logging_config import MAOSLogger


class CoordinationPhase(Enum):
    """Phases of coordinated execution."""
    PLANNING = "planning"
    DISCOVERY = "discovery"
    IMPLEMENTATION = "implementation"
    INTEGRATION = "integration"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"


@dataclass
class AgentAssignment:
    """Assignment of an agent to a task."""
    agent_id: str
    agent_type: str
    task: str
    phase: CoordinationPhase
    dependencies: List[str] = None  # Other agents this depends on
    status: str = "pending"
    result: Optional[Dict] = None


@dataclass
class CoordinationPlan:
    """Execution plan for coordinated agents."""
    goal: str
    phases: List[CoordinationPhase]
    assignments: List[AgentAssignment]
    constraints: Dict[str, Any]
    created_at: str


class CoordinatorAgent:
    """
    Special agent that orchestrates other agents for complex tasks.
    
    The coordinator:
    - Breaks down goals into phases
    - Assigns agents to phases
    - Monitors progress via message bus
    - Adjusts plan based on discoveries
    - Synthesizes results from all agents
    """
    
    def __init__(
        self,
        coordinator_id: str,
        message_bus: AgentMessageBus
    ):
        """
        Initialize coordinator agent.
        
        Args:
            coordinator_id: Unique coordinator identifier
            message_bus: Message bus for communication
        """
        self.coordinator_id = coordinator_id
        self.message_bus = message_bus
        self.logger = MAOSLogger(f"coordinator_{coordinator_id}")
        
        # Tracking
        self.active_agents: Dict[str, AgentAssignment] = {}
        self.discoveries: List[Dict] = []
        self.phase_results: Dict[CoordinationPhase, List[Dict]] = {}
        self.current_phase: Optional[CoordinationPhase] = None
        self.plan: Optional[CoordinationPlan] = None
        
        # Register coordinator with message bus
        asyncio.create_task(self._register_coordinator())
    
    async def _register_coordinator(self):
        """Register coordinator with message bus."""
        await self.message_bus.register_agent(
            agent_id=self.coordinator_id,
            agent_info={
                "name": f"coordinator-{self.coordinator_id[:8]}",
                "type": "coordinator",
                "capabilities": ["coordination", "synthesis", "planning"]
            },
            subscriptions=[MessageType.DISCOVERY, MessageType.DEPENDENCY, MessageType.ERROR],
            create_in_db=False
        )
    
    async def coordinate(
        self,
        agents: List[Dict[str, str]],
        goal: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate multiple agents to achieve a goal.
        
        Args:
            agents: List of agent dictionaries with 'agent_id' and 'agent_type'
            goal: The goal to achieve
            constraints: Optional constraints (time, resources, etc.)
            
        Returns:
            Coordination result with synthesized output
        """
        self.logger.logger.info(f"Starting coordination for goal: {goal}")
        
        # Step 1: Create coordination plan
        self.plan = await self._create_plan(agents, goal, constraints or {})
        
        # Step 2: Announce plan to all agents
        await self._announce_plan()
        
        # Step 3: Execute phases
        for phase in self.plan.phases:
            self.current_phase = phase
            self.logger.logger.info(f"Executing phase: {phase.value}")
            
            # Get agents for this phase
            phase_agents = [
                a for a in self.plan.assignments
                if a.phase == phase
            ]
            
            if phase_agents:
                # Execute phase
                phase_results = await self._execute_phase(phase, phase_agents)
                self.phase_results[phase] = phase_results
                
                # Adjust plan based on results if needed
                await self._adjust_plan_if_needed(phase, phase_results)
        
        # Step 4: Synthesize results
        final_result = await self._synthesize_results()
        
        # Step 5: Notify completion
        await self._notify_completion(final_result)
        
        return {
            "success": True,
            "goal": goal,
            "phases_completed": len(self.phase_results),
            "discoveries": self.discoveries,
            "synthesized_result": final_result,
            "coordination_summary": self._get_coordination_summary()
        }
    
    async def _create_plan(
        self,
        agents: List[Dict[str, str]],
        goal: str,
        constraints: Dict[str, Any]
    ) -> CoordinationPlan:
        """
        Create execution plan based on goal and available agents.
        
        Args:
            agents: Available agents
            goal: Goal to achieve
            constraints: Execution constraints
            
        Returns:
            Coordination plan
        """
        # Determine phases based on goal
        phases = self._determine_phases(goal)
        
        # Create assignments
        assignments = []
        
        for agent in agents:
            agent_id = agent["agent_id"]
            agent_type = agent["agent_type"]
            
            # Assign agent to appropriate phase based on type
            phase = self._get_agent_phase(agent_type)
            task = self._get_agent_task(agent_type, goal)
            
            assignment = AgentAssignment(
                agent_id=agent_id,
                agent_type=agent_type,
                task=task,
                phase=phase,
                dependencies=self._get_agent_dependencies(agent_type, agents)
            )
            assignments.append(assignment)
            self.active_agents[agent_id] = assignment
        
        return CoordinationPlan(
            goal=goal,
            phases=phases,
            assignments=assignments,
            constraints=constraints,
            created_at=datetime.now().isoformat()
        )
    
    def _determine_phases(self, goal: str) -> List[CoordinationPhase]:
        """
        Determine execution phases based on goal.
        
        Args:
            goal: Goal description
            
        Returns:
            List of phases
        """
        # Analysis goals need discovery first
        if "analyze" in goal.lower() or "audit" in goal.lower():
            return [
                CoordinationPhase.DISCOVERY,
                CoordinationPhase.PLANNING,
                CoordinationPhase.VALIDATION,
                CoordinationPhase.SYNTHESIS
            ]
        
        # Building/implementation goals
        elif "build" in goal.lower() or "implement" in goal.lower() or "create" in goal.lower():
            return [
                CoordinationPhase.PLANNING,
                CoordinationPhase.IMPLEMENTATION,
                CoordinationPhase.INTEGRATION,
                CoordinationPhase.VALIDATION,
                CoordinationPhase.SYNTHESIS
            ]
        
        # Default phases
        else:
            return [
                CoordinationPhase.PLANNING,
                CoordinationPhase.DISCOVERY,
                CoordinationPhase.IMPLEMENTATION,
                CoordinationPhase.SYNTHESIS
            ]
    
    def _get_agent_phase(self, agent_type: str) -> CoordinationPhase:
        """
        Determine which phase an agent should work in.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Appropriate phase
        """
        type_lower = agent_type.lower()
        
        if "analyst" in type_lower or "audit" in type_lower:
            return CoordinationPhase.DISCOVERY
        elif "architect" in type_lower or "design" in type_lower:
            return CoordinationPhase.PLANNING
        elif "developer" in type_lower or "implement" in type_lower:
            return CoordinationPhase.IMPLEMENTATION
        elif "test" in type_lower or "qa" in type_lower:
            return CoordinationPhase.VALIDATION
        elif "security" in type_lower:
            return CoordinationPhase.DISCOVERY
        else:
            return CoordinationPhase.IMPLEMENTATION
    
    def _get_agent_task(self, agent_type: str, goal: str) -> str:
        """
        Create specific task for agent based on type and goal.
        
        Args:
            agent_type: Type of agent
            goal: Overall goal
            
        Returns:
            Specific task for agent
        """
        type_lower = agent_type.lower()
        
        if "analyst" in type_lower:
            return f"Analyze the codebase for: {goal}. Share key findings."
        elif "developer" in type_lower:
            return f"Implement required changes for: {goal}. Coordinate with other developers."
        elif "security" in type_lower:
            return f"Perform security analysis for: {goal}. Report vulnerabilities."
        elif "architect" in type_lower:
            return f"Design architecture for: {goal}. Share design decisions."
        elif "tester" in type_lower:
            return f"Create and run tests for: {goal}. Report coverage."
        else:
            return f"Complete your part of: {goal}"
    
    def _get_agent_dependencies(
        self,
        agent_type: str,
        all_agents: List[Dict[str, str]]
    ) -> List[str]:
        """
        Determine agent dependencies.
        
        Args:
            agent_type: Type of agent
            all_agents: All available agents
            
        Returns:
            List of agent IDs this agent depends on
        """
        dependencies = []
        type_lower = agent_type.lower()
        
        # Developers depend on architects
        if "developer" in type_lower:
            for agent in all_agents:
                if "architect" in agent["agent_type"].lower():
                    dependencies.append(agent["agent_id"])
        
        # Testers depend on developers
        elif "test" in type_lower:
            for agent in all_agents:
                if "developer" in agent["agent_type"].lower():
                    dependencies.append(agent["agent_id"])
        
        # Integration depends on implementation
        elif "integrat" in type_lower:
            for agent in all_agents:
                if "developer" in agent["agent_type"].lower() or "implement" in agent["agent_type"].lower():
                    dependencies.append(agent["agent_id"])
        
        return dependencies
    
    async def _announce_plan(self):
        """Announce coordination plan to all agents."""
        plan_summary = f"""
COORDINATION PLAN:
Goal: {self.plan.goal}
Phases: {', '.join([p.value for p in self.plan.phases])}
Agents: {len(self.plan.assignments)}

Your assignments:
"""
        
        for assignment in self.plan.assignments:
            agent_message = plan_summary + f"""
Agent: {assignment.agent_id}
Task: {assignment.task}
Phase: {assignment.phase.value}
Dependencies: {', '.join(assignment.dependencies) if assignment.dependencies else 'None'}
"""
            
            await self.message_bus.send_message(
                from_agent=self.coordinator_id,
                to_agent=assignment.agent_id,
                content=agent_message,
                message_type=MessageType.COORDINATION
            )
        
        self.logger.logger.info(f"Announced plan to {len(self.plan.assignments)} agents")
    
    async def _execute_phase(
        self,
        phase: CoordinationPhase,
        agents: List[AgentAssignment]
    ) -> List[Dict[str, Any]]:
        """
        Execute a coordination phase.
        
        Args:
            phase: Phase to execute
            agents: Agents assigned to this phase
            
        Returns:
            Phase results
        """
        self.logger.logger.info(f"Executing phase {phase.value} with {len(agents)} agents")
        
        # Notify phase start
        for agent in agents:
            await self.message_bus.send_message(
                from_agent=self.coordinator_id,
                to_agent=agent.agent_id,
                content=f"START_PHASE: {phase.value}. Execute your task: {agent.task}",
                message_type=MessageType.COORDINATION
            )
            agent.status = "executing"
        
        # Monitor phase execution
        phase_complete = False
        phase_results = []
        start_time = asyncio.get_event_loop().time()
        timeout = 120  # 2 minutes per phase
        
        while not phase_complete:
            # Check for discoveries
            await self._check_discoveries()
            
            # Check if all agents completed
            completed = sum(1 for a in agents if a.status == "completed")
            if completed == len(agents):
                phase_complete = True
                self.logger.logger.info(f"Phase {phase.value} completed by all agents")
            
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                self.logger.logger.warning(f"Phase {phase.value} timed out")
                phase_complete = True
            
            await asyncio.sleep(2)
        
        # Collect results
        for agent in agents:
            if agent.result:
                phase_results.append({
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "status": agent.status,
                    "result": agent.result
                })
        
        return phase_results
    
    async def _check_discoveries(self):
        """Check for and process discoveries from agents."""
        messages = await self.message_bus.get_messages_for_agent(
            self.coordinator_id,
            message_types=[MessageType.DISCOVERY]
        )
        
        for message in messages:
            if message.message_id not in [d.get("message_id") for d in self.discoveries]:
                discovery = {
                    "message_id": message.message_id,
                    "from_agent": message.from_agent,
                    "content": message.content,
                    "timestamp": message.timestamp,
                    "phase": self.current_phase.value if self.current_phase else None
                }
                self.discoveries.append(discovery)
                
                # Broadcast important discoveries
                if message.metadata.get("importance") == "high":
                    await self.message_bus.broadcast(
                        from_agent=self.coordinator_id,
                        content=f"IMPORTANT DISCOVERY from {message.from_agent}: {message.content}",
                        message_type=MessageType.COORDINATION
                    )
    
    async def _adjust_plan_if_needed(
        self,
        phase: CoordinationPhase,
        results: List[Dict]
    ):
        """
        Adjust plan based on phase results.
        
        Args:
            phase: Completed phase
            results: Phase results
        """
        # Check for failures
        failures = [r for r in results if r.get("status") != "completed"]
        if failures:
            self.logger.logger.warning(f"Phase {phase.value} had {len(failures)} failures")
            
            # Could add retry logic or reassignment here
        
        # Check for critical discoveries
        critical_discoveries = [
            d for d in self.discoveries
            if d.get("phase") == phase.value and "critical" in d.get("content", "").lower()
        ]
        
        if critical_discoveries:
            self.logger.logger.info(f"Found {len(critical_discoveries)} critical discoveries")
            
            # Notify all agents about critical findings
            for discovery in critical_discoveries:
                await self.message_bus.broadcast(
                    from_agent=self.coordinator_id,
                    content=f"CRITICAL: {discovery['content']}",
                    message_type=MessageType.COORDINATION
                )
    
    async def _synthesize_results(self) -> Dict[str, Any]:
        """
        Synthesize results from all phases.
        
        Returns:
            Synthesized result
        """
        self.logger.logger.info("Synthesizing results from all phases")
        
        synthesis = {
            "goal": self.plan.goal,
            "phases_completed": list(self.phase_results.keys()),
            "total_agents": len(self.plan.assignments),
            "discoveries_count": len(self.discoveries),
            "key_findings": [],
            "recommendations": [],
            "issues": [],
            "success_metrics": {}
        }
        
        # Extract key findings from discoveries
        for discovery in self.discoveries[:10]:  # Top 10 discoveries
            synthesis["key_findings"].append({
                "from": discovery["from_agent"],
                "finding": discovery["content"][:200]
            })
        
        # Analyze phase results
        for phase, results in self.phase_results.items():
            successful = sum(1 for r in results if r.get("status") == "completed")
            synthesis["success_metrics"][phase.value] = f"{successful}/{len(results)}"
        
        # Generate recommendations based on discoveries
        if any("security" in d["content"].lower() for d in self.discoveries):
            synthesis["recommendations"].append("Address security findings before deployment")
        
        if any("performance" in d["content"].lower() for d in self.discoveries):
            synthesis["recommendations"].append("Optimize performance based on analysis")
        
        return synthesis
    
    async def _notify_completion(self, result: Dict[str, Any]):
        """
        Notify all agents of completion.
        
        Args:
            result: Final synthesized result
        """
        completion_message = f"""
COORDINATION COMPLETE:
Goal: {self.plan.goal}
Success: {result.get('success', False)}
Phases: {', '.join([p.value for p in self.plan.phases])}
Key Findings: {len(result.get('key_findings', []))}

Thank you for your contribution to this coordinated effort.
"""
        
        await self.message_bus.broadcast(
            from_agent=self.coordinator_id,
            content=completion_message,
            message_type=MessageType.COORDINATION
        )
        
        self.logger.logger.info("Notified all agents of completion")
    
    def _get_coordination_summary(self) -> str:
        """
        Get human-readable coordination summary.
        
        Returns:
            Coordination summary
        """
        summary = f"""
Coordination Summary:
━━━━━━━━━━━━━━━━━━━
Goal: {self.plan.goal if self.plan else 'N/A'}
Phases Executed: {len(self.phase_results)}
Total Agents: {len(self.active_agents)}
Discoveries: {len(self.discoveries)}

Phase Results:
"""
        
        for phase, results in self.phase_results.items():
            successful = sum(1 for r in results if r.get("status") == "completed")
            summary += f"  {phase.value}: {successful}/{len(results)} successful\n"
        
        if self.discoveries:
            summary += "\nTop Discoveries:\n"
            for discovery in self.discoveries[:3]:
                summary += f"  - {discovery['from_agent']}: {discovery['content'][:100]}...\n"
        
        return summary
    
    async def handle_agent_failure(self, agent_id: str, error: str):
        """
        Handle agent failure during coordination.
        
        Args:
            agent_id: Failed agent ID
            error: Error message
        """
        if agent_id in self.active_agents:
            assignment = self.active_agents[agent_id]
            assignment.status = "failed"
            assignment.result = {"error": error}
            
            self.logger.logger.error(f"Agent {agent_id} failed: {error}")
            
            # Notify other agents in same phase
            phase_agents = [
                a for a in self.plan.assignments
                if a.phase == assignment.phase and a.agent_id != agent_id
            ]
            
            for agent in phase_agents:
                await self.message_bus.send_message(
                    from_agent=self.coordinator_id,
                    to_agent=agent.agent_id,
                    content=f"Agent {agent_id} has failed. Adjust your execution if needed.",
                    message_type=MessageType.COORDINATION
                )
    
    async def pause_coordination(self):
        """Pause coordination (for resumption later)."""
        self.logger.logger.info("Pausing coordination")
        
        await self.message_bus.broadcast(
            from_agent=self.coordinator_id,
            content="PAUSE: Coordination paused. Stand by for resumption.",
            message_type=MessageType.COORDINATION
        )
    
    async def resume_coordination(self):
        """Resume paused coordination."""
        self.logger.logger.info("Resuming coordination")
        
        await self.message_bus.broadcast(
            from_agent=self.coordinator_id,
            content=f"RESUME: Continuing from phase {self.current_phase.value if self.current_phase else 'start'}",
            message_type=MessageType.COORDINATION
        )