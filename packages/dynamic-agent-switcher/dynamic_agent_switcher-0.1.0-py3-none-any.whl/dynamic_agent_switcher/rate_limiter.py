"""
Rate Limiter for managing API rate limits across different AI models.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from asyncio import Semaphore
import logging

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    cooldown_seconds: int = 60
    retry_after_seconds: int = 30

class RateLimiter:
    """
    Rate limiter that manages API rate limits for multiple models.
    """
    
    def __init__(self):
        self.request_timestamps: Dict[str, List[float]] = {}
        self.semaphores: Dict[str, Semaphore] = {}
        self.rate_limit_configs: Dict[str, RateLimitConfig] = {}
        self.last_rate_limit_time: Dict[str, float] = {}
        
    def add_model(
        self, 
        model_name: str, 
        config: RateLimitConfig,
        semaphore_limit: Optional[int] = None
    ):
        """Add a model to the rate limiter."""
        self.rate_limit_configs[model_name] = config
        self.request_timestamps[model_name] = []
        self.last_rate_limit_time[model_name] = 0
        
        # Create semaphore for concurrent request limiting
        if semaphore_limit is None:
            semaphore_limit = config.burst_limit
        self.semaphores[model_name] = Semaphore(semaphore_limit)
        
    def is_rate_limited(self, model_name: str) -> bool:
        """Check if a model is currently rate limited."""
        if model_name not in self.rate_limit_configs:
            return True
            
        current_time = time.time()
        config = self.rate_limit_configs[model_name]
        
        # Check if we're in cooldown period
        if current_time - self.last_rate_limit_time.get(model_name, 0) < config.cooldown_seconds:
            return True
            
        # Clean old timestamps
        self._clean_timestamps(model_name)
        
        # Check minute limit
        minute_ago = current_time - 60
        recent_requests = [
            ts for ts in self.request_timestamps.get(model_name, [])
            if ts > minute_ago
        ]
        
        if len(recent_requests) >= config.requests_per_minute:
            return True
            
        # Check hour limit
        hour_ago = current_time - 3600
        hourly_requests = [
            ts for ts in self.request_timestamps.get(model_name, [])
            if ts > hour_ago
        ]
        
        if len(hourly_requests) >= config.requests_per_hour:
            return True
            
        return False
        
    def record_request(self, model_name: str):
        """Record a request for rate limiting."""
        if model_name not in self.request_timestamps:
            return
            
        current_time = time.time()
        self.request_timestamps[model_name].append(current_time)
        
    def record_rate_limit(self, model_name: str):
        """Record a rate limit hit."""
        self.last_rate_limit_time[model_name] = time.time()
        logger.warning(f"Rate limit hit for model: {model_name}")
        
    def get_wait_time(self, model_name: str) -> float:
        """Get the time to wait before next request."""
        if model_name not in self.rate_limit_configs:
            return 60.0
            
        config = self.rate_limit_configs[model_name]
        current_time = time.time()
        
        # Check cooldown
        cooldown_remaining = config.cooldown_seconds - (current_time - self.last_rate_limit_time.get(model_name, 0))
        if cooldown_remaining > 0:
            return cooldown_remaining
            
        # Check minute limit
        minute_ago = current_time - 60
        recent_requests = [
            ts for ts in self.request_timestamps.get(model_name, [])
            if ts > minute_ago
        ]
        
        if len(recent_requests) >= config.requests_per_minute:
            # Wait until oldest request is more than 1 minute old
            oldest_recent = min(recent_requests)
            return 60 - (current_time - oldest_recent) + 1
            
        # Check hour limit
        hour_ago = current_time - 3600
        hourly_requests = [
            ts for ts in self.request_timestamps.get(model_name, [])
            if ts > hour_ago
        ]
        
        if len(hourly_requests) >= config.requests_per_hour:
            # Wait until oldest request is more than 1 hour old
            oldest_hourly = min(hourly_requests)
            return 3600 - (current_time - oldest_hourly) + 1
            
        return 0.0
        
    def get_available_models(self) -> List[str]:
        """Get list of models that are not rate limited."""
        available = []
        for model_name in self.rate_limit_configs.keys():
            if not self.is_rate_limited(model_name):
                available.append(model_name)
        return available
        
    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Get detailed status for a model."""
        if model_name not in self.rate_limit_configs:
            return {"error": "Model not found"}
            
        current_time = time.time()
        config = self.rate_limit_configs[model_name]
        
        # Clean timestamps
        self._clean_timestamps(model_name)
        
        # Count recent requests
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        recent_requests = [
            ts for ts in self.request_timestamps.get(model_name, [])
            if ts > minute_ago
        ]
        
        hourly_requests = [
            ts for ts in self.request_timestamps.get(model_name, [])
            if ts > hour_ago
        ]
        
        return {
            "model_name": model_name,
            "is_rate_limited": self.is_rate_limited(model_name),
            "requests_last_minute": len(recent_requests),
            "requests_last_hour": len(hourly_requests),
            "minute_limit": config.requests_per_minute,
            "hour_limit": config.requests_per_hour,
            "wait_time": self.get_wait_time(model_name),
            "semaphore_available": self.semaphores[model_name]._value if model_name in self.semaphores else 0
        }
        
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall status of all models."""
        status = {
            "total_models": len(self.rate_limit_configs),
            "available_models": len(self.get_available_models()),
            "rate_limited_models": len(self.rate_limit_configs) - len(self.get_available_models()),
            "models": {}
        }
        
        for model_name in self.rate_limit_configs.keys():
            status["models"][model_name] = self.get_model_status(model_name)
            
        return status
        
    def _clean_timestamps(self, model_name: str):
        """Clean old timestamps for a model."""
        if model_name not in self.request_timestamps:
            return
            
        current_time = time.time()
        hour_ago = current_time - 3600
        
        # Keep only timestamps from last hour
        self.request_timestamps[model_name] = [
            ts for ts in self.request_timestamps[model_name]
            if ts > hour_ago
        ]
        
    async def acquire_semaphore(self, model_name: str):
        """Acquire semaphore for a model."""
        if model_name in self.semaphores:
            await self.semaphores[model_name].acquire()
            
    def release_semaphore(self, model_name: str):
        """Release semaphore for a model."""
        if model_name in self.semaphores:
            self.semaphores[model_name].release()
            
    async def wait_if_needed(self, model_name: str):
        """Wait if the model is rate limited."""
        if self.is_rate_limited(model_name):
            wait_time = self.get_wait_time(model_name)
            if wait_time > 0:
                logger.info(f"Waiting {wait_time:.2f}s for rate limit on {model_name}")
                await asyncio.sleep(wait_time)
