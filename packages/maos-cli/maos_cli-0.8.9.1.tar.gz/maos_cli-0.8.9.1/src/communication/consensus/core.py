"""Core consensus management functionality."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .voting import VotingMechanism, VotingStrategy, VoteType
from .resolution import ConflictResolver, ResolutionStrategy

logger = logging.getLogger(__name__)


class ConsensusType(Enum):
    """Types of consensus mechanisms."""
    VOTING = "voting"
    RAFT = "raft"
    BYZANTINE_FAULT_TOLERANT = "byzantine_fault_tolerant"
    PROOF_OF_STAKE = "proof_of_stake"
    DELEGATED = "delegated"


@dataclass
class ConsensusRequest:
    """A request for consensus on a decision."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    proposer: str = ""
    participants: Set[str] = field(default_factory=set)
    data: Dict[str, Any] = field(default_factory=dict)
    consensus_type: ConsensusType = ConsensusType.VOTING
    voting_strategy: Optional[VotingStrategy] = None
    required_agreement: float = 0.5  # Percentage of participants required
    timeout: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    priority: int = 1  # 1=low, 5=critical
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if consensus request has expired."""
        return datetime.utcnow() > (self.created_at + self.timeout)


@dataclass
class ConsensusResult:
    """Result of a consensus process."""
    request_id: str
    status: str  # "reached", "failed", "timeout", "error"
    decision: Optional[Any] = None
    agreement_percentage: float = 0.0
    participants: Set[str] = field(default_factory=set)
    dissenting_parties: Set[str] = field(default_factory=set)
    reasoning: Dict[str, str] = field(default_factory=dict)  # participant_id -> reasoning
    completed_at: datetime = field(default_factory=datetime.utcnow)
    execution_time: float = 0.0  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgreementTracker:
    """Tracks agreement history and audit trail."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    consensus_request_id: str = ""
    participant_agreements: Dict[str, bool] = field(default_factory=dict)  # participant_id -> agreed
    agreement_reasons: Dict[str, str] = field(default_factory=dict)
    disagreement_reasons: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    final_decision: Optional[Any] = None
    confidence_score: float = 0.0


