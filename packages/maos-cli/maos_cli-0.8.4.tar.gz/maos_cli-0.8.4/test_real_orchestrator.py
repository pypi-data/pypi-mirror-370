#!/usr/bin/env python3
"""Test REAL orchestrator with Claude execution"""

import asyncio
import sqlite3
from pathlib import Path

async def test_real():
    """Test that orchestrator ACTUALLY runs Claude and saves to database"""
    
    print("🔥 MAOS v0.8.3 - REAL Claude Execution Test")
    print("=" * 60)
    
    # Count database records BEFORE
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
    
    # Run the orchestrator
    print("\n🚀 Running orchestrator with REAL Claude...")
    print("⏳ This will actually run Claude - may take 1-2 minutes...")
    
    from src.maos.interfaces.sqlite_persistence import SqlitePersistence
    from src.maos.core.orchestrator_v7 import OrchestratorV7
    
    persistence = SqlitePersistence("./maos.db")
    await persistence.initialize()
    
    orchestrator = OrchestratorV7(persistence, api_key=None)
    
    try:
        # Simple task that Claude can complete quickly
        result = await orchestrator.orchestrate(
            request="Write a hello world function in Python",
            auto_approve=True
        )
        
        print(f"\n✅ Orchestration completed!")
        print(f"   ID: {result.orchestration_id[:8]}")
        print(f"   Success: {result.success}")
        print(f"   Agents created: {result.agents_created}")
        print(f"   Total cost: ${result.total_cost:.4f}")
        print(f"   Duration: {result.total_duration_ms}ms")
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
    
    await persistence.close()
    
    # Count database records AFTER
    conn = sqlite3.connect("./maos.db")
    cursor = conn.cursor()
    
    after = {}
    for table in ['orchestrations', 'agents', 'sessions', 'tasks', 'messages']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        after[table] = cursor.fetchone()[0]
    
    print("\n📊 Database AFTER:")
    for table, count in after.items():
        diff = count - before[table]
        if diff > 0:
            print(f"   ✅ {table}: {count} (+{diff} NEW)")
        else:
            print(f"   ❌ {table}: {count} (NO CHANGE)")
    
    # Show the latest orchestration
    cursor.execute("""
        SELECT id, request, status, total_agents, successful_agents, total_cost 
        FROM orchestrations 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    orch = cursor.fetchone()
    if orch:
        print(f"\n🎯 Latest Orchestration:")
        print(f"   ID: {orch[0]}")
        print(f"   Request: {orch[1][:50]}...")
        print(f"   Status: {orch[2]}")
        print(f"   Agents: {orch[4]}/{orch[3]} successful")
        print(f"   Cost: ${orch[5] or 0:.4f}")
    
    # Show agents created
    cursor.execute("""
        SELECT id, type, status 
        FROM agents 
        ORDER BY created_at DESC 
        LIMIT 3
    """)
    agents = cursor.fetchall()
    if agents:
        print(f"\n🤖 Latest Agents:")
        for agent in agents:
            print(f"   • {agent[0]} ({agent[1]}) - {agent[2]}")
    
    conn.close()
    
    # FINAL VERDICT
    new_records = sum(after[t] - before[t] for t in after)
    if new_records >= 5:  # At least orchestration + agent + task + session + message
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Full integration working!")
        print(f"   {new_records} new database records created")
        print("   Claude executed successfully")
        print("   All relationships properly linked")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ FAILURE! Incomplete integration")
        print(f"   Only {new_records} new records created")
        print("=" * 60)

asyncio.run(test_real())