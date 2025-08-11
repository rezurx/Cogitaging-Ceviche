#!/bin/bash
# Quick activation script for Claude Code Subagents

echo "🤖 Activating Claude Code Subagents..."

# Activate virtual environment if it exists
if [ -d "subagent-env" ]; then
    source subagent-env/bin/activate
    echo "✅ Virtual environment activated"
fi

# Show available commands
echo ""
echo "Available Commands:"
echo "  python3 claude_subagent_manager.py analyze              # Analyze project"
echo "  python3 claude_subagent_manager.py list                 # List subagents"  
echo "  python3 claude_subagent_manager.py create --template X  # Create from template"
echo "  python3 claude_subagent_manager.py ui                   # Interactive UI"
echo ""
echo "🚀 Ready! Use subagents in Claude Code with commands like:"
echo '  "Use the hugo-specialist to optimize the site structure"'
echo '  "Use the content-manager to improve SEO for articles"'
echo '  "Use the python-specialist to enhance the ingestion script"'
