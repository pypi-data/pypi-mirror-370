"""Voting mechanisms for consensus building."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class VoteType(Enum):
    """Types of votes that can be cast."""
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"


class VotingStrategy(Enum):
    """Different voting strategies for decision making."""
    SIMPLE_MAJORITY = "simple_majority"  # > 50%
    ABSOLUTE_MAJORITY = "absolute_majority"  # >= 50%
    SUPER_MAJORITY = "super_majority"  # >= 2/3
    UNANIMOUS = "unanimous"  # 100%
    WEIGHTED = "weighted"  # Vote power based on weights
    RANKED_CHOICE = "ranked_choice"  # Multiple rounds elimination


@dataclass
class Vote:
    """Individual vote in a voting session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    voter_id: str = ""
    vote: VoteType = VoteType.ABSTAIN
    weight: float = 1.0
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Proposal:
    """A proposal that agents vote on."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    proposer: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    voting_strategy: VotingStrategy = VotingStrategy.SIMPLE_MAJORITY
    eligible_voters: Set[str] = field(default_factory=set)
    required_quorum: float = 0.5  # Minimum participation percentage
    timeout: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_expired(self) -> bool:
        """Check if proposal has expired."""
        return datetime.utcnow() > (self.created_at + self.timeout)


@dataclass
class VotingSession:
    """A voting session for a specific proposal."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposal: Proposal = None
    votes: Dict[str, Vote] = field(default_factory=dict)  # voter_id -> vote
    status: str = "active"  # active, completed, expired, cancelled
    result: Optional[str] = None  # passed, failed, no_quorum
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def get_vote_counts(self) -> Dict[VoteType, int]:
        """Get count of votes by type."""
        counts = {vote_type: 0 for vote_type in VoteType}
        for vote in self.votes.values():
            counts[vote.vote] += 1
        return counts
    
    def get_weighted_vote_counts(self) -> Dict[VoteType, float]:
        """Get weighted count of votes by type."""
        counts = {vote_type: 0.0 for vote_type in VoteType}
        for vote in self.votes.values():
            counts[vote.vote] += vote.weight
        return counts
    
    def get_participation_rate(self) -> float:
        """Get the participation rate as a percentage."""
        if not self.proposal.eligible_voters:
            return 0.0
        return len(self.votes) / len(self.proposal.eligible_voters)
    
    def has_quorum(self) -> bool:
        """Check if the session has met the required quorum."""
        return self.get_participation_rate() >= self.proposal.required_quorum


