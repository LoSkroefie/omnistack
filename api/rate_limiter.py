from typing import Optional, Dict
import time
from dataclasses import dataclass
import redis
import structlog
from fastapi import HTTPException, Request
import asyncio

logger = structlog.get_logger()

@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int
    burst_size: int
    key_prefix: str

class RateLimiter:
    """Token bucket rate limiter using Redis."""
    
    def __init__(
        self,
        redis_url: str,
        default_config: Optional[RateLimitConfig] = None
    ):
        self.redis = redis.from_url(redis_url)
        self.default_config = default_config or RateLimitConfig(
            requests_per_minute=60,
            burst_size=10,
            key_prefix="rate_limit"
        )
        
        # Rate limit configs by subscription tier
        self.tier_configs = {
            "free": RateLimitConfig(
                requests_per_minute=60,
                burst_size=10,
                key_prefix="rate_limit:free"
            ),
            "pro": RateLimitConfig(
                requests_per_minute=300,
                burst_size=50,
                key_prefix="rate_limit:pro"
            ),
            "enterprise": RateLimitConfig(
                requests_per_minute=1000,
                burst_size=100,
                key_prefix="rate_limit:enterprise"
            )
        }
    
    async def check_rate_limit(
        self,
        key: str,
        subscription_tier: str = "free"
    ) -> bool:
        """
        Check if request is within rate limit.
        Uses token bucket algorithm.
        """
        config = self.tier_configs.get(
            subscription_tier,
            self.default_config
        )
        
        bucket_key = f"{config.key_prefix}:{key}"
        
        try:
            # Atomic rate limit check using Redis
            lua_script = """
            local bucket_key = KEYS[1]
            local now = tonumber(ARGV[1])
            local rate = tonumber(ARGV[2])
            local burst = tonumber(ARGV[3])
            local window = 60  -- 1 minute window
            
            -- Get current bucket
            local bucket = redis.call('hgetall', bucket_key)
            local tokens = tonumber(bucket[2] or burst)
            local last_update = tonumber(bucket[4] or 0)
            
            -- Calculate tokens to add based on time passed
            local time_passed = now - last_update
            local new_tokens = math.min(
                burst,
                tokens + (rate * time_passed / window)
            )
            
            -- Try to consume a token
            if new_tokens >= 1 then
                -- Update bucket
                redis.call('hmset', bucket_key,
                    'tokens', new_tokens - 1,
                    'last_update', now
                )
                redis.call('expire', bucket_key, window)
                return 1
            else
                return 0
            end
            """
            
            # Execute rate limit check
            result = await asyncio.to_thread(
                self.redis.eval,
                lua_script,
                1,  # Number of keys
                bucket_key,  # KEYS[1]
                time.time(),  # ARGV[1]
                config.requests_per_minute,  # ARGV[2]
                config.burst_size  # ARGV[3]
            )
            
            return bool(result)
            
        except Exception as e:
            logger.error(
                "Rate limit check failed",
                error=str(e),
                key=key
            )
            return True  # Allow request if rate limit check fails
    
    def get_rate_limit_headers(
        self,
        key: str,
        subscription_tier: str = "free"
    ) -> Dict[str, str]:
        """Get rate limit headers for response."""
        config = self.tier_configs.get(
            subscription_tier,
            self.default_config
        )
        
        bucket_key = f"{config.key_prefix}:{key}"
        
        try:
            # Get current bucket state
            bucket = self.redis.hgetall(bucket_key)
            tokens = float(bucket.get(b'tokens', config.burst_size))
            
            return {
                "X-RateLimit-Limit": str(config.requests_per_minute),
                "X-RateLimit-Remaining": str(int(tokens)),
                "X-RateLimit-Reset": str(60)  # Reset after 1 minute
            }
        except Exception as e:
            logger.error(
                "Failed to get rate limit headers",
                error=str(e),
                key=key
            )
            return {}

async def rate_limit_middleware(
    request: Request,
    rate_limiter: RateLimiter
):
    """FastAPI middleware for rate limiting."""
    # Get client IP or user ID for rate limit key
    key = request.client.host
    
    # Get user's subscription tier
    subscription_tier = "free"  # Default to free tier
    if hasattr(request.state, "user"):
        subscription_tier = request.state.user.subscription_tier
    
    # Check rate limit
    if not await rate_limiter.check_rate_limit(key, subscription_tier):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    
    # Add rate limit headers to response
    headers = rate_limiter.get_rate_limit_headers(
        key,
        subscription_tier
    )
    request.state.rate_limit_headers = headers
