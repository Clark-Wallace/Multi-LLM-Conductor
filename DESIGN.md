# Conductor Design Philosophy

## What We Built (Simple & Correct)

```
CLI Tool 1 ──subprocess──> Output ──┐
                                    ├──> Real-time Display
CLI Tool 2 ──subprocess──> Output ──┤
                                    └──> Pass data via files/pipes
```

## What We Built Before (Complex & Wrong)

```
Python Code ──API SDK──> OpenAI/Anthropic APIs ──> Hidden Processing ──> Result
     │                                                      │
     └─────────── No visibility into what's happening ──────┘
```

## Core Principles

1. **Subprocess, not SDKs** - We orchestrate CLI tools, not APIs
2. **Transparent, not opaque** - See every command and output
3. **Simple, not complex** - ~200 lines of code, not 2000
4. **Real tools, not simulations** - Actually run `claude`, `aider`, etc.

## Data Flow Patterns

### Pattern 1: File-based
```bash
claude analyze > analysis.txt
codex implement --context analysis.txt > code.py
claude review --file code.py > review.txt
```

### Pattern 2: Pipe-based
```bash
claude analyze | codex implement | claude review
```

### Pattern 3: Structured (JSON)
```bash
claude analyze --json > plan.json
codex implement --plan plan.json --json > result.json
```

## Why This Works

1. **No API Keys in Code** - CLI tools handle their own auth
2. **Tool Independence** - Each tool runs in isolation
3. **Debugging** - Can run commands manually to debug
4. **Extensibility** - Add any CLI tool without code changes

## Usage Example

Instead of:
```python
client = anthropic.Anthropic(api_key="...")
response = client.messages.create(...)  # What's happening? 🤷
```

We do:
```python
await conductor.run_tool('claude', ['analyze', 'task'])  # See everything! 👀
```

## The Difference

**Before**: "Trust me, the AI is working on it..."  
**Now**: "Here's exactly what each tool is doing, line by line"

That's Conductor. Simple subprocess orchestration with full transparency.