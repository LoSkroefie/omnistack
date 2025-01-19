from typing import Any, Optional, Union, Dict
import redis
from datetime import timedelta
import pickle
import hashlib
import json
from functools import wraps

class CacheManager:
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        default_ttl: int = 3600
    ):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.default_ttl = default_ttl
        self.binary_redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=False
        )
    
    def get(
        self,
        key: str,
        default: Any = None
    ) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return default
            return json.loads(value)
        except json.JSONDecodeError:
            # Try binary data
            value = self.binary_redis.get(key)
            if value is None:
                return default
            return pickle.loads(value)
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ):
        """Set value in cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            serialized = json.dumps(value)
            self.redis_client.set(key, serialized, ex=ttl)
        except (TypeError, json.JSONEncodeError):
            # Handle non-JSON serializable objects
            serialized = pickle.dumps(value)
            self.binary_redis.set(key, serialized, ex=ttl)
    
    def delete(self, key: str):
        """Delete value from cache."""
        self.redis_client.delete(key)
        self.binary_redis.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(
            self.redis_client.exists(key) or
            self.binary_redis.exists(key)
        )
    
    def clear(self):
        """Clear all cache entries."""
        self.redis_client.flushall()
    
    def get_many(self, keys: list[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        pipeline = self.redis_client.pipeline()
        for key in keys:
            pipeline.get(key)
        
        values = pipeline.execute()
        result = {}
        
        for key, value in zip(keys, values):
            if value is not None:
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    # Try binary data
                    binary_value = self.binary_redis.get(key)
                    if binary_value is not None:
                        result[key] = pickle.loads(binary_value)
        
        return result
    
    def set_many(
        self,
        mapping: Dict[str, Any],
        ttl: Optional[Union[int, timedelta]] = None
    ):
        """Set multiple values in cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        json_pipeline = self.redis_client.pipeline()
        binary_pipeline = self.binary_redis.pipeline()
        
        for key, value in mapping.items():
            try:
                serialized = json.dumps(value)
                json_pipeline.set(key, serialized, ex=ttl)
            except (TypeError, json.JSONEncodeError):
                serialized = pickle.dumps(value)
                binary_pipeline.set(key, serialized, ex=ttl)
        
        json_pipeline.execute()
        binary_pipeline.execute()
    
    def delete_many(self, keys: list[str]):
        """Delete multiple values from cache."""
        pipeline = self.redis_client.pipeline()
        binary_pipeline = self.binary_redis.pipeline()
        
        for key in keys:
            pipeline.delete(key)
            binary_pipeline.delete(key)
        
        pipeline.execute()
        binary_pipeline.execute()

def cached(
    ttl: Optional[Union[int, timedelta]] = None,
    key_prefix: str = ""
):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = CacheManager()
            
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add args and kwargs to key
            if args:
                key_parts.append(
                    hashlib.md5(
                        str(args).encode()
                    ).hexdigest()
                )
            if kwargs:
                key_parts.append(
                    hashlib.md5(
                        str(sorted(kwargs.items())).encode()
                    ).hexdigest()
                )
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

class ModelCache:
    def __init__(
        self,
        cache_size: int = 1000,
        ttl: int = 3600
    ):
        self.cache_manager = CacheManager(
            default_ttl=ttl
        )
        self.cache_size = cache_size
    
    async def get_model_prediction(
        self,
        model_name: str,
        input_data: Any
    ) -> Optional[Any]:
        """Get cached model prediction."""
        cache_key = self._get_prediction_key(model_name, input_data)
        return self.cache_manager.get(cache_key)
    
    async def set_model_prediction(
        self,
        model_name: str,
        input_data: Any,
        prediction: Any
    ):
        """Cache model prediction."""
        cache_key = self._get_prediction_key(model_name, input_data)
        self.cache_manager.set(cache_key, prediction)
    
    def _get_prediction_key(
        self,
        model_name: str,
        input_data: Any
    ) -> str:
        """Generate cache key for model prediction."""
        input_hash = hashlib.md5(
            str(input_data).encode()
        ).hexdigest()
        return f"model:{model_name}:prediction:{input_hash}"
    
    def clear_model_cache(self, model_name: str):
        """Clear all cached predictions for a model."""
        pattern = f"model:{model_name}:prediction:*"
        keys = self.cache_manager.redis_client.keys(pattern)
        if keys:
            self.cache_manager.delete_many(keys)
