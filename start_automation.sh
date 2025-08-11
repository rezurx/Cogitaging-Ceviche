#!/bin/bash
# Quick start script for automation system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Starting Cogitating Ceviche Automation..."

# Activate virtual environment
if [ -d "subagent-env" ]; then
    source subagent-env/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check dependencies
python3 -c "import schedule, rich, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Please run setup_automation.sh first"
    exit 1
fi

# Start automation manager
echo "🚀 Starting automation manager..."
python3 automation_manager.py start
