#!/usr/bin/env python3
"""
SSL Certificate Generator for Hugo Site
Generates self-signed SSL certificates for local HTTPS development
"""

import os
import subprocess
import sys
from pathlib import Path

def install_openssl():
    """Install OpenSSL if not available"""
    try:
        if sys.platform.startswith('linux'):
            print("Installing OpenSSL...")
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'openssl'], check=True)
        elif sys.platform == 'darwin':
            subprocess.run(['brew', 'install', 'openssl'], check=True)
        else:
            print("Please install OpenSSL manually on your system")
            return False
        return True
    except Exception as e:
        print(f"Failed to install OpenSSL: {e}")
        return False

def generate_with_openssl():
    """Generate SSL certificate using OpenSSL command"""
    try:
        # Create ssl directory
        ssl_dir = Path("ssl")
        ssl_dir.mkdir(exist_ok=True)
        
        cert_path = ssl_dir / "cert.pem"
        key_path = ssl_dir / "key.pem"
        
        # Generate certificate with OpenSSL
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', str(key_path),
            '-out', str(cert_path),
            '-days', '365', '-nodes',
            '-subj', '/C=US/ST=Dev/L=Local/O=CogitatingCeviche/CN=localhost',
            '-addext', 'subjectAltName=DNS:localhost,IP:127.0.0.1'
        ]
        
        print("Generating SSL certificate with OpenSSL...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ SSL certificate generated successfully!")
            print(f"  Certificate: {cert_path}")
            print(f"  Private Key: {key_path}")
            return True
        else:
            print(f"OpenSSL error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("OpenSSL not found. Attempting to install...")
        if install_openssl():
            return generate_with_openssl()
        return False
    except Exception as e:
        print(f"Error generating certificate with OpenSSL: {e}")
        return False

def generate_with_python():
    """Generate SSL certificate using Python cryptography library"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        import ipaddress
    except ImportError:
        print("Installing cryptography library...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'cryptography'], check=True)
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            import ipaddress
        except Exception as e:
            print(f"Failed to install cryptography: {e}")
            return False
    
    try:
        # Create ssl directory
        ssl_dir = Path("ssl")
        ssl_dir.mkdir(exist_ok=True)
        
        cert_path = ssl_dir / "cert.pem"
        key_path = ssl_dir / "key.pem"
        
        print("Generating SSL certificate with Python...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Dev"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CogitatingCeviche"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate and key
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"✓ SSL certificate generated successfully!")
        print(f"  Certificate: {cert_path}")
        print(f"  Private Key: {key_path}")
        return True
        
    except Exception as e:
        print(f"Error generating certificate with Python: {e}")
        return False

def main():
    """Main certificate generation function"""
    print("SSL Certificate Generator for Hugo Site")
    print("=" * 40)
    
    # Try OpenSSL first, then fallback to Python
    success = generate_with_openssl()
    if not success:
        print("\nFalling back to Python method...")
        success = generate_with_python()
    
    if success:
        print("\n✓ Certificate generation complete!")
        print("\nTo use HTTPS with Hugo:")
        print("hugo server --bind 0.0.0.0 --port 1313 --tlsCertFile ssl/cert.pem --tlsKeyFile ssl/key.pem")
        print("\nAccess your site at: https://localhost:1313/")
    else:
        print("\n✗ Certificate generation failed!")
        print("Please check the errors above and try again.")

if __name__ == "__main__":
    main()