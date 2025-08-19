"""Conflict resolution protocols for consensus building."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""
    PRIORITY_BASED = "priority_based"  # Higher priority wins
    TIMESTAMP_BASED = "timestamp_based"  # First-come-first-serve
    AUTHORITY_BASED = "authority_based"  # Designated authority decides
    WEIGHTED_AVERAGE = "weighted_average"  # Weighted combination
    NEGOTIATION = "negotiation"  # Multi-round negotiation
    ARBITRATION = "arbitration"  # Third-party arbitrator
    CONSENSUS_BUILDING = "consensus_building"  # Build mutual agreement


@dataclass
class Conflict:
    """Represents a conflict between multiple proposals or decisions."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    conflicting_proposals: List[str] = field(default_factory=list)  # proposal IDs
    participants: Set[str] = field(default_factory=set)
    conflict_type: str = "resource"  # resource, priority, decision, value
    severity: int = 1  # 1=low, 5=critical
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionProposal:
    """A proposed resolution to a conflict."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conflict_id: str = ""
    proposer: str = ""
    solution: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    affected_parties: Set[str] = field(default_factory=set)
    cost_benefit: Dict[str, float] = field(default_factory=dict)
    implementation_complexity: int = 1  # 1=simple, 5=complex
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResolutionResult:
    """Result of a conflict resolution process."""
    conflict_id: str
    resolution_proposal_id: Optional[str] = None
    status: str = "resolved"  # resolved, failed, escalated
    solution: Dict[str, Any] = field(default_factory=dict)
    agreement_level: float = 0.0  # 0.0 to 1.0
    dissenting_parties: Set[str] = field(default_factory=set)
    implementation_plan: List[Dict[str, Any]] = field(default_factory=list)
    follow_up_required: bool = False
    resolved_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConflictResolver:
    """Manages conflict resolution processes."""
    
    def __init__(self):
        # Active conflicts
        self.conflicts: Dict[str, Conflict] = {}
        
        # Resolution proposals
        self.resolution_proposals: Dict[str, List[ResolutionProposal]] = {}  # conflict_id -> proposals
        
        # Completed resolutions
        self.completed_resolutions: Dict[str, ResolutionResult] = {}
        
        # Authority mappings for authority-based resolution
        self.authorities: Dict[str, str] = {}  # domain -> authority_agent_id
        
        # Agent priorities for priority-based resolution
        self.agent_priorities: Dict[str, int] = {}  # agent_id -> priority_level
        
        # Agent weights for weighted resolution
        self.agent_weights: Dict[str, float] = {}  # agent_id -> weight
        
        # Resolution callbacks
        self.resolution_callbacks: Dict[str, callable] = {}
        
        # Background tasks
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.metrics = {
            "conflicts_created": 0,
            "conflicts_resolved": 0,
            "conflicts_escalated": 0,
            "average_resolution_time": 0.0,
            "resolution_success_rate": 0.0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Conflict resolver initialized")
    
    async def start(self):
        """Start the conflict resolver."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start monitoring task
        self.monitor_task = asyncio.create_task(self._monitor_conflicts())
        
        logger.info("Conflict resolver started")
    
    async def stop(self):
        """Stop the conflict resolver."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel monitoring task
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Conflict resolver stopped")
    
    async def report_conflict(
        self,
        title: str,
        description: str,
        conflicting_proposals: List[str],
        participants: List[str],
        conflict_type: str = "resource",
        severity: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Report a new conflict that needs resolution."""
        try:
            conflict = Conflict(
                title=title,
                description=description,
                conflicting_proposals=conflicting_proposals,
                participants=set(participants),
                conflict_type=conflict_type,
                severity=severity,
                metadata=metadata or {}
            )
            
            # Store conflict
            self.conflicts[conflict.id] = conflict
            self.resolution_proposals[conflict.id] = []
            
            self.metrics["conflicts_created"] += 1
            
            logger.info(f"Reported conflict '{title}' with ID {conflict.id}")
            return conflict.id
            
        except Exception as e:
            logger.error(f"Failed to report conflict: {e}")
            raise
    
    async def propose_resolution(
        self,
        conflict_id: str,
        proposer: str,
        solution: Dict[str, Any],
        rationale: str = "",
        affected_parties: Optional[List[str]] = None,
        cost_benefit: Optional[Dict[str, float]] = None,
        implementation_complexity: int = 1
    ) -> str:
        """Propose a resolution to a conflict."""
        try:
            if conflict_id not in self.conflicts:
                raise ValueError(f"Conflict {conflict_id} not found")
            
            conflict = self.conflicts[conflict_id]
            
            proposal = ResolutionProposal(
                conflict_id=conflict_id,
                proposer=proposer,
                solution=solution,
                rationale=rationale,
                affected_parties=set(affected_parties or []),
                cost_benefit=cost_benefit or {},
                implementation_complexity=implementation_complexity
            )
            
            # Add to proposals
            self.resolution_proposals[conflict_id].append(proposal)
            
            logger.info(f"Added resolution proposal {proposal.id} for conflict {conflict_id}")
            return proposal.id
            
        except Exception as e:
            logger.error(f"Failed to propose resolution: {e}")
            raise
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        strategy: ResolutionStrategy = ResolutionStrategy.CONSENSUS_BUILDING,
        callback: Optional[callable] = None
    ) -> str:
        """Resolve a conflict using the specified strategy."""
        try:
            if conflict_id not in self.conflicts:
                raise ValueError(f"Conflict {conflict_id} not found")
            
            conflict = self.conflicts[conflict_id]
            proposals = self.resolution_proposals[conflict_id]
            
            if not proposals:
                raise ValueError(f"No resolution proposals for conflict {conflict_id}")
            
            # Register callback if provided
            if callback:
                self.resolution_callbacks[conflict_id] = callback
            
            # Apply resolution strategy
            result = await self._apply_resolution_strategy(conflict, proposals, strategy)
            
            # Complete resolution
            await self._complete_resolution(conflict_id, result)
            
            logger.info(f"Resolved conflict {conflict_id} using {strategy.value}")
            return result.resolution_proposal_id or ""
            
        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict_id}: {e}")
            # Create failed result
            result = ResolutionResult(
                conflict_id=conflict_id,
                status="failed",
                metadata={"error": str(e)}
            )
            await self._complete_resolution(conflict_id, result)
            raise
    
    async def _apply_resolution_strategy(
        self,
        conflict: Conflict,
        proposals: List[ResolutionProposal],
        strategy: ResolutionStrategy
    ) -> ResolutionResult:
        """Apply the specified resolution strategy."""
        if strategy == ResolutionStrategy.PRIORITY_BASED:
            return await self._resolve_by_priority(conflict, proposals)
        elif strategy == ResolutionStrategy.TIMESTAMP_BASED:
            return await self._resolve_by_timestamp(conflict, proposals)
        elif strategy == ResolutionStrategy.AUTHORITY_BASED:
            return await self._resolve_by_authority(conflict, proposals)
        elif strategy == ResolutionStrategy.WEIGHTED_AVERAGE:
            return await self._resolve_by_weighted_average(conflict, proposals)
        elif strategy == ResolutionStrategy.NEGOTIATION:
            return await self._resolve_by_negotiation(conflict, proposals)
        elif strategy == ResolutionStrategy.ARBITRATION:
            return await self._resolve_by_arbitration(conflict, proposals)
        elif strategy == ResolutionStrategy.CONSENSUS_BUILDING:
            return await self._resolve_by_consensus_building(conflict, proposals)
        else:
            raise ValueError(f"Unknown resolution strategy: {strategy}")
    
    async def _resolve_by_priority(
        self,
        conflict: Conflict,
        proposals: List[ResolutionProposal]
    ) -> ResolutionResult:
        """Resolve conflict by choosing proposal from highest priority agent."""
        try:
            best_proposal = None
            highest_priority = -1
            
            for proposal in proposals:
                proposer_priority = self.agent_priorities.get(proposal.proposer, 0)
                if proposer_priority > highest_priority:
                    highest_priority = proposer_priority
                    best_proposal = proposal
            
            if not best_proposal:
                best_proposal = proposals[0]  # Fallback to first proposal
            
            return ResolutionResult(
                conflict_id=conflict.id,
                resolution_proposal_id=best_proposal.id,
                status="resolved",
                solution=best_proposal.solution,
                agreement_level=0.7,  # Moderate agreement for priority-based
                metadata={"strategy": "priority_based", "winning_priority": highest_priority}
            )
            
        except Exception as e:
            logger.error(f"Priority-based resolution failed: {e}")
            raise
    
    async def _resolve_by_timestamp(
        self,
        conflict: Conflict,
        proposals: List[ResolutionProposal]
    ) -> ResolutionResult:
        """Resolve conflict by choosing earliest proposal."""
        try:
            earliest_proposal = min(proposals, key=lambda p: p.created_at)
            
            return ResolutionResult(
                conflict_id=conflict.id,
                resolution_proposal_id=earliest_proposal.id,
                status="resolved",
                solution=earliest_proposal.solution,
                agreement_level=0.6,  # Lower agreement for timestamp-based
                metadata={"strategy": "timestamp_based", "winning_timestamp": earliest_proposal.created_at.isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Timestamp-based resolution failed: {e}")
            raise
    
    async def _resolve_by_authority(
        self,
        conflict: Conflict,
        proposals: List[ResolutionProposal]
    ) -> ResolutionResult:
        """Resolve conflict by deferring to designated authority."""
        try:
            # Find authority for this conflict type
            authority_agent = self.authorities.get(conflict.conflict_type)
            
            if not authority_agent:
                raise ValueError(f"No authority defined for conflict type: {conflict.conflict_type}")
            
            # Find proposal from authority
            authority_proposal = None
            for proposal in proposals:
                if proposal.proposer == authority_agent:
                    authority_proposal = proposal
                    break
            
            if not authority_proposal:
                raise ValueError(f"No proposal from authority {authority_agent}")
            
            return ResolutionResult(
                conflict_id=conflict.id,
                resolution_proposal_id=authority_proposal.id,
                status="resolved",
                solution=authority_proposal.solution,
                agreement_level=0.8,  # High agreement for authority-based
                metadata={"strategy": "authority_based", "authority": authority_agent}
            )
            
        except Exception as e:
            logger.error(f"Authority-based resolution failed: {e}")
            raise
    
    async def _resolve_by_weighted_average(
        self,
        conflict: Conflict,
        proposals: List[ResolutionProposal]
    ) -> ResolutionResult:
        """Resolve conflict by creating weighted average solution."""
        try:
            if not proposals:
                raise ValueError("No proposals to average")
            
            # Calculate weighted solution
            weighted_solution = {}
            total_weight = 0.0
            
            for proposal in proposals:
                weight = self.agent_weights.get(proposal.proposer, 1.0)
                total_weight += weight
                
                # Combine numerical values
                for key, value in proposal.solution.items():
                    if isinstance(value, (int, float)):
                        if key not in weighted_solution:
                            weighted_solution[key] = 0.0
                        weighted_solution[key] += value * weight
            
            # Normalize by total weight
            if total_weight > 0:
                for key in weighted_solution:
                    weighted_solution[key] /= total_weight
            
            # Add non-numerical values from highest weighted proposal
            best_proposal = max(proposals, key=lambda p: self.agent_weights.get(p.proposer, 1.0))
            for key, value in best_proposal.solution.items():
                if not isinstance(value, (int, float)):
                    weighted_solution[key] = value
            
            return ResolutionResult(
                conflict_id=conflict.id,
                status="resolved",
                solution=weighted_solution,
                agreement_level=0.75,  # Good agreement for weighted average
                metadata={"strategy": "weighted_average", "total_weight": total_weight}
            )
            
        except Exception as e:
            logger.error(f"Weighted average resolution failed: {e}")
            raise
    
    async def _resolve_by_negotiation(
        self,
        conflict: Conflict,
        proposals: List[ResolutionProposal]
    ) -> ResolutionResult:
        """Resolve conflict through multi-round negotiation."""
        try:
            # Simplified negotiation: find compromise between proposals
            if len(proposals) < 2:
                return await self._resolve_by_priority(conflict, proposals)
            
            # For now, implement as weighted average of top 2 proposals
            # In a real implementation, this would involve multiple rounds
            top_proposals = sorted(
                proposals,
                key=lambda p: self.agent_priorities.get(p.proposer, 0),
                reverse=True
            )[:2]
            
            compromise_solution = {}
            
            # Merge solutions
            for key in set().union(*(p.solution.keys() for p in top_proposals)):
                values = [p.solution.get(key) for p in top_proposals if key in p.solution]
                
                if all(isinstance(v, (int, float)) for v in values):
                    # Average numerical values
                    compromise_solution[key] = sum(values) / len(values)
                else:
                    # Take first non-None value for non-numerical
                    compromise_solution[key] = next((v for v in values if v is not None), None)
            
            return ResolutionResult(
                conflict_id=conflict.id,
                status="resolved",
                solution=compromise_solution,
                agreement_level=0.85,  # High agreement for negotiated solution
                metadata={"strategy": "negotiation", "rounds": 1}  # Simplified
            )
            
        except Exception as e:
            logger.error(f"Negotiation-based resolution failed: {e}")
            raise
    
    async def _resolve_by_arbitration(
        self,
        conflict: Conflict,
        proposals: List[ResolutionProposal]
    ) -> ResolutionResult:
        """Resolve conflict through third-party arbitration."""
        try:
            # Find neutral arbitrator (not involved in conflict)
            arbitrator = None
            for agent_id in self.agent_priorities:
                if agent_id not in conflict.participants:
                    arbitrator = agent_id
                    break
            
            if not arbitrator:
                # Fallback to authority-based if no neutral arbitrator
                return await self._resolve_by_authority(conflict, proposals)
            
            # Simplified arbitration: arbitrator chooses based on rationale quality
            best_proposal = max(proposals, key=lambda p: len(p.rationale))
            
            return ResolutionResult(
                conflict_id=conflict.id,
                resolution_proposal_id=best_proposal.id,
                status="resolved",
                solution=best_proposal.solution,
                agreement_level=0.9,  # Very high agreement for arbitrated solution
                metadata={"strategy": "arbitration", "arbitrator": arbitrator}
            )
            
        except Exception as e:
            logger.error(f"Arbitration-based resolution failed: {e}")
            raise
    
    async def _resolve_by_consensus_building(
        self,
        conflict: Conflict,
        proposals: List[ResolutionProposal]
    ) -> ResolutionResult:
        """Resolve conflict by building consensus among participants."""
        try:
            # Simplified consensus building: find most acceptable proposal
            proposal_scores = {}
            
            for proposal in proposals:
                score = 0.0
                
                # Score based on various factors
                
                # 1. Rationale quality (longer = better)
                score += min(len(proposal.rationale) / 100, 1.0)
                
                # 2. Lower implementation complexity is better
                score += (5 - proposal.implementation_complexity) / 5
                
                # 3. Positive cost-benefit ratio
                if proposal.cost_benefit:
                    benefits = sum(v for k, v in proposal.cost_benefit.items() if "benefit" in k.lower())
                    costs = sum(abs(v) for k, v in proposal.cost_benefit.items() if "cost" in k.lower())
                    if costs > 0:
                        score += min(benefits / costs, 2.0)
                    else:
                        score += benefits
                
                # 4. Fewer affected parties is sometimes better
                score += max(0, 1 - len(proposal.affected_parties) / len(conflict.participants))
                
                proposal_scores[proposal.id] = score
            
            # Choose highest scoring proposal
            best_proposal_id = max(proposal_scores, key=proposal_scores.get)
            best_proposal = next(p for p in proposals if p.id == best_proposal_id)
            
            # Calculate agreement level based on score distribution
            scores = list(proposal_scores.values())
            max_score = max(scores)
            avg_score = sum(scores) / len(scores)
            agreement_level = min(1.0, max_score / max(avg_score, 0.1))
            
            return ResolutionResult(
                conflict_id=conflict.id,
                resolution_proposal_id=best_proposal.id,
                status="resolved",
                solution=best_proposal.solution,
                agreement_level=agreement_level,
                metadata={
                    "strategy": "consensus_building",
                    "proposal_scores": proposal_scores,
                    "winning_score": max_score
                }
            )
            
        except Exception as e:
            logger.error(f"Consensus building resolution failed: {e}")
            raise
    
    async def _complete_resolution(self, conflict_id: str, result: ResolutionResult):
        """Complete a conflict resolution process."""
        try:
            # Store result
            self.completed_resolutions[conflict_id] = result
            
            # Remove from active conflicts
            if conflict_id in self.conflicts:
                conflict = self.conflicts[conflict_id]
                execution_time = (result.resolved_at - conflict.created_at).total_seconds()
                
                # Update metrics
                if result.status == "resolved":
                    self.metrics["conflicts_resolved"] += 1
                elif result.status == "escalated":
                    self.metrics["conflicts_escalated"] += 1
                
                # Update average resolution time
                total_resolved = self.metrics["conflicts_resolved"] + self.metrics["conflicts_escalated"]
                if total_resolved > 0:
                    current_avg = self.metrics["average_resolution_time"]
                    self.metrics["average_resolution_time"] = (
                        (current_avg * (total_resolved - 1) + execution_time) / total_resolved
                    )
                
                # Update success rate
                total_attempts = (self.metrics["conflicts_resolved"] + 
                                self.metrics["conflicts_escalated"])
                if total_attempts > 0:
                    self.metrics["resolution_success_rate"] = (
                        self.metrics["conflicts_resolved"] / total_attempts
                    )
                
                del self.conflicts[conflict_id]
            
            # Clean up proposals
            if conflict_id in self.resolution_proposals:
                del self.resolution_proposals[conflict_id]
            
            # Trigger callback
            if conflict_id in self.resolution_callbacks:
                try:
                    callback = self.resolution_callbacks[conflict_id]
                    callback_result = callback(result)
                    
                    if asyncio.iscoroutine(callback_result):
                        await callback_result
                        
                    del self.resolution_callbacks[conflict_id]
                    
                except Exception as e:
                    logger.error(f"Resolution callback error: {e}")
            
            logger.info(f"Completed resolution for conflict {conflict_id}")
            
        except Exception as e:
            logger.error(f"Error completing resolution: {e}")
    
    async def set_authority(self, domain: str, agent_id: str):
        """Set an agent as authority for a specific domain."""
        self.authorities[domain] = agent_id
        logger.info(f"Set {agent_id} as authority for domain '{domain}'")
    
    async def set_agent_priority(self, agent_id: str, priority: int):
        """Set priority level for an agent."""
        self.agent_priorities[agent_id] = priority
        logger.info(f"Set priority {priority} for agent {agent_id}")
    
    async def set_agent_weight(self, agent_id: str, weight: float):
        """Set weight for an agent in weighted resolutions."""
        self.agent_weights[agent_id] = weight
        logger.info(f"Set weight {weight} for agent {agent_id}")
    
    async def get_conflict_status(self, conflict_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a conflict."""
        if conflict_id in self.conflicts:
            conflict = self.conflicts[conflict_id]
            proposals = self.resolution_proposals.get(conflict_id, [])
            
            return {
                "conflict_id": conflict_id,
                "title": conflict.title,
                "status": "active",
                "participants": list(conflict.participants),
                "conflict_type": conflict.conflict_type,
                "severity": conflict.severity,
                "proposal_count": len(proposals),
                "created_at": conflict.created_at.isoformat()
            }
        
        elif conflict_id in self.completed_resolutions:
            result = self.completed_resolutions[conflict_id]
            return {
                "conflict_id": conflict_id,
                "status": result.status,
                "agreement_level": result.agreement_level,
                "dissenting_parties": list(result.dissenting_parties),
                "resolved_at": result.resolved_at.isoformat()
            }
        
        return None
    
    async def _monitor_conflicts(self):
        """Monitor active conflicts for escalation needs."""
        try:
            while self.is_running:
                await asyncio.sleep(60)  # Check every minute
                
                try:
                    # Check for conflicts that need escalation
                    current_time = datetime.utcnow()
                    
                    for conflict_id, conflict in list(self.conflicts.items()):
                        # Escalate high-severity conflicts after 1 hour
                        if conflict.severity >= 4:
                            age = (current_time - conflict.created_at).total_seconds()
                            if age > 3600:  # 1 hour
                                await self._escalate_conflict(conflict_id)
                        
                        # Escalate any conflict after 4 hours
                        elif (current_time - conflict.created_at).total_seconds() > 14400:
                            await self._escalate_conflict(conflict_id)
                            
                except Exception as e:
                    logger.error(f"Conflict monitoring error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Conflict monitor loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Conflict monitor loop error: {e}")
    
    async def _escalate_conflict(self, conflict_id: str):
        """Escalate a conflict that couldn't be resolved."""
        try:
            if conflict_id not in self.conflicts:
                return
            
            conflict = self.conflicts[conflict_id]
            
            # Create escalated result
            result = ResolutionResult(
                conflict_id=conflict_id,
                status="escalated",
                metadata={
                    "reason": "timeout",
                    "original_severity": conflict.severity,
                    "escalated_at": datetime.utcnow().isoformat()
                }
            )
            
            await self._complete_resolution(conflict_id, result)
            
            logger.warning(f"Escalated unresolved conflict {conflict_id}")
            
        except Exception as e:
            logger.error(f"Failed to escalate conflict {conflict_id}: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get conflict resolver metrics."""
        return {
            **self.metrics,
            "active_conflicts": len(self.conflicts),
            "completed_resolutions": len(self.completed_resolutions),
            "registered_authorities": len(self.authorities)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            return {
                "status": "healthy" if self.is_running else "stopped",
                "is_running": self.is_running,
                "active_conflicts": len(self.conflicts),
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}