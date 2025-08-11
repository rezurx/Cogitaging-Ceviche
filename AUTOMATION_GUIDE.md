# Cogitating Ceviche Automation System Guide

This comprehensive automation system provides scheduled content ingestion, build, and deployment for the Cogitating Ceviche website.

## 🌟 Features

### ✅ Automated Content Ingestion
- Scheduled scraping from configured sources (Substack feeds, Vocal Media)
- Duplicate detection and skip logic
- Enhanced content processing with Substack preview extraction
- Configurable ingestion frequency (default: every 6 hours)

### ✅ Build and Deploy Pipeline
- Automatic Hugo site building after content updates
- Multi-target deployment (Netlify, local backups)
- Build verification and validation
- Deployment rollback capabilities

### ✅ Error Handling and Logging
- Robust retry logic with exponential backoff
- Comprehensive logging with rotation
- Error notifications and alerting
- Performance metrics tracking

### ✅ Configuration Management
- YAML-based configuration system
- Environment-specific settings
- Runtime configuration updates
- Default configuration templates

### ✅ Status Monitoring
- Real-time system health monitoring
- Performance metrics collection
- Historical operation tracking
- Status dashboard and reporting

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Run the setup script
./setup_automation.sh

# This will:
# - Create virtual environment and install dependencies
# - Set up directory structure
# - Create configuration files
# - Generate helper scripts
```

### 2. Configuration

Edit `automation_config.yaml` to customize your setup:

```yaml
content:
  ingestion_schedule: "0 */6 * * *"  # Every 6 hours
  max_articles_per_run: 50
  
build:
  auto_build: true
  auto_deploy: true
  
error_handling:
  max_retries: 3
  retry_delay: 300
```

### 3. Test the System

```bash
# Test single run
python3 automation_manager.py run-once

# Check system status
python3 automation_manager.py status

# Run health check
python3 automation_manager.py health-check
```

### 4. Start Automation

Choose your preferred method:

#### Option A: Interactive Mode
```bash
./start_automation.sh
```

#### Option B: Cron Jobs (Recommended)
```bash
./setup_cron.sh
```

#### Option C: Systemd Service (Servers)
```bash
sudo cp /tmp/cogitating-ceviche-automation.service /etc/systemd/system/
sudo systemctl enable --now cogitating-ceviche-automation.service
```

#### Option D: GitHub Actions (Repository)
The system includes a GitHub Actions workflow that runs automatically when pushed to a repository.

## 📋 Available Commands

### Main Automation Manager

```bash
python3 automation_manager.py [command] [options]

Commands:
  start          # Run continuous automation (default)
  run-once       # Execute pipeline once
  deploy         # Deploy only (build + deploy)
  status         # Show system status
  health-check   # Run health verification
  init-config    # Create default configuration

Options:
  --config, -c   # Configuration file path (default: automation_config.yaml)
  --force, -f    # Force execution regardless of schedule
  --verbose, -v  # Enable detailed logging
```

### Helper Scripts

```bash
./start_automation.sh      # Quick start with environment setup
./setup_cron.sh           # Configure cron jobs
./maintenance.sh          # Run maintenance tasks
```

## 📊 Monitoring and Status

### Status Dashboard

```bash
python3 automation_manager.py status
```

Shows:
- System health status
- Last operation timestamps
- Success/error statistics
- Current configuration
- Performance metrics

### Log Files

- `automation_logs/automation.log` - Main application log
- `automation_logs/performance.log` - Performance metrics
- `automation_logs/status.json` - Current system status
- `automation_logs/cron.log` - Cron job output (if using cron)

### Health Monitoring

The system continuously monitors:
- Last successful operations
- Error rates and patterns
- System responsiveness
- Content source availability
- Build and deployment success

## ⚙️ Configuration Reference

### Content Settings

```yaml
content:
  ingestion_schedule: "0 */6 * * *"    # Cron format schedule
  sources:                             # Override source configurations
    cogitating-ceviche:
      enabled: true
      priority: 1
    vocal:
      enabled: true
      priority: 2
  max_articles_per_run: 50             # Limit articles per run
  enable_content_enhancement: true     # Enhanced Substack previews
  skip_duplicates: true                # Skip existing articles
```

### Build & Deploy Settings

```yaml
build:
  auto_build: true                     # Build after ingestion
  auto_deploy: true                    # Deploy after build
  build_command: "hugo --gc --minify"  # Hugo build command
  deploy_methods:
    netlify: true                      # Netlify deployment
    local_backup: true                 # Create local backups
  deploy_schedule: "0 8,20 * * *"      # Manual deploy schedule
```

### Error Handling

```yaml
error_handling:
  max_retries: 3                       # Retry attempts
  retry_delay: 300                     # Delay between retries (seconds)
  notifications:
    console: true                      # Console notifications
    log_file: true                     # File logging
    email: false                       # Email notifications (requires SMTP)
  critical_errors:                     # Define critical error patterns
    - "Build failed"
    - "Deploy failed"
```

### Logging Configuration

```yaml
logging:
  level: "INFO"                        # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  log_file: "automation_logs/automation.log"
  max_log_size: 10485760              # 10MB
  backup_count: 5                      # Number of backup log files
  rotate_logs: true                    # Enable log rotation
