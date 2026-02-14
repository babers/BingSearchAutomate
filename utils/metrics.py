# utils/metrics.py
"""Metrics collection and statistics for search automation."""

import time
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class SearchMetrics:
    """Container for search-related metrics."""
    total_searches: int = 0
    successful_searches: int = 0
    failed_searches: int = 0
    total_points_gained: int = 0
    search_durations: List[float] = field(default_factory=list)
    errors_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    start_time: Optional[float] = None
    
    def record_search_start(self) -> float:
        """Record when a search starts and return the timestamp."""
        return time.time()
    
    def record_search_success(self, duration_seconds: float, points_gained: int) -> None:
        """Record a successful search."""
        self.total_searches += 1
        self.successful_searches += 1
        self.search_durations.append(duration_seconds)
        if points_gained > 0:
            self.total_points_gained += points_gained
    
    def record_search_failure(self, error_type: str) -> None:
        """Record a failed search."""
        self.total_searches += 1
        self.failed_searches += 1
        self.errors_by_type[error_type] += 1
    
    def get_average_search_duration(self) -> float:
        """Get average search duration in seconds."""
        if not self.search_durations:
            return 0.0
        return sum(self.search_durations) / len(self.search_durations)
    
    def get_success_rate(self) -> float:
        """Get success rate as a percentage."""
        if self.total_searches == 0:
            return 0.0
        return (self.successful_searches / self.total_searches) * 100
    
    def get_searches_per_minute(self) -> float:
        """Calculate searches per minute since start."""
        if not self.start_time or self.total_searches == 0:
            return 0.0
        elapsed_minutes = (time.time() - self.start_time) / 60
        if elapsed_minutes == 0:
            return 0.0
        return self.total_searches / elapsed_minutes
    
    def get_points_per_search(self) -> float:
        """Calculate average points gained per search."""
        if self.successful_searches == 0:
            return 0.0
        return self.total_points_gained / self.successful_searches
    
    def estimate_time_to_target(self, current_points: int, target_points: int) -> Optional[float]:
        """Estimate seconds until target is reached based on current velocity.
        
        Returns:
            Optional[float]: Estimated seconds to target, or None if cannot estimate
        """
        if not self.start_time or current_points >= target_points:
            return None
        
        points_needed = target_points - current_points
        elapsed_seconds = time.time() - self.start_time
        
        if elapsed_seconds == 0 or self.total_points_gained == 0:
            return None
        
        points_per_second = self.total_points_gained / elapsed_seconds
        if points_per_second <= 0:
            return None
        
        return points_needed / points_per_second
    
    def get_summary(self) -> Dict[str, any]:
        """Get a comprehensive summary of all metrics."""
        return {
            'total_searches': self.total_searches,
            'successful_searches': self.successful_searches,
            'failed_searches': self.failed_searches,
            'success_rate': round(self.get_success_rate(), 2),
            'total_points_gained': self.total_points_gained,
            'average_search_duration': round(self.get_average_search_duration(), 2),
            'searches_per_minute': round(self.get_searches_per_minute(), 2),
            'points_per_search': round(self.get_points_per_search(), 2),
            'errors_by_type': dict(self.errors_by_type)
        }


class MetricsCollector:
    """Collects and manages metrics for the automation session."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = SearchMetrics()
        self.metrics.start_time = time.time()
        self.logger.info("MetricsCollector initialized")
    
    def record_search_duration(self, duration_ms: float, points_gained: int = 0) -> None:
        """Record a search completion with duration and points gained."""
        duration_seconds = duration_ms / 1000
        self.metrics.record_search_success(duration_seconds, points_gained)
        self.logger.debug(
            f"Recorded search: {duration_seconds:.2f}s, {points_gained} points gained"
        )
    
    def record_points_gained(self, points: int) -> None:
        """Record points gained (alternative to recording with duration)."""
        self.metrics.total_points_gained += points
    
    def record_error(self, error_type: str) -> None:
        """Record an error occurrence."""
        self.metrics.record_search_failure(error_type)
        self.logger.debug(f"Recorded error: {error_type}")
    
    def get_metrics(self) -> SearchMetrics:
        """Get the current metrics object."""
        return self.metrics
    
    def get_summary(self) -> Dict[str, any]:
        """Get a summary of all collected metrics."""
        return self.metrics.get_summary()
    
    def reset(self) -> None:
        """Reset all metrics for a new session."""
        self.logger.info("Resetting metrics")
        self.metrics = SearchMetrics()
        self.metrics.start_time = time.time()
