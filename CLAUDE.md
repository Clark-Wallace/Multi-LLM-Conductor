# CLAUDE.md - AI Assistant Context & Instructions

## Project Overview
This is a Multi-AI Collaboration System (Orchestrator) that coordinates multiple AI agents to work together on software development tasks.

## System Architecture

### Main Components
1. **Orchestrator** (Parent Directory)
   - `api_server.py` - Main FastAPI server (port 8100)
   - `orchestrator_core.py` - Core orchestration logic
   - `agent_bridge.py` - AI service interfaces
   - `collaborative_orchestrator.py` - Multi-agent collaboration

2. **Conductor** (Subdirectory: `/Conductor/`)
   - `server.py` - Web UI for CLI orchestration (port 8200)
   - `collaborative_conductor.py` - Shows AI dialogue (SLOW)
   - `fast_collaborative_conductor.py` - Parallel execution (FAST)
   - `server_fast.py` - Enhanced UI with speed toggle

## Important Commands

### Linting & Type Checking
```bash
# Python linting (if configured)
python -m pylint *.py
python -m mypy *.py

# Or use ruff if available
ruff check .
```

### Starting Services
```bash
# Main orchestrator
python api_server.py

# Fast conductor (recommended)
python Conductor/server_fast.py

# Access points
# Main dashboard: http://localhost:8100
# Conductor UI: http://localhost:8200
```

## Recent Updates (June 28, 2025)

### Performance Optimizations
1. Created parallel execution system (`fast_collaborative_conductor.py`)
2. Added speed toggle to UI (FAST vs DETAILED modes)
3. Reduced execution time by 3-5x through parallelization

### Bug Fixes
1. Fixed server.py connection to use CollaborativeConductor
2. Added compatibility wrapper methods
3. Implemented 30-second timeout protection

## Key Features

### Fast Mode
- Parallel agent execution
- Combined insights from multiple agents
- Streamlined 3-phase process
- ThreadPoolExecutor for efficiency

### Detailed Mode
- Full 5-phase collaboration
- Complete dialogue visibility
- Step-by-step agent communication
- Comprehensive review cycles

## Working Directories
- Main workspace: `./workspace/`
- Collaborative: `./collab_workspace/`
- Fast mode: `./fast_collab_workspace/`
- Archives: `./archive/`

## API Keys Required
Configure in `settings.json`:
- OpenAI API key (for GPT/Codex)
- Anthropic API key (for Claude)
- DeepSeek API key (optional)

## Testing & Validation

### Performance Testing
```bash
# Compare modes
time python Conductor/collaborative_conductor.py
time python Conductor/fast_collaborative_conductor.py
```

### Integration Testing
1. Start main orchestrator
2. Start conductor server
3. Submit test task through UI
4. Verify file generation

## Common Issues & Solutions

### Slow Performance
- Use Fast Mode (toggle in UI)
- Check API rate limits
- Monitor subprocess timeouts

### Connection Issues
- Verify ports 8100/8200 are free
- Check WebSocket connections
- Restart services if needed

### File Generation
- Check working directories exist
- Verify write permissions
- Monitor workspace folders

## Development Guidelines

### When Making Changes
1. Test both FAST and DETAILED modes
2. Verify WebSocket communication
3. Check file generation consistency
4. Monitor performance impact

### Code Style
- Use type hints where possible
- Follow async/await patterns
- Handle exceptions gracefully
- Add logging for debugging

## Future Enhancements
1. Streaming responses for real-time updates
2. Caching for common prompts
3. Advanced error recovery
4. Progress indicators
5. Performance metrics dashboard

## Quick Debugging
```bash
# Check running processes
ps aux | grep python

# Monitor logs
tail -f server.log

# Test WebSocket connection
wscat -c ws://localhost:8200/ws
```

## Session Notes
- System configured for multi-AI collaboration
- Performance optimizations implemented
- UI supports mode switching
- All components tested and working

---
*Last updated: June 28, 2025*
*Next session: Test fast mode with complex tasks*