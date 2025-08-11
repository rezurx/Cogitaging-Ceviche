#!/bin/bash

# Setup script for Cogitating Ceviche Automation System
# This script installs dependencies and sets up the automation system

set -e  # Exit on any error

echo "🚀 Setting up Cogitating Ceviche Automation System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "hugo.toml" ]; then
    print_error "This script must be run from the cogitating-ceviche project root directory"
    exit 1
fi

# Create necessary directories
print_status "Creating automation directories..."
mkdir -p automation_logs
mkdir -p backups
mkdir -p .claude/agents

# Check if virtual environment exists
if [ ! -d "subagent-env" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv subagent-env
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source subagent-env/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install additional dependencies for automation
print_status "Installing automation dependencies..."
pip install schedule APScheduler

# Install existing requirements
if [ -f "requirements.txt" ]; then
    print_status "Installing existing requirements..."
    pip install -r requirements.txt
else
    print_status "Installing basic requirements..."
    pip install rich questionary PyYAML feedparser beautifulsoup4 lxml requests colorama click
fi

# Check Hugo installation
print_status "Checking Hugo installation..."
if command -v hugo &> /dev/null; then
    HUGO_VERSION=$(hugo version)
    print_success "Hugo is installed: $HUGO_VERSION"
else
    print_warning "Hugo is not installed. Please install Hugo 0.128.0 or later."
    print_status "Install instructions: https://gohugo.io/installation/"
fi

# Check git installation and setup
print_status "Checking git configuration..."
if command -v git &> /dev/null; then
    if git rev-parse --git-dir > /dev/null 2>&1; then
        print_success "Git repository detected"
    else
        print_warning "Not in a git repository. Consider initializing git for better deployment options."
    fi
else
    print_warning "Git is not installed. Some deployment features may not work."
fi

# Make scripts executable
print_status "Setting script permissions..."
chmod +x automation_manager.py
chmod +x activate_subagents.sh
chmod +x ingest_external_articles.py

# Initialize configuration if it doesn't exist
if [ ! -f "automation_config.yaml" ]; then
    print_status "Configuration file not found. Creating default configuration..."
    python3 automation_manager.py init-config --config automation_config.yaml
fi

# Create systemd service file (optional)
create_systemd_service() {
    local service_file="/tmp/cogitating-ceviche-automation.service"
    local current_user=$(whoami)
    local working_dir=$(pwd)
    local python_path="$working_dir/subagent-env/bin/python3"
    
    cat > "$service_file" << EOF
[Unit]
Description=Cogitating Ceviche Automation Manager
After=network.target
Wants=network.target

[Service]
Type=simple
User=$current_user
WorkingDirectory=$working_dir
Environment=PATH=$working_dir/subagent-env/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$python_path $working_dir/automation_manager.py start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Systemd service file created at $service_file"
    print_status "To install the service, run:"
    print_status "  sudo cp $service_file /etc/systemd/system/"
    print_status "  sudo systemctl daemon-reload"
    print_status "  sudo systemctl enable cogitating-ceviche-automation.service"
    print_status "  sudo systemctl start cogitating-ceviche-automation.service"
}

# Create cron job setup script
create_cron_setup() {
    cat > setup_cron.sh << 'EOF'
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
EOF
    
    chmod +x setup_cron.sh
    print_success "Cron setup script created: setup_cron.sh"
}

# Create quick start script
create_quick_start() {
    cat > start_automation.sh << 'EOF'
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
EOF
    
    chmod +x start_automation.sh
    print_success "Quick start script created: start_automation.sh"
}

# Create maintenance script
create_maintenance_script() {
    cat > maintenance.sh << 'EOF'
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
EOF
    
    chmod +x maintenance.sh
    print_success "Maintenance script created: maintenance.sh"
}

# Ask user about setup options
echo ""
print_status "Creating additional setup scripts..."
create_systemd_service
create_cron_setup
create_quick_start
create_maintenance_script

# Test the automation system
echo ""
print_status "Testing automation system..."
python3 automation_manager.py status

if [ $? -eq 0 ]; then
    print_success "Automation system setup completed successfully! ✨"
else
    print_error "There was an issue with the setup. Please check the logs."
    exit 1
fi

echo ""
echo "📋 Next steps:"
echo ""
echo "1. Review and customize automation_config.yaml"
echo "2. Test the system:"
echo "   ./start_automation.sh          # Start interactive mode"
echo "   python3 automation_manager.py run-once  # Test one run"
echo ""
echo "3. Setup automated execution (choose one):"
echo "   a) Cron jobs (recommended):"
echo "      ./setup_cron.sh"
echo ""
echo "   b) Systemd service (for servers):"
echo "      sudo cp /tmp/cogitating-ceviche-automation.service /etc/systemd/system/"
echo "      sudo systemctl enable --now cogitating-ceviche-automation.service"
echo ""
echo "4. Monitor the system:"
echo "   python3 automation_manager.py status    # Check status"
echo "   tail -f automation_logs/automation.log  # View logs"
echo ""
echo "5. Run maintenance periodically:"
echo "   ./maintenance.sh"

print_success "Setup complete! The automation system is ready to use. 🎉"