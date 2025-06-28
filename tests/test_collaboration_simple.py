#!/usr/bin/env python3
"""
Test collaborative conductor with a simple task
"""

import asyncio
import sys
from pathlib import Path
from collaborative_conductor import CollaborativeConductor

async def test_collaboration():
    """Test the collaborative conductor"""
    conductor = CollaborativeConductor()
    
    # Clear workspace
    import shutil
    if conductor.working_dir.exists():
        shutil.rmtree(conductor.working_dir)
    conductor.working_dir.mkdir()
    
    print(f"🚀 Starting collaboration test...")
    print(f"📁 Output will be in: {conductor.working_dir}")
    
    # Run a simple task
    await conductor.orchestrate_with_dialogue(
        "Create a simple number guessing game in Python"
    )
    
    # Show results
    print(f"\n📊 Results:")
    files = list(conductor.working_dir.glob("*"))
    print(f"Total files created: {len(files)}")
    for f in files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

if __name__ == "__main__":
    asyncio.run(test_collaboration())