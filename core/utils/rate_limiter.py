"""
Rate limiting utility for API calls
"""

import time
from datetime import datetime, timedelta
from typing import Optional


class RateLimiter:
    """
    Simple rate limiter for API calls.
    """
    
    def __init__(self, calls_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call_time: Optional[datetime] = None
    
    def wait_if_needed(self) -> None:
        """
        Wait if necessary to respect rate limits.
        """
        now = datetime.now()
        
        if self.last_call_time is not None:
            time_since_last_call = (now - self.last_call_time).total_seconds()
            
            if time_since_last_call < self.min_interval:
                sleep_time = self.min_interval - time_since_last_call
                time.sleep(sleep_time)
        
        self.last_call_time = datetime.now()
    
    def reset(self) -> None:
        """
        Reset the rate limiter.
        """
        self.last_call_time = None