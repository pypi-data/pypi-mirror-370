#!/usr/bin/env python3
"""Find and fix the hanging issue"""

import asyncio
from pathlib import Path

async def test_decomposer():
    """Test where decomposer hangs"""
    
    print("Testing decomposer...")
    
    from src.maos.interfaces.sqlite_persistence import SqlitePersistence
    from src.maos.core.task_decomposer_v2 import EnhancedTaskDecomposer
    
    persistence = SqlitePersistence("./maos.db")
    await persistence.initialize()
    print("✓ Persistence initialized")
    
    decomposer = EnhancedTaskDecomposer(persistence)
    print("✓ Decomposer created")
    
    # This is where it hangs
    print("Calling decompose...")
    try:
        result = await asyncio.wait_for(
            decomposer.decompose("test task"),
            timeout=2.0
        )
        print(f"✓ Decompose completed: {len(result.subtasks)} subtasks")
    except asyncio.TimeoutError:
        print("✗ HANGS in decompose!")
        
        # Try calling get_active_agents directly
        print("\nTesting get_active_agents directly...")
        try:
            agents = await asyncio.wait_for(
                persistence.get_active_agents(),
                timeout=1.0
            )
            print(f"✓ get_active_agents works: {len(agents)} agents")
        except asyncio.TimeoutError:
            print("✗ get_active_agents HANGS!")
    
    await persistence.close()

asyncio.run(test_decomposer())