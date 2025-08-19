#!/usr/bin/env python3
"""
Definitive test to verify if Claude Code CLI can run multiple processes in parallel.
This tests the actual Claude CLI, not just Python's asyncio capabilities.
"""

import asyncio
import subprocess
import time
from datetime import datetime
import json

async def run_claude_process(task_id: str, prompt: str):
    """Run a single Claude process and track timing."""
    start_time = datetime.now()
    
    cmd = [
        "claude", 
        "-p",
        "--output-format", "json",
        prompt
    ]
    
    print(f"[{task_id}] Starting at {start_time.strftime('%H:%M:%S.%f')[:-3]}")
    
    try:
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for completion
        stdout, stderr = await process.communicate()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"[{task_id}] Completed at {end_time.strftime('%H:%M:%S.%f')[:-3]} (Duration: {duration:.2f}s)")
        
        # Try to parse result
        try:
            result = json.loads(stdout.decode())
            success = result.get('subtype') == 'success'
        except:
            success = process.returncode == 0
            
        return {
            "task_id": task_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": duration,
            "success": success,
            "error": stderr.decode() if stderr else None
        }
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"[{task_id}] Failed at {end_time.strftime('%H:%M:%S.%f')[:-3]} - {str(e)}")
        return {
            "task_id": task_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": duration,
            "success": False,
            "error": str(e)
        }

async def test_parallel_claude():
    """Test if multiple Claude CLI processes can run in parallel."""
    
    print("\n" + "="*80)
    print("CLAUDE CLI PARALLEL EXECUTION TEST")
    print("="*80)
    print("\nThis test will spawn 3 Claude processes with simple prompts.")
    print("If they run in PARALLEL, all should start within 1 second of each other.")
    print("If they run SEQUENTIALLY, each will wait for the previous to complete.\n")
    
    # Create 3 simple tasks
    tasks = [
        ("Agent-1", "What is 2+2? Answer in one word only."),
        ("Agent-2", "What is the capital of France? Answer in one word only."),
        ("Agent-3", "What color is the sky? Answer in one word only.")
    ]
    
    print("Starting 3 Claude processes...\n")
    
    # Run all tasks in parallel using asyncio.gather
    overall_start = datetime.now()
    
    results = await asyncio.gather(*[
        run_claude_process(task_id, prompt)
        for task_id, prompt in tasks
    ])
    
    overall_end = datetime.now()
    overall_duration = (overall_end - overall_start).total_seconds()
    
    print("\n" + "-"*80)
    print("RESULTS ANALYSIS")
    print("-"*80)
    
    # Analyze timing
    start_times = [datetime.fromisoformat(r['start_time']) for r in results]
    end_times = [datetime.fromisoformat(r['end_time']) for r in results]
    
    # Calculate start time spread
    earliest_start = min(start_times)
    latest_start = max(start_times)
    start_spread = (latest_start - earliest_start).total_seconds()
    
    # Calculate individual durations
    durations = [r['duration'] for r in results]
    avg_duration = sum(durations) / len(durations)
    
    print(f"Overall duration: {overall_duration:.2f} seconds")
    print(f"Average individual duration: {avg_duration:.2f} seconds")
    print(f"Start time spread: {start_spread:.2f} seconds")
    print(f"Successful processes: {sum(1 for r in results if r['success'])}/{len(results)}")
    
    print("\n" + "-"*80)
    print("CONCLUSION")
    print("-"*80)
    
    # Determine if execution was parallel
    if start_spread < 2.0:  # All started within 2 seconds
        print("✅ PARALLEL EXECUTION CONFIRMED!")
        print(f"   All {len(tasks)} processes started within {start_spread:.2f} seconds of each other.")
        
        if overall_duration < avg_duration * 1.5:
            print(f"   Total time ({overall_duration:.2f}s) is less than 1.5x average individual time ({avg_duration:.2f}s).")
            print("   This confirms true parallel execution.")
        else:
            print(f"   Total time ({overall_duration:.2f}s) suggests some serialization despite parallel starts.")
    else:
        print("❌ SEQUENTIAL EXECUTION DETECTED!")
        print(f"   Process starts were spread over {start_spread:.2f} seconds.")
        print("   This indicates processes are queuing and running one after another.")
    
    print("\n" + "="*80)
    
    return start_spread < 2.0

async def test_python_parallel():
    """Control test to verify Python's asyncio works correctly."""
    
    print("\n" + "="*80)
    print("PYTHON ASYNCIO CONTROL TEST")
    print("="*80)
    print("Testing Python's ability to run async tasks in parallel...\n")
    
    async def dummy_task(task_id: str, delay: float):
        start = datetime.now()
        print(f"[{task_id}] Starting at {start.strftime('%H:%M:%S.%f')[:-3]}")
        await asyncio.sleep(delay)
        end = datetime.now()
        print(f"[{task_id}] Completed at {end.strftime('%H:%M:%S.%f')[:-3]}")
        return (end - start).total_seconds()
    
    start = datetime.now()
    results = await asyncio.gather(
        dummy_task("Python-1", 2),
        dummy_task("Python-2", 2),
        dummy_task("Python-3", 2)
    )
    total = (datetime.now() - start).total_seconds()
    
    print(f"\nTotal time for 3x 2-second tasks: {total:.2f} seconds")
    if total < 3:
        print("✅ Python asyncio is working correctly (parallel execution)")
    else:
        print("❌ Python asyncio issue detected (sequential execution)")
    
    return total < 3

async def main():
    """Run all tests."""
    
    print("\n🔬 CLAUDE PARALLEL EXECUTION CAPABILITY TEST")
    print("=" * 80)
    
    # First verify Python asyncio works
    python_ok = await test_python_parallel()
    
    if not python_ok:
        print("\n⚠️ Python asyncio not working correctly. Results may be unreliable.")
        return
    
    # Now test Claude CLI
    print("\n" + "="*80)
    print("Proceeding with Claude CLI test...")
    print("NOTE: This requires 'claude' CLI to be installed and authenticated.")
    response = input("\nContinue? This will spawn 3 Claude processes [y/N]: ")
    
    if response.lower() == 'y':
        is_parallel = await test_parallel_claude()
        
        if is_parallel:
            print("\n🎉 FINAL VERDICT: Claude CLI SUPPORTS PARALLEL EXECUTION!")
        else:
            print("\n⚠️ FINAL VERDICT: Claude CLI appears to run SEQUENTIALLY")
    else:
        print("Test cancelled.")

if __name__ == "__main__":
    asyncio.run(main())