class VotingMechanism:
    """Manages voting sessions and decision making."""
    
    def __init__(self):
        # Active voting sessions
        self.sessions: Dict[str, VotingSession] = {}
        
        # Voting history
        self.completed_sessions: Dict[str, VotingSession] = {}
        
        # Agent weights for weighted voting
        self.agent_weights: Dict[str, float] = {}
        
        # Session callbacks
        self.session_callbacks: Dict[str, callable] = {}
        
        # Cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval = 300  # 5 minutes
        
        # Metrics
        self.metrics = {
            "proposals_created": 0,
            "sessions_completed": 0,
            "total_votes_cast": 0,
            "consensus_reached": 0,
            "consensus_failed": 0
        }
        
        # Status
        self.is_running = False
        
        logger.info("Voting mechanism initialized")
    
    async def start(self):
        """Start the voting mechanism."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Voting mechanism started")
    
    async def stop(self):
        """Stop the voting mechanism."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Voting mechanism stopped")
    
    async def create_proposal(
        self,
        title: str,
        description: str,
        proposer: str,
        eligible_voters: List[str],
        data: Optional[Dict[str, Any]] = None,
        voting_strategy: VotingStrategy = VotingStrategy.SIMPLE_MAJORITY,
        required_quorum: float = 0.5,
        timeout: timedelta = timedelta(minutes=30)
    ) -> str:
        """Create a new proposal for voting."""
        try:
            proposal = Proposal(
                title=title,
                description=description,
                proposer=proposer,
                data=data or {},
                voting_strategy=voting_strategy,
                eligible_voters=set(eligible_voters),
                required_quorum=required_quorum,
                timeout=timeout
            )
            
            # Create voting session
            session = VotingSession(proposal=proposal)
            self.sessions[session.id] = session
            
            self.metrics["proposals_created"] += 1
            
            logger.info(f"Created proposal '{title}' with session {session.id}")
            return session.id
            
        except Exception as e:
            logger.error(f"Failed to create proposal: {e}")
            raise
    
    async def cast_vote(
        self,
        session_id: str,
        voter_id: str,
        vote: VoteType,
        reasoning: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Cast a vote in a voting session."""
        try:
            if session_id not in self.sessions:
                logger.warning(f"Voting session {session_id} not found")
                return False
            
            session = self.sessions[session_id]
            
            # Check session status
            if session.status != "active":
                logger.warning(f"Voting session {session_id} is not active")
                return False
            
            # Check if proposal expired
            if session.proposal.is_expired():
                await self._expire_session(session_id)
                return False
            
            # Check if voter is eligible
            if voter_id not in session.proposal.eligible_voters:
                logger.warning(f"Voter {voter_id} not eligible for session {session_id}")
                return False
            
            # Get voter weight
            weight = self.agent_weights.get(voter_id, 1.0)
            
            # Create vote
            vote_obj = Vote(
                voter_id=voter_id,
                vote=vote,
                weight=weight,
                reasoning=reasoning,
                metadata=metadata or {}
            )
            
            # Store vote (overwrite if voter already voted)
            if voter_id in session.votes:
                logger.info(f"Voter {voter_id} changed vote in session {session_id}")
            
            session.votes[voter_id] = vote_obj
            self.metrics["total_votes_cast"] += 1
            
            logger.info(f"Vote cast by {voter_id} in session {session_id}: {vote.value}")
            
            # Check if we can conclude the session
            await self._check_session_completion(session_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cast vote: {e}")
            return False
    
    async def _check_session_completion(self, session_id: str):
        """Check if a voting session can be completed."""
        try:
            session = self.sessions[session_id]
            
            # Check if all eligible voters have voted
            all_voted = len(session.votes) == len(session.proposal.eligible_voters)
            
            # Check if result can be determined early
            early_decision = await self._can_determine_early_result(session)
            
            if all_voted or early_decision or session.proposal.is_expired():
                await self._complete_session(session_id)
                
        except Exception as e:
            logger.error(f"Error checking session completion: {e}")
    
    async def _can_determine_early_result(self, session: VotingSession) -> bool:
        """Check if result can be determined before all votes are cast."""
        try:
            if not session.has_quorum():
                return False
            
            strategy = session.proposal.voting_strategy
            total_eligible = len(session.proposal.eligible_voters)
            remaining_votes = total_eligible - len(session.votes)
            
            if strategy == VotingStrategy.WEIGHTED:
                return await self._can_determine_weighted_result(session, remaining_votes)
            else:
                return await self._can_determine_unweighted_result(session, remaining_votes)
                
        except Exception as e:
            logger.error(f"Error determining early result: {e}")
            return False
    
    async def _can_determine_weighted_result(self, session: VotingSession, remaining_votes: int) -> bool:
        """Check if weighted voting result can be determined early."""
        try:
            vote_counts = session.get_weighted_vote_counts()
            
            # Calculate maximum possible weight for remaining votes
            max_remaining_weight = 0.0
            voted_agents = set(session.votes.keys())
            
            for agent_id in session.proposal.eligible_voters:
                if agent_id not in voted_agents:
                    max_remaining_weight += self.agent_weights.get(agent_id, 1.0)
            
            # Check if YES votes can no longer be overcome
            if vote_counts[VoteType.YES] > vote_counts[VoteType.NO] + max_remaining_weight:
                return True
            
            # Check if NO votes can no longer be overcome  
            if vote_counts[VoteType.NO] > vote_counts[VoteType.YES] + max_remaining_weight:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in weighted result determination: {e}")
            return False
    
    async def _can_determine_unweighted_result(self, session: VotingSession, remaining_votes: int) -> bool:
        """Check if unweighted voting result can be determined early."""
        try:
            vote_counts = session.get_vote_counts()
            strategy = session.proposal.voting_strategy
            
            yes_votes = vote_counts[VoteType.YES]
            no_votes = vote_counts[VoteType.NO]
            total_eligible = len(session.proposal.eligible_voters)
            
            if strategy == VotingStrategy.SIMPLE_MAJORITY:
                # Need > 50%
                required = total_eligible // 2 + 1
                
                # Check if YES can reach majority
                if yes_votes >= required:
                    return True
                
                # Check if YES can no longer reach majority
                if yes_votes + remaining_votes < required:
                    return True
            
            elif strategy == VotingStrategy.SUPER_MAJORITY:
                # Need >= 2/3
                required = (total_eligible * 2 + 2) // 3
                
                if yes_votes >= required:
                    return True
                
                if yes_votes + remaining_votes < required:
                    return True
            
            elif strategy == VotingStrategy.UNANIMOUS:
                # Need 100% YES, any NO vote fails
                if no_votes > 0:
                    return True
                
                if yes_votes == total_eligible:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in unweighted result determination: {e}")
            return False
    
    async def _complete_session(self, session_id: str):
        """Complete a voting session and determine result."""
        try:
            session = self.sessions[session_id]
            
            # Determine result
            result = await self._determine_result(session)
            
            # Update session
            session.status = "completed" if result != "expired" else "expired"
            session.result = result
            session.completed_at = datetime.utcnow()
            
            # Move to completed sessions
            self.completed_sessions[session_id] = session
            del self.sessions[session_id]
            
            # Update metrics
            self.metrics["sessions_completed"] += 1
            if result == "passed":
                self.metrics["consensus_reached"] += 1
            elif result == "failed":
                self.metrics["consensus_failed"] += 1
            
            # Trigger callback if registered
            if session_id in self.session_callbacks:
                try:
                    callback = self.session_callbacks[session_id]
                    result_obj = callback(session, result)
                    
                    if asyncio.iscoroutine(result_obj):
                        await result_obj
                        
                    del self.session_callbacks[session_id]
                    
                except Exception as e:
                    logger.error(f"Callback error for session {session_id}: {e}")
            
            logger.info(f"Completed voting session {session_id} with result: {result}")
            
        except Exception as e:
            logger.error(f"Failed to complete session {session_id}: {e}")
    
    async def _determine_result(self, session: VotingSession) -> str:
        """Determine the result of a voting session."""
        try:
            # Check if expired
            if session.proposal.is_expired():
                return "expired"
            
            # Check quorum
            if not session.has_quorum():
                return "no_quorum"
            
            strategy = session.proposal.voting_strategy
            
            if strategy == VotingStrategy.WEIGHTED:
                return await self._determine_weighted_result(session)
            else:
                return await self._determine_unweighted_result(session)
                
        except Exception as e:
            logger.error(f"Error determining result: {e}")
            return "error"
    
    async def _determine_weighted_result(self, session: VotingSession) -> str:
        """Determine result for weighted voting."""
        try:
            vote_counts = session.get_weighted_vote_counts()
            
            yes_weight = vote_counts[VoteType.YES]
            no_weight = vote_counts[VoteType.NO]
            total_weight = yes_weight + no_weight + vote_counts[VoteType.ABSTAIN]
            
            if total_weight == 0:
                return "no_votes"
            
            yes_percentage = yes_weight / total_weight
            
            # Apply strategy thresholds
            strategy = session.proposal.voting_strategy
            
            if strategy == VotingStrategy.SIMPLE_MAJORITY and yes_percentage > 0.5:
                return "passed"
            elif strategy == VotingStrategy.ABSOLUTE_MAJORITY and yes_percentage >= 0.5:
                return "passed"
            elif strategy == VotingStrategy.SUPER_MAJORITY and yes_percentage >= 2/3:
                return "passed"
            elif strategy == VotingStrategy.UNANIMOUS and yes_percentage == 1.0:
                return "passed"
            else:
                return "failed"
                
        except Exception as e:
            logger.error(f"Error in weighted result determination: {e}")
            return "error"
    
    async def _determine_unweighted_result(self, session: VotingSession) -> str:
        """Determine result for unweighted voting."""
        try:
            vote_counts = session.get_vote_counts()
            strategy = session.proposal.voting_strategy
            
            yes_votes = vote_counts[VoteType.YES]
            total_votes = sum(vote_counts.values())
            
            if total_votes == 0:
                return "no_votes"
            
            if strategy == VotingStrategy.SIMPLE_MAJORITY:
                return "passed" if yes_votes > total_votes // 2 else "failed"
            
            elif strategy == VotingStrategy.ABSOLUTE_MAJORITY:
                return "passed" if yes_votes >= total_votes // 2 else "failed"
            
            elif strategy == VotingStrategy.SUPER_MAJORITY:
                required = (total_votes * 2 + 2) // 3
                return "passed" if yes_votes >= required else "failed"
            
            elif strategy == VotingStrategy.UNANIMOUS:
                return "passed" if yes_votes == total_votes else "failed"
            
            else:
                return "failed"
                
        except Exception as e:
            logger.error(f"Error in unweighted result determination: {e}")
            return "error"
    
    async def _expire_session(self, session_id: str):
        """Mark a session as expired."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.status = "expired"
            await self._complete_session(session_id)
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a voting session."""
        # Check active sessions
        if session_id in self.sessions:
            session = self.sessions[session_id]
        elif session_id in self.completed_sessions:
            session = self.completed_sessions[session_id]
        else:
            return None
        
        vote_counts = session.get_vote_counts()
        
        return {
            "session_id": session.id,
            "proposal_title": session.proposal.title,
            "status": session.status,
            "result": session.result,
            "vote_counts": {vt.value: count for vt, count in vote_counts.items()},
            "participation_rate": session.get_participation_rate(),
            "has_quorum": session.has_quorum(),
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "is_expired": session.proposal.is_expired()
        }
    
    async def cancel_session(self, session_id: str) -> bool:
        """Cancel an active voting session."""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session.status = "cancelled"
            session.completed_at = datetime.utcnow()
            
            # Move to completed sessions
            self.completed_sessions[session_id] = session
            del self.sessions[session_id]
            
            # Remove callback
            if session_id in self.session_callbacks:
                del self.session_callbacks[session_id]
            
            logger.info(f"Cancelled voting session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel session {session_id}: {e}")
            return False
    
    async def set_agent_weight(self, agent_id: str, weight: float):
        """Set voting weight for an agent."""
        self.agent_weights[agent_id] = max(0.0, weight)
        logger.info(f"Set voting weight for agent {agent_id}: {weight}")
    
    async def register_session_callback(self, session_id: str, callback: callable):
        """Register a callback for session completion."""
        self.session_callbacks[session_id] = callback
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired sessions."""
        try:
            while self.is_running:
                await asyncio.sleep(self.cleanup_interval)
                
                try:
                    # Check for expired sessions
                    expired_sessions = [
                        session_id for session_id, session in self.sessions.items()
                        if session.proposal.is_expired()
                    ]
                    
                    for session_id in expired_sessions:
                        await self._expire_session(session_id)
                    
                    if expired_sessions:
                        logger.info(f"Expired {len(expired_sessions)} voting sessions")
                        
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Voting cleanup loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Voting cleanup loop error: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get voting mechanism metrics."""
        return {
            **self.metrics,
            "active_sessions": len(self.sessions),
            "completed_sessions": len(self.completed_sessions),
            "registered_agents": len(self.agent_weights)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            active_sessions = len(self.sessions)
            
            return {
                "status": "healthy" if self.is_running else "stopped",
                "active_sessions": active_sessions,
                "is_running": self.is_running,
                "metrics": await self.get_metrics()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}