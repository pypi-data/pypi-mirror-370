"""
Example usage of Redis-based shared state management system for MAOS.

This example demonstrates how to use the comprehensive Redis state management
system with all its features including distributed operations, memory pools,
versioning, and monitoring.
"""

import asyncio
import logging
from datetime import datetime
from uuid import uuid4

from src.storage.redis_state import (
    RedisStateManager,
    StateKey,
    StateValue,
    StateChangeType,
    MemoryPartitionType
)
from src.storage.redis_state.integration import create_integrated_state_manager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_operations_example():
    """Demonstrate basic state operations."""
    print("=== Basic State Operations Example ===")
    
    # Initialize Redis state manager
    manager = RedisStateManager(
        redis_urls=['redis://localhost:6379'],
        cluster_mode=False,
        memory_pool_size_gb=2,
        enable_monitoring=True,
        enable_backup=True
    )
    
    try:
        await manager.initialize()
        
        # Create state keys and values
        user_key = StateKey(
            namespace="app",
            category="users",
            identifier="user123"
        )
        
        user_data = StateValue(
            data={
                "name": "John Doe",
                "email": "john.doe@example.com",
                "age": 30,
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            },
            metadata={"created_by": "system"}
        )
        
        # Set state
        success = await manager.set_state(user_key, user_data)
        print(f"Set state result: {success}")
        
        # Get state
        retrieved_data = await manager.get_state(user_key)
        if retrieved_data:
            print(f"Retrieved user: {retrieved_data.data['name']}")
            print(f"Version: {retrieved_data.version}")
        
        # Update state atomically
        def update_age(current_value):
            if current_value:
                new_data = current_value.data.copy()
                new_data["age"] += 1
                return StateValue(data=new_data)
            return current_value
        
        updated_value = await manager.update_state(user_key, update_age)
        print(f"Updated age to: {updated_value.data['age']}")
        
        # Delete state
        deleted = await manager.delete_state(user_key)
        print(f"Deleted state: {deleted}")
        
    finally:
        await manager.shutdown()


