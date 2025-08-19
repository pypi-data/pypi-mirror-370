#!/usr/bin/env python3
"""Test real Claude Code integration."""

import asyncio
import os
import sys
sys.path.insert(0, 'src')

# Don't set any API key - use Claude Code
if "ANTHROPIC_API_KEY" in os.environ:
    del os.environ["ANTHROPIC_API_KEY"]

from maos.core.orchestrator_v7 import OrchestratorV7
from maos.interfaces.sqlite_persistence import SqlitePersistence

async def test_claude_code():
    print("🧪 TESTING REAL CLAUDE CODE INTEGRATION")
    print("="*50)
    
    # Check Claude Code
    import subprocess
    result = subprocess.run(["claude", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Claude Code not available!")
        return False
    print(f"✅ Claude Code: {result.stdout.strip()}")
    
    # Initialize WITHOUT API key
    persistence = SqlitePersistence("test_claude.db")
    await persistence.initialize()
    
    orchestrator = OrchestratorV7(persistence, api_key=None)  # No API key!
    print("✅ Orchestrator initialized without API key")
    
    try:
        print("\n🚀 Testing orchestration with Claude Code...")
        result = await orchestrator.orchestrate(
            "write a hello world in Python", 
            auto_approve=True
        )
        
        print(f"✅ SUCCESS! Orchestration ID: {result.orchestration_id[:8]}")
        print(f"✅ Used Claude Code session successfully!")
        
        if result.agents_created:
            print(f"✅ Agents created: {len(result.agents_created)}")
            for agent_id in result.agents_created:
                print(f"   - {agent_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_claude_code())
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")