"""
Core utilities for Ultra Sports Betting System
"""

import logging
import os
from datetime import datetime
from typing import Optional


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create handler
        handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Set level
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger


def ensure_directory(path: str) -> None:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Directory path to ensure
    """
    os.makedirs(path, exist_ok=True)


def get_project_root() -> str:
    """
    Get the project root directory.
    
    Returns:
        Project root path
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get configuration value from environment or default.
    
    Args:
        key: Configuration key
        default: Default value if not found
    
    Returns:
        Configuration value
    """
    return os.getenv(key, default)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format timestamp for consistent display.
    
    Args:
        dt: Datetime to format (defaults to now)
    
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")