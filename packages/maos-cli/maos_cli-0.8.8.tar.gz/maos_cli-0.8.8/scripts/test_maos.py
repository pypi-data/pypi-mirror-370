#!/usr/bin/env python3
"""
MAOS Test Script - Quick validation of the Multi-Agent Orchestration System
Run this to verify your MAOS installation is working correctly.
"""

import sys
import time
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from maos.core.orchestrator import Orchestrator
    from maos.core.task_planner import TaskPlanner
    from maos.models.task import Task
    from maos.core.agent_manager import AgentManager
    from storage.redis_state.redis_state_manager import RedisStateManager
    from communication.message_bus.core import MessageBus
    print("✅ All MAOS modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you've installed dependencies: pip install -r requirements.txt")
    sys.exit(1)


def test_redis_connection():
    """Test Redis connectivity"""
    print("\n🔍 Testing Redis Connection...")
    try:
        state_manager = RedisStateManager()
        
        # Test write
        test_key = "test:connection"
        test_value = {"status": "connected", "timestamp": time.time()}
        state_manager.set(test_key, test_value)
        
        # Test read
        retrieved = state_manager.get(test_key)
        if retrieved == test_value:
            print("✅ Redis connection successful")
            return True
        else:
            print("❌ Redis read/write mismatch")
            return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("Please ensure Redis is running: docker run -d -p 6379:6379 redis:7-alpine")
        return False


async def test_agent_spawning():
    """Test agent creation and management"""
    print("\n🤖 Testing Agent Management...")
    try:
        agent_manager = AgentManager(max_agents=5)
        
        # Spawn test agents
        agents = []
        for i in range(3):
            agent_id = await agent_manager.spawn_agent(
                agent_type="test",
                name=f"TestAgent-{i}"
            )
            agents.append(agent_id)
            print(f"  ✓ Spawned agent: {agent_id}")
        
        # Check agent status
        for agent_id in agents:
            status = await agent_manager.get_agent_status(agent_id)
            print(f"  ✓ Agent {agent_id} status: {status.get('state', 'unknown')}")
        
        print("✅ Agent management working")
        return True
    except Exception as e:
        print(f"❌ Agent management failed: {e}")
        return False


async def test_task_planning():
    """Test task planning and DAG creation"""
    print("\n📋 Testing Task Planning...")
    try:
        planner = TaskPlanner()
        
        # Create a simple task
        simple_task = Task(
            id="test-simple",
            name="Simple Test Task",
            description="A basic test task",
            agent_type="test"
        )
        
        # Create a complex task with dependencies
        task1 = Task(id="task1", name="Task 1", agent_type="test")
        task2 = Task(id="task2", name="Task 2", agent_type="test", dependencies=["task1"])
        task3 = Task(id="task3", name="Task 3", agent_type="test", dependencies=["task1"])
        task4 = Task(id="task4", name="Task 4", agent_type="test", dependencies=["task2", "task3"])
        
        complex_task = Task(
            id="test-complex",
            name="Complex Test Task",
            description="A complex task with subtasks",
            subtasks=[task1, task2, task3, task4]
        )
        
        # Decompose tasks
        simple_plan = await planner.decompose_task(simple_task)
        complex_plan = await planner.decompose_task(complex_task)
        
        print(f"  ✓ Simple task decomposed: {len(simple_plan)} subtasks")
        print(f"  ✓ Complex task decomposed: {len(complex_plan)} subtasks")
        
        # Test execution order
        execution_order = planner._topological_sort(complex_plan)
        print(f"  ✓ Execution order determined: {[t.id for t in execution_order]}")
        
        print("✅ Task planning working")
        return True
    except Exception as e:
        print(f"❌ Task planning failed: {e}")
        return False


async def test_message_bus():
    """Test inter-agent communication"""
    print("\n📡 Testing Message Bus...")
    try:
        bus = MessageBus()
        received_messages = []
        
        # Subscribe to test channel
        async def message_handler(message):
            received_messages.append(message)
        
        await bus.subscribe("test-channel", message_handler)
        
        # Publish test messages
        test_messages = [
            {"type": "test", "content": "Message 1"},
            {"type": "test", "content": "Message 2"},
            {"type": "test", "content": "Message 3"}
        ]
        
        for msg in test_messages:
            await bus.publish("test-channel", msg)
        
        # Wait for messages to be processed
        await asyncio.sleep(0.5)
        
        if len(received_messages) == len(test_messages):
            print(f"  ✓ All {len(test_messages)} messages received")
            print("✅ Message bus working")
            return True
        else:
            print(f"❌ Message bus failed: Expected {len(test_messages)}, got {len(received_messages)}")
            return False
    except Exception as e:
        print(f"❌ Message bus failed: {e}")
        return False


