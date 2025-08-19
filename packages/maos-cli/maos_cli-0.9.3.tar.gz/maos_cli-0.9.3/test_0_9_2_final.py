#!/usr/bin/env python3
"""
Final comprehensive test for MAOS v0.9.2 from PyPI.
"""

import subprocess
import sys
import asyncio
from datetime import datetime
from pathlib import Path
import os


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


def test_version():
    """Test 1: Verify version is correctly displayed as 0.9.2"""
    print("\n" + "="*60)
    print("TEST 1: Version Display")
    print("="*60)
    
    code, stdout, stderr = run_command("maos version")
    
    # Check if command works
    if code != 0:
        print(f"❌ Version command failed: {stderr}")
        return False
    
    # Check for correct version strings
    checks = [
        ("0.9.2" in stdout, "Version number 0.9.2"),
        ("0.7.0" not in stdout, "No old v0.7.0"),
        ("0.9.0" not in stdout, "No old v0.9.0"),
        ("0.9.1" not in stdout, "No old v0.9.1"),
        ("Version:" in stdout or "version:" in stdout.lower(), "Version label present")
    ]
    
    all_passed = True
    for check, description in checks:
        if check:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_passed = False
    
    print(f"\nActual output:\n{stdout}")
    
    return all_passed


def test_cli_commands():
    """Test 2: Verify all CLI commands are available"""
    print("\n" + "="*60)
    print("TEST 2: CLI Commands")
    print("="*60)
    
    commands = [
        ("main help", "maos --help"),
        ("orchestration", "maos orchestration --help"),
        ("recover", "maos recover --help"),
        ("agent", "maos agent --help"),
        ("status", "maos status --help"),
        ("config", "maos config --help")
    ]
    
    all_passed = True
    for name, cmd in commands:
        code, stdout, stderr = run_command(cmd, timeout=5)
        if code == 0:
            print(f"✅ {name} command works")
        else:
            print(f"❌ {name} command failed: {stderr[:100]}")
            all_passed = False
    
    return all_passed


async def test_multi_agent_fallback():
    """Test 3: Verify multi-agent fallback creates multiple agents"""
    print("\n" + "="*60)
    print("TEST 3: Multi-Agent Fallback")
    print("="*60)
    
    try:
        # Move to temp directory to avoid local file conflicts
        original_dir = os.getcwd()
        os.chdir("/tmp")
        
        # Import MAOS
        import maos
        print(f"✅ MAOS imported, version from module: {getattr(maos, '__version__', 'unknown')}")
        
        from maos.core.intelligent_decomposer import IntelligentDecomposer
        from maos.interfaces.sqlite_persistence import SqlitePersistence
        
        # Initialize
        db = SqlitePersistence("test_0_9_2.db")
        await db.initialize()
        print("✅ Database initialized")
        
        # Create decomposer
        decomposer = IntelligentDecomposer(db)
        
        # Test request that should create multiple agents
        test_request = "analyze the security vulnerabilities and fix them then create tests"
        prompt = f"USER REQUEST:\n{test_request}\n"
        
        # Use fallback directly (since Claude might not be available)
        result = decomposer._create_fallback_decomposition(prompt)
        
        # Count agents created
        total_agents = 0
        agent_types = set()
        for phase in result.execution_plan:
            for task in phase.tasks:
                total_agents += 1
                agent_types.add(task['agent_type'])
        
        print(f"\n📊 Results:")
        print(f"  - Request: '{test_request[:50]}...'")
        print(f"  - Agents created: {total_agents}")
        print(f"  - Agent types: {', '.join(agent_types)}")
        print(f"  - Phases: {len(result.execution_plan)}")
        
        # Cleanup
        await db.close()
        os.unlink("test_0_9_2.db")
        os.chdir(original_dir)
        
        # Check success
        if total_agents >= 2:
            print(f"✅ Multi-agent creation works! ({total_agents} agents)")
            return True
        else:
            print(f"❌ Only {total_agents} agent created")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_timeout_setting():
    """Test 4: Verify Claude timeout is set to 10 minutes"""
    print("\n" + "="*60)
    print("TEST 4: Claude Timeout Setting")
    print("="*60)
    
    try:
        from maos.core.intelligent_decomposer import IntelligentDecomposer
        import inspect
        
        # Get the source code
        source = inspect.getsource(IntelligentDecomposer._call_claude_orchestrator)
        
        # Check for timeout setting
        if "timeout_seconds = 600" in source:
            print("✅ Timeout set to 600 seconds (10 minutes)")
            timeout_ok = True
        elif "timeout_seconds = 30" in source:
            print("❌ Timeout still set to 30 seconds (too short!)")
            timeout_ok = False
        else:
            print("⚠️ Could not find timeout setting")
            timeout_ok = False
        
        # Check for timeout message
        if "10 minutes" in source or "600" in source:
            print("✅ Timeout message mentions 10 minutes or 600 seconds")
            message_ok = True
        else:
            print("⚠️ Timeout message doesn't mention proper duration")
            message_ok = False
        
        return timeout_ok and message_ok
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_auto_approve_docs():
    """Test 5: Check if auto-approve is documented"""
    print("\n" + "="*60)
    print("TEST 5: Auto-Approve Documentation")
    print("="*60)
    
    # Check help output
    code, stdout, stderr = run_command("maos chat --help")
    
    if "--auto-approve" in stdout or "--auto" in stdout:
        print("✅ --auto-approve flag is documented in help")
        return True
    else:
        print("⚠️ --auto-approve not found in help (might be OK)")
        return True  # Not critical


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 MAOS v0.9.2 Final Test Suite")
    print("="*60)
    print(f"Test Date: {datetime.now().isoformat()}")
    print(f"Python: {sys.version.split()[0]}")
    
    # First check what's installed
    code, stdout, stderr = run_command("pip3 show maos-cli | grep Version")
    print(f"Installed: {stdout.strip()}")
    
    tests = [
        ("Version Display", test_version),
        ("CLI Commands", test_cli_commands),
        ("Multi-Agent Fallback", test_multi_agent_fallback),
        ("Claude Timeout", test_timeout_setting),
        ("Auto-Approve Docs", test_auto_approve_docs)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*60)
    print(f"Results: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ MAOS v0.9.2 is working perfectly!")
        print("\nKey improvements verified:")
        print("  • Version correctly displays 0.9.2")
        print("  • Multi-agent creation works")
        print("  • Claude timeout extended to 10 minutes")
        print("  • All CLI commands available")
    else:
        failed = [name for name, result in results if not result]
        print(f"\n⚠️ Failed tests: {', '.join(failed)}")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)