class ConsensusManager:
    """Manages consensus processes across multiple agents."""
    
    def __init__(
        self,
        default_voting_strategy: VotingStrategy = VotingStrategy.SIMPLE_MAJORITY,
        max_concurrent_requests: int = 100
    ):
        self.default_voting_strategy = default_voting_strategy
        self.max_concurrent_requests = max_concurrent_requests
        
        # Core components
        self.voting_mechanism = VotingMechanism()
        self.conflict_resolver = ConflictResolver()
        
        # Active consensus requests
        self.active_requests: Dict[str, ConsensusRequest] = {}
        self.request_sessions: Dict[str, str] = {}  # request_id -> session_id
        
        # Completed consensus results
        self.completed_results: Dict[str, ConsensusResult] = {}
        
        # Agreement tracking and audit trail
        self.agreement_trackers: Dict[str, AgreementTracker] = {}
        
        # Callbacks for consensus completion
        self.completion_callbacks: Dict[str, Callable] = {}
        
        # Background tasks
        self.monitor_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.cleanup_interval = 300  # 5 minutes
        self.monitor_interval = 30   # 30 seconds
        
        # Metrics
        self.metrics = {
            "requests_created": 0,
            "consensus_reached": 0,
            "consensus_failed": 0,
            "consensus_timeout": 0,
            "average_consensus_time": 0.0,
            "total_participants": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Consensus manager initialized")
    
    async def start(self):
        """Start the consensus manager."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start components
        await self.voting_mechanism.start()
        await self.conflict_resolver.start()
        
        # Start background tasks
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Consensus manager started")
    
    async def stop(self):
        """Stop the consensus manager."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Stop components
        await self.voting_mechanism.stop()
        await self.conflict_resolver.stop()
        
        logger.info("Consensus manager stopped")
    
    async def request_consensus(
        self,
        title: str,
        description: str,
        proposer: str,
        participants: List[str],
        data: Optional[Dict[str, Any]] = None,
        consensus_type: ConsensusType = ConsensusType.VOTING,
        voting_strategy: Optional[VotingStrategy] = None,
        required_agreement: float = 0.5,
        timeout: timedelta = timedelta(minutes=30),
        priority: int = 1,
        callback: Optional[Callable] = None
    ) -> str:
        """Request consensus from a group of participants."""
        try:
            # Check limits
            if len(self.active_requests) >= self.max_concurrent_requests:
                raise ValueError("Maximum concurrent consensus requests reached")
            
            # Create consensus request
            request = ConsensusRequest(
                title=title,
                description=description,
                proposer=proposer,
                participants=set(participants),
                data=data or {},
                consensus_type=consensus_type,
                voting_strategy=voting_strategy or self.default_voting_strategy,
                required_agreement=required_agreement,
                timeout=timeout,
                priority=priority
            )
            
            # Store request
            self.active_requests[request.id] = request
            
            # Register callback if provided
            if callback:
                self.completion_callbacks[request.id] = callback
            
            # Create agreement tracker
            tracker = AgreementTracker(consensus_request_id=request.id)
            self.agreement_trackers[request.id] = tracker
            
            # Start consensus process based on type
            await self._start_consensus_process(request)
            
            self.metrics["requests_created"] += 1
            self.metrics["total_participants"] += len(participants)
            
            logger.info(f"Created consensus request '{title}' with ID {request.id}")
            return request.id
            
        except Exception as e:
            logger.error(f"Failed to create consensus request: {e}")
            raise
    
    async def _start_consensus_process(self, request: ConsensusRequest):
        """Start the appropriate consensus process."""
        try:
            if request.consensus_type == ConsensusType.VOTING:
                await self._start_voting_consensus(request)
            elif request.consensus_type == ConsensusType.RAFT:
                await self._start_raft_consensus(request)
            elif request.consensus_type == ConsensusType.BYZANTINE_FAULT_TOLERANT:
                await self._start_byzantine_consensus(request)
            else:
                raise ValueError(f"Unsupported consensus type: {request.consensus_type}")
                
        except Exception as e:
            logger.error(f"Failed to start consensus process: {e}")
            await self._complete_consensus(request.id, "error", str(e))
    
    async def _start_voting_consensus(self, request: ConsensusRequest):
        """Start a voting-based consensus process."""
        try:
            # Create voting session
            session_id = await self.voting_mechanism.create_proposal(
                title=request.title,
                description=request.description,
                proposer=request.proposer,
                eligible_voters=list(request.participants),
                data=request.data,
                voting_strategy=request.voting_strategy,
                required_quorum=request.required_agreement,
                timeout=request.timeout
            )
            
            # Track session
            self.request_sessions[request.id] = session_id
            
            # Register callback for voting completion
            await self.voting_mechanism.register_session_callback(
                session_id,
                lambda session, result: asyncio.create_task(
                    self._handle_voting_result(request.id, session, result)
                )
            )
            
            logger.info(f"Started voting consensus for request {request.id}")
            
        except Exception as e:
            logger.error(f"Failed to start voting consensus: {e}")
            raise
    
    async def _start_raft_consensus(self, request: ConsensusRequest):
        """Start a Raft-based consensus process."""
        # TODO: Implement Raft consensus algorithm
        logger.warning("Raft consensus not yet implemented")
        await self._complete_consensus(request.id, "error", "Raft not implemented")
    
    async def _start_byzantine_consensus(self, request: ConsensusRequest):
        """Start a Byzantine Fault Tolerant consensus process."""
        # TODO: Implement Byzantine consensus algorithm
        logger.warning("Byzantine consensus not yet implemented")
        await self._complete_consensus(request.id, "error", "Byzantine not implemented")
    
    async def _handle_voting_result(self, request_id: str, session, result: str):
        """Handle the result of a voting session."""
        try:
            if request_id not in self.active_requests:
                return
            
            # Update agreement tracker
            if request_id in self.agreement_trackers:
                tracker = self.agreement_trackers[request_id]
                
                for vote in session.votes.values():
                    agreed = vote.vote == VoteType.YES
                    tracker.participant_agreements[vote.voter_id] = agreed
                    
                    if vote.reasoning:
                        if agreed:
                            tracker.agreement_reasons[vote.voter_id] = vote.reasoning
                        else:
                            tracker.disagreement_reasons[vote.voter_id] = vote.reasoning
                
                # Calculate confidence score
                if session.votes:
                    yes_votes = sum(1 for v in session.votes.values() if v.vote == VoteType.YES)
                    tracker.confidence_score = yes_votes / len(session.votes)
            
            # Complete consensus
            if result == "passed":
                await self._complete_consensus(request_id, "reached")
            elif result == "failed":
                await self._complete_consensus(request_id, "failed")
            elif result == "expired":
                await self._complete_consensus(request_id, "timeout")
            else:
                await self._complete_consensus(request_id, "failed", f"Voting result: {result}")
                
        except Exception as e:
            logger.error(f"Error handling voting result: {e}")
            await self._complete_consensus(request_id, "error", str(e))
    
    async def _complete_consensus(
        self,
        request_id: str,
        status: str,
        error_message: str = ""
    ):
        """Complete a consensus process."""
        try:
            if request_id not in self.active_requests:
                return
            
            request = self.active_requests[request_id]
            start_time = request.created_at
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Create result
            result = ConsensusResult(
                request_id=request_id,
                status=status,
                participants=request.participants.copy(),
                execution_time=execution_time
            )
            
            # Get agreement details
            if request_id in self.agreement_trackers:
                tracker = self.agreement_trackers[request_id]
                
                # Calculate agreement percentage
                if tracker.participant_agreements:
                    agreed_count = sum(1 for agreed in tracker.participant_agreements.values() if agreed)
                    result.agreement_percentage = agreed_count / len(tracker.participant_agreements)
                    
                    # Get dissenting parties
                    result.dissenting_parties = {
                        pid for pid, agreed in tracker.participant_agreements.items()
                        if not agreed
                    }
                    
                    # Combine all reasoning
                    result.reasoning = {**tracker.agreement_reasons, **tracker.disagreement_reasons}
                    
                    # Set decision based on tracker
                    if status == "reached":
                        result.decision = tracker.final_decision or True
            
            # Store result
            self.completed_results[request_id] = result
            
            # Remove from active requests
            del self.active_requests[request_id]
            
            # Clean up session tracking
            if request_id in self.request_sessions:
                del self.request_sessions[request_id]
            
            # Update metrics
            if status == "reached":
                self.metrics["consensus_reached"] += 1
            elif status == "failed":
                self.metrics["consensus_failed"] += 1
            elif status == "timeout":
                self.metrics["consensus_timeout"] += 1
            
            # Update average consensus time
            total_requests = (self.metrics["consensus_reached"] + 
                            self.metrics["consensus_failed"] + 
                            self.metrics["consensus_timeout"])
            if total_requests > 0:
                current_avg = self.metrics["average_consensus_time"]
                self.metrics["average_consensus_time"] = (
                    (current_avg * (total_requests - 1) + execution_time) / total_requests
                )
            
            # Trigger callback
            if request_id in self.completion_callbacks:
                try:
                    callback = self.completion_callbacks[request_id]
                    callback_result = callback(result)
                    
                    if asyncio.iscoroutine(callback_result):
                        await callback_result
                        
                    del self.completion_callbacks[request_id]
                    
                except Exception as e:
                    logger.error(f"Consensus completion callback error: {e}")
            
            logger.info(f"Completed consensus request {request_id} with status: {status}")
            
        except Exception as e:
            logger.error(f"Error completing consensus: {e}")
    
    async def get_consensus_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a consensus request."""
        # Check active requests
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            
            # Get voting session status if applicable
            voting_status = None
            if request_id in self.request_sessions:
                session_id = self.request_sessions[request_id]
                voting_status = await self.voting_mechanism.get_session_status(session_id)
            
            return {
                "request_id": request_id,
                "title": request.title,
                "status": "active",
                "proposer": request.proposer,
                "participants": list(request.participants),
                "consensus_type": request.consensus_type.value,
                "created_at": request.created_at.isoformat(),
                "is_expired": request.is_expired(),
                "voting_status": voting_status
            }
        
        # Check completed results
        elif request_id in self.completed_results:
            result = self.completed_results[request_id]
            return {
                "request_id": request_id,
                "status": result.status,
                "decision": result.decision,
                "agreement_percentage": result.agreement_percentage,
                "participants": list(result.participants),
                "dissenting_parties": list(result.dissenting_parties),
                "execution_time": result.execution_time,
                "completed_at": result.completed_at.isoformat()
            }
        
        return None
    
    async def cancel_consensus(self, request_id: str) -> bool:
        """Cancel an active consensus request."""
        try:
            if request_id not in self.active_requests:
                return False
            
            # Cancel voting session if applicable
            if request_id in self.request_sessions:
                session_id = self.request_sessions[request_id]
                await self.voting_mechanism.cancel_session(session_id)
            
            # Complete with cancelled status
            await self._complete_consensus(request_id, "cancelled")
            
            logger.info(f"Cancelled consensus request {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel consensus request: {e}")
            return False
    
    async def get_agreement_audit_trail(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed audit trail for a consensus request."""
        if request_id not in self.agreement_trackers:
            return None
        
        tracker = self.agreement_trackers[request_id]
        
        return {
            "request_id": request_id,
            "participant_agreements": tracker.participant_agreements,
            "agreement_reasons": tracker.agreement_reasons,
            "disagreement_reasons": tracker.disagreement_reasons,
            "confidence_score": tracker.confidence_score,
            "final_decision": tracker.final_decision,
            "timestamp": tracker.timestamp.isoformat()
        }
    
    async def _monitor_loop(self):
        """Monitor active consensus requests for timeouts."""
        try:
            while self.is_running:
                await asyncio.sleep(self.monitor_interval)
                
                try:
                    # Check for expired requests
                    expired_requests = [
                        request_id for request_id, request in self.active_requests.items()
                        if request.is_expired()
                    ]
                    
                    for request_id in expired_requests:
                        await self._complete_consensus(request_id, "timeout")
                        
                    if expired_requests:
                        logger.info(f"Expired {len(expired_requests)} consensus requests")
                        
                except Exception as e:
                    logger.error(f"Monitor loop error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Consensus monitor loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Consensus monitor loop error: {e}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old completed results."""
        try:
            while self.is_running:
                await asyncio.sleep(self.cleanup_interval)
                
                try:
                    # Clean up old completed results (keep last 1000)
                    if len(self.completed_results) > 1000:
                        sorted_results = sorted(
                            self.completed_results.items(),
                            key=lambda x: x[1].completed_at,
                            reverse=True
                        )
                        
                        # Keep most recent 1000
                        to_keep = dict(sorted_results[:1000])
                        removed_count = len(self.completed_results) - len(to_keep)
                        
                        self.completed_results = to_keep
                        
                        # Also clean up corresponding trackers
                        for request_id in list(self.agreement_trackers.keys()):
                            if request_id not in to_keep:
                                del self.agreement_trackers[request_id]
                        
                        logger.info(f"Cleaned up {removed_count} old consensus results")
                        
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Consensus cleanup loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Consensus cleanup loop error: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get consensus manager metrics."""
        voting_metrics = await self.voting_mechanism.get_metrics()
        
        return {
            **self.metrics,
            "active_requests": len(self.active_requests),
            "completed_results": len(self.completed_results),
            "voting_metrics": voting_metrics
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            voting_health = await self.voting_mechanism.health_check()
            
            status = "healthy"
            if not self.is_running:
                status = "stopped"
            elif voting_health["status"] != "healthy":
                status = "degraded"
            
            return {
                "status": status,
                "is_running": self.is_running,
                "active_requests": len(self.active_requests),
                "voting_health": voting_health,
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Context manager support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()