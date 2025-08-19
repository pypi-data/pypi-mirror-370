#!/usr/bin/env python3
"""Test FULL orchestrator and see if it writes to database"""

import asyncio
from pathlib import Path
import sqlite3

async def test_full():
    """Test the complete orchestrator flow"""
    
    print("🔥 Testing FULL Orchestrator v0.8.3")
    print("=" * 60)
    
    # Count records before
    conn = sqlite3.connect("./maos.db")
    cursor = conn.cursor()
    
    before = {}
    for table in ['orchestrations', 'agents', 'sessions', 'tasks', 'messages']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        before[table] = cursor.fetchone()[0]
    
    print("\n📊 Database BEFORE:")
    for table, count in before.items():
        print(f"   {table}: {count}")
    
    conn.close()
    
    # Run orchestrator
    print("\n🚀 Running orchestrator...")
    
    from src.maos.interfaces.sqlite_persistence import SqlitePersistence
    from src.maos.core.orchestrator_v7 import OrchestratorV7
    
    persistence = SqlitePersistence("./maos.db")
    await persistence.initialize()
    
    orchestrator = OrchestratorV7(persistence, api_key=None)
    
    try:
        # Run with auto-approve to skip prompts
        result = await orchestrator.orchestrate(
            request="analyze this project and write tests",
            auto_approve=True
        )
        
        print(f"\n✅ Orchestration completed!")
        print(f"   ID: {result.orchestration_id[:8]}")
        print(f"   Success: {result.success}")
        print(f"   Agents: {len(result.agents_created)}")
        
    except Exception as e:
        print(f"\n❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
    
    await persistence.close()
    
    # Count records after
    conn = sqlite3.connect("./maos.db")
    cursor = conn.cursor()
    
    after = {}
    for table in ['orchestrations', 'agents', 'sessions', 'tasks', 'messages']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        after[table] = cursor.fetchone()[0]
    
    print("\n📊 Database AFTER:")
    for table, count in after.items():
        diff = count - before[table]
        symbol = "✅" if diff > 0 else "❌"
        print(f"   {symbol} {table}: {count} (+{diff})")
    
    # Check if orchestration was saved
    cursor.execute("SELECT id, status, total_agents FROM orchestrations ORDER BY created_at DESC LIMIT 1")
    orch = cursor.fetchone()
    if orch:
        print(f"\n🎯 Latest orchestration:")
        print(f"   ID: {orch[0]}")
        print(f"   Status: {orch[1]}")
        print(f"   Agents: {orch[2]}")
    
    conn.close()
    
    # Final verdict
    new_records = sum(after[t] - before[t] for t in after)
    if new_records > 0:
        print(f"\n✅ SUCCESS! {new_records} new records created")
    else:
        print(f"\n❌ FAILURE! NO new records created")

asyncio.run(test_full())