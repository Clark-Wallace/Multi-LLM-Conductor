#!/usr/bin/env python3
"""
Test fast collaborative conductor
"""

import asyncio
from pathlib import Path
from fast_collaborative_conductor import FastCollaborativeConductor

async def test_fast():
    conductor = FastCollaborativeConductor()
    
    # Clear workspace
    import shutil
    if conductor.working_dir.exists():
        shutil.rmtree(conductor.working_dir)
    conductor.working_dir.mkdir()
    
    print(f"⚡ Testing FAST collaborative conductor")
    print(f"📁 Output directory: {conductor.working_dir}")
    
    # Run fast orchestration
    result = await conductor.fast_orchestrate(
        "Create a simple calculator function"
    )
    
    print(f"\n📊 Results:")
    print(f"Duration: {result['duration']:.1f} seconds")
    print(f"Files created: {result['files_created']}")
    
    # List files
    for f in conductor.working_dir.glob("*"):
        print(f"  - {f.name}")

if __name__ == "__main__":
    asyncio.run(test_fast())