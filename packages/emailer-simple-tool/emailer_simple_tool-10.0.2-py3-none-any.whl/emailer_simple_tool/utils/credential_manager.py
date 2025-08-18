"""
Secure credential management for SMTP settings.
"""

import os
import json
from cryptography.fernet import Fernet
from typing import Dict, Any, Optional

from .logger import get_logger


class CredentialManager:
    """Manages encrypted storage of SMTP credentials."""
    
    def __init__(self, campaign_folder: str):
        self.campaign_folder = campaign_folder
        self.cred_file = os.path.join(campaign_folder, 'smtp-credentials.enc')
        self.key_file = os.path.join(campaign_folder, '.smtp-key')
        self.logger = get_logger(__name__)
    
    def store_credentials(self, smtp_config: Dict[str, Any]) -> None:
        """Store SMTP credentials securely."""
        try:
            # Generate or load encryption key
            key = self._get_or_create_key()
            
            # Encrypt credentials
            fernet = Fernet(key)
            credentials_json = json.dumps(smtp_config)
            encrypted_data = fernet.encrypt(credentials_json.encode())
            
            # Save encrypted credentials
            with open(self.cred_file, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.info("SMTP credentials stored successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to store credentials: {e}")
            raise
    
    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """Load and decrypt SMTP credentials."""
        if not self.has_credentials():
            return None
        
        try:
            # Load encryption key
            key = self._load_key()
            if not key:
                self.logger.error("Encryption key not found")
                return None
            
            # Decrypt credentials
            fernet = Fernet(key)
            
            with open(self.cred_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            
            self.logger.info("SMTP credentials loaded successfully")
            return credentials
            
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            return None
    
    def has_credentials(self) -> bool:
        """Check if credentials are stored."""
        return os.path.exists(self.cred_file) and os.path.exists(self.key_file)
    
    def delete_credentials(self) -> None:
        """Delete stored credentials and key."""
        try:
            if os.path.exists(self.cred_file):
                os.remove(self.cred_file)
            
            if os.path.exists(self.key_file):
                os.remove(self.key_file)
            
            self.logger.info("SMTP credentials deleted successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to delete credentials: {e}")
            raise
    
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create a new one."""
        if os.path.exists(self.key_file):
            return self._load_key()
        else:
            return self._create_key()
    
    def _create_key(self) -> bytes:
        """Create a new encryption key."""
        key = Fernet.generate_key()
        
        with open(self.key_file, 'wb') as f:
            f.write(key)
        
        # Make key file readable only by owner
        os.chmod(self.key_file, 0o600)
        
        return key
    
    def _load_key(self) -> Optional[bytes]:
        """Load existing encryption key."""
        try:
            with open(self.key_file, 'rb') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to load encryption key: {e}")
            return None
