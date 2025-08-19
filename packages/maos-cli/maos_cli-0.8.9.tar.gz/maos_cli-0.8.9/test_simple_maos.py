#!/usr/bin/env python3
"""
Simple standalone test for MAOS components.
"""

import asyncio
import tempfile
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from maos.core.orchestrator import Orchestrator
from maos.core.agent_manager import AgentManager
from maos.models.agent import Agent, AgentStatus, AgentCapability
from maos.interfaces.sqlite_persistence import SqlitePersistence


def test_orchestrator():
    """Test basic orchestrator functionality."""
    print("\n=== Testing Orchestrator ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Create orchestrator with test config
            config = {
                'state_manager': {
                    'auto_checkpoint_interval': 300,
                    'max_snapshots': 50
                }
            }
            
            persistence = SqlitePersistence(f"{tmpdir}/test.db")
            orch = Orchestrator(
                persistence_backend=persistence,
                component_config=config
            )
            
            print("✓ Orchestrator created successfully")
            
            # Test components are initialized
            assert orch.state_manager is not None, "State manager not initialized"
            print("✓ State manager initialized")
            
            assert orch.agent_manager is not None, "Agent manager not initialized"
            print("✓ Agent manager initialized")
            
            assert orch.task_planner is not None, "Task planner not initialized"
            print("✓ Task planner initialized")
            
            return True
            
        except Exception as e:
            print(f"✗ Orchestrator test failed: {e}")
            return False


async def test_agent_manager():
    """Test agent manager functionality."""
    print("\n=== Testing Agent Manager ===")
    
    try:
        manager = AgentManager()
        
        # Start the manager
        await manager.start()
        print("✓ Agent manager started")
        
        # Create an agent using spawn_agent
        agent_config = {
            'name': 'TestAgent',
            'type': 'worker',
            'capabilities': [AgentCapability.TASK_EXECUTION]
        }
        
        agent_id = await manager.spawn_agent(agent_config)
        assert agent_id is not None, "Failed to spawn agent"
        print(f"✓ Spawned agent with ID: {agent_id}")
        
        # Get the agent
        agent = manager.get_agent(agent_id)
        assert agent is not None, "Failed to get agent"
        print(f"✓ Retrieved agent: {agent.name}")
        
        # Get available agents
        available = manager.get_available_agents()
        assert len(available) > 0, "No available agents found"
        print(f"✓ Found {len(available)} available agent(s)")
        
        # Stop the manager
        await manager.stop()
        print("✓ Agent manager stopped")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_sqlite_persistence():
    """Test SQLite persistence functionality."""
    print("\n=== Testing SQLite Persistence ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        persistence = SqlitePersistence(db_path)
        await persistence.initialize()
        print("✓ SQLite persistence initialized")
        
        # Test creating an agent in the database
        agent_id = str(uuid.uuid4())
        await persistence.create_agent(
            agent_id=agent_id,
            name="TestAgent",
            agent_type="worker",
            capabilities=["task_execution"]
        )
        print(f"✓ Created agent in database: {agent_id}")
        
        # Test retrieving the agent
        agent_data = await persistence.get_agent(agent_id)
        assert agent_data is not None, "Failed to retrieve agent"
        assert agent_data['name'] == "TestAgent", "Agent name mismatch"
        print(f"✓ Retrieved agent: {agent_data['name']}")
        
        # Test getting active agents
        active_agents = await persistence.get_active_agents()
        assert len(active_agents) > 0, "No active agents found"
        print(f"✓ Found {len(active_agents)} active agent(s)")
        
        # Test save/load with key-value store
        test_data = {"test": "data", "number": 42}
        await persistence.save("test_key", test_data)
        print("✓ Saved test data")
        
        loaded_data = await persistence.load("test_key")
        assert loaded_data == test_data, "Loaded data mismatch"
        print("✓ Loaded test data successfully")
        
        # Test deletion
        deleted = await persistence.delete("test_key")
        assert deleted == True, "Failed to delete key"
        print("✓ Deleted test key")
        
        # Close the connection
        await persistence.close()
        print("✓ Closed database connection")
        
        return True
        
    except Exception as e:
        print(f"✗ SQLite Persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


async def test_full_integration():
    """Test full integration of components."""
    print("\n=== Testing Full Integration ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Create orchestrator
            persistence = SqlitePersistence(f"{tmpdir}/test.db")
            await persistence.initialize()
            
            orchestrator = Orchestrator(
                persistence_backend=persistence,
                component_config={'state_manager': {'auto_checkpoint_interval': 300}}
            )
            print("✓ Created orchestrator with persistence")
            
            # Start orchestrator
            await orchestrator.start()
            print("✓ Started orchestrator")
            
            # Create an agent pool
            pool_id = await orchestrator.agent_manager.create_agent_pool(
                name="TestPool",
                size=2,
                agent_type="worker"
            )
            print(f"✓ Created agent pool with ID: {pool_id}")
            
            # Get available agents
            available = orchestrator.agent_manager.get_available_agents()
            print(f"✓ Found {len(available)} available agents")
            
            # Execute a task
            task_request = {
                'name': 'Integration Test Task',
                'description': 'Test task execution',
                'priority': 'high'
            }
            
            result = await orchestrator.execute_task(task_request)
            assert result is not None, "Task execution returned None"
            print("✓ Executed task successfully")
            
            # Get metrics
            metrics = orchestrator.agent_manager.get_metrics()
            print(f"✓ Retrieved metrics: {metrics.get('total_agents', 0)} total agents")
            
            # Shutdown
            await orchestrator.shutdown()
            print("✓ Shut down orchestrator")
            
            return True
            
        except Exception as e:
            print(f"✗ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_orchestration_tracking():
    """Test orchestration tracking in database."""
    print("\n=== Testing Orchestration Tracking ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        persistence = SqlitePersistence(db_path)
        await persistence.initialize()
        print("✓ Database initialized")
        
        # Create an orchestration
        orch_id = str(uuid.uuid4())
        await persistence.save_orchestration(
            orchestration_id=orch_id,
            request="Test orchestration request",
            orchestration_type="test"
        )
        print(f"✓ Created orchestration: {orch_id}")
        
        # Update orchestration with agent assignment
        agent_id = str(uuid.uuid4())
        await persistence.update_orchestration(
            orchestration_id=orch_id,
            status="running",
            assigned_agents=[agent_id]
        )
        print("✓ Updated orchestration with agent assignment")
        
        # Retrieve orchestration
        orch_data = await persistence.get_orchestration(orch_id)
        assert orch_data is not None, "Failed to retrieve orchestration"
        assert orch_data['status'] == "running", "Status mismatch"
        print(f"✓ Retrieved orchestration with status: {orch_data['status']}")
        
        # Complete orchestration
        await persistence.update_orchestration(
            orchestration_id=orch_id,
            status="completed",
            result={"success": True, "message": "Test completed"}
        )
        print("✓ Completed orchestration")
        
        # Get statistics
        stats = await persistence.get_statistics()
        assert stats['orchestrations'] > 0, "No orchestrations in statistics"
        print(f"✓ Statistics: {stats}")
        
        await persistence.close()
        return True
        
    except Exception as e:
        print(f"✗ Orchestration tracking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


async def main():
    """Run all tests."""
    print("=" * 50)
    print("MAOS Simple Test Suite")
    print("=" * 50)
    
    results = []
    
    # Run synchronous tests
    results.append(("Orchestrator", test_orchestrator()))
    
    # Run async tests
    results.append(("Agent Manager", await test_agent_manager()))
    results.append(("SQLite Persistence", await test_sqlite_persistence()))
    results.append(("Orchestration Tracking", await test_orchestration_tracking()))
    results.append(("Full Integration", await test_full_integration()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)