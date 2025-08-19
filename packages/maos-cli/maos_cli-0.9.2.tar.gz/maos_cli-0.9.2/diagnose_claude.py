#!/usr/bin/env python3
"""Diagnose Claude Code CLI issues."""

import subprocess
import os
import json

print("🔍 DIAGNOSING CLAUDE CODE CLI")
print("="*50)

# Test different command variations
tests = [
    {
        "name": "Version check",
        "cmd": ["claude", "--version"],
        "timeout": 2
    },
    {
        "name": "Simple -p without permissions flag",
        "cmd": ["claude", "-p", "say hello"],
        "timeout": 10
    },
    {
        "name": "With --dangerously-skip-permissions",
        "cmd": ["claude", "-p", "say hello", "--dangerously-skip-permissions"],
        "timeout": 10
    },
    {
        "name": "With JSON output",
        "cmd": ["claude", "-p", "say hello", "--output-format", "json"],
        "timeout": 10
    },
    {
        "name": "Both flags",
        "cmd": ["claude", "-p", "say hello", "--dangerously-skip-permissions", "--output-format", "json"],
        "timeout": 10
    }
]

for test in tests:
    print(f"\n📝 Test: {test['name']}")
    print(f"   Command: {' '.join(test['cmd'])}")
    
    try:
        result = subprocess.run(
            test['cmd'],
            capture_output=True,
            text=True,
            timeout=test['timeout']
        )
        
        if result.returncode == 0:
            print(f"   ✅ Success (exit code: {result.returncode})")
            if result.stdout:
                print(f"   Output preview: {result.stdout[:100]}...")
        else:
            print(f"   ❌ Failed (exit code: {result.returncode})")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
                
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT after {test['timeout']}s")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Check environment
print("\n📋 Environment Check:")
print(f"   ANTHROPIC_API_KEY set: {'Yes' if 'ANTHROPIC_API_KEY' in os.environ else 'No'}")
print(f"   Current directory: {os.getcwd()}")

# Check if Claude config exists
claude_config_paths = [
    os.path.expanduser("~/.claude"),
    os.path.expanduser("~/.config/claude"),
    os.path.expanduser("~/Library/Application Support/claude")
]

print("\n📁 Claude Config Locations:")
for path in claude_config_paths:
    if os.path.exists(path):
        print(f"   ✅ Found: {path}")
    else:
        print(f"   ❌ Not found: {path}")

print("\n" + "="*50)
print("💡 Analysis:")
print("If all commands timeout, Claude Code might:")
print("1. Not be properly authenticated")
print("2. Require an active Claude window")
print("3. Have a different authentication mechanism")
print("4. Need special environment variables")