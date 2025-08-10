"""
Redis Service - Connection and basic operations
"""

import redis.asyncio as redis
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RedisService:
    """Redis connection and basic operations service"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=False,  # Keep bytes for vector operations
                max_connections=50,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.client.ping()
            logger.info("✅ Redis connection established")
            
            # Set basic configurations
            try:
                await self.client.config_set('maxmemory-policy', 'allkeys-lru')
                logger.info("✅ Redis memory policy configured")
            except Exception as e:
                logger.warning(f"Could not set Redis config: {e}")
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def health_check(self) -> bool:
        """Check if Redis is healthy"""
        try:
            await self.client.ping()
            return True
        except Exception:
            return False