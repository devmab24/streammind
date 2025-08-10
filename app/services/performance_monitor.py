"""
Performance monitoring service (simplified)
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    requests_per_second: float = 0.0
    cache_hit_rate: dict = None
    events_per_second: float = 0.0

    def __post_init__(self):
        if self.cache_hit_rate is None:
            self.cache_hit_rate = {}

class PerformanceMonitor:
    """Simplified performance monitoring"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.metrics = PerformanceMetrics()
        self.response_times = deque(maxlen=1000)
        self.request_timestamps = deque(maxlen=10000)
        self.monitor_task = None
        
    async def start_monitoring(self):
        """Start monitoring background task"""
        try:
            self.monitor_task = asyncio.create_task(self._monitoring_loop())
            logger.info("✅ Performance monitoring started")
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        if self.monitor_task:
            self.monitor_task.cancel()
            logger.info("Performance monitoring stopped")
    
    async def record_request(self, duration_ms: float, success: bool = True):
        """Record a request for metrics"""
        try:
            self.metrics.total_requests += 1
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
            
            # Update response times
            self.response_times.append(duration_ms)
            self.request_timestamps.append(time.time())
            
            # Update average
            if self.response_times:
                self.metrics.average_response_time_ms = sum(self.response_times) / len(self.response_times)
                
        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")
    
    async def get_current_metrics(self):
        """Get current performance metrics"""
        return self.metrics
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                await self._update_metrics()
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)
    
    async def _update_metrics(self):
        """Update calculated metrics"""
        try:
            # Calculate requests per second
            current_time = time.time()
            recent_requests = [ts for ts in self.request_timestamps 
                             if current_time - ts <= 60]
            self.metrics.requests_per_second = len(recent_requests) / 60.0
            
            # Mock cache hit rate for demo
            self.metrics.cache_hit_rate = {
                "l1_memory": 0.92,
                "l2_redis": 0.85,
                "semantic": 0.78
            }
            
            # Mock events per second
            self.metrics.events_per_second = 1200 + (time.time() % 600 - 300)  # Vary between 900-1500
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")