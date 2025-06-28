#!/bin/bash
# Simple run script for Multi-LLM Conductor

echo "🎭 Starting Multi-LLM Conductor..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting server..."
python api/server_fast.py