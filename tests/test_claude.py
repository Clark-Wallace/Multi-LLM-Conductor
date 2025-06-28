#!/usr/bin/env python3
"""
Test Claude Code CLI integration
"""

import asyncio
import subprocess
from pathlib import Path


async def test_claude_code_basic():
    """Test basic Claude Code functionality"""
    print("🧪 Testing Claude Code CLI...")
    
    # Create workspace
    workspace = Path.cwd() / 'test_workspace'
    workspace.mkdir(exist_ok=True)
    
    # Create a simple prompt file
    prompt_file = workspace / "test_prompt.md"
    prompt_file.write_text("Write a Python function that returns 'Hello, World!'")
    
    # Test 1: Check if Claude Code is available via npx
    print("\n1️⃣ Checking Claude Code availability...")
    try:
        result = subprocess.run(
            ['npx', '-y', 'claude-code', '--version'],
            capture_output=True,
            text=True
        )
        print(f"   Exit code: {result.returncode}")
        print(f"   Output: {result.stdout}")
        if result.stderr:
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure you have Node.js and npx installed")
        return
    
    # Test 2: Run Claude Code with a simple prompt
    print("\n2️⃣ Running Claude Code with test prompt...")
    try:
        # Run with explicit prompt
        cmd = ['npx', '-y', 'claude-code', str(prompt_file)]
        print(f"   Command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(workspace)
        )
        
        stdout, stderr = await process.communicate()
        
        print(f"   Exit code: {process.returncode}")
        if stdout:
            print(f"   Output preview: {stdout.decode()[:200]}...")
        if stderr:
            print(f"   Error: {stderr.decode()}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Alternative - test with stdin input
    print("\n3️⃣ Testing with direct input...")
    try:
        cmd = ['npx', '-y', 'claude-code']
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(workspace)
        )
        
        input_text = "Create a simple Python hello world function"
        stdout, stderr = await process.communicate(input_text.encode())
        
        print(f"   Exit code: {process.returncode}")
        if stdout:
            print(f"   Output: {stdout.decode()[:200]}...")
        if stderr:
            print(f"   Error: {stderr.decode()}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Test complete!")
    print(f"📁 Check outputs in: {workspace}")


if __name__ == "__main__":
    asyncio.run(test_claude_code_basic())