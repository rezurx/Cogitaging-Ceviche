#!/usr/bin/env python3
"""
Comprehensive Automation Manager for Cogitating Ceviche Site

This script provides a complete automation system including:
- Automated content ingestion with scheduling
- Build and deploy pipeline automation  
- Error handling and retry logic
- Comprehensive logging and monitoring
- Status tracking and health checks
- Configuration management
"""

import os
import sys
import json
try:
    import yaml
    print(f"✅ PyYAML imported successfully (version: {yaml.__version__})")
except ImportError as e:
    print("❌ ERROR: PyYAML not installed or not accessible")
    print(f"ImportError details: {e}")
    print("\n🔧 Diagnostic information:")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
    
    # Try to show what packages are available
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=30)
        print(f"Installed packages:\n{result.stdout}")
    except Exception as pkg_error:
        print(f"Could not list packages: {pkg_error}")
    
    print("\n💡 Solutions to try:")
    print("1. pip install PyYAML")
    print("2. python -m pip install PyYAML") 
    print("3. pip install pyyaml")
    print("4. Check if running in virtual environment")
    
    sys.exit(1)
except Exception as e:
    print(f"❌ UNEXPECTED ERROR importing yaml: {e}")
    print(f"Error type: {type(e).__name__}")
    sys.exit(1)
import logging
import traceback
import subprocess
import time
import shutil
import schedule
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.status import Status
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

console = Console()

@dataclass
class AutomationStatus:
    """Current status of automation system"""
    last_ingestion: Optional[datetime] = None
    last_build: Optional[datetime] = None  
    last_deploy: Optional[datetime] = None
    last_error: Optional[datetime] = None
    error_count: int = 0
    total_runs: int = 0
    successful_runs: int = 0
    articles_processed: int = 0
    system_healthy: bool = True
    current_operation: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    timestamp: datetime
    operation: str
    duration: float
    articles_found: int = 0
    articles_processed: int = 0
    build_time: float = 0.0
    deploy_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

class AutomationLogger:
    """Enhanced logging system with rotation and formatting"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging with file rotation and console output"""
        log_config = self.config.get('logging', {})
        
        # Create logs directory
        log_file = log_config.get('log_file', 'automation_logs/automation.log')
        log_dir = Path(log_file).parent
        log_dir.mkdir(exist_ok=True)
        
        # Setup root logger
        self.logger = logging.getLogger('automation')
        self.logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler with rotation
        if log_config.get('rotate_logs', True):
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=log_config.get('max_log_size', 10*1024*1024),  # 10MB
                backupCount=log_config.get('backup_count', 5)
            )
        else:
            file_handler = logging.FileHandler(log_file)
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        if log_config.get('console', True):
            self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

class NotificationManager:
    """Handle various notification methods"""
    
    def __init__(self, config: Dict[str, Any], logger: AutomationLogger):
        self.config = config.get('error_handling', {}).get('notifications', {})
        self.logger = logger
    
    def send_notification(self, subject: str, message: str, severity: str = 'INFO'):
        """Send notification via configured methods"""
        
        if self.config.get('console', True):
            self.logger.info(f"NOTIFICATION [{severity}]: {subject} - {message}")
        
        if self.config.get('email', False):
            self._send_email(subject, message, severity)
    
    def _send_email(self, subject: str, message: str, severity: str):
        """Send email notification (requires SMTP configuration)"""
        # TODO: Implement email notifications if needed
        # This would require additional SMTP configuration in the config file
        pass

