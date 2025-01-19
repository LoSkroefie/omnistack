import logging
import logging.handlers
import json
from typing import Any, Dict, Optional
from pathlib import Path
import sys
import traceback
from datetime import datetime
import structlog
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = True
) -> None:
    """Setup structured logging configuration."""
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if json_format:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

class LoggerAdapter:
    """Adapter for structured logging with context."""
    
    def __init__(self, logger_name: str):
        self.logger = structlog.get_logger(logger_name)
        self.context: Dict[str, Any] = {}
    
    def bind(self, **kwargs) -> 'LoggerAdapter':
        """Bind additional context to logger."""
        self.context.update(kwargs)
        return self
    
    def _log(
        self,
        level: str,
        event: str,
        **kwargs
    ) -> None:
        """Internal logging method."""
        context = {**self.context, **kwargs}
        logger_method = getattr(self.logger, level)
        logger_method(event, **context)
    
    def debug(self, event: str, **kwargs) -> None:
        self._log('debug', event, **kwargs)
    
    def info(self, event: str, **kwargs) -> None:
        self._log('info', event, **kwargs)
    
    def warning(self, event: str, **kwargs) -> None:
        self._log('warning', event, **kwargs)
    
    def error(self, event: str, **kwargs) -> None:
        self._log('error', event, **kwargs)
    
    def exception(
        self,
        event: str,
        exc_info: Optional[Exception] = None,
        **kwargs
    ) -> None:
        if exc_info:
            kwargs['exc_info'] = exc_info
        self._log('exception', event, **kwargs)

class RequestLogger:
    """Logger for HTTP requests with timing and context."""
    
    def __init__(self, logger: LoggerAdapter):
        self.logger = logger
    
    async def log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log HTTP request details."""
        log_data = {
            'request_id': request_id,
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': duration_ms
        }
        
        if user_id:
            log_data['user_id'] = user_id
        
        if extra:
            log_data.update(extra)
        
        level = 'info' if status_code < 400 else 'error'
        self.logger.bind(**log_data)._log(
            level,
            f"{method} {path} completed"
        )

class AuditLogger:
    """Logger for audit events with user context."""
    
    def __init__(self, logger: LoggerAdapter):
        self.logger = logger
    
    def log_audit_event(
        self,
        event_type: str,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log audit event."""
        audit_data = {
            'event_type': event_type,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            audit_data['details'] = details
        
        self.logger.info(
            f"Audit: {event_type}",
            **audit_data
        )
