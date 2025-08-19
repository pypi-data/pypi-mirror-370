#!/usr/bin/env python3
"""Debug why Claude Code integration is hanging."""

import subprocess
import os

print("🔍 DEBUGGING CLAUDE CODE ISSUE")
print("="*50)

# Remove any API key
if "ANTHROPIC_API_KEY" in os.environ:
    del os.environ["ANTHROPIC_API_KEY"]

# Test 1: Can we run claude directly?
print("\n1️⃣ Testing direct claude command...")
try:
    result = subprocess.run(
        ["claude", "-p", "say hello", "--max-turns", "1", "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=10
    )
    print(f"Return code: {result.returncode}")
    print(f"STDOUT: {result.stdout[:200]}")
    print(f"STDERR: {result.stderr[:200]}")
    
    if result.returncode == 0:
        print("✅ Claude command works!")
    else:
        print("❌ Claude command failed!")
        
except subprocess.TimeoutExpired:
    print("❌ Claude command TIMED OUT!")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Check if claude needs authentication
print("\n2️⃣ Checking claude authentication...")
try:
    result = subprocess.run(
        ["claude", "--version"],
        capture_output=True,
        text=True,
        timeout=2
    )
    print(f"Claude version: {result.stdout.strip()}")
    
    # Try to check status
    result = subprocess.run(
        ["claude", "api", "show-key"],
        capture_output=True,
        text=True,
        timeout=2
    )
    print(f"API status: {result.stdout[:100] if result.stdout else result.stderr[:100]}")
    
except Exception as e:
    print(f"Status check: {e}")

print("\n" + "="*50)
print("DIAGNOSIS:")
print("Claude Code is installed but may not be authenticated")
print("or may not work without an active Claude Code window")