class StatusManager:
    """Manage system status and health monitoring"""
    
    def __init__(self, config: Dict[str, Any], logger: AutomationLogger):
        self.config = config
        self.logger = logger
        self.status_file = config.get('monitoring', {}).get('status_file', 'automation_logs/status.json')
        self.performance_log = config.get('monitoring', {}).get('performance_log', 'automation_logs/performance.log')
        self.status = AutomationStatus()
        self.load_status()
    
    def load_status(self):
        """Load status from file"""
        try:
            if Path(self.status_file).exists():
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    # Convert string dates back to datetime objects
                    for key, value in data.items():
                        if key.endswith('_ingestion') or key.endswith('_build') or key.endswith('_deploy') or key.endswith('_error'):
                            if value:
                                data[key] = datetime.fromisoformat(value)
                    self.status = AutomationStatus(**data)
        except Exception as e:
            self.logger.warning(f"Could not load status file: {e}")
            self.status = AutomationStatus()
    
    def save_status(self):
        """Save status to file"""
        try:
            # Create directory if it doesn't exist
            Path(self.status_file).parent.mkdir(exist_ok=True)
            
            # Convert datetime objects to strings for JSON serialization
            data = asdict(self.status)
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
            
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save status file: {e}")
    
    def update_status(self, **kwargs):
        """Update status fields"""
        for key, value in kwargs.items():
            if hasattr(self.status, key):
                setattr(self.status, key, value)
        self.save_status()
    
    def log_performance(self, metrics: PerformanceMetrics):
        """Log performance metrics"""
        try:
            # Create directory if it doesn't exist
            Path(self.performance_log).parent.mkdir(exist_ok=True)
            
            with open(self.performance_log, 'a') as f:
                f.write(f"{metrics.timestamp.isoformat()},{metrics.operation},{metrics.duration:.2f},"
                       f"{metrics.articles_found},{metrics.articles_processed},{metrics.build_time:.2f},"
                       f"{metrics.deploy_time:.2f},{metrics.success},{metrics.error_message or ''}\n")
        except Exception as e:
            self.logger.error(f"Could not log performance metrics: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        now = datetime.now()
        health = {
            'healthy': True,
            'issues': [],
            'last_successful_run': None,
            'uptime_hours': 0
        }
        
        # Check when last successful operation occurred
        last_operations = [
            self.status.last_ingestion,
            self.status.last_build,
            self.status.last_deploy
        ]
        
        last_successful = max([op for op in last_operations if op], default=None)
        if last_successful:
            health['last_successful_run'] = last_successful
            time_since_success = (now - last_successful).total_seconds() / 3600
            health['uptime_hours'] = time_since_success
            
            # Mark as unhealthy if no successful operations in 24 hours
            if time_since_success > 24:
                health['healthy'] = False
                health['issues'].append(f"No successful operations in {time_since_success:.1f} hours")
        
        # Check error rate
        if self.status.total_runs > 0:
            error_rate = self.status.error_count / self.status.total_runs
            if error_rate > 0.5:  # More than 50% error rate
                health['healthy'] = False
                health['issues'].append(f"High error rate: {error_rate:.1%}")
        
        # Check recent errors
        if self.status.last_error:
            hours_since_error = (now - self.status.last_error).total_seconds() / 3600
            if hours_since_error < 1:
                health['issues'].append(f"Recent error {hours_since_error:.1f} hours ago")
        
        return health

class ContentIngestor:
    """Enhanced content ingestion with error handling"""
    
    def __init__(self, config: Dict[str, Any], logger: AutomationLogger):
        self.config = config
        self.logger = logger
        self.working_dir = Path(config.get('environment', {}).get('working_directory', '.'))
    
    def run_ingestion(self) -> Tuple[bool, Dict[str, Any]]:
        """Run content ingestion with enhanced error handling and metrics"""
        start_time = datetime.now()
        
        try:
            self.logger.info("Starting content ingestion...")
            
            # Run the ingestion script
            cmd = [sys.executable, 'ingest_external_articles.py']
            
            # Set working directory and environment
            env = os.environ.copy()
            if 'python_env' in self.config.get('environment', {}):
                # Activate virtual environment in subprocess
                python_env = self.config['environment']['python_env']
                env['VIRTUAL_ENV'] = str(self.working_dir / python_env)
                env['PATH'] = f"{self.working_dir / python_env / 'bin'}:{env['PATH']}"
            
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                env=env
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                self.logger.info(f"Content ingestion completed successfully in {duration:.2f}s")
                
                # Parse output for article count
                articles_processed = self._count_processed_articles(result.stdout)
                
                return True, {
                    'duration': duration,
                    'articles_processed': articles_processed,
                    'output': result.stdout
                }
            else:
                self.logger.error(f"Content ingestion failed: {result.stderr}")
                return False, {
                    'duration': duration,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("Content ingestion timed out")
            return False, {'error': 'Timeout', 'duration': (datetime.now() - start_time).total_seconds()}
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Content ingestion error: {e}")
            return False, {'error': str(e), 'duration': duration}
    
    def _count_processed_articles(self, output: str) -> int:
        """Count processed articles from ingestion output"""
        count = 0
        for line in output.split('\n'):
            if 'Successfully ingested:' in line:
                count += 1
        return count

class BuildManager:
    """Handle Hugo build operations"""
    
    def __init__(self, config: Dict[str, Any], logger: AutomationLogger):
        self.config = config
        self.logger = logger
        self.working_dir = Path(config.get('environment', {}).get('working_directory', '.'))
        self.build_command = config.get('build', {}).get('build_command', 'hugo --gc --minify')
    
    def build_site(self) -> Tuple[bool, Dict[str, Any]]:
        """Build the Hugo site"""
        start_time = datetime.now()
        
        try:
            self.logger.info("Starting site build...")
            
            # Check Hugo version
            hugo_version = self.config.get('environment', {}).get('hugo_version')
            if hugo_version:
                version_result = subprocess.run(['hugo', 'version'], capture_output=True, text=True)
                if version_result.returncode == 0:
                    if hugo_version not in version_result.stdout:
                        self.logger.warning(f"Hugo version mismatch. Expected: {hugo_version}")
            
            # Run Hugo build
            result = subprocess.run(
                self.build_command.split(),
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                self.logger.info(f"Site build completed successfully in {duration:.2f}s")
                return True, {
                    'duration': duration,
                    'output': result.stdout
                }
            else:
                self.logger.error(f"Site build failed: {result.stderr}")
                return False, {
                    'duration': duration,
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("Site build timed out")
            return False, {'error': 'Build timeout', 'duration': (datetime.now() - start_time).total_seconds()}
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Build error: {e}")
            return False, {'error': str(e), 'duration': duration}

class DeploymentManager:
    """Handle deployment operations"""
    
    def __init__(self, config: Dict[str, Any], logger: AutomationLogger):
        self.config = config
        self.logger = logger
        self.working_dir = Path(config.get('environment', {}).get('working_directory', '.'))
        self.deploy_config = config.get('build', {}).get('deploy_methods', {})
    
    def deploy_site(self) -> Tuple[bool, Dict[str, Any]]:
        """Deploy the site using configured methods"""
        start_time = datetime.now()
        results = {}
        overall_success = True
        
        try:
            self.logger.info("Starting site deployment...")
            
            # Netlify deployment (automatic if configured)
            if self.deploy_config.get('netlify', False):
                netlify_success, netlify_result = self._deploy_netlify()
                results['netlify'] = netlify_result
                if not netlify_success:
                    overall_success = False
            
            # Local backup
            if self.deploy_config.get('local_backup', False):
                backup_success, backup_result = self._create_backup()
                results['backup'] = backup_result
                if not backup_success:
                    overall_success = False
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if overall_success:
                self.logger.info(f"Deployment completed successfully in {duration:.2f}s")
            else:
                self.logger.error("Some deployment methods failed")
            
            return overall_success, {
                'duration': duration,
                'methods': results
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Deployment error: {e}")
            return False, {'error': str(e), 'duration': duration}
    
    def _deploy_netlify(self) -> Tuple[bool, Dict[str, Any]]:
        """Deploy to Netlify (assumes git-based deployment)"""
        try:
            # Check if we're in a git repository
            git_check = subprocess.run(['git', 'status'], 
                                     cwd=self.working_dir, 
                                     capture_output=True, 
                                     text=True)
            
            if git_check.returncode != 0:
                return False, {'error': 'Not a git repository'}
            
            # Netlify deploys automatically from git push if configured
            # This would trigger on git push to the connected branch
            self.logger.info("Netlify deployment will occur automatically via git push")
            
            return True, {'method': 'netlify', 'message': 'Auto-deploy configured'}
            
        except Exception as e:
            return False, {'error': f'Netlify deployment error: {e}'}
    
    def _create_backup(self) -> Tuple[bool, Dict[str, Any]]:
        """Create local backup of the site"""
        try:
            backup_dir = self.working_dir / self.config.get('maintenance', {}).get('backup_location', 'backups')
            backup_dir.mkdir(exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"site_backup_{timestamp}.tar.gz"
            backup_path = backup_dir / backup_name
            
            # Create compressed backup
            cmd = ['tar', '-czf', str(backup_path), '-C', str(self.working_dir), 'public']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Clean up old backups
                self._cleanup_old_backups(backup_dir)
                return True, {'method': 'backup', 'file': str(backup_path)}
            else:
                return False, {'error': f'Backup failed: {result.stderr}'}
                
        except Exception as e:
            return False, {'error': f'Backup error: {e}'}
    
    def _cleanup_old_backups(self, backup_dir: Path):
        """Clean up old backup files"""
        try:
            retention_days = self.config.get('maintenance', {}).get('backup_retention_days', 7)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for backup_file in backup_dir.glob('site_backup_*.tar.gz'):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    self.logger.info(f"Removed old backup: {backup_file.name}")
                    
        except Exception as e:
            self.logger.warning(f"Error cleaning up old backups: {e}")

class AutomationManager:
    """Main automation manager orchestrating all operations"""
    
    def __init__(self, config_file: str = 'automation_config.yaml'):
        self.config_file = config_file
        self.config = self.load_config()
        self.logger = AutomationLogger(self.config)
        self.status_manager = StatusManager(self.config, self.logger)
        self.notification_manager = NotificationManager(self.config, self.logger)
        self.content_ingestor = ContentIngestor(self.config, self.logger)
        self.build_manager = BuildManager(self.config, self.logger)
        self.deployment_manager = DeploymentManager(self.config, self.logger)
        
        # Setup scheduled jobs
        self.setup_schedules()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            # Fallback to default config if file doesn't exist
            print(f"Warning: Could not load config file {self.config_file}: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'content': {
                'ingestion_schedule': '0 */6 * * *',
                'max_articles_per_run': 50
            },
            'build': {
                'auto_build': True,
                'auto_deploy': True,
                'build_command': 'hugo --gc --minify'
            },
            'error_handling': {
                'max_retries': 3,
                'retry_delay': 300
            },
            'logging': {
                'level': 'INFO',
                'log_file': 'automation_logs/automation.log'
            },
            'environment': {
                'working_directory': '.'
            }
        }
    
    def setup_schedules(self):
        """Setup scheduled jobs"""
        # Content ingestion schedule
        ingestion_schedule = self.config.get('content', {}).get('ingestion_schedule', '0 */6 * * *')
        schedule.every(6).hours.do(self.run_content_pipeline)
        
        # Deploy schedule (if different from content schedule)
        deploy_schedule = self.config.get('build', {}).get('deploy_schedule')
        if deploy_schedule:
            schedule.every().day.at("08:00").do(self.run_deploy_only)
            schedule.every().day.at("20:00").do(self.run_deploy_only)
        
        # Health check schedule
        health_interval = self.config.get('monitoring', {}).get('health_check_interval', 3600)
        schedule.every(health_interval // 60).minutes.do(self.health_check)
        
        self.logger.info("Scheduled jobs configured successfully")
    
    def run_content_pipeline(self, force: bool = False) -> bool:
        """Run the full content pipeline: ingest -> build -> deploy"""
        start_time = datetime.now()
        self.status_manager.update_status(
            current_operation="Content Pipeline",
            total_runs=self.status_manager.status.total_runs + 1
        )
        
        try:
            self.logger.info("=== Starting Content Pipeline ===")
            
            # Step 1: Content Ingestion
            ingestion_success, ingestion_result = self.retry_operation(
                self.content_ingestor.run_ingestion,
                "Content Ingestion"
            )
            
            if not ingestion_success:
                self.handle_pipeline_error("Content ingestion failed", ingestion_result)
                return False
            
            self.status_manager.update_status(
                last_ingestion=datetime.now(),
                articles_processed=self.status_manager.status.articles_processed + 
                                ingestion_result.get('articles_processed', 0)
            )
            
            # Step 2: Build (if auto-build enabled or forced)
            if self.config.get('build', {}).get('auto_build', True) or force:
                build_success, build_result = self.retry_operation(
                    self.build_manager.build_site,
                    "Site Build"
                )
                
                if not build_success:
                    self.handle_pipeline_error("Site build failed", build_result)
                    return False
                
                self.status_manager.update_status(last_build=datetime.now())
            
            # Step 3: Deploy (if auto-deploy enabled or forced)
            if self.config.get('build', {}).get('auto_deploy', True) or force:
                deploy_success, deploy_result = self.retry_operation(
                    self.deployment_manager.deploy_site,
                    "Site Deployment"
                )
                
                if not deploy_success:
                    self.handle_pipeline_error("Site deployment failed", deploy_result)
                    return False
                
                self.status_manager.update_status(last_deploy=datetime.now())
            
            # Pipeline completed successfully
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"=== Content Pipeline Completed Successfully in {duration:.2f}s ===")
            
            self.status_manager.update_status(
                successful_runs=self.status_manager.status.successful_runs + 1,
                system_healthy=True,
                current_operation=None
            )
            
            # Log performance metrics
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                operation="Full Pipeline",
                duration=duration,
                articles_processed=ingestion_result.get('articles_processed', 0),
                success=True
            )
            self.status_manager.log_performance(metrics)
            
            # Send success notification
            self.notification_manager.send_notification(
                "Pipeline Success",
                f"Content pipeline completed successfully. Processed {ingestion_result.get('articles_processed', 0)} articles.",
                "INFO"
            )
            
            return True
            
        except Exception as e:
            self.handle_pipeline_error("Pipeline error", {'error': str(e), 'traceback': traceback.format_exc()})
            return False
    
    def run_deploy_only(self) -> bool:
        """Run only the deployment step"""
        self.logger.info("=== Running Deploy Only ===")
        
        # Build first
        build_success, build_result = self.retry_operation(
            self.build_manager.build_site,
            "Site Build"
        )
        
        if not build_success:
            self.logger.error("Build failed, skipping deployment")
            return False
        
        # Then deploy
        deploy_success, deploy_result = self.retry_operation(
            self.deployment_manager.deploy_site,
            "Site Deployment"
        )
        
        if deploy_success:
            self.status_manager.update_status(
                last_build=datetime.now(),
                last_deploy=datetime.now()
            )
            self.logger.info("=== Deploy Only Completed Successfully ===")
        
        return deploy_success
    
    def retry_operation(self, operation, operation_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Retry an operation with exponential backoff"""
        max_retries = self.config.get('error_handling', {}).get('max_retries', 3)
        base_delay = self.config.get('error_handling', {}).get('retry_delay', 300)
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
                    self.logger.info(f"Retrying {operation_name} (attempt {attempt + 1}/{max_retries + 1}) after {delay}s delay")
                    time.sleep(delay)
                
                success, result = operation()
                
                if success:
                    if attempt > 0:
                        self.logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
                    return True, result
                else:
                    self.logger.warning(f"{operation_name} failed on attempt {attempt + 1}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.logger.error(f"{operation_name} exception on attempt {attempt + 1}: {e}")
                result = {'error': str(e), 'traceback': traceback.format_exc()}
        
        self.logger.error(f"{operation_name} failed after {max_retries + 1} attempts")
        return False, result
    
    def handle_pipeline_error(self, error_message: str, error_details: Dict[str, Any]):
        """Handle pipeline errors with logging and notifications"""
        self.logger.error(f"PIPELINE ERROR: {error_message}")
        self.logger.error(f"Error details: {error_details}")
        
        self.status_manager.update_status(
            last_error=datetime.now(),
            error_count=self.status_manager.status.error_count + 1,
            system_healthy=False,
            current_operation=None
        )
        
        # Log error metrics
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            operation="Pipeline Error",
            duration=0,
            success=False,
            error_message=error_message
        )
        self.status_manager.log_performance(metrics)
        
        # Send error notification
        self.notification_manager.send_notification(
            "Pipeline Error",
            f"{error_message}: {error_details.get('error', 'Unknown error')}",
            "ERROR"
        )
    
    def health_check(self):
        """Perform system health check"""
        health = self.status_manager.get_health_status()
        
        if health['healthy']:
            self.logger.debug("System health check: OK")
        else:
            self.logger.warning(f"System health check: Issues detected - {'; '.join(health['issues'])}")
            self.notification_manager.send_notification(
                "Health Check Warning",
                f"System health issues: {'; '.join(health['issues'])}",
                "WARNING"
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        health = self.status_manager.get_health_status()
        
        return {
            'status': self.status_manager.status,
            'health': health,
            'config': {
                'ingestion_schedule': self.config.get('content', {}).get('ingestion_schedule'),
                'auto_build': self.config.get('build', {}).get('auto_build'),
                'auto_deploy': self.config.get('build', {}).get('auto_deploy')
            }
        }
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.logger.info("Automation Manager started - running scheduled jobs")
        self.notification_manager.send_notification(
            "System Started",
            "Automation Manager has started successfully",
            "INFO"
        )
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Automation Manager stopped by user")
            self.notification_manager.send_notification(
                "System Stopped",
                "Automation Manager has been stopped",
                "INFO"
            )
        except Exception as e:
            self.logger.critical(f"Scheduler error: {e}")
            self.notification_manager.send_notification(
                "System Error",
                f"Automation Manager encountered a critical error: {e}",
                "CRITICAL"
            )

def main():
    """Main entry point with CLI interface"""
    parser = argparse.ArgumentParser(description="Cogitating Ceviche Automation Manager")
    parser.add_argument('command', nargs='?', choices=[
        'start', 'run-once', 'status', 'deploy', 'health-check', 'init-config'
    ], default='start', help='Command to execute')
    
    parser.add_argument('--config', '-c', default='automation_config.yaml', 
                       help='Configuration file path')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force execution even if not scheduled')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Initialize manager
    try:
        manager = AutomationManager(args.config)
        
        if args.verbose:
            manager.logger.logger.setLevel(logging.DEBUG)
        
        if args.command == 'start':
            # Run the scheduler
            manager.run_scheduler()
            
        elif args.command == 'run-once':
            # Run pipeline once
            console.print("[blue]Running content pipeline once...[/blue]")
            success = manager.run_content_pipeline(force=args.force)
            if success:
                console.print("[green]✓ Pipeline completed successfully[/green]")
                sys.exit(0)
            else:
                console.print("[red]✗ Pipeline failed[/red]")
                sys.exit(1)
        
        elif args.command == 'deploy':
            # Deploy only
            console.print("[blue]Running deployment only...[/blue]")  
            success = manager.run_deploy_only()
            if success:
                console.print("[green]✓ Deployment completed successfully[/green]")
                sys.exit(0)
            else:
                console.print("[red]✗ Deployment failed[/red]")
                sys.exit(1)
        
        elif args.command == 'status':
            # Show status
            status = manager.get_status()
            
            # Display status in a nice table
            console.print("\n[bold blue]🤖 Automation System Status[/bold blue]")
            
            status_table = Table(title="System Overview")
            status_table.add_column("Metric", style="cyan")
            status_table.add_column("Value", style="white")
            
            status_obj = status['status']
            health = status['health']
            
            # System health
            health_color = "green" if health['healthy'] else "red"
            health_text = "Healthy" if health['healthy'] else f"Issues: {'; '.join(health['issues'])}"
            status_table.add_row("System Health", f"[{health_color}]{health_text}[/{health_color}]")
            
            # Last operations
            status_table.add_row("Last Ingestion", 
                               status_obj.last_ingestion.strftime("%Y-%m-%d %H:%M:%S") if status_obj.last_ingestion else "Never")
            status_table.add_row("Last Build", 
                               status_obj.last_build.strftime("%Y-%m-%d %H:%M:%S") if status_obj.last_build else "Never") 
            status_table.add_row("Last Deploy",
                               status_obj.last_deploy.strftime("%Y-%m-%d %H:%M:%S") if status_obj.last_deploy else "Never")
            
            # Statistics
            status_table.add_row("Total Runs", str(status_obj.total_runs))
            status_table.add_row("Successful Runs", str(status_obj.successful_runs))
            status_table.add_row("Error Count", str(status_obj.error_count))
            status_table.add_row("Articles Processed", str(status_obj.articles_processed))
            
            # Current operation
            current_op = status_obj.current_operation or "Idle"
            status_table.add_row("Current Operation", current_op)
            
            console.print(status_table)
            
            # Configuration
            console.print("\n[bold yellow]⚙️ Configuration[/bold yellow]")
            config_table = Table()
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="white")
            
            config = status['config']
            config_table.add_row("Ingestion Schedule", config.get('ingestion_schedule', 'Not set'))
            config_table.add_row("Auto Build", "Enabled" if config.get('auto_build') else "Disabled")
            config_table.add_row("Auto Deploy", "Enabled" if config.get('auto_deploy') else "Disabled")
            
            console.print(config_table)
        
        elif args.command == 'health-check':
            # Run health check
            manager.health_check()
            health = manager.status_manager.get_health_status()
            
            if health['healthy']:
                console.print("[green]✓ System is healthy[/green]")
                sys.exit(0)
            else:
                console.print(f"[red]✗ System issues detected: {'; '.join(health['issues'])}[/red]")
                sys.exit(1)
        
        elif args.command == 'init-config':
            # Initialize configuration file
            config_path = Path(args.config)
            if config_path.exists():
                console.print(f"[yellow]Configuration file {args.config} already exists[/yellow]")
                sys.exit(1)
            else:
                # Copy default config
                default_config = manager.get_default_config()
                with open(config_path, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
                console.print(f"[green]✓ Created configuration file: {args.config}[/green]")
                console.print("Edit the configuration file to customize settings")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if args.verbose:
            console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()