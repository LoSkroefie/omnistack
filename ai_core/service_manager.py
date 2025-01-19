from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
from datetime import datetime

from .context_analyzer import ContextAnalyzer
from .predictive_debugger import PredictiveDebugger
from .code_optimizer import CodeOptimizer
from ..monitoring.telemetry import TelemetryManager
from ..cache.cache_manager import CacheManager
from ..config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    quality_score: float
    issues: List[Dict]
    optimizations: List[Dict]
    patterns: List[Dict]
    execution_time: float
    timestamp: str

class AIServiceManager:
    def __init__(
        self,
        config_path: Optional[str] = None,
        model_name: str = "microsoft/codebert-base"
    ):
        self.config = ConfigManager(config_path)
        self.telemetry = TelemetryManager()
        self.cache = CacheManager()
        
        # Initialize AI services
        self.context_analyzer = ContextAnalyzer(model_name)
        self.predictive_debugger = PredictiveDebugger(model_name)
        self.code_optimizer = CodeOptimizer(model_name)
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get_api_config().workers
        )
    
    async def analyze_code(
        self,
        code: str,
        context: Optional[Dict] = None,
        use_cache: bool = True
    ) -> AnalysisResult:
        """
        Perform comprehensive code analysis using all AI services.
        """
        start_time = datetime.utcnow()
        
        # Check cache
        if use_cache:
            cache_key = f"analysis:{hash(code)}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info("Using cached analysis result")
                return AnalysisResult(**cached_result)
        
        try:
            # Run analyses in parallel
            tasks = [
                self._run_context_analysis(code, context),
                self._run_debug_analysis(code, context),
                self._run_optimization_analysis(code, context)
            ]
            
            results = await asyncio.gather(*tasks)
            context_result, debug_result, optimization_result = results
            
            # Combine results
            result = AnalysisResult(
                quality_score=context_result["code_quality_score"],
                issues=debug_result,
                optimizations=optimization_result,
                patterns=context_result.get("related_patterns", []),
                execution_time=(
                    datetime.utcnow() - start_time
                ).total_seconds(),
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Cache result
            if use_cache:
                await self.cache.set(
                    cache_key,
                    result.__dict__,
                    ttl=3600  # 1 hour
                )
            
            # Record telemetry
            self.telemetry.record_analysis(
                code_size=len(code),
                execution_time=result.execution_time,
                quality_score=result.quality_score,
                issue_count=len(result.issues)
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            self.telemetry.record_error("analysis_failure", str(e))
            raise
    
    async def _run_context_analysis(
        self,
        code: str,
        context: Optional[Dict]
    ) -> Dict:
        """Run context analysis in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.context_analyzer.analyze_code_context,
            code,
            context
        )
    
    async def _run_debug_analysis(
        self,
        code: str,
        context: Optional[Dict]
    ) -> List[Dict]:
        """Run debug analysis in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.predictive_debugger.analyze_code,
            code,
            context
        )
    
    async def _run_optimization_analysis(
        self,
        code: str,
        context: Optional[Dict]
    ) -> List[Dict]:
        """Run optimization analysis in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.code_optimizer.optimize_code,
            code,
            context
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all AI services."""
        return {
            "context_analyzer": {
                "status": "healthy",
                "model": self.context_analyzer.model.config.name_or_path
            },
            "predictive_debugger": {
                "status": "healthy",
                "model": self.predictive_debugger.model.config.name_or_path
            },
            "code_optimizer": {
                "status": "healthy",
                "model": self.code_optimizer.model.config.name_or_path
            }
        }
    
    async def warm_up_models(self):
        """Pre-warm models for faster initial inference."""
        sample_code = "def hello(): return 'world'"
        await self.analyze_code(
            sample_code,
            use_cache=False
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
        if exc_type:
            logger.error(
                f"Error during service manager execution: {str(exc_val)}"
            )