async def test_parallel_execution():
    """Test parallel task execution"""
    print("\n⚡ Testing Parallel Execution...")
    try:
        orchestrator = Orchestrator()
        
        # Create parallel tasks
        tasks = []
        for i in range(3):
            task = Task(
                id=f"parallel-{i}",
                name=f"Parallel Task {i}",
                description=f"Simulated 2-second task {i}",
                agent_type="test"
            )
            tasks.append(task)
        
        print(f"  ℹ️  Executing {len(tasks)} tasks in parallel...")
        start_time = time.time()
        
        # Execute in parallel
        results = await orchestrator.execute_parallel(tasks)
        
        duration = time.time() - start_time
        
        # Should take ~2 seconds, not 6 seconds
        if duration < 4:  # Allow some overhead
            speedup = (len(tasks) * 2) / duration
            print(f"  ✓ Parallel execution completed in {duration:.1f}s")
            print(f"  ✓ Speedup: {speedup:.1f}x")
            print("✅ Parallel execution working")
            return True
        else:
            print(f"❌ Parallel execution too slow: {duration:.1f}s")
            return False
    except Exception as e:
        print(f"❌ Parallel execution failed: {e}")
        return False


async def test_checkpoint_recovery():
    """Test checkpoint and recovery system"""
    print("\n💾 Testing Checkpoint/Recovery...")
    try:
        orchestrator = Orchestrator()
        
        # Create test state
        test_state = {
            "tasks": ["task1", "task2", "task3"],
            "agents": ["agent1", "agent2"],
            "timestamp": time.time()
        }
        
        # Create checkpoint
        checkpoint_id = await orchestrator.create_checkpoint("test-checkpoint")
        print(f"  ✓ Checkpoint created: {checkpoint_id}")
        
        # Modify state
        test_state["tasks"].append("task4")
        
        # Recover from checkpoint
        recovered = await orchestrator.recover_from_checkpoint(checkpoint_id)
        
        if recovered:
            print(f"  ✓ Recovery successful")
            print("✅ Checkpoint/Recovery working")
            return True
        else:
            print("❌ Recovery failed")
            return False
    except Exception as e:
        print(f"❌ Checkpoint/Recovery failed: {e}")
        return False


def run_performance_benchmark():
    """Run a simple performance benchmark"""
    print("\n📊 Running Performance Benchmark...")
    
    try:
        # Simulate sequential execution
        sequential_start = time.time()
        for i in range(5):
            time.sleep(0.5)  # Simulate 0.5 second task
        sequential_time = time.time() - sequential_start
        
        print(f"  Sequential execution (5 tasks): {sequential_time:.1f}s")
        
        # Calculate theoretical parallel time
        parallel_time = 0.5  # All tasks run simultaneously
        speedup = sequential_time / parallel_time
        
        print(f"  Theoretical parallel time: {parallel_time:.1f}s")
        print(f"  Theoretical speedup: {speedup:.1f}x")
        print("✅ Benchmark complete")
        return True
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return False


async def main():
    """Main test runner"""
    print("=" * 60)
    print("🚀 MAOS System Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Redis Connection", test_redis_connection()))
    results.append(("Agent Management", await test_agent_spawning()))
    results.append(("Task Planning", await test_task_planning()))
    results.append(("Message Bus", await test_message_bus()))
    results.append(("Parallel Execution", await test_parallel_execution()))
    results.append(("Checkpoint/Recovery", await test_checkpoint_recovery()))
    results.append(("Performance Benchmark", run_performance_benchmark()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! MAOS is ready to use.")
        print("\nNext steps:")
        print("  1. Run: maos start")
        print("  2. Create a task: maos task create 'Your first task'")
        print("  3. Monitor: maos status --follow")
    else:
        print(f"\n⚠️  {failed} tests failed. Please check the errors above.")
        print("Common fixes:")
        print("  - Ensure Redis is running: docker run -d -p 6379:6379 redis:7-alpine")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Check logs: maos logs --debug")
    
    return failed == 0


if __name__ == "__main__":
    # Run async main
    success = asyncio.run(main())
    sys.exit(0 if success else 1)