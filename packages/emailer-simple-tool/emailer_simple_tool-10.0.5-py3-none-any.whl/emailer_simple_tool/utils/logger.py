"""
Logging utilities for the emailer-simple-tool application.
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(campaign_folder: Optional[str] = None, log_level: str = 'INFO') -> logging.Logger:
    """Set up logging for the application."""
    
    # Create logger
    logger = logging.getLogger('emailer-simple-tool')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if campaign folder is provided)
    if campaign_folder:
        logs_dir = os.path.join(campaign_folder, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_filename = f"emailer-{datetime.now().strftime('%Y-%m-%d')}.log"
        log_path = os.path.join(logs_dir, log_filename)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f'emailer-simple-tool.{name}')


class CampaignLogger:
    """Campaign-specific logger that writes to campaign folder."""
    
    def __init__(self, campaign_folder: str, log_level: str = 'INFO'):
        self.campaign_folder = campaign_folder
        self.log_level = log_level
        self.logger = setup_logger(campaign_folder, log_level)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
