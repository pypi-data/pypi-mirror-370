#!/usr/bin/env python3
"""
Simple test of MAOS persistence features.
Tests the core database persistence without complex dependencies.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from maos.interfaces.sqlite_persistence import SqlitePersistence


async def test_basic_persistence():
    """Test basic database persistence features."""
    
    print("=" * 60)
    print("MAOS BASIC PERSISTENCE TEST")
    print("=" * 60)
    
    # Use test database
    test_db = "./test_basic_persistence.db"
    
    # Clean up old test database
    if Path(test_db).exists():
        Path(test_db).unlink()
        print("✓ Cleaned up old test database")
    
    # Initialize persistence
    db = SqlitePersistence(test_db)
    await db.initialize()
    print("✓ Database initialized")
    
    # Test 1: Create and retrieve agent
    print("\n📝 Test 1: Agent Persistence")
    print("-" * 40)
    
    agent_id = "test-agent-001"
    await db.create_agent(
        agent_id=agent_id,
        name="Test Agent",
        agent_type="tester",
        capabilities=["testing", "validation"]
    )
    print(f"✓ Created agent: {agent_id}")
    
    agent = await db.get_agent(agent_id)
    assert agent is not None, "Agent not found"
    assert agent['name'] == "Test Agent", "Agent name mismatch"
    print(f"✓ Retrieved agent: {agent['name']}")
    
    # Test 2: Create and update session
    print("\n📝 Test 2: Session Persistence")
    print("-" * 40)
    
    session_id = f"session-{agent_id}"
    await db.create_session(
        session_id=session_id,
        agent_id=agent_id,
        task="Test task"
    )
    print(f"✓ Created session: {session_id}")
    
    # Update session
    await db.update_session(
        session_id=session_id,
        conversation_turn={
            "role": "test",
            "content": "Test message",
            "timestamp": datetime.now().isoformat()
        },
        cost=0.01
    )
    print("✓ Updated session")
    
    session = await db.get_session(session_id)
    assert session is not None, "Session not found"
    assert session['agent_id'] == agent_id, "Session agent mismatch"
    print(f"✓ Retrieved session for agent: {session['agent_id']}")
    
    # Test 3: Save and retrieve messages
    print("\n📝 Test 3: Message Persistence")
    print("-" * 40)
    
    message_ids = []
    for i in range(3):
        msg_id = await db.save_message(
            from_agent=agent_id,
            to_agent=None,  # Broadcast
            message=f"Test message {i+1}",
            message_type="info"
        )
        message_ids.append(msg_id)
    print(f"✓ Saved {len(message_ids)} messages")
    
    messages = await db.get_messages_for_agent(agent_id)
    print(f"✓ Retrieved {len(messages)} messages")
    
    # Test 4: Create orchestration
    print("\n📝 Test 4: Orchestration Persistence")
    print("-" * 40)
    
    orch_id = "test-orch-001"
    await db.save_orchestration(
        orchestration_id=orch_id,
        request="Test orchestration",
        agents=[agent_id],
        batches=[[agent_id]],
        status="running"
    )
    print(f"✓ Created orchestration: {orch_id}")
    
    # Update orchestration
    await db.update_orchestration(
        orchestration_id=orch_id,
        total_cost=0.05,
        status="completed",
        summary="Test completed"
    )
    print("✓ Updated orchestration")
    
    orch = await db.get_orchestration(orch_id)
    assert orch is not None, "Orchestration not found"
    assert orch['status'] == "completed", "Status not updated"
    print(f"✓ Retrieved orchestration: {orch['status']}")
    
    # Test 5: Create checkpoint
    print("\n📝 Test 5: Checkpoint Persistence")
    print("-" * 40)
    
    checkpoint_id = f"checkpoint-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    checkpoint_data = {
        'orchestration_id': orch_id,
        'agents': [agent_id],
        'timestamp': datetime.now().isoformat()
    }
    
    await db.save_checkpoint(
        checkpoint_id=checkpoint_id,
        name="Test checkpoint",
        checkpoint_data=checkpoint_data
    )
    print(f"✓ Created checkpoint: {checkpoint_id}")
    
    checkpoint = await db.load_checkpoint("Test checkpoint")
    assert checkpoint is not None, "Checkpoint not found"
    print("✓ Retrieved checkpoint")
    
    # Test 6: Database statistics
    print("\n📝 Test 6: Database Statistics")
    print("-" * 40)
    
    stats = await db.get_statistics()
    print("Database statistics:")
    for table, count in stats.items():
        print(f"  {table}: {count} records")
    
    # Test 7: Helper methods
    print("\n📝 Test 7: Helper Methods")
    print("-" * 40)
    
    # Test execute_query
    results = await db.execute_query(
        "SELECT COUNT(*) as count FROM agents"
    )
    assert len(results) > 0, "Query failed"
    print(f"✓ execute_query works: {results[0]['count']} agents")
    
    # Test update_agent_status
    await db.update_agent_status(agent_id, "completed")
    agent = await db.get_agent(agent_id)
    assert agent['status'] == "completed", "Status not updated"
    print(f"✓ update_agent_status works: {agent['status']}")
    
    # Clean up
    await db.close()
    
    print("\n" + "=" * 60)
    print("✅ ALL BASIC PERSISTENCE TESTS PASSED!")
    print("=" * 60)
    
    return True


async def main():
    """Run basic persistence tests."""
    
    try:
        success = await test_basic_persistence()
        
        if success:
            print("\n🎉 Basic persistence features are working!")
            print("\nSummary:")
            print("  ✅ Database initialization works")
            print("  ✅ Agent persistence works")
            print("  ✅ Session persistence works")
            print("  ✅ Message persistence works")
            print("  ✅ Orchestration persistence works")
            print("  ✅ Checkpoint persistence works")
            print("  ✅ Helper methods (execute_query, update_agent_status) work")
            return 0
        else:
            print("\n❌ Some tests failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)