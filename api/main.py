from typing import Dict, Optional
from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import structlog
from datetime import datetime
import prometheus_client
from prometheus_client import multiprocess
import os

from ai_core.service_manager import AIServiceManager
from auth.auth_service import get_current_user, User
from config.config_manager import ConfigManager
from monitoring.telemetry import TelemetryManager
from monitoring.metrics_collector import MetricsCollector
from api.rate_limiter import RateLimiter, rate_limit_middleware

# Initialize logging
logger = structlog.get_logger()

# Initialize services
config = ConfigManager()
ai_service = AIServiceManager()
telemetry = TelemetryManager()
metrics = MetricsCollector()

# Initialize rate limiter
rate_limiter = RateLimiter(
    redis_url=config.get_redis_url()
)

app = FastAPI(
    title="OmniStack AI Framework",
    description="Advanced AI services for software development",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class CodeAnalysisRequest(BaseModel):
    code: str
    context: Optional[Dict] = None
    use_cache: bool = True

class OptimizationRequest(BaseModel):
    code: str
    context: Optional[Dict] = None

# Middleware
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    """Add metrics middleware."""
    # Start timer
    stop_timer = metrics.time_request(request.url.path)
    
    try:
        # Apply rate limiting
        await rate_limit_middleware(request, rate_limiter)
        
        # Process request
        response = await call_next(request)
        
        # Record metrics
        metrics.record_request(
            request.url.path,
            str(response.status_code)
        )
        
        # Add rate limit headers
        if hasattr(request.state, "rate_limit_headers"):
            for key, value in request.state.rate_limit_headers.items():
                response.headers[key] = value
        
        return response
        
    except HTTPException as e:
        # Record error metrics
        metrics.record_request(
            request.url.path,
            "error"
        )
        raise
        
    finally:
        # Stop timer
        stop_timer()

# Metrics endpoint
@app.get("/metrics")
async def metrics_endpoint():
    """Expose Prometheus metrics."""
    return prometheus_client.generate_latest()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check the health of all services."""
    try:
        # Get service status
        ai_status = ai_service.get_service_status()
        
        # Get current metrics
        current_metrics = metrics.get_current_metrics()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "ai_services": ai_status,
                "config": "healthy",
                "telemetry": "healthy"
            },
            "metrics": current_metrics
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Service health check failed"
        )

# AI endpoints
@app.post("/api/v1/analyze")
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze code using AI services.
    Requires authentication.
    """
    try:
        # Record request
        telemetry.record_request(
            endpoint="/api/v1/analyze",
            user_id=current_user.id
        )
        
        # Start model timer
        start_time = datetime.utcnow()
        
        # Perform analysis
        result = await ai_service.analyze_code(
            request.code,
            request.context,
            request.use_cache
        )
        
        # Record model metrics
        duration = (
            datetime.utcnow() - start_time
        ).total_seconds()
        metrics.record_model_inference(
            "context_analyzer",
            duration
        )
        
        if request.use_cache:
            metrics.record_cache_access(
                "analysis_cache",
                hit=hasattr(result, "from_cache")
            )
        
        return {
            "status": "success",
            "data": result.__dict__,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(
            "Code analysis failed",
            error=str(e),
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail="Analysis failed"
        )

@app.post("/api/v1/optimize")
async def optimize_code(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get code optimization suggestions.
    Requires authentication.
    """
    try:
        # Record request
        telemetry.record_request(
            endpoint="/api/v1/optimize",
            user_id=current_user.id
        )
        
        # Start model timer
        start_time = datetime.utcnow()
        
        # Get optimization suggestions
        suggestions = await ai_service.code_optimizer.optimize_code(
            request.code,
            request.context
        )
        
        # Record model metrics
        duration = (
            datetime.utcnow() - start_time
        ).total_seconds()
        metrics.record_model_inference(
            "code_optimizer",
            duration
        )
        
        return {
            "status": "success",
            "data": {
                "suggestions": [s.__dict__ for s in suggestions]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(
            "Code optimization failed",
            error=str(e),
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail="Optimization failed"
        )

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Set up multiprocess metrics
        prometheus_client.REGISTRY.unregister(
            prometheus_client.PROCESS_COLLECTOR
        )
        prometheus_client.REGISTRY.unregister(
            prometheus_client.PLATFORM_COLLECTOR
        )
        prometheus_client.REGISTRY.unregister(
            prometheus_client.GC_COLLECTOR
        )
        
        # Warm up AI models
        await ai_service.warm_up_models()
        logger.info("AI models warmed up successfully")
        
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    try:
        # Clean up AI service
        ai_service.__exit__(None, None, None)
        logger.info("Services shut down successfully")
        
    except Exception as e:
        logger.error("Failed to shut down services", error=str(e))
        raise

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
