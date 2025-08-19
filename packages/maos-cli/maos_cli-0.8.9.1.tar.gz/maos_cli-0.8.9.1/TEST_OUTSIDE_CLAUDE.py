#!/usr/bin/env python3
"""
⚠️ IMPORTANT: Run this script OUTSIDE of Claude Code!

This script tests MAOS integration with Claude Code.

INSTRUCTIONS:
1. First, make sure Claude Code is authenticated:
   $ claude
   (Complete OAuth login if needed, then you can exit)

2. Then run this script in a SEPARATE terminal:
   $ python3 TEST_OUTSIDE_CLAUDE.py

DO NOT run this from within Claude Code - it won't work!
"""

import subprocess
import sys
import os

print("="*60)
print("🧪 TESTING MAOS + CLAUDE CODE INTEGRATION")
print("="*60)
print("\n⚠️  This script must be run OUTSIDE of Claude Code!")
print("   If you're running this from Claude Code, it will hang!\n")

# Remove any API key to ensure we're using Claude Code OAuth
if "ANTHROPIC_API_KEY" in os.environ:
    del os.environ["ANTHROPIC_API_KEY"]
    print("✅ Removed ANTHROPIC_API_KEY - using Claude Code OAuth")

# Test 1: Check Claude Code is installed and authenticated
print("\n1️⃣ Checking Claude Code...")
try:
    result = subprocess.run(
        ["claude", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print(f"✅ Claude Code installed: {result.stdout.strip()}")
    else:
        print("❌ Claude Code not found or not working")
        print("   Please install: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)
except subprocess.TimeoutExpired:
    print("❌ Claude Code command timed out")
    print("   This might mean you're running from INSIDE Claude Code")
    print("   Please run this script from a SEPARATE terminal!")
    sys.exit(1)

# Test 2: Test non-interactive mode
print("\n2️⃣ Testing Claude Code non-interactive mode...")
print("   Running: claude -p 'say hello' --dangerously-skip-permissions")

try:
    result = subprocess.run(
        ["claude", "-p", "say hello", "--dangerously-skip-permissions", "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("✅ Claude Code non-interactive mode works!")
        print(f"   Output length: {len(result.stdout)} characters")
        
        # Test 3: Now test MAOS
        print("\n3️⃣ Testing MAOS with Claude Code...")
        
        # Add src to path
        sys.path.insert(0, 'src')
        
        import asyncio
        from maos.core.orchestrator_v7 import OrchestratorV7
        from maos.interfaces.sqlite_persistence import SqlitePersistence
        
        async def test_maos():
            persistence = SqlitePersistence("test_external.db")
            await persistence.initialize()
            
            # No API key - using Claude Code OAuth
            orchestrator = OrchestratorV7(persistence, api_key=None)
            
            result = await orchestrator.orchestrate(
                "write a haiku about Python", 
                auto_approve=True
            )
            
            print(f"✅ MAOS orchestration complete!")
            print(f"   Orchestration ID: {result.orchestration_id[:8]}")
            return True
        
        success = asyncio.run(test_maos())
        
        if success:
            print("\n" + "="*60)
            print("🎉 SUCCESS! MAOS + Claude Code integration works!")
            print("="*60)
            print("\nYou can now use MAOS with your Claude Code session:")
            print("  $ maos chat")
            print("\nMAOS will use your authenticated Claude Code (OAuth)")
            print("without needing an API key!")
        
    else:
        print("❌ Claude Code command failed")
        print(f"   Error: {result.stderr}")
        print("\nPossible issues:")
        print("1. Claude Code not authenticated - run 'claude' first")
        print("2. You're running this from INSIDE Claude Code (won't work)")
        
except subprocess.TimeoutExpired:
    print("❌ Command timed out after 30 seconds")
    print("\n⚠️  This usually means you're running from INSIDE Claude Code!")
    print("   Please run this script from a SEPARATE terminal")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)