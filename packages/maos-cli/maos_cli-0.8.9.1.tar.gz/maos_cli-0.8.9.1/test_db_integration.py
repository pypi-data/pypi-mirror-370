#!/usr/bin/env python3
"""Test database integration for MAOS v0.8.1"""

import asyncio
import sqlite3
from pathlib import Path

async def test_database():
    """Test that all database operations work correctly"""
    
    # Test database path
    db_path = Path("./maos.db")
    
    print(f"🔍 Testing database at: {db_path}")
    print(f"   Database exists: {db_path.exists()}")
    print(f"   Database size: {db_path.stat().st_size if db_path.exists() else 0} bytes")
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\n📋 Tables in database:")
    for table in tables:
        print(f"   • {table[0]}")
    
    # Check orchestrations table specifically
    if 'orchestrations' in [t[0] for t in tables]:
        print(f"\n✅ Orchestrations table EXISTS!")
        
        # Check orchestrations
        cursor.execute("SELECT COUNT(*) FROM orchestrations")
        orch_count = cursor.fetchone()[0]
        print(f"   Orchestrations: {orch_count}")
        
        if orch_count > 0:
            cursor.execute("SELECT id, request, status, created_at FROM orchestrations ORDER BY created_at DESC LIMIT 5")
            rows = cursor.fetchall()
            print("\n📊 Recent orchestrations:")
            for row in rows:
                print(f"   • {row[0][:8]}... | {row[2]} | {row[1][:50]}...")
    else:
        print(f"\n❌ Orchestrations table MISSING!")
    
    # Check data in each table
    print(f"\n📊 Record counts:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   • {table[0]}: {count} records")
    
    # Show recent agents
    cursor.execute("SELECT id, type, created_at FROM agents ORDER BY created_at DESC LIMIT 5")
    agents = cursor.fetchall()
    if agents:
        print(f"\n🤖 Recent agents:")
        for agent in agents:
            print(f"   • {agent[0]} ({agent[1]}) - {agent[2]}")
    
    conn.close()
    
    # Now test async operations
    print("\n🔄 Testing async persistence operations...")
    from src.maos.interfaces.sqlite_persistence import SqlitePersistence
    
    persistence = SqlitePersistence(str(db_path))
    await persistence.initialize()
    
    # Test saving an orchestration
    import uuid
    test_orch_id = str(uuid.uuid4())
    print(f"\n💾 Saving test orchestration {test_orch_id[:8]}...")
    
    await persistence.save_orchestration(
        orchestration_id=test_orch_id,
        request="Test orchestration for v0.8.1",
        agents=["test-agent-1", "test-agent-2"],
        batches=[["test-agent-1"], ["test-agent-2"]],
        status="running"
    )
    
    # Update it
    print(f"📝 Updating orchestration...")
    await persistence.update_orchestration(
        orchestration_id=test_orch_id,
        total_cost=0.05,
        total_duration_ms=1500,
        successful_agents=2,
        total_agents=2,
        status="completed",
        summary="Test completed successfully"
    )
    
    # Load it back
    print(f"📖 Loading orchestration back...")
    loaded = await persistence.get_orchestration(test_orch_id)
    if loaded:
        print(f"   ✅ Loaded successfully!")
        print(f"   • ID: {loaded['id'][:8]}...")
        print(f"   • Status: {loaded['status']}")
        print(f"   • Cost: ${loaded['total_cost']}")
        print(f"   • Agents: {loaded['agents']}")
    else:
        print(f"   ❌ Failed to load!")
    
    # List all orchestrations
    all_orchs = await persistence.list_orchestrations()
    print(f"\n📋 Total orchestrations in database: {len(all_orchs)}")
    
    await persistence.close()
    
    print("\n✅ Database integration test complete!")

if __name__ == "__main__":
    asyncio.run(test_database())