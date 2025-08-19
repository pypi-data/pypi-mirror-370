#!/usr/bin/env python3
"""
Simple MAOS Test - Basic validation that the system is working
"""

import sys
import redis
import psutil
from pathlib import Path

print("=" * 60)
print("MAOS - Multi-Agent Orchestration System")
print("Simple Test Script")
print("=" * 60)

# Test 1: Check Python version
print("\n1. Python Version Check:")
print(f"   Python {sys.version}")
if sys.version_info >= (3, 11):
    print("   ✅ Python version OK (3.11+)")
else:
    print("   ⚠️  Python 3.11+ recommended")

# Test 2: Test Redis connection
print("\n2. Redis Connection Test:")
try:
    r = redis.Redis(host='redis', port=6379, db=0)
    r.ping()
    print("   ✅ Redis connection successful")
    
    # Test read/write
    r.set('test:key', 'test_value')
    value = r.get('test:key')
    if value == b'test_value':
        print("   ✅ Redis read/write OK")
    r.delete('test:key')
except Exception as e:
    print(f"   ❌ Redis connection failed: {e}")
    print("   Make sure Redis container is running")

# Test 3: Check system resources
print("\n3. System Resources:")
print(f"   CPU Count: {psutil.cpu_count()}")
print(f"   Memory: {psutil.virtual_memory().percent:.1f}% used")
print(f"   Disk: {psutil.disk_usage('/').percent:.1f}% used")

# Test 4: Check MAOS modules exist
print("\n4. MAOS Module Check:")
src_path = Path(__file__).parent.parent / 'src'
if src_path.exists():
    modules = ['maos', 'communication', 'storage', 'monitoring', 'security']
    for module in modules:
        module_path = src_path / module
        if module_path.exists():
            print(f"   ✅ {module} module found")
        else:
            print(f"   ❌ {module} module missing")
else:
    print("   ❌ src directory not found")

print("\n" + "=" * 60)
print("🎉 MAOS Container is running!")
print("You can now use MAOS commands inside this container.")
print("\nExample commands:")
print("  python -m maos.cli.main --help")
print("  python scripts/demo.py")
print("=" * 60)