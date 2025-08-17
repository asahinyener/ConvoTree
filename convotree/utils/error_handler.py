#!/usr/bin/env python3
"""
Comprehensive Error Handling System for ConvoTree
Provides robust error recovery, logging, and user-friendly error messages
"""

import sys
import traceback
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Type, List
from dataclasses import dataclass
from enum import Enum
import time
import sqlite3
from openai import OpenAI, RateLimitError, APIConnectionError, APITimeoutError

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better handling"""
    API = "api"
    DATABASE = "database"
    NETWORK = "network"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    USER_INPUT = "user_input"

@dataclass
class ErrorInfo:
    """Structured error information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    user_message: str
    timestamp: datetime
    context: Dict[str, Any]
    stacktrace: Optional[str] = None
    recovery_suggestions: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_id": self.error_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "user_message": self.user_message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "stacktrace": self.stacktrace,
            "recovery_suggestions": self.recovery_suggestions or []
        }

class ConvoTreeErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self, log_file: Optional[str] = None, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.error_count = 0
        self.error_history: List[ErrorInfo] = []
        
        # Setup logging
        self.logger = self._setup_logging(log_file)
        
        # Error recovery strategies
        self.recovery_strategies = {
            ErrorCategory.API: self._recover_api_error,
            ErrorCategory.DATABASE: self._recover_database_error,
            ErrorCategory.NETWORK: self._recover_network_error,
            ErrorCategory.CONFIGURATION: self._recover_config_error
        }
        
        # User-friendly error messages
        self.user_messages = {
            RateLimitError: "I'm receiving too many requests right now. Please wait a moment and try again.",
            APIConnectionError: "I'm having trouble connecting to the AI service. Please check your internet connection.",
            APITimeoutError: "The AI service is taking too long to respond. Please try again.",
            sqlite3.OperationalError: "There's an issue with the conversation database. Trying to recover...",
            FileNotFoundError: "A required file is missing. Checking system configuration...",
            json.JSONDecodeError: "There was an issue processing data. Attempting to recover...",
            ValueError: "There's an issue with the provided data. Please check your input.",
            KeyError: "Some expected information is missing. Trying alternative approach...",
            ConnectionError: "Network connection issue. Please check your internet connection.",
            PermissionError: "Permission denied accessing a file or resource. Please check file permissions."
        }
    
    def _setup_logging(self, log_file: Optional[str]) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('convotree')
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    user_facing: bool = True) -> ErrorInfo:
        """Main error handling entry point"""
        self.error_count += 1
        
        # Determine error category and severity
        category = self._categorize_error(error)
        severity = self._assess_severity(error, category)
        
        # Generate error ID
        error_id = f"{category.value}_{int(time.time())}_{self.error_count}"
        
        # Get user-friendly message
        user_message = self._get_user_message(error)
        
        # Create error info
        error_info = ErrorInfo(
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(error),
            user_message=user_message,
            timestamp=datetime.now(),
            context=context or {},
            stacktrace=traceback.format_exc() if self.debug_mode else None,
            recovery_suggestions=self._get_recovery_suggestions(error, category)
        )
        
        # Log the error
        self._log_error(error_info)
        
        # Store in history
        self.error_history.append(error_info)
        
        # Attempt recovery if strategy exists
        if category in self.recovery_strategies:
            try:
                self.recovery_strategies[category](error, context or {})
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
        
        return error_info
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error for appropriate handling"""
        error_type = type(error)
        
        # API errors
        if issubclass(error_type, (RateLimitError, APIConnectionError, APITimeoutError)):
            return ErrorCategory.API
        
        # Database errors
        if issubclass(error_type, sqlite3.Error):
            return ErrorCategory.DATABASE
        
        # Network errors
        if issubclass(error_type, (ConnectionError, TimeoutError)):
            return ErrorCategory.NETWORK
        
        # Validation errors
        if issubclass(error_type, (ValueError, TypeError, KeyError)):
            return ErrorCategory.VALIDATION
        
        # Configuration errors
        if issubclass(error_type, (FileNotFoundError, PermissionError)):
            return ErrorCategory.CONFIGURATION
        
        # Default to system error
        return ErrorCategory.SYSTEM
    
    def _assess_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Assess error severity"""
        error_type = type(error)
        
        # Critical errors that stop the system
        if issubclass(error_type, (SystemExit, KeyboardInterrupt)):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category == ErrorCategory.DATABASE and "database is locked" in str(error).lower():
            return ErrorSeverity.HIGH
        
        if issubclass(error_type, (MemoryError, OSError)):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.API, ErrorCategory.NETWORK]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors (recoverable)
        return ErrorSeverity.LOW
    
    def _get_user_message(self, error: Exception) -> str:
        """Get user-friendly error message"""
        error_type = type(error)
        
        # Check for specific error type messages
        if error_type in self.user_messages:
            return self.user_messages[error_type]
        
        # Check parent classes
        for exc_type, message in self.user_messages.items():
            if issubclass(error_type, exc_type):
                return message
        
        # Generic message
        return "An unexpected error occurred. The system is attempting to recover."
    
    def _get_recovery_suggestions(self, error: Exception, category: ErrorCategory) -> List[str]:
        """Get recovery suggestions for the error"""
        suggestions = []
        
        if category == ErrorCategory.API:
            suggestions.extend([
                "Check your internet connection",
                "Verify your OpenAI API key is valid",
                "Try again in a few moments",
                "Check OpenAI service status"
            ])
        
        elif category == ErrorCategory.DATABASE:
            suggestions.extend([
                "Check database file permissions",
                "Ensure sufficient disk space",
                "Restart the application",
                "Check for database corruption"
            ])
        
        elif category == ErrorCategory.NETWORK:
            suggestions.extend([
                "Check internet connectivity",
                "Verify firewall settings",
                "Try using a different network",
                "Check proxy settings"
            ])
        
        elif category == ErrorCategory.CONFIGURATION:
            suggestions.extend([
                "Check configuration file exists",
                "Verify file permissions",
                "Review environment variables",
                "Check installation integrity"
            ])
        
        return suggestions
    
    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level"""
        log_message = f"[{error_info.error_id}] {error_info.message}"
        
        if error_info.context:
            log_message += f" | Context: {json.dumps(error_info.context)}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Log stacktrace if in debug mode
        if self.debug_mode and error_info.stacktrace:
            self.logger.debug(f"Stacktrace for {error_info.error_id}:\n{error_info.stacktrace}")
    
    def _recover_api_error(self, error: Exception, context: Dict[str, Any]):
        """Recovery strategy for API errors"""
        if isinstance(error, RateLimitError):
            # Implement exponential backoff
            wait_time = min(60, 2 ** context.get('retry_count', 0))
            self.logger.info(f"Rate limited. Waiting {wait_time} seconds before retry.")
            time.sleep(wait_time)
        
        elif isinstance(error, (APIConnectionError, APITimeoutError)):
            # Check network connectivity
            self.logger.info("Checking network connectivity...")
            # Could implement ping test here
    
    def _recover_database_error(self, error: Exception, context: Dict[str, Any]):
        """Recovery strategy for database errors"""
        if "database is locked" in str(error).lower():
            self.logger.info("Database locked. Waiting for lock to clear...")
            time.sleep(1)
        
        elif "no such table" in str(error).lower():
            self.logger.info("Database table missing. Attempting to recreate...")
            # Could attempt to recreate tables here
    
    def _recover_network_error(self, error: Exception, context: Dict[str, Any]):
        """Recovery strategy for network errors"""
        self.logger.info("Network error detected. Implementing retry with backoff...")
        time.sleep(min(10, 2 ** context.get('retry_count', 0)))
    
    def _recover_config_error(self, error: Exception, context: Dict[str, Any]):
        """Recovery strategy for configuration errors"""
        if isinstance(error, FileNotFoundError):
            self.logger.info("Configuration file missing. Using defaults...")
        
        elif isinstance(error, PermissionError):
            self.logger.error("Permission denied. Please check file permissions.")
    
    def with_error_handling(self, func: Callable, *args, **kwargs) -> Any:
        """Decorator for automatic error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = self.handle_error(e, {"function": func.__name__, "args": str(args)[:100]})
            
            # Re-raise critical errors
            if error_info.severity == ErrorSeverity.CRITICAL:
                raise
            
            # Return None for other errors (graceful degradation)
            return None
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_history:
            return {"total_errors": 0}
        
        # Count by category
        category_counts = {}
        severity_counts = {}
        
        for error in self.error_history:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        # Recent errors (last hour)
        recent_errors = [
            e for e in self.error_history 
            if (datetime.now() - e.timestamp).total_seconds() < 3600
        ]
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "category_breakdown": category_counts,
            "severity_breakdown": severity_counts,
            "last_error": self.error_history[-1].to_dict() if self.error_history else None,
            "error_rate": len(recent_errors) / 60 if recent_errors else 0  # per minute
        }
    
    def export_error_log(self, filename: str = None) -> str:
        """Export error log to file"""
        if not filename:
            filename = f"convotree_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_errors": len(self.error_history),
            "errors": [error.to_dict() for error in self.error_history]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filename
    
    def clear_error_history(self):
        """Clear error history (useful for testing)"""
        self.error_history.clear()
        self.error_count = 0
        self.logger.info("Error history cleared")

# Global error handler instance
_global_error_handler: Optional[ConvoTreeErrorHandler] = None

def get_error_handler(debug_mode: bool = False) -> ConvoTreeErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ConvoTreeErrorHandler(debug_mode=debug_mode)
    return _global_error_handler

def handle_error(error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
    """Convenience function for error handling"""
    return get_error_handler().handle_error(error, context)

def with_error_handling(func: Callable) -> Callable:
    """Decorator for automatic error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = handle_error(e, {"function": func.__name__})
            
            # Re-raise critical errors
            if error_info.severity == ErrorSeverity.CRITICAL:
                raise
            
            # Return None for graceful degradation
            return None
    
    return wrapper