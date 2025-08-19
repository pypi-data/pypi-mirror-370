#!/usr/bin/env python3
"""
Example demonstrating MAOS swarm coordination with Claude agents.

This example shows how to:
1. Create an agent swarm with multiple Claude agents
2. Execute tasks using different coordination patterns
3. Monitor swarm progress and results
"""

import asyncio
import yaml
from pathlib import Path
from uuid import uuid4
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.maos.core.orchestrator import Orchestrator
from src.maos.core.swarm_coordinator import SwarmPattern, CoordinationStrategy
from src.maos.models.task import Task, TaskPriority
from src.maos.utils.logging_config import setup_logging


async def parallel_code_review_example(orchestrator):
    """
    Example: Multiple agents review different parts of a codebase in parallel.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Parallel Code Review")
    print("="*60)
    
    # Create a swarm for code review
    swarm_id = await orchestrator.create_agent_swarm(
        name="code_review_swarm",
        pattern=SwarmPattern.PARALLEL,
        strategy=CoordinationStrategy.CAPABILITY_BASED,
        agent_templates=["code-analyzer", "security-auditor", "test-engineer"],
        min_agents=3,
        max_agents=5
    )
    
    print(f"✓ Created code review swarm: {swarm_id}")
    
    # Create review tasks for different modules
    review_task = Task(
        name="comprehensive_code_review",
        description="Review the entire codebase for quality, security, and testing",
        priority=TaskPriority.HIGH,
        metadata={
            'subtasks': [
                {
                    'name': 'analyze_code_quality',
                    'description': 'Analyze code quality, patterns, and best practices',
                    'metadata': {'focus': 'quality'}
                },
                {
                    'name': 'security_audit',
                    'description': 'Perform security audit and vulnerability scanning',
                    'metadata': {'focus': 'security'}
                },
                {
                    'name': 'test_coverage_analysis',
                    'description': 'Analyze test coverage and suggest improvements',
                    'metadata': {'focus': 'testing'}
                }
            ]
        }
    )
    
    # Execute parallel review
    results = await orchestrator.execute_swarm_task(
        swarm_id=swarm_id,
        task=review_task,
        execution_mode="parallel"
    )
    
    print("\n📊 Review Results:")
    print(f"  • Success rate: {results.get('success_rate', 0):.1%}")
    print(f"  • Total time: {results.get('total_time', 0):.1f}s")
    print(f"  • Successful reviews: {len(results.get('successful', []))}")
    print(f"  • Failed reviews: {len(results.get('failed', []))}")
    
    # Get swarm status
    status = await orchestrator.get_swarm_status(swarm_id)
    if status:
        print(f"\n📈 Swarm Metrics:")
        metrics = status.get('metrics', {})
        print(f"  • Active agents: {metrics.get('active_agents', 0)}")
        print(f"  • Completed tasks: {metrics.get('completed_tasks', 0)}")
        print(f"  • Success rate: {metrics.get('success_rate', 0):.1%}")
    
    # Shutdown swarm
    await orchestrator.shutdown_swarm(swarm_id)
    print("✓ Swarm shutdown complete")


async def pipeline_development_example(orchestrator):
    """
    Example: Pipeline pattern for sequential development workflow.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Pipeline Development Workflow")
    print("="*60)
    
    # Create a development pipeline swarm
    swarm_id = await orchestrator.create_agent_swarm(
        name="development_pipeline",
        pattern=SwarmPattern.PIPELINE,
        strategy=CoordinationStrategy.CAPABILITY_BASED,
        agent_templates=[
            "architect",
            "web-developer",
            "test-engineer",
            "documentation-writer"
        ],
        min_agents=4
    )
    
    print(f"✓ Created development pipeline swarm: {swarm_id}")
    
    # Create pipeline task
    pipeline_task = Task(
        name="feature_development_pipeline",
        description="Develop a new feature through architecture, implementation, testing, and documentation",
        priority=TaskPriority.HIGH,
        metadata={
            'pipeline_stages': [
                {
                    'name': 'architecture_design',
                    'description': 'Design the architecture for the new feature',
                    'metadata': {'stage': 'design'}
                },
                {
                    'name': 'implementation',
                    'description': 'Implement the feature based on the architecture',
                    'metadata': {'stage': 'development'}
                },
                {
                    'name': 'testing',
                    'description': 'Write and run tests for the implementation',
                    'metadata': {'stage': 'testing'}
                },
                {
                    'name': 'documentation',
                    'description': 'Document the feature and update guides',
                    'metadata': {'stage': 'documentation'}
                }
            ]
        }
    )
    
    # Execute pipeline
    result = await orchestrator.execute_swarm_task(
        swarm_id=swarm_id,
        task=pipeline_task,
        execution_mode="pipeline"
    )
    
    print("\n🔄 Pipeline Execution Complete")
    print(f"  • Final result: {type(result).__name__}")
    
    # Shutdown swarm
    await orchestrator.shutdown_swarm(swarm_id)
    print("✓ Pipeline swarm shutdown")


