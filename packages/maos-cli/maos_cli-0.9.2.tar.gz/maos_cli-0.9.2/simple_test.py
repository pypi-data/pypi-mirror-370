#!/usr/bin/env python3
"""Simple test to check orchestration and database."""

import asyncio
import os
import sys
sys.path.insert(0, 'src')

from maos.core.orchestrator_v7 import OrchestratorV7
from maos.interfaces.sqlite_persistence import SqlitePersistence

async def simple_test():
    print("🧪 SIMPLE ORCHESTRATION TEST")
    
    # Clean database
    if os.path.exists("test.db"):
        os.remove("test.db")
    
    # Initialize
    persistence = SqlitePersistence("test.db")
    await persistence.initialize()
    print("✅ Database initialized")
    
    orchestrator = OrchestratorV7(persistence, api_key="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")
    print("✅ Orchestrator initialized")
    
    try:
        print("🚀 Starting orchestration...")
        result = await orchestrator.orchestrate("explain this test", auto_approve=True)
        print(f"✅ Orchestration completed: {result.orchestration_id[:8]}")
        
        # Check database
        import sqlite3
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM agents")
        agents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM checkpoints") 
        checkpoints = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"💾 Database: {agents} agents, {checkpoints} checkpoints")
        
        if agents > 0 or checkpoints > 0:
            print("✅ DATABASE INTEGRATION WORKING!")
            return True
        else:
            print("❌ DATABASE NOT SAVING DATA!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(simple_test())
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")