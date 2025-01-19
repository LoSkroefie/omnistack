from typing import Dict, Any, Optional, List
import traceback
import logging
import json
from datetime import datetime
from dataclasses import dataclass
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

@dataclass
class ErrorContext:
    user_id: Optional[str]
    component: str
    operation: str
    input_data: Optional[Dict[str, Any]]
    stack_trace: str
    timestamp: str

class ErrorTracker:
    def __init__(self, environment: str = "production"):
        # Initialize Sentry
        sentry_sdk.init(
            dsn="your-sentry-dsn",
            environment=environment,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
            ],
            traces_sample_rate=1.0
        )
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    def track_error(
        self,
        error: Exception,
        context: ErrorContext
    ):
        """Track an error with full context."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": {
                "user_id": context.user_id,
                "component": context.component,
                "operation": context.operation,
                "input_data": context.input_data,
                "timestamp": context.timestamp
            },
            "stack_trace": context.stack_trace
        }
        
        # Log locally
        self.logger.error(
            "Error occurred",
            extra=error_data
        )
        
        # Send to Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_context("error_context", error_data["context"])
            scope.set_tag("component", context.component)
            scope.set_tag("operation", context.operation)
            if context.user_id:
                scope.set_user({"id": context.user_id})
            
            sentry_sdk.capture_exception(error)
    
    def track_warning(
        self,
        message: str,
        context: Dict[str, Any]
    ):
        """Track a warning with context."""
        warning_data = {
            "message": message,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.warning(
            "Warning occurred",
            extra=warning_data
        )
        
        with sentry_sdk.push_scope() as scope:
            scope.set_context("warning_context", context)
            scope.set_level("warning")
            sentry_sdk.capture_message(message)

class ErrorAnalyzer:
    def __init__(self):
        self.error_patterns: Dict[str, List[ErrorContext]] = {}
    
    def analyze_error(
        self,
        error: Exception,
        context: ErrorContext
    ) -> Dict[str, Any]:
        """Analyze an error and provide insights."""
        error_type = type(error).__name__
        
        # Store error pattern
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = []
        self.error_patterns[error_type].append(context)
        
        # Analyze pattern
        pattern_count = len(self.error_patterns[error_type])
        similar_contexts = self._find_similar_contexts(context)
        
        return {
            "error_type": error_type,
            "frequency": pattern_count,
            "similar_occurrences": len(similar_contexts),
            "common_context": self._extract_common_context(similar_contexts),
            "suggested_fixes": self._suggest_fixes(error_type, context)
        }
    
    def _find_similar_contexts(
        self,
        context: ErrorContext
    ) -> List[ErrorContext]:
        """Find similar error contexts."""
        similar_contexts = []
        
        for stored_context in self.error_patterns.get(
            context.component, []
        ):
            if self._is_similar_context(stored_context, context):
                similar_contexts.append(stored_context)
        
        return similar_contexts
    
    def _is_similar_context(
        self,
        context1: ErrorContext,
        context2: ErrorContext
    ) -> bool:
        """Check if two error contexts are similar."""
        return (
            context1.component == context2.component and
            context1.operation == context2.operation
        )
    
    def _extract_common_context(
        self,
        contexts: List[ErrorContext]
    ) -> Dict[str, Any]:
        """Extract common patterns from similar error contexts."""
        if not contexts:
            return {}
        
        common_context = {
            "component": contexts[0].component,
            "operation": contexts[0].operation,
            "input_patterns": self._analyze_input_patterns(contexts)
        }
        
        return common_context
    
    def _analyze_input_patterns(
        self,
        contexts: List[ErrorContext]
    ) -> Dict[str, Any]:
        """Analyze patterns in input data across similar errors."""
        input_patterns = {}
        
        for context in contexts:
            if context.input_data:
                for key, value in context.input_data.items():
                    if key not in input_patterns:
                        input_patterns[key] = []
                    input_patterns[key].append(value)
        
        return {
            key: self._summarize_values(values)
            for key, values in input_patterns.items()
        }
    
    def _summarize_values(self, values: List[Any]) -> Dict[str, Any]:
        """Summarize a list of values to find patterns."""
        return {
            "types": list(set(type(v).__name__ for v in values)),
            "unique_count": len(set(values)),
            "total_count": len(values)
        }
    
    def _suggest_fixes(
        self,
        error_type: str,
        context: ErrorContext
    ) -> List[str]:
        """Suggest potential fixes based on error type and context."""
        suggestions = []
        
        if "IndexError" in error_type:
            suggestions.append("Add bounds checking before accessing indices")
        elif "KeyError" in error_type:
            suggestions.append("Add key existence check before dictionary access")
        elif "TypeError" in error_type:
            suggestions.append("Verify input types and add type checking")
        
        return suggestions
