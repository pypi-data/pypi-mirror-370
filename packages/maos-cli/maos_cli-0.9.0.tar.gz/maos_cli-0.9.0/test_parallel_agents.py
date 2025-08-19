#!/usr/bin/env python3
"""
Test script to verify if MAOS can spawn multiple agents and run them in parallel.
This will test various request patterns to see which ones trigger multi-agent spawning.
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from maos.core.task_decomposer_v2 import EnhancedTaskDecomposer
from maos.core.claude_sdk_executor import ClaudeSDKExecutor, AgentExecution
from maos.interfaces.sqlite_persistence import SqlitePersistence

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_decomposer_patterns():
    """Test various request patterns to see which ones create multiple agents."""
    
    persistence = SqlitePersistence(db_path="test_parallel.db")
    await persistence.initialize()
    decomposer = EnhancedTaskDecomposer(db=persistence)
    
    test_cases = [
        # Your original request
        "analyze the calculator.html and explain how it works and do a security audit",
        
        # Variations to test
        "analyze calculator.html and perform security analysis",
        "explain the code and do security audit", 
        "analyze and security",
        "do analysis and security audit",
        
        # Using explicit spawn keywords
        "spawn analyst agent and security agent to analyze calculator.html",
        "create analyst and security agents",
        "use analyst agent and security agent",
        
        # Testing the codebase analysis pattern
        "analyze the codebase and security",
        "explain the code and analyze security",
        
        # Clear multi-task requests
        "1. analyze the code 2. perform security audit",
        "first analyze the code, then do security audit",
    ]
    
    print("\n" + "="*80)
    print("TESTING TASK DECOMPOSER PATTERNS")
    print("="*80)
    
    for i, request in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Request: {request}")
        print("-" * 40)
        
        plan = await decomposer.decompose(request)
        
        print(f"✓ Subtasks created: {len(plan.subtasks)}")
        for j, task in enumerate(plan.subtasks, 1):
            print(f"  {j}. {task.assigned_agent or task.task_type.value}: {task.description[:60]}...")
        
        print(f"✓ Parallel possible: {plan.parallel_execution_possible}")
        print(f"✓ Explanation: {plan.explanation}")
    
    await persistence.close()

async def test_parallel_execution():
    """Test if multiple Claude agents can actually run in parallel."""
    
    print("\n" + "="*80)
    print("TESTING PARALLEL CLAUDE EXECUTION")
    print("="*80)
    
    executor = ClaudeSDKExecutor()
    
    # Create two simple test executions
    executions = [
        AgentExecution(
            agent_id="test-agent-1",
            task="echo 'Agent 1 says hello' && sleep 2 && echo 'Agent 1 done'",
            session_id=None,
            max_turns=1,
            timeout=10
        ),
        AgentExecution(
            agent_id="test-agent-2", 
            task="echo 'Agent 2 says hello' && sleep 2 && echo 'Agent 2 done'",
            session_id=None,
            max_turns=1,
            timeout=10
        )
    ]
    
    print("\nTesting parallel execution of 2 agents...")
    print("If truly parallel, both should complete in ~2 seconds")
    print("If sequential, it will take ~4 seconds\n")
    
    start_time = datetime.now()
    
    # Test parallel execution
    results = await executor.execute_parallel(executions)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\nExecution completed in {duration:.2f} seconds")
    
    for result in results:
        print(f"\nAgent: {result['agent_id']}")
        print(f"Success: {result['success']}")
        if result.get('error'):
            print(f"Error: {result['error']}")
    
    if duration < 3:
        print("\n✅ PARALLEL EXECUTION CONFIRMED - Both agents ran simultaneously!")
    else:
        print("\n❌ SEQUENTIAL EXECUTION - Agents ran one after another")
    
    return duration < 3

async def test_real_claude_parallel():
    """Test if real Claude instances can run in parallel."""
    
    print("\n" + "="*80)
    print("TESTING REAL CLAUDE PARALLEL EXECUTION")
    print("="*80)
    print("\nNOTE: This test requires Claude Code to be installed and authenticated")
    print("It will try to spawn 2 Claude agents with simple tasks\n")
    
    executor = ClaudeSDKExecutor()
    
    # Create two Claude executions with simple tasks
    executions = [
        AgentExecution(
            agent_id="analyst-test",
            task="List 3 benefits of Python programming",
            session_id=None,
            max_turns=1,
            timeout=60,
            agent_type="analyst"
        ),
        AgentExecution(
            agent_id="security-test",
            task="List 3 common web security vulnerabilities",
            session_id=None,
            max_turns=1,
            timeout=60,
            agent_type="security"
        )
    ]
    
    print("Starting 2 Claude agents with simple tasks...")
    print("Monitoring execution time to verify parallelism...\n")
    
    start_time = datetime.now()
    
    try:
        results = await executor.execute_parallel(executions)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✓ Execution completed in {duration:.2f} seconds")
        
        success_count = sum(1 for r in results if r.get('success'))
        print(f"✓ Successful agents: {success_count}/{len(results)}")
        
        for result in results:
            print(f"\n[{result['agent_id']}]")
            if result['success']:
                print("✅ Success")
                # Try to parse and show a snippet of the result
                try:
                    import json
                    parsed = json.loads(result.get('result', '{}'))
                    if 'result' in parsed:
                        print(f"Preview: {parsed['result'][:200]}...")
                except:
                    print(f"Preview: {str(result.get('result', ''))[:200]}...")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Check if execution was parallel
        # Claude takes 30-60s to start, so if both run in parallel, 
        # total time should be similar to single agent time
        print("\n" + "="*40)
        print("PARALLEL EXECUTION ANALYSIS:")
        print("-"*40)
        
        if success_count == 2:
            print("✅ Both agents completed successfully")
            if duration < 90:  # Less than 1.5x single agent time
                print("✅ Execution time suggests parallel processing")
            else:
                print("⚠️ Execution time suggests sequential processing")
        elif success_count == 1:
            print("⚠️ Only one agent succeeded - partial parallelism possible")
        else:
            print("❌ Both agents failed - cannot determine parallelism")
            
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests."""
    
    print("\n" + "🔬"*40)
    print("MAOS PARALLEL AGENT TESTING SUITE v0.8.8")
    print("🔬"*40)
    
    # Test 1: Task Decomposer
    await test_decomposer_patterns()
    
    # Test 2: Basic Parallel Execution (without Claude)
    # await test_parallel_execution()
    
    # Test 3: Real Claude Parallel Execution
    print("\n\nProceed with real Claude parallel test? (requires Claude Code)")
    response = input("This will spawn 2 Claude instances [y/N]: ")
    if response.lower() == 'y':
        await test_real_claude_parallel()
    else:
        print("Skipping real Claude test")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())