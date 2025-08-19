#!/usr/bin/env python3
"""Simple database test for v0.8.2"""

import asyncio
import sqlite3
from pathlib import Path

async def simple_test():
    """Simple test to verify database integration works"""
    
    print("🧪 Testing MAOS v0.8.2 Database Integration")
    print("=" * 50)
    
    from src.maos.interfaces.sqlite_persistence import SqlitePersistence
    
    # Use the actual maos.db
    db_path = Path("./maos.db")
    
    persistence = SqlitePersistence(str(db_path))
    await persistence.initialize()
    
    # Test saving all entity types
    import uuid
    test_id = str(uuid.uuid4())[:8]
    
    print("\n1️⃣ Creating orchestration...")
    orch_id = f"test-orch-{test_id}"
    await persistence.save_orchestration(
        orchestration_id=orch_id,
        request="Test orchestration for v0.8.2",
        agents=[f"agent1-{test_id}", f"agent2-{test_id}"],
        batches=[[f"agent1-{test_id}"], [f"agent2-{test_id}"]],
        status="running"
    )
    
    print("2️⃣ Creating agents...")
    agent_id = f"test-agent-{test_id}"
    await persistence.create_agent(
        agent_id=agent_id,
        name=f"Test Agent {test_id}",
        agent_type="tester",
        capabilities=["testing"],
        metadata={"test": True}
    )
    
    print("3️⃣ Creating session...")
    session_id = f"test-session-{test_id}"
    await persistence.create_session(
        session_id=session_id,
        agent_id=agent_id,
        task="Test task for v0.8.2"
    )
    
    print("4️⃣ Creating task...")
    task_id = f"test-task-{test_id}"
    await persistence.create_task(
        task_id=task_id,
        description="Test task for database integration",
        assigned_agents=[agent_id]
    )
    
    print("5️⃣ Creating message...")
    msg_id = await persistence.save_message(
        from_agent=agent_id,
        to_agent=None,  # Broadcast
        message="Test message for v0.8.2",
        message_type="test"
    )
    
    print("6️⃣ Updating orchestration...")
    await persistence.update_orchestration(
        orchestration_id=orch_id,
        total_cost=0.01,
        total_duration_ms=100,
        successful_agents=1,
        total_agents=1,
        status="completed"
    )
    
    await persistence.close()
    
    # Verify with raw SQL
    print("\n🔍 Verifying database contents...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    tables = ['orchestrations', 'agents', 'sessions', 'tasks', 'messages']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  • {table}: {count} records")
    
    # Check our specific test data
    cursor.execute("SELECT id, status FROM orchestrations WHERE id = ?", (orch_id,))
    orch = cursor.fetchone()
    if orch:
        print(f"\n✅ Test orchestration found: {orch[0]} ({orch[1]})")
    else:
        print(f"\n❌ Test orchestration NOT found!")
    
    conn.close()
    
    print("\n✅ Database integration test complete!")

if __name__ == "__main__":
    asyncio.run(simple_test())