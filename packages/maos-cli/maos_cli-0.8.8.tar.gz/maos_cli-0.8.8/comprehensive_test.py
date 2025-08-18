#!/usr/bin/env python3
"""
Comprehensive MAOS System Test Suite
Tests all major functionality components
"""

import asyncio
import json
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

async def test_core_imports():
    """Test that all core modules can be imported"""
    print_section("Testing Core Imports")
    
    modules = [
        "maos.core.orchestrator",
        "maos.core.agent_manager",
        "maos.core.claude_cli_manager",
        "maos.core.swarm_coordinator",
        "maos.interfaces.state_manager",
        "maos.interfaces.message_bus",
        "maos.models.agent",
        "maos.utils.logging_config",
    ]
    
    results = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
            results.append(True)
        except Exception as e:
            print(f"✗ {module}: {e}")
            results.append(False)
    
    return all(results)

async def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    print_section("Testing Orchestrator Initialization")
    
    try:
        from maos.core.orchestrator import Orchestrator
        
        # Create minimal config
        config = {
            'state_manager': {
                'auto_checkpoint_interval': 300,
                'max_snapshots': 50
            }
        }
        
        orchestrator = Orchestrator(component_config=config)
        print("✓ Orchestrator created successfully")
        
        # Start orchestrator
        await orchestrator.start()
        print("✓ Orchestrator started successfully")
        
        # Check components
        assert orchestrator.state_manager is not None
        print("✓ State manager initialized")
        
        assert orchestrator.agent_manager is not None
        print("✓ Agent manager initialized")
        
        assert orchestrator.message_bus is not None
        print("✓ Message bus initialized")
        
        # Shutdown
        await orchestrator.shutdown()
        print("✓ Orchestrator shutdown successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Orchestrator test failed: {e}")
        traceback.print_exc()
        return False

async def test_agent_creation():
    """Test agent creation and management"""
    print_section("Testing Agent Management")
    
    try:
        from maos.core.orchestrator import Orchestrator
        from maos.models.agent import AgentConfig, AgentRole
        
        config = {
            'state_manager': {
                'auto_checkpoint_interval': 300,
                'max_snapshots': 50
            }
        }
        
        orchestrator = Orchestrator(component_config=config)
        await orchestrator.start()
        
        # Create agent config
        agent_config = AgentConfig(
            name="test_agent",
            role=AgentRole.DEVELOPER,
            capabilities=["coding", "testing"],
            system_prompt="You are a test agent"
        )
        
        # Create agent
        agent_id = await orchestrator.agent_manager.create_agent(agent_config)
        print(f"✓ Agent created: {agent_id}")
        
        # Get agent
        agent = await orchestrator.agent_manager.get_agent(agent_id)
        assert agent is not None
        print(f"✓ Agent retrieved: {agent.name}")
        
        # List agents
        agents = await orchestrator.agent_manager.list_agents()
        assert len(agents) > 0
        print(f"✓ Listed {len(agents)} agent(s)")
        
        await orchestrator.shutdown()
        return True
        
    except Exception as e:
        print(f"✗ Agent management test failed: {e}")
        traceback.print_exc()
        return False

async def test_database_operations():
    """Test database persistence"""
    print_section("Testing Database Operations")
    
    try:
        import sqlite3
        from pathlib import Path
        
        # Check if database exists
        db_path = Path("maos.db")
        if db_path.exists():
            print(f"✓ Database exists: {db_path}")
            
            # Connect and check tables
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                print(f"✓ Found {len(tables)} table(s):")
                for table in tables:
                    print(f"  - {table[0]}")
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"    ({count} rows)")
            
            conn.close()
            return True
        else:
            print("✗ Database not found")
            return False
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        traceback.print_exc()
        return False

async def test_cli_commands():
    """Test CLI command structure"""
    print_section("Testing CLI Commands")
    
    try:
        from maos.cli.main import app
        import typer
        
        # Get all commands
        commands = []
        for name, command in app.registered_commands:
            commands.append(name)
            print(f"✓ Command registered: {name}")
        
        expected_commands = ['agent', 'task', 'status', 'recover']
        for cmd in expected_commands:
            if cmd in commands:
                print(f"✓ Required command found: {cmd}")
            else:
                print(f"✗ Missing command: {cmd}")
        
        return True
        
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        traceback.print_exc()
        return False

async def test_error_recovery():
    """Test error handling and recovery"""
    print_section("Testing Error Recovery")
    
    try:
        from maos.core.orchestrator import Orchestrator
        from maos.utils.exceptions import MAOSError
        
        config = {
            'state_manager': {
                'auto_checkpoint_interval': 300,
                'max_snapshots': 50
            }
        }
        
        orchestrator = Orchestrator(component_config=config)
        await orchestrator.start()
        
        # Test error handling with invalid agent ID
        try:
            await orchestrator.agent_manager.get_agent("invalid_id")
            print("✗ Should have raised error for invalid agent")
            result = False
        except MAOSError:
            print("✓ Properly handled invalid agent error")
            result = True
        
        await orchestrator.shutdown()
        return result
        
    except Exception as e:
        print(f"✗ Error recovery test failed: {e}")
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  MAOS COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Orchestrator Init", test_orchestrator_initialization),
        ("Agent Management", test_agent_creation),
        ("Database Operations", test_database_operations),
        ("CLI Commands", test_cli_commands),
        ("Error Recovery", test_error_recovery),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("  🎉 ALL TESTS PASSED!")
    else:
        print(f"  ⚠️  {total - passed} test(s) failed")
    
    print('='*60)
    
    return passed == total

if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)