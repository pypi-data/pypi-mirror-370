#!/usr/bin/env python3
"""Test with timeout to find where it hangs"""

import asyncio
from pathlib import Path

async def test_orchestrate_timeout():
    """Test orchestrate with timeout"""
    
    print("Testing orchestrate with timeout...")
    
    from src.maos.interfaces.sqlite_persistence import SqlitePersistence
    from src.maos.core.orchestrator_v7 import OrchestratorV7
    
    persistence = SqlitePersistence("./maos.db")
    await persistence.initialize()
    
    orchestrator = OrchestratorV7(persistence, api_key=None)
    
    try:
        result = await asyncio.wait_for(
            orchestrator.orchestrate("simple test", auto_approve=True),
            timeout=5.0
        )
        print(f"✅ Completed: {result.orchestration_id}")
    except asyncio.TimeoutError:
        print("❌ TIMEOUT in orchestrate!")
        
        # It must be hanging in the executor
        print("\nThe problem is likely in ClaudeSDKExecutor")
        print("It's trying to run Claude agents but hanging")
    
    await persistence.close()

asyncio.run(test_orchestrate_timeout())