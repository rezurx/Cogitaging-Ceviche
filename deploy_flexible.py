#!/usr/bin/env python3
"""
Flexible Hugo site deployment script for Hostinger
Supports both SSH key and password authentication
Builds Hugo site and uploads to Hostinger via SFTP
"""

import os
import sys
import subprocess
import argparse
import getpass
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
    def __init__(self, test_mode=False, use_password=False):
        self.test_mode = test_mode
        self.use_password = use_password
        self.password = None
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
            
        # Check authentication method
        if self.use_password:
            self.log("Using password authentication")
            self.password = getpass.getpass("Enter your Hostinger password: ")
        else:
            # Check SSH key
            ssh_key = Path(HOSTINGER_CONFIG['ssh_key_path'])
            if not ssh_key.exists():
                self.log(f"SSH key not found at {ssh_key}", 'ERROR')
                self.log("Please ensure your SSH key is at ~/.ssh/id_ed25519", 'ERROR')
                self.log("Or use --password flag for password authentication", 'ERROR')
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
            
    def connect_ssh(self):
        """Create and return SSH connection"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        
        if self.use_password:
            ssh.connect(
                hostname=HOSTINGER_CONFIG['hostname'],
                port=HOSTINGER_CONFIG['port'],
                username=HOSTINGER_CONFIG['username'],
                password=self.password,
                timeout=30
            )
        else:
            ssh.connect(
                hostname=HOSTINGER_CONFIG['hostname'],
                port=HOSTINGER_CONFIG['port'],
                username=HOSTINGER_CONFIG['username'],
                key_filename=HOSTINGER_CONFIG['ssh_key_path'],
                timeout=30,
                allow_agent=False,
                look_for_keys=False
            )
        return ssh
        
    def test_connection(self):
        """Test SFTP connection to Hostinger"""
        self.log("Testing connection to Hostinger...")
        
        try:
            ssh = self.connect_ssh()
            
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
            if self.use_password:
                self.log("Password authentication failed.", 'ERROR')
            else:
                self.log("SSH key authentication failed. Try --password for password auth.", 'ERROR')
            return False
        except paramiko.SSHException as e:
            self.log(f"SSH connection failed: {e}", 'ERROR')
            return False
        except Exception as e:
            self.log(f"Connection test failed: {e}", 'ERROR')
            return False
            
    def clear_remote_directory(self, sftp):
        """Clear the remote directory before upload"""
        self.log("Clearing remote directory...")
        try:
            def remove_remote_files(path):
                files = sftp.listdir(path)
                for f in files:
                    filepath = f"{path}/{f}"
                    try:
                        # Try to remove as file first
                        sftp.remove(filepath)
                        print(f"  Removed file: {f}")
                    except:
                        try:
                            # If that fails, it might be a directory
                            remove_remote_files(filepath)
                            sftp.rmdir(filepath)
                            print(f"  Removed directory: {f}")
                        except Exception as e:
                            print(f"  Could not remove {f}: {e}")
            
            remove_remote_files(HOSTINGER_CONFIG['remote_path'])
            self.log("Remote directory cleared")
        except Exception as e:
            self.log(f"Warning: Could not fully clear remote directory: {e}", 'WARN')
            
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
            ssh = self.connect_ssh()
            
            # Use SFTP for more control
            sftp = ssh.open_sftp()
            
            # Clear remote directory first
            self.clear_remote_directory(sftp)
            
            # Upload files with progress
            total_files = len(list(self.public_dir.rglob('*')))
            current_file = 0
            
            def upload_recursive(local_path, remote_path):
                nonlocal current_file
                
                if local_path.is_file():
                    current_file += 1
                    filename = local_path.name
                    percent = int(100 * current_file / total_files)
                    print(f"\r  [{percent:3d}%] Uploading {filename:<40}", end='', flush=True)
                    
                    sftp.put(str(local_path), remote_path)
                    
                elif local_path.is_dir():
                    # Create remote directory
                    try:
                        sftp.mkdir(remote_path)
                    except:
                        pass  # Directory might already exist
                        
                    # Upload contents
                    for item in local_path.iterdir():
                        remote_item_path = f"{remote_path}/{item.name}"
                        upload_recursive(item, remote_item_path)
            
            # Upload all contents of public directory
            for item in self.public_dir.iterdir():
                remote_item_path = f"{HOSTINGER_CONFIG['remote_path']}/{item.name}"
                upload_recursive(item, remote_item_path)
                
            print()  # New line after progress
            
            sftp.close()
            ssh.close()
            
            self.log("Upload completed successfully!")
            return True
            
        except Exception as e:
            self.log(f"Upload failed: {e}", 'ERROR')
            return False
                
    def deploy(self):
        """Main deployment process"""
        auth_method = "password" if self.use_password else "SSH key"
        self.log(f"Starting Hugo deployment to Hostinger (Test mode: {self.test_mode}, Auth: {auth_method})")
        
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
        self.log("Your site is now live at your Hostinger domain!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Deploy Hugo site to Hostinger')
    parser.add_argument('--test', action='store_true', 
                       help='Test connection only (no build or upload)')
    parser.add_argument('--password', action='store_true', 
                       help='Use password authentication instead of SSH key')
    args = parser.parse_args()
    
    try:
        deployer = HugoDeployer(test_mode=args.test, use_password=args.password)
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