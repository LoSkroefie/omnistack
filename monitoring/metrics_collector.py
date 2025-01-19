from typing import Dict, Optional
import time
from dataclasses import dataclass, field
from datetime import datetime
import prometheus_client as prom
from prometheus_client import Counter, Histogram, Gauge
import structlog
import psutil

logger = structlog.get_logger()

@dataclass
class MetricsCollector:
    """Collect and expose metrics for monitoring."""
    
    # Request metrics
    request_count: Counter = field(default_factory=lambda: prom.Counter(
        'omnistack_requests_total',
        'Total number of requests',
        ['endpoint', 'status']
    ))
    
    request_latency: Histogram = field(default_factory=lambda: prom.Histogram(
        'omnistack_request_latency_seconds',
        'Request latency in seconds',
        ['endpoint'],
        buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
    ))
    
    # AI metrics
    model_inference_time: Histogram = field(default_factory=lambda: prom.Histogram(
        'omnistack_model_inference_seconds',
        'Model inference time in seconds',
        ['model_name'],
        buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
    ))
    
    model_cache_hits: Counter = field(default_factory=lambda: prom.Counter(
        'omnistack_cache_hits_total',
        'Total number of cache hits',
        ['cache_type']
    ))
    
    model_cache_misses: Counter = field(default_factory=lambda: prom.Counter(
        'omnistack_cache_misses_total',
        'Total number of cache misses',
        ['cache_type']
    ))
    
    # Resource metrics
    cpu_usage: Gauge = field(default_factory=lambda: prom.Gauge(
        'omnistack_cpu_usage_percent',
        'CPU usage percentage'
    ))
    
    memory_usage: Gauge = field(default_factory=lambda: prom.Gauge(
        'omnistack_memory_usage_bytes',
        'Memory usage in bytes'
    ))
    
    gpu_memory_usage: Gauge = field(default_factory=lambda: prom.Gauge(
        'omnistack_gpu_memory_usage_bytes',
        'GPU memory usage in bytes',
        ['device']
    ))
    
    def __post_init__(self):
        # Start resource monitoring
        self._start_resource_monitoring()
    
    def record_request(
        self,
        endpoint: str,
        status: str = "success"
    ):
        """Record API request metrics."""
        self.request_count.labels(
            endpoint=endpoint,
            status=status
        ).inc()
    
    def time_request(self, endpoint: str) -> None:
        """Context manager to time request duration."""
        start_time = time.time()
        
        def stop_timer():
            duration = time.time() - start_time
            self.request_latency.labels(endpoint=endpoint).observe(duration)
        
        return stop_timer
    
    def record_model_inference(
        self,
        model_name: str,
        duration: float
    ):
        """Record model inference time."""
        self.model_inference_time.labels(
            model_name=model_name
        ).observe(duration)
    
    def record_cache_access(
        self,
        cache_type: str,
        hit: bool = True
    ):
        """Record cache hit/miss."""
        if hit:
            self.model_cache_hits.labels(
                cache_type=cache_type
            ).inc()
        else:
            self.model_cache_misses.labels(
                cache_type=cache_type
            ).inc()
    
    def _start_resource_monitoring(self):
        """Start monitoring system resources."""
        def update_resource_metrics():
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_usage.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.memory_usage.set(memory.used)
                
                # GPU usage (if available)
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    device_count = pynvml.nvmlDeviceGetCount()
                    
                    for i in range(device_count):
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        self.gpu_memory_usage.labels(
                            device=f"gpu{i}"
                        ).set(info.used)
                        
                except (ImportError, Exception) as e:
                    logger.debug(
                        "GPU monitoring not available",
                        error=str(e)
                    )
                    
            except Exception as e:
                logger.error(
                    "Failed to update resource metrics",
                    error=str(e)
                )
        
        # Update metrics periodically
        import threading
        def metrics_worker():
            while True:
                update_resource_metrics()
                time.sleep(15)  # Update every 15 seconds
        
        thread = threading.Thread(
            target=metrics_worker,
            daemon=True
        )
        thread.start()
    
    def get_current_metrics(self) -> Dict:
        """Get current metrics snapshot."""
        return {
            "cpu_usage": float(self.cpu_usage._value.get()),
            "memory_usage": float(self.memory_usage._value.get()),
            "request_count": {
                label_dict["endpoint"]: value
                for label_dict, value in self.request_count._metrics.items()
            },
            "cache_hits": {
                label_dict["cache_type"]: value
                for label_dict, value in self.model_cache_hits._metrics.items()
            },
            "cache_misses": {
                label_dict["cache_type"]: value
                for label_dict, value in self.model_cache_misses._metrics.items()
            }
        }