async def bulk_operations_example():
    """Demonstrate bulk operations for high performance."""
    print("\n=== Bulk Operations Example ===")
    
    manager = RedisStateManager(
        redis_urls=['redis://localhost:6379'],
        cluster_mode=False
    )
    
    try:
        await manager.initialize()
        
        # Prepare bulk data
        bulk_data = {}
        for i in range(100):
            key = StateKey("bulk", "items", f"item_{i}")
            value = StateValue(
                data={
                    "id": i,
                    "name": f"Item {i}",
                    "value": i * 10,
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            bulk_data[key] = value
        
        # Bulk set
        print(f"Performing bulk set of {len(bulk_data)} items...")
        start_time = asyncio.get_event_loop().time()
        
        bulk_result = await manager.bulk_set(bulk_data)
        
        end_time = asyncio.get_event_loop().time()
        elapsed_ms = (end_time - start_time) * 1000
        
        print(f"Bulk set completed in {elapsed_ms:.2f}ms")
        print(f"Status: {bulk_result.status}")
        print(f"Operations: {len(bulk_result.operations)}")
        
        # Bulk get
        keys = list(bulk_data.keys())[:10]  # Get first 10
        retrieved_data = await manager.bulk_get(keys)
        
        print(f"Retrieved {len(retrieved_data)} items")
        for key, value in retrieved_data.items():
            if value:
                print(f"  {key.identifier}: {value.data['name']}")
        
        # Bulk delete
        delete_keys = keys[:5]  # Delete first 5
        delete_result = await manager.bulk_delete(delete_keys)
        print(f"Bulk delete status: {delete_result.status}")
        
    finally:
        await manager.shutdown()


async def memory_pool_example():
    """Demonstrate memory pool management."""
    print("\n=== Memory Pool Management Example ===")
    
    manager = RedisStateManager(
        redis_urls=['redis://localhost:6379'],
        memory_pool_size_gb=1  # 1GB pool
    )
    
    try:
        await manager.initialize()
        
        # Get initial memory usage
        initial_stats = await manager.get_memory_usage()
        print(f"Initial memory usage: {initial_stats}")
        
        # Allocate agent-specific partition
        agent_id = uuid4()
        partition_id = await manager.allocate_memory_partition(
            agent_id=agent_id,
            size_mb=50,  # 50MB partition
            partition_type="agent_dedicated"
        )
        
        print(f"Allocated partition {partition_id} for agent {agent_id}")
        
        # Store data that will use this partition
        agent_key = StateKey("agents", "data", str(agent_id))
        agent_data = StateValue(
            data={
                "agent_id": str(agent_id),
                "type": "worker",
                "status": "active",
                "large_data": "x" * 1000  # 1KB of data
            }
        )
        
        await manager.set_state(agent_key, agent_data)
        
        # Get updated memory usage
        updated_stats = await manager.get_memory_usage()
        print(f"Updated memory usage: {updated_stats}")
        
        # Deallocate partition
        deallocated = await manager.deallocate_memory_partition(partition_id)
        print(f"Deallocated partition: {deallocated}")
        
    finally:
        await manager.shutdown()


async def data_structures_example():
    """Demonstrate Redis data structures operations."""
    print("\n=== Data Structures Example ===")
    
    manager = RedisStateManager(redis_urls=['redis://localhost:6379'])
    
    try:
        await manager.initialize()
        
        # List operations
        list_key = StateKey("app", "lists", "todo_list")
        list_ops = await manager.list_operations(list_key)
        
        await list_ops.push_right("Buy groceries")
        await list_ops.push_right("Walk the dog")
        await list_ops.push_right("Read a book")
        
        todo_items = await list_ops.get_range()
        print(f"Todo items: {todo_items}")
        
        # Set operations
        set_key = StateKey("app", "sets", "tags")
        set_ops = await manager.set_operations(set_key)
        
        await set_ops.add("python", "redis", "async", "distributed")
        tags = await set_ops.members()
        print(f"Tags: {tags}")
        
        # Sorted set operations (leaderboard)
        leaderboard_key = StateKey("game", "leaderboard", "high_scores")
        sorted_set_ops = await manager.sorted_set_operations(leaderboard_key)
        
        scores = {100.0: "Alice", 95.0: "Bob", 87.0: "Charlie"}
        await sorted_set_ops.add(scores)
        
        top_players = await sorted_set_ops.range_by_rank(0, 2, reverse=True, with_scores=True)
        print(f"Top players: {top_players}")
        
        # Hash operations (user profile)
        profile_key = StateKey("users", "profiles", "user456")
        hash_ops = await manager.hash_operations(profile_key)
        
        await hash_ops.set_multiple({
            "name": "Jane Smith",
            "level": 15,
            "score": 1250,
            "last_login": datetime.utcnow().isoformat()
        })
        
        profile = await hash_ops.get_all()
        print(f"User profile: {profile}")
        
    finally:
        await manager.shutdown()


async def state_watching_example():
    """Demonstrate state watching and notifications."""
    print("\n=== State Watching Example ===")
    
    manager = RedisStateManager(redis_urls=['redis://localhost:6379'])
    
    try:
        await manager.initialize()
        
        # Set up state watcher
        changes_received = []
        
        def state_change_handler(change):
            changes_received.append(change)
            print(f"State change: {change.key} -> {change.change_type.value}")
        
        # Watch for changes to user data
        watcher_id = await manager.watch_state(
            key_pattern="users:*:*",
            callback=state_change_handler,
            change_types=[StateChangeType.CREATED, StateChangeType.UPDATED]
        )
        
        print(f"Started watching with ID: {watcher_id}")
        
        # Create some state changes
        for i in range(3):
            user_key = StateKey("users", "data", f"user{i}")
            user_data = StateValue(data={"name": f"User {i}", "id": i})
            
            await manager.set_state(user_key, user_data)
            await asyncio.sleep(0.1)  # Small delay for notification processing
        
        print(f"Received {len(changes_received)} change notifications")
        
        # Remove watcher
        await manager.unwatch_state(watcher_id)
        
    finally:
        await manager.shutdown()


async def backup_recovery_example():
    """Demonstrate backup and recovery operations."""
    print("\n=== Backup and Recovery Example ===")
    
    manager = RedisStateManager(
        redis_urls=['redis://localhost:6379'],
        enable_backup=True
    )
    
    try:
        await manager.initialize()
        
        # Create some test data
        test_data = {}
        for i in range(5):
            key = StateKey("backup_test", "data", f"item{i}")
            value = StateValue(data={"id": i, "content": f"Test data {i}"})
            test_data[key] = value
        
        await manager.bulk_set(test_data)
        print("Created test data for backup")
        
        # Create backup
        backup_id = await manager.create_backup(
            name="test_backup",
            namespaces=["backup_test"]
        )
        print(f"Created backup: {backup_id}")
        
        # Delete some data
        keys_to_delete = list(test_data.keys())[:2]
        await manager.bulk_delete(keys_to_delete)
        print("Deleted some test data")
        
        # Verify deletion
        remaining = await manager.bulk_get(list(test_data.keys()))
        remaining_count = sum(1 for v in remaining.values() if v is not None)
        print(f"Remaining items: {remaining_count}")
        
        # Restore from backup
        restored = await manager.restore_backup(backup_id)
        print(f"Backup restored: {restored}")
        
        # Verify restoration
        restored_data = await manager.bulk_get(list(test_data.keys()))
        restored_count = sum(1 for v in restored_data.values() if v is not None)
        print(f"Restored items: {restored_count}")
        
    finally:
        await manager.shutdown()


async def monitoring_example():
    """Demonstrate monitoring and performance metrics."""
    print("\n=== Monitoring Example ===")
    
    manager = RedisStateManager(
        redis_urls=['redis://localhost:6379'],
        enable_monitoring=True
    )
    
    try:
        await manager.initialize()
        
        # Perform some operations to generate metrics
        for i in range(10):
            key = StateKey("metrics", "test", f"key{i}")
            value = StateValue(data={"value": i})
            await manager.set_state(key, value)
        
        # Wait a moment for metrics collection
        await asyncio.sleep(2)
        
        # Get performance metrics
        metrics = manager.get_performance_metrics()
        print(f"Performance metrics:")
        print(f"  Total operations: {metrics.get('total_operations', 0)}")
        print(f"  Successful operations: {metrics.get('successful_operations', 0)}")
        print(f"  Average latency: {metrics.get('avg_latency_ms', 0):.2f}ms")
        print(f"  Operations per second: {metrics.get('operations_per_second', 0):.2f}")
        
        # Get cluster status
        cluster_status = await manager.get_cluster_status()
        print(f"Cluster status: {cluster_status['mode']}")
        print(f"Memory usage: {cluster_status.get('memory_usage', 0)} bytes")
        
    finally:
        await manager.shutdown()


async def integration_example():
    """Demonstrate integration with existing MAOS state manager."""
    print("\n=== MAOS Integration Example ===")
    
    # Create integrated state manager
    integrated_manager = await create_integrated_state_manager(
        redis_urls=['redis://localhost:6379'],
        cluster_mode=False,
        memory_pool_size_gb=1
    )
    
    try:
        # Use standard MAOS StateManager interface
        from src.maos.models.task import Task
        from src.maos.models.agent import Agent
        
        # Create and store a task (this will be stored in Redis automatically)
        task = Task(
            id=uuid4(),
            name="Example Task",
            description="This is an example task",
            status="pending"
        )
        
        await integrated_manager.store_object("tasks", task)
        print(f"Stored task: {task.name}")
        
        # Retrieve the task
        retrieved_task = await integrated_manager.get_object("tasks", task.id)
        if retrieved_task:
            print(f"Retrieved task: {retrieved_task.name}")
        
        # Get all tasks
        all_tasks = await integrated_manager.get_objects("tasks")
        print(f"Total tasks: {len(all_tasks)}")
        
        # Create a snapshot (backed by Redis backup)
        snapshot = await integrated_manager.create_snapshot("integration_test")
        print(f"Created snapshot: {snapshot.id}")
        
        # Get comprehensive health information
        health = await integrated_manager.get_cluster_health()
        print(f"Integration status: {health['integration_status']}")
        
    finally:
        await integrated_manager.shutdown()


async def main():
    """Run all examples."""
    print("Redis State Management System Examples")
    print("=" * 50)
    
    examples = [
        basic_operations_example,
        bulk_operations_example,
        memory_pool_example,
        data_structures_example,
        state_watching_example,
        backup_recovery_example,
        monitoring_example,
        integration_example
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"Example failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()  # Add spacing between examples


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())