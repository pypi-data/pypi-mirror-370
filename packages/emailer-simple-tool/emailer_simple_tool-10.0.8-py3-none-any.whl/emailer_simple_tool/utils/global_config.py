"""
Global configuration management for emailer-simple-tool.
Handles persistent storage of application state between CLI invocations.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class GlobalConfig:
    """Manages global application configuration and state."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.emailer-simple-tool'
        self.config_file = self.config_dir / 'config.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def set_active_campaign(self, campaign_path: str):
        """Set the active campaign path."""
        config = self._load_config()
        config['active_campaign'] = os.path.abspath(campaign_path)
        self._save_config(config)
    
    def get_active_campaign(self) -> Optional[str]:
        """Get the active campaign path."""
        config = self._load_config()
        campaign_path = config.get('active_campaign')
        
        # Verify the campaign path still exists and is valid
        if campaign_path and os.path.exists(campaign_path):
            return campaign_path
        elif campaign_path:
            # Campaign path no longer exists, clear it
            self.clear_active_campaign()
        
        return None
    
    def clear_active_campaign(self):
        """Clear the active campaign."""
        config = self._load_config()
        config.pop('active_campaign', None)
        self._save_config(config)
    
    def has_active_campaign(self) -> bool:
        """Check if there's an active campaign set."""
        return self.get_active_campaign() is not None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If config file is corrupted, start fresh
                pass
        
        return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            # Log error but don't fail the operation
            print(f"Warning: Could not save configuration: {e}")
