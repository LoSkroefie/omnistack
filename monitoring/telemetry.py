from typing import Dict, Any, Optional
import time
from dataclasses import dataclass
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

@dataclass
class PerformanceMetrics:
    latency_ms: float
    cpu_usage: float
    memory_usage: float
    gpu_usage: Optional[float] = None

class TelemetryManager:
    def __init__(self):
        resource = Resource.create({
            "service.name": "omnistack-ai",
            "service.version": "1.0.0"
        })
        
        # Initialize tracing
        trace.set_tracer_provider(TracerProvider(resource=resource))
        self.tracer = trace.get_tracer(__name__)
        
        # Initialize metrics
        metrics.set_meter_provider(MeterProvider(resource=resource))
        self.meter = metrics.get_meter(__name__)
        
        # Create metrics
        self.request_counter = self.meter.create_counter(
            "requests",
            description="Number of requests"
        )
        
        self.latency_histogram = self.meter.create_histogram(
            "request_latency",
            description="Request latency in milliseconds"
        )
        
        self.error_counter = self.meter.create_counter(
            "errors",
            description="Number of errors"
        )
        
        self.model_inference_time = self.meter.create_histogram(
            "model_inference_time",
            description="Model inference time in milliseconds"
        )
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency: float
    ):
        """Record API request metrics."""
        attributes = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code
        }
        
        self.request_counter.add(1, attributes)
        self.latency_histogram.record(latency, attributes)
        
        if status_code >= 400:
            self.error_counter.add(1, attributes)
    
    def record_model_inference(
        self,
        model_name: str,
        inference_time: float,
        success: bool
    ):
        """Record model inference metrics."""
        attributes = {
            "model_name": model_name,
            "success": success
        }
        
        self.model_inference_time.record(inference_time, attributes)
    
    def start_operation_tracking(
        self,
        operation_name: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> trace.Span:
        """Start tracking an operation with distributed tracing."""
        return self.tracer.start_span(
            operation_name,
            attributes=attributes or {}
        )
    
    def record_performance_metrics(
        self,
        metrics: PerformanceMetrics,
        component: str
    ):
        """Record component performance metrics."""
        attributes = {"component": component}
        
        self.meter.create_observable_gauge(
            f"{component}_cpu_usage",
            callbacks=[lambda x: metrics.cpu_usage],
            description=f"CPU usage for {component}"
        )
        
        self.meter.create_observable_gauge(
            f"{component}_memory_usage",
            callbacks=[lambda x: metrics.memory_usage],
            description=f"Memory usage for {component}"
        )
        
        if metrics.gpu_usage is not None:
            self.meter.create_observable_gauge(
                f"{component}_gpu_usage",
                callbacks=[lambda x: metrics.gpu_usage],
                description=f"GPU usage for {component}"
            )

class AnalyticsCollector:
    def __init__(self):
        self.meter = metrics.get_meter(__name__)
        
        # Create analytics metrics
        self.feature_usage = self.meter.create_counter(
            "feature_usage",
            description="Feature usage statistics"
        )
        
        self.user_engagement = self.meter.create_histogram(
            "user_engagement",
            description="User engagement duration"
        )
        
        self.optimization_impact = self.meter.create_histogram(
            "optimization_impact",
            description="Impact of code optimizations"
        )
    
    def track_feature_usage(
        self,
        feature_name: str,
        user_id: str,
        success: bool
    ):
        """Track feature usage analytics."""
        attributes = {
            "feature": feature_name,
            "user_id": user_id,
            "success": success
        }
        
        self.feature_usage.add(1, attributes)
    
    def track_engagement(
        self,
        user_id: str,
        duration_seconds: float,
        session_type: str
    ):
        """Track user engagement duration."""
        attributes = {
            "user_id": user_id,
            "session_type": session_type
        }
        
        self.user_engagement.record(duration_seconds, attributes)
    
    def track_optimization_impact(
        self,
        optimization_type: str,
        performance_improvement: float,
        code_reduction: float
    ):
        """Track the impact of code optimizations."""
        attributes = {
            "optimization_type": optimization_type
        }
        
        self.optimization_impact.record(
            performance_improvement,
            {**attributes, "metric": "performance"}
        )
        self.optimization_impact.record(
            code_reduction,
            {**attributes, "metric": "code_reduction"}
        )

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {}
    
    def start_operation(self, operation_name: str):
        """Start timing an operation."""
        self.metrics[operation_name] = {
            "start_time": time.time(),
            "cpu_start": self._get_cpu_usage(),
            "memory_start": self._get_memory_usage()
        }
    
    def end_operation(self, operation_name: str) -> PerformanceMetrics:
        """End timing an operation and return metrics."""
        if operation_name not in self.metrics:
            raise ValueError(f"Operation {operation_name} not started")
        
        end_time = time.time()
        start_metrics = self.metrics[operation_name]
        
        return PerformanceMetrics(
            latency_ms=(end_time - start_metrics["start_time"]) * 1000,
            cpu_usage=self._get_cpu_usage() - start_metrics["cpu_start"],
            memory_usage=self._get_memory_usage() - start_metrics["memory_start"],
            gpu_usage=self._get_gpu_usage()
        )
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage."""
        # Implement CPU usage monitoring
        return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage."""
        # Implement memory usage monitoring
        return 0.0
    
    def _get_gpu_usage(self) -> Optional[float]:
        """Get current GPU usage if available."""
        # Implement GPU usage monitoring
        return None
