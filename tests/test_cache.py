import pytest
import redis
import pickle
import json
from datetime import timedelta
import time
from cache.cache_manager import (
    CacheManager,
    ModelCache
)

@pytest.fixture
def cache_manager():
    manager = CacheManager(
        redis_host="localhost",
        redis_port=6379,
        default_ttl=3600
    )
    manager.clear()
    return manager

@pytest.fixture
def model_cache():
    cache = ModelCache(
        cache_size=1000,
        ttl=3600
    )
    cache.cache_manager.clear()
    return cache

class TestCacheManager:
    def test_set_get_string(self, cache_manager):
        cache_manager.set("test_key", "test_value")
        assert cache_manager.get("test_key") == "test_value"
    
    def test_set_get_dict(self, cache_manager):
        test_dict = {"key": "value", "number": 42}
        cache_manager.set("test_dict", test_dict)
        assert cache_manager.get("test_dict") == test_dict
    
    def test_set_get_list(self, cache_manager):
        test_list = [1, 2, "three", {"four": 4}]
        cache_manager.set("test_list", test_list)
        assert cache_manager.get("test_list") == test_list
    
    def test_get_nonexistent(self, cache_manager):
        assert cache_manager.get("nonexistent") is None
        assert cache_manager.get("nonexistent", "default") == "default"
    
    def test_set_with_ttl(self, cache_manager):
        cache_manager.set("ttl_key", "value", ttl=1)
        assert cache_manager.get("ttl_key") == "value"
        time.sleep(1.1)
        assert cache_manager.get("ttl_key") is None
    
    def test_delete(self, cache_manager):
        cache_manager.set("delete_key", "value")
        assert cache_manager.get("delete_key") == "value"
        cache_manager.delete("delete_key")
        assert cache_manager.get("delete_key") is None
    
    def test_exists(self, cache_manager):
        cache_manager.set("exists_key", "value")
        assert cache_manager.exists("exists_key")
        assert not cache_manager.exists("nonexistent")
    
    def test_clear(self, cache_manager):
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        cache_manager.clear()
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None
    
    def test_get_many(self, cache_manager):
        cache_manager.set_many({
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        })
        
        values = cache_manager.get_many(["key1", "key2", "nonexistent"])
        assert values == {
            "key1": "value1",
            "key2": "value2"
        }
    
    def test_set_many(self, cache_manager):
        mapping = {
            "set_many1": "value1",
            "set_many2": "value2"
        }
        cache_manager.set_many(mapping)
        
        for key, value in mapping.items():
            assert cache_manager.get(key) == value
    
    def test_delete_many(self, cache_manager):
        cache_manager.set_many({
            "del1": "value1",
            "del2": "value2",
            "keep": "value3"
        })
        
        cache_manager.delete_many(["del1", "del2"])
        assert cache_manager.get("del1") is None
        assert cache_manager.get("del2") is None
        assert cache_manager.get("keep") == "value3"
    
    def test_binary_data(self, cache_manager):
        class CustomObject:
            def __init__(self, value):
                self.value = value
        
        obj = CustomObject(42)
        cache_manager.set("binary_key", obj)
        
        retrieved = cache_manager.get("binary_key")
        assert isinstance(retrieved, CustomObject)
        assert retrieved.value == 42

class TestModelCache:
    async def test_model_prediction_cache(self, model_cache):
        model_name = "test_model"
        input_data = {"features": [1, 2, 3]}
        prediction = {"result": 0.95}
        
        # Cache prediction
        await model_cache.set_model_prediction(
            model_name,
            input_data,
            prediction
        )
        
        # Retrieve prediction
        cached = await model_cache.get_model_prediction(
            model_name,
            input_data
        )
        assert cached == prediction
    
    async def test_different_inputs(self, model_cache):
        model_name = "test_model"
        input1 = {"features": [1, 2, 3]}
        input2 = {"features": [4, 5, 6]}
        pred1 = {"result": 0.95}
        pred2 = {"result": 0.85}
        
        await model_cache.set_model_prediction(
            model_name,
            input1,
            pred1
        )
        await model_cache.set_model_prediction(
            model_name,
            input2,
            pred2
        )
        
        assert await model_cache.get_model_prediction(
            model_name,
            input1
        ) == pred1
        assert await model_cache.get_model_prediction(
            model_name,
            input2
        ) == pred2
    
    async def test_clear_model_cache(self, model_cache):
        model_name = "test_model"
        input_data = {"features": [1, 2, 3]}
        prediction = {"result": 0.95}
        
        await model_cache.set_model_prediction(
            model_name,
            input_data,
            prediction
        )
        
        model_cache.clear_model_cache(model_name)
        
        assert await model_cache.get_model_prediction(
            model_name,
            input_data
        ) is None
