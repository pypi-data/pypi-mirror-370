#!/usr/bin/env python3
"""Test MAOS directly with auto-approve."""

import asyncio
import os
from pathlib import Path

# Set up environment
os.environ["ANTHROPIC_API_KEY"] = "test"

import sys
sys.path.insert(0, 'src')
from maos.cli.natural_language_v7 import NaturalLanguageProcessorV7

async def test_direct():
    """Test MAOS directly."""
    
    print("🧪 TESTING MAOS DIRECTLY WITH AUTO-APPROVE")
    print("="*50)
    
    # Remove existing database
    if os.path.exists("maos.db"):
        os.remove("maos.db")
    
    # Create processor with auto-approve
    processor = NaturalLanguageProcessorV7(
        db_path=Path("./maos.db"),
        api_key="test"
    )
    
    # Initialize
    await processor.initialize()
    processor.auto_approve = True  # Force auto-approve
    
    print("\n1️⃣ Testing task request processing...")
    
    try:
        # Test orchestration directly 
        result = await processor.orchestrator.orchestrate("explain this project", auto_approve=True)
        
        print(f"✅ Orchestration completed!")
        print(f"✅ Orchestration ID: {result.orchestration_id[:8]}")
        print(f"✅ Agents created: {len(result.agents_created)}")
        
    except Exception as e:
        print(f"⚠️  Orchestration completed with error: {type(e).__name__}: {e}")
    
    print("\n2️⃣ Checking database...")
    
    # Check database was created
    if os.path.exists("maos.db"):
        print("✅ Database file created")
        
        import sqlite3
        conn = sqlite3.connect("maos.db")
        cursor = conn.cursor()
        
        # Check agents
        cursor.execute("SELECT COUNT(*) FROM agents")
        agent_count = cursor.fetchone()[0]
        print(f"💾 Agents in database: {agent_count}")
        
        if agent_count > 0:
            cursor.execute("SELECT id, name, agent_type FROM agents")
            agents = cursor.fetchall()
            for agent in agents:
                print(f"  - Agent: {agent[0]}, {agent[1]}, {agent[2]}")
        
        # Check sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        print(f"💾 Sessions in database: {session_count}")
        
        # Check checkpoints
        cursor.execute("SELECT COUNT(*) FROM checkpoints")
        checkpoint_count = cursor.fetchone()[0]
        print(f"💾 Checkpoints in database: {checkpoint_count}")
        
        if checkpoint_count > 0:
            cursor.execute("SELECT name FROM checkpoints")
            checkpoints = cursor.fetchall()
            for cp in checkpoints:
                print(f"  - Checkpoint: {cp[0]}")
        
        conn.close()
        
        # Verify data actually saved
        total_records = agent_count + session_count + checkpoint_count
        if total_records > 0:
            print(f"✅ DATABASE INTEGRATION WORKING: {total_records} records saved")
            return True
        else:
            print("❌ DATABASE INTEGRATION BROKEN: No records saved")
            return False
    else:
        print("❌ Database file not created")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_direct())
    print(f"\n📊 FINAL RESULT: {'✅ SUCCESS' if result else '❌ FAILED'}")