async def consensus_decision_example(orchestrator):
    """
    Example: Multiple agents reach consensus on a critical decision.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Consensus-Based Decision Making")
    print("="*60)
    
    # Create a consensus swarm
    swarm_id = await orchestrator.create_agent_swarm(
        name="consensus_swarm",
        pattern=SwarmPattern.CONSENSUS,
        strategy=CoordinationStrategy.ROUND_ROBIN,
        agent_templates=["architect", "security-auditor", "web-developer"],
        min_agents=3
    )
    
    print(f"✓ Created consensus swarm: {swarm_id}")
    
    # Create decision task
    decision_task = Task(
        name="technology_stack_decision",
        description="Decide on the best technology stack for a new microservice",
        priority=TaskPriority.CRITICAL,
        metadata={
            'options': ['Node.js + Express', 'Python + FastAPI', 'Go + Gin'],
            'criteria': ['performance', 'scalability', 'maintainability', 'team expertise'],
            'require_consensus': True
        }
    )
    
    # Execute with consensus
    results = await orchestrator.execute_swarm_task(
        swarm_id=swarm_id,
        task=decision_task,
        execution_mode="consensus"
    )
    
    print("\n🤝 Consensus Results:")
    print(f"  • Consensus reached: {results.get('consensus_reached', False)}")
    if results.get('consensus_reached'):
        print(f"  • Agreement ratio: {results.get('agreement_ratio', 0):.1%}")
        print(f"  • Decision: {results.get('consensus_result', 'N/A')}")
    else:
        print(f"  • Reason: {results.get('reason', 'Unknown')}")
    
    # Shutdown swarm
    await orchestrator.shutdown_swarm(swarm_id)
    print("✓ Consensus swarm shutdown")


async def map_reduce_analysis_example(orchestrator):
    """
    Example: Map-reduce pattern for analyzing large datasets.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Map-Reduce Data Analysis")
    print("="*60)
    
    # Create a map-reduce swarm
    swarm_id = await orchestrator.create_agent_swarm(
        name="analysis_swarm",
        pattern=SwarmPattern.MAP_REDUCE,
        strategy=CoordinationStrategy.LOAD_BALANCED,
        agent_templates=["data-analyst", "data-analyst", "data-analyst"],
        min_agents=3,
        max_agents=5
    )
    
    print(f"✓ Created map-reduce swarm: {swarm_id}")
    
    # Create map-reduce task
    analysis_task = Task(
        name="log_analysis",
        description="Analyze application logs for patterns and anomalies",
        priority=TaskPriority.MEDIUM,
        metadata={
            'map_task': {
                'name': 'analyze_log_chunk',
                'description': 'Analyze a chunk of log data for patterns',
                'metadata': {'analysis_type': 'pattern_detection'}
            },
            'reduce_task': {
                'name': 'aggregate_patterns',
                'description': 'Aggregate patterns from all chunks',
                'metadata': {'aggregation_type': 'frequency_analysis'}
            },
            'data_chunks': [
                {'log_file': 'app.log', 'lines': '1-1000'},
                {'log_file': 'app.log', 'lines': '1001-2000'},
                {'log_file': 'app.log', 'lines': '2001-3000'}
            ]
        }
    )
    
    # Execute map-reduce
    result = await orchestrator.execute_swarm_task(
        swarm_id=swarm_id,
        task=analysis_task,
        execution_mode="map_reduce"
    )
    
    print("\n🗂️ Map-Reduce Analysis Complete")
    print(f"  • Result type: {type(result).__name__}")
    
    # Shutdown swarm
    await orchestrator.shutdown_swarm(swarm_id)
    print("✓ Analysis swarm shutdown")


async def main():
    """Main function to run swarm examples."""
    
    print("="*60)
    print("MAOS Swarm Coordination Examples")
    print("="*60)
    
    # Load configuration
    config_file = project_root / "config" / "maos_config.yaml"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {
            'claude_integration': {
                'enabled': True,
                'cli_command': 'claude',
                'working_directory': './claude_workspaces'
            },
            'swarm_coordinator': {
                'enable_monitoring': True
            }
        }
    
    # Setup logging
    setup_logging(level='INFO')
    
    # Initialize orchestrator
    print("\nInitializing MAOS Orchestrator...")
    orchestrator = Orchestrator(component_config=config)
    
    # Start orchestrator
    await orchestrator.start()
    print("✓ Orchestrator started")
    
    try:
        # Run examples
        print("\nSelect an example to run:")
        print("1. Parallel Code Review")
        print("2. Pipeline Development Workflow")
        print("3. Consensus-Based Decision Making")
        print("4. Map-Reduce Data Analysis")
        print("5. Run All Examples")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            await parallel_code_review_example(orchestrator)
        elif choice == '2':
            await pipeline_development_example(orchestrator)
        elif choice == '3':
            await consensus_decision_example(orchestrator)
        elif choice == '4':
            await map_reduce_analysis_example(orchestrator)
        elif choice == '5':
            # Run all examples
            await parallel_code_review_example(orchestrator)
            await pipeline_development_example(orchestrator)
            await consensus_decision_example(orchestrator)
            await map_reduce_analysis_example(orchestrator)
        else:
            print("Invalid choice")
        
    finally:
        # Shutdown orchestrator
        print("\n" + "="*60)
        print("Shutting down orchestrator...")
        await orchestrator.stop()
        print("✓ Orchestrator stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()