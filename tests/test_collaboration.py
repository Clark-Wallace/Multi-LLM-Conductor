#!/usr/bin/env python3
"""
Test collaborative orchestration with two Claude instances
"""

import asyncio
from conductor import Conductor


async def test_collaboration():
    """Test two Claude instances collaborating"""
    conductor = Conductor()
    
    # Test with a simple task
    await conductor.orchestrate("Create a todo list web app with add, remove, and mark complete features")


if __name__ == "__main__":
    print("🎯 Testing Claude-to-Claude Collaboration...")
    print("Watch as Claude1 creates, Claude2 reviews and improves!\n")
    asyncio.run(test_collaboration())