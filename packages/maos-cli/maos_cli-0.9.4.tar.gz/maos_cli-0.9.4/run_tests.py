#!/usr/bin/env python3
"""
Comprehensive test runner for MAOS project.
Runs all test suites and generates coverage reports.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        
        if result.returncode != 0:
            print(f"❌ Failed with exit code: {result.returncode}")
            return False
        else:
            print(f"✅ Success")
            return True
            
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Run all test suites."""
    print("\n" + "="*60)
    print("MAOS Comprehensive Test Suite")
    print("="*60)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Install test dependencies if needed
    print("\n📦 Installing test dependencies...")
    run_command(
        ["pip", "install", "-q", "pytest", "pytest-asyncio", "pytest-cov", "pytest-mock"],
        "Installing test dependencies"
    )
    
    test_suites = [
        {
            'name': 'Unit Tests - Orchestrator',
            'command': ["pytest", "tests/unit/test_orchestrator_complete.py", "-v", "--tb=short"]
        },
        {
            'name': 'Unit Tests - Agent Manager',
            'command': ["pytest", "tests/unit/test_agent_manager_complete.py", "-v", "--tb=short"]
        },
        {
            'name': 'Integration Tests - CLI',
            'command': ["pytest", "tests/integration/test_cli_integration.py", "-v", "--tb=short"]
        },
        {
            'name': 'End-to-End Tests',
            'command': ["pytest", "tests/e2e/test_end_to_end_workflows.py", "-v", "--tb=short"]
        }
    ]
    
    results = []
    
    for suite in test_suites:
        success = run_command(suite['command'], suite['name'])
        results.append((suite['name'], success))
    
    # Run all tests with coverage
    print("\n" + "="*60)
    print("Running all tests with coverage report")
    print("="*60)
    
    coverage_command = [
        "pytest",
        "tests/",
        "--cov=maos",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--tb=short",
        "-q"
    ]
    
    coverage_success = run_command(
        coverage_command,
        "All tests with coverage"
    )
    
    # Summary
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
    
    if coverage_success:
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    # Overall result
    all_passed = all(success for _, success in results)
    
    if all_passed and coverage_success:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())