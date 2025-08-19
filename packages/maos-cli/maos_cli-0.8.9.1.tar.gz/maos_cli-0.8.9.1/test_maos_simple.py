#!/usr/bin/env python3
"""Simple test for MAOS functionality"""

import sys
import os
sys.path.insert(0, 'src')

from maos.core.orchestrator import Orchestrator
from maos.models.agent import Agent, AgentCapability

def test_basic_functionality():
    """Test basic MAOS components"""
    
    print("Testing MAOS basic functionality...")
    
    # Test 1: Create orchestrator
    print("\n1. Creating orchestrator...")
    orchestrator = Orchestrator()
    print("✓ Orchestrator created")
    
    # Test 2: Create a simple agent
    print("\n2. Creating simple agent...")
    agent = Agent(
        name="test-agent",
        capabilities=[AgentCapability.CODE_GENERATION],
        description="A test agent"
    )
    print(f"✓ Agent created: {agent.name}")
    
    # Test 3: Register agent
    print("\n3. Registering agent with orchestrator...")
    orchestrator.agent_manager.register_agent(agent)
    print("✓ Agent registered")
    
    # Test 4: List agents
    print("\n4. Listing agents...")
    agents = orchestrator.agent_manager.list_agents()
    print(f"✓ Found {len(agents)} agent(s)")
    for a in agents:
        print(f"  - {a['name']}: {a['status']}")
    
    # Test 5: Check orchestrator status
    print("\n5. Getting orchestrator status...")
    status = orchestrator.get_status()
    print(f"✓ Orchestrator status: {status.get('orchestrator_status', 'Unknown')}")
    print(f"  Active agents: {status.get('active_agents', 0)}")
    
    print("\n✅ All basic tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)