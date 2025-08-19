#!/usr/bin/env python3
"""Test that simulates what happens when you run 'maos chat'"""

import asyncio
from pathlib import Path

async def test_chat_flow():
    """Simulate the exact flow of 'maos chat' command"""
    
    print("🧪 Testing MAOS Chat Flow (v0.8.3)")
    print("=" * 50)
    
    # This simulates what main.py does when you run 'maos chat'
    from src.maos.cli.natural_language_v7 import NaturalLanguageProcessorV7
    
    # Create processor just like main.py does
    processor = NaturalLanguageProcessorV7(
        db_path=Path("./maos.db"),
        api_key=None  # No API key, like when using Claude Code
    )
    
    # Initialize (this is called in run())
    await processor.initialize()
    print("✅ Processor initialized")
    
    # Set auto_approve like run() does
    processor.auto_approve = True
    print("✅ Auto-approve set")
    
    # Simulate processing a request
    test_request = "test task - just a simple test"
    print(f"\n📝 Processing request: '{test_request}'")
    
    try:
        # This is what happens when user types something
        await processor._process_task_request(test_request)
        print("✅ Request processed without errors")
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        import traceback
        traceback.print_exc()
    
    # Check database
    stats = await processor.persistence.get_statistics()
    print(f"\n📊 Database statistics after processing:")
    for table, count in stats.items():
        print(f"  • {table}: {count}")
    
    # Check orchestrations specifically
    orchs = await processor.persistence.list_orchestrations()
    print(f"\n🎯 Orchestrations in database: {len(orchs)}")
    for orch in orchs[-3:]:  # Show last 3
        print(f"  • {orch['id'][:8]}... - {orch['status']}")
    
    await processor.persistence.close()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_chat_flow())