```

### Monitoring Settings

```yaml
monitoring:
  enabled: true                        # Enable monitoring
  health_check_interval: 3600          # Health check frequency (seconds)
  status_file: "automation_logs/status.json"
  track_performance: true              # Performance metrics
  performance_log: "automation_logs/performance.log"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf subagent-env
python3 -m venv subagent-env
source subagent-env/bin/activate
pip install -r requirements.txt
```

#### 2. Permission Errors
```bash
# Fix script permissions
chmod +x *.sh
chmod +x *.py
```

#### 3. Hugo Build Failures
```bash
# Check Hugo version
hugo version

# Test manual build
hugo --gc --minify --verbose
```

#### 4. Content Ingestion Issues
```bash
# Test ingestion manually
python3 ingest_external_articles.py

# Check source accessibility
curl -I https://thecogitatingceviche.substack.com/feed
```

### Log Analysis

```bash
# View recent logs
tail -f automation_logs/automation.log

# Search for errors
grep -i error automation_logs/automation.log

# View performance metrics
cat automation_logs/performance.log | tail -10
```

### Health Check Details

```bash
# Detailed health check
python3 automation_manager.py health-check --verbose

# System status with configuration
python3 automation_manager.py status
```

## 🔄 Maintenance

### Regular Maintenance

Run the maintenance script monthly:

```bash
./maintenance.sh
```

This script:
- Cleans old log files
- Removes outdated backups
- Updates Python dependencies
- Runs health checks

### Manual Maintenance Tasks

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Clean logs manually
find automation_logs -name "*.log*" -mtime +30 -delete

# Clean old backups
find backups -name "site_backup_*.tar.gz" -mtime +7 -delete

# Reset status (if needed)
rm automation_logs/status.json
```

## 📈 Performance Optimization

### Tuning Ingestion Frequency

Adjust based on your needs:

```yaml
# For high-frequency updates (every 2 hours)
content:
  ingestion_schedule: "0 */2 * * *"

# For daily updates (once per day at 9 AM)
content:
  ingestion_schedule: "0 9 * * *"

# For testing (every 15 minutes)
content:
  ingestion_schedule: "*/15 * * * *"
```

### Optimizing Build Performance

```yaml
# Faster builds for development
build:
  build_command: "hugo --gc"  # Remove --minify for faster builds

# Production optimization
build:
  build_command: "hugo --gc --minify --cleanDestinationDir"
```

### Resource Management

```yaml
# Limit resource usage
content:
  max_articles_per_run: 25    # Process fewer articles per run

error_handling:
  max_retries: 1              # Reduce retries for faster failures
```

## 🔐 Security Considerations

### File Permissions

Ensure proper permissions:
```bash
chmod 700 automation_logs/
chmod 600 automation_config.yaml
chmod 600 automation_logs/status.json
```

### Environment Variables

For sensitive configuration, use environment variables:

```yaml
# In automation_config.yaml
email_settings:
  smtp_password: "${SMTP_PASSWORD}"  # Set via environment

# Set environment variable
export SMTP_PASSWORD="your-password"
```

### Log Security

- Regularly rotate and archive logs
- Avoid logging sensitive information
- Monitor log files for unauthorized access

## 🆘 Support and Debugging

### Enable Debug Mode

```bash
python3 automation_manager.py start --verbose
```

### Create Debug Report

```bash
# Generate comprehensive debug information
{
  echo "=== System Information ==="
  python3 --version
  hugo version
  
  echo -e "\n=== Current Status ==="
  python3 automation_manager.py status
  
  echo -e "\n=== Recent Logs ==="
  tail -50 automation_logs/automation.log
  
  echo -e "\n=== Configuration ==="
  cat automation_config.yaml
  
  echo -e "\n=== File Permissions ==="
  ls -la *.py *.sh *.yaml
  
} > debug_report.txt
```

### Contact and Issues

- Check logs first: `automation_logs/automation.log`
- Verify configuration: `automation_config.yaml`
- Test individual components: `python3 automation_manager.py run-once --verbose`
- Create debug report (see above) when reporting issues

## 🎯 Advanced Usage

### Custom Deployment Methods

Add custom deployment in `automation_manager.py`:

```python
def _deploy_custom(self) -> Tuple[bool, Dict[str, Any]]:
    """Custom deployment method"""
    try:
        # Your custom deployment logic
        return True, {'method': 'custom', 'message': 'Success'}
    except Exception as e:
        return False, {'error': f'Custom deployment error: {e}'}
```

### Custom Content Sources

Extend the content ingestion by modifying `ingest_external_articles.py` or creating custom processors.

### Integration with CI/CD

The system works well with:
- GitHub Actions (included workflow)
- GitLab CI/CD
- Jenkins
- Docker containers

### Monitoring Integration

Connect with external monitoring:
- Prometheus metrics export
- Grafana dashboards
- PagerDuty alerts
- Slack notifications

---

## 📝 Summary

This automation system provides a complete solution for:

1. **Automated content ingestion** from multiple sources
2. **Reliable build and deployment** with error handling
3. **Comprehensive monitoring** and health checks
4. **Flexible configuration** for different environments
5. **Multiple deployment options** (cron, systemd, GitHub Actions)

The system is designed to be:
- **Reliable**: Robust error handling and retry logic
- **Maintainable**: Clear configuration and comprehensive logging
- **Scalable**: Easily extended with new sources and deployment methods
- **Monitorable**: Built-in status tracking and health monitoring

Start with the quick setup and customize as needed for your specific requirements!