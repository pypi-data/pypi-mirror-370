#!/usr/bin/env python3
"""
Quick test to verify MAOS components work.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from maos.core.orchestrator import Orchestrator
        print("✓ Orchestrator imported")
        
        from maos.core.agent_manager import AgentManager
        print("✓ AgentManager imported")
        
        from maos.models.agent import Agent, AgentStatus
        print("✓ Agent models imported")
        
        from maos.interfaces.sqlite_persistence import SqlitePersistence
        print("✓ SqlitePersistence imported")
        
        from maos.cli.main import app
        print("✓ CLI app imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_creation():
    """Test basic object creation."""
    print("\nTesting object creation...")
    
    try:
        from maos.core.agent_manager import AgentManager
        from maos.models.agent import Agent
        
        # Create agent manager
        manager = AgentManager()
        print("✓ AgentManager created")
        
        # Create agent
        agent = Agent(name="TestAgent", type="worker")
        print(f"✓ Agent created: {agent.name}")
        
        return True
    except Exception as e:
        print(f"✗ Creation failed: {e}")
        return False


def main():
    """Run quick tests."""
    print("=" * 40)
    print("MAOS Quick Test")
    print("=" * 40)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Basic Creation", test_basic_creation()))
    
    print("\n" + "=" * 40)
    print("Results:")
    print("=" * 40)
    
    all_passed = True
    for name, passed in results:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())