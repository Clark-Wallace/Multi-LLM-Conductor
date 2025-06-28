#!/usr/bin/env python3
"""
Simple test of Claude CLI integration
"""

import asyncio
import subprocess
from pathlib import Path
import shutil

async def test_simple_collaboration():
    """Test basic Claude CLI functionality"""
    
    # Create test workspace
    workspace = Path.cwd() / 'test_workspace'
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir()
    
    print("🧪 Testing Claude CLI Communication")
    print("="*50)
    
    # Test 1: Simple prompt with --print flag
    print("\n1️⃣ Testing analysis mode (--print flag)...")
    cmd = [
        'claude',
        '--print',
        '--dangerously-skip-permissions',
        'Write a simple Python function that adds two numbers'
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(workspace)
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=30.0
        )
        
        if stdout:
            print("✅ Claude responded:")
            print("-"*50)
            print(stdout.decode()[:500])
            print("-"*50)
        else:
            print("❌ No output received")
            
        if stderr:
            print("⚠️ Stderr:", stderr.decode()[:200])
            
    except asyncio.TimeoutError:
        print("❌ Command timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Action mode (without --print)
    print("\n2️⃣ Testing action mode (file creation)...")
    cmd = [
        'claude',
        '--dangerously-skip-permissions',
        'Create a file called test_add.py with a function that adds two numbers'
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(workspace)
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=30.0
        )
        
        # Check if file was created
        created_files = list(workspace.glob("*.py"))
        if created_files:
            print("✅ Files created:")
            for f in created_files:
                print(f"   - {f.name}")
                # Show content
                content = f.read_text()
                print(f"   Content preview: {content[:200]}...")
        else:
            print("❌ No files created")
            
    except asyncio.TimeoutError:
        print("❌ Command timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Show final workspace contents
    print("\n📁 Final workspace contents:")
    for item in workspace.iterdir():
        print(f"   - {item.name}")
    
    return workspace

if __name__ == "__main__":
    workspace = asyncio.run(test_simple_collaboration())
    print(f"\n✅ Test complete. Check {workspace} for output files.")