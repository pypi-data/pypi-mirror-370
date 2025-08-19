#!/usr/bin/env python3
"""Quick test to find where it hangs"""

import asyncio
from pathlib import Path

async def quick_test():
    print("1. Importing...")
    from src.maos.cli.natural_language_v7 import NaturalLanguageProcessorV7
    
    print("2. Creating processor...")
    processor = NaturalLanguageProcessorV7(
        db_path=Path("./maos.db"),
        api_key=None
    )
    
    print("3. Initializing...")
    await processor.initialize()
    
    print("4. Checking orchestrator...")
    print(f"   Orchestrator: {processor.orchestrator}")
    print(f"   Persistence: {processor.persistence}")
    
    print("5. Calling orchestrate directly...")
    # Try calling orchestrate with a simple request
    from src.maos.core.orchestrator_v7 import OrchestratorV7
    
    # The problem might be in the orchestrator itself
    print("   Creating test orchestrator...")
    test_orch = OrchestratorV7(processor.persistence, api_key=None)
    
    print("6. Done!")

if __name__ == "__main__":
    asyncio.run(quick_test())