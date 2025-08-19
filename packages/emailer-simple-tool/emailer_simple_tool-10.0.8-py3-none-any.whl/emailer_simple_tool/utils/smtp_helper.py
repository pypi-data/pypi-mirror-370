"""
SMTP connection and email sending utilities.
"""

import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from .logger import get_logger


class SMTPHelper:
    """Helper class for SMTP operations."""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.config = smtp_config
        self.logger = get_logger(__name__)
    
    def test_connection(self) -> bool:
        """Test SMTP connection and authentication."""
        try:
            print("Testing SMTP connection...")
            
            # Test basic connectivity
            if not self._test_tcp_connection():
                return False
            
            # Test SMTP authentication
            if not self._test_smtp_auth():
                return False
            
            print("✅ SMTP connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            print(f"❌ SMTP connection test failed: {e}")
            return False
    
    def send_email(self, message: MIMEMultipart) -> bool:
        """Send a single email message."""
        try:
            server = self._create_smtp_connection()
            if not server:
                return False
            
            # Authenticate with SMTP server
            server.login(self.config['username'], self.config['password'])
            
            # Send the email
            server.send_message(message)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def _test_tcp_connection(self) -> bool:
        """Test basic TCP connection to SMTP server."""
        try:
            server = self.config['server']
            port = self.config['port']
            
            print(f"  Testing TCP connection to {server}:{port}...")
            
            # Test socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout
            
            result = sock.connect_ex((server, port))
            sock.close()
            
            if result == 0:
                print("  ✅ TCP connection successful")
                return True
            else:
                print(f"  ❌ TCP connection failed (error code: {result})")
                self._provide_tcp_troubleshooting(server, port)
                return False
                
        except socket.gaierror as e:
            print(f"  ❌ DNS resolution failed: {e}")
            self._provide_dns_troubleshooting(server)
            return False
        except Exception as e:
            print(f"  ❌ TCP connection error: {e}")
            return False
    
    def _test_smtp_auth(self) -> bool:
        """Test SMTP authentication."""
        try:
            print("  Testing SMTP authentication...")
            
            server = self._create_smtp_connection()
            if not server:
                return False
            
            # Test login
            server.login(self.config['username'], self.config['password'])
            server.quit()
            
            print("  ✅ SMTP authentication successful")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"  ❌ SMTP authentication failed: {e}")
            self._provide_auth_troubleshooting()
            return False
        except Exception as e:
            print(f"  ❌ SMTP error: {e}")
            return False
    
    def _create_smtp_connection(self) -> Optional[smtplib.SMTP]:
        """Create and configure SMTP connection."""
        try:
            server = self.config['server']
            port = self.config['port']
            security = self.config.get('security', 'tls')
            
            if security == 'ssl':
                smtp_server = smtplib.SMTP_SSL(server, port)
            else:
                smtp_server = smtplib.SMTP(server, port)
                if security == 'tls':
                    smtp_server.starttls()
            
            return smtp_server
            
        except Exception as e:
            self.logger.error(f"Failed to create SMTP connection: {e}")
            return None
    
    def _provide_tcp_troubleshooting(self, server: str, port: int):
        """Provide troubleshooting guidance for TCP connection issues."""
        print("\n🔧 TCP Connection Troubleshooting:")
        print("  1. Check if you're behind a firewall or proxy")
        print("  2. Verify the server address and port number")
        print("  3. Try different ports (587 for TLS, 465 for SSL, 25 for plain)")
        
        # Provide specific guidance for common providers
        if 'gmail.com' in server.lower():
            print("  📧 Gmail specific:")
            print("     - Use smtp.gmail.com:587 with TLS")
            print("     - Enable 2-factor authentication and use App Password")
        elif 'outlook' in server.lower() or 'hotmail' in server.lower():
            print("  📧 Outlook specific:")
            print("     - Use smtp-mail.outlook.com:587 with TLS")
            print("     - Ensure account has SMTP enabled")
    
    def _provide_dns_troubleshooting(self, server: str):
        """Provide troubleshooting guidance for DNS issues."""
        print("\n🔧 DNS Resolution Troubleshooting:")
        print(f"  1. Check if '{server}' is the correct server address")
        print("  2. Try using a different DNS server (8.8.8.8, 1.1.1.1)")
        print("  3. Check your internet connection")
    
    def _provide_auth_troubleshooting(self):
        """Provide troubleshooting guidance for authentication issues."""
        print("\n🔧 Authentication Troubleshooting:")
        print("  1. Verify username and password are correct")
        print("  2. Check if 2-factor authentication is enabled")
        print("  3. Use App Password instead of regular password")
        print("  4. Enable 'Less secure app access' if available")
        
        server = self.config['server'].lower()
        
        if 'gmail.com' in server:
            print("  📧 Gmail specific:")
            print("     - Go to Google Account settings")
            print("     - Enable 2-factor authentication")
            print("     - Generate App Password for email")
            print("     - Use App Password instead of regular password")
        elif 'outlook' in server or 'hotmail' in server:
            print("  📧 Outlook specific:")
            print("     - Go to Microsoft Account security settings")
            print("     - Enable 2-factor authentication")
            print("     - Generate App Password")
        elif 'yahoo' in server:
            print("  📧 Yahoo specific:")
            print("     - Go to Yahoo Account security")
            print("     - Enable 2-factor authentication")
            print("     - Generate App Password")
