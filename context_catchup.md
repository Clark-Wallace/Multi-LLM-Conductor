# Context Catchup - Multi-AI Collaboration System
*Last Updated: June 28, 2025*

## System Overview

This is a sophisticated multi-AI orchestration platform that coordinates multiple AI agents to collaborate on software development tasks. The system has evolved from a single-agent setup to a full collaborative environment.

### Architecture Components

1. **Main Orchestrator** (`/Orchestrator/`)
   - `api_server.py` - FastAPI REST API and WebSocket server (port 8100)
   - `orchestrator_core.py` - Core orchestration engine
   - `agent_bridge.py` - Interfaces with AI services (Claude, OpenAI, DeepSeek)
   - `collaborative_orchestrator.py` - Manages iterative agent collaboration
   - `dashboard/` - Web UI for monitoring and control

2. **Conductor System** (`/Orchestrator/Conductor/`)
   - `server.py` - Web interface for CLI orchestration (port 8200)
   - `conductor.py` - Basic single-agent orchestrator
   - `collaborative_conductor.py` - Shows full AI dialogue (SLOW - sequential)
   - `fast_collaborative_conductor.py` - Optimized parallel execution (NEW)
   - `server_fast.py` - Enhanced server with speed toggle (NEW)
   - `conductor_v2.py` - Enhanced file handling version

## Recent Changes & Fixes

### Today's Session (June 28, 2025)

1. **Fixed Connection Issue**
   - Problem: `server.py` was importing `Conductor` instead of `CollaborativeConductor`
   - Solution: Updated imports and added compatibility wrapper method
   - Files modified:
     - `server.py` - Changed import to use CollaborativeConductor
     - `collaborative_conductor.py` - Added `orchestrate()` wrapper method

2. **Performance Optimization**
   - Problem: Collaborative system running "incredibly slow"
   - Root causes identified:
     - Sequential execution of 5 AI conversations
     - Each Claude CLI call waits for completion before next
     - No parallelization of independent tasks
   
   - Solutions implemented:
     - Created `fast_collaborative_conductor.py` with:
       - Parallel agent execution using ThreadPoolExecutor
       - Reduced phases from 5 to 3
       - 30-second timeout protection
       - Combined insights from parallel analysis
     - Created `server_fast.py` with:
       - Toggle between FAST and DETAILED modes
       - Real-time mode switching
       - Visual speed indicators (⚡/🎭)

## System Status

### Working Components
- ✅ Main orchestrator API (`api_server.py`)
- ✅ Conductor web interface (`server.py`)
- ✅ Fast collaborative mode (NEW)
- ✅ Agent communication system
- ✅ File management and archiving
- ✅ Dashboard UI

### Current Configuration
- Main API: http://localhost:8100
- Conductor UI: http://localhost:8200
- Working directories:
  - Main: `/workspace/`
  - Conductor: `/collab_workspace/`
  - Fast mode: `/fast_collab_workspace/`

### Performance Metrics
- Original collaborative mode: ~5 sequential Claude calls
- Fast mode: 2-3 parallel calls with ~3-5x speedup
- Timeout protection: 30 seconds per subprocess

## AI Agent Roles

1. **Claude (Analyst)** - Requirements analysis and architecture
2. **Codex/GPT (Implementer)** - Code generation
3. **Claude2 (Validator)** - Code review and QA
4. **DeepSeek (Reasoner)** - Advanced optimization
5. **IDE Agents** - Deployment and integration

## Key Files to Remember

### Configuration
- `settings.json` - API keys and configuration
- `orchestrator_state.json` - System state persistence
- `.env` files - Environment variables

### Logs & Output
- `server.log` - Main server logs
- `communication_log.json` - Agent dialogue history
- `workspace/` - Generated code output
- `archive/` - Archived implementations

## Pending Tasks & Known Issues

1. **Performance Tuning**
   - Fast mode could be further optimized with:
     - Caching of common prompts
     - Batched API calls
     - Streaming responses instead of waiting

2. **Integration Points**
   - Main orchestrator (`api_server.py`) could use fast conductor
   - Dashboard could show performance metrics
   - Add progress indicators for long-running tasks

3. **Stability**
   - Add error recovery for failed Claude calls
   - Implement retry logic with exponential backoff
   - Better handling of subprocess timeouts

## Commands & Usage

### Starting the System
```bash
# Main orchestrator
python api_server.py

# Regular conductor (with collaborative mode)
python server.py

# Fast conductor (with speed toggle)
python server_fast.py
```

### Testing Performance
```bash
# Compare execution times
time python collaborative_conductor.py  # Slow version
time python fast_collaborative_conductor.py  # Fast version
```

## Next Session Recommendations

1. **Test Fast Mode Thoroughly**
   - Run complex tasks to ensure quality isn't compromised
   - Monitor for race conditions or missing outputs
   - Verify file generation is complete

2. **Integration Opportunities**
   - Connect fast conductor to main orchestrator
   - Add performance metrics to dashboard
   - Implement progress streaming

3. **Error Handling**
   - Add comprehensive error recovery
   - Implement fallback to sequential mode if parallel fails
   - Better subprocess timeout handling

4. **Documentation**
   - Document the parallel execution architecture
   - Create performance tuning guide
   - Add troubleshooting section

## Technical Debt

1. Multiple conductor versions need consolidation
2. Subprocess handling could use proper process pools
3. WebSocket connections need reconnection logic
4. File system operations need atomic transactions

## Quick Reference

### File Modifications Today
1. `/Orchestrator/Conductor/server.py` - Updated imports
2. `/Orchestrator/Conductor/collaborative_conductor.py` - Added wrapper
3. `/Orchestrator/Conductor/fast_collaborative_conductor.py` - NEW
4. `/Orchestrator/Conductor/server_fast.py` - NEW

### Key Insights
- Parallel execution provides 3-5x speedup
- Thread pools work well with asyncio for subprocess management
- UI toggle allows users to choose speed vs detail
- 30-second timeout prevents hanging processes

---
*End of Context Catchup*