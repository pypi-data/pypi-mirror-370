#!/usr/bin/env python3
"""Test MAOS with proper Claude Code timing."""

import subprocess
import time
import sys
import os

print("🧪 TESTING MAOS WITH CLAUDE CODE")
print("="*60)

# First verify Claude Code works with proper timeout
print("\n1️⃣ Testing Claude Code with realistic timeout...")
print("   Command: claude -p 'say hello'")
print("   ⏳ Please wait, Claude Code takes 30-60 seconds to start...")

start_time = time.time()

try:
    result = subprocess.run(
        ["claude", "-p", "say hello"],
        capture_output=True,
        text=True,
        timeout=120  # 2 minute timeout
    )
    
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"   ✅ Success! (took {elapsed:.1f} seconds)")
        print(f"   Response: {result.stdout[:200]}...")
        
        # Now test MAOS
        print("\n2️⃣ Testing MAOS orchestration...")
        print("   This will use Claude Code for agent execution")
        
        sys.path.insert(0, 'src')
        import asyncio
        from maos.core.orchestrator_v7 import OrchestratorV7
        from maos.interfaces.sqlite_persistence import SqlitePersistence
        
        async def test_maos():
            # Clean database
            if os.path.exists("test_working.db"):
                os.remove("test_working.db")
            
            persistence = SqlitePersistence("test_working.db")
            await persistence.initialize()
            
            # No API key - using Claude Code OAuth
            orchestrator = OrchestratorV7(persistence, api_key=None)
            
            print("   🚀 Starting orchestration...")
            print("   ⏳ This may take 1-2 minutes...")
            
            result = await orchestrator.orchestrate(
                "write a simple Python hello world", 
                auto_approve=True
            )
            
            print(f"\n   ✅ Orchestration complete!")
            print(f"   Orchestration ID: {result.orchestration_id[:8]}")
            print(f"   Agents created: {len(result.agents_created)}")
            
            return True
        
        success = asyncio.run(test_maos())
        
        if success:
            print("\n" + "="*60)
            print("🎉 SUCCESS! MAOS + Claude Code works!")
            print("="*60)
            print("\n✅ MAOS is now configured to use your Claude Code session")
            print("✅ No API key needed - uses your Claude Max plan via OAuth")
            print("\n📌 To use MAOS:")
            print("   1. Make sure Claude Code is authenticated (run 'claude' once)")
            print("   2. Run 'maos chat' from any terminal")
            print("   3. Be patient - Claude Code takes 30-60s to start")
    else:
        print(f"   ❌ Failed (exit code: {result.returncode})")
        print(f"   Error: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print(f"   ⏰ Timed out after 120 seconds")
    print("   Claude Code might not be authenticated")
    print("   Try running 'claude' first to authenticate")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)