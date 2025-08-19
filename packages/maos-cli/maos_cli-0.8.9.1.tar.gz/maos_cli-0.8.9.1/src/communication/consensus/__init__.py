"""Consensus management for MAOS communication layer."""

from .core import ConsensusManager
from .voting import VotingMechanism, VoteType, VotingStrategy
from .protocols import RaftConsensus, ByzantineFaultTolerant
from .resolution import ConflictResolver, ResolutionStrategy

__all__ = [
    "ConsensusManager",
    "VotingMechanism",
    "VoteType", 
    "VotingStrategy",
    "RaftConsensus",
    "ByzantineFaultTolerant",
    "ConflictResolver",
    "ResolutionStrategy"
]