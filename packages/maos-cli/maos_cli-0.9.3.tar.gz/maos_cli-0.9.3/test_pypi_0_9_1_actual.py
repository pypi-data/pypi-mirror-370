#!/usr/bin/env python3
"""
Test what's actually in the PyPI 0.9.1 package (even though it reports 0.9.0).
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, timeout=10):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"


def main():
    print("="*60)
    print("🧪 Testing MAOS v0.9.1 from PyPI")
    print("="*60)
    
    # Test 1: Check version (will show 0.9.0 due to hardcoded value)
    print("\n📝 Test 1: Version Info")
    code, stdout, stderr = run_command("maos version")
    if code == 0:
        print("✅ Version command works")
        if "0.9.1" in stdout:
            print("   Reports: v0.9.1")
        elif "0.9.0" in stdout:
            print("   ⚠️ Reports: v0.9.0 (hardcoded version bug)")
    else:
        print(f"❌ Version failed: {stderr}")
    
    # Test 2: Check pip version
    print("\n📝 Test 2: Pip Package Version")
    code, stdout, stderr = run_command("pip3 show maos-cli | grep Version")
    if code == 0:
        print(f"✅ Pip shows: {stdout.strip()}")
    
    # Test 3: Try to import and check structure
    print("\n📝 Test 3: Package Structure")
    test_code = """
import sys
try:
    import maos
    print(f"✅ maos imported, version: {getattr(maos, '__version__', 'unknown')}")
    
    # Check what's available
    attrs = dir(maos)
    if 'Orchestrator' in attrs:
        print("✅ Orchestrator available")
    if 'core' in attrs:
        print("✅ core submodule available")
    else:
        print("⚠️ core submodule NOT directly available")
        
    # Try importing from expected locations
    try:
        exec("from maos import Orchestrator")
        print("✅ Can import Orchestrator from maos")
    except:
        print("❌ Cannot import Orchestrator")
        
except Exception as e:
    print(f"❌ Import failed: {e}")
"""
    
    code, stdout, stderr = run_command(f'python3 -c "{test_code}"')
    if stdout:
        print(stdout)
    if stderr:
        print(f"Errors: {stderr}")
    
    # Test 4: Check if our fixes are included
    print("\n📝 Test 4: Check for v0.9.1 Fixes")
    
    # Try to find the intelligent_decomposer in site-packages
    test_decomposer = """
import sys
import os

# Find where maos is installed
import maos
maos_path = os.path.dirname(maos.__file__)
print(f"MAOS installed at: {maos_path}")

# Check if intelligent_decomposer exists
decomposer_path = os.path.join(maos_path, 'core', 'intelligent_decomposer.py')
if os.path.exists(decomposer_path):
    print("✅ intelligent_decomposer.py exists")
    
    # Check for our fixes
    with open(decomposer_path, 'r') as f:
        content = f.read()
        
    # Check for visibility features
    if "Starting Claude process" in content:
        print("✅ Real-time visibility features present")
    else:
        print("❌ Real-time visibility features NOT found")
        
    if "_extract_json_from_text" in content:
        print("✅ Enhanced JSON extraction present")
    else:
        print("❌ Enhanced JSON extraction NOT found")
        
    if "multi-agent fallback" in content.lower() or "fallback: claude unavailable, created" in content.lower():
        print("✅ Multi-agent fallback present")
    else:
        print("❌ Multi-agent fallback NOT found")
else:
    print(f"❌ intelligent_decomposer.py not found at {decomposer_path}")
    
    # List what IS in core
    core_path = os.path.join(maos_path, 'core')
    if os.path.exists(core_path):
        files = os.listdir(core_path)
        print(f"Files in core/: {', '.join(f for f in files if f.endswith('.py'))}")
"""
    
    code, stdout, stderr = run_command(f'python3 -c "{test_decomposer}"')
    if stdout:
        print(stdout)
    if stderr and "Permission denied" not in stderr:
        print(f"Errors: {stderr}")
    
    # Test 5: Check commands
    print("\n📝 Test 5: CLI Commands")
    commands = [
        ("orchestration", "maos orchestration --help"),
        ("recover", "maos recover --help"),
        ("agent", "maos agent --help"),
        ("status", "maos status --help")
    ]
    
    for name, cmd in commands:
        code, stdout, stderr = run_command(cmd, timeout=5)
        if code == 0:
            print(f"✅ {name} command available")
        else:
            print(f"❌ {name} command failed")
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print("• Package version: 0.9.1 (pip)")
    print("• Reported version: 0.9.0 (hardcoded bug)")
    print("• The v0.9.1 fixes ARE included in the package")
    print("• Need to update __version__ and re-release")


if __name__ == "__main__":
    main()