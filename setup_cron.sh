#!/bin/bash
# Script to setup cron jobs for automation

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="$SCRIPT_DIR/subagent-env/bin/python3"
AUTOMATION_SCRIPT="$SCRIPT_DIR/automation_manager.py"

# Add cron jobs
(crontab -l 2>/dev/null; echo "# Cogitating Ceviche Automation") | crontab -
(crontab -l 2>/dev/null; echo "0 */6 * * * cd $SCRIPT_DIR && $PYTHON_PATH $AUTOMATION_SCRIPT run-once >> automation_logs/cron.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "*/30 * * * * cd $SCRIPT_DIR && $PYTHON_PATH $AUTOMATION_SCRIPT health-check >> automation_logs/cron.log 2>&1") | crontab -

echo "Cron jobs added successfully!"
echo "Content ingestion will run every 6 hours"
echo "Health checks will run every 30 minutes"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove cron jobs: crontab -r"
