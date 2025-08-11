#!/usr/bin/env python3
"""
Simple SSH connection test script for Hostinger
"""

import paramiko
import sys
from pathlib import Path

# Hostinger connection details
hostname = '82.180.172.252'
port = 65002
username = 'u344797311'
ssh_key_path = Path.home() / '.ssh' / 'id_ed25519'

def test_ssh_connection():
    print("Testing SSH connection to Hostinger...")
    print(f"Host: {hostname}:{port}")
    print(f"User: {username}")
    print(f"SSH Key: {ssh_key_path}")
    print()
    
    if not ssh_key_path.exists():
        print(f"ERROR: SSH key not found at {ssh_key_path}")
        return False
        
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        
        # Load system host keys
        ssh.load_system_host_keys()
        ssh.load_host_keys(Path.home() / '.ssh' / 'known_hosts')
        
        # Set policy for unknown hosts
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        
        print("Attempting SSH connection...")
        
        # Connect using SSH key
        ssh.connect(
            hostname=hostname,
            port=port,
            username=username,
            key_filename=str(ssh_key_path),
            timeout=30,
            allow_agent=False,
            look_for_keys=False
        )
        
        print("SSH connection successful!")
        
        # Test basic command
        stdin, stdout, stderr = ssh.exec_command('pwd')
        pwd_output = stdout.read().decode().strip()
        print(f"Current directory on server: {pwd_output}")
        
        # Test SFTP
        print("Testing SFTP...")
        sftp = ssh.open_sftp()
        
        try:
            files = sftp.listdir('/public_html')
            print(f"Files in /public_html: {len(files)} items")
            if files:
                print("Some files found:")
                for f in files[:5]:  # Show first 5 files
                    print(f"  {f}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")
        except Exception as e:
            print(f"Error listing /public_html: {e}")
            
        sftp.close()
        ssh.close()
        
        print("All tests passed!")
        return True
        
    except paramiko.AuthenticationException as e:
        print(f"Authentication failed: {e}")
        print("This could mean:")
        print("1. The SSH key is not added to your Hostinger account")
        print("2. The SSH key has wrong permissions")
        print("3. The SSH key passphrase is required")
        return False
    except paramiko.SSHException as e:
        print(f"SSH connection failed: {e}")
        return False
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_ssh_connection()
    sys.exit(0 if success else 1)