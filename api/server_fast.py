#!/usr/bin/env python3
"""
Conductor Server - With Fast Mode Option
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from orchestration.collaborative_conductor_v2 import CollaborativeConductor
from orchestration.fast_collaborative_conductor_v2 import FastCollaborativeConductor
import json

app = FastAPI()

# Global conductor instances
slow_conductor = CollaborativeConductor()
fast_conductor = FastCollaborativeConductor()
current_conductor = fast_conductor  # Default to fast mode
connected_clients = []


@app.get("/")
async def get():
    """Serve the enhanced HTML interface with speed toggle"""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Multi-LLM Conductor - Fast Collaborative Orchestrator</title>
    <style>
        body {
            font-family: 'Monaco', 'Menlo', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            color: #569cd6;
            font-size: 24px;
            margin-bottom: 20px;
        }
        
        .input-section {
            background: #252526;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        input {
            width: 50%;
            padding: 10px;
            background: #3c3c3c;
            border: 1px solid #464647;
            color: #d4d4d4;
            font-family: inherit;
            font-size: 14px;
            border-radius: 4px;
        }
        
        button {
            padding: 10px 20px;
            background: #007acc;
            color: white;
            border: none;
            border-radius: 4px;
            font-family: inherit;
            cursor: pointer;
            margin-left: 10px;
        }
        
        button:hover {
            background: #005a9e;
        }
        
        .toggle-section {
            float: right;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .toggle-switch {
            position: relative;
            width: 60px;
            height: 28px;
        }
        
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 28px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background-color: #4ec9b0;
        }
        
        input:checked + .slider:before {
            transform: translateX(32px);
        }
        
        .mode-label {
            color: #4ec9b0;
            font-weight: bold;
        }
        
        .output-section {
            background: #1e1e1e;
            border: 1px solid #464647;
            border-radius: 8px;
            padding: 20px;
            height: 600px;
            overflow-y: auto;
        }
        
        .output-line {
            margin: 2px 0;
            font-size: 13px;
            line-height: 1.4;
        }
        
        .timestamp {
            color: #858585;
        }
        
        .tool-claude {
            color: #c586c0;
        }
        
        .phase-header {
            color: #dcdcaa;
            font-weight: bold;
            margin: 10px 0;
            border-bottom: 1px solid #464647;
            padding-bottom: 5px;
        }
        
        .status-connected {
            color: #4ec9b0;
            font-size: 12px;
        }
        
        .status-disconnected {
            color: #f44747;
            font-size: 12px;
        }
        
        .speed-indicator {
            color: #ffcc00;
            font-size: 18px;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <span id="speed-indicator" class="speed-indicator">⚡</span> Multi-LLM Conductor
            <span id="status" class="status-disconnected">● Disconnected</span>
        </h1>
        
        <div class="input-section">
            <input type="text" id="task-input" placeholder="Enter a task to orchestrate..." 
                   value="Create a simple calculator web app">
            <button onclick="orchestrate()">Orchestrate</button>
            <button onclick="clearOutput()">Clear</button>
            
            <div class="toggle-section">
                <span>Mode:</span>
                <label class="toggle-switch">
                    <input type="checkbox" id="speed-toggle" checked onchange="toggleSpeed()">
                    <span class="slider"></span>
                </label>
                <span id="mode-label" class="mode-label">FAST</span>
            </div>
        </div>
        
        <div class="output-section" id="output">
            <div class="output-line">⚡ Ready for fast collaborative orchestration...</div>
        </div>
    </div>
    
    <script>
        let ws = null;
        const output = document.getElementById('output');
        const status = document.getElementById('status');
        const taskInput = document.getElementById('task-input');
        const speedToggle = document.getElementById('speed-toggle');
        const modeLabel = document.getElementById('mode-label');
        const speedIndicator = document.getElementById('speed-indicator');
        
        function connect() {
            ws = new WebSocket('ws://localhost:8200/ws');
            
            ws.onopen = () => {
                status.textContent = '● Connected';
                status.className = 'status-connected';
                addOutput('Connected to Fast Conductor server', 'system');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'output') {
                    addOutput(data.line, data.tool, data.timestamp);
                } else if (data.type === 'phase') {
                    addPhaseHeader(data.phase);
                }
            };
            
            ws.onclose = () => {
                status.textContent = '● Disconnected';
                status.className = 'status-disconnected';
                addOutput('Disconnected from server', 'system');
                setTimeout(connect, 3000);
            };
        }
        
        function addOutput(line, tool = 'system', timestamp = null) {
            const div = document.createElement('div');
            div.className = 'output-line';
            
            if (timestamp) {
                div.innerHTML = `<span class="timestamp">[${timestamp}]</span> `;
            }
            
            if (tool !== 'system') {
                div.innerHTML += `<span class="tool-${tool}">${tool}:</span> `;
            }
            
            div.innerHTML += escapeHtml(line);
            
            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        }
        
        function addPhaseHeader(phase) {
            const div = document.createElement('div');
            div.className = 'phase-header';
            div.textContent = phase;
            output.appendChild(div);
        }
        
        function orchestrate() {
            const task = taskInput.value.trim();
            if (!task) return;
            
            const isFast = speedToggle.checked;
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ 
                    action: 'orchestrate', 
                    task: task,
                    fast: isFast 
                }));
                addPhaseHeader(`Starting ${isFast ? 'FAST' : 'detailed'} orchestration: ${task}`);
            }
        }
        
        function clearOutput() {
            const isFast = speedToggle.checked;
            output.innerHTML = `<div class="output-line">${isFast ? '⚡' : '🎭'} Ready for ${isFast ? 'fast' : 'detailed'} collaborative orchestration...</div>`;
        }
        
        function toggleSpeed() {
            const isFast = speedToggle.checked;
            modeLabel.textContent = isFast ? 'FAST' : 'DETAILED';
            speedIndicator.textContent = isFast ? '⚡' : '🎭';
            speedIndicator.style.color = isFast ? '#ffcc00' : '#569cd6';
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ action: 'toggle_speed', fast: isFast }));
            }
            
            clearOutput();
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Connect on load
        connect();
        
        // Enter key submits
        taskInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') orchestrate();
        });
    </script>
</body>
</html>
    """)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time CLI output"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    # Set up output handler
    async def output_handler(data):
        try:
            await websocket.send_json({
                'type': 'output',
                'tool': data['tool'],
                'line': data['line'],
                'timestamp': data['timestamp']
            })
        except:
            pass
    
    global current_conductor
    current_conductor.add_output_handler(output_handler)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data['action'] == 'orchestrate':
                # Use fast or slow conductor based on setting
                is_fast = data.get('fast', True)
                conductor = fast_conductor if is_fast else slow_conductor
                
                # Run orchestration in background
                asyncio.create_task(conductor.orchestrate(data['task']))
                
            elif data['action'] == 'toggle_speed':
                # Switch conductor mode
                current_conductor = fast_conductor if data['fast'] else slow_conductor
                current_conductor.add_output_handler(output_handler)
                
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        if output_handler in current_conductor.output_handlers:
            current_conductor.output_handlers.remove(output_handler)


if __name__ == "__main__":
    import uvicorn
    print("⚡ Starting Multi-LLM Conductor server on http://localhost:8200")
    print("Toggle between FAST and DETAILED modes in the UI")
    uvicorn.run(app, host="0.0.0.0", port=8200)