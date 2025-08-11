#!/bin/bash
# Maintenance script for automation system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧹 Running maintenance tasks..."

# Activate virtual environment
if [ -d "subagent-env" ]; then
    source subagent-env/bin/activate
fi

# Clean up old log files (older than 30 days)
find automation_logs -name "*.log*" -mtime +30 -delete 2>/dev/null || true
echo "✅ Cleaned up old log files"

# Clean up old backups (older than 7 days)
find backups -name "site_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true
echo "✅ Cleaned up old backups"

# Update dependencies
echo "📦 Updating Python dependencies..."
pip install --upgrade -r requirements.txt

# Run health check
echo "🏥 Running health check..."
python3 automation_manager.py health-check

echo "✨ Maintenance completed!"
