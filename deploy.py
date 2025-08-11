#!/usr/bin/env python3
"""
Simple Hugo site deployment script for Hostinger
Builds Hugo site and uploads to Hostinger via SFTP
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import paramiko
import stat
from scp import SCPClient

# Hostinger connection details
HOSTINGER_CONFIG = {
    'hostname': '82.180.172.252',
    'port': 65002,
    'username': 'u344797311',
    'remote_path': '/public_html',
    'ssh_key_path': os.path.expanduser('~/.ssh/id_ed25519')
}

class HugoDeployer:
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        self.project_root = Path(__file__).parent
        self.public_dir = self.project_root / 'public'
        
    def log(self, message, level='INFO'):
        """Simple logging"""
        print(f"[{level}] {message}")
        
    def check_requirements(self):
        """Check if all requirements are met"""
        self.log("Checking requirements...")
        
        # Check if hugo is available
        try:
            result = subprocess.run(['hugo', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.log("Hugo not found. Please install Hugo first.", 'ERROR')
                return False
            self.log(f"Hugo found: {result.stdout.strip()}")
        except FileNotFoundError:
            self.log("Hugo not found. Please install Hugo first.", 'ERROR')
            return False
            
        # Check SSH key
        ssh_key = Path(HOSTINGER_CONFIG['ssh_key_path'])
        if not ssh_key.exists():
            self.log(f"SSH key not found at {ssh_key}", 'ERROR')
            self.log("Please ensure your SSH key is at ~/.ssh/id_ed25519", 'ERROR')
            return False
        self.log(f"SSH key found: {ssh_key}")
        
        # Check SSH key permissions
        key_stat = ssh_key.stat()
        if key_stat.st_mode & 0o077:
            self.log("SSH key has incorrect permissions. Fixing...", 'WARN')
            ssh_key.chmod(0o600)
            
        return True
        
    def build_hugo_site(self):
        """Build the Hugo site"""
        if self.test_mode:
            self.log("TEST MODE: Skipping Hugo build")
            return True
            
        self.log("Building Hugo site...")
        
        try:
            # Clean previous build
            if self.public_dir.exists():
                subprocess.run(['rm', '-rf', str(self.public_dir)], check=True)
                
            # Build site
            result = subprocess.run(
                ['hugo', '--cleanDestinationDir'], 
                cwd=self.project_root,
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                self.log(f"Hugo build failed: {result.stderr}", 'ERROR')
                return False
                
            self.log("Hugo build completed successfully")
            self.log(f"Build output: {result.stdout}")
            
            # Verify public directory exists
            if not self.public_dir.exists():
                self.log("Public directory not created after build", 'ERROR')
                return False
                
            # Count files
            file_count = len(list(self.public_dir.rglob('*')))
            self.log(f"Built site contains {file_count} files/directories")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Hugo build failed: {e}", 'ERROR')
            return False
        except Exception as e:
            self.log(f"Unexpected error during build: {e}", 'ERROR')
            return False
            
    def test_connection(self):
        """Test SFTP connection to Hostinger"""
        self.log("Testing connection to Hostinger...")
        
        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
            
            # Connect using SSH key
            ssh.connect(
                hostname=HOSTINGER_CONFIG['hostname'],
                port=HOSTINGER_CONFIG['port'],
                username=HOSTINGER_CONFIG['username'],
                key_filename=HOSTINGER_CONFIG['ssh_key_path'],
                timeout=30
            )
            
            # Test SFTP
            sftp = ssh.open_sftp()
            
            # Check if remote directory exists
            try:
                remote_files = sftp.listdir(HOSTINGER_CONFIG['remote_path'])
                self.log(f"Connected successfully! Remote directory has {len(remote_files)} items")
            except FileNotFoundError:
                self.log(f"Remote directory {HOSTINGER_CONFIG['remote_path']} not found", 'ERROR')
                return False
                
            sftp.close()
            ssh.close()
            
            self.log("Connection test successful!")
            return True
            
        except paramiko.AuthenticationException:
            self.log("SSH authentication failed. Check your SSH key.", 'ERROR')
            return False
        except paramiko.SSHException as e:
            self.log(f"SSH connection failed: {e}", 'ERROR')
            return False
        except Exception as e:
            self.log(f"Connection test failed: {e}", 'ERROR')
            return False
            
    def upload_files(self):
        """Upload files to Hostinger via SFTP"""
        if self.test_mode:
            self.log("TEST MODE: Skipping file upload")
            return True
            
        if not self.public_dir.exists():
            self.log("Public directory not found. Run build first.", 'ERROR')
            return False
            
        self.log("Uploading files to Hostinger...")
        
        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
            
            # Connect
            ssh.connect(
                hostname=HOSTINGER_CONFIG['hostname'],
                port=HOSTINGER_CONFIG['port'],
                username=HOSTINGER_CONFIG['username'],
                key_filename=HOSTINGER_CONFIG['ssh_key_path'],
                timeout=30
            )
            
            # Create SCP client
            with SCPClient(ssh.get_transport(), progress=self._progress) as scp:
                self.log("Starting file upload...")
                
                # Upload entire public directory contents
                # Note: We upload the contents of public/, not the public/ directory itself
                for item in self.public_dir.iterdir():
                    if item.is_file():
                        remote_file = f"{HOSTINGER_CONFIG['remote_path']}/{item.name}"
                        scp.put(str(item), remote_file)
                    elif item.is_dir():
                        remote_dir = f"{HOSTINGER_CONFIG['remote_path']}/{item.name}"
                        scp.put(str(item), remote_dir, recursive=True)
            
            ssh.close()
            self.log("Upload completed successfully!")
            return True
            
        except Exception as e:
            self.log(f"Upload failed: {e}", 'ERROR')
            return False
            
    def _progress(self, filename, size, sent):
        """Progress callback for SCP"""
        if size > 0:
            percent = int(100 * sent / size)
            filename_short = Path(filename).name
            if len(filename_short) > 30:
                filename_short = filename_short[:27] + "..."
            print(f"\r  Uploading {filename_short:<30} {percent:3d}%", end='', flush=True)
            if sent >= size:
                print()  # New line after completion
                
    def deploy(self):
        """Main deployment process"""
        self.log(f"Starting Hugo deployment to Hostinger (Test mode: {self.test_mode})")
        
        # Check requirements
        if not self.check_requirements():
            return False
            
        # Test connection
        if not self.test_connection():
            return False
            
        if self.test_mode:
            self.log("TEST MODE: Connection successful! Ready for deployment.")
            return True
            
        # Build site
        if not self.build_hugo_site():
            return False
            
        # Upload files
        if not self.upload_files():
            return False
            
        self.log("Deployment completed successfully!")
        self.log(f"Your site is now live at your Hostinger domain!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Deploy Hugo site to Hostinger')
    parser.add_argument('--test', action='store_true', 
                       help='Test connection only (no build or upload)')
    args = parser.parse_args()
    
    try:
        deployer = HugoDeployer(test_mode=args.test)
        success = deployer.deploy()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nDeployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()