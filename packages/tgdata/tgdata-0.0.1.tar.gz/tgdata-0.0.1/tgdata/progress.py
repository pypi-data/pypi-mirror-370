"""
Progress tracking utilities for long-running operations.
"""

from datetime import datetime, timedelta
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Track progress of long-running operations.
    This doesn't need persistence as it's for real-time progress only.
    """
    
    def __init__(self, 
                 total_expected: Optional[int] = None,
                 callback: Optional[Callable[[int, Optional[int], float], None]] = None):
        """
        Initialize progress tracker.
        
        Args:
            total_expected: Expected total items (if known)
            callback: Optional callback function(current, total, rate)
        """
        self.total_expected = total_expected
        self.callback = callback
        self.current = 0
        self.start_time: Optional[datetime] = None
        
    def start(self) -> None:
        """Start tracking progress."""
        self.start_time = datetime.now()
        self.current = 0
        logger.debug("Progress tracking started")
        
    def update(self, count: int = 1) -> None:
        """
        Update progress.
        
        Args:
            count: Number of items processed
        """
        self.current += count
        
        # Calculate rate
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = self.current / elapsed if elapsed > 0 else 0
        else:
            rate = 0
            
        # Call callback
        if self.callback:
            try:
                self.callback(self.current, self.total_expected, rate)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
        
    def get_rate(self) -> float:
        """Get current processing rate (items per second)."""
        if not self.start_time:
            return 0.0
            
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return self.current / elapsed if elapsed > 0 else 0.0
        
    def get_eta(self) -> Optional[datetime]:
        """Get estimated time of completion."""
        if not self.total_expected or not self.start_time or self.current <= 0:
            return None
            
        rate = self.get_rate()
        if rate <= 0:
            return None
            
        remaining = self.total_expected - self.current
        eta_seconds = remaining / rate
        
        return datetime.now() + timedelta(seconds=eta_seconds)
    
    def get_elapsed(self) -> Optional[timedelta]:
        """Get elapsed time since start."""
        if not self.start_time:
            return None
        return datetime.now() - self.start_time
    
    def get_progress_percentage(self) -> Optional[float]:
        """Get progress as percentage (0-100)."""
        if not self.total_expected or self.total_expected <= 0:
            return None
        return min(100.0, (self.current / self.total_expected) * 100)
    
    def get_summary(self) -> dict:
        """Get progress summary."""
        return {
            'current': self.current,
            'total': self.total_expected,
            'rate': self.get_rate(),
            'eta': self.get_eta(),
            'elapsed': self.get_elapsed(),
            'percentage': self.get_progress_percentage()
        }