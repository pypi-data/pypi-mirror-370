#!/usr/bin/env python3
"""
Test just the fallback decomposer functionality.
"""

import asyncio
import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from maos.core.intelligent_decomposer import IntelligentDecomposer
from maos.interfaces.sqlite_persistence import SqlitePersistence


async def test_fallback():
    """Test the fallback decomposer directly."""
    
    print("=" * 60)
    print("TESTING FALLBACK DECOMPOSER")
    print("=" * 60)
    
    # Initialize persistence
    db = SqlitePersistence("test_fallback.db")
    await db.initialize()
    
    # Create decomposer
    decomposer = IntelligentDecomposer(db)
    
    # Test the fallback directly
    test_request = "analyze the calculator.html and tell me what it does and then add a feature so that we can see a screen and we can run functions (basic function like linear regression)"
    
    print(f"\nRequest: {test_request[:60]}...")
    
    # Create a prompt for fallback
    prompt = f"USER REQUEST:\n{test_request}\n"
    
    # Call fallback directly
    result = decomposer._create_fallback_decomposition(prompt)
    
    print(f"\n✅ Fallback decomposition created!")
    print(f"📊 Analysis:")
    print(f"  - User intent: {result.analysis.user_intent}")
    print(f"  - Tasks identified: {len(result.analysis.identified_tasks)}")
    print(f"  - Parallel execution: {result.analysis.requires_parallel}")
    
    print(f"\n📋 Execution Plan:")
    total_agents = 0
    for phase in result.execution_plan:
        print(f"\n  Phase {phase.phase_number} ({'Parallel' if phase.parallel else 'Sequential'}):")
        for task in phase.tasks:
            print(f"    • {task['agent_type']}: {task['description'][:50]}...")
            total_agents += 1
    
    print(f"\n📊 Summary:")
    print(f"  - Total agents: {total_agents}")
    print(f"  - Phases: {len(result.execution_plan)}")
    print(f"  - Reasoning: {result.reasoning}")
    
    if total_agents == 1:
        print("\n⚠️ WARNING: Only 1 agent created!")
    else:
        print(f"\n✅ SUCCESS: Created {total_agents} specialized agents!")
    
    # Clean up
    await db.close()
    os.unlink("test_fallback.db")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_fallback())