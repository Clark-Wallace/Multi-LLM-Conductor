#!/usr/bin/env python3
"""
Quick test of Conductor with Claude CLI
"""

import asyncio
from conductor import Conductor


async def test_orchestration():
    """Test the orchestration with Claude"""
    conductor = Conductor()
    
    # Simple handler to show output
    async def print_handler(data):
        # Output is already printed by conductor, this is for websocket
        pass
    
    conductor.add_output_handler(print_handler)
    
    # Run a simple task
    await conductor.orchestrate("Create a Python function to calculate fibonacci numbers")


if __name__ == "__main__":
    print("🚀 Testing Conductor with Claude CLI...")
    asyncio.run(test_orchestration())