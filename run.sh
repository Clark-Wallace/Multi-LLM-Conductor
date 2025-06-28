#!/bin/bash
# Simple run script for Conductor

echo "🎭 Starting Conductor CLI Orchestrator..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting server..."
python server.py