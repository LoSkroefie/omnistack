from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Response
import psutil
import redis
import asyncpg
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class HealthCheck:
    def __init__(
        self,
        database_url: str,
        redis_url: str
    ):
        self.database_url = database_url
        self.redis_url = redis_url
        self.start_time = datetime.utcnow()
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connection."""
        try:
            conn = await asyncpg.connect(self.database_url)
            version = await conn.fetchval('SELECT version()')
            await conn.close()
            return {
                "status": "healthy",
                "version": version
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis connection."""
        try:
            client = redis.from_url(self.redis_url)
            info = client.info()
            return {
                "status": "healthy",
                "version": info["redis_version"]
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def check_system(self) -> Dict[str, Any]:
        """Check system resources."""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy",
                "metrics": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent
                }
            }
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        db_health = await self.check_database()
        redis_health = self.check_redis()
        system_health = self.check_system()
        
        status = "healthy"
        if any(
            check["status"] == "unhealthy"
            for check in [db_health, redis_health, system_health]
        ):
            status = "unhealthy"
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": uptime,
            "checks": {
                "database": db_health,
                "redis": redis_health,
                "system": system_health
            }
        }

@router.get("/health")
async def health_check(response: Response):
    """Basic health check endpoint."""
    return {"status": "healthy"}

@router.get("/ready")
async def readiness_check(response: Response):
    """Readiness check endpoint."""
    health_checker = HealthCheck(
        database_url="postgresql://user:pass@localhost:5432/omnistack",
        redis_url="redis://localhost:6379/0"
    )
    
    result = await health_checker.check_all()
    
    if result["status"] == "unhealthy":
        response.status_code = 503
    
    return result

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        metrics = [
            f'# HELP omnistack_cpu_usage Current CPU usage',
            f'# TYPE omnistack_cpu_usage gauge',
            f'omnistack_cpu_usage {cpu_percent}',
            f'# HELP omnistack_memory_usage Current memory usage',
            f'# TYPE omnistack_memory_usage gauge',
            f'omnistack_memory_usage {memory.percent}'
        ]
        
        return Response(
            content='\n'.join(metrics),
            media_type='text/plain'
        )
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to collect metrics"
        )
