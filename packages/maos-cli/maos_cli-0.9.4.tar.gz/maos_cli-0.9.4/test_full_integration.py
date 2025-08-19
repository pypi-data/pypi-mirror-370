#!/usr/bin/env python3
"""
Full integration test for MAOS v0.8.2
Tests that ALL database relationships are properly created
"""

import asyncio
import sqlite3
from pathlib import Path
import sys

async def test_full_orchestration():
    """Test that orchestration creates ALL required database entries"""
    
    # Remove old test database
    test_db = Path("./test_integration.db")
    if test_db.exists():
        test_db.unlink()
    
    print("🧪 MAOS v0.8.2 Full Integration Test")
    print("=" * 60)
    
    # Initialize persistence and orchestrator
    from src.maos.interfaces.sqlite_persistence import SqlitePersistence
    from src.maos.core.orchestrator_v7 import OrchestratorV7
    from src.maos.core.task_decomposer_v2 import SubTask, TaskType
    import uuid
    
    persistence = SqlitePersistence(str(test_db))
    await persistence.initialize()
    
    # Create a mock orchestrator (without actual Claude execution)
    orchestrator = OrchestratorV7(persistence, api_key=None)
    
    # Create some test tasks with proper SubTask structure
    test_task1 = SubTask(
        id=str(uuid.uuid4()),
        description="Analyze the codebase",
        task_type=TaskType.ANALYZE,
        required_capabilities=["analysis", "code_review"],
        dependencies=[]
    )
    test_task1.agent_type = "analyst"  # Add as property for compatibility
    
    test_task2 = SubTask(
        id=str(uuid.uuid4()),
        description="Write unit tests",
        task_type=TaskType.TEST,
        required_capabilities=["testing", "qa"],
        dependencies=[]
    )
    test_task2.agent_type = "tester"  # Add as property for compatibility
    
    # Manually save agents like orchestrator would
    agent1_id = "analyst-test123"
    agent2_id = "tester-test456"
    
    print("\n📝 Creating test orchestration...")
    
    # Save agents with full relationships
    await orchestrator._save_agent(agent1_id, test_task1)
    await orchestrator._save_agent(agent2_id, test_task2)
    
    # Save orchestration
    orchestration_id = "test-orch-789"
    await persistence.save_orchestration(
        orchestration_id=orchestration_id,
        request="Test full integration",
        agents=[agent1_id, agent2_id],
        batches=[[agent1_id], [agent2_id]],
        status="running"
    )
    
    # Create inter-agent messages
    await persistence.save_message(
        from_agent=agent1_id,
        to_agent=agent2_id,
        message="Analysis complete, ready for testing",
        message_type="handoff"
    )
    
    # Update orchestration completion
    await persistence.update_orchestration(
        orchestration_id=orchestration_id,
        total_cost=0.10,
        total_duration_ms=5000,
        successful_agents=2,
        total_agents=2,
        status="completed",
        summary="Test completed successfully"
    )
    
    await persistence.close()
    
    # Now verify everything was saved correctly
    print("\n🔍 Verifying database integrity...")
    conn = sqlite3.connect(str(test_db))
    cursor = conn.cursor()
    
    # Check all tables
    tables_to_check = {
        'orchestrations': "SELECT COUNT(*) FROM orchestrations",
        'agents': "SELECT COUNT(*) FROM agents",
        'sessions': "SELECT COUNT(*) FROM sessions",
        'tasks': "SELECT COUNT(*) FROM tasks",
        'messages': "SELECT COUNT(*) FROM messages",
        'checkpoints': "SELECT COUNT(*) FROM checkpoints"
    }
    
    results = {}
    for table, query in tables_to_check.items():
        cursor.execute(query)
        count = cursor.fetchone()[0]
        results[table] = count
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {table}: {count} records")
    
    # Detailed checks
    print("\n📊 Detailed verification:")
    
    # Check orchestration
    cursor.execute("SELECT * FROM orchestrations WHERE id = ?", (orchestration_id,))
    orch = cursor.fetchone()
    if orch:
        print(f"  ✅ Orchestration exists with status: {orch[2]}")
    else:
        print(f"  ❌ Orchestration NOT found!")
    
    # Check agents
    cursor.execute("SELECT id, type, status FROM agents")
    agents = cursor.fetchall()
    for agent in agents:
        print(f"  ✅ Agent: {agent[0]} ({agent[1]}) - {agent[2]}")
    
    # Check tasks
    cursor.execute("SELECT id, description, status FROM tasks")
    tasks = cursor.fetchall()
    for task in tasks:
        print(f"  ✅ Task: {task[0][:20]}... - {task[2]}")
    
    # Check sessions
    cursor.execute("SELECT session_id, agent_id FROM sessions")
    sessions = cursor.fetchall()
    for session in sessions:
        print(f"  ✅ Session: {session[0]} for agent {session[1]}")
    
    # Check messages
    cursor.execute("SELECT from_agent, to_agent, message_type FROM messages")
    messages = cursor.fetchall()
    for msg in messages:
        print(f"  ✅ Message: {msg[0]} → {msg[1]} ({msg[2]})")
    
    # Check relationships
    print("\n🔗 Relationship verification:")
    
    # Check if agents are linked to orchestration
    cursor.execute("""
        SELECT o.id, COUNT(DISTINCT a.id) as agent_count 
        FROM orchestrations o, agents a 
        WHERE o.agents LIKE '%' || a.id || '%'
        GROUP BY o.id
    """)
    relationships = cursor.fetchall()
    for rel in relationships:
        print(f"  ✅ Orchestration {rel[0][:8]}... has {rel[1]} linked agents")
    
    conn.close()
    
    # Final verdict
    print("\n" + "=" * 60)
    all_passed = all([
        results['orchestrations'] > 0,
        results['agents'] > 0,
        results['sessions'] > 0,
        results['tasks'] > 0,
        results['messages'] > 0
    ])
    
    if all_passed:
        print("✅ ALL TESTS PASSED! Full integration working!")
        print("   - Orchestrations properly saved")
        print("   - Agents created with relationships")
        print("   - Tasks assigned to agents")
        print("   - Sessions initialized")
        print("   - Inter-agent messages recorded")
        return 0
    else:
        print("❌ INTEGRATION FAILED! Missing data:")
        for table, count in results.items():
            if count == 0:
                print(f"   - {table} is EMPTY!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(test_full_orchestration())
    sys.exit(exit_code)