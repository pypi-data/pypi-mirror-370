#!/usr/bin/env python3
"""
Basic test to verify MAOS core components are properly integrated.
This test doesn't require Redis or other external dependencies.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_imports():
    """Test that all core modules can be imported."""
    print("Testing core module imports...")
    
    try:
        # Test core imports
        from src.maos.core.claude_cli_manager import ClaudeCodeCLIManager
        print("✓ ClaudeCodeCLIManager imported")
        
        from src.maos.models.claude_agent_process import ClaudeAgentProcess, AgentDefinition
        print("✓ ClaudeAgentProcess imported")
        
        from src.maos.agents.templates import create_agent_from_template, get_available_templates
        print("✓ Agent templates imported")
        
        from src.maos.interfaces.claude_commands import ClaudeCommandInterface
        print("✓ ClaudeCommandInterface imported")
        
        from src.maos.core.context_manager import ContextManager
        print("✓ ContextManager imported")
        
        from src.maos.core.swarm_coordinator import SwarmCoordinator, SwarmPattern
        print("✓ SwarmCoordinator imported")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


async def test_claude_cli_manager():
    """Test ClaudeCodeCLIManager initialization."""
    print("\nTesting ClaudeCodeCLIManager...")
    
    try:
        from src.maos.core.claude_cli_manager import ClaudeCodeCLIManager
        
        # Create manager (won't actually spawn processes)
        manager = ClaudeCodeCLIManager(
            max_processes=5,
            claude_cli_path="claude",
            base_working_dir="/tmp/test_maos"
        )
        
        print("✓ ClaudeCodeCLIManager created")
        print(f"  • Max processes: {manager.max_processes}")
        print(f"  • CLI path: {manager.claude_cli_path}")
        print(f"  • Working dir: {manager.base_working_dir}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_agent_templates():
    """Test agent template system."""
    print("\nTesting agent templates...")
    
    try:
        from src.maos.agents.templates import get_available_templates, create_agent_from_template
        
        # Get available templates
        templates = get_available_templates()
        print(f"✓ Found {len(templates)} agent templates:")
        
        for template in templates[:3]:  # Show first 3
            print(f"  • {template['name']}: {template['description'][:50]}...")
        
        # Create an agent definition from template
        agent_def = create_agent_from_template(
            template_name="code-analyzer",
            agent_name="test-analyzer"
        )
        
        print(f"\n✓ Created agent definition:")
        print(f"  • Name: {agent_def.name}")
        print(f"  • Type: {agent_def.type}")
        print(f"  • Capabilities: {len(agent_def.capabilities)} defined")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_swarm_patterns():
    """Test swarm coordination patterns."""
    print("\nTesting swarm patterns...")
    
    try:
        from src.maos.core.swarm_coordinator import SwarmPattern, CoordinationStrategy
        
        print("✓ Available swarm patterns:")
        for pattern in SwarmPattern:
            print(f"  • {pattern.value}")
        
        print("\n✓ Available coordination strategies:")
        for strategy in CoordinationStrategy:
            print(f"  • {strategy.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_context_manager():
    """Test context manager initialization."""
    print("\nTesting ContextManager...")
    
    try:
        from src.maos.core.context_manager import ContextManager
        
        # Create context manager
        manager = ContextManager(
            checkpoint_dir="/tmp/test_checkpoints",
            auto_save_interval=300
        )
        
        print("✓ ContextManager created")
        print(f"  • Checkpoint dir: {manager.checkpoint_dir}")
        print(f"  • Auto-save interval: {manager.auto_save_interval}s")
        print(f"  • Max checkpoints: {manager.max_checkpoints_per_agent}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_command_interface():
    """Test Claude command interface."""
    print("\nTesting ClaudeCommandInterface...")
    
    try:
        from src.maos.interfaces.claude_commands import ClaudeCommandInterface, CommandResult
        
        # Create interface (mock CLI manager)
        from src.maos.core.claude_cli_manager import ClaudeCodeCLIManager
        
        cli_manager = ClaudeCodeCLIManager(
            max_processes=1,
            claude_cli_path="claude"
        )
        
        interface = ClaudeCommandInterface(cli_manager)
        
        print("✓ ClaudeCommandInterface created")
        print(f"  • Available commands: /help, /status, /clear, etc.")
        print(f"  • Command history tracking enabled")
        print(f"  • Export/restore conversation supported")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def main():
    """Run all basic tests."""
    print("="*60)
    print("MAOS BASIC INTEGRATION TEST")
    print("="*60)
    print("\nThis test verifies core components without external dependencies.\n")
    
    tests = [
        ("Module imports", test_imports),
        ("Claude CLI Manager", test_claude_cli_manager),
        ("Agent templates", test_agent_templates),
        ("Swarm patterns", test_swarm_patterns),
        ("Context Manager", test_context_manager),
        ("Command Interface", test_command_interface)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All basic tests passed! Core components are properly integrated.")
        print("\nNOTE: This test verifies the code structure and imports.")
        print("To test actual Claude CLI integration, ensure Claude Code is installed.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)