#!/usr/bin/env python3
"""Find the REAL problem with maos chat"""

import asyncio
from pathlib import Path

async def test_orchestrate():
    """Test the actual orchestrate method"""
    
    print("Testing MAOS orchestrate (v0.8.3)")
    print("=" * 50)
    
    from src.maos.interfaces.sqlite_persistence import SqlitePersistence
    from src.maos.core.orchestrator_v7 import OrchestratorV7
    
    # Initialize
    persistence = SqlitePersistence("./maos.db")
    await persistence.initialize()
    
    orchestrator = OrchestratorV7(persistence, api_key=None)
    
    print("\n📝 Calling orchestrate with test request...")
    
    try:
        # This is what actually gets called
        result = await orchestrator.orchestrate(
            request="simple test task",
            auto_approve=True  # Skip confirmation
        )
        
        print(f"\n✅ Orchestration completed!")
        print(f"   Success: {result.success}")
        print(f"   Orchestration ID: {result.orchestration_id[:8]}...")
        print(f"   Agents created: {len(result.agents_created)}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Check database
    stats = await persistence.get_statistics()
    print(f"\n📊 Database after orchestration:")
    for table, count in stats.items():
        print(f"   {table}: {count}")
    
    await persistence.close()

if __name__ == "__main__":
    asyncio.run(test_orchestrate())