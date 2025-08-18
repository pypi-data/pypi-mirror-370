"""
Advanced Logging System for UMAT API Testing
Provides comprehensive logging with file rotation, structured logging, and performance metrics
"""

import logging
import logging.handlers
import json
import time
import functools
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    extra_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured data"""
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            extra_data=getattr(record, 'extra_data', None)
        )

        return log_entry.to_json()

class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """Format with colors"""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

class PerformanceLogger:
    """Performance monitoring and logging"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._timers: Dict[str, float] = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation"""
        self._timers[operation] = time.time()
        self.logger.debug(f"Started timing: {operation}")

    def end_timer(self, operation: str) -> float:
        """End timing and log duration"""
        if operation not in self._timers:
            self.logger.warning(f"Timer not found for operation: {operation}")
            return 0.0

        duration = time.time() - self._timers[operation]
        del self._timers[operation]

        self.logger.info(f"Operation '{operation}' completed in {duration:.4f}s")
        return duration

    def time_function(self, func: Callable) -> Callable:
        """Decorator to time function execution"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                self.logger.info(
                    f"Function '{func.__name__}' executed successfully in {duration:.4f}s",
                    extra={'extra_data': {'duration': duration, 'function': func.__name__}}
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                self.logger.error(
                    f"Function '{func.__name__}' failed after {duration:.4f}s: {str(e)}",
                    extra={'extra_data': {'duration': duration, 'function': func.__name__, 'error': str(e)}}
                )
                raise
        return wrapper

class APILogger:
    """Specialized logger for API operations"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_request(self, method: str, url: str, headers: Dict[str, str],
                   payload: Optional[Dict[str, Any]] = None) -> None:
        """Log API request details"""
        request_data = {
            'method': method,
            'url': url,
            'headers': {k: v for k, v in headers.items() if k.lower() != 'authorization'},
            'payload': payload
        }

        # Mask sensitive data
        if 'authorization' in [h.lower() for h in headers.keys()]:
            request_data['headers']['authorization'] = '[MASKED]'

        self.logger.info(
            f"API Request: {method} {url}",
            extra={'extra_data': request_data}
        )

    def log_response(self, status_code: int, response_time: float,
                    response_data: Optional[Dict[str, Any]] = None,
                    error: Optional[str] = None) -> None:
        """Log API response details"""
        response_info = {
            'status_code': status_code,
            'response_time': response_time,
            'success': 200 <= status_code < 300
        }

        if response_data:
            response_info['response_data'] = response_data

        if error:
            response_info['error'] = error

        level = logging.INFO if response_info['success'] else logging.ERROR
        message = f"API Response: {status_code} ({response_time:.4f}s)"

        self.logger.log(level, message, extra={'extra_data': response_info})

class LoggerManager:
    """Advanced logger management system"""

    def __init__(self, base_path: str = "logs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self._loggers: Dict[str, logging.Logger] = {}
        self._performance_loggers: Dict[str, PerformanceLogger] = {}
        self._api_loggers: Dict[str, APILogger] = {}

    def setup_logger(self, name: str, level: LogLevel = LogLevel.INFO,
                    enable_file_logging: bool = True,
                    enable_console_logging: bool = False,  # Disabled by default for clean UI
                    enable_structured_logging: bool = False) -> logging.Logger:
        """Setup a comprehensive logger"""

        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level.value)
        logger.handlers.clear()  # Clear existing handlers
        logger.propagate = False  # Prevent propagation to root logger

        # Console handler with colors
        if enable_console_logging:
            console_handler = logging.StreamHandler()
            console_formatter = ColoredConsoleFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # File handler with rotation
        if enable_file_logging:
            log_file = self.base_path / f"{name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )

            if enable_structured_logging:
                file_formatter = StructuredFormatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
                )

            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # Error file handler
        if enable_file_logging:
            error_file = self.base_path / f"{name}_errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_file, maxBytes=5*1024*1024, backupCount=3
            )
            error_handler.setLevel(logging.ERROR)
            error_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s\n%(exc_info)s'
            )
            error_handler.setFormatter(error_formatter)
            logger.addHandler(error_handler)

        self._loggers[name] = logger
        return logger

    def get_logger(self, name: str) -> logging.Logger:
        """Get existing logger or create new one"""
        if name not in self._loggers:
            return self.setup_logger(name)
        return self._loggers[name]

    def get_performance_logger(self, name: str) -> PerformanceLogger:
        """Get performance logger for timing operations"""
        if name not in self._performance_loggers:
            logger = self.get_logger(f"{name}_performance")
            self._performance_loggers[name] = PerformanceLogger(logger)
        return self._performance_loggers[name]

    def get_api_logger(self, name: str) -> APILogger:
        """Get API logger for request/response logging"""
        if name not in self._api_loggers:
            logger = self.get_logger(f"{name}_api")
            self._api_loggers[name] = APILogger(logger)
        return self._api_loggers[name]

    def shutdown_all_loggers(self) -> None:
        """Shutdown all loggers and handlers"""
        for logger in self._loggers.values():
            for handler in logger.handlers:
                handler.close()
            logger.handlers.clear()

        self._loggers.clear()
        self._performance_loggers.clear()
        self._api_loggers.clear()

# Global logger manager instance
logger_manager = LoggerManager()

# Convenience functions
def setup_logger(name: str, level: LogLevel = LogLevel.INFO, **kwargs) -> logging.Logger:
    """Setup logger with default configuration (file-only for clean UI)"""
    return logger_manager.setup_logger(name, level, **kwargs)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logger_manager.get_logger(name)

def get_performance_logger(name: str) -> PerformanceLogger:
    """Get performance logger instance"""
    return logger_manager.get_performance_logger(name)

def get_api_logger(name: str) -> APILogger:
    """Get API logger instance"""
    return logger_manager.get_api_logger(name)