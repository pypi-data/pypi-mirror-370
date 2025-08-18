#!/usr/bin/env python3
"""
Start MAOS with Redis integration enabled.

This script initializes the MAOS orchestrator with Redis backend for
distributed state management and messaging.
"""

import asyncio
import os
import sys
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.maos.core.orchestrator import Orchestrator
from src.maos.utils.logging_config import setup_logging


async def check_redis_connection():
    """Check if Redis is available."""
    import aioredis
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    try:
        print(f"Checking Redis connection at {redis_url}...")
        redis = await aioredis.from_url(redis_url)
        await redis.ping()
        await redis.close()
        print("✓ Redis is available")
        return True
    except Exception as e:
        print(f"✗ Redis is not available: {e}")
        return False


async def main():
    """Main entry point."""
    
    print("=" * 60)
    print("MAOS - Multi-Agent Orchestration System")
    print("Starting with Redis Integration Enabled")
    print("=" * 60)
    
    # Check Redis availability
    redis_available = await check_redis_connection()
    
    if not redis_available:
        print("\nRedis is not available. You can:")
        print("1. Start Redis locally: redis-server")
        print("2. Use Docker: docker run -d -p 6379:6379 redis:7.2-alpine")
        print("3. Use docker-compose: docker compose up -d redis")
        
        response = input("\nContinue without Redis? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Load configuration
    config_file = project_root / "config" / "maos_config.yaml"
    
    if config_file.exists():
        print(f"\nLoading configuration from {config_file}")
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        print("\nUsing default configuration")
        config = {}
    
    # Override Redis setting based on availability
    if redis_available:
        config['use_redis'] = True
        if 'redis' not in config:
            config['redis'] = {}
        config['redis']['enabled'] = True
        print("✓ Redis integration enabled")
    else:
        config['use_redis'] = False
        print("✗ Running with file-based persistence")
    
    # Setup logging
    logging_config = config.get('logging', {})
    setup_logging(
        level=logging_config.get('level', 'INFO'),
        log_format=logging_config.get('format', 'json'),
        log_file=logging_config.get('output_dir', './logs') + '/maos.log' if logging_config.get('output_dir') else None
    )
    
    # Initialize orchestrator
    print("\nInitializing MAOS Orchestrator...")
    
    orchestrator = Orchestrator(
        component_config=config,
        use_redis=config.get('use_redis', redis_available)
    )
    
    # Start orchestrator
    print("Starting MAOS Orchestrator...")
    await orchestrator.start()
    
    print("\n" + "=" * 60)
    print("MAOS Orchestrator is running!")
    print("=" * 60)
    
    # Display status
    print("\nSystem Status:")
    print(f"  • Redis: {'Enabled ✓' if orchestrator.use_redis else 'Disabled ✗'}")
    print(f"  • Message Bus: {'Redis-backed' if orchestrator.use_redis else 'In-memory'}")
    print(f"  • Persistence: {'Redis' if orchestrator.use_redis else 'File-based'}")
    print(f"  • Claude Integration: {'Enabled ✓' if orchestrator.claude_command_interface else 'Disabled ✗'}")
    print(f"  • Context Manager: {'Enabled ✓' if orchestrator.context_manager else 'Disabled ✗'}")
    
    # Get component health
    health = await orchestrator.get_component_health()
    print("\nComponent Health:")
    for component, status in health.items():
        symbol = "✓" if status == "healthy" else "✗"
        print(f"  • {component}: {status} {symbol}")
    
    print("\n" + "-" * 60)
    print("Press Ctrl+C to stop the orchestrator")
    print("-" * 60)
    
    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(60)
            
            # Periodic health check
            metrics = orchestrator.get_system_metrics()
            orchestrator_metrics = metrics.get('orchestrator', {})
            
            print(f"\n[Status Update]")
            print(f"  • Uptime: {orchestrator_metrics.get('uptime_seconds', 0):.0f}s")
            print(f"  • Tasks Completed: {orchestrator_metrics.get('tasks_completed', 0)}")
            print(f"  • Active Agents: {metrics.get('agent_manager', {}).get('active_agents', 0)}")
            
            if orchestrator.use_redis:
                # Get Redis stats
                if hasattr(orchestrator.state_manager.persistence_backend, 'get_stats'):
                    redis_stats = await orchestrator.state_manager.persistence_backend.get_stats()
                    print(f"  • Redis Operations: {redis_stats.get('redis_operations', 0)}")
                    print(f"  • Redis Latency: {redis_stats.get('redis_latency_ms', 0):.1f}ms")
            
    except KeyboardInterrupt:
        print("\n\nShutting down MAOS Orchestrator...")
        await orchestrator.stop()
        print("MAOS Orchestrator stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)