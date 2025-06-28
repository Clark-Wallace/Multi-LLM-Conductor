#!/usr/bin/env python3
"""
Example: How to orchestrate CLI tools with data passing
"""

import asyncio
import json
import tempfile
from pathlib import Path
from conductor import Conductor


class SmartConductor(Conductor):
    """Extended conductor that can pass data between tools"""
    
    def __init__(self):
        super().__init__()
        self.workspace = Path(tempfile.mkdtemp())
        print(f"📁 Workspace: {self.workspace}")
        
    async def orchestrate_with_data_passing(self, task: str):
        """Orchestrate with actual data passing between tools"""
        print(f"\n🎭 Smart Orchestration: {task}")
        print("=" * 60)
        
        # Phase 1: Analysis - Save output to file
        print("\n📋 Phase 1: Analysis")
        analysis_file = self.workspace / "analysis.md"
        
        # Run Claude to analyze and save output
        await self.run_tool('claude', [
            '--no-interactive',
            f'Analyze this requirement and create a detailed plan: {task}',
            '> ' + str(analysis_file)  # Redirect output to file
        ])
        
        # Phase 2: Implementation - Use analysis as input
        print("\n💻 Phase 2: Implementation")
        implementation_file = self.workspace / "implementation.py"
        
        if analysis_file.exists():
            # Pass analysis to implementation tool
            await self.run_tool('codex', [
                '--no-interactive',
                '--file', str(analysis_file),  # Use analysis as context
                f'Implement based on the analysis in {analysis_file}',
                '> ' + str(implementation_file)
            ])
        
        # Phase 3: Review - Review the implementation
        print("\n✅ Phase 3: Review")
        review_file = self.workspace / "review.md"
        
        if implementation_file.exists():
            await self.run_tool('claude', [
                '--no-interactive',
                '--file', str(implementation_file),
                'Review this implementation and suggest improvements',
                '> ' + str(review_file)
            ])
        
        # Phase 4: Show results
        print("\n📊 Results:")
        print(f"- Analysis: {analysis_file}")
        print(f"- Implementation: {implementation_file}")
        print(f"- Review: {review_file}")
        
        return {
            'analysis': analysis_file,
            'implementation': implementation_file,
            'review': review_file,
            'workspace': self.workspace
        }


async def demo_file_based_orchestration():
    """Demo: Orchestrate using files for inter-tool communication"""
    conductor = SmartConductor()
    
    # Example 1: Simple task
    result = await conductor.orchestrate_with_data_passing(
        "Create a Python function to calculate fibonacci numbers"
    )
    
    print("\n✨ Orchestration complete!")
    print(f"Files created in: {result['workspace']}")


async def demo_pipe_orchestration():
    """Demo: Orchestrate using Unix pipes"""
    conductor = Conductor()
    
    print("\n🔧 Pipe-based Orchestration")
    print("=" * 60)
    
    # Example: Pipe Claude output directly to another tool
    # claude "analyze X" | codex "implement based on stdin"
    
    # This would work with real CLI tools that support piping
    # For now, showing the concept:
    
    process = await asyncio.create_subprocess_shell(
        'echo "Design: Calculator with +,-,*,/" | cat',  # Simplified example
        stdout=asyncio.subprocess.PIPE
    )
    
    output, _ = await process.communicate()
    print("Output:", output.decode())


async def demo_json_orchestration():
    """Demo: Orchestrate using JSON for structured data"""
    conductor = Conductor()
    
    print("\n📦 JSON-based Orchestration")
    print("=" * 60)
    
    # Many CLI tools support JSON output/input
    # Example workflow:
    
    # 1. Get JSON from first tool
    analysis_json = {
        "task": "calculator",
        "features": ["add", "subtract", "multiply", "divide"],
        "language": "python"
    }
    
    # 2. Save to temp file
    json_file = Path(tempfile.mktemp(suffix='.json'))
    json_file.write_text(json.dumps(analysis_json, indent=2))
    
    # 3. Pass to next tool
    await conductor.run_tool('codex', [
        '--json-input', str(json_file),
        '--json-output',
        'implement'
    ])
    
    print(f"JSON config: {json_file}")


if __name__ == "__main__":
    print("🎯 Conductor Examples - Data Passing Patterns\n")
    
    # Run different orchestration patterns
    asyncio.run(demo_file_based_orchestration())
    # asyncio.run(demo_pipe_orchestration())
    # asyncio.run(demo_json_orchestration())