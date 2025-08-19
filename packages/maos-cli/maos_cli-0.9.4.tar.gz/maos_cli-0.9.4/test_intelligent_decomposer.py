#!/usr/bin/env python3
"""
Test the fixed intelligent decomposer with multi-agent creation.
"""

import asyncio
import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from maos.core.intelligent_decomposer import IntelligentDecomposer
from maos.interfaces.sqlite_persistence import SqlitePersistence


async def test_decomposer():
    """Test the intelligent decomposer with various requests."""
    
    print("=" * 60)
    print("TESTING INTELLIGENT TASK DECOMPOSER")
    print("=" * 60)
    
    # Initialize persistence
    db = SqlitePersistence("test_decomposer.db")
    await db.initialize()
    
    # Create decomposer
    decomposer = IntelligentDecomposer(db)
    
    # Test requests
    test_requests = [
        "analyze the calculator.html and tell me what it does and then add a feature so that we can see a screen and we can run functions (basic function like linear regression)",
        "build a web application with user authentication and database",
        "analyze the codebase and fix all security vulnerabilities",
        "create comprehensive tests for the entire project"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {request[:60]}...")
        print("="*60)
        
        try:
            # Decompose the task
            task_plan, decomposition = await decomposer.decompose(request, show_prompt=False)
            
            print(f"\n✅ Decomposition successful!")
            print(f"📊 Analysis:")
            print(f"  - User intent: {decomposition.analysis.user_intent}")
            print(f"  - Complexity: {decomposition.analysis.complexity}")
            print(f"  - Tasks identified: {len(decomposition.analysis.identified_tasks)}")
            print(f"  - Parallel execution: {decomposition.analysis.requires_parallel}")
            
            print(f"\n📋 Execution Plan:")
            total_agents = 0
            for phase in decomposition.execution_plan:
                print(f"\n  Phase {phase.phase_number} ({'Parallel' if phase.parallel else 'Sequential'}):")
                for task in phase.tasks:
                    print(f"    • {task['agent_type']}: {task['description'][:50]}...")
                    total_agents += 1
            
            print(f"\n📊 Summary:")
            print(f"  - Total agents: {total_agents}")
            print(f"  - Phases: {len(decomposition.execution_plan)}")
            print(f"  - Reasoning: {decomposition.reasoning[:100]}...")
            
            if total_agents == 1:
                print("\n⚠️ WARNING: Only 1 agent created - decomposer may have fallen back!")
            else:
                print(f"\n✅ SUCCESS: Created {total_agents} specialized agents!")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Clean up
    await db.close()
    os.unlink("test_decomposer.db")
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_decomposer())