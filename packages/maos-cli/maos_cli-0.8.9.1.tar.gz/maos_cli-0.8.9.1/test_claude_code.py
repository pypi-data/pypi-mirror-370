#!/usr/bin/env python3
"""Test MAOS with Claude Code integration."""

import subprocess
import sys

print("🧪 TESTING CLAUDE CODE INTEGRATION")
print("="*50)

# Test 1: Check Claude Code is available
print("\n1️⃣ Checking Claude Code availability...")
result = subprocess.run(["claude", "--version"], capture_output=True, text=True)
if result.returncode == 0:
    print(f"✅ Claude Code detected: {result.stdout.strip()}")
else:
    print("❌ Claude Code not available")
    sys.exit(1)

# Test 2: Run MAOS without API key
print("\n2️⃣ Running MAOS without API key...")
print("   (Using Claude Code session instead)")

# Run a simple test
proc = subprocess.Popen(
    ["maos", "chat"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send a command and exit
output, errors = proc.communicate(input="help\nexit\n", timeout=10)

# Check output
if "Claude Code detected" in output:
    print("✅ MAOS detected Claude Code session!")
elif "Using provided API key" in output:
    print("⚠️  MAOS using API key instead of Claude Code")
elif "No Claude Code session or API key" in output:
    print("❌ MAOS didn't detect Claude Code")
else:
    print("🔍 Output:")
    print(output[:500])

print("\n" + "="*50)
print("✅ CLAUDE CODE INTEGRATION TEST COMPLETE")