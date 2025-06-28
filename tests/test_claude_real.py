#!/usr/bin/env python3
"""
Test real Claude CLI integration
"""

import asyncio
import subprocess
from pathlib import Path


async def test_claude_cli():
    """Test Claude CLI (claude-desktop)"""
    print("🧪 Testing Claude CLI...")
    
    # Check Claude version
    print("\n1️⃣ Checking Claude CLI...")
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        print(f"   Version: {result.stdout.strip()}")
    except Exception as e:
        print(f"   ❌ Claude CLI not found: {e}")
        return
    
    # Test running Claude with a simple prompt
    print("\n2️⃣ Testing Claude with prompt...")
    
    # Claude CLI expects input via stdin or chat interface
    # Let's try a non-interactive command
    cmd = ['claude', '--help']
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"   Help output: {result.stdout[:200]}...")
    
    # Test 3: Actual usage pattern
    print("\n3️⃣ Testing interactive prompt...")
    
    # Claude desktop is primarily interactive, but we can try piping
    process = await asyncio.create_subprocess_exec(
        'claude',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Send a prompt and close stdin
    prompt = "Write a simple Python hello world function and exit\n"
    stdout, stderr = await process.communicate(prompt.encode())
    
    print(f"   Exit code: {process.returncode}")
    if stdout:
        print(f"   Output: {stdout.decode()[:300]}...")
    if stderr:
        print(f"   Stderr: {stderr.decode()[:200]}...")


async def test_with_echo():
    """Test Claude with echo piping (workaround for interactive CLI)"""
    print("\n4️⃣ Testing with echo pipe...")
    
    # Use shell command with echo
    cmd = 'echo "Write a Python hello world function" | claude'
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    print(f"   Exit code: {process.returncode}")
    if stdout:
        print(f"   Output: {stdout.decode()[:300]}...")


if __name__ == "__main__":
    asyncio.run(test_claude_cli())
    # asyncio.run(test_